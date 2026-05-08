## Why

Research agent sessions currently have no way to track which sessions belong to which research project. Users need to manually remember which conversations relate to which project, and there's no structured way to browse or review all sessions within a research context.

## What Changes

- Add `myassistant_project_id` (TEXT UNIQUE) to `research_projects` table, linking each research project to its corresponding myassistant project directory
- Add `research_sessions` table for explicitly linking myassistant sessions to research projects
- Add three new MCP tools: `link_session`, `unlink_session`, `list_project_sessions`
- Update `create_project` MCP tool to accept optional `myassistant_project_id` parameter

## Capabilities

### New Capabilities
- `research-session-linking`: Link myassistant sessions to research projects with optional phase metadata (literature review, experiment design, etc.), managed entirely through MCP tools with no changes to myassistant core

### Modified Capabilities
(None)

## Impact

- `packages/mcp/src/sqlite.ts` — new table schema, new functions for session linking, `createProject` signature change
- `packages/mcp/src/index.ts` — three new MCP tool registrations
- `~/.myassistant/research.db` — new columns and table added at runtime via `CREATE TABLE IF NOT EXISTS`
- No changes to myassistant core, agent module, or session module
