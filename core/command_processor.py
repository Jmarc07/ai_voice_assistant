# core/command_processor.py
import os
import sys

# Import settings and modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.constants import (
    CMD_WEB_SEARCH, CMD_APP_CONTROL, CMD_FILE_MANAGEMENT, 
    CMD_SYSTEM_CONTROL, RESPONSE_NOT_UNDERSTOOD
)
from logs.logger import logger

class CommandProcessor:
    def __init__(self, assistant):
        self.assistant = assistant
        logger.info("Command processor initialized")
        
        # Import command handlers here to avoid circular imports
        from commands.web_search import WebSearch
        from commands.app_control import AppControl
        from commands.file_management import FileManagement
        from commands.system_control import SystemControl
        
        # Initialize command handlers
        self.web_search = WebSearch(assistant)
        self.app_control = AppControl(assistant)
        self.file_management = FileManagement(assistant)
        self.system_control = SystemControl(assistant)
    
    def process_command(self, command_text, is_admin=False):
        """
        Process a command and route it to the appropriate handler
        
        Args:
            command_text (str): The command text to process
            is_admin (bool): Whether the user has admin privileges
        
        Returns:
            bool: True if the command was processed successfully, False otherwise
        """
        if not command_text:
            logger.warning("Empty command received")
            self.assistant.respond(RESPONSE_NOT_UNDERSTOOD)
            return False
        
        # Log the command
        logger.log_command(command_text, is_admin)
        
        # Convert to lowercase for easier matching
        command_lower = command_text.lower()
        
        # Check for web search commands
        if any(keyword in command_lower for keyword in CMD_WEB_SEARCH):
            return self.web_search.handle(command_text, is_admin)
        
        # Check for app control commands
        elif any(keyword in command_lower for keyword in CMD_APP_CONTROL):
            return self.app_control.handle(command_text, is_admin)
        
        # Check for file management commands
        elif any(keyword in command_lower for keyword in CMD_FILE_MANAGEMENT):
            return self.file_management.handle(command_text, is_admin)
        
        # Check for system control commands (admin only)
        elif any(keyword in command_lower for keyword in CMD_SYSTEM_CONTROL):
            if is_admin:
                return self.system_control.handle(command_text, is_admin)
            else:
                logger.warning("Non-admin user attempted to use system control command")
                self.assistant.respond("Sorry, system control commands require admin mode.")
                return False
        
        # Special commands
        elif "help" in command_lower:
            self._show_help(is_admin)
            return True
        
        elif "exit" in command_lower or "goodbye" in command_lower or "bye" in command_lower:
            self.assistant.respond("Goodbye! Voice assistant is shutting down.")
            logger.info("Exit command received, shutting down")
            sys.exit(0)
        
        # Command not recognized
        else:
            logger.warning(f"Unrecognized command: {command_text}")
            self.assistant.respond(RESPONSE_NOT_UNDERSTOOD)
            return False
    
    def _show_help(self, is_admin):
        """Show available commands based on user's access level"""
        help_text = "Here are some commands you can use:\n"
        help_text += "- Search for information by saying 'search for' followed by your query\n"
        help_text += "- Open applications by saying 'open' followed by the app name\n"
        help_text += "- Create files by saying 'create file' followed by the filename\n"
        
        if is_admin:
            help_text += "\nAs an admin, you can also:\n"
            help_text += "- Control system settings like volume by saying 'volume up' or 'volume down'\n"
            help_text += "- Shutdown or restart the system\n"
        
        help_text += "\nYou can say 'exit' or 'goodbye' to shut down the assistant."
        
        self.assistant.respond(help_text)