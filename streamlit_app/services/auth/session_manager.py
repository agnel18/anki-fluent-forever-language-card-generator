"""
Session Manager - Handles authentication session state
"""

import time
import streamlit as st
from typing import Optional, Dict, Any

# Session timeout: 30 minutes of inactivity
SESSION_TIMEOUT_SECONDS = 30 * 60


class SessionManager:
    """
    Service for managing authentication-related session state.
    """

    # API key fields to clear on sign-out / timeout
    _SENSITIVE_KEYS = ("google_api_key", "google_tts_api_key", "pixabay_api_key")

    def __init__(self):
        """Initialize session manager."""
        pass

    def _touch_activity(self):
        """Update last activity timestamp."""
        st.session_state["last_activity"] = time.time()

    def _is_session_expired(self) -> bool:
        """Check if session has expired due to inactivity."""
        last = st.session_state.get("last_activity")
        if last is None:
            return False
        return (time.time() - last) > SESSION_TIMEOUT_SECONDS

    def _clear_sensitive_session_data(self):
        """Clear decrypted API keys and sensitive data from session state."""
        for key in self._SENSITIVE_KEYS:
            if key in st.session_state:
                del st.session_state[key]

    def is_signed_in(self) -> bool:
        """
        Check if user is authenticated. Auto-expires after inactivity timeout.

        Returns:
            bool: True if user is signed in and session not expired
        """
        if st.session_state.get("user") is None:
            return False
        if self._is_session_expired():
            self.sign_out()
            return False
        self._touch_activity()
        return True

    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """
        Get current authenticated user info.

        Returns:
            Dict containing user information or None if not signed in
        """
        return st.session_state.get("user")

    def sign_out(self):
        """
        Sign out user by clearing session state and sensitive data.
        """
        self._clear_sensitive_session_data()
        st.session_state.user = None
        st.session_state.is_guest = True
        st.session_state.pop("last_activity", None)

    def set_user(self, user_data: Dict[str, Any]):
        """
        Set authenticated user in session state.

        Args:
            user_data: User information dictionary
        """
        st.session_state.user = user_data
        st.session_state.is_guest = False
        self._touch_activity()

    def set_pending_verification_user(self, user_data: Dict[str, Any]):
        """
        Set pending verification user data.

        Args:
            user_data: User data for pending verification
        """
        st.session_state.pending_verification_user = user_data

    def get_pending_verification_user(self) -> Optional[Dict[str, Any]]:
        """
        Get pending verification user data.

        Returns:
            Dict containing pending user data or None
        """
        return st.session_state.get("pending_verification_user")

    def clear_pending_verification_user(self):
        """
        Clear pending verification user data.
        """
        if "pending_verification_user" in st.session_state:
            del st.session_state.pending_verification_user

    def set_verification_options(self, email: str):
        """
        Set flags to show verification options.

        Args:
            email: Email address needing verification
        """
        st.session_state.show_verification_options = True
        st.session_state.verification_email = email

    def clear_verification_options(self):
        """
        Clear verification options flags.
        """
        st.session_state.show_verification_options = False
        if "verification_email" in st.session_state:
            del st.session_state.verification_email

    def get_verification_email(self) -> Optional[str]:
        """
        Get email address for verification.

        Returns:
            Email address or None
        """
        return st.session_state.get("verification_email")

    def should_show_verification_options(self) -> bool:
        """
        Check if verification options should be shown.

        Returns:
            bool: True if verification options should be displayed
        """
        return st.session_state.get("show_verification_options", False)