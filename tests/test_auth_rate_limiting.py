"""
Tests for auth service rate limiting and input validation.

Covers:
- Rate limit enforcement (5 attempts / 5-min window)
- 10-minute lockout after exceeding limit
- Window pruning of old attempts
- Login vs registration independent counters
- Email/password validation
- Google Sign-In (verify_id_token) flow
"""

import time
import pytest
from unittest.mock import patch, MagicMock, PropertyMock


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
    """Mock streamlit across all auth service modules."""
    fake = FakeSessionState()
    with patch("streamlit_app.services.auth.session_manager.st") as mock_sm_st, \
         patch("streamlit_app.services.auth.auth_service.st") as mock_auth_st:
        mock_sm_st.session_state = fake
        mock_auth_st.session_state = fake
        mock_auth_st.secrets = MagicMock()
        yield fake


@pytest.fixture
def session_manager():
    from streamlit_app.services.auth.session_manager import SessionManager
    return SessionManager()


@pytest.fixture
def email_service():
    mock = MagicMock()
    mock.send_verification_email.return_value = True
    return mock


@pytest.fixture
def auth_service(email_service, session_manager):
    from streamlit_app.services.auth.auth_service import AuthService
    svc = AuthService(email_service=email_service, session_manager=session_manager)
    svc._firebase_initialized = True  # skip real Firebase init
    return svc


# ──────────────────────────────────────────────────────────
# Rate Limiting — _check_rate_limit / _record_attempt
# ──────────────────────────────────────────────────────────

class TestRateLimitBasics:
    """Test rate limiting mechanics in isolation."""

    def test_first_attempt_allowed(self, auth_service):
        allowed, msg = auth_service._check_rate_limit("login")
        assert allowed is True
        assert msg == ""

    def test_five_attempts_allowed(self, auth_service):
        """Exactly 5 attempts within window should all be allowed."""
        for _ in range(5):
            auth_service._record_attempt("login")
        # After 5 recorded, 6th check should be blocked
        allowed, msg = auth_service._check_rate_limit("login")
        assert allowed is False
        assert "Too many attempts" in msg

    def test_four_attempts_allowed_fifth_allowed(self, auth_service):
        """4 prior attempts — 5th check is still allowed."""
        for _ in range(4):
            auth_service._record_attempt("login")
        allowed, _ = auth_service._check_rate_limit("login")
        assert allowed is True

    def test_lockout_message_includes_wait_time(self, auth_service):
        """Lockout message tells user to wait N minutes."""
        for _ in range(5):
            auth_service._record_attempt("login")
        _, msg = auth_service._check_rate_limit("login")
        assert "minutes" in msg

    def test_old_attempts_pruned_outside_window(self, auth_service, mock_streamlit):
        """Attempts older than 5 min are pruned and don't count."""
        key = "_rate_limit_login"
        now = time.time()
        # Place 5 attempts at 6 minutes ago (outside 300s window)
        mock_streamlit[key] = [now - 360] * 5
        allowed, _ = auth_service._check_rate_limit("login")
        assert allowed is True
        # Old attempts should be pruned
        assert len(mock_streamlit[key]) == 0

    def test_lockout_expires_after_timeout(self, auth_service, mock_streamlit):
        """After lockout period, attempts are cleared and access restored."""
        key = "_rate_limit_login"
        now = time.time()
        # Simulate 5 attempts made 11 minutes ago (lockout = 10 min = 600s)
        mock_streamlit[key] = [now - 660] * 5
        allowed, _ = auth_service._check_rate_limit("login")
        assert allowed is True
        # State should be cleared
        assert len(mock_streamlit[key]) == 0

    def test_login_and_register_counters_independent(self, auth_service):
        """Login rate limit is independent from registration."""
        for _ in range(5):
            auth_service._record_attempt("login")
        # Login should be blocked
        allowed_login, _ = auth_service._check_rate_limit("login")
        assert allowed_login is False
        # Registration should still be allowed
        allowed_reg, _ = auth_service._check_rate_limit("register")
        assert allowed_reg is True

    def test_record_attempt_appends_timestamp(self, auth_service, mock_streamlit):
        """Each _record_attempt adds a timestamp."""
        auth_service._record_attempt("login")
        auth_service._record_attempt("login")
        key = "_rate_limit_login"
        assert len(mock_streamlit[key]) == 2
        assert all(isinstance(t, float) for t in mock_streamlit[key])

    def test_record_creates_key_if_missing(self, auth_service, mock_streamlit):
        """_record_attempt creates the session key if it doesn't exist."""
        assert "_rate_limit_test_action" not in mock_streamlit
        auth_service._record_attempt("test_action")
        assert "_rate_limit_test_action" in mock_streamlit
        assert len(mock_streamlit["_rate_limit_test_action"]) == 1


# ──────────────────────────────────────────────────────────
# Rate Limiting — wired into authenticate_user / register_user
# ──────────────────────────────────────────────────────────

class TestAuthenticateRateLimited:
    """Test that authenticate_user respects rate limits."""

    @patch("streamlit_app.services.auth.auth_service.auth")
    def test_login_blocked_after_5_attempts(self, mock_firebase_auth, auth_service):
        """authenticate_user returns rate-limit error on 6th attempt."""
        # Exhaust rate limit
        for _ in range(5):
            auth_service._record_attempt("login")

        success, msg, data = auth_service.authenticate_user("test@x.com", "pass")
        assert success is False
        assert "Too many attempts" in msg
        assert data is None
        # Firebase auth should NOT have been called
        mock_firebase_auth.get_user_by_email.assert_not_called()

    @patch("streamlit_app.services.auth.auth_service.auth")
    def test_login_records_attempt(self, mock_firebase_auth, auth_service, mock_streamlit):
        """Each login call records an attempt even on failure."""
        mock_firebase_auth.get_user_by_email.side_effect = Exception("fail")
        auth_service.authenticate_user("test@x.com", "pass")
        assert len(mock_streamlit.get("_rate_limit_login", [])) == 1


class TestRegisterRateLimited:
    """Test that register_user respects rate limits."""

    @patch("streamlit_app.services.auth.auth_service.auth")
    def test_register_blocked_after_5_attempts(self, mock_firebase_auth, auth_service):
        """register_user returns rate-limit error on 6th attempt."""
        for _ in range(5):
            auth_service._record_attempt("register")

        success, msg = auth_service.register_user("new@x.com", "Str0ngPass!")
        assert success is False
        assert "Too many attempts" in msg
        mock_firebase_auth.create_user.assert_not_called()

    @patch("streamlit_app.services.auth.auth_service.auth")
    def test_register_records_attempt(self, mock_firebase_auth, auth_service, mock_streamlit):
        """Each register call records an attempt even on failure."""
        mock_firebase_auth.create_user.side_effect = Exception("fail")
        auth_service.register_user("new@x.com", "Str0ngPass!")
        assert len(mock_streamlit.get("_rate_limit_register", [])) == 1


# ──────────────────────────────────────────────────────────
# Email / Password Validation
# ──────────────────────────────────────────────────────────

class TestEmailValidation:
    """Test email format validation."""

    def test_valid_email(self, auth_service):
        assert auth_service.validate_email("user@example.com") is True

    def test_valid_email_with_dots(self, auth_service):
        assert auth_service.validate_email("first.last@sub.example.co.uk") is True

    def test_invalid_no_at(self, auth_service):
        assert auth_service.validate_email("userexample.com") is False

    def test_invalid_no_domain(self, auth_service):
        assert auth_service.validate_email("user@") is False

    def test_invalid_empty(self, auth_service):
        assert auth_service.validate_email("") is False

    def test_invalid_spaces(self, auth_service):
        assert auth_service.validate_email("user @example.com") is False


class TestPasswordValidation:
    """Test password strength validation."""

    def test_valid_password(self, auth_service):
        valid, msg = auth_service.validate_password("Str0ngPass")
        assert valid is True

    def test_too_short(self, auth_service):
        valid, msg = auth_service.validate_password("Ab1")
        assert valid is False
        assert "8 characters" in msg

    def test_no_uppercase(self, auth_service):
        valid, msg = auth_service.validate_password("str0ngpass")
        assert valid is False
        assert "uppercase" in msg

    def test_no_lowercase(self, auth_service):
        valid, msg = auth_service.validate_password("STR0NGPASS")
        assert valid is False
        assert "lowercase" in msg

    def test_no_number(self, auth_service):
        valid, msg = auth_service.validate_password("StrongPass")
        assert valid is False
        assert "number" in msg


# ──────────────────────────────────────────────────────────
# Google Sign-In — verify_id_token
# ──────────────────────────────────────────────────────────

def _set_real_auth_exceptions(mock_firebase_auth):
    """Set real Firebase exception classes on a mocked auth module."""
    from firebase_admin.auth import ExpiredIdTokenError, RevokedIdTokenError, InvalidIdTokenError
    mock_firebase_auth.ExpiredIdTokenError = ExpiredIdTokenError
    mock_firebase_auth.RevokedIdTokenError = RevokedIdTokenError
    mock_firebase_auth.InvalidIdTokenError = InvalidIdTokenError


class TestVerifyIdToken:
    """Test the server-side Google Sign-In verification flow."""

    @patch("streamlit_app.services.auth.auth_service.auth")
    def test_valid_token_creates_session(self, mock_firebase_auth, auth_service, mock_streamlit):
        """Valid ID token → session established, user data returned."""
        _set_real_auth_exceptions(mock_firebase_auth)
        mock_firebase_auth.verify_id_token.return_value = {
            "uid": "google_uid_123",
            "email": "user@gmail.com",
            "name": "Test User",
            "email_verified": True,
        }
        # Mock Firestore profile check
        auth_service._db = MagicMock()
        mock_doc = MagicMock()
        mock_doc.exists = False  # No existing profile → will create
        auth_service._db.collection.return_value.document.return_value.get.return_value = mock_doc

        success, msg, user_data = auth_service.verify_id_token("valid_token_abc")

        assert success is True
        assert "Welcome" in msg
        assert user_data["uid"] == "google_uid_123"
        assert user_data["email"] == "user@gmail.com"
        assert user_data["emailVerified"] is True
        # Session should be set
        assert mock_streamlit.get("user") is not None
        assert mock_streamlit["user"]["uid"] == "google_uid_123"

    @patch("streamlit_app.services.auth.auth_service.auth")
    def test_unverified_email_rejected(self, mock_firebase_auth, auth_service):
        """Token with unverified email is rejected."""
        _set_real_auth_exceptions(mock_firebase_auth)
        mock_firebase_auth.verify_id_token.return_value = {
            "uid": "uid_456",
            "email": "unverified@gmail.com",
            "email_verified": False,
        }

        success, msg, data = auth_service.verify_id_token("token_unverified")
        assert success is False
        assert "verify" in msg.lower()
        assert data is None

    @patch("streamlit_app.services.auth.auth_service.auth")
    def test_expired_token(self, mock_firebase_auth, auth_service):
        """Expired ID token returns appropriate error."""
        from firebase_admin.auth import ExpiredIdTokenError
        _set_real_auth_exceptions(mock_firebase_auth)
        mock_firebase_auth.verify_id_token.side_effect = ExpiredIdTokenError("expired", cause=None)

        success, msg, data = auth_service.verify_id_token("expired_token")
        assert success is False
        assert "expired" in msg.lower()
        assert data is None

    @patch("streamlit_app.services.auth.auth_service.auth")
    def test_revoked_token(self, mock_firebase_auth, auth_service):
        """Revoked ID token returns appropriate error."""
        from firebase_admin.auth import RevokedIdTokenError
        _set_real_auth_exceptions(mock_firebase_auth)
        mock_firebase_auth.verify_id_token.side_effect = RevokedIdTokenError("revoked")

        success, msg, data = auth_service.verify_id_token("revoked_token")
        assert success is False
        assert "revoked" in msg.lower()
        assert data is None

    @patch("streamlit_app.services.auth.auth_service.auth")
    def test_invalid_token(self, mock_firebase_auth, auth_service):
        """Completely invalid token returns appropriate error."""
        from firebase_admin.auth import InvalidIdTokenError
        _set_real_auth_exceptions(mock_firebase_auth)
        mock_firebase_auth.verify_id_token.side_effect = InvalidIdTokenError("bad token")

        success, msg, data = auth_service.verify_id_token("garbage")
        assert success is False
        assert "invalid" in msg.lower() or "Invalid" in msg
        assert data is None

    @patch("streamlit_app.services.auth.auth_service.auth")
    def test_token_with_no_email_uses_fallback_name(self, mock_firebase_auth, auth_service):
        """Token missing 'name' falls back to email prefix."""
        _set_real_auth_exceptions(mock_firebase_auth)
        mock_firebase_auth.verify_id_token.return_value = {
            "uid": "uid_no_name",
            "email": "fallback@test.com",
            "email_verified": True,
        }
        auth_service._db = MagicMock()
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {"email": "fallback@test.com"}
        auth_service._db.collection.return_value.document.return_value.get.return_value = mock_doc

        success, msg, user_data = auth_service.verify_id_token("token_no_name")
        assert success is True
        assert user_data["displayName"] == "fallback"

    @patch("streamlit_app.services.auth.auth_service.auth")
    def test_existing_profile_not_recreated(self, mock_firebase_auth, auth_service):
        """If Firestore profile already exists, don't overwrite it."""
        _set_real_auth_exceptions(mock_firebase_auth)
        mock_firebase_auth.verify_id_token.return_value = {
            "uid": "existing_uid",
            "email": "exists@test.com",
            "name": "Existing",
            "email_verified": True,
        }
        auth_service._db = MagicMock()
        mock_doc = MagicMock()
        mock_doc.exists = True  # Profile exists
        mock_doc.to_dict.return_value = {"email": "exists@test.com"}
        auth_service._db.collection.return_value.document.return_value.get.return_value = mock_doc

        auth_service.verify_id_token("token_existing")

        # set() should NOT be called (profile already exists)
        auth_service._db.collection.return_value.document.return_value.set.assert_not_called()
