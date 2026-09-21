# flume-reporting-cli

CLI wrapper for the [Flume](https://flumewater.com) Water API that fetches a water sensor's
usage for a specific day (yesterday by default, or any past day you specify) or a calendar
month (the last full month by default, or any past month you specify) and writes it to a CSV
file.

## Prerequisites

- Python 3.9+
- A Flume account with at least one connected water sensor
- API credentials generated from the Flume Customer Portal (see below)

## Obtaining API credentials

1. Log in to the [Flume Customer Portal](https://portal.flumetech.com).
2. Go to **Settings**, scroll to the bottom, and click **Generate API Client**.
3. Note the `client_id` and `client_secret` shown — you'll need them below, along with the
   email/password you use to log in to Flume.

See [`docs/accessing-the-api.md`](docs/accessing-the-api.md) for more detail.

## Installation

```bash
pip install .
```

This installs a `flume-report` console command (`python -m flume_cli` also works).

## Configuration

The CLI reads credentials from environment variables:

| Variable | Description |
|---|---|
| `FLUME_CLIENT_ID` | API client ID from the Customer Portal |
| `FLUME_CLIENT_SECRET` | API client secret from the Customer Portal |
| `FLUME_USERNAME` | Email address you log in to Flume with |
| `FLUME_PASSWORD` | Flume account password |

You can either export these in your shell, or create a `.env` file in the working directory
(already covered by `.gitignore` — never commit it):

```
FLUME_CLIENT_ID=...
FLUME_CLIENT_SECRET=...
FLUME_USERNAME=you@example.com
FLUME_PASSWORD=...
```

## Usage

The CLI requires one of two subcommands:

- `flume-report day` — yesterday's usage (midnight-to-midnight), or a specific past day via
  `--day`/`--month`/`--year`.
- `flume-report month` — the last full calendar month of usage, or a specific past month via
  `--month`/`--year`.

Both write usage at 1-minute granularity (in gallons) for every water sensor on the account to
`flume_report.csv` in the current directory, unless overridden by the flags below.

If `--output` already points at a file that exists, `flume-report` first checks that file's bucket
(inferred from the gap between existing rows) and its `units` column against the requested `--bucket`
and `--units`, and errors out (exit 1, no API calls) if either doesn't match. If both match (or the
existing bucket can't be determined), it then asks for confirmation before merging (`y`/`N`,
defaulting to no). Answering no exits cleanly (code 0) without writing or making any API calls.
Answering yes **merges** the freshly fetched rows into the existing file rather than replacing it —
a new reading is inserted in its correct chronological position (and overwrites any existing reading
for the same device and timestamp), instead of being appended to the end.

Shared flags (available on both `day` and `month`):

| Flag | Default | Description |
|---|---|---|
| `--output PATH` | `flume_report.csv` | Where to write the CSV |
| `--bucket BUCKET` | `MIN` | `MIN`, `HR`, `DAY`, `MON`, or `YR` |
| `--device-id ID` | all sensors | Limit the report to one device (repeatable) |
| `--units UNIT` | `GALLONS` | `GALLONS`, `LITERS`, `CUBIC_FEET`, or `CUBIC_METERS` |

`day`-only flags (must be used together):

| Flag | Default | Description |
|---|---|---|
| `--day N` | yesterday | Day of month to fetch (1-31) |
| `--month N` | yesterday | Month to fetch (1-12) |
| `--year YYYY` | yesterday | Year to fetch, e.g. `2025` |

`month`-only flags (must be used together):

| Flag | Default | Description |
|---|---|---|
| `--month N` | last full month | Month to fetch (1-12) |
| `--year YYYY` | last full month | Year to fetch, e.g. `2025` |

Example: yesterday's hourly usage for a specific device, in liters:

```bash
flume-report day --bucket HR --device-id 6721255604737738501 --units LITERS --output usage.csv
```

Example: a specific past day (March 15, 2025) for every sensor:

```bash
flume-report day --day 15 --month 3 --year 2025
```

Example: last full calendar month for every sensor, at the default `MIN` bucket:

```bash
flume-report month
```

Example: a specific past month (March 2025) for every sensor:

```bash
flume-report month --month 3 --year 2025
```

The output CSV has one row per reading at the requested bucket interval (1-minute rows by
default):

```
device_id,datetime,value,units
6721255604737738501,2026-09-11 12:01:00,0.1,GALLONS
...
```

## Token caching

Access and refresh tokens are cached in `~/.flume/token.json` so the CLI doesn't have to log
in with your password on every run — it reuses the cached token until it's close to expiring,
then refreshes it automatically. Delete this file to force a fresh login.

## Known limitations / assumptions

- **Timezone**: the Flume API's `since_datetime`/`until_datetime` query fields are undocumented
  with respect to timezone. This CLI sends naive local timestamps (your machine's local time),
  matching Flume's account/location-based dashboard. If your reports look off by a fixed number
  of hours, this is the first thing to check.
- **Bucket interval**: `--bucket` selects one of Flume's documented bucket values
  (`MIN`/`HR`/`DAY`/`MON`/`YR`), defaulting to `MIN`. This isn't shown explicitly in the
  reference docs in `docs/`, so verify against a live response if usage looks wrong.
- **Paging strategy**: the usage query endpoint doesn't document a `limit`/`offset` style of
  pagination, so this CLI pages by issuing one query per calendar day instead (`month` →
  ~28-31 requests per device; `day` → 1 request per device, since it's always a single calendar
  day) to stay well under any undocumented per-request range limits. At the default `MIN`
  bucket this means up to 1440 rows per request (vs. 24/day previously at `HR`) — day-sized
  chunking was chosen defensively for `HR` and hasn't been independently verified as safe at
  `MIN` against an undocumented row/range limit, so watch for errors or truncated results on
  large accounts. This applies the same way whether `month` fetches the default last-full-month
  or an explicit `--month`/`--year`.
- **Month range**: `flume-report month --month N --year Y` only accepts a month strictly before
  the current one — it's rejected up front with a clear error rather than silently returning an
  empty or partial report, since "month" is meant to always be a *full* calendar month.
- **Day range**: `flume-report day --day D --month M --year Y` only accepts a day strictly
  before today — it's rejected up front with a clear error rather than silently returning an
  empty or partial report.
- **Merge confirmation**: if `--output` points at an existing file, the CLI prompts for
  `y`/`N` confirmation before merging (checked before any API calls, so declining costs no
  rate-limited requests). There's currently no flag to skip the prompt (e.g. for scripting/cron
  use) — declining just exits 0 without changing the file.
- **Bucket mismatch on merge**: since the CSV doesn't store which `--bucket` it was written
  with, the existing file's bucket is *inferred* from the time gap between its first two rows for
  a device (e.g. ~60s apart → `MIN`, ~1hr → `HR`). This is a heuristic, not a stored fact — a
  sparse or edited file can produce a wrong or undetectable guess. A confident mismatch errors out
  (exit 1) before the merge prompt; an undetermined bucket is treated as compatible and falls
  through to the normal prompt.
- **Units mismatch on merge**: unlike bucket, `units` is a real column in the CSV, so this
  check is exact rather than inferred — if the existing file's `units` differ from the requested
  `--units`, the CLI errors out (exit 1) before the merge prompt rather than mixing unit
  systems in one file.
- **Merging on confirmation**: answering `y` to the merge prompt merges the freshly
  fetched rows into the existing file instead of replacing it. Rows are grouped by device and
  sorted ascending by datetime; a fetched row overwrites an existing row sharing the same device
  and datetime, and devices present in the existing file but not covered by this run are left
  untouched. There's no way to instead force a full replace of an existing file's contents (short
  of deleting it first).
- **Rate limiting**: Flume enforces a 120 requests/hour limit per account. With `month`'s
  default `MIN`-bucket paging above, an account with several devices can hit this in a single
  run. Hitting it produces a clear `error: Flume API rate limit reached (429): ...` message and
  the CLI exits (code 1) without retrying — wait for the limit to reset (up to an hour) and
  re-run, or narrow the request with `--device-id` to use fewer requests.
- **Network errors**: requests time out after 30s, and connection failures (DNS, refused
  connections, timeouts) are caught and reported as a clean `error: ...` message rather than a
  raw Python traceback.

## Development

Dev dependencies ([ruff](https://docs.astral.sh/ruff/) for linting, [pytest](https://pytest.org)
for tests) are managed with [`uv`](https://docs.astral.sh/uv/) via a `dev` dependency group in
`pyproject.toml`:

```bash
uv sync                    # installs runtime + dev dependencies into .venv
uv run ruff check .        # lint
uv run pytest              # run tests
```

## Troubleshooting

- `invalid_client`: your `FLUME_CLIENT_ID`/`FLUME_CLIENT_SECRET` are wrong.
- `unverified_user`: the Flume account hasn't finished email verification/signup.
- Missing env var errors: the CLI lists exactly which `FLUME_*` variables aren't set.
