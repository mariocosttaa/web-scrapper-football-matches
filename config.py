"""
Configuration File
==================
All static variables and configuration settings.
Edit this file to customize the scraper behavior.
"""

# ============================================================================
# TARGET URL
# ============================================================================

# Target URL to scrape
URL = "https://www.flashscore.pt/"


# ============================================================================
# REPEAT/SCHEDULE CONFIGURATION
# ============================================================================

# Set how often to run the scraper
# IMPORTANT: If False, the scraper will NOT run automatically
# You must run it manually with: ./dc run
REPEAT_ENABLED = False  # Set to True to enable automatic repeating

# Repeat interval options (use one of these):
REPEAT_INTERVAL_MINUTES = 5   # Run every 5 minutes (only if REPEAT_ENABLED = True)
# REPEAT_INTERVAL_HOURS = 1    # Run every hour (uncomment to use)
# REPEAT_INTERVAL_DAYS = 1     # Run every day (uncomment to use)


# ============================================================================
# VISUAL MODE CONFIGURATION
# ============================================================================

# Set to True to see the browser in action (useful for debugging)
VISUAL_MODE = False  # Change to True to see the browser window

# Slow motion speed (in milliseconds)
# Higher values = slower actions (easier to see what's happening)
SLOW_MO = 1500  # 1500 = 1.5 seconds per action


# ============================================================================
# BROWSER CONFIGURATION
# ============================================================================

# User agent string (makes the scraper look like a real browser)
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# Page load timeout (in milliseconds)
PAGE_LOAD_TIMEOUT = 30000  # 30 seconds

# Wait time after page loads (in seconds)
# Gives JavaScript time to execute
WAIT_AFTER_LOAD = 2  # Seconds

# Browser viewport size
VIEWPORT_WIDTH = 1920
VIEWPORT_HEIGHT = 1080


# ============================================================================
# OUTPUT CONFIGURATION
# ============================================================================

# Base output directory
OUTPUT_BASE_DIR = "outputs"

# Output directories for each step
OUTPUT_STEP_1_DIR = "outputs/step-1"
OUTPUT_STEP_2_DIR = "outputs/step-2"
OUTPUT_STEP_3_DIR = "outputs/step-3"


# ============================================================================
# ELEMENT SELECTOR TIMEOUTS
# ============================================================================

# Default timeout for finding elements (in milliseconds)
DEFAULT_SELECTOR_TIMEOUT = 3000  # 3 seconds

# Timeout for waiting for page load
PAGE_LOAD_WAIT_TIMEOUT = 5000  # 5 seconds


# ============================================================================
# STEP CONFIGURATION
# ============================================================================

# Enable/disable specific steps
STEP_1_ENABLED = True  # Accept cookies
STEP_2_ENABLED = True  # Click "Ao Vivo"
STEP_3_ENABLED = True  # Extract data


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

# Enable detailed logging
VERBOSE_LOGGING = True

# Show debug information
DEBUG_MODE = True

