"""Configuration for browser automation MCP server.

All parameters are loaded from environment variables. The naming convention uses
BROWSER_ prefix to avoid conflict with other services.
"""
import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class BrowserAutomationConfig:
    """Configuration loaded from environment variables."""
    
    # LLM configuration
    llm_provider: str = field(default_factory=lambda: os.getenv("BROWSER_LLM_PROVIDER", "ollama"))
    llm_model: str = field(default_factory=lambda: os.getenv("BROWSER_LLM_MODEL", "qwen2.5-vl:7b"))
    ollama_base_url: str = field(default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
    openai_api_key: Optional[str] = field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    openai_base_url: Optional[str] = field(default_factory=lambda: os.getenv("OPENAI_BASE_URL"))
    openai_model: str = field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o"))
    anthropic_api_key: Optional[str] = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY"))
    anthropic_model: str = field(default_factory=lambda: os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"))
    
    # Browser settings
    headless: bool = field(default_factory=lambda: os.getenv("BROWSER_HEADLESS", "false").lower() == "true")
    viewport_width: int = field(default_factory=lambda: int(os.getenv("BROWSER_VIEWPORT_WIDTH", "1280")))
    viewport_height: int = field(default_factory=lambda: int(os.getenv("BROWSER_VIEWPORT_HEIGHT", "720")))
    browser_data_dir: Optional[str] = field(default_factory=lambda: os.getenv("BROWSER_DATA_DIR"))
    
    # MCP Server settings
    mcp_server_name: str = field(default_factory=lambda: "browser-automation")
    log_dir: Optional[str] = field(default_factory=lambda: os.getenv("BROWSER_LOG_DIR"))

    # Session management
    max_concurrent_browsers: int = field(default_factory=lambda: int(os.getenv("MAX_CONCURRENT_BROWSERS", "1")))
    browser_idle_timeout_seconds: int = field(default_factory=lambda: int(os.getenv("BROWSER_IDLE_TIMEOUT_SECONDS", "300")))


config = BrowserAutomationConfig()
