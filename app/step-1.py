"""
Step 1: Accept Cookies
======================
Description:
    This step handles the cookie consent banner that appears on the website.
    It clicks the "Aceito" (Accept) button to accept cookies and allow
    the scraper to continue with the rest of the steps.

Function:
    execute_step_1(page) -> bool
        - Accepts a Playwright page object
        - Clicks the cookie accept button
        - Saves HTML and screenshot to outputs/step-1/
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
    print_step_header,
    print_success,
    print_info
)
from db.database import init_database
from app.extract_matches import extract_all_matches_from_html, save_matches_to_database

# Step configuration
STEP_NUMBER = 1
STEP_NAME = "Accept Cookies"
STEP_OUTPUT_DIR = config.OUTPUT_STEP_1_DIR


def execute_step_1(page: Page) -> bool:
    """
    Execute Step 1: Accept cookies.
    
    This function:
    1. Looks for cookie consent banner
    2. Clicks the "Aceito" (Accept) button
    3. Waits for banner to disappear
    4. Saves HTML and screenshot
    
    Args:
        page: Playwright page object
        
    Returns:
        bool: True if cookies were accepted successfully, False otherwise
    """
    print_step_header(STEP_NUMBER, STEP_NAME)
    
    # Cookie accept button selectors
    # We try multiple selectors because different sites use different HTML
    cookie_selectors = [
        "button:has-text('Aceito')",           # Button with text "Aceito"
        "button:has-text('Accept')",           # Button with text "Accept"
        "#onetrust-accept-btn-handler",        # Common OneTrust cookie banner ID
        "[data-testid*='accept']",             # Data attribute with "accept"
        ".cookie-consent button",              # Button inside cookie consent div
        "button[id*='accept']",                # Button with "accept" in ID
    ]
    
    # Try to click the accept button
    clicked = click_element_with_selectors(page, cookie_selectors, "Aceito")
    
    # Wait a moment for the cookie banner to disappear
    if clicked:
        time.sleep(1)
        print_success("Cookies accepted successfully")
    else:
        print_info("Cookie button not found (might already be accepted or not present)")
    
    # Save the HTML and screenshot after accepting cookies
    print_info("Saving page state...")
    html_path, screenshot_path = save_html_and_screenshot(
        page=page,
        output_dir=STEP_OUTPUT_DIR,
        filename="after_accept_cookies.html",
        step_name=STEP_NAME
    )
    
    # Extract matches from the saved HTML and save to database
    print_info("Extracting matches from HTML...")
    try:
        # Initialize database
        init_database()
        
        # Extract matches
        matches = extract_all_matches_from_html(html_path)
        
        # Save to database
        if matches:
            saved_count = save_matches_to_database(matches)
            print_success(f"Extracted and saved {saved_count} matches to database")
            
            # Export to JSON
            try:
                from app.export_json import export_matches_to_json
                json_file = export_matches_to_json()
                print_success(f"Matches exported to JSON: {json_file}")
            except Exception as e:
                print_info(f"Could not export to JSON: {e}")
        else:
            print_info("No matches found in HTML")
    except Exception as e:
        print_info(f"Could not extract matches: {e}")
        # Don't fail the step if extraction fails
    
    return clicked

