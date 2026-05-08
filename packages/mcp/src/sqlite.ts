import initSqlJs, { Database } from "sql.js"
import fs from "fs"
import path from "path"
import { fileURLToPath } from "url"

const PKG_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..")
const DB_PATH = process.env.RESEARCH_DB_PATH ?? path.join(process.env.HOME ?? ".", ".myassistant", "research.db")

const SQL = await initSqlJs({
  locateFile: (file) => `file://${path.join(PKG_ROOT, "node_modules", "sql.js", "dist", file)}`,
})

// MCP tool calls run in the same subprocess but may re-import the module.
// We use disk-backed persistence: load → execute → save → close for each call.
function withDb<T>(fn: (db: Database) => T): T {
  const dbDir = path.dirname(DB_PATH)
  if (!fs.existsSync(dbDir)) {
    fs.mkdirSync(dbDir, { recursive: true })
  }

  let buffer: Uint8Array | undefined
  if (fs.existsSync(DB_PATH)) {
    buffer = new Uint8Array(fs.readFileSync(DB_PATH))
  }

  const db = new SQL.Database(buffer)
  initSchema(db)
  const result = fn(db)
  saveToDisk(db)
  db.close()
  return result
}

function initSchema(db: Database): void {
  db.run(`
    CREATE TABLE IF NOT EXISTS research_projects (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      description TEXT NOT NULL,
      keywords TEXT NOT NULL,
      data_dir TEXT NOT NULL,
      status TEXT NOT NULL DEFAULT 'active',
      created_at TEXT NOT NULL,
      updated_at TEXT NOT NULL
    )
  `)
}

function saveToDisk(db: Database): void {
  const data = db.export()
  fs.writeFileSync(DB_PATH, new Uint8Array(data))
}

// sql.js exec returns rows with this shape
type ExecResult = { columns: string[]; values: unknown[][] }

function formatExecResult(result: ExecResult): Record<string, unknown>[] {
  return result.values.map((row) => {
    const obj: Record<string, unknown> = {}
    for (let i = 0; i < result.columns.length; i++) {
      obj[result.columns[i]] = row[i]
    }
    return obj
  })
}

export async function createProject(
  name: string,
  description: string,
  keywords: string[] | string,
  data_dir: string,
): Promise<Record<string, unknown>> {
  return withDb((db) => {
    const keywordsStr = Array.isArray(keywords) ? JSON.stringify(keywords) : keywords
    const now = new Date().toISOString()

    db.run(
      `INSERT INTO research_projects (name, description, keywords, data_dir, created_at, updated_at)
       VALUES (?, ?, ?, ?, ?, ?)`,
      [name, description, keywordsStr, data_dir, now, now],
    )

    const lastId = db.exec("SELECT last_insert_rowid() as id")[0].values[0][0]
    return { id: lastId, message: "项目创建成功" }
  })
}

export async function listProjects(status?: string): Promise<Record<string, unknown>[]> {
  return withDb((db) => {
    if (status) {
      const res = db.exec(`SELECT * FROM research_projects WHERE status = ? ORDER BY created_at DESC`, [status])
      if (res.length === 0) return []
      return formatExecResult(res[0])
    }

    const res = db.exec(`SELECT * FROM research_projects ORDER BY created_at DESC`)
    if (res.length === 0) return []
    return formatExecResult(res[0])
  })
}

export async function getProject(id: number): Promise<Record<string, unknown> | null> {
  return withDb((db) => {
    const res = db.exec(`SELECT * FROM research_projects WHERE id = ?`, [id])
    if (res.length === 0 || res[0].values.length === 0) return null
    return formatExecResult(res[0])[0]
  })
}

export async function updateProject(
  id: number,
  updates: { name?: string; description?: string; keywords?: string[] | string; status?: string },
): Promise<Record<string, unknown>> {
  return withDb((db) => {
    const existing = db.exec(`SELECT * FROM research_projects WHERE id = ?`, [id])
    if (existing.length === 0 || existing[0].values.length === 0) {
      return { error: `项目 ${id} 不存在` }
    }

    const fields: string[] = []
    const values: (string | number)[] = []

    if (updates.name !== undefined) {
      fields.push(`name = ?`)
      values.push(updates.name)
    }

    if (updates.description !== undefined) {
      fields.push(`description = ?`)
      values.push(updates.description)
    }

    if (updates.keywords !== undefined) {
      const keywordsStr = Array.isArray(updates.keywords) ? JSON.stringify(updates.keywords) : updates.keywords
      fields.push(`keywords = ?`)
      values.push(keywordsStr)
    }

    if (updates.status !== undefined) {
      fields.push(`status = ?`)
      values.push(updates.status)
    }

    if (fields.length === 0) {
      return { error: "没有提供可更新的字段" }
    }

    fields.push(`updated_at = ?`)
    values.push(new Date().toISOString())

    db.run(`UPDATE research_projects SET ${fields.join(", ")} WHERE id = ?`, [...values, id])
    return { id, message: "项目更新成功" }
  })
}

export async function deleteProject(id: number): Promise<Record<string, unknown>> {
  return withDb((db) => {
    const existing = db.exec(`SELECT * FROM research_projects WHERE id = ?`, [id])
    if (existing.length === 0 || existing[0].values.length === 0) {
      return { error: `项目 ${id} 不存在` }
    }

    db.run(`DELETE FROM research_projects WHERE id = ?`, [id])
    return { id, message: "项目删除成功" }
  })
}
