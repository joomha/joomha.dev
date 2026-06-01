"""
publisher.py — Saves validated articles to the blog content directory
and updates article history.
"""

from pathlib import Path
from utils import log, log_error, get_blog_dir, now_wib
from duplicate_checker import add_to_history


def publish_article(content: str, slug: str, title: str) -> Path | None:
    """
    Save an article as an MDX file to src/content/blog/YYYY/.
    Returns the file path if successful, None if skipped or failed.
    """
    log("PUBLISHER", f"Publishing article: '{title}'")

    year = now_wib().year
    blog_dir = get_blog_dir(year)
    filename = f"{slug}.mdx"
    file_path = blog_dir / filename

    # Duplicate file protection
    if file_path.exists():
        log("PUBLISHER", f"⚠ File already exists, skipping: {file_path}")
        return None

    try:
        # Ensure content ends with a newline
        if not content.endswith("\n"):
            content += "\n"

        file_path.write_text(content, encoding="utf-8")
        log("PUBLISHER", f"Article saved: {file_path}")

        # Update article history
        add_to_history(title, slug)

        return file_path

    except Exception as e:
        log_error("PUBLISHER", f"Failed to save article: {e}")
        return None


if __name__ == "__main__":
    # Quick test (dry run)
    test_content = """---
title: "Test Article"
pubDatetime: 2026-06-01T10:00:00+07:00
description: "Test description"
tags:
  - test
draft: false
---

## Test Content

This is a test.
"""
    print("Would save to:", get_blog_dir() / "test-article.mdx")
