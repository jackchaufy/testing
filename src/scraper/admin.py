from __future__ import annotations

import html
import json

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from starlette.responses import RedirectResponse

from scraper.config import get_db_path
from scraper.db import delete_match, fetch_matches

app = FastAPI(title="Scraper Admin")


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return _render_table_page(
        "Scraper Admin",
        ["Page", "Description"],
        "\n".join(
            [
                _render_link_row("/", "Home"),
                _render_link_row("/matches", "Matched threads"),
                _render_link_row("/user-comments", "Comments from target user"),
                _render_link_row("/stock-comments", "Comments grouped by stock"),
            ]
        ),
    )


@app.get("/matches", response_class=HTMLResponse)
def index() -> str:
    db_path = get_db_path()
    rows = fetch_matches(db_path)
    table_rows = "\n".join(
        _render_row(row_id, scraped_at, url, thread_id, title, payload)
        for row_id, scraped_at, url, thread_id, title, payload in rows
    )
    return _render_table_page(
        "Scraper Matches",
        ["ID", "Scraped At", "URL", "Thread ID", "Title", "Payload", "Actions"],
        table_rows,
    )


@app.get("/user-comments", response_class=HTMLResponse)
def user_comments() -> str:
    db_path = get_db_path()
    rows = _fetch_user_comments(db_path)
    table_rows = "\n".join(
        _render_user_comment_row(*row) for row in rows
    )
    return _render_table_page(
        "User Comments",
        [
            "ID",
            "Scraped At",
            "Thread ID",
            "Page",
            "Post ID",
            "User ID",
            "User Nickname",
            "Reply Time",
            "Message",
        ],
        table_rows,
    )


@app.get("/stock-comments", response_class=HTMLResponse)
def stock_comments() -> str:
    db_path = get_db_path()
    rows = _fetch_stock_comments(db_path)
    table_rows = "\n".join(
        _render_stock_comment_row(*row) for row in rows
    )
    return _render_table_page(
        "Stock Comments",
        [
            "ID",
            "Scraped At",
            "Stock",
            "Thread ID",
            "Page",
            "Post ID",
            "User ID",
            "User Nickname",
            "Reply Time",
            "Message",
        ],
        table_rows,
    )


@app.post("/delete/{match_id}")
def delete_match_row(match_id: int) -> RedirectResponse:
    db_path = get_db_path()
    delete_match(db_path, match_id)
    return RedirectResponse(url="/matches", status_code=303)


def _render_row(
    row_id: int, scraped_at: str, url: str, thread_id: int, title: str, payload: str
) -> str:
    safe_title = html.escape(title)
    safe_url = html.escape(url)
    formatted_payload = _format_payload(payload)
    return (
        "<tr>"
        f"<td>{row_id}</td>"
        f"<td>{scraped_at}</td>"
        f"<td>{safe_url}</td>"
        f"<td>{thread_id}</td>"
        f"<td>{safe_title}</td>"
        f"<td><pre>{formatted_payload}</pre></td>"
        "<td>"
        f"<form method='post' action='/delete/{row_id}'>"
        "<button type='submit'>Delete</button>"
        "</form>"
        "</td>"
        "</tr>"
    )


def _render_table_page(title: str, headers: list[str], rows_html: str) -> str:
    header_cells = "".join(f"<th>{html.escape(header)}</th>" for header in headers)
    return f"""
    <html>
      <head>
        <title>{html.escape(title)}</title>
        <style>
          body {{ font-family: Arial, sans-serif; margin: 24px; }}
          table {{ border-collapse: collapse; width: 100%; }}
          th, td {{ border: 1px solid #ddd; padding: 8px; vertical-align: top; }}
          th {{ background-color: #f4f4f4; }}
          pre {{ margin: 0; white-space: pre-wrap; word-break: break-word; }}
        </style>
      </head>
      <body>
        <h1>{html.escape(title)}</h1>
        <table>
          <thead>
            <tr>
              {header_cells}
            </tr>
          </thead>
          <tbody>
            {rows_html}
          </tbody>
        </table>
      </body>
    </html>
    """


def _render_link_row(path: str, description: str) -> str:
    safe_path = html.escape(path)
    safe_description = html.escape(description)
    return (
        "<tr>"
        f"<td><a href='{safe_path}'>{safe_path}</a></td>"
        f"<td>{safe_description}</td>"
        "</tr>"
    )


def _fetch_user_comments(db_path):
    import sqlite3

    with sqlite3.connect(db_path) as conn:
        return conn.execute(
            """
            SELECT id, scraped_at, thread_id, page, post_id, user_id, user_nickname, reply_time, msg
            FROM user_comments
            ORDER BY id DESC
            """
        ).fetchall()


def _fetch_stock_comments(db_path):
    import sqlite3

    with sqlite3.connect(db_path) as conn:
        return conn.execute(
            """
            SELECT id, scraped_at, stock, thread_id, page, post_id, user_id, user_nickname, reply_time, msg
            FROM stock_comments
            ORDER BY id DESC
            """
        ).fetchall()


def _render_user_comment_row(
    row_id: int,
    scraped_at: str,
    thread_id: int,
    page: int,
    post_id: str,
    user_id: int,
    user_nickname: str,
    reply_time: int,
    msg: str,
) -> str:
    return (
        "<tr>"
        f"<td>{row_id}</td>"
        f"<td>{scraped_at}</td>"
        f"<td>{thread_id}</td>"
        f"<td>{page}</td>"
        f"<td>{html.escape(post_id)}</td>"
        f"<td>{user_id}</td>"
        f"<td>{html.escape(user_nickname)}</td>"
        f"<td>{reply_time}</td>"
        f"<td><pre>{html.escape(msg)}</pre></td>"
        "</tr>"
    )


def _render_stock_comment_row(
    row_id: int,
    scraped_at: str,
    stock: str,
    thread_id: int,
    page: int,
    post_id: str,
    user_id: int,
    user_nickname: str,
    reply_time: int,
    msg: str,
) -> str:
    return (
        "<tr>"
        f"<td>{row_id}</td>"
        f"<td>{scraped_at}</td>"
        f"<td>{html.escape(stock)}</td>"
        f"<td>{thread_id}</td>"
        f"<td>{page}</td>"
        f"<td>{html.escape(post_id)}</td>"
        f"<td>{user_id}</td>"
        f"<td>{html.escape(user_nickname)}</td>"
        f"<td>{reply_time}</td>"
        f"<td><pre>{html.escape(msg)}</pre></td>"
        "</tr>"
    )


def _format_payload(payload: str) -> str:
    try:
        parsed = json.loads(payload)
    except json.JSONDecodeError:
        return html.escape(payload)
    return html.escape(json.dumps(parsed, ensure_ascii=False, indent=2))


def main() -> None:
    import uvicorn

    uvicorn.run("scraper.admin:app", host="0.0.0.0", port=8000, reload=False)
