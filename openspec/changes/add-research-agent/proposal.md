# Proposal: Add Research Assistant Agent

## Summary

Add a new primary agent called `research` (display name: "research assistant") that implements a full-cycle personal academic research workflow. This change implements the first step: creating a new research project.

## Motivation

用户需要一个专用的 agent 来管理学术研究全流程 —— 从项目创建到文献检索、笔记整理、写作辅助。`research` agent 提供结构化的方式来组织和管理研究活动。

## Scope

### In Scope

- 在 `agent.ts` 中注册新 primary agent `research`，权限与 `build` 一致
- 创建中文 agent prompt 文件 `agent/prompt/research.txt`
- Agent 通过外部 MCP 工具（后续注册）完成 SQLite 操作和目录创建
- 项目创建时收集：项目名称、研究目标与内容、关键词、资料保存目录

### Out of Scope

- MCP 数据库工具的注册与实现（外部依赖，后续完成）
- 新建独立的 research tool（通过 MCP 间接操作）
- 文献检索与导入（后续步骤）
- 文献阅读与笔记（后续步骤）
- 论文写作辅助（后续步骤）
- 综述生成（后续步骤）

## User Flow

1. 用户通过 `@research` 切换到 research agent
2. Agent 用中文欢迎用户，介绍功能
3. 用户说"创建新项目"或类似指令
4. Agent 依次询问项目信息：
   - **项目名称**（必填）
   - **研究目标与内容**（必填）
   - **关键词**（必填，逗号分隔）
   - **资料保存目录**（必填，用户指定本地路径）
5. Agent 调用 MCP 工具创建项目：
   - 在 `~/.myassistant/research.db` 插入记录
   - 在指定目录下创建 `raw/` 和 `dist/` 子目录
6. Agent 返回创建确认信息

## Key Decisions

| 决策项 | 选择 |
|--------|------|
| Agent 内部名称 | `research` |
| 显示名称 | `research assistant` |
| Mode | `primary` |
| 默认权限 | 与 `build` agent 一致（全权限） |
| Prompt 语言 | 中文 |
| SQLite 存储路径 | `~/.myassistant/research.db`（独立数据库文件） |
| 数据库操作方式 | 通过外部 MCP 工具（当前未注册，后续由其他任务完成） |
| 资料目录结构 | 用户指定根目录 + `raw/`（原始资料）、`dist/`（处理后资料） |

## Database Schema

```sql
CREATE TABLE research_projects (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  description TEXT NOT NULL,
  keywords TEXT NOT NULL,  -- JSON array
  data_dir TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'active',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
```

数据库文件路径：`~/.myassistant/research.db`
建表由 MCP 工具负责执行（`CREATE TABLE IF NOT EXISTS`）。

## Risks

- MCP 工具可用性：当前 MCP 数据库工具尚未注册，agent 注册后需等待 MCP 就绪
- 目录权限：用户指定的目录需要读写权限
- 目录已存在：`raw/` 或 `dist/` 已存在时不报错，直接复用
