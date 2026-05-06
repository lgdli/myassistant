import { afterEach, describe, expect, test } from "bun:test"
import { Option, Redacted } from "effect"
import { Flag } from "@myassistant-ai/core/flag/flag"
import { ServerAuth } from "../../src/server/auth"

const original = {
  MYASSISTANT_SERVER_PASSWORD: Flag.MYASSISTANT_SERVER_PASSWORD,
  MYASSISTANT_SERVER_USERNAME: Flag.MYASSISTANT_SERVER_USERNAME,
}

afterEach(() => {
  Flag.MYASSISTANT_SERVER_PASSWORD = original.MYASSISTANT_SERVER_PASSWORD
  Flag.MYASSISTANT_SERVER_USERNAME = original.MYASSISTANT_SERVER_USERNAME
})

describe("ServerAuth", () => {
  test("does not emit auth headers without a password", () => {
    Flag.MYASSISTANT_SERVER_PASSWORD = undefined
    Flag.MYASSISTANT_SERVER_USERNAME = "alice"

    expect(ServerAuth.header()).toBeUndefined()
    expect(ServerAuth.headers()).toBeUndefined()
  })

  test("defaults to the myassistant username", () => {
    Flag.MYASSISTANT_SERVER_PASSWORD = "secret"
    Flag.MYASSISTANT_SERVER_USERNAME = undefined

    expect(ServerAuth.headers()).toEqual({
      Authorization: `Basic ${Buffer.from("myassistant:secret").toString("base64")}`,
    })
  })

  test("uses the configured username", () => {
    Flag.MYASSISTANT_SERVER_PASSWORD = "secret"
    Flag.MYASSISTANT_SERVER_USERNAME = "alice"

    expect(ServerAuth.headers()).toEqual({
      Authorization: `Basic ${Buffer.from("alice:secret").toString("base64")}`,
    })
  })

  test("prefers explicit credentials", () => {
    Flag.MYASSISTANT_SERVER_PASSWORD = "secret"
    Flag.MYASSISTANT_SERVER_USERNAME = "alice"

    expect(ServerAuth.headers({ password: "cli-secret", username: "bob" })).toEqual({
      Authorization: `Basic ${Buffer.from("bob:cli-secret").toString("base64")}`,
    })
  })

  test("validates decoded credentials against effect config", () => {
    const config = { password: Option.some("secret"), username: "alice" }

    expect(ServerAuth.required(config)).toBe(true)
    expect(ServerAuth.authorized({ username: "alice", password: Redacted.make("secret") }, config)).toBe(true)
    expect(ServerAuth.authorized({ username: "myassistant", password: Redacted.make("secret") }, config)).toBe(false)
  })
})
