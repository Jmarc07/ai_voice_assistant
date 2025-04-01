# app_control.py - Handles opening applications

import os
import subprocess
import platform
import re
from logs.logger import log_action, log_error
from config.constants import APP_OPEN_KEYWORDS

# Dictionary of common applications and their commands for different platforms
COMMON_APPS = {
    "windows": {
        "chrome": "start chrome",
        "firefox": "start firefox",
        "edge": "start msedge",
        "notepad": "start notepad",
        "word": "start winword",
        "excel": "start excel",
        "calculator": "start calc",
        "explorer": "start explorer",
        "cmd": "start cmd",
        "powershell": "start powershell"
    },
    "darwin": {  # macOS
        "chrome": "open -a 'Google Chrome'",
        "firefox": "open -a Firefox",
        "safari": "open -a Safari",
        "textedit": "open -a TextEdit",
        "calculator": "open -a Calculator",
        "finder": "open -a Finder",
        "terminal": "open -a Terminal"
    },
    "linux": {
        "chrome": "google-chrome",
        "firefox": "firefox",
        "gedit": "gedit",
        "calculator": "gnome-calculator",
        "files": "nautilus",
        "terminal": "gnome-terminal"
    }
}

def open_application(command):
    """
    Open an application based on the command.
    
    Args:
        command (str): The command containing the app name
        
    Returns:
        str: Response message
    """
    try:
        # Get the current operating system
        current_os = platform.system().lower()
        if current_os == "darwin":
            os_name = "macOS"
        elif current_os == "windows":
            os_name = "Windows"
        elif current_os == "linux":
            os_name = "Linux"
        else:
            os_name = "your operating system"
        
        # Extract app name by removing open keywords
        app_name = command.lower()
        for keyword in APP_OPEN_KEYWORDS:
            app_name = re.sub(f"{keyword}\\s+", "", app_name, flags=re.IGNORECASE)
        
        # Clean up the app name
        app_name = app_name.strip()
        
        if not app_name:
            return "Which application would you like me to open?"
        
        log_action(f"Attempting to open application: {app_name}")
        
        # Get OS-specific app dictionary
        if current_os in COMMON_APPS:
            os_apps = COMMON_APPS[current_os]
            
            # Check if the app is in our dictionary
            for app_key, app_command in os_apps.items():
                if app_key in app_name or app_name in app_key:
                    # Execute the command to open the application
                    subprocess.Popen(app_command, shell=True)
                    log_action(f"Opened application: {app_key}")
                    return f"Opening {app_key} for you."
            
            # If app not found in dictionary, try to open it directly
            if current_os == "windows":
                subprocess.Popen(f"start {app_name}", shell=True)
            elif current_os == "darwin":
                subprocess.Popen(f"open -a '{app_name}'", shell=True)
            elif current_os == "linux":
                subprocess.Popen(app_name, shell=True)
            
            log_action(f"Attempted to open unknown application: {app_name}")
            return f"I've tried to open {app_name}, but I'm not sure if it exists on {os_name}."
        
        else:
            log_error(f"Unsupported operating system: {current_os}")
            return f"I'm not sure how to open applications on {os_name}."
            
    except Exception as e:
        log_error(f"Error opening application: {app_name}", e)
        return f"I encountered an error trying to open {app_name}. Please check if it's installed."