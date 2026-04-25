# pages/settings.py - Settings page for the language learning app
#
# Structure:
#   1. Back button + unified save/export/import (above tabs)
#   2. Three tabs: Preferences, Language Defaults, Favorites
#
# API key configuration lives in Step 0 (api_setup) — Settings only offers
# a shortcut button + the export/import backup block.

import json
import streamlit as st
from streamlit_sortables import sort_items

from constants import PAGE_API_SETUP
from streamlit_app.user_settings_io import (
    load_user_settings,
    save_user_settings,
    settings_payload_json,
)
from streamlit_app.api_keys_ui import render_api_key_backup_section


def _save_user_settings(favorites_order: list, per_language_settings: dict) -> bool:
    """Wrapper that surfaces an error toast on failure."""
    ok = save_user_settings(favorites_order, per_language_settings)
    if not ok:
        st.error("Failed to save user_settings.json")
    return ok


def _render_unified_save_restore() -> None:
    """The single canonical save/export/import bar that lives above the tabs."""
    st.markdown("### 💾 Save & Restore All Your Settings")
    st.caption("Favorites + per-language defaults are saved together in one file (user_settings.json)")

    col_save_export, col_import = st.columns([2, 1])

    with col_save_export:
        if st.button("💾 Save & Export All Settings", type="primary", use_container_width=True):
            favorites_order = st.session_state.get("favorites_order", [])
            per_lang = st.session_state.get("per_language_settings", {})
            if _save_user_settings(favorites_order, per_lang):
                st.download_button(
                    label="📤 Download user_settings.json",
                    data=settings_payload_json(favorites_order, per_lang),
                    file_name="user_settings.json",
                    mime="application/json",
                    key="unified_export"
                )
                st.success("✅ All settings saved and ready to download!")

    with col_import:
        if not st.session_state.get("show_settings_import"):
            if st.button("📥 Import All Settings", use_container_width=True, key="open_settings_import"):
                st.session_state.show_settings_import = True
                st.rerun()
        else:
            uploaded = st.file_uploader(
                "Choose user_settings.json",
                type=["json"],
                key="full_import",
                label_visibility="collapsed",
            )
            if uploaded:
                try:
                    imported = json.load(uploaded)
                    st.session_state.favorites_order = imported.get("favorites_order", [])
                    st.session_state.per_language_settings = imported.get("per_language_settings", {})
                    _save_user_settings(st.session_state.favorites_order, st.session_state.per_language_settings)
                    st.session_state.show_settings_import = False
                    st.success("✅ All settings imported successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Import failed: {e}")
            if st.button("Cancel", key="cancel_settings_import"):
                st.session_state.show_settings_import = False
                st.rerun()


def _render_preferences_tab() -> None:
    """Tab 1 — API key shortcut, API key backup, theme, cache."""
    # API key access
    st.markdown("### 🔑 API Keys")
    st.caption("API key configuration lives in Step 0. Use the button below to edit, or back up your existing keys to a file.")
    if st.button("🔑 Edit API Keys in Step 0", use_container_width=True):
        st.session_state.return_to = "settings"
        st.session_state.page = PAGE_API_SETUP
        st.rerun()

    st.markdown("")
    render_api_key_backup_section("settings")

    # Theme
    st.markdown("### 🎨 Theme")
    theme_options = ["Light", "Dark"]
    current_theme = st.session_state.get("theme", "dark").capitalize()
    selected_theme = st.selectbox(
        "Select Theme",
        theme_options,
        index=theme_options.index(current_theme),
        key="theme_select",
        help="Switch between light and dark themes"
    )
    if selected_theme.lower() != st.session_state.get("theme", "dark"):
        st.session_state.theme = selected_theme.lower()
        st.success(f"Theme changed to {selected_theme}! Refresh the page to apply.")
        st.rerun()

    st.markdown("---")

    # Cache (advanced, collapsed)
    with st.expander("💾 Cache Management (Advanced)", expanded=False):
        st.caption(
            "Caching reduces API costs and speeds up deck generation by reusing previous results. "
            "Clear only if you suspect stale results."
        )
        try:
            from cache_manager import CacheManager
            cache_mgr = CacheManager()
            stats = cache_mgr.get_stats() if hasattr(cache_mgr, 'get_stats') else {}

            if stats:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Cache Entries", stats.get('entries', stats.get('memory_entries', 0)))
                with col2:
                    hits = stats.get('hits', 0)
                    misses = stats.get('misses', 0)
                    total = hits + misses
                    hit_rate = (hits / max(total, 1)) * 100
                    st.metric("Hit Rate", f"{hit_rate:.1f}%")

            if st.button("🔄 Clear All Cache", key="clear_all_cache"):
                if hasattr(cache_mgr, 'clear') and cache_mgr.clear():
                    st.success("Cache cleared!")
                elif hasattr(cache_mgr, 'clear_all'):
                    cache_mgr.clear_all()
                    st.success("Cache cleared!")
                else:
                    st.warning("Cache clear not available.")
                st.rerun()
        except Exception:
            st.info("Cache management unavailable. Cache will work automatically during generation.")


def _render_language_defaults_tab() -> None:
    """Tab 2 — per-language defaults editor + summary."""
    st.caption("Set sentence length, difficulty, voice, and audio speed defaults per language. These auto-apply when you create a new deck.")

    if "per_language_settings" not in st.session_state:
        st.session_state.per_language_settings = {}

    # Summary
    configured_langs = list(st.session_state.per_language_settings.keys())
    total_custom = len(configured_langs)
    total_langs = len(st.session_state.get("all_languages", []))
    if total_custom == 0:
        st.info("📭 No custom defaults saved yet.")
    else:
        st.success(f"✅ **{total_custom}** of {total_langs} languages have custom defaults")
        if configured_langs:
            st.caption("Configured: " + " • ".join(configured_langs[:8]) + (" …" if len(configured_langs) > 8 else ""))

    st.markdown("---")

    st.markdown("## 🌐 Select Language to Configure:")

    # Language picker
    all_languages = st.session_state.get("all_languages", [])
    lang_names = [lang["name"] for lang in all_languages] if all_languages else ["English", "Spanish", "French", "German", "Italian"]
    config_lang = st.selectbox("Language to configure", options=lang_names, key="per_lang_default_select")

    defaults = st.session_state.per_language_settings.get(config_lang, {})

    # Sentence settings
    st.markdown("#### ✍️ Sentence Settings")
    col1, col2 = st.columns(2)
    with col1:
        sentence_min = st.slider("Min words", 3, 20, value=int(defaults.get("sentence_length_range", (4, 20))[0]), key=f"def_min_{config_lang}")
    with col2:
        sentence_max = st.slider("Max words", 8, 30, value=int(defaults.get("sentence_length_range", (4, 20))[1]), key=f"def_max_{config_lang}")
    sentences_per_word = st.slider("Sentences per word", 3, 15, value=defaults.get("sentences_per_word", 5), key=f"def_spw_{config_lang}")

    # Difficulty
    st.markdown("#### 🎯 Difficulty Level")
    difficulty_options = ["beginner", "intermediate", "advanced"]
    difficulty_idx = difficulty_options.index(defaults.get("difficulty", "beginner"))
    difficulty = st.selectbox(
        "Select Difficulty",
        options=difficulty_options,
        index=difficulty_idx,
        format_func=lambda x: {
            "beginner": "Beginner — Simple vocabulary",
            "intermediate": "Intermediate — Mixed tenses",
            "advanced": "Advanced — Complex structures",
        }[x],
        key=f"def_diff_{config_lang}"
    )

    # Audio
    st.markdown("#### 🎵 Audio Settings")
    try:
        from audio_generator import get_google_voices_for_language
        voice_options, _, voice_display_map = get_google_voices_for_language(config_lang)
        current_display = defaults.get("selected_voice_display", voice_options[0] if voice_options else "")
        idx = voice_options.index(current_display) if current_display in voice_options else 0
        selected_voice_display = st.selectbox("Voice", options=voice_options, index=idx, key=f"def_voice_display_{config_lang}")
        selected_voice = voice_display_map.get(selected_voice_display, "en-US-Standard-D")
    except Exception:
        selected_voice_display = st.text_input("Voice (Google TTS)", value=defaults.get("selected_voice_display", ""), key=f"def_voice_display_{config_lang}")
        selected_voice = st.text_input("Voice Code", value=defaults.get("selected_voice", ""), key=f"def_voice_{config_lang}")

    audio_speed = st.slider("Audio Speed", 0.5, 1.5, value=defaults.get("audio_speed", 1.0), step=0.05, key=f"def_speed_{config_lang}")

    # Save / recommended
    col_save, col_recommend = st.columns([2, 1])
    with col_save:
        if st.button(f"💾 Save as Defaults for **{config_lang}**", type="primary", use_container_width=True, key=f"save_def_{config_lang}"):
            st.session_state.per_language_settings[config_lang] = {
                "sentence_length_range": (sentence_min, sentence_max),
                "sentences_per_word": sentences_per_word,
                "difficulty": difficulty,
                "selected_voice": selected_voice,
                "selected_voice_display": selected_voice_display,
                "audio_speed": audio_speed,
            }
            _save_user_settings(
                st.session_state.get("favorites_order", []),
                st.session_state.per_language_settings,
            )
            st.success(f"✅ Defaults saved for **{config_lang}**")
            st.rerun()

    with col_recommend:
        if st.button("🔄 Use Recommended Defaults", use_container_width=True):
            st.session_state.per_language_settings[config_lang] = {
                "sentence_length_range": (6, 14),
                "sentences_per_word": 5,
                "difficulty": "beginner",
                "audio_speed": 0.85,
            }
            st.success("✅ Recommended defaults applied")
            st.rerun()


def _render_favorites_tab() -> None:
    """Tab 3 — favorites kanban reorder."""
    st.caption("Pin languages to the top of the Step 1 selector. Add, reorder, or remove below.")

    if "favorites_order" not in st.session_state or "per_language_settings" not in st.session_state:
        favorites_order, per_lang_settings = load_user_settings()
        st.session_state.favorites_order = favorites_order
        st.session_state.per_language_settings = per_lang_settings

    favorites = st.session_state.favorites_order
    all_languages = st.session_state.get("all_languages", [])
    lang_names = [lang["name"] for lang in all_languages] if all_languages else [
        "English", "Spanish", "French", "German", "Italian", "Japanese", "Chinese (Simplified)"
    ]

    col_available, col_favorites = st.columns([1, 1])

    with col_available:
        st.subheader("📋 Available")
        add_lang = st.selectbox(
            "Add to Favorites",
            options=[l for l in lang_names if l not in favorites],
            key="add_favorite_select"
        )
        if st.button("➕ Add to Top Favorites", type="primary", use_container_width=True):
            if add_lang and add_lang not in favorites:
                favorites.insert(0, add_lang)
                st.session_state.favorites_order = favorites
                st.rerun()

    with col_favorites:
        st.subheader("⭐ Your Favorites")
        if not favorites:
            st.info("No favorites yet — add some from the left panel.")
        else:
            st.caption("🖱️ Drag to reorder")
            new_order = sort_items(favorites, direction="vertical", key="favorites_sort")
            if new_order != favorites:
                st.session_state.favorites_order = new_order
                st.rerun()

            # Removal: separate row of small ✖ buttons (one per item) — keeps deletion explicit
            st.markdown("")
            for name in list(new_order):
                cols = st.columns([5, 1])
                cols[0].caption(f"⭐ {name}")
                if cols[1].button("✖", key=f"fav_remove_{name}", help=f"Remove {name}"):
                    favs = st.session_state.favorites_order
                    if name in favs:
                        favs.remove(name)
                    st.session_state.favorites_order = favs
                    st.rerun()

    st.caption("💡 Use **Save & Export All Settings** at the top of this page to persist your favorites.")


def render_settings_page():
    """Render the Settings page."""
    st.title("Settings")

    if st.button("← Back to Main", key="back_to_main"):
        st.session_state.page = "main"
        st.rerun()

    st.markdown("---")
    _render_unified_save_restore()
    st.markdown("---")

    tab_prefs, tab_defaults, tab_favs = st.tabs(["⚙️ Preferences", "🌍 Language Defaults", "⭐ Favorites"])

    with tab_prefs:
        _render_preferences_tab()

    with tab_defaults:
        _render_language_defaults_tab()

    with tab_favs:
        _render_favorites_tab()
