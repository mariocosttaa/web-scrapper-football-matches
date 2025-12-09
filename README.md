# ⚽ Web Scraper - FlashScore.pt

A powerful web scraper for extracting live match data from FlashScore.pt, with a modern frontend, REST API, SQLite database storage, and Docker support.

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![Playwright](https://img.shields.io/badge/Playwright-1.48+-green.svg)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-4.12-orange.svg)
![SQLite](https://img.shields.io/badge/SQLite-3-lightgrey.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4-cyan.svg)

## 📋 Table of Contents

- [Tech Stack](#-tech-stack)
- [Features](#-features)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Usage](#-usage)
- [Database Schema](#-database-schema)
- [API Endpoints](#-api-endpoints)
- [Frontend](#-frontend)
- [Image Caching](#-image-caching)
- [Docker Helper Script](#-docker-helper-script-dc)
- [Troubleshooting](#-troubleshooting)

## 🛠 Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.12+ | Core language |
| **Playwright** | ≥1.48.0 | Browser automation & web scraping |
| **BeautifulSoup4** | 4.12.2 | HTML parsing & data extraction |
| **SQLite** | 3 | Relational database storage |
| **Flask** | Latest | REST API & Static File Serving |
| **Tailwind CSS** | 3.4 | Frontend styling |
| **Docker** | Latest | Containerization |

## ✨ Features

- ✅ **Automated Web Scraping** - Browser automation with Playwright
- ✅ **Relational Database** - Normalized schema (Leagues, Teams, Matches)
- ✅ **REST API** - Endpoints for matches, stats, and health checks
- ✅ **Modern Frontend** - Responsive UI with Dark/Light mode, Search, and League Grouping
- ✅ **Local Image Caching** - Downloads and serves team/league logos locally
- ✅ **Docker Support** - Fully containerized with helper scripts
- ✅ **Logging** - Detailed file-based logging
- ✅ **Scheduled Runs** - Optional automatic repeating mode

## 📁 Project Structure

```
.
├── app/                          # Application logic
│   ├── __init__.py
│   ├── browser.py               # Browser management
│   ├── extract_matches.py       # HTML parsing & extraction
│   ├── image_downloader.py      # Image downloading & caching
│   ├── landing_page.py          # Flask API & Server
│   ├── helper.py                # Utilities
│   ├── logger.py                # Logging config
│   └── step-*.py                # Scraper steps
├── db/                          # Database
│   ├── database.py              # Database operations & schema
│   └── matches.db               # SQLite database (auto-created)
├── public/                      # Frontend & Static Files
│   ├── index.html               # Main frontend interface
│   └── images/                  # Downloaded images (teams/leagues)
├── outputs/                     # Scraper debug outputs
├── main.py                      # Scraper entry point
├── start_server.py              # Web server entry point
├── config.py                    # Configuration
├── dc                           # Docker helper script
├── docker-compose.yml           # Docker Compose config
└── requirements.txt             # Python dependencies
```

## 🚀 Installation

### Option 1: Docker (Recommended)

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd web-scrapping-app
   ```

2. **Start the application:**
   ```bash
   ./dc up
   ```
   This starts the web server automatically at `http://localhost:8080`.

3. **Run the scraper:**
   ```bash
   ./dc run
   ```
   This executes the scraper, populates the database, and downloads images.

### Option 2: Local Installation

1. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   playwright install
   ```

3. **Start the server:**
   ```bash
   python start_server.py
   ```

4. **Run the scraper:**
   ```bash
   python main.py
   ```

## 💾 Database Schema

The project uses a normalized SQLite database with the following tables:

### `leagues`
- `id`: Primary Key
- `name`: League name
- `country`: Country/Category
- `flag_class`: CSS class for flag
- `logo_url`: Local path to league logo

### `teams`
- `id`: Primary Key
- `name`: Team name
- `logo_url`: Local path to team logo

### `matches`
- `match_id`: Unique Identifier (from source)
- `league_id`: Foreign Key -> `leagues.id`
- `home_team_id`: Foreign Key -> `teams.id`
- `away_team_id`: Foreign Key -> `teams.id`
- `home_score`: Integer
- `away_score`: Integer
- `match_status`: Status (live, scheduled, finished)
- `match_time`: Time string (e.g., "15:30")
- `match_date`: Date object
- `is_live`: Boolean

## 🔌 API Endpoints

The Flask server (`start_server.py`) exposes:

- `GET /api/matches` - All matches grouped by status
- `GET /api/matches/live` - Live matches only
- `GET /api/matches/scheduled` - Scheduled matches only
- `GET /api/matches/finished` - Finished matches only
- `GET /api/stats` - Global statistics
- `GET /api/health` - System health check

## 💻 Frontend

The frontend is served at `http://localhost:8080/` and features:
- **Live Data**: Fetches from `/api/matches`
- **Search**: Filter matches by team or league
- **Grouping**: Matches grouped by League
- **Dark Mode**: Toggleable theme
- **Responsive**: Mobile-friendly grid layout

## 🖼 Image Caching

The system automatically downloads team and league logos to `public/images/`.
- **Downloader**: `app/image_downloader.py` handles fetching and saving.
- **Naming**: Files are named using team slugs (e.g., `kairat-almaty.png`).
- **Storage**: Database stores the relative local path (e.g., `/images/teams/kairat-almaty.png`).

## 🐳 Docker Helper Script (`./dc`)

- `./dc up` - Start web server container
- `./dc run` - Run the scraper
- `./dc logs` - View logs
- `./dc shell` - Open shell in container
- `./dc test` - Run tests

## 🔧 Troubleshooting

- **Server not starting?** Check if port 8080 is free.
- **Images missing?** Run `./dc run` to re-scrape and download images.
- **Database errors?** Delete `db/matches.db` and run `./dc run` to recreate.

