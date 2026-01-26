# Periodic Web Scraper

This project provides a minimal folder structure for a periodic API scraper that:

- Uses **Playwright** for browser automation.
- Stores results in **SQLite**.
- Uses **uv** for dependency management.

## Project layout

```
.
├── data/
├── src/
│   └── scraper/
│       ├── __init__.py
│       ├── app.py
│       ├── config.py
│       ├── db.py
│       └── scrape.py
├── pyproject.toml
└── README.md
```

## Setup

1. Create a virtual environment and install dependencies with `uv`:

```bash
uv venv
uv pip install -e .
```

2. Install Playwright browsers:

```bash
uv run playwright install
```

## Configuration

The scraper reads settings from environment variables (defaults in `config.py`):

- `SCRAPER_TARGET_URL` (default: the LIHKG API URL shown below)
- `SCRAPER_INTERVAL_SECONDS` (default: `3`)
- `SCRAPER_DB_PATH` (default: `data/scraper.db`)

Example:

```bash
export SCRAPER_TARGET_URL="https://lihkg.com/api_v2/thread/category?cat_id=15&page=1&count=60&type=now"
export SCRAPER_INTERVAL_SECONDS=3
export SCRAPER_DB_PATH="data/scraper.db"
```

Default request headers (configurable in `config.py`) match the provided curl example:

```text
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36
Accept: application/json, text/plain, */*
Accept-Language: en-US,en;q=0.9
Referer: https://lihkg.com/
Origin: https://lihkg.com
```

The scraper only saves threads whose titles contain one of these keywords (editable in
`config.py`):

- `最有價值收息股研究所`
- `ASPI`
- `美日韓 超長線十倍價投`

When a thread title matches, the scraper fetches each thread page from the LIHKG
thread API (`/api_v2/thread/{thread_id}/page/{page}`) and stores:

- All comments from `user_id=734436` in the `user_comments` table.
- Any comments whose message contains a stock keyword in the `stock_comments` table.

## Run

```bash
uv run run-scraper
```

Logs are written to `data/scraper.log`.

## Admin UI

Run the admin server to view matches in a browser:

```bash
uv run run-admin
```

Then open `http://localhost:8000` to see a table of matched threads.
Use the Delete button on each row to remove a stored match.

The scraper will:

1. Call the target API URL with Playwright's request context.
2. Filter response items by title keywords (configured in `config.py`).
3. Store matching thread IDs, titles, and JSON payloads in SQLite.
4. Wait for the configured interval and repeat.
