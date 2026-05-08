import { describe, it, expect, beforeAll, afterAll } from "bun:test"
import fs from "fs"
import path from "path"

const TEST_DB = path.join(import.meta.dirname, ".test.db")

process.env.RESEARCH_DB_PATH = TEST_DB

async function importFresh() {
  delete require.cache[require.resolve("./sqlite")]
  const mod = await import("./sqlite.ts")
  return mod
}

beforeAll(() => {
  if (fs.existsSync(TEST_DB)) fs.unlinkSync(TEST_DB)
})

afterAll(() => {
  if (fs.existsSync(TEST_DB)) fs.unlinkSync(TEST_DB)
})

describe("create_project", () => {
  it("creates project without myassistant_project_id", async () => {
    const { createProject } = await importFresh()
    const result = await createProject("Test", "desc", ["kw"], "/tmp/test")
    expect(result.message).toBe("项目创建成功")
    expect(result.id).toBe(1)
  })

  it("creates project with myassistant_project_id", async () => {
    const { createProject } = await importFresh()
    const result = await createProject("Linked", "desc", ["kw"], "/tmp/linked", "ma-proj-1")
    expect(result.message).toBe("项目创建成功")
    expect(result.id).toBe(2)
  })

  it("rejects duplicate myassistant_project_id", async () => {
    const { createProject } = await importFresh()
    const result = await createProject("Dup", "desc", ["kw"], "/tmp/dup", "ma-proj-1")
    expect(result.error).toContain("已被占用")
  })
})

describe("link_session", () => {
  it("links session to project", async () => {
    const m = await importFresh()
    const result = await m.linkSession(1, "sess-abc", "文献综述", "initial")
    expect(result.message).toBe("会话关联成功")
    expect(result.project_id).toBe(1)
    expect(result.session_id).toBe("sess-abc")
  })

  it("rejects duplicate link", async () => {
    const m = await importFresh()
    const result = await m.linkSession(1, "sess-abc", "实验设计")
    expect(result.error).toContain("已关联")
  })

  it("rejects non-existent project", async () => {
    const m = await importFresh()
    const result = await m.linkSession(999, "sess-xyz")
    expect(result.error).toContain("不存在")
  })
})

describe("unlink_session", () => {
  it("unlinks existing session", async () => {
    const m = await importFresh()
    const result = await m.unlinkSession(1, "sess-abc")
    expect(result.message).toBe("会话解关联成功")
  })

  it("rejects unlinking non-existent association", async () => {
    const m = await importFresh()
    const result = await m.unlinkSession(1, "sess-abc")
    expect(result.error).toContain("未关联")
  })
})

describe("list_project_sessions", () => {
  it("returns sessions for project", async () => {
    const m = await importFresh()
    await m.linkSession(1, "sess-1")
    await m.linkSession(1, "sess-2", "实验设计")
    const sessions = await m.listProjectSessions(1)
    expect(sessions.length).toBe(2)
    const ids = sessions.map((s: any) => s.session_id)
    expect(ids).toContain("sess-1")
    expect(ids).toContain("sess-2")
  })

  it("returns empty for project with no sessions", async () => {
    const m = await importFresh()
    const sessions = await m.listProjectSessions(2)
    expect(sessions.length).toBe(0)
  })
})

describe("get_project includes myassistant_project_id", () => {
  it("returns myassistant_project_id when set", async () => {
    const m = await importFresh()
    const project = await m.getProject(2)
    expect(project).not.toBeNull()
    expect(project!.myassistant_project_id).toBe("ma-proj-1")
  })

  it("returns null myassistant_project_id when not set", async () => {
    const m = await importFresh()
    const project = await m.getProject(1)
    expect(project).not.toBeNull()
    expect(project!.myassistant_project_id).toBe(null)
  })
})
