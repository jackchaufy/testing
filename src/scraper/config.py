import os
from pathlib import Path

DEFAULT_TARGET_URL = "https://example.com"
DEFAULT_INTERVAL_SECONDS = 300
DEFAULT_DB_PATH = Path("data/scraper.db")


def get_target_url() -> str:
    return os.getenv("SCRAPER_TARGET_URL", DEFAULT_TARGET_URL)


def get_interval_seconds() -> int:
    return int(os.getenv("SCRAPER_INTERVAL_SECONDS", DEFAULT_INTERVAL_SECONDS))


def get_db_path() -> Path:
    return Path(os.getenv("SCRAPER_DB_PATH", DEFAULT_DB_PATH))
