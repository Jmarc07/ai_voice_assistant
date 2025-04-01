# speech_recognition.py - Handles speech-to-text conversion

import speech_recognition as sr
import subprocess
import shutil
import os
from logs.logger import log_action, log_error
from config.settings import WAKEWORD, DEBUG_MODE

# Initialize recognizer globally for reuse
recognizer = sr.Recognizer()

def check_audio_input_available():
    """Check if audio input devices are available and functioning."""
    # If we're already in debug mode, skip the check
    if DEBUG_MODE:
        return False
        
    # First check if we're in a headless or container environment
    if 'DISPLAY' not in os.environ:
        log_action("No display detected, likely headless environment", "WARNING")
        return False
    
    try:
        # Try to list available microphones
        mics = sr.Microphone.list_microphone_names()
        if not mics:
            log_action("No microphones found", "WARNING")
            return False
            
        return True
    except Exception as e:
        log_action(f"Error checking microphone availability: {e}", "WARNING")
        return False

def listen(timeout=5, phrase_time_limit=None):
    """
    Listen to the microphone and convert speech to text.
    
    Args:
        timeout (int): How long to wait before timing out (seconds)
        phrase_time_limit (int, optional): Max length of phrase to detect
    
    Returns:
        str: The recognized text, or empty string if nothing recognized
    """
    # Check if we're in debug mode or if audio input is not available
    if DEBUG_MODE or not check_audio_input_available():
        return text_input_fallback()
        
    try:
        with sr.Microphone() as source:
            print("Listening...")
            
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            # Set dynamic energy threshold
            recognizer.energy_threshold = 4000
            recognizer.dynamic_energy_threshold = True
            
            # Listen for audio
            audio = recognizer.listen(
                source, 
                timeout=timeout,
                phrase_time_limit=phrase_time_limit
            )
            
            print("Processing speech...")
            
            # Use Google Speech Recognition
            text = recognizer.recognize_google(audio)
            print(f"Recognized: {text}")
            return text
            
    except sr.WaitTimeoutError:
        log_action("Speech recognition timeout - no speech detected", "WARNING")
        return ""
    except sr.UnknownValueError:
        log_action("Speech recognition could not understand audio", "WARNING")
        return ""
    except sr.RequestError as e:
        log_error(f"Could not request results from Google Speech Recognition service", e)
        return ""
    except Exception as e:
        log_error("Error in speech recognition", e)
        return text_input_fallback()

def text_input_fallback():
    """
    Fallback to text input when speech recognition is not available.
    
    Returns:
        str: The text entered by the user
    """
    print("\n[DEBUG MODE] Using text input instead of speech recognition")
    text = input("Type your command (or 'exit' to quit): ")
    return text

def is_wake_word(text):
    """
    Check if the recognized text contains the wake word.
    
    Args:
        text (str): The text to check for wake word
    
    Returns:
        bool: True if wake word found, False otherwise
    """
    if not text:
        return False
    
    # In debug mode, allow special commands
    if DEBUG_MODE and text.lower() == "activate":
        log_action("Debug wake word detected")
        return True
    
    # Case-insensitive check for wake word
    wake_word_found = WAKEWORD.lower() in text.lower()
    
    if wake_word_found:
        log_action(f"Wake word detected: {text}")
    
    return wake_word_found