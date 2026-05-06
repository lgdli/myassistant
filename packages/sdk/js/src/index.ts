export * from "./client.js"
export * from "./server.js"

import { createMyassistantClient } from "./client.js"
import { createMyassistantServer } from "./server.js"
import type { ServerOptions } from "./server.js"

export async function createMyassistant(options?: ServerOptions) {
  const server = await createMyassistantServer({
    ...options,
  })

  const client = createMyassistantClient({
    baseUrl: server.url,
  })

  return {
    client,
    server,
  }
}

// Alias for backwards compatibility
export { createMyassistant as createOpencode }
