import os
from pathlib import Path

DEFAULT_TARGET_URL = (
    "https://lihkg.com/api_v2/thread/category?cat_id=15&page=1&count=60&type=now"
)
DEFAULT_INTERVAL_SECONDS = 60
DEFAULT_DB_PATH = Path("data/scraper.db")
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://lihkg.com/",
    "Origin": "https://lihkg.com",
}
DEFAULT_TITLE_KEYWORDS = [
    "最有價值收息股研究所",
    "ASPI",
    "美日韓 超長線十倍價投",
]
DEFAULT_STOCK_KEYWORDS = [
    "最有價值收息股研究所",
    "ASPI",
    "美日韓 超長線十倍價投",
]
DEFAULT_TARGET_USER_ID = 734436
THREAD_URL_TEMPLATE = "https://lihkg.com/api_v2/thread/{thread_id}/page/{page}"
DEFAULT_THREAD_START_PAGES = {
    4046873: 4,
}


def get_target_url() -> str:
    return os.getenv("SCRAPER_TARGET_URL", DEFAULT_TARGET_URL)


def get_interval_seconds() -> int:
    return int(os.getenv("SCRAPER_INTERVAL_SECONDS", DEFAULT_INTERVAL_SECONDS))


def get_db_path() -> Path:
    return Path(os.getenv("SCRAPER_DB_PATH", DEFAULT_DB_PATH))


def get_request_headers() -> dict[str, str]:
    return DEFAULT_HEADERS.copy()


def get_title_keywords() -> list[str]:
    return list(DEFAULT_TITLE_KEYWORDS)


def get_stock_keywords() -> list[str]:
    return list(DEFAULT_STOCK_KEYWORDS)


def get_target_user_id() -> int:
    return DEFAULT_TARGET_USER_ID


def get_thread_url(thread_id: int, page: int) -> str:
    return THREAD_URL_TEMPLATE.format(thread_id=thread_id, page=page)


def get_thread_start_page(thread_id: int) -> int:
    return DEFAULT_THREAD_START_PAGES.get(thread_id, 1)
