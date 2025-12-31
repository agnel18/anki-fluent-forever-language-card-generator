"""
Firebase Data Migration Service

Handles migration of guest session data to authenticated user accounts.
Manages data transfer between guest and authenticated user contexts.
"""

import logging
from typing import Optional
from datetime import datetime

from .firebase_init import init_firebase, is_firebase_initialized, get_firestore_client
from .settings_service import load_settings_from_firebase, save_settings_to_firebase
from .stats_service import load_usage_stats_from_firebase, merge_guest_stats_to_firebase

logger = logging.getLogger(__name__)


def migrate_guest_data_to_user(firebase_uid: str) -> bool:
    """
    Migrate guest session data to authenticated Firebase user account.

    Args:
        firebase_uid: The Firebase UID of the authenticated user

    Returns:
        True if migration successful, False otherwise
    """
    if not is_firebase_initialized():
        logger.warning("Firebase not initialized, cannot migrate data")
        return False

    try:
        import streamlit as st
        db = get_firestore_client()
        if not db:
            return False

        # Get current guest session data
        guest_session_id = st.session_state.get('session_id')
        if not guest_session_id:
            logger.warning("No guest session ID found for migration")
            return False

        logger.info(f"Migrating data from guest session {guest_session_id} to user {firebase_uid}")

        # Migrate settings
        success = migrate_settings(guest_session_id, firebase_uid)
        if not success:
            logger.warning("Settings migration failed, but continuing...")

        # Migrate progress data
        success = migrate_progress(guest_session_id, firebase_uid)
        if not success:
            logger.warning("Progress migration failed, but continuing...")

        # Migrate word stats
        success = migrate_word_stats(guest_session_id, firebase_uid)
        if not success:
            logger.warning("Word stats migration failed, but continuing...")

        # Migrate usage statistics
        success = migrate_usage_stats(guest_session_id, firebase_uid)
        if not success:
            logger.warning("Usage stats migration failed, but continuing...")

        # Migrate generation history
        success = migrate_history(guest_session_id, firebase_uid)
        if not success:
            logger.warning("History migration failed, but continuing...")

        # Mark migration as complete
        mark_migration_complete(firebase_uid, guest_session_id)

        # Update session state
        st.session_state.data_migrated = True
        st.session_state.migrated_from_session = guest_session_id

        logger.info(f"✅ Successfully migrated all guest data to user {firebase_uid}")
        return True

    except Exception as e:
        logger.error(f"Error migrating guest data to user: {e}")
        return False


def migrate_settings(guest_session_id: str, firebase_uid: str) -> bool:
    """
    Migrate settings from guest session to user account.

    Args:
        guest_session_id: Guest session ID
        firebase_uid: Firebase user ID

    Returns:
        True if successful, False otherwise
    """
    try:
        guest_settings = load_settings_from_firebase(guest_session_id)
        if guest_settings:
            # Save settings under Firebase UID
            success = save_settings_to_firebase(firebase_uid, guest_settings)
            if success:
                logger.info("Migrated settings to user account")
                return True
        return False
    except Exception as e:
        logger.error(f"Error migrating settings: {e}")
        return False


def migrate_progress(guest_session_id: str, firebase_uid: str) -> bool:
    """
    Migrate progress data from guest session to user account.

    Args:
        guest_session_id: Guest session ID
        firebase_uid: Firebase user ID

    Returns:
        True if successful, False otherwise
    """
    try:
        db = get_firestore_client()
        if not db:
            return False

        # Get all progress documents for the guest session
        progress_docs = db.collection("users").document(guest_session_id).collection("progress").stream()

        migrated_count = 0
        for doc in progress_docs:
            progress_data = doc.to_dict()
            # Save under Firebase UID
            doc_ref = db.collection("users").document(firebase_uid).collection("progress").document(doc.id)
            doc_ref.set(progress_data, merge=True)
            migrated_count += 1
            logger.debug(f"Migrated progress for language: {doc.id}")

        logger.info(f"Migrated {migrated_count} progress entries")
        return True

    except Exception as e:
        logger.error(f"Error migrating progress: {e}")
        return False


def migrate_word_stats(guest_session_id: str, firebase_uid: str) -> bool:
    """
    Migrate word statistics from guest session to user account.

    Args:
        guest_session_id: Guest session ID
        firebase_uid: Firebase user ID

    Returns:
        True if successful, False otherwise
    """
    try:
        db = get_firestore_client()
        if not db:
            return False

        # Get all word stats documents for the guest session
        word_stats_docs = db.collection("users").document(guest_session_id).collection("word_stats").stream()

        migrated_count = 0
        for doc in word_stats_docs:
            stats_data = doc.to_dict()
            doc_ref = db.collection("users").document(firebase_uid).collection("word_stats").document(doc.id)
            doc_ref.set(stats_data, merge=True)
            migrated_count += 1
            logger.debug(f"Migrated word stats for language: {doc.id}")

        logger.info(f"Migrated {migrated_count} word stats entries")
        return True

    except Exception as e:
        logger.error(f"Error migrating word stats: {e}")
        return False


def migrate_usage_stats(guest_session_id: str, firebase_uid: str) -> bool:
    """
    Migrate usage statistics from guest session to user account.

    Args:
        guest_session_id: Guest session ID
        firebase_uid: Firebase user ID

    Returns:
        True if successful, False otherwise
    """
    try:
        guest_usage = load_usage_stats_from_firebase(guest_session_id)
        if guest_usage:
            # Merge guest usage stats with any existing user stats
            success = merge_guest_stats_to_firebase(firebase_uid, guest_usage)
            if success:
                logger.info("Migrated usage statistics")
                return True
        return False
    except Exception as e:
        logger.error(f"Error migrating usage stats: {e}")
        return False


def migrate_history(guest_session_id: str, firebase_uid: str) -> bool:
    """
    Migrate generation history from guest session to user account.

    Args:
        guest_session_id: Guest session ID
        firebase_uid: Firebase user ID

    Returns:
        True if successful, False otherwise
    """
    try:
        db = get_firestore_client()
        if not db:
            return False

        # Get all history documents for the guest session
        history_docs = db.collection("users").document(guest_session_id).collection("history").stream()

        migrated_count = 0
        for doc in history_docs:
            history_data = doc.to_dict()
            # Create new document under user account
            doc_ref = db.collection("users").document(firebase_uid).collection("history").document()
            doc_ref.set(history_data)
            migrated_count += 1

        logger.info(f"Migrated {migrated_count} history entries")
        return True

    except Exception as e:
        logger.error(f"Error migrating history: {e}")
        return False


def mark_migration_complete(firebase_uid: str, guest_session_id: str) -> bool:
    """
    Mark migration as complete in user metadata.

    Args:
        firebase_uid: Firebase user ID
        guest_session_id: Original guest session ID

    Returns:
        True if successful, False otherwise
    """
    try:
        db = get_firestore_client()
        if not db:
            return False

        migration_data = {
            "migrated_from_session": guest_session_id,
            "migration_timestamp": datetime.now().isoformat(),
            "migration_version": "1.0"
        }
        migration_ref = db.collection("users").document(firebase_uid).collection("metadata").document("migration")
        migration_ref.set(migration_data)

        logger.info("Migration completion marked")
        return True

    except Exception as e:
        logger.error(f"Error marking migration complete: {e}")
        return False


def is_data_migrated(firebase_uid: str) -> bool:
    """
    Check if data has already been migrated for this user.

    Args:
        firebase_uid: Firebase user ID

    Returns:
        True if migration already completed, False otherwise
    """
    try:
        db = get_firestore_client()
        if not db:
            return False

        migration_ref = db.collection("users").document(firebase_uid).collection("metadata").document("migration")
        doc = migration_ref.get()

        return doc.exists

    except Exception as e:
        logger.error(f"Error checking migration status: {e}")
        return False