"""
Fluent Forever Anki Card Generator - Streamlit GUI (v2)
Production-ready, accessible, with progress tracking and optimal UX
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
    st.session_state.current_batch_size = None

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
# HEADER
# ============================================================================

st.markdown("# 🌍 Language Learning Anki Deck Generator")
st.markdown("Create custom Anki decks in minutes | Free, no data stored")

st.divider()

# ============================================================================
# SIDEBAR - SETTINGS & API KEYS
# ============================================================================

with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    # Language selector
    lang_options = ["English", "Español", "Français", "हिन्दी", "中文"]
    lang_codes = ["en", "es", "fr", "hi", "zh"]
    selected_lang_idx = st.selectbox(
        "Interface Language:",
        range(len(lang_options)),
        format_func=lambda i: lang_options[i],
        key="lang_select"
    )
    st.session_state.app_language = lang_codes[selected_lang_idx]
    
    st.divider()
    
    # API Keys
    st.markdown("### 🔑 API Keys")
    st.info("⚠️ Never share your API keys. They stay in your browser.")
    
    groq_key = st.text_input(
        "Groq API Key",
        type="password",
        value=st.session_state.groq_api_key or get_secret("GROQ_API_KEY", ""),
        key="groq_input",
    )
    if groq_key and not st.session_state.groq_api_key:
        st.session_state.groq_api_key = groq_key
    
    pixabay_key = st.text_input(
        "Pixabay API Key",
        type="password",
        value=st.session_state.pixabay_api_key or get_secret("PIXABAY_API_KEY", ""),
        key="pixabay_input",
    )
    if pixabay_key and not st.session_state.pixabay_api_key:
        st.session_state.pixabay_api_key = pixabay_key
    
    st.divider()
    
    # Voice options (collapsible)
    with st.expander("🎤 Voice Settings (Optional)"):
        st.markdown("**Customize how sentences are spoken**")
        
        voice_gender = st.radio(
            "Narrator gender:",
            ["Female (Default)", "Male"],
            horizontal=True,
            help="Choose voice gender preference"
        )
        
        pitch_value = st.slider(
            "Pitch adjustment:",
            -30, 30, 0,
            help="Higher = higher pitch, Lower = lower pitch"
        )
        
        speed_value = st.slider(
            "Playback speed:",
            0.5, 2.0, 0.8,
            0.1,
            help="0.8x is recommended for language learners"
        )
        
        st.caption(f"Current: {voice_gender} | Pitch: {pitch_value:+d} | Speed: {speed_value}x")

# ============================================================================
# MAIN AREA - INPUT METHOD SELECTION
# ============================================================================

st.markdown("## 📋 How would you like to learn?")

# Three main input methods
tab1, tab2, tab3 = st.tabs(["📚 Frequency List", "📥 Upload Words", "🎯 Quick Demo"])

# ============================================================================
# TAB 1: FREQUENCY LIST (DEFAULT)
# ============================================================================

with tab1:
    st.markdown("### 📚 Use our curated frequency lists")
    st.markdown("Best for beginners - pre-selected words in order of importance")
    
    # Step 1: Select language
    st.markdown("**Step 1: Select Language**")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        lang_names = [lang["name"] for lang in all_languages]
        selected_lang = st.selectbox(
            "Choose language:",
            lang_names,
            key="freq_language",
            help="Select from all 109 available languages"
        )
    
    with col2:
        available_lists = get_available_frequency_lists()
        max_words = available_lists.get(selected_lang, 5000)
        st.metric("Available words", f"{max_words:,}")
    
    st.markdown("---")
    
    # Step 2: Select batch size
    st.markdown("**Step 2: Choose batch size**")
    st.markdown("⏱️ *Estimated time includes generation + audio + images*")
    
    cols = st.columns(2)
    batch_selection = None
    
    for idx, (batch_size, info) in enumerate(BATCH_PRESETS.items()):
        col = cols[idx % 2]
        
        if info.get("disabled"):
            col.info(f"{info['emoji']} **{batch_size} words** - {info['description']}")
        else:
            is_recommended = "⭐ RECOMMENDED" if info["recommended"] else ""
            col.button(
                f"{info['emoji']} **{batch_size} words**\n{info['time_estimate']}\n{is_recommended}",
                key=f"batch_{batch_size}",
                use_container_width=True,
                on_click=lambda b=batch_size: setattr(st.session_state, "selected_batch_size", b)
            )
    
    selected_batch = getattr(st.session_state, "selected_batch_size", 100)
    
    st.divider()
    
    # Check for existing progress
    progress = firebase.get_user_progress(
        st.session_state.user_id,
        selected_lang,
        selected_batch
    )
    
    if progress:
        st.markdown("### 📊 Your Progress")
        progress_pct = progress["percentage_complete"]
        st.progress(progress_pct / 100)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Completed", f"{progress['completed_words']} / {selected_batch}")
        col2.metric("Progress", f"{progress_pct}%")
        col3.metric("Last session", progress["last_updated"].split("T")[0])
        
        col1, col2, col3 = st.columns(3)
        if col1.button("✅ Continue from word #" + str(progress["last_word_index"] + 1)):
            st.session_state.current_progress = progress
            st.session_state.current_language = selected_lang
            st.session_state.current_batch_size = selected_batch
            st.success(f"Resuming from word #{progress['last_word_index'] + 1}")
        
        if col2.button("🔄 Restart this batch"):
            firebase.reset_progress(st.session_state.user_id, selected_lang, selected_batch)
            st.success("Progress reset. Starting fresh!")
            st.rerun()
        
        if col3.button("❓ Preview first"):
            st.info("Loading preview...")
    
    else:
        st.markdown("### ✨ Ready to begin?")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if st.button(f"🎬 Generate {selected_batch}-word deck", use_container_width=True):
                st.session_state.current_language = selected_lang
                st.session_state.current_batch_size = selected_batch
                st.session_state.generating = True
        
        with col2:
            if st.button("👁️ Preview demo", use_container_width=True):
                st.info("Loading preview of 1 random word...")

# ============================================================================
# TAB 2: CSV/XLSX UPLOAD
# ============================================================================

with tab2:
    st.markdown("### 📥 Upload your own word list")
    st.markdown("Supported formats: CSV, XLSX | Required column: **Word**")
    
    # Template download
    csv_template = get_csv_template()
    st.download_button(
        label="📋 Download CSV template",
        data=csv_template,
        file_name="word_list_template.csv",
        mime="text/csv",
        use_container_width=True
    )
    
    st.divider()
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose CSV or XLSX file",
        type=["csv", "xlsx"],
        help="First column should contain words"
    )
    
    if uploaded_file:
        try:
            if uploaded_file.type == "text/csv":
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            # Get words from first column
            words = df.iloc[:, 0].dropna().tolist()
            words = [str(w).strip() for w in words if w]
            
            # Validate
            is_valid, message = validate_word_list(words)
            
            if is_valid:
                st.success(message)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Words found", len(words))
                with col2:
                    st.metric("Ready to generate", "✅")
                
                col1, col2 = st.columns(2)
                if col1.button("🎬 Generate deck", use_container_width=True):
                    st.session_state.current_language = "Custom"
                    st.session_state.current_batch_size = len(words)
                    st.session_state.custom_words = words
                    st.session_state.generating = True
                
                if col2.button("👁️ Preview 1 word", use_container_width=True):
                    st.info("Loading preview...")
            else:
                st.error(message)
        
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")

# ============================================================================
# TAB 3: QUICK DEMO
# ============================================================================

with tab3:
    st.markdown("### 🎯 Try it with one word")
    st.markdown("See exactly what you'll get in your Anki deck")
    
    demo_lang = st.selectbox(
        "Select language for demo:",
        [l["name"] for l in all_languages[:10]],
        key="demo_language"
    )
    
    demo_word = st.text_input(
        "Enter a word (optional - we'll pick a random one):",
        placeholder="e.g., water, house, love",
        key="demo_word_input"
    )
    
    if st.button("🎬 Generate demo", use_container_width=True):
        if not st.session_state.groq_api_key:
            st.error("❌ Groq API key required. Add it in Settings →")
        else:
            st.info(f"Generating demo for '{demo_word or 'random word'}' in {demo_lang}...")
            
            try:
                sentences = generate_sentences(
                    word=demo_word or "water",
                    meaning="sample word",
                    language=demo_lang,
                    num_sentences=1,
                    difficulty="beginner",
                    groq_api_key=st.session_state.groq_api_key or groq_key,
                )
                
                if sentences:
                    st.success("✅ Generated sentence:")
                    st.json(sentences[0])
                    
                    # Try to generate audio
                    voices = get_available_voices(demo_lang.lower()[:2])
                    if voices:
                        audio_files = generate_audio(
                            sentences=[sentences[0]["sentence"]],
                            voice=voices[0],
                            output_dir=Path(tempfile.gettempdir()) / "demo_audio",
                            batch_name="demo",
                            rate=0.8,
                        )
                        
                        if audio_files:
                            st.success("✅ Audio generated!")
                            audio_path = Path(tempfile.gettempdir()) / "demo_audio" / audio_files[0]
                            st.audio(str(audio_path))
                else:
                    st.error("❌ Failed to generate. Check your Groq API key.")
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# ============================================================================
# FOOTER
# ============================================================================

st.divider()

st.markdown("---")
st.markdown(
    "Made with ❤️ for language learners | "
    "[GitHub](https://github.com/agnel18/anki-fluent-forever-language-card-generator) | "
    "Privacy: No data stored online, only your progress"
)
