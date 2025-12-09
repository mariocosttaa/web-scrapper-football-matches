"""
Step 2: Click "Ao Vivo" (Live Section)
======================================
Description:
    This step navigates to the live matches section by clicking the
    "Ao Vivo" (Live) filter tab. On FlashScore, this is a tab filter
    located near "Todos" (All) that shows only live/ongoing matches.

Function:
    execute_step_2(page) -> bool
        - Accepts a Playwright page object
        - Clicks the "Ao Vivo" filter tab
        - Waits for page to load
        - Saves HTML and screenshot to outputs/step-2/
        - Returns True if successful, False otherwise
"""

from playwright.sync_api import Page
import time
import sys
import os
# Add parent directory to path to import config from root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from app.helper import (
    click_element_with_selectors,
    save_html_and_screenshot,
    wait_for_page_load,
    print_step_header,
    print_success,
    print_info,
    print_error
)

# Step configuration
STEP_NUMBER = 2
STEP_NAME = "Click 'Ao Vivo' (Live Section)"
STEP_OUTPUT_DIR = config.OUTPUT_STEP_2_DIR


def execute_step_2(page: Page) -> bool:
    """
    Execute Step 2: Click "Ao Vivo" filter tab.
    
    This function:
    1. Looks for the "Ao Vivo" filter tab
    2. Clicks it to show live matches
    3. Waits for page to update
    4. Saves HTML and screenshot
    
    Args:
        page: Playwright page object
        
    Returns:
        bool: True if "Ao Vivo" was clicked successfully, False otherwise
    """
    print_step_header(STEP_NUMBER, STEP_NAME)
    
    # Selectors for "Ao Vivo" tab on FlashScore
    # The structure is: <div class="filters__tab" data-analytics-alias="live">
    #                    <div class="filters__text">Ao Vivo</div>
    #                    </div>
    ao_vivo_selectors = [
        # Best selector: target the tab with data-analytics-alias="live"
        'div.filters__tab[data-analytics-alias="live"]',
        # Alternative: find tab containing "Ao Vivo" text
        '.filters__tab:has-text("Ao Vivo")',
        # More specific: tab with filters__text containing "Ao Vivo"
        '.filters__tab:has(.filters__text:has-text("Ao Vivo"))',
        # Fallback: any element with "Ao Vivo" text in filters area
        '.filters .filters__tab:has-text("Ao Vivo")',
        # Generic fallbacks
        "a:has-text('Ao Vivo')",
        "button:has-text('Ao Vivo')",
        "[href*='ao-vivo']",
        "[href*='live']",
    ]
    
    # Try to click the "Ao Vivo" tab
    clicked = click_element_with_selectors(page, ao_vivo_selectors, "Ao Vivo")
    
    # Wait for the page to load after clicking
    if clicked:
        print_success("'Ao Vivo' tab clicked successfully")
        # Wait until network requests finish (page fully loaded)
        wait_for_page_load(page, wait_seconds=2)
    else:
        # If clicking didn't work, try to debug
        print_error("Could not click 'Ao Vivo' tab")
        print_info("Debugging: Looking for filter tabs...")
        try:
            tabs = page.query_selector_all('.filters__tab')
            print_info(f"Found {len(tabs)} filter tabs")
            for i, tab in enumerate(tabs):
                text = tab.inner_text()
                alias = tab.get_attribute('data-analytics-alias')
                print_info(f"  Tab {i+1}: '{text}' (alias: {alias})")
        except Exception as e:
            print_error(f"Could not inspect tabs: {e}")
    
    # Save the HTML and screenshot after clicking "Ao Vivo"
    print_info("Saving page state...")
    save_html_and_screenshot(
        page=page,
        output_dir=STEP_OUTPUT_DIR,
        filename="after_click_ao_vivo.html",
        step_name=STEP_NAME
    )
    
    return clicked

