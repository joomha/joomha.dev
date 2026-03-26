import type { APIRoute } from "astro";

export const GET: APIRoute = async () => {
  const markdownContent = `# Ahmad Jumhadi (@joomha)

Personal space of Ahmad Jumhadi. Developer interested in Data Science, AI, and SEO.

## Navigation

- [About](/about.md)
- [Recent Posts](/posts.md)
- [Archives](/archives.md)
- [RSS Feed](/rss.xml)

## Links

- X/Twitter: [@joomha](https://x.com/joomha)
- GitHub: [@joomha](https://github.com/joomha)
- LinkedIn: [joomha](https://www.linkedin.com/in/joomha)
- Email: hi@joomha.dev

---

*This is the markdown-only version of joomha.dev. Visit [joomha.dev](https://joomha.dev) for the full experience.*`;

  return new Response(markdownContent, {
    status: 200,
    headers: {
      "Content-Type": "text/markdown; charset=utf-8",
      "Cache-Control": "public, max-age=3600",
    },
  });
};
