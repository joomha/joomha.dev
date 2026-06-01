"""
generator.py — LLM-powered article generation via OpenRouter API.
Uses OpenAI SDK with model fallback chain and exponential backoff retry.
"""

import os
import time
from openai import OpenAI
from slugify import slugify
from utils import log, log_error, iso_now


# ─── Model Fallback Chain ────────────────────────────────────
MODELS = [
    "openai/gpt-oss-120b",
    "meta-llama/llama-4-maverick",
    "google/gemini-2.5-flash",
]

MAX_RETRIES = 3
BASE_DELAY = 2  # seconds, doubles each retry


# ─── System Prompt ───────────────────────────────────────────
SYSTEM_PROMPT = """Kamu adalah seorang tech blogger berpengalaman yang menulis untuk blog developer modern berbahasa Indonesia.

ATURAN PENULISAN:
- Tulis dalam Bahasa Indonesia yang natural dan santai
- Gaya tulisan: informatif, teknikal ringan, cocok untuk developer modern
- Gunakan variasi panjang kalimat — campur kalimat pendek dan panjang
- Berikan opini teknikal ringan berbasis observasi umum developer
- Hindari kalimat template AI (jangan mulai dengan "Dalam era..." atau "Di dunia modern...")
- Jangan terdengar seperti artikel SEO spam
- Hindari pengulangan berlebihan
- Jangan terlalu formal, tapi tetap profesional
- Gunakan kata-kata natural yang biasa dipakai developer Indonesia

STRUKTUR ARTIKEL WAJIB:
1. Intro hook yang menarik (1-2 paragraf)
2. Heading H2 dan H3 yang terstruktur
3. Bullet list untuk poin-poin penting
4. Contoh praktis (code snippet jika relevan)
5. Section FAQ (minimal 3 pertanyaan)
6. Conclusion yang ringkas

FORMAT OUTPUT:
- Panjang: 500-900 kata
- Format: MDX valid
- Jangan sertakan frontmatter — frontmatter akan ditambahkan secara otomatis
- Mulai langsung dari heading H2 atau paragraf intro
- Gunakan backtick untuk code inline dan code blocks dengan language tag"""


def _get_client() -> OpenAI:
    """Initialize OpenRouter client with API key from environment."""
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENROUTER_API_KEY not found in environment variables. "
            "Set it in .env (local) or GitHub Secrets (CI)."
        )
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )


def _build_user_prompt(topic_title: str) -> str:
    """Build the user prompt for article generation."""
    return f"""Tulis artikel blog tentang topik berikut:

TOPIK: {topic_title}

INSTRUKSI TAMBAHAN:
- Fokus pada insight praktis yang berguna untuk developer
- Sertakan contoh nyata atau code snippet jika relevan
- Buat FAQ section dengan 3-4 pertanyaan yang developer biasa tanyakan
- Akhiri dengan kesimpulan yang actionable
- Jangan copy-paste dari sumber lain, tulis dengan gaya kamu sendiri
- Tulis 500-900 kata"""


def _call_llm(client: OpenAI, model: str, topic_title: str) -> str | None:
    """Call a single LLM model with retry logic."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            log("GENERATOR", f"Calling {model} (attempt {attempt}/{MAX_RETRIES})...")

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": _build_user_prompt(topic_title)},
                ],
                max_tokens=4096,
                temperature=0.7,
            )

            content = response.choices[0].message.content
            if content and len(content.strip()) > 200:
                log("GENERATOR", f"Success with {model} ({len(content)} chars)")
                return content.strip()
            else:
                log_error("GENERATOR", f"Response too short from {model}")

        except Exception as e:
            log_error("GENERATOR", f"Error with {model} (attempt {attempt}): {e}")

        # Exponential backoff
        if attempt < MAX_RETRIES:
            delay = BASE_DELAY * (2 ** (attempt - 1))
            log("GENERATOR", f"Retrying in {delay}s...")
            time.sleep(delay)

    return None


def _build_frontmatter(topic_title: str, slug: str, tags: list[str]) -> str:
    """Build YAML frontmatter for the article."""
    pub_datetime = iso_now()
    # Clean title for YAML (escape quotes)
    safe_title = topic_title.replace('"', '\\"')

    # Generate a concise description from the title
    description = f"Pembahasan mendalam tentang {topic_title} — insight praktis untuk developer modern."
    if len(description) > 160:
        description = description[:157] + "..."

    tag_lines = "\n".join(f"  - {tag}" for tag in tags)

    return f"""---
title: "{safe_title}"
pubDatetime: {pub_datetime}
description: "{description}"
tags:
{tag_lines}
draft: false
featured: false
ogImage: "../../../assets/images/blog/{slug}.png"
lang: "id"
---"""


def _extract_tags(topic_title: str) -> list[str]:
    """Extract 2-5 relevant tags from the topic title."""
    tag_map = {
        "ai": "ai", "llm": "ai", "agent": "ai", "gpt": "ai",
        "machine learning": "ai", "deep learning": "ai",
        "react": "react", "nextjs": "react", "next.js": "react",
        "astro": "astro",
        "javascript": "javascript", "js": "javascript",
        "typescript": "typescript", "ts": "typescript",
        "css": "css", "tailwind": "css",
        "performance": "performance", "speed": "performance", "optimization": "performance",
        "frontend": "frontend", "ui": "frontend", "ux": "frontend",
        "backend": "backend", "api": "backend", "server": "backend",
        "nodejs": "nodejs", "node": "nodejs", "deno": "nodejs", "bun": "nodejs",
        "web": "web-development",
        "developer": "developer-productivity",
    }

    title_lower = topic_title.lower()
    found_tags = set()

    for keyword, tag in tag_map.items():
        if keyword in title_lower:
            found_tags.add(tag)

    # Ensure at least 2 tags
    if len(found_tags) < 2:
        found_tags.add("web-development")
    if len(found_tags) < 2:
        found_tags.add("developer-productivity")

    # Cap at 5 tags
    return sorted(list(found_tags))[:5]


def generate_article(topic_title: str) -> dict | None:
    """
    Generate a complete MDX article for the given topic.
    Tries models in fallback order. Returns dict with 'content', 'slug', 'title'
    or None if all models fail.
    """
    log("GENERATOR", f"Generating article for: '{topic_title}'")

    client = _get_client()
    slug = slugify(topic_title, max_length=60)
    tags = _extract_tags(topic_title)

    # Try each model in the fallback chain
    for model in MODELS:
        body = _call_llm(client, model, topic_title)
        if body:
            frontmatter = _build_frontmatter(topic_title, slug, tags)
            full_content = f"{frontmatter}\n\n{body}\n"

            return {
                "content": full_content,
                "slug": slug,
                "title": topic_title,
                "tags": tags,
                "model_used": model,
            }

        log_error("GENERATOR", f"All retries failed for {model}, trying next...")

    log_error("GENERATOR", "All models failed. Could not generate article.")
    return None


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    result = generate_article("Building AI Agents with Astro and TypeScript")
    if result:
        print(result["content"][:500])
        print(f"\n--- Slug: {result['slug']}, Model: {result['model_used']}")
