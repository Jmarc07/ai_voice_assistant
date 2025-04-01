# __init__.py - Initializes the core package

# Import all core modules to make them available
from core.assistant import VoiceAssistant
from core.authentication import authenticate_user
from core.command_processor import process_command

# Define package exports
__all__ = ['VoiceAssistant', 'authenticate_user', 'process_command']