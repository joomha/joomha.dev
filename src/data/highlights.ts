/**
 * Highlights Data
 *
 * This is the data source for the "story highlight" circles on the homepage.
 * To add a new highlight:
 *   1. Add an image to public/highlights/ (recommended: square, 200x200 PNG)
 *   2. Add an entry to the HIGHLIGHTS array below
 *   3. Push to GitHub — done!
 */

export interface Highlight {
  /** Display title below the circle */
  title: string;
  /** Image path relative to public/, e.g. "/highlights/my-project.png" */
  image: string;
  /** URL to the related blog post (internal link) */
  postUrl?: string;
  /** External action URL (GitHub, Play Store, website, etc.) */
  actionUrl?: string;
  /** Label for the external action, e.g. "GitHub", "Play Store", "Website" */
  actionLabel?: string;
}

export const HIGHLIGHTS: Highlight[] = [
  {
    title: "ScholarGuard",
    image: "/highlights/scholarguard.png",
    postUrl: "/posts/2026/hello-world",
    actionUrl: "https://github.com/joomha",
    actionLabel: "GitHub",
  },
  {
    title: "BSC Website",
    image: "/highlights/bsc-website.png",
    postUrl: "/posts/2026/hello-world",
    actionUrl: "https://github.com/joomha",
    actionLabel: "GitHub",
  },
  { title: "Dummy 3", image: "/highlights/scholarguard.png", postUrl: "#", actionUrl: "#", actionLabel: "Link" },
  { title: "Dummy 4", image: "/highlights/bsc-website.png", postUrl: "#", actionUrl: "#", actionLabel: "Link" },
  { title: "Dummy 5", image: "/highlights/scholarguard.png", postUrl: "#", actionUrl: "#", actionLabel: "Link" },
  { title: "Dummy 6", image: "/highlights/bsc-website.png", postUrl: "#", actionUrl: "#", actionLabel: "Link" },
  { title: "Dummy 7", image: "/highlights/scholarguard.png", postUrl: "#", actionUrl: "#", actionLabel: "Link" },
  { title: "Dummy 8", image: "/highlights/bsc-website.png", postUrl: "#", actionUrl: "#", actionLabel: "Link" },
  { title: "Dummy 9", image: "/highlights/scholarguard.png", postUrl: "#", actionUrl: "#", actionLabel: "Link" },
  { title: "Dummy 10", image: "/highlights/bsc-website.png", postUrl: "#", actionUrl: "#", actionLabel: "Link" },
  { title: "Dummy 11", image: "/highlights/scholarguard.png", postUrl: "#", actionUrl: "#", actionLabel: "Link" },
  { title: "Dummy 12", image: "/highlights/bsc-website.png", postUrl: "#", actionUrl: "#", actionLabel: "Link" },
  { title: "Dummy 13", image: "/highlights/scholarguard.png", postUrl: "#", actionUrl: "#", actionLabel: "Link" },
  { title: "Dummy 14", image: "/highlights/bsc-website.png", postUrl: "#", actionUrl: "#", actionLabel: "Link" },
  { title: "Dummy 15", image: "/highlights/scholarguard.png", postUrl: "#", actionUrl: "#", actionLabel: "Link" },
  { title: "Dummy 16", image: "/highlights/bsc-website.png", postUrl: "#", actionUrl: "#", actionLabel: "Link" },
  { title: "Dummy 17", image: "/highlights/scholarguard.png", postUrl: "#", actionUrl: "#", actionLabel: "Link" },
  { title: "Dummy 18", image: "/highlights/bsc-website.png", postUrl: "#", actionUrl: "#", actionLabel: "Link" },
  { title: "Dummy 19", image: "/highlights/scholarguard.png", postUrl: "#", actionUrl: "#", actionLabel: "Link" },
  { title: "Dummy 20", image: "/highlights/bsc-website.png", postUrl: "#", actionUrl: "#", actionLabel: "Link" },
];
