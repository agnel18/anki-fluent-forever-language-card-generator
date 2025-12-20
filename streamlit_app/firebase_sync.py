# Firebase sync module
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

def sync_progress_to_firebase(
    session_id: str,
    language: str,
    completed_words: List[str],
    stats: Dict = None
) -> bool:
    """
    Sync progress to Firebase Firestore.

    Args:
        session_id: Anonymous session ID
        language: Language name
        completed_words: List of completed words
        stats: Optional statistics dict

    Returns:
        True if successful, False otherwise
    """
    if not firebase_initialized:
        logger.debug("Firebase not initialized, skipping sync")
        return False

    try:
        db = firestore.client()

        # Document path: users/{session_id}/progress/{language}
        doc_ref = db.collection("users").document(session_id).collection("progress").document(language)

        data = {
            "words": completed_words,
            "total_generated": len(completed_words),
            "last_updated": datetime.now().isoformat(),
        }

        if stats:
            data.update(stats)

        doc_ref.set(data, merge=True)
        logger.info(f"✅ Synced {len(completed_words)} completed words to Firebase ({language})")
        return True

    except Exception as e:
        logger.error(f"Firebase sync error: {e}")
        return False

def sync_stats_to_firebase(
    session_id: str,
    language: str,
    stats: Dict
) -> bool:
    """
    Sync word statistics to Firebase.

    Args:
        session_id: Anonymous session ID
        language: Language name
        stats: Statistics dict (times_generated, last_generated, etc.)

    Returns:
        True if successful
    """
    if not firebase_initialized:
        return False

    try:
        db = firestore.client()

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

    Args:
        session_id: Anonymous session ID
        language: Language name

    Returns:
        List of completed words or None if not found
    """
    if not firebase_initialized:
        return None

    try:
        db = firestore.client()

        doc = db.collection("users").document(session_id).collection("progress").document(language).get()

        if doc.exists:
            return doc.get("words", [])

        return None

    except Exception as e:
        logger.error(f"Error loading progress from Firebase: {e}")
        return None