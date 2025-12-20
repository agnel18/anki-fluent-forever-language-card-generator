# Firebase authentication module
# Extracted from firebase_manager.py for better separation of concerns

import logging
import uuid
from typing import Optional

logger = logging.getLogger(__name__)

# ============================================================================
# SESSION MANAGEMENT
# ============================================================================
def get_session_id() -> str:
    """Get or create anonymous session ID."""
    # Session ID stored in browser via Streamlit session state
    return str(uuid.uuid4())

# ============================================================================
# USER AUTHENTICATION
# ============================================================================
def is_signed_in() -> bool:
    """Check if user is authenticated with Firebase."""
    try:
        import streamlit as st
        return st.session_state.get('user') is not None
    except:
        return False

def sign_in_with_google():
    """Handle Google OAuth sign-in flow."""
    try:
        import streamlit as st
        # Navigate to auth handler page
        st.session_state.page = "auth_handler"
        st.rerun()
    except:
        pass

def sign_out():
    """Sign out user and clear authentication state."""
    try:
        import streamlit as st
        if 'user' in st.session_state:
            del st.session_state.user
        st.session_state.is_guest = True
        logger.info("User signed out successfully")
    except Exception as e:
        logger.error(f"Error during sign out: {e}")

def get_current_user():
    """Get current authenticated user info."""
    try:
        import streamlit as st
        if is_signed_in():
            return st.session_state.user
        return None
    except:
        return None