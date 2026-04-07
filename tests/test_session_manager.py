"""
Tests for session manager — session timeout and sensitive data clearing.
"""

import time
import pytest
from unittest.mock import patch, MagicMock


class FakeSessionState(dict):
    """dict subclass that also supports attribute access (like st.session_state)."""
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
def mock_session_state():
    """Provide a fresh mock session state for each test."""
    fake = FakeSessionState()
    with patch("streamlit_app.services.auth.session_manager.st") as mock_st:
        mock_st.session_state = fake
        yield fake


@pytest.fixture
def manager():
    from streamlit_app.services.auth.session_manager import SessionManager
    return SessionManager()


class TestSessionTimeout:
    """Test session timeout after 30 minutes of inactivity."""

    def test_signed_in_no_timeout(self, manager, mock_session_state):
        """User signed in recently — session is valid."""
        mock_session_state["user"] = {"uid": "u1", "email": "a@b.com"}
        mock_session_state["last_activity"] = time.time()
        assert manager.is_signed_in() is True

    def test_signed_in_expired(self, manager, mock_session_state):
        """User idle for > 30 min — session expires automatically."""
        mock_session_state["user"] = {"uid": "u1", "email": "a@b.com"}
        mock_session_state["last_activity"] = time.time() - 31 * 60  # 31 min ago
        assert manager.is_signed_in() is False
        # After expiry, user should be cleared
        assert mock_session_state.get("user") is None

    def test_not_signed_in(self, manager, mock_session_state):
        """No user set — not signed in."""
        assert manager.is_signed_in() is False

    def test_activity_touch_updates_timestamp(self, manager, mock_session_state):
        """Calling is_signed_in refreshes the activity timestamp."""
        mock_session_state["user"] = {"uid": "u1"}
        mock_session_state["last_activity"] = time.time() - 10 * 60  # 10 min ago
        assert manager.is_signed_in() is True
        # Timestamp should be refreshed to ~now
        assert time.time() - mock_session_state["last_activity"] < 2


class TestSignOutClearsKeys:
    """Test that sign_out clears decrypted API keys."""

    def test_sign_out_clears_api_keys(self, manager, mock_session_state):
        """API keys are removed from session on sign-out."""
        mock_session_state["user"] = {"uid": "u1"}
        mock_session_state["google_api_key"] = "AIza..."
        mock_session_state["google_tts_api_key"] = "AIza2..."
        mock_session_state["pixabay_api_key"] = "px123"
        mock_session_state["last_activity"] = time.time()

        manager.sign_out()

        assert "google_api_key" not in mock_session_state
        assert "google_tts_api_key" not in mock_session_state
        assert "pixabay_api_key" not in mock_session_state
        assert mock_session_state.get("user") is None
        assert mock_session_state.get("is_guest") is True

    def test_sign_out_no_keys_no_error(self, manager, mock_session_state):
        """Sign-out works even if no API keys were in session."""
        mock_session_state["user"] = {"uid": "u1"}
        manager.sign_out()
        assert mock_session_state.get("user") is None

    def test_timeout_clears_api_keys(self, manager, mock_session_state):
        """When session expires, API keys are also cleared."""
        mock_session_state["user"] = {"uid": "u1"}
        mock_session_state["google_api_key"] = "AIza..."
        mock_session_state["pixabay_api_key"] = "px123"
        mock_session_state["last_activity"] = time.time() - 31 * 60

        # This should trigger auto-expire
        assert manager.is_signed_in() is False
        assert "google_api_key" not in mock_session_state
        assert "pixabay_api_key" not in mock_session_state


class TestSetUser:
    """Test that set_user initializes activity tracking."""

    def test_set_user_touches_activity(self, manager, mock_session_state):
        """Setting user starts the activity timer."""
        manager.set_user({"uid": "u1", "email": "a@b.com"})
        assert "last_activity" in mock_session_state
        assert time.time() - mock_session_state["last_activity"] < 2
        assert mock_session_state.get("is_guest") is False
