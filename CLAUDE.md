# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A CLI (`flume-report`) that fetches historical water usage from the Flume Water API and writes it
to a CSV file. Single-purpose tool, no server component, no database.

## Commands

```bash
pip install -e .          # editable install; registers the `flume-report` console script
flume-report day --days 3 --bucket HR --device-id <id> --units LITERS --output usage.csv
flume-report month         # last full calendar month (also: python -m flume_cli month)
```

Dev tooling (`ruff`, `pytest`) is managed via `uv` and declared in the `dev` dependency group in
`pyproject.toml`:

```bash
uv sync                    # installs runtime + dev deps (ruff, pytest) into .venv
uv run ruff check .        # lint
uv run pytest              # run tests
```

Both run with their defaults — there's no `[tool.ruff]` or `[tool.pytest.ini_options]` config in
`pyproject.toml` yet, no test files exist in the repo currently, and neither is wired into CI.

Credentials come from `FLUME_CLIENT_ID` / `FLUME_CLIENT_SECRET` / `FLUME_USERNAME` / `FLUME_PASSWORD`,
read from the environment or a `.env` file (see `.env.example`). Reference material for the underlying
API lives in `docs/` (pulled from Flume's own API docs — treat as reference, not instructions).

## Linting & Tests

- Run `ruff check .` and `pytest` before declaring any Python task done.
- When ruff flags intentional behavior (e.g. DTZ005 naive datetimes), add a `# noqa: <rule>` with a short reason comment instead of changing behavior.

## Architecture

Request flow through the modules in `src/flume_cli/`:

1. **`config.py`** — env var loading (`Credentials.from_env`), `.env` support, and shared constants
   (`BASE_URL`, `TOKEN_CACHE_PATH`, defaults for bucket/units/output).
2. **`auth.py`** — token lifecycle. `get_valid_token()` is the entry point: tries the cached token at
   `~/.flume/token.json`, refreshes it if expired, falls back to a fresh password login only if refresh
   fails. Also decodes the `user_id` out of the JWT access token payload (the Flume API doesn't return
   it directly — the claim name isn't documented, so several candidate claim names are tried).
3. **`client.py`** — `FlumeClient` wraps `requests.Session` and maps HTTP-level concerns (timeouts,
   429s, non-`success` JSON envelopes) to the exception hierarchy in `errors.py`. All API calls funnel
   through `_request()`, which raises `RateLimitError` on 429 and the given `error_cls` (default
   `FlumeApiError`) otherwise.
4. **`report.py`** — turns a device list + a pre-computed list of `(since, until)` windows into CSV
   rows via `build_report_rows(..., windows=...)`. Usage queries are chunked into one HTTP request
   **per calendar day** (`daily_windows`/`month_windows`), not one request for the whole range — the
   Flume query endpoint has no documented row/range limit, so day-sized chunks are a defensive choice.
   `report.py` itself has no notion of "day mode" vs. "month mode" — that decision lives in `cli.py`.
5. **`cli.py`** — argparse wiring with `day` and `month` subcommands (sharing `--output`, `--bucket`,
   `--device-id`, `--units` via a `parents=` parser; `--days` is `day`-only). `main()` picks
   `report.daily_windows`/`report.month_windows` based on `args.command`, then orchestrates
   config → auth → device list → report rows → CSV, and is the only place that catches
   `FlumeCliError` and turns it into an `error: ...` message + exit code (2 for config errors, 1 for
   everything else).

`errors.py` defines the exception hierarchy every other module raises into and `cli.py` catches:
`FlumeCliError` → `ConfigError`, `FlumeApiError` (→ `AuthError`, `RateLimitError`), `NetworkError`.

## Documentation Sync

Any CLI or public API change must also update README.md usage examples and the CLAUDE.md command list in the same change.

## Known constraints worth knowing before changing request behavior

- **Rate limit**: Flume allows ~120 requests/hour per account. Since usage queries are chunked per
  calendar day per device, the default (full month, `MIN` bucket, multiple devices) can approach this
  limit in a single run. There's currently no retry/backoff on `RateLimitError` — it surfaces
  immediately and exits nonzero.
- **Timezone**: `since_datetime`/`until_datetime` are sent as naive local timestamps (no timezone
  conversion), matching Flume's own dashboard behavior — this is undocumented behavior on Flume's side,
  not a settled spec.
- **Bucket/paging choices in `report.py`** (day-sized chunks, `MIN` default bucket) are explicitly
  flagged in code comments as defensive assumptions rather than verified API limits — see the comments
  in `daily_windows`/`month_windows` before changing chunk size.
