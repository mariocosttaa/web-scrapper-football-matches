"""
Helper Functions
===============
General utility functions used across all steps.
These are reusable functions for common operations.
"""

import os
import sys
from playwright.sync_api import Page
from datetime import datetime
# Add parent directory to path to import config from root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# ============================================================================
# FILE OPERATIONS
# ============================================================================

def save_html_and_screenshot(page: Page, output_dir: str, filename: str, step_name: str):
    """
    Save the current page HTML and screenshot to a file.
    
    Args:
        page: Playwright page object
        output_dir: Directory to save files (e.g., "outputs/step-1")
        filename: Name of the output file (e.g., "page.html")
        step_name: Description of what step this is (for logging)
    
    Returns:
        tuple: (html_path, screenshot_path) - Paths to saved files
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get the full HTML content of the page
    html_content = page.content()
    
    # Create file paths
    html_path = os.path.join(output_dir, filename)
    screenshot_path = os.path.join(output_dir, filename.replace('.html', '.png'))
    
    # Write HTML to file
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Save screenshot
    page.screenshot(path=screenshot_path, full_page=True)
    
    # Print confirmation
    print(f"  💾 Saved HTML: {html_path}")
    print(f"  📸 Saved Screenshot: {screenshot_path}")
    print(f"  📊 HTML Size: {len(html_content):,} characters")
    
    return html_path, screenshot_path


def generate_timestamped_filename(base_name: str, extension: str = "html") -> str:
    """
    Generate a filename with timestamp.
    
    Args:
        base_name: Base name for the file (e.g., "page")
        extension: File extension (default: "html")
        
    Returns:
        str: Filename like "page_2025-01-15_14-30-45.html"
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"{base_name}_{timestamp}.{extension}"


# ============================================================================
# ELEMENT INTERACTION
# ============================================================================

def click_element_with_selectors(page: Page, selectors: list, element_name: str, timeout: int = None) -> bool:
    """
    Try to click an element using multiple selector strategies.
    
    This function tries different CSS selectors until one works.
    This is useful because websites can change their HTML structure.
    
    Args:
        page: Playwright page object
        selectors: List of CSS selectors to try
        element_name: Name of element (for logging)
        timeout: How long to wait for element (milliseconds). 
                 Defaults to config.DEFAULT_SELECTOR_TIMEOUT
    
    Returns:
        bool: True if clicked successfully, False otherwise
    """
    if timeout is None:
        timeout = config.DEFAULT_SELECTOR_TIMEOUT
    
    print(f"  🔍 Looking for '{element_name}'...")
    
    # Try each selector until one works
    for selector in selectors:
        try:
            # Wait for the element to appear on the page
            page.wait_for_selector(selector, timeout=timeout)
            
            # Click the element
            page.click(selector)
            
            print(f"  ✓ Successfully clicked '{element_name}' using: {selector}")
            return True
            
        except Exception as e:
            # This selector didn't work, try the next one
            continue
    
    # None of the selectors worked
    print(f"  ⚠ Could not find '{element_name}' (tried {len(selectors)} selectors)")
    return False


def wait_for_element(page: Page, selector: str, timeout: int = None) -> bool:
    """
    Wait for an element to appear on the page.
    
    Args:
        page: Playwright page object
        selector: CSS selector for the element
        timeout: How long to wait (milliseconds). 
                 Defaults to config.PAGE_LOAD_WAIT_TIMEOUT
        
    Returns:
        bool: True if element found, False otherwise
    """
    if timeout is None:
        timeout = config.PAGE_LOAD_WAIT_TIMEOUT
    
    try:
        page.wait_for_selector(selector, timeout=timeout)
        return True
    except:
        return False


def get_element_text(page: Page, selector: str) -> str:
    """
    Get text content from an element.
    
    Args:
        page: Playwright page object
        selector: CSS selector for the element
        
    Returns:
        str: Text content, or empty string if not found
    """
    try:
        element = page.query_selector(selector)
        if element:
            return element.inner_text()
        return ""
    except:
        return ""


# ============================================================================
# PAGE UTILITIES
# ============================================================================

def wait_for_page_load(page: Page, wait_seconds: int = 2):
    """
    Wait for page to fully load and JavaScript to execute.
    
    Args:
        page: Playwright page object
        wait_seconds: Additional seconds to wait after network idle
    """
    page.wait_for_load_state('networkidle')
    import time
    time.sleep(wait_seconds)


def scroll_page(page: Page, direction: str = "down", pixels: int = 500):
    """
    Scroll the page.
    
    Args:
        page: Playwright page object
        direction: "down", "up", or "to-bottom"
        pixels: Number of pixels to scroll (for down/up)
    """
    if direction == "to-bottom":
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    elif direction == "down":
        page.evaluate(f"window.scrollBy(0, {pixels})")
    elif direction == "up":
        page.evaluate(f"window.scrollBy(0, -{pixels})")


# ============================================================================
# LOGGING UTILITIES
# ============================================================================

def print_step_header(step_number: int, step_name: str):
    """
    Print a formatted header for a step.
    
    Args:
        step_number: Step number (1, 2, 3, etc.)
        step_name: Name/description of the step
    """
    import logging
    logger = logging.getLogger(__name__)
    
    header = f"STEP {step_number}: {step_name}"
    logger.info("="*60)
    logger.info(header)
    logger.info("="*60)
    
    print("\n" + "="*60)
    print(header)
    print("="*60)


def print_success(message: str):
    """Print a success message and log it."""
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"✅ {message}")
    print(f"  ✅ {message}")


def print_error(message: str):
    """Print an error message and log it."""
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"❌ {message}")
    print(f"  ❌ {message}")


def print_info(message: str):
    """Print an info message and log it."""
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"ℹ️  {message}")
    print(f"  ℹ️  {message}")

