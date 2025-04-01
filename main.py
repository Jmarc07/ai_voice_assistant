# main.py
import os
import sys

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.assistant import VoiceAssistant
from logs.logger import logger

def main():
    """Main entry point for the voice assistant"""
    try:
        logger.info("Starting Voice Assistant application...")
        
        # Create and start the voice assistant
        assistant = VoiceAssistant()
        assistant.start()
    except Exception as e:
        logger.critical(f"Critical error in main application: {e}")
        print(f"Critical error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())