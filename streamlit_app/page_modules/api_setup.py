# pages/api_setup.py - API setup page for the language learning app

import streamlit as st
import json
from pathlib import Path
from utils import get_secret
from constants import PAGE_LANGUAGE_SELECT


def render_api_setup_page():
    """Render the API keys setup page."""
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
    
    st.markdown("# 🌍 Language Learning Anki Deck Generator")
    st.markdown("Create custom Anki decks in minutes | Free, no data stored")
    st.divider()
    st.markdown("## 🔐 API Keys Setup")
    st.markdown(
        """
**How it works:**
1. You enter your API keys in this form
2. They stay in your browser\'s temporary memory (session only)
3. We use them ONLY to make API calls on YOUR behalf
4. Your keys are NEVER stored anywhere
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
    if st.button("🚀 Next: Select Language", use_container_width=True):
        if not groq_key:
            st.error("❌ Please enter your Groq API key")
        elif not pixabay_key:
            st.error("❌ Please enter your Pixabay API key")
        else:
            st.session_state.groq_api_key = groq_key
            st.session_state.pixabay_api_key = pixabay_key
            # Save API keys to local file for persistence
            secrets_path = Path(__file__).parent.parent / "user_secrets.json"
            user_secrets = {"groq_api_key": groq_key, "pixabay_api_key": pixabay_key}
            with open(secrets_path, "w", encoding="utf-8") as f:
                json.dump(user_secrets, f, indent=2)
            # Save API keys to Firebase if not guest
            if not st.session_state.get("is_guest", True):
                try:
                    from firebase_manager import save_settings_to_firebase
                    save_settings_to_firebase(st.session_state.session_id, {
                        "groq_api_key": groq_key,
                        "pixabay_api_key": pixabay_key
                    })
                except Exception as e:
                    st.warning(f"Could not save API keys to cloud: {e}")
            st.session_state.page = PAGE_LANGUAGE_SELECT
            st.session_state.scroll_to_top = True
            st.rerun()