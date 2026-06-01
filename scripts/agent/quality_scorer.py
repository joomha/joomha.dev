"""
quality_scorer.py — Scores article quality across multiple dimensions.
Returns a 1-10 score; articles scoring < 7 should be regenerated.
"""

import re
from utils import log


def _readability_score(body: str) -> float:
    """
    Score readability based on sentence variety and paragraph structure.
    Returns 0.0 - 1.0
    """
    sentences = re.split(r"[.!?。]+", body)
    sentences = [s.strip() for s in sentences if s.strip()]

    if not sentences:
        return 0.2

    # Sentence length variety
    lengths = [len(s.split()) for s in sentences]
    if not lengths:
        return 0.3

    avg_len = sum(lengths) / len(lengths)
    variance = sum((l - avg_len) ** 2 for l in lengths) / len(lengths)

    # Good readability: avg sentence 10-20 words, with variety
    score = 0.0

    # Average length score
    if 10 <= avg_len <= 20:
        score += 0.4
    elif 7 <= avg_len <= 25:
        score += 0.25
    else:
        score += 0.1

    # Variance score (higher variety = better)
    if variance > 20:
        score += 0.3
    elif variance > 10:
        score += 0.2
    else:
        score += 0.1

    # Paragraph count (split by double newlines)
    paragraphs = [p.strip() for p in body.split("\n\n") if p.strip()]
    if len(paragraphs) >= 5:
        score += 0.3
    elif len(paragraphs) >= 3:
        score += 0.2
    else:
        score += 0.1

    return min(score, 1.0)


def _seo_score(body: str, title: str = "", description: str = "") -> float:
    """
    Score SEO quality based on heading usage, description length, etc.
    Returns 0.0 - 1.0
    """
    score = 0.0

    # H2/H3 headings present
    h2_count = len(re.findall(r"^## ", body, re.MULTILINE))
    h3_count = len(re.findall(r"^### ", body, re.MULTILINE))

    if h2_count >= 3:
        score += 0.3
    elif h2_count >= 2:
        score += 0.2
    elif h2_count >= 1:
        score += 0.1

    if h3_count >= 1:
        score += 0.1

    # Description length (50-160 chars is ideal for meta descriptions)
    if description:
        desc_len = len(description)
        if 50 <= desc_len <= 160:
            score += 0.2
        elif 30 <= desc_len <= 200:
            score += 0.1

    # Title length (30-70 chars ideal)
    if title:
        title_len = len(title)
        if 30 <= title_len <= 70:
            score += 0.2
        elif 20 <= title_len <= 90:
            score += 0.1

    # Internal linking / external references
    link_count = len(re.findall(r"\[.*?\]\(.*?\)", body))
    if link_count >= 2:
        score += 0.1
    elif link_count >= 1:
        score += 0.05

    # Bold/emphasis usage
    emphasis_count = len(re.findall(r"\*\*.*?\*\*", body))
    if emphasis_count >= 3:
        score += 0.1
    elif emphasis_count >= 1:
        score += 0.05

    return min(score, 1.0)


def _technical_depth_score(body: str) -> float:
    """
    Score technical depth based on code blocks and technical terms.
    Returns 0.0 - 1.0
    """
    score = 0.0

    # Code blocks
    code_blocks = len(re.findall(r"```", body)) // 2
    if code_blocks >= 3:
        score += 0.4
    elif code_blocks >= 1:
        score += 0.25
    else:
        score += 0.05

    # Inline code
    inline_code = len(re.findall(r"`[^`]+`", body))
    if inline_code >= 5:
        score += 0.2
    elif inline_code >= 2:
        score += 0.1

    # Technical terms
    tech_terms = [
        "api", "framework", "library", "component", "function",
        "class", "module", "package", "deploy", "build",
        "runtime", "compiler", "bundler", "server", "client",
        "database", "query", "middleware", "hook", "state",
        "render", "virtual dom", "hydration", "ssr", "ssg",
        "cdn", "cache", "docker", "ci/cd", "git",
    ]
    body_lower = body.lower()
    term_count = sum(1 for t in tech_terms if t in body_lower)
    if term_count >= 8:
        score += 0.4
    elif term_count >= 4:
        score += 0.25
    elif term_count >= 2:
        score += 0.15

    return min(score, 1.0)


def _originality_score(body: str) -> float:
    """
    Score originality based on repetition detection.
    Returns 0.0 - 1.0
    """
    words = body.lower().split()
    if not words:
        return 0.3

    # Check for repeated phrases (trigrams)
    trigrams = [" ".join(words[i:i+3]) for i in range(len(words) - 2)]
    if not trigrams:
        return 0.5

    unique_trigrams = len(set(trigrams))
    total_trigrams = len(trigrams)
    uniqueness_ratio = unique_trigrams / total_trigrams

    if uniqueness_ratio >= 0.9:
        return 1.0
    elif uniqueness_ratio >= 0.8:
        return 0.8
    elif uniqueness_ratio >= 0.7:
        return 0.6
    elif uniqueness_ratio >= 0.6:
        return 0.4
    else:
        return 0.2


def _structure_score(body: str) -> float:
    """
    Score article structure based on required elements.
    Returns 0.0 - 1.0
    """
    score = 0.0

    # Has H2 headings
    if re.search(r"^## ", body, re.MULTILINE):
        score += 0.2

    # Has H3 headings
    if re.search(r"^### ", body, re.MULTILINE):
        score += 0.1

    # Has bullet lists
    if re.search(r"^[\-\*] ", body, re.MULTILINE):
        score += 0.15

    # Has FAQ section
    body_lower = body.lower()
    if "faq" in body_lower or "pertanyaan" in body_lower or "tanya" in body_lower:
        score += 0.2

    # Has conclusion
    if ("kesimpulan" in body_lower or "penutup" in body_lower
            or "conclusion" in body_lower or "rangkuman" in body_lower):
        score += 0.15

    # Has intro (first paragraph before first heading)
    first_heading = re.search(r"^## ", body, re.MULTILINE)
    if first_heading and first_heading.start() > 50:
        score += 0.1

    # Numbered lists
    if re.search(r"^\d+\. ", body, re.MULTILINE):
        score += 0.1

    return min(score, 1.0)


def score_article(content: str, title: str = "", description: str = "") -> dict:
    """
    Score an article across 5 dimensions. Returns a dict with individual
    scores and a final weighted score (1-10 scale).

    If the final score < 7, the article should be regenerated.
    """
    log("QUALITY", "Scoring article quality...")

    # Extract body (skip frontmatter)
    body = content
    fm_match = re.match(r"^---\s*\n.*?\n---\s*\n(.*)$", content, re.DOTALL)
    if fm_match:
        body = fm_match.group(1)

    # Individual scores (0.0 - 1.0)
    readability = _readability_score(body)
    seo = _seo_score(body, title, description)
    technical = _technical_depth_score(body)
    originality = _originality_score(body)
    structure = _structure_score(body)

    # Weighted average (scale to 1-10)
    weights = {
        "readability": 0.20,
        "seo": 0.15,
        "technical_depth": 0.25,
        "originality": 0.20,
        "structure": 0.20,
    }

    weighted = (
        readability * weights["readability"]
        + seo * weights["seo"]
        + technical * weights["technical_depth"]
        + originality * weights["originality"]
        + structure * weights["structure"]
    )

    # Scale to 1-10
    final_score = round(1 + weighted * 9, 1)

    result = {
        "readability": round(readability * 10, 1),
        "seo": round(seo * 10, 1),
        "technical_depth": round(technical * 10, 1),
        "originality": round(originality * 10, 1),
        "structure": round(structure * 10, 1),
        "final_score": final_score,
        "pass": final_score >= 7.0,
    }

    log("QUALITY", f"Scores: readability={result['readability']}, "
        f"seo={result['seo']}, technical={result['technical_depth']}, "
        f"originality={result['originality']}, structure={result['structure']}")
    log("QUALITY", f"Final score: {final_score}/10 "
        f"({'PASS ✓' if result['pass'] else 'FAIL ✗ (regenerate)'})")

    return result


if __name__ == "__main__":
    sample_body = """## Introduction

This is a sample article about building web applications.

### Why This Matters

Modern **frontend** development requires understanding of multiple tools and frameworks.

- React for UI components
- TypeScript for type safety
- Astro for static site generation

```javascript
const app = createApp();
app.use(router);
```

## FAQ

**Q: What is the best framework?**
A: It depends on your use case.

**Q: Should I learn TypeScript?**
A: Absolutely, it improves developer productivity.

**Q: Is SSR important?**
A: For SEO-heavy sites, yes.

## Kesimpulan

Choose the right tool for the right job. """ + "word " * 300

    scores = score_article(f"---\ntitle: Test\n---\n\n{sample_body}", "Test Article", "A test description")
    print(scores)
