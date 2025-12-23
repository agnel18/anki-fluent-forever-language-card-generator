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
    st.markdown("## 👤 Account & Cloud Sync")

    try:
        from firebase_manager import firebase_initialized, is_signed_in, get_current_user
        from sync_manager import sync_user_data, load_cloud_data, export_user_data

        if firebase_initialized:
            if is_signed_in():
                # Signed in state
                user = get_current_user()
                if user:
                    user_email = user.get('email', 'Unknown')
                    user_name = user.get('display_name', user_email.split('@')[0])
                    st.success(f"✅ **Signed in as {user_name}**")
                    st.info(f"**Email:** {user_email}")
                    st.info("Your settings are automatically synced to the cloud.")

                    # Account management
                    st.markdown("**Account Management:**")
                    account_col1, account_col2, account_col3 = st.columns(3)

                    with account_col1:
                        if st.button("🔄 Sync Now", help="Manually sync your data to the cloud"):
                            if sync_user_data():
                                st.success("✅ Data synced successfully!")
                            else:
                                st.error("❌ Sync failed. Check your connection.")

                    with account_col2:
                        if st.button("📤 Export Data", help="Download all your data as JSON"):
                            data = export_user_data()
                            if data:
                                import json
                                st.download_button(
                                    label="📥 Download Data",
                                    data=json.dumps(data, indent=2),
                                    file_name="language_app_data.json",
                                    mime="application/json"
                                )
                                st.success("✅ Data exported!")
                            else:
                                st.error("❌ Failed to export data.")

                    with account_col3:
                        if st.button("🚪 Sign Out", help="Sign out and use local storage only"):
                            from firebase_manager import sign_out
                            sign_out()
                            st.success("✅ Signed out successfully!")
                            st.rerun()

                    # Data deletion (with confirmation)
                    st.markdown("**Danger Zone:**")
                    with st.expander("🗑️ Delete Cloud Data", expanded=False):
                        st.warning("⚠️ This will permanently delete all your data from the cloud.")
                        st.write("This includes API keys, settings, and usage statistics.")

                        if st.checkbox("I understand this cannot be undone"):
                            if st.button("🗑️ Permanently Delete All Cloud Data", type="secondary"):
                                # This would need implementation in firebase_manager
                                st.error("⚠️ Cloud data deletion not yet implemented")
                                # TODO: Implement delete_user_data in firebase_manager

            else:
                # Firebase available but not signed in
                st.info("🔐 **Enable Cloud Sync** to backup your settings across devices.")

                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("🚀 Sign In with Google", use_container_width=True, type="primary"):
                        from firebase_manager import sign_in_with_google
                        sign_in_with_google()

                with col2:
                    st.caption("Keep using local storage only")

                st.markdown("**Benefits of Cloud Sync:**")
                benefits = [
                    "✅ Secure backup of your API keys",
                    "✅ Access settings on any device",
                    "✅ Never lose your configuration",
                    "✅ Automatic data synchronization"
                ]
                for benefit in benefits:
                    st.markdown(benefit)

        else:
            # Firebase unavailable
            st.warning("☁️ **Cloud sync is currently unavailable**")
            st.info("Your data is stored locally only. Cloud features will be available when Firebase is accessible.")

    except Exception as e:
        st.error(f"Account section error: {e}")
        st.info("🔄 **Local storage only** - Account features unavailable")

    # Privacy Controls Section (only show if signed in or Firebase available)
    try:
        firebase_available = firebase_initialized
        user_signed_in = is_signed_in()
        if user_signed_in or firebase_available:
            st.markdown("---")
            st.markdown("## 🔒 Privacy Controls")
            st.info("Choose exactly what data gets synced to the cloud.")
        
        # Initialize sync preferences if not set
        if "sync_preferences" not in st.session_state:
            st.session_state.sync_preferences = ["API Keys", "Theme Settings", "Audio Preferences"]
        
        sync_options = st.multiselect(
            "Select data to sync:",
            ["API Keys", "Theme Settings", "Audio Preferences", "Usage Statistics"],
            default=st.session_state.sync_preferences,
            help="Only selected data types will be stored in the cloud"
        )
        
        if st.button("💾 Update Sync Preferences"):
            st.session_state.sync_preferences = sync_options
            st.success("✅ Sync preferences updated!")
            # Trigger a sync to apply new preferences
            if user_signed_in and firebase_available:
                from sync_manager import sync_user_data
                sync_user_data()
    
    except Exception as e:
        st.error(f"Privacy controls error: {e}")
    
    st.markdown("---")

    # --- API Keys Management Section ---
    st.markdown("## 🔑 API Keys Management")
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
    st.markdown("## 🎨 Theme")
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
    st.markdown("## 🔑 API Keys")
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
    st.markdown("## 🌟 Favorite Languages (Pinned for Quick Access)")
    st.info("Select your favorite languages below. They'll appear first in all dropdowns for faster selection.")

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

    st.markdown("Your Favorites:")

    # Get current favorite language names
    current_favorites = [lang["name"] for lang in st.session_state.learned_languages]

    # Create multiselect for managing favorites
    selected_favorites = st.multiselect(
        "Select your favorite languages (max 5):",
        options=all_lang_names,
        default=current_favorites,
        max_selections=5,
        key="favorite_languages_multiselect",
        help="These languages will appear first in all dropdowns for faster selection"
    )

    # Update session state when multiselect changes
    if selected_favorites != current_favorites:
        # Convert selected names back to language objects with usage data
        updated_favorites = []
        for lang_name in selected_favorites:
            # Find existing language data or create new entry
            existing = next((lang for lang in st.session_state.learned_languages if lang["name"] == lang_name), None)
            if existing:
                updated_favorites.append(existing)
            else:
                updated_favorites.append({"name": lang_name, "usage": 0})

        st.session_state.learned_languages = updated_favorites

    # Display current favorites as clean numbered list (read-only)
    if st.session_state.learned_languages:
        st.markdown("**Current Favorites:**")
        for idx, lang in enumerate(st.session_state.learned_languages, 1):
            st.markdown(f"**{idx}. {lang['name']}**")

    st.caption(f"{len(st.session_state.learned_languages)}/5 favorites selected")
    st.markdown("---")

    # --- Default Settings Per Language (original design) ---
    st.markdown("## ⚙️ Default Settings Per Language")
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
        "audio_speed": 0.8,
        "enable_topics": False,
        "selected_topics": [],
        "custom_topics": []
    })

    # --- Sentence Parameters ---
    with st.container():
        st.markdown("### 📏 Sentence Parameters")
        st.markdown("*Control the length and quantity of generated sentences*")

        col_len, col_sent = st.columns(2)
        with col_len:
            st.markdown("**Sentence Length (words)**")
            settings["sentence_length_range"] = st.slider(
                "Sentence Length Range",
                min_value=4,
                max_value=30,
                value=settings["sentence_length_range"],
                step=1,
                key="perlang_sentlen",
                help="Minimum and maximum words per sentence for this language",
                label_visibility="collapsed"
            )
        with col_sent:
            st.markdown("**Sentences Per Word**")
            settings["sentences_per_word"] = st.slider(
                "Sentences Per Word",
                min_value=3,
                max_value=15,
                value=settings["sentences_per_word"],
                step=1,
                key="perlang_sentcount",
                help="How many different sentences to generate for each word",
                label_visibility="collapsed"
            )

    st.markdown("---")

    # --- Audio Settings ---
    with st.container():
        st.markdown("### 🔊 Audio Settings")
        st.markdown("*Adjust pronunciation speed for language learning*")

        st.markdown("**Audio Speed**")
        settings["audio_speed"] = st.slider(
            "Audio Speed",
            min_value=0.5,
            max_value=1.5,
            value=settings["audio_speed"],
            step=0.1,
            key="perlang_audiospeed",
            help="0.5 = very slow (beginners), 0.8 = recommended for learners, 1.0 = normal speed",
            label_visibility="collapsed"
        )

    st.markdown("---")

    # --- Difficulty Level ---
    with st.container():
        st.markdown("## 🎯 Difficulty Level")
        st.markdown("*Choose the complexity level for generated content*")

        difficulty_options = {
            "beginner": "Beginner - Simple vocabulary and basic sentence structures",
            "intermediate": "Intermediate - Moderate vocabulary with varied sentence patterns",
            "advanced": "Advanced - Complex vocabulary and sophisticated sentence structures"
        }

        settings["difficulty"] = st.selectbox(
            "Difficulty",
            ["beginner", "intermediate", "advanced"],
            index=["beginner", "intermediate", "advanced"].index(settings["difficulty"]),
            key="perlang_difficulty",
            format_func=lambda x: difficulty_options[x],
            help="Choose the complexity level for generated sentences"
        )

        # Show difficulty explanations
        difficulty = settings["difficulty"]
        if difficulty == "beginner":
            st.info("**Beginner**: Simple vocabulary and grammar, perfect for absolute beginners.")
        elif difficulty == "intermediate":
            st.info("**Intermediate**: Mixed vocabulary and grammar, suitable for learners with basic knowledge.")
        elif difficulty == "advanced":
            st.info("**Advanced**: Complex structures and vocabulary, ideal for proficient learners.")

    st.markdown("---")

    # --- Topic Settings ---
    with st.container():
        st.markdown("## 🎯 Topic Settings")
        st.markdown("*Choose topics to focus sentence generation for contextual learning*")

        # Enable/disable toggle
        settings["enable_topics"] = st.toggle(
            "Enable topic-based generation",
            value=settings.get("enable_topics", False),
            key="perlang_enable_topics",
            help="When enabled, generated sentences will be themed around selected topics"
        )

        if settings["enable_topics"]:
            # Initialize selected_topics if not exists
            if "selected_topics" not in settings:
                settings["selected_topics"] = []

            # Topic limit
            TOPIC_LIMIT = 5
            current_topic_count = len(settings["selected_topics"])
            limit_reached = current_topic_count >= TOPIC_LIMIT

            if limit_reached:
                st.warning(f"⚠️ **Topic limit reached:** Maximum of {TOPIC_LIMIT} topics allowed.")
            else:
                st.info(f"📊 **Topics selected:** {current_topic_count}/{TOPIC_LIMIT}")

            # Import curated topics
            from constants import CURATED_TOPICS

            # Curated topics selection in two columns
            st.markdown("**Select topics:**")
            col1, col2 = st.columns(2)

            # Split curated topics into two columns
            mid_point = len(CURATED_TOPICS) // 2
            left_topics = CURATED_TOPICS[:mid_point]
            right_topics = CURATED_TOPICS[mid_point:]

            with col1:
                for topic in left_topics:
                    is_selected = topic in settings["selected_topics"]
                    disabled = limit_reached and not is_selected

                    if st.checkbox(
                        topic,
                        value=is_selected,
                        key=f"perlang_topic_{topic}",
                        disabled=disabled
                    ):
                        if topic not in settings["selected_topics"] and not limit_reached:
                            settings["selected_topics"].append(topic)
                        elif topic in settings["selected_topics"]:
                            settings["selected_topics"].remove(topic)

            with col2:
                for topic in right_topics:
                    is_selected = topic in settings["selected_topics"]
                    disabled = limit_reached and not is_selected

                    if st.checkbox(
                        topic,
                        value=is_selected,
                        key=f"perlang_topic_{topic}_right",
                        disabled=disabled
                    ):
                        if topic not in settings["selected_topics"] and not limit_reached:
                            settings["selected_topics"].append(topic)
                        elif topic in settings["selected_topics"]:
                            settings["selected_topics"].remove(topic)

            # Display selected topics
            if settings["selected_topics"]:
                st.markdown("**Selected topics:**")
                selected_display = ", ".join(settings["selected_topics"])
                st.info(f"🎯 {selected_display}")
            else:
                st.info("No topics selected - sentences will use general themes")

            # Custom topics section
            st.markdown("### ➕ Custom Topics")
            col_add, col_list = st.columns([1, 2])

            with col_add:
                new_topic = st.text_input(
                    "Add custom topic:",
                    placeholder="e.g., Gardening, Photography",
                    key=f"perlang_new_topic_{selected_lang}",
                    max_chars=50,
                    disabled=limit_reached
                )

                if st.button("➕ Add Topic", key=f"perlang_add_custom_{selected_lang}", disabled=limit_reached):
                    if new_topic.strip():
                        # Validate input
                        clean_topic = new_topic.strip()
                        if len(clean_topic) < 2:
                            st.error("Topic must be at least 2 characters long.")
                        elif clean_topic in settings["selected_topics"]:
                            st.warning("This topic is already selected.")
                        elif clean_topic in CURATED_TOPICS:
                            st.warning("This topic already exists in the curated list.")
                        else:
                            settings["custom_topics"].append(clean_topic)
                            settings["selected_topics"].append(clean_topic)
                            st.success(f"Added topic: {clean_topic}")
                            st.rerun()

            with col_list:
                if settings["custom_topics"]:
                    st.markdown("**Your Custom Topics:**")
                    for i, topic in enumerate(settings["custom_topics"]):
                        col_topic, col_remove = st.columns([3, 1])
                        with col_topic:
                            is_selected = st.checkbox(
                                topic,
                                value=topic in settings["selected_topics"],
                                key=f"perlang_custom_{selected_lang}_{topic}_{i}"
                            )
                            if is_selected and topic not in settings["selected_topics"]:
                                settings["selected_topics"].append(topic)
                            elif not is_selected and topic in settings["selected_topics"]:
                                settings["selected_topics"].remove(topic)

                        with col_remove:
                            if st.button("🗑️", key=f"perlang_remove_custom_{selected_lang}_{i}", help=f"Remove {topic}"):
                                if topic in settings["selected_topics"]:
                                    settings["selected_topics"].remove(topic)
                                settings["custom_topics"].remove(topic)
                                st.rerun()

    if st.button("Save Settings", key="perlang_save_btn", type="primary"):
        st.session_state.per_language_settings[selected_lang] = settings.copy()
        st.success(f"Settings saved for {selected_lang}!")
    st.markdown("---")

    # --- Cache Management Section ---
    st.markdown("## 💾 API Response Cache")
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