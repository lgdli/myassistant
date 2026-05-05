import { $ } from "bun"

await $`bun ./scripts/copy-icons.ts ${process.env.MYASSISTANT_CHANNEL ?? "dev"}`

await $`cd ../myassistant && bun script/build-node.ts`
