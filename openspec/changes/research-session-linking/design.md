## Context

Research projects are managed in a standalone SQLite database (`~/.myassistant/research.db`) via the `research-db` MCP server. Myassistant sessions live in the main myassistant SQLite database. The two are currently independent.

Current `research_projects` schema:
- `id` INTEGER PK AUTOINCREMENT (research-db's own ID)
- `name`, `description`, `keywords`, `data_dir`, `status`, `created_at`, `updated_at`

Constraint: one myassistant directory = one research project. The `data_dir` corresponds to the myassistant working directory.

## Goals / Non-Goals

**Goals:**
- Link myassistant sessions to research projects so users can browse all sessions for a project
- Support optional phase/role metadata per session (literature review, experiment design, etc.)
- Keep myassistant core untouched — all changes confined to the MCP package

**Non-Goals:**
- Cross-session context passing (sessions are independent)
- Automatic session linking (user/manual only)
- Changes to myassistant session schema or agent module

## Schema Design

### `research_projects` (modified)
| Column                 | Type          | Constraint              |
|------------------------|---------------|-------------------------|
| id                     | INTEGER       | PK AUTOINCREMENT        |
| myassistant_project_id | TEXT          | UNIQUE, nullable        |
| name                   | TEXT          | NOT NULL                |
| description            | TEXT          | NOT NULL                |
| keywords               | TEXT          | NOT NULL                |
| data_dir               | TEXT          | NOT NULL                |
| status                 | TEXT          | NOT NULL DEFAULT 'active'|
| created_at             | TEXT          | NOT NULL                |
| updated_at             | TEXT          | NOT NULL                |

### `research_sessions` (new)
| Column       | Type    | Constraint                                      |
|--------------|---------|-------------------------------------------------|
| project_id   | INTEGER | NOT NULL, FK → research_projects.id, cascade delete |
| session_id   | TEXT    | NOT NULL                                        |
| phase        | TEXT    | nullable (e.g., "文献综述", "实验设计")          |
| notes        | TEXT    | nullable                                        |
| linked_at    | TEXT    | NOT NULL, default CURRENT_TIMESTAMP             |

Composite unique on `(project_id, session_id)`.

## Decisions

### 1. Separate `research_sessions` table (not JSON array)
A dedicated table allows efficient querying, filtering by phase, and future extensions. Storing session IDs as a JSON array in `research_projects` would require reading the full project record for any session-level operation.

### 2. `myassistant_project_id` on `research_projects` with UNIQUE constraint
One directory = one research project, so the mapping is 1:1. The UNIQUE constraint prevents accidental duplicate projects for the same directory. This field is added to existing rows as NULL; existing projects remain functional.

### 3. sql.js schema migration via PRAGMA check + conditional ALTER TABLE
The research-db uses sql.js (not a managed ORM). Schema changes happen at runtime in `initSchema()`. SQLite does not support `ALTER TABLE IF NOT EXISTS`, so we use `PRAGMA table_info(table_name)` to inspect existing columns, then conditionally run `ALTER TABLE ... ADD COLUMN` only if missing. The UNIQUE constraint on `myassistant_project_id` is applied via a separate `CREATE UNIQUE INDEX IF NOT EXISTS`. New tables use `CREATE TABLE IF NOT EXISTS`. All changes are additive and backward compatible — old clients simply won't see the new fields.

### 4. Session linking is purely manual via MCP tools
No lifecycle hooks, no automatic creation. The user (or research agent on behalf of the user) calls `link_session` explicitly.

## Risks / Trade-offs

[Risk] sql.js schema migration requires PRAGMA-based column existence check. → `PRAGMA table_info(table_name)` is a standard SQLite feature supported by all versions of sql.js. The `CREATE UNIQUE INDEX IF NOT EXISTS` approach handles the UNIQUE constraint separately, which works reliably and avoids SQLite's limitation on adding UNIQUE constraints via `ALTER TABLE ADD COLUMN`.

[Risk] User creates sessions in multiple directories for one research project. → By design, one directory = one project. If users need cross-project linking, that's a future enhancement.

[Risk] Stale session references (session deleted in myassistant but still in `research_sessions`). → No cascade; the MCP layer doesn't have access to delete myassistant sessions. The `list_project_sessions` tool should gracefully handle missing sessions.

## Migration Plan

1. `initSchema()` adds `myassistant_project_id` column via `ALTER TABLE`
2. `initSchema()` creates `research_sessions` table via `CREATE TABLE IF NOT EXISTS`
3. Existing `create_project`, `list_projects`, etc. continue to work unchanged
4. New tools registered in `index.ts` alongside existing tools
5. Rollback: simply remove the new `ALTER TABLE` / `CREATE TABLE` calls; no data loss since changes are additive

## Open Questions

None at this time.
