# pages/api_setup.py - API setup page for the language learning app

import streamlit as st
import json
from pathlib import Path
from utils import get_secret
from constants import PAGE_LANGUAGE_SELECT

# Import centralized configuration
from streamlit_app.shared_utils import get_gemini_model, get_gemini_api


def render_api_setup_page():
    """Render the API keys setup page."""
    st.write("🔧 API Setup Page Loaded")  # Debug message
    st.markdown("### Please enter your API keys below:")

    # Check if we have real API keys (not fallback keys)
    google_key = st.session_state.get("google_api_key", "")
    pixabay_key = st.session_state.get("pixabay_api_key", "")

    # Also check TTS configuration
    tts_configured = False
    try:
        from audio_generator import is_google_tts_configured
        tts_configured = is_google_tts_configured()
    except:
        tts_configured = False

    has_real_api_keys = (
        google_key and
        not google_key.startswith("sk-fallback") and
        pixabay_key and
        tts_configured
    )

    # Show a quick test section even if keys are already configured
    if has_real_api_keys:
        st.markdown("# 🌍 Language Anki Deck Generator")
        st.markdown("Create custom Anki decks in minutes | Free, no data stored")
        st.success("✅ **API Keys Already Configured** - You can proceed to language selection or re-test your connection below")
        st.divider()

        # Quick re-test section
        st.markdown("### 🔄 Re-test API Connection")
        col_test, col_proceed = st.columns([1, 2])
        with col_test:
            if st.button("🧪 Re-test Google Cloud Connection", help="Re-test your Google Cloud API key"):
                with st.spinner("Testing Google Cloud API connection..."):
                    try:
                        import warnings
                        warnings.filterwarnings("ignore", category=FutureWarning)
                        api = get_gemini_api()
                        api.configure(api_key=google_key)
                        response = api.generate_content(
                            model=get_gemini_model(),
                            contents="Hello"
                        )
                        st.success("✅ Google Cloud API connection successful!")
                    except Exception as e:
                        st.error(f"❌ Google Cloud API test failed: {str(e)}")

        with col_proceed:
            if st.button("🚀 Proceed to Language Selection", use_container_width=True):
                st.session_state.page = PAGE_LANGUAGE_SELECT
                st.rerun()

        st.divider()
        return

    st.markdown("# 🌍 Language Anki Deck Generator")
    st.markdown("Create custom Anki decks in minutes | Free, no data stored")
    st.divider()
    st.markdown("## 🔐 API Keys Setup")
    st.markdown("*Configure a single Google Cloud API key with access to Gemini API and Cloud Text-to-Speech API*")

    # Firebase sync status and loading
    try:
        from firebase_manager import init_firebase
        firebase_available = init_firebase()
        if firebase_available:
            st.success("✅ **Cloud Sync Available** - Your API keys can be securely stored and synced across devices")

            # Load from Firebase option
            if st.button("📥 Load API Keys from Cloud", help="Load your previously saved API keys from Firebase"):
                try:
                    from firebase_manager import load_settings_from_firebase
                    cloud_settings = load_settings_from_firebase(st.session_state.session_id)
                    if cloud_settings and 'google_api_key' in cloud_settings:
                        st.session_state.google_api_key = cloud_settings['google_api_key']
                        st.success("✅ API keys loaded from cloud!")
                        st.session_state.page = PAGE_LANGUAGE_SELECT
                        st.rerun()
                    else:
                        st.warning("No API keys found in cloud. Please enter your key below.")
                except Exception as e:
                    st.error(f"Failed to load from cloud: {e}")
        else:
            st.info("🔄 **Local Storage Only** - API keys will be saved locally on this device")
    except Exception as e:
        st.info("🔄 **Local Storage Only** - Firebase unavailable")

    # Status overview
    google_key = st.session_state.get("google_api_key", "")
    pixabay_key = st.session_state.get("pixabay_api_key", "")

    if google_key:
        st.success("✅ **Google Cloud API** - Set")
    else:
        st.error("❌ **Google Cloud API** - Required")

    if pixabay_key:
        st.success("✅ **Pixabay API** - Set")
    else:
        st.error("❌ **Pixabay API** - Required")

    st.markdown("---")

    # === GOOGLE CLOUD API SECTION ===
    st.markdown("### ☁️ Google Cloud APIs (AI Generation & Audio)")

    # Quick Start Summary
    st.info("**🚀 Quick Start:** Get API key → Enable 2 APIs → Restrict key → Test connection")

    # Consolidated Setup Instructions Expander
    with st.expander("📖 Setup Instructions", expanded=not bool(google_key)):
        # Step 1: Setup Instructions
        st.markdown("#### 📖 Step 1: Get Your API Key")
        st.markdown("""
        **Follow these steps to get your Google Cloud API key:**

        1. **Go to** [Google Cloud Console](https://console.cloud.google.com/)
        2. **Create a new project** or select an existing one
        3. **Enable exactly these two APIs:**
           - **Gemini API** - For AI text generation and translations
           - **Cloud Text-to-Speech API** - For audio generation

        > [!IMPORTANT]
        > Do NOT enable other Google Cloud APIs unless you specifically need them for other projects.

        4. **Create credentials:**
           - Go to "APIs & Services" → "Credentials"
           - Click "Create Credentials" → "API key"
        5. **Copy and paste** the key into the field below
        """)

        st.markdown("---")

        # Step 2: Enable Billing & Set Up Budget Alerts
        st.markdown("#### 💰 Step 2: Enable Billing & Set Hard Quota Limits")
        st.markdown("""
        **Google requires billing to be enabled for API access, even for FREE usage.** Setting a hard quota is the safest way to make sure you're never charged more than you expect — we've seen users accidentally receive bills of ₹600+ (≈ $7) because alerts arrived too late.

        ### Quick Billing Setup:
        1. **Go to** [Google Cloud Console](https://console.cloud.google.com/)
        2. **Click "Billing"** → **"Create Billing Account"**
        3. **Add your credit/debit card** (won't be charged until you exceed ALL free limits)
        4. **Complete verification**

        ### ✅ Set Hard Quotas (Strongly Recommended — Better Than Budget Alerts):

        > 💡 **Why quotas?** Budget alerts only *email* you after spending starts. Hard quotas *block* the API before charges accumulate — like a spending cap, not just a warning.

        **For Gemini AI (text generation):**
        1. Go to [APIs & Services → Enabled APIs](https://console.cloud.google.com/apis/dashboard)
        2. Click **"Generative Language API"**
        3. Click the **"Quotas & System Limits"** tab
        4. Find **"Generate content requests per day per project"**
        5. Click the ✏️ pencil icon → enter your limit (e.g., **500** for casual use)
        6. Click **"Save"**

        **For Text-to-Speech (audio generation):**
        1. Go to [APIs & Services → Enabled APIs](https://console.cloud.google.com/apis/dashboard)
        2. Click **"Cloud Text-to-Speech API"**
        3. Click the **"Quotas & System Limits"** tab
        4. Find **"Characters synthesized per day"**
        5. Click ✏️ → enter your limit (e.g., **50,000** characters/day ≈ 30–50 cards)
        6. Click **"Save"**

        **Free Tier Limits:** 1,500 Gemini requests/day and 1 million TTS characters/month — hard quotas keep you safely below these!
        """)

        st.markdown("---")

        # Step 3: API Key Security (CRITICAL)
        st.markdown("#### 🔒 Step 3: API Key Security (CRITICAL)")
        st.markdown("""
        **Restrict your API key to prevent unauthorized usage and reduce security risks:**

        1. **Go to** [Google Cloud Console](https://console.cloud.google.com/)
        2. **Navigate to** "APIs & Services" → "Credentials"
        3. **Click on your API key** to edit it
        4. **Under "API restrictions":**
           - Select **"Restrict key"**
           - Check ONLY these two APIs:
             - ✅ **Generative Language API**
             - ✅ **Cloud Text-to-Speech API**
        5. **Click "Save"**

        > [!WARNING]
        > An unrestricted API key can be used for expensive Google Cloud services like GPUs, Maps, or other APIs. Always restrict your keys!
        """)

    google_key_input = st.text_input(
        "Google Cloud API Key",
        value=google_key,
        type="password",
        help="Paste your Google Cloud API key here (used for Gemini AI and Text-to-Speech)",
        key="google_api_key_input"
    )

    # API Key Validation
    if google_key_input and not google_key_input.startswith('AIza'):
        st.warning("⚠️ Google API keys typically start with 'AIza'. Please verify your key.")

    col_save, col_test = st.columns([1, 1])
    with col_save:
        if st.button("💾 Save Google Cloud Key", help="Save the Google Cloud API key"):
            if google_key_input:
                if not google_key_input.startswith('AIza'):
                    st.warning("⚠️ This doesn't look like a valid Google API key format. Please verify.")
                st.session_state.google_api_key = google_key_input
                st.success("✅ Google Cloud API key saved!")
            else:
                st.error("❌ Please enter a Google Cloud API key")

    with col_test:
        if google_key_input or google_key:
            test_key = google_key_input or google_key
            if st.button("🧪 Test Google Cloud Connection", help="Test your Google Cloud API key"):
                with st.spinner("Testing Google Cloud API connection..."):
                    try:
                        api = get_gemini_api()
                        api.configure(api_key=test_key)
                        api.generate_content(
                            model=get_gemini_model(),
                            contents="Hello"
                        )
                        st.success("✅ Google Cloud API connection successful!")
                    except Exception as e:
                        st.error(f"❌ Google Cloud API test failed: {str(e)}")

    st.markdown("---")

    # === PIXABAY API SECTION ===
    st.markdown("### 🖼️ Pixabay API (Image Generation)")
    with st.expander("📖 How to Get Your Free Pixabay API Key", expanded=not bool(pixabay_key)):
        st.markdown("""
        **Follow these steps to get your free Pixabay API key:**

        1. **Go to** [Pixabay API Documentation](https://pixabay.com/api/docs/)
        2. **Click "Get Started for Free"** or go to [pixabay.com/api/](https://pixabay.com/api/)
        3. **Sign up** for a free account (email verification required)
        4. **Once signed in**, visit [https://pixabay.com/api/docs/](https://pixabay.com/api/docs/)
        5. **Find your API key** in the "Parameters" section on that page
        6. **Copy and paste** the key into the field below

        **Free Plan:** 5,000 images/month, then $0.001 per additional image.
        """)

    pixabay_key_input = st.text_input(
        "Pixabay API Key",
        value=pixabay_key,
        type="password",
        help="Required: Your free Pixabay API key for image generation",
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
            if st.button("🧪 Test Pixabay Connection", help="Test your Pixabay API key"):
                with st.spinner("Testing Pixabay API connection..."):
                    try:
                        import requests
                        # Use Pixabay API with proper parameters
                        params = {
                            'key': test_key,
                            'q': 'test',  # Simple search term
                            'image_type': 'photo',
                            'per_page': 3  # Minimum allowed by Pixabay API
                        }
                        response = requests.get("https://pixabay.com/api/", params=params)
                        if response.status_code == 200:
                            data = response.json()
                            if "hits" in data and len(data["hits"]) > 0:
                                st.success("✅ Pixabay API connection successful!")
                            elif "hits" in data:
                                st.success("✅ Pixabay API connection successful! (No results for 'test' query)")
                            else:
                                st.error("❌ Pixabay API test failed: Invalid response format")
                        else:
                            error_msg = f"HTTP {response.status_code}"
                            try:
                                error_data = response.json()
                                if "message" in error_data:
                                    error_msg += f": {error_data['message']}"
                            except:
                                pass
                            st.error(f"❌ Pixabay API test failed: {error_msg}")
                    except Exception as e:
                        st.error(f"❌ Pixabay API test failed: {str(e)}")

    st.markdown("---")
    google_env = get_secret("GOOGLE_API_KEY", "")

    # Only auto-load from environment if it's a real key (not fallback)
    if (google_env and not google_key and
        not google_env.startswith("sk-fallback")):
        st.info("ℹ️ **Development Mode Detected** - Your API key was auto-loaded from environment")
        google_key = google_env
        # Auto-submit if we have valid key
        if google_key:
            st.session_state.google_api_key = google_key
            st.session_state.page = PAGE_LANGUAGE_SELECT
            st.rerun()
            return
    st.divider()

    # Cloud sync option
    save_to_cloud = False
    try:
        from firebase_manager import init_firebase
        if init_firebase():
            save_to_cloud = st.checkbox("💾 Also save API keys to cloud for cross-device sync", value=True,
                                      help="Your API keys will be encrypted and stored securely in Firebase")
    except Exception:
        pass

    if st.button("🚀 Next: Select Language", use_container_width=True):
        # Use the input values, falling back to session state if input is empty
        final_google_key = google_key_input or google_key
        final_pixabay_key = pixabay_key_input or pixabay_key

        if not final_google_key:
            st.error("❌ Please enter your Google Cloud API key")
            st.stop()

        if not final_pixabay_key:
            st.error("❌ Please enter your Pixabay API key")
            st.stop()

        st.session_state.google_api_key = final_google_key
        st.session_state.pixabay_api_key = final_pixabay_key

        # Save API keys locally
        secrets_path = Path(__file__).parent.parent / "user_secrets.json"
        user_secrets = {
            "google_api_key": final_google_key,
            "pixabay_api_key": final_pixabay_key
        }
        with open(secrets_path, "w", encoding="utf-8") as f:
            json.dump(user_secrets, f, indent=2)

            # Save to Firebase if requested
            if save_to_cloud:
                try:
                    from firebase_manager import save_settings_to_firebase
                    cloud_data = {
                        "google_api_key": final_google_key,
                        "pixabay_api_key": final_pixabay_key
                    }
                    save_settings_to_firebase(st.session_state.session_id, cloud_data)
                    st.success("✅ API keys saved locally and to cloud!")
                except Exception as e:
                    st.warning(f"Local save successful, but cloud save failed: {e}")
            else:
                st.success("✅ API keys saved locally!")

            st.session_state.page = PAGE_LANGUAGE_SELECT
            st.rerun()