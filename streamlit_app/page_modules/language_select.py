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

    # === Two stacked dropdowns: Favorites (if any) + All Languages ===
    # Last-changed wins via on_change callbacks tracking which dropdown was touched.
    PLACEHOLDER_FAV = "— pick a favorite —"
    PLACEHOLDER_ALL = "— pick a language —"

    def _set_source_favorites():
        st.session_state.lang_source = "favorites"

    def _set_source_all():
        st.session_state.lang_source = "all"

    favorite_pick = None
    if favorite_langs:
        favorite_pick = st.selectbox(
            "⭐ Favorites",
            options=[PLACEHOLDER_FAV] + favorite_langs,
            key="lang_favorites_select",
            on_change=_set_source_favorites,
        )

    other_pick = st.selectbox(
        "🌍 All Languages",
        options=[PLACEHOLDER_ALL] + all_lang_names,
        key="lang_all_select",
        on_change=_set_source_all,
    )

    # Resolve which dropdown's selection is authoritative
    fav_picked = favorite_pick and favorite_pick != PLACEHOLDER_FAV
    all_picked = other_pick and other_pick != PLACEHOLDER_ALL
    source = st.session_state.get("lang_source")

    if source == "favorites" and fav_picked:
        selected_lang = favorite_pick
    elif source == "all" and all_picked:
        selected_lang = other_pick
    elif fav_picked:
        selected_lang = favorite_pick
    elif all_picked:
        selected_lang = other_pick
    else:
        # Nothing picked yet — default to first favorite, else first language, else nothing
        selected_lang = (
            favorite_langs[0] if favorite_langs
            else (all_lang_names[0] if all_lang_names else None)
        )

    if not selected_lang:
        st.warning("No languages available. Check your language configuration.")
        return

    if selected_lang in favorite_langs:
        st.success(f"⭐ **{selected_lang}** selected — one of your favorites!")
    else:
        st.info(f"🎉 **{selected_lang}** selected!")
    
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