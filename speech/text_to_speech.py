# speech/text_to_speech.py
import os
import sys
import pyttsx3
from gtts import gTTS
import tempfile
import playsound
import time

# Import settings and logger
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.settings import VOICE_ENGINE, VOICE_RATE, VOICE_VOLUME, LANGUAGE
from logs.logger import logger

class TextToSpeech:
    def __init__(self):
        self.engine_type = VOICE_ENGINE
        self.rate = VOICE_RATE
        self.volume = VOICE_VOLUME
        self.language = LANGUAGE
        
        # Initialize the appropriate TTS engine
        if self.engine_type.lower() == 'pyttsx3':
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', self.rate)
            self.engine.setProperty('volume', self.volume)
            
            # Get available voices
            voices = self.engine.getProperty('voices')
            if voices:
                # Set a default voice - using the first available voice
                self.engine.setProperty('voice', voices[0].id)
    
    def speak(self, text):
        """
        Convert text to speech and play it
        
        Args:
            text (str): The text to be spoken
        """
        if not text:
            return
            
        logger.info(f"Speaking: '{text}'")
        
        try:
            if self.engine_type.lower() == 'pyttsx3':
                self.engine.say(text)
                self.engine.runAndWait()
            elif self.engine_type.lower() == 'gtts':
                with tempfile.NamedTemporaryFile(delete=True) as fp:
                    temp_filename = f"{fp.name}.mp3"
                tts = gTTS(text=text, lang=self.language[:2])
                tts.save(temp_filename)
                playsound.playsound(temp_filename)
                try:
                    os.remove(temp_filename)
                except:
                    pass
        except Exception as e:
            logger.error(f"Error in text-to-speech: {e}")
