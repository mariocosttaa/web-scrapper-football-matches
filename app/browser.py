"""
Browser Management
==================
Handles all browser-related operations:
- Browser creation and configuration
- Page setup and navigation
- Browser lifecycle management
"""

from playwright.sync_api import sync_playwright, Browser, Page
import time
import sys
import os
# Add parent directory to path to import config from root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def create_browser(playwright) -> Browser:
    """
    Create and configure the browser instance.
    
    Uses configuration from config.py:
    - VISUAL_MODE: Whether to show browser window
    - SLOW_MO: Slow motion speed for visual mode
    
    Returns:
        Browser: Configured Playwright browser instance
    """
    print("\n🌐 Launching browser...")
    
    if config.VISUAL_MODE:
        print("  👀 VISUAL MODE: Browser window will be visible!")
        print(f"  🐌 Slow motion: {config.SLOW_MO}ms per action")
        browser = playwright.chromium.launch(
            headless=False,  # Show browser window
            slow_mo=config.SLOW_MO  # Slow down actions so you can see them
        )
    else:
        print("  🔇 Running in headless mode (no visible window)")
        browser = playwright.chromium.launch(headless=True)
    
    return browser


def setup_page(browser: Browser) -> Page:
    """
    Create and configure a new page with settings.
    
    Configures:
    - User agent (from config.USER_AGENT)
    - Viewport size (from config.VIEWPORT_WIDTH/HEIGHT)
    
    Args:
        browser: Browser instance
        
    Returns:
        Page: Configured page instance
    """
    page = browser.new_page()
    
    # Set a realistic user agent (makes us look like a real browser)
    page.set_extra_http_headers({
        'User-Agent': config.USER_AGENT
    })
    
    # Set viewport size (optional, but good for consistency)
    page.set_viewport_size({
        "width": config.VIEWPORT_WIDTH,
        "height": config.VIEWPORT_HEIGHT
    })
    
    return page


def navigate_to_url(page: Page, url: str = None):
    """
    Navigate to the target URL and wait for page to load.
    
    Uses configuration from config.py:
    - URL: Default target URL
    - PAGE_LOAD_TIMEOUT: Maximum time to wait for page load
    - WAIT_AFTER_LOAD: Additional wait time after page loads
    
    Args:
        page: Page instance
        url: URL to navigate to (defaults to config.URL)
    """
    if url is None:
        url = config.URL
    
    print(f"\n📄 Loading page: {url}")
    page.goto(
        url,
        wait_until='networkidle',
        timeout=config.PAGE_LOAD_TIMEOUT
    )
    time.sleep(config.WAIT_AFTER_LOAD)  # Give extra time for JavaScript to execute
    print("  ✓ Page loaded successfully")


def run_scraping_session():
    """
    Run a single scraping session (one complete cycle).
    
    This function:
    1. Opens browser using Playwright
    2. Creates and configures a page
    3. Navigates to the target URL
    4. Returns browser and page objects for steps to use
    
    Note: The browser must be closed by the caller!
    
    Returns:
        tuple: (browser, page, playwright_context) objects
        - browser: Browser instance
        - page: Page instance
        - playwright_context: Context manager (use with 'with' statement)
        
    Example:
        browser, page, playwright_context = run_scraping_session()
        # ... do scraping ...
        close_browser(browser, playwright_context)
    """
    playwright_context = sync_playwright()
    playwright = playwright_context.__enter__()
    
    browser = create_browser(playwright)
    page = setup_page(browser)
    navigate_to_url(page)
    
    return browser, page, playwright_context


def close_browser(browser: Browser, playwright_context=None):
    """
    Close the browser and clean up resources.
    
    Args:
        browser: Browser instance to close
        playwright_context: Playwright context manager (optional)
    """
    if browser:
        print("\n🔒 Closing browser...")
        browser.close()
        print("  ✓ Browser closed")
    
    if playwright_context:
        try:
            playwright_context.__exit__(None, None, None)
        except:
            pass

