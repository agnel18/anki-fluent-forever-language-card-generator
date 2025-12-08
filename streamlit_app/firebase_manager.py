"""
Firebase Manager for Language Learning App
Handles user sessions, progress sync, and statistics persistence
Supports anonymous authentication and Firestore data storage
"""

import logging
import os
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

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
    
    Args:
        config_path: Path to Firebase service account key JSON
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
    
    try:
        # Determine config path
        if config_path is None:
            config_path = Path(__file__).parent.parent / "firebase_config.json"
        
        config_path = Path(config_path)
        
        if not config_path.exists():
            logger.warning(f"Firebase config not found at {config_path}")
            logger.info("Firebase sync disabled. Progress will only be saved locally.")
            return False
        
        # Initialize Firebase
        cred = credentials.Certificate(str(config_path))
        firebase_admin.initialize_app(cred, {
            'projectId': json.load(open(config_path))['project_id']
        })
        
        firebase_initialized = True
        logger.info("✅ Firebase initialized successfully")
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
# INITIALIZATION
# ============================================================================

# Try to initialize Firebase on import
try:
    init_firebase()
except Exception as e:
    logger.debug(f"Firebase auto-init: {e}")
