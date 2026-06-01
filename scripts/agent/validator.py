"""
validator.py — Validates MDX articles for frontmatter correctness and content quality.
"""

import re
import yaml
from utils import log, log_error


# ─── Required Frontmatter Fields ─────────────────────────────
REQUIRED_FIELDS = ["title", "description", "pubDatetime", "tags"]

MIN_WORD_COUNT = 400


def _extract_frontmatter(content: str) -> tuple[dict | None, str]:
    """Extract YAML frontmatter and body from MDX content."""
    pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
    match = re.match(pattern, content, re.DOTALL)

    if not match:
        return None, content

    try:
        fm = yaml.safe_load(match.group(1))
        body = match.group(2)
        return fm, body
    except yaml.YAMLError as e:
        log_error("VALIDATOR", f"YAML parse error: {e}")
        return None, content


def _check_frontmatter(fm: dict | None) -> list[str]:
    """Validate frontmatter fields. Returns list of error messages."""
    errors = []

    if fm is None:
        return ["Frontmatter is missing or invalid YAML"]

    if not isinstance(fm, dict):
        return ["Frontmatter is not a valid YAML mapping"]

    for field in REQUIRED_FIELDS:
        if field not in fm or fm[field] is None:
            errors.append(f"Missing required field: '{field}'")

    # Check tags is a list
    if "tags" in fm and fm["tags"] is not None:
        if not isinstance(fm["tags"], list):
            errors.append("'tags' must be an array/list")
        elif len(fm["tags"]) < 2:
            errors.append("'tags' should have at least 2 items")

    # Check title is non-empty
    if "title" in fm and fm["title"] is not None:
        if not str(fm["title"]).strip():
            errors.append("'title' is empty")

    # Check description is non-empty
    if "description" in fm and fm["description"] is not None:
        if not str(fm["description"]).strip():
            errors.append("'description' is empty")

    return errors


def _check_body(body: str) -> list[str]:
    """Validate article body content. Returns list of error messages."""
    errors = []

    # Word count check
    words = body.split()
    word_count = len(words)
    if word_count < MIN_WORD_COUNT:
        errors.append(
            f"Content too short: {word_count} words (minimum {MIN_WORD_COUNT})"
        )

    # Check for unclosed JSX/MDX tags (basic check)
    open_tags = re.findall(r"<([A-Z][a-zA-Z]*)[^/>]*>", body)
    close_tags = re.findall(r"</([A-Z][a-zA-Z]*)>", body)

    for tag in open_tags:
        if tag not in close_tags:
            # Only warn for custom components, not standard HTML
            if tag[0].isupper():
                errors.append(f"Possibly unclosed MDX component: <{tag}>")

    # Check for broken code blocks
    code_block_count = body.count("```")
    if code_block_count % 2 != 0:
        errors.append("Unbalanced code blocks (odd number of ``` markers)")

    return errors


def validate_article(content: str) -> tuple[bool, list[str]]:
    """
    Validate a complete MDX article (frontmatter + body).
    Returns (is_valid, error_list).
    """
    log("VALIDATOR", "Validating article...")

    fm, body = _extract_frontmatter(content)
    errors = []

    # Validate frontmatter
    fm_errors = _check_frontmatter(fm)
    errors.extend(fm_errors)

    # Validate body
    body_errors = _check_body(body)
    errors.extend(body_errors)

    is_valid = len(errors) == 0

    if is_valid:
        word_count = len(body.split())
        log("VALIDATOR", f"Article valid ✓ ({word_count} words)")
    else:
        log_error("VALIDATOR", f"Validation failed with {len(errors)} error(s):")
        for err in errors:
            log_error("VALIDATOR", f"  - {err}")

    return is_valid, errors


if __name__ == "__main__":
    sample = """---
title: "Test Article"
pubDatetime: 2026-06-01T10:00:00+07:00
description: "A test article description"
tags:
  - test
  - sample
draft: false
---

## Hello World

This is a test article body. """ + "word " * 400

    valid, errs = validate_article(sample)
    print(f"Valid: {valid}, Errors: {errs}")
