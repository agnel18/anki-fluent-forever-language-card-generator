# pages/generate.py - Generate deck page for the language learning app

import streamlit as st
import pandas as pd
import sys
import os
import logging

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)

try:
    from persistent_cache import process_large_dataset_with_memory_management, optimize_memory_for_large_datasets
except ImportError:
    pass

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
    
    # Separate section for viewing and editing selected words with enrichment data
    st.markdown("---")
    st.markdown("### 📚 Word Enrichment and Review (Optional)")
    st.markdown("Provide Word Meanings, Variations, Examples, or cultural notes (max 300 characters).")
    st.markdown("Your input helps create more personalized and accurate sentences.")
    st.markdown("*Leave blank to skip - the AI will generate content based on the word itself.*")
    
    st.markdown("**Example:** For \"house\" you might enter:")
    st.code("Meanings: A building where people live; home; residence\nUsage: He built a house in the outskirts of town.", language=None)
    
    if selected_words:
        # Initialize with empty meanings for user input
        word_data = [{'word': word, 'meaning': '', 'source': 'User Input'} for word in selected_words]
        st.session_state.word_enrichment_data = word_data
        st.session_state.last_selected_words = selected_words.copy()
        
        # Convert to DataFrame for editing
        df = pd.DataFrame(word_data)
        
        # Display editable consolidated meaning fields for each word

        # Create individual text areas for each word
        edited_data = []
        for idx, row in df.iterrows():
            word = row['word']
            current_meaning = row['meaning']
            source = row['source']

            st.markdown(f"### 📝 **{word}**")
            st.caption(f"Source: {source}")

            # Use text_area for multi-line editing
            edited_meaning = st.text_area(
                f"Consolidated meaning for '{word}':",
                value=current_meaning,
                height=200,
                max_chars=300,
                help=f"Enter comprehensive meaning information for '{word}'. Include alternatives, examples, and context. The AI will parse this intelligently.",
                key=f"meaning_editor_{idx}"
            )

            # Encapsulate user input in {} for AI processing
            meaning_to_use = f"{{{edited_meaning}}}" if edited_meaning.strip() else ""

            edited_data.append({
                'word': word,
                'meaning': meaning_to_use,
                'source': source
            })

            st.markdown("---")

        # Convert back to DataFrame for consistency
        edited_df = pd.DataFrame(edited_data)

        # Store edited data in session state for use in generation
        if edited_data:
            st.session_state.edited_word_data = edited_data

        # Show data quality summary
        valid_meanings = sum(1 for item in edited_data if item['meaning'] and item['meaning'] != 'N/A')
        st.markdown(f"**Data Quality:** {valid_meanings}/{len(edited_data)} words have meanings")
        
    else:
        st.warning("No words selected!")
        st.session_state.word_enrichment_data = []
        st.session_state.edited_word_data = []

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
                # Get selected words and edited enrichment data from previous step
                selected_words = st.session_state.get('selected_words', [])
                edited_word_data = st.session_state.get('edited_word_data', [])
                selected_lang = st.session_state.get('selected_language', '')
                if not selected_words:
                    st.error("No words selected. Please go back and select some words.")
                else:
                    # Set loading state and transition immediately
                    st.session_state.generating_deck = True
                    st.session_state.selected_lang = selected_lang
                    st.session_state.selected_words = selected_words
                    st.session_state.word_enrichment_data = edited_word_data  # Pass enriched data
                    st.session_state.page = "generating"
                    st.rerun()

    # Scroll to top after all content is rendered
    st.markdown("""
    <script>
        setTimeout(function() {
            window.scrollTo({top: 0, behavior: 'smooth'});
        }, 1000);
    </script>
    """, unsafe_allow_html=True)