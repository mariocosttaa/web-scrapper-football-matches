"""
Main Entry Point - Web Scraper
===============================
This is the main entry point for the web scraper application.

It:
1. Initializes database
2. Sets up browser and navigates to URL
3. Executes all scraping steps in sequence
4. Handles errors gracefully
5. Supports repeating/scheduling mode

Usage:
    python main.py
"""

import time
import sys
import importlib.util
from datetime import datetime, timedelta

# Import config (in root) and app modules
import config
from app.logger import setup_logging
from app.browser import run_scraping_session, close_browser
from app.helper import (
    save_html_and_screenshot,
    print_step_header,
    print_success,
    print_info,
    print_error
)
from db.database import init_database


def import_step_module(module_name, function_name):
    """Import a module with hyphen in name from app folder."""
    spec = importlib.util.spec_from_file_location(
        module_name, 
        f"app/{module_name}.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return getattr(module, function_name)


# Import step functions
execute_step_1 = import_step_module("step-1", "execute_step_1")
execute_step_2 = import_step_module("step-2", "execute_step_2")
execute_step_3 = import_step_module("step-3", "execute_step_3")


def calculate_next_run_time(interval_minutes: int) -> datetime:
    """Calculate when the next run should happen."""
    return datetime.now() + timedelta(minutes=interval_minutes)


def run_with_repeat(scraping_function):
    """
    Run scraping function repeatedly based on REPEAT_INTERVAL.
    
    Uses configuration from app.config:
    - REPEAT_ENABLED: Whether to enable repeating
    - REPEAT_INTERVAL_MINUTES: How often to run
    
    Args:
        scraping_function: Function to run (should accept no arguments)
    """
    if not config.REPEAT_ENABLED:
        print("\n🔄 Single run mode (REPEAT_ENABLED = False)")
        scraping_function()
        return
    
    print(f"\n🔄 Repeat mode enabled")
    print(f"   Interval: Every {config.REPEAT_INTERVAL_MINUTES} minutes")
    print(f"   Press Ctrl+C to stop\n")
    
    run_count = 0
    
    try:
        while True:
            run_count += 1
            next_run = calculate_next_run_time(config.REPEAT_INTERVAL_MINUTES)
            
            print("\n" + "="*60)
            print(f"🔄 RUN #{run_count}")
            print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"⏰ Next run at: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*60)
            
            # Run the scraping function
            scraping_function()
            
            # Wait until next run time
            wait_seconds = (next_run - datetime.now()).total_seconds()
            if wait_seconds > 0:
                print(f"\n⏳ Waiting {wait_seconds/60:.1f} minutes until next run...")
                print(f"   (Press Ctrl+C to stop)")
                time.sleep(wait_seconds)
            else:
                # If we're already past the next run time, continue immediately
                time.sleep(1)
                
    except KeyboardInterrupt:
        print("\n\n🛑 Stopped by user (Ctrl+C)")
        print(f"✅ Completed {run_count} run(s)")
        print("👋 Goodbye!\n")


def run_all_steps():
    """
    Execute all scraping steps in sequence.
    
    This function:
    1. Initializes database
    2. Opens browser and navigates to URL
    3. Runs Step 1: Accept cookies
    4. Runs Step 2: Click "Ao Vivo"
    5. Runs Step 3: Extract data
    6. Closes browser
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info("🚀" * 30)
    logger.info("WEB SCRAPER - FlashScore.pt")
    logger.info("🚀" * 30)
    logger.info(f"📍 Target URL: {config.URL}")
    logger.info(f"📁 Output Directory: {config.OUTPUT_BASE_DIR}/")
    
    print("\n" + "🚀" * 30)
    print("WEB SCRAPER - FlashScore.pt")
    print("🚀" * 30)
    print(f"\n📍 Target URL: {config.URL}")
    print(f"📁 Output Directory: {config.OUTPUT_BASE_DIR}/")
    
    # Initialize database (create if not exists)
    print_info("Initializing database...")
    init_database()
    
    browser = None
    page = None
    playwright_context = None
    
    try:
        # Setup browser and page
        browser, page, playwright_context = run_scraping_session()
        
        # Save initial page state (before any steps)
        print_step_header(0, "Initial Page State")
        print_info("Saving initial page state...")
        save_html_and_screenshot(
            page=page,
            output_dir=config.OUTPUT_BASE_DIR,
            filename="00_initial_page.html",
            step_name="Initial Page"
        )
        
        # Execute all steps in sequence
        results = {}
        
        # Step 1: Accept cookies
        results['step_1'] = execute_step_1(page)
        
        # Step 2: Click "Ao Vivo"
        results['step_2'] = execute_step_2(page)
        
        # Step 3: Extract data
        results['step_3'] = execute_step_3(page)
        
        # Print summary
        print("\n" + "="*60)
        print("📊 EXECUTION SUMMARY")
        print("="*60)
        print(f"  Step 1 (Accept Cookies): {'✅ Success' if results['step_1'] else '⚠️  Skipped/Not Found'}")
        print(f"  Step 2 (Click Ao Vivo):  {'✅ Success' if results['step_2'] else '❌ Failed'}")
        print(f"  Step 3 (Extract Data):   {'✅ Success' if results['step_3'] else '❌ Failed'}")
        print("="*60)
        
        print_success("All steps completed!")
        print_info(f"Check the '{config.OUTPUT_BASE_DIR}/' folder for results")
        print_info(f"  • {config.OUTPUT_STEP_1_DIR}/ - After accepting cookies")
        print_info(f"  • {config.OUTPUT_STEP_2_DIR}/ - After clicking 'Ao Vivo'")
        print_info(f"  • {config.OUTPUT_STEP_3_DIR}/ - Live matches data")
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        print_error(f"ERROR: {e}")
        logger.error(f"ERROR: {e}", exc_info=True)
        import traceback
        traceback.print_exc()
        
    finally:
        # Always close the browser, even if there was an error
        close_browser(browser, playwright_context)


def main():
    """
    Main entry point.
    Handles single run or repeating mode based on configuration.
    - If REPEAT_ENABLED is True: runs automatically in repeat mode
    - If REPEAT_ENABLED is False: runs once (manual execution)
    """
    # Set up logging at application start
    logger = setup_logging("app-log.log")
    
    if config.REPEAT_ENABLED:
        logger.info("🔄 Starting scraper in repeat mode")
        logger.info(f"   Interval: Every {config.REPEAT_INTERVAL_MINUTES} minutes")
        # Run with repeating/scheduling
        run_with_repeat(run_all_steps)
    else:
        logger.info("▶️  Starting scraper (single run - manual execution)")
        logger.info("   Note: REPEAT_ENABLED is False - this is a manual run")
        # Single run (manual execution)
        run_all_steps()
        logger.info("✅ Scraper completed successfully")
        print("\n" + "🎉" * 20 + "\n")


if __name__ == "__main__":
    # Initialize logging at application start
    setup_logging("app-log.log")
    main()
