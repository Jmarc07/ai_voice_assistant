# commands/file_management.py
import os
import sys
import re
from datetime import datetime

# Import settings and modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.constants import CMD_FILE_MANAGEMENT
from logs.logger import logger

class FileManagement:
    def __init__(self, assistant):
        self.assistant = assistant
        logger.info("File management handler initialized")
    
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
            # Determine the file operation type
            if "create" in command.lower() or "make" in command.lower() or "new" in command.lower():
                return self._handle_file_creation(command, is_admin)
            elif "delete" in command.lower() or "remove" in command.lower():
                if is_admin:
                    return self._handle_file_deletion(command)
                else:
                    logger.warning("Non-admin user attempted to delete a file")
                    self.assistant.respond("Sorry, deleting files requires admin mode.")
                    return False
            elif "rename" in command.lower():
                return self._handle_file_rename(command, is_admin)
            elif "list" in command.lower() or "show" in command.lower():
                return self._handle_list_files(command)
            else:
                logger.warning(f"Unrecognized file management command: {command}")
                self.assistant.respond("I don't understand that file command.")
                return False
                
        except Exception as e:
            logger.error(f"Error in file management: {e}")
            self.assistant.respond("I had trouble performing that file operation.")
            return False
    
    def _handle_file_creation(self, command, is_admin):
        """Handle file creation commands"""
        # Try to extract the filename and content
        file_name = self._extract_file_name(command)
        
        if not file_name:
            self.assistant.respond("What would you like to name the file?")
            file_name_response = self.assistant.speech_recognizer.listen(phrase_time_limit=5)
            file_name = file_name_response.strip()
            
            if not file_name:
                self.assistant.respond("I couldn't understand the filename.")
                return False
        
        # Add extension if not present
        if "." not in file_name:
            file_name += ".txt"  # Default to text file
        
        # Determine appropriate directory for saving
        file_path = self._get_save_path(file_name, is_admin)
        
        # Ask for content
        self.assistant.respond(f"What content would you like to put in {file_name}?")
        content = self.assistant.speech_recognizer.listen(phrase_time_limit=10)
        
        if not content:
            self.assistant.respond("I couldn't understand the content. Creating an empty file.")
            content = ""
        
        # Create the file
        try:
            with open(file_path, 'w') as file:
                file.write(content)
            
            logger.info(f"File created: {file_path}")
            self.assistant.respond(f"I've created the file {file_name} with your content.")
            return True
        except Exception as e:
            logger.error(f"Error creating file: {e}")
            self.assistant.respond(f"I couldn't create the file {file_name}. Make sure you have permission to write to this location.")
            return False
    
    def _handle_file_deletion(self, command):
        """Handle file deletion commands (admin only)"""
        # Extract the filename
        file_name = self._extract_file_name(command)
        
        if not file_name:
            self.assistant.respond("Which file would you like to delete?")
            file_name_response = self.assistant.speech_recognizer.listen(phrase_time_limit=5)
            file_name = file_name_response.strip()
            
            if not file_name:
                self.assistant.respond("I couldn't understand the filename.")
                return False
        
        # Search for the file in common directories
        file_path = self._find_file(file_name)
        
        if not file_path:
            self.assistant.respond(f"I couldn't find the file {file_name}.")
            return False
        
        # Confirm deletion
        self.assistant.respond(f"Are you sure you want to delete {file_name}? Say 'yes' to confirm.")
        confirmation = self.assistant.speech_recognizer.listen(phrase_time_limit=3)
        
        if not confirmation or 'yes' not in confirmation.lower():
            self.assistant.respond("File deletion cancelled.")
            return False
        
        # Delete the file
        try:
            os.remove(file_path)
            logger.info(f"File deleted: {file_path}")
            self.assistant.respond(f"File {file_name} has been deleted.")
            return True
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            self.assistant.respond(f"I couldn't delete the file {file_name}. Make sure you have permission to delete this file.")
            return False
    
    def _handle_file_rename(self, command, is_admin):
        """Handle file rename commands"""
        # Try to extract original filename
        match = re.search(r'rename\s+([^\s]+)\s+to\s+([^\s]+)', command.lower())
        
        if match:
            old_name = match.group(1)
            new_name = match.group(2)
        else:
            self.assistant.respond("Please specify which file you want to rename and the new name.")
            self.assistant.respond("For example, say 'rename file.txt to newfile.txt'")
            return False
        
        # Search for the file
        old_path = self._find_file(old_name)
        
        if not old_path:
            self.assistant.respond(f"I couldn't find the file {old_name}.")
            return False
        
        # Determine the new path
        new_path = os.path.join(os.path.dirname(old_path), new_name)
        
        # Check if the new file already exists
        if os.path.exists(new_path):
            self.assistant.respond(f"A file named {new_name} already exists. Please choose a different name.")
            return False
        
        # Rename the file
        try:
            os.rename(old_path, new_path)
            logger.info(f"File renamed: {old_path} -> {new_path}")
            self.assistant.respond(f"File {old_name} has been renamed to {new_name}.")
            return True
        except Exception as e:
            logger.error(f"Error renaming file: {e}")
            self.assistant.respond(f"I couldn't rename the file. Make sure you have permission to modify this file.")
            return False
    
    def _handle_list_files(self, command):
        """Handle commands to list files in a directory"""
        # Try to extract directory path
        directory = self._extract_directory(command)
        
        if not directory:
            # Default to user's home directory
            directory = os.path.expanduser("~")
        
        try:
            if not os.path.isdir(directory):
                self.assistant.respond(f"{directory} is not a valid directory.")
                return False
            
            # List files in the directory
            files = os.listdir(directory)
            
            if not files:
                self.assistant.respond(f"The directory {directory} is empty.")
                return True
            
            # Count files and format the response
            file_count = len(files)
            
            if file_count > 10:
                self.assistant.respond(f"There are {file_count} files in {directory}. Here are the first 10:")
                files = files[:10]
            else:
                self.assistant.respond(f"There are {file_count} files in {directory}. Here they are:")
            
            for file in files:
                self.assistant.respond(file)
            
            return True
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            self.assistant.respond("I had trouble listing the files in that directory.")
            return False
    
    def _extract_file_name(self, command):
        """Extract filename from a command"""
        # Try different patterns to extract the filename
        patterns = [
            r'(?:create|make|new|delete|remove)\s+(?:file|document)?\s+(?:called|named)?\s+([^\s]+)',
            r'(?:create|make|new|delete|remove)\s+(?:a\s+)?(?:file|document)?\s+(?:called|named)?\s+([^\s]+)',
            r'(?:create|make|new|delete|remove)\s+([^\s]+)\.(?:txt|doc|pdf|csv)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, command.lower())
            if match:
                return match.group(1)
        
        return None
    
    def _extract_directory(self, command):
        """Extract directory path from a command"""
        # Try to find "in directory" or "in folder" pattern
        match = re.search(r'(?:in|from)\s+(?:directory|folder|path)?\s+([^\s]+)', command.lower())
        
        if match:
            directory = match.group(1)
            
            # Expand user directory if using ~
            if directory.startswith('~'):
                directory = os.path.expanduser(directory)
            
            return directory
        
        return None
    
    def _get_save_path(self, file_name, is_admin):
        """Determine the appropriate save path for a file"""
        # Default to user's Documents folder
        user_docs = os.path.join(os.path.expanduser("~"), "Documents")
        
        if not os.path.exists(user_docs):
            # Fallback to user's home directory
            user_docs = os.path.expanduser("~")
        
        # Create a subdirectory for assistant-generated files
        assistant_dir = os.path.join(user_docs, "AssistantFiles")
        
        if not os.path.exists(assistant_dir):
            os.makedirs(assistant_dir)
        
        return os.path.join(assistant_dir, file_name)
    
    def _find_file(self, file_name):
        """Search for a file in common directories"""
        # List of directories to search
        search_dirs = [
            os.path.expanduser("~"),
            os.path.join(os.path.expanduser("~"), "Documents"),
            os.path.join(os.path.expanduser("~"), "Downloads"),
            os.path.join(os.path.expanduser("~"), "Desktop"),
            os.path.join(os.path.expanduser("~"), "Documents", "AssistantFiles")
        ]
        
        # Look for the file in each directory
        for directory in search_dirs:
            if not os.path.exists(directory):
                continue
                
            file_path = os.path.join(directory, file_name)
            
            if os.path.exists(file_path):
                return file_path
        
        return None