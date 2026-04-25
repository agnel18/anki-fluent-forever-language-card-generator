"""Shared export/import for the 3 API keys (Gemini, TTS, Pixabay).

Keys live in st.session_state at runtime; this module bridges that with:
  - api_keys.json (user-controlled file the user keeps locally)
  - streamlit_app/.env (so subsequent sessions read keys via os.getenv)

api_keys.json schema:
{
    "version": 1,
    "google_api_key": "...",
    "google_tts_api_key": "...",
    "pixabay_api_key": ""
}

Empty strings for unset keys. Never log values.
"""

import json
from pathlib import Path
from typing import Dict, IO

ENV_PATH = Path(__file__).parent / ".env"

# Map session_state name -> .env variable name
SESSION_TO_ENV: Dict[str, str] = {
    "google_api_key": "GEMINI_API_KEY",
    "google_tts_api_key": "GOOGLE_TTS_API_KEY",
    "pixabay_api_key": "PIXABAY_API_KEY",
}

SCHEMA_VERSION = 1


def build_export_payload(session_state) -> Dict[str, object]:
    """Build the dict that becomes api_keys.json. Reads from session_state only."""
    payload: Dict[str, object] = {"version": SCHEMA_VERSION}
    for session_key in SESSION_TO_ENV:
        payload[session_key] = session_state.get(session_key, "") or ""
    return payload


def export_api_keys_json(session_state) -> str:
    """Return the JSON string for download. Indent for readability."""
    return json.dumps(build_export_payload(session_state), indent=2, ensure_ascii=False)


# Characters that would corrupt the .env line we're about to write.
# Newlines/CR break .env line-by-line parsing; '=' would split a value
# into a second variable. Reject these in imported keys.
_FORBIDDEN_KEY_CHARS = ("\n", "\r", "=", '"', "'", "\x00")


def _is_safe_key_value(value: str) -> bool:
    """Return True if value can be safely written as one .env line."""
    return not any(ch in value for ch in _FORBIDDEN_KEY_CHARS)


def parse_imported_file(file_obj: IO) -> Dict[str, str]:
    """Parse an uploaded api_keys.json. Returns {session_key: value} for non-empty keys.

    Raises ValueError on bad JSON, wrong shape, or values containing characters
    that would corrupt the .env file (newline injection / quote escape).
    """
    try:
        data = json.load(file_obj)
    except json.JSONDecodeError as e:
        raise ValueError(f"Not valid JSON: {e}") from e

    if not isinstance(data, dict):
        raise ValueError("Expected a JSON object at the top level")

    out: Dict[str, str] = {}
    for session_key in SESSION_TO_ENV:
        value = data.get(session_key, "")
        if not isinstance(value, str):
            continue
        stripped = value.strip()
        if not stripped:
            continue
        if not _is_safe_key_value(stripped):
            raise ValueError(
                f"{session_key} contains forbidden characters (newline, =, or quote). Refusing to import."
            )
        out[session_key] = stripped

    if not out:
        raise ValueError("No recognized API keys found in file")
    return out


def save_keys_to_env(keys: Dict[str, str]) -> int:
    """Persist the given session-keyed values to streamlit_app/.env. Returns count written.

    Reads existing .env, updates matching lines or appends new ones, writes back.
    Silently skips on I/O failure (Streamlit Cloud filesystem may be read-only).
    """
    if not keys:
        return 0
    try:
        existing = ENV_PATH.read_text() if ENV_PATH.exists() else ""
        lines = existing.split("\n") if existing else []

        for session_key, value in keys.items():
            env_var = SESSION_TO_ENV.get(session_key)
            if not env_var:
                continue
            updated = False
            for i, line in enumerate(lines):
                if line.startswith(f"{env_var}="):
                    lines[i] = f"{env_var}={value}"
                    updated = True
                    break
            if not updated:
                lines.append(f"{env_var}={value}")

        ENV_PATH.write_text("\n".join(lines))
        return len(keys)
    except Exception:
        return 0


def apply_imported_keys(session_state, keys: Dict[str, str]) -> int:
    """Populate session_state with imported keys AND persist to .env. Returns count."""
    for session_key, value in keys.items():
        session_state[session_key] = value
    save_keys_to_env(keys)
    return len(keys)
