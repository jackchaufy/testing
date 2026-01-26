import os
from pathlib import Path

DEFAULT_TARGET_URL = (
    "https://lihkg.com/api_v2/thread/category?cat_id=15&page=1&count=60&type=now"
)
DEFAULT_INTERVAL_SECONDS = 300
DEFAULT_DB_PATH = Path("data/scraper.db")
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://lihkg.com/",
}


def get_target_url() -> str:
    return os.getenv("SCRAPER_TARGET_URL", DEFAULT_TARGET_URL)


def get_interval_seconds() -> int:
    return int(os.getenv("SCRAPER_INTERVAL_SECONDS", DEFAULT_INTERVAL_SECONDS))


def get_db_path() -> Path:
    return Path(os.getenv("SCRAPER_DB_PATH", DEFAULT_DB_PATH))


def get_request_headers() -> dict[str, str]:
    return DEFAULT_HEADERS.copy()
