# pages/generating.py - Deck generation page for the language learning app

import streamlit as st
import shutil
import os
import tempfile
import datetime
import time
import re
from pathlib import Path
from utils import get_secret, log_message
from core_functions import generate_complete_deck


def render_generating_page():
    """Render the deck generation page with comprehensive error recovery."""
    
    st.markdown("# ⚙️ Generating Your Deck")

    # Safety check: ensure required session state exists
    try:
        # Ensure st.session_state is a dict-like object
        if not hasattr(st.session_state, 'get'):
            st.error("❌ **Session state corrupted!** Please restart the application.")
            return
            
        required_vars = [
            'selected_lang', 'selected_words', 'sentences_per_word', 
            'sentence_length_range', 'difficulty', 'audio_speed', 'selected_voice'
        ]
        
        missing_vars = []
        for var in required_vars:
            try:
                if var not in st.session_state:
                    missing_vars.append(var)
            except (TypeError, AttributeError) as e:
                st.error(f"❌ **Session state access error for {var}:** {str(e)}")
                return
        
        if missing_vars:
            st.error("❌ **Missing required data!** Please complete the setup process first.")
            st.markdown(f"**Missing:** {', '.join(missing_vars)}")
            st.markdown("**Required:** Language selection, word selection, and sentence settings must be completed first.")
            if st.button("← Go Back to Setup", type="primary"):
                st.switch_page("pages/language_select.py")
            return
    except Exception as e:
        st.error(f"❌ **Critical session state error:** {str(e)}")
        st.error("Please restart the application and complete the setup process.")
        return
    
    selected_lang = st.session_state.selected_lang
    selected_words = st.session_state.selected_words
    
    # Get topics settings (needed throughout the function)
    enable_topics = st.session_state.get("enable_topics", False)
    selected_topics = st.session_state.get("selected_topics", [])
    
    st.markdown(f"**Language:** {selected_lang} | **Words:** {len(selected_words)}")
    st.divider()

    # Initialize generation progress if not exists
    if 'generation_progress' not in st.session_state:
        st.session_state['generation_progress'] = {
            'step': 0,  # 0: not started, 1: generating, 2: complete
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

    step = st.session_state['generation_progress']['step']

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
        
        # Get all parameters for display
        num_sentences = st.session_state.sentences_per_word
        min_length, max_length = st.session_state.sentence_length_range
        difficulty = st.session_state.difficulty
        audio_speed = st.session_state.audio_speed
        voice = st.session_state.selected_voice
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

    # Initialize logging (persistent to ./logs/) - moved up so logs show during generation
    if 'generation_log' not in st.session_state:
        st.session_state['generation_log'] = []
        st.session_state['generation_log_active'] = True
        
        # Create logs directory if it doesn't exist
        logs_dir = Path("./logs")
        logs_dir.mkdir(exist_ok=True)
        
        # Create persistent log file with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"generation_{timestamp}.log"
        log_filepath = logs_dir / log_filename
        
        st.session_state['log_file_path'] = str(log_filepath)
        st.session_state['log_stream'] = open(log_filepath, "w+", encoding="utf-8")
        
        log_message_local(f"<b>📝 Generation log started:</b> {log_filename}")
        log_message(f"[LOG] Generation log started: {log_filename}")

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

        # Display initial log content
        if st.session_state.get('generation_logs'):
            log_display.code(st.session_state['generation_logs'], language=None)
        else:
            log_display.code("Generation logs will appear here...", language=None)

    # Helper to log and update UI (defined after UI elements so it can access log_display)
    def log_message_local(msg):
        st.session_state['generation_log'].append(msg)
        # Write to persistent log file
        st.session_state['log_stream'].write(msg + '\n')
        st.session_state['log_stream'].flush()
        
        # Also update the UI display logs
        if 'generation_logs' not in st.session_state:
            st.session_state['generation_logs'] = ""
        
        # Clean HTML tags for display and add timestamp
        clean_msg = re.sub(r'<[^>]+>', '', msg)  # Remove HTML tags
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        st.session_state['generation_logs'] += f"[{timestamp}] {clean_msg}\n"
        
        # Update the display
        log_display.code(st.session_state['generation_logs'], language=None)

    # Get generation parameters
    groq_api_key = st.session_state.get('groq_api_key', get_secret('GROQ_API_KEY', ''))
    pixabay_api_key = st.session_state.get('pixabay_api_key', get_secret('PIXABAY_API_KEY', ''))
    num_sentences = st.session_state.sentences_per_word
    min_length, max_length = st.session_state.sentence_length_range
    difficulty = st.session_state.difficulty
    audio_speed = st.session_state.audio_speed
    voice = st.session_state.selected_voice
    output_dir = str(Path("./output"))

    # Clear output directories at start
    if 'output_dirs_cleared' not in st.session_state:
        media_dir = str(Path(output_dir) / "media")
        if os.path.exists(media_dir):
            try:
                shutil.rmtree(media_dir)
                log_message_local(f"<b>🧹 Cleared existing media directory:</b> {media_dir}")
                log_message(f"[DEBUG] Cleared media directory: {media_dir}")
            except Exception as e:
                log_message_local(f"<b>⚠️ Could not clear media directory:</b> {e}")
                log_message(f"[WARNING] Could not clear media directory {media_dir}: {e}")

        images_dir = str(Path(output_dir) / "images")
        if os.path.exists(images_dir):
            try:
                shutil.rmtree(images_dir)
                log_message_local(f"<b>🧹 Cleared existing images directory:</b> {images_dir}")
                log_message(f"[DEBUG] Cleared images directory: {images_dir}")
            except Exception as e:
                log_message_local(f"<b>⚠️ Could not clear images directory:</b> {e}")
                log_message(f"[WARNING] Could not clear images directory {images_dir}: {e}")

        st.session_state['output_dirs_cleared'] = True
        log_message(f"[DEBUG] Output directories cleared. Media: {media_dir}, Images: {images_dir}")

    # Generation logic with comprehensive error recovery
    step = st.session_state['generation_progress']['step']

    if step == 0:
        # Clear previous generation log for fresh UI display with delay
        # (detailed log stream for export is preserved)
        if st.session_state.get('generation_log') and len(st.session_state['generation_log']) > 0:
            log_message_local("<b>🧹 Clearing previous log in 2 seconds...</b>")
            time.sleep(2)  # 2-second delay as requested
        
        # Clear the log completely for fresh start
        st.session_state['generation_log'] = []
        st.session_state['generation_logs'] = ""  # Clear the new logs accumulator
        
        # Start generation
        current_status.markdown("🚀 **Starting deck generation...**")
        step_indicator.markdown("⚙️ **Initializing**")
        log_message_local("<b>🚀 Starting comprehensive deck generation with error recovery...</b>")
        status_text.info("🚀 Initializing deck generation...")
        detail_text.markdown("*Setting up generation with comprehensive error recovery and graceful degradation...*")

        # Mark as started
        st.session_state['generation_progress']['step'] = 1
        st.rerun()

    # Check word limit before generation
    elif len(selected_words) > 5:
        current_status.markdown("⚠️ **Generation Limit Exceeded**")
        step_indicator.markdown("❌ **Too Many Words**")
        log_message_local("<b>❌ Generation cancelled - too many words selected</b>")
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
        # Perform generation using the resilient generate_complete_deck function
        current_status.markdown("⚙️ **Generating your complete deck...**")
        step_indicator.markdown("🔄 **Processing**")
        log_message_local("<b>⚙️ Running comprehensive deck generation...</b>")
        status_text.info("⚙️ Generating your complete deck...")
        detail_text.markdown("*This process includes error recovery - if any component fails, we'll continue with the rest...*")

        try:
            # Progress callback for UI updates and detailed logging
            def progress_callback(progress_pct, current_word, status):
                # Update progress bar based on pass
                pass_progress = {
                    "PASS 1": 16.67,
                    "PASS 2": 33.33,
                    "PASS 3": 50.0,
                    "PASS 4": 66.67,
                    "PASS 5": 83.33,
                    "PASS 6": 100.0
                }
                for pass_name, pct in pass_progress.items():
                    if pass_name in status:
                        progress_bar.progress(pct)
                        break
                else:
                    progress_bar.progress(progress_pct)  # fallback to original
                
                # Update pass indicator
                import re
                pass_match = re.search(r'PASS (\d+)', status)
                if pass_match:
                    pass_num = pass_match.group(1)
                    pass_indicator.markdown(f"**Current Pass:** {pass_num}/6")
                
                detail_text.markdown(f"*{status}*")
                status_text.info(f"⚙️ {current_word}: {status}")
                
                # Add detailed technical logs for debugging
                log_message_local(f"[DEBUG] Progress: {progress_pct:.1%} - Word: '{current_word}' - Status: {status}")
                log_message(f"[DEBUG] Progress: {progress_pct:.1%} - Word: '{current_word}' - Status: {status}")

            # Call the comprehensive generation function with error recovery
            # Initialize retry counter if not exists
            if 'generation_retry_count' not in st.session_state:
                st.session_state['generation_retry_count'] = 0
            
            retry_count = st.session_state['generation_retry_count']
            max_retries = 2  # Allow up to 2 automatic retries for temporary failures
            
            log_message_local(f"[DEBUG] Starting generate_complete_deck with params:")
            log_message_local(f"[DEBUG] - Words: {selected_words}")
            log_message_local(f"[DEBUG] - Language: {selected_lang}")
            log_message_local(f"[DEBUG] - Output dir: {output_dir}")
            log_message_local(f"[DEBUG] - Sentences per word: {num_sentences}")
            log_message_local(f"[DEBUG] - Sentence length range: {min_length}-{max_length}")
            log_message_local(f"[DEBUG] - Difficulty: {difficulty}")
            log_message_local(f"[DEBUG] - Audio speed: {audio_speed}")
            log_message_local(f"[DEBUG] - Voice: {voice}")
            log_message_local(f"[DEBUG] - API keys present: Groq={bool(groq_api_key)}, Pixabay={bool(pixabay_api_key)}")
            log_message_local(f"[DEBUG] - Retry attempt: {retry_count + 1}/{max_retries + 1}")
            
            log_message(f"[DEBUG] Starting generate_complete_deck with {len(selected_words)} words")
            log_message(f"[DEBUG] Language: {selected_lang}, Output dir: {output_dir}")
            log_message(f"[DEBUG] API keys configured: Groq={'YES' if groq_api_key else 'NO'}, Pixabay={'YES' if pixabay_api_key else 'NO'}")
            log_message(f"[DEBUG] Retry attempt: {retry_count + 1}/{max_retries + 1}")
            
            # Define progress callback for real-time updates
            def progress_callback(progress, status, detail):
                """Update UI with real-time progress information."""
                # Update progress bar
                progress_pct = int(progress * 100)
                progress_bar.progress(progress_pct / 100)
                
                # Update status text
                current_status.markdown(f"**{status}**")
                
                # Update detail text
                if detail:
                    detail_text.markdown(f"*{detail}*")
                
                # Update pass indicator
                if 'PASS' in status:
                    try:
                        pass_num = int(re.search(r'PASS (\d+)', status).group(1))
                        pass_indicator.markdown(f"**Pass {pass_num}/6**")
                    except:
                        pass
                
                # Accumulate logs
                if 'generation_logs' not in st.session_state:
                    st.session_state['generation_logs'] = ""
                
                timestamp = datetime.datetime.now().strftime('%H:%M:%S')
                st.session_state['generation_logs'] += f"[{timestamp}] {status}\n"
                if detail:
                    st.session_state['generation_logs'] += f"  └─ {detail}\n"
                
                # Update log display in real-time using the empty placeholder
                log_display.code(st.session_state['generation_logs'], language=None)
            
            # Call the comprehensive generation function with error recovery
            result = generate_complete_deck(
                words=selected_words,
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
                progress_callback=progress_callback,
                topics=selected_topics if enable_topics else None,
                native_language="English",  # Default to English, will be configurable later
            )

            # Safety check: ensure result is not None
            if result is None:
                log_message_local("<b>❌ CRITICAL ERROR: generate_complete_deck() returned None</b>")
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
                    log_message_local(f"<b>🔄 Automatic retry #{retry_count + 1} due to temporary failure...</b>")
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
            log_message_local(f"[DEBUG] Generation result: success={result.get('success', False)}")
            log_message_local(f"[DEBUG] Result details: {result}")
            log_message(f"[DEBUG] Generation completed. Success: {result.get('success', False)}")
            log_message(f"[DEBUG] TSV path: {result.get('tsv_path')}")
            log_message(f"[DEBUG] Media dir: {result.get('media_dir')}")
            log_message(f"[DEBUG] Errors: {len(result.get('errors', []))}")

            if result.get('success'):
                log_message_local("<b>✅ Deck generation completed successfully!</b>")
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
                log_message_local("<b>📦 Using APKG file from generation...</b>")
                log_message("[DEBUG] Using APKG file from generate_complete_deck")
                
                try:
                    apkg_path = result.get('apkg_path')
                    if apkg_path and os.path.exists(apkg_path):
                        progress['apkg_path'] = apkg_path
                        progress['apkg_ready'] = True
                        
                        log_message(f"[DEBUG] APKG path from result: {apkg_path}")
                        log_message_local(f"<b>📦 APKG file found:</b> {apkg_path}")
                        
                        # Read APKG file and store in session state for download
                        with open(apkg_path, 'rb') as f:
                            st.session_state.apkg_file = f.read()
                        # Generate timestamp for unique filename
                        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                        st.session_state.apkg_filename = f"{selected_lang.replace(' ', '_')}_{timestamp}_deck.apkg"
                        log_message_local(f"<b>📁 APKG file loaded for download:</b> {len(st.session_state.apkg_file)} bytes")
                        log_message(f"[DEBUG] APKG file loaded: {len(st.session_state.apkg_file)} bytes, filename: {st.session_state.apkg_filename}")
                        
                        # Save deck metadata to Firebase (for logged-in users)
                        try:
                            from firebase_manager import is_signed_in
                            if is_signed_in():
                                deck_metadata = {
                                    'deck_name': f"{selected_lang} Learning Deck",
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
                                
                                log_message_local(f"<b>💾 Deck metadata saved to cloud</b>")
                                log_message(f"[DEBUG] Deck metadata saved for user {st.session_state.user['uid']}: {deck_metadata['deck_name']}")
                            else:
                                log_message(f"[DEBUG] User not signed in, skipping deck metadata save")
                        except Exception as e:
                            log_message_local(f"<b>⚠️ Could not save deck metadata:</b> {e}")
                            log_message(f"[WARNING] Failed to save deck metadata: {e}")
                        
                    else:
                        log_message_local(f"<b>⚠️ APKG file not found at path:</b> {apkg_path}")
                        log_message(f"[ERROR] APKG file not found at path: {apkg_path}")
                        progress['apkg_ready'] = False
                        
                except Exception as e:
                    log_message_local(f"<b>⚠️ Failed to load APKG file:</b> {e}")
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

                log_message_local(f"<b>❌ Deck generation completed with errors:</b> {error_msg}")
                log_message(f"[ERROR] Deck generation failed: {error_msg}")
                log_message(f"[ERROR] Error summary: {error_summary}")
                log_message(f"[ERROR] Total errors: {len(errors)}")
                
                if error_summary:
                    log_message_local(f"<b>Error Details:</b><br>{error_summary.replace(chr(10), '<br>')}")
                    log_message(f"[ERROR] Details: {error_summary}")
                
                # Log individual errors
                for i, error in enumerate(errors):
                    log_message(f"[ERROR #{i+1}] {error.get('component', 'Unknown')}: {error.get('error', 'Unknown error')}")
                    if error.get('critical'):
                        log_message(f"[CRITICAL] {error.get('component', 'Unknown')} failed critically")

                if error_summary:
                    log_message_local(f"<b>Error Details:</b><br>{error_summary.replace(chr(10), '<br>')}")

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

        except Exception as e:
            progress = st.session_state['generation_progress']
            progress['error'] = f"Unexpected error during generation: {e}"
            progress['step'] = 2  # Move to completion with error
            st.session_state['generation_progress'] = progress
            log_message_local(f"<b>💥 Critical error:</b> {e}")
            log_message(f"[CRITICAL] Unexpected error during generation: {e}")
            log_message(f"[CRITICAL] Error type: {type(e).__name__}")
            import traceback
            log_message(f"[CRITICAL] Traceback: {traceback.format_exc()}")
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
                if "log_file_path" in st.session_state and st.session_state['log_file_path'] and os.path.exists(st.session_state['log_file_path']):
                    st.markdown("### 📝 Download Generation Log for Debugging")
                    with open(st.session_state['log_file_path'], "rb") as f:
                        st.download_button(
                            label="⬇️ Download Error Log (TXT)",
                            data=f.read(),
                            file_name="generation_error_log.txt",
                            mime="text/plain",
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