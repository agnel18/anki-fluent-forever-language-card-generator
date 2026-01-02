# pages/generating.py - Deck generation page for the language learning app

import streamlit as st
import shutil
import os
import tempfile
import datetime
import time
import re
from utils import get_secret, log_message
from core_functions import generate_complete_deck
from services.generation.log_manager import LogManager
from services.generation.progress_tracker import ProgressTracker
from services.generation.session_validator import SessionValidator
from services.generation.file_manager import FileManager


def render_generating_page():
    """Render the deck generation page with comprehensive error recovery."""
    
    st.markdown("# ⚙️ Generating Your Deck")

    # Initialize session validator and validate session state
    session_validator = SessionValidator()
    if not session_validator.validate_session_state():
        return

    # Get generation settings from session validator
    settings = session_validator.get_generation_settings()
    selected_lang = settings['selected_lang']
    selected_words = settings['selected_words']
    enable_topics = settings['enable_topics']
    selected_topics = settings['selected_topics']
    
    st.markdown(f"**Language:** {selected_lang} | **Words:** {len(selected_words)}")
    st.divider()

    # Initialize generation progress and logging
    session_validator.initialize_generation_progress()
    session_validator.initialize_logging()

    # Initialize LogManager service (always available after logging is set up)
    if 'log_stream' in st.session_state:
        st.session_state['log_manager'] = LogManager(st.session_state['log_stream'])

    step = session_validator.get_generation_step()

    # Show summary only if not yet generating
    if step == 0:
        # --- Generation Summary ---
        with st.container():
            st.markdown("## 📋 Generation Summary")
            
            # Get all parameters for display
            num_sentences = st.session_state.sentences_per_word
            min_length, max_length = st.session_state.sentence_length_range
            difficulty = st.session_state.difficulty
            audio_speed = st.session_state.audio_speed
            voice = st.session_state.selected_voice
            
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
            st.markdown("### 👀 **Selected Words**")
            if selected_words:
                # Display words in a simple grid (no expander needed for 5 words max)
                cols = st.columns(4)
                for i, word in enumerate(selected_words):
                    cols[i % 4].write(f"• {word}")
            else:
                st.warning("No words selected!")
            
    # Clear any previous content when transitioning to generation
    elif step > 0:
        # Force clear of any lingering summary content
        st.empty()
        
        # Show generation summary at the top (compact format for active generation)
        st.markdown("## 📋 **Generation Summary**")
        st.markdown("**Settings Used:**")

        # Get all parameters for display using SessionValidator
        settings = session_validator.get_generation_settings()
        num_sentences = settings['num_sentences']
        min_length = settings['min_length']
        max_length = settings['max_length']
        difficulty = settings['difficulty']
        audio_speed = settings['audio_speed']
        voice = settings['voice']
        total_cards = len(selected_words) * num_sentences
        
        # Compact 2-column layout for generation page
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"🌍 **Language:** {selected_lang}")
            st.markdown(f"📝 **Words:** {len(selected_words)}")
            st.markdown(f"🎯 **Difficulty:** {difficulty}")
            st.markdown(f"📏 **Sentence Length:** {min_length}-{max_length} words")
            
        with col2:
            st.markdown(f"⚙️ **Sentences per Word:** {num_sentences}")
            if enable_topics and selected_topics:
                topics_str = ", ".join(selected_topics)
                if len(topics_str) > 30:
                    topics_str = topics_str[:27] + "..."
                st.markdown(f"🎨 **Topics:** {topics_str}")
            else:
                st.markdown("🎨 **Topics:** None")
            st.markdown(f"🎵 **Audio Speed:** {audio_speed}x")
            st.markdown(f"🔊 **Voice:** {voice}")
        
        st.markdown(f"**Total Cards:** {total_cards} ({len(selected_words)} words × {num_sentences} cards)")
        st.markdown("*Ready to import!* 🚀")
        
        st.markdown("---")
        
        # Show process overview only when generating
        st.markdown("## 📖 **6-Pass Generation Process**")
        st.markdown("Your deck is created through a comprehensive 6-pass process, each building on the previous for optimal learning:")
        
        # Simplified, user-focused timeline format
        st.markdown("""
**1. 🔤 Smart Sentences**  
Generate contextual sentences with pronunciation and visual cues.  
*Foundation for quality learning - creates the core content efficiently.*

**2. ✅ Quality Validation**  
Ensure natural speech patterns and add translations.  
*Quality control - catches issues before expensive media generation.*

**3. 🎨 Grammar Analysis**  
Break down sentence structure with color-coded explanations.  
*Transforms vocabulary into comprehensive grammar lessons.*

**4. 🔊 Audio Generation**  
Create natural-sounding pronunciations with adjustable speed.  
*Builds listening skills - makes learning active and accessible.*

**5. 🖼️ Visual Media**  
Find and download relevant images for memory reinforcement.  
*Dual-coding theory - improves recall by combining text and visuals.*

**6. 📦 Final Assembly**  
Combine all components into a professional Anki deck.  
*Creates ready-to-use flashcards with multimedia support.*
""")
        
        st.markdown("---")

    # Logging is now initialized by SessionValidator above

    # Enhanced progress display with animations (always available for generation)
    st.markdown("## 📊 **Real-Time Progress**")

    # Add IPA explanation
    with st.expander("📚 **What are IPA Transcriptions?**", expanded=False):
        st.markdown("""
        **IPA (International Phonetic Alphabet)** is the universal system for phonetic transcription.
        
        - **Purpose**: Represents pronunciation accurately using special symbols
        - **Why it helps**: Learn correct pronunciation, especially for tricky sounds
        - **How to use**: Compare the IPA symbols with your native language sounds
        
        **Interactive Learning**: Visit [ipachart.com](https://www.ipachart.com/) to hear each IPA symbol pronounced by native speakers.
        
        *Example*: The English word "think" is transcribed as /θɪŋk/ in IPA.
        """)

    progress_container = st.container()
    with progress_container:
        progress_bar = st.progress(0)
        status_text = st.empty()
        detail_text = st.empty()

        # Define progress elements before columns
        current_status = st.empty()
        step_indicator = st.empty()
        pass_indicator = st.empty()

        # Add animated status indicators
        status_col1, status_col2 = st.columns([3, 1])
        with status_col1:
            pass
        with status_col2:
            pass

        messages_container = st.container()

        # Create an empty placeholder for real-time log updates
        log_display = st.empty()

        # Initialize services (log_manager is now always available)
        progress_tracker = ProgressTracker(
            progress_bar=progress_bar,
            status_text=status_text,
            detail_text=detail_text,
            pass_indicator=pass_indicator,
            log_manager=st.session_state['log_manager'],
            log_display=log_display
        )

        # Initialize FileManager service
        file_manager = FileManager(log_manager=st.session_state['log_manager'])

        # Define log update function for real-time updates
        def update_log_display(msg, display_element):
            """Update log display in real-time during generation."""
            st.session_state['log_manager'].log_message(msg)
            display_element.code(st.session_state['log_manager'].get_display_logs(), language=None)
            time.sleep(0.05)  # Brief pause for UI update

        # Display initial log content
        log_display.code(st.session_state['log_manager'].get_display_logs(), language=None)

    # Display Pass 1 results if available
    if step == 1 and 'generation_results' in st.session_state and st.session_state['generation_results'].get('pass1_results'):
        st.markdown("---")
        st.markdown("## 📝 **Generated Sentences (Pass 1 Results)**")
        for word_result in st.session_state['generation_results']['pass1_results']:
            st.markdown(f"### {word_result['word']}")
            for i, sentence in enumerate(word_result['sentences'], 1):
                st.markdown(f"**Sentence {i}:** {sentence['sentence']}")
                if 'ipa' in sentence:
                    st.markdown(f"**IPA:** /{sentence['ipa']}/")
                if 'keywords' in sentence:
                    st.markdown(f"**Keywords:** {', '.join(sentence['keywords'])}")
            st.markdown("---")

    # Get generation parameters
    groq_api_key = st.session_state.get('groq_api_key', get_secret('GROQ_API_KEY', ''))
    pixabay_api_key = st.session_state.get('pixabay_api_key', get_secret('PIXABAY_API_KEY', ''))
    num_sentences = st.session_state.sentences_per_word
    min_length, max_length = st.session_state.sentence_length_range
    difficulty = st.session_state.difficulty
    audio_speed = st.session_state.audio_speed
    voice = st.session_state.selected_voice
    import pathlib
    output_dir = str(pathlib.Path("./output"))

    # Clear output directories using FileManager
    file_manager.clear_output_directories()

    # Generation logic with comprehensive error recovery
    step = st.session_state['generation_progress']['step']

    if step == 0:
        # Clear previous generation log for fresh UI display with delay
        # (detailed log stream for export is preserved)
        if st.session_state.get('generation_log') and len(st.session_state['generation_log']) > 0:
            st.session_state['log_manager'].log_message("<b>🧹 Clearing previous log in 2 seconds...</b>")
            time.sleep(2)  # 2-second delay as requested
        
        # Clear the log completely for fresh start
        st.session_state['generation_log'] = []
        if 'log_manager' in st.session_state:
            st.session_state['log_manager'].clear_logs()
        
        # Start generation
        current_status.markdown("🚀 **Starting deck generation...**")
        step_indicator.markdown("⚙️ **Initializing**")
        st.session_state['log_manager'].log_message("<b>🚀 Starting comprehensive deck generation with error recovery...</b>")
        status_text.info("🚀 Initializing deck generation...")
        detail_text.markdown("*Setting up generation with comprehensive error recovery and graceful degradation...*")

        # Mark as started
        st.session_state['generation_progress']['step'] = 1
        st.rerun()

    # Check word limit before generation
    elif len(selected_words) > 5:
        current_status.markdown("⚠️ **Generation Limit Exceeded**")
        step_indicator.markdown("❌ **Too Many Words**")
        st.session_state['log_manager'].log_message("<b>❌ Generation cancelled - too many words selected</b>")
        status_text.error(f"You selected {len(selected_words)} words, but the maximum is 5 words per generation.")
        detail_text.markdown("*This limit helps prevent API rate limits and ensures reliable generation.*")
        
        # Show selected words and ask user to reduce
        with st.expander("📋 Your Selected Words (Please reduce to 10 or fewer)", expanded=True):
            cols = st.columns(4)
            for i, word in enumerate(selected_words):
                cols[i % 4].write(f"• {word}")
        
        # Provide options
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Back to Word Selection", use_container_width=True):
                st.session_state.page = "word_select"
                st.rerun()
        with col2:
            if st.button("🔄 Clear Selection & Start Over", use_container_width=True):
                st.session_state.selected_words = []
                st.session_state.page = "word_select"
                st.rerun()

    elif step == 1:
        # Perform progressive generation - process one word at a time for real-time UI updates
        current_status.markdown("⚙️ **Generating your complete deck...**")
        step_indicator.markdown("🔄 **Processing**")

        # Initialize progressive generation state
        if 'generation_substep' not in st.session_state:
            st.session_state['generation_substep'] = 0
            st.session_state['generation_results'] = {
                'words_data': [],
                'audio_files': [],
                'image_files': [],
                'errors': [],
                'partial_success': True,
                'pass1_results': []
            }
            st.session_state['log_manager'].log_message("<b>⚙️ Starting progressive deck generation...</b>")
            status_text.info("⚙️ Starting progressive deck generation...")
            detail_text.markdown("*Processing words one by one for real-time updates...*")

        # Get current substep
        substep = st.session_state['generation_substep']
        results = st.session_state['generation_results']

        # If we've processed all words, finalize the generation
        if substep >= len(selected_words):
            # All words processed - finalize the deck
            st.session_state['log_manager'].log_message("<b>📦 FINAL PASS: Deck Assembly</b>")
            st.session_state['log_manager'].log_message("Combining all word components into a professional Anki deck...")
            status_text.info("📦 Finalizing deck assembly...")

            try:
                from core_functions import create_apkg_from_word_data
                import pathlib

                output_path = pathlib.Path(output_dir)
                media_dir = output_path / "media"

                # Create the final APKG file
                apkg_file_path = output_path / f"{selected_lang}.apkg"
                success = create_apkg_from_word_data(
                    results['words_data'],
                    str(media_dir),
                    str(apkg_file_path),
                    selected_lang,
                    selected_lang
                )
                
                if success and apkg_file_path.exists():
                    apkg_path = str(apkg_file_path)
                    
                    # Load the APKG file into session state for download
                    if not file_manager.load_apkg_file(apkg_path):
                        raise Exception("Failed to load created APKG file for download")
                    
                    # Success!
                    result = {
                        'success': True,
                        'apkg_path': apkg_path,
                        'tsv_path': str(output_path / "ANKI_IMPORT.tsv"),
                        'media_dir': str(media_dir),
                        'output_dir': output_dir,
                        'errors': results['errors'],
                        'partial_success': results['partial_success']
                    }

                    st.session_state['log_manager'].log_message("<b>✅ Deck assembly completed successfully!</b>")
                    st.session_state['log_manager'].log_message(f"Created Anki deck with {len(results['words_data'])} words, {len(results['audio_files'])} audio files, {len(results['image_files'])} images")
                    progress_bar.progress(1.0)
                    current_status.markdown("🎉 **Deck generation completed!**")
                    step_indicator.markdown("✅ **Success!**")
                    status_text.success("🎉 Deck generation completed successfully!")
                    detail_text.markdown("*Your Anki deck is ready. Moving to export...*")

                    # Update log display one final time
                    log_display.code(st.session_state['log_manager'].get_display_logs(), language=None)

                    # Store results and move to completion
                    progress = st.session_state['generation_progress']
                    progress['result'] = result
                    progress['success'] = True
                    progress['step'] = 2
                    st.session_state['generation_progress'] = progress

                    # Clean up progressive generation state
                    del st.session_state['generation_substep']
                    del st.session_state['generation_results']

                    st.rerun()
                else:
                    raise Exception("APKG file creation failed")

            except Exception as e:
                st.session_state['log_manager'].log_message(f"<b>❌ Deck finalization failed:</b> {e}")
                result = {
                    'success': False,
                    'error': f'Deck finalization failed: {e}',
                    'errors': results['errors'] + [{'error': f'Finalization failed: {e}'}],
                    'partial_success': False
                }

                # Update log display for error
                log_display.code(st.session_state['log_manager'].get_display_logs(), language=None)

                # Store results and move to completion
                progress = st.session_state['generation_progress']
                progress['result'] = result
                progress['success'] = False
                progress['step'] = 2
                st.session_state['generation_progress'] = progress

                # Clean up progressive generation state
                del st.session_state['generation_substep']
                del st.session_state['generation_results']

                st.rerun()

        else:
            # Process the current word using core_functions
            current_word = selected_words[substep]
            word_progress = (substep + 1) / len(selected_words)

            st.session_state['log_manager'].log_message(f"<b>🔤 Processing word {substep + 1}/{len(selected_words)}: '{current_word}'</b>")
            progress_bar.progress(word_progress)
            status_text.info(f"🔤 Processing word {substep + 1}/{len(selected_words)}: '{current_word}'")
            detail_text.markdown(f"*Generating sentences, audio, and images for '{current_word}'...*")

            try:
                from core_functions import generate_deck_progressive

                # Generate the word using core_functions with log callback
                result = generate_deck_progressive(
                    word=current_word,
                    language=selected_lang,
                    groq_api_key=groq_api_key,
                    pixabay_api_key=pixabay_api_key,
                    output_dir=output_dir,
                    num_sentences=num_sentences,
                    min_length=min_length,
                    max_length=max_length,
                    difficulty=difficulty,
                    audio_speed=audio_speed,
                    voice=voice,
                    topics=selected_topics if enable_topics else None,
                    native_language="English",
                    log_callback=lambda msg: update_log_display(msg, log_display)
                )

                if result['success']:
                    # Add successful word data to results
                    results['words_data'].append(result['word_data'])
                    results['audio_files'].extend(result['audio_files'])
                    results['image_files'].extend(result['image_files'])
                else:
                    # Handle partial failure
                    results['words_data'].append(result['word_data'])  # Add empty data to maintain structure
                    results['errors'].extend(result['errors'])
                    results['partial_success'] = False

                # Add Pass 1 results for display
                results['pass1_results'].append({
                    'word': current_word,
                    'sentences': result['word_data']['sentences']
                })

            except Exception as e:
                error_msg = f"Failed to process word '{current_word}': {e}"
                st.session_state['log_manager'].log_message(f"<b>⚠️ {error_msg}</b>")
                results['errors'].append({
                    'component': f"Word processing for '{current_word}'",
                    'error': str(e),
                    'critical': False
                })
                results['partial_success'] = False

                # Continue with empty data for this word to maintain structure
                word_data = {
                    'word': current_word,
                    'meaning': '',
                    'sentences': [],
                    'audio_files': ["" for _ in range(num_sentences)],
                    'image_files': ["" for _ in range(num_sentences)]
                }
                results['words_data'].append(word_data)

                # Add Pass 1 results for display (empty for failed words)
                results['pass1_results'].append({
                    'word': current_word,
                    'sentences': word_data['sentences']
                })

            # Move to next word
            st.session_state['generation_substep'] = substep + 1
            st.session_state['generation_results'] = results

            # Update log display in real-time
            log_display.code(st.session_state['log_manager'].get_display_logs(), language=None)

            # Trigger UI update
            time.sleep(0.1)  # Brief pause for UI stability
            st.rerun()
            if result is None:
                st.session_state['log_manager'].log_message("<b>❌ CRITICAL ERROR: generate_complete_deck() returned None</b>")
                log_message(f"[CRITICAL] generate_complete_deck() returned None for {len(selected_words)} words")
                result = {
                    'success': False,
                    'error': 'Function returned None - critical error',
                    'errors': [{'error': 'generate_complete_deck() returned None'}],
                    'error_summary': 'Critical: generation function failed to return result'
                }

            # Check if we should retry for temporary failures
            should_retry = False
            if not result.get('success') and retry_count < max_retries:
                errors = result.get('errors', [])
                # Retry for API rate limits, network issues, or temporary failures
                retryable_errors = ['rate limit', 'timeout', 'connection', 'network', 'temporary', '429', '503', '502']
                for error in errors:
                    if error and isinstance(error, dict):  # Safety check for None or non-dict errors
                        error_msg = error.get('error', '').lower()
                        if any(retryable_term in error_msg for retryable_term in retryable_errors):
                            should_retry = True
                            break
                
                if should_retry:
                    st.session_state['generation_retry_count'] = retry_count + 1
                    st.session_state['log_manager'].log_message(f"<b>🔄 Automatic retry #{retry_count + 1} due to temporary failure...</b>")
                    log_message(f"[RETRY] Attempting retry #{retry_count + 1} due to temporary failure")
                    time.sleep(3)  # Brief pause before retry
                    st.rerun()
                else:
                    # Reset retry counter for next generation
                    st.session_state['generation_retry_count'] = 0
            else:
                # Reset retry counter for next generation
                st.session_state['generation_retry_count'] = 0

            # Store results
            progress = st.session_state['generation_progress']
            progress['result'] = result
            progress['success'] = result.get('success', False)
            progress['error'] = result.get('error')
            progress['errors'] = result.get('errors', [])
            progress['error_summary'] = result.get('error_summary', '')
            progress['tsv_path'] = result.get('tsv_path')
            progress['media_dir'] = result.get('media_dir')
            progress['output_dir'] = result.get('output_dir')
            progress['partial_success'] = result.get('partial_success', False)

            # Log detailed results
            st.session_state['log_manager'].log_message(f"[DEBUG] Generation result: success={result.get('success', False)}")
            st.session_state['log_manager'].log_message(f"[DEBUG] Result details: {result}")
            log_message(f"[DEBUG] Generation completed. Success: {result.get('success', False)}")
            log_message(f"[DEBUG] TSV path: {result.get('tsv_path')}")
            log_message(f"[DEBUG] Media dir: {result.get('media_dir')}")
            log_message(f"[DEBUG] Errors: {len(result.get('errors', []))}")

            if result.get('success'):
                st.session_state['log_manager'].log_message("<b>✅ Deck generation completed successfully!</b>")
                log_message("[SUCCESS] Deck generation completed successfully!")
                progress_bar.progress(1.0)
                current_status.markdown("🎉 **Deck generation completed!**")
                step_indicator.markdown("✅ **Success!**")
                status_text.success("🎉 Deck generation completed successfully!")
                detail_text.markdown("*Your Anki deck is ready. Moving to export...*")

                # Track usage for achievements and analytics
                try:
                    from firebase_manager import is_signed_in
                    if is_signed_in() and 'user' in st.session_state and st.session_state.user:
                        user_id = st.session_state.user.get('uid')
                        if user_id:
                            # Log app usage
                            from usage_tracker import log_app_usage
                            log_app_usage(
                                user_id=user_id,
                                decks_generated=1,
                                words_generated=len(selected_words),
                                languages_used=[selected_lang],
                                session_duration=int(time.time() - st.session_state.get('session_start_time', time.time()))
                            )

                        # Update achievements
                        from achievements_manager import check_and_update_achievements
                        check_and_update_achievements(user_id)

                        log_message(f"[DEBUG] Usage tracked for user {user_id}: 1 deck, {len(selected_words)} words")
                except Exception as e:
                    log_message(f"[WARNING] Failed to track usage: {e}")

                # Use APKG file created by generate_complete_deck
                st.session_state['log_manager'].log_message("<b>📦 Using APKG file from generation...</b>")
                log_message("[DEBUG] Using APKG file from generate_complete_deck")
                
                try:
                    apkg_path = result.get('apkg_path')
                    if apkg_path and os.path.exists(apkg_path):
                        progress['apkg_path'] = apkg_path
                        progress['apkg_ready'] = True
                        
                        log_message(f"[DEBUG] APKG path from result: {apkg_path}")
                        st.session_state['log_manager'].log_message(f"<b>📦 APKG file found:</b> {apkg_path}")
                        
                        # Read APKG file and store in session state for download
                        if not file_manager.load_apkg_file(apkg_path):
                            st.error("Failed to load APKG file for download")
                            return
                        
                        # Save deck metadata to Firebase (for logged-in users)
                        try:
                            from firebase_manager import is_signed_in
                            if is_signed_in():
                                deck_metadata = {
                                    'deck_name': selected_lang,
                                    'language': selected_lang,
                                    'word_count': len(selected_words),
                                    'card_count': len(selected_words) * 3,  # 3 cards per word
                                    'created_at': datetime.datetime.now().isoformat(),
                                    'file_size': len(st.session_state.apkg_file),
                                    'filename': st.session_state.apkg_filename,
                                    'generation_settings': {
                                        'sentences_per_word': num_sentences,
                                        'sentence_length_range': [min_length, max_length],
                                        'difficulty': difficulty,
                                        'audio_speed': audio_speed,
                                        'voice': voice,
                                        'enable_topics': st.session_state.get('enable_topics', False),
                                        'selected_topics': st.session_state.get('selected_topics', [])
                                    },
                                    'words_used': selected_words
                                }
                                
                                # Save to Firebase
                                import firebase_admin
                                from firebase_admin import firestore
                                db = firestore.client()
                                
                                # Create deck document with auto-generated ID
                                deck_ref = db.collection('users').document(st.session_state.user['uid']).collection('decks').document()
                                deck_ref.set(deck_metadata)
                                
                                st.session_state['log_manager'].log_message(f"<b>💾 Deck metadata saved to cloud</b>")
                                log_message(f"[DEBUG] Deck metadata saved for user {st.session_state.user['uid']}: {deck_metadata['deck_name']}")
                            else:
                                log_message(f"[DEBUG] User not signed in, skipping deck metadata save")
                        except Exception as e:
                            st.session_state['log_manager'].log_message(f"<b>⚠️ Could not save deck metadata:</b> {e}")
                            log_message(f"[WARNING] Failed to save deck metadata: {e}")
                        
                    else:
                        st.session_state['log_manager'].log_message(f"<b>⚠️ APKG file not found at path:</b> {apkg_path}")
                        log_message(f"[ERROR] APKG file not found at path: {apkg_path}")
                        progress['apkg_ready'] = False
                        
                except Exception as e:
                    st.session_state['log_manager'].log_message(f"<b>⚠️ Failed to load APKG file:</b> {e}")
                    log_message(f"[ERROR] Failed to load APKG file: {e}")
                    progress['apkg_ready'] = False

                progress['step'] = 2  # Move to completion
                st.session_state['generation_progress'] = progress
                st.rerun()

            else:
                # Handle errors
                error_msg = result.get('error', 'Unknown error occurred')
                error_summary = result.get('error_summary', '')
                errors = result.get('errors', [])

                st.session_state['log_manager'].log_message(f"<b>❌ Deck generation completed with errors:</b> {error_msg}")
                log_message(f"[ERROR] Deck generation failed: {error_msg}")
                log_message(f"[ERROR] Error summary: {error_summary}")
                log_message(f"[ERROR] Total errors: {len(errors)}")
                
                if error_summary:
                    st.session_state['log_manager'].log_message(f"<b>Error Details:</b><br>{error_summary.replace(chr(10), '<br>')}")
                    log_message(f"[ERROR] Details: {error_summary}")
                
                # Log individual errors
                for i, error in enumerate(errors):
                    log_message(f"[ERROR #{i+1}] {error.get('component', 'Unknown')}: {error.get('error', 'Unknown error')}")
                    if error.get('critical'):
                        log_message(f"[CRITICAL] {error.get('component', 'Unknown')} failed critically")

                if error_summary:
                    st.session_state['log_manager'].log_message(f"<b>Error Details:</b><br>{error_summary.replace(chr(10), '<br>')}")

                # Enhanced Error Recovery Section
                st.markdown("---")
                st.markdown("### 🔧 Error Recovery Options")
                
                recovery_col1, recovery_col2 = st.columns(2)
                
                with recovery_col1:
                    st.markdown("**Quick Fixes:**")
                    
                    # Check for common issues and provide solutions
                    has_api_errors = any(error.get('component', '').startswith(('API', 'Groq', 'Pixabay')) for error in errors)
                    has_audio_errors = any('audio' in error.get('component', '').lower() for error in errors)
                    has_image_errors = any('image' in error.get('component', '').lower() for error in errors)
                    
                    if has_api_errors:
                        st.error("🔑 **API Issues Detected**")
                        st.info("• Check your API keys in Settings\n• Verify API limits/quota\n• Try again in a few minutes")
                        
                        if st.button("🔑 Go to API Settings", key="fix_api_keys"):
                            st.session_state.page = "settings"
                            st.rerun()
                    
                    if has_audio_errors:
                        st.warning("🔊 **Audio Generation Issues**")
                        st.info("• Audio will be skipped (cards still work)\n• Check internet connection\n• Try different voice settings")
                    
                    if has_image_errors:
                        st.warning("🖼️ **Image Generation Issues**")
                        st.info("• Images will be skipped (cards still work)\n• Check internet connection\n• Try again later")

                with recovery_col2:
                    st.markdown("**Recovery Actions:**")
                    
                    # Offer retry with reduced settings
                    if st.button("🔄 Retry with Safer Settings", key="retry_safer", help="Reduce sentences per word and try again"):
                        # Reduce sentences per word for retry
                        original_sentences = st.session_state.get('sentences_per_word', 10)
                        st.session_state['sentences_per_word'] = max(3, original_sentences // 2)
                        st.session_state['generation_progress'] = {
                            'step': 0, 'result': None, 'success': False, 'error': None, 'errors': [], 'error_summary': '',
                            'tsv_path': None, 'media_dir': None, 'output_dir': None, 'apkg_ready': False, 'apkg_path': None, 'partial_success': False
                        }
                        st.success("🔄 Retrying with reduced settings...")
                        time.sleep(1)
                        st.rerun()

                progress_bar.progress(1.0)
                current_status.markdown("⚠️ **Deck generation completed with issues**")
                step_indicator.markdown("⚠️ **Partial Success**")
                status_text.warning("⚠️ Deck generation completed with some issues")
                detail_text.markdown(f"*Errors encountered: {error_summary}*")

                progress['step'] = 2  # Move to completion
                st.session_state['generation_progress'] = progress
                st.rerun()

    elif step == 2:
        # Generation complete - show results and move to complete page
        progress = st.session_state.get('generation_progress', {})
        if progress is None:
            progress = {}
        
        result = progress.get('result', {})

        # Reset generating flag since generation is complete
        st.session_state.generating_deck = False

        if result and isinstance(result, dict) and result.get('success'):
            st.session_state.page = "complete"
            st.rerun()
        else:
            # Show error details and options
            error = progress.get('error', 'Unknown error')
            error_summary = progress.get('error_summary', '')

            status_text.error("❌ Deck generation encountered issues")
            detail_text.markdown(f"**Error:** {error}")

            if error_summary:
                with st.expander("📋 Detailed Error Report"):
                    st.markdown(error_summary)

            # Show download options for partial results
            if progress.get('apkg_ready'):
                st.success("📦 Despite errors, a partial deck was created and is available for download.")
                st.session_state.page = "complete"
                st.rerun()
            else:
                st.warning("❌ No usable deck could be created due to critical errors.")
                
                # Show log download option for debugging
                log_data = file_manager.get_log_file_data()
                if log_data:
                    st.markdown("### 📝 Download Generation Log for Debugging")
                    st.download_button(
                        label="⬇️ Download Error Log (TXT)",
                        data=log_data["data"],
                        file_name=log_data["filename"],
                        mime=log_data["mime_type"],
                        use_container_width=True,
                        key="error_log_download"
                    )

            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Try Again", use_container_width=True):
                    # Reset generation progress
                    st.session_state['generation_progress'] = {
                        'step': 0,
                        'result': None,
                        'success': False,
                        'error': None,
                        'errors': [],
                        'error_summary': '',
                        'tsv_path': None,
                        'media_dir': None,
                        'output_dir': None,
                        'apkg_ready': False,
                        'apkg_path': None,
                        'partial_success': False
                    }
                    st.session_state['output_dirs_cleared'] = False
                    st.rerun()

            with col2:
                if st.button("⬅️ Back to Settings", use_container_width=True):
                    st.session_state.page = "generate"
                    st.rerun()

    # Scroll to top after all content is rendered
    st.markdown("""
    <script>
        setTimeout(function() {
            window.scrollTo({top: 0, behavior: 'smooth'});
        }, 1000);
    </script>
    """, unsafe_allow_html=True)