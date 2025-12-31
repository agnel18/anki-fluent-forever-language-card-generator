"""
Firebase Session Service

Handles user session management and metadata in Firebase Firestore.
Manages session creation, updates, and user activity tracking.
"""

import logging
from typing import Optional
from datetime import datetime

from .firebase_init import init_firebase, is_firebase_initialized, get_firestore_client

logger = logging.getLogger(__name__)


def create_user_session(session_id: str) -> bool:
    """
    Create or update user session metadata.

    Args:
        session_id: User session ID

    Returns:
        True if successful, False otherwise
    """
    if not is_firebase_initialized():
        return False

    try:
        db = get_firestore_client()
        if not db:
            return False

        doc_ref = db.collection("users").document(session_id)

        doc_ref.set({
            "created_at": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat(),
            "status": "active",
        }, merge=True)

        logger.debug(f"User session created/updated for {session_id}")
        return True

    except Exception as e:
        logger.error(f"Error creating session: {e}")
        return False


def update_last_active(session_id: str) -> bool:
    """
    Update last active timestamp for a session.

    Args:
        session_id: User session ID

    Returns:
        True if successful, False otherwise
    """
    if not is_firebase_initialized():
        return False

    try:
        db = get_firestore_client()
        if not db:
            return False

        db.collection("users").document(session_id).update({
            "last_active": datetime.now().isoformat()
        })

        logger.debug(f"Last active updated for session {session_id}")
        return True

    except Exception as e:
        logger.debug(f"Error updating last_active: {e}")
        return False


def get_session_info(session_id: str) -> Optional[dict]:
    """
    Get session information from Firebase.

    Args:
        session_id: User session ID

    Returns:
        Session info dictionary if found, None otherwise
    """
    if not is_firebase_initialized():
        return None

    try:
        db = get_firestore_client()
        if not db:
            return None

        doc_ref = db.collection("users").document(session_id)
        doc = doc_ref.get()

        if doc.exists:
            return doc.to_dict()
        else:
            return None

    except Exception as e:
        logger.error(f"Error getting session info: {e}")
        return None


def is_session_active(session_id: str) -> bool:
    """
    Check if a session is marked as active.

    Args:
        session_id: User session ID

    Returns:
        True if session is active, False otherwise
    """
    session_info = get_session_info(session_id)
    if session_info:
        return session_info.get("status") == "active"
    return False


def deactivate_session(session_id: str) -> bool:
    """
    Mark a session as inactive.

    Args:
        session_id: User session ID

    Returns:
        True if successful, False otherwise
    """
    if not is_firebase_initialized():
        return False

    try:
        db = get_firestore_client()
        if not db:
            return False

        db.collection("users").document(session_id).update({
            "status": "inactive",
            "deactivated_at": datetime.now().isoformat()
        })

        logger.debug(f"Session {session_id} marked as inactive")
        return True

    except Exception as e:
        logger.error(f"Error deactivating session: {e}")
        return False


def get_active_sessions() -> list:
    """
    Get all active sessions (admin function).

    Returns:
        List of active session IDs
    """
    if not is_firebase_initialized():
        return []

    try:
        db = get_firestore_client()
        if not db:
            return []

        # Query for active sessions
        query = db.collection("users").where("status", "==", "active")
        docs = query.stream()

        active_sessions = [doc.id for doc in docs]
        return active_sessions

    except Exception as e:
        logger.error(f"Error getting active sessions: {e}")
        return []