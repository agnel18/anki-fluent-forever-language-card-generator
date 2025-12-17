# pages/statistics.py - Statistics page for the language learning app

import streamlit as st
from constants import (
    GROQ_CALL_LIMIT, GROQ_TOKEN_LIMIT, PIXABAY_CALL_LIMIT,
    PAGE_LANGUAGE_SELECT, PAGE_LOGIN
)
from utils import fmt_num, usage_bar


def render_statistics_page():
    """Render the usage statistics and progress tracking page."""
    st.title("📊 Usage Statistics & Progress Tracking")

    # Back button
    if st.button("← Back to Main", key="back_to_main_stats"):
        st.session_state.page = "main"
        st.session_state.scroll_to_top = True
        st.rerun()

    st.markdown("---")

    # Use persistent stats if logged in, else session stats
    stats = st.session_state.get("persistent_usage_stats") if not st.session_state.get("is_guest", True) else None
    if stats:
        groq_calls = stats.get("groq_calls", 0)
        groq_tokens = stats.get("groq_tokens", 0)
        pixabay_calls = stats.get("pixabay_calls", 0)
        decks_exported = stats.get("decks_exported", 0)
        cards_generated = stats.get("cards_generated", 0)
        images_downloaded = stats.get("images_downloaded", 0)
        audio_generated = stats.get("audio_generated", 0)
        api_errors = stats.get("api_errors", 0)
        per_language = stats.get("per_language", {})
    else:
        groq_calls = st.session_state.get("groq_api_calls", 0)
        groq_tokens = st.session_state.get("groq_tokens_used", 0)
        pixabay_calls = st.session_state.get("pixabay_api_calls", 0)
        decks_exported = st.session_state.get("decks_exported", 0)
        cards_generated = st.session_state.get("cards_generated", 0)
        images_downloaded = st.session_state.get("images_downloaded", 0)
        audio_generated = st.session_state.get("audio_generated", 0)
        api_errors = st.session_state.get("api_errors", 0)
        per_language = {}

    st.markdown("#### API Usage")
    st.markdown(f"Groq Calls: {fmt_num(groq_calls)} / {fmt_num(GROQ_CALL_LIMIT)}", unsafe_allow_html=True)
    st.markdown(usage_bar(groq_calls, GROQ_CALL_LIMIT), unsafe_allow_html=True)
    st.markdown(f"Groq Tokens: {fmt_num(groq_tokens)} / {fmt_num(GROQ_TOKEN_LIMIT)}", unsafe_allow_html=True)
    st.markdown(usage_bar(groq_tokens, GROQ_TOKEN_LIMIT), unsafe_allow_html=True)
    st.markdown(f"Pixabay Calls: {fmt_num(pixabay_calls)} / {fmt_num(PIXABAY_CALL_LIMIT)}", unsafe_allow_html=True)
    st.markdown(usage_bar(pixabay_calls, PIXABAY_CALL_LIMIT), unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("#### Generation & Export Stats")
    st.metric("Decks Exported", decks_exported)
    st.metric("Cards Generated", cards_generated)
    st.metric("Images Downloaded", images_downloaded)
    st.metric("Audio Generated", audio_generated)
    st.metric("API Errors", api_errors)
    st.markdown("---")

    if per_language:
        st.markdown("#### Per-Language Usage")
        for lang, lang_stats in per_language.items():
            st.markdown(f"**{lang}**")
            st.write({k: v for k, v in lang_stats.items() if isinstance(v, int)})

    st.markdown("---")
    st.caption("Counts update live as you generate decks. Persistent stats for logged-in users, session stats for guests.")

    if st.button("⬅️ Back", key="stats_back_btn"):
        st.session_state.page = PAGE_LANGUAGE_SELECT if st.session_state.get("first_run_complete", False) else PAGE_LOGIN
        st.session_state.scroll_to_top = True
        st.rerun()