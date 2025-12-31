"""
Firebase Progress Service

Handles saving and loading user learning progress to/from Firebase Firestore.
Manages synchronization of progress data across devices.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from .firebase_init import init_firebase, is_firebase_initialized, get_firestore_client

logger = logging.getLogger(__name__)


def save_progress_to_firebase(session_id: str, language: str, progress_data: Dict[str, Any]) -> bool:
    """
    Save learning progress for a specific language to Firebase.

    Args:
        session_id: User session ID
        language: Language code (e.g., 'english', 'spanish')
        progress_data: Progress data dictionary

    Returns:
        True if successful, False otherwise
    """
    if not is_firebase_initialized():
        return False

    try:
        db = get_firestore_client()
        if not db:
            return False

        # Add metadata
        progress_with_meta = progress_data.copy()
        progress_with_meta["last_updated"] = datetime.now().isoformat()
        progress_with_meta["language"] = language

        # Save to Firebase
        doc_ref = db.collection("users").document(session_id).collection("progress").document(language)
        doc_ref.set(progress_with_meta, merge=True)

        logger.debug(f"Progress saved to Firebase for {language} (session {session_id})")
        return True

    except Exception as e:
        logger.error(f"Error saving progress to Firebase: {e}")
        return False


def load_progress_from_firebase(session_id: str, language: str) -> Optional[Dict[str, Any]]:
    """
    Load learning progress for a specific language from Firebase.

    Args:
        session_id: User session ID
        language: Language code

    Returns:
        Progress data dictionary if found, None otherwise
    """
    if not is_firebase_initialized():
        return None

    try:
        db = get_firestore_client()
        if not db:
            return None

        # Load from Firebase
        doc_ref = db.collection("users").document(session_id).collection("progress").document(language)
        doc = doc_ref.get()

        if doc.exists:
            progress = doc.to_dict()
            # Remove metadata
            progress.pop("last_updated", None)
            progress.pop("language", None)
            logger.debug(f"Progress loaded from Firebase for {language} (session {session_id})")
            return progress
        else:
            logger.debug(f"No progress found in Firebase for {language} (session {session_id})")
            return None

    except Exception as e:
        logger.error(f"Error loading progress from Firebase: {e}")
        return None


def sync_progress_to_firebase(session_id: str, all_progress: Dict[str, Dict[str, Any]]) -> bool:
    """
    Sync all progress data to Firebase.

    Args:
        session_id: User session ID
        all_progress: Dictionary of language -> progress data

    Returns:
        True if successful, False otherwise
    """
    if not is_firebase_initialized():
        return False

    try:
        db = get_firestore_client()
        if not db:
            return False

        # Use batch write for efficiency
        batch = db.batch()

        for language, progress_data in all_progress.items():
            progress_with_meta = progress_data.copy()
            progress_with_meta["last_updated"] = datetime.now().isoformat()
            progress_with_meta["language"] = language

            doc_ref = db.collection("users").document(session_id).collection("progress").document(language)
            batch.set(doc_ref, progress_with_meta, merge=True)

        batch.commit()
        logger.info(f"All progress synced to Firebase for session {session_id}")
        return True

    except Exception as e:
        logger.error(f"Error syncing progress to Firebase: {e}")
        return False


def sync_progress_from_firebase(session_id: str) -> Optional[Dict[str, Dict[str, Any]]]:
    """
    Sync all progress data from Firebase.

    Args:
        session_id: User session ID

    Returns:
        Dictionary of language -> progress data, or None if error
    """
    if not is_firebase_initialized():
        return None

    try:
        db = get_firestore_client()
        if not db:
            return None

        # Get all progress documents
        progress_docs = db.collection("users").document(session_id).collection("progress").stream()

        all_progress = {}
        for doc in progress_docs:
            progress = doc.to_dict()
            language = progress.pop("language", doc.id)
            # Remove metadata
            progress.pop("last_updated", None)
            all_progress[language] = progress

        logger.info(f"All progress synced from Firebase for session {session_id} ({len(all_progress)} languages)")
        return all_progress

    except Exception as e:
        logger.error(f"Error syncing progress from Firebase: {e}")
        return None


def get_progress_languages(session_id: str) -> List[str]:
    """
    Get list of languages that have progress data.

    Args:
        session_id: User session ID

    Returns:
        List of language codes
    """
    if not is_firebase_initialized():
        return []

    try:
        db = get_firestore_client()
        if not db:
            return []

        # Get all progress document IDs
        progress_docs = db.collection("users").document(session_id).collection("progress").stream()
        languages = [doc.id for doc in progress_docs]

        return languages

    except Exception as e:
        logger.error(f"Error getting progress languages: {e}")
        return []