declare global {
  const MYASSISTANT_VERSION: string
  const MYASSISTANT_CHANNEL: string
}

export const InstallationVersion = typeof MYASSISTANT_VERSION === "string" ? MYASSISTANT_VERSION : "local"
export const InstallationChannel = typeof MYASSISTANT_CHANNEL === "string" ? MYASSISTANT_CHANNEL : "local"
export const InstallationLocal = InstallationChannel === "local"
