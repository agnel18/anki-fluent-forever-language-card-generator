import streamlit as st
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
# SIDEBAR AUTHENTICATION SECTION
# ============================================================================

def render_sidebar_auth_section():
    """Render authentication section in sidebar."""
    from firebase_manager import get_sync_status, sign_in_with_google, sign_out
    from utils import should_show_cloud_prompt
    from sync_manager import sync_user_data
    
    firebase_status = get_sync_status()
    
    if firebase_status == "enabled":
        # Signed in state
        user = st.session_state.get('user', {})
        user_email = user.get('email', 'User')
        st.sidebar.success(f"✅ {user_email}")
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.sidebar.button("🔄 Sync", key="sync_now", help="Sync your data to the cloud"):
                if sync_user_data():
                    st.sidebar.success("✅ Synced!")
                else:
                    st.sidebar.error("❌ Sync failed")
        with col2:
            if st.sidebar.button("🚪 Sign Out", key="sign_out", help="Sign out and use local storage only"):
                sign_out()
                st.sidebar.success("Signed out!")
                st.rerun()
                
    elif firebase_status == "available":
        # Available but not signed in
        if should_show_cloud_prompt():
            st.sidebar.info("💡 **Backup your settings to the cloud?**")
            
            col1, col2 = st.sidebar.columns([1, 1])
            with col1:
                if st.sidebar.button("🔐 Sign In", key="sidebar_signin", help="Sign in with Google to enable cloud sync"):
                    sign_in_with_google()
            with col2:
                if st.sidebar.button("❌ Later", key="dismiss_prompt", help="Remind me later"):
                    st.session_state.dismissed_cloud_prompt = True
                    st.sidebar.success("Will remind you later!")
        else:
            # Subtle sign-in option
            with st.sidebar.expander("☁️ Cloud Sync", expanded=False):
                st.write("Sign in to backup your API keys and settings across devices.")
                if st.button("🚀 Enable Cloud Sync", key="enable_cloud_sync"):
                    sign_in_with_google()
                    
    else:
        # Firebase unavailable
        st.sidebar.warning("☁️ Cloud features unavailable")

def handle_auto_sync():
    """Handle automatic sync operations."""
    from firebase_manager import is_signed_in
    from sync_manager import load_cloud_data, safe_sync
    
    # Sync on app start if signed in and not done yet
    if is_signed_in() and not st.session_state.get('initial_sync_done'):
        try:
            load_cloud_data()
            st.session_state.initial_sync_done = True
        except Exception as e:
            print(f"Initial sync failed: {e}")
    
    # Periodic sync (every 5 minutes) if signed in
    last_sync = st.session_state.get('last_sync_time')
    if (is_signed_in() and last_sync and 
        (datetime.now() - last_sync).seconds > 300):  # 5 minutes
        try:
            safe_sync()
        except Exception as e:
            print(f"Periodic sync failed: {e}")

# ============================================================================
# MAIN APPLICATION - MULTI-PAGE WITH SIDEBAR NAVIGATION
# ============================================================================

def main():
    """Main application entry point."""
    # Configure the page - must be called first and only once
    st.set_page_config(
        page_title="Language Learning App",
        page_icon="🌍",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Initialize theme if not set (fallback)
    if "theme" not in st.session_state:
        st.session_state.theme = "dark"

    # Initialize Firebase settings (moved here from module level to avoid import-time issues)
    try:
        initialize_firebase_settings()
    except Exception as e:
        print(f"Firebase initialization failed: {e}")
        pass

    # Handle automatic sync operations
    try:
        handle_auto_sync()
    except Exception as e:
        print(f"Auto sync failed: {e}")
        pass

    # Import the modular page functions (inside main to avoid import-time issues)
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
        # Initialize languages config if not set
        if "all_languages" not in st.session_state:
            initialize_languages_config()
    except Exception as e:
        print(f"Failed to initialize languages: {e}")
        pass

    try:
        # Validate and initialize session state
        if "page" not in st.session_state:
            st.session_state.page = None
        if "theme" not in st.session_state:
            st.session_state.theme = "dark"

        # Handle URL parameters for direct page access (Razorpay compliance)
        page_param = st.query_params.get("page", [None])[0]
        print(f"DEBUG: URL param 'page' = {page_param}")  # Debug logging
        if page_param and page_param in ["privacy_policy", "terms_conditions", "refund_policy", "shipping_delivery", "contact_us"]:
            st.session_state.page = page_param
            print(f"DEBUG: Set session state page to {page_param}")  # Debug logging
            print(f"DEBUG: Current session state page = {st.session_state.get('page')}")  # Additional debug

        # Determine which section to show based on session state
        current_page = st.session_state.get("page")

        # Theme-aware CSS with CSS variables
        is_dark = st.session_state.get("theme", "dark") == "dark"
        st.markdown(f"""
        <style>
            :root {{
                --bg-color: {'#0e1117' if is_dark else '#ffffff'};
                --bg-color-rgb: {'14, 17, 23' if is_dark else '255, 255, 255'};
                --secondary-bg: {'#161b22' if is_dark else '#f6f8fa'};
                --text-color: {'#e6edf3' if is_dark else '#0c0c0c'};
                --subtle-text: {'#8b949e' if is_dark else '#24292f'};
                --primary-color: {'#58a6ff' if is_dark else '#0969da'};
                --secondary-color: {'#79c0ff' if is_dark else '#218bff'};
                --tertiary-color: {'#a5d6ff' if is_dark else '#79c0ff'};
                --accent-color: {'#ff6b6b' if is_dark else '#d73a49'};
                --accent-secondary: {'#4ecdc4' if is_dark else '#218bff'};
                --button-primary-bg: {'#238636' if is_dark else '#1a7f37'};
                --button-primary-border: {'#3fb950' if is_dark else '#1f883d'};
                --button-primary-hover-bg: {'#2ea043' if is_dark else '#218838'};
                --button-secondary-bg: {'#30363d' if is_dark else '#f6f8fa'};
                --button-secondary-border: {'#8b949e' if is_dark else '#d0d7de'};
                --button-secondary-hover-bg: {'#484f58' if is_dark else '#f3f4f6'};
                --button-text: {'white' if is_dark else 'black'};
                --button-secondary-text: {'#e6edf3' if is_dark else '#24292f'};
                --hover-bg: {'#30363d' if is_dark else '#f3f4f6'};
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
                --gradient-primary: {'linear-gradient(135deg, #ff6b6b 0%, #4ecdc4 100%)' if is_dark else 'linear-gradient(135deg, #0969da 0%, #218bff 100%)'};
                --box-shadow: {'0 8px 25px rgba(0,0,0,0.2)' if is_dark else '0 8px 25px rgba(0,0,0,0.1)'};
                --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                --base-font-size: 16px;
                --link-color: var(--primary-color);
                --usage-green: #238636;
                --usage-yellow: #eab308;
                --usage-red: #ef4444;
            }}
            .stSidebar {{
                background-color: var(--bg-color) !important;
                color: var(--text-color) !important;
            }}
            .stApp {{
                background-color: var(--bg-color) !important;
                color: var(--text-color) !important;
            }}
            .main {{
                background-color: var(--bg-color) !important;
                color: var(--text-color) !important;
            }}
            .block-container {{
                background-color: var(--bg-color) !important;
                color: var(--text-color) !important;
            }}
            .stButton > button {{
                background-color: var(--button-primary-bg) !important;
                border-color: var(--button-primary-border) !important;
                color: var(--button-text) !important;
            }}
            .stButton > button:hover {{
                background-color: var(--button-primary-hover-bg) !important;
                border-color: var(--button-primary-border) !important;
            }}
            /* Secondary buttons - simpler approach */
            .stButton > button {{
                background-color: var(--button-secondary-bg) !important;
                border-color: var(--button-secondary-border) !important;
                color: var(--button-secondary-text) !important;
            }}
            .stButton > button:hover {{
                background-color: var(--button-secondary-hover-bg) !important;
                border-color: var(--button-secondary-border) !important;
            }}
            /* Primary buttons - override secondary styling */
            .stButton > button[style*="rgb(26, 127, 55)"], 
            .stButton > button[style*="rgb(35, 134, 54)"] {{
                background-color: var(--button-primary-bg) !important;
                border-color: var(--button-primary-border) !important;
                color: var(--button-text) !important;
            }}
            .stButton > button[style*="rgb(26, 127, 55)"]:hover,
            .stButton > button[style*="rgb(35, 134, 54)"]:hover {{
                background-color: var(--button-primary-hover-bg) !important;
                border-color: var(--button-primary-border) !important;
            }}
            .stTextInput > div > div > input {{
                background-color: var(--secondary-bg) !important;
                color: var(--text-color) !important;
                border-color: var(--card-border) !important;
            }}
            .stSelectbox > div > div {{
                background-color: var(--secondary-bg) !important;
                color: var(--text-color) !important;
            }}
            .stMarkdown a {{
                color: var(--link-color) !important;
            }}
            .stProgress > div > div > div {{
                background-color: var(--primary-color) !important;
            }}
            .stMetric {{
                background-color: var(--card-bg) !important;
                border: 1px solid var(--card-border) !important;
                border-radius: 8px !important;
                color: var(--text-color) !important;
            }}
            .stMetric label {{
                color: var(--text-color) !important;
            }}
            .stMetric [data-testid="stMetricValue"] {{
                color: var(--text-color) !important;
            }}
            .stWidgetLabel {{
                color: var(--text-color) !important;
            }}
            .stWidgetLabel p {{
                color: var(--text-color) !important;
            }}
            /* Tab styling for light mode visibility */
            .stTabs [data-baseweb="tab-list"] button {{
                color: var(--text-color) !important;
                background-color: var(--secondary-bg) !important;
                border-color: var(--card-border) !important;
            }}
            .stTabs [data-baseweb="tab-list"] button:hover {{
                background-color: var(--hover-bg) !important;
            }}
            .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {{
                background-color: var(--card-bg) !important;
                border-bottom-color: var(--primary-color) !important;
            }}
            /* Input field styling for light mode */
            input[type="number"], input[type="text"], input[type="password"], input[type="email"], textarea {{
                background-color: var(--secondary-bg) !important;
                color: var(--text-color) !important;
                border-color: var(--card-border) !important;
            }}
            input[type="number"]:focus, input[type="text"]:focus, input[type="password"]:focus, input[type="email"]:focus, textarea:focus {{
                border-color: var(--primary-color) !important;
                box-shadow: 0 0 0 1px var(--primary-color) !important;
            }}
            /* Slider styling for light mode visibility */
            .stSlider {{
                color: var(--text-color) !important;
            }}
            .stSlider [data-baseweb="slider"] {{
                background-color: var(--secondary-bg) !important;
            }}
            .stSlider [role="slider"] {{
                background-color: var(--primary-color) !important;
                color: white !important;
            }}
            .stSlider [data-testid="stSliderThumbValue"] {{
                background-color: var(--primary-color) !important;
                color: white !important;
            }}
            .stSlider [data-testid="stSliderTickBar"] {{
                color: var(--text-color) !important;
            }}
            .stSlider [data-testid="stSliderTickBar"] span {{
                color: var(--text-color) !important;
            }}
            /* Checkbox styling for light mode */
            .stCheckbox {{
                color: var(--text-color) !important;
            }}
            .stCheckbox [data-baseweb="checkbox"] {{
                background-color: var(--secondary-bg) !important;
                border-color: var(--card-border) !important;
            }}
            .stCheckbox input[type="checkbox"] {{
                accent-color: var(--primary-color) !important;
            }}
            /* General text visibility */
            .stMarkdown p, .stMarkdown span, .stMarkdown div {{
                color: var(--text-color) !important;
            }}
            /* Specific markdown container visibility */
            [data-testid="stMarkdownContainer"] p {{
                color: var(--text-color) !important;
            }}
            /* Download button styling for light mode */
            .stDownloadButton button {{
                background-color: var(--button-secondary-bg) !important;
                border-color: var(--button-secondary-border) !important;
                color: var(--button-secondary-text) !important;
            }}
            .stDownloadButton button:hover {{
                background-color: var(--button-secondary-hover-bg) !important;
                border-color: var(--button-secondary-border) !important;
            }}
            /* Ensure download button text is visible */
            .stDownloadButton [data-testid="stMarkdownContainer"] p {{
                color: var(--button-secondary-text) !important;
            }}
        </style>
        """, unsafe_allow_html=True)

        # If no page is set, determine default based on API key availability
        if current_page is None:
            # Always start with main page - it will guide user to API setup if needed
            current_page = "main"
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

            # Legal & Policy Links
            st.sidebar.markdown("---")
            st.sidebar.markdown("### 📄 Legal")

            # Legal links in a compact format
            if st.sidebar.button("🔒 Privacy Policy", key="sidebar_privacy", use_container_width=True):
                st.session_state.page = "privacy_policy"
                st.rerun()

            if st.sidebar.button("📋 Terms & Conditions", key="sidebar_terms", use_container_width=True):
                st.session_state.page = "terms_conditions"
                st.rerun()

            if st.sidebar.button("💰 Refund Policy", key="sidebar_refund", use_container_width=True):
                st.session_state.page = "refund_policy"
                st.rerun()

            if st.sidebar.button("📞 Contact Us", key="sidebar_contact", use_container_width=True):
                st.session_state.page = "contact_us"
                st.rerun()

            # Cloud Sync Authentication Section
            st.sidebar.markdown("---")
            render_sidebar_auth_section()

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

        # Route to the appropriate page
        try:
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
            elif current_page == "privacy_policy":
                render_privacy_policy_page()
            elif current_page == "terms_conditions":
                render_terms_conditions_page()
            elif current_page == "refund_policy":
                render_refund_policy_page()
            elif current_page == "shipping_delivery":
                render_shipping_delivery_page()
            elif current_page == "contact_us":
                render_contact_us_page()
            elif current_page == "auth_handler":
                from page_modules.auth_handler import render_auth_handler_page
                render_auth_handler_page()
            else:
                # Default to main page
                print(f"Warning: Unknown page '{current_page}', defaulting to main")
                render_main_page()
        except Exception as page_error:
            st.error(f"Error loading page '{current_page}': {page_error}")
            st.write("Falling back to main page...")
            try:
                render_main_page()
            except Exception as fallback_error:
                st.error(f"Critical error: Could not load any page. {fallback_error}")
                st.stop()

    except Exception as e:
        st.error(f"App error: {e}")
        st.write("Please refresh the page or contact support.")

# Run the main function if this script is executed directly
if __name__ == "__main__":
    main()
