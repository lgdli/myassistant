## 1. Schema Migration

- [ ] 1.1 Add `myassistant_project_id TEXT UNIQUE` to `research_projects` via `ALTER TABLE` in `initSchema()`
- [ ] 1.2 Add `research_sessions` table to `initSchema()` via `CREATE TABLE IF NOT EXISTS`
- [ ] 1.3 Add unique index on `(project_id, session_id)` in `research_sessions`

## 2. Database Functions (sqlite.ts)

- [ ] 2.1 Update `createProject()` to accept optional `myassistant_project_id` parameter
- [ ] 2.2 Implement `linkSession(projectId, sessionId, phase?, notes?)` function
- [ ] 2.3 Implement `unlinkSession(projectId, sessionId)` function
- [ ] 2.4 Implement `listProjectSessions(projectId)` function

## 3. MCP Tool Registrations (index.ts)

- [ ] 3.1 Register `link_session` tool with Zod schema validation
- [ ] 3.2 Register `unlink_session` tool with Zod schema validation
- [ ] 3.3 Register `list_project_sessions` tool with Zod schema validation
- [ ] 3.4 Update `create_project` tool to accept optional `myassistant_project_id`

## 4. Tests

- [ ] 4.1 Test `create_project` with and without `myassistant_project_id`
- [ ] 4.2 Test `link_session` success path
- [ ] 4.3 Test `link_session` duplicate detection
- [ ] 4.4 Test `unlink_session` success and not-found cases
- [ ] 4.5 Test `list_project_sessions` with results and empty case
