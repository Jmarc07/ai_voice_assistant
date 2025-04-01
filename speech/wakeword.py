# wakeword.py - Handles wake word detection
# Note: For a complete implementation, you would need to install packages like pvporcupine

import time
from logs.logger import log_action, log_error
from config.settings import WAKEWORD

# Flag to indicate if we're using the advanced wake word detection
# Set to False to use the simpler method based on speech recognition
USE_ADVANCED_WAKEWORD = False

try:
    # Try to import Porcupine for wake word detection
    import pvporcupine
    import pyaudio
    import struct
    USE_ADVANCED_WAKEWORD = True
    log_action("Advanced wake word detection available")
except ImportError:
    log_action("Advanced wake word detection not available, using fallback method", "WARNING")

def detect_wake_word_porcupine():
    """
    Detect wake word using Porcupine (more efficient method).
    
    Returns:
        str: The detected wake word or empty string if not detected
    """
    try:
        # Initialize Porcupine with the wake word
        porcupine = pvporcupine.create(keywords=[WAKEWORD.lower()])
        
        # Initialize PyAudio
        audio = pyaudio.PyAudio()
        
        # Open stream
        stream = audio.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length
        )
        
        log_action("Listening for wake word with Porcupine")
        
        # Listen for the wake word
        while True:
            # Read audio
            pcm = stream.read(porcupine.frame_length)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
            
            # Process with Porcupine
            keyword_index = porcupine.process(pcm)
            
            # Check if wake word detected
            if keyword_index >= 0:
                log_action("Wake word detected with Porcupine")
                
                # Clean up
                stream.close()
                audio.terminate()
                porcupine.delete()
                
                return WAKEWORD
            
            # Small delay to prevent excessive CPU usage
            time.sleep(0.1)
            
    except Exception as e:
        log_error("Error in Porcupine wake word detection", e)
        return ""

def detect_wake_word():
    """
    Wrapper function to detect wake word using the appropriate method.
    
    Returns:
        str: The detected wake word or empty string if not detected
    """
    if USE_ADVANCED_WAKEWORD:
        return detect_wake_word_porcupine()
    else:
        # This is a placeholder - the actual implementation will use
        # speech_recognition.py's listen() and is_wake_word() functions
        log_action("Using simple wake word detection via speech recognition")
        return None  # Handled by main assistant loop