# Tasks: Add Research Agent

## 1. 创建 agent prompt 文件

在 `packages/myassistant/src/agent/prompt/research.txt` 创建中文 system prompt：
- 角色定义：学术研究全流程管理助手
- 当前功能：创建新研究项目
- 创建流程：依次询问名称、目标与内容、关键词、资料保存目录
- 目录结构说明：raw/ 和 dist/ 的用途
- 错误处理指导：目录无权限、字段缺失等场景
- 未来功能预告：文献检索、笔记整理、写作辅助

## 2. 注册 research agent

在 `packages/myassistant/src/agent/agent.ts`：
- 顶部添加 `import PROMPT_RESEARCH from "./prompt/research.txt"`
- 在 `agents` 记录中添加 `research` 条目（参照 build 模式）
- name: "research", mode: "primary", native: true
- permission 与 build 一致
- prompt: PROMPT_RESEARCH

## 3. 验证

- `cd packages/myassistant && bun typecheck` 确认类型通过
