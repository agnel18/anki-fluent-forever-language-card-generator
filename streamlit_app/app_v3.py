import streamlit as st
import logging
import io
import atexit
import os

# Configure the page
st.set_page_config(
    page_title="Language Learning App",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize theme if not set (fallback)
if "theme" not in st.session_state:
    st.session_state.theme = "dark"



# --- Additional Imports to Fix Errors ---
import yaml
import pandas as pd
import datetime
from pathlib import Path

# Import constants and functions from local modules
try:
    from edge_tts_voices import EDGE_TTS_VOICES
except ImportError:
    EDGE_TTS_VOICES = {}  # Fallback empty dict
    print("Warning: Could not import EDGE_TTS_VOICES, using empty fallback")

try:
    from frequency_utils import get_available_frequency_lists, get_csv_template, get_words_with_ranks, validate_word_list, parse_uploaded_word_file
except ImportError as e:
    print(f"Warning: Could not import frequency_utils: {e}")
    # Define fallback functions
    def get_available_frequency_lists(): return []
    def get_csv_template(): return ""
    def get_words_with_ranks(): return []
    def validate_word_list(): return True
    def parse_uploaded_word_file(): return []

try:
    from db_manager import get_completed_words, get_word_stats
except ImportError as e:
    print(f"Warning: Could not import db_manager: {e}")
    def get_completed_words(): return []
    def get_word_stats(): return {}

try:
    from firebase_manager import get_session_id
except ImportError as e:
    print(f"Warning: Could not import firebase_manager: {e}")
    def get_session_id(): return None

# Import our new modular components
try:
    from constants import *
except ImportError as e:
    print(f"Warning: Could not import constants: {e}")

try:
    from utils import log_message, fmt_num, usage_bar
except ImportError as e:
    print(f"Warning: Could not import utils: {e}")
    def log_message(msg): print(msg)
    def fmt_num(n): return str(n)
    def usage_bar(current, max_val): return ""

try:
    from state_manager import initialize_session_state, initialize_languages_config, initialize_firebase_settings
except ImportError as e:
    print(f"Warning: Could not import state_manager: {e}")
    def initialize_session_state(): pass
    def initialize_languages_config(): pass
    def initialize_firebase_settings(): pass

# Initialize session state and languages config (only if in Streamlit context)
try:
    # Check if we're in a Streamlit context
    if hasattr(st, 'session_state'):
        initialize_session_state()
        initialize_languages_config()
        initialize_firebase_settings()
except Exception as e:
    # If not in Streamlit context or initialization fails, skip
    print(f"Initialization skipped: {e}")
    pass

# ============================================================================
# MAIN APPLICATION - MULTI-PAGE WITH SIDEBAR NAVIGATION
# ============================================================================

# Import the modular page functions
from page_modules.main import render_main_page
from page_modules.api_setup import render_api_setup_page
from page_modules.language_select import render_language_select_page
from page_modules.word_select import render_word_select_page
from page_modules.sentence_settings import render_sentence_settings_page
from page_modules.generate import render_generate_page
from page_modules.generating import render_generating_page
from page_modules.complete import render_complete_page
from page_modules.settings import render_settings_page
from page_modules.statistics import render_statistics_page

def format_number_compact(num):
    """Format numbers in compact form (K, M) for better mobile display."""
    if num >= 1000000:
        return f"{num // 1000000}M"
    elif num >= 1000:
        return f"{num // 1000}K"
    else:
        return str(num)

# --- LOGGING CAPTURE FOR DOWNLOADABLE LOG ---
# Restore pinned languages fallback if not set (must be after all imports)
try:
    if "learned_languages" not in st.session_state:
        from pathlib import Path
        import yaml
        config_path = Path(__file__).parent / "languages.yaml"
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        st.session_state.learned_languages = [
            {"name": lang["name"], "usage": 0, "pinned": True} for lang in config["top_5"]
        ]
except Exception as e:
    print(f"Failed to initialize learned_languages: {e}")
    pass

try:
    # Determine which section to show based on session state
    current_page = st.session_state.get("page")

    # Theme-aware CSS with CSS variables
    is_dark = st.session_state.get("theme", "dark") == "dark"
    st.markdown(f"""
    <style>
        :root {{
            --bg-color: {'#0e1117' if is_dark else '#ffffff'};
            --bg-color-rgb: {'14, 17, 23' if is_dark else '255, 255, 255'};
            --text-color: {'#e6edf3' if is_dark else '#0c0c0c'};
            --primary-color: {'#58a6ff' if is_dark else '#0969da'};
            --secondary-color: {'#79c0ff' if is_dark else '#218bff'};
            --tertiary-color: {'#a5d6ff' if is_dark else '#79c0ff'};
            --button-bg: {'#238636' if is_dark else '#238636'};
            --button-border: {'#3fb950' if is_dark else '#3fb950'};
            --button-hover-bg: {'#2ea043' if is_dark else '#2ea043'};
            --button-hover-border: {'#56d364' if is_dark else '#56d364'};
            --info-bg: {'#0550ae' if is_dark else '#ddf4ff'};
            --info-border: {'#79c0ff' if is_dark else '#218bff'};
            --success-bg: {'#1f6feb' if is_dark else '#ddf4ff'};
            --success-border: {'#58a6ff' if is_dark else '#0969da'};
            --warning-bg: {'#8b4513' if is_dark else '#fff3cd'};
            --warning-border: {'#d9a040' if is_dark else '#bf8700'};
            --error-bg: {'#da3633' if is_dark else '#ffebe9'};
            --error-border: {'#f85149' if is_dark else '#cf222e'};
            --card-bg: {'#161b22' if is_dark else '#f6f8fa'};
            --card-border: {'#30363d' if is_dark else '#d0d7de'};
            --base-font-size: 16px;
        }}
    </style>
    """, unsafe_allow_html=True)

    # If no page is set, determine default based on API key availability
    if current_page is None:
        groq_key = st.session_state.get("groq_api_key", "")
        pixabay_key = st.session_state.get("pixabay_api_key", "")

        # Check if we have real API keys (not fallback keys)
        has_real_api_keys = (
            groq_key and pixabay_key and
            not groq_key.startswith("sk-fallback") and
            not pixabay_key.startswith("fallback")
        )

        current_page = "api_setup" if not has_real_api_keys else "main"
        st.session_state.page = current_page

    # Add sidebar navigation (except on login page)
    if current_page != "login":
        # Create sidebar content with better mobile alignment
        st.sidebar.markdown("## ⚙️ Quick Access")

        # Quick access buttons stacked vertically
        if st.sidebar.button("🏠 Main", key="sidebar_main", use_container_width=True):
            st.session_state.page = "main"
            st.rerun()
        
        if st.sidebar.button("⚙️ Settings", key="sidebar_settings", use_container_width=True):
            st.session_state.page = "settings"
            st.rerun()

        # Statistics button full width
        if st.sidebar.button("📊 Statistics", key="sidebar_stats", use_container_width=True):
            st.session_state.page = "statistics"
        st.rerun()

    # Documentation button
    if st.sidebar.button("📖 Documentation", key="sidebar_docs", use_container_width=True):
        import webbrowser
        webbrowser.open("https://github.com/your-repo")
        st.sidebar.success("Opening documentation...")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### API Usage")

    # Use persistent stats if logged in, else session stats
    stats = st.session_state.get("persistent_usage_stats") if not st.session_state.get("is_guest", True) else None
    if stats:
        groq_calls = stats.get("groq_calls", 0)
        groq_tokens = stats.get("groq_tokens", 0)
        pixabay_calls = stats.get("pixabay_calls", 0)
    else:
        groq_calls = st.session_state.get("groq_api_calls", 0)
        groq_tokens = st.session_state.get("groq_tokens_used", 0)
        pixabay_calls = st.session_state.get("pixabay_api_calls", 0)

    # Display metrics with compact formatting
    st.sidebar.metric(
        "Groq Calls",
        f"{format_number_compact(groq_calls)} / {format_number_compact(GROQ_CALL_LIMIT)}"
    )
    st.sidebar.metric(
        "Groq Tokens",
        f"{format_number_compact(groq_tokens)} / {format_number_compact(GROQ_TOKEN_LIMIT)}"
    )
    st.sidebar.metric(
        "Pixabay Calls",
        f"{format_number_compact(pixabay_calls)} / {format_number_compact(PIXABAY_CALL_LIMIT)}"
    )

    st.sidebar.caption("Limits are approximate—check your API dashboard for exact quotas.")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎨 Theme")

    theme_options = ["Light", "Dark"]
    current_theme = st.session_state.theme.capitalize()

    selected_theme = st.sidebar.selectbox(
        "Select Theme",
        theme_options,
        index=theme_options.index(current_theme),
        key="theme_select_sidebar",
        help="Switch between light and dark themes"
    )

    if selected_theme.lower() != st.session_state.theme:
        st.session_state.theme = selected_theme.lower()
        st.sidebar.success(f"Theme changed to {selected_theme}! Refresh the page to apply changes.")
        st.rerun()

    # Show generation status if in progress
    if st.session_state.get('page') == 'generating':
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🔄 Generation Status")
        progress = st.session_state.get('generation_progress', {})
        word_idx = progress.get('word_idx', 0)
        total_words = len(st.session_state.get('selected_words', []))
        if total_words > 0:
            st.sidebar.progress(min((word_idx + 1) / total_words, 1.0))
            st.sidebar.caption(f"Processing word {word_idx + 1} of {total_words}")


    # Route to the appropriate page
    st.write(f"Debug: Current page = {current_page}")
    if current_page == "api_setup":
        render_api_setup_page()
    elif current_page == "main":
        render_main_page()
    elif current_page == "language_select":
        render_language_select_page()
    elif current_page == "word_select":
        render_word_select_page()
    elif current_page == "sentence_settings":
        render_sentence_settings_page()
    elif current_page == "generate":
        render_generate_page()
    elif current_page == "generating":
        render_generating_page()
    elif current_page == "complete":
        render_complete_page()
    elif current_page == "settings":
        render_settings_page()
    elif current_page == "statistics":
        render_statistics_page()
    else:
        # Default to main page
        render_main_page()

except Exception as e:
    st.error(f"App error: {e}")
    st.write("Please refresh the page or contact support.")
