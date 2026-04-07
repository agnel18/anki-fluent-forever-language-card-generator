"""
Firebase Settings Service

Handles saving and loading user settings to/from Firebase Firestore.
Manages user preferences and configuration persistence.
API keys are encrypted with per-user Fernet keys before storage.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .firebase_init import init_firebase, is_firebase_initialized, get_firestore_client

logger = logging.getLogger(__name__)

# Lazy import to avoid circular dependency at module load
_encryption = None


def _get_encryption():
    """Lazy-load encryption service."""
    global _encryption
    if _encryption is None:
        from streamlit_app.services.security import encryption_service
        _encryption = encryption_service
    return _encryption


def save_settings_to_firebase(session_id: str, settings: Dict[str, Any], user_uid: str = None) -> bool:
    """
    Save user settings to Firebase.

    If user_uid is provided and encryption is available, API key fields
    are encrypted before storage. Non-key fields are stored in plaintext.

    Args:
        session_id: User session ID (Firestore document path key)
        settings: Settings dictionary to save
        user_uid: Firebase UID for encryption (None = skip encryption)

    Returns:
        True if successful, False otherwise
    """
    if not is_firebase_initialized():
        return False

    try:
        db = get_firestore_client()
        if not db:
            return False

        settings_with_meta = settings.copy()
        settings_with_meta["last_updated"] = datetime.now().isoformat()

        # Encrypt API key fields if user_uid is available
        if user_uid:
            try:
                enc = _get_encryption()
                if enc.is_encryption_available():
                    settings_with_meta = enc.encrypt_api_keys(user_uid, settings_with_meta)
                    logger.debug("API keys encrypted for user %s", user_uid)
                else:
                    logger.warning("Encryption not available — saving without encryption")
            except Exception as e:
                logger.error("Encryption failed, aborting save to protect keys: %s", e)
                return False

        # Save to Firebase
        doc_ref = db.collection("users").document(session_id).collection("metadata").document("settings")
        doc_ref.set(settings_with_meta, merge=True)

        logger.debug(f"Settings saved to Firebase for session {session_id}")
        return True

    except Exception as e:
        logger.error(f"Error saving settings to Firebase: {e}")
        return False


def load_settings_from_firebase(session_id: str, user_uid: str = None) -> Optional[Dict[str, Any]]:
    """
    Load user settings from Firebase.

    If the stored document has ``"encrypted": True``, API key fields are
    decrypted using the per-user key.  If the document is legacy plaintext
    and *user_uid* is provided, the keys are automatically encrypted and
    re-saved (one-time migration).

    Args:
        session_id: User session ID (Firestore document path key)
        user_uid: Firebase UID for decryption (None = return raw)

    Returns:
        Settings dictionary with plaintext API keys if found, None otherwise
    """
    if not is_firebase_initialized():
        return None

    try:
        db = get_firestore_client()
        if not db:
            return None

        doc_ref = db.collection("users").document(session_id).collection("metadata").document("settings")
        doc = doc_ref.get()

        if not doc.exists:
            logger.debug(f"No settings found in Firebase for session {session_id}")
            return None

        settings = doc.to_dict()

        if user_uid:
            try:
                enc = _get_encryption()
                if settings.get("encrypted"):
                    # Decrypt API key fields
                    settings = enc.decrypt_api_keys(user_uid, settings)
                    logger.debug("API keys decrypted for user %s", user_uid)
                elif enc.is_encryption_available():
                    # Legacy plaintext — migrate by encrypting and re-saving
                    logger.info("Migrating plaintext keys to encrypted for user %s", user_uid)
                    encrypted = enc.encrypt_api_keys(user_uid, settings)
                    encrypted["last_updated"] = datetime.now().isoformat()
                    doc_ref.set(encrypted, merge=True)
                    # Return the original plaintext settings for immediate use
            except Exception as e:
                logger.error("Decryption/migration failed for user %s: %s", user_uid, e)
                # Return None rather than exposing potentially garbled data
                return None

        # Remove internal metadata fields
        settings.pop("last_updated", None)
        settings.pop("encrypted", None)

        logger.debug(f"Settings loaded from Firebase for session {session_id}")
        return settings

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