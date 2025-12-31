"""
Firebase Settings Service

Handles saving and loading user settings to/from Firebase Firestore.
Manages user preferences and configuration persistence.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .firebase_init import init_firebase, is_firebase_initialized, get_firestore_client

logger = logging.getLogger(__name__)


def save_settings_to_firebase(session_id: str, settings: Dict[str, Any]) -> bool:
    """
    Save user settings to Firebase.

    Args:
        session_id: User session ID
        settings: Settings dictionary to save

    Returns:
        True if successful, False otherwise
    """
    if not is_firebase_initialized():
        return False

    try:
        db = get_firestore_client()
        if not db:
            return False

        # Add timestamp
        settings_with_meta = settings.copy()
        settings_with_meta["last_updated"] = datetime.now().isoformat()

        # Save to Firebase
        doc_ref = db.collection("users").document(session_id).collection("metadata").document("settings")
        doc_ref.set(settings_with_meta, merge=True)

        logger.debug(f"Settings saved to Firebase for session {session_id}")
        return True

    except Exception as e:
        logger.error(f"Error saving settings to Firebase: {e}")
        return False


def load_settings_from_firebase(session_id: str) -> Optional[Dict[str, Any]]:
    """
    Load user settings from Firebase.

    Args:
        session_id: User session ID

    Returns:
        Settings dictionary if found, None otherwise
    """
    if not is_firebase_initialized():
        return None

    try:
        db = get_firestore_client()
        if not db:
            return None

        # Load from Firebase
        doc_ref = db.collection("users").document(session_id).collection("metadata").document("settings")
        doc = doc_ref.get()

        if doc.exists:
            settings = doc.to_dict()
            # Remove metadata fields
            settings.pop("last_updated", None)
            logger.debug(f"Settings loaded from Firebase for session {session_id}")
            return settings
        else:
            logger.debug(f"No settings found in Firebase for session {session_id}")
            return None

    except Exception as e:
        logger.error(f"Error loading settings from Firebase: {e}")
        return None


def save_settings_to_session(settings: Dict[str, Any]) -> None:
    """
    Save settings to Streamlit session state.

    Args:
        settings: Settings dictionary to save
    """
    try:
        import streamlit as st
        st.session_state.settings = settings
        logger.debug("Settings saved to session state")
    except Exception as e:
        logger.error(f"Error saving settings to session: {e}")


def load_settings_from_session() -> Optional[Dict[str, Any]]:
    """
    Load settings from Streamlit session state.

    Returns:
        Settings dictionary if found, None otherwise
    """
    try:
        import streamlit as st
        return st.session_state.get("settings")
    except Exception as e:
        logger.error(f"Error loading settings from session: {e}")
        return None