# logs/logger.py
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Import settings
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.settings import LOG_FILE, LOG_LEVEL

class Logger:
    def __init__(self):
        # Create logs directory if it doesn't exist
        log_dir = Path(os.path.dirname(__file__))
        log_dir.mkdir(exist_ok=True)
        
        # Set up logging configuration
        log_levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        
        # Set log level (default to INFO if setting is invalid)
        log_level = log_levels.get(LOG_LEVEL, logging.INFO)
        
        # Configure the logger
        logging.basicConfig(
            filename=os.path.join(log_dir, LOG_FILE),
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Add console handler to display logs in console as well
        console = logging.StreamHandler()
        console.setLevel(log_level)
        formatter = logging.Formatter('%(levelname)s - %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)
    
    def debug(self, message):
        logging.debug(message)
    
    def info(self, message):
        logging.info(message)
    
    def warning(self, message):
        logging.warning(message)
    
    def error(self, message):
        logging.error(message)
    
    def critical(self, message):
        logging.critical(message)
    
    def log_command(self, command, is_admin=False):
        """Log commands with admin status"""
        mode = "ADMIN" if is_admin else "BASIC"
        logging.info(f"[{mode} MODE] Command: {command}")
    
    def log_response(self, response):
        """Log assistant responses"""
        logging.info(f"Assistant Response: {response}")

# Create a global logger instance
logger = Logger()