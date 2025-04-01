# text_to_speech.py - Converts text to speech for the assistant

import pyttsx3
import subprocess
import shutil
import os
from logs.logger import log_action, log_error
from config.settings import VOICE_ENGINE, VOICE_RATE, VOICE_VOLUME, VOICE_GENDER, DEBUG_MODE

# Initialize the TTS engine
engine = None
# Flag to track if we're in text-only mode
TEXT_ONLY_MODE = False

def check_audio_dependencies():
    """Check if necessary audio dependencies are available and functioning."""
    # First check if we're in a headless or container environment
    if 'DISPLAY' not in os.environ:
        log_action("No display detected, likely headless environment", "WARNING")
        return False
    
    # Check for aplay binary
    if shutil.which('aplay') is None:
        log_action("Audio player 'aplay' not found", "WARNING")
        return False
    
    # Test if ALSA can actually access audio devices
    try:
        # Try to list audio devices
        result = subprocess.run(
            ["aplay", "-l"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True,
            timeout=1
        )
        
        # Check if any sound cards were found
        if "no soundcards found" in result.stderr.lower() or result.returncode != 0:
            log_action("ALSA reports no sound cards available", "WARNING")
            return False
            
        # If we got here, audio should be working
        return True
        
    except (subprocess.SubprocessError, subprocess.TimeoutExpired) as e:
        log_action(f"Error testing audio capabilities: {e}", "WARNING")
        return False

def initialize_engine():
    """Initialize and configure the text-to-speech engine."""
    global engine, TEXT_ONLY_MODE
    
    # If audio dependencies aren't available, default to text-only mode
    if not check_audio_dependencies():
        TEXT_ONLY_MODE = True
        log_action("Audio system not available, forcing text-only mode", "WARNING")
        print("\n[SYSTEM] Audio system not available. This could be because:")
        print("  - Running in a container or virtualized environment")
        print("  - No sound card detected or properly configured")
        print("  - Missing ALSA utilities or configuration")
        print("[SYSTEM] Continuing in text-only mode...\n")
        return False
    
    # If in debug mode and TTS fails, default to text-only
    if DEBUG_MODE:
        try:
            if VOICE_ENGINE == "pyttsx3":
                engine = pyttsx3.init()
                
                # Configure voice properties
                engine.setProperty('rate', VOICE_RATE)
                engine.setProperty('volume', VOICE_VOLUME)
                
                # Set voice gender
                voices = engine.getProperty('voices')
                if VOICE_GENDER.lower() == "female" and len(voices) > 1:
                    engine.setProperty('voice', voices[1].id)  # Female voice
                else:
                    engine.setProperty('voice', voices[0].id)  # Male voice
                
                log_action("Text-to-speech engine initialized")
                return True
            else:
                log_error(f"Unsupported TTS engine: {VOICE_ENGINE}")
                TEXT_ONLY_MODE = True
                return False
        except Exception as e:
            log_error("Failed to initialize text-to-speech engine", e)
            TEXT_ONLY_MODE = True
            print("\n[SYSTEM] TTS initialization failed. Missing dependencies.")
            print("[SYSTEM] On Linux, install espeak with: sudo apt-get install espeak")
            print("[SYSTEM] On Linux, install alsa-utils with: sudo apt-get install alsa-utils")
            print("[SYSTEM] Continuing in text-only mode...\n")
            return False
    else:
        # Non-debug mode logic (original)
        try:
            if VOICE_ENGINE == "pyttsx3":
                engine = pyttsx3.init()
                
                # Configure voice properties
                engine.setProperty('rate', VOICE_RATE)
                engine.setProperty('volume', VOICE_VOLUME)
                
                # Set voice gender
                voices = engine.getProperty('voices')
                if VOICE_GENDER.lower() == "female" and len(voices) > 1:
                    engine.setProperty('voice', voices[1].id)  # Female voice
                else:
                    engine.setProperty('voice', voices[0].id)  # Male voice
                
                log_action("Text-to-speech engine initialized")
                return True
            else:
                log_error(f"Unsupported TTS engine: {VOICE_ENGINE}")
                return False
        except Exception as e:
            log_error("Failed to initialize text-to-speech engine", e)
            return False

def speak(text):
    """
    Convert text to speech and play it.
    
    Args:
        text (str): The text to convert to speech
    """
    global engine, TEXT_ONLY_MODE
    
    try:
        # Initialize engine if not already done
        if engine is None and not TEXT_ONLY_MODE:
            if not initialize_engine():
                TEXT_ONLY_MODE = True
        
        # Log the text being spoken
        log_action(f"Speaking: {text}")
        
        # Print text for debugging/accessibility
        if TEXT_ONLY_MODE:
            print(f"\n[ASSISTANT]: {text}\n")
        else:
            print(f"Assistant: {text}")
            
            # Convert to speech and play
            try:
                engine.say(text)
                engine.runAndWait()
            except Exception as e:
                log_error("Error in text-to-speech playback", e)
                print(f"[ERROR] Speech playback failed. Continuing in text-only mode.")
                TEXT_ONLY_MODE = True
                print(f"\n[ASSISTANT]: {text}\n")
        
    except Exception as e:
        log_error("Error in text-to-speech", e)
        print(f"[ERROR] Could not speak: {text}")
        print(f"\n[ASSISTANT]: {text}\n")