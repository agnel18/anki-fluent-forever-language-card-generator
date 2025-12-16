# pages/generate.py - Generate deck page for the language learning app

import streamlit as st


def render_generate_page():
    """Render the generate deck page."""
    # Reset generating flag if we're not actually generating
    if not st.session_state.get('generation_progress', {}).get('step', 0) == 1:
        st.session_state.generating_deck = False
    
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
    num_sentences = st.session_state.get('sentences_per_word', 10)
    audio_speed = st.session_state.get('audio_speed', 0.8)
    voice = st.session_state.get('selected_voice_display', 'Default')
    enable_topics = st.session_state.get("enable_topics", False)
    selected_topics = st.session_state.get("selected_topics", [])

    # Main settings overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🌍 **Language**")
        st.info(f"**{selected_lang}**")
        
        st.markdown("### 📝 **Words Selected**")
        st.info(f"**{len(selected_words)} words**")
        
    with col2:
        st.markdown("### ⚙️ **Sentences per Word**")
        st.info(f"**{num_sentences} sentences**")
        
        st.markdown("### 🔊 **Audio Voice**")
        st.info(f"**{voice}**")
        
    with col3:
        st.markdown("### 🎵 **Audio Speed**")
        st.info(f"**{audio_speed}x**")
        
        st.markdown("### 🎯 **Topics Selected**")
        if enable_topics and selected_topics:
            st.info(f"**{len(selected_topics)} topics**")
            topics_text = ", ".join(selected_topics)
            if len(topics_text) > 80:
                topics_text = topics_text[:77] + "..."
            st.caption(f"{topics_text}")
        else:
            st.info("**No topics**")
    
    # Separate section for viewing selected words
    st.markdown("---")
    st.markdown("### 👀 **View Selected Words**")
    if selected_words:
        with st.expander("Click to view all selected words", expanded=False):
            # Display words in a nice grid
            cols = st.columns(4)
            for i, word in enumerate(selected_words):
                cols[i % 4].write(f"• {word}")
    else:
        st.warning("No words selected!")

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
            if st.button("🚀 Generate Deck", key="generate_deck_button", use_container_width=True, type="primary"):
                # Get selected words from previous step
                selected_words = st.session_state.get('selected_words', [])
                selected_lang = st.session_state.get('selected_language', '')
                if not selected_words:
                    st.error("No words selected. Please go back and select some words.")
                else:
                    # Show full-screen loading overlay to hide previous content
                    st.markdown("""
                    <style>
                    .loading-overlay {
                        position: fixed;
                        top: 0;
                        left: 0;
                        width: 100%;
                        height: 100%;
                        background: rgba(var(--bg-color-rgb, 255, 255, 255), 0.95);
                        z-index: 9999;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        flex-direction: column;
                    }
                    .loading-spinner {
                        border: 4px solid #f3f3f3;
                        border-top: 4px solid #3498db;
                        border-radius: 50%;
                        width: 50px;
                        height: 50px;
                        animation: spin 2s linear infinite;
                    }
                    @keyframes spin {
                        0% { transform: rotate(0deg); }
                        100% { transform: rotate(360deg); }
                    }
                    </style>
                    <div class="loading-overlay">
                        <div class="loading-spinner"></div>
                        <h2 style="color: #3498db; margin-top: 20px;">🚀 Starting Deck Generation...</h2>
                        <p style="color: #666;">Please wait while we prepare your personalized Anki deck</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Small delay to show loading overlay
                    import time
                    time.sleep(1)
                    
                    # Set loading state and transition
                    st.session_state.generating_deck = True
                    st.session_state.selected_lang = selected_lang
                    st.session_state.selected_words = selected_words
                    st.session_state.page = "generating"
                    st.session_state.scroll_to_top = True
                    st.rerun()