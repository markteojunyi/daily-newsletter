import re
from datetime import datetime, timedelta, timezone
from time import mktime
from urllib.parse import urlparse

import feedparser
import requests

from database import filter_unseen

FEEDS = [
    ("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/"),
    ("MIT Sloan Review", "https://sloanreview.mit.edu/feed/"),
    ("HBR", "https://feeds.hbr.org/harvardbusiness"),
    ("Google News — LLM releases",
     "https://news.google.com/rss/search?q=LLM+model+release+OR+update&hl=en-US&gl=US&ceid=US:en"),
    ("Google News — AI adoption",
     "https://news.google.com/rss/search?q=%22AI+adoption%22+enterprise&hl=en-US&gl=US&ceid=US:en"),
    ("OpenAI Blog", "https://openai.com/blog/rss.xml"),
    ("VentureBeat AI", "https://venturebeat.com/category/ai/feed/"),
]

MAX_AGE_DAYS = 3
MAX_ITEMS_PER_FEED = 4
SUMMARY_MAX_CHARS = 250
REDIRECT_TIMEOUT = 8

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)


def _clean(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text or "")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _is_google_news_url(url: str) -> bool:
    try:
        return urlparse(url).netloc.endswith("news.google.com")
    except Exception:
        return False


def _publisher_from_entry(entry, fallback: str) -> str:
    """Extract the real publisher name from a Google News RSS entry."""
    src = entry.get("source")
    if isinstance(src, dict) and src.get("title"):
        return src["title"].strip()
    title_attr = getattr(src, "title", None) if src is not None else None
    if title_attr:
        return title_attr.strip()

    # Fallback: Google News titles end with "  - Publisher"
    title = entry.get("title", "")
    m = re.search(r"\s+-\s+([^-]+)$", title)
    if m:
        return m.group(1).strip()
    return fallback


def _strip_publisher_suffix(title: str) -> str:
    """Strip the trailing ' - Publisher' that Google News appends to titles."""
    return re.sub(r"\s+-\s+[^-]+$", "", title or "").strip()


def _resolve_redirect(url: str) -> str:
    """Follow redirects on a Google News link to recover the original article URL."""
    try:
        resp = requests.get(
            url,
            timeout=REDIRECT_TIMEOUT,
            allow_redirects=True,
            headers={"User-Agent": USER_AGENT},
        )
        final = resp.url
        if final and not _is_google_news_url(final):
            return final
    except Exception as exc:
        print(f"Could not resolve Google News redirect: {exc}")
    return url


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

            raw_title = _clean(entry.get("title", ""))
            raw_url = entry.get("link", "")
            display_source = source_name
            display_title = raw_title
            display_url = raw_url

            if _is_google_news_url(raw_url):
                display_source = _publisher_from_entry(entry, source_name)
                display_title = _strip_publisher_suffix(raw_title)
                display_url = _resolve_redirect(raw_url)

            stories.append({
                "source": display_source,
                "title": display_title,
                "url": display_url,
                "summary": _clean(entry.get("summary", ""))[:SUMMARY_MAX_CHARS],
            })
            kept += 1

    print(f"Fetched {len(stories)} stories from {len(FEEDS)} feeds.")

    fresh = filter_unseen(stories)
    print(f"{len(fresh)} stories are new (after dedup against the seen-articles database).")
    return fresh
