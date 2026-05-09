"""Main entry point for the browser automation MCP server.

This module implements the MCP protocol server that exposes browser
automation capabilities as tools consumable by myassistant and other clients.
"""
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime
from pathlib import Path

from mcp.server import Server
from mcp.server import NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

from browser_automation.config import config
from browser_automation.tools import TOOL_HANDLERS

log = logging.getLogger("browser_automation.server")


# ---------------------------------------------------------------------------
# MCP Server Definition
# ---------------------------------------------------------------------------

server = Server("browser-automation")

# ---------------------------------------------------------------------------
# MCP Server Definition
# ---------------------------------------------------------------------------

server = Server("browser-automation")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List all available browser automation tools."""
    return [
        types.Tool(
            name="browser_navigate",
            description="Navigate the browser to a specified URL and return the new page state.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "The URL to navigate to (required)"},
                },
                "required": ["url"],
            },
        ),
        types.Tool(
            name="browser_click",
            description="Click a page element by its DOM index. Use browser_get_state first to obtain current elements.",
            inputSchema={
                "type": "object",
                "properties": {
                    "index": {
                        "type": "integer",
                        "description": "DOM index of the element to click (from browser_get_state)",
                    },
                },
                "required": ["index"],
            },
        ),
        types.Tool(
            name="browser_type",
            description="Type text into an input field identified by its DOM index.",
            inputSchema={
                "type": "object",
                "properties": {
                    "index": {"type": "integer", "description": "DOM index of element (from browser_get_state)"},
                    "text": {"type": "string", "description": "The text to type into the element"},
                },
                "required": ["index", "text"],
            },
        ),
        types.Tool(
            name="browser_screenshot",
            description="Take a screenshot of the current browser page. Returns the base64-encoded image.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="browser_get_state",
            description="Get the current interactive elements on the page with their DOM indices, tags, text, and attributes.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="browser_scroll",
            description="Scroll the page up or down.",
            inputSchema={
                "type": "object",
                "properties": {
                    "direction": {
                        "type": "string",
                        "enum": ["up", "down"],
                        "description": "Direction to scroll (up or down). Defaults to down.",
                        "default": "down",
                    },
                },
            },
        ),
        types.Tool(
            name="browser_go_back",
            description="Go back to the previous page in browser history.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="browser_execute_task",
            description="Execute a high-level browser automation task using an LLM agent. Requires a local Ollama instance or OpenAI API key.",
            inputSchema={
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "Natural language task description (e.g. 'Go to google.com and search for cats')",
                    },
                    "model": {
                        "type": "string",
                        "description": "Optional LLM model override (e.g. 'gpt-4o', 'qwen2.5:7b'). Uses config default if not provided.",
                    },
                },
                "required": ["task"],
            },
        ),
        types.Tool(
            name="browser_close",
            description="Close the browser session. Use this when done to free resources.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> types.CallToolResult:
    """Route a tool call to the appropriate handler."""
    if not arguments:
        arguments = {}
    handler = TOOL_HANDLERS.get(name)
    if handler is None:
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=f"Unknown tool: {name}")],
            isError=True,
        )
    try:
        raw_result = await handler(**arguments)
        if isinstance(raw_result, list):
            # Handler returned list[types.TextContent] directly
            return types.CallToolResult(
                content=raw_result,
                isError=False,
            )
        # Handler returned dict format {"content": [...], "isError": ...}
        content_raw: list[dict] = raw_result.get("content", [])
        is_error = raw_result.get("isError", False) or any(
            c.get("isError", False) for c in content_raw if isinstance(c, dict)
        )
        content: list[types.TextContent | types.ImageContent | types.EmbeddedResource] = []
        for c in content_raw:
            content.append(
                types.TextContent(type="text", text=c.get("text", ""))
            )
        return types.CallToolResult(content=content, isError=is_error)
    except Exception as e:
        log.exception("tool handler error")
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=f"Handler error: {e}")],
            isError=True,
        ) 




async def main() -> None:
    """Start the MCP server over stdio."""
    log_dir = Path(config.log_dir or Path(__file__).resolve().parent / "logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "browser-automation.log"

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s"))

    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.INFO)
    stderr_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s"))

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        handlers=[file_handler, stderr_handler],
    )

    log.info("Browser Automation MCP server starting...")
    log.info(f"Log file: {log_file}")
    log.info(f"Headless mode: {config.headless}")
    log.info(f"LLM provider: {config.llm_provider} (model: {config.llm_model if config.llm_provider == 'ollama' else config.openai_model})")
    if config.openai_api_key:
        log.info(f"OpenAI key configured, available as fallback")
    if config.ollama_base_url:
        log.info(f"Ollama endpoint: {config.ollama_base_url}")

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="browser-automation",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    import anyio
    anyio.run(main)
