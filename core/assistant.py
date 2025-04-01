# core/assistant.py
import os
import sys
import time

# Import modules and components
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.constants import RESPONSE_GREETING, RESPONSE_NOT_UNDERSTOOD
from core.authentication import Authenticator
from speech.speech_recognition import SpeechRecognizer
from speech.text_to_speech import TextToSpeech
from speech.wakeword import WakewordDetector
from logs.logger import logger

class VoiceAssistant:
    def __init__(self):
        logger.info("Initializing Voice Assistant...")
        
        # Initialize components
        self.speech_recognizer = SpeechRecognizer()
        self.tts = TextToSpeech()
        self.wakeword_detector = WakewordDetector()
        self.authenticator = Authenticator()
        
        # Authentication state
        self.is_authenticated = False
        self.is_admin = False
        
        # Command processor will be imported later to avoid circular imports
        self.command_processor = None
        
        logger.info("Voice Assistant initialized successfully")
    
    def start(self):
        """Start the voice assistant and listen for commands"""
        logger.info("Starting Voice Assistant...")
        self.tts.speak(RESPONSE_GREETING)
        
        # Import command processor here to avoid circular imports
        from core.command_processor import CommandProcessor
        self.command_processor = CommandProcessor(self)
        
        try:
            while True:
                # Wait for wake word
                if self.wakeword_detector.listen_for_wakeword():
                    # Wake word detected, handle authentication
                    if not self.is_authenticated:
                        self._handle_authentication()
                    
                    # Listen for and process command
                    self._listen_and_process_command()
        except KeyboardInterrupt:
            logger.info("Voice Assistant stopped by user")
            self.tts.speak("Goodbye!")
        except Exception as e:
            logger.error(f"Error in Voice Assistant: {e}")
            self.tts.speak("I've encountered an error and need to shut down.")
    
    def _handle_authentication(self):
        """Handle user authentication"""
        self.tts.speak("Please provide your admin password or say 'basic mode' for limited access.")
        
        # Listen for password
        password_input = self.speech_recognizer.listen(phrase_time_limit=5)
        
        # Check if user wants basic mode
        if "basic mode" in password_input.lower():
            is_auth, is_admin, message = self.authenticator.authenticate(None)
        else:
            is_auth, is_admin, message = self.authenticator.authenticate(password_input)
        
        # Update authentication state
        self.is_authenticated = is_auth
        self.is_admin = is_admin
        
        # Provide feedback to user
        self.tts.speak(message)
    
    def _listen_and_process_command(self):
        """Listen for a command and process it"""
        self.tts.speak("How can I help you?")
        
        # Listen for command
        command = self.speech_recognizer.listen(phrase_time_limit=5)
        
        if command:
            # Process the command
            if self.command_processor:
                self.command_processor.process_command(command, self.is_admin)
            else:
                logger.error("Command processor not initialized")
                self.tts.speak(RESPONSE_NOT_UNDERSTOOD)
        else:
            self.tts.speak(RESPONSE_NOT_UNDERSTOOD)
    
    def respond(self, text):
        """Speak a response to the user"""
        self.tts.speak(text)