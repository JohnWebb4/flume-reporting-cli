# flume-reporting-cli

CLI wrapper for the [Flume](https://flumewater.com) Water API that fetches a water sensor's
hourly usage for the last week and writes it to a CSV file.

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

```bash
flume-report
```

By default this fetches the last 7 days of hourly usage (in gallons) for every water sensor
on the account and writes it to `flume_report.csv` in the current directory.

| Flag | Default | Description |
|---|---|---|
| `--output PATH` | `flume_report.csv` | Where to write the CSV |
| `--days N` | `7` | Number of trailing days of hourly usage to fetch |
| `--device-id ID` | all sensors | Limit the report to one device (repeatable) |
| `--units UNIT` | `GALLONS` | `GALLONS`, `LITERS`, `CUBIC_FEET`, or `CUBIC_METERS` |

Example: last 3 days for a specific device, in liters:

```bash
flume-report --days 3 --device-id 6721255604737738501 --units LITERS --output usage.csv
```

The output CSV has one row per hourly reading:

```
device_id,datetime,value,units
6721255604737738501,2026-09-11 12:00:00,1.5,GALLONS
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
- **Hourly bucket**: hourly queries use `bucket="HR"`, based on Flume's documented bucket
  vocabulary (`MIN`/`HR`/`DAY`/`MON`/`YR`). This isn't shown explicitly in the reference docs in
  `docs/`, so verify against a live response if usage looks wrong.
- **Paging strategy**: the usage query endpoint doesn't document a `limit`/`offset` style of
  pagination, so this CLI pages by issuing one hourly-bucket query per calendar day instead
  (`--days 7` → 7 requests per device) to stay well under any undocumented per-request range
  limits.

## Troubleshooting

- `invalid_client`: your `FLUME_CLIENT_ID`/`FLUME_CLIENT_SECRET` are wrong.
- `unverified_user`: the Flume account hasn't finished email verification/signup.
- Missing env var errors: the CLI lists exactly which `FLUME_*` variables aren't set.
