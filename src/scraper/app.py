import asyncio

from scraper.config import get_db_path, get_interval_seconds, get_target_url
from scraper.db import init_db
from scraper.scrape import scrape_api


async def run_periodic() -> None:
    db_path = get_db_path()
    init_db(db_path)

    url = get_target_url()
    interval = get_interval_seconds()

    while True:
        await scrape_api(db_path, url)
        await asyncio.sleep(interval)


def main() -> None:
    asyncio.run(run_periodic())


if __name__ == "__main__":
    main()
