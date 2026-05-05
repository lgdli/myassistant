// @ts-nocheck

import { MyAssistant } from "@myassistant-ai/core"
import { ReadTool } from "@myassistant-ai/core/tools"

const myassistant = MyAssistant.make({})

myassistant.tool.add(ReadTool)

myassistant.tool.add({
  name: "bash",
  schema: {
    type: "object",
    properties: {
      command: {
        type: "string",
        description: "The command to run.",
      },
    },
    required: ["command"],
  },
  execute(input, ctx) {},
})

myassistant.auth.add({
  provider: "openai",
  type: "api",
  value: process.env.OPENAI_API_KEY,
})

myassistant.agent.add({
  name: "build",
  permissions: [],
  model: {
    id: "gpt-5-5",
    provider: "openai",
    variant: "xhigh",
  },
})

const sessionID = await myassistant.session.create({
  agent: "build",
})

myassistant.subscribe((event) => {
  console.log(event)
})

await myassistant.session.prompt({
  sessionID,
  text: "hey what is up",
})

await myassistant.session.prompt({
  sessionID,
  text: "what is up with this",
  files: [
    {
      mime: "image/png",
      uri: "data:image/png;base64,xxxx",
    },
  ],
})

await myassistant.session.wait()

console.log(await myassistant.session.messages(sessionID))
