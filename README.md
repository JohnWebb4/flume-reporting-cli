# flume-reporting-cli

w`flume-report` is a command-line tool that fetches historical water usage from your
[Flume](https://flumewater.com) water sensor(s) and writes it to a CSV file — one you can open
in Excel, Numbers, Google Sheets, or any spreadsheet app.

It fetches either:

- a **day** of usage — yesterday by default, or any specific past day, or
- a **month** of usage — the last full calendar month by default, or any specific past month.

No server, no database, no Flume account changes — it just reads usage data and writes a file.

## Contents

- [Prerequisites](#prerequisites)
- [1. Get Flume API credentials](#1-get-flume-api-credentials)
- [2. Install flume-report](#2-install-flume-report)
- [3. Set your credentials](#3-set-your-credentials)
- [4. Run it](#4-run-it)
- [Command reference](#command-reference)
- [More examples](#more-examples)
- [Understanding the output CSV](#understanding-the-output-csv)
- [Updating a report you already have](#updating-a-report-you-already-have)
- [Token caching](#token-caching)
- [Troubleshooting](#troubleshooting)
- [Known limitations](#known-limitations)
- [Development](#development)

## Prerequisites

- **Python 3.9 or newer.**
- A Flume account with at least one connected water sensor.
- API credentials from the Flume Customer Portal — see the next section.

## 1. Get Flume API credentials

`flume-report` talks to Flume on your behalf, so it needs its own API client ID/secret, plus
your normal Flume login:

1. Log in to the [Flume Customer Portal](https://portal.flumetech.com).
2. Go to **Settings**, scroll to the bottom, and click **Generate API Client**.
3. Note the `client_id` and `client_secret` shown — you'll need them below, along with the
   email/password you use to log in to Flume.

(More detail, straight from Flume, in [`docs/accessing-the-api.md`](docs/accessing-the-api.md).)

## 2. Install flume-report

From inside this project's folder, run:

```bash
pip install .
```

This installs a `flume-report` command (`python -m flume_cli` also works, if `flume-report`
isn't found on your PATH for some reason).

If your system's `pip` refuses a global install (you may see an `externally-managed-environment`
error — common on newer macOS/Linux setups), the cleanest fix is
[`pipx`](https://pipx.pypa.io/), which installs command-line tools like this one into their own
isolated environment automatically:

```bash
pipx install .
```

Either way, confirm it worked:

```bash
flume-report --help
```

You should see a usage message listing the `day` and `month` subcommands. (That `--help` flag
works on every subcommand too — `flume-report day --help` and `flume-report month --help` print
the full, always-current list of flags for each. If anything below ever looks out of date, that's
the tiebreaker.)

## 3. Set your credentials

`flume-report` reads four environment variables:

| Variable | Description |
|---|---|
| `FLUME_CLIENT_ID` | API client ID from the Customer Portal |
| `FLUME_CLIENT_SECRET` | API client secret from the Customer Portal |
| `FLUME_USERNAME` | Email address you log in to Flume with |
| `FLUME_PASSWORD` | Flume account password |

The easiest way to set these: create a file named `.env` in the folder you'll run
`flume-report` from (copy [`.env.example`](.env.example) as a starting point):

```
FLUME_CLIENT_ID=...
FLUME_CLIENT_SECRET=...
FLUME_USERNAME=you@example.com
FLUME_PASSWORD=...
```

`flume-report` picks this file up automatically — no need to source it or export anything.
**Never commit or share this file** — it has your password in it (it's already listed in
`.gitignore` if you're working from a clone of this repo).

Alternatively, you can export the same four variables in your shell instead of using a file.

## 4. Run it

```bash
flume-report day
```

This fetches yesterday's usage (midnight to midnight, 1-minute readings, in gallons)
for every water sensor on your account, and writes it to `flume_report.csv` in your current
folder. Open that file in Excel/Numbers/Sheets and you'll see one row per reading.

Everything past this point is about customizing *what* gets fetched and *how* it's saved.

## Command reference

There's day and month subcommads. Both accept the same shared flags below, plus their own
date-selection flags.

| Subcommand | Fetches | Defaults to |
|---|---|---|
| `flume-report day` | usage for one calendar day | yesterday |
| `flume-report month` | usage for one calendar month | the last full calendar month |

### Shared flags (both `day` and `month`)

| Flag | Default | Description |
|---|---|---|
| `--output PATH` | `flume_report.csv` | Where to write the CSV |
| `--bucket BUCKET` | `MIN` | How finely to group readings — see table below |
| `--device-id ID` | all sensors | Limit the report to one sensor (repeat the flag to name several) |
| `--units UNIT` | `GALLONS` | `GALLONS`, `LITERS`, `CUBIC_FEET`, or `CUBIC_METERS` |

**`--bucket`** controls how many rows you get and how granular they are:

| Bucket | One row per... |
|---|---|
| `MIN` (default) | minute — the most detail, and the biggest file |
| `HR` | hour |
| `DAY` | calendar day |
| `MON` | calendar month |
| `YR` | year |

**`--device-id`**: don't know your sensor's ID? Run `flume-report day` (or `month`) once with
no `--device-id` at all. It fetches every sensor on the account, and the `device_id` column in
the resulting CSV shows each one's ID. Copy the one you want, then pass it on future runs:
`--device-id 6721255604737738501`. Repeat the flag to select more than one sensor without
fetching all of them.

### `day` only flags (must be given together, or not at all)

| Flag | Description |
|---|---|
| `--day [1-31]` | Day of month to fetch |
| `--month [1-12]` | Month to fetch |
| `--year YYYY` | Year to fetch, e.g. `2025` |

Leave all three out to get yesterday. The requested day must be strictly before today. You
can't fetch a day that hasn't finished yet.

### `month` only flags (must be given together, or not at all)

| Flag | Description |
|---|---|
| `--month 1-12` | Month to fetch |
| `--year YYYY` | Year to fetch, e.g. `2025` |

Leave both out to get the last full calendar month. The requested month must be strictly before
the current one "month" always means a *complete* calendar month, never a partial one.

## More examples

Yesterday's usage, per hour instead of per minute, in liters, for one specific sensor, saved to
a named file:

```bash
flume-report day --bucket HR --device-id 6721255604737738501 --units LITERS --output usage.csv
```

A specific past day (March 15, 2025), every sensor, default settings:

```bash
flume-report day --day 15 --month 3 --year 2025
```

Last full calendar month, every sensor, default (`MIN`) bucket:

```bash
flume-report month
```

A specific past month (March 2025):

```bash
flume-report month --month 3 --year 2025
```

Building up a running log across multiple runs. See
[Updating a report you already have](#updating-a-report-you-already-have) below for what
happens when `--output` already exists:

```bash
flume-report month --output water-log.csv
# next month:
flume-report month --output water-log.csv
```

## Understanding the output CSV

The CSV has one row per reading, with these columns:

```
device_id,datetime,value,units
6721255604737738501,2026-09-11 12:01:00,0.1,GALLONS
...
```

- `device_id` — which sensor the reading is from (see the `--device-id` tip above for finding
  these).
- `datetime` — the reading's timestamp, in your local time (not UTC).
- `value` — usage for that interval, in whatever `--units` you requested.
- `units` — the units that `value` is in, spelled out on every row so the file is
  self-describing even if you open it later.

## Updating a report you already have

If `--output` already points at an existing file, `flume-report` doesn't just overwrite it. It:

1. Checks the existing file's bucket (guessed from the time gap between its rows) and its
   `units` column against what you just requested. If either clearly doesn't match, it stops
   with an error and makes **no API calls** — you'll need to match `--bucket`/`--units` to the
   existing file, or use a different `--output`.
2. Otherwise, asks for confirmation:

   ```
   flume_report.csv already exists. Merge fetched data into it? [y/N]:
   ```

   Answering anything other than `y`/`yes` exits cleanly without touching the file or making any
   API calls.
3. On `y`, **merges** the newly fetched rows into the existing file rather than appending.
   Each device's rows are re-sorted chronologically, and a freshly fetched row overwrites an
   existing row for the same device and timestamp. This is how you'd build up a running log by
   re-running `flume-report month --output water-log.csv` every month.

If you're scripting this and want to skip the interactive prompt, pipe `yes` into the command —
this always answers `y`, so only do it when you're sure that's what you want:

```bash
yes | flume-report month --output water-log.csv
```

There's currently no flag to force a full replace of an existing file.

## Token caching

After your first successful run, `flume-report` caches an access/refresh token pair at
`~/.flume/token.json` so it doesn't have to log in with your password every time. It reuses the
cached token until it's close to expiring, then refreshes it automatically. Delete that file to
force a fresh login (useful if you ever change your Flume password).

## Troubleshooting

- **`flume-report: command not found`** — The install succeeded but the command isn't on your
  PATH. Try `python3 -m flume_cli day` instead, or reinstall with `pipx install .` (pipx handles
  PATH setup for you).
- **`Missing required environment variable(s): ...`** — One or more of the four `FLUME_*`
  variables from [step 3](#3-set-your-credentials) aren't set, or your `.env` file isn't in the
  folder you're running the command from. The error names exactly which ones are missing.
- **`invalid_client`** — Your `FLUME_CLIENT_ID`/`FLUME_CLIENT_SECRET` are wrong; re-check them
  against the Customer Portal.
- **`unverified_user`** — The Flume account hasn't finished email verification/signup.
- **`Flume API rate limit reached (429): ...`** — Flume allows about 120 requests/hour per
  account. A full month at the default `MIN` bucket, across several sensors, can approach that in
  one run. There's no automatic retry — wait up to an hour and try again, or narrow the request
  with `--device-id` or a coarser `--bucket`.
- **A network error message instead of a Python traceback** — That's intentional; timeouts and
  connection failures are caught and reported cleanly rather than crashing.
- **Report looks off by a fixed number of hours** — See [Known limitations](#known-limitations)
  below; timestamps are local time, not UTC.

## Known limitations

- **Timezone**: Timestamps sent to and received from Flume are naive local time (no timezone
  conversion), matching Flume's own dashboard. This is undocumented behavior on Flume's side, not
  a settled spec. If your numbers look shifted by a fixed number of hours, this is why.
- **Paging**: Usage is fetched one HTTP request per calendar day per device (so `month` makes
  roughly 28-31 requests per sensor), since Flume doesn't document a range limit for a single
  query. This was chosen defensively and hasn't been independently verified as safe at every
  `--bucket` setting on very large accounts. Watch for errors or unexpectedly short results if
  you have a lot of sensors or a long history.
- **No merge-skip flag**: See [Updating a report you already have](#updating-a-report-you-already-have)
  — there's no flag to bypass the confirmation prompt; use `yes | flume-report ...` instead.
- **Bucket mismatch detection is a heuristic**: The CSV has no bucket column, so an existing
  file's bucket is *guessed* from the time gap between its first two rows. A sparse or hand-edited
  file can produce a wrong or undetectable guess (treated as compatible in that case).

## Development

For contributors — you don't need any of this just to run `flume-report`.

Dev dependencies ([ruff](https://docs.astral.sh/ruff/) for linting, [pytest](https://pytest.org)
for tests) are managed with [`uv`](https://docs.astral.sh/uv/) via a `dev` dependency group in
`pyproject.toml`:

```bash
uv sync                    # installs runtime + dev dependencies into .venv
uv run ruff check .        # lint
uv run pytest              # run tests
```

See [`CLAUDE.md`](CLAUDE.md) for an overview of how the code is organized.
