import { Layer } from "effect"
import { TuiConfig } from "./config/tui"
import { Npm } from "@myassistant-ai/core/npm"
import { Observability } from "@myassistant-ai/core/effect/observability"

export const CliLayer = Observability.layer.pipe(Layer.merge(TuiConfig.layer), Layer.provide(Npm.defaultLayer))
