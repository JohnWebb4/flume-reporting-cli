from datetime import datetime

import pytest

from flume_cli import cli
from flume_cli.errors import ConfigError


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
