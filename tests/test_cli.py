import csv
from datetime import datetime

import pytest

from flume_cli import cli
from flume_cli.errors import ConfigError, FlumeCliError


def _dt(*args):
    """Build a naive local datetime, matching cli.py's own assumption (see CLAUDE.md)."""
    return datetime(*args)  # noqa: DTZ001


class TestMonthArgParsing:
    def test_both_flags_parse_correctly(self):
        args = cli.build_parser().parse_args(["month", "--month", "3", "--year", "2025"])

        assert args.month == 3
        assert args.year == 2025

    def test_no_flags_default_to_none(self):
        args = cli.build_parser().parse_args(["month"])

        assert args.month is None
        assert args.year is None

    def test_rejects_out_of_range_month(self):
        with pytest.raises(SystemExit) as exc_info:
            cli.build_parser().parse_args(["month", "--month", "13", "--year", "2025"])

        assert exc_info.value.code == 2

    def test_rejects_month_zero(self):
        with pytest.raises(SystemExit) as exc_info:
            cli.build_parser().parse_args(["month", "--month", "0", "--year", "2025"])

        assert exc_info.value.code == 2

    def test_month_subcommand_rejects_day_flag(self):
        with pytest.raises(SystemExit) as exc_info:
            cli.build_parser().parse_args(["month", "--day", "15"])

        assert exc_info.value.code == 2


class TestDayArgParsing:
    def test_all_three_flags_parse_correctly(self):
        args = cli.build_parser().parse_args(
            ["day", "--day", "15", "--month", "3", "--year", "2025"]
        )

        assert args.day == 15
        assert args.month == 3
        assert args.year == 2025

    def test_no_flags_default_to_none(self):
        args = cli.build_parser().parse_args(["day"])

        assert args.day is None
        assert args.month is None
        assert args.year is None

    def test_rejects_out_of_range_month(self):
        with pytest.raises(SystemExit) as exc_info:
            cli.build_parser().parse_args(
                ["day", "--day", "1", "--month", "13", "--year", "2025"]
            )

        assert exc_info.value.code == 2


class TestMonthYearPairingValidation:
    def test_only_month_flag_exits_2(self, capsys):
        with pytest.raises(SystemExit) as exc_info:
            cli.main(["month", "--month", "3"])

        assert exc_info.value.code == 2
        assert "--month and --year must be provided together" in capsys.readouterr().err

    def test_only_year_flag_exits_2(self, capsys):
        with pytest.raises(SystemExit) as exc_info:
            cli.main(["month", "--year", "2025"])

        assert exc_info.value.code == 2
        assert "--month and --year must be provided together" in capsys.readouterr().err


class TestDayFlagsPairingValidation:
    def test_only_day_flag_exits_2(self, capsys):
        with pytest.raises(SystemExit) as exc_info:
            cli.main(["day", "--day", "15"])

        assert exc_info.value.code == 2
        assert "--day, --month, and --year must be provided together" in capsys.readouterr().err

    def test_only_month_flag_exits_2(self, capsys):
        with pytest.raises(SystemExit) as exc_info:
            cli.main(["day", "--month", "3"])

        assert exc_info.value.code == 2
        assert "--day, --month, and --year must be provided together" in capsys.readouterr().err

    def test_only_year_flag_exits_2(self, capsys):
        with pytest.raises(SystemExit) as exc_info:
            cli.main(["day", "--year", "2025"])

        assert exc_info.value.code == 2
        assert "--day, --month, and --year must be provided together" in capsys.readouterr().err

    def test_day_and_month_without_year_exits_2(self, capsys):
        with pytest.raises(SystemExit) as exc_info:
            cli.main(["day", "--day", "15", "--month", "3"])

        assert exc_info.value.code == 2
        assert "--day, --month, and --year must be provided together" in capsys.readouterr().err


class TestRejectCurrentOrFutureMonth:
    def test_raises_for_current_month(self):
        now = _dt(2026, 9, 20)

        with pytest.raises(ConfigError, match="still in progress"):
            cli._reject_current_or_future_month(2026, 9, now=now)

    def test_raises_for_future_month(self):
        now = _dt(2026, 9, 20)

        with pytest.raises(ConfigError, match="still in progress"):
            cli._reject_current_or_future_month(2026, 10, now=now)

    def test_accepts_past_month(self):
        now = _dt(2026, 9, 20)

        cli._reject_current_or_future_month(2026, 8, now=now)


class TestRejectTodayOrFutureDay:
    def test_raises_for_today(self):
        now = _dt(2026, 9, 20)

        with pytest.raises(ConfigError, match="hasn't finished yet"):
            cli._reject_today_or_future_day(2026, 9, 20, now=now)

    def test_raises_for_future_day(self):
        now = _dt(2026, 9, 20)

        with pytest.raises(ConfigError, match="hasn't finished yet"):
            cli._reject_today_or_future_day(2026, 9, 21, now=now)

    def test_accepts_past_day(self):
        now = _dt(2026, 9, 20)

        cli._reject_today_or_future_day(2026, 9, 19, now=now)


class TestRejectBucketMismatch:
    def test_no_op_when_file_does_not_exist(self, tmp_path):
        cli._reject_bucket_mismatch(tmp_path / "missing.csv", "HR")

    def test_no_op_when_bucket_cannot_be_inferred(self, tmp_path):
        existing = tmp_path / "report.csv"
        existing.write_text("device_id,datetime,value,units\n")

        cli._reject_bucket_mismatch(existing, "HR")

    def test_no_op_when_bucket_matches(self, tmp_path):
        existing = tmp_path / "report.csv"
        existing.write_text(
            "device_id,datetime,value,units\n"
            "dev-1,2026-09-01 00:00:00,1.0,GALLONS\n"
            "dev-1,2026-09-01 01:00:00,1.0,GALLONS\n"
        )

        cli._reject_bucket_mismatch(existing, "HR")

    def test_raises_when_bucket_differs(self, tmp_path):
        existing = tmp_path / "report.csv"
        existing.write_text(
            "device_id,datetime,value,units\n"
            "dev-1,2026-09-01 00:00:00,1.0,GALLONS\n"
            "dev-1,2026-09-01 01:00:00,1.0,GALLONS\n"
        )

        with pytest.raises(FlumeCliError, match="HR"):
            cli._reject_bucket_mismatch(existing, "MIN")


class TestRejectUnitsMismatch:
    def test_no_op_when_file_does_not_exist(self, tmp_path):
        cli._reject_units_mismatch(tmp_path / "missing.csv", "GALLONS")

    def test_no_op_when_file_is_header_only(self, tmp_path):
        existing = tmp_path / "report.csv"
        existing.write_text("device_id,datetime,value,units\n")

        cli._reject_units_mismatch(existing, "GALLONS")

    def test_no_op_when_units_match(self, tmp_path):
        existing = tmp_path / "report.csv"
        existing.write_text(
            "device_id,datetime,value,units\n"
            "dev-1,2026-09-01 00:00:00,1.0,GALLONS\n"
        )

        cli._reject_units_mismatch(existing, "GALLONS")

    def test_raises_when_units_differ(self, tmp_path):
        existing = tmp_path / "report.csv"
        existing.write_text(
            "device_id,datetime,value,units\n"
            "dev-1,2026-09-01 00:00:00,1.0,GALLONS\n"
        )

        with pytest.raises(FlumeCliError, match="GALLONS"):
            cli._reject_units_mismatch(existing, "LITERS")


class TestConfirmOutputOverwrite:
    def test_returns_true_when_file_does_not_exist(self, tmp_path):
        def fail_if_called(_msg):
            raise AssertionError("prompt should not be called when file does not exist")

        result = cli._confirm_output_overwrite(tmp_path / "missing.csv", prompt=fail_if_called)

        assert result is True

    @pytest.mark.parametrize("answer", ["y", "Y", "yes", "YES"])
    def test_returns_true_for_yes_answer(self, tmp_path, answer):
        existing = tmp_path / "report.csv"
        existing.write_text("")

        result = cli._confirm_output_overwrite(existing, prompt=lambda _msg: answer)

        assert result is True

    def test_returns_false_for_no_answer(self, tmp_path):
        existing = tmp_path / "report.csv"
        existing.write_text("")

        result = cli._confirm_output_overwrite(existing, prompt=lambda _msg: "n")

        assert result is False

    def test_returns_false_for_empty_answer(self, tmp_path):
        existing = tmp_path / "report.csv"
        existing.write_text("")

        result = cli._confirm_output_overwrite(existing, prompt=lambda _msg: "")

        assert result is False

    def test_prompt_message_includes_output_path(self, tmp_path):
        existing = tmp_path / "report.csv"
        existing.write_text("")
        messages = []

        def capture(msg):
            messages.append(msg)
            return "n"

        cli._confirm_output_overwrite(existing, prompt=capture)

        assert str(existing) in messages[0]


class TestMainAbortsOnDeclinedOverwrite:
    def test_declining_exits_0_without_any_api_calls(self, tmp_path, monkeypatch, capsys):
        output = tmp_path / "existing.csv"
        output.write_text("device_id,datetime,value,units\n")

        def fail_if_called(*args, **kwargs):
            raise AssertionError("API should not be called when overwrite is declined")

        monkeypatch.setattr(cli, "FlumeClient", fail_if_called)
        monkeypatch.setenv("FLUME_CLIENT_ID", "id")
        monkeypatch.setenv("FLUME_CLIENT_SECRET", "secret")
        monkeypatch.setenv("FLUME_USERNAME", "user@example.com")
        monkeypatch.setenv("FLUME_PASSWORD", "pw")
        monkeypatch.setattr("builtins.input", lambda _msg: "n")

        exit_code = cli.main(["day", "--output", str(output)])

        assert exit_code == 0
        assert "Kept existing" in capsys.readouterr().out


class TestMainRejectsBucketMismatchBeforePrompting:
    def test_mismatch_exits_1_without_prompting_or_any_api_calls(
        self, tmp_path, monkeypatch, capsys
    ):
        output = tmp_path / "existing.csv"
        output.write_text(
            "device_id,datetime,value,units\n"
            "dev-1,2026-09-01 00:00:00,1.0,GALLONS\n"
            "dev-1,2026-09-01 01:00:00,1.0,GALLONS\n"
        )

        def fail_if_called(*args, **kwargs):
            raise AssertionError("should not be called on bucket mismatch")

        monkeypatch.setattr(cli, "FlumeClient", fail_if_called)
        monkeypatch.setattr("builtins.input", fail_if_called)
        monkeypatch.setenv("FLUME_CLIENT_ID", "id")
        monkeypatch.setenv("FLUME_CLIENT_SECRET", "secret")
        monkeypatch.setenv("FLUME_USERNAME", "user@example.com")
        monkeypatch.setenv("FLUME_PASSWORD", "pw")

        exit_code = cli.main(["day", "--output", str(output), "--bucket", "MIN"])

        assert exit_code == 1
        assert "error:" in capsys.readouterr().err


class TestMainRejectsUnitsMismatchBeforePrompting:
    def test_mismatch_exits_1_without_prompting_or_any_api_calls(
        self, tmp_path, monkeypatch, capsys
    ):
        output = tmp_path / "existing.csv"
        output.write_text(
            "device_id,datetime,value,units\n"
            "dev-1,2026-09-01 00:00:00,1.0,GALLONS\n"
            "dev-1,2026-09-01 01:00:00,1.0,GALLONS\n"
        )

        def fail_if_called(*args, **kwargs):
            raise AssertionError("should not be called on units mismatch")

        monkeypatch.setattr(cli, "FlumeClient", fail_if_called)
        monkeypatch.setattr("builtins.input", fail_if_called)
        monkeypatch.setenv("FLUME_CLIENT_ID", "id")
        monkeypatch.setenv("FLUME_CLIENT_SECRET", "secret")
        monkeypatch.setenv("FLUME_USERNAME", "user@example.com")
        monkeypatch.setenv("FLUME_PASSWORD", "pw")

        exit_code = cli.main(
            ["day", "--output", str(output), "--bucket", "HR", "--units", "LITERS"]
        )

        assert exit_code == 1
        assert "error:" in capsys.readouterr().err


class TestMainMergesOnConfirmedOverwrite:
    def test_new_rows_are_merged_into_existing_rows_preserving_sort_order(
        self, tmp_path, monkeypatch
    ):
        output = tmp_path / "existing.csv"
        output.write_text(
            "device_id,datetime,value,units\n"
            "dev-1,2026-09-01 00:00:00,1.0,GALLONS\n"
            "dev-1,2026-09-01 01:00:00,1.0,GALLONS\n"
            "dev-1,2026-09-01 03:00:00,1.0,GALLONS\n"
        )

        class FakeClient:
            def __init__(self, *args, **kwargs):
                pass

            def set_token(self, token):
                pass

            def fetch_devices(self, user_id, type_=None):
                return [{"id": "dev-1"}]

            def query_device(self, user_id, device_id, *, since, until, bucket, units):
                return [{"datetime": "2026-09-01 02:00:00", "value": 9.0}]

        class FakeToken:
            access_token = "tok"
            user_id = "user-1"

        monkeypatch.setattr(cli, "FlumeClient", FakeClient)
        monkeypatch.setattr(cli.auth, "get_valid_token", lambda client, creds: FakeToken())
        monkeypatch.setenv("FLUME_CLIENT_ID", "id")
        monkeypatch.setenv("FLUME_CLIENT_SECRET", "secret")
        monkeypatch.setenv("FLUME_USERNAME", "user@example.com")
        monkeypatch.setenv("FLUME_PASSWORD", "pw")
        monkeypatch.setattr("builtins.input", lambda _msg: "y")

        exit_code = cli.main(["day", "--output", str(output), "--bucket", "HR"])

        assert exit_code == 0
        with open(output, newline="") as f:
            written = list(csv.DictReader(f))
        assert [row["datetime"] for row in written] == [
            "2026-09-01 00:00:00", "2026-09-01 01:00:00",
            "2026-09-01 02:00:00", "2026-09-01 03:00:00",
        ]
