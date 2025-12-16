# pages/generating.py - Deck generation page for the language learning app

import streamlit as st
import shutil
import os
import tempfile
import datetime
from pathlib import Path
from utils import get_secret, log_message
from core_functions import generate_complete_deck, create_apkg_export


def render_generating_page():
    """Render the deck generation page with comprehensive error recovery."""

    # Add minimal CSS to ensure visibility without overriding theme
    st.markdown("""
    <style>
    /* Ensure log container is visible */
    .log-container {
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 8px;
        padding: 10px 14px;
        max-height: 400px;
        overflow-y: auto;
        font-family: monospace;
        font-size: 14px;
        margin: 10px 0;
        color: var(--text-color);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Force scroll to top when entering generating page
    st.markdown('<script>window.scrollTo({top: 0, behavior: "smooth"});</script>', unsafe_allow_html=True)

    st.markdown("# ⚙️ Generating Your Deck")
    st.markdown(f"**Language:** {st.session_state.selected_lang} | **Words:** {len(st.session_state.selected_words)}")
    st.divider()

    # --- Generation Summary ---
    with st.container():
        st.markdown("## 📋 Generation Summary")
        
        # Get all parameters for display
        selected_words = st.session_state.selected_words
        selected_lang = st.session_state.selected_lang
        num_sentences = st.session_state.sentences_per_word
        min_length, max_length = st.session_state.sentence_length_range
        difficulty = st.session_state.difficulty
        audio_speed = st.session_state.audio_speed
        voice = st.session_state.selected_voice
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

    # Enhanced progress display with animations
    progress_container = st.container()
    with progress_container:
        progress_bar = st.progress(0)
        status_text = st.empty()
        detail_text = st.empty()

        # Add animated status indicators
        status_col1, status_col2 = st.columns([3, 1])
        with status_col1:
            current_status = st.empty()
        with status_col2:
            step_indicator = st.empty()

        messages_container = st.container()

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

    # Initialize logging
    if 'generation_log' not in st.session_state:
        st.session_state['generation_log'] = []
        st.session_state['generation_log_active'] = True
        st.session_state['log_stream'] = tempfile.NamedTemporaryFile(delete=False, mode="w+", encoding="utf-8")
        st.session_state['log_file_path'] = None

    # Helper to log and update UI
    def log_message_local(msg):
        st.session_state['generation_log'].append(msg)
        with messages_container:
            st.markdown('<div class="log-container">'+"<br>".join(st.session_state['generation_log'])+"</div>", unsafe_allow_html=True)
        # Write to backend log stream for download
        st.session_state['log_stream'].write(msg + '\n')
        st.session_state['log_stream'].flush()
        # Update temp file for download
        st.session_state['log_stream'].seek(0)
        full_log = st.session_state['log_stream'].read()
        tmp_log = tempfile.NamedTemporaryFile(delete=False, suffix="_generation_log.txt", mode="w", encoding="utf-8")
        tmp_log.write(full_log)
        tmp_log.close()
        st.session_state['log_file_path'] = tmp_log.name

    # Get generation parameters
    selected_words = st.session_state.selected_words
    selected_lang = st.session_state.selected_lang
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
        # Clear previous generation log for fresh UI display
        # (detailed log stream for export is preserved)
        st.session_state['generation_log'] = []
        
        # Start generation
        current_status.markdown("🚀 **Starting deck generation...**")
        step_indicator.markdown("⚙️ **Initializing**")
        log_message_local("<b>🚀 Starting comprehensive deck generation with error recovery...</b>")
        status_text.info("🚀 Initializing deck generation...")
        detail_text.markdown("*Setting up generation with comprehensive error recovery and graceful degradation...*")

        # Mark as started
        st.session_state['generation_progress']['step'] = 1
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
                progress_bar.progress(progress_pct)
                detail_text.markdown(f"*{status}*")
                status_text.info(f"⚙️ {current_word}: {status}")
                
                # Add detailed technical logs for debugging
                log_message_local(f"[DEBUG] Progress: {progress_pct:.1%} - Word: '{current_word}' - Status: {status}")
                log_message(f"[DEBUG] Progress: {progress_pct:.1%} - Word: '{current_word}' - Status: {status}")

            # Call the comprehensive generation function with error recovery
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
            
            log_message(f"[DEBUG] Starting generate_complete_deck with {len(selected_words)} words")
            log_message(f"[DEBUG] Language: {selected_lang}, Output dir: {output_dir}")
            log_message(f"[DEBUG] API keys configured: Groq={'YES' if groq_api_key else 'NO'}, Pixabay={'YES' if pixabay_api_key else 'NO'}")
            
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
                progress_callback=progress_callback
            )

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

                # Create APKG file
                log_message_local("<b>📦 Creating APKG file...</b>")
                log_message("[DEBUG] Starting APKG creation")
                
                try:
                    apkg_path = create_apkg_export(
                        deck_name=f"{selected_lang} Learning Deck",
                        tsv_path=result['tsv_path'],
                        media_dir=result['media_dir'],
                        output_dir=result['output_dir']
                    )
                    progress['apkg_path'] = apkg_path
                    progress['apkg_ready'] = True
                    
                    log_message(f"[DEBUG] APKG creation result: {apkg_path}")
                    log_message_local(f"<b>📦 APKG file created:</b> {apkg_path}")
                    
                    # Read APKG file and store in session state for download
                    if apkg_path and os.path.exists(apkg_path):
                        with open(apkg_path, 'rb') as f:
                            st.session_state.apkg_file = f.read()
                        st.session_state.apkg_filename = f"{selected_lang.replace(' ', '_')}_deck.apkg"
                        log_message_local(f"<b>📁 APKG file loaded for download:</b> {len(st.session_state.apkg_file)} bytes")
                        log_message(f"[DEBUG] APKG file loaded: {len(st.session_state.apkg_file)} bytes, filename: {st.session_state.apkg_filename}")
                    else:
                        log_message_local(f"<b>⚠️ APKG file not found at path:</b> {apkg_path}")
                        log_message(f"[ERROR] APKG file not found at path: {apkg_path}")
                        progress['apkg_ready'] = False
                        
                except Exception as e:
                    log_message_local(f"<b>⚠️ APKG creation failed:</b> {e}")
                    log_message(f"[ERROR] APKG creation failed: {e}")
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

                progress_bar.progress(1.0)
                current_status.markdown("⚠️ **Deck generation completed with issues**")
                step_indicator.markdown("⚠️ **Partial Success**")
                status_text.warning("⚠️ Deck generation completed with some issues")
                detail_text.markdown(f"*Errors encountered: {error_summary}*")

                # Still try to create APKG if we have partial results
                if result.get('tsv_path') and result.get('partial_success'):
                    log_message("[DEBUG] Attempting partial APKG creation")
                    try:
                        apkg_path = create_apkg_export(
                            deck_name=f"{selected_lang} Learning Deck (Partial)",
                            tsv_path=result['tsv_path'],
                            media_dir=result['media_dir'],
                            output_dir=result['output_dir']
                        )
                        progress['apkg_path'] = apkg_path
                        progress['apkg_ready'] = True
                        log_message_local(f"<b>📦 Partial APKG file created:</b> {apkg_path}")
                        log_message(f"[SUCCESS] Partial APKG created: {apkg_path}")
                        detail_text.markdown("*Despite errors, a partial deck was created and is available for download.*")
                        
                        # Read APKG file and store in session state for download
                        if apkg_path and os.path.exists(apkg_path):
                            with open(apkg_path, 'rb') as f:
                                st.session_state.apkg_file = f.read()
                            st.session_state.apkg_filename = f"{selected_lang.replace(' ', '_')}_deck_partial.apkg"
                            log_message_local(f"<b>📁 Partial APKG file loaded for download:</b> {len(st.session_state.apkg_file)} bytes")
                            log_message(f"[DEBUG] Partial APKG loaded: {len(st.session_state.apkg_file)} bytes")
                        else:
                            log_message_local(f"<b>⚠️ Partial APKG file not found at path:</b> {apkg_path}")
                            log_message(f"[ERROR] Partial APKG not found: {apkg_path}")
                            progress['apkg_ready'] = False
                            
                    except Exception as e:
                        log_message_local(f"<b>❌ APKG creation also failed:</b> {e}")
                        log_message(f"[ERROR] Partial APKG creation failed: {e}")
                        progress['apkg_ready'] = False
                else:
                    log_message("[DEBUG] No partial success - skipping APKG creation")
                    progress['apkg_ready'] = False

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
        result = st.session_state['generation_progress'].get('result', {})

        # Reset generating flag since generation is complete
        st.session_state.generating_deck = False

        if result.get('success'):
            st.session_state.page = "complete"
            st.rerun()
        else:
            # Show error details and options
            error = st.session_state['generation_progress'].get('error', 'Unknown error')
            error_summary = st.session_state['generation_progress'].get('error_summary', '')

            status_text.error("❌ Deck generation encountered issues")
            detail_text.markdown(f"**Error:** {error}")

            if error_summary:
                with st.expander("📋 Detailed Error Report"):
                    st.markdown(error_summary)

            # Show download options for partial results
            if st.session_state['generation_progress'].get('apkg_ready'):
                st.success("📦 Despite errors, a partial deck was created and is available for download.")
                st.session_state.page = "complete"
                st.rerun()
            else:
                st.warning("❌ No usable deck could be created due to critical errors.")

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