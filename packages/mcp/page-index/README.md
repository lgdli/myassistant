# PageIndex MCP

Local inference-based RAG MCP server using PageIndex.

## Tools

- `pageindex_create`: Create a PageIndex tree from a PDF document
- `pageindex_get_structure`: Get the document structure tree for LLM reasoning
- `pageindex_get_pages`: Get content from specific pages

## Configuration

Set environment variables:
- `OPENAI_API_KEY`: API key for LLM
- `OPENAI_BASE_URL`: OpenAI compatible API base URL
- `PAGEINDEX_MODEL`: Model to use (default: gpt-4o)

## Usage

```bash
python -m page_index_mcp
```