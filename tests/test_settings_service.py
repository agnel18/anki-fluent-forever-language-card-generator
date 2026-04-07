"""
Tests for Firebase settings service — input validation, encryption integration,
legacy migration, and error handling.

Covers:
- _ALLOWED_SETTINGS_KEYS whitelist enforcement
- _MAX_VALUE_LENGTH (4096) and _MAX_FIELDS (20) limits
- Encryption on save when user_uid provided
- Decryption on load when 'encrypted' flag is set
- Legacy plaintext → encrypted auto-migration on load
- Graceful failure when encryption unavailable or corrupted
"""

import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from datetime import datetime


# ──────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────

def _make_mock_db(existing_doc=None):
    """Create a mock Firestore client with an optional existing document."""
    db = MagicMock()
    doc_ref = MagicMock()
    mock_doc = MagicMock()

    if existing_doc is not None:
        mock_doc.exists = True
        mock_doc.to_dict.return_value = existing_doc.copy()
    else:
        mock_doc.exists = False
        mock_doc.to_dict.return_value = None

    doc_ref.get.return_value = mock_doc
    db.collection.return_value.document.return_value.collection.return_value.document.return_value = doc_ref

    return db, doc_ref


@pytest.fixture
def mock_firebase_ready():
    """Patch firebase_init so settings_service thinks Firebase is ready."""
    with patch("streamlit_app.services.firebase.settings_service.is_firebase_initialized", return_value=True), \
         patch("streamlit_app.services.firebase.settings_service.get_firestore_client") as mock_get_client:
        yield mock_get_client


@pytest.fixture
def mock_encryption():
    """Patch the encryption service used by settings_service."""
    mock_enc = MagicMock()
    mock_enc.is_encryption_available.return_value = True
    mock_enc.API_KEY_FIELDS = frozenset({"google_api_key", "google_tts_api_key", "pixabay_api_key"})

    def fake_encrypt(uid, d):
        result = d.copy()
        for k in mock_enc.API_KEY_FIELDS:
            if k in result and result[k]:
                result[k] = f"ENC({result[k]})"
        result["encrypted"] = True
        return result

    def fake_decrypt(uid, d):
        result = d.copy()
        for k in mock_enc.API_KEY_FIELDS:
            if k in result and isinstance(result[k], str) and result[k].startswith("ENC("):
                result[k] = result[k][4:-1]
        result.pop("encrypted", None)
        return result

    mock_enc.encrypt_api_keys.side_effect = fake_encrypt
    mock_enc.decrypt_api_keys.side_effect = fake_decrypt

    with patch("streamlit_app.services.firebase.settings_service._get_encryption", return_value=mock_enc):
        yield mock_enc


# ──────────────────────────────────────────────────────────
# Input Validation — save_settings_to_firebase
# ──────────────────────────────────────────────────────────

class TestInputValidation:
    """Test input validation on save_settings_to_firebase."""

    def test_disallowed_keys_filtered(self, mock_firebase_ready, mock_encryption):
        """Keys not in _ALLOWED_SETTINGS_KEYS are silently dropped."""
        from streamlit_app.services.firebase.settings_service import save_settings_to_firebase

        db, doc_ref = _make_mock_db()
        mock_firebase_ready.return_value = db

        settings = {
            "google_api_key": "valid_key",
            "evil_injected_field": "hacker_data",
            "__proto__": "attack",
        }
        result = save_settings_to_firebase("session1", settings, user_uid="uid1")
        assert result is True

        # Check what was actually saved
        saved = doc_ref.set.call_args[0][0]
        assert "evil_injected_field" not in saved
        assert "__proto__" not in saved
        assert "google_api_key" in saved or "ENC(" in str(saved.get("google_api_key", ""))

    def test_too_many_fields_rejected(self, mock_firebase_ready, mock_encryption):
        """More than _MAX_FIELDS (20) top-level fields → save rejected."""
        from streamlit_app.services.firebase.settings_service import save_settings_to_firebase

        db, doc_ref = _make_mock_db()
        mock_firebase_ready.return_value = db

        # 21 fields — exceeds limit
        settings = {f"field_{i}": f"value_{i}" for i in range(21)}
        result = save_settings_to_firebase("session1", settings)
        assert result is False
        doc_ref.set.assert_not_called()

    def test_oversized_value_rejected(self, mock_firebase_ready, mock_encryption):
        """A string value > 4096 chars → save rejected."""
        from streamlit_app.services.firebase.settings_service import save_settings_to_firebase

        db, doc_ref = _make_mock_db()
        mock_firebase_ready.return_value = db

        settings = {"google_api_key": "A" * 5000}
        result = save_settings_to_firebase("session1", settings, user_uid="uid1")
        assert result is False
        doc_ref.set.assert_not_called()

    def test_value_at_max_length_accepted(self, mock_firebase_ready, mock_encryption):
        """Exactly 4096 chars → allowed."""
        from streamlit_app.services.firebase.settings_service import save_settings_to_firebase

        db, doc_ref = _make_mock_db()
        mock_firebase_ready.return_value = db

        settings = {"google_api_key": "A" * 4096}
        result = save_settings_to_firebase("session1", settings, user_uid="uid1")
        assert result is True

    def test_empty_settings_after_filter_rejected(self, mock_firebase_ready) :
        """If ALL keys are disallowed, save is rejected (no empty writes)."""
        from streamlit_app.services.firebase.settings_service import save_settings_to_firebase

        db, doc_ref = _make_mock_db()
        mock_firebase_ready.return_value = db

        settings = {"evil": "hack", "admin": True}
        result = save_settings_to_firebase("session1", settings)
        assert result is False
        doc_ref.set.assert_not_called()

    def test_non_string_values_bypass_length_check(self, mock_firebase_ready, mock_encryption):
        """Non-string values (bools, dicts) skip the max-length check."""
        from streamlit_app.services.firebase.settings_service import save_settings_to_firebase

        db, doc_ref = _make_mock_db()
        mock_firebase_ready.return_value = db

        settings = {
            "google_api_key": "valid",
            "per_language_settings": {"fr": {"speed": 1.2}},  # dict, not string
        }
        result = save_settings_to_firebase("session1", settings, user_uid="uid1")
        assert result is True


# ──────────────────────────────────────────────────────────
# Encryption on Save
# ──────────────────────────────────────────────────────────

class TestEncryptionOnSave:
    """Test encryption integration during save."""

    def test_save_with_uid_encrypts_api_keys(self, mock_firebase_ready, mock_encryption):
        """When user_uid is provided, API key fields are encrypted before storage."""
        from streamlit_app.services.firebase.settings_service import save_settings_to_firebase

        db, doc_ref = _make_mock_db()
        mock_firebase_ready.return_value = db

        settings = {"google_api_key": "AIzaSy_test123", "theme": "dark"}
        result = save_settings_to_firebase("uid1", settings, user_uid="uid1")
        assert result is True

        mock_encryption.encrypt_api_keys.assert_called_once()
        saved = doc_ref.set.call_args[0][0]
        # API key should be encrypted
        assert saved["google_api_key"] == "ENC(AIzaSy_test123)"
        # Non-key fields should be plaintext
        assert saved["theme"] == "dark"
        # Encrypted flag set
        assert saved["encrypted"] is True

    def test_save_without_uid_no_encryption(self, mock_firebase_ready):
        """When user_uid is None (guest), keys are saved as plaintext."""
        from streamlit_app.services.firebase.settings_service import save_settings_to_firebase

        db, doc_ref = _make_mock_db()
        mock_firebase_ready.return_value = db

        settings = {"google_api_key": "AIzaSy_guest"}
        result = save_settings_to_firebase("session_abc", settings, user_uid=None)
        assert result is True

        saved = doc_ref.set.call_args[0][0]
        assert saved["google_api_key"] == "AIzaSy_guest"
        assert "encrypted" not in saved or saved.get("encrypted") is not True

    def test_encryption_failure_aborts_save(self, mock_firebase_ready):
        """If encryption raises, save is aborted to protect plaintext keys."""
        from streamlit_app.services.firebase.settings_service import save_settings_to_firebase

        db, doc_ref = _make_mock_db()
        mock_firebase_ready.return_value = db

        mock_enc = MagicMock()
        mock_enc.is_encryption_available.return_value = True
        mock_enc.encrypt_api_keys.side_effect = RuntimeError("crypto failure")

        with patch("streamlit_app.services.firebase.settings_service._get_encryption", return_value=mock_enc):
            result = save_settings_to_firebase("uid1", {"google_api_key": "key"}, user_uid="uid1")

        assert result is False
        doc_ref.set.assert_not_called()


# ──────────────────────────────────────────────────────────
# Decryption on Load
# ──────────────────────────────────────────────────────────

class TestDecryptionOnLoad:
    """Test decryption and migration during load."""

    def test_load_encrypted_doc_decrypts(self, mock_firebase_ready, mock_encryption):
        """Loading a doc with encrypted=True decrypts API keys."""
        from streamlit_app.services.firebase.settings_service import load_settings_from_firebase

        stored = {
            "google_api_key": "ENC(real_key)",
            "google_tts_api_key": "ENC(tts_key)",
            "theme": "dark",
            "encrypted": True,
            "last_updated": "2026-04-07T10:00:00",
        }
        db, doc_ref = _make_mock_db(stored)
        mock_firebase_ready.return_value = db

        result = load_settings_from_firebase("uid1", user_uid="uid1")
        assert result is not None
        assert result["google_api_key"] == "real_key"
        assert result["google_tts_api_key"] == "tts_key"
        assert result["theme"] == "dark"
        # Metadata should be stripped
        assert "encrypted" not in result
        assert "last_updated" not in result

    def test_load_legacy_plaintext_migrates(self, mock_firebase_ready, mock_encryption):
        """Loading legacy plaintext doc auto-encrypts and re-saves."""
        from streamlit_app.services.firebase.settings_service import load_settings_from_firebase

        stored = {
            "google_api_key": "plaintext_key",
            "theme": "light",
            # No "encrypted" flag — legacy
        }
        db, doc_ref = _make_mock_db(stored)
        mock_firebase_ready.return_value = db

        result = load_settings_from_firebase("uid1", user_uid="uid1")
        assert result is not None
        # Returns plaintext for immediate use
        assert result["google_api_key"] == "plaintext_key"
        # But should have re-saved encrypted version to Firestore
        doc_ref.set.assert_called_once()
        saved = doc_ref.set.call_args[0][0]
        assert saved.get("encrypted") is True

    def test_load_without_uid_returns_raw(self, mock_firebase_ready):
        """Loading without user_uid returns raw data (no decryption)."""
        from streamlit_app.services.firebase.settings_service import load_settings_from_firebase

        stored = {
            "google_api_key": "ENC(cipher)",
            "encrypted": True,
            "last_updated": "2026-04-07",
        }
        db, _ = _make_mock_db(stored)
        mock_firebase_ready.return_value = db

        result = load_settings_from_firebase("session1", user_uid=None)
        assert result is not None
        # Raw ciphertext — not decrypted
        assert result["google_api_key"] == "ENC(cipher)"

    def test_load_missing_doc_returns_none(self, mock_firebase_ready):
        """Non-existent Firestore document returns None."""
        from streamlit_app.services.firebase.settings_service import load_settings_from_firebase

        db, _ = _make_mock_db(None)  # No document
        mock_firebase_ready.return_value = db

        result = load_settings_from_firebase("nonexistent_uid")
        assert result is None

    def test_decryption_failure_returns_none(self, mock_firebase_ready):
        """If decryption fails, returns None (not garbled data)."""
        from streamlit_app.services.firebase.settings_service import load_settings_from_firebase

        stored = {"google_api_key": "corrupted_cipher", "encrypted": True}
        db, _ = _make_mock_db(stored)
        mock_firebase_ready.return_value = db

        mock_enc = MagicMock()
        mock_enc.decrypt_api_keys.side_effect = Exception("InvalidToken")

        with patch("streamlit_app.services.firebase.settings_service._get_encryption", return_value=mock_enc):
            result = load_settings_from_firebase("uid1", user_uid="uid1")

        assert result is None

    def test_firebase_not_initialized_returns_none(self):
        """If Firebase not initialized, load returns None immediately."""
        from streamlit_app.services.firebase.settings_service import load_settings_from_firebase

        with patch("streamlit_app.services.firebase.settings_service.is_firebase_initialized", return_value=False):
            result = load_settings_from_firebase("uid1")
        assert result is None

    def test_firebase_not_initialized_save_returns_false(self):
        """If Firebase not initialized, save returns False immediately."""
        from streamlit_app.services.firebase.settings_service import save_settings_to_firebase

        with patch("streamlit_app.services.firebase.settings_service.is_firebase_initialized", return_value=False):
            result = save_settings_to_firebase("uid1", {"google_api_key": "key"})
        assert result is False
