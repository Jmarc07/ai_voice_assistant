ADMIN_PASSWORD = "admin123"  # Change this to a secure password

# Speech recognition settings
WAKEWORD = "Hey Assistant"
LANGUAGE = "en-US"

# Text-to-speech settings
VOICE_ENGINE = "pyttsx3"  # Options: 'pyttsx3', 'gTTS'
VOICE_RATE = 150  # Speed of speech
VOICE_VOLUME = 1.0  # Volume level (0.0 to 1.0)
VOICE_GENDER = "male"  # Options: 'male' or 'female'

# API Keys (replace with your actual keys)
GOOGLE_SEARCH_API_KEY = " your_google_api_key_here"
GOOGLE_SEARCH_ENGINE_ID = " your_search_engine_id_here"

# Application paths (customize for your system)
DEFAULT_BROWSER = "chrome"
DEFAULT_TEXT_EDITOR = "notepad"  # Windows default
DEFAULT_TEXT_EDITOR = "gedit"  # Linux default
DEFAULT_TEXT_EDITOR = "TextEdit"  # macOS default

# Logging settings
LOG_FILE = "logs/assistant_logs.txt"  # Specify logs directory
LOG_LEVEL = "INFO"

# Debug settings
DEBUG_MODE = True  # Set to True to use text input instead of microphone