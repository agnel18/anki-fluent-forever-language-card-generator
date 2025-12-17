# state_manager.py - Session state management for the language learning app

import streamlit as st
from pathlib import Path
import yaml
from typing import Dict, Any, Optional
from constants import (
    DEFAULT_BATCH_SIZE, DEFAULT_SENTENCES_PER_WORD, DEFAULT_AUDIO_SPEED,
    DEFAULT_SELECTION_MODE, DEFAULT_DIFFICULTY, DEFAULT_VOICE_DISPLAY, DEFAULT_VOICE,
    DEFAULT_ENABLE_TOPICS, DEFAULT_SELECTED_TOPICS,
    LANGUAGES_CONFIG_PATH, SESSION_PAGE, SESSION_GROQ_API_KEY, SESSION_PIXABAY_API_KEY,
    SESSION_CURRENT_BATCH_SIZE, SESSION_LOADED_WORDS, SESSION_CURRENT_LANG_WORDS,
    SESSION_COMPLETED_WORDS, SESSION_SELECTION_MODE, SESSION_SENTENCES_PER_WORD,
    SESSION_AUDIO_SPEED, SESSION_DIFFICULTY, SESSION_SELECTED_VOICE_DISPLAY,
    SESSION_SELECTED_VOICE, SESSION_LOG_STREAM, SESSION_ENABLE_TOPICS,
    SESSION_SELECTED_TOPICS, SESSION_CUSTOM_TOPICS, PAGE_LOGIN, PAGE_MAIN
)


def initialize_session_state():
    """Initialize all session state variables with defaults."""

    # Page navigation
    if SESSION_PAGE not in st.session_state:
        st.session_state[SESSION_PAGE] = PAGE_MAIN

    # API keys - load from saved secrets if available
    if SESSION_GROQ_API_KEY not in st.session_state:
        st.session_state[SESSION_GROQ_API_KEY] = ""
    if SESSION_PIXABAY_API_KEY not in st.session_state:
        st.session_state[SESSION_PIXABAY_API_KEY] = ""
    
    # Try to load saved API keys from user_secrets.json
    try:
        secrets_path = Path(__file__).parent / "user_secrets.json"
        if secrets_path.exists():
            import json
            with open(secrets_path, "r", encoding="utf-8") as f:
                user_secrets = json.load(f)
            if user_secrets.get("groq_api_key") and not st.session_state[SESSION_GROQ_API_KEY]:
                st.session_state[SESSION_GROQ_API_KEY] = user_secrets["groq_api_key"]
            if user_secrets.get("pixabay_api_key") and not st.session_state[SESSION_PIXABAY_API_KEY]:
                st.session_state[SESSION_PIXABAY_API_KEY] = user_secrets["pixabay_api_key"]
    except Exception:
        # If loading fails, continue with empty keys
        pass

    # Cloud sync state
    if "cloud_sync_enabled" not in st.session_state:
        st.session_state.cloud_sync_enabled = False
    if "last_sync_time" not in st.session_state:
        st.session_state.last_sync_time = None
    if "sync_errors" not in st.session_state:
        st.session_state.sync_errors = []
    if "dismissed_cloud_prompt" not in st.session_state:
        st.session_state.dismissed_cloud_prompt = False
    if "initial_sync_done" not in st.session_state:
        st.session_state.initial_sync_done = False

    # Batch settings
    if SESSION_CURRENT_BATCH_SIZE not in st.session_state:
        st.session_state[SESSION_CURRENT_BATCH_SIZE] = DEFAULT_BATCH_SIZE

    # Word data
    if SESSION_LOADED_WORDS not in st.session_state:
        st.session_state[SESSION_LOADED_WORDS] = {}
    if SESSION_CURRENT_LANG_WORDS not in st.session_state:
        st.session_state[SESSION_CURRENT_LANG_WORDS] = []
    if SESSION_COMPLETED_WORDS not in st.session_state:
        st.session_state[SESSION_COMPLETED_WORDS] = {}  # {language: [list of completed words]}

    # Selection settings
    if SESSION_SELECTION_MODE not in st.session_state:
        st.session_state[SESSION_SELECTION_MODE] = DEFAULT_SELECTION_MODE

    # Global settings defaults
    if "difficulty" not in st.session_state:
        st.session_state.difficulty = DEFAULT_DIFFICULTY
    if "sentence_length_range" not in st.session_state:
        st.session_state.sentence_length_range = (6, 16)
    if SESSION_SENTENCES_PER_WORD not in st.session_state:
        st.session_state[SESSION_SENTENCES_PER_WORD] = DEFAULT_SENTENCES_PER_WORD
    if "track_progress" not in st.session_state:
        st.session_state.track_progress = True
    if SESSION_AUDIO_SPEED not in st.session_state:
        st.session_state[SESSION_AUDIO_SPEED] = DEFAULT_AUDIO_SPEED
    if SESSION_SELECTED_VOICE not in st.session_state:
        st.session_state[SESSION_SELECTED_VOICE] = None
    if SESSION_SELECTED_VOICE_DISPLAY not in st.session_state:
        st.session_state[SESSION_SELECTED_VOICE_DISPLAY] = None
    if "first_run_complete" not in st.session_state:
        st.session_state.first_run_complete = False
    
    # Topic settings
    if SESSION_ENABLE_TOPICS not in st.session_state:
        st.session_state[SESSION_ENABLE_TOPICS] = DEFAULT_ENABLE_TOPICS
    if SESSION_SELECTED_TOPICS not in st.session_state:
        st.session_state[SESSION_SELECTED_TOPICS] = DEFAULT_SELECTED_TOPICS.copy()
    if SESSION_CUSTOM_TOPICS not in st.session_state:
        st.session_state[SESSION_CUSTOM_TOPICS] = []

    # Logging
    if SESSION_LOG_STREAM not in st.session_state:
        import io
        import logging
        import atexit
        st.session_state[SESSION_LOG_STREAM] = io.StringIO()
        log_handler = logging.StreamHandler(st.session_state[SESSION_LOG_STREAM])
        log_handler.setLevel(logging.INFO)
        log_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s:%(name)s:%(message)s'))
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)

    # Theme settings
    if "theme" not in st.session_state:
        st.session_state.theme = "dark"
        # Remove existing handlers to avoid duplicate logs
        for h in root_logger.handlers[:]:
            root_logger.removeHandler(h)
        root_logger.addHandler(log_handler)
        # Also keep logging to stderr for devs
        root_logger.addHandler(logging.StreamHandler())
        # Clean up StringIO on exit
        def cleanup_log_stream():
            try:
                if SESSION_LOG_STREAM in st.session_state:
                    st.session_state[SESSION_LOG_STREAM].close()
            except:
                pass  # Ignore errors during shutdown
        atexit.register(cleanup_log_stream)

    # Initialize cache manager
    if "cache_manager_initialized" not in st.session_state:
        try:
            from cache_manager import get_cache_manager
            cache_manager = get_cache_manager()
            # Perform initial cleanup of expired entries
            cache_manager.cleanup()
            st.session_state.cache_manager_initialized = True
        except Exception as e:
            # Cache initialization failed, but don't break the app
            print(f"Warning: Cache manager initialization failed: {e}")
            st.session_state.cache_manager_initialized = False


def initialize_languages_config():
    """Initialize learned languages from config if not set."""
    if "learned_languages" not in st.session_state:
        config_path = Path(__file__).parent / LANGUAGES_CONFIG_PATH
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        st.session_state.learned_languages = [
            {"name": lang["name"], "usage": 0, "pinned": True} for lang in config["top_5"]
        ]
        # Also set all_languages globally if needed
        if "all_languages" not in st.session_state:
            st.session_state.all_languages = config["all_languages"]


def initialize_firebase_settings():
    """Initialize Firebase settings and session ID."""
    from firebase_manager import load_settings_from_firebase, get_session_id, is_signed_in

    if "session_id" not in st.session_state:
        st.session_state.session_id = get_session_id()
    if "current_page" not in st.session_state:
        st.session_state.current_page = {}

    # Set default guest status
    if "is_guest" not in st.session_state:
        st.session_state.is_guest = True

    # Auto-load settings for signed-in users
    if is_signed_in():
        st.session_state.is_guest = False
        firebase_settings = load_settings_from_firebase(st.session_state.session_id)
        if firebase_settings:
            # Load settings from Firebase (cloud takes precedence for API keys)
            if firebase_settings.get("groq_api_key"):
                st.session_state.groq_api_key = firebase_settings["groq_api_key"]
            if firebase_settings.get("pixabay_api_key"):
                st.session_state.pixabay_api_key = firebase_settings["pixabay_api_key"]
            # Load other settings if available
            if "theme" in firebase_settings:
                st.session_state.theme = firebase_settings["theme"]
            if "audio_speed" in firebase_settings:
                st.session_state.audio_speed = firebase_settings["audio_speed"]