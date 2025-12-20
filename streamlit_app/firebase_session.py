# Firebase session module
# Extracted from firebase_manager.py for better separation of concerns

import logging
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