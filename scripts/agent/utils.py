"""
utils.py — Shared utilities for the Auto Article Agent.
Provides structured logging, path helpers, and date utilities.
"""

import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path


# ─── Timezone ────────────────────────────────────────────────
WIB = timezone(timedelta(hours=7))  # Asia/Jakarta UTC+7


# ─── Logging ─────────────────────────────────────────────────
def log(tag: str, message: str) -> None:
    """Print a structured log message with tag prefix."""
    print(f"[{tag.upper()}] {message}")


def log_error(tag: str, message: str) -> None:
    """Print a structured error message to stderr."""
    print(f"[{tag.upper()} ERROR] {message}", file=sys.stderr)


# ─── Path Helpers ────────────────────────────────────────────
def get_project_root() -> Path:
    """Return the project root directory (two levels up from this file)."""
    return Path(__file__).resolve().parent.parent.parent


def get_blog_dir(year: int | None = None) -> Path:
    """Return the blog content directory, optionally for a specific year."""
    root = get_project_root()
    if year is None:
        year = now_wib().year
    blog_dir = root / "src" / "content" / "blog" / str(year)
    blog_dir.mkdir(parents=True, exist_ok=True)
    return blog_dir


def get_image_dir() -> Path:
    """Return the blog images directory under src/assets/images/blog."""
    root = get_project_root()
    img_dir = root / "src" / "assets" / "images" / "blog"
    img_dir.mkdir(parents=True, exist_ok=True)
    return img_dir


def get_history_path() -> Path:
    """Return the path to article_history.json."""
    root = get_project_root()
    data_dir = root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "article_history.json"


# ─── Date Helpers ────────────────────────────────────────────
def now_wib() -> datetime:
    """Return the current datetime in WIB (UTC+7)."""
    return datetime.now(WIB)


def iso_now() -> str:
    """Return the current datetime as ISO 8601 string with +07:00 offset."""
    return now_wib().isoformat()


def today_str() -> str:
    """Return today's date as YYYY-MM-DD string."""
    return now_wib().strftime("%Y-%m-%d")
