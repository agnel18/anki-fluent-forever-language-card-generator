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

    ## Why should I set API quotas in Google Cloud?

    Budget alerts (email notifications) tell you *after* you've started spending — 
    by then it may be too late. **Hard quotas block API calls the moment your limit is 
    hit**, so Google can never charge you beyond what you've allowed.

    One of our users generated a large deck without realising they'd left their key 
    unrestricted and received an unexpected ₹600 (~$7) bill. A hard quota set to 
    500 requests/day would have stopped generation automatically and prevented the charge entirely.

    **To set hard quotas (takes 2 minutes):**
    1. Open [Google Cloud Console → APIs & Services](https://console.cloud.google.com/apis/dashboard)
    2. Click **"Generative Language API"** → **"Quotas & System Limits"** tab
    3. Edit **"Generate content requests per day per project"** → set e.g. **500**
    4. Repeat for **Cloud Text-to-Speech API** → **"Characters synthesized per day"** → set e.g. **50,000**

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