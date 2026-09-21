import csv
from datetime import datetime, timedelta

from flume_cli.errors import FlumeCliError

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
CSV_FIELDNAMES = ["device_id", "datetime", "value", "units"]


def daily_windows(days, end=None):
    """Rolling 24h windows covering the last `days` days, oldest first.

    Flume's since/until_datetime examples carry no timezone info, so these are
    naive local timestamps (assumed to match the account's local timezone).
    """
    end = end or datetime.now()  # noqa: DTZ005 -- naive local time is intentional, see docstring
    windows = []
    for day_offset in range(days, 0, -1):
        since = end - timedelta(days=day_offset)
        until = end - timedelta(days=day_offset - 1)
        windows.append((since.strftime(DATETIME_FORMAT), until.strftime(DATETIME_FORMAT)))
    return windows

def month_windows(reference=None):
    """Daily windows covering the last full calendar month, oldest first.

    e.g. run in September, this covers Aug 1 00:00:00 -> Sep 1 00:00:00,
    chunked into one request per day (see daily_windows for why: no
    documented per-request row/range limit on the query endpoint).
    """
    reference = reference or datetime.now()  # noqa: DTZ005 -- naive local time is intentional, see docstring
    start_of_this_month = reference.replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )
    if start_of_this_month.month == 1:
        start_of_last_month = start_of_this_month.replace(
            year=start_of_this_month.year - 1, month=12
        )
    else:
        start_of_last_month = start_of_this_month.replace(
            month=start_of_this_month.month - 1
        )

    windows = []
    day_start = start_of_last_month
    while day_start < start_of_this_month:
        day_end = min(day_start + timedelta(days=1), start_of_this_month)
        windows.append((day_start.strftime(DATETIME_FORMAT), day_end.strftime(DATETIME_FORMAT)))
        day_start = day_end
    return windows


def select_device_ids(devices, requested_ids):
    if not requested_ids:
        return [device["id"] for device in devices]

    available = {device["id"] for device in devices}
    unknown = [device_id for device_id in requested_ids if device_id not in available]
    if unknown:
        raise FlumeCliError(
            f"Requested device id(s) not found for this account: {', '.join(unknown)}"
        )
    return list(requested_ids)


def build_report_rows(client, user_id, device_ids, *, windows, bucket, units):
    for device_id in device_ids:
        for since, until in windows:
            readings = client.query_device(
                user_id, device_id, since=since, until=until, bucket=bucket, units=units
            )
            for reading in readings:
                yield {
                    "device_id": device_id,
                    "datetime": reading["datetime"],
                    "value": reading["value"],
                    "units": units,
                }


def write_csv(rows, output_path):
    count = 0
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
            count += 1
    return count
