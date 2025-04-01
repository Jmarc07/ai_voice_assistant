# core/authentication.py
import os
import sys

# Import settings and logger
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.settings import ADMIN_PASSWORD
from config.constants import RESPONSE_ADMIN_MODE, RESPONSE_BASIC_MODE, RESPONSE_AUTH_FAILED
from logs.logger import logger

class Authenticator:
    def __init__(self):
        self.is_authenticated = False
        self.is_admin = False
    
    def authenticate(self, password=None):
        """
        Authenticate the user based on the provided password
        
        Args:
            password (str, optional): The password to check. If None, user is authenticated in basic mode.
        
        Returns:
            tuple: (is_authenticated, is_admin, message)
        """
        # If no password is provided, authenticate as basic user
        if password is None:
            self.is_authenticated = True
            self.is_admin = False
            logger.info("User authenticated in basic mode (no password provided)")
            return True, False, RESPONSE_BASIC_MODE
        
        # Check if the password matches the admin password
        if password == ADMIN_PASSWORD:
            self.is_authenticated = True
            self.is_admin = True
            logger.info("User authenticated in admin mode")
            return True, True, RESPONSE_ADMIN_MODE
        else:
            # Invalid password, default to basic mode
            self.is_authenticated = True
            self.is_admin = False
            logger.warning("Authentication failed: incorrect password. Using basic mode.")
            return True, False, RESPONSE_AUTH_FAILED
    
    def check_admin_permission(self):
        """Check if the current user has admin permissions"""
        return self.is_admin
    
    def reset_authentication(self):
        """Reset the authentication state"""
        self.is_authenticated = False
        self.is_admin = False
        logger.info("Authentication has been reset")