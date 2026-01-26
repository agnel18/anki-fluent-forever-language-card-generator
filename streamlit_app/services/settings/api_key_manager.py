"""
API Key Manager Service
Handles API key storage, retrieval, and cloud synchronization.
"""

import streamlit as st
from typing import Dict, Optional, Tuple
from utils import persist_api_keys

# Import centralized configuration
from streamlit_app.shared_utils import get_gemini_model


class APIKeyManager:
    """Manages API key operations and cloud synchronization."""

    def __init__(self):
        """Initialize the API key manager."""
        pass

    def get_api_key_status(self) -> Dict[str, str]:
        """
        Get the current status of API keys.

        Returns:
            Dictionary with 'google' status message
        """
        google_key = st.session_state.get("google_api_key", "")

        status = {}

        if google_key:
            masked_google = google_key[:8] + "..." + google_key[-4:] if len(google_key) > 12 else google_key
            status['google'] = f"✅ Google API Key: {masked_google}"
        else:
            status['google'] = "❌ No Google API key set"

        return status

    def save_api_keys_to_cloud(self) -> bool:
        """
        Save current API keys to Firebase cloud storage.

        Returns:
            True if save successful, False otherwise
        """
        try:
            from streamlit_app.services.firebase import is_firebase_initialized, save_settings_to_firebase

            if not is_firebase_initialized():
                st.error("❌ Firebase unavailable")
                return False

            google_key = st.session_state.get("google_api_key", "")

            if not google_key:
                st.error("❌ Missing Google API key - required for app functionality")
                return False

            session_id = st.session_state.get("session_id", "")
            if not session_id:
                st.error("❌ No session ID available")
                return False

            api_keys = {
                "google_api_key": google_key
            }

            success = save_settings_to_firebase(session_id, api_keys)
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
        Load API keys from Firebase cloud storage.

        Returns:
            True if load successful, False otherwise
        """
        try:
            from streamlit_app.services.firebase import is_firebase_initialized, load_settings_from_firebase

            if not is_firebase_initialized():
                st.error("❌ Firebase unavailable")
                return False

            session_id = st.session_state.get("session_id", "")
            if not session_id:
                st.error("❌ No session ID available")
                return False

            cloud_settings = load_settings_from_firebase(session_id)
            if not cloud_settings:
                st.warning("No API keys found in cloud")
                return False

            if 'google_api_key' in cloud_settings:
                st.session_state.google_api_key = cloud_settings['google_api_key']
                # Persist to local storage
                persist_api_keys()
                st.success("✅ API keys loaded from cloud!")
                return True
            else:
                st.warning("Incomplete API keys found in cloud")
                return False

        except Exception as e:
            st.error(f"❌ Failed to load from cloud: {e}")
            return False

    def update_api_keys(self, google_key: str) -> None:
        """
        Update API keys in session state and persist locally.

        Args:
            google_key: New Google API key
        """
        st.session_state.google_api_key = google_key
        persist_api_keys()

    def get_api_keys(self) -> str:
        """
        Get current API keys from session state.

        Returns:
            Google API key
        """
        google_key = st.session_state.get("google_api_key", "")
        return google_key

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
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(get_gemini_model())
                response = model.generate_content("Hello")
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