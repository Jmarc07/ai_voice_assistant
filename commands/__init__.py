# __init__.py - Initializes the commands package

# Import all command modules to make them available
from commands.web_search import web_search
from commands.app_control import open_application
from commands.file_management import create_file
from commands.system_control import control_system

# Define package exports
__all__ = ['web_search', 'open_application', 'create_file', 'control_system']