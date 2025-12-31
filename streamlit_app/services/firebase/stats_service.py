"""
Firebase Statistics Service

Handles saving and loading usage statistics to/from Firebase Firestore.
Manages user activity tracking and analytics data.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from collections import defaultdict

from .firebase_init import init_firebase, is_firebase_initialized, get_firestore_client

logger = logging.getLogger(__name__)


def save_usage_stats_to_firebase(session_id: str, stats_data: Dict[str, Any]) -> bool:
    """
    Save usage statistics to Firebase.

    Args:
        session_id: User session ID
        stats_data: Statistics data dictionary

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
        stats_with_meta = stats_data.copy()
        stats_with_meta["last_updated"] = datetime.now().isoformat()

        # Save to Firebase
        doc_ref = db.collection("users").document(session_id).collection("metadata").document("usage_stats")
        doc_ref.set(stats_with_meta, merge=True)

        logger.debug(f"Usage stats saved to Firebase for session {session_id}")
        return True

    except Exception as e:
        logger.error(f"Error saving usage stats to Firebase: {e}")
        return False


def load_usage_stats_from_firebase(session_id: str) -> Optional[Dict[str, Any]]:
    """
    Load usage statistics from Firebase.

    Args:
        session_id: User session ID

    Returns:
        Statistics data dictionary if found, None otherwise
    """
    if not is_firebase_initialized():
        return None

    try:
        db = get_firestore_client()
        if not db:
            return None

        # Load from Firebase
        doc_ref = db.collection("users").document(session_id).collection("metadata").document("usage_stats")
        doc = doc_ref.get()

        if doc.exists:
            stats = doc.to_dict()
            # Remove metadata
            stats.pop("last_updated", None)
            logger.debug(f"Usage stats loaded from Firebase for session {session_id}")
            return stats
        else:
            logger.debug(f"No usage stats found in Firebase for session {session_id}")
            return None

    except Exception as e:
        logger.error(f"Error loading usage stats from Firebase: {e}")
        return None


def merge_guest_stats_to_firebase(firebase_uid: str, guest_stats: Dict[str, Any]) -> bool:
    """
    Merge guest session statistics with existing user statistics.

    Args:
        firebase_uid: Firebase user ID
        guest_stats: Guest session statistics

    Returns:
        True if successful, False otherwise
    """
    if not is_firebase_initialized():
        return False

    try:
        db = get_firestore_client()
        if not db:
            return False

        # Load existing user stats
        existing_stats = load_usage_stats_from_firebase(firebase_uid) or {}

        # Merge statistics
        merged_stats = merge_statistics(existing_stats, guest_stats)

        # Save merged stats
        return save_usage_stats_to_firebase(firebase_uid, merged_stats)

    except Exception as e:
        logger.error(f"Error merging guest stats to Firebase: {e}")
        return False


def merge_statistics(existing_stats: Dict[str, Any], guest_stats: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two statistics dictionaries intelligently.

    Args:
        existing_stats: Existing user statistics
        guest_stats: Guest session statistics

    Returns:
        Merged statistics dictionary
    """
    merged = existing_stats.copy()

    # Handle different stat types
    for key, guest_value in guest_stats.items():
        if key not in merged:
            merged[key] = guest_value
        elif isinstance(guest_value, dict) and isinstance(merged[key], dict):
            # Merge nested dictionaries (like language-specific stats)
            merged[key] = merge_nested_stats(merged[key], guest_value)
        elif isinstance(guest_value, (int, float)) and isinstance(merged[key], (int, float)):
            # Add numeric values
            merged[key] += guest_value
        elif isinstance(guest_value, list) and isinstance(merged[key], list):
            # Extend lists
            merged[key].extend(guest_value)
        else:
            # For other types, prefer the newer value
            merged[key] = guest_value

    return merged


def merge_nested_stats(existing: Dict[str, Any], guest: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge nested statistics dictionaries.

    Args:
        existing: Existing nested stats
        guest: Guest nested stats

    Returns:
        Merged nested stats
    """
    merged = existing.copy()

    for key, guest_value in guest.items():
        if key not in merged:
            merged[key] = guest_value
        elif isinstance(guest_value, (int, float)) and isinstance(merged[key], (int, float)):
            merged[key] += guest_value
        elif isinstance(guest_value, list) and isinstance(merged[key], list):
            merged[key].extend(guest_value)
        else:
            merged[key] = guest_value

    return merged


def get_usage_stats(session_id: str) -> Optional[Dict[str, Any]]:
    """
    Get usage statistics, trying session state first, then Firebase.

    Args:
        session_id: User session ID

    Returns:
        Statistics data dictionary
    """
    try:
        import streamlit as st

        # Try session state first
        session_stats = st.session_state.get("usage_stats")
        if session_stats:
            return session_stats

        # Fall back to Firebase
        firebase_stats = load_usage_stats_from_firebase(session_id)
        if firebase_stats:
            # Cache in session state
            st.session_state.usage_stats = firebase_stats
            return firebase_stats

        return None

    except Exception as e:
        logger.error(f"Error getting usage stats: {e}")
        return None


def increment_stat(session_id: str, stat_key: str, increment: int = 1) -> bool:
    """
    Increment a specific statistic counter.

    Args:
        session_id: User session ID
        stat_key: Statistics key to increment
        increment: Amount to increment by

    Returns:
        True if successful, False otherwise
    """
    try:
        import streamlit as st

        # Get current stats
        stats = get_usage_stats(session_id) or {}

        # Increment the stat
        current_value = stats.get(stat_key, 0)
        stats[stat_key] = current_value + increment

        # Save to session state
        st.session_state.usage_stats = stats

        # Save to Firebase (async operation)
        save_usage_stats_to_firebase(session_id, stats)

        return True

    except Exception as e:
        logger.error(f"Error incrementing stat {stat_key}: {e}")
        return False