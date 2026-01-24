# Firebase stats module
# Extracted from firebase_manager.py for better separation of concerns

import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Check if firebase is available
try:
    import firebase_admin
    from firebase_admin import firestore
    firebase_available = True
except ImportError:
    firebase_available = False
    firestore = None

# Firebase initialization status (will be set by firebase_manager)
firebase_initialized = False

def update_usage_stats_to_firebase(session_id: str, stats_delta: Dict, language: Optional[str] = None) -> bool:
    """
    Incrementally update persistent usage stats for a user in Firebase.
    Args:
        session_id: User/session ID
        stats_delta: Dict of fields to increment (e.g., {"gemini_calls": 2, "google_search_calls": 1})
        language: If provided, also update per-language stats
    Returns:
        True if successful, False otherwise
    """
    if not firebase_initialized:
        return False
    try:
        db = firestore.client()
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

def load_usage_stats_from_firebase(session_id: str) -> Optional[Dict]:
    """
    Load persistent usage stats for a user from Firebase.
    Returns the usage_stats dict or None if not found.
    """
    if not firebase_initialized:
        return None
    try:
        db = firestore.client()
        doc = db.collection("users").document(session_id).get()
        if doc.exists:
            return doc.to_dict().get("usage_stats", {})
        return None
    except Exception as e:
        logger.error(f"Error loading usage stats: {e}")
        return None

def merge_guest_stats_to_firebase(session_id: str, guest_stats: Dict) -> bool:
    """
    Merge guest session stats into persistent usage stats in Firebase.
    Adds guest_stats values to existing persistent stats.
    """
    if not firebase_initialized or not guest_stats:
        return False
    try:
        db = firestore.client()
        user_ref = db.collection("users").document(session_id)
        updates = {}
        for k, v in guest_stats.items():
            if isinstance(v, int):
                updates[f"usage_stats.{k}"] = firestore.Increment(v)
            elif isinstance(v, dict):
                # For per_language dicts
                for lang, lang_stats in v.items():
                    for lk, lv in lang_stats.items():
                        updates[f"usage_stats.per_language.{lang}.{lk}"] = firestore.Increment(lv)
        updates["usage_stats.last_updated"] = datetime.now().isoformat()
        user_ref.set(updates, merge=True)
        return True
    except Exception as e:
        logger.error(f"Error merging guest stats: {e}")
        return False

def log_generation_to_firebase(
    session_id: str,
    language: str,
    words_count: int,
    sentences_count: int
) -> bool:
    """
    Log deck generation to Firebase.

    Args:
        session_id: Anonymous session ID
        language: Language name
        words_count: Number of words generated
        sentences_count: Number of sentences generated

    Returns:
        True if successful
    """
    if not firebase_initialized:
        return False

    try:
        db = firestore.client()

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
    if not firebase_initialized:
        return []

    try:
        db = firestore.client()

        docs = (db.collection("users").document(session_id)
                .collection("history")
                .order_by("timestamp", direction=firestore.Query.DESCENDING)
                .limit(limit)
                .stream())

        return [doc.to_dict() for doc in docs]

    except Exception as e:
        logger.error(f"Error loading history: {e}")
        return []