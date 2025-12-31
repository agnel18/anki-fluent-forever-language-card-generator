"""
Firebase Authentication Service

Handles Firebase authentication UI interactions for Streamlit.
Provides sign-in, sign-out, and authentication state management.
"""

import logging
from typing import Optional, Dict, Any

from .firebase_init import init_firebase, is_firebase_initialized

logger = logging.getLogger(__name__)


def sign_in_with_google():
    """
    Handle Google OAuth sign-in flow for Streamlit.

    Note: This is a simplified implementation for Streamlit.
    In production, implement proper OAuth flow.
    """
    try:
        import streamlit as st

        # Check if Firebase is initialized
        if not is_firebase_initialized():
            st.error("❌ Firebase not available")
            return

        # For Streamlit Cloud, we need to use a different approach
        # since we can't do full OAuth redirects

        # For now, we'll use a simplified approach
        # In production, you'd implement proper OAuth flow
        st.info("🔄 Redirecting to Google sign-in...")

        # This would normally redirect to Google OAuth
        # For Streamlit, we need to handle this differently
        st.session_state.page = "auth_handler"
        st.rerun()

    except Exception as e:
        logger.error(f"Error in sign_in_with_google: {e}")
        import streamlit as st
        st.error(f"❌ Sign-in failed: {e}")


def sign_out():
    """
    Sign out user and clear authentication state.
    """
    try:
        import streamlit as st
        if 'user' in st.session_state:
            del st.session_state.user
        st.session_state.is_guest = True
        logger.info("User signed out successfully")
    except Exception as e:
        logger.error(f"Error during sign out: {e}")


def is_signed_in() -> bool:
    """
    Check if user is currently signed in.

    Returns:
        True if user is signed in, False otherwise
    """
    try:
        import streamlit as st
        return 'user' in st.session_state and not st.session_state.get('is_guest', True)
    except:
        return False


def get_current_user() -> Optional[Dict[str, Any]]:
    """
    Get current authenticated user info.

    Returns:
        User info dictionary if signed in, None otherwise
    """
    try:
        import streamlit as st
        if is_signed_in():
            return st.session_state.user
        return None
    except:
        return None


def set_user_session(user_info: Dict[str, Any]):
    """
    Set user session state after successful authentication.

    Args:
        user_info: User information dictionary
    """
    try:
        import streamlit as st
        st.session_state.user = user_info
        st.session_state.is_guest = False
        logger.info(f"User session set for: {user_info.get('email', 'unknown')}")
    except Exception as e:
        logger.error(f"Error setting user session: {e}")


def clear_user_session():
    """
    Clear user session state.
    """
    try:
        import streamlit as st
        if 'user' in st.session_state:
            del st.session_state.user
        st.session_state.is_guest = True
        logger.info("User session cleared")
    except Exception as e:
        logger.error(f"Error clearing user session: {e}")