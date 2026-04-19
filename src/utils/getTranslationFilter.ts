import type { CollectionEntry } from "astro:content";

/**
 * Filters a list of posts so that paired translations (same translationGroupId)
 * only appear once in listing pages (homepage, /posts archive, etc.)
 *
 * Rules:
 * - If a post has NO translationGroupId → always show it.
 * - If a post IS in a translation group and its lang is "id" → always show it
 *   (Indonesian is the default/priority language).
 * - If a post IS in a translation group and its lang is "en" → only show it
 *   when there is NO matching "id" version (i.e. the article is English-only).
 */
export function filterListingPosts(
  posts: CollectionEntry<"blog">[]
): CollectionEntry<"blog">[] {
  return posts.filter((post) => {
    const { translationGroupId, lang } = post.data;

    // No translation group → show the post normally
    if (!translationGroupId) return true;

    // Indonesian version → always prioritised in listing
    if (lang === "id") return true;

    // English version → only show if there is no Indonesian counterpart
    const hasIdVersion = posts.some(
      (p) =>
        p.data.translationGroupId === translationGroupId &&
        p.data.lang === "id"
    );

    return !hasIdVersion;
  });
}

/**
 * Given the current post, finds its translation counterpart (if any)
 * from the full collection.
 */
export function findTranslation(
  currentPost: CollectionEntry<"blog">,
  allPosts: CollectionEntry<"blog">[]
): CollectionEntry<"blog"> | undefined {
  const { translationGroupId, lang } = currentPost.data;
  if (!translationGroupId) return undefined;

  return allPosts.find(
    (p) =>
      p.data.translationGroupId === translationGroupId &&
      p.data.lang !== lang &&
      !p.data.draft
  );
}
