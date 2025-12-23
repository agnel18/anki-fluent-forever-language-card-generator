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

    has_real_api_keys = (
        groq_key and pixabay_key and
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
    
    # Firebase sync status
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
                    if cloud_settings and 'groq_api_key' in cloud_settings and 'pixabay_api_key' in cloud_settings:
                        st.session_state.groq_api_key = cloud_settings['groq_api_key']
                        st.session_state.pixabay_api_key = cloud_settings['pixabay_api_key']
                        st.success("✅ API keys loaded from cloud!")
                        st.session_state.page = PAGE_LANGUAGE_SELECT
                        st.rerun()
                    else:
                        st.warning("No API keys found in cloud. Please enter them below.")
                except Exception as e:
                    st.error(f"Failed to load from cloud: {e}")
        else:
            st.info("🔄 **Local Storage Only** - API keys will be saved locally on this device")
    except Exception as e:
        st.info("🔄 **Local Storage Only** - Firebase unavailable")
    
    st.markdown(
        """
**How it works:**
1. You enter your API keys in this form
2. They stay in your browser\'s temporary memory (session only)
3. We use them ONLY to make API calls on YOUR behalf
4. Your keys are NEVER stored anywhere without your permission
5. When you close this tab, keys are automatically deleted

**Important privacy notes:**
- ✅ Your API keys are YOUR responsibility
- ✅ Your data stays with you (nothing uploaded)
- ✅ You control API usage and costs
- ✅ You can regenerate keys anytime
"""
    )
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🤖 Groq API Key")
        st.markdown("""
        **What it's for:** Generate sentences in your language
        **Get free key:**
        1. https://console.groq.com/keys
        2. Create account (free)
        3. Generate new API key
        4. Copy & paste below
        """)
        groq_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...", key="groq_api_key_input")
    with col2:
        st.markdown("### 🖼️ Pixabay API Key")
        st.markdown("""
        **What it's for:** Download images for each word
        **Get free key:**
        1. https://pixabay.com/api/docs/
        2. Create account (free)
        3. Find API key in dashboard
        4. Copy & paste below
        """)
        pixabay_key = st.text_input("Pixabay API Key", type="password", placeholder="53606933-...", key="pixabay_api_key_input")
    st.divider()
    groq_env = get_secret("GROQ_API_KEY", "")
    pixabay_env = get_secret("PIXABAY_API_KEY", "")

    # Only auto-load from environment if they're real keys (not fallbacks)
    if (groq_env and pixabay_env and not groq_key and
        not groq_env.startswith("sk-fallback") and not pixabay_env.startswith("fallback")):
        st.info("ℹ️ **Development Mode Detected** - Your API keys were auto-loaded from environment")
        groq_key = groq_env
        pixabay_key = pixabay_env
        # Auto-submit if we have valid keys
        if groq_key and pixabay_key:
            st.session_state.groq_api_key = groq_key
            st.session_state.pixabay_api_key = pixabay_key
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
        if not groq_key:
            st.error("❌ Please enter your Groq API key")
        elif not pixabay_key:
            st.error("❌ Please enter your Pixabay API key")
        else:
            st.session_state.groq_api_key = groq_key
            st.session_state.pixabay_api_key = pixabay_key
            
            # Save API keys locally
            secrets_path = Path(__file__).parent.parent / "user_secrets.json"
            user_secrets = {"groq_api_key": groq_key, "pixabay_api_key": pixabay_key}
            with open(secrets_path, "w", encoding="utf-8") as f:
                json.dump(user_secrets, f, indent=2)
            
            # Save to Firebase if requested
            if save_to_cloud:
                try:
                    from firebase_manager import save_settings_to_firebase
                    save_settings_to_firebase(st.session_state.session_id, {
                        "groq_api_key": groq_key,
                        "pixabay_api_key": pixabay_key
                    })
                    st.success("✅ API keys saved locally and to cloud!")
                except Exception as e:
                    st.warning(f"Local save successful, but cloud save failed: {e}")
            else:
                st.success("✅ API keys saved locally!")
            
            st.session_state.page = PAGE_LANGUAGE_SELECT
            st.rerun()