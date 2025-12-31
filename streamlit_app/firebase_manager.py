# ============================================================================
# IMPORTS
# ============================================================================

import logging
import os
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

# ============================================================================
# IMPORTS
# ============================================================================

import logging
import os
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

# Import Firebase services
try:
    from services.firebase import (
        # Firebase initialization
        init_firebase, is_firebase_initialized, is_firebase_available,
        get_firestore_client, get_auth_client,

        # Settings management
        save_settings_to_firebase, load_settings_from_firebase,
        save_settings_to_session, load_settings_from_session,

        # Progress synchronization
        save_progress_to_firebase, load_progress_from_firebase,
        sync_progress_to_firebase, sync_progress_from_firebase,

        # Usage statistics
        save_usage_stats_to_firebase, load_usage_stats_from_firebase,
        merge_guest_stats_to_firebase, get_usage_stats, increment_stat,

        # Session management
        create_user_session, update_last_active,

        # Authentication
        sign_in_with_google as _sign_in_with_google,
        sign_out as _sign_out,
        is_signed_in as _is_signed_in,
        get_current_user as _get_current_user,

        # Data migration
        migrate_guest_data_to_user as _migrate_guest_data_to_user
    )
    logger.info("✅ Using Firebase service modules")
except ImportError as e:
    logger.error(f"❌ Could not import Firebase service modules: {e}")
    raise

# Import firestore for incremental operations
try:
    from firebase_admin import firestore
except ImportError:
    logger.warning("Firebase SDK not available for incremental operations")

# ============================================================================
# USAGE STATS PERSISTENCE
# ============================================================================

def update_usage_stats_to_firebase(session_id: str, stats_delta: Dict, language: Optional[str] = None) -> bool:
    """
    Incrementally update persistent usage stats for a user in Firebase.
    Uses services.firebase.get_firestore_client() for database access.
    """
    if not is_firebase_initialized():
        return False
    try:
        db = get_firestore_client()
        if not db:
            return False

        user_ref = db.collection("users").document(session_id)
        updates = {}
        # Top-level usage_stats
        for k, v in stats_delta.items():
            updates[f"usage_stats.{k}"] = firestore.Increment(v)
        # Per-language usage_stats
        if language:
            for k, v in stats_delta.items():
                updates[f"usage_stats.per_language.{language}.{k}"] = firestore.Increment(v)
        updates["usage_stats.last_updated"] = datetime.now().isoformat()
        user_ref.set(updates, merge=True)
        return True
    except Exception as e:
        logger.error(f"Error updating usage stats: {e}")
        return False

# ============================================================================
# USAGE STATS LOAD & MERGE
# ============================================================================
def load_usage_stats_from_firebase(session_id: str) -> Optional[Dict]:
    """
    Load persistent usage stats for a user from Firebase.
    Delegates to services.firebase.stats_service.load_usage_stats_from_firebase()
    """
    return load_usage_stats_from_firebase(session_id)


def merge_guest_stats_to_firebase(session_id: str, guest_stats: Dict) -> bool:
    """
    Merge guest session stats into persistent usage stats in Firebase.
    Delegates to services.firebase.stats_service.merge_guest_stats_to_firebase()
    """
    return merge_guest_stats_to_firebase(session_id, guest_stats)
"""
Firebase Manager for Language Learning App
Handles user sessions, progress sync, and statistics persistence
Supports anonymous authentication and Firestore data storage

NOTE: This module now delegates to services/firebase/ for all Firebase operations.
It maintains backward compatibility while using the new service architecture.
"""


# ============================================================================
# FIREBASE INITIALIZATION
# ============================================================================

# ============================================================================
# FIREBASE INITIALIZATION
# ============================================================================

def init_firebase(config_path: Optional[Path] = None) -> bool:
    """
    Initialize Firebase admin SDK.
    Delegates to services.firebase.firebase_init.init_firebase()

    Args:
        config_path: Path to Firebase service account key JSON (fallback only)

    Returns:
        True if successful, False otherwise
    """
    return init_firebase()


def get_session_id() -> str:
    """Get or create anonymous session ID."""
    # Session ID stored in browser via Streamlit session state
    return str(uuid.uuid4())


# ============================================================================
# PROGRESS SYNC
# ============================================================================

def sync_progress_to_firebase(
    session_id: str,
    language: str,
    completed_words: List[str],
    stats: Dict = None
) -> bool:
    """
    Sync progress to Firebase Firestore.
    Delegates to services.firebase.progress_service.save_progress_to_firebase()

    Args:
        session_id: Anonymous session ID
        language: Language name
        completed_words: List of completed words
        stats: Optional statistics dict

    Returns:
        True if successful, False otherwise
    """
    progress_data = {
        "words": completed_words,
        "total_generated": len(completed_words),
    }
    if stats:
        progress_data.update(stats)

    return save_progress_to_firebase(session_id, language, progress_data)


def sync_stats_to_firebase(
    session_id: str,
    language: str,
    stats: Dict
) -> bool:
    """
    Sync word statistics to Firebase.
    Uses services.firebase.get_firestore_client() for database access.
    """
    if not is_firebase_initialized():
        return False

    try:
        db = get_firestore_client()
        if not db:
            return False

        doc_ref = db.collection("users").document(session_id).collection("word_stats").document(language)

        data = {
            "total": stats.get("total", 0),
            "completed": stats.get("completed", 0),
            "remaining": stats.get("remaining", 0),
            "times_generated": stats.get("times_generated", 0),
            "completion_percent": stats.get("completion_percent", 0),
            "last_updated": datetime.now().isoformat(),
        }

        doc_ref.set(data)
        return True

    except Exception as e:
        logger.error(f"Error syncing stats: {e}")
        return False


def load_progress_from_firebase(session_id: str, language: str) -> Optional[List[str]]:
    """
    Load progress from Firebase.
    Delegates to services.firebase.progress_service.load_progress_from_firebase()

    Args:
        session_id: Anonymous session ID
        language: Language name

    Returns:
        List of completed words or None if not found
    """
    progress_data = load_progress_from_firebase(session_id, language)
    if progress_data:
        return progress_data.get("words", [])
    return None


# ============================================================================
# SETTINGS PERSISTENCE
# ============================================================================

def save_settings_to_firebase(session_id: str, settings: Dict) -> bool:
    """
    Save app settings to Firebase.
    Delegates to services.firebase.settings_service.save_settings_to_firebase()

    Args:
        session_id: Anonymous session ID
        settings: Settings dict (difficulty, audio_speed, sentences_per_word, etc.)

    Returns:
        True if successful
    """
    return save_settings_to_firebase(session_id, settings)


def load_settings_from_firebase(session_id: str) -> Optional[Dict]:
    """
    Load settings from Firebase.
    Delegates to services.firebase.settings_service.load_settings_from_firebase()
    """
    return load_settings_from_firebase(session_id)


# ============================================================================
# GENERATION HISTORY
# ============================================================================

def log_generation_to_firebase(
    session_id: str,
    language: str,
    words_count: int,
    sentences_count: int
) -> bool:
    """
    Log deck generation to Firebase.
    Uses services.firebase.get_firestore_client() for database access.
    """
    if not is_firebase_initialized():
        return False

    try:
        db = get_firestore_client()
        if not db:
            return False

        doc_ref = db.collection("users").document(session_id).collection("history").document()

        data = {
            "language": language,
            "words_count": words_count,
            "sentences_count": sentences_count,
            "timestamp": datetime.now().isoformat(),
        }

        doc_ref.set(data)
        logger.info(f"✅ Logged generation to Firebase: {words_count} words, {sentences_count} sentences")
        return True

    except Exception as e:
        logger.error(f"Error logging to Firebase: {e}")
        return False


def get_generation_history(session_id: str, limit: int = 10) -> List[Dict]:
    """Get recent generation history from Firebase."""
    if not is_firebase_initialized():
        return []

    try:
        db = get_firestore_client()
        if not db:
            return []

        docs = (db.collection("users").document(session_id)
                .collection("history")
                .order_by("timestamp", direction=firestore.Query.DESCENDING)
                .limit(limit)
                .stream())

        return [doc.to_dict() for doc in docs]

    except Exception as e:
        logger.error(f"Error loading history: {e}")
        return []


# ============================================================================
# USER AUTHENTICATION & SYNC STATUS
# ============================================================================

def is_signed_in() -> bool:
    """Check if user is authenticated with Firebase."""
    try:
        import streamlit as st
        return st.session_state.get('user') is not None
    except:
        return False


def get_sync_status() -> str:
    """Return cloud sync status for UI display.

    Returns:
        "enabled" - User signed in, sync active
        "available" - Firebase available but user not signed in
        "unavailable" - Firebase not available
    """
    # Ensure Firebase is initialized before checking status
    if is_firebase_available() and not is_firebase_initialized():
        try:
            init_firebase()
        except Exception as e:
            logger.debug(f"Firebase init failed in get_sync_status: {e}")

    if not is_firebase_available():
        return "unavailable"

    if not is_firebase_initialized():
        return "unavailable"

    if is_signed_in():
        return "enabled"

    return "available"


# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

def create_user_session(session_id: str) -> bool:
    """Create or update user session metadata."""
    return create_user_session(session_id)


def update_last_active(session_id: str) -> bool:
    """Update last active timestamp."""
    return update_last_active(session_id)


# ============================================================================
# AUTHENTICATION
# ============================================================================

def sign_in_with_google():
    """Handle Google OAuth sign-in flow for Streamlit."""
    return _sign_in_with_google()


def sign_out():
    """Sign out user and clear authentication state."""
    return _sign_out()


def is_signed_in() -> bool:
    """Check if user is currently signed in."""
    return _is_signed_in()


def get_current_user():
    """Get current authenticated user info."""
    return _get_current_user()


# ============================================================================
# DATA MIGRATION
# ============================================================================

def migrate_guest_data_to_user(firebase_uid: str) -> bool:
    """
    Migrate guest session data to authenticated Firebase user account.
    Delegates to services.firebase.migration_service.migrate_guest_data_to_user()
    """
    return _migrate_guest_data_to_user(firebase_uid)


# ============================================================================
# LEGACY COMPATIBILITY FUNCTIONS
# ============================================================================

# These functions maintain backward compatibility while delegating to services

def get_session_id() -> str:
    """Get or create session ID (legacy compatibility)."""
    try:
        import streamlit as st
        if 'session_id' not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())
        return st.session_state.session_id
    except:
        return str(uuid.uuid4())
