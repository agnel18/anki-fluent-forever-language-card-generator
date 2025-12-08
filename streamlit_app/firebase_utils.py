"""
Firebase integration for progress tracking and user management.
Lightweight wrapper for Firestore to track user progress without storing generated content.
"""

import json
from datetime import datetime
from typing import Optional, Dict, Any

# Note: In production, install firebase-admin and initialize
# For now, this is a mock implementation that works locally with session state

class FirebaseManager:
    """Mock Firebase manager for local testing. Swap with real Firebase when deploying."""
    
    def __init__(self):
        """Initialize Firebase manager."""
        self.data = {}
    
    def create_user(self, email: str) -> str:
        """Create a new user and return user_id."""
        user_id = f"user_{hash(email) % 1000000}"
        self.data[user_id] = {
            "email": email,
            "created_at": datetime.now().isoformat(),
            "progress": {},
            "language_preferences": {}
        }
        return user_id
    
    def get_user_progress(self, user_id: str, language: str, list_size: int) -> Optional[Dict]:
        """Get user's progress on a specific language list."""
        if user_id not in self.data:
            return None
        
        progress_key = f"{language}_{list_size}"
        return self.data[user_id]["progress"].get(progress_key)
    
    def update_progress(self, user_id: str, language: str, list_size: int, 
                       completed_count: int, last_word_index: int, last_word: str) -> bool:
        """Update user's progress on a list."""
        if user_id not in self.data:
            return False
        
        progress_key = f"{language}_{list_size}"
        self.data[user_id]["progress"][progress_key] = {
            "language": language,
            "list_size": list_size,
            "completed_words": completed_count,
            "last_word_index": last_word_index,
            "last_word": last_word,
            "last_updated": datetime.now().isoformat(),
            "percentage_complete": round((completed_count / list_size) * 100, 1)
        }
        return True
    
    def get_user_stats(self, user_id: str) -> Optional[Dict]:
        """Get overall user statistics."""
        if user_id not in self.data:
            return None
        
        progress = self.data[user_id]["progress"]
        total_words = sum(p["completed_words"] for p in progress.values())
        total_lists = len(progress)
        
        return {
            "total_words_generated": total_words,
            "total_lists_started": total_lists,
            "completed_lists": sum(1 for p in progress.values() 
                                  if p["completed_words"] == p["list_size"]),
            "in_progress_lists": sum(1 for p in progress.values() 
                                    if p["completed_words"] < p["list_size"]),
            "languages": list(set(p["language"] for p in progress.values()))
        }
    
    def reset_progress(self, user_id: str, language: str, list_size: int) -> bool:
        """Reset progress for a specific list."""
        if user_id not in self.data:
            return False
        
        progress_key = f"{language}_{list_size}"
        if progress_key in self.data[user_id]["progress"]:
            del self.data[user_id]["progress"][progress_key]
        return True


# Initialize global Firebase manager
firebase = FirebaseManager()


# ============================================================================
# PRODUCTION FIREBASE SETUP (Replace with this when deploying)
# ============================================================================

"""
To use real Firebase in production:

1. Install: pip install firebase-admin

2. Get credentials from Firebase Console:
   - Go to Project Settings > Service Accounts
   - Generate new private key (JSON)
   - Save as streamlit_app/firebase-key.json

3. Replace the mock implementation:

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.exceptions import NotFound

class FirebaseManager:
    def __init__(self):
        if not firebase_admin._apps:
            cred = credentials.Certificate("firebase-key.json")
            firebase_admin.initialize_app(cred)
        self.db = firestore.client()
    
    def create_user(self, email: str) -> str:
        user_ref = self.db.collection("users").document(email)
        user_ref.set({
            "email": email,
            "created_at": firestore.SERVER_TIMESTAMP,
            "progress": {},
            "language_preferences": {}
        })
        return email
    
    # ... implement other methods using self.db.collection().document()
"""
