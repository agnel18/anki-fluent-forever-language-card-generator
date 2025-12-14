# pages/generate.py - Generate deck page for the language learning app

import streamlit as st


def render_generate_page():
    """Render the generate deck page."""
    st.markdown("# ⚙️ Step 4: Generate Deck")
    st.markdown("Review your settings and start generating your personalized Anki deck.")

    # Progress indicator
    st.markdown("**Progress:** Step 4 of 5")
    st.progress(0.8)

    st.markdown("---")

    # Show summary of settings
    st.markdown("## 📋 Generation Summary")

    selected_words = st.session_state.get('selected_words', [])
    selected_lang = st.session_state.get('selected_language', '')

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Language:**")
        st.info(selected_lang if selected_lang else "Not selected")

        st.markdown("**Words Selected:**")
        st.info(f"{len(selected_words)} words")

        if selected_words:
            with st.expander("View Selected Words"):
                st.write(", ".join(selected_words[:20]))
                if len(selected_words) > 20:
                    st.write(f"... and {len(selected_words) - 20} more")

    with col2:
        st.markdown("**Sentences per Word:**")
        st.info(f"{st.session_state.get('sentences_per_word', 10)}")

        st.markdown("**Audio Voice:**")
        st.info(st.session_state.get('selected_voice_display', 'Default'))

        st.markdown("**Audio Speed:**")
        st.info(f"{st.session_state.get('audio_speed', 0.8)}x")

    st.markdown("---")
    st.markdown("### Ready to Generate!")
    st.markdown("Click the **Generate Deck** button above to start creating your Anki deck. This process will:")
    st.markdown("- Generate example sentences for each word")
    st.markdown("- Create audio pronunciations")
    st.markdown("- Find relevant images")
    st.markdown("- Package everything into an Anki deck file")

    if not selected_words:
        st.warning("⚠️ No words selected. Please go back to the word selection step.")

    st.markdown("---")

    # Navigation buttons at bottom
    col_back, col_generate = st.columns([1, 1])
    with col_back:
        if st.button("⬅️ Back to Output Settings", key="back_from_generate", use_container_width=True):
            st.session_state.page = "sentence_settings"
            st.rerun()
    with col_generate:
        # Add loading state for generate button
        if st.session_state.get('generating_deck', False):
            with st.spinner("🚀 Starting deck generation..."):
                st.markdown("**Please wait while we prepare your deck generation...**")
                # Keep the spinner active while transitioning
                import time
                time.sleep(0.5)  # Brief pause for visual feedback
        else:
            if st.button("🚀 Generate Deck", key="generate_deck_button", use_container_width=True):
                # Get selected words from previous step
                selected_words = st.session_state.get('selected_words', [])
                selected_lang = st.session_state.get('selected_language', '')
                if not selected_words:
                    st.error("No words selected. Please go back and select some words.")
                else:
                    # Set loading state
                    st.session_state.generating_deck = True
                    st.session_state.selected_lang = selected_lang
                    st.session_state.selected_words = selected_words
                    st.session_state.page = "generating"
                    st.session_state.scroll_to_top = True
                    st.rerun()