from __future__ import annotations

import datetime as dt
import json

from playwright.async_api import async_playwright

from scraper.config import (
    get_request_headers,
    get_stock_keywords,
    get_target_user_id,
    get_thread_url,
    get_title_keywords,
)
from scraper.db import insert_match, insert_stock_comment, insert_user_comment


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
        await _scrape_thread(db_path, thread_id, scraped_at)
        matches += 1
    return matches


async def _scrape_thread(db_path, thread_id: int, scraped_at: str) -> None:
    async with async_playwright() as playwright:
        request = await playwright.request.new_context(
            extra_http_headers=get_request_headers()
        )
        await scrape_thread_pages(db_path, request, thread_id, scraped_at)
        await request.dispose()


async def scrape_thread_pages(db_path, request, thread_id: int, scraped_at: str) -> None:
    thread_url = get_thread_url(thread_id, 1)
    response = await request.get(thread_url)
    if not response.ok:
        return
    body = await response.text()
    payload = json.loads(body)
    response_payload = payload.get("response", {})
    total_page = int(response_payload.get("total_page", 1))
    _process_thread_page(db_path, response_payload, thread_id, 1, scraped_at)
    for page in range(2, total_page + 1):
        page_url = get_thread_url(thread_id, page)
        page_response = await request.get(page_url)
        if not page_response.ok:
            continue
        page_body = await page_response.text()
        page_payload = json.loads(page_body)
        page_response_payload = page_payload.get("response", {})
        _process_thread_page(db_path, page_response_payload, thread_id, page, scraped_at)


def _process_thread_page(
    db_path, response_payload: dict, thread_id: int, page: int, scraped_at: str
) -> None:
    items = response_payload.get("item_data", [])
    target_user_id = get_target_user_id()
    stock_keywords = get_stock_keywords()
    for item in items:
        user_id = int(item.get("user_id", 0))
        post_id = str(item.get("post_id", ""))
        user_nickname = str(item.get("user_nickname", ""))
        msg = str(item.get("msg", ""))
        if user_id == target_user_id:
            insert_user_comment(
                db_path,
                scraped_at,
                thread_id,
                page,
                post_id,
                user_id,
                user_nickname,
                msg,
                json.dumps(item, ensure_ascii=False),
            )
        for stock in stock_keywords:
            if stock in msg:
                insert_stock_comment(
                    db_path,
                    scraped_at,
                    stock,
                    thread_id,
                    page,
                    post_id,
                    user_id,
                    user_nickname,
                    msg,
                    json.dumps(item, ensure_ascii=False),
                )
