# constants.py - Define constants used throughout the application

# Command keywords
SEARCH_KEYWORDS = ["search", "look up", "find", "google"]
APP_OPEN_KEYWORDS = ["open", "launch", "start", "run"]
FILE_CREATE_KEYWORDS = ["create", "make", "new"]
SYSTEM_CONTROL_KEYWORDS = ["volume", "brightness", "shutdown", "restart"]

# Admin-only commands
ADMIN_COMMANDS = ["shutdown", "restart", "install", "uninstall", "update system"]

# Response templates
GREETING_RESPONSES = [
    "Hello! How can I help you today?",
    "Hi there! What can I do for you?",
    "Hey! Ready for your commands."
]

ERROR_RESPONSES = [
    "I'm sorry, I didn't understand that command.",
    "Could you please repeat that?",
    "I didn't quite catch that.",
    "I'm having trouble understanding your request."
]

ADMIN_MODE_MESSAGE = "Admin mode activated. You have access to all system functions."
BASIC_MODE_MESSAGE = "Basic mode activated. Some system functions are restricted."
UNAUTHORIZED_MESSAGE = "Sorry, you don't have permission to use this command. Admin access is required."