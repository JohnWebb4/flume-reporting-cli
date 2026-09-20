# flume-reporting-cli

CLI wrapper for the [Flume](https://flumewater.com) Water API that fetches a water sensor's
usage for a given day range or the last full calendar month and writes it to a CSV file.

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

- `flume-report day` — a rolling window of the last N days of usage, ending now.
- `flume-report month` — the last full calendar month of usage.

Both write usage at 1-minute granularity (in gallons) for every water sensor on the account to
`flume_report.csv` in the current directory, unless overridden by the flags below.

Shared flags (available on both `day` and `month`):

| Flag | Default | Description |
|---|---|---|
| `--output PATH` | `flume_report.csv` | Where to write the CSV |
| `--bucket BUCKET` | `MIN` | `MIN`, `HR`, `DAY`, `MON`, or `YR` |
| `--device-id ID` | all sensors | Limit the report to one device (repeatable) |
| `--units UNIT` | `GALLONS` | `GALLONS`, `LITERS`, `CUBIC_FEET`, or `CUBIC_METERS` |

`day`-only flag:

| Flag | Default | Description |
|---|---|---|
| `--days N` | `7` | Number of trailing days of usage to fetch |

Example: last 3 days of hourly usage for a specific device, in liters:

```bash
flume-report day --days 3 --bucket HR --device-id 6721255604737738501 --units LITERS --output usage.csv
```

Example: last full calendar month for every sensor, at the default `MIN` bucket:

```bash
flume-report month
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
  ~28-31 requests per device; `day --days N` → N requests per device) to stay well under any
  undocumented per-request range limits. At the default `MIN` bucket this means up to 1440 rows
  per request (vs. 24/day previously at `HR`) — day-sized chunking was chosen defensively for
  `HR` and hasn't been independently verified as safe at `MIN` against an undocumented
  row/range limit, so watch for errors or truncated results on large accounts.
- **Rate limiting**: Flume enforces a 120 requests/hour limit per account. With `month`'s
  default `MIN`-bucket paging above, an account with several devices can hit this in a single
  run. Hitting it produces a clear `error: Flume API rate limit reached (429): ...` message and
  the CLI exits (code 1) without retrying — wait for the limit to reset (up to an hour) and
  re-run, or narrow the request with `day --days N`/`--device-id` to use fewer requests.
- **Network errors**: requests time out after 30s, and connection failures (DNS, refused
  connections, timeouts) are caught and reported as a clean `error: ...` message rather than a
  raw Python traceback.

## Troubleshooting

- `invalid_client`: your `FLUME_CLIENT_ID`/`FLUME_CLIENT_SECRET` are wrong.
- `unverified_user`: the Flume account hasn't finished email verification/signup.
- Missing env var errors: the CLI lists exactly which `FLUME_*` variables aren't set.
