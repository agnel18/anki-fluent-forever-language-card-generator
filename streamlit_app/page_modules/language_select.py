# pages/language_select.py - Language selection page for the language learning app

import streamlit as st
import json
from pathlib import Path
from frequency_utils import get_available_frequency_lists


def load_per_language_settings(selected_lang):
    """Load per-language settings for the selected language."""
    if "per_language_settings" in st.session_state:
        lang_settings = st.session_state.per_language_settings.get(selected_lang, {})
        if lang_settings:
            # Apply the per-language settings to session state
            if "difficulty" in lang_settings:
                st.session_state.difficulty = lang_settings["difficulty"]
            if "sentence_length_range" in lang_settings:
                st.session_state.sentence_length_range = lang_settings["sentence_length_range"]
            if "sentences_per_word" in lang_settings:
                st.session_state.sentences_per_word = lang_settings["sentences_per_word"]
            if "audio_speed" in lang_settings:
                st.session_state.audio_speed = lang_settings["audio_speed"]
            return True
    return False


def render_language_select_page():
    """Render the language selection page."""
    with st.container():
        st.markdown("# 🌍 Step 1: Select Your Language")
        st.markdown("Choose your target language for learning. Your favorite languages appear first.")
        
        # Progress indicator
        st.markdown("**Progress:** Step 1 of 5")
        st.progress(0.2)

        st.markdown("---")

        st.info("💡 **Tip:** Your favorite languages are pinned to the top for quick access. You can change their order in Settings → Favorite Languages.")

    # Get languages configuration from session state
    all_languages = st.session_state.get("all_languages", [])

    # --- Preferred order: learned_languages at top, divider, then all others ---
    user_settings_path = Path(__file__).parent.parent / "user_settings.json"
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

    # Enhanced language selection - more prominent
    with st.container():
        st.markdown("### 🎯 **Which language do you want to learn?**")
        st.markdown("*Choose your target language from the dropdown below*")

        # Make the selectbox more prominent with larger styling
        st.markdown("""
        <style>
        .language-select-container {
            background: var(--gradient-primary);
            padding: 25px;
            border-radius: 20px;
            margin: 25px 0;
            box-shadow: var(--box-shadow);
        }
        .language-select-label {
            color: white;
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 20px;
        }
        </style>
        """, unsafe_allow_html=True)

        with st.container():
            # Prominent header above dropdown
            st.markdown("### 🌍 Select Your Language")
            # Large, prominent selectbox (label removed)
            selected_opt = st.selectbox(
                "Language Selection",
                options,
                index=default_idx,
                format_func=format_func,
                key="main_language_select",
                help="Choose the language you want to create Anki decks for",
                label_visibility="hidden"
            )

            # Add visual feedback for selection
            if selected_opt["section"] != "divider":
                st.success(f"🎉 **{selected_opt['name']}** selected! Ready to continue.")
    # If divider is selected, auto-select first real language
    if selected_opt["section"] == "divider":
        # Pick first after divider, or first pinned
        next_idx = options.index(selected_opt) + 1
        if next_idx < len(options):
            selected_opt = options[next_idx]
        else:
            selected_opt = options[0]

    selected_lang = selected_opt["name"]
    
    # Load per-language settings for the selected language
    settings_loaded = load_per_language_settings(selected_lang)
    if settings_loaded:
        st.info(f"✅ Loaded custom settings for {selected_lang}")
    
    available_lists = get_available_frequency_lists()
    max_words = available_lists.get(selected_lang, 5000)

    # Show language stats in a nice metric layout
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Available Words", f"{max_words:,}")
    with col2:
        st.metric("Your Favorites", len(learned_langs))
    with col3:
        st.metric("Total Languages", len(all_languages))

    st.markdown("---")

    # Navigation buttons and progress in single row
    with st.container():
        col_back, col_progress, col_next = st.columns([1, 2, 1])
        with col_back:
            if st.button("← Back to Main", key="lang_back"):
                st.session_state.page = "main"
                st.rerun()
        with col_progress:
            st.markdown("<div style='text-align: center;'><small>Step 1 of 5: Language Selection</small></div>", unsafe_allow_html=True)
        with col_next:
            if st.button("Next: Select Words →", use_container_width=True, type="primary"):
                # Load per-language settings before proceeding
                load_per_language_settings(selected_lang)
                st.session_state.selected_language = selected_lang
                st.session_state.page = "word_select"
                st.rerun()

    # Scroll to top after all content is rendered
    st.markdown("""
    <script>
        setTimeout(function() {
            window.scrollTo({top: 0, behavior: 'smooth'});
        }, 1000);
    </script>
    """, unsafe_allow_html=True)