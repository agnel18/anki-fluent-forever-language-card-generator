# pages/language_select.py - Language selection page for the language learning app

import streamlit as st
from frequency_utils import get_available_frequency_lists
from streamlit_app.user_settings_io import load_user_settings


def load_per_language_settings(selected_lang):
    """Load per-language default settings (now fully restored)."""
    if "per_language_settings" in st.session_state:
        lang_settings = st.session_state.per_language_settings.get(selected_lang, {})
        if lang_settings:
            if "sentence_length_range" in lang_settings:
                st.session_state.sentence_length_range = tuple(lang_settings["sentence_length_range"])
            if "sentences_per_word" in lang_settings:
                st.session_state.sentences_per_word = lang_settings["sentences_per_word"]
            if "difficulty" in lang_settings:
                st.session_state.difficulty = lang_settings["difficulty"]
            if "audio_speed" in lang_settings:
                st.session_state.audio_speed = lang_settings["audio_speed"]
            if "selected_voice" in lang_settings:
                st.session_state.selected_voice = lang_settings["selected_voice"]
            if "selected_voice_display" in lang_settings:
                st.session_state.selected_voice_display = lang_settings["selected_voice_display"]
            st.info(f"✅ Loaded default settings for **{selected_lang}**")
            return True
    return False


def render_language_select_page():
    """Render the language selection page — Step 1 with Favorites section."""
    st.markdown("# 🌍 Step 1: Select Your Language")
    st.caption("Choose your target language. Your favorites are pinned to the top — change their order in Settings.")
    st.progress(0.2)
    st.markdown("---")

    # Get languages configuration from session state
    all_languages = st.session_state.get("all_languages", [])

    # === Load favorites from unified user_settings.json (via shared helper) ===
    favorites_order, _ = load_user_settings()

    # Get user's learned languages (kept as fallback)
    learned_langs = [l["name"] for l in st.session_state.get("learned_languages", [])]

    # All language names
    all_lang_names = [lang["name"] for lang in all_languages]

    # Prioritize: Favorites first → learned languages → others
    favorite_langs = [f for f in favorites_order if f in all_lang_names]
    other_langs = [l for l in all_lang_names if l not in favorite_langs]

    # Build options: Favorites + divider + others
    options = []
    if favorite_langs:
        options.append({"name": "⭐ FAVORITES", "section": "header"})
        for lang in favorite_langs:
            options.append({"name": lang, "section": "favorite"})
    
    if favorite_langs and other_langs:
        options.append({"name": "──────────────", "section": "divider"})
    
    for lang in other_langs:
        options.append({"name": lang, "section": "other"})

    # Default selection (first favorite if available)
    default_idx = 0
    if favorite_langs:
        default_idx = 1  # skip header
    elif options:
        default_idx = next((i for i, opt in enumerate(options) if opt["section"] != "divider"), 0)

    def format_func(opt):
        if opt["section"] == "header":
            return opt["name"]
        elif opt["section"] == "favorite":
            return f"⭐ {opt['name']}"
        elif opt["section"] == "divider":
            return opt["name"]
        else:
            return opt["name"]

    # Language selection
    with st.container():
        # Prominent selectbox
        selected_opt = st.selectbox(
            "Language Selection",
            options,
            index=default_idx,
            format_func=format_func,
            key="main_language_select",
            help="Your favorite languages appear first with a star ⭐",
            label_visibility="hidden"
        )

        # Visual feedback (skip non-selectable section labels)
        if selected_opt["section"] not in ("divider", "header"):
            if selected_opt["section"] == "favorite":
                st.success(f"⭐ **{selected_opt['name']}** selected — one of your favorites!")
            else:
                st.info(f"🎉 **{selected_opt['name']}** selected!")

    # If a non-selectable label (header or divider) is picked, jump to the next real language
    if selected_opt["section"] in ("divider", "header"):
        next_idx = options.index(selected_opt) + 1
        # Skip past any consecutive non-selectable labels
        while next_idx < len(options) and options[next_idx]["section"] in ("divider", "header"):
            next_idx += 1
        if next_idx < len(options):
            selected_opt = options[next_idx]
        else:
            # Fall back to the first real language
            selected_opt = next(
                (o for o in options if o["section"] not in ("divider", "header")),
                options[0],
            )

    selected_lang = selected_opt["name"]
    
    # Load per-language settings for the selected language (unchanged)
    settings_loaded = load_per_language_settings(selected_lang)
    if settings_loaded:
        st.info(f"✅ Loaded custom settings for {selected_lang}")
    
    available_lists = get_available_frequency_lists()
    max_words = available_lists.get(selected_lang, 5000)

    # Show language stats in a nice metric layout (unchanged)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Available Words", f"{max_words:,}")
    with col2:
        st.metric("Your Favorites", len(favorite_langs))
    with col3:
        st.metric("Total Languages", len(all_languages))

    st.markdown("---")

    # Navigation buttons and progress (unchanged)
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
                # Clear words from a prior language so they don't leak into the new flow
                if st.session_state.get("selected_language") != selected_lang:
                    st.session_state.selected_words = []
                    st.session_state.pop("selected_word", None)
                load_per_language_settings(selected_lang)
                st.session_state.selected_language = selected_lang
                st.session_state.page = "word_select"
                st.rerun()

    # Scroll to top after all content is rendered (unchanged)
    st.markdown("""
    <script>
        setTimeout(function() {
            window.scrollTo({top: 0, behavior: 'smooth'});
        }, 1000);
    </script>
    """, unsafe_allow_html=True)