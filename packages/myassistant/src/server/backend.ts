import { Flag } from "@myassistant-ai/core/flag/flag"
import { InstallationChannel, InstallationVersion } from "@myassistant-ai/core/installation/version"

export type Backend = "effect-httpapi" | "hono"

export type Selection = {
  backend: Backend
  reason: "env" | "stable" | "explicit"
}

export type Attributes = ReturnType<typeof attributes>

export function select(): Selection {
  if (Flag.MYASSISTANT_EXPERIMENTAL_HTTPAPI) return { backend: "effect-httpapi", reason: "env" }
  return { backend: "hono", reason: "stable" }
}

export function attributes(selection: Selection): Record<string, string> {
  return {
    "myassistant.server.backend": selection.backend,
    "myassistant.server.backend.reason": selection.reason,
    "myassistant.installation.channel": InstallationChannel,
    "myassistant.installation.version": InstallationVersion,
  }
}

export function force(selection: Selection, backend: Backend): Selection {
  return {
    backend,
    reason: selection.backend === backend ? selection.reason : "explicit",
  }
}
