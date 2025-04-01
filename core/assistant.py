# assistant.py - Main class that controls the assistant logic

import random
import time
from speech.speech_recognition import listen, is_wake_word
from speech.text_to_speech import speak
from core.authentication import authenticate_user
from core.command_processor import process_command
from logs.logger import log_action, log_command, log_error
from config.settings import WAKEWORD
from config.constants import GREETING_RESPONSES

class VoiceAssistant:
    """Main voice assistant class that controls the flow and processing of commands."""
    
    def __init__(self):
        """Initialize the voice assistant."""
        self.is_authenticated = False
        self.is_admin = False
        self.active = False
        self.listening = True
        log_action("Voice Assistant initialized")
    
    def start(self):
        """Start the voice assistant and listen for commands."""
        try:
            log_action("Starting voice assistant main loop")
            
            while self.listening:
                # Wait for wake word
                print("Listening for wake word...")
                
                # Listen for the wake word
                command = listen()
                
                if is_wake_word(command):
                    self.handle_wake_word()
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.1)
                
        except Exception as e:
            log_error("Error in assistant main loop", e)
            speak("I encountered an error and need to restart.")
    
    def handle_wake_word(self):
        """Handle actions after wake word is detected."""
        try:
            # Acknowledge wake word
            greeting = random.choice(GREETING_RESPONSES)
            speak(greeting)
            
            # Authenticate the user
            self.authenticate()
            
            # Start listening for commands if authenticated
            if self.is_authenticated:
                self.active = True
                self.listen_for_commands()
                
        except Exception as e:
            log_error("Error handling wake word", e)
            speak("I'm having trouble processing your request.")
    
    def authenticate(self):
        """Authenticate the user to determine access level."""
        try:
            log_action("Authenticating user")
            
            # Ask for authentication
            speak("Please provide authentication for access level.")
            
            # Get authentication result (admin or basic)
            self.is_admin, self.is_authenticated = authenticate_user()
            
            if self.is_authenticated:
                mode = "Admin" if self.is_admin else "Basic"
                log_action(f"User authenticated in {mode} mode")
                speak(f"{mode} mode activated.")
            else:
                log_action("Authentication failed")
                speak("Authentication failed. Please try again.")
                
        except Exception as e:
            log_error("Error during authentication", e)
            self.is_authenticated = False
            self.is_admin = False
            speak("Authentication error. Using basic mode.")
    
    def listen_for_commands(self):
        """Listen for and process user commands after wake word activation."""
        try:
            # Keep listening for commands until timeout or exit command
            command_count = 0
            max_commands = 5  # Listen for up to 5 commands before requiring wake word again
            
            while self.active and command_count < max_commands:
                speak("What would you like me to do?")
                
                # Listen for the command
                command = listen()
                
                if command and len(command.strip()) > 0:
                    log_command(command, self.is_admin)
                    
                    # Process the command
                    response = process_command(command, self.is_admin)
                    
                    # Speak the response
                    if response:
                        speak(response)
                    
                    # Increment command counter
                    command_count += 1
                    
                    # Check for exit command
                    if command.lower() in ["exit", "quit", "goodbye", "bye"]:
                        speak("Goodbye!")
                        self.active = False
                        break
                else:
                    # No command detected
                    speak("I didn't hear anything. Please try again.")
            
            # Reset active state if max commands reached
            if command_count >= max_commands:
                speak("Session timeout. Please say the wake word again when you need me.")
                self.active = False
                
        except Exception as e:
            log_error("Error listening for commands", e)
            speak("I encountered an error processing commands.")
            self.active = False