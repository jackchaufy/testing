from __future__ import annotations

import datetime as dt
import json

from playwright.async_api import async_playwright

from scraper.config import get_request_headers, get_title_keywords
from scraper.db import insert_match


async def scrape_api(db_path, url: str) -> int:
    async with async_playwright() as playwright:
        request = await playwright.request.new_context(
            extra_http_headers=get_request_headers()
        )
        response = await request.get(url)
        if not response.ok:
            await request.dispose()
            return 0
        body = await response.text()
        await request.dispose()

    scraped_at = dt.datetime.utcnow().isoformat()
    payload = json.loads(body)
    items = payload.get("response", {}).get("items", [])
    keywords = get_title_keywords()
    matches = 0
    for item in items:
        title = str(item.get("title", ""))
        if not title or not any(keyword in title for keyword in keywords):
            continue
        thread_id = int(item.get("thread_id", 0))
        insert_match(db_path, scraped_at, url, thread_id, title, json.dumps(item))
        matches += 1
    return matches
