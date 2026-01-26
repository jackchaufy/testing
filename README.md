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
- `SCRAPER_INTERVAL_SECONDS` (default: `300`)
- `SCRAPER_DB_PATH` (default: `data/scraper.db`)

Example:

```bash
export SCRAPER_TARGET_URL="https://lihkg.com/api_v2/thread/category?cat_id=15&page=1&count=60&type=now"
export SCRAPER_INTERVAL_SECONDS=120
export SCRAPER_DB_PATH="data/scraper.db"
```

Default request headers (configurable in `config.py`) match the provided curl example:

```text
User-Agent: Mozilla/5.0
Accept: application/json, text/plain, */*
Accept-Language: en-US,en;q=0.9
Referer: https://lihkg.com/
```

## Run

```bash
uv run run-scraper
```

The scraper will:

1. Call the target API URL with Playwright's request context.
2. Store the HTTP status code and response body in SQLite.
4. Wait for the configured interval and repeat.
