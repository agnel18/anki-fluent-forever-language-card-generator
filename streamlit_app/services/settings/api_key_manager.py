"""
API Key Manager Service
Handles API key storage, retrieval, and cloud synchronization.
"""

import streamlit as st
from typing import Dict, Optional, Tuple
from utils import persist_api_keys


class APIKeyManager:
    """Manages API key operations and cloud synchronization."""

    def __init__(self):
        """Initialize the API key manager."""
        pass

    def get_api_key_status(self) -> Dict[str, str]:
        """
        Get the current status of API keys.

        Returns:
            Dictionary with 'groq' and 'pixabay' status messages
        """
        groq_key = st.session_state.get("groq_api_key", "")
        pixabay_key = st.session_state.get("pixabay_api_key", "")

        status = {}

        if groq_key:
            masked_groq = groq_key[:8] + "..." + groq_key[-4:] if len(groq_key) > 12 else groq_key
            status['groq'] = f"✅ Groq Key: {masked_groq}"
        else:
            status['groq'] = "❌ No Groq API key set"

        if pixabay_key:
            masked_pixabay = pixabay_key[:8] + "..." + pixabay_key[-4:] if len(pixabay_key) > 12 else pixabay_key
            status['pixabay'] = f"✅ Pixabay Key: {masked_pixabay}"
        else:
            status['pixabay'] = "❌ No Pixabay API key set"

        return status

    def save_api_keys_to_cloud(self) -> bool:
        """
        Save current API keys to Firebase cloud storage.

        Returns:
            True if save successful, False otherwise
        """
        try:
            from ..firebase import is_firebase_initialized, save_settings_to_firebase

            if not is_firebase_initialized():
                st.error("❌ Firebase unavailable")
                return False

            groq_key = st.session_state.get("groq_api_key", "")
            pixabay_key = st.session_state.get("pixabay_api_key", "")

            if not groq_key or not pixabay_key:
                st.error("❌ Missing API keys - both Groq and Pixabay keys are required")
                return False

            session_id = st.session_state.get("session_id", "")
            if not session_id:
                st.error("❌ No session ID available")
                return False

            api_keys = {
                "groq_api_key": groq_key,
                "pixabay_api_key": pixabay_key
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
            from ..firebase import is_firebase_initialized, load_settings_from_firebase

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

            if 'groq_api_key' in cloud_settings and 'pixabay_api_key' in cloud_settings:
                st.session_state.groq_api_key = cloud_settings['groq_api_key']
                st.session_state.pixabay_api_key = cloud_settings['pixabay_api_key']
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

    def update_api_keys(self, groq_key: str, pixabay_key: str) -> None:
        """
        Update API keys in session state and persist locally.

        Args:
            groq_key: New Groq API key
            pixabay_key: New Pixabay API key
        """
        st.session_state.groq_api_key = groq_key
        st.session_state.pixabay_api_key = pixabay_key
        persist_api_keys()

    def get_api_keys(self) -> Tuple[str, str]:
        """
        Get current API keys from session state.

        Returns:
            Tuple of (groq_key, pixabay_key)
        """
        groq_key = st.session_state.get("groq_api_key", "")
        pixabay_key = st.session_state.get("pixabay_api_key", "")
        return groq_key, pixabay_key