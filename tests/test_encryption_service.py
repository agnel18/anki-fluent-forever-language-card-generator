"""
Tests for the encryption service.

Covers:
- Encrypt/decrypt roundtrip
- Per-user key isolation (different UIDs produce different ciphertext)
- Wrong UID cannot decrypt
- Empty/None handling
- Missing master secret raises ValueError
- Corrupted ciphertext raises InvalidToken
- encrypt_api_keys / decrypt_api_keys dict helpers
- Legacy plaintext passthrough in decrypt_api_keys
"""

import os
import pytest
from unittest.mock import patch

# Set a test master secret BEFORE importing the module
TEST_MASTER_SECRET = "test-master-secret-32-bytes-long!"
os.environ["MASTER_ENCRYPTION_KEY"] = TEST_MASTER_SECRET

from streamlit_app.services.security.encryption_service import (
    encrypt_value,
    decrypt_value,
    encrypt_api_keys,
    decrypt_api_keys,
    is_encryption_available,
    API_KEY_FIELDS,
)


class TestEncryptDecryptRoundtrip:
    """Basic encrypt → decrypt should return the original plaintext."""

    def test_roundtrip_short_string(self):
        uid = "user123"
        plaintext = "AIzaSyD_short_key"
        ciphertext = encrypt_value(uid, plaintext)
        assert ciphertext != plaintext
        assert decrypt_value(uid, ciphertext) == plaintext

    def test_roundtrip_long_api_key(self):
        uid = "MfRC8KEOLXQ0OGFxmE2tDVsBtsk1"
        plaintext = "AIzaSyD-abcdefghijklmnopqrstuvwxyz12345"
        ciphertext = encrypt_value(uid, plaintext)
        assert decrypt_value(uid, ciphertext) == plaintext

    def test_roundtrip_unicode(self):
        uid = "user456"
        plaintext = "key-with-üñíçödé-chars"
        ciphertext = encrypt_value(uid, plaintext)
        assert decrypt_value(uid, ciphertext) == plaintext

    def test_ciphertext_is_base64_string(self):
        uid = "user789"
        plaintext = "AIzaSyD_test_key_value"
        ciphertext = encrypt_value(uid, plaintext)
        # Fernet tokens are URL-safe base64
        assert isinstance(ciphertext, str)
        assert len(ciphertext) > len(plaintext)


class TestPerUserIsolation:
    """Different UIDs must produce different ciphertext for the same plaintext."""

    def test_different_uids_different_ciphertext(self):
        plaintext = "AIzaSyD_same_key_for_both"
        ct_alice = encrypt_value("alice-uid", plaintext)
        ct_bob = encrypt_value("bob-uid", plaintext)
        assert ct_alice != ct_bob

    def test_wrong_uid_cannot_decrypt(self):
        plaintext = "AIzaSyD_secret_key"
        ciphertext = encrypt_value("alice-uid", plaintext)
        with pytest.raises(Exception):
            # Fernet raises InvalidToken
            decrypt_value("bob-uid", ciphertext)

    def test_same_uid_can_decrypt(self):
        plaintext = "AIzaSyD_secret_key"
        ciphertext = encrypt_value("alice-uid", plaintext)
        assert decrypt_value("alice-uid", ciphertext) == plaintext


class TestEdgeCases:
    """Empty strings, None values, missing secrets."""

    def test_empty_string_encrypt(self):
        result = encrypt_value("user123", "")
        assert result == ""

    def test_empty_string_decrypt(self):
        result = decrypt_value("user123", "")
        assert result == ""

    def test_empty_uid_raises(self):
        with pytest.raises(ValueError, match="user_uid is required"):
            encrypt_value("", "some-key")

    def test_empty_uid_decrypt_raises(self):
        with pytest.raises(ValueError, match="user_uid is required"):
            decrypt_value("", "some-ciphertext")

    def test_missing_master_secret_raises(self):
        with patch.dict(os.environ, {}, clear=True):
            # Also patch streamlit secrets to return None
            with patch("streamlit_app.services.security.encryption_service._get_master_secret", return_value=None):
                with pytest.raises(ValueError, match="MASTER_ENCRYPTION_KEY not configured"):
                    encrypt_value("user123", "some-key")

    def test_corrupted_ciphertext_raises(self):
        with pytest.raises(Exception):
            decrypt_value("user123", "not-valid-fernet-token")


class TestDictHelpers:
    """encrypt_api_keys and decrypt_api_keys work on settings dicts."""

    SAMPLE_SETTINGS = {
        "google_api_key": "AIzaSyD_gemini_key_here",
        "google_tts_api_key": "AIzaSyD_tts_key_here",
        "pixabay_api_key": "12345678-abcdef",
        "theme": "dark",
        "audio_speed": 1.0,
    }

    def test_encrypt_api_keys_adds_flag(self):
        result = encrypt_api_keys("uid1", self.SAMPLE_SETTINGS)
        assert result["encrypted"] is True

    def test_encrypt_api_keys_changes_key_fields(self):
        result = encrypt_api_keys("uid1", self.SAMPLE_SETTINGS)
        for field in API_KEY_FIELDS:
            # Encrypted values should differ from plaintext
            assert result[field] != self.SAMPLE_SETTINGS[field]

    def test_encrypt_api_keys_preserves_non_key_fields(self):
        result = encrypt_api_keys("uid1", self.SAMPLE_SETTINGS)
        assert result["theme"] == "dark"
        assert result["audio_speed"] == 1.0

    def test_full_roundtrip_dict(self):
        uid = "uid_roundtrip"
        encrypted = encrypt_api_keys(uid, self.SAMPLE_SETTINGS)
        decrypted = decrypt_api_keys(uid, encrypted)
        for field in API_KEY_FIELDS:
            assert decrypted[field] == self.SAMPLE_SETTINGS[field]
        assert decrypted["theme"] == "dark"
        assert decrypted["audio_speed"] == 1.0
        assert "encrypted" not in decrypted

    def test_decrypt_legacy_plaintext_passthrough(self):
        """Settings without 'encrypted' flag should pass through unchanged."""
        legacy = {
            "google_api_key": "AIzaSyD_plaintext",
            "theme": "light",
        }
        result = decrypt_api_keys("uid1", legacy)
        assert result["google_api_key"] == "AIzaSyD_plaintext"
        assert result["theme"] == "light"

    def test_decrypt_empty_key_values(self):
        encrypted = encrypt_api_keys("uid1", {
            "google_api_key": "AIzaSyD_test",
            "google_tts_api_key": "",
            "pixabay_api_key": "",
            "theme": "dark",
        })
        decrypted = decrypt_api_keys("uid1", encrypted)
        assert decrypted["google_api_key"] == "AIzaSyD_test"
        assert decrypted["google_tts_api_key"] == ""
        assert decrypted["pixabay_api_key"] == ""


class TestIsEncryptionAvailable:
    """is_encryption_available reflects master secret presence."""

    def test_available_with_env_var(self):
        assert is_encryption_available() is True

    def test_not_available_without_secret(self):
        with patch("streamlit_app.services.security.encryption_service._get_master_secret", return_value=None):
            assert is_encryption_available() is False
