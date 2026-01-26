import asyncio
import logging

from scraper.config import get_db_path, get_interval_seconds, get_target_url
from scraper.db import init_db
from scraper.scrape import scrape_api

LOGGER = logging.getLogger(__name__)


async def run_periodic() -> None:
    db_path = get_db_path()
    init_db(db_path)

    url = get_target_url()
    interval = get_interval_seconds()

    LOGGER.info("Starting scraper", extra={"url": url, "interval": interval})
    while True:
        matches = await scrape_api(db_path, url)
        LOGGER.info("Scrape completed", extra={"matches": matches})
        await asyncio.sleep(interval)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    asyncio.run(run_periodic())


if __name__ == "__main__":
    main()
