"""
topic_ranker.py — Scores and ranks topics by relevance, freshness, and quality.
"""

from datetime import datetime
from email.utils import parsedate_to_datetime
from utils import log, now_wib


# ─── Scoring Weights ─────────────────────────────────────────
WEIGHT_KEYWORD = 4.0
WEIGHT_TITLE_LENGTH = 1.0
WEIGHT_FRESHNESS = 3.0
WEIGHT_UNIQUENESS = 2.0

# High-value keywords get bonus points
HIGH_VALUE_KEYWORDS = [
    "ai", "llm", "agent", "astro", "react", "nextjs",
    "performance", "typescript", "tailwind",
]

TOP_N = 3


def _keyword_score(title: str) -> float:
    """Score based on how many high-value keywords appear in the title."""
    title_lower = title.lower()
    matches = sum(1 for kw in HIGH_VALUE_KEYWORDS if kw in title_lower)
    return min(matches / 2.0, 1.0)  # Normalize to 0-1


def _title_length_score(title: str) -> float:
    """
    Prefer medium-length titles (40-80 chars).
    Too short = vague, too long = cluttered.
    """
    length = len(title)
    if 40 <= length <= 80:
        return 1.0
    elif 20 <= length < 40 or 80 < length <= 120:
        return 0.6
    else:
        return 0.3


def _freshness_score(published: str) -> float:
    """Score based on how recent the article is."""
    if not published:
        return 0.3  # Unknown date gets low score

    try:
        pub_date = parsedate_to_datetime(published)
        now = now_wib()
        # Make both offset-aware for comparison
        if pub_date.tzinfo is None:
            from datetime import timezone
            pub_date = pub_date.replace(tzinfo=timezone.utc)

        days_old = (now - pub_date).days

        if days_old <= 1:
            return 1.0
        elif days_old <= 3:
            return 0.8
        elif days_old <= 7:
            return 0.6
        elif days_old <= 14:
            return 0.4
        else:
            return 0.2
    except Exception:
        return 0.3


def _uniqueness_score(title: str, all_titles: list[str]) -> float:
    """Score based on how different this title is from others in the batch."""
    title_words = set(title.lower().split())
    if not title_words:
        return 0.5

    max_overlap = 0.0
    for other in all_titles:
        if other.lower() == title.lower():
            continue
        other_words = set(other.lower().split())
        if not other_words:
            continue
        overlap = len(title_words & other_words) / len(title_words | other_words)
        max_overlap = max(max_overlap, overlap)

    return 1.0 - max_overlap


def rank_topics(topics: list[dict]) -> list[dict]:
    """
    Score and rank topics. Returns the top N topics sorted by score.
    Each topic dict gets an additional 'score' field.
    """
    if not topics:
        log("RANKER", "No topics to rank")
        return []

    log("RANKER", f"Ranking {len(topics)} topics...")

    all_titles = [t["title"] for t in topics]

    scored = []
    for topic in topics:
        title = topic["title"]
        published = topic.get("published", "")

        kw = _keyword_score(title) * WEIGHT_KEYWORD
        tl = _title_length_score(title) * WEIGHT_TITLE_LENGTH
        fr = _freshness_score(published) * WEIGHT_FRESHNESS
        uq = _uniqueness_score(title, all_titles) * WEIGHT_UNIQUENESS

        total = kw + tl + fr + uq
        topic_copy = {**topic, "score": round(total, 2)}
        scored.append(topic_copy)

    # Sort descending by score
    scored.sort(key=lambda t: t["score"], reverse=True)

    top = scored[:TOP_N]
    for i, t in enumerate(top, 1):
        log("RANKER", f"  #{i} (score={t['score']}): {t['title']}")

    return top


if __name__ == "__main__":
    # Quick test with sample data
    sample = [
        {"title": "AI Agent Framework for React Developers", "published": "", "link": ""},
        {"title": "New CSS Feature", "published": "", "link": ""},
        {"title": "Building LLM-Powered Astro Sites with TypeScript", "published": "", "link": ""},
    ]
    ranked = rank_topics(sample)
    for t in ranked:
        print(f"  {t['score']}: {t['title']}")
