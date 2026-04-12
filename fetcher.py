import re
from datetime import datetime, timedelta, timezone
from time import mktime

import feedparser

FEEDS = [
    ("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/"),
    ("MIT Sloan Review", "https://sloanreview.mit.edu/feed/"),
    ("HBR", "https://feeds.hbr.org/harvardbusiness"),
    ("Google News — LLM releases",
     "https://news.google.com/rss/search?q=LLM+model+release+OR+update&hl=en-US&gl=US&ceid=US:en"),
    ("Google News — AI adoption",
     "https://news.google.com/rss/search?q=%22AI+adoption%22+enterprise&hl=en-US&gl=US&ceid=US:en"),
]

MAX_AGE_DAYS = 3
MAX_ITEMS_PER_FEED = 4
SUMMARY_MAX_CHARS = 250


def _clean(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text or "")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def fetch_stories() -> list[dict]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=MAX_AGE_DAYS)
    stories: list[dict] = []

    for source_name, url in FEEDS:
        try:
            feed = feedparser.parse(url)
        except Exception as exc:
            print(f"Feed failed ({source_name}): {exc}")
            continue

        kept = 0
        for entry in feed.entries:
            if kept >= MAX_ITEMS_PER_FEED:
                break

            published_struct = entry.get("published_parsed") or entry.get("updated_parsed")
            if published_struct:
                published_dt = datetime.fromtimestamp(mktime(published_struct), tz=timezone.utc)
                if published_dt < cutoff:
                    continue

            stories.append({
                "source": source_name,
                "title": _clean(entry.get("title", "")),
                "url": entry.get("link", ""),
                "summary": _clean(entry.get("summary", ""))[:SUMMARY_MAX_CHARS],
            })
            kept += 1

    print(f"Fetched {len(stories)} stories from {len(FEEDS)} feeds.")
    return stories
