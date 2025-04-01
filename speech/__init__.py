# __init__.py - Initializes the speech package

# Import all speech-related modules to make them available
from speech.speech_recognition import listen, is_wake_word
from speech.text_to_speech import speak, initialize_engine
from speech.wakeword import detect_wake_word

# Define package exports
__all__ = ['listen', 'is_wake_word', 'speak', 'initialize_engine', 'detect_wake_word']