"""
main.py — Pipeline orchestrator for the Auto Article Agent.

Pipeline Flow:
  Research → Rank Topics → Duplicate Check → Generate Article
  → Validate Article → Quality Score → Generate Thumbnail
  → Save Article → Update History → Done
"""

import sys
import os

# Ensure the agent directory is in the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv

# Load .env for local development
load_dotenv()

from utils import log, log_error
from researcher import get_trending_topics
from topic_ranker import rank_topics
from duplicate_checker import is_duplicate
from generator import generate_article
from validator import validate_article
from quality_scorer import score_article
from image_generator import generate_thumbnail
from publisher import publish_article


# ─── Config ──────────────────────────────────────────────────
MAX_QUALITY_RETRIES = 2  # Max regeneration attempts for low-quality articles


def run_pipeline() -> bool:
    """
    Execute the full auto-article pipeline.
    Returns True if an article was successfully published, False otherwise.
    """
    log("PIPELINE", "=" * 60)
    log("PIPELINE", "Auto Article Agent v2 — Starting pipeline")
    log("PIPELINE", "=" * 60)

    # ── Step 1: Research ─────────────────────────────────────
    log("PIPELINE", "Step 1/8: Research")
    topics = get_trending_topics()

    if not topics:
        log_error("PIPELINE", "No topics found from RSS feeds. Exiting.")
        return False

    log("PIPELINE", f"Found {len(topics)} raw topics")

    # ── Step 2: Rank ─────────────────────────────────────────
    log("PIPELINE", "Step 2/8: Ranking topics")
    ranked = rank_topics(topics)

    if not ranked:
        log_error("PIPELINE", "No topics after ranking. Exiting.")
        return False

    # ── Step 3: Duplicate Check ──────────────────────────────
    log("PIPELINE", "Step 3/8: Checking for duplicates")
    selected_topic = None

    for topic in ranked:
        if not is_duplicate(topic["title"]):
            selected_topic = topic
            break
        log("PIPELINE", f"Skipping duplicate: '{topic['title']}'")

    if not selected_topic:
        log("PIPELINE", "⚠ All top topics are duplicates. "
            "No new article to generate this week.")
        return False

    topic_title = selected_topic["title"]
    log("PIPELINE", f"Selected topic: '{topic_title}'")

    # ── Step 4-6: Generate + Validate + Quality Loop ─────────
    article = None

    for attempt in range(1, MAX_QUALITY_RETRIES + 2):
        # Step 4: Generate
        log("PIPELINE", f"Step 4/8: Generating article (attempt {attempt})")
        result = generate_article(topic_title)

        if not result:
            log_error("PIPELINE", "Article generation failed. Exiting.")
            return False

        content = result["content"]
        slug = result["slug"]
        title = result["title"]
        model_used = result["model_used"]

        log("PIPELINE", f"Generated with model: {model_used}")

        # Step 5: Validate
        log("PIPELINE", "Step 5/8: Validating article")
        is_valid, errors = validate_article(content)

        if not is_valid:
            log_error("PIPELINE", f"Validation failed: {errors}")
            if attempt <= MAX_QUALITY_RETRIES:
                log("PIPELINE", "Regenerating...")
                continue
            else:
                log_error("PIPELINE", "Max validation retries exceeded. Exiting.")
                return False

        # Step 6: Quality Score
        log("PIPELINE", "Step 6/8: Scoring quality")
        scores = score_article(content, title)

        if scores["pass"]:
            article = result
            break
        else:
            log("PIPELINE", f"Quality score {scores['final_score']}/10 — below threshold")
            if attempt <= MAX_QUALITY_RETRIES:
                log("PIPELINE", "Regenerating for better quality...")
                continue
            else:
                log("PIPELINE", "Max quality retries exceeded. "
                    "Publishing best effort article.")
                article = result
                break

    if not article:
        log_error("PIPELINE", "Failed to produce a valid article. Exiting.")
        return False

    # ── Step 7: Generate Thumbnail ───────────────────────────
    log("PIPELINE", "Step 7/8: Generating thumbnail")
    thumbnail_path = generate_thumbnail(article["title"], article["slug"])

    if thumbnail_path:
        log("PIPELINE", f"Thumbnail: {thumbnail_path}")
    else:
        log("PIPELINE", "⚠ Thumbnail generation failed (non-critical, continuing)")

    # ── Step 8: Publish ──────────────────────────────────────
    log("PIPELINE", "Step 8/8: Publishing article")
    saved_path = publish_article(
        article["content"],
        article["slug"],
        article["title"]
    )

    if not saved_path:
        log_error("PIPELINE", "Publishing failed. Exiting.")
        return False

    # ── Done ─────────────────────────────────────────────────
    log("PIPELINE", "=" * 60)
    log("PIPELINE", "✓ Pipeline complete!")
    log("PIPELINE", f"  Title: {article['title']}")
    log("PIPELINE", f"  File:  {saved_path}")
    log("PIPELINE", f"  Slug:  {article['slug']}")
    log("PIPELINE", f"  Model: {article['model_used']}")
    log("PIPELINE", f"  Tags:  {', '.join(article['tags'])}")
    log("PIPELINE", "=" * 60)

    return True


if __name__ == "__main__":
    try:
        success = run_pipeline()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        log("PIPELINE", "Interrupted by user")
        sys.exit(1)
    except Exception as e:
        log_error("PIPELINE", f"Unhandled error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
