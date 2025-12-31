"""
Profile Manager Service
Handles user profile operations, account management, and deck library functionality.
"""

import streamlit as st
import datetime
from typing import Dict, List, Optional, Any
import json

# Import Firebase services
from services.firebase.firebase_init import get_firestore_client


class ProfileManager:
    """Manages user profile operations and account functionality."""

    def __init__(self):
        """Initialize the profile manager."""
        pass

    def get_user_display_info(self) -> Optional[Dict[str, str]]:
        """
        Get user display information for the current signed-in user.

        Returns:
            Dict with 'name' and 'email' keys, or None if not signed in
        """
        try:
            from ..firebase import is_signed_in, get_current_user

            if not is_signed_in():
                return None

            user = get_current_user()
            if not user:
                return None

            user_email = user.get('email', 'Unknown')
            user_name = user.get('display_name', user_email.split('@')[0] if user_email != 'Unknown' else 'Unknown')

            return {
                'name': user_name,
                'email': user_email
            }
        except Exception as e:
            st.error(f"Error getting user info: {e}")
            return None

    def get_user_deck_library(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the user's deck library from Firebase.

        Args:
            limit: Maximum number of decks to retrieve

        Returns:
            List of deck dictionaries
        """
        try:
            from ..firebase import is_signed_in, get_current_user, is_firebase_initialized

            if not is_signed_in() or not is_firebase_initialized():
                return []

            user = get_current_user()
            if not user or 'uid' not in user:
                return []

            db = get_firestore_client()
            if not db:
                return []

            decks_ref = db.collection('users').document(user['uid']).collection('decks')
            decks = decks_ref.order_by('created_at', direction='DESCENDING').limit(limit).get()

            deck_list = []
            for deck_doc in decks:
                deck_data = deck_doc.to_dict()
                # Convert timestamp to readable format
                created_at = deck_data.get('created_at', 'Unknown')
                if created_at != 'Unknown' and hasattr(created_at, 'strftime'):
                    deck_data['created_at_display'] = created_at.strftime('%Y-%m-%d')
                    deck_data['created_at_full'] = created_at.strftime('%Y-%m-%d %H:%M')
                else:
                    deck_data['created_at_display'] = str(created_at).split('+')[0][:10] if created_at != 'Unknown' else 'Unknown'
                    deck_data['created_at_full'] = str(created_at).split('+')[0][:16].replace('T', ' ') if created_at != 'Unknown' else 'Unknown'

                deck_list.append(deck_data)

            return deck_list

        except Exception as e:
            st.error(f"Error loading deck library: {e}")
            return []

    def sign_out_user(self) -> bool:
        """
        Sign out the current user.

        Returns:
            True if sign out successful, False otherwise
        """
        try:
            from ..firebase import sign_out
            return sign_out()
        except Exception as e:
            st.error(f"Error signing out: {e}")
            return False

    def export_user_data(self) -> Optional[Dict[str, Any]]:
        """
        Export all user data for backup.

        Returns:
            Dictionary containing all user data, or None if failed
        """
        try:
            from ..firebase import load_settings_from_firebase, get_usage_stats, sync_progress_from_firebase

            session_id = st.session_state.get("session_id", "")
            if not session_id:
                st.error("No session ID available")
                return None

            # Collect all user data
            user_data = {
                'exported_at': datetime.datetime.now().isoformat(),
                'version': '1.0',
                'settings': load_settings_from_firebase(session_id),
                'usage_stats': get_usage_stats(session_id),
                'progress': sync_progress_from_firebase(session_id),
                'note': 'This is a complete user data export for backup purposes.'
            }

            return user_data

        except Exception as e:
            st.error(f"Error exporting user data: {e}")
            return None

    def delete_user_cloud_data(self) -> bool:
        """
        Delete all user data from the cloud.
        WARNING: This is a destructive operation.

        Returns:
            True if deletion successful, False otherwise
        """
        # TODO: Implement cloud data deletion
        # This would require coordination with all Firebase services
        st.error("⚠️ Cloud data deletion not yet implemented")
        return False