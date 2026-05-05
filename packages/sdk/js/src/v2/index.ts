export * from "./client.js"
export * from "./server.js"

import { createMyassistantClient } from "./client.js"
import { createMyassistantServer } from "./server.js"
import type { ServerOptions } from "./server.js"

export * as data from "./data.js"

export async function createOpencode(options?: ServerOptions) {
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
