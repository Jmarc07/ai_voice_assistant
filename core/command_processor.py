# command_processor.py - Processes commands and routes to appropriate handlers

from logs.logger import log_action, log_error
from config.constants import (
    SEARCH_KEYWORDS, APP_OPEN_KEYWORDS, FILE_CREATE_KEYWORDS,
    SYSTEM_CONTROL_KEYWORDS, ADMIN_COMMANDS, UNAUTHORIZED_MESSAGE
)

# Import command modules
from commands.web_search import web_search
from commands.app_control import open_application
from commands.file_management import create_file
from commands.system_control import control_system

def process_command(command, is_admin):
    """
    Process a user command and route it to the appropriate handler.
    
    Args:
        command (str): The command to process
        is_admin (bool): Whether the user is authenticated as admin
        
    Returns:
        str: Response message to the user
    """
    try:
        # Convert command to lowercase for easier matching
        cmd_lower = command.lower()
        
        # Check for admin-only commands
        if any(admin_cmd in cmd_lower for admin_cmd in ADMIN_COMMANDS) and not is_admin:
            log_action(f"Unauthorized admin command attempted: {command}")
            return UNAUTHORIZED_MESSAGE
            
        # Route command to appropriate handler based on keywords
        
        # Web search commands
        if any(keyword in cmd_lower for keyword in SEARCH_KEYWORDS):
            log_action(f"Processing search command: {command}")
            return web_search(command)
            
        # App control commands
        elif any(keyword in cmd_lower for keyword in APP_OPEN_KEYWORDS):
            log_action(f"Processing app command: {command}")
            return open_application(command)
            
        # File management commands
        elif any(keyword in cmd_lower for keyword in FILE_CREATE_KEYWORDS):
            log_action(f"Processing file command: {command}")
            return create_file(command)
            
        # System control commands (admin check handled within function)
        elif any(keyword in cmd_lower for keyword in SYSTEM_CONTROL_KEYWORDS):
            log_action(f"Processing system command: {command}")
            return control_system(command, is_admin)
            
        # Handle help command
        elif "help" in cmd_lower:
            log_action("Help command requested")
            return get_help_message(is_admin)
            
        # Handle exit/quit command
        elif any(word in cmd_lower for word in ["exit", "quit", "goodbye", "bye"]):
            log_action("Exit command received")
            return "Goodbye! Say the wake word when you need me again."
            
        # Unknown command
        else:
            log_action(f"Unknown command: {command}")
            return "I'm not sure how to process that command. Try saying 'help' for available commands."
            
    except Exception as e:
        log_error("Error processing command", e)
        return "I encountered an error processing your command. Please try again."

def get_help_message(is_admin):
    """
    Generate a help message based on user's access level.
    
    Args:
        is_admin (bool): Whether the user is authenticated as admin
        
    Returns:
        str: Help message with available commands
    """
    basic_commands = [
        "Search for [topic] - Search the web",
        "Open [application] - Launch an application",
        "Create file [filename] - Create a new file",
        "Help - Show this help message",
        "Exit/Quit/Goodbye - End the current session"
    ]
    
    admin_commands = [
        "Volume [up/down/mute] - Control system volume",
        "Shutdown/Restart - Control system power",
        "Install [program] - Install new software",
        "Update system - Check for system updates"
    ]
    
    help_message = "Available commands:\n" + "\n".join(basic_commands)
    
    if is_admin:
        help_message += "\n\nAdmin commands:\n" + "\n".join(admin_commands)
    
    return help_message