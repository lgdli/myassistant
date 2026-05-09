"""Pydantic models for browser automation MCP."""
from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class Element(BaseModel):
    """A clickable/interactable element on the page."""
    index: int = Field(description="Unique index for this element")
    tag: str = Field(description="HTML tag name")
    text: str = Field(default="", description="Visible text content")
    attributes: dict[str, str] = Field(default_factory=dict, description="Key attribute-value pairs")
    is_clickable: bool = Field(default=True, description="Whether the element is clickable")
    is_input: bool = Field(default=False, description="Whether the element accepts text input")


class PageState(BaseModel):
    """The current state of the browser page."""
    url: str = Field(description="Current page URL")
    title: str = Field(description="Page title")
    elements: list[Element] = Field(description="Interactive elements found on the page")
    screenshot: str | None = Field(default=None, description="Base64 encoded screenshot of the page")
    error: str | None = Field(default=None, description="Error message if any")


class ActionResult(BaseModel):
    """Result of executing a browser action."""
    success: bool = Field(default=True)
    message: str = Field(default="")
    data: Any | None = Field(default=None, description="Additional result data")


class BrowserSessionInfo(BaseModel):
    """Information about an active browser session."""
    browser_id: str
    url: str
    title: str
    created_at: float
    last_active_at: float
