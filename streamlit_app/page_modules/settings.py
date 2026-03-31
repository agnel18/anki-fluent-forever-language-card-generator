# pages/settings.py - Settings page for the language learning app

import streamlit as st
import datetime
import time
import os
from pathlib import Path
from utils import persist_api_keys

# Import centralized configuration
from streamlit_app.shared_utils import get_gemini_model


def render_settings_page():
    """Render the settings page with profile, API keys, favorite languages, and per-language settings."""
    st.title("Settings")

    # Back button
    if st.button("← Back to Main", key="back_to_main"):
        st.session_state.page = "main"
        st.rerun()

    st.markdown("---")

    # Initialize services (available throughout the function)
    try:
        from services.firebase import is_firebase_initialized, is_signed_in
        from services.settings.profile_manager import ProfileManager
        from services.settings.sync_manager import SyncManager
        from services.settings.preferences_manager import PreferencesManager
        from services.settings.api_key_manager import APIKeyManager
        from services.settings.cache_service import CacheService

        profile_manager = ProfileManager()
        sync_manager = SyncManager()
        prefs_manager = PreferencesManager()
        api_key_manager = APIKeyManager()
        cache_service = CacheService()

        firebase_available = is_firebase_initialized()
        user_signed_in = is_signed_in()

    except Exception as e:
        st.error(f"Failed to initialize services: {e}")
        st.info("🔄 **Local storage only** - Some features may be unavailable")
        # Set defaults for when services fail to initialize
        firebase_available = False
        user_signed_in = False
        profile_manager = None
        sync_manager = None
        prefs_manager = None
        api_key_manager = None
        cache_service = None

    # --- Profile & Cloud Sync Section ---
    st.markdown("## 👤 Account & Cloud Sync")

    if firebase_available:
            if user_signed_in:
                # Signed in state
                user_info = profile_manager.get_user_display_info()
                if user_info:
                    st.success(f"✅ **Signed in as {user_info['name']}**")
                    st.info(f"**Email:** {user_info['email']}")
                    st.info("Your settings are automatically synced to the cloud.")

                    # Account management
                    st.markdown("**Account Management:**")
                    account_col1, account_col2, account_col3 = st.columns(3)

                    with account_col1:
                        if st.button("🔄 Sync Now", help="Manually sync your data to the cloud"):
                            if sync_manager.sync_user_data():
                                pass  # Success message handled in service
                            else:
                                pass  # Error message handled in service

                    with account_col2:
                        if st.button("📤 Export Data", help="Download all your data as JSON"):
                            data = profile_manager.export_user_data()
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
                            if profile_manager.sign_out_user():
                                st.success("✅ Signed out successfully!")
                                st.rerun()

                    # Deck Library Section (only for signed-in users)
                    st.markdown("**Your Deck Library:**")
                    try:
                        deck_list = profile_manager.get_user_deck_library()

                        if deck_list:
                            st.markdown("### 📚 Your Generated Decks")

                            for deck_data in deck_list:
                                created_at_display = deck_data.get('created_at_display', 'Unknown')
                                created_at_full = deck_data.get('created_at_full', 'Unknown')

                                with st.expander(f"📖 {deck_data.get('deck_name', 'Unnamed Deck')} - {created_at_display}", expanded=False):
                                    col_info, col_stats = st.columns([2, 1])

                                    with col_info:
                                        st.markdown(f"**Language:** {deck_data.get('language', 'Unknown')}")
                                        st.markdown(f"**Words:** {deck_data.get('word_count', 0)}")
                                        st.markdown(f"**Cards:** {deck_data.get('card_count', 0)}")
                                        st.markdown(f"**Created:** {created_at_full}")

                                        # Show generation settings
                                        settings = deck_data.get('generation_settings', {})
                                        if settings:
                                            st.markdown("**Settings Used:**")
                                            st.caption(f"Difficulty: {settings.get('difficulty', 'Unknown')}")
                                            st.caption(f"Sentences/word: {settings.get('sentences_per_word', 'Unknown')}")

                                    with col_stats:
                                        file_size = deck_data.get('file_size', 0)
                                        if file_size > 0:
                                            # Convert bytes to MB
                                            size_mb = file_size / (1024 * 1024)
                                            st.metric("File Size", f"{size_mb:.1f} MB")

                                        # Note that actual deck files are not stored in cloud
                                        st.caption("*Decks are downloaded locally to Anki*")

                            if len(deck_list) >= 10:
                                st.info("Showing your 10 most recent decks. Older decks are still saved in your account.")
                        else:
                            st.info("📝 No decks generated yet. Create your first deck to see it here!")

                    except Exception as e:
                        st.warning(f"Could not load deck library: {e}")
                        st.caption("Deck history will be available when Firebase is accessible.")

                    st.markdown("---")
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

    # Privacy Controls Section (only show if signed in or Firebase available)
    try:
        if user_signed_in or firebase_available:
            st.markdown("---")
            st.markdown("## 🔒 Privacy Controls")
            st.info("Choose exactly what data gets synced to the cloud.")

        # Initialize sync preferences if not set
        if prefs_manager:
            current_sync_prefs = prefs_manager.get_sync_preferences()

            sync_options = st.multiselect(
                "Select data to sync:",
                ["API Keys", "Theme Settings", "Audio Preferences", "Usage Statistics"],
                default=current_sync_prefs,
                help="Only selected data types will be stored in the cloud"
            )

            if st.button("💾 Update Sync Preferences"):
                prefs_manager.set_sync_preferences(sync_options)
                st.success("✅ Sync preferences updated!")
                # Trigger a sync to apply new preferences
                if user_signed_in and firebase_available and sync_manager:
                    sync_manager.sync_user_data()
        else:
            st.warning("Privacy controls unavailable - preferences service not loaded")

    except Exception as e:
        st.error(f"Privacy controls error: {e}")
    
    st.markdown("---")

    # --- API Configuration Sections ---
    st.markdown("## 🔑 API Configuration")

    # Load current API keys
    google_key = st.session_state.get("google_api_key", os.getenv("GOOGLE_API_KEY", ""))
    tts_key = st.session_state.get("google_tts_api_key", os.getenv("GOOGLE_TTS_API_KEY", ""))
    pixabay_key = st.session_state.get("pixabay_api_key", "")

    # Status overview (vertical — mobile friendly)
    if google_key:
        st.success("✅ **Gemini AI** — Configured")
    else:
        st.error("❌ **Gemini AI** — Required")
    if tts_key:
        st.success("✅ **Text-to-Speech** — Configured")
    else:
        st.error("❌ **Text-to-Speech** — Required")
    if pixabay_key:
        st.success("✅ **Pixabay Images** — Configured")
    else:
        st.error("❌ **Pixabay Images** — Required")

    st.markdown("---")

    # Helper to save a key to .env file
    def _save_key_to_env(env_key_name, key_value):
        env_path = Path(__file__).parent.parent / ".env"
        try:
            env_content = ""
            if env_path.exists():
                env_content = env_path.read_text()
            lines = env_content.split('\n')
            key_found = False
            for i, line in enumerate(lines):
                if line.startswith(f'{env_key_name}='):
                    lines[i] = f'{env_key_name}={key_value}'
                    key_found = True
                    break
            if not key_found:
                lines.append(f'{env_key_name}={key_value}')
            env_path.write_text('\n'.join(lines))
            return True
        except Exception as e:
            st.error(f"❌ Failed to save to .env file: {e}")
            st.info("💡 The key is set for this session only.")
            return False

    # ==========================================================
    # SECTION 1: Gemini AI — FREE (no billing needed)
    # ==========================================================
    st.markdown("### 🤖 Gemini AI — FREE (no billing needed)")

    with st.expander("📖 How to get your Gemini API key", expanded=not bool(google_key)):
        st.markdown("""
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Select a project"** → **"New Project"**
3. Name it **"Language Cards - Gemini"** → click **"Create"**
4. **Do NOT enable billing** — this keeps Gemini free!
5. Go to **APIs & Services** → **Enable APIs and Services**
6. Search for **"Generative Language API"** → click **"Enable"**
7. Go to **APIs & Services** → **Credentials**
8. Click **"Create Credentials"** → **"API key"**
9. Copy the key and paste it below
10. Click on the key → **"API restrictions"** → **"Restrict key"** → select only **"Generative Language API"** → **"Save"**

> ✅ **Free tier: ~1,500 requests/day, 1 million tokens/day — no credit card needed!**
        """)

    google_key_input = st.text_input(
        "Gemini API Key",
        value=google_key,
        type="password",
        help="Your API key from the billing-free Gemini project",
        key="google_key_input"
    )

    col_save, col_test = st.columns([1, 1])
    with col_save:
        if st.button("💾 Save Gemini Key", help="Save the Gemini API key", key="settings_save_gemini"):
            if google_key_input:
                st.session_state.google_api_key = google_key_input
                os.environ["GOOGLE_API_KEY"] = google_key_input
                if _save_key_to_env("GOOGLE_API_KEY", google_key_input):
                    st.success("✅ Gemini API key saved!")
                    time.sleep(1)
                    st.rerun()
            else:
                st.error("❌ Please enter your Gemini API key")

    with col_test:
        if google_key_input or google_key:
            test_key = google_key_input or google_key
            if st.button("🧪 Test Gemini", help="Test your Gemini API key", key="settings_test_gemini"):
                with st.spinner("Testing Gemini API..."):
                    try:
                        from streamlit_app.shared_utils import get_gemini_model, get_gemini_api
                        api = get_gemini_api()
                        api.configure(api_key=test_key)
                        api.generate_content(model=get_gemini_model(), contents="Hello")
                        st.success("✅ Gemini API connection successful!")
                    except Exception as e:
                        st.error(f"❌ Gemini test failed: {str(e)}")

    st.markdown("---")

    # ==========================================================
    # SECTION 2: Text-to-Speech — FREE (billing enabled for activation only)
    # ==========================================================
    st.markdown("### 🔊 Text-to-Speech — FREE (billing enabled for activation only)")

    with st.expander("📖 How to get your TTS API key", expanded=not bool(tts_key)):
        st.markdown("""
> ⚠️ **This must be a DIFFERENT Google Cloud project from Gemini** (see "Why?" below)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Select a project"** → **"New Project"**
3. Name it **"Language Cards - TTS"** → click **"Create"**
4. Go to **Billing** → **Link a billing account** (required to activate TTS, but the service itself is free within limits)
5. Go to **APIs & Services** → **Enable APIs and Services**
6. Search for **"Cloud Text-to-Speech API"** → click **"Enable"**
7. Go to **APIs & Services** → **Credentials**
8. Click **"Create Credentials"** → **"API key"**
9. Copy the key and paste it below
10. Click on the key → **"API restrictions"** → **"Restrict key"** → select only **"Cloud Text-to-Speech API"** → **"Save"**

> 💰 **FREE: 1 million characters/month (Standard voices) — that's ~600+ flashcard decks!**
        """)

        with st.expander("⚠️ Why a separate project from Gemini?"):
            st.markdown("""
Enabling billing on a Google Cloud project upgrades **ALL** APIs in that project to the paid tier.

If Gemini and TTS share one project:
- You enable billing for TTS → Gemini silently loses its free 1,500 requests/day
- Gemini starts charging per request → unexpected costs

**Two projects = both services stay free:**
- **Project A (Gemini):** No billing → free 1,500 requests/day
- **Project B (TTS):** Billing enabled → free 1M characters/month
            """)

        with st.expander("🛡️ Optional: Set a daily spend limit"):
            st.markdown("""
1. Open [Google Cloud Console](https://console.cloud.google.com/) → select your TTS project
2. Go to **APIs & Services** → click **"Cloud Text-to-Speech API"**
3. Click the **"Quotas & System Limits"** tab
4. Find **"Characters synthesized per day"** → click ✏️
5. Set e.g. **50,000** characters/day → click **"Save"**

This caps your daily usage. Even without a limit, the first 1M characters/month are free.
            """)

    tts_key_input = st.text_input(
        "TTS API Key",
        value=tts_key,
        type="password",
        help="Your API key from the billing-enabled TTS project",
        key="google_tts_key_input"
    )

    col_save_tts, col_test_tts = st.columns([1, 1])
    with col_save_tts:
        if st.button("💾 Save TTS Key", help="Save the TTS API key", key="settings_save_tts"):
            if tts_key_input:
                st.session_state.google_tts_api_key = tts_key_input
                os.environ["GOOGLE_TTS_API_KEY"] = tts_key_input
                if _save_key_to_env("GOOGLE_TTS_API_KEY", tts_key_input):
                    st.success("✅ TTS API key saved!")
                    time.sleep(1)
                    st.rerun()
            else:
                st.error("❌ Please enter your TTS API key")

    with col_test_tts:
        if tts_key_input or tts_key:
            test_tts = tts_key_input or tts_key
            if st.button("🧪 Test TTS", help="Test your TTS API key", key="settings_test_tts"):
                with st.spinner("Testing TTS API..."):
                    try:
                        import requests
                        url = f"https://texttospeech.googleapis.com/v1/voices?key={test_tts}"
                        resp = requests.get(url, timeout=10)
                        if resp.status_code == 200:
                            st.success("✅ TTS API connection successful!")
                        else:
                            st.error(f"❌ TTS test failed: HTTP {resp.status_code}")
                    except Exception as e:
                        st.error(f"❌ TTS test failed: {str(e)}")

    st.markdown("---")

    # ==========================================================
    # SECTION 3: Pixabay — FREE Images
    # ==========================================================
    st.markdown("### 🖼️ Pixabay — FREE Images")

    with st.expander("📖 How to get your Pixabay API key", expanded=not bool(pixabay_key)):
        st.markdown("""
1. Go to [Pixabay API Documentation](https://pixabay.com/api/docs/)
2. Click **"Get Started for Free"** or go to [pixabay.com/api/](https://pixabay.com/api/)
3. Sign up for a free account (email verification required)
4. Once signed in, visit [pixabay.com/api/docs/](https://pixabay.com/api/docs/)
5. Find your API key in the "Parameters" section
6. Copy and paste the key below

> ✅ **Free: 5,000 images/month**
        """)

    pixabay_key_input = st.text_input(
        "Pixabay API Key",
        value=pixabay_key,
        type="password",
        help="Your free Pixabay API key for image generation",
        key="pixabay_key_input"
    )

    col_save_pix, col_test_pix = st.columns([1, 1])
    with col_save_pix:
        if st.button("💾 Save Pixabay Key", help="Save the Pixabay API key", key="settings_save_pixabay"):
            if pixabay_key_input:
                st.session_state.pixabay_api_key = pixabay_key_input
                if _save_key_to_env("PIXABAY_API_KEY", pixabay_key_input):
                    st.success("✅ Pixabay API key saved!")
                    time.sleep(1)
                    st.rerun()
            else:
                st.error("❌ Please enter a Pixabay API key")

    with col_test_pix:
        if pixabay_key_input or pixabay_key:
            test_key = pixabay_key_input or pixabay_key
            if st.button("🧪 Test Pixabay", help="Test your Pixabay API key", key="settings_test_pixabay"):
                with st.spinner("Testing Pixabay API..."):
                    try:
                        import requests
                        response = requests.get(
                            "https://pixabay.com/api/",
                            params={"key": test_key, "q": "test", "image_type": "photo", "per_page": 3}
                        )
                        if response.status_code == 200:
                            data = response.json()
                            if "hits" in data:
                                st.success("✅ Pixabay API connection successful!")
                            else:
                                st.error("❌ Pixabay test failed: Invalid response")
                        else:
                            st.error(f"❌ Pixabay test failed: HTTP {response.status_code}")
                    except Exception as e:
                        st.error(f"❌ Pixabay test failed: {str(e)}")

    st.markdown("---")
    st.markdown("## 🎨 Theme")
    st.info("Choose your preferred theme for the application interface.")

    if prefs_manager:
        theme_options = ["Light", "Dark"]
        current_theme = prefs_manager.get_theme().capitalize()

        selected_theme = st.selectbox(
            "Select Theme",
            theme_options,
            index=theme_options.index(current_theme),
            key="theme_select",
            help="Switch between light and dark themes"
        )

        if selected_theme.lower() != prefs_manager.get_theme():
            prefs_manager.set_theme(selected_theme.lower())
            st.success(f"Theme changed to {selected_theme}! Refresh the page to apply changes.")
            st.rerun()
    else:
        st.warning("Theme settings unavailable - using system default")

    st.markdown("---")

    # --- Favorite Languages Section ---
    st.markdown("## 🌟 Favorite Languages (Pinned for Quick Access)")
    st.info("Select your favorite languages below. They'll appear first in all dropdowns for faster selection.")

    if prefs_manager:
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
        current_favorites = prefs_manager.get_favorite_languages()
        current_names = [lang["name"] for lang in current_favorites]

        # Create multiselect for managing favorites
        selected_favorites = st.multiselect(
            "Select your favorite languages (max 5):",
            options=all_lang_names,
            default=current_names,
            max_selections=5,
            key="favorite_languages_multiselect",
            help="These languages will appear first in all dropdowns for faster selection"
        )

        # Update favorites when multiselect changes
        prefs_manager.update_favorite_languages(selected_favorites)

        # Display current favorites as clean numbered list (read-only)
        current_favorites = prefs_manager.get_favorite_languages()
        if current_favorites:
            st.markdown("**Current Favorites:**")
            for idx, lang in enumerate(current_favorites, 1):
                st.markdown(f"**{idx}. {lang['name']}**")

        st.caption(f"{len(current_favorites)}/5 favorites selected")
    else:
        st.warning("Favorite languages management unavailable - preferences service not loaded")

    st.markdown("---")

    # --- Default Settings Per Language (original design) ---
    st.markdown("## ⚙️ Default Settings Per Language")
    st.info("Select a language, adjust its default settings, and save.")

    if prefs_manager:
        lang_names = prefs_manager.get_language_names()
        selected_lang = st.selectbox("Select language to edit settings", lang_names, key="perlang_settings_select")

        # Load or initialize settings for selected language
        settings = prefs_manager.get_per_language_settings(selected_lang)

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

            difficulty_options = prefs_manager.get_difficulty_options()

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

                # Topic limit validation
                is_valid, error_msg = prefs_manager.validate_topic_selection(
                    settings["selected_topics"],
                    settings.get("custom_topics", [])
                )
                if not is_valid:
                    st.warning(f"⚠️ {error_msg}")
                else:
                    current_topic_count = len(settings["selected_topics"])
                    TOPIC_LIMIT = 5
                    if current_topic_count < TOPIC_LIMIT:
                        st.info(f"📊 **Topics selected:** {current_topic_count}/{TOPIC_LIMIT}")
            else:
                # When topics are disabled, allow all selections
                is_valid = True

            # Get curated topics
            curated_topics = prefs_manager.get_curated_topics()

            # Curated topics selection in two columns
            st.markdown("**Select topics:**")
            col1, col2 = st.columns(2)

            # Split curated topics into two columns
            mid_point = len(curated_topics) // 2
            left_topics = curated_topics[:mid_point]
            right_topics = curated_topics[mid_point:]

            with col1:
                for topic in left_topics:
                    is_selected = topic in settings["selected_topics"]
                    disabled = not is_valid and not is_selected

                    if st.checkbox(
                        topic,
                        value=is_selected,
                        key=f"perlang_topic_{topic}",
                        disabled=disabled
                    ):
                        if topic not in settings["selected_topics"] and is_valid:
                            settings["selected_topics"].append(topic)
                        elif topic in settings["selected_topics"]:
                            settings["selected_topics"].remove(topic)

            with col2:
                for topic in right_topics:
                    is_selected = topic in settings["selected_topics"]
                    disabled = not is_valid and not is_selected

                    if st.checkbox(
                        topic,
                        value=is_selected,
                        key=f"perlang_topic_{topic}_right",
                        disabled=disabled
                    ):
                        if topic not in settings["selected_topics"] and is_valid:
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
                    disabled=not is_valid
                )

                if st.button("➕ Add Topic", key=f"perlang_add_custom_{selected_lang}", disabled=not is_valid):
                    success, message = prefs_manager.add_custom_topic(new_topic, selected_lang)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

            with col_list:
                custom_topics = settings.get("custom_topics", [])
                if custom_topics:
                    st.markdown("**Your Custom Topics:**")
                    for i, topic in enumerate(custom_topics):
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
                                prefs_manager.remove_custom_topic(topic, selected_lang)
                                st.rerun()

        st.markdown("---")

        # --- Image Settings ---
        with st.container():
            st.markdown("## 🖼️ Image Settings")
            st.markdown("*Image generation uses Pixabay API for high-quality, free images*")

            st.info("🖼️ **Image Generation**: Uses Pixabay API with 5,000 free images per month. Requires Pixabay API key (set in API Setup).")

        st.markdown("---")

        if st.button("Save Settings", key="perlang_save_btn", type="primary"):
            prefs_manager.save_per_language_settings(selected_lang, settings)
            st.success(f"Settings saved for {selected_lang}!")
    else:
        st.warning("Per-language settings unavailable - preferences service not loaded")
    st.markdown("---")

    # --- Guest Data Export/Import Section (for non-signed-in users) ---
    try:
        if sync_manager and not sync_manager.is_user_signed_in():
            st.markdown("## 💾 Guest Data Backup")
            st.info("As a guest user, your data is stored locally. Export your settings to backup or transfer to another device.")

            guest_col1, guest_col2 = st.columns([1, 1])

            with guest_col1:
                if st.button("📤 Export Guest Data", key="export_guest_data", help="Download your settings and API keys as JSON", use_container_width=True):
                    guest_data = sync_manager.export_guest_data()
                    if guest_data:
                        st.download_button(
                            label="📥 Download Backup",
                            data=guest_data,
                            file_name=f"language_app_guest_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json",
                            key="download_guest_backup"
                        )
                        st.success("✅ Guest data exported! Download the file above.")
                    else:
                        st.error("❌ Failed to export guest data.")

            with guest_col2:
                uploaded_backup = st.file_uploader(
                    "📥 Import Guest Data",
                    type=['json'],
                    key="import_guest_data",
                    help="Upload a previously exported guest data file to restore your settings"
                )

                if uploaded_backup:
                    try:
                        if sync_manager.import_guest_data(uploaded_backup.getvalue().decode('utf-8')):
                            st.success("✅ Guest data imported successfully!")
                            st.info("🔄 Refreshing page to apply imported settings...")
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error("❌ Failed to import guest data.")

                    except Exception as e:
                        st.error(f"❌ Failed to import backup: {e}")
                        st.info("Make sure you're uploading a valid guest data export file.")

    except Exception as e:
        st.error(f"Guest data management error: {e}")

    st.markdown("---")

    # --- Cache Management Section ---
    st.markdown("## 💾 API Response Cache")
    st.info("Caching reduces API costs and speeds up deck generation by reusing previous results. Cache expires automatically.")

    try:
        if cache_service and cache_service.is_cache_available():
            stats = cache_service.get_cache_stats()

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
                    cleared = cache_service.clear_all_cache()
                    st.success(f"Cleared {cleared} cached entries!")
                    st.rerun()

            with cache_col2:
                if st.button("🧹 Clear Expired", key="clear_expired_cache", help="Remove only expired cache entries"):
                    cache_service.clear_expired_cache()
                    st.success("Cleaned up expired cache entries!")
                    st.rerun()

            with cache_col3:
                if st.button("📊 Refresh Stats", key="refresh_cache_stats", help="Update cache statistics display"):
                    st.rerun()

            # Namespace-specific clearing
            st.markdown("**Clear Specific Cache Types:**")
            ns_col1, ns_col2, ns_col3 = st.columns(3)

            with ns_col1:
                if st.button("🗣️ Clear Gemini Cache", key="clear_gemini_cache", help="Clear cached Gemini API responses"):
                    cleared = cache_service.clear_gemini_cache()
                    st.success(f"Cleared {cleared} Gemini cached entries!")

            with ns_col2:
                if st.button(" View Details", key="view_cache_details", help="Show detailed cache information"):
                    with st.expander("Cache Details", expanded=True):
                        st.json(stats)
        else:
            st.error("Cache management unavailable.")
            st.info("Cache functionality requires proper initialization. Try restarting the app.")

    except Exception as e:
        st.error(f"Cache management unavailable: {e}")
        st.info("Cache functionality requires proper initialization. Try restarting the app.")