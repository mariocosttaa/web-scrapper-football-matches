"""
Start Web Server
================
Starts the Flask web server for the landing page.
This is used by Docker to automatically start the server when container starts.
"""

import logging
from app.logger import setup_logging
from app.landing_page import run_server
import config

if __name__ == "__main__":
    # Set up logging
    logger = setup_logging("app-log.log")
    
    # Start web server
    logger.info("="*60)
    logger.info("Starting MarFutGames Web Server")
    logger.info("="*60)
    
    print("\n" + "="*60)
    print("🚀 MarFutGames Web Server")
    print("="*60)
    print(f"🌐 Frontend: http://localhost:{config.WEB_SERVER_PORT}/")
    print(f"🔌 API: http://localhost:{config.WEB_SERVER_PORT}/api/matches")
    print(f"❤️  Health: http://localhost:{config.WEB_SERVER_PORT}/api/health")
    print("="*60)
    print("💡 Server is running. Use './dc run' to run the scraper.")
    print("="*60 + "\n")
    
    # Run server (this blocks)
    run_server(
        host=config.WEB_SERVER_HOST,
        port=config.WEB_SERVER_PORT,
        debug=False
    )

