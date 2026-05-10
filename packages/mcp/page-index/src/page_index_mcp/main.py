import os
import sys
import json
import concurrent.futures
from pathlib import Path

os.environ.setdefault('LITELLM_LOCAL_MODEL_COST_MAP', 'True')

from mcp.server import Server
from mcp.server import NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types
import anyio

# Debug: print environment on startup
print(f"[page-index] OPENAI_BASE_URL: {os.getenv('OPENAI_BASE_URL', 'NOT SET')}", file=sys.stderr)
print(f"[page-index] PAGEINDEX_MODEL: {os.getenv('PAGEINDEX_MODEL', 'NOT SET')}", file=sys.stderr)
print(f"[page-index] LITELLM_MODEL_COST_MAP: {os.getenv('LITELLM_MODEL_COST_MAP', 'NOT SET')}", file=sys.stderr)


DEFAULT_MODEL = os.getenv("PAGEINDEX_MODEL", "gpt-4o")

server = Server("page-index-mcp")


def _normalize_model(model: str) -> str:
    """Add 'openai/' prefix for OpenAI-compatible APIs when needed."""
    if not model:
        return model
    if "/" in model:
        return model
    base_url = os.getenv("OPENAI_BASE_URL", "")
    if base_url and not base_url.endswith("/openai"):
        return f"openai/{model}"
    return model


def get_client(model: str | None = None):
    from .client import PageIndexClient
    
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not configured")
    if base_url:
        os.environ["OPENAI_BASE_URL"] = base_url
    
    final_model = _normalize_model(model or DEFAULT_MODEL)
    
    return PageIndexClient(
        api_key=api_key,
        model=final_model,
    )


def _count_nodes(structure):
    count = 1
    for child in structure.get("children", []):
        count += _count_nodes(child)
    return count


def _parse_pages(pages_str: str) -> list[int]:
    result = []
    for part in pages_str.split(','):
        part = part.strip()
        if '-' in part:
            start, end = part.split('-', 1)
            result.extend(range(int(start.strip()), int(end.strip()) + 1))
        else:
            result.append(int(part))
    return sorted(set(result))


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="pageindex_create",
            description="Create a PageIndex tree from a PDF document",
            inputSchema={
                "type": "object",
                "properties": {
                    "pdf_path": {"type": "string", "description": "Path to the PDF file"},
                    "output_dir": {"type": "string", "description": "Directory to save the tree JSON file"},
                    "model": {"type": "string", "description": "Optional LLM model to use"},
                },
                "required": ["pdf_path", "output_dir"],
            },
        ),
        types.Tool(
            name="pageindex_get_structure",
            description="Get the document structure tree for LLM reasoning",
            inputSchema={
                "type": "object",
                "properties": {
                    "tree_path": {"type": "string", "description": "Path to the tree JSON file"},
                },
                "required": ["tree_path"],
            },
        ),
        types.Tool(
            name="pageindex_get_pages",
            description="Get content from specific pages",
            inputSchema={
                "type": "object",
                "properties": {
                    "tree_path": {"type": "string", "description": "Path to the tree JSON file"},
                    "pages": {"type": "string", "description": "Page range like '5-7', '3,8', or '12'"},
                },
                "required": ["tree_path", "pages"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, object]) -> list[types.TextContent]:
    try:
        if name == "pageindex_create":
            result = _pageindex_create_sync(arguments)
        elif name == "pageindex_get_structure":
            result = _pageindex_get_structure(arguments)
        elif name == "pageindex_get_pages":
            result = _pageindex_get_pages(arguments)
        else:
            result = {"error": f"Unknown tool: {name}", "status": "error"}
        
        return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]
    except Exception as e:
        return [types.TextContent(type="text", text=json.dumps({"error": str(e), "status": "error"}))]


def _pageindex_create_sync(args: dict[str, object]) -> dict[str, object]:
    pdf_path = os.path.abspath(os.path.expanduser(str(args["pdf_path"])))
    output_dir = os.path.abspath(os.path.expanduser(str(args["output_dir"])))
    model = str(args["model"]) if args.get("model") else None
    
    if not os.path.exists(pdf_path):
        return {"error": f"PDF file not found: {pdf_path}", "status": "error"}
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    client = get_client(model)
    
    doc_id = client.index(pdf_path, mode="pdf")
    
    tree = json.loads(client.get_document_structure(doc_id))
    
    tree_path = os.path.join(output_dir, f"{Path(pdf_path).stem}_tree.json")
    with open(tree_path, "w", encoding="utf-8") as f:
        json.dump({
            "doc_id": doc_id,
            "doc_name": tree.get("doc_name", ""),
            "doc_description": tree.get("doc_description", ""),
            "structure": tree.get("structure", {}),
            "pages": client.documents.get(doc_id, {}).get("pages", []),
        }, f, ensure_ascii=False, indent=2)
    
    node_count = _count_nodes(tree.get("structure", {}))
    
    return {
        "tree_path": tree_path,
        "node_count": node_count,
        "doc_name": tree.get("doc_name", ""),
        "status": "success",
    }


def _pageindex_get_structure(args: dict[str, object]) -> dict[str, object]:
    tree_path = os.path.abspath(os.path.expanduser(str(args["tree_path"])))
    
    if not os.path.exists(tree_path):
        return {"error": f"Tree file not found: {tree_path}", "status": "error"}
    
    with open(tree_path, "r", encoding="utf-8") as f:
        tree_data = json.load(f)
    
    return {
        "structure": tree_data.get("structure", {}),
        "doc_name": tree_data.get("doc_name", ""),
        "doc_description": tree_data.get("doc_description", ""),
        "status": "success",
    }


def _pageindex_get_pages(args: dict[str, object]) -> dict[str, object]:
    tree_path = os.path.abspath(os.path.expanduser(str(args["tree_path"])))
    pages_str = str(args["pages"])
    
    if not os.path.exists(tree_path):
        return {"error": f"Tree file not found: {tree_path}", "status": "error"}
    
    with open(tree_path, "r", encoding="utf-8") as f:
        tree_data = json.load(f)
    
    pages_data = tree_data.get("pages", [])
    
    page_nums = _parse_pages(pages_str)
    
    content_parts = []
    for page_num in page_nums:
        for page in pages_data:
            if page.get("page") == page_num:
                content_parts.append(f"=== Page {page_num} ===\n{page.get('content', '')}")
                break
    
    return {
        "content": "\n\n".join(content_parts),
        "status": "success",
    }


async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="page-index-mcp",
                server_version="0.0.1",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    anyio.run(main)