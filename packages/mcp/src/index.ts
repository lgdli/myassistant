import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js"
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js"
import { z } from "zod/v4"
import {
  createProject,
  listProjects,
  getProject,
  updateProject,
  deleteProject,
  linkSession,
  unlinkSession,
  listProjectSessions,
} from "./sqlite.js"

const server = new McpServer({
  name: "research-db",
  version: "1.0.0",
})

server.registerTool(
  "create_project",
  {
    title: "Create New Research Project",
    description:
      "Create a new research project with name, description, keywords, and data directory. Automatically creates raw/ and dist/ subdirectories.",
    inputSchema: z.object({
      name: z.string().describe("Project name (required)"),
      description: z.string().describe("Research goal and content (required)"),
      keywords: z
        .array(z.string())
        .describe("Research keywords as an array of strings (required)"),
      data_dir: z.string().describe("Absolute path for research data directory (required)"),
      myassistant_project_id: z.string().optional().describe("Optional myassistant project ID for linking (unique)"),
    }),
  },
  async (args) => {
    try {
      const result = await createProject(
        args.name,
        args.description,
        args.keywords,
        args.data_dir,
        args.myassistant_project_id,
      )
      return {
        content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
      }
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify({ error: error instanceof Error ? error.message : String(error) }, null, 2),
          },
        ],
        isError: true,
      }
    }
  },
)

server.registerTool(
  "list_projects",
  {
    title: "List Research Projects",
    description: "List all research projects, optionally filtered by status.",
    inputSchema: z.object({
      status: z
        .enum(["active", "archived"])
        .optional()
        .describe("Filter projects by status (active or archived)"),
    }),
  },
  async (args) => {
    try {
      const results = await listProjects(args.status)
      return {
        content: [{ type: "text", text: JSON.stringify(results, null, 2) }],
      }
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify({ error: error instanceof Error ? error.message : String(error) }, null, 2),
          },
        ],
        isError: true,
      }
    }
  },
)

server.registerTool(
  "get_project",
  {
    title: "Get Research Project",
    description: "Get detailed information about a specific research project by ID.",
    inputSchema: z.object({
      id: z.number().describe("Project ID (required)"),
    }),
  },
  async (args) => {
    try {
      const result = await getProject(args.id)
      if (!result) {
        return {
          content: [{ type: "text", text: JSON.stringify({ error: `Project with ID ${args.id} not found` }, null, 2) }],
          isError: true,
        }
      }
      return {
        content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
      }
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify({ error: error instanceof Error ? error.message : String(error) }, null, 2),
          },
        ],
        isError: true,
      }
    }
  },
)

server.registerTool(
  "update_project",
  {
    title: "Update Research Project",
    description:
      "Update an existing research project. Only provided fields will be updated.",
    inputSchema: z.object({
      id: z.number().describe("Project ID (required)"),
      name: z.string().optional().describe("New project name"),
      description: z.string().optional().describe("New research goal and content"),
      keywords: z.array(z.string()).optional().describe("New research keywords"),
      status: z.enum(["active", "archived"]).optional().describe("New status (active or archived)"),
    }),
  },
  async (args) => {
    try {
      const updates: Record<string, unknown> = {}
      if (args.name !== undefined) updates.name = args.name
      if (args.description !== undefined) updates.description = args.description
      if (args.keywords !== undefined) updates.keywords = args.keywords
      if (args.status !== undefined) updates.status = args.status

      const result = await updateProject(args.id, updates)
      return {
        content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
      }
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify({ error: error instanceof Error ? error.message : String(error) }, null, 2),
          },
        ],
        isError: true,
      }
    }
  },
)

server.registerTool(
  "delete_project",
  {
    title: "Delete Research Project",
    description:
      "Delete a research project by ID. Note: This only removes the database record, not the data directory.",
    inputSchema: z.object({
      id: z.number().describe("Project ID (required)"),
    }),
  },
  async (args) => {
    try {
      const result = await deleteProject(args.id)
      return {
        content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
      }
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify({ error: error instanceof Error ? error.message : String(error) }, null, 2),
          },
        ],
        isError: true,
      }
    }
  },
)

server.registerTool(
  "link_session",
  {
    title: "Link Session to Research Project",
    description: "Link a myassistant session to a research project with optional phase and notes.",
    inputSchema: z.object({
      project_id: z.number().describe("Research project ID (required)"),
      session_id: z.string().describe("Myassistant session ID (required)"),
      phase: z.string().optional().describe("Phase of research (e.g., 文献综述, 实验设计)"),
      notes: z.string().optional().describe("Additional notes about this session"),
    }),
  },
  async (args) => {
    try {
      const result = await linkSession(args.project_id, args.session_id, args.phase, args.notes)
      return {
        content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
      }
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify({ error: error instanceof Error ? error.message : String(error) }, null, 2),
          },
        ],
        isError: true,
      }
    }
  },
)

server.registerTool(
  "unlink_session",
  {
    title: "Unlink Session from Research Project",
    description: "Remove a session association from a research project.",
    inputSchema: z.object({
      project_id: z.number().describe("Research project ID (required)"),
      session_id: z.string().describe("Myassistant session ID (required)"),
    }),
  },
  async (args) => {
    try {
      const result = await unlinkSession(args.project_id, args.session_id)
      return {
        content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
      }
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify({ error: error instanceof Error ? error.message : String(error) }, null, 2),
          },
        ],
        isError: true,
      }
    }
  },
)

server.registerTool(
  "list_project_sessions",
  {
    title: "List Project Sessions",
    description: "List all sessions linked to a research project.",
    inputSchema: z.object({
      project_id: z.number().describe("Research project ID (required)"),
    }),
  },
  async (args) => {
    try {
      const results = await listProjectSessions(args.project_id)
      return {
        content: [{ type: "text", text: JSON.stringify(results, null, 2) }],
      }
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify({ error: error instanceof Error ? error.message : String(error) }, null, 2),
          },
        ],
        isError: true,
      }
    }
  },
)

async function main() {
  const transport = new StdioServerTransport()
  await server.connect(transport)
  console.error("research-db MCP server started successfully")
}

main().catch((error) => {
  console.error("Failed to start MCP server:", error)
  process.exit(1)
})
