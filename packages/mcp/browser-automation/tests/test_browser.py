"""Integration tests for browser automation MCP server."""

import asyncio
import json
import sys
from pathlib import Path

import pytest
import pytest_asyncio


class EventBusMock:
    """Mock for bubus EventBus."""
    class MockEvent:
        def __init__(self, event):
            self._event = event
            self._result = None
        def __await__(self):
            yield
            return self
        async def event_result(self, raise_if_any=False, raise_if_none=False):
            return self._result
    def dispatch(self, event):
        return self.MockEvent(event)


class MockElement:
    node_id = 0
    backend_node_id = 0
    session_id = "mock-session"
    frame_id = None
    target_id = "mock-target-id"
    uuid = "mock-uuid"
    node_type = 1
    node_name = "a"
    node_value = "Click me"
    tag_name = "a"
    text = "Click me"
    attributes = {"href": "https://example.com/next"}
    is_clickable = True
    is_interactable = True
    is_scrollable = True
    is_visible = True
    absolute_position = None
    
    # Mock ax_node for text content
    class MockAXNode:
        name = "Click me"
        role = "link"
    ax_node = MockAXNode()

    def get_all_children_text(self, max_depth=2):
        return "child text"


class MockBrowserSession:
    """Mimics BrowserSession from browser-use."""
    def __init__(self):
        self.browser = self
        self.id = "test-browser-id"
        self._current_url = "about:blank"
        self._tabs = []
        self._is_open = True
        self.event_bus = EventBusMock()

    async def get_current_page_url(self):
        return self._current_url

    async def get_current_page_title(self):
        return "Test Page"

    async def get_browser_state_summary(self):
        DOMState = type('DOMState', (), {'selector_map': {0: MockElement(), 1: MockElement(), 2: MockElement()}})
        state = type('BrowserStateSummary', (), {'url': 'https://example.com', 'title': 'Example Domain', 'dom_state': DOMState(), 'screenshot': None, 'page_info': None})
        return state()

    async def get_dom_element_by_index(self, index):
        return MockElement()

    async def take_screenshot(self):
        return b"fake_image_data"

    async def kill(self):
        pass


class MockPageInfo:
    viewport_width = 1280
    viewport_height = 720
    page_width = 1280
    page_height = 2000
    scroll_x = 0
    scroll_y = 0


@pytest.mark.asyncio
async def test_server_initialization():
    """Verify the server module can be imported, has correct tools and config."""
    import os
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
    from browser_automation import server as server_mod
    from browser_automation import browser_manager as bm
    from browser_automation import config as cfg

    assert server_mod is not None
    assert bm is not None
    assert cfg is not None
    assert cfg.config.mcp_server_name == "browser-automation"

    tools = await server_mod.handle_list_tools()
    tool_names = [t.name for t in tools]
    assert "browser_navigate" in tool_names
    assert "browser_get_state" in tool_names
    assert "browser_click" in tool_names
    assert "browser_type" in tool_names
    assert "browser_screenshot" in tool_names
    assert "browser_execute_task" in tool_names
    assert "browser_close" in tool_names

    for tool in tools:
        assert tool.name, f"Tool missing name: {tool}"
        assert tool.description, f"Tool {tool.name} missing description"
        assert tool.inputSchema, f"Tool {tool.name} missing inputSchema"
        assert "type" in tool.inputSchema, f"Tool {tool.name} inputSchema missing 'type'"
        assert "properties" in tool.inputSchema, f"Tool {tool.name} inputSchema missing 'properties'"

    navigate_tool = [t for t in tools if t.name == "browser_navigate"][0]
    assert "url" in navigate_tool.inputSchema["properties"]
    assert navigate_tool.inputSchema["properties"]["url"]["type"] == "string"

    click_tool = [t for t in tools if t.name == "browser_click"][0]
    assert "index" in click_tool.inputSchema["properties"]
    assert click_tool.inputSchema["properties"]["index"]["type"] in ("number", "integer")

    type_tool = [t for t in tools if t.name == "browser_type"][0]
    assert "index" in type_tool.inputSchema["properties"]
    assert "text" in type_tool.inputSchema["properties"]

    # Verify config values match the intended defaults
    expected_llm_provider = os.getenv("BROWSER_LLM_PROVIDER", "ollama")
    assert cfg.config.llm_provider == expected_llm_provider
    expected_llm_model = os.getenv("BROWSER_LLM_MODEL", "qwen2.5-vl:7b")
    assert cfg.config.llm_model == expected_llm_model
    expected_openai_model = os.getenv("OPENAI_MODEL", "gpt-4o")
    assert cfg.config.openai_model == expected_openai_model
    expected_ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    assert cfg.config.ollama_base_url == expected_ollama_base_url


@pytest.mark.asyncio
async def test_navigate_and_get_state(monkeypatch):
    """Test that we can navigate to a page and get its state."""
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
    from browser_automation import server as server_mod
    from browser_automation import browser_manager as bm
    
    mock_browser = MockBrowserSession()
    
    async def mock_get_or_create_browser(browser_id=None):
        return mock_browser
    
    monkeypatch.setattr(bm.manager, "get_or_create_browser", mock_get_or_create_browser)
    
    result = await server_mod.handle_call_tool("browser_navigate", {"url": "https://example.com"})
    assert result is not None
    assert len(result.content) > 0
    assert result.content[0].type == "text"
    assert "Navigated" in result.content[0].text or "Error" in result.content[0].text
    
    state_result = await server_mod.handle_call_tool("browser_get_state", {})
    state = json.loads(state_result.content[0].text)
    assert "url" in state
    assert "title" in state
    assert "elements" in state


@pytest.mark.asyncio
async def test_end_to_end_flow(monkeypatch):
    """Full end-to-end test: navigate, get state, click, type, screenshot, close."""
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
    from browser_automation import server as server_mod
    from browser_automation import browser_manager as bm
    
    mock_browser = MockBrowserSession()
    
    async def mock_get_or_create_browser(browser_id=None):
        return mock_browser
    
    monkeypatch.setattr(bm.manager, "get_or_create_browser", mock_get_or_create_browser)
    
    nav_result = await server_mod.handle_call_tool("browser_navigate", {"url": "https://example.com"})
    assert nav_result.content[0].text.startswith("Navigated")
    
    state_result = await server_mod.handle_call_tool("browser_get_state", {})
    state = json.loads(state_result.content[0].text)
    assert len(state["elements"]) > 0
    
    click_result = await server_mod.handle_call_tool("browser_click", {"index": 0})
    assert click_result is not None
    assert len(click_result.content) > 0
    assert click_result.content[0].text.startswith("Clicked")
    
    type_result = await server_mod.handle_call_tool("browser_type", {"index": 1, "text": "hello"})
    assert type_result is not None
    assert len(type_result.content) > 0
    assert type_result.content[0].text.startswith("Typed")
    
    ss_result = await server_mod.handle_call_tool("browser_screenshot", {})
    assert ss_result is not None
    assert len(ss_result.content) > 0
    assert len(ss_result.content[0].text) > 0
    
    close_result = await server_mod.handle_call_tool("browser_close", {})
    assert close_result is not None
    assert len(close_result.content) > 0
    assert close_result.content[0].text == "Browser closed"


@pytest.mark.asyncio
async def test_error_handling(monkeypatch):
    """Test that errors in handlers are caught and returned properly."""
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
    from browser_automation import server as server_mod
    from browser_automation import browser_manager as bm
    
    async def mock_get_or_create_browser(browser_id=None):
        raise RuntimeError("simulated error")
    
    monkeypatch.setattr(bm.manager, "get_or_create_browser", mock_get_or_create_browser)
    
    result = await server_mod.handle_call_tool("browser_navigate", {"url": "https://example.com"})
    assert result.isError or "failed" in result.content[0].text.lower() or "error" in result.content[0].text.lower()


@pytest.mark.asyncio
async def test_unknown_tool(monkeypatch):
    """Test that unknown tool returns an error."""
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
    from browser_automation import server as server_mod
    
    result = await server_mod.handle_call_tool("browser_unknown", {})
    assert result.isError
    assert "unknown" in result.content[0].text.lower()


@pytest.mark.asyncio
async def test_click_nonexistent_element(monkeypatch):
    """Test clicking a non-existent element."""
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
    from browser_automation import server as server_mod
    from browser_automation import browser_manager as bm
    
    class MockSessionNoElement(MockBrowserSession):
        async def get_dom_element_by_index(self, index):
            return None
    
    mock_browser = MockSessionNoElement()
    
    async def mock_get_or_create_browser(browser_id=None):
        return mock_browser
    
    monkeypatch.setattr(bm.manager, "get_or_create_browser", mock_get_or_create_browser)
    
    result = await server_mod.handle_call_tool("browser_click", {"index": 999})
    assert "not found" in result.content[0].text.lower()


@pytest.mark.asyncio
async def test_type_nonexistent_element(monkeypatch):
    """Test typing into a non-existent element."""
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
    from browser_automation import server as server_mod
    from browser_automation import browser_manager as bm
    
    class MockSessionNoElement(MockBrowserSession):
        async def get_dom_element_by_index(self, index):
            return None
    
    mock_browser = MockSessionNoElement()
    
    async def mock_get_or_create_browser(browser_id=None):
        return mock_browser
    
    monkeypatch.setattr(bm.manager, "get_or_create_browser", mock_get_or_create_browser)
    
    result = await server_mod.handle_call_tool("browser_type", {"index": 999, "text": "hello"})
    assert "not found" in result.content[0].text.lower()
