# ⚽ Web Scraper - FlashScore.pt

A powerful web scraper for extracting live match data from FlashScore.pt, with SQLite database storage, JSON export capabilities, and Docker support.

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![Playwright](https://img.shields.io/badge/Playwright-1.48+-green.svg)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-4.12-orange.svg)
![SQLite](https://img.shields.io/badge/SQLite-3-lightgrey.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)

## 📋 Table of Contents

- [Tech Stack](#-tech-stack)
- [Features](#-features)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Usage](#-usage)
- [Configuration](#-configuration)
- [Testing](#-testing)
- [Debugging](#-debugging)
- [Database](#-database)
- [JSON Export](#-json-export)
- [Docker Helper Script](#-docker-helper-script-dc)
- [Troubleshooting](#-troubleshooting)

## 🛠 Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.12+ | Core language |
| **Playwright** | ≥1.48.0 | Browser automation & web scraping |
| **BeautifulSoup4** | 4.12.2 | HTML parsing & data extraction |
| **SQLite** | 3 | Database storage |
| **Docker** | Latest | Containerization |
| **Docker Compose** | Latest | Container orchestration |

## ✨ Features

- ✅ **Automated Web Scraping** - Browser automation with Playwright
- ✅ **Match Data Extraction** - Extracts all match details (teams, scores, times, leagues)
- ✅ **SQLite Database** - Persistent storage with automatic schema migration
- ✅ **JSON Export** - Export matches to JSON with summary by status
- ✅ **Docker Support** - Fully containerized with helper scripts
- ✅ **Test Mode** - Test extraction from local HTML files
- ✅ **Logging** - File-based logging (`app-log.log`)
- ✅ **Error Handling** - Graceful error handling with detailed logging
- ✅ **Scheduled Runs** - Optional automatic repeating mode

## 📁 Project Structure

```
.
├── app/                          # Application logic
│   ├── __init__.py
│   ├── browser.py               # Browser management & Playwright setup
│   ├── extract_matches.py       # HTML parsing & match data extraction
│   ├── export_json.py           # JSON export functionality
│   ├── helper.py                # Utility functions (print helpers, file ops)
│   ├── logger.py                # Logging configuration
│   ├── step-1.py                # Step 1: Accept cookies
│   ├── step-2.py                # Step 2: Click "Ao Vivo" button
│   └── step-3.py                # Step 3: Extract live match data
├── db/                          # Database
│   ├── database.py              # Database operations & schema
│   └── matches.db               # SQLite database file (auto-created)
├── test/                        # Test files
│   ├── __init__.py
│   ├── __main__.py              # Test entry point (run: python -m test)
│   ├── output/                  # Test output (JSON files)
│   │   ├── matches.json         # All extracted matches
│   │   └── matches_summary.json # Summary grouped by status
│   └── *.html                   # Test HTML files
├── outputs/                     # Scraper output files
│   ├── step-1/                  # After accepting cookies
│   │   ├── after_accept_cookies.html
│   │   └── after_accept_cookies.png
│   ├── step-2/                  # After clicking "Ao Vivo"
│   │   ├── after_click_ao_vivo.html
│   │   └── after_click_ao_vivo.png
│   ├── step-3/                  # Live matches data
│   │   ├── live_matches_data.html
│   │   └── live_matches_data.png
│   └── matches_*.json           # Exported match data
├── public/                      # Public web files
│   └── index.html               # Landing page (generated from database)
├── main.py                      # Main entry point
├── config.py                    # Configuration settings
├── dc                           # Docker helper script (./dc [command])
├── docker-compose.yml            # Docker Compose configuration
├── Dockerfile                   # Docker image definition
├── requirements.txt             # Python dependencies
├── app-log.log                  # Application logs (auto-created)
└── README.md                    # This file
```

## 🚀 Installation

### Option 1: Docker (Recommended)

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd web-scrapping-app
   ```

2. **Start the container:**
   ```bash
   ./dc up
   ```

3. **That's it!** The container is ready to use.

### Option 2: Local Installation

1. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers:**
   ```bash
   playwright install
   ```

## 💻 Usage

### Running the Scraper

#### Docker (Recommended)

```bash
# Start container (doesn't run scraper automatically)
./dc up

# Run scraper manually
./dc run

# Or run directly
./dc python main.py
```

#### Local

```bash
python main.py
```

**Note:** The scraper will only run automatically if `REPEAT_ENABLED = True` in `config.py`. Otherwise, it requires manual execution.

### Automatic Mode vs Manual Mode

- **Automatic Mode:** Set `REPEAT_ENABLED = True` in `config.py` - scraper runs automatically at intervals
- **Manual Mode:** Set `REPEAT_ENABLED = False` in `config.py` - run with `./dc run` or `python main.py`

## ⚙️ Configuration

Edit `config.py` to customize the scraper:

```python
# Target URL
URL = "https://www.flashscore.pt/"

# Automatic repeating (set to True to enable)
REPEAT_ENABLED = False

# Repeat interval (only if REPEAT_ENABLED = True)
REPEAT_INTERVAL_MINUTES = 5  # Run every 5 minutes

# Browser settings
VISUAL_MODE = False  # Set to True to see browser (headless by default)
BROWSER_TYPE = "chromium"  # Options: "chromium", "firefox", "webkit"
```

**Important:** When `REPEAT_ENABLED = False`, the scraper will not run automatically. You must run it manually with `./dc run`.

## 🧪 Testing

### Test Match Extraction from HTML

The test module extracts matches from local HTML files without running the full browser automation:

```bash
# In Docker
./dc test

# Or locally (if dependencies installed)
python -m test
```

**Test Output:**
- `test/output/matches.json` - All extracted matches
- `test/output/matches_summary.json` - Summary grouped by status

**Test HTML Files:**
- `test/output-code.html` (priority) - **Put your HTML code here for testing**
- `outputs/step-1/after_accept_cookies.html` (fallback - from actual scraper run)

### What Tests Do

1. Load HTML from test files
2. Extract all matches using the same extraction logic as production
3. Export to JSON (does NOT save to database)
4. Display summary statistics

### Test HTML File

The test module looks for HTML files in this order:
1. **`test/output-code.html`** - **Your test file** (put your HTML code here)
2. `outputs/step-1/after_accept_cookies.html` - From actual scraper run (fallback)

**To test with your own HTML:**
1. Copy HTML code from the browser (after accepting cookies on FlashScore.pt)
2. Paste it into `test/output-code.html`
3. Run: `./dc test` or `python -m test`
4. Check results in `test/output/matches.json`

## 🐛 Debugging

### View HTML Outputs

After running the scraper, check the `outputs/` directory:

```bash
# View HTML files
ls -la outputs/step-1/
ls -la outputs/step-2/
ls -la outputs/step-3/

# Open HTML in browser (Docker)
./dc exec cat outputs/step-1/after_accept_cookies.html

# Or copy to local machine
docker cp web-scraper-app:/app/outputs/step-1/after_accept_cookies.html ./
```

### View Screenshots

Screenshots are saved alongside HTML files:
- `outputs/step-1/after_accept_cookies.png`
- `outputs/step-2/after_click_ao_vivo.png`
- `outputs/step-3/live_matches_data.png`

### View Logs

```bash
# Application logs
tail -f app-log.log

# Docker logs
./dc logs

# Follow logs in real-time
./dc logs -f
```

### Debug Database

```bash
# View all matches
./dc exec sqlite3 db/matches.db "SELECT COUNT(*) FROM matches;"

# View specific match
./dc exec sqlite3 db/matches.db "SELECT * FROM matches WHERE match_id = 'YOUR_MATCH_ID';"

# View matches by status
./dc exec sqlite3 db/matches.db "SELECT COUNT(*) FROM matches WHERE match_status = 'live';"
```

### Enable Visual Mode

To see the browser while scraping (useful for debugging):

1. Edit `config.py`:
   ```python
   VISUAL_MODE = True
   ```

2. Run the scraper:
   ```bash
   ./dc run
   ```

## 💾 Database

### Database Location

- **File:** `db/matches.db`
- **Auto-created:** Yes, on first run
- **Auto-migrated:** Yes, schema updates automatically

### Database Schema

The `matches` table contains:

| Field | Type | Description |
|-------|------|-------------|
| `match_id` | TEXT (UNIQUE) | Unique match identifier |
| `match_url` | TEXT | URL to match page |
| `league_name` | TEXT | League name |
| `league_country` | TEXT | League country/category |
| `match_time` | TEXT | Match time (e.g., "15:30") |
| `home_team_name` | TEXT | Home team name |
| `away_team_name` | TEXT | Away team name |
| `home_score` | INTEGER | Home team score |
| `away_score` | INTEGER | Away team score |
| `match_status` | TEXT | Status: live, scheduled, finished, etc. |
| `is_live` | BOOLEAN | Is match currently live |
| `has_tv_icon` | BOOLEAN | Has TV broadcast icon |
| `has_audio_icon` | BOOLEAN | Has audio icon |
| `has_info_icon` | BOOLEAN | Has info icon |
| `current_minute` | INTEGER | Current minute (if live) |
| `scraped_at` | TIMESTAMP | When match was scraped |
| `updated_at` | TIMESTAMP | Last update time |

### Query Examples

```sql
-- Count all matches
SELECT COUNT(*) FROM matches;

-- Get all live matches
SELECT * FROM matches WHERE match_status = 'live';

-- Get matches by league
SELECT * FROM matches WHERE league_name LIKE '%Champions%';

-- Get recent matches
SELECT * FROM matches ORDER BY scraped_at DESC LIMIT 10;
```

## 🌐 Landing Page

Generate a beautiful HTML landing page displaying all matches from the database:

```bash
# In Docker
./dc python -c "from app.generate_landing import generate_landing_page; generate_landing_page()"

# Or locally
python -c "from app.generate_landing import generate_landing_page; generate_landing_page()"
```

**Output:** `public/index.html`

**Features:**
- 🎨 Beautiful Tailwind CSS design
- ⚽ Live match cards with scores
- 📊 Statistics dashboard
- 🔄 Auto-refresh every 30 seconds
- 📱 Responsive design
- 🎯 Click cards to view match details

**To view:**
```bash
# Open in browser
open public/index.html  # macOS
xdg-open public/index.html  # Linux
start public/index.html  # Windows
```

## 📄 JSON Export

### Automatic Export

JSON files are automatically generated during scraping:

- **Location:** `outputs/matches_YYYY-MM-DD_HH-MM-SS.json`
- **Contains:** All matches with full details
- **Format:** JSON array of match objects

### Summary Export

Summary files group matches by status:

- **Location:** `outputs/matches_summary_YYYY-MM-DD_HH-MM-SS.json`
- **Contains:** Summary grouped by status (live, scheduled, finished, etc.)
- **Format:** JSON object with status groups

### Test Export

Test mode exports to:
- `test/output/matches.json` - All test matches
- `test/output/matches_summary.json` - Test summary

### JSON Structure

```json
{
  "export_date": "2025-12-09T06:10:17",
  "total_matches": 102,
  "matches": [
    {
      "match_id": "KMICP6x0",
      "home_team_name": "Kairat Almaty",
      "away_team_name": "Olympiakos",
      "match_time": "15:30",
      "league_name": "Liga dos Campeões - Fase de Liga",
      "match_status": "live",
      "home_score": null,
      "away_score": null
    }
  ]
}
```

## 🐳 Docker Helper Script (`./dc`)

The `./dc` script simplifies Docker commands. **Always use `./dc` prefix** (not just `dc`):

### Basic Commands

```bash
./dc up          # Start containers
./dc down        # Stop containers
./dc build       # Build images
./dc logs        # View logs
./dc logs -f     # Follow logs in real-time
./dc help        # Show all commands
```

### Application Commands

```bash
./dc run         # Run scraper (python main.py)
./dc test        # Run tests (python -m test)
./dc shell       # Open interactive shell in container
```

### Execute Any Command

```bash
# Run any command inside the container
./dc python -m test
./dc pip install package-name
./dc ls -la
./dc cat app-log.log
./dc sqlite3 db/matches.db "SELECT COUNT(*) FROM matches;"
```

**Important:** The script must be run with `./dc` from the project root directory.

## 🔧 Troubleshooting

### Container Won't Start

```bash
# Check if container is running
./dc ps

# View container logs
./dc logs

# Rebuild container
./dc build --no-cache
./dc up
```

### Database Issues

```bash
# Check database file
ls -la db/matches.db

# Verify database integrity
./dc exec sqlite3 db/matches.db "PRAGMA integrity_check;"

# Reset database (WARNING: deletes all data)
rm db/matches.db
./dc run  # Will recreate database
```

### Missing Dependencies

```bash
# In Docker (dependencies are pre-installed)
# If you need to install additional packages:
./dc pip install package-name

# Locally
pip install -r requirements.txt
```

### Playwright Browser Issues

```bash
# Install browsers (local)
playwright install

# In Docker, browsers are pre-installed
# If issues occur, rebuild:
./dc build --no-cache
```

### Permission Issues

```bash
# Make dc script executable
chmod +x dc

# Fix Docker permissions
sudo chown -R $USER:$USER .
```

### Viewing Output Files

```bash
# List all outputs
ls -la outputs/

# View HTML file
cat outputs/step-1/after_accept_cookies.html

# Copy file from container to local
docker cp web-scraper-app:/app/outputs/step-1/after_accept_cookies.html ./
```

## 📝 License

This project is for educational purposes.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

**Made with ❤️ for web scraping enthusiasts**
