const stage = process.env.SST_STAGE || "dev"

export default {
  url: stage === "production" ? "https://myassistant.ai" : `https://${stage}.myassistant.ai`,
  console: stage === "production" ? "https://myassistant.ai/auth" : `https://${stage}.myassistant.ai/auth`,
  email: "contact@anoma.ly",
  socialCard: "https://social-cards.sst.dev",
  github: "https://github.com/anomalyco/myassistant",
  discord: "https://myassistant.ai/discord",
  headerLinks: [
    { name: "app.header.home", url: "/" },
    { name: "app.header.docs", url: "/docs/" },
  ],
}
