# utils.py - Utility functions for the language learning app

import os
import streamlit as st
from constants import USAGE_BAR_GREEN, USAGE_BAR_YELLOW, USAGE_BAR_RED


def log_message(message: str) -> None:
    """Log a message to the session state's log stream."""
    if 'log_stream' in st.session_state:
        st.session_state['log_stream'].write(message + '\n')
        st.session_state['log_stream'].flush()


def fmt_num(n: int) -> str:
    """Format a number for display (e.g., 1000 -> '1k', 1000000 -> '1M')."""
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M".rstrip('0').rstrip('.')
    elif n >= 1_000:
        return f"{n/1_000:.1f}k".rstrip('0').rstrip('.')
    elif n >= 10_000:
        return f"{n/1000:.1f}k"
    return str(n)


def usage_bar(val: int, limit: int) -> str:
    """Generate HTML for a usage progress bar."""
    pct = min(val / limit, 1.0)
    color = USAGE_BAR_GREEN if pct < 0.8 else (USAGE_BAR_YELLOW if pct < 0.9 else USAGE_BAR_RED)
    bar = f'''<div style="background:var(--card-bg);width:100%;height:12px;border-radius:6px;overflow:hidden;margin-bottom:6px;border:1px solid var(--card-border);">
        <div style="background:{color};width:{pct*100:.1f}%;height:100%;transition:width 0.3s;"></div></div>'''
    return bar


def get_secret(key: str, default: str = "") -> str:
    """Get a secret from Streamlit secrets or environment variables."""
    try:
        return st.secrets.get(key, os.getenv(key, default))
    except:
        return os.getenv(key, default)


def persist_api_keys() -> None:
    """Persist API keys to Firebase if user is logged in."""
    if not st.session_state.get("is_guest", True):
        from firebase_manager import save_settings_to_firebase
        save_settings_to_firebase(
            st.session_state.session_id,
            {
                "groq_api_key": st.session_state.get("groq_api_key", ""),
                "pixabay_api_key": st.session_state.get("pixabay_api_key", "")
            }
        )