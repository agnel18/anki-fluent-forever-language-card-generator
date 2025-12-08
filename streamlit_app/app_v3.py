"""
Fluent Forever Anki Card Generator - Streamlit GUI (v3)
Production-ready, accessible, with progress tracking and optimal UX
API keys upfront, "Let's Go!" button, optimized loading
"""

import streamlit as st
import yaml
import os
import json
from pathlib import Path
import tempfile
from datetime import datetime
import pandas as pd
from core_functions import (
    generate_sentences,
    generate_audio,
    generate_images_pixabay,
    create_anki_tsv,
    create_zip_export,
    estimate_api_costs,
    get_available_voices,
    parse_csv_upload,
)
from firebase_utils import firebase
from frequency_utils import (
    get_available_frequency_lists,
    load_frequency_list,
    BATCH_PRESETS,
    format_batch_option,
    recommend_batch_strategy,
    get_csv_template,
    validate_word_list,
)

# ============================================================================
# PAGE CONFIG & STYLING
# ============================================================================

st.set_page_config(
    page_title="Fluent Forever Anki Generator",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# High contrast dark theme with large fonts
st.markdown("""
<style>
    :root {
        --base-font-size: 16px;
    }
    
    body {
        font-size: var(--base-font-size);
        background-color: #0e1117;
        color: #e6edf3;
    }
    
    /* High contrast colors */
    .stTitle {
        font-size: 2.5rem !important;
        color: #58a6ff !important;
        font-weight: bold !important;
    }
    
    .stMarkdown {
        font-size: 1rem !important;
    }
    
    .stButton > button {
        background-color: #238636 !important;
        color: #ffffff !important;
        font-size: 1.1rem !important;
        padding: 0.75rem 1.5rem !important;
        border-radius: 0.5rem !important;
        border: 2px solid #238636 !important;
        font-weight: bold !important;
    }
    
    .stButton > button:hover {
        background-color: #2ea043 !important;
        border-color: #58a6ff !important;
    }
    
    .stSelectbox, .stSlider, .stFileUploader, .stTextInput {
        font-size: 1rem !important;
    }
    
    .stAlert {
        font-size: 1.05rem !important;
        padding: 1rem !important;
    }
    
    /* Accessibility: High contrast */
    .stMetric {
        background-color: #161b22 !important;
        padding: 1.5rem !important;
        border-radius: 0.5rem !important;
        border: 1px solid #30363d !important;
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background-color: #58a6ff !important;
    }
    
    /* CTA Button - larger and more prominent */
    .cta-button {
        font-size: 1.3rem !important;
        padding: 1rem 2rem !important;
        background-color: #238636 !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE & INITIALIZATION
# ============================================================================

if "app_language" not in st.session_state:
    st.session_state.app_language = "en"

if "generated_data" not in st.session_state:
    st.session_state.generated_data = None

if "groq_api_key" not in st.session_state:
    st.session_state.groq_api_key = ""

if "pixabay_api_key" not in st.session_state:
    st.session_state.pixabay_api_key = ""

if "user_id" not in st.session_state:
    st.session_state.user_id = f"user_{hash(str(datetime.now())) % 1000000}"

if "current_progress" not in st.session_state:
    st.session_state.current_progress = None

if "current_language" not in st.session_state:
    st.session_state.current_language = None

if "current_batch_size" not in st.session_state:
    st.session_state.current_batch_size = 5

if "api_keys_set" not in st.session_state:
    st.session_state.api_keys_set = False

if "page" not in st.session_state:
    st.session_state.page = "api_setup"

# Load configuration
config_path = Path(__file__).parent / "languages.yaml"
with open(config_path, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

top_5 = config["top_5"]
all_languages = config["all_languages"]
ui_strings_all = config["ui_strings"]

def get_secret(key: str, default: str = "") -> str:
    """Get secret from environment or Streamlit secrets."""
    try:
        return st.secrets.get(key, os.getenv(key, default))
    except:
        return os.getenv(key, default)

def t(key: str) -> str:
    """Translate UI string."""
    lang = st.session_state.app_language
    if lang not in ui_strings_all:
        lang = "en"
    return ui_strings_all[lang].get(key, key)

# ============================================================================
# PAGE 1: API SETUP (FIRST-TIME)
# ============================================================================

if st.session_state.page == "api_setup":
    st.markdown("# 🌍 Language Learning Anki Deck Generator")
    st.markdown("Create custom Anki decks in minutes | Free, no data stored")
    
    st.divider()
    
    st.markdown("## 🔐 API Keys Setup")
    st.markdown("""
    Before we begin, we need your API keys to generate sentences and download images.
    
    **How this works:**
    1. You enter your API keys in this form
    2. They stay in your browser's temporary memory (session)
    3. We use them only to make API calls on YOUR behalf
    4. Your keys are NEVER stored anywhere - we can't access them
    5. When you close this tab/browser, keys are deleted
    
    **For Deployed Apps (Streamlit Cloud, etc):**
    - You never paste keys into the web form
    - App admin sets keys securely on the server
    - You just use the app - no key entry needed
    
    **Important privacy notes:**
    - ✅ Your API keys are **YOUR responsibility** - we never store them
    - ✅ Your data **stays with you** - nothing uploaded to our servers
    - ✅ You control the API usage and costs
    - ✅ You can delete/regenerate your keys anytime
    - ❌ DO NOT share your API keys with anyone
    - ❌ DO NOT upload .env files to websites
    - ❌ DO NOT commit .env to GitHub
    """)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🤖 Groq API Key")
        st.markdown("""
        **What it's for:** Generate example sentences in your target language
        
        **Get your free key:**
        1. Visit https://console.groq.com/keys
        2. Create an account (free)
        3. Generate new API key
        4. Copy and paste below
        """)
        
        groq_key_input = st.text_input(
            "Groq API Key",
            type="password",
            key="groq_setup",
            placeholder="gsk_...",
            help="Your Groq API key - kept secure in your session"
        )
    
    with col2:
        st.markdown("### 🖼️ Pixabay API Key")
        st.markdown("""
        **What it's for:** Download relevant images for each word
        
        **Get your free key:**
        1. Visit https://pixabay.com/api/docs/
        2. Create an account (free)
        3. Find your API key in dashboard
        4. Copy and paste below
        """)
        
        pixabay_key_input = st.text_input(
            "Pixabay API Key",
            type="password",
            key="pixabay_setup",
            placeholder="53606933-...",
            help="Your Pixabay API key - kept secure in your session"
        )
    
    st.divider()
    
    # Check for environment variables as fallback (development only)
    groq_env = get_secret("GROQ_API_KEY", "")
    pixabay_env = get_secret("PIXABAY_API_KEY", "")
    
    # If both env keys are available, auto-load them (no user action needed)
    if groq_env and pixabay_env and not groq_key_input:
        st.info("""
        ℹ️ **Development Mode Detected**
        
        Your API keys were found in environment variables (automatically loaded).
        
        **⚠️ Important:**
        - You are running this app locally on your computer
        - Your .env file stays on your computer only
        - DO NOT upload .env to any website or server
        - DO NOT commit .env to GitHub
        """)
        groq_key_input = groq_env
        pixabay_key_input = pixabay_env
    
    st.divider()
    
    # Validate and continue
    if st.button("🚀 Let's Go!", use_container_width=True, key="start_button"):
        if not groq_key_input:
            st.error("❌ Please enter your Groq API key")
        elif not pixabay_key_input:
            st.error("❌ Please enter your Pixabay API key")
        else:
            st.session_state.groq_api_key = groq_key_input
            st.session_state.pixabay_api_key = pixabay_key_input
            st.session_state.api_keys_set = True
            st.session_state.page = "main"
            st.success("✅ API keys saved securely!")
            st.rerun()

# ============================================================================
# PAGE 2: MAIN APP (AFTER API KEYS)
# ============================================================================

elif st.session_state.page == "main":
    
    # Header
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("# 🌍 Language Learning Anki Deck Generator")
    with col2:
        if st.button("🔐 API Keys"):
            st.session_state.page = "api_setup"
            st.rerun()
    
    st.markdown("Create custom Anki decks in minutes | Free, no data stored")
    st.divider()
    
    # ============================================================================
    # LANGUAGE SELECTION (Step 1)
    # ============================================================================
    
    st.markdown("## 📋 Select Your Language")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        lang_names = [lang["name"] for lang in all_languages]
        selected_lang = st.selectbox(
            "Which language do you want to learn?",
            lang_names,
            key="main_language",
            help="Choose from all available languages"
        )
    
    with col2:
        st.markdown("**Available**")
        available_lists = get_available_frequency_lists()
        max_words = available_lists.get(selected_lang, 5000)
        st.metric("", f"{max_words:,} words")
    
    st.divider()
    
    # ============================================================================
    # BATCH SIZE SELECTION (Step 2 - Fast loading with radio)
    # ============================================================================
    
    st.markdown("## ⏱️ Choose Your Batch Size")
    st.markdown("*10 sentences will be generated for each word*")
    
    # Create batch options
    batch_options = []
    batch_values = []
    for batch_size, info in BATCH_PRESETS.items():
        label = f"{info['emoji']} {batch_size} words • {info['time_estimate']} • {batch_size * 10} sentences"
        batch_options.append(label)
        batch_values.append(batch_size)
    
    selected_idx = batch_values.index(st.session_state.current_batch_size)
    selected_batch = st.radio(
        "Batch size options:",
        batch_options,
        index=selected_idx,
        key="batch_radio",
        label_visibility="collapsed"
    )
    
    # Update session state
    selected_batch_value = batch_values[batch_options.index(selected_batch)]
    st.session_state.current_batch_size = selected_batch_value
    
    st.divider()
    
    # ============================================================================
    # CTA BUTTON - "LET'S GO!"
    # ============================================================================
    
    st.markdown("## 🚀 Ready to Generate?")
    
    col1, col2, col3 = st.columns([1.5, 1.5, 1])
    
    with col1:
        if st.button(
            f"✨ Generate {selected_batch_value}-word Deck",
            use_container_width=True,
            key="generate_main",
        ):
            st.info(f"🎬 Generating {selected_batch_value} words in {selected_lang}...")
            st.session_state.current_language = selected_lang
            st.session_state.current_batch_size = selected_batch_value
            st.session_state.generating = True
    
    with col2:
        if st.button(
            f"👁️ Preview 1 Word",
            use_container_width=True,
            key="preview_main",
        ):
            st.info(f"Loading preview for {selected_lang}...")
    
    with col3:
        if st.button(
            "📥 Upload CSV",
            use_container_width=True,
            key="upload_tab",
        ):
            st.session_state.page = "upload"
            st.rerun()
    
    st.divider()
    
    # ============================================================================
    # QUICK TIPS
    # ============================================================================
    
    st.markdown("### 💡 Getting Started Tips")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🟢 First time?**
        Start with 5 words to see how it works.
        Takes only 5-10 minutes!
        """)
    
    with col2:
        st.markdown("""
        **💰 Cost?**
        Completely FREE using free tiers.
        You control your API usage.
        """)
    
    st.divider()
    
    st.markdown("---")
    st.markdown(
        "Made with ❤️ for language learners | "
        "[GitHub](https://github.com/agnel18/anki-fluent-forever-language-card-generator)"
    )

# ============================================================================
# PAGE 3: UPLOAD (CSV/XLSX)
# ============================================================================

elif st.session_state.page == "upload":
    
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("# 📥 Upload Your Own Words")
    with col2:
        if st.button("← Back"):
            st.session_state.page = "main"
            st.rerun()
    
    st.markdown("Import your custom word list from CSV or XLSX file")
    st.divider()
    
    # Template
    csv_template = get_csv_template()
    st.download_button(
        label="📋 Download CSV Template",
        data=csv_template,
        file_name="word_list_template.csv",
        mime="text/csv",
        use_container_width=True
    )
    
    st.divider()
    
    # Upload
    uploaded_file = st.file_uploader(
        "Choose CSV or XLSX file",
        type=["csv", "xlsx"],
        help="First column should contain words (one word per row)"
    )
    
    if uploaded_file:
        try:
            if uploaded_file.type == "text/csv":
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            words = df.iloc[:, 0].dropna().tolist()
            words = [str(w).strip() for w in words if w]
            
            is_valid, message = validate_word_list(words)
            
            if is_valid:
                st.success(message)
                
                col1, col2 = st.columns(2)
                col1.metric("Words found", len(words))
                col2.metric("Ready to generate", "✅")
                
                st.divider()
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🚀 Generate Deck", use_container_width=True):
                        st.session_state.custom_words = words
                        st.session_state.current_language = "Custom"
                        st.session_state.current_batch_size = len(words)
                        st.session_state.generating = True
                
                with col2:
                    if st.button("👁️ Preview 1 Word", use_container_width=True):
                        st.info("Loading preview...")
            else:
                st.error(message)
        
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")
