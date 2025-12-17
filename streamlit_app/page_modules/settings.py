# pages/settings.py - Settings page for the language learning app

import streamlit as st
from pathlib import Path
from utils import persist_api_keys


def render_settings_page():
    """Render the settings page with profile, API keys, favorite languages, and per-language settings."""
    st.title("Settings")

    # Back button
    if st.button("← Back to Main", key="back_to_main"):
        st.session_state.page = "main"
        st.rerun()

    st.markdown("---")

    # --- Profile & Cloud Sync Section ---
    st.markdown("### 👤 Profile & Cloud Sync")
    
    try:
        from firebase_manager import init_firebase
        firebase_available = init_firebase()
        
        if firebase_available:
            st.success("✅ **Cloud Sync Active** - Your data is securely stored in Firebase")
            
            # Show session info
            session_id = st.session_state.get("session_id", "Unknown")
            masked_session = session_id[:8] + "..." if len(session_id) > 8 else session_id
            st.info(f"**Session ID:** {masked_session}")
            
            # Cloud data management
            st.markdown("**Cloud Data:**")
            cloud_col1, cloud_col2 = st.columns(2)
            
            with cloud_col1:
                if st.button("📊 View Cloud Stats", help="Show your usage statistics from Firebase"):
                    try:
                        from firebase_manager import load_usage_stats_from_firebase
                        stats = load_usage_stats_from_firebase(session_id)
                        if stats:
                            with st.expander("Cloud Usage Statistics", expanded=True):
                                st.json(stats)
                        else:
                            st.info("No usage statistics found in cloud")
                    except Exception as e:
                        st.error(f"Failed to load stats: {e}")
            
            with cloud_col2:
                if st.button("🗑️ Clear Cloud Data", help="Remove all your data from Firebase"):
                    if st.checkbox("⚠️ Confirm deletion - this cannot be undone"):
                        try:
                            # Note: This would require implementing a delete function
                            st.warning("Cloud data deletion not yet implemented")
                        except Exception as e:
                            st.error(f"Failed to delete cloud data: {e}")
        else:
            st.warning("🔄 **Local Storage Only** - Firebase unavailable, data stored locally only")
            st.info("To enable cloud sync, ensure firebase_config.json is properly configured")
            
    except Exception as e:
        st.error(f"Profile section error: {e}")
        st.info("🔄 **Local Storage Only** - Profile features unavailable")
    
    st.markdown("---")

    # --- API Keys Management Section ---
    st.markdown("### 🔑 API Keys Management")
    st.info("Manage your API keys for Groq and Pixabay services.")
    
    # Current API keys status
    groq_key = st.session_state.get("groq_api_key", "")
    pixabay_key = st.session_state.get("pixabay_api_key", "")
    
    col1, col2 = st.columns(2)
    with col1:
        if groq_key:
            masked_groq = groq_key[:8] + "..." + groq_key[-4:] if len(groq_key) > 12 else groq_key
            st.success(f"✅ Groq Key: {masked_groq}")
        else:
            st.warning("❌ No Groq API key set")
    
    with col2:
        if pixabay_key:
            masked_pixabay = pixabay_key[:8] + "..." + pixabay_key[-4:] if len(pixabay_key) > 12 else pixabay_key
            st.success(f"✅ Pixabay Key: {masked_pixabay}")
        else:
            st.warning("❌ No Pixabay API key set")
    
    # API key management options
    st.markdown("**Manage API Keys:**")
    manage_col1, manage_col2, manage_col3 = st.columns(3)
    
    with manage_col1:
        if st.button("🔄 Update API Keys", help="Go back to API setup to change your keys"):
            st.session_state.page = "api_setup"
            st.rerun()
    
    with manage_col2:
        if st.button("💾 Save to Cloud", help="Save current API keys to Firebase for cross-device sync"):
            try:
                from firebase_manager import init_firebase, save_settings_to_firebase
                if init_firebase() and groq_key and pixabay_key:
                    save_settings_to_firebase(st.session_state.session_id, {
                        "groq_api_key": groq_key,
                        "pixabay_api_key": pixabay_key
                    })
                    st.success("✅ API keys saved to cloud!")
                else:
                    st.error("❌ Firebase unavailable or missing API keys")
            except Exception as e:
                st.error(f"❌ Failed to save to cloud: {e}")
    
    with manage_col3:
        if st.button("📥 Load from Cloud", help="Load API keys from Firebase"):
            try:
                from firebase_manager import init_firebase, load_settings_from_firebase
                if init_firebase():
                    cloud_settings = load_settings_from_firebase(st.session_state.session_id)
                    if cloud_settings and 'groq_api_key' in cloud_settings and 'pixabay_api_key' in cloud_settings:
                        st.session_state.groq_api_key = cloud_settings['groq_api_key']
                        st.session_state.pixabay_api_key = cloud_settings['pixabay_api_key']
                        st.success("✅ API keys loaded from cloud!")
                        st.rerun()
                    else:
                        st.warning("No API keys found in cloud")
                else:
                    st.error("❌ Firebase unavailable")
            except Exception as e:
                st.error(f"❌ Failed to load from cloud: {e}")
    
    st.markdown("---")
    st.markdown("### 🎨 Theme")
    st.info("Choose your preferred theme for the application interface.")

    # Initialize theme if not set
    if "theme" not in st.session_state:
        st.session_state.theme = "dark"

    theme_options = ["Light", "Dark"]
    current_theme = st.session_state.theme.capitalize()

    selected_theme = st.selectbox(
        "Select Theme",
        theme_options,
        index=theme_options.index(current_theme),
        key="theme_select",
        help="Switch between light and dark themes"
    )

    if selected_theme.lower() != st.session_state.theme:
        st.session_state.theme = selected_theme.lower()
        st.success(f"Theme changed to {selected_theme}! Refresh the page to apply changes.")
        st.rerun()

    st.markdown("---")

    # --- API Keys Section (Single) ---
    st.markdown("### 🔑 API Keys")
    st.info("Your API keys are securely stored in your account (never in the cloud for guests). Changes are saved automatically.")
    st.text_input(
        "Groq API Key",
        value=st.session_state.get("groq_api_key", ""),
        key="groq_api_key",
        type="password",
        on_change=persist_api_keys
    )
    st.text_input(
        "Pixabay API Key",
        value=st.session_state.get("pixabay_api_key", ""),
        key="pixabay_api_key",
        type="password",
        on_change=persist_api_keys
    )
    st.markdown("---")

    # --- Favorite Languages Section ---
    st.markdown("### 🌟 Favorite Languages (Pinned for Quick Access)")
    st.info("Your favorite languages appear first in all dropdowns for faster selection.")

    # Access all_languages from session state (set in state_manager.py)
    all_languages = st.session_state.get("all_languages", [])
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
        if st.button("Add", key="add_lang_btn", type="secondary") and new_lang and len(st.session_state.learned_languages) < 5:
            st.session_state.learned_languages.append({"name": new_lang, "usage": 0})
            st.success(f"Added {new_lang}")
            st.rerun()

    st.markdown("Your Favorites:")
    st.markdown("""
    <style>
    .lang-card-grid {display: flex; flex-direction: column; gap: 12px; margin-bottom: 16px;}
    .lang-card {background: var(--card-bg); color: var(--text-color); border: 1px solid var(--card-border); border-radius: 8px; box-shadow: var(--box-shadow); padding: 12px 16px; display: flex; flex-direction: column; align-items: stretch; position: relative; transition: box-shadow 0.2s;}
    .lang-card .lang-title {font-size: 1.1em; font-weight: 600; margin-bottom: 4px;}
    .lang-card .lang-usage {font-size: 0.9em; color: var(--text-color); opacity: 0.7; margin-bottom: 8px;}
    .lang-card .lang-actions {display: flex; justify-content: space-between; align-items: center;}
    .lang-card .stButton>button {background: none !important; color: var(--error-bg) !important; font-size: 1.2em !important; border: none !important; box-shadow: none !important; padding: 4px 8px !important;}
    .lang-card .stButton>button:hover {color: var(--button-text) !important; background: var(--error-bg) !important; border-radius: 50% !important;}
    .lang-card .arrow-btn .stButton>button {color: var(--primary-color) !important; font-size: 1.1em !important;}
    .lang-card .arrow-btn .stButton>button:hover {color: var(--button-text) !important; background: var(--primary-color) !important; border-radius: 50% !important;}
    @media (max-width: 768px) {
        .lang-card {padding: 10px 12px;}
        .lang-card .lang-title {font-size: 1em;}
        .lang-card .lang-actions {flex-direction: column; gap: 8px;}
    }
    </style>
    <div class='lang-card-grid'>
    """, unsafe_allow_html=True)

    for idx, lang in enumerate(st.session_state.learned_languages):
        # Mobile-responsive layout: stack actions vertically on small screens
        with st.container():
            st.markdown(f"<div class='lang-card'><div class='lang-title'>{lang['name']}</div><div class='lang-usage'>Usage: {lang['usage']}</div></div>", unsafe_allow_html=True)
            action_cols = st.columns([1, 1, 1]) if len(st.session_state.learned_languages) > 1 else st.columns([1])
            if len(st.session_state.learned_languages) > 1:
                with action_cols[0]:
                    if idx > 0:
                        if st.button("↑", key=f"moveup_{lang['name']}_{idx}", help=f"Move {lang['name']} up"):
                            st.session_state.learned_languages[idx-1], st.session_state.learned_languages[idx] = st.session_state.learned_languages[idx], st.session_state.learned_languages[idx-1]
                            st.rerun()
                    else:
                        st.empty()
                with action_cols[1]:
                    if idx < len(st.session_state.learned_languages) - 1:
                        if st.button("↓", key=f"movedown_{lang['name']}_{idx}", help=f"Move {lang['name']} down"):
                            st.session_state.learned_languages[idx+1], st.session_state.learned_languages[idx] = st.session_state.learned_languages[idx], st.session_state.learned_languages[idx+1]
                            st.rerun()
                    else:
                        st.empty()
            with action_cols[-1]:
                if st.button("❌", key=f"remove_{lang['name']}_{idx}", help=f"Remove {lang['name']}"):
                    st.session_state.learned_languages.pop(idx)
                    st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.caption("Reorder with arrows. Remove with ❌. Max 5.")
    st.markdown("---")

    # --- Default Settings Per Language (original design) ---
    st.markdown("### ⚙️ Default Settings Per Language")
    st.info("Select a language, adjust its default settings, and save.")
    if "per_language_settings" not in st.session_state:
        st.session_state.per_language_settings = {}

    lang_names = [lang["name"] for lang in all_languages]
    selected_lang = st.selectbox("Select language to edit settings", lang_names, key="perlang_settings_select")

    # Load or initialize settings for selected language
    settings = st.session_state.per_language_settings.get(selected_lang, {
        "difficulty": "intermediate",
        "sentence_length_range": (6, 16),
        "sentences_per_word": 10,
        "audio_speed": 0.8
    })

    settings["difficulty"] = st.selectbox(
        "Difficulty",
        ["beginner", "intermediate", "advanced"],
        index=["beginner", "intermediate", "advanced"].index(settings["difficulty"]),
        key="perlang_difficulty"
    )
    settings["sentence_length_range"] = st.slider(
        "Sentence length (words)",
        min_value=4,
        max_value=30,
        value=settings["sentence_length_range"],
        step=1,
        key="perlang_sentlen"
    )
    settings["sentences_per_word"] = st.slider(
        "Sentences per word",
        min_value=3,
        max_value=15,
        value=settings["sentences_per_word"],
        step=1,
        key="perlang_sentcount"
    )
    settings["audio_speed"] = st.slider(
        "Audio speed",
        min_value=0.5,
        max_value=1.5,
        value=settings["audio_speed"],
        step=0.1,
        key="perlang_audiospeed"
    )

    if st.button("Save Settings", key="perlang_save_btn", type="primary"):
        st.session_state.per_language_settings[selected_lang] = settings.copy()
        st.success(f"Settings saved for {selected_lang}!")
    st.markdown("---")

    # --- Cache Management Section ---
    st.markdown("### 💾 API Response Cache")
    st.info("Caching reduces API costs and speeds up deck generation by reusing previous results. Cache expires automatically.")

    try:
        from cache_manager import get_cache_manager
        cache_manager = get_cache_manager()
        stats = cache_manager.get_stats()

        # Display cache statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Memory Cache", f"{stats['memory_entries']}/{stats['max_memory_entries']}")
        with col2:
            st.metric("Disk Cache", stats['disk_entries'])
        with col3:
            hit_rate = (stats['hits'] / max(stats['hits'] + stats['misses'], 1)) * 100
            st.metric("Hit Rate", f"{hit_rate:.1f}%")

        st.caption(f"Cache directory: {stats['cache_dir']}")

        # Cache management buttons
        st.markdown("**Cache Management:**")
        cache_col1, cache_col2, cache_col3 = st.columns(3)

        with cache_col1:
            if st.button("🔄 Clear All Cache", key="clear_all_cache", help="Delete all cached API responses"):
                cleared = cache_manager.clear_all()
                st.success(f"Cleared {cleared} cached entries!")
                st.rerun()

        with cache_col2:
            if st.button("🧹 Clear Expired", key="clear_expired_cache", help="Remove only expired cache entries"):
                cache_manager.cleanup()
                st.success("Cleaned up expired cache entries!")
                st.rerun()

        with cache_col3:
            if st.button("📊 Refresh Stats", key="refresh_cache_stats", help="Update cache statistics display"):
                st.rerun()

        # Namespace-specific clearing
        st.markdown("**Clear Specific Cache Types:**")
        ns_col1, ns_col2, ns_col3 = st.columns(3)

        with ns_col1:
            if st.button("🗣️ Clear Groq Cache", key="clear_groq_cache", help="Clear cached Groq API responses"):
                cleared = cache_manager.clear_namespace("groq_meaning") + \
                         cache_manager.clear_namespace("groq_sentences_pass1") + \
                         cache_manager.clear_namespace("groq_sentences_pass2")
                st.success(f"Cleared {cleared} Groq cached entries!")

        with ns_col2:
            if st.button("🖼️ Clear Image Cache", key="clear_image_cache", help="Clear cached Pixabay search results"):
                cleared = cache_manager.clear_namespace("pixabay_search")
                st.success(f"Cleared {cleared} image search cached entries!")

        with ns_col3:
            if st.button("📈 View Details", key="view_cache_details", help="Show detailed cache information"):
                with st.expander("Cache Details", expanded=True):
                    st.json(stats)

    except Exception as e:
        st.error(f"Cache management unavailable: {e}")
        st.info("Cache functionality requires proper initialization. Try restarting the app.")