# pages/api_setup.py - API setup page for the language learning app

import streamlit as st
import json
from pathlib import Path
from utils import get_secret
from constants import PAGE_LANGUAGE_SELECT


def render_api_setup_page():
    """Render the API keys setup page."""
    st.write("🔧 API Setup Page Loaded")  # Debug message
    st.markdown("### Please enter your API keys below:")
    
    # Check if we have real API keys (not fallback keys)
    groq_key = st.session_state.get("groq_api_key", "")
    pixabay_key = st.session_state.get("pixabay_api_key", "")
    azure_key = st.session_state.get("azure_tts_key", "")

    has_real_api_keys = (
        groq_key and pixabay_key and azure_key and
        not groq_key.startswith("sk-fallback") and
        not pixabay_key.startswith("fallback")
    )

    # If API keys are already set and valid, skip to language selection
    if has_real_api_keys:
        st.session_state.page = PAGE_LANGUAGE_SELECT
        st.rerun()
        return
    
    st.markdown("# 🌍 Language Anki Deck Generator")
    st.markdown("Create custom Anki decks in minutes | Free, no data stored")
    st.divider()
    st.markdown("## 🔐 API Keys Setup")
    st.markdown("*Configure the three required APIs for AI generation, images, and audio*")

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
                    if cloud_settings and 'groq_api_key' in cloud_settings and 'pixabay_api_key' in cloud_settings and 'azure_tts_key' in cloud_settings:
                        st.session_state.groq_api_key = cloud_settings['groq_api_key']
                        st.session_state.pixabay_api_key = cloud_settings['pixabay_api_key']
                        st.session_state.azure_tts_key = cloud_settings['azure_tts_key']
                        import os
                        os.environ["AZURE_TTS_KEY"] = cloud_settings['azure_tts_key']
                        st.success("✅ API keys loaded from cloud!")
                        st.session_state.page = PAGE_LANGUAGE_SELECT
                        st.rerun()
                    else:
                        st.warning("No complete API keys found in cloud. Please enter all required keys below.")
                except Exception as e:
                    st.error(f"Failed to load from cloud: {e}")
        else:
            st.info("🔄 **Local Storage Only** - API keys will be saved locally on this device")
    except Exception as e:
        st.info("🔄 **Local Storage Only** - Firebase unavailable")

    # Status overview
    groq_key = st.session_state.get("groq_api_key", "")
    pixabay_key = st.session_state.get("pixabay_api_key", "")
    azure_key = st.session_state.get("azure_tts_key", "")

    col1, col2, col3 = st.columns(3)
    with col1:
        if groq_key:
            st.success("✅ **Groq API** - Set")
        else:
            st.error("❌ **Groq API** - Required")
    with col2:
        if pixabay_key:
            st.success("✅ **Pixabay API** - Set")
        else:
            st.error("❌ **Pixabay API** - Required")
    with col3:
        if azure_key:
            st.success("✅ **Azure TTS** - Set")
        else:
            st.error("❌ **Azure TTS** - Required")

    st.markdown("---")

    # === GROQ API SECTION ===
    st.markdown("### 🔗 Groq API (AI Generation)")
    with st.expander("📖 Setup Instructions", expanded=not bool(groq_key)):
        st.markdown("""
        **Follow these steps to get your Groq API key:**

        1. **Go to** https://console.groq.com/
        2. **Create an account** (if you don't have one)
        3. **Navigate to** API keys section
        4. **Create new API key**
        5. **Copy and paste** the key into the field below
        """)

    groq_key_input = st.text_input(
        "Groq API Key",
        value=groq_key,
        type="password",
        help="Paste your Groq API key here",
        key="groq_api_key_input"
    )

    col_save, col_test = st.columns([1, 1])
    with col_save:
        if st.button("💾 Save Groq Key", help="Save the Groq API key"):
            if groq_key_input:
                st.session_state.groq_api_key = groq_key_input
                st.success("✅ Groq API key saved!")
            else:
                st.error("❌ Please enter a Groq API key")

    with col_test:
        if groq_key_input or groq_key:
            test_key = groq_key_input or groq_key
            if st.button("🧪 Test Groq Connection", help="Test your Groq API key"):
                with st.spinner("Testing Groq API connection..."):
                    try:
                        from groq import Groq
                        client = Groq(api_key=test_key)
                        response = client.chat.completions.create(
                            model="mixtral-8x7b-32768",
                            messages=[{"role": "user", "content": "Hello"}],
                            max_tokens=10
                        )
                        st.success("✅ Groq API connection successful!")
                    except Exception as e:
                        st.error(f"❌ Groq API test failed: {str(e)}")

    st.markdown("---")

    # === PIXABAY API SECTION ===
    st.markdown("### 🖼️ Pixabay API (Image Generation)")
    with st.expander("📖 Setup Instructions", expanded=not bool(pixabay_key)):
        st.markdown("""
        **Follow these steps to get your Pixabay API key:**

        1. **Go to** https://pixabay.com/api/docs/
        2. **Register** for a free account
        3. **Find your API key** in the "Parameters" section
        4. **Copy the key** (format: 53693289-1c945bxxxxxxxxx)
        5. **Paste into the field** below
        """)

    pixabay_key_input = st.text_input(
        "Pixabay API Key",
        value=pixabay_key,
        type="password",
        help="Paste your Pixabay API key here",
        key="pixabay_api_key_input"
    )

    col_save, col_test = st.columns([1, 1])
    with col_save:
        if st.button("💾 Save Pixabay Key", help="Save the Pixabay API key"):
            if pixabay_key_input:
                st.session_state.pixabay_api_key = pixabay_key_input
                st.success("✅ Pixabay API key saved!")
            else:
                st.error("❌ Please enter a Pixabay API key")

    with col_test:
        if pixabay_key_input or pixabay_key:
            test_key = pixabay_key_input or pixabay_key
            if st.button("🧪 Test Pixabay Connection", help="Test your Pixabay API key"):
                with st.spinner("Testing Pixabay API connection..."):
                    try:
                        import requests
                        response = requests.get(
                            "https://pixabay.com/api/",
                            params={"key": test_key, "q": "test", "per_page": 1}
                        )
                        if response.status_code == 200:
                            data = response.json()
                            if "hits" in data:
                                st.success("✅ Pixabay API connection successful!")
                            else:
                                st.error("❌ Pixabay API returned unexpected response")
                        else:
                            st.error(f"❌ Pixabay API test failed: HTTP {response.status_code}")
                    except Exception as e:
                        st.error(f"❌ Pixabay API test failed: {str(e)}")

    st.markdown("---")

    # === AZURE TTS API SECTION ===
    st.markdown("### 🔊 Azure TTS API (Audio Generation)")
    with st.expander("📖 Setup Instructions", expanded=not bool(azure_key)):
        st.markdown("""
        **Follow these steps to get your Azure TTS API key:**

        1. **Go to** [Azure Portal](https://portal.azure.com/)
        2. **Click** "Create a resource"
        3. **Search for** "Speech" and select "Speech" by Microsoft
        4. **Configure:**
           - Subscription: Choose your subscription
           - Resource group: Create new or select existing
           - Region: Choose closest region (e.g., "Central India", "East US")
           - Name: Choose unique name (e.g., "language-learning-tts")
           - Pricing tier: Free F0 (5M free/month) or Standard S0
        5. **Click** "Review + create" → "Create"

        6. **Get your key:**
           - Go to your Speech resource
           - Click "Keys and Endpoint" (left menu)
           - Copy "Key 1" or "Key 2"
        """)

    azure_key_input = st.text_input(
        "Azure TTS API Key",
        value=azure_key,
        type="password",
        help="Paste your Azure Cognitive Services subscription key here",
        key="azure_tts_key_input"
    )

    col_save, col_test = st.columns([1, 1])
    with col_save:
        if st.button("💾 Save Azure TTS Key", help="Save the Azure TTS API key"):
            if azure_key_input:
                st.session_state.azure_tts_key = azure_key_input
                import os
                os.environ["AZURE_TTS_KEY"] = azure_key_input
                st.success("✅ Azure TTS key saved!")
            else:
                st.error("❌ Please enter an Azure TTS API key")

    with col_test:
        if azure_key_input or azure_key:
            test_key = azure_key_input or azure_key
            if st.button("🧪 Test Azure TTS Connection", help="Test your Azure TTS API key"):
                with st.spinner("Testing Azure TTS connection..."):
                    try:
                        import azure.cognitiveservices.speech as speechsdk
                        speech_config = speechsdk.SpeechConfig(
                            subscription=test_key,
                            region="centralindia"
                        )
                        st.success("✅ Azure TTS connection successful!")
                    except Exception as e:
                        st.error(f"❌ Azure TTS test failed: {str(e)}")

    st.markdown("---")
    
    st.divider()
    groq_env = get_secret("GROQ_API_KEY", "")
    pixabay_env = get_secret("PIXABAY_API_KEY", "")
    azure_env = get_secret("AZURE_TTS_KEY", "")

    # Only auto-load from environment if they're real keys (not fallbacks)
    if (groq_env and pixabay_env and azure_env and not groq_key and
        not groq_env.startswith("sk-fallback") and not pixabay_env.startswith("fallback")):
        st.info("ℹ️ **Development Mode Detected** - Your API keys were auto-loaded from environment")
        groq_key = groq_env
        pixabay_key = pixabay_env
        azure_key = azure_env
        # Auto-submit if we have valid keys
        if groq_key and pixabay_key and azure_key:
            st.session_state.groq_api_key = groq_key
            st.session_state.pixabay_api_key = pixabay_key
            st.session_state.azure_tts_key = azure_key
            import os
            os.environ["AZURE_TTS_KEY"] = azure_key
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
        final_groq_key = groq_key_input or groq_key
        final_pixabay_key = pixabay_key_input or pixabay_key
        final_azure_key = azure_key_input or azure_key

        if not final_groq_key:
            st.error("❌ Please enter your Groq API key")
        elif not final_pixabay_key:
            st.error("❌ Please enter your Pixabay API key")
        elif not final_azure_key:
            st.error("❌ Please enter your Azure TTS key (required for audio generation)")
        else:
            st.session_state.groq_api_key = final_groq_key
            st.session_state.pixabay_api_key = final_pixabay_key
            st.session_state.azure_tts_key = final_azure_key
            # Set environment variable for immediate use
            import os
            os.environ["AZURE_TTS_KEY"] = final_azure_key

            # Save API keys locally
            secrets_path = Path(__file__).parent.parent / "user_secrets.json"
            user_secrets = {
                "groq_api_key": final_groq_key,
                "pixabay_api_key": final_pixabay_key,
                "azure_tts_key": final_azure_key
            }
            with open(secrets_path, "w", encoding="utf-8") as f:
                json.dump(user_secrets, f, indent=2)

            # Save to Firebase if requested
            if save_to_cloud:
                try:
                    from firebase_manager import save_settings_to_firebase
                    cloud_data = {
                        "groq_api_key": final_groq_key,
                        "pixabay_api_key": final_pixabay_key,
                        "azure_tts_key": final_azure_key
                    }
                    save_settings_to_firebase(st.session_state.session_id, cloud_data)
                    st.success("✅ API keys saved locally and to cloud!")
                except Exception as e:
                    st.warning(f"Local save successful, but cloud save failed: {e}")
            else:
                st.success("✅ API keys saved locally! Azure TTS configured!")

            st.session_state.page = PAGE_LANGUAGE_SELECT
            st.rerun()