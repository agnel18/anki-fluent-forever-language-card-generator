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
    from word_data_fetcher import enrich_word_data as fetch_word_data, enrich_word_data_batch, get_word_data_for_cards_batch
    from persistent_cache import process_large_dataset_with_memory_management, optimize_memory_for_large_datasets
except ImportError:
    def fetch_word_data(word, lang):
        return f"{word} = [No enrichment module available]"
    def enrich_word_data_batch(words, lang, batch_size=5):
        return {word: fetch_word_data(word, lang) for word in words}

def fetch_word_enrichment_data(selected_words, selected_lang):
    """Fetch enrichment data for selected words with progress tracking, batch processing, and memory management."""
    if not selected_words:
        return []

    # Initialize progress
    progress_bar = st.progress(0)
    status_text = st.empty()

    # Use full language name instead of 2-letter code
    lang_name = selected_lang

    # Determine processing strategy based on dataset size
    word_count = len(selected_words)
    large_dataset_threshold = 50  # Consider datasets > 50 words as large

    if word_count > large_dataset_threshold:
        # Use memory-managed processing for large datasets
        status_text.text(f"Processing large dataset ({word_count} words) with memory management...")

        def progress_callback(batch_num, total_batches, batch_size):
            progress = batch_num / total_batches
            progress_bar.progress(progress)
            status_text.text(f"Processing batch {batch_num}/{total_batches} ({batch_size} words)")

        def process_batch(batch):
            """Process a batch of words and return word data entries."""
            batch_results = enrich_word_data_batch([word for word, _ in batch], lang_name, batch_size=len(batch))

            word_entries = []
            for word in [word for word, _ in batch]:
                consolidated_data = batch_results.get(word, f"{word} = [Batch processing error]")
                word_entries.append({
                    'word': word,
                    'meaning': consolidated_data,
                    'source': _extract_source_from_consolidated(consolidated_data)
                })
            return word_entries

        # Prepare batch data (word, index pairs for tracking)
        batch_data = [(word, i) for i, word in enumerate(selected_words)]

        try:
            word_data = process_large_dataset_with_memory_management(
                batch_data,
                process_batch,
                batch_size=min(10, word_count),  # Smaller batches for memory management
                max_memory_mb=400,  # 400MB limit
                progress_callback=progress_callback
            )

        except Exception as e:
            logger.error(f"Memory-managed processing failed: {e}")
            status_text.text("⚠️ Memory-managed processing failed, falling back to standard batch processing...")
            # Fall back to regular batch processing
            return _fetch_with_standard_batch_processing(selected_words, lang_name, progress_bar, status_text)

    else:
        # Use standard batch processing for smaller datasets
        word_data = _fetch_with_standard_batch_processing(selected_words, lang_name, progress_bar, status_text)

    progress_bar.progress(1.0)
    status_text.text("✅ Word enrichment data fetched successfully!")
    progress_bar.empty()
    status_text.empty()

    return word_data


def _fetch_with_standard_batch_processing(selected_words, lang_name, progress_bar, status_text):
    """Standard batch processing implementation."""
    # Use batch processing for better performance
    batch_size = min(5, len(selected_words))  # Process up to 5 words at a time
    status_text.text(f"Batch processing {len(selected_words)} words (batch size: {batch_size})...")

    try:
        # Batch enrich all words at once
        enriched_data = enrich_word_data_batch(selected_words, lang_name, batch_size)

        # Convert to expected format
        word_data = []
        for i, word in enumerate(selected_words):
            progress_bar.progress((i + 1) / len(selected_words))
            status_text.text(f"Processing results for word {i+1}/{len(selected_words)}: {word}")

            consolidated_data = enriched_data.get(word, f"{word} = [Batch processing error]")
            word_data.append({
                'word': word,
                'meaning': consolidated_data,  # Single consolidated field
                'source': _extract_source_from_consolidated(consolidated_data)
            })

    except Exception as e:
        logger.error(f"Batch processing failed, falling back to sequential: {e}")
        # Fallback to original sequential processing
        word_data = []
        for i, word in enumerate(selected_words):
            status_text.text(f"Fetching data for word {i+1}/{len(selected_words)}: {word}")
            progress_bar.progress(i / len(selected_words))

            try:
                consolidated_data = fetch_word_data(word, lang_name)
                word_data.append({
                    'word': word,
                    'meaning': consolidated_data,
                    'source': _extract_source_from_consolidated(consolidated_data)
                })
            except Exception as e:
                word_data.append({
                    'word': word,
                    'meaning': f'{word} = [Error fetching data: {str(e)}]',
                    'source': 'Error'
                })

    return word_data

def _extract_source_from_consolidated(consolidated_text: str) -> str:
    """Extract source information from consolidated meaning text."""
    if "Sources:" in consolidated_text:
        # Find the sources section
        sources_start = consolidated_text.find("Sources:")
        sources_section = consolidated_text[sources_start:]
        # Extract the first line after "Sources:"
        lines = sources_section.split('\n')
        if len(lines) > 1:
            source_line = lines[1].strip()
            if source_line.startswith('- Data from:'):
                return source_line.replace('- Data from:', '').strip()
    return "Unknown"


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
    st.markdown("### 📚 **Review & Edit Word Meanings**")
    st.markdown("Review the consolidated meaning data fetched from reliable sources. Edit the single meaning field to add multiple definitions, variations, examples, and cultural context - the AI will intelligently parse all information for better sentence generation.")
    
    if selected_words:
        # Fetch word enrichment data if not already cached in session
        # Force refresh for now to test new consolidated format
        with st.spinner("🔍 Fetching word enrichment data..."):
            word_data = fetch_word_enrichment_data(selected_words, selected_lang)
            st.session_state.word_enrichment_data = word_data
            st.session_state.last_selected_words = selected_words.copy()
        
        # Convert to DataFrame for editing
        df = pd.DataFrame(word_data)
        
        # Display editable consolidated meaning fields for each word
        st.markdown("**Edit the consolidated meaning data below to improve sentence generation quality:**")
        st.markdown("*💡 Tip: You can add multiple meanings, variations, examples, and cultural notes in each field. The AI will intelligently parse all information.*")

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
                help=f"Enter comprehensive meaning information for '{word}'. Include alternatives, examples, and context. The AI will parse this intelligently.",
                key=f"meaning_editor_{idx}"
            )

            edited_data.append({
                'word': word,
                'meaning': edited_meaning,
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