# pages/help.py - Help and FAQ page for the language learning app

import streamlit as st


def render_help_page():
    """Render the help and FAQ page."""

    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("# ℹ️ Help & FAQ")
    with col2:
        if st.button("← Back"):
            st.session_state.page = "main"
            st.session_state.scroll_to_top = True
            st.rerun()

    st.markdown("""
    ## What does this app do?

    - Creates custom Anki decks for language learning:
        - Select words from frequency lists
        - Generate natural sentences (Groq AI)
        - Create native audio at 0.8x speed (learner-friendly)
        - Download relevant images (Pixabay)
        - Export ready-to-import Anki files

    ## Cost?
    - 100% FREE for personal use
        - Groq: Free tier (AI sentences)
        - Pixabay: Free tier (5,000 images/day)

    ## How long does it take?
    - 5 words: 5–10 min
    - 10 words: 10–15 min
    - 20 words: 20–30 min

    ## Privacy
    - Your data and API keys stay on your device
    - Nothing is stored or sent to external servers

    ## Troubleshooting
    - Double-check API keys
    - Ensure internet connection
    - Start with 3–5 words to test
    - Refresh the page and try again if errors occur
    """)
    # End of Help & FAQ section