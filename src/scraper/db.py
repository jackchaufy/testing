import sqlite3
from pathlib import Path
from typing import Iterable


def init_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS thread_matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scraped_at TEXT NOT NULL,
                url TEXT NOT NULL,
                thread_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                payload TEXT NOT NULL,
                UNIQUE(thread_id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scraped_at TEXT NOT NULL,
                thread_id INTEGER NOT NULL,
                page INTEGER NOT NULL,
                post_id TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                user_nickname TEXT NOT NULL,
                reply_time INTEGER NOT NULL,
                msg TEXT NOT NULL,
                payload TEXT NOT NULL,
                UNIQUE(thread_id, post_id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS stock_comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scraped_at TEXT NOT NULL,
                stock TEXT NOT NULL,
                thread_id INTEGER NOT NULL,
                page INTEGER NOT NULL,
                post_id TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                user_nickname TEXT NOT NULL,
                reply_time INTEGER NOT NULL,
                msg TEXT NOT NULL,
                payload TEXT NOT NULL,
                UNIQUE(stock, thread_id, post_id)
            )
            """
        )
        conn.commit()


def insert_match(
    db_path: Path, scraped_at: str, url: str, thread_id: int, title: str, payload: str
) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT OR IGNORE INTO thread_matches"
            " (scraped_at, url, thread_id, title, payload)"
            " VALUES (?, ?, ?, ?, ?)",
            (scraped_at, url, thread_id, title, payload),
        )
        conn.commit()


def fetch_matches(db_path: Path) -> Iterable[tuple[int, str, str, int, str, str]]:
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            "SELECT id, scraped_at, url, thread_id, title, payload"
            " FROM thread_matches ORDER BY id DESC"
        ).fetchall()
    return rows


def insert_user_comment(
    db_path: Path,
    scraped_at: str,
    thread_id: int,
    page: int,
    post_id: str,
    user_id: int,
    user_nickname: str,
    reply_time: int,
    msg: str,
    payload: str,
) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO user_comments
            (scraped_at, thread_id, page, post_id, user_id, user_nickname, reply_time, msg, payload)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                scraped_at,
                thread_id,
                page,
                post_id,
                user_id,
                user_nickname,
                reply_time,
                msg,
                payload,
            ),
        )
        conn.commit()


def insert_stock_comment(
    db_path: Path,
    scraped_at: str,
    stock: str,
    thread_id: int,
    page: int,
    post_id: str,
    user_id: int,
    user_nickname: str,
    reply_time: int,
    msg: str,
    payload: str,
) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO stock_comments
            (scraped_at, stock, thread_id, page, post_id, user_id, user_nickname, reply_time, msg, payload)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                scraped_at,
                stock,
                thread_id,
                page,
                post_id,
                user_id,
                user_nickname,
                reply_time,
                msg,
                payload,
            ),
        )
        conn.commit()


def delete_match(db_path: Path, match_id: int) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute("DELETE FROM thread_matches WHERE id = ?", (match_id,))
        conn.commit()
