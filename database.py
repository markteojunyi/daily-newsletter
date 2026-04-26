import hashlib
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).parent / "articles.db"


def _normalize_title(title: str) -> str:
    """Lowercase, strip punctuation and collapse whitespace for stable fingerprinting."""
    title = (title or "").lower()
    title = re.sub(r"[^\w\s]", "", title)
    title = re.sub(r"\s+", " ", title).strip()
    return title


def article_id(title: str) -> str:
    """Stable fingerprint: SHA-1 of the normalized title.

    Title-based rather than URL-based because syndicated/aggregator URLs
    (Google News in particular) are dynamic redirects that change every fetch.
    """
    return hashlib.sha1(_normalize_title(title).encode("utf-8")).hexdigest()


def init_db() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS seen_articles (
                id          TEXT PRIMARY KEY,
                title       TEXT NOT NULL,
                source      TEXT,
                url         TEXT,
                first_seen  TEXT NOT NULL
            )
            """
        )


def filter_unseen(stories: list[dict]) -> list[dict]:
    """Return only stories whose fingerprint is not already in the database."""
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        existing = {row[0] for row in conn.execute("SELECT id FROM seen_articles")}

    fresh: list[dict] = []
    seen_in_batch: set[str] = set()
    for story in stories:
        aid = article_id(story["title"])
        if aid in existing or aid in seen_in_batch:
            continue
        seen_in_batch.add(aid)
        fresh.append(story)
    return fresh


def mark_seen(stories: list[dict]) -> None:
    """Persist the fingerprints of stories we just sent."""
    if not stories:
        return
    init_db()
    now = datetime.now(timezone.utc).isoformat()
    rows = [
        (article_id(s["title"]), s["title"], s.get("source"), s.get("url"), now)
        for s in stories
    ]
    with sqlite3.connect(DB_PATH) as conn:
        conn.executemany(
            "INSERT OR IGNORE INTO seen_articles (id, title, source, url, first_seen) "
            "VALUES (?, ?, ?, ?, ?)",
            rows,
        )
