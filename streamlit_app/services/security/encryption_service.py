"""
Encryption Service for API Key Protection

Uses Fernet symmetric encryption (AES-128-CBC + HMAC-SHA256) with per-user
derived keys. Each user's Firebase UID is combined with a master secret via
PBKDF2 to produce a unique encryption key, so compromising one user's data
does not expose others.

Master secret is stored in Streamlit secrets (encrypted at rest on Community Cloud).
If the master secret is lost, users must re-enter their API keys.
"""

import base64
import logging
import os
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Lazy-loaded to avoid import errors when cryptography isn't installed
_Fernet = None
_PBKDF2HMAC = None
_hashes = None

API_KEY_FIELDS = frozenset({
    "google_api_key",
    "google_tts_api_key",
    "pixabay_api_key",
})

# PBKDF2 iterations — OWASP 2024 recommendation for SHA-256
_PBKDF2_ITERATIONS = 600_000


def _load_crypto():
    """Lazy-load cryptography library."""
    global _Fernet, _PBKDF2HMAC, _hashes
    if _Fernet is None:
        try:
            from cryptography.fernet import Fernet
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            from cryptography.hazmat.primitives import hashes
            _Fernet = Fernet
            _PBKDF2HMAC = PBKDF2HMAC
            _hashes = hashes
        except ImportError:
            logger.error("cryptography library not installed — pip install cryptography")
            raise


def _get_master_secret() -> Optional[str]:
    """
    Retrieve the master encryption key from Streamlit secrets or environment.

    Returns:
        Master secret string, or None if not configured.
    """
    # 1. Streamlit secrets (production — Community Cloud)
    try:
        import streamlit as st
        secret = st.secrets.get("MASTER_ENCRYPTION_KEY")
        if secret:
            return str(secret)
    except Exception:
        pass

    # 2. Environment variable (local dev, CI)
    secret = os.environ.get("MASTER_ENCRYPTION_KEY")
    if secret:
        return secret

    return None


def _derive_user_key(user_uid: str, master_secret: str) -> bytes:
    """
    Derive a per-user Fernet key from the master secret + user UID.

    Uses PBKDF2-HMAC-SHA256 with 600 000 iterations.
    The user UID serves as the salt, ensuring each user gets a unique key.

    Args:
        user_uid: Firebase UID (used as salt).
        master_secret: Application-wide master secret.

    Returns:
        32-byte URL-safe base64-encoded Fernet key.
    """
    _load_crypto()
    kdf = _PBKDF2HMAC(
        algorithm=_hashes.SHA256(),
        length=32,
        salt=user_uid.encode("utf-8"),
        iterations=_PBKDF2_ITERATIONS,
    )
    raw_key = kdf.derive(master_secret.encode("utf-8"))
    return base64.urlsafe_b64encode(raw_key)


def is_encryption_available() -> bool:
    """Check whether encryption can be performed (master secret configured)."""
    return _get_master_secret() is not None


def encrypt_value(user_uid: str, plaintext: str) -> str:
    """
    Encrypt a single string value for a specific user.

    Args:
        user_uid: Firebase UID of the user.
        plaintext: The value to encrypt.

    Returns:
        Base64-encoded ciphertext string (safe for Firestore storage).

    Raises:
        ValueError: If master secret is not configured or user_uid is empty.
    """
    if not user_uid:
        raise ValueError("user_uid is required for encryption")
    if not plaintext:
        return ""

    master = _get_master_secret()
    if not master:
        raise ValueError(
            "MASTER_ENCRYPTION_KEY not configured — "
            "add it to .streamlit/secrets.toml or environment"
        )

    _load_crypto()
    key = _derive_user_key(user_uid, master)
    f = _Fernet(key)
    token = f.encrypt(plaintext.encode("utf-8"))
    return token.decode("utf-8")


def decrypt_value(user_uid: str, ciphertext: str) -> str:
    """
    Decrypt a single string value for a specific user.

    Args:
        user_uid: Firebase UID of the user.
        ciphertext: Base64-encoded ciphertext from Firestore.

    Returns:
        Decrypted plaintext string.

    Raises:
        ValueError: If master secret is not configured or user_uid is empty.
        cryptography.fernet.InvalidToken: If ciphertext is corrupted or
            was encrypted with a different key.
    """
    if not user_uid:
        raise ValueError("user_uid is required for decryption")
    if not ciphertext:
        return ""

    master = _get_master_secret()
    if not master:
        raise ValueError(
            "MASTER_ENCRYPTION_KEY not configured — "
            "add it to .streamlit/secrets.toml or environment"
        )

    _load_crypto()
    key = _derive_user_key(user_uid, master)
    f = _Fernet(key)
    plaintext = f.decrypt(ciphertext.encode("utf-8"))
    return plaintext.decode("utf-8")


def encrypt_api_keys(user_uid: str, settings: Dict) -> Dict:
    """
    Encrypt all API key fields in a settings dictionary.

    Non-key fields are passed through unchanged. An ``"encrypted": True``
    flag is added so readers know decryption is required.

    Args:
        user_uid: Firebase UID.
        settings: Settings dict (may contain plaintext API keys).

    Returns:
        New dict with API key values replaced by ciphertext.
    """
    result = {}
    for key, value in settings.items():
        if key in API_KEY_FIELDS and value:
            result[key] = encrypt_value(user_uid, str(value))
        else:
            result[key] = value
    result["encrypted"] = True
    return result


def decrypt_api_keys(user_uid: str, settings: Dict) -> Dict:
    """
    Decrypt all API key fields in a settings dictionary.

    If the ``"encrypted"`` flag is missing or False, the dict is returned
    unchanged (legacy plaintext data — caller should re-encrypt and save).

    Args:
        user_uid: Firebase UID.
        settings: Settings dict from Firestore (may contain ciphertext).

    Returns:
        New dict with API key values decrypted to plaintext.
    """
    if not settings.get("encrypted"):
        # Legacy plaintext — return as-is; caller should migrate
        logger.warning("Unencrypted settings detected for user %s — migration needed", user_uid)
        return dict(settings)

    result = {}
    for key, value in settings.items():
        if key == "encrypted":
            continue
        if key in API_KEY_FIELDS and value:
            try:
                result[key] = decrypt_value(user_uid, str(value))
            except Exception:
                logger.error("Failed to decrypt %s for user %s", key, user_uid)
                result[key] = ""
        else:
            result[key] = value
    return result
