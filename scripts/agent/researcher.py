"""
researcher.py — RSS-based trending topic research pipeline.
Fetches and filters tech topics from multiple RSS feeds.
"""

import feedparser
from utils import log, log_error


# ─── RSS Sources ─────────────────────────────────────────────
RSS_FEEDS = [
    "https://hnrss.org/frontpage",
    "https://dev.to/feed",
    "https://www.smashingmagazine.com/feed/",
    "https://astro.build/rss.xml",
    "https://vercel.com/atom",
    "https://react.dev/rss.xml",
]

# ─── Keyword Filter ──────────────────────────────────────────
KEYWORDS = [
    "ai", "web", "frontend", "backend", "astro", "react",
    "javascript", "typescript", "css", "performance", "developer",
    "llm", "agent", "nextjs", "tailwind", "nodejs",
]

MAX_TOPICS = 10


def _matches_keywords(title: str) -> bool:
    """Check if a title contains at least one relevant keyword."""
    title_lower = title.lower()
    return any(kw in title_lower for kw in KEYWORDS)


def _parse_feed(url: str) -> list[dict]:
    """Parse a single RSS feed and return filtered entries."""
    try:
        log("RESEARCH", f"Fetching {url}")
        feed = feedparser.parse(url)

        if feed.bozo and not feed.entries:
            log_error("RESEARCH", f"Failed to parse feed: {url}")
            return []

        topics = []
        for entry in feed.entries:
            title = entry.get("title", "").strip()
            link = entry.get("link", "")
            published = entry.get("published", entry.get("updated", ""))

            if not title:
                continue

            if _matches_keywords(title):
                topics.append({
                    "title": title,
                    "link": link,
                    "published": published,
                    "source": url,
                })

        log("RESEARCH", f"Found {len(topics)} relevant topics from {url}")
        return topics

    except Exception as e:
        log_error("RESEARCH", f"Error fetching {url}: {e}")
        return []


def get_trending_topics() -> list[dict]:
    """
    Fetch trending tech topics from all RSS sources.
    Returns up to MAX_TOPICS unique topics, resilient to individual feed failures.
    """
    log("RESEARCH", "Starting RSS research pipeline...")
    all_topics = []
    seen_titles = set()

    for feed_url in RSS_FEEDS:
        topics = _parse_feed(feed_url)
        for topic in topics:
            # Deduplicate by lowercase title
            title_key = topic["title"].lower().strip()
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                all_topics.append(topic)

    # Cap at MAX_TOPICS
    result = all_topics[:MAX_TOPICS]
    log("RESEARCH", f"Research complete: {len(result)} unique topics collected")
    return result


if __name__ == "__main__":
    topics = get_trending_topics()
    for i, t in enumerate(topics, 1):
        print(f"  {i}. {t['title']}")
