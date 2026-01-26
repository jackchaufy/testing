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
                payload TEXT NOT NULL
            )
            """
        )
        conn.commit()


def insert_match(
    db_path: Path, scraped_at: str, url: str, thread_id: int, title: str, payload: str
) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO thread_matches (scraped_at, url, thread_id, title, payload)"
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
