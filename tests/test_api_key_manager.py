"""
Tests for API key manager and sync manager — cloud CRUD, push/pull flows,
and error handling.

Covers:
- APIKeyManager.save_api_keys_to_cloud (encrypted for signed-in, plain for guest)
- APIKeyManager.load_api_keys_from_cloud (decryption)
- APIKeyManager.get_api_keys / update_api_keys
- SyncManager.load_cloud_data
- SyncManager.safe_sync
- Error handling for Firebase unavailable scenarios
"""

import pytest
from unittest.mock import patch, MagicMock


class FakeSessionState(dict):
    """dict subclass that supports attribute access (like st.session_state)."""
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError:
            raise AttributeError(key)


@pytest.fixture(autouse=True)
def mock_streamlit():
    """Mock streamlit across all modules."""
    fake = FakeSessionState()
    with patch("streamlit_app.services.settings.api_key_manager.st") as mock_akm_st, \
         patch("streamlit_app.services.settings.sync_manager.st") as mock_sync_st:
        mock_akm_st.session_state = fake
        mock_akm_st.error = MagicMock()
        mock_akm_st.success = MagicMock()
        mock_akm_st.warning = MagicMock()
        mock_sync_st.session_state = fake
        mock_sync_st.error = MagicMock()
        mock_sync_st.success = MagicMock()
        mock_sync_st.warning = MagicMock()
        yield fake


# ──────────────────────────────────────────────────────────
# APIKeyManager — save_api_keys_to_cloud
# ──────────────────────────────────────────────────────────

class TestAPIKeyManagerSave:
    """Test saving API keys to cloud."""

    @patch("streamlit_app.services.settings.api_key_manager.persist_api_keys")
    def test_save_signed_in_user(self, mock_persist, mock_streamlit):
        """Signed-in user → keys saved with user_uid for encryption."""
        from streamlit_app.services.settings.api_key_manager import APIKeyManager

        mock_streamlit["user"] = {"uid": "firebase_uid_1"}
        mock_streamlit["google_api_key"] = "gemini_key"
        mock_streamlit["google_tts_api_key"] = "tts_key"
        mock_streamlit["pixabay_api_key"] = "pix_key"

        with patch("streamlit_app.services.firebase.is_firebase_initialized",
                    return_value=True), \
             patch("streamlit_app.services.firebase.save_settings_to_firebase",
                    return_value=True) as mock_save:
            mgr = APIKeyManager()
            result = mgr.save_api_keys_to_cloud()

        assert result is True
        call_kwargs = mock_save.call_args
        assert call_kwargs[1]["user_uid"] == "firebase_uid_1"
        assert call_kwargs[0][0] == "firebase_uid_1"

    @patch("streamlit_app.services.settings.api_key_manager.persist_api_keys")
    def test_save_missing_gemini_key_fails(self, mock_persist, mock_streamlit):
        """Missing Gemini key → save rejected (required)."""
        from streamlit_app.services.settings.api_key_manager import APIKeyManager

        mock_streamlit["user"] = {"uid": "uid1"}
        mock_streamlit["google_tts_api_key"] = "tts_key"

        with patch("streamlit_app.services.firebase.is_firebase_initialized",
                    return_value=True):
            mgr = APIKeyManager()
            result = mgr.save_api_keys_to_cloud()

        assert result is False

    @patch("streamlit_app.services.settings.api_key_manager.persist_api_keys")
    def test_save_firebase_unavailable(self, mock_persist, mock_streamlit):
        """Firebase not initialized → save returns False."""
        from streamlit_app.services.settings.api_key_manager import APIKeyManager

        mock_streamlit["google_api_key"] = "key"

        with patch("streamlit_app.services.firebase.is_firebase_initialized",
                    return_value=False):
            mgr = APIKeyManager()
            result = mgr.save_api_keys_to_cloud()

        assert result is False

    @patch("streamlit_app.services.settings.api_key_manager.persist_api_keys")
    def test_save_no_session_id_no_user(self, mock_persist, mock_streamlit):
        """No user and no session_id → save fails."""
        from streamlit_app.services.settings.api_key_manager import APIKeyManager

        mock_streamlit["google_api_key"] = "key"

        with patch("streamlit_app.services.firebase.is_firebase_initialized",
                    return_value=True), \
             patch("streamlit_app.services.firebase.save_settings_to_firebase",
                    return_value=True):
            mgr = APIKeyManager()
            result = mgr.save_api_keys_to_cloud()

        assert result is False


# ──────────────────────────────────────────────────────────
# APIKeyManager — load_api_keys_from_cloud
# ──────────────────────────────────────────────────────────

class TestAPIKeyManagerLoad:
    """Test loading API keys from cloud."""

    @patch("streamlit_app.services.settings.api_key_manager.persist_api_keys")
    def test_load_signed_in_user(self, mock_persist, mock_streamlit):
        """Signed-in user → keys loaded with decryption via user_uid."""
        from streamlit_app.services.settings.api_key_manager import APIKeyManager

        mock_streamlit["user"] = {"uid": "uid1"}

        cloud_data = {
            "google_api_key": "decrypted_gemini",
            "google_tts_api_key": "decrypted_tts",
            "pixabay_api_key": "decrypted_pix",
        }

        with patch("streamlit_app.services.firebase.is_firebase_initialized",
                    return_value=True), \
             patch("streamlit_app.services.firebase.load_settings_from_firebase",
                    return_value=cloud_data):
            mgr = APIKeyManager()
            result = mgr.load_api_keys_from_cloud()

        assert result is True
        assert mock_streamlit["google_api_key"] == "decrypted_gemini"
        assert mock_streamlit["google_tts_api_key"] == "decrypted_tts"
        assert mock_streamlit["pixabay_api_key"] == "decrypted_pix"
        mock_persist.assert_called_once()

    @patch("streamlit_app.services.settings.api_key_manager.persist_api_keys")
    def test_load_no_cloud_data(self, mock_persist, mock_streamlit):
        """No data in cloud → returns False."""
        from streamlit_app.services.settings.api_key_manager import APIKeyManager

        mock_streamlit["user"] = {"uid": "uid1"}

        with patch("streamlit_app.services.firebase.load_settings_from_firebase",
                    return_value=None), \
             patch("streamlit_app.services.firebase.is_firebase_initialized",
                    return_value=True):
            mgr = APIKeyManager()
            result = mgr.load_api_keys_from_cloud()

        assert result is False

    @patch("streamlit_app.services.settings.api_key_manager.persist_api_keys")
    def test_load_partial_keys(self, mock_persist, mock_streamlit):
        """Cloud has only some keys → loads what's available."""
        from streamlit_app.services.settings.api_key_manager import APIKeyManager

        mock_streamlit["user"] = {"uid": "uid1"}

        cloud_data = {"google_api_key": "gemini_only"}

        with patch("streamlit_app.services.firebase.load_settings_from_firebase",
                    return_value=cloud_data), \
             patch("streamlit_app.services.firebase.is_firebase_initialized",
                    return_value=True):
            mgr = APIKeyManager()
            result = mgr.load_api_keys_from_cloud()

        assert result is True
        assert mock_streamlit["google_api_key"] == "gemini_only"
        assert mock_streamlit.get("google_tts_api_key") is None


# ──────────────────────────────────────────────────────────
# APIKeyManager — get/update helpers
# ──────────────────────────────────────────────────────────

class TestAPIKeyManagerHelpers:
    """Test get_api_keys and update_api_keys."""

    @patch("streamlit_app.services.settings.api_key_manager.persist_api_keys")
    def test_get_api_keys_returns_set_keys(self, mock_persist, mock_streamlit):
        from streamlit_app.services.settings.api_key_manager import APIKeyManager

        mock_streamlit["google_api_key"] = "g1"
        mock_streamlit["pixabay_api_key"] = "p1"

        mgr = APIKeyManager()
        keys = mgr.get_api_keys()
        assert keys == {"google_api_key": "g1", "pixabay_api_key": "p1"}

    @patch("streamlit_app.services.settings.api_key_manager.persist_api_keys")
    def test_get_api_keys_empty_session(self, mock_persist, mock_streamlit):
        from streamlit_app.services.settings.api_key_manager import APIKeyManager

        mgr = APIKeyManager()
        keys = mgr.get_api_keys()
        assert keys == {}

    @patch("streamlit_app.services.settings.api_key_manager.persist_api_keys")
    def test_update_api_keys_sets_session(self, mock_persist, mock_streamlit):
        from streamlit_app.services.settings.api_key_manager import APIKeyManager

        mgr = APIKeyManager()
        mgr.update_api_keys(google_key="new_gem", tts_key="new_tts")

        assert mock_streamlit["google_api_key"] == "new_gem"
        assert mock_streamlit["google_tts_api_key"] == "new_tts"
        mock_persist.assert_called_once()

    @patch("streamlit_app.services.settings.api_key_manager.persist_api_keys")
    def test_update_partial_keys(self, mock_persist, mock_streamlit):
        """Updating only one key doesn't affect others."""
        from streamlit_app.services.settings.api_key_manager import APIKeyManager

        mock_streamlit["google_api_key"] = "existing"
        mgr = APIKeyManager()
        mgr.update_api_keys(pixabay_key="new_pix")

        assert mock_streamlit["google_api_key"] == "existing"
        assert mock_streamlit["pixabay_api_key"] == "new_pix"


# ──────────────────────────────────────────────────────────
# SyncManager — load_cloud_data
# ──────────────────────────────────────────────────────────

class TestSyncManagerLoad:
    """Test SyncManager.load_cloud_data pull flow."""

    def test_load_cloud_data_signed_in(self, mock_streamlit):
        """Signed-in user → loads and restores all API keys."""
        from streamlit_app.services.settings.sync_manager import SyncManager

        mock_streamlit["user"] = {"uid": "sync_uid"}
        cloud = {
            "google_api_key": "synced_gem",
            "google_tts_api_key": "synced_tts",
            "pixabay_api_key": "synced_pix",
            "theme": "dark",
        }

        with patch("streamlit_app.services.firebase.load_settings_from_firebase",
                    return_value=cloud) as mock_load:
            mgr = SyncManager()
            result = mgr.load_cloud_data()

        assert result is True
        assert mock_streamlit["google_api_key"] == "synced_gem"
        assert mock_streamlit["google_tts_api_key"] == "synced_tts"
        assert mock_streamlit["theme"] == "dark"

    def test_load_cloud_data_not_signed_in(self, mock_streamlit):
        """No user → returns False immediately."""
        from streamlit_app.services.settings.sync_manager import SyncManager

        mgr = SyncManager()
        result = mgr.load_cloud_data()
        assert result is False

    def test_load_cloud_data_no_data(self, mock_streamlit):
        """Signed in but no cloud data → returns False."""
        from streamlit_app.services.settings.sync_manager import SyncManager

        mock_streamlit["user"] = {"uid": "uid_no_data"}

        with patch("streamlit_app.services.firebase.load_settings_from_firebase",
                    return_value=None):
            mgr = SyncManager()
            result = mgr.load_cloud_data()

        assert result is False

    def test_load_cloud_data_exception(self, mock_streamlit):
        """Exception during load → returns False gracefully."""
        from streamlit_app.services.settings.sync_manager import SyncManager

        mock_streamlit["user"] = {"uid": "uid_err"}

        with patch("streamlit_app.services.firebase.load_settings_from_firebase",
                    side_effect=Exception("network error")):
            mgr = SyncManager()
            result = mgr.load_cloud_data()

        assert result is False


# ──────────────────────────────────────────────────────────
# SyncManager — safe_sync
# ──────────────────────────────────────────────────────────

class TestSyncManagerSafeSync:
    """Test safe_sync wrapper."""

    def test_safe_sync_not_signed_in(self, mock_streamlit):
        """Not signed in → safe_sync returns False."""
        from streamlit_app.services.settings.sync_manager import SyncManager

        with patch.object(SyncManager, "is_firebase_available", return_value=True), \
             patch.object(SyncManager, "is_user_signed_in", return_value=False):
            mgr = SyncManager()
            result = mgr.safe_sync()

        assert result is False

    def test_safe_sync_firebase_unavailable(self, mock_streamlit):
        """Firebase unavailable → safe_sync returns False."""
        from streamlit_app.services.settings.sync_manager import SyncManager

        with patch.object(SyncManager, "is_firebase_available", return_value=False):
            mgr = SyncManager()
            result = mgr.safe_sync()

        assert result is False
