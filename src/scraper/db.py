import sqlite3
from pathlib import Path
from typing import Iterable


def init_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS page_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scraped_at TEXT NOT NULL,
                url TEXT NOT NULL,
                title TEXT NOT NULL
            )
            """
        )
        conn.commit()


def insert_snapshot(db_path: Path, scraped_at: str, url: str, title: str) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO page_snapshots (scraped_at, url, title) VALUES (?, ?, ?)",
            (scraped_at, url, title),
        )
        conn.commit()


def fetch_snapshots(db_path: Path) -> Iterable[tuple[int, str, str, str]]:
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            "SELECT id, scraped_at, url, title FROM page_snapshots ORDER BY id DESC"
        ).fetchall()
    return rows
