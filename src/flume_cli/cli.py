import argparse
import sys

from flume_cli import auth, report
from flume_cli.client import FlumeClient
from flume_cli.config import (
    DEFAULT_BUCKET,
    DEFAULT_DAYS,
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
        help="Fetch a rolling window of the last N days of usage.",
    )
    day_parser.add_argument(
        "--days", type=int, default=DEFAULT_DAYS,
        help=f"Number of trailing days of usage to fetch (default: {DEFAULT_DAYS})",
    )

    subparsers.add_parser(
        "month", parents=[common],
        help="Fetch usage for the last full calendar month.",
    )

    return parser


def main(argv=None):
    load_dotenv_if_present()
    args = build_parser().parse_args(argv)

    try:
        creds = Credentials.from_env()
    except ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    try:
        client = FlumeClient()
        token = auth.get_valid_token(client, creds)
        client.set_token(token.access_token)

        devices = client.fetch_devices(token.user_id, type_=DEFAULT_DEVICE_TYPE)
        device_ids = report.select_device_ids(devices, args.device_ids)

        if args.command == "day":
            windows = report.daily_windows(args.days)
        else:
            windows = report.month_windows()

        rows = report.build_report_rows(
            client, token.user_id, device_ids,
            windows=windows, bucket=args.bucket, units=args.units,
        )
        count = report.write_csv(rows, args.output)
    except FlumeCliError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"Wrote {count} rows to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
