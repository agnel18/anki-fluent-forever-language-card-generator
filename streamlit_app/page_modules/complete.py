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
            # Calculate file size in KB
            file_size_kb = round(len(st.session_state.apkg_file) / 1024)
            
            # Create consistent button layout
            button_col1, button_col2 = st.columns(2)
            with button_col1:
                st.download_button(
                    label=f"⬇️ Download Anki Deck (.apkg) ({file_size_kb} KB)",
                    data=st.session_state.apkg_file,
                    file_name=st.session_state.get("apkg_filename", f"{st.session_state.selected_lang.replace(' ', '_')}_deck.apkg"),
                    mime="application/octet-stream",
                    use_container_width=True,
                    key="apkg_download_complete",
                    type="primary"
                )
            with button_col2:
                # Show log file download button in the same column layout
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
                else:
                    # Empty space to maintain layout if no log file
                    st.write("")
        else:
            st.warning("⚠️ Deck file not found. Please try regenerating your deck.")

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

    # Donation Section
    st.markdown("### 💝 Enjoying the App?")
    st.markdown("**Support our mission to keep language learning free and accessible!**")

    donation_url = "https://razorpay.me/@agneljosephn"

    col_donate1, col_donate2, col_donate3 = st.columns([1, 2, 1])
    with col_donate2:
        st.markdown(f'<a href="{donation_url}" target="_blank" style="text-decoration: none;"><button style="background-color: #FF6B35; color: white; border: none; padding: 12px 24px; border-radius: 6px; cursor: pointer; font-size: 16px; font-weight: bold; width: 100%;">💳 Make a Donation</button></a>', unsafe_allow_html=True)

    st.markdown("*Your support helps us add more languages and features!* 🎉")

    st.divider()

    # Navigation buttons
    col_back, col_new, col_keys = st.columns([1, 1, 1])
    with col_back:
        if st.button("⬅️ Back to Generate", key="back_from_complete", use_container_width=True):
            # Reset generation progress when going back
            if 'generation_progress' in st.session_state:
                st.session_state['generation_progress']['step'] = 0
            # Clear the apkg_file and related state since we're going back to regenerate
            for key in ["apkg_file", "apkg_filename", "log_file_path", "log_stream", "output_dirs_cleared"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.page = "generate"
            st.rerun()
    with col_new:
        if st.button("🔄 Create New Deck", key="generate_another", use_container_width=True):
            # Reset generating flag for new deck creation
            st.session_state.generating_deck = False
            
            # Clean up old files and reset state relevant to generation
            for key in ["selected_words", "selected_lang", "selected_language", "apkg_file", "apkg_filename", "generation_progress", "generation_log", "log_file_path", "log_stream", "output_dirs_cleared"]:
                if key in st.session_state:
                    del st.session_state[key]
            # Clean up log file if it exists
            if "log_file_path" in st.session_state and st.session_state.get('log_file_path'):
                try:
                    if os.path.exists(st.session_state['log_file_path']):
                        os.remove(st.session_state['log_file_path'])
                except Exception:
                    pass
            st.session_state.page = "language_select"
            st.rerun()
    with col_keys:
        if st.button("🔑 API Settings", key="change_keys", use_container_width=True, type="secondary"):
            st.session_state.page = "api_setup"
            st.rerun()

    # Scroll to top after all content is rendered
    st.markdown("""
    <script>
        setTimeout(function() {
            window.scrollTo({top: 0, behavior: 'smooth'});
        }, 1000);
    </script>
    """, unsafe_allow_html=True)