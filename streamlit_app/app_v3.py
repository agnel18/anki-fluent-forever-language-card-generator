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

# Add custom CSS for better desktop layout
st.markdown("""
<style>
/* Center content and limit width on desktop */
@media (min-width: 1024px) {
    .main .block-container {
        max-width: 900px;
        margin: 0 auto;
        padding-left: 2rem;
        padding-right: 2rem;
    }
}

/* Improve spacing and readability */
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Better button spacing and animations */
.stButton>button {
    margin: 0.25rem 0;
    transition: all 0.2s ease-in-out;
    border-radius: 8px;
}

.stButton>button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.stButton>button:active {
    transform: translateY(0);
    transition: all 0.1s ease-in-out;
}

/* Primary button special styling */
.stButton>button[data-testid*="primary"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    color: white;
    font-weight: 600;
}

.stButton>button[data-testid*="primary"]:hover {
    background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
    box-shadow: 0 6px 12px rgba(102, 126, 234, 0.3);
}

/* Improve expander appearance */
.streamlit-expanderHeader {
    font-weight: 600;
}

/* Hamburger menu for sidebar toggle */
[data-testid="collapsedControl"] {
    background: none !important;
    border: none !important;
}

[data-testid="collapsedControl"]::before {
    content: "☰";
    font-size: 18px;
    color: #666;
    display: block;
    width: 20px;
    height: 20px;
    text-align: center;
    line-height: 20px;
}

[data-testid="collapsedControl"]:hover::before {
    color: #000;
}

/* Loading animations */
@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
}

.loading-pulse {
    animation: pulse 2s infinite;
}

/* Progress bar enhancements */
.stProgress > div > div {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    border-radius: 10px;
}

/* Success message styling */
.stSuccess {
    border-left: 4px solid #28a745;
    background-color: #d4edda;
    color: #155724;
    padding: 1rem;
    border-radius: 8px;
    margin: 1rem 0;
}

/* Info message styling */
.stInfo {
    border-left: 4px solid #17a2b8;
    background-color: #d1ecf1;
    color: #0c5460;
    padding: 1rem;
    border-radius: 8px;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# --- Additional Imports to Fix Errors ---
import yaml
import pandas as pd
import datetime
from pathlib import Path

# Import constants and functions from local modules
from edge_tts_voices import EDGE_TTS_VOICES
from frequency_utils import get_available_frequency_lists, get_csv_template, get_words_with_ranks, validate_word_list, parse_uploaded_word_file
from db_manager import get_completed_words, get_word_stats
from firebase_manager import get_session_id

# Import our new modular components
from constants import *
from utils import log_message, fmt_num, usage_bar
from state_manager import initialize_session_state, initialize_languages_config, initialize_firebase_settings

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
if "learned_languages" not in st.session_state:
    from pathlib import Path
    import yaml
    config_path = Path(__file__).parent / "languages.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    st.session_state.learned_languages = [
        {"name": lang["name"], "usage": 0, "pinned": True} for lang in config["top_5"]
    ]

# Determine which section to show based on session state
current_page = st.session_state.get("page", "main")

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
