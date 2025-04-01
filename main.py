# main.py - Entry point for starting the assistant

import sys
import time
from core.assistant import VoiceAssistant
from logs.logger import setup_logger

def print_welcome_message():
    """Display welcome message and application information."""
    print("=" * 50)
    print("        AI-POWERED VOICE ASSISTANT        ")
    print("=" * 50)
    print("Starting up your personal voice assistant...")
    print("Say 'Hey Assistant' to activate")
    print("=" * 50)

if __name__ == "__main__":
    # Set up logging
    setup_logger()
    
    # Display welcome message
    print_welcome_message()
    
    try:
        # Initialize and start the voice assistant
        assistant = VoiceAssistant()
        assistant.start()
    except KeyboardInterrupt:
        print("\nShutting down assistant...")
        time.sleep(1)
        print("Voice assistant terminated.")
        sys.exit(0)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)