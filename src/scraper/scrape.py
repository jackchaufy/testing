from __future__ import annotations

import datetime as dt

from playwright.async_api import async_playwright

from scraper.config import get_request_headers
from scraper.db import insert_snapshot


async def scrape_api(db_path, url: str) -> None:
    async with async_playwright() as playwright:
        request = await playwright.request.new_context(
            extra_http_headers=get_request_headers()
        )
        response = await request.get(url)
        status = response.status
        body = await response.text()
        await request.dispose()

    scraped_at = dt.datetime.utcnow().isoformat()
    insert_snapshot(db_path, scraped_at, url, status, body)
