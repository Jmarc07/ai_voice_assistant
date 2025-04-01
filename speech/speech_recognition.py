# speech/speech_recognition.py
import os
import sys
import speech_recognition as sr

# Import settings and logger
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.settings import LANGUAGE
from logs.logger import logger

class SpeechRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.language = LANGUAGE
        
        # Adjust for ambient noise level
        self.adjust_for_ambient_noise()
    
    def adjust_for_ambient_noise(self):
        """Adjust the recognizer sensitivity to ambient noise"""
        logger.info("Adjusting for ambient noise...")
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        logger.info("Ambient noise adjustment complete")
    
    def listen(self, timeout=None, phrase_time_limit=None):
        """
        Listen for speech and convert it to text
        
        Args:
            timeout (int, optional): Seconds of non-speaking audio before a phrase is considered complete
            phrase_time_limit (int, optional): Maximum number of seconds that a phrase continues before stopping
        
        Returns:
            str: The recognized text or an empty string if recognition fails
        """
        try:
            with sr.Microphone() as source:
                logger.info("Listening...")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                
                try:
                    logger.info("Recognizing speech...")
                    text = self.recognizer.recognize_google(audio, language=self.language)
                    logger.info(f"Recognized: '{text}'")
                    return text
                except sr.UnknownValueError:
                    logger.warning("Speech Recognition could not understand audio")
                    return ""
                except sr.RequestError as e:
                    logger.error(f"Could not request results from Speech Recognition service; {e}")
                    return ""
        except Exception as e:
            logger.error(f"Error in speech recognition: {e}")
            return ""