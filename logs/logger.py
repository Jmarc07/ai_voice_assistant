# logger.py - Handles logging of assistant's actions

import logging
import os
import datetime
from config.settings import LOG_FILE, LOG_LEVEL

def setup_logger():
    """Set up the logger for the voice assistant."""
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(LOG_FILE)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Convert string log level to logging level
    numeric_level = getattr(logging, LOG_LEVEL.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {LOG_LEVEL}")
    
    # Configure the logger
    logging.basicConfig(
        filename=LOG_FILE,
        level=numeric_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Log application startup
    logging.info("Voice Assistant started")

def log_action(action, level="INFO"):
    """Log an action performed by the assistant.
    
    Args:
        action (str): The action to log
        level (str): Log level (INFO, WARNING, ERROR, etc.)
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    logging.log(log_level, action)

def log_command(command, is_admin=False):
    """Log a user command.
    
    Args:
        command (str): The command issued by the user
        is_admin (bool): Whether the command was issued in admin mode
    """
    mode = "ADMIN" if is_admin else "BASIC"
    logging.info(f"[{mode} MODE] Command: {command}")

def log_error(error_message, exception=None):
    """Log an error that occurred.
    
    Args:
        error_message (str): Description of the error
        exception (Exception, optional): The exception object
    """
    if exception:
        logging.error(f"{error_message}: {str(exception)}")
    else:
        logging.error(error_message)