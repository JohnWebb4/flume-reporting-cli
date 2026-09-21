import csv
import os
from datetime import datetime, timedelta

from flume_cli.errors import FlumeCliError

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
CSV_FIELDNAMES = ["device_id", "datetime", "value", "units"]


def day_windows(reference=None, *, year=None, month=None, day=None):
    """Single-day window, returned as a one-item list for build_report_rows' windows=.

    With no arguments, covers yesterday relative to `reference` (or now, if
    `reference` is omitted) -- e.g. run on Sep 20, this covers
    Sep 19 00:00:00 -> Sep 20 00:00:00.

    With `year`/`month`/`day` given (all required together -- see cli.py for
    that validation), covers that exact calendar day instead.

    Flume's since/until_datetime examples carry no timezone info, so these are
    naive local timestamps (assumed to match the account's local timezone).
    """
    if year is not None and month is not None and day is not None:
        start_of_day = datetime(year, month, day)  # noqa: DTZ001 -- naive local time is intentional, see docstring
    else:
        reference = reference or datetime.now()  # noqa: DTZ005 -- naive local time is intentional, see docstring
        start_of_today = reference.replace(hour=0, minute=0, second=0, microsecond=0)
        start_of_day = start_of_today - timedelta(days=1)

    end_of_day = start_of_day + timedelta(days=1)
    return [(start_of_day.strftime(DATETIME_FORMAT), end_of_day.strftime(DATETIME_FORMAT))]

def month_windows(reference=None, *, year=None, month=None):
    """Daily windows covering a calendar month, oldest first.

    With no arguments, covers the last full calendar month relative to
    `reference` (or now, if `reference` is omitted) -- e.g. run in September,
    this covers Aug 1 00:00:00 -> Sep 1 00:00:00.

    With `year`/`month` given (both required together -- see cli.py for that
    validation), covers that exact calendar month instead.

    Either way, the month is chunked into one request per day (see
    day_windows for why: no documented per-request row/range limit on the
    query endpoint).
    """
    if year is not None and month is not None:
        start_of_target_month = datetime(year, month, 1)  # noqa: DTZ001 -- naive local time is intentional, see docstring
    else:
        reference = reference or datetime.now()  # noqa: DTZ005 -- naive local time is intentional, see docstring
        start_of_this_month = reference.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        if start_of_this_month.month == 1:
            start_of_target_month = start_of_this_month.replace(
                year=start_of_this_month.year - 1, month=12
            )
        else:
            start_of_target_month = start_of_this_month.replace(
                month=start_of_this_month.month - 1
            )

    if start_of_target_month.month == 12:
        start_of_next_month = start_of_target_month.replace(
            year=start_of_target_month.year + 1, month=1
        )
    else:
        start_of_next_month = start_of_target_month.replace(
            month=start_of_target_month.month + 1
        )

    windows = []
    day_start = start_of_target_month
    while day_start < start_of_next_month:
        day_end = min(day_start + timedelta(days=1), start_of_next_month)
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
            f"Requested device id(s) not found for this account: {', '.join(unknown)}. "
            "Run a report with no --device-id to see valid ids in the output CSV's "
            "device_id column."
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


_BUCKET_INTERVAL_SECONDS = {
    "MIN": 60,
    "HR": 3600,
    "DAY": 86400,
    "MON": 30 * 86400,
    "YR": 365 * 86400,
}


def read_csv_rows(output_path):
    """Read an existing report CSV into a list of row dicts.

    Returns [] if the file doesn't exist -- including header-only files,
    which naturally produce no data rows once opened. Any other read
    failure (permissions, garbled file, etc.) propagates; callers that want
    a forgiving, non-blocking read (like infer_bucket_from_csv) should catch
    around their own call instead of relying on this to swallow errors.
    """
    if not os.path.exists(output_path):
        return []
    with open(output_path, newline="") as f:
        return list(csv.DictReader(f))


def infer_bucket_from_csv(output_path):
    """Best-effort guess at the --bucket used to write an existing report CSV.

    The CSV has no bucket column, so this compares the datetime gap between
    the first two consecutive rows for the same device against each known
    bucket's typical interval. Returns the closest matching bucket, or None
    if there isn't enough data to tell (missing/empty file, a single row, or
    a gap that doesn't clearly match any bucket) -- callers should treat
    None as "can't tell, don't block".
    """
    try:
        rows = read_csv_rows(output_path)
        first = rows[0] if rows else None
        if first is None:
            return None
        second = next(
            (row for row in rows[1:] if row.get("device_id") == first.get("device_id")), None
        )
        if second is None:
            return None
        first_dt = datetime.strptime(first["datetime"], DATETIME_FORMAT)  # noqa: DTZ007 -- naive local time is intentional, matches write_csv's own format
        second_dt = datetime.strptime(second["datetime"], DATETIME_FORMAT)  # noqa: DTZ007
    except (OSError, csv.Error, KeyError, ValueError):
        return None

    gap_seconds = abs((second_dt - first_dt).total_seconds())
    if gap_seconds == 0:
        return None

    closest_bucket = min(
        _BUCKET_INTERVAL_SECONDS,
        key=lambda bucket: abs(_BUCKET_INTERVAL_SECONDS[bucket] - gap_seconds),
    )
    expected_seconds = _BUCKET_INTERVAL_SECONDS[closest_bucket]
    if abs(expected_seconds - gap_seconds) > expected_seconds * 0.1:
        return None
    return closest_bucket


def _index_row(by_device, device_order, row):
    device_id = row["device_id"]
    if device_id not in by_device:
        by_device[device_id] = {}
        device_order.append(device_id)
    by_device[device_id][row["datetime"]] = row


def merge_rows(existing_rows, new_rows):
    """Merge freshly fetched rows into an existing report's rows.

    Grouped by device (existing devices first, then any new ones, in
    first-seen order); within a device, a new row overwrites an existing row
    sharing the same datetime, and each device's rows are re-sorted
    ascending by datetime -- so new readings land in their correct
    chronological position rather than being appended to the end.
    """
    by_device = {}
    device_order = []
    for row in existing_rows:
        _index_row(by_device, device_order, row)
    for row in new_rows:
        _index_row(by_device, device_order, row)

    merged = []
    for device_id in device_order:
        try:
            sorted_datetimes = sorted(
                by_device[device_id],
                key=lambda dt: datetime.strptime(dt, DATETIME_FORMAT),  # noqa: DTZ007 -- naive local time is intentional, matches write_csv's own format
            )
        except ValueError as exc:
            raise FlumeCliError(
                f"Cannot merge: found a datetime that doesn't match the expected format "
                f"{DATETIME_FORMAT!r} for device {device_id} ({exc})."
            ) from exc
        for dt in sorted_datetimes:
            merged.append(by_device[device_id][dt])
    return merged


def write_csv(rows, output_path):
    count = 0
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
            count += 1
    return count
