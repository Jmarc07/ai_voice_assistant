# commands/app_control.py
import os
import sys
import re
import subprocess
import platform

# Import settings and modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.constants import COMMON_APPS
from logs.logger import logger

class AppControl:
    def __init__(self, assistant):
        self.assistant = assistant
        self.system = platform.system()
        logger.info(f"App control handler initialized for {self.system} platform")
    
    def handle(self, command, is_admin=False):
        """
        Handle application control commands
        
        Args:
            command (str): The command to open an application
            is_admin (bool): Whether the user has admin privileges
        
        Returns:
            bool: True if the command was handled successfully, False otherwise
        """
        try:
            # Extract the application name from the command
            app_name = self._extract_app_name(command)
            
            if not app_name:
                self.assistant.respond("What application would you like me to open?")
                return False
            
            logger.info(f"Attempting to open application: {app_name}")
            
            # Try to get the actual executable name for common apps
            app_executable = self._get_app_executable(app_name)
            
            # Open the application
            success = self._open_application(app_executable)
            
            if success:
                self.assistant.respond(f"Opening {app_name}.")
                return True
            else:
                self.assistant.respond(f"I couldn't find or open {app_name}.")
                return False
                
        except Exception as e:
            logger.error(f"Error opening application: {e}")
            self.assistant.respond("I had trouble opening that application.")
            return False
    
    def _extract_app_name(self, command):
        """Extract the application name from the command"""
        # Look for patterns like "open X", "start X", "launch X", "run X"
        patterns = [
            r'open\s+(.+)',
            r'start\s+(.+)',
            r'launch\s+(.+)',
            r'run\s+(.+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, command.lower())
            if match:
                return match.group(1).strip()
        
        return None
    
    def _get_app_executable(self, app_name):
        """
        Get the actual executable name for common applications
        Or return the app_name if not found in common apps
        """
        # Check if it's a common app
        for common_name, executable in COMMON_APPS.items():
            if app_name.lower() == common_name.lower() or app_name.lower() in common_name.lower():
                return executable
        
        # If not found in common apps, return the app name itself
        return app_name
    
    def _open_application(self, app_name):
        """Open an application based on the current operating system"""
        try:
            if self.system == 'Windows':
                # Try to open using the start command
                subprocess.Popen(f'start {app_name}', shell=True)
                return True
            
            elif self.system == 'Darwin':  # macOS
                # Try to open using the open command
                subprocess.Popen(['open', '-a', app_name])
                return True
            
            elif self.system == 'Linux':
                # Try to open using various methods
                try:
                    subprocess.Popen([app_name])
                except FileNotFoundError:
                    try:
                        # Try with the which command to find the executable
                        app_path = subprocess.check_output(['which', app_name]).decode().strip()
                        subprocess.Popen([app_path])
                    except:
                        return False
                return True
            
            else:
                logger.error(f"Unsupported operating system: {self.system}")
                return False
                
        except Exception as e:
            logger.error(f"Error opening application '{app_name}': {e}")
            return False