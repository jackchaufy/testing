import sqlite3
from pathlib import Path
from typing import Iterable


def init_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS api_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scraped_at TEXT NOT NULL,
                url TEXT NOT NULL,
                status INTEGER NOT NULL,
                body TEXT NOT NULL
            )
            """
        )
        conn.commit()


def insert_snapshot(
    db_path: Path, scraped_at: str, url: str, status: int, body: str
) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO api_responses (scraped_at, url, status, body) VALUES (?, ?, ?, ?)",
            (scraped_at, url, status, body),
        )
        conn.commit()


def fetch_snapshots(db_path: Path) -> Iterable[tuple[int, str, str, int, str]]:
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            "SELECT id, scraped_at, url, status, body FROM api_responses ORDER BY id DESC"
        ).fetchall()
    return rows
