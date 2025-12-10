"""
Step 3: Extract Live Match Data
================================
Description:
    This step extracts data from the live matches section.
    After clicking "Ao Vivo", this step can collect match information,
    scores, teams, and other relevant data from the live matches table.

Function:
    execute_step_3(page) -> bool
        - Accepts a Playwright page object
        - Extracts data from live matches
        - Saves HTML and screenshot to outputs/step-3/
        - Returns True if successful, False otherwise

Note:
    This is a template step. You can customize it to extract
    specific data you need from the live matches section.
"""

from playwright.sync_api import Page
import time
import sys
import os
# Add parent directory to path to import config from root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from app.helper import (
    save_html_and_screenshot,
    wait_for_element,
    print_step_header,
    print_success,
    print_info,
    print_error
)
from db.database import init_database
from app.extract_matches import extract_all_matches_from_html, save_matches_to_database

# Step configuration
STEP_NUMBER = 3
STEP_NAME = "Extract Live Match Data"
STEP_OUTPUT_DIR = config.OUTPUT_STEP_3_DIR


def execute_step_3(page: Page) -> bool:
    """
    Execute Step 3: Extract data from live matches.
    
    This function:
    1. Waits for live matches to load
    2. Extracts match data (customize this part)
    3. Saves HTML and screenshot
    
    Args:
        page: Playwright page object
        
    Returns:
        bool: True if data extraction was successful, False otherwise
    """
    print_step_header(STEP_NUMBER, STEP_NAME)
    
    # Wait for live matches table to be visible
    print_info("Waiting for live matches to load...")
    
    # Try to find the live matches container
    live_matches_loaded = wait_for_element(page, '#live-table', timeout=5000)
    
    if live_matches_loaded:
        print_success("Live matches table found")
        
        # Save the HTML and screenshot first (before extraction)
        print_info("Saving page state...")
        html_path, screenshot_path = save_html_and_screenshot(
            page=page,
            output_dir=STEP_OUTPUT_DIR,
            filename="live_matches_data.html",
            step_name=STEP_NAME
        )
        
        # Extract matches from the saved HTML and save to database
        print_info("Extracting match data...")
        try:
            # Initialize database
            init_database()
            
            # Extract matches from HTML
            matches = extract_all_matches_from_html(html_path)
            
            if matches:
                print_success(f"Extracted {len(matches)} matches")
                
                # Save to database
                print_info("Saving to database...")
                saved_count = save_matches_to_database(matches)
                print_success(f"Saved {saved_count} matches to database")
                
                # Export to JSON
                try:
                    from app.export_json import export_matches_to_json
                    json_file = export_matches_to_json()
                    print_success(f"Matches exported to JSON: {json_file}")
                except Exception as e:
                    print_info(f"Could not export to JSON: {e}")
            else:
                print_error("No matches extracted")
        except Exception as e:
            print_error(f"Error extracting matches: {e}")
    else:
        print_error("Live matches table not found")
        
        # Still save the HTML and screenshot even if table not found
        print_info("Saving page state...")
        save_html_and_screenshot(
            page=page,
            output_dir=STEP_OUTPUT_DIR,
            filename="live_matches_data.html",
            step_name=STEP_NAME
        )
    
    return live_matches_loaded

