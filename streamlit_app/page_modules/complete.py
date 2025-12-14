# pages/complete.py - Deck completion and download page for the language learning app

import streamlit as st
import os


def render_complete_page():
    """Render the deck completion page with download options."""
    
    # Clear any previous page content to prevent bleeding
    st.empty()
    
    # Check if we have the required session state for this page
    if "selected_words" not in st.session_state or "selected_lang" not in st.session_state:
        st.markdown("# 🔄 Redirecting...")
        st.markdown("Setting up a new deck generation...")
        return

    st.markdown("# ✅ Step 5: Download Your Deck")
    st.markdown("Your personalized Anki deck is ready! Download and import it into Anki to start learning.")

    # Progress indicator with celebration
    st.markdown("**Progress:** Complete! 🎉")
    st.progress(1.0)

    # Success animation/message
    st.success("🎊 **Deck generation completed successfully!**")
    st.markdown("---")

    total_cards = len(st.session_state.selected_words) * 3  # 3 cards per word

    # Generation Summary
    st.markdown("## 📋 Generation Summary")
    
    col_summary1, col_summary2 = st.columns(2)
    
    with col_summary1:
        st.markdown("**Settings Used:**")
        st.markdown(f"- **Language:** {st.session_state.selected_lang}")
        st.markdown(f"- **Words:** {len(st.session_state.selected_words)}")
        st.markdown(f"- **Difficulty:** {st.session_state.get('difficulty', 'intermediate').title()}")
        st.markdown(f"- **Sentence Length:** {st.session_state.get('sentence_length_range', [5, 15])[0]}-{st.session_state.get('sentence_length_range', [5, 15])[1]} words")
        st.markdown(f"- **Sentences per Word:** {st.session_state.get('sentences_per_word', 10)}")
    
    with col_summary2:
        # Topic information
        enable_topics = st.session_state.get('enable_topics', False)
        if enable_topics:
            selected_topics = st.session_state.get('selected_topics', [])
            if selected_topics:
                st.markdown("**Topics:** " + ", ".join(selected_topics))
            else:
                st.markdown("**Topics:** None selected")
        else:
            st.markdown("**Topics:** Off")
        
        st.markdown(f"- **Audio Speed:** {st.session_state.get('audio_speed', 0.8)}x")
        st.markdown(f"- **Voice:** {st.session_state.get('selected_voice', 'Default')}")
        st.markdown(f"- **Total Cards:** {total_cards}")

    st.divider()

    st.markdown(f"**{len(st.session_state.selected_words)} words** • **{total_cards} cards** (3 learning modes per word) • **Ready to import!**")
    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📥 Download Your Deck")
        st.markdown("""
        Your .apkg file includes:
        - ✅ All flashcards with 3 card types each
        - ✅ Audio files (embedded)
        - ✅ Images (embedded)
        - ✅ IPA transcriptions
        - ✅ Image search keywords

        **3 Card Types:**
        1. 🎧 **Listening**: Hear → Understand
        2. 💬 **Production**: English → Speak target language
        3. 📖 **Reading**: Read → Comprehend
        """)

        if "apkg_file" in st.session_state and st.session_state.apkg_file:
            # Add download button with enhanced styling
            st.markdown("**Ready to download!** 📥")
            download_col1, download_col2 = st.columns([3, 1])
            with download_col1:
                st.download_button(
                    label="⬇️ Download Anki Deck (.apkg)",
                    data=st.session_state.apkg_file,
                    file_name=st.session_state.get("apkg_filename", f"{st.session_state.selected_lang.replace(' ', '_')}_deck.apkg"),
                    mime="application/octet-stream",
                    use_container_width=True,
                    key="apkg_download_complete"
                )
            with download_col2:
                st.markdown(f"**{len(st.session_state.apkg_file):,} bytes**")
        else:
            st.warning("⚠️ Deck file not found. Please try regenerating your deck.")
        # Show log file download button next to .apkg
        if "log_file_path" in st.session_state and st.session_state['log_file_path'] and os.path.exists(st.session_state['log_file_path']):
            with open(st.session_state['log_file_path'], "rb") as f:
                st.download_button(
                    label="⬇️ Download Generation Log (TXT)",
                    data=f.read(),
                    file_name="generation_log.txt",
                    mime="text/plain",
                    use_container_width=True,
                    key="log_download_complete"
                )
            # Don't delete the log file immediately - let user download it
            # File will be cleaned up when session ends or user creates new deck

    with col2:
        st.markdown("### 📖 How to Import")
        st.markdown(f"""
        **Super Easy! Just 2 steps:**

        1. **Double-click** the downloaded .apkg file
        2. Anki opens and imports automatically! ✨

        **Or manually:**
        1. Open Anki
        2. File → Import...
        3. Select the .apkg file
        4. Click Import

        **All done!** Your {st.session_state.selected_lang} deck with {total_cards} cards is ready to study.

        Cards include audio, images, and phonetic guides (IPA) for pronunciation.
        """)

    st.divider()

    # Navigation buttons
    col_back, col_new, col_keys = st.columns([1, 1, 1])
    with col_back:
        if st.button("⬅️ Back to Generate", key="back_from_complete", use_container_width=True):
            # Reset generation progress when going back
            if 'generation_progress' in st.session_state:
                st.session_state['generation_progress']['step'] = 0
            st.session_state.page = "generate"
            st.rerun()
    with col_new:
        if st.button("🔄 Create New Deck", key="generate_another", use_container_width=True):
            # Clean up old files and reset state relevant to generation
            for key in ["selected_words", "selected_lang", "apkg_file", "apkg_filename"]:
                if key in st.session_state:
                    del st.session_state[key]
            # Clean up log file if it exists
            if "log_file_path" in st.session_state and st.session_state['log_file_path']:
                try:
                    if os.path.exists(st.session_state['log_file_path']):
                        os.remove(st.session_state['log_file_path'])
                except Exception:
                    pass
                st.session_state['log_file_path'] = None
            st.session_state.page = "language_select"
            st.rerun()
    with col_keys:
        if st.button("🔑 API Settings", key="change_keys", use_container_width=True):
            st.session_state.page = "api_setup"
            st.rerun()