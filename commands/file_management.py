# commands/file_management.py
import os
import sys
import re
import platform
import subprocess
from datetime import datetime

# Import settings and modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from logs.logger import logger

class FileManagement:
    def __init__(self, assistant):
        self.assistant = assistant
        self.system = platform.system()
        
        # Set default documents directory based on OS
        if self.system == 'Windows':
            self.docs_dir = os.path.join(os.path.expanduser('~'), 'Documents')
        elif self.system == 'Darwin':  # macOS
            self.docs_dir = os.path.join(os.path.expanduser('~'), 'Documents')
        else:  # Linux and others
            self.docs_dir = os.path.join(os.path.expanduser('~'), 'Documents')
            
            # Create Documents directory if it doesn't exist
            if not os.path.exists(self.docs_dir):
                try:
                    os.makedirs(self.docs_dir)
                except:
                    self.docs_dir = os.path.expanduser('~')
        
        logger.info(f"File management handler initialized with documents directory: {self.docs_dir}")
    
    def handle(self, command, is_admin=False):
        """
        Handle file management commands
        
        Args:
            command (str): The file management command
            is_admin (bool): Whether the user has admin privileges
        
        Returns:
            bool: True if the command was handled successfully, False otherwise
        """
        try:
            # Check what kind of file management command it is
            if self._is_create_file_command(command):
                return self._handle_create_file(command, is_admin)
            else:
                self.assistant.respond("I'm not sure what file operation you want me to perform.")
                return False
                
        except Exception as e:
            logger.error(f"Error in file management: {e}")
            self.assistant.respond("I had trouble with that file operation.")
            return False
    
    def _is_create_file_command(self, command):
        """Check if the command is to create a file"""
        create_patterns = [
            r'create (?:a |)file',
            r'make (?:a |)file',
            r'new file'
        ]
        
        command_lower = command.lower()
        return any(re.search(pattern, command_lower) for pattern in create_patterns)
    
    def _handle_create_file(self, command, is_admin):
        """Handle commands to create a new file"""
        # Extract the filename from the command
        filename = self._extract_filename(command)
        
        if not filename:
            # Ask for a filename if not provided
            self.assistant.respond("What would you like to name the file?")
            response = self.assistant.speech_recognizer.listen(phrase_time_limit=5)
            
            if response:
                filename = self._sanitize_filename(response)
            else:
                self.assistant.respond("I couldn't understand the filename.")
                return False
        
        # Add a default extension if none provided
        if '.' not in filename:
            filename += '.txt'
        
        # Create the full file path
        file_path = os.path.join(self.docs_dir, filename)
        
        # Create the file
        try:
            # Check if file already exists
            if os.path.exists(file_path):
                self.assistant.respond(f"A file named {filename} already exists. Would you like to overwrite it?")
                response = self.assistant.speech_recognizer.listen(phrase_time_limit=3)
                
                if not response or not ('yes' in response.lower() or 'yeah' in response.lower()):
                    self.assistant.respond("File creation cancelled.")
                    return False
            
            # Create the file
            with open(file_path, 'w') as f:
                f.write(f"File created by Voice Assistant on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            logger.info(f"Created file: {file_path}")
            self.assistant.respond(f"I've created a file named {filename} in your Documents folder.")
            
            # Ask if user wants to open the file
            self.assistant.respond("Would you like me to open this file for you?")
            response = self.assistant.speech_recognizer.listen(phrase_time_limit=3)
            
            if response and ('yes' in response.lower() or 'yeah' in response.lower()):
                self._open_file(file_path)
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating file {filename}: {e}")
            self.assistant.respond(f"I had trouble creating the file {filename}.")
            return False
    
    def _extract_filename(self, command):
        """Extract a filename from the command"""
        # Patterns to look for filenames
        patterns = [
            r'(?:called|named) ["\']?([^"\']+)["\']?',
            r'file ["\']?([^"\']+)["\']?',
            r'create (?:a |)file ["\']?([^"\']+)["\']?',
            r'make (?:a |)file ["\']?([^"\']+)["\']?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, command.lower())
            if match:
                return self._sanitize_filename(match.group(1))
        
        return None
    
    def _sanitize_filename(self, filename):
        """Clean up a filename to make it valid"""
        # Remove invalid characters
        invalid_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
        for char in invalid_chars:
            filename = filename.replace(char, '')
        
        # Trim whitespace
        filename = filename.strip()
        
        # If filename is empty, use a default name
        if not filename:
            filename = f"new_file_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return filename
    
    def _open_file(self, file_path):
        """Open a file with the default application"""
        try:
            if self.system == 'Windows':
                os.startfile(file_path)
            elif self.system == 'Darwin':  # macOS
                subprocess.Popen(['open', file_path])
            else:  # Linux and others
                subprocess.Popen(['xdg-open', file_path])
                
            self.assistant.respond("Opening the file now.")
            return True
        except Exception as e:
            logger.error(f"Error opening file {file_path}: {e}")
            self.assistant.respond("I couldn't open the file.")
            return False