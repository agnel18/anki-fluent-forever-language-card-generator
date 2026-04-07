import streamlit as st

# Session state guard for Streamlit bug workaround
if not hasattr(st, "session_state") or st.session_state is None:
    st.session_state = {}
import os
from constants import GEMINI_CALL_LIMIT, GEMINI_TOKEN_LIMIT, GOOGLE_SEARCH_CALL_LIMIT

def render_sidebar():
    """Render the main sidebar content."""
    
    # Center the logo vertically in the sidebar using HTML/CSS
    # Center the sidebar logo horizontally using HTML
    logo_path = os.path.join(os.path.dirname(__file__), "..", "logo.svg")
    if os.path.exists(logo_path):
        st.sidebar.image(logo_path, width="stretch")
    st.sidebar.markdown("---")

    # Create sidebar content with better mobile alignment
    st.sidebar.markdown("## ⚙️ Quick Access")

    # Quick access buttons stacked vertically
    if st.sidebar.button("🏠 Main", key="sidebar_main", use_container_width=True):
        st.session_state.page = "main"
        st.rerun()

    if st.sidebar.button("⚙️ Settings", key="sidebar_settings", use_container_width=True):
        st.session_state.page = "settings"
        st.rerun()

    # Documentation button
    if st.sidebar.button("📖 Documentation", key="sidebar_docs", use_container_width=True):
        import webbrowser
        webbrowser.open("https://github.com/agnel18/anki-fluent-forever-language-card-generator")
        st.sidebar.success("Opening documentation...")

    st.sidebar.markdown("---")

    # TTS Status Indicator
    try:
        from audio_generator import is_google_tts_configured
        if is_google_tts_configured():
            st.sidebar.caption("🔊 Google TTS Active")
        else:
            st.sidebar.caption("🔊 TTS Not Configured")
    except ImportError:
        st.sidebar.caption("🔊 TTS Unavailable")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### API Usage")

    gemini_calls = st.session_state.get("gemini_api_calls", 0)
    gemini_tokens = st.session_state.get("gemini_tokens_used", 0)
    google_search_calls = st.session_state.get("google_search_api_calls", 0)

    def format_number_compact(num):
        if num >= 1000000:
            return f"{num // 1000000}M"
        elif num >= 1000:
            return f"{num // 1000}K"
        else:
            return str(num)

    # Display metrics with compact formatting
    st.sidebar.metric(
        "Gemini Calls",
        f"{format_number_compact(gemini_calls)} / {format_number_compact(GEMINI_CALL_LIMIT)}"
    )
    st.sidebar.metric(
        "Gemini Tokens",
        f"{format_number_compact(gemini_tokens)} / {format_number_compact(GEMINI_TOKEN_LIMIT)}"
    )
    st.sidebar.metric(
        "Google Search Calls",
        f"{format_number_compact(google_search_calls)} / {format_number_compact(GOOGLE_SEARCH_CALL_LIMIT)}"
    )

    st.sidebar.caption("Limits are approximate—check your API dashboard for exact quotas.")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎨 Theme")

    theme_options = ["Light", "Dark"]
    current_theme = st.session_state.get("theme", "dark").capitalize()

    selected_theme = st.sidebar.selectbox(
        "Select Theme",
        theme_options,
        index=theme_options.index(current_theme),
        key="theme_select_sidebar",
        help="Switch between light and dark themes"
    )

    theme_changed = False
    if selected_theme.lower() != st.session_state.get("theme", "dark"):
        st.session_state.theme = selected_theme.lower()
        theme_changed = True
        st.sidebar.success(f"Theme changed to {selected_theme}!")

    # Continue with sidebar content (outside the theme selection block)
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💸 Pay Fees of Any Amount")
    st.sidebar.markdown("Help keep this language learning app running!")

    payment_url = "https://razorpay.me/@agneljosephn"
    st.sidebar.markdown(f'<a href="{payment_url}" target="_blank" style="text-decoration: none;"><button style="background-color: #FF6B35; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-size: 14px; font-weight: bold; width: 100%; margin-bottom: 8px;">Pay Fees</button></a>', unsafe_allow_html=True)

    # Legal & Policy Links
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📄 Legal")

    # Legal links in a compact format
    if st.sidebar.button("🔒 Privacy Policy", key="sidebar_privacy", use_container_width=True):
        st.session_state.page = "privacy_policy"
        st.rerun()

    if st.sidebar.button("📋 Terms & Conditions", key="sidebar_terms", use_container_width=True):
        st.session_state.page = "terms_conditions"
        st.rerun()

    if st.sidebar.button("💰 Refund Policy", key="sidebar_refund", use_container_width=True):
        st.session_state.page = "refund_policy"
        st.rerun()

    if st.sidebar.button("📞 Contact Us", key="sidebar_contact", use_container_width=True):
        st.session_state.page = "contact_us"
        st.rerun()

    # Show generation status if in progress
    if st.session_state.get('page') == 'generating':
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🔄 Generation Status")
        progress = st.session_state.get('generation_progress', {})
        word_idx = progress.get('word_idx', 0)
        total_words = len(st.session_state.get('selected_words', []))
        if total_words > 0:
            st.sidebar.progress(min((word_idx + 1) / total_words, 1.0))
            st.sidebar.caption(f"Processing word {word_idx + 1} of {total_words}")

    return theme_changed