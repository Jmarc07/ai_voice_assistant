# authentication.py - Handles user authentication

from getpass import getpass
from speech.text_to_speech import speak
from speech.speech_recognition import listen
from logs.logger import log_action, log_error
from config.settings import ADMIN_PASSWORD

def authenticate_user():
    """
    Authenticate the user to determine access level.
    
    Returns:
        tuple: (is_admin, is_authenticated) boolean values
    """
    try:
        # Ask if the user wants to authenticate as admin
        speak("Do you want to authenticate as admin? Say yes or no.")
        response = listen().lower()
        
        # If user doesn't want admin access, return basic mode
        if response not in ["yes", "yeah", "yep", "sure", "okay"]:
            log_action("User chose basic mode")
            return False, True  # Not admin, but authenticated for basic use
        
        # Ask for the admin password
        speak("Please enter the admin password.")
        print("Enter admin password (input will be hidden): ", end="")
        
        # Get password from terminal (hidden input)
        password = getpass("")
        
        # Check if password matches
        if password == ADMIN_PASSWORD:
            log_action("Admin authentication successful")
            return True, True  # Admin mode, authenticated
        else:
            log_action("Admin authentication failed, using basic mode")
            speak("Incorrect password. Using basic mode.")
            return False, True  # Not admin, but authenticated for basic use
            
    except Exception as e:
        log_error("Authentication error", e)
        return False, True  # Default to basic mode on error