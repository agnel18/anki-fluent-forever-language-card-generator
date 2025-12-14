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
        
        # Create summary columns
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📝 **Language & Words**")
            st.info(f"**Language:** {selected_lang}")
            st.info(f"**Words Selected:** {len(selected_words)}")
            if selected_words:
                # Show first few words as preview
                preview_words = selected_words[:5] if len(selected_words) > 5 else selected_words
                preview_text = ", ".join(preview_words)
                if len(selected_words) > 5:
                    preview_text += f" ... (+{len(selected_words) - 5} more)"
                st.caption(f"Preview: {preview_text}")
            
            st.markdown("### ⚙️ **Sentence Settings**")
            st.info(f"**Sentences per Word:** {num_sentences}")
            st.info(f"**Sentence Length:** {min_length}-{max_length} words")
            st.info(f"**Difficulty:** {difficulty.capitalize()}")
        
        with col2:
            st.markdown("### 🔊 **Audio Settings**")
            st.info(f"**Voice:** {voice}")
            st.info(f"**Speed:** {audio_speed}x")
            
            st.markdown("### 🎯 **Topics**")
            if enable_topics and selected_topics:
                st.info(f"**Topics Enabled:** {len(selected_topics)} selected")
                # Show selected topics
                topics_text = ", ".join(selected_topics)
                if len(topics_text) > 100:
                    topics_text = topics_text[:97] + "..."
                st.caption(f"Selected: {topics_text}")
            else:
                st.info("**Topics:** Disabled (general vocabulary)")
        
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
            st.markdown('<div style="background:#23272e;color:#f3f6fa;font-family:monospace,monospace;font-size:16px;padding:10px 14px;max-height:300px;overflow-y:auto;border-radius:8px;border:1px solid #30363d;">'+"<br>".join(st.session_state['generation_log'])+"</div>", unsafe_allow_html=True)
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
            except Exception as e:
                log_message_local(f"<b>⚠️ Could not clear media directory:</b> {e}")

        images_dir = str(Path(output_dir) / "images")
        if os.path.exists(images_dir):
            try:
                shutil.rmtree(images_dir)
                log_message_local(f"<b>🧹 Cleared existing images directory:</b> {images_dir}")
            except Exception as e:
                log_message_local(f"<b>⚠️ Could not clear images directory:</b> {e}")

        st.session_state['output_dirs_cleared'] = True

    # Generation logic with comprehensive error recovery
    step = st.session_state['generation_progress']['step']

    if step == 0:
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
            # Progress callback for UI updates
            def progress_callback(progress_pct, current_word, status):
                progress_bar.progress(progress_pct)
                detail_text.markdown(f"*{status}*")
                status_text.info(f"⚙️ {current_word}: {status}")

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

            if result.get('success'):
                log_message_local("<b>✅ Deck generation completed successfully!</b>")
                progress_bar.progress(1.0)
                current_status.markdown("🎉 **Deck generation completed!**")
                step_indicator.markdown("✅ **Success!**")
                status_text.success("🎉 Deck generation completed successfully!")
                detail_text.markdown("*Your Anki deck is ready. Moving to export...*")

                # Create APKG file
                try:
                    apkg_path = create_apkg_export(
                        deck_name=f"{selected_lang} Learning Deck",
                        tsv_path=result['tsv_path'],
                        media_dir=result['media_dir'],
                        output_dir=result['output_dir']
                    )
                    progress['apkg_path'] = apkg_path
                    progress['apkg_ready'] = True
                    log_message_local(f"<b>📦 APKG file created:</b> {apkg_path}")
                    
                    # Read APKG file and store in session state for download
                    if apkg_path and os.path.exists(apkg_path):
                        with open(apkg_path, 'rb') as f:
                            st.session_state.apkg_file = f.read()
                        st.session_state.apkg_filename = f"{selected_lang.replace(' ', '_')}_deck.apkg"
                        log_message_local(f"<b>📁 APKG file loaded for download:</b> {len(st.session_state.apkg_file)} bytes")
                    else:
                        log_message_local(f"<b>⚠️ APKG file not found at path:</b> {apkg_path}")
                        progress['apkg_ready'] = False
                        
                except Exception as e:
                    log_message_local(f"<b>⚠️ APKG creation failed:</b> {e}")
                    progress['apkg_ready'] = False

                progress['step'] = 2  # Move to completion
                st.session_state['generation_progress'] = progress
                st.rerun()

            else:
                # Handle errors
                error_msg = result.get('error', 'Unknown error occurred')
                error_summary = result.get('error_summary', '')

                log_message_local(f"<b>❌ Deck generation completed with errors:</b> {error_msg}")
                if error_summary:
                    log_message_local(f"<b>Error Details:</b><br>{error_summary.replace(chr(10), '<br>')}")

                progress_bar.progress(1.0)
                current_status.markdown("⚠️ **Deck generation completed with issues**")
                step_indicator.markdown("⚠️ **Partial Success**")
                status_text.warning("⚠️ Deck generation completed with some issues")
                detail_text.markdown(f"*Errors encountered: {error_summary}*")

                # Still try to create APKG if we have partial results
                if result.get('tsv_path') and result.get('partial_success'):
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
                        detail_text.markdown("*Despite errors, a partial deck was created and is available for download.*")
                        
                        # Read APKG file and store in session state for download
                        if apkg_path and os.path.exists(apkg_path):
                            with open(apkg_path, 'rb') as f:
                                st.session_state.apkg_file = f.read()
                            st.session_state.apkg_filename = f"{selected_lang.replace(' ', '_')}_deck_partial.apkg"
                            log_message_local(f"<b>📁 Partial APKG file loaded for download:</b> {len(st.session_state.apkg_file)} bytes")
                        else:
                            log_message_local(f"<b>⚠️ Partial APKG file not found at path:</b> {apkg_path}")
                            progress['apkg_ready'] = False
                            
                    except Exception as e:
                        log_message_local(f"<b>❌ APKG creation also failed:</b> {e}")
                        progress['apkg_ready'] = False
                else:
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
            st.rerun()

    elif step == 2:
        # Generation complete - show results and move to complete page
        result = st.session_state['generation_progress'].get('result', {})

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