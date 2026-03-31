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
    billing, we use two separate projects to keep Gemini free:

    - **Project A ("Language Cards - Gemini"):** Gemini only, NO billing → free tier preserved
    - **Project B ("Language Cards - TTS"):** TTS only, billing enabled → pay only for audio

    Set the `GOOGLE_TTS_API_KEY` environment variable (in your `.env` file) to Project B's key.
    The main API key entered in the app should be Project A's key.

    **To set a spend limit on TTS:**
    1. Open [Google Cloud Console](https://console.cloud.google.com/) → select your TTS project
    2. Go to **APIs & Services** → **Cloud Text-to-Speech API** → **Quotas & System Limits**
    3. Find **"Characters synthesized per day"** → click ✏️ → set e.g. **50,000**

    > 💰 TTS first 1M characters/month are FREE (Standard voices). Full setup guide is in the **API Setup** page.

    Full step-by-step guide is in the **API Setup** page under "Step 2".

    ## Troubleshooting
    - Double-check API keys
    - Ensure internet connection
    - Start with 3–5 words to test
    - Refresh the page and try again if errors occur
    - If you see a quota error, wait until midnight UTC for your daily limit to reset,
      or raise your quota ceiling in Google Cloud Console.
    """)
    # End of Help & FAQ section