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

# Import Firebase service modules (with fallback)
try:
    from firebase_auth import get_session_id, is_signed_in, sign_in_with_google, sign_out
    from firebase_sync import sync_progress_to_firebase, sync_stats_to_firebase, load_progress_from_firebase
    from firebase_stats import update_usage_stats_to_firebase, load_usage_stats_from_firebase, merge_guest_stats_to_firebase, log_generation_to_firebase, get_generation_history
    from firebase_session import create_user_session, update_last_active
    logger.info("Using new Firebase service modules")
except ImportError as e:
    logger.warning(f"Could not import Firebase service modules: {e}, using fallback functions")
    # Fallback functions will be defined later in the file

# ============================================================================
# USAGE STATS PERSISTENCE
# ============================================================================

def update_usage_stats_to_firebase(session_id: str, stats_delta: Dict, language: Optional[str] = None) -> bool:
    """
    Incrementally update persistent usage stats for a user in Firebase.
    Args:
        session_id: User/session ID
        stats_delta: Dict of fields to increment (e.g., {"groq_calls": 2, "pixabay_calls": 1})
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

# ============================================================================
# USAGE STATS LOAD & MERGE
# ============================================================================
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
"""
Firebase Manager for Language Learning App
Handles user sessions, progress sync, and statistics persistence
Supports anonymous authentication and Firestore data storage
"""

# Firebase will be initialized on demand
firebase_initialized = False
firebase_available = False

try:
    import firebase_admin
    from firebase_admin import credentials, firestore, auth
    firebase_available = True
except ImportError:
    logger.warning("Firebase SDK not installed. Install with: pip install firebase-admin")
    firebase_available = False


# ============================================================================
# FIREBASE INITIALIZATION
# ============================================================================

def init_firebase(config_path: Optional[Path] = None) -> bool:
    """
    Initialize Firebase admin SDK.
    First tries to use Streamlit secrets, then falls back to config file.

    Args:
        config_path: Path to Firebase service account key JSON (fallback only)
                    Default: LanguagLearning/firebase_config.json

    Returns:
        True if successful, False otherwise
    """
    global firebase_initialized

    if not firebase_available:
        logger.error("Firebase SDK not available. Install with: pip install firebase-admin")
        return False

    if firebase_initialized:
        return True

    # Check if Firebase app already exists
    if firebase_admin._apps:
        firebase_initialized = True
        logger.info("✅ Firebase already initialized")
        return True

    try:
        # First try to initialize with Streamlit secrets
        try:
            import streamlit as st
            project_id = st.secrets.get("FIREBASE_PROJECT_ID")

            if project_id:
                logger.info("Initializing Firebase with Streamlit secrets...")

                # For Firebase Admin SDK, we need service account credentials
                private_key = st.secrets.get("FIREBASE_PRIVATE_KEY")
                client_email = st.secrets.get("FIREBASE_CLIENT_EMAIL")

                if private_key and client_email:
                    logger.info("Found service account credentials, creating certificate...")
                    # Create credentials from individual secrets
                    cred_dict = {
                        "type": "service_account",
                        "project_id": project_id,
                        "private_key_id": st.secrets.get("FIREBASE_PRIVATE_KEY_ID", ""),
                        "private_key": private_key.replace('\\n', '\n'),
                        "client_email": client_email,
                        "client_id": st.secrets.get("FIREBASE_CLIENT_ID", ""),
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                        "client_x509_cert_url": st.secrets.get("FIREBASE_CLIENT_X509_CERT_URL", "")
                    }

                    logger.info("Creating Firebase credentials certificate...")
                    cred = credentials.Certificate(cred_dict)

                    logger.info("Initializing Firebase app...")
                    firebase_admin.initialize_app(cred, {
                        'projectId': project_id
                    })

                    firebase_initialized = True
                    logger.info("✅ Firebase initialized successfully with Streamlit secrets")
                    return True
                else:
                    logger.warning(f"Firebase service account secrets incomplete - missing private_key or client_email. Available secrets: {list(st.secrets.keys()) if hasattr(st, 'secrets') else 'No secrets available'}")
            else:
                logger.debug(f"Firebase project_id not found in secrets")

        except Exception as secrets_error:
            logger.error(f"Streamlit secrets initialization failed: {secrets_error}")
            logger.debug(f"Secrets error details: {str(secrets_error)}")

        # Fallback to config file
        logger.info("Falling back to config file initialization...")
        if config_path is None:
            config_path = Path(__file__).parent.parent / "firebase_config.json"

        config_path = Path(config_path)

        if not config_path.exists():
            logger.warning(f"Firebase config not found at {config_path}")
            logger.info("Firebase sync disabled. Progress will only be saved locally.")
            return False

        # Initialize Firebase with config file
        cred = credentials.Certificate(str(config_path))
        firebase_admin.initialize_app(cred, {
            'projectId': json.load(open(config_path))['project_id']
        })

        firebase_initialized = True
        logger.info("✅ Firebase initialized successfully with config file")
        return True

    except Exception as e:
        logger.warning(f"Firebase initialization failed: {e}")
        logger.info("Continuing without Firebase sync...")
        return False


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


# ============================================================================
# SETTINGS PERSISTENCE
# ============================================================================

def save_settings_to_firebase(session_id: str, settings: Dict) -> bool:
    """
    Save app settings to Firebase.
    
    Args:
        session_id: Anonymous session ID
        settings: Settings dict (difficulty, audio_speed, sentences_per_word, etc.)
        
    Returns:
        True if successful
    """
    if not firebase_initialized:
        return False
    
    try:
        db = firestore.client()
        
        doc_ref = db.collection("users").document(session_id).collection("metadata").document("settings")
        
        data = {
            **settings,
            "last_updated": datetime.now().isoformat(),
        }
        
        doc_ref.set(data, merge=True)
        return True
        
    except Exception as e:
        logger.error(f"Error saving settings: {e}")
        return False


def load_settings_from_firebase(session_id: str) -> Optional[Dict]:
    """Load settings from Firebase."""
    if not firebase_initialized:
        return None
    
    try:
        db = firestore.client()
        
        doc = db.collection("users").document(session_id).collection("metadata").document("settings").get()
        
        if doc.exists:
            data = doc.to_dict()
            # Remove timestamp
            data.pop("last_updated", None)
            return data
        
        return None
        
    except Exception as e:
        logger.error(f"Error loading settings: {e}")
        return None


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
    if firebase_available and not firebase_initialized:
        try:
            init_firebase()
        except Exception as e:
            logger.debug(f"Firebase init failed in get_sync_status: {e}")

    if not firebase_available:
        return "unavailable"

    if not firebase_initialized:
        return "unavailable"

    if is_signed_in():
        return "enabled"

    return "available"


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


# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

def create_user_session(session_id: str) -> bool:
    """Create or update user session metadata."""
    if not firebase_initialized:
        return False
    
    try:
        db = firestore.client()
        
        doc_ref = db.collection("users").document(session_id)
        
        doc_ref.set({
            "created_at": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat(),
            "status": "active",
        }, merge=True)
        
        return True
        
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        return False


def update_last_active(session_id: str) -> bool:
    """Update last active timestamp."""
    if not firebase_initialized:
        return False
    
    try:
        db = firestore.client()
        
        db.collection("users").document(session_id).update({
            "last_active": datetime.now().isoformat()
        })
        
        return True
        
    except Exception as e:
        logger.debug(f"Error updating last_active: {e}")
        return False


# ============================================================================
# AUTHENTICATION
# ============================================================================

def sign_in_with_google():
    """Handle Google OAuth sign-in flow for Streamlit."""
    try:
        import streamlit as st
        # For Streamlit Cloud, we need to use a different approach
        # since we can't do full OAuth redirects

        # Check if we have Firebase Auth initialized
        if not firebase_initialized:
            st.error("❌ Firebase not available")
            return

        # For now, we'll use a simplified approach
        # In production, you'd implement proper OAuth flow
        st.info("🔄 Redirecting to Google sign-in...")

        # This would normally redirect to Google OAuth
        # For Streamlit, we need to handle this differently
        st.session_state.page = "auth_handler"
        st.rerun()

    except Exception as e:
        logger.error(f"Error in sign_in_with_google: {e}")
        import streamlit as st
        st.error(f"❌ Sign-in failed: {e}")


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


def is_signed_in() -> bool:
    """Check if user is currently signed in."""
    try:
        import streamlit as st
        return 'user' in st.session_state and not st.session_state.get('is_guest', True)
    except:
        return False


def get_current_user():
    """Get current authenticated user info."""
    try:
        import streamlit as st
        if is_signed_in():
            return st.session_state.user
        return None
    except:
        return None


# ============================================================================
# DATA MIGRATION
# ============================================================================

def migrate_guest_data_to_user(firebase_uid: str) -> bool:
    """
    Migrate guest session data to authenticated Firebase user account.

    Args:
        firebase_uid: The Firebase UID of the authenticated user

    Returns:
        True if migration successful, False otherwise
    """
    if not firebase_initialized:
        logger.warning("Firebase not initialized, cannot migrate data")
        return False

    try:
        import streamlit as st
        db = firestore.client()

        # Get current guest session data
        guest_session_id = st.session_state.get('session_id')
        if not guest_session_id:
            logger.warning("No guest session ID found for migration")
            return False

        logger.info(f"Migrating data from guest session {guest_session_id} to user {firebase_uid}")

        # Migrate settings
        guest_settings = load_settings_from_firebase(guest_session_id)
        if guest_settings:
            # Save settings under Firebase UID
            user_settings_ref = db.collection("users").document(firebase_uid).collection("metadata").document("settings")
            user_settings_ref.set(guest_settings, merge=True)
            logger.info("Migrated settings to user account")

        # Migrate progress data for each language
        # Get all progress documents for the guest session
        progress_docs = db.collection("users").document(guest_session_id).collection("progress").stream()
        for doc in progress_docs:
            progress_data = doc.to_dict()
            # Save under Firebase UID
            user_progress_ref = db.collection("users").document(firebase_uid).collection("progress").document(doc.id)
            user_progress_ref.set(progress_data, merge=True)
            logger.info(f"Migrated progress for language: {doc.id}")

        # Migrate word stats
        word_stats_docs = db.collection("users").document(guest_session_id).collection("word_stats").stream()
        for doc in word_stats_docs:
            stats_data = doc.to_dict()
            user_stats_ref = db.collection("users").document(firebase_uid).collection("word_stats").document(doc.id)
            user_stats_ref.set(stats_data, merge=True)
            logger.info(f"Migrated word stats for language: {doc.id}")

        # Migrate usage statistics
        guest_usage = load_usage_stats_from_firebase(guest_session_id)
        if guest_usage:
            # Merge guest usage stats with any existing user stats
            merge_guest_stats_to_firebase(firebase_uid, guest_usage)
            logger.info("Migrated usage statistics")

        # Migrate generation history
        history_docs = db.collection("users").document(guest_session_id).collection("history").stream()
        for doc in history_docs:
            history_data = doc.to_dict()
            # Create new document under user account
            user_history_ref = db.collection("users").document(firebase_uid).collection("history").document()
            user_history_ref.set(history_data)
            logger.info("Migrated generation history entry")

        # Mark migration as complete in user metadata
        migration_data = {
            "migrated_from_session": guest_session_id,
            "migration_timestamp": datetime.now().isoformat(),
            "migration_version": "1.0"
        }
        migration_ref = db.collection("users").document(firebase_uid).collection("metadata").document("migration")
        migration_ref.set(migration_data)

        # Update session state to reflect migration
        st.session_state.data_migrated = True
        st.session_state.migrated_from_session = guest_session_id

        logger.info(f"✅ Successfully migrated all guest data to user {firebase_uid}")
        return True

    except Exception as e:
        logger.error(f"Error migrating guest data to user: {e}")
        return False


# ============================================================================
# INITIALIZATION
# ============================================================================

# Try to initialize Firebase on import (but defer secrets access)
try:
    # Only try basic import check here
    import firebase_admin
    from firebase_admin import credentials, firestore, auth
    firebase_available = True

    # Try to initialize immediately if we have a config file
    try:
        init_firebase()
    except Exception as e:
        logger.debug(f"Firebase auto-init failed (expected if no secrets yet): {e}")

except ImportError:
    logger.warning("Firebase SDK not installed. Install with: pip install firebase-admin")
    firebase_available = False
