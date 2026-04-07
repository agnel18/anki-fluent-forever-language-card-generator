"""
Sync Manager Service
Handles cloud synchronization and guest data export/import operations.
"""

import streamlit as st
import datetime
import time
from typing import Dict, Optional, Any
import json


class SyncManager:
    """Manages data synchronization and backup operations."""

    def __init__(self):
        """Initialize the sync manager."""
        pass

    def sync_user_data(self) -> bool:
        """
        Synchronize user data to the cloud.

        Returns:
            True if sync successful, False otherwise
        """
        try:
            from streamlit_app.services.firebase import save_settings_to_firebase, save_usage_stats_to_firebase, sync_progress_to_firebase

            session_id = st.session_state.get("session_id", "")
            if not session_id:
                st.error("❌ No session ID available")
                return False

            # Determine Firebase UID for encryption (None for guests)
            user_uid = None
            user = st.session_state.get("user")
            if user:
                user_uid = user.get("uid")

            # Sync settings (API keys are encrypted if user_uid is available)
            settings_data = self._collect_local_settings()
            doc_id = user_uid or session_id
            settings_success = save_settings_to_firebase(doc_id, settings_data, user_uid=user_uid)

            # Sync usage stats
            stats_success = save_usage_stats_to_firebase(session_id, self._collect_local_stats())

            # Sync progress
            progress_success = sync_progress_to_firebase(session_id, self._collect_local_progress())

            if settings_success and stats_success and progress_success:
                st.success("✅ Data synced successfully!")
                return True
            else:
                st.error("❌ Sync failed - some data may not have been saved")
                return False

        except Exception as e:
            st.error(f"❌ Sync failed: {e}")
            return False

    def load_cloud_data(self) -> bool:
        """
        Load user data from Firestore into session state (pull).
        Handles encrypted API key decryption for signed-in users.

        Returns:
            True if data loaded successfully, False otherwise
        """
        try:
            from streamlit_app.services.firebase import load_settings_from_firebase

            user = st.session_state.get("user")
            if not user:
                return False

            user_uid = user.get("uid")
            doc_id = user_uid or st.session_state.get("session_id", "")
            if not doc_id:
                return False

            settings = load_settings_from_firebase(doc_id, user_uid=user_uid)
            if not settings:
                return False

            # Restore API keys to session state
            for key in ("google_api_key", "google_tts_api_key", "pixabay_api_key"):
                if key in settings and settings[key]:
                    st.session_state[key] = settings[key]

            # Restore preferences
            if "theme" in settings:
                st.session_state["theme"] = settings["theme"]
            if "per_language_settings" in settings:
                st.session_state["per_language_settings"] = settings["per_language_settings"]

            return True

        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Failed to load cloud data: {e}")
            return False

    def safe_sync(self) -> bool:
        """
        Safe sync wrapper — checks Firebase availability and sign-in status.

        Returns:
            True if sync successful, False otherwise
        """
        if not self.is_firebase_available() or not self.is_user_signed_in():
            return False
        return self.sync_user_data()

    def _collect_local_settings(self) -> Dict[str, Any]:
        """
        Collect local settings for synchronization.

        Returns:
            Dictionary of local settings
        """
        from .preferences_manager import PreferencesManager
        from .api_key_manager import APIKeyManager

        prefs_manager = PreferencesManager()
        api_manager = APIKeyManager()

        settings = {
            'theme': prefs_manager.get_theme(),
            'sync_preferences': prefs_manager.get_sync_preferences(),
            'learned_languages': prefs_manager.get_favorite_languages(),
            'per_language_settings': st.session_state.get('per_language_settings', {}),
        }

        # Only include API keys if they're set
        google_key = api_manager.get_api_keys()
        if google_key:
            settings['google_api_key'] = google_key

        return settings

    def _collect_local_stats(self) -> Dict[str, Any]:
        """
        Collect local usage stats for synchronization.

        Returns:
            Dictionary of local usage stats
        """
        return st.session_state.get('persistent_usage_stats', {})

    def _collect_local_progress(self) -> Dict[str, Dict[str, Any]]:
        """
        Collect local progress data for synchronization.

        Returns:
            Dictionary of progress data by language
        """
        # For now, return empty dict as progress sync may not be implemented yet
        # TODO: Implement proper progress data collection from database/session state
        return st.session_state.get('user_progress', {})

    def export_guest_data(self) -> Optional[str]:
        """
        Export guest user data for backup.

        Returns:
            JSON string of guest data, or None if failed
        """
        try:
            guest_data = {
                'exported_at': datetime.datetime.now().isoformat(),
                'version': '1.0',
                'settings': self._collect_local_settings(),
                'usage_stats': st.session_state.get('persistent_usage_stats', {}),
                'note': 'This is a guest data export. Import this file on another device to restore your settings.'
            }

            return json.dumps(guest_data, indent=2)

        except Exception as e:
            st.error(f"❌ Failed to export guest data: {e}")
            return None

    def import_guest_data(self, json_data: str) -> bool:
        """
        Import guest user data from backup.

        Args:
            json_data: JSON string containing guest data

        Returns:
            True if import successful, False otherwise
        """
        try:
            backup_data = json.loads(json_data)

            # Validate backup format
            if 'settings' not in backup_data:
                st.error("❌ Invalid backup file format")
                return False

            # Restore settings
            settings = backup_data['settings']
            for key, value in settings.items():
                st.session_state[key] = value

            # Restore usage stats if present
            if 'usage_stats' in backup_data:
                st.session_state['persistent_usage_stats'] = backup_data['usage_stats']

            return True

        except Exception as e:
            st.error(f"❌ Failed to import backup: {e}")
            return False

    def is_firebase_available(self) -> bool:
        """
        Check if Firebase is available for operations.

        Returns:
            True if Firebase is initialized, False otherwise
        """
        try:
            from streamlit_app.services.firebase import is_firebase_initialized
            return is_firebase_initialized()
        except:
            return False

    def is_user_signed_in(self) -> bool:
        """
        Check if user is currently signed in.

        Returns:
            True if user is signed in, False otherwise
        """
        try:
            from streamlit_app.services.firebase import is_signed_in
            return is_signed_in()
        except:
            return False