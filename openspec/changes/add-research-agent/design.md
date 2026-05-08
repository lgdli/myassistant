# Design: Research Agent - Create Project Feature

## Overview

`research` agent 是 primary agent，专注于学术研究流程管理。本设计覆盖第一个功能：创建新研究项目。

## Architecture

```
用户 ──→ @research ──→ Agent (中文 prompt) ──→ MCP 工具 ──→ SQLite (~/.myassistant/research.db)
                    │                          │
                    │                          └──→ 文件系统 (mkdir raw/, dist/)
                    │
                    └──→ 中文响应
```

关键点：Agent 本身不实现任何 tool，仅通过 MCP 工具间接操作数据库和文件系统。

## Agent 注册

### 位置：`packages/myassistant/src/agent/agent.ts`

在 `agents` 记录中新增 `research` 条目，遵循 `build` 的模式：

```typescript
// 顶部导入 prompt
import PROMPT_RESEARCH from "./prompt/research.txt"

// agents 记录中新增：
research: {
  name: "research",
  description: "学术研究全流程管理助手，帮助创建和管理研究项目、检索文献、整理研究资料等。",
  options: {},
  permission: Permission.merge(
    defaults,
    Permission.fromConfig({
      question: "allow",
      plan_enter: "allow",
    }),
    user,
  ),
  mode: "primary",
  native: true,
  prompt: PROMPT_RESEARCH,
},
```

与 `build` agent 对比：
| 字段 | build | research |
|------|-------|----------|
| `name` | `"build"` | `"research"` |
| `description` | 英文 | 中文 |
| `permission` | `question: "allow"`, `plan_enter: "allow"` | 相同 |
| `mode` | `"primary"` | `"primary"` |
| `native` | `true` | `true` |
| `prompt` | 无（使用默认 system prompt） | `PROMPT_RESEARCH` |

**权限说明**：`Permission.merge(defaults, Permission.fromConfig({ question: "allow", plan_enter: "allow" }), user)` 与 `build` 完全一致，提供全权限操作。

## Agent Prompt

### 文件：`packages/myassistant/src/agent/prompt/research.txt`

纯中文，指导 agent 的行为和交互流程。内容结构：

1. **角色定义**：学术研究全流程管理助手
2. **当前功能**：创建新研究项目
3. **创建流程**：
   - 依次询问项目名称、研究目标与内容、关键词、资料保存目录
   - 确认信息后调用 MCP 工具创建
4. **数据目录说明**：
   - `raw/`：存放 AI 下载的论文和用户已有资料
   - `dist/`：存放 LLM + Agent 处理过的资料
5. **未来功能预告**：文献检索、笔记整理、写作辅助（尚未实现）
6. **错误处理指导**：目录不存在时提示用户重新选择

## 数据库操作

所有数据库操作通过 MCP 工具完成，agent prompt 中指导 agent 调用对应的 MCP 工具。

### MCP 工具需要提供的能力

| 操作 | SQL |
|------|-----|
| 建表（幂等） | `CREATE TABLE IF NOT EXISTS research_projects (...)` |
| 插入项目 | `INSERT INTO research_projects (name, description, keywords, data_dir) VALUES (?, ?, ?, ?)` |
| 查询项目 | `SELECT * FROM research_projects WHERE id = ?` |
| 列出所有项目 | `SELECT * FROM research_projects ORDER BY created_at DESC` |

数据库文件路径：`~/.myassistant/research.db`

**注意**：MCP 工具不是本次任务的交付物，由外部注册。Agent 注册时不依赖 MCP 的存在。

## 目录结构

创建项目时在用户指定目录下创建：

```
<用户指定目录>/
├── raw/    # AI 下载的论文 + 用户已有资料
└── dist/   # LLM + Agent 处理过的资料
```

- 如果 `raw/` 或 `dist/` 已存在，不报错，直接复用
- 通过 MCP 工具的文件系统操作能力创建

## Error Handling

- **目录不存在/无权限**：MCP 工具返回错误，agent 用中文提示用户并请求重新指定路径
- **数据库错误**：MCP 工具返回错误，agent 用中文表面给用户
- **必填字段缺失**：agent 在调用 MCP 前检查，不完整的请求不发起

## Implementation Steps

1. 在 `agent.ts` 顶部导入 `PROMPT_RESEARCH`，在 `agents` 记录中添加 `research` 条目
2. 创建 `agent/prompt/research.txt`，编写中文 prompt（包含角色定义 + 创建项目流程）
3. 验证 type checking：`bun typecheck`
