"""MCP tool handlers for browser automation."""
from __future__ import annotations

import json
import logging
from typing import Any

import mcp.types as types
from browser_use.browser.events import (
    ClickElementEvent,
    ClickCoordinateEvent,
    NavigateToUrlEvent,
    TypeTextEvent,
    ScrollEvent,
    GoBackEvent,
)

from .browser_manager import BrowserManager, manager as default_manager


def _get_manager(bm: BrowserManager | None) -> BrowserManager:
    """Return the given manager or the default singleton."""
    return bm if bm is not None else default_manager


async def handle_navigate(
    url: str,
    browser_manager: BrowserManager | None = None,
    browser_id: str | None = None,
) -> list[types.TextContent]:
    """Navigate to a URL."""
    bm = _get_manager(browser_manager)
    try:
        wrapper = await bm.get_or_create_browser(browser_id)
        session = wrapper.browser
        event = session.event_bus.dispatch(NavigateToUrlEvent(url=url, new_tab=False))
        await event
        return [
            types.TextContent(
                type="text",
                text=f"Navigated to {url}",
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"Navigation failed: {str(e)}",
            )
        ]


async def handle_get_state(
    browser_manager: BrowserManager = None,
    browser_id: str | None = None,
) -> list[types.TextContent]:
    """Get the current page state with interactive elements."""
    try:
        bm = _get_manager(browser_manager)
        wrapper = await bm.get_or_create_browser(browser_id)
        session = wrapper.browser

        url = await session.get_current_page_url()
        title = await session.get_current_page_title()

        state = await session.get_browser_state_summary()

        elements_data = []
        if state.dom_state and state.dom_state.selector_map:
            for idx, element in state.dom_state.selector_map.items():
                attrs = {}
                if element.attributes:
                    attrs = {
                        k: str(v) for k, v in element.attributes.items()
                        if v is not None
                    }
                # Get text from accessibility node (ax_node.name) or node_value
                text_content = ""
                if element.ax_node and element.ax_node.name:
                    text_content = element.ax_node.name
                elif element.node_value:
                    text_content = element.node_value
                    
                elements_data.append({
                    "index": idx,
                    "tag": element.node_name if element.node_name else "",
                    "text": text_content,
                    "attributes": attrs,
                    "is_visible": element.is_visible if element.is_visible else True,
                    "is_scrollable": element.is_scrollable if element.is_scrollable else False,
                })

        return [
            types.TextContent(
                type="text",
                text=json.dumps({
                    "url": url,
                    "title": title,
                    "elements_count": len(elements_data),
                    "elements": elements_data,
                    "screenshot": state.screenshot if state.screenshot else None,
                }),
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=json.dumps({"error": str(e)}),
            )
        ]


async def handle_click(
    index: int,
    browser_manager: BrowserManager = None,
    browser_id: str | None = None,
    coordinate_x: int | None = None,
    coordinate_y: int | None = None,
) -> list[types.TextContent]:
    """Click an element by index or at viewport coordinates."""
    try:
        bm = _get_manager(browser_manager)
        wrapper = await bm.get_or_create_browser(browser_id)
        session = wrapper.browser

        if coordinate_x is not None and coordinate_y is not None:
            event = session.event_bus.dispatch(
                ClickCoordinateEvent(coordinate_x=coordinate_x, coordinate_y=coordinate_y)
            )
            await event
            return [
                types.TextContent(
                    type="text",
                    text=f"Clicked at coordinates ({coordinate_x}, {coordinate_y})",
                )
            ]

        element = await session.get_dom_element_by_index(index)
        if not element:
            return [
                types.TextContent(
                    type="text",
                    text=f"Element with index {index} not found",
                )
            ]

        event = session.event_bus.dispatch(ClickElementEvent(node=element))
        await event
        return [
            types.TextContent(
                type="text",
                text=f"Clicked element at index {index}",
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"Click failed: {str(e)}",
            )
        ]


async def handle_type(
    index: int,
    text: str,
    browser_manager: BrowserManager = None,
    browser_id: str | None = None,
) -> list[types.TextContent]:
    """Type text into an input field."""
    try:
        bm = _get_manager(browser_manager)
        wrapper = await bm.get_or_create_browser(browser_id)
        session = wrapper.browser

        element = await session.get_dom_element_by_index(index)
        if not element:
            return [
                types.TextContent(
                    type="text",
                    text=f"Element with index {index} not found",
                )
            ]

        event = session.event_bus.dispatch(TypeTextEvent(node=element, text=text))
        await event
        return [
            types.TextContent(
                type="text",
                text=f"Typed '{text}' into element at index {index}",
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"Type failed: {str(e)}",
            )
        ]


async def handle_screenshot(
    browser_manager: BrowserManager = None,
    browser_id: str | None = None,
) -> list[types.TextContent]:
    """Take a screenshot of the current page."""
    try:
        bm = _get_manager(browser_manager)
        wrapper = await bm.get_or_create_browser(browser_id)
        session = wrapper.browser

        screenshot_bytes = await session.take_screenshot()
        import base64
        screenshot_b64 = base64.b64encode(screenshot_bytes).decode() if isinstance(screenshot_bytes, bytes) else screenshot_bytes

        return [
            types.TextContent(
                type="text",
                text=screenshot_b64,
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"Screenshot failed: {str(e)}",
            )
        ]


async def handle_scroll(
    direction: str,
    browser_manager: BrowserManager = None,
    browser_id: str | None = None,
) -> list[types.TextContent]:
    """Scroll the page up or down."""
    try:
        bm = _get_manager(browser_manager)
        wrapper = await bm.get_or_create_browser(browser_id)
        session = wrapper.browser

        scroll_direction = direction.lower() if direction else "down"
        event = session.event_bus.dispatch(ScrollEvent(direction=scroll_direction, amount=500))
        await event
        return [
            types.TextContent(
                type="text",
                text=f"Scrolled {direction}",
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"Scroll failed: {str(e)}",
            )
        ]


async def handle_go_back(
    browser_manager: BrowserManager = None,
    browser_id: str | None = None,
) -> list[types.TextContent]:
    """Go back to the previous page."""
    try:
        bm = _get_manager(browser_manager)
        wrapper = await bm.get_or_create_browser(browser_id)
        session = wrapper.browser

        event = session.event_bus.dispatch(GoBackEvent())
        await event
        return [
            types.TextContent(
                type="text",
                text=f"Navigated back",
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"Go back failed: {str(e)}",
            )
        ]


async def handle_execute_task(
    task: str,
    browser_manager: BrowserManager = None,
    browser_id: str | None = None,
    model: str | None = None,
) -> list[types.TextContent]:
    """Use LLM-powered agent to execute a complex browser task."""
    try:
        from browser_use import Agent
        from browser_use.llm.ollama.chat import ChatOllama
        from browser_use.llm.openai.chat import ChatOpenAI
        from browser_use.llm.anthropic.chat import ChatAnthropic

        from .config import config as app_config

        bm = _get_manager(browser_manager)
        wrapper = await bm.get_or_create_browser(browser_id)
        session = wrapper.browser

        llm_provider = app_config.llm_provider
        if model:
            if model.startswith("gpt"):
                llm = ChatOpenAI(model=model, api_key=app_config.openai_api_key, base_url=app_config.openai_base_url)
            elif model.startswith("claude"):
                llm = ChatAnthropic(model=model, api_key=app_config.anthropic_api_key)
            elif "/" in model:
                llm = ChatOllama(model=model, base_url=app_config.ollama_base_url)
            else:
                llm = ChatOpenAI(model=model, api_key=app_config.openai_api_key, base_url=app_config.openai_base_url)
        else:
            if llm_provider == "ollama":
                llm = ChatOllama(model=app_config.llm_model, base_url=app_config.ollama_base_url)
            elif llm_provider == "openai":
                llm = ChatOpenAI(model=app_config.openai_model, api_key=app_config.openai_api_key, base_url=app_config.openai_base_url)
            elif llm_provider == "anthropic":
                llm = ChatAnthropic(model=app_config.anthropic_model, api_key=app_config.anthropic_api_key)
            else:
                llm = ChatOpenAI(model=app_config.llm_model, api_key=app_config.openai_api_key, base_url=app_config.openai_base_url)

        agent = Agent(
            task=task,
            llm=llm,
            browser=session,
            use_vision=True,
        )

        history = await agent.run()

        result = {
            "success": history.is_successful(),
            "final_result": history.final_result(),
            "steps_count": len(history),
            "errors": history.errors(),
        }

        return [
            types.TextContent(
                type="text",
                text=json.dumps(result),
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=json.dumps({"error": str(e), "success": False}),
            )
        ]


async def handle_close_browser(
    browser_manager: BrowserManager = None,
    browser_id: str | None = None,
) -> list[types.TextContent]:
    """Close the browser session."""
    try:
        bm = _get_manager(browser_manager)
        if browser_id:
            await bm.close_browser(browser_id)
        else:
            await bm.close_all()
        return [types.TextContent(type="text", text="Browser closed")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Close failed: {str(e)}")]
    

TOOL_HANDLERS: dict[str, callable] = {
    "browser_navigate": handle_navigate,
    "browser_click": handle_click,
    "browser_type": handle_type,
    "browser_screenshot": handle_screenshot,
    "browser_get_state": handle_get_state,
    "browser_execute_task": handle_execute_task,
    "browser_close": handle_close_browser,
    "browser_scroll": handle_scroll,
    "browser_go_back": handle_go_back,
}
