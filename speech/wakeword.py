# speech/wakeword.py
import os
import sys
import time

# Import settings and logger
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.settings import WAKEWORD
from logs.logger import logger
from speech.speech_recognition import SpeechRecognizer

class WakewordDetector:
    def __init__(self):
        self.wakeword = WAKEWORD.lower()
        self.recognizer = SpeechRecognizer()
        logger.info(f"Wakeword detector initialized with wakeword: '{self.wakeword}'")
    
    def listen_for_wakeword(self):
        """
        Listen for the wake word
        
        Returns:
            bool: True if wake word is detected, False otherwise
        """
        logger.info("Listening for wake word...")
        
        # Using the speech recognizer to listen for the wake word
        text = self.recognizer.listen(phrase_time_limit=3)
        
        if text.lower().find(self.wakeword.lower()) != -1:
            logger.info("Wake word detected!")
            return True
        
        return False