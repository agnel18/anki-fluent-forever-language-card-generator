# pages/api_setup.py - API setup page for the language learning app

import streamlit as st
from constants import PAGE_LANGUAGE_SELECT

# Import centralized configuration
from streamlit_app.shared_utils import get_gemini_model, get_gemini_api


def render_api_setup_page():
    """Render the API keys setup page."""

    # Check if we have real API keys (not fallback keys)
    google_key = st.session_state.get("google_api_key", "")
    tts_key = st.session_state.get("google_tts_api_key", "")
    pixabay_key = st.session_state.get("pixabay_api_key", "")

    has_real_api_keys = (
        google_key and
        not google_key.startswith("sk-fallback") and
        tts_key and
        pixabay_key
    )

    # Show a quick test section if keys are already configured
    if has_real_api_keys:
        st.markdown("# Step 0: API Keys")
        st.success("✅ **All API Keys Configured** — You can proceed to language selection or re-test below")
        st.divider()

        st.markdown("### 🔄 Re-test API Connections")
        col_test, col_proceed = st.columns([1, 2])
        with col_test:
            if st.button("🧪 Re-test Gemini Connection", help="Re-test your Gemini API key"):
                with st.spinner("Testing Gemini API connection..."):
                    try:
                        import warnings
                        warnings.filterwarnings("ignore", category=FutureWarning)
                        api = get_gemini_api()
                        api.configure(api_key=google_key)
                        api.generate_content(model=get_gemini_model(), contents="Hello")
                        st.success("✅ Gemini API connection successful!")
                    except Exception as e:
                        st.error(f"❌ Gemini API test failed: {str(e)}")

        with col_proceed:
            if st.button("🚀 Proceed to Language Selection", use_container_width=True):
                st.session_state.page = PAGE_LANGUAGE_SELECT
                st.rerun()

        st.divider()
        return

    # ==========================================
    # MAIN SETUP PAGE (keys not yet configured)
    # ==========================================
    st.markdown("# Step 0: API Keys")
    st.divider()

    # --- Status Overview (vertical — mobile friendly) ---
    google_key = st.session_state.get("google_api_key", "")
    tts_key = st.session_state.get("google_tts_api_key", "")
    pixabay_key = st.session_state.get("pixabay_api_key", "")

    if google_key:
        st.success("✅ **Gemini AI** — Set")
    else:
        st.error("❌ **Gemini AI** — Required")
    if tts_key:
        st.success("✅ **Text-to-Speech** — Set")
    else:
        st.error("❌ **Text-to-Speech** — Required")
    if pixabay_key:
        st.success("✅ **Pixabay Images** — Set")
    else:
        st.error("❌ **Pixabay Images** — Required")

    st.markdown("---")

    # ==========================================================
    # SECTION 1: Gemini AI — FREE & SUPER SIMPLE (30 seconds)
    # ==========================================================
    st.markdown("### 🤖 Gemini AI — FREE (no billing needed)")

    with st.expander("📖 How to get your Gemini API key (30 seconds)", expanded=not bool(google_key)):
        st.markdown("""
    **✅ Easiest way — no projects, no billing, no OAuth consent screen:**

    1. Go to **[https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)**
    2. Sign in with your Google account (Gmail works)
    3. Click **"Create API key"**
    4. Copy the key (it starts with `AIza...`)
    5. Paste it below

    > **Free tier: ~1,500 requests/day** — perfect for creating Malayalam (and all 77 languages) decks.
        """)

    google_key_input = st.text_input(
        "Gemini API Key",
        value=google_key,
        type="password",
        help="Get it instantly at aistudio.google.com/app/apikey",
        key="google_api_key_input"
    )

    if google_key_input and not google_key_input.startswith('AIza'):
        st.warning("⚠️ Google API keys typically start with 'AIza'. Please verify your key.")

    col_save, col_test = st.columns([1, 1])
    with col_save:
        if st.button("💾 Save Gemini Key", help="Save the Gemini API key"):
            if google_key_input.strip():
                st.session_state.google_api_key = google_key_input.strip()
                st.success("✅ Gemini key saved!")
            else:
                st.error("Please enter a key")

    with col_test:
        if google_key_input or google_key:
            test_key = google_key_input or google_key
            if st.button("🧪 Test Gemini", help="Test your Gemini API key"):
                with st.spinner("Testing Gemini API..."):
                    try:
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
        key="google_tts_api_key_input"
    )

    if tts_key_input and not tts_key_input.startswith('AIza'):
        st.warning("⚠️ Google API keys typically start with 'AIza'. Please verify your key.")

    col_save_tts, col_test_tts = st.columns([1, 1])
    with col_save_tts:
        if st.button("💾 Save TTS Key", help="Save the TTS API key"):
            if tts_key_input:
                st.session_state.google_tts_api_key = tts_key_input
                st.success("✅ TTS API key saved!")
            else:
                st.error("❌ Please enter your TTS API key")

    with col_test_tts:
        if tts_key_input or tts_key:
            test_tts = tts_key_input or tts_key
            if st.button("🧪 Test TTS", help="Test your TTS API key"):
                with st.spinner("Testing TTS API..."):
                    try:
                        import requests as req
                        url = f"https://texttospeech.googleapis.com/v1/voices?key={test_tts}"
                        resp = req.get(url, timeout=10)
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
        key="pixabay_api_key_input"
    )

    col_save_pixabay, col_test_pixabay = st.columns([1, 1])
    with col_save_pixabay:
        if st.button("💾 Save Pixabay Key", help="Save the Pixabay API key"):
            if pixabay_key_input:
                st.session_state.pixabay_api_key = pixabay_key_input
                st.success("✅ Pixabay API key saved!")
            else:
                st.error("❌ Please enter a Pixabay API key")

    with col_test_pixabay:
        if pixabay_key_input or pixabay_key:
            test_key = pixabay_key_input or pixabay_key
            if st.button("🧪 Test Pixabay", help="Test your Pixabay API key"):
                with st.spinner("Testing Pixabay API..."):
                    try:
                        import requests
                        params = {
                            'key': test_key,
                            'q': 'test',
                            'image_type': 'photo',
                            'per_page': 3
                        }
                        response = requests.get("https://pixabay.com/api/", params=params)
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

    # Auto-load from environment (dev mode)
    import os
    google_env = os.environ.get("GOOGLE_API_KEY", "")
    if (google_env and not google_key and not google_env.startswith("sk-fallback")):
        st.info("ℹ️ **Development Mode** — API key auto-loaded from environment")
        st.session_state.google_api_key = google_env
        st.session_state.page = PAGE_LANGUAGE_SELECT
        st.rerun()
        return

    st.divider()

    if st.button("🚀 Next: Select Language", use_container_width=True):
        final_google_key = google_key_input or google_key
        final_tts_key = tts_key_input or tts_key
        final_pixabay_key = pixabay_key_input or pixabay_key

        if not final_google_key:
            st.error("❌ Please enter your **Gemini API key** (Section 1 above)")
            st.stop()

        if not final_tts_key:
            st.error("❌ Please enter your **TTS API key** (Section 2 above)")
            st.stop()

        if not final_pixabay_key:
            st.error("❌ Please enter your **Pixabay API key** (Section 3 above)")
            st.stop()

        st.session_state.google_api_key = final_google_key
        st.session_state.google_tts_api_key = final_tts_key
        st.session_state.pixabay_api_key = final_pixabay_key

        st.success("✅ API keys saved!")

        st.session_state.page = PAGE_LANGUAGE_SELECT
        st.rerun()