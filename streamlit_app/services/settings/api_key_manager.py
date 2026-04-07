"""
API Key Manager Service
Handles API key storage, retrieval, and cloud synchronization.
"""

import streamlit as st
from typing import Dict, Optional, Tuple
from utils import persist_api_keys

# Import centralized configuration
from streamlit_app.shared_utils import get_gemini_model, get_gemini_api


class APIKeyManager:
    """Manages API key operations and cloud synchronization."""

    def __init__(self):
        """Initialize the API key manager."""
        pass

    def get_api_key_status(self) -> Dict[str, str]:
        """
        Get the current status of all API keys.

        Returns:
            Dictionary with status messages for each key
        """
        status = {}
        key_labels = {
            'google_api_key': 'Gemini AI',
            'google_tts_api_key': 'Text-to-Speech',
            'pixabay_api_key': 'Pixabay Images',
        }
        for key, label in key_labels.items():
            val = st.session_state.get(key, "")
            if val:
                masked = val[:8] + "..." + val[-4:] if len(val) > 12 else val
                status[key] = f"✅ {label}: {masked}"
            else:
                status[key] = f"❌ {label}: Not set"
        return status

    def save_api_keys_to_cloud(self) -> bool:
        """
        Save all current API keys to Firebase cloud storage (encrypted for signed-in users).

        Returns:
            True if save successful, False otherwise
        """
        try:
            from streamlit_app.services.firebase import is_firebase_initialized, save_settings_to_firebase

            if not is_firebase_initialized():
                st.error("❌ Firebase unavailable")
                return False

            api_keys = {}
            for key in ("google_api_key", "google_tts_api_key", "pixabay_api_key"):
                val = st.session_state.get(key, "")
                if val:
                    api_keys[key] = val

            if not api_keys.get("google_api_key"):
                st.error("❌ Missing Gemini API key — required")
                return False

            # Use Firebase UID for encryption if signed in
            user_uid = None
            user = st.session_state.get("user")
            if user:
                user_uid = user.get("uid")
            doc_id = user_uid or st.session_state.get("session_id", "")
            if not doc_id:
                st.error("❌ No session ID available")
                return False

            success = save_settings_to_firebase(doc_id, api_keys, user_uid=user_uid)
            if success:
                st.success("✅ API keys saved to cloud!")
                return True
            else:
                st.error("❌ Failed to save API keys to cloud")
                return False

        except Exception as e:
            st.error(f"❌ Failed to save to cloud: {e}")
            return False

    def load_api_keys_from_cloud(self) -> bool:
        """
        Load all API keys from Firebase cloud storage (decrypted for signed-in users).

        Returns:
            True if load successful, False otherwise
        """
        try:
            from streamlit_app.services.firebase import is_firebase_initialized, load_settings_from_firebase

            if not is_firebase_initialized():
                st.error("❌ Firebase unavailable")
                return False

            # Use Firebase UID for decryption if signed in
            user_uid = None
            user = st.session_state.get("user")
            if user:
                user_uid = user.get("uid")
            doc_id = user_uid or st.session_state.get("session_id", "")
            if not doc_id:
                st.error("❌ No session ID available")
                return False

            cloud_settings = load_settings_from_firebase(doc_id, user_uid=user_uid)
            if not cloud_settings:
                st.warning("No API keys found in cloud")
                return False

            loaded_any = False
            for key in ("google_api_key", "google_tts_api_key", "pixabay_api_key"):
                if key in cloud_settings and cloud_settings[key]:
                    st.session_state[key] = cloud_settings[key]
                    loaded_any = True

            if loaded_any:
                # Persist to local storage
                persist_api_keys()
                st.success("✅ API keys loaded from cloud!")
                return True
            else:
                st.warning("No API keys found in cloud")
                return False

        except Exception as e:
            st.error(f"❌ Failed to load from cloud: {e}")
            return False

    def update_api_keys(self, google_key: str = None, tts_key: str = None, pixabay_key: str = None) -> None:
        """
        Update API keys in session state and persist locally.

        Args:
            google_key: Gemini API key (optional)
            tts_key: TTS API key (optional)
            pixabay_key: Pixabay API key (optional)
        """
        if google_key is not None:
            st.session_state.google_api_key = google_key
        if tts_key is not None:
            st.session_state.google_tts_api_key = tts_key
        if pixabay_key is not None:
            st.session_state.pixabay_api_key = pixabay_key
        persist_api_keys()

    def get_api_keys(self) -> Dict[str, str]:
        """
        Get current API keys from session state.

        Returns:
            Dictionary with all API keys
        """
        keys = {}
        for key in ("google_api_key", "google_tts_api_key", "pixabay_api_key"):
            val = st.session_state.get(key, "")
            if val:
                keys[key] = val
        return keys

    def validate_api_key(self, api_key: str, service: str) -> Tuple[bool, str]:
        """
        Validate an API key by making a test request.

        Args:
            api_key: The API key to validate
            service: The service name ('gemini')

        Returns:
            Tuple of (is_valid, message)
        """
        if not api_key:
            return False, "❌ API key is empty"

        try:
            if service.lower() == 'gemini':
                # Test Gemini API key with a simple generation
                api = get_gemini_api()
                api.configure(api_key=api_key)
                response = api.generate_content(
                    model=get_gemini_model(),
                    contents="Hello"
                )
                if response.text and len(response.text.strip()) > 0:
                    return True, "✅ Gemini API key is valid"
                else:
                    return False, "❌ Gemini API returned empty response"

            else:
                return False, f"❌ Unknown service: {service}"

        except Exception as e:
            error_msg = str(e).lower()
            if 'unauthorized' in error_msg or 'invalid' in error_msg or 'authentication' in error_msg:
                return False, f"❌ Invalid {service} API key"
            elif 'rate limit' in error_msg or 'quota' in error_msg:
                return False, f"⚠️ {service} API key valid but rate limited"
            else:
                return False, f"❌ {service} API error: {str(e)}"