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

# Theme-aware CSS with CSS variables
is_dark = st.session_state.theme == "dark"

st.markdown(f"""
<style>
    /*
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
    */
    
    /*
    body {{
        font-size: var(--base-font-size);
        background-color: var(--bg-color);
        color: var(--text-color);
    }}
    */
    
    /* High contrast colors */
    /*
    .stTitle {{
        font-size: 2.5rem !important;
        font-weight: bold;
        color: var(--primary-color);
    }}
    */
    
    /*
    .stMarkdown h1 {{
        font-size: 2.2rem !important;
        color: var(--primary-color);
    }}
    
    .stMarkdown h2 {{
        font-size: 1.8rem !important;
        color: var(--secondary-color);
    }}
    
    .stMarkdown h3 {{
        font-size: 1.4rem !important;
        color: var(--tertiary-color);
    }}
    */
    
    /* Button color system */
    /*
    .stButton > button {{
        font-size: 1.1rem !important;
        padding: 0.8rem 1.6rem !important;
        border-radius: 6px !important;
        border: 2px solid transparent !important;
        transition: all 0.2s ease-in-out !important;
    }}
    */
    
    /* Primary Actions - Green */
    /*
    .stButton > button[data-testid*="primary"],
    .btn-primary {{
        background-color: #238636 !important;
        color: white !important;
        border-color: #3fb950 !important;
    }}
    
    .stButton > button[data-testid*="primary"]:hover,
    .btn-primary:hover {{
        background-color: #2ea043 !important;
        border-color: #56d364 !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(35, 134, 54, 0.3);
    }}
    */
    
    /* Secondary Actions - Blue */
    /*
    .btn-secondary {{
        background-color: #0969da !important;
        color: white !important;
        border-color: #218bff !important;
    }}
    
    .btn-secondary:hover {{
        background-color: #218bff !important;
        border-color: #79c0ff !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(9, 105, 218, 0.3);
    }}
    */
    
    /* Navigation Actions - Gray */
    .btn-navigation {{
        background-color: #f6f8fa !important;
        color: #24292f !important;
        border-color: #d0d7de !important;
    }}
    
    .btn-navigation:hover {{
        background-color: #f3f4f6 !important;
        border-color: #8c959f !important;
        transform: translateY(-1px);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }}
    
    /* Destructive Actions - Red */
    .btn-destructive {{
        background-color: #da3633 !important;
        color: white !important;
        border-color: #f85149 !important;
    }}
    
    .btn-destructive:hover {{
        background-color: #b62324 !important;
        border-color: #f85149 !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(218, 54, 51, 0.3);
    }}
    
    /* Cautionary Actions - Orange */
    .btn-caution {{
        background-color: #d29922 !important;
        color: white !important;
        border-color: #f2cc60 !important;
    }}
    
    .btn-caution:hover {{
        background-color: #bb8009 !important;
        border-color: #f2cc60 !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(210, 153, 34, 0.3);
    }}
    
    /* Utility Actions - Light Gray */
    .btn-utility {{
        background-color: #f6f8fa !important;
        color: #656d76 !important;
        border-color: #d1d9e0 !important;
    }}
    
    .btn-utility:hover {{
        background-color: #f3f4f6 !important;
        border-color: #8c959f !important;
        color: #24292f !important;
    }}
    
    /* Target specific buttons by text content - handled by JavaScript below */
    
    .stSelectbox, .stSlider, .stFileUploader, .stTextInput {{
        font-size: 1.05rem !important;
    }}
    
    .stInfo, .stSuccess, .stWarning, .stError {{
        font-size: 1.1rem !important;
        padding: 1.2rem !important;
    }}
    
    /* Accessible colors for colorblind users */
    .stInfo {{
        background-color: var(--info-bg) !important;
        border-color: var(--info-border) !important;
        color: var(--text-color) !important;
    }}
    
    .stSuccess {{
        background-color: var(--success-bg) !important;
        border-color: var(--success-border) !important;
        color: var(--text-color) !important;
    }}
    
    /*
    .stWarning {{
        background-color: var(--warning-bg) !important;
        border-color: var(--warning-border) !important;
        color: var(--text-color) !important;
    }}
    
    .stError {{
        background-color: var(--error-bg) !important;
        border-color: var(--error-border) !important;
        color: var(--text-color) !important;
    }}
    */
    
    /*
    .stTooltip {{
        font-size: 0.95rem !important;
    }}
    
    .metric-box {{
        background-color: var(--card-bg);
        border: 2px solid var(--card-border);
        border-radius: 8px;
        padding: 1.2rem;
        margin: 0.8rem 0;
        font-size: 1.1rem;
        color: var(--text-color);
    }}
    */

/* Center content and limit width on desktop */
/*
@media (min-width: 1024px) {{
    .main .block-container {{
        max-width: 900px;
        margin: 0 auto;
        padding-left: 2rem;
        padding-right: 2rem;
    }}
}}
*/

/* Improve spacing and readability */
/*
.main .block-container {{
    padding-top: 2rem;
    padding-bottom: 2rem;
}}
*/

/* Better button spacing and animations */
/*
.stButton>button {{
    margin: 0.25rem 0;
    transition: all 0.2s ease-in-out;
    border-radius: 8px;
}}

.stButton>button:hover {{
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}}

.stButton>button:active {{
    transform: translateY(0);
    transition: all 0.1s ease-in-out;
}}
*/

/* Primary button special styling */
/*
.stButton>button[data-testid*="primary"] {{
    background: var(--button-bg) !important;
    border: none;
    color: white;
    font-weight: 600;
}}

.stButton>button[data-testid*="primary"]:hover {{
    background: var(--button-hover-bg) !important;
    box-shadow: 0 6px 12px rgba(35, 134, 54, 0.3);
}}
*/

/* Improve expander appearance */
/*
.streamlit-expanderHeader {{
    font-weight: 600;
}}
*/

/* Hamburger menu for sidebar toggle */
/*
[data-testid="collapsedControl"] {{
    background: none !important;
    border: none !important;
}}

[data-testid="collapsedControl"]::before {{
    content: "☰";
    font-size: 18px;
    color: var(--text-color);
    display: block;
    width: 20px;
    height: 20px;
    text-align: center;
    line-height: 20px;
}}

[data-testid="collapsedControl"]:hover::before {{
    color: var(--primary-color);
}}
*/

/* Loading animations */
/*
@keyframes pulse {{
    0% {{ opacity: 1; }}
    50% {{ opacity: 0.5; }}
    100% {{ opacity: 1; }}
}}

.loading-pulse {{
    animation: pulse 2s infinite;
}}
*/

/* Progress bar enhancements */
/*
.stProgress > div > div {{
    background: var(--primary-color);
    border-radius: 10px;
}}
*/

/* Success message styling */
/*
.stSuccess {{
    border-left: 4px solid var(--button-bg);
    background-color: var(--success-bg);
    color: var(--text-color);
    padding: 1rem;
    border-radius: 8px;
    margin: 1rem 0;
}}
*/

/* Info message styling */
/*
.stInfo {{
    border-left: 4px solid var(--info-border);
    background-color: var(--info-bg);
    color: var(--text-color);
    padding: 1rem;
    border-radius: 8px;
    margin: 1rem 0;
}}
*/
</style>
""", unsafe_allow_html=True)

# Add JavaScript for dynamic button styling
st.markdown("""
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Utility buttons
    const utilityTexts = ['↑', '↓', '🏠 Main', '⚙️ Settings', '📊 Statistics', '📖 Documentation', '⬇️ Download Generation Log (TXT)', '🔄 Create New Deck'];
    utilityTexts.forEach(text => {
        const buttons = document.querySelectorAll('.stButton > button');
        buttons.forEach(button => {
            if (button.textContent.includes(text)) {
                button.classList.add('btn-utility');
            }
        });
    });
    
    // Destructive buttons
    const destructiveTexts = ['🗑️ Clear Text', '❌', '🔄 Clear All Cache'];
    destructiveTexts.forEach(text => {
        const buttons = document.querySelectorAll('.stButton > button');
        buttons.forEach(button => {
            if (button.textContent.includes(text)) {
                button.classList.add('btn-destructive');
            }
        });
    });
    
    // Caution buttons
    const cautionTexts = ['🧹 Clear Expired'];
    cautionTexts.forEach(text => {
        const buttons = document.querySelectorAll('.stButton > button');
        buttons.forEach(button => {
            if (button.textContent.includes(text)) {
                button.classList.add('btn-caution');
            }
        });
    });
    
    // Navigation buttons (back buttons)
    const navigationTexts = ['← Back', '⬅️ Back', '⬅️ Previous', 'Next ➡️'];
    navigationTexts.forEach(text => {
        const buttons = document.querySelectorAll('.stButton > button');
        buttons.forEach(button => {
            if (button.textContent.includes(text)) {
                button.classList.add('btn-navigation');
            }
        });
    });
});
</script>
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
