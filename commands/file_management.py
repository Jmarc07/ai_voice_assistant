# file_management.py - Handles file creation and management

import os
import re
import platform
import subprocess
from datetime import datetime
from logs.logger import log_action, log_error
from config.constants import FILE_CREATE_KEYWORDS
from config.settings import DEFAULT_TEXT_EDITOR

def create_file(command):
    """
    Create a new file based on the command.
    
    Args:
        command (str): The command containing file details
        
    Returns:
        str: Response message
    """
    try:
        # Extract file name and content from command
        file_info = extract_file_info(command)
        
        if not file_info["name"]:
            return "What would you like to name the file?"
        
        # Get the file path
        file_path = get_file_path(file_info["name"])
        
        log_action(f"Creating file: {file_path}")
        
        # Create the file
        with open(file_path, "w") as f:
            # Add default content or user-specified content
            if file_info["content"]:
                f.write(file_info["content"])
            else:
                f.write(f"File created by Voice Assistant\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Open the file in the default text editor if requested
        if file_info["open"]:
            open_file_in_editor(file_path)
            return f"I've created and opened {file_info['name']} for you."
        else:
            return f"I've created {file_info['name']} for you."
            
    except PermissionError:
        log_error(f"Permission denied when creating file: {file_path}")
        return "I don't have permission to create that file. Try a different location."
    except Exception as e:
        log_error("Error creating file", e)
        return "I encountered an error while trying to create the file. Please check file permissions."

def extract_file_info(command):
    """
    Extract file name, content, and open flag from command.
    
    Args:
        command (str): The command containing file details
        
    Returns:
        dict: Dictionary with file information
    """
    # Initialize file info
    file_info = {
        "name": "",
        "content": "",
        "open": False
    }
    
    # Remove create keywords from command
    cleaned_command = command.lower()
    for keyword in FILE_CREATE_KEYWORDS:
        cleaned_command = re.sub(f"{keyword}\\s+", "", cleaned_command, flags=re.IGNORECASE)
    
    # Check if user wants to open the file after creation
    if "and open" in cleaned_command or "then open" in cleaned_command:
        file_info["open"] = True
        cleaned_command = cleaned_command.replace("and open", "").replace("then open", "")
    
    # Check for content specification
    content_match = re.search(r"with content\s+(.+)", cleaned_command, re.IGNORECASE)
    if content_match:
        file_info["content"] = content_match.group(1).strip()
        cleaned_command = cleaned_command.replace(content_match.group(0), "")
    
    # Extract file name (what's left)
    file_name = cleaned_command.strip()
    
    # Add extension if not specified
    if file_name and "." not in file_name:
        file_name += ".txt"
    
    file_info["name"] = file_name
    
    return file_info

def get_file_path(file_name):
    """
    Get the full path for a file based on the OS.
    
    Args:
        file_name (str): The name of the file
        
    Returns:
        str: Full path to the file
    """
    # Determine appropriate directory based on OS
    if platform.system() == "Windows":
        # Windows - use Documents folder
        documents_path = os.path.join(os.path.expanduser("~"), "Documents")
    else:
        # macOS/Linux - use home directory
        documents_path = os.path.expanduser("~")
    
    # Create a voice assistant folder if it doesn't exist
    assistant_folder = os.path.join(documents_path, "VoiceAssistant")
    if not os.path.exists(assistant_folder):
        os.makedirs(assistant_folder)
    
    # Return full path
    return os.path.join(assistant_folder, file_name)

def open_file_in_editor(file_path):
    """
    Open a file in the default text editor.
    
    Args:
        file_path (str): Path to the file to open
    """
    try:
        current_os = platform.system().lower()
        
        if current_os == "windows":
            os.startfile(file_path)
        elif current_os == "darwin":  # macOS
            subprocess.Popen(["open", file_path])
        else:  # Linux
            subprocess.Popen([DEFAULT_TEXT_EDITOR, file_path])
            
        log_action(f"Opened file in editor: {file_path}")
        
    except Exception as e:
        log_error(f"Error opening file in editor: {file_path}", e)