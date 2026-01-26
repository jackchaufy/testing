from __future__ import annotations

import datetime as dt

from playwright.async_api import async_playwright

from scraper.db import insert_snapshot


async def scrape_title(db_path, url: str) -> None:
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        page = await browser.new_page()
        await page.goto(url, wait_until="domcontentloaded")
        title = await page.title()
        await browser.close()

    scraped_at = dt.datetime.utcnow().isoformat()
    insert_snapshot(db_path, scraped_at, url, title)
