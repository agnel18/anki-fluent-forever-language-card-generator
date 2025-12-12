"""
Fluent Forever Anki Card Generator - Streamlit GUI (v3)
Production-ready with full generation workflow
"""

import streamlit as st
import yaml
import os
import datetime
from edge_tts_voices import EDGE_TTS_VOICES
from pathlib import Path
import pandas as pd
from core_functions import (
    generate_complete_deck,
    create_zip_export,
    create_apkg_export,
)
from frequency_utils import (
    get_available_frequency_lists,
    load_frequency_list,
    BATCH_PRESETS,
    validate_word_list,
    get_csv_template,
    parse_uploaded_word_file,
    get_words_with_ranks,
)
from db_manager import (
    get_words_paginated,
    search_words,
    mark_words_completed,
    get_completed_words,
    get_word_stats,
    log_generation,
)
from firebase_manager import get_session_id, sync_progress_to_firebase, log_generation_to_firebase

st.markdown("""
<style>
    body { font-size: 16px !important; }
    .stButton > button {
        background-color: #238636 !important;
        color: #ffffff !important;
        font-size: 1.1rem !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: bold !important;
        border-radius: 6px !important;
    }
    .stProgress > div > div > div > div {
        background-color: #58a6ff !important;
    }

    /* Responsive adjustments for mobile */
    @media (max-width: 700px) {
        html, body {
            font-size: 15px !important;
        }
        .stButton > button {
            font-size: 1rem !important;
            padding: 0.7rem 1rem !important;
        }
        .stMetric, .stMarkdown, .stTextInput, .stSelectbox, .stSlider, .stFileUploader {
            font-size: 0.98rem !important;
        }
        .stColumn {
            min-width: 100% !important;
            flex-basis: 100% !important;
            max-width: 100% !important;
        }
        .stTabs {
            flex-direction: column !important;
        }
        .stMarkdown h1 {
            font-size: 1.5rem !important;
        }
        .stMarkdown h2 {
            font-size: 1.2rem !important;
        }
        .stMarkdown h3 {
            font-size: 1rem !important;
        }
        .lang-card-grid {
            grid-template-columns: 1fr !important;
        }
        .lang-card {
            flex-direction: column !important;
            align-items: flex-start !important;
        }
        .stDownloadButton > button {
            font-size: 1rem !important;
            padding: 0.7rem 1rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# SESSION STATE
# ============================================================================
if "settings" not in st.session_state:
    st.session_state.settings = {}
if "settings_dirty" not in st.session_state:
    st.session_state.settings_dirty = False

# Always initialize learned_languages with top 5 most spoken if not set
if "learned_languages" not in st.session_state:
    # Try to load from user_settings.json if available
    user_settings_path = Path(__file__).parent / "user_settings.json"
    loaded = False
    if user_settings_path.exists():
        import json
        with open(user_settings_path, "r", encoding="utf-8") as f:
            per_lang_settings = json.load(f)
        if "learned_languages" in per_lang_settings:
            st.session_state.learned_languages = per_lang_settings["learned_languages"]
            loaded = True
    if not loaded:
        # Fallback: use top 5 most spoken
        config_path = Path(__file__).parent / "languages.yaml"
        import yaml
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        st.session_state.learned_languages = [
            {"name": lang["name"], "usage": 0, "pinned": True} for lang in config["top_5"]
        ]

# ============================================================================
# PAGE NAVIGATION: SIDEBAR
# ============================================================================



if "page" not in st.session_state:
    st.session_state.page = "login"
# Only show sidebar if not on login or api_setup page
if st.session_state.get("page", "login") not in ["login", "api_setup"]:
    with st.sidebar:
        st.markdown("## ⚙️ Settings")
        if st.button("Open Settings", key="sidebar_settings_btn"):
            st.session_state.page = "settings"
            st.rerun()
        st.markdown("---")
        # Basic API usage summary (no details)
        st.markdown("### API Usage (Session)")
        # Groq: 1000 calls/day (typical free tier), 3,000,000 tokens/month (example)
        groq_calls = st.session_state.get("groq_api_calls", 0)
        groq_tokens = st.session_state.get("groq_tokens_used", 0)
        pixabay_calls = st.session_state.get("pixabay_api_calls", 0)
        # These limits can be adjusted to match actual API tier
        GROQ_CALL_LIMIT = 1000  # per day (example)
        GROQ_TOKEN_LIMIT = 3000000  # per month (example)
        PIXABAY_CALL_LIMIT = 5000  # per day (free tier)
        def fmt_num(n):
            if n >= 1_000_000:
                return f"{n//1_000_000}M"
            elif n >= 100_000:
                return f"{n//1_000}k"
            elif n >= 10_000:
                return f"{n/1000:.1f}k"
            return str(n)
        st.metric("Groq Calls", f"{fmt_num(groq_calls)} / {fmt_num(GROQ_CALL_LIMIT)}")
        st.metric("Groq Tokens", f"{fmt_num(groq_tokens)} / {fmt_num(GROQ_TOKEN_LIMIT)}")
        st.metric("Pixabay Calls", f"{fmt_num(pixabay_calls)} / {fmt_num(PIXABAY_CALL_LIMIT)}")
        st.caption("See more details → Usage Statistics page. Limits are approximate—check your API dashboard for exact quotas.")
        if st.button("📊 Usage Statistics", key="sidebar_stats_btn"):
            st.session_state.page = "statistics"
            st.rerun()
        st.markdown("---")
        st.markdown("[Project README](../README.md)")
        st.markdown("---")
# ============================================================================
# STATISTICS PAGE
# ============================================================================

if st.session_state.get("page", "login") == "statistics":
    st.title("📊 Usage Statistics & Progress Tracking")
    st.markdown("---")
    st.markdown("### API Usage (Session)")
    st.metric("Groq Calls", st.session_state.get("groq_api_calls", 0))
    st.metric("Groq Tokens", st.session_state.get("groq_tokens_used", 0))
    st.metric("Pixabay Calls", st.session_state.get("pixabay_api_calls", 0))
    st.caption("Counts update live as you generate decks. Tracks only this session.")
    st.markdown("---")
    # Add more progress/statistics here as needed
    if st.button("⬅️ Back", key="stats_back_btn"):
        st.session_state.page = "language_select" if st.session_state.get("first_run_complete", False) else "login"
        st.rerun()


if "page" not in st.session_state:
    st.session_state.page = "login"
if "groq_api_key" not in st.session_state:
    st.session_state.groq_api_key = ""
if "pixabay_api_key" not in st.session_state:
    st.session_state.pixabay_api_key = ""
if "current_batch_size" not in st.session_state:
    st.session_state.current_batch_size = 5

if "loaded_words" not in st.session_state:
    st.session_state.loaded_words = {}

if "current_lang_words" not in st.session_state:
    st.session_state.current_lang_words = []

if "completed_words" not in st.session_state:
    st.session_state.completed_words = {}  # {language: [list of completed words]}

if "selection_mode" not in st.session_state:
    st.session_state.selection_mode = "range"  # range, manual, search

# Global settings defaults
if "difficulty" not in st.session_state:
    st.session_state.difficulty = "intermediate"  # beginner, intermediate, advanced
if "sentence_length_range" not in st.session_state:
    st.session_state.sentence_length_range = (6, 16)
if "sentences_per_word" not in st.session_state:
    st.session_state.sentences_per_word = 10
if "track_progress" not in st.session_state:
    st.session_state.track_progress = True
if "audio_speed" not in st.session_state:
    st.session_state.audio_speed = 0.8
## Pitch feature removed
if "selected_voice" not in st.session_state:
    st.session_state.selected_voice = None
if "selected_voice_display" not in st.session_state:
    st.session_state.selected_voice_display = None
if "first_run_complete" not in st.session_state:
    st.session_state.first_run_complete = False

from firebase_manager import load_settings_from_firebase, save_settings_to_firebase
# Database and Firebase
if "session_id" not in st.session_state:
    st.session_state.session_id = get_session_id()
if "current_page" not in st.session_state:
    st.session_state.current_page = {}

# Auto-load API keys from Firebase for logged-in users
if not st.session_state.get("is_guest", True):
    firebase_settings = load_settings_from_firebase(st.session_state.session_id)
    if firebase_settings:
        st.session_state.groq_api_key = firebase_settings.get("groq_api_key", "")
        st.session_state.pixabay_api_key = firebase_settings.get("pixabay_api_key", "")

config_path = Path(__file__).parent / "languages.yaml"
with open(config_path, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

all_languages = config["all_languages"]

def get_secret(key: str, default: str = "") -> str:
    try:
        return st.secrets.get(key, os.getenv(key, default))
    except:
        return os.getenv(key, default)

# ============================================================================

# ============================================================================
# SETTINGS PAGE
# ============================================================================

if st.session_state.page == "settings":
    st.title("Settings")
    st.markdown("---")
    st.markdown("### 👤 Profile (Mocked Firebase)")
    # Mocked Firebase user info
    mock_user = {
        "name": "Jane Doe",
        "email": "jane.doe@email.com",
        "avatar": "https://randomuser.me/api/portraits/women/44.jpg"
    }
    cols = st.columns([1, 4])
    with cols[0]:
        st.image(mock_user["avatar"], width=80)
    with cols[1]:
        st.markdown(f"**Name:** {mock_user['name']}")
        st.markdown(f"**Email:** {mock_user['email']}")
        st.caption("(Firebase integration coming soon)")
    st.markdown("---")
    st.markdown("### 🌟 Favorite Languages (Pinned for Quick Access)")
    st.info("Your favorite languages appear first in all dropdowns for faster selection.")
    # Add favorite language
    all_lang_names = [lang["name"] for lang in all_languages]
    if "learned_languages" not in st.session_state:
        st.session_state.learned_languages = [
            {"name": "Spanish", "usage": 42, "pinned": True},
            {"name": "French", "usage": 35, "pinned": True},
            {"name": "Japanese", "usage": 28, "pinned": True},
            {"name": "German", "usage": 19, "pinned": False},
            {"name": "Italian", "usage": 12, "pinned": False},
        ]
    st.markdown("Add a favorite language:")
    add_col1, add_col2 = st.columns([4,1])
    with add_col1:
        available_langs = [l for l in all_lang_names if l not in [x["name"] for x in st.session_state.learned_languages]]
        new_lang = st.selectbox("Select language", available_langs, key="add_lang_select", disabled=len(st.session_state.learned_languages) >= 5)
    with add_col2:
        if st.button("Add", key="add_lang_btn") and new_lang and len(st.session_state.learned_languages) < 5:
            st.session_state.learned_languages.append({"name": new_lang, "usage": 0})
            st.success(f"Added {new_lang}")
            st.rerun()

    # --- Favorite Languages List ---
    st.markdown("Your Favorites:")
    st.markdown("""
    <style>
    .lang-card-grid {display: flex; flex-direction: column; gap: 18px; margin-bottom: 16px;}
    .lang-card {background: #181a20; color: #e0e0e0; border-radius: 12px; box-shadow: 0 2px 8px #0002; padding: 18px 22px 14px 22px; min-width: 180px; max-width: 320px; display: flex; flex-direction: row; align-items: center; position: relative; transition: box-shadow 0.2s;}
    .lang-card .lang-title {font-size: 1.15em; font-weight: 600; margin-bottom: 6px;}
    .lang-card .lang-usage {font-size: 0.98em; color: #aaa; margin-bottom: 8px;}
    .lang-card .lang-actions {margin-left: auto; display: flex; gap: 4px;}
    .lang-card .stButton>button {background: none !important; color: #ff5555 !important; font-size: 1.2em !important; border: none !important; box-shadow: none !important; padding: 0 8px !important;}
    .lang-card .stButton>button:hover {color: #fff !important; background: #ff5555 !important; border-radius: 50% !important;}
    .lang-card .arrow-btn .stButton>button {color: #58a6ff !important; font-size: 1.1em !important;}
    .lang-card .arrow-btn .stButton>button:hover {color: #fff !important; background: #58a6ff !important; border-radius: 50% !important;}
    </style>
    <div class='lang-card-grid'>
    """, unsafe_allow_html=True)
    for idx, lang in enumerate(st.session_state.learned_languages):
        card_cols = st.columns([8,1,1,1])
        with card_cols[0]:
            st.markdown(f"<div class='lang-card'><span class='lang-title'>{lang['name']}</span><span class='lang-usage'>Usage: {lang['usage']}</span></div>", unsafe_allow_html=True)
        with card_cols[1]:
            if idx > 0:
                if st.button("↑", key=f"moveup_{lang['name']}_{idx}", help=f"Move {lang['name']} up"):
                    st.session_state.learned_languages[idx-1], st.session_state.learned_languages[idx] = st.session_state.learned_languages[idx], st.session_state.learned_languages[idx-1]
                    st.rerun()
        with card_cols[2]:
            if idx < len(st.session_state.learned_languages)-1:
                if st.button("↓", key=f"movedown_{lang['name']}_{idx}", help=f"Move {lang['name']} down"):
                    st.session_state.learned_languages[idx+1], st.session_state.learned_languages[idx] = st.session_state.learned_languages[idx], st.session_state.learned_languages[idx+1]
                    st.rerun()
        with card_cols[3]:
            if st.button("❌", key=f"remove_{lang['name']}_{idx}", help=f"Remove {lang['name']}"):
                st.session_state.learned_languages = [l for i, l in enumerate(st.session_state.learned_languages) if i != idx]
                st.rerun()
    st.caption("Reorder with arrows. Remove with ❌. Max 5.")
    # Save Order button
    user_settings_path = Path(__file__).parent / "user_settings.json"
    if st.button("💾 Save Order", key="save_lang_order"):
        import json
        # Save the current order to user_settings.json
        if user_settings_path.exists():
            with open(user_settings_path, "r", encoding="utf-8") as f:
                per_lang_settings = json.load(f)
        else:
            per_lang_settings = {}
        per_lang_settings["learned_languages"] = st.session_state.learned_languages
        with open(user_settings_path, "w", encoding="utf-8") as f:
            json.dump(per_lang_settings, f, indent=2)
        st.success("Order saved!")
    st.markdown("---")

    # Handle pin/unpin/remove actions via query params
    import streamlit as stmod
    query_params = stmod.query_params
    if "remove" in query_params:
        lang_name = query_params["remove"]
        st.session_state.learned_languages = [l for l in st.session_state.learned_languages if l["name"] != lang_name]
        stmod.query_params.clear()
        st.rerun()
    st.markdown("### 🔑 API Keys")
    import json
    secrets_path = Path(__file__).parent / "user_secrets.json"
    # Load secrets
    if secrets_path.exists():
        with open(secrets_path, "r", encoding="utf-8") as f:
            user_secrets = json.load(f)
    else:
        user_secrets = {"groq_api_key": "", "pixabay_api_key": ""}

    st.caption("Your API keys are stored only on your device (never uploaded). Edit or reveal as needed.")
    api_keys = {
        "Groq API Key": "groq_api_key",
        "Pixabay API Key": "pixabay_api_key"
    }
    for label, key in api_keys.items():
        st.markdown(f"**{label}**")
        masked = user_secrets.get(key, "")
        if masked:
            masked_display = "*" * max(6, len(masked) - 4) + masked[-4:]
        else:
            masked_display = "(not set)"
        col1, col2, col3 = st.columns([3,1,1])
        with col1:
            if st.session_state.get(f"reveal_{key}", False):
                st.text_input(f"{label}", value=masked, key=f"edit_{key}")
            else:
                st.text_input(f"{label}", value=masked_display, disabled=True, key=f"disp_{key}")
        with col2:
            if st.button("👁️" if not st.session_state.get(f"reveal_{key}", False) else "🙈", key=f"revealbtn_{key}"):
                st.session_state[f"reveal_{key}"] = not st.session_state.get(f"reveal_{key}", False)
                st.rerun()
        with col3:
            if st.session_state.get(f"reveal_{key}", False):
                if st.button("💾 Save", key=f"save_{key}"):
                    new_val = st.session_state.get(f"edit_{key}", "")
                    user_secrets[key] = new_val
                    with open(secrets_path, "w", encoding="utf-8") as f:
                        json.dump(user_secrets, f, indent=2)
                    st.success(f"{label} saved!")
                    st.session_state[f"reveal_{key}"] = False
                    st.experimental_rerun()
    st.markdown("---")
    st.markdown("---")
    st.markdown("### ⚡ Default Settings Per Language")
    import json
    user_settings_path = Path(__file__).parent / "user_settings.json"
    # Load per-language settings
    if user_settings_path.exists():
        with open(user_settings_path, "r", encoding="utf-8") as f:
            per_lang_settings = json.load(f)
    else:
        per_lang_settings = {}

    st.caption("Set your preferred speed, difficulty, and voice for each language you are learning. These will be used as defaults when generating decks.")
    all_lang_names = list(EDGE_TTS_VOICES.keys())
    selected_lang = st.selectbox("Select language to set defaults:", all_lang_names, key="default_settings_lang_select")
    # Difficulty
    diff_key = f"{selected_lang}_difficulty"
    diff_val = per_lang_settings.get(selected_lang, {}).get("difficulty", "intermediate")
    new_diff = st.radio(
        f"Difficulty for {selected_lang}",
        ["beginner", "intermediate", "advanced"],
        index=["beginner", "intermediate", "advanced"].index(diff_val),
        key=diff_key,
        horizontal=True
    )
    # Speed
    speed_key = f"{selected_lang}_speed"
    speed_val = per_lang_settings.get(selected_lang, {}).get("speed", 0.8)
    new_speed = st.slider(
        f"Audio Speed for {selected_lang}",
        min_value=0.5,
        max_value=1.5,
        value=speed_val,
        step=0.1,
        key=speed_key
    )
    # Voice
    voice_key = f"{selected_lang}_voice"
    voice_val = per_lang_settings.get(selected_lang, {}).get("voice", None)
    voice_options = [f"{v[0]} ({v[1]}, {v[2]})" for v in EDGE_TTS_VOICES[selected_lang]]
    default_voice_idx = 0
    if voice_val and voice_val in [v[0] for v in EDGE_TTS_VOICES[selected_lang]]:
        default_voice_idx = [v[0] for v in EDGE_TTS_VOICES[selected_lang]].index(voice_val)
    new_voice_display = st.selectbox(
        f"Voice for {selected_lang}",
        options=voice_options,
        index=default_voice_idx,
        key=voice_key
    )
    new_voice = EDGE_TTS_VOICES[selected_lang][voice_options.index(new_voice_display)][0]
    # Save button for this language
    if st.button(f"Save Defaults for {selected_lang}", key=f"save_{selected_lang}"):
        per_lang_settings[selected_lang] = {
            "difficulty": new_diff,
            "speed": new_speed,
            "voice": new_voice
        }
        with open(user_settings_path, "w", encoding="utf-8") as f:
            json.dump(per_lang_settings, f, indent=2)
        st.session_state["show_save_defaults_msg"] = True
    st.markdown("---")
    # Show confirmation if just saved defaults
    if st.session_state.get("show_save_defaults_msg"):
        st.success(f"Defaults saved for {selected_lang}!")
        st.session_state["show_save_defaults_msg"] = False
    st.markdown("---")
    if st.button("⬅️ Back", key="settings_back_btn"):
        st.session_state.page = "language_select" if st.session_state.get("first_run_complete", False) else "login"
        st.rerun()


if st.session_state.page == "login":
    st.markdown("# 🔐 Login to Language Card Generator")
    st.markdown("""
    - **Sign in with Google for full access and persistent stats**  
    - Or continue as guest (limited, no cloud sync)
    """)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Sign in with Google", use_container_width=True):
            st.session_state.page = "api_setup"
            st.session_state.is_guest = False
            st.rerun()
    with col2:
        if st.button("Continue as Guest", use_container_width=True):
            st.session_state.page = "api_setup"
            st.session_state.is_guest = True
            st.rerun()

# ============================================================================
# PAGE 1: API SETUP
# ============================================================================

elif st.session_state.page == "api_setup":
    st.markdown("# 🌍 Language Learning Anki Deck Generator")
    st.markdown("Create custom Anki decks in minutes | Free, no data stored")
    st.divider()
    st.markdown("## 🔐 API Keys Setup")
    st.markdown(
        """
**How it works:**
1. You enter your API keys in this form
2. They stay in your browser\'s temporary memory (session only)
3. We use them ONLY to make API calls on YOUR behalf
4. Your keys are NEVER stored anywhere
5. When you close this tab, keys are automatically deleted

**Important privacy notes:**
- ✅ Your API keys are YOUR responsibility
- ✅ Your data stays with you (nothing uploaded)
- ✅ You control API usage and costs
- ✅ You can regenerate keys anytime
"""
    )
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🤖 Groq API Key")
        st.markdown("""
        **What it's for:** Generate sentences in your language
        **Get free key:**
        1. https://console.groq.com/keys
        2. Create account (free)
        3. Generate new API key
        4. Copy & paste below
        """)
        groq_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...", key="groq_api_key_input")
    with col2:
        st.markdown("### 🖼️ Pixabay API Key")
        st.markdown("""
        **What it's for:** Download images for each word
        **Get free key:**
        1. https://pixabay.com/api/docs/
        2. Create account (free)
        3. Find API key in dashboard
        4. Copy & paste below
        """)
        pixabay_key = st.text_input("Pixabay API Key", type="password", placeholder="53606933-...", key="pixabay_api_key_input")
    st.divider()
    groq_env = get_secret("GROQ_API_KEY", "")
    pixabay_env = get_secret("PIXABAY_API_KEY", "")
    if groq_env and pixabay_env and not groq_key:
        st.info("ℹ️ **Development Mode Detected** - Your API keys were auto-loaded from .env file")
        groq_key = groq_env
        pixabay_key = pixabay_env
    st.divider()
    if st.button("🚀 Next: Select Language", use_container_width=True):
        if not groq_key:
            st.error("❌ Please enter your Groq API key")
        elif not pixabay_key:
            st.error("❌ Please enter your Pixabay API key")
        else:
            st.session_state.groq_api_key = groq_key
            st.session_state.pixabay_api_key = pixabay_key
            # Save API keys to local file for persistence
            import json
            secrets_path = Path(__file__).parent / "user_secrets.json"
            user_secrets = {"groq_api_key": groq_key, "pixabay_api_key": pixabay_key}
            with open(secrets_path, "w", encoding="utf-8") as f:
                json.dump(user_secrets, f, indent=2)
            # Save API keys to Firebase if not guest
            if not st.session_state.get("is_guest", True):
                try:
                    from firebase_manager import save_settings_to_firebase
                    save_settings_to_firebase(st.session_state.session_id, {
                        "groq_api_key": groq_key,
                        "pixabay_api_key": pixabay_key
                    })
                except Exception as e:
                    st.warning(f"Could not save API keys to cloud: {e}")
            st.session_state.page = "language_select"
            st.session_state.scroll_to_top = True
            st.rerun()

# ============================================================================
# PAGE 2: MAIN APP
# ============================================================================

elif st.session_state.page == "language_select":
    st.markdown("# 🌍 Step 1: Select Language")
    st.info("Your favorite languages are pinned to the top for quick access. You can change their order in Settings → Favorite Languages.")
    # --- Preferred order: learned_languages at top, divider, then all others ---
    import json
    user_settings_path = Path(__file__).parent / "user_settings.json"
    if user_settings_path.exists():
        with open(user_settings_path, "r", encoding="utf-8") as f:
            per_lang_settings = json.load(f)
        default_lang = per_lang_settings.get("default_language", None)
    else:
        per_lang_settings = {}
        default_lang = None

    # Get user's learned languages (in preferred order)
    learned_langs = [l["name"] for l in st.session_state.get("learned_languages", [])]
    # All language names
    all_lang_names = [lang["name"] for lang in all_languages]
    # Languages not in learned list
    other_langs = [l for l in all_lang_names if l not in learned_langs]

    # Build options: learned (pinned) + divider + others
    options = []
    for l in learned_langs:
        options.append({"name": l, "section": "pinned"})
    if learned_langs and other_langs:
        options.append({"name": "──────────────", "section": "divider"})
    for l in other_langs:
        options.append({"name": l, "section": "other"})

    # Find default selection
    if default_lang and any(opt["name"] == default_lang for opt in options if opt["section"] != "divider"):
        default_idx = [i for i, opt in enumerate(options) if opt["name"] == default_lang][0]
    elif learned_langs:
        default_idx = 0
    else:
        default_idx = next((i for i, opt in enumerate(options) if opt["section"] != "divider"), 0)

    def format_func(opt):
        if opt["section"] == "divider":
            return opt["name"]
        elif opt["section"] == "pinned":
            # Show rank (1-based) for pinned
            rank = learned_langs.index(opt["name"]) + 1 if opt["name"] in learned_langs else ""
            return f"{rank}. {opt['name']} ★"
        else:
            return opt["name"]

    selected_opt = st.selectbox(
        "Which language do you want to learn?",
        options,
        index=default_idx,
        format_func=format_func,
        key="main_language_select"
    )
    # If divider is selected, auto-select first real language
    if selected_opt["section"] == "divider":
        # Pick first after divider, or first pinned
        next_idx = options.index(selected_opt) + 1
        if next_idx < len(options):
            selected_opt = options[next_idx]
        else:
            selected_opt = options[0]

    selected_lang = selected_opt["name"]
    available_lists = get_available_frequency_lists()
    max_words = available_lists.get(selected_lang, 5000)
    st.metric("Available", f"{max_words:,} words")
    if st.button("Next: Select Words", use_container_width=True):
        st.session_state.selected_language = selected_lang
        st.session_state.page = "word_select"
        st.session_state.scroll_to_top = True
        st.rerun()

elif st.session_state.page == "word_select":
    # Back button
    if st.button("⬅️ Back", key="back_from_word_select"):
        st.session_state.page = "language_select"
        st.rerun()
    st.markdown("---")
    st.markdown(f"# 🌍 Step 2: Select Words for {st.session_state.get('selected_language', '')}")
    if "current_page" not in st.session_state:
        st.session_state.current_page = {}
    if st.session_state.get('selected_language', None) and st.session_state.get('selected_language') not in st.session_state.current_page:
        st.session_state.current_page[st.session_state.get('selected_language')] = 1
    try:
        from frequency_utils import get_words_with_ranks
        words_df, total_words = get_words_with_ranks(st.session_state.get('selected_language', ''), page=st.session_state.current_page[st.session_state.get('selected_language', '')], page_size=25)
    except Exception as e:
        st.error(f"DEBUG: Error in get_words_with_ranks: {e}")

    # Restore main Step 2 UI logic
    selected_words = []
    uploaded_file_name = None
    custom_words = []
    if total_words > 0:
        st.markdown("### Pick from **Top Words Used in** " + st.session_state.get('selected_language', ''))
        tab_frequency, tab_custom = st.tabs(["📊 Frequency List", "📥 Import Your Own Words"])
        with tab_frequency:
            page_size = 25
            current_page = st.session_state.current_page[st.session_state.get('selected_language', '')]
            total_pages = (total_words + page_size - 1) // page_size
            st.markdown("#### Select words to include in your deck:")
            col_rank, col_word, col_select, col_status = st.columns([0.8, 1.5, 1.2, 0.8])
            with col_rank:
                st.write("**Rank**")
            with col_word:
                st.write("**Word**")
            with col_select:
                st.write("**Select**")
            with col_status:
                st.write("**Status**")
            st.divider()
            for idx, row in words_df.iterrows():
                col_rank, col_word, col_select, col_status = st.columns([0.8, 1.5, 1.2, 0.8])
                with col_rank:
                    st.write(f"#{row['Rank']}")
                with col_word:
                    st.write(row['Word'])
                with col_select:
                    is_selected = st.checkbox(
                        "Select",
                        key=f"word_select_{st.session_state.get('selected_language', '')}_{row['Word']}_{idx}",
                        label_visibility="collapsed"
                    )
                    if is_selected:
                        selected_words.append(row['Word'])
                with col_status:
                    if row['Completed']:
                        st.write("✅")
            st.divider()
            start_rank = (current_page - 1) * page_size + 1
            end_rank = min(current_page * page_size, total_words)
            st.markdown(f"**Top {start_rank}–{end_rank}** | Page {current_page} of {total_pages}")
            col_prev, col_next, col_jump = st.columns([1, 1, 2])
            with col_prev:
                if st.button("⬅️ Previous", key="prev_page"):
                    if current_page > 1:
                        st.session_state.current_page[st.session_state.get('selected_language', '')] -= 1
                        st.rerun()
            with col_next:
                if st.button("Next ➡️", key="next_page"):
                    if current_page < total_pages:
                        st.session_state.current_page[st.session_state.get('selected_language', '')] += 1
                        st.rerun()
            with col_jump:
                if total_pages > 1:
                    jump_page = st.number_input("Jump to page", min_value=1, max_value=total_pages, value=current_page, key="jump_page")
                    if jump_page != current_page:
                        st.session_state.current_page[st.session_state.get('selected_language', '')] = jump_page
                        st.rerun()
        with tab_custom:
            st.markdown("**Import your own list of words** for exams, specific topics, or custom learning needs.")
            st.divider()
            st.markdown("**Expected format:** One word per line (plain text, CSV, or XLSX)")
            uploaded_file = st.file_uploader(
                "Choose CSV or XLSX file",
                type=['csv', 'xlsx', 'xls'],
                key="custom_words_upload",
                help="First column will be used as word list"
            )
            if uploaded_file:
                uploaded_file_name = uploaded_file.name if hasattr(uploaded_file, 'name') else None
                st.info(f"Custom word import detected: {uploaded_file_name}")
                from frequency_utils import parse_uploaded_word_file, validate_word_list
                custom_words, parse_msg = parse_uploaded_word_file(uploaded_file)
                st.info(parse_msg)
                if custom_words:
                    is_valid, validation_msg = validate_word_list(custom_words)
                    st.info(validation_msg)
                    if is_valid:
                        st.markdown(f"#### Words from custom list ({len(custom_words)})")
                        col_rank, col_word, col_select = st.columns([0.8, 1.5, 1.2])
                        with col_rank:
                            st.write("**#**")
                        with col_word:
                            st.write("**Word**")
                        with col_select:
                            st.write("**Select**")
                        st.divider()
                        for custom_idx, word in enumerate(custom_words, 1):
                            col_rank, col_word, col_select = st.columns([0.8, 1.5, 1.2])
                            with col_rank:
                                st.write(f"{custom_idx}")
                            with col_word:
                                st.write(word)
                            with col_select:
                                is_selected = st.checkbox(
                                    "Select",
                                    key=f"custom_word_select_{word}_{custom_idx}",
                                    label_visibility="collapsed"
                                )
                                if is_selected:
                                    if word not in selected_words:
                                        selected_words.append(word)
    # Add navigation button
    if st.button("Next: Sentence Settings", use_container_width=True):
        st.session_state.selected_words = selected_words
        st.session_state.page = "sentence_settings"
        st.session_state.scroll_to_top = True
        st.rerun()

elif st.session_state.page == "sentence_settings":
    # Persist all settings and progress to local file (JSON)
    persist_path = Path(__file__).parent / "user_full_state.json"
    full_state = {k: v for k, v in st.session_state.items() if not k.startswith("_")}
    try:
        with open(persist_path, "w", encoding="utf-8") as f:
            import json
            json.dump(full_state, f, indent=2, default=str)
    except Exception as e:
        st.warning(f"Could not persist settings: {e}")
    st.markdown("# 🌍 Step 3: Settings")
    # --- Difficulty Settings ---
    st.markdown("## 🧠 Difficulty Settings")
    st.session_state.difficulty = st.radio(
        "Select difficulty:",
        [
            "beginner",
            "intermediate",
            "advanced"
        ],
        index=["beginner", "intermediate", "advanced"].index(st.session_state.difficulty),
        format_func=lambda x: {
            "beginner": "Beginner (Short, simple sentences and basic vocabulary)",
            "intermediate": "Intermediate (Moderately complex sentences and vocabulary)",
            "advanced": "Advanced (Long, complex sentences and advanced vocabulary)"
        }[x],
    )

    # --- Sentence Settings ---
    st.markdown("---")
    st.markdown("## ✍️ Sentence Settings")
    col_len, col_sent = st.columns(2)
    with col_len:
        st.session_state.sentence_length_range = st.slider(
            "Sentence length (words)",
            min_value=4,
            max_value=30,
            value=st.session_state.sentence_length_range,
            step=1,
            help="Min and max words per sentence."
        )
    with col_sent:
        st.session_state.sentences_per_word = st.slider(
            "Sentences per word",
            min_value=3,
            max_value=15,
            value=st.session_state.sentences_per_word,
            step=1,
            help="How many sentences to generate for each word."
        )

    # --- Audio Settings ---
    st.markdown("---")
    st.markdown("## 🎵 Audio Settings")
    col_voice, col_speed = st.columns(2)
    with col_voice:
        lang = st.session_state.selected_language
        if lang in EDGE_TTS_VOICES:
            voice_options = [f"{v[0]} ({v[1]}, {v[2]})" for v in EDGE_TTS_VOICES[lang]]
            selected_voice_idx = voice_options.index(st.session_state.selected_voice_display) if st.session_state.selected_voice_display in voice_options else 0
            selected_voice_display = st.selectbox(
                "Voice",
                options=voice_options,
                index=selected_voice_idx,
                help="Choose the voice for audio generation."
            )
            st.session_state.selected_voice_display = selected_voice_display
            st.session_state.selected_voice = EDGE_TTS_VOICES[lang][voice_options.index(selected_voice_display)][0]
        else:
            st.session_state.selected_voice_display = "en-US-AvaNeural (Female, Ava)"
            st.session_state.selected_voice = "en-US-AvaNeural"
    with col_speed:
        audio_speed = st.slider(
            "Audio Speed",
            min_value=0.5,
            max_value=1.5,
            value=st.session_state.audio_speed,
            step=0.1,
            help="0.5 = very slow, 0.8 = learner-friendly (recommended), 1.0 = normal, 1.5 = fast"
        )
        st.session_state.audio_speed = audio_speed

    # --- Summary ---
    st.markdown("---")
    st.markdown(f"**Audio:** {st.session_state.audio_speed}x, **Voice:** {st.session_state.selected_voice_display}")
    st.divider()
    # Add Back button to settings step
    if st.button("⬅️ Back", key="back_from_settings"):
        st.session_state.page = "language_select"
        st.rerun()
    if st.button("Next: Generate Deck", use_container_width=True):
        st.session_state.page = "generate"
        st.session_state.scroll_to_top = True
        st.rerun()

elif st.session_state.page == "generate":
    # Back button
    if st.button("⬅️ Back", key="back_from_generate"):
        st.session_state.page = "sentence_settings"
        st.rerun()
    st.markdown("# 🌍 Step 4: Generate & Download Deck")
    st.markdown("## ✨ Ready to Generate!")
    # Get selected words from previous step
    selected_words = st.session_state.get('selected_words', [])
    selected_lang = st.session_state.get('selected_language', '')
    st.info(f"Selected words: {len(selected_words)}")
    if st.button("Generate Deck", use_container_width=True):
        st.session_state.selected_lang = selected_lang
        st.session_state.selected_words = selected_words
        st.session_state.page = "generating"
        st.session_state.scroll_to_top = True
        st.rerun()
    if st.button("Back to Start", use_container_width=True):
        st.session_state.page = "api_setup"
        st.session_state.scroll_to_top = True
        st.rerun()

elif st.session_state.page == "help":
    # ...existing help/FAQ code...

    # Only scroll to top if requested (after button click)
    if st.session_state.get('scroll_to_top', False):
        st.markdown('<script>window.scrollTo({top: 0, behavior: "smooth"});</script>', unsafe_allow_html=True)
        st.session_state.scroll_to_top = False
    
    col1, col2, col3 = st.columns([4, 1, 1])
    with col1:
        st.markdown("# 🌍 Language Learning Anki Deck Generator")
    with col2:
        if st.button("🔐 Change Keys"):
            st.session_state.page = "api_setup"
            st.rerun()
    with col3:
        settings_pop = st.popover("⚙️ Settings", help="Adjust difficulty, sentence length, audio, and tracking", use_container_width=True)
        with settings_pop:
            st.markdown("### Global Settings")
            st.session_state.difficulty = st.radio(
                "Difficulty",
                ["beginner", "intermediate", "advanced"],
                index=["beginner", "intermediate", "advanced"].index(st.session_state.difficulty),
                help="Beginner uses shorter sentences and simpler vocab; Advanced leans into longer, more complex structures.",
            )
            st.session_state.sentence_length_range = st.slider(
                "Sentence length (words)",
                min_value=4,
                max_value=30,
                value=st.session_state.sentence_length_range,
                step=1,
                help="Min and max words per sentence",
            )
            st.session_state.sentences_per_word = st.slider(
                "Sentences per word",
                min_value=3,
                max_value=15,
                value=st.session_state.sentences_per_word,
                step=1,
                help="How many sentences to generate per word",
            )
            st.session_state.track_progress = st.checkbox(
                "Track progress (mark generated words as completed)",
                value=st.session_state.track_progress,
            )
            st.session_state.audio_speed = st.slider(
                "Audio speed",
                min_value=0.5,
                max_value=1.5,
                value=st.session_state.audio_speed,
                step=0.1,
                help="0.5 = slow, 1.0 = normal, 1.5 = fast",
            )
            st.caption("Voice and pitch are chosen in Step 3 (Audio Settings).")
    
    st.divider()
    
    # Step 1: Language
    st.markdown("## 📋 Step 1: Select Language")
    lang_names = [lang["name"] for lang in all_languages]
    col_lang, col_available = st.columns([3, 1])
    with col_lang:
        selected_lang = st.selectbox("Which language do you want to learn?", lang_names)
    
    available_lists = get_available_frequency_lists()
    max_words = available_lists.get(selected_lang, 5000)
    with col_available:
        st.metric("Available", f"{max_words:,} words")
    
    st.divider()
    
    # Step 2: Select words (batch + list combined)
    st.markdown("## 📚 Step 2: Select Your Words")
    st.markdown("**We pull from frequency lists so you start with the most useful words first.**")
    
    # Info about frequency lists - moved right after description
    with st.expander("📖 What is a Frequency List?", expanded=False):
        st.markdown("""
        A **Frequency List** contains the most commonly used words in a language, ranked by how often they appear in real conversations, books, movies, and other sources.
        
        **Why use it?**
        - Focus on words you'll actually encounter
        - Learn vocabulary efficiently (top 1,000 words = ~80% of everyday language)
        - Build a strong foundation for real communication
        
        **Example:** In Spanish, "the" (el/la) is word #1, "and" (y) is word #2, "to" (a) is word #3, etc.
        """)
    st.info("For your first run, try 1 word. After that, keep batches around 5–10 to respect rate limits.")
    
    # Initialize page tracking
    if selected_lang not in st.session_state.current_page:
        st.session_state.current_page[selected_lang] = 1
    
    # Get completed words and stats
    completed = get_completed_words(selected_lang)
    stats = get_word_stats(selected_lang)
    
    # Display stats
    col1, col2, col3 = st.columns(3)
    col1.metric("Total words", stats.get("total", 0))
    col2.metric("Completed", stats.get("completed", 0))
    col3.metric("Remaining", stats.get("remaining", 0))

    st.divider()

    # ========================================================================
    # FREQUENCY LIST SELECTION & CUSTOM IMPORT
    # ========================================================================
    
    st.markdown("### Pick from **Top Words Used in** " + selected_lang)
    
    # Create tabs: Frequency List vs Custom Import
    tab_frequency, tab_custom = st.tabs(["📊 Frequency List", "📥 Import Your Own Words"])
    
    with tab_frequency:
        # Pagination settings
        page_size = 25
        current_page = st.session_state.current_page[selected_lang]
        
        # Get words with ranks
        words_df, total_words = get_words_with_ranks(selected_lang, page=current_page, page_size=page_size)
        total_pages = (total_words + page_size - 1) // page_size
        
        # Display words in a clean table with checkboxes
        st.markdown("#### Select words to include in your deck:")
        
        # Create columns for display
        col_rank, col_word, col_select, col_status = st.columns([0.8, 1.5, 1.2, 0.8])
        
        with col_rank:
            st.write("**Rank**")
        with col_word:
            st.write("**Word**")
        with col_select:
            st.write("**Select**")
        with col_status:
            st.write("**Status**")
        
        st.divider()
        
        selected_words = []
        
        # Display each word with checkbox
        for idx, row in words_df.iterrows():
            col_rank, col_word, col_select, col_status = st.columns([0.8, 1.5, 1.2, 0.8])
            
            with col_rank:
                st.write(f"#{row['Rank']}")
            
            with col_word:
                st.write(row['Word'])
            
            with col_select:
                is_selected = st.checkbox(
                    "Select",
                    key=f"word_select_{selected_lang}_{row['Word']}_{idx}",
                    label_visibility="collapsed"
                )
                if is_selected:
                    selected_words.append(row['Word'])
            
            with col_status:
                if row['Completed']:
                    st.write("✅")
        
        st.divider()
        
        # Pagination controls (below word table)
        start_rank = (current_page - 1) * page_size + 1
        end_rank = min(current_page * page_size, total_words)
        st.markdown(f"**Top {start_rank}–{end_rank}** | Page {current_page} of {total_pages}")
        
        col_prev, col_next, col_jump = st.columns([1, 1, 2])
        
        with col_prev:
            if st.button("⬅️ Previous", key="prev_page"):
                if current_page > 1:
                    st.session_state.current_page[selected_lang] -= 1
                    st.rerun()
        
        with col_next:
            if st.button("Next ➡️", key="next_page"):
                if current_page < total_pages:
                    st.session_state.current_page[selected_lang] += 1
                    st.rerun()
        
        with col_jump:
            if total_pages > 1:
                jump_page = st.number_input("Jump to page", min_value=1, max_value=total_pages, value=current_page, key="jump_page")
                if jump_page != current_page:
                    st.session_state.current_page[selected_lang] = jump_page
                    st.rerun()
        
        # Search within frequency list
        st.divider()
        st.markdown("#### 🔍 Search for specific words:")
        search_term = st.text_input("Search", placeholder="e.g., 'water', 'love', 'cat'...", key="word_search")
        
        if search_term:
            search_results = search_words(selected_lang, search_term, limit=50)
            if search_results:
                st.markdown(f"**Found {len(search_results)} matching words:**")
                
                # Build dataframe for search results with ranks
                search_data = []
                for word in search_results:
                    # Get rank from database
                    from db_manager import get_word_rank
                    rank = get_word_rank(selected_lang, word)
                    search_data.append({
                        'Rank': rank,
                        'Word': word,
                        'Completed': '✓' if word in completed else ''
                    })
                
                search_df = pd.DataFrame(search_data)
                
                # Display search results
                col_rank, col_word, col_select, col_status = st.columns([0.8, 1.5, 1.2, 0.8])
                
                with col_rank:
                    st.write("**Rank**")
                with col_word:
                    st.write("**Word**")
                with col_select:
                    st.write("**Select**")
                with col_status:
                    st.write("**Status**")
                
                st.divider()
                
                for idx, row in search_df.iterrows():
                    col_rank, col_word, col_select, col_status = st.columns([0.8, 1.5, 1.2, 0.8])
                    
                    with col_rank:
                        st.write(f"#{row['Rank']}" if row['Rank'] else "—")
                    
                    with col_word:
                        st.write(row['Word'])
                    
                    with col_select:
                        is_selected = st.checkbox(
                            "Select",
                            key=f"word_search_select_{selected_lang}_{row['Word']}_{idx}",
                            label_visibility="collapsed"
                        )
                        if is_selected:
                            selected_words.append(row['Word'])
                    
                    with col_status:
                        if row['Completed']:
                            st.write("✅")
            else:
                st.info("No words found matching your search")
    
    # ========================================================================
    # CUSTOM WORD IMPORT TAB
    # ========================================================================
    
    with tab_custom:
        st.markdown("""
        **Import your own list of words** for exams, specific topics, or custom learning needs.
        
        **Example use cases:**
        - 🇨🇳 HSK Word Lists (Chinese proficiency test)
        - 📚 Exam prep (DELF, DELE, etc.)
        - 🎯 Domain-specific vocabulary (medical, business, etc.)
        - 📋 Custom topic lists
        """)
        
        st.divider()
        
        # Template download
        csv_template = get_csv_template()
        st.download_button(
            label="📥 Download CSV Template",
            data=csv_template,
            file_name="word_list_template.csv",
            mime="text/csv",
            help="Download and fill in with your own words"
        )
        
        st.markdown("**Expected format:** One word per line (plain text, CSV, or XLSX)")
        st.code("\n".join(csv_template.split('\n')[0:4]), language="text")
        
        st.divider()
        
        # File uploader
        st.markdown("**Upload your word list:**")
        uploaded_file = st.file_uploader(
            "Choose CSV or XLSX file",
            type=['csv', 'xlsx', 'xls'],
            key="custom_words_upload",
            help="First column will be used as word list"
        )
        
        if uploaded_file:
            custom_words, parse_msg = parse_uploaded_word_file(uploaded_file)
            st.info(parse_msg)
            
            if custom_words:
                is_valid, validation_msg = validate_word_list(custom_words)
                st.info(validation_msg)
                
                if is_valid:
                    st.markdown(f"#### Words from custom list ({len(custom_words)})")
                    
                    # Display custom words with selection
                    col_rank, col_word, col_select = st.columns([0.8, 1.5, 1.2])
                    
                    with col_rank:
                        st.write("**#**")
                    with col_word:
                        st.write("**Word**")
                    with col_select:
                        st.write("**Select**")
                    
                    st.divider()
                    
                    for custom_idx, word in enumerate(custom_words, 1):
                        col_rank, col_word, col_select = st.columns([0.8, 1.5, 1.2])
                        
                        with col_rank:
                            st.write(f"{custom_idx}")
                        
                        with col_word:
                            st.write(word)
                        
                        with col_select:
                            is_selected = st.checkbox(
                                "Select",
                                key=f"custom_word_select_{word}_{custom_idx}",
                                label_visibility="collapsed"
                            )
                            if is_selected:
                                if word not in selected_words:
                                    selected_words.append(word)
    
    # ========================================================================
    # SELECTION SUMMARY
    # ========================================================================
    
    st.divider()

    if selected_words:
        est_sentences = len(selected_words) * st.session_state.sentences_per_word
        st.markdown("### ⏱️ Rate Limit Monitor")
        st.caption("Stay under ~10 words per run unless you know your rate limits.*")
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Selected words", len(selected_words))
        with col_b:
            st.metric("Est. API calls", f"{est_sentences} sentences / {est_sentences} images")
        if not st.session_state.first_run_complete and len(selected_words) > 1:
            st.warning("First run? Stick to 1 word to verify keys and audio.")
        elif len(selected_words) > 10:
            st.warning("That’s a big batch. Consider 5–10 words to avoid rate limits/timeouts.")
    
    if selected_words:
        st.success(f"✅ Selected: **{len(selected_words)} words**")
        with st.expander("View selected words"):
            st.write(", ".join(selected_words))
    else:
        st.info("📝 Select words from the frequency list or import your own")
    
    st.divider()
    
    # Step 3: Audio Settings
    st.markdown("## ⚙️ Step 3: Audio Settings")
    
    col_speed, col_voice = st.columns(2)
    
    with col_speed:
        audio_speed = st.slider(
            "🎵 Audio Speed",
            min_value=0.5,
            max_value=1.5,
            value=st.session_state.audio_speed,
            step=0.1,
            help="0.5 = very slow, 0.8 = learner-friendly (recommended), 1.0 = normal, 1.5 = fast"
        )
        st.session_state.audio_speed = audio_speed

    # Pitch UI removed
    
    with col_voice:
        # Get available voices for the language
        voice_options = {
            "Spanish": ["es-ES-ElviraNeural (Female)", "es-ES-AlvaroNeural (Male)", "es-MX-DaliaNeural (Female MX)"],
            "French": ["fr-FR-DeniseNeural (Female)", "fr-FR-HenriNeural (Male)"],
            "German": ["de-DE-KatjaNeural (Female)", "de-DE-ConradNeural (Male)"],
            "Italian": ["it-IT-IsabellaNeural (Female)", "it-IT-DiegoNeural (Male)"],
            "Portuguese": ["pt-BR-FranciscaNeural (Female)", "pt-BR-AntonioNeural (Male)"],
            "Russian": ["ru-RU-SvetlanaNeural (Female)", "ru-RU-DmitryNeural (Male)"],
            "Japanese": ["ja-JP-NanamiNeural (Female)", "ja-JP-KeitaNeural (Male)"],
            "Korean": ["ko-KR-SoonBokNeural (Female)", "ko-KR-InJoonNeural (Male)"],
            "Chinese (Simplified)": ["zh-CN-XiaoxiaoNeural (Female)", "zh-CN-YunxiNeural (Male)"],
            "Mandarin Chinese": ["zh-CN-XiaoxiaoNeural (Female)", "zh-CN-YunxiNeural (Male)"],
            "Arabic": ["ar-SA-LeenNeural (Female)", "ar-SA-HamedNeural (Male)"],
            "Hindi": ["hi-IN-SwaraNeural (Female)", "hi-IN-MadhurNeural (Male)"],
            "English": ["en-US-AvaNeural (Female)", "en-US-AndrewNeural (Male)", "en-GB-SoniaNeural (Female UK)"],
        }
        
        available_voices = voice_options.get(selected_lang, ["Auto-detect"])
        default_voice_display = st.session_state.selected_voice_display
        if default_voice_display and default_voice_display not in available_voices:
            default_voice_display = available_voices[0]

        selected_voice_display = st.selectbox(
            "🎤 Voice",
            options=available_voices,
            index=available_voices.index(default_voice_display) if default_voice_display in available_voices else 0,
            help="Select the voice for audio generation"
        )
        
        # Extract actual voice code from display name
        selected_voice = selected_voice_display.split(" (")[0] if "(" in selected_voice_display else None
        st.session_state.selected_voice_display = selected_voice_display
        st.session_state.selected_voice = selected_voice

    st.caption(
        f"Difficulty: **{st.session_state.difficulty}**, Sentences/word: **{st.session_state.sentences_per_word}**, "
        f"Length: **{st.session_state.sentence_length_range[0]}-{st.session_state.sentence_length_range[1]} words**, "
        f"Audio: **{st.session_state.audio_speed}x**, "
        f"Tracking: {'On' if st.session_state.track_progress else 'Off'}"
    )
    
    st.divider()
    
    # Step 4: Generate
    st.markdown("## ✨ Step 4: Generate Your Deck")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.button(
            f"🚀 Generate Deck ({len(selected_words)} words)",
            use_container_width=True,
            disabled=len(selected_words) == 0
        ):
            # Show API estimates
            st.info(f"""
            📊 **API Usage Estimate:**
            - **Groq API calls:** ~{len(selected_words)} (1 per word for sentences)
            - **Pixabay API calls:** ~{len(selected_words) * st.session_state.sentences_per_word} (1 per sentence)
            - **Total images:** {len(selected_words) * st.session_state.sentences_per_word}
            
            Generation will begin in a moment...
            """)
            st.info("Scroll down to see the progress log.")
            st.session_state.page = "generating"
            st.session_state.selected_lang = selected_lang
            st.session_state.selected_words = selected_words
            st.session_state.scroll_to_top = True
            st.rerun()
    
    with col2:
        if st.button("ℹ️ Help", use_container_width=True):
            st.session_state.page = "help"
            st.rerun()

# ============================================================================
# PAGE 3: GENERATING
# ============================================================================

elif st.session_state.page == "generating":

    # Force scroll to top when entering generating page
    st.markdown('<script>window.scrollTo({top: 0, behavior: "smooth"});</script>', unsafe_allow_html=True)
    
    st.markdown("# ⚙️ Generating Your Deck")
    st.markdown(f"**Language:** {st.session_state.selected_lang} | **Words:** {len(st.session_state.selected_words)}")
    st.divider()

    # --- NEW: Stepwise, live-updating generation logic ---
    progress_container = st.container()
    with progress_container:
        progress_bar = st.progress(0)
        status_text = st.empty()
        detail_text = st.empty()
        messages_container = st.container()

    # Initialize or resume stepwise generation state
    if 'generation_progress' not in st.session_state:
        st.session_state['generation_progress'] = {
            'step': 0,
            'words_data': [],
            'audio_files': [],
            'image_files': [],
            'error': None,
            'apkg_ready': False,
            'apkg_path': None,
            'media_dir': None,
            'tsv_path': None,
        }
        st.session_state['generation_log'] = []
        st.session_state['generation_log_active'] = True

    # Helper to log and update UI
    def log_message(msg):
        st.session_state['generation_log'].append(msg)
        with messages_container:
            st.markdown('<div style="background:#23272e;color:#f3f6fa;font-family:monospace,monospace;font-size:16px;padding:10px 14px;max-height:300px;overflow-y:auto;border-radius:8px;border:1px solid #30363d;">'+"<br>".join(st.session_state['generation_log'])+"</div>", unsafe_allow_html=True)

    # Stepwise generation logic (scaffold)
    # 0: Not started, 1: Generating per word, 2: Exporting, 3: Done
    step = st.session_state['generation_progress']['step']
    selected_words = st.session_state.selected_words
    selected_lang = st.session_state.selected_lang
    groq_api_key = st.session_state.get('groq_api_key', get_secret('GROQ_API_KEY', ''))
    pixabay_api_key = st.session_state.get('pixabay_api_key', get_secret('PIXABAY_API_KEY', ''))
    num_sentences = st.session_state.sentences_per_word
    min_length, max_length = st.session_state.sentence_length_range
    difficulty = st.session_state.difficulty
    audio_speed = st.session_state.audio_speed
    voice = st.session_state.selected_voice
    output_dir = str(Path("./output"))


    # Stepwise generation logic
    progress = st.session_state['generation_progress']
    word_idx = progress.get('word_idx', 0)
    substep = progress.get('substep', 0)  # 0: meaning, 1: sentences, 2: audio, 3: images, 4: tsv/export
    words_data = progress['words_data']
    audio_files = progress['audio_files']
    image_files = progress['image_files']
    error = progress['error']
    apkg_ready = progress['apkg_ready']
    apkg_path = progress['apkg_path']
    media_dir = progress['media_dir']
    tsv_path = progress['tsv_path']

    total_words = len(selected_words)
    # Progress bar: (word_idx + substep/5) / total_words
    progress_bar.progress(min((word_idx + substep/5) / max(1, total_words), 1.0))

    # If error, show and stop
    if error:
        status_text.error("❌ Error during generation")
        detail_text.write(error)
        log_message(f"<b>❌ ERROR:</b> {error}")
        st.session_state['generation_log_active'] = False
        if st.button("← Back to Main"):
            st.session_state.page = "main"
            st.rerun()
        st.stop()

    # If done, move to export step
    if word_idx >= total_words:
        # TODO: Export logic (TSV, APKG, etc.)
        log_message("<b>✅ All words processed. Exporting deck...</b>")
        status_text.success("All words processed. Exporting deck...")
        # (Export logic will be added in next step)
        # For now, mark as done and move to complete page
        st.session_state['generation_log_active'] = False
        st.session_state.page = "complete"
        st.rerun()

    # Stepwise per-word logic
    word = selected_words[word_idx]
    if substep == 0:
        # Generate meaning
        log_message(f"<b>Step 1/5</b> Generating meaning for '<b>{word}</b>'...")
        status_text.info(f"Generating meaning for '{word}'...")
        try:
            from core_functions import generate_word_meaning
            meaning = generate_word_meaning(word, selected_lang, groq_api_key)
            # Store in progress
            progress['current_word'] = {'word': word, 'meaning': meaning}
            progress['substep'] = 1
            st.session_state['generation_progress'] = progress
            st.rerun()
        except Exception as e:
            progress['error'] = f"Error generating meaning for '{word}': {e}"
            st.session_state['generation_progress'] = progress
            st.rerun()
    elif substep == 1:
        # Generate sentences
        log_message(f"<b>Step 2/5</b> Generating sentences for '<b>{word}</b>'...")
        status_text.info(f"Generating sentences for '{word}'...")
        try:
            from core_functions import generate_sentences
            meaning = progress['current_word']['meaning']
            sentences = generate_sentences(word, meaning, selected_lang, num_sentences, min_length, max_length, difficulty, groq_api_key)
            progress['current_word']['sentences'] = sentences
            progress['substep'] = 2
            st.session_state['generation_progress'] = progress
            st.rerun()
        except Exception as e:
            progress['error'] = f"Error generating sentences for '{word}': {e}"
            st.session_state['generation_progress'] = progress
            st.rerun()
    elif substep == 2:
        # Generate audio
        log_message(f"<b>Step 3/5</b> Generating audio for '<b>{word}</b>'...")
        status_text.info(f"Generating audio for '{word}'...")
        try:
            from core_functions import generate_audio, _sanitize_word
            sentences = progress['current_word']['sentences']
            # Extract only the sentence text if sentences are dicts
            sentence_texts = [s["sentence"] if isinstance(s, dict) and "sentence" in s else str(s) for s in sentences]
            # Prepare output dir and filenames
            audio_output_dir = str(Path(output_dir) / "audio" / _sanitize_word(word))
            os.makedirs(audio_output_dir, exist_ok=True)
            audio_filenames = [f"{_sanitize_word(word)}_{i+1:02d}.mp3" for i in range(len(sentence_texts))]
            generated_files = generate_audio(
                sentences=sentence_texts,
                voice=voice,
                output_dir=audio_output_dir,
                batch_name=_sanitize_word(word),
                rate=audio_speed,
                exact_filenames=audio_filenames,
                language=selected_lang
            )
            # Store audio file paths in current_word
            progress['current_word']['audio_files'] = [str(Path(audio_output_dir) / fname) for fname in generated_files]
            progress['substep'] = 3
            st.session_state['generation_progress'] = progress
            st.rerun()
        except Exception as e:
            progress['error'] = f"Error generating audio for '{word}': {e}"
            st.session_state['generation_progress'] = progress
            st.rerun()
    elif substep == 3:
        # Download images
        log_message(f"<b>Step 4/5</b> Downloading images for '<b>{word}</b>'...")
        status_text.info(f"Downloading images for '{word}'...")
        try:
            from core_functions import generate_images_pixabay, _sanitize_word
            sentences = progress['current_word']['sentences']
            image_output_dir = str(Path(output_dir) / "images" / _sanitize_word(word))
            os.makedirs(image_output_dir, exist_ok=True)
            image_filenames = [f"{_sanitize_word(word)}_{i+1:02d}.jpg" for i in range(len(sentences))]
            # Use each sentence as a query for image search
            generated_images = generate_images_pixabay(
                queries=sentences,
                output_dir=image_output_dir,
                batch_name=_sanitize_word(word),
                num_images=1,
                pixabay_api_key=pixabay_api_key,
                randomize=True,
                exact_filenames=image_filenames
            )
            progress['current_word']['image_files'] = [str(Path(image_output_dir) / fname) for fname in generated_images]
            progress['substep'] = 4
            st.session_state['generation_progress'] = progress
            st.rerun()
        except Exception as e:
            progress['error'] = f"Error downloading images for '{word}': {e}"
            st.session_state['generation_progress'] = progress
            st.rerun()
    elif substep == 4:
        # Export TSV and APKG
        log_message(f"<b>Step 5/5</b> Exporting deck for '<b>{word}</b>'...")
        status_text.info(f"Exporting deck for '{word}'...")
        try:
            from core_functions import create_apkg_export, _sanitize_word
            # Collect all data for this word
            if 'words_data' not in progress or not isinstance(progress['words_data'], list):
                progress['words_data'] = []
            # Assemble card dicts for each sentence
            current = progress['current_word']
            sentences = current.get('sentences', [])
            audio_files = current.get('audio_files', [])
            image_files = current.get('image_files', [])
            for i, s in enumerate(sentences):
                # s may be dict or str
                if isinstance(s, dict):
                    sentence = s.get('sentence', str(s))
                    english = s.get('english_translation', '')
                    ipa = s.get('ipa', '')
                    image_keywords = s.get('image_keywords', '')
                else:
                    sentence = str(s)
                    english = ''
                    ipa = ''
                    image_keywords = ''
                audio = f"[sound:{os.path.basename(audio_files[i])}]" if i < len(audio_files) and audio_files[i] else ''
                image = f'<img src="{os.path.basename(image_files[i])}">' if i < len(image_files) and image_files[i] else ''
                card = {
                    'file_name': f"{current['word']}_{i+1:02d}",
                    'word': current['word'],
                    'meaning': current.get('meaning', ''),
                    'sentence': sentence,
                    'english': english,
                    'ipa': ipa,
                    'audio': audio,
                    'image': image,
                    'image_keywords': image_keywords,
                    'tags': '',
                }
                progress['words_data'].append(card)
            # If last word, export deck
            if word_idx + 1 >= total_words:
                # Prepare export paths
                export_dir = str(Path(output_dir) / "export")
                os.makedirs(export_dir, exist_ok=True)
                apkg_filename = f"{_sanitize_word(selected_lang)}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.apkg"
                apkg_path = str(Path(export_dir) / apkg_filename)
                # Use all words_data for export
                rows = progress['words_data']
                # Media dir: use output_dir (audio/images are inside)
                media_dir = str(Path(output_dir))
                # Export APKG
                success = create_apkg_export(
                    rows=rows,
                    media_dir=media_dir,
                    output_apkg=apkg_path,
                    language=selected_lang,
                    deck_name=f"{selected_lang} Deck"
                )
                if not success:
                    raise Exception("APKG export failed")
                progress['apkg_ready'] = True
                progress['apkg_path'] = apkg_path
                st.session_state['apkg_file'] = open(apkg_path, "rb").read()
                st.session_state['apkg_filename'] = apkg_filename
                log_message(f"<b>✅ Deck exported: {apkg_filename}</b>")
                status_text.success(f"Deck exported: {apkg_filename}")
                st.session_state['generation_log_active'] = False
                st.session_state.page = "complete"
                st.rerun()
            else:
                # Move to next word
                progress['word_idx'] = word_idx + 1
                progress['substep'] = 0
                st.session_state['generation_progress'] = progress
                st.rerun()
        except Exception as e:
            progress['error'] = f"Error exporting deck for '{word}': {e}"
            st.session_state['generation_progress'] = progress
            st.rerun()

# ============================================================================
# PAGE 4: COMPLETE
# ============================================================================

elif st.session_state.page == "complete":
    
    st.markdown("# ✅ Your Anki Deck is Ready!")
    total_cards = len(st.session_state.selected_words) * 3  # 3 cards per word
    st.markdown(f"**{len(st.session_state.selected_words)} words** • **{total_cards} cards** (3 learning modes per word) • **Ready to import!**")
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📥 Download Your Deck")
        st.markdown("""
        Your .apkg file includes:
        - ✅ All flashcards with 3 card types each
        - ✅ Audio files (embedded)
        - ✅ Images (embedded)
        - ✅ IPA transcriptions
        - ✅ Image search keywords
        
        **3 Card Types:**
        1. 🎧 **Listening**: Hear → Understand
        2. 💬 **Production**: English → Speak target language
        3. 📖 **Reading**: Read → Comprehend
        """)
        
        if "apkg_file" in st.session_state and st.session_state.apkg_file:
            st.download_button(
                label="⬇️ Download Anki Deck (.apkg)",
                data=st.session_state.apkg_file,
                file_name=st.session_state.get("apkg_filename", f"{st.session_state.selected_lang.replace(' ', '_')}_deck.apkg"),
                mime="application/octet-stream",
                use_container_width=True
            )
    
    with col2:
        st.markdown("### 📖 How to Import")
        st.markdown(f"""
        **Super Easy! Just 2 steps:**
        
        1. **Double-click** the downloaded .apkg file
        2. Anki opens and imports automatically! ✨
        
        **Or manually:**
        1. Open Anki
        2. File → Import...
        3. Select the .apkg file
        4. Click Import
        
        **All done!** Your {st.session_state.selected_lang} deck with {total_cards} cards is ready to study.
        
        Cards include audio, images, and phonetic guides (IPA) for pronunciation.
        """)
    
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 Generate Another", use_container_width=True):
            # Only reset state relevant to generation, not the whole session
            for key in ["selected_words", "selected_lang", "apkg_file", "apkg_filename"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.page = "language_select"
            st.rerun()
    with col2:
        if st.button("🔐 Change Keys", use_container_width=True):
            st.session_state.page = "api_setup"
            st.rerun()
    with col3:
        if st.button("ℹ️ Help", use_container_width=True):
            st.session_state.page = "help"
            st.rerun()

# ============================================================================
# PAGE 5: UPLOAD CSV
# ============================================================================

elif st.session_state.page == "upload":
    
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("# 📥 Upload Your Own Words")
    with col2:
        if st.button("← Back"):
            st.session_state.page = "main"
            st.rerun()
    
    st.divider()
    
    csv_template = get_csv_template()
    st.download_button(
        label="📋 Download CSV Template",
        data=csv_template,
        file_name="word_list_template.csv",
        mime="text/csv",
        use_container_width=True
    )
    
    st.divider()
    
    uploaded_file = st.file_uploader("Choose CSV or XLSX file", type=["csv", "xlsx"])
    
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
                col1.metric("Words", len(words))
                col2.metric("Ready", "✅")
                
                st.divider()
                
                if st.button("🚀 Generate from Custom Words", use_container_width=True):
                    st.session_state.selected_lang = "Custom"
                    st.session_state.selected_words = words
                    st.session_state.page = "generating"
                    st.rerun()
            else:
                st.error(message)
        
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# ============================================================================
# PAGE 6: HELP
# ============================================================================

elif st.session_state.page == "help":
    
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("# ℹ️ Help & FAQ")
    with col2:
        if st.button("← Back"):
            st.session_state.page = "main"
            st.markdown("""
    ## What does this app do?

    - Creates custom Anki decks for language learning:
        - Select words from frequency lists
        - Generate natural sentences (Groq AI)
        - Create native audio at 0.8x speed (learner-friendly)
        - Download relevant images (Pixabay)
        - Export ready-to-import Anki files

    ## Cost?
    - 100% FREE for personal use
        - Groq: Free tier (AI sentences)
        - Pixabay: Free tier (5,000 images/day)

    ## How long does it take?
    - 5 words: 5–10 min
    - 10 words: 10–15 min
    - 20 words: 20–30 min

    ## Privacy
    - Your data and API keys stay on your device
    - Nothing is stored or sent to external servers

    ## Troubleshooting
    - Double-check API keys
    - Ensure internet connection
    - Start with 3–5 words to test
    - Refresh the page and try again if errors occur
            """)
    # End of Help & FAQ section


# =============================
# API USAGE TRACKING COUNTERS
# =============================
if "groq_api_calls" not in st.session_state:
    st.session_state.groq_api_calls = 0
if "groq_tokens_used" not in st.session_state:
    st.session_state.groq_tokens_used = 0
if "pixabay_api_calls" not in st.session_state:
    st.session_state.pixabay_api_calls = 0

# Reset API usage counters when starting a new deck generation session
if st.session_state.page == "language_select":
    st.session_state.groq_api_calls = 0
    st.session_state.groq_tokens_used = 0
    st.session_state.pixabay_api_calls = 0
