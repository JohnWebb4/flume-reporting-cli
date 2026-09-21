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

    def test_day_subcommand_rejects_month_flag(self):
        with pytest.raises(SystemExit) as exc_info:
            cli.build_parser().parse_args(["day", "--month", "3"])

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
