# config/constants.py
# Constants used throughout the application

# Command types
CMD_WEB_SEARCH = ["search", "look up", "find", "google"]
CMD_APP_CONTROL = ["open", "start", "launch", "run"]
CMD_FILE_MANAGEMENT = ["create file", "make file", "new file"]
CMD_SYSTEM_CONTROL = ["volume", "brightness", "shutdown", "restart"]

# Common applications
COMMON_APPS = {
    "browser": "chrome",
    "notepad": "notepad",
    "calculator": "calc",
    "explorer": "explorer",
    "music": "spotify"
}

# System response messages
RESPONSE_GREETING = "Hello, I'm your voice assistant. How can I help you today?"
RESPONSE_NOT_UNDERSTOOD = "Sorry, I didn't understand that command."
RESPONSE_ADMIN_MODE = "Admin mode activated. You have full access to all commands."
RESPONSE_BASIC_MODE = "Basic mode activated. Some commands may be restricted."
RESPONSE_AUTH_FAILED = "Authentication failed. You'll be in basic mode."