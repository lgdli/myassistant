#!/usr/bin/env python
"""Diagnostic script to test browser automation MCP server components."""

import asyncio
import logging
import sys
import os

# Setup logging to see what's happening
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)]
)

async def test_browser_creation():
    """Test creating a browser session."""
    print("=" * 60, file=sys.stderr)
    print("Testing browser creation...", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    
    # Set environment for testing
    os.environ.setdefault("BROWSER_HEADLESS", "true")
    
    from browser_automation.config import config
    print(f"Config - headless: {config.headless}", file=sys.stderr)
    print(f"Config - browser_data_dir: {config.browser_data_dir}", file=sys.stderr)
    print(f"Config - llm_provider: {config.llm_provider}", file=sys.stderr)
    
    from browser_use.browser.session import BrowserSession
    print("\nCreating BrowserSession...", file=sys.stderr)
    
    browser = BrowserSession(
        headless=config.headless,
    )
    
    print("BrowserSession created, starting...", file=sys.stderr)
    
    try:
        await asyncio.wait_for(browser.start(), timeout=30)
        print("Browser started successfully!", file=sys.stderr)
        
        # Test navigation
        print("\nTesting navigation to xjtu.edu.cn...", file=sys.stderr)
        from browser_use.browser.events import NavigateToUrlEvent
        event = browser.event_bus.dispatch(NavigateToUrlEvent(url="https://www.xjtu.edu.cn", new_tab=False))
        await event
        result = await event.event_result(raise_if_any=True, raise_if_none=False)
        print(f"Navigation result: {result}", file=sys.stderr)
        
        # Get page state
        url = await browser.get_current_page_url()
        title = await browser.get_current_page_title()
        print(f"\nCurrent URL: {url}", file=sys.stderr)
        print(f"Page title: {title}", file=sys.stderr)
        
        # Clean up
        print("\nClosing browser...", file=sys.stderr)
        await browser.kill()
        print("Done!", file=sys.stderr)
        
    except asyncio.TimeoutError:
        print("ERROR: Browser start timed out!", file=sys.stderr)
        return False
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return False
    
    return True


async def test_manager():
    """Test the BrowserManager."""
    print("\n" + "=" * 60, file=sys.stderr)
    print("Testing BrowserManager...", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    
    from browser_automation.browser_manager import BrowserManager
    
    manager = BrowserManager()
    
    try:
        wrapper = await asyncio.wait_for(manager.get_or_create_browser(), timeout=60)
        print(f"Browser created with ID: {wrapper.browser_id}", file=sys.stderr)
        
        # Test navigation via manager
        state = await asyncio.wait_for(manager.navigate("https://www.xjtu.edu.cn"), timeout=60)
        print(f"Navigation successful! URL: {state.url}, Title: {state.title}", file=sys.stderr)
        print(f"Number of elements: {len(state.elements)}", file=sys.stderr)
        
        await manager.close_all()
        return True
        
    except asyncio.TimeoutError:
        print("ERROR: Operation timed out!", file=sys.stderr)
        return False
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return False


async def main():
    print("Browser Automation Diagnostic Test", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    
    # Test 1: Direct browser creation
    success1 = await test_browser_creation()
    
    # Test 2: Via BrowserManager
    if success1:
        success2 = await test_manager()
    else:
        print("Skipping manager test due to browser creation failure", file=sys.stderr)
        success2 = False
    
    print("\n" + "=" * 60, file=sys.stderr)
    print("RESULTS:", file=sys.stderr)
    print(f"  Browser creation: {'PASS' if success1 else 'FAIL'}", file=sys.stderr)
    print(f"  BrowserManager: {'PASS' if success2 else 'FAIL'}", file=sys.stderr)
    
    return 0 if (success1 and success2) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))