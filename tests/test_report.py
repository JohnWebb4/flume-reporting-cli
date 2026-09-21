import csv
from datetime import datetime
from typing import ClassVar

import pytest

from flume_cli import report
from flume_cli.errors import FlumeCliError


def _dt(*args):
    """Build a naive local datetime, matching report.py's own assumption (see CLAUDE.md)."""
    return datetime(*args)  # noqa: DTZ001


class _FixedDateTime:
    """Stand-in for the `datetime` name in report.py, fixing `.now()`."""

    def __init__(self, fixed):
        self._fixed = fixed

    def now(self):
        return self._fixed


@pytest.fixture
def fixed_now(monkeypatch):
    def _apply(fixed):
        monkeypatch.setattr(report, "datetime", _FixedDateTime(fixed))
        return fixed

    return _apply


class TestDailyWindows:
    def test_returns_one_window_per_day_oldest_first(self):
        end = _dt(2026, 9, 20, 8, 30, 0)

        windows = report.daily_windows(3, end=end)

        assert windows == [
            ("2026-09-17 08:30:00", "2026-09-18 08:30:00"),
            ("2026-09-18 08:30:00", "2026-09-19 08:30:00"),
            ("2026-09-19 08:30:00", "2026-09-20 08:30:00"),
        ]

    def test_windows_are_contiguous(self):
        end = _dt(2026, 9, 20, 8, 30, 0)

        windows = report.daily_windows(5, end=end)

        for (_, until), (next_since, _) in zip(windows, windows[1:]):
            assert until == next_since

    def test_zero_days_returns_no_windows(self):
        assert report.daily_windows(0, end=_dt(2026, 9, 20)) == []

    def test_defaults_end_to_now(self, fixed_now):
        fixed_now(_dt(2026, 9, 20, 12, 0, 0))

        windows = report.daily_windows(1)

        assert windows == [("2026-09-19 12:00:00", "2026-09-20 12:00:00")]


class TestMonthWindows:
    def test_covers_last_full_calendar_month(self):
        reference = _dt(2026, 9, 15, 10, 0, 0)

        windows = report.month_windows(reference)

        assert windows[0][0] == "2026-08-01 00:00:00"
        assert windows[-1][1] == "2026-09-01 00:00:00"
        assert len(windows) == 31  # August has 31 days

    def test_windows_are_contiguous(self):
        reference = _dt(2026, 9, 15, 10, 0, 0)

        windows = report.month_windows(reference)

        for (_, until), (next_since, _) in zip(windows, windows[1:]):
            assert until == next_since

    def test_january_wraps_to_previous_december(self):
        reference = _dt(2026, 1, 10, 0, 0, 0)

        windows = report.month_windows(reference)

        assert windows[0][0] == "2025-12-01 00:00:00"
        assert windows[-1][1] == "2026-01-01 00:00:00"
        assert len(windows) == 31  # December has 31 days

    def test_leap_year_february(self):
        reference = _dt(2024, 3, 5, 0, 0, 0)

        windows = report.month_windows(reference)

        assert windows[0][0] == "2024-02-01 00:00:00"
        assert windows[-1][1] == "2024-03-01 00:00:00"
        assert len(windows) == 29  # 2024 is a leap year

    def test_non_leap_year_february(self):
        reference = _dt(2026, 3, 5, 0, 0, 0)

        windows = report.month_windows(reference)

        assert len(windows) == 28

    def test_each_window_spans_one_day(self):
        reference = _dt(2026, 9, 15, 0, 0, 0)

        windows = report.month_windows(reference)

        for since, until in windows:
            since_dt = datetime.strptime(since, report.DATETIME_FORMAT)  # noqa: DTZ007
            until_dt = datetime.strptime(until, report.DATETIME_FORMAT)  # noqa: DTZ007
            assert (until_dt - since_dt).total_seconds() == 24 * 3600

    def test_defaults_reference_to_now(self, fixed_now):
        fixed_now(_dt(2026, 9, 15, 10, 0, 0))

        windows = report.month_windows()

        assert windows[0][0] == "2026-08-01 00:00:00"
        assert windows[-1][1] == "2026-09-01 00:00:00"


class TestSelectDeviceIds:
    DEVICES: ClassVar = [{"id": "a"}, {"id": "b"}, {"id": "c"}]

    def test_returns_all_device_ids_when_none_requested(self):
        assert report.select_device_ids(self.DEVICES, None) == ["a", "b", "c"]

    def test_returns_all_device_ids_when_empty_list_requested(self):
        assert report.select_device_ids(self.DEVICES, []) == ["a", "b", "c"]

    def test_returns_requested_subset_in_requested_order(self):
        assert report.select_device_ids(self.DEVICES, ["c", "a"]) == ["c", "a"]

    def test_raises_when_requested_id_not_found(self):
        with pytest.raises(FlumeCliError, match="not found for this account"):
            report.select_device_ids(self.DEVICES, ["a", "missing"])

    def test_error_message_lists_all_unknown_ids(self):
        with pytest.raises(FlumeCliError, match="x, y"):
            report.select_device_ids(self.DEVICES, ["x", "y"])


class FakeClient:
    def __init__(self, readings_by_call):
        self._readings_by_call = readings_by_call
        self.calls = []

    def query_device(self, user_id, device_id, *, since, until, bucket, units):
        self.calls.append((user_id, device_id, since, until, bucket, units))
        return self._readings_by_call.get((device_id, since, until), [])


class TestBuildReportRows:
    def test_yields_rows_per_device_per_window_in_order(self):
        windows = [("2026-09-01 00:00:00", "2026-09-02 00:00:00"),
                   ("2026-09-02 00:00:00", "2026-09-03 00:00:00")]
        readings = {
            ("dev-1", *windows[0]): [{"datetime": "2026-09-01 05:00:00", "value": 1.5}],
            ("dev-1", *windows[1]): [{"datetime": "2026-09-02 05:00:00", "value": 2.5}],
            ("dev-2", *windows[0]): [{"datetime": "2026-09-01 06:00:00", "value": 3.0}],
            ("dev-2", *windows[1]): [],
        }
        client = FakeClient(readings)

        rows = list(
            report.build_report_rows(
                client, "user-1", ["dev-1", "dev-2"],
                windows=windows, bucket="HR", units="GALLONS",
            )
        )

        assert rows == [
            {"device_id": "dev-1", "datetime": "2026-09-01 05:00:00", "value": 1.5, "units": "GALLONS"},
            {"device_id": "dev-1", "datetime": "2026-09-02 05:00:00", "value": 2.5, "units": "GALLONS"},
            {"device_id": "dev-2", "datetime": "2026-09-01 06:00:00", "value": 3.0, "units": "GALLONS"},
        ]

    def test_calls_client_once_per_device_per_window(self):
        windows = [("since-1", "until-1"), ("since-2", "until-2")]
        client = FakeClient({})

        list(
            report.build_report_rows(
                client, "user-1", ["dev-1", "dev-2"],
                windows=windows, bucket="MIN", units="LITERS",
            )
        )

        assert client.calls == [
            ("user-1", "dev-1", "since-1", "until-1", "MIN", "LITERS"),
            ("user-1", "dev-1", "since-2", "until-2", "MIN", "LITERS"),
            ("user-1", "dev-2", "since-1", "until-1", "MIN", "LITERS"),
            ("user-1", "dev-2", "since-2", "until-2", "MIN", "LITERS"),
        ]

    def test_no_devices_yields_no_rows_and_makes_no_calls(self):
        client = FakeClient({})

        rows = list(
            report.build_report_rows(
                client, "user-1", [], windows=[("s", "u")], bucket="HR", units="GALLONS",
            )
        )

        assert rows == []
        assert client.calls == []


class TestWriteCsv:
    def test_writes_header_and_rows(self, tmp_path):
        output = tmp_path / "report.csv"
        rows = [
            {"device_id": "dev-1", "datetime": "2026-09-01 00:00:00", "value": 1.5, "units": "GALLONS"},
            {"device_id": "dev-2", "datetime": "2026-09-01 01:00:00", "value": 2.0, "units": "GALLONS"},
        ]

        count = report.write_csv(rows, output)

        assert count == 2
        with open(output, newline="") as f:
            reader = csv.DictReader(f)
            assert reader.fieldnames == report.CSV_FIELDNAMES
            written = list(reader)
        assert written == [
            {"device_id": "dev-1", "datetime": "2026-09-01 00:00:00", "value": "1.5", "units": "GALLONS"},
            {"device_id": "dev-2", "datetime": "2026-09-01 01:00:00", "value": "2.0", "units": "GALLONS"},
        ]

    def test_writes_header_only_for_empty_rows(self, tmp_path):
        output = tmp_path / "empty.csv"

        count = report.write_csv([], output)

        assert count == 0
        with open(output, newline="") as f:
            reader = csv.DictReader(f)
            assert reader.fieldnames == report.CSV_FIELDNAMES
            assert list(reader) == []

    def test_rows_is_consumed_lazily_from_an_iterator(self, tmp_path):
        output = tmp_path / "report.csv"

        def row_generator():
            yield {"device_id": "dev-1", "datetime": "t", "value": 1, "units": "GALLONS"}

        count = report.write_csv(row_generator(), output)

        assert count == 1
