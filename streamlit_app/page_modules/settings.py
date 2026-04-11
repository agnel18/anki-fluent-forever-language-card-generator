# pages/settings.py - Settings page for the language learning app

import streamlit as st
import time
import os
import json
from pathlib import Path


# Import centralized configuration
from streamlit_app.shared_utils import get_gemini_model


def render_settings_page():
    """Render the settings page with API keys, theme, and cache management."""
    st.title("Settings")

    # Back button
    if st.button("← Back to Main", key="back_to_main"):
        st.session_state.page = "main"
        st.rerun()

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
                os.environ["GEMINI_API_KEY"] = google_key_input
                if _save_key_to_env("GEMINI_API_KEY", google_key_input):
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

    # --- Theme Section ---
    st.markdown("## 🎨 Theme")
    st.info("Choose your preferred theme for the application interface.")

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
        st.success(f"Theme changed to {selected_theme}! Refresh the page to apply changes.")
        st.rerun()

    st.markdown("---")

    # ==========================================================
    # PER-LANGUAGE DEFAULT OUTPUT SETTINGS — Final Improved UX
    # Single global JSON file for all languages
    # ==========================================================
    st.markdown("---")
    st.markdown("## 🌍 Per-Language Default Output Settings")
    st.caption("Set once. Reuse forever. All languages share one global `language_defaults.json` file.")

    # Safe initialization
    if "per_language_settings" not in st.session_state:
        st.session_state.per_language_settings = {}

    # === Friendly Summary + Quick Actions ===
    configured_langs = list(st.session_state.per_language_settings.keys())
    total_custom = len(configured_langs)
    total_langs = len(st.session_state.get("all_languages", []))

    col_summary, col_download = st.columns([3, 1])
    with col_summary:
        if total_custom == 0:
            st.info("📭 No custom defaults saved yet.")
        else:
            st.success(f"✅ **{total_custom}** of {total_langs} languages have custom defaults")
            if configured_langs:
                st.caption("Configured: " + " • ".join(configured_langs[:8]) + (" …" if len(configured_langs) > 8 else ""))

    with col_download:
        if st.button("⬇️ Download Global JSON", use_container_width=True):
            data = json.dumps(st.session_state.per_language_settings, indent=2, ensure_ascii=False)
            st.download_button(
                label="language_defaults.json",
                data=data,
                file_name="language_defaults.json",
                mime="application/json",
                key="global_download_top"
            )

    # Language selector
    all_languages = st.session_state.get("all_languages", [])
    lang_names = [lang["name"] for lang in all_languages] if all_languages else ["English", "Spanish", "French", "German", "Italian"]
    
    config_lang = st.selectbox(
        "Language",                    # hidden label
        options=lang_names,
        key="per_lang_default_select",
        label_visibility="collapsed"   # removes the default label
    )

    defaults = st.session_state.per_language_settings.get(config_lang, {})

    # Sentence Settings
    st.markdown("### ✍️ Sentence Settings")
    col1, col2 = st.columns(2)
    with col1:
        sentence_min = st.slider("Min words", 3, 20, value=int(defaults.get("sentence_length_range", (4, 20))[0]), key=f"def_min_{config_lang}")
    with col2:
        sentence_max = st.slider("Max words", 8, 30, value=int(defaults.get("sentence_length_range", (4, 20))[1]), key=f"def_max_{config_lang}")

    sentences_per_word = st.slider("Sentences per word", 3, 15, value=defaults.get("sentences_per_word", 5), key=f"def_spw_{config_lang}")

    # Difficulty
    st.markdown("### 🎯 Difficulty Level")
    difficulty_options = ["beginner", "intermediate", "advanced"]
    difficulty_idx = difficulty_options.index(defaults.get("difficulty", "beginner"))
    difficulty = st.selectbox(
        "Select Difficulty",
        options=difficulty_options,
        index=difficulty_idx,
        format_func=lambda x: {"beginner": "Beginner — Simple vocabulary", "intermediate": "Intermediate — Mixed tenses", "advanced": "Advanced — Complex structures"}[x],
        key=f"def_diff_{config_lang}"
    )

    # Audio Settings — proper dropdown
    st.markdown("### 🎵 Audio Settings")
    try:
        from audio_generator import get_google_voices_for_language
        voice_options, _, voice_display_map = get_google_voices_for_language(config_lang)
        current_display = defaults.get("selected_voice_display", voice_options[0] if voice_options else "")
        idx = voice_options.index(current_display) if current_display in voice_options else 0

        selected_voice_display = st.selectbox(
            "Voice",
            options=voice_options,
            index=idx,
            key=f"def_voice_display_{config_lang}"
        )
        selected_voice = voice_display_map.get(selected_voice_display, "en-US-Standard-D")
    except Exception:
        selected_voice_display = st.text_input("Voice (Google TTS)", value=defaults.get("selected_voice_display", ""), key=f"def_voice_display_{config_lang}")
        selected_voice = st.text_input("Voice Code", value=defaults.get("selected_voice", ""), key=f"def_voice_{config_lang}")

    audio_speed = st.slider("Audio Speed", 0.5, 1.5, value=defaults.get("audio_speed", 1.0), step=0.05, key=f"def_speed_{config_lang}")

    # Save + Recommended
    col_save, col_recommend = st.columns([2, 1])
    with col_save:
        if st.button(f"💾 Save as Defaults for **{config_lang}**", type="primary", use_container_width=True, key=f"save_def_{config_lang}"):
            st.session_state.per_language_settings[config_lang] = {
                "sentence_length_range": (sentence_min, sentence_max),
                "sentences_per_word": sentences_per_word,
                "difficulty": difficulty,
                "selected_voice": selected_voice,
                "selected_voice_display": selected_voice_display,
                "audio_speed": audio_speed
            }
            st.success(f"✅ Defaults saved for **{config_lang}**")
            st.rerun()

    with col_recommend:
        if st.button("🔄 Use Recommended Defaults", use_container_width=True):
            rec = {
                "sentence_length_range": (6, 14),
                "sentences_per_word": 5,
                "difficulty": "beginner",
                "audio_speed": 0.85
            }
            st.session_state.per_language_settings[config_lang] = rec
            st.success("✅ Recommended defaults applied")
            st.rerun()

    # === GLOBAL BACKUP / RESTORE (kept exactly as you had it) ===
    st.markdown("---")
    st.subheader("💾 Global Backup & Restore (All Languages)")
    st.caption("One file contains defaults for every language.")

    col_dl, col_ul, col_reset = st.columns([1, 1, 1])

    with col_dl:
        if st.button("⬇️ Download Global Defaults JSON"):
            data = json.dumps(st.session_state.per_language_settings, indent=2, ensure_ascii=False)
            st.download_button(
                label="Click to download language_defaults.json",
                data=data,
                file_name="language_defaults.json",
                mime="application/json",
                key="download_global_json"
            )

    with col_ul:
        uploaded_file = st.file_uploader("📥 Upload & Restore Global JSON", type=["json"], key="upload_global_json")
        if uploaded_file is not None:
            try:
                imported = json.load(uploaded_file)
                st.session_state.per_language_settings.update(imported)
                st.success("✅ All language defaults restored from JSON!")
                
            except Exception as e:
                st.error(f"Failed to load JSON: {e}")

    with col_reset:
        if st.button("🗑️ Reset All Defaults", type="secondary"):
            if st.checkbox("I am sure I want to delete ALL custom defaults", key="confirm_reset"):
                st.session_state.per_language_settings = {}
                st.success("All defaults have been reset.")
                st.rerun()

    st.caption("Tip: After saving in Step 3, use the button at the top or here to download the updated global file.")

    st.markdown("---")

    # --- Cache Management Section ---
    st.markdown("## 💾 API Response Cache")
    st.info("Caching reduces API costs and speeds up deck generation by reusing previous results.")

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

        if st.button("🔄 Clear All Cache", key="clear_all_cache", help="Delete all cached API responses"):
            if hasattr(cache_mgr, 'clear') and cache_mgr.clear():
                st.success("Cache cleared!")
            elif hasattr(cache_mgr, 'clear_all'):
                cache_mgr.clear_all()
                st.success("Cache cleared!")
            else:
                st.warning("Cache clear not available.")
            st.rerun()

    except Exception as e:
        st.info("Cache management unavailable. Cache will work automatically during generation.")
