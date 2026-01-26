# constants.py - Centralized constants for the language learning app

# API Limits
GEMINI_CALL_LIMIT = 1000
GEMINI_TOKEN_LIMIT = 3000000
GOOGLE_SEARCH_CALL_LIMIT = 100

# Default Settings
DEFAULT_BATCH_SIZE = 5
DEFAULT_SENTENCES_PER_WORD = 4
DEFAULT_AUDIO_SPEED = 0.8
DEFAULT_SELECTION_MODE = "range"  # range, manual, search
DEFAULT_DIFFICULTY = "intermediate"  # beginner, intermediate, advanced
DEFAULT_VOICE_DISPLAY = "en-US-Standard-D"
DEFAULT_VOICE = "en-US-Standard-D"
DEFAULT_ENABLE_TOPICS = False  # Whether to enable topic selection by default
DEFAULT_SELECTED_TOPICS = []  # Default selected topics

# Curated Topics List
CURATED_TOPICS = [
    "Daily Life", "Food & Cooking", "Travel", "Work & Business", "Education", 
    "Health & Fitness", "Family & Relationships", "Hobbies & Entertainment", 
    "Technology", "Nature & Environment", "Sports", "Shopping", "Transportation", 
    "Weather", "Emotions & Feelings", "Time & Dates", "Colors", "Numbers & Math",
    "Music", "Art & Creativity", "Science", "History", "Geography", "Politics",
    "Religion", "Culture & Traditions", "Celebrations", "Animals", "Plants",
    "Buildings & Architecture", "Clothing & Fashion", "Money & Finance"
]

# UI Constants
PAGE_SIZE = 25

# Color codes for usage bars
USAGE_BAR_GREEN = "#238636"
USAGE_BAR_YELLOW = "#eab308"
USAGE_BAR_RED = "#ef4444"

# File paths
LANGUAGES_CONFIG_PATH = "languages.yaml"

# Session state keys (for consistency)
SESSION_PAGE = "page"
SESSION_GOOGLE_API_KEY = "google_api_key"
SESSION_CURRENT_BATCH_SIZE = "current_batch_size"
SESSION_LOADED_WORDS = "loaded_words"
SESSION_CURRENT_LANG_WORDS = "current_lang_words"
SESSION_COMPLETED_WORDS = "completed_words"
SESSION_SELECTION_MODE = "selection_mode"
SESSION_SENTENCES_PER_WORD = "sentences_per_word"
SESSION_AUDIO_SPEED = "audio_speed"
SESSION_DIFFICULTY = "difficulty"
SESSION_SELECTED_VOICE_DISPLAY = "selected_voice_display"
SESSION_SELECTED_VOICE = "selected_voice"
SESSION_LOG_STREAM = "log_stream"
SESSION_ENABLE_TOPICS = "enable_topics"
SESSION_SELECTED_TOPICS = "selected_topics"
SESSION_CUSTOM_TOPICS = "custom_topics"

# Page names
PAGE_LOGIN = "login"
PAGE_MAIN = "main"
PAGE_API_SETUP = "api_setup"
PAGE_LANGUAGE_SELECT = "language_select"
PAGE_WORD_SELECT = "word_select"
PAGE_SENTENCE_SETTINGS = "sentence_settings"
PAGE_GENERATE = "generate"
PAGE_GENERATING = "generating"
PAGE_COMPLETE = "complete"
PAGE_STATISTICS = "statistics"
PAGE_SETTINGS = "settings"
PAGE_HELP = "help"
PAGE_UPLOAD = "upload"