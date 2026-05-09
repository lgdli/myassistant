"""Browser session management.

Manages one or more browser instances via the browser-use library.
Supports lazy initialization, idle-timeout cleanup, and multi-session tagging.
Uses browser-use event buses for all browser operations.
"""
from __future__ import annotations

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4

from browser_use.browser.session import BrowserSession as Browser
from browser_use.browser.events import (
    ClickElementEvent,
    NavigateToUrlEvent,
    TypeTextEvent,
    ScrollEvent,
    GoBackEvent,
)

from .config import config
from .models import PageState, Element as ElementInfo

logger = logging.getLogger(__name__)


class BrowserSessionWrapper:
    """Wraps a Browser session with metadata for management."""

    def __init__(self, browser_id: str, browser: Browser):
        self.browser_id = browser_id
        self.browser = browser
        self.created_at = time.time()
        self.last_active_at = time.time()

    def touch(self) -> None:
        self.last_active_at = time.time()

    @property
    def idle_seconds(self) -> float:
        return time.time() - self.last_active_at


class BrowserManager:
    """
    Manages browser instances.
    Supports single-instance mode (default) for simplicity, with
    the ability to scale to multiple concurrent sessions.
    """

    def __init__(self):
        self._sessions: dict[str, BrowserSessionWrapper] = {}
        self._lock = asyncio.Lock()

    async def get_or_create_browser(
        self, browser_id: Optional[str] = None
    ) -> BrowserSessionWrapper:
        async with self._lock:
            if browser_id and browser_id in self._sessions:
                wrapper = self._sessions[browser_id]
                wrapper.touch()
                return wrapper

            if not browser_id and len(self._sessions) > 0:
                bid = next(iter(self._sessions.keys()))
                wrapper = self._sessions[bid]
                wrapper.touch()
                return wrapper

            new_id = browser_id or str(uuid4())
            logger.info(f"Creating new browser session: {new_id}")
            browser = await self._create_browser()
            wrapper = BrowserSessionWrapper(new_id, browser)
            self._sessions[new_id] = wrapper
            return wrapper

    async def _create_browser(self) -> Browser:
        import os
        os.environ.setdefault("BROWSER_USE_DISABLE_EXTENSIONS", "1")
        
        extension_path = os.path.expanduser("~/.config/browseruse/extensions/ublock")
        chrome_args = []
        if os.path.isdir(extension_path):
            chrome_args.append(f"--load-extension={extension_path}")
            logger.info(f"Loading local extension from: {extension_path}")
        
        browser = Browser(
            headless=config.headless,
            user_data_dir=config.browser_data_dir,
            args=chrome_args if chrome_args else None,
        )
        await browser.start()
        return browser

    async def close_browser(self, browser_id: str) -> None:
        async with self._lock:
            wrapper = self._sessions.pop(browser_id, None)
            if wrapper:
                logger.info(f"Closing browser session: {browser_id}")
                await wrapper.browser.kill()

    async def close_all(self) -> None:
        async with self._lock:
            for bid in list(self._sessions.keys()):
                await self.close_browser(bid)

    async def cleanup_idle_sessions(self) -> None:
        async with self._lock:
            now = time.time()
            to_remove = []
            for bid, wrapper in self._sessions.items():
                if wrapper.idle_seconds > config.browser_idle_timeout_seconds:
                    to_remove.append(bid)
            for bid in to_remove:
                logger.info(f"Cleaning up idle session: {bid}")
                wrapper = self._sessions.pop(bid)
                await wrapper.browser.kill()

    # -----------------------------------------------------------------------
    # Browser operations — all use event_bus dispatch, NOT Playwright directly
    # -----------------------------------------------------------------------

    async def navigate(self, url: str) -> BrowserState:
        """Navigate to a URL and return the page state."""
        browser = await self.get_or_create_browser()
        event = browser.browser.event_bus.dispatch(NavigateToUrlEvent(url=url, new_tab=False))
        await event
        await event.event_result(raise_if_any=True, raise_if_none=False)
        return await self._get_state(browser.browser)

    async def click_element(self, index: int) -> BrowserState:
        """Click an element by its DOM index. Index from browser_get_state."""
        browser = await self.get_or_create_browser()
        element = await browser.browser.get_dom_element_by_index(index)
        if not element:
            raise ValueError(f"Element with index {index} not found")
        event = browser.browser.event_bus.dispatch(ClickElementEvent(node=element))
        await event
        return await self._get_state(browser.browser)

    async def type_text(self, index: int, text: str) -> BrowserState:
        """Type text into an input element."""
        browser = await self.get_or_create_browser()
        element = await browser.browser.get_dom_element_by_index(index)
        if not element:
            raise ValueError(f"Element with index {index} not found")
        event = browser.browser.event_bus.dispatch(TypeTextEvent(node=element, text=text))
        await event
        return await self._get_state(browser.browser)

    async def take_screenshot(self) -> str:
        """Take a screenshot of the current page."""
        import base64
        browser = await self.get_or_create_browser()
        data = await browser.browser.take_screenshot()
        return base64.b64encode(data).decode() if isinstance(data, bytes) else data

    async def get_page_state(self) -> BrowserState:
        """Get the current page state."""
        browser = await self.get_or_create_browser()
        return await self._get_state(browser.browser)

    async def scroll(self, direction: str) -> BrowserState:
        """Scroll the page up or down."""
        browser = await self.get_or_create_browser()
        scroll_down = direction.lower() == "down"
        event = browser.browser.event_bus.dispatch(ScrollEvent(direction=scroll_down, amount=500))
        await event
        return await self._get_state(browser.browser)

    async def go_back(self) -> BrowserState:
        """Go back to the previous page."""
        browser = await self.get_or_create_browser()
        event = browser.browser.event_bus.dispatch(GoBackEvent())
        await event
        return await self._get_state(browser.browser)

    async def _get_state(self, browser: Browser) -> BrowserState:
        """Extract interactable elements from the via browser-use's DOM state."""
        url = await browser.get_current_page_url()
        title = await browser.get_current_page_title()

        state = await browser.get_browser_state_summary()
        elements_data = []
        if state.dom_state and state.dom_state.selector_map:
            for idx, element in state.dom_state.selector_map.items():
                attrs = {}
                if element.attributes:
                    attrs = {k: str(v) for k, v in element.attributes.items() if v is not None}
                elements_data.append(
                    ElementInfo(
                        index=idx,
                        tag=element.node_name if element.node_name else "",
                        text=element.node_value if element.node_value else "",
                        attributes=attrs,
                    )
                )
        return PageState(url=url, title=title, elements=elements_data)

    @property
    def is_active(self) -> bool:
        return self._session is not None and self._session.state.is_running


# Singleton
manager: BrowserManager = BrowserManager()
