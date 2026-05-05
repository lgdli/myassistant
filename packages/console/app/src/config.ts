/**
 * Application-wide constants and configuration
 */
export const config = {
  // Base URL
  baseUrl: "https://myassistant.ai",

  // GitHub
  github: {
    repoUrl: "https://github.com/anomalyco/myassistant",
    starsFormatted: {
      compact: "150K",
      full: "150,000",
    },
  },

  // Social links
  social: {
    twitter: "https://x.com/myassistant",
    discord: "https://discord.gg/myassistant",
  },

  // Static stats (used on landing page)
  stats: {
    contributors: "850",
    commits: "11,000",
    monthlyUsers: "6.5M",
  },
} as const
