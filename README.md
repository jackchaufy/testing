# Periodic Web Scraper

This project provides a minimal folder structure for a periodic web scraper that:

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

- `SCRAPER_TARGET_URL` (default: `https://example.com`)
- `SCRAPER_INTERVAL_SECONDS` (default: `300`)
- `SCRAPER_DB_PATH` (default: `data/scraper.db`)

Example:

```bash
export SCRAPER_TARGET_URL="https://example.com"
export SCRAPER_INTERVAL_SECONDS=120
export SCRAPER_DB_PATH="data/scraper.db"
```

## Run

```bash
uv run run-scraper
```

The scraper will:

1. Open the target URL.
2. Extract the page title and timestamp.
3. Store results in SQLite.
4. Wait for the configured interval and repeat.
