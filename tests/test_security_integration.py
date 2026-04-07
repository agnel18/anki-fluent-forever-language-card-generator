"""
Integration tests for cross-component security flows.

Tests the full paths:
- Login → auto-sync → keys loaded into session
- Save API keys → encrypted push to cloud → load back matches
- Session timeout → keys cleared
- Sign out → keys cleared, cloud data unchanged
- Google Sign-In → session established → cloud data loaded
"""

import time
import os
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


@pytest.fixture
def fake_session():
    """Provide a fresh session state shared across all modules."""
    return FakeSessionState()


@pytest.fixture
def patch_all_st(fake_session):
    """Patch st.session_state in all relevant modules to share state."""
    modules = [
        "streamlit_app.services.auth.session_manager.st",
        "streamlit_app.services.auth.auth_service.st",
        "streamlit_app.services.settings.api_key_manager.st",
        "streamlit_app.services.settings.sync_manager.st",
    ]
    patchers = []
    for mod in modules:
        p = patch(mod)
        mock_st = p.start()
        mock_st.session_state = fake_session
        mock_st.secrets = MagicMock()
        mock_st.error = MagicMock()
        mock_st.success = MagicMock()
        mock_st.warning = MagicMock()
        patchers.append(p)
    yield fake_session
    for p in patchers:
        p.stop()


# ──────────────────────────────────────────────────────────
# Encryption round-trip integration
# ──────────────────────────────────────────────────────────

class TestEncryptionRoundTrip:
    """Test real encrypt → save → load → decrypt with the actual encryption service."""

    def test_save_and_load_with_real_encryption(self, patch_all_st):
        """Full round-trip: save encrypted → load decrypted via settings_service."""
        # Use REAL encryption (not mocked)
        test_secret = "test_master_secret_for_integration_tests"

        with patch.dict(os.environ, {"MASTER_ENCRYPTION_KEY": test_secret}):
            from streamlit_app.services.security.encryption_service import (
                encrypt_api_keys, decrypt_api_keys, is_encryption_available,
            )
            assert is_encryption_available()

            user_uid = "integration_test_user_1"
            original = {
                "google_api_key": "AIzaSyOriginalKey123",
                "google_tts_api_key": "AIzaTTSKey456",
                "pixabay_api_key": "pix789",
                "theme": "dark",
            }

            # Encrypt
            encrypted = encrypt_api_keys(user_uid, original)
            assert encrypted["encrypted"] is True
            assert encrypted["google_api_key"] != original["google_api_key"]
            assert encrypted["theme"] == "dark"  # Non-key field unchanged

            # Decrypt
            decrypted = decrypt_api_keys(user_uid, encrypted)
            assert decrypted["google_api_key"] == "AIzaSyOriginalKey123"
            assert decrypted["google_tts_api_key"] == "AIzaTTSKey456"
            assert decrypted["pixabay_api_key"] == "pix789"
            assert decrypted["theme"] == "dark"

    def test_wrong_user_cannot_decrypt(self, patch_all_st):
        """User B cannot decrypt User A's keys — gets empty strings."""
        test_secret = "test_master_secret_for_isolation"

        with patch.dict(os.environ, {"MASTER_ENCRYPTION_KEY": test_secret}):
            from streamlit_app.services.security.encryption_service import (
                encrypt_api_keys, decrypt_api_keys,
            )

            encrypted = encrypt_api_keys("user_A", {"google_api_key": "secret"})

            # decrypt_api_keys swallows InvalidToken and returns "" for failed fields
            result = decrypt_api_keys("user_B", encrypted)
            assert result.get("google_api_key") == ""


# ──────────────────────────────────────────────────────────
# Login → cloud sync integration
# ──────────────────────────────────────────────────────────

class TestLoginCloudSyncFlow:
    """Test the login → set_user → load_cloud_data flow."""

    def test_login_then_sync_loads_keys(self, patch_all_st):
        """After successful login, cloud sync restores API keys."""
        from streamlit_app.services.auth.session_manager import SessionManager
        from streamlit_app.services.settings.sync_manager import SyncManager

        sm = SessionManager()

        # Simulate successful login setting user
        user_data = {"uid": "uid_login_sync", "email": "test@x.com", "displayName": "Test"}
        sm.set_user(user_data)

        assert sm.is_signed_in() is True
        assert patch_all_st["user"]["uid"] == "uid_login_sync"

        # Simulate cloud data available
        cloud_keys = {
            "google_api_key": "restored_gem",
            "google_tts_api_key": "restored_tts",
            "pixabay_api_key": "restored_pix",
        }

        with patch("streamlit_app.services.firebase.load_settings_from_firebase",
                    return_value=cloud_keys):
            sync = SyncManager()
            loaded = sync.load_cloud_data()

        assert loaded is True
        assert patch_all_st["google_api_key"] == "restored_gem"
        assert patch_all_st["google_tts_api_key"] == "restored_tts"
        assert patch_all_st["pixabay_api_key"] == "restored_pix"


# ──────────────────────────────────────────────────────────
# Session timeout → key clearance
# ──────────────────────────────────────────────────────────

class TestSessionTimeoutIntegration:
    """Test that session timeout clears keys and blocks access."""

    def test_timeout_clears_keys_and_blocks_sync(self, patch_all_st):
        """After 30-min timeout, keys cleared and sync fails."""
        from streamlit_app.services.auth.session_manager import SessionManager
        from streamlit_app.services.settings.sync_manager import SyncManager

        sm = SessionManager()

        # Set up active session with keys
        sm.set_user({"uid": "uid_timeout", "email": "t@x.com"})
        patch_all_st["google_api_key"] = "secret_gem"
        patch_all_st["google_tts_api_key"] = "secret_tts"

        # Fast-forward past timeout (31 minutes ago)
        patch_all_st["last_activity"] = time.time() - 31 * 60

        # is_signed_in triggers auto-expire
        assert sm.is_signed_in() is False

        # Keys should be cleared
        assert patch_all_st.get("google_api_key") is None
        assert patch_all_st.get("google_tts_api_key") is None
        assert patch_all_st.get("user") is None

        # Sync should fail (not signed in)
        sync = SyncManager()
        result = sync.load_cloud_data()
        assert result is False


# ──────────────────────────────────────────────────────────
# Sign out → key clearance
# ──────────────────────────────────────────────────────────

class TestSignOutIntegration:
    """Test that sign-out clears session keys."""

    def test_sign_out_clears_all_keys(self, patch_all_st):
        """Explicit sign-out clears keys and sets is_guest."""
        from streamlit_app.services.auth.session_manager import SessionManager

        sm = SessionManager()
        sm.set_user({"uid": "uid_signout", "email": "s@x.com"})
        patch_all_st["google_api_key"] = "key1"
        patch_all_st["google_tts_api_key"] = "key2"
        patch_all_st["pixabay_api_key"] = "key3"

        sm.sign_out()

        assert patch_all_st.get("user") is None
        assert patch_all_st.get("is_guest") is True
        assert "google_api_key" not in patch_all_st
        assert "google_tts_api_key" not in patch_all_st
        assert "pixabay_api_key" not in patch_all_st
        assert "last_activity" not in patch_all_st


# ──────────────────────────────────────────────────────────
# Google Sign-In → session → sync
# ──────────────────────────────────────────────────────────

def _set_real_auth_exceptions(mock_firebase_auth):
    """Set real Firebase exception classes on a mocked auth module."""
    from firebase_admin.auth import ExpiredIdTokenError, RevokedIdTokenError, InvalidIdTokenError
    mock_firebase_auth.ExpiredIdTokenError = ExpiredIdTokenError
    mock_firebase_auth.RevokedIdTokenError = RevokedIdTokenError
    mock_firebase_auth.InvalidIdTokenError = InvalidIdTokenError


class TestGoogleSignInIntegration:
    """Test Google Sign-In verify_id_token → session → sync chain."""

    @patch("streamlit_app.services.auth.auth_service.auth")
    def test_google_signin_establishes_session(self, mock_firebase_auth, patch_all_st):
        """verify_id_token with valid Google token → session established."""
        from streamlit_app.services.auth.session_manager import SessionManager
        from streamlit_app.services.auth.auth_service import AuthService

        _set_real_auth_exceptions(mock_firebase_auth)
        sm = SessionManager()
        email_svc = MagicMock()
        svc = AuthService(email_service=email_svc, session_manager=sm)
        svc._firebase_initialized = True

        # Mock verify_id_token
        mock_firebase_auth.verify_id_token.return_value = {
            "uid": "google_uid_abc",
            "email": "google@gmail.com",
            "name": "Google User",
            "email_verified": True,
        }
        # Mock Firestore profile
        svc._db = MagicMock()
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {"email": "google@gmail.com"}
        svc._db.collection.return_value.document.return_value.get.return_value = mock_doc

        success, msg, user_data = svc.verify_id_token("google_id_token_xyz")

        assert success is True
        assert user_data["uid"] == "google_uid_abc"

        # Session should be active
        assert sm.is_signed_in() is True
        assert patch_all_st["user"]["uid"] == "google_uid_abc"
        assert patch_all_st.get("is_guest") is False

    @patch("streamlit_app.services.auth.auth_service.auth")
    def test_google_signin_then_sync_loads_keys(self, mock_firebase_auth, patch_all_st):
        """Full flow: Google Sign-In → verify token → sync → keys in session."""
        from streamlit_app.services.auth.session_manager import SessionManager
        from streamlit_app.services.auth.auth_service import AuthService
        from streamlit_app.services.settings.sync_manager import SyncManager

        _set_real_auth_exceptions(mock_firebase_auth)
        sm = SessionManager()
        email_svc = MagicMock()
        svc = AuthService(email_service=email_svc, session_manager=sm)
        svc._firebase_initialized = True

        mock_firebase_auth.verify_id_token.return_value = {
            "uid": "google_full_flow",
            "email": "full@gmail.com",
            "name": "Full Flow",
            "email_verified": True,
        }
        svc._db = MagicMock()
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {"email": "full@gmail.com"}
        svc._db.collection.return_value.document.return_value.get.return_value = mock_doc

        # Step 1: Verify token
        success, _, _ = svc.verify_id_token("token_full")
        assert success is True

        # Step 2: Sync cloud data
        cloud_keys = {
            "google_api_key": "google_synced_gem",
            "google_tts_api_key": "google_synced_tts",
        }
        with patch("streamlit_app.services.firebase.load_settings_from_firebase",
                    return_value=cloud_keys):
            sync = SyncManager()
            loaded = sync.load_cloud_data()

        assert loaded is True
        assert patch_all_st["google_api_key"] == "google_synced_gem"
        assert patch_all_st["google_tts_api_key"] == "google_synced_tts"


# ──────────────────────────────────────────────────────────
# Rate limit → login → lockout integration  
# ──────────────────────────────────────────────────────────

class TestRateLimitIntegration:
    """Test rate limiting works across the full auth flow."""

    @patch("streamlit_app.services.auth.auth_service.auth")
    def test_repeated_failed_logins_trigger_lockout(self, mock_firebase_auth, patch_all_st):
        """5 failed logins → 6th attempt blocked without hitting Firebase."""
        from streamlit_app.services.auth.session_manager import SessionManager
        from streamlit_app.services.auth.auth_service import AuthService

        sm = SessionManager()
        email_svc = MagicMock()
        svc = AuthService(email_service=email_svc, session_manager=sm)
        svc._firebase_initialized = True

        mock_firebase_auth.get_user_by_email.side_effect = Exception("USER_NOT_FOUND")

        # 5 failed attempts
        for _ in range(5):
            success, msg, _ = svc.authenticate_user("bad@x.com", "wrong")
            assert success is False

        # 6th attempt should be rate-limited (not reach Firebase)
        mock_firebase_auth.get_user_by_email.reset_mock()
        success, msg, _ = svc.authenticate_user("bad@x.com", "wrong")
        assert success is False
        assert "Too many attempts" in msg
        mock_firebase_auth.get_user_by_email.assert_not_called()
