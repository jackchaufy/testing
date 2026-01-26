from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from scraper.config import get_db_path
from scraper.db import fetch_matches

app = FastAPI(title="Scraper Admin")


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    db_path = get_db_path()
    rows = fetch_matches(db_path)
    table_rows = "\n".join(
        f"<tr><td>{row_id}</td><td>{scraped_at}</td><td>{url}</td>"
        f"<td>{thread_id}</td><td>{title}</td><td><pre>{payload}</pre></td></tr>"
        for row_id, scraped_at, url, thread_id, title, payload in rows
    )
    return f"""
    <html>
      <head>
        <title>Scraper Admin</title>
        <style>
          body {{ font-family: Arial, sans-serif; margin: 24px; }}
          table {{ border-collapse: collapse; width: 100%; }}
          th, td {{ border: 1px solid #ddd; padding: 8px; vertical-align: top; }}
          th {{ background-color: #f4f4f4; }}
          pre {{ margin: 0; white-space: pre-wrap; word-break: break-word; }}
        </style>
      </head>
      <body>
        <h1>Scraper Matches</h1>
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Scraped At</th>
              <th>URL</th>
              <th>Thread ID</th>
              <th>Title</th>
              <th>Payload</th>
            </tr>
          </thead>
          <tbody>
            {table_rows}
          </tbody>
        </table>
      </body>
    </html>
    """


def main() -> None:
    import uvicorn

    uvicorn.run("scraper.admin:app", host="0.0.0.0", port=8000, reload=False)
