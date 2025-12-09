"""
Logging Configuration
=====================
Sets up logging to write to app-log.log file and console.
"""

import logging
import os
from datetime import datetime

# Global flag to track if logging is initialized
_logging_initialized = False


def setup_logging(log_file: str = "app-log.log"):
    """
    Set up logging configuration.
    
    Args:
        log_file: Path to log file (default: app-log.log)
        
    Returns:
        Logger instance
    """
    global _logging_initialized
    
    # Check if logging is already configured
    if _logging_initialized and logging.getLogger().handlers:
        return logging.getLogger(__name__)
    
    # Create logs directory if needed
    log_dir = os.path.dirname(log_file) if os.path.dirname(log_file) else "."
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    # Configure logging format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=[
            # File handler - write to app-log.log (append mode)
            logging.FileHandler(log_file, encoding='utf-8', mode='a'),
            # Console handler - also print to console
            logging.StreamHandler()
        ],
        force=True  # Override any existing configuration
    )
    
    # Mark as initialized
    _logging_initialized = True
    
    # Get logger for this module
    logger = logging.getLogger(__name__)
    logger.info("="*60)
    logger.info(f"Logging initialized - Log file: {os.path.abspath(log_file)}")
    logger.info(f"Application started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*60)
    
    return logger


def get_logger(name: str = None):
    """
    Get a logger instance.
    
    Args:
        name: Logger name (default: root logger)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)

