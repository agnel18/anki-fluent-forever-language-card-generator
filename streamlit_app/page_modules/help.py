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
            st.rerun()

    st.markdown("""
    ## What does this app do?

    - Creates custom Anki decks for language learning:
        - Select words from frequency lists
        - Generate natural sentences (Google Gemini AI)
        - Create native audio at 0.8x speed (learner-friendly)
        - Download relevant images (Pixabay)
        - Export ready-to-import Anki files

    ## Cost?
    - 100% FREE for personal use
        - Google Gemini AI: Free tier (AI sentences)
        - Pixabay: Free (up to 5000 images/month)

    ## How long does it take?
    - 5 words: 5–10 min
    - 10 words: 10–15 min
    - 20 words: 20–30 min

    ## Privacy
    - Your data and API keys stay on your device
    - Nothing is stored or sent to external servers

    ## Why do I need two Google Cloud projects?

    Enabling billing on a GCP project upgrades **ALL** its APIs to the paid tier — including
    Gemini. This means you lose the **1,500 free Gemini requests/day**. Since TTS requires
    billing to activate (even though **TTS itself is FREE within 1M characters/month**),
    we use two separate projects so both services stay free:

    - **Project A ("Language Cards - Gemini"):** Gemini only, NO billing → free 1,500 requests/day
    - **Project B ("Language Cards - TTS"):** TTS only, billing enabled → free 1M characters/month

    Enter both keys on the **API Setup** page — one in the Gemini section, one in the TTS section.

    **To set a daily spend limit on TTS:**
    1. Open [Google Cloud Console](https://console.cloud.google.com/) → select your TTS project
    2. Go to **APIs & Services** → **Cloud Text-to-Speech API** → **Quotas & System Limits**
    3. Find **"Characters synthesized per day"** → click ✏️ → set e.g. **50,000**

    > 💰 TTS is **FREE**: 1 million characters/month (Standard voices) — that's ~600+ flashcard decks!

    ## Troubleshooting
    - Double-check API keys
    - Ensure internet connection
    - Start with 3–5 words to test
    - Refresh the page and try again if errors occur
    - If you see a quota error, wait until midnight UTC for your daily limit to reset,
      or raise your quota ceiling in Google Cloud Console.
    """)
    # End of Help & FAQ section