import argparse
import sys

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


def build_parser():
    parser = argparse.ArgumentParser(
        prog="flume-report",
        description="Fetch Flume water usage and write it to a CSV file.",
    )
    parser.add_argument(
        "--output", default=DEFAULT_OUTPUT,
        help=f"CSV output path (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--days", type=int, default=None,
        help=(
            "Number of trailing days of usage to fetch. Defaults to the last full "
            "calendar month when omitted."
        ),
    )
    parser.add_argument(
        "--bucket", default=DEFAULT_BUCKET,
        choices=["MIN", "HR", "DAY", "MON", "YR"],
        help=f"Bucket interval for usage values (default: {DEFAULT_BUCKET})",
    )
    parser.add_argument(
        "--device-id", action="append", default=None, dest="device_ids",
        help="Limit the report to this device id (repeatable). Defaults to all water sensors.",
    )
    parser.add_argument(
        "--units", default=DEFAULT_UNITS,
        choices=["GALLONS", "LITERS", "CUBIC_FEET", "CUBIC_METERS"],
        help=f"Unit of measurement for usage values (default: {DEFAULT_UNITS})",
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

        rows = report.build_report_rows(
            client, token.user_id, device_ids,
            days=args.days, bucket=args.bucket, units=args.units,
        )
        count = report.write_csv(rows, args.output)
    except FlumeCliError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"Wrote {count} rows to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
