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
];
