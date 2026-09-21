import argparse
import os
import sys
from datetime import datetime

from flume_cli import auth, report
from flume_cli.client import FlumeClient
from flume_cli.config import (
    DEFAULT_BUCKET,
    DEFAULT_DEVICE_TYPE,
    DEFAULT_OUTPUT,
    DEFAULT_UNITS,
    Credentials,
    load_dotenv_if_present,
)
from flume_cli.errors import ConfigError, FlumeCliError


def _build_common_parser():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--output", default=DEFAULT_OUTPUT,
        help=f"CSV output path (default: {DEFAULT_OUTPUT})",
    )
    common.add_argument(
        "--bucket", default=DEFAULT_BUCKET,
        choices=["MIN", "HR", "DAY", "MON", "YR"],
        help=f"Bucket interval for usage values (default: {DEFAULT_BUCKET})",
    )
    common.add_argument(
        "--device-id", action="append", default=None, dest="device_ids",
        help="Limit the report to this device id (repeatable). Defaults to all water sensors.",
    )
    common.add_argument(
        "--units", default=DEFAULT_UNITS,
        choices=["GALLONS", "LITERS", "CUBIC_FEET", "CUBIC_METERS"],
        help=f"Unit of measurement for usage values (default: {DEFAULT_UNITS})",
    )
    return common


def build_parser():
    parser = argparse.ArgumentParser(
        prog="flume-report",
        description="Fetch Flume water usage and write it to a CSV file.",
    )
    common = _build_common_parser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    day_parser = subparsers.add_parser(
        "day", parents=[common],
        help="Fetch usage for yesterday, or a specific past day with --day/--month/--year.",
    )
    day_parser.add_argument(
        "--day", type=int, default=None, metavar="1-31",
        help="Day of month to fetch (1-31). Must be used together with --month and --year. "
             "Defaults to yesterday.",
    )
    day_parser.add_argument(
        "--month", type=int, default=None, choices=range(1, 13), metavar="1-12",
        help="Month to fetch (1-12). Must be used together with --day and --year. "
             "Defaults to yesterday.",
    )
    day_parser.add_argument(
        "--year", type=int, default=None, metavar="YYYY",
        help="Year to fetch, e.g. 2025. Must be used together with --day and --month. "
             "Defaults to yesterday.",
    )

    month_parser = subparsers.add_parser(
        "month", parents=[common],
        help="Fetch usage for the last full calendar month, or a specific month with --month/--year.",
    )
    month_parser.add_argument(
        "--month", type=int, default=None, choices=range(1, 13), metavar="1-12",
        help="Month to fetch (1-12). Must be used together with --year. "
             "Defaults to the last full calendar month.",
    )
    month_parser.add_argument(
        "--year", type=int, default=None, metavar="YYYY",
        help="Year to fetch, e.g. 2025. Must be used together with --month. "
             "Defaults to the last full calendar month.",
    )

    return parser


def _reject_current_or_future_month(year, month, now=None):
    now = now or datetime.now()  # noqa: DTZ005 -- naive local time is intentional, matches report.py
    if (year, month) >= (now.year, now.month):
        raise ConfigError(
            f"Cannot fetch usage for {year:04d}-{month:02d}: that month is still in "
            "progress or hasn't started yet. Pass a month before the current one."
        )


def _reject_today_or_future_day(year, month, day, now=None):
    now = now or datetime.now()  # noqa: DTZ005 -- naive local time is intentional, matches report.py
    if (year, month, day) >= (now.year, now.month, now.day):
        raise ConfigError(
            f"Cannot fetch usage for {year:04d}-{month:02d}-{day:02d}: that day hasn't "
            "finished yet or hasn't happened yet. Pass a day before today."
        )


def _reject_bucket_mismatch(output_path, requested_bucket):
    if not os.path.exists(output_path):
        return
    existing_bucket = report.infer_bucket_from_csv(output_path)
    if existing_bucket is not None and existing_bucket != requested_bucket:
        raise FlumeCliError(
            f"{output_path} appears to have been written with bucket {existing_bucket}, "
            f"but this run requested bucket {requested_bucket}. Refusing to overwrite a "
            f"differently bucketed report; use --bucket {existing_bucket} or a different "
            "--output."
        )


def _reject_units_mismatch(output_path, requested_units):
    if not os.path.exists(output_path):
        return
    existing_rows = report.read_csv_rows(output_path)
    if not existing_rows:
        return
    existing_units = existing_rows[0].get("units")
    if existing_units and existing_units != requested_units:
        raise FlumeCliError(
            f"{output_path} appears to have been written with units {existing_units}, "
            f"but this run requested units {requested_units}. Refusing to overwrite a "
            f"report using different units; use --units {existing_units} or a different "
            "--output."
        )


def _confirm_output_overwrite(output_path, *, prompt=None):
    if not os.path.exists(output_path):
        return True
    prompt = prompt or input
    answer = prompt(f"{output_path} already exists. Overwrite? [y/N]: ")
    return answer.strip().lower() in ("y", "yes")


def main(argv=None):
    load_dotenv_if_present()
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "month" and (args.month is None) != (args.year is None):
        parser.error("--month and --year must be provided together")

    if args.command == "day":
        day_flags_given = [args.day is not None, args.month is not None, args.year is not None]
        if any(day_flags_given) and not all(day_flags_given):
            parser.error("--day, --month, and --year must be provided together")

    try:
        creds = Credentials.from_env()
    except ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    try:
        if args.command == "day" and args.day is not None:
            _reject_today_or_future_day(args.year, args.month, args.day)
        elif args.command == "month" and args.month is not None:
            _reject_current_or_future_month(args.year, args.month)

        _reject_bucket_mismatch(args.output, args.bucket)
        _reject_units_mismatch(args.output, args.units)

        if not _confirm_output_overwrite(args.output):
            print(f"Kept existing {args.output}; nothing written.")
            return 0

        client = FlumeClient()
        token = auth.get_valid_token(client, creds)
        client.set_token(token.access_token)

        devices = client.fetch_devices(token.user_id, type_=DEFAULT_DEVICE_TYPE)
        device_ids = report.select_device_ids(devices, args.device_ids)

        if args.command == "day":
            if args.day is not None:
                windows = report.day_windows(year=args.year, month=args.month, day=args.day)
            else:
                windows = report.day_windows()
        elif args.month is not None:
            windows = report.month_windows(year=args.year, month=args.month)
        else:
            windows = report.month_windows()

        rows = report.build_report_rows(
            client, token.user_id, device_ids,
            windows=windows, bucket=args.bucket, units=args.units,
        )
        if os.path.exists(args.output):
            rows = report.merge_rows(report.read_csv_rows(args.output), rows)
        count = report.write_csv(rows, args.output)
    except FlumeCliError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"Wrote {count} rows to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
