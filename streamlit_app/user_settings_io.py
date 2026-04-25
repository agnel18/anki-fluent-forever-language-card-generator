"""Shared loader/saver for user_settings.json.

Single canonical persistence for {favorites_order, per_language_settings}.
Replaces the duplicated helpers that previously lived in settings.py and the
ad-hoc reads in language_select.py and sentence_settings.py.
"""

import json
from pathlib import Path
from typing import Tuple

USER_SETTINGS_PATH = Path(__file__).parent / "user_settings.json"


def load_user_settings() -> Tuple[list, dict]:
    """Return (favorites_order, per_language_settings). Empty defaults if missing or unreadable."""
    if not USER_SETTINGS_PATH.exists():
        return [], {}
    try:
        with open(USER_SETTINGS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("favorites_order", []), data.get("per_language_settings", {})
    except Exception:
        return [], {}


def save_user_settings(favorites_order: list, per_language_settings: dict) -> bool:
    """Persist both fields atomically. Returns True on success."""
    data = {
        "favorites_order": favorites_order,
        "per_language_settings": per_language_settings,
    }
    try:
        USER_SETTINGS_PATH.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return True
    except Exception:
        return False


def settings_payload_json(favorites_order: list, per_language_settings: dict) -> str:
    """Build the canonical export payload as a JSON string (used by download buttons)."""
    return json.dumps(
        {
            "favorites_order": favorites_order,
            "per_language_settings": per_language_settings,
        },
        indent=2,
        ensure_ascii=False,
    )
