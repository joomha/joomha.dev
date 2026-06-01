"""
duplicate_checker.py — Prevents publishing similar articles
by checking against article history using keyword overlap (Jaccard similarity).
"""

import json
from pathlib import Path
from utils import log, log_error, get_history_path, today_str


SIMILARITY_THRESHOLD = 0.50  # 50% keyword overlap = duplicate


def _load_history() -> list[dict]:
    """Load article history from JSON file."""
    path = get_history_path()
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        log_error("DEDUP", f"Failed to load history: {e}")
        return []


def _save_history(history: list[dict]) -> None:
    """Save article history to JSON file."""
    path = get_history_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def _extract_keywords(title: str) -> set[str]:
    """Extract meaningful keywords from a title (lowercase, stripped)."""
    # Remove common stop words
    stop_words = {
        "the", "a", "an", "is", "are", "was", "were", "in", "on", "at",
        "to", "for", "of", "with", "by", "from", "and", "or", "but",
        "not", "this", "that", "it", "its", "as", "be", "has", "had",
        "do", "does", "did", "will", "can", "could", "should", "would",
        "how", "what", "why", "when", "where", "which", "who",
        "yang", "dan", "di", "ke", "dari", "untuk", "dengan", "ini",
        "itu", "atau", "adalah", "akan", "bisa", "sudah", "juga",
        "pada", "tidak", "lebih", "baru", "cara", "tentang",
    }
    words = set(title.lower().split())
    return words - stop_words


def _jaccard_similarity(set_a: set, set_b: set) -> float:
    """Calculate Jaccard similarity between two sets."""
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 0.0


def is_duplicate(topic_title: str) -> bool:
    """
    Check if a topic is too similar to any previously published article.
    Returns True if similarity exceeds threshold.
    """
    history = _load_history()
    if not history:
        return False

    new_keywords = _extract_keywords(topic_title)
    if not new_keywords:
        return False

    for entry in history:
        old_title = entry.get("title", "")
        old_keywords = _extract_keywords(old_title)
        similarity = _jaccard_similarity(new_keywords, old_keywords)

        if similarity >= SIMILARITY_THRESHOLD:
            log("DEDUP", f"Duplicate detected (sim={similarity:.2f}): "
                f"'{topic_title}' ≈ '{old_title}'")
            return True

    return False


def add_to_history(title: str, slug: str) -> None:
    """Add a newly published article to the history."""
    history = _load_history()
    history.append({
        "title": title,
        "slug": slug,
        "date": today_str(),
    })
    _save_history(history)
    log("DEDUP", f"Added to history: '{title}' ({slug})")


if __name__ == "__main__":
    # Quick test
    print("Duplicate?", is_duplicate("Building AI Agents with React"))
    add_to_history("Building AI Agents with React", "building-ai-agents-with-react")
    print("Duplicate?", is_duplicate("Building AI Agents with React and TypeScript"))
    print("Duplicate?", is_duplicate("CSS Grid Layout Performance Tips"))
