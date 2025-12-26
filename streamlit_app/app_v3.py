import streamlit as st

# Session state guard for Streamlit bug workaround
if not hasattr(st, "session_state") or st.session_state is None:
    st.session_state = {}
import logging
import io
import atexit
import os

# ============================================================================
# MAIN APPLICATION - MULTI-PAGE WITH SIDEBAR NAVIGATION
# ============================================================================

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

try:
    from ui.sidebar import render_sidebar, handle_auto_sync
except ImportError as e:
    print(f"Warning: Could not import ui.sidebar: {e}")
    def render_sidebar(): return False
    def handle_auto_sync(): pass

try:
    from ui.theming import apply_theme_css
except ImportError as e:
    print(f"Warning: Could not import ui.theming: {e}")
    def apply_theme_css(): pass

try:
    from router import route_to_page
except ImportError as e:
    print(f"Warning: Could not import router: {e}")
    def route_to_page(page): pass

# Initialize session state and languages config (only if in Streamlit context)
try:
    # Check if we're in a Streamlit context
    if hasattr(st, 'session_state'):
        initialize_session_state()
        # Move languages config initialization inside main() function to avoid import-time issues
        # Move firebase initialization inside main() function to avoid import-time issues
except Exception as e:
    # If not in Streamlit context or initialization fails, skip
    print(f"Initialization skipped: {e}")
    pass

# ============================================================================
# LOGGING SETUP
# ============================================================================

logger = logging.getLogger(__name__)

# ============================================================================
# MAIN APPLICATION - MULTI-PAGE WITH SIDEBAR NAVIGATION
# ============================================================================

def main():

    # Import option_menu for the hamburger menu
    from streamlit_option_menu import option_menu
    
    # Google Site Verification Meta Tag
    st.markdown('<meta name="google-site-verification" content="YUTo7TlPD5g4Yz_i6pCEEnIMTKlwplPMIukMKhOyfnw" />', unsafe_allow_html=True)

    # Inject global CSS to fix accessibility and contrast issues app-wide
    st.markdown("""
    <style>
    /* Fix text contrast issues - override Streamlit's emotion classes globally */
    .st-emotion-cache-n2fj4p {
        opacity: 1 !important;
        color: var(--text-color, #31333F) !important;
        font-weight: 500 !important;
    }
    
    .st-emotion-cache-svhcdj {
        color: var(--text-color, #31333F) !important;
        opacity: 1 !important;
        font-weight: 500 !important;
    }
    
    /* Fix label association issues - hide decorative labels that cause accessibility warnings */
    label[data-testid="stWidgetLabel"][aria-hidden="true"] {
        display: none !important;
        visibility: hidden !important;
        position: absolute !important;
        left: -9999px !important;
    }
    
    /* Ensure form elements remain accessible through their help text and context */
    .stSelectbox [data-testid="stSelectbox"] {
        position: relative;
    }
    
    /* Theme-aware text colors for better contrast */
    [data-theme="light"] .st-emotion-cache-n2fj4p,
    [data-theme="light"] .st-emotion-cache-svhcdj {
        color: #0F1419 !important;
    }
    
    [data-theme="dark"] .st-emotion-cache-n2fj4p,
    [data-theme="dark"] .st-emotion-cache-svhcdj {
        color: #FAFAFA !important;
    }
    
    /* Improve tooltip visibility */
    .stTooltipIcon {
        opacity: 0.7 !important;
        transition: opacity 0.2s ease;
    }
    
    .stTooltipIcon:hover {
        opacity: 1 !important;
    }
    
    /* Ensure slider labels are properly styled */
    .stSlider label {
        color: var(--text-color, #31333F) !important;
        opacity: 1 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Import all page rendering functions and format_number_compact utility
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
    from page_modules.privacy_policy import render_privacy_policy_page
    from page_modules.terms_conditions import render_terms_conditions_page
    from page_modules.refund_policy import render_refund_policy_page
    from page_modules.shipping_delivery import render_shipping_delivery_page
    from page_modules.contact_us import render_contact_us_page
    def format_number_compact(num):
        if num >= 1000000:
            return f"{num // 1000000}M"
        elif num >= 1000:
            return f"{num // 1000}K"
        else:
            return str(num)

    # Handle auto sync
    handle_auto_sync()

    # Determine which section to show based on session state
    current_page = st.session_state.get("page")

    # Check for OAuth callback - if we have auth code in URL, go to auth handler
    if st.query_params.get("code"):
        current_page = "auth_handler"
        st.session_state.page = current_page

    # If no page is set, determine default based on API key availability
    if current_page is None:
        # Always start with main page - it will guide user to API setup if needed
        current_page = "main"
        st.session_state.page = current_page

    # Add sidebar navigation (except on login page)
    if current_page != "login":
        # Apply theme CSS before rendering sidebar
        apply_theme_css()
        
        theme_changed = render_sidebar()

        # Apply theme change if needed
        if theme_changed:
            st.rerun()


    # Ensure critical session state variables are initialized (mobile compatibility)
    if "sentence_length_range" not in st.session_state:
        st.session_state.sentence_length_range = (6, 16)
    if "sentences_per_word" not in st.session_state:
        st.session_state.sentences_per_word = 10
    if "difficulty" not in st.session_state:
        st.session_state.difficulty = "intermediate"
    if "audio_speed" not in st.session_state:
        st.session_state.audio_speed = 0.8
    if "selected_voice" not in st.session_state:
        st.session_state.selected_voice = None
    if "selected_voice_display" not in st.session_state:
        st.session_state.selected_voice_display = None
    if "enable_topics" not in st.session_state:
        st.session_state.enable_topics = False
    if "selected_topics" not in st.session_state:
        st.session_state.selected_topics = []
    if "custom_topics" not in st.session_state:
        st.session_state.custom_topics = []

    # Initialize languages and firebase settings
    initialize_languages_config()
    initialize_firebase_settings()

    # Route to the appropriate page
    route_to_page(current_page)

# Run the main function if this script is executed directly
if __name__ == "__main__":
    main()
