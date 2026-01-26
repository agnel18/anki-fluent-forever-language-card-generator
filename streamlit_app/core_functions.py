"""
Core Functions Module

Central orchestrator with modular imports and fallbacks.
Imports functions from specialized modules while maintaining backward compatibility.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
import streamlit as st

# Setup logging
logger = logging.getLogger(__name__)

# ============================================================================
# MODULAR IMPORTS WITH FALLBACKS
# ============================================================================

# Import from sentence_generator module
try:
    from streamlit_app.sentence_generator import generate_sentences, generate_word_meaning
    logger.info("Successfully imported from sentence_generator")
except ImportError as e:
    logger.warning(f"Failed to import from sentence_generator: {e}. Using fallback implementations.")

# Import from audio_generator module
try:
    from streamlit_app.audio_generator import generate_audio_google as generate_audio, _voice_for_language, is_google_tts_configured
    logger.info("Successfully imported Google TTS from audio_generator")
except ImportError as e:
    logger.warning(f"Failed to import Google TTS from audio_generator: {e}. Using fallback implementations.")
    # Define fallback functions
    def generate_audio(sentences, voice, output_dir, **kwargs):
        """Fallback audio generation - returns empty list when audio is unavailable."""
        logger.warning("Audio generation not available - returning empty audio list")
        return []
    def _voice_for_language(language):
        """Fallback voice selection."""
        return "en-US-AriaNeural"

# Import from image_generator module
try:
    from streamlit_app.image_generator import generate_images_pixabay
    logger.info("Successfully imported Pixabay image generation from image_generator")
except ImportError as e:
    logger.warning(f"Failed to import Pixabay from image_generator: {e}. Using fallback implementations.")

# Import from deck_exporter module
try:
    from streamlit_app.deck_exporter import create_apkg_export
    logger.info("Successfully imported from deck_exporter")
except ImportError as e:
    logger.warning(f"Failed to import from deck_exporter: {e}. Using fallback implementations.")

# Import from generation_utils module
try:
    from streamlit_app.generation_utils import estimate_api_costs, parse_csv_upload, generate_image_keywords
    logger.info("Successfully imported from generation_utils")
except ImportError as e:
    logger.warning(f"Failed to import from generation_utils: {e}. Using fallback implementations.")

# Import grammar processor for sentence coloring
try:
    from streamlit_app.services.generation.grammar_processor import get_grammar_processor
    logger.info("Successfully imported grammar processor")
except ImportError as e:
    logger.warning(f"Failed to import grammar processor: {e}. Grammar analysis will be unavailable.")
    get_grammar_processor = None

# ============================================================================
# MAIN ORCHESTRATOR FUNCTION
# ============================================================================

def generate_complete_deck(
    words: list,
    language: str,
    gemini_api_key: str,
    google_custom_search_engine_id: str,
    output_dir: str,
    num_sentences: int = 10,
    min_length: int = 5,
    max_length: int = 20,
    difficulty: str = "intermediate",
    audio_speed: float = 0.8,
    voice: str = None,
    all_words: list = None,
    progress_callback: callable = None,
    topics: list = None,
    native_language: str = "English",
) -> dict:
    """
    Main orchestrator for deck generation. Returns dict with success, tsv_path, media_dir, output_dir, error.
    Implements comprehensive error recovery and graceful degradation.
    """
    try:
        # Generate unique ID for this deck generation to prevent filename conflicts
        deck_unique_id = _generate_unique_id()

        # Initialize error tracking
        errors = []
        partial_success = True

        # Create temp output dir if not exists
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        media_dir = output_path / "media"
        media_dir.mkdir(exist_ok=True)

        words_data = []
        audio_files = []
        image_files = []

        for idx, word in enumerate(words):
            if progress_callback:
                progress_callback(idx / max(1, len(words)), f"Generating for '{word}'", "Generating sentences...")

            try:
                # 1. Generate meaning + sentences + keywords (combined in one API call)
                meaning, sentences = generate_sentences(word, language, num_sentences, min_length, max_length, difficulty, gemini_api_key, topics, native_language)
                if sentences is None:
                    sentences = []
                if not sentences:
                    errors.append({
                        "component": f"Sentence generation for '{word}'",
                        "error": "Failed to generate sentences",
                        "critical": True
                    })
                    continue  # Skip this word entirely

                # 1.5. Analyze grammar and color sentences
                if get_grammar_processor:
                    try:
                        grammar_processor = get_grammar_processor()
                        # Get language code for analyzer
                        from language_registry import get_language_registry
                        registry = get_language_registry()
                        language_code = registry.get_iso_code(language)
                        
                        grammar_results = grammar_processor.batch_analyze_grammar_and_color(
                            sentences=[s['sentence'] for s in sentences],
                            target_words=[word] * len(sentences),
                            language=language,
                            gemini_api_key=gemini_api_key,
                            language_code=language_code
                        )
                        
                        # Update sentences with grammar analysis results
                        for i, result in enumerate(grammar_results):
                            sentences[i]['colored_sentence'] = result.get('colored_sentence', '')
                            sentences[i]['word_explanations'] = result.get('word_explanations', [])
                            sentences[i]['grammar_summary'] = result.get('grammar_summary', '')
                        
                        logger.info(f"Grammar analysis completed for {len(sentences)} sentences")
                    except Exception as e:
                        logger.warning(f"Grammar analysis failed for '{word}': {e}")
                        # Continue without grammar analysis
                else:
                    logger.info("Grammar processor not available, skipping grammar analysis")

                # 2. Generate audio (with graceful degradation)
                try:
                    v = voice or _voice_for_language(language)
                    audio_filenames = generate_audio([s['sentence'] for s in sentences], v, str(media_dir), batch_name=word, rate=audio_speed, unique_id=deck_unique_id)
                    audio_files.extend(audio_filenames)
                except Exception as e:
                    errors.append({
                        "component": f"Audio generation for '{word}'",
                        "error": f"Audio generation failed: {e}",
                        "critical": False
                    })
                    logger.warning(f"Continuing without audio for '{word}': {e}")
                    # Create empty audio filenames to maintain structure
                    audio_filenames = ["" for _ in sentences]

                # 3. Generate images (with graceful degradation)
                try:
                    # Extract keywords from sentences (already generated in combined first pass)
                    queries = [s.get('image_keywords', f"{word}, language, learning") for s in sentences]
                    
                    # Reset used_image_urls for each word to allow image reuse across different words
                    used_image_urls = set()
                    image_filenames, used_image_urls = generate_images_pixabay(
                        queries,
                        str(media_dir),
                        batch_name=word,
                        num_images=1,
                        pixabay_api_key=st.session_state.get('pixabay_api_key', ''),
                        used_image_urls=used_image_urls,  # Pass the word-specific set
                        unique_id=deck_unique_id,
                    )
                    image_files.extend(image_filenames)
                except Exception as e:
                    errors.append({
                        "component": f"Image generation for '{word}'",
                        "error": f"Image generation failed: {e}",
                        "critical": False
                    })
                    logger.warning(f"Continuing without images for '{word}': {e}")
                    # Create empty image filenames to maintain structure
                    image_filenames = ["" for _ in sentences]

                # 4. Build TSV rows
                for idx_sent, sent in enumerate(sentences):
                    file_base = f"{word}_{idx_sent+1:02d}_{deck_unique_id}"
                    _build_tsv_row(idx_sent, audio_filenames, image_filenames, sent, word, file_base, language, words_data)

            except Exception as e:
                errors.append({
                    "component": f"Processing word '{word}'",
                    "error": f"Unexpected error: {e}",
                    "critical": True
                })
                logger.error(f"Failed to process word '{word}': {e}")
                partial_success = False
                continue

        # 5. Create APKG
        apkg_path = output_path / f"{language.replace(' ', '_')}_deck.apkg"
        if not create_apkg_export(words_data, str(media_dir), str(apkg_path), language):
            errors.append({
                "component": "APKG creation",
                "error": "Failed to create APKG file",
                "critical": True
            })
            return {
                "success": False,
                "apkg_path": None,
                "media_dir": None,
                "output_dir": None,
                "error": "Failed to create APKG file",
                "errors": errors,
                "error_summary": _create_error_summary(errors),
                "partial_success": False
            }

        # Check for critical errors
        critical_errors = [e for e in errors if e.get('critical', False)]
        success = len(critical_errors) == 0

        result = {
            "success": success,
            "apkg_path": str(apkg_path),
            "media_dir": str(media_dir),
            "output_dir": str(output_path),
            "error": None if success else f"Completed with {len(critical_errors)} critical errors",
            "errors": errors,
            "error_summary": _create_error_summary(errors),
            "partial_success": partial_success
        }

        if errors:
            logger.warning(f"Deck generation completed with {len(errors)} issues: {_create_error_summary(errors)}")

        return result

    except Exception as e:
        logger.error(f"Complete deck generation error: {e}")
        return {
            "success": False,
            "apkg_path": None,
            "media_dir": None,
            "output_dir": None,
            "error": str(e),
            "errors": [{"component": "General", "error": str(e), "critical": True}],
            "error_summary": f"Critical error: {e}",
            "partial_success": False
        }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _generate_unique_id() -> str:
    """Generate a unique identifier for filenames to prevent overwrites."""
    import datetime
    import threading

    # Use thread-safe counter to ensure uniqueness even within same millisecond
    if not hasattr(_generate_unique_id, '_counter'):
        _generate_unique_id._counter = 0
        _generate_unique_id._lock = threading.Lock()

    with _generate_unique_id._lock:
        _generate_unique_id._counter += 1
        counter = _generate_unique_id._counter

    # Use timestamp format: YYYYMMDD_HHMMSS_MMM_CCC (includes milliseconds and counter)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Keep only first 3 digits of microseconds
    return f"{timestamp}_{counter:03d}"

def _create_unique_filename(base_name: str, extension: str = "", unique_id: str = None) -> str:
    """Create a unique filename with optional extension."""
    if unique_id is None:
        unique_id = _generate_unique_id()
    if extension:
        return f"{base_name}_{unique_id}.{extension}"
    else:
        return f"{base_name}_{unique_id}"

def _build_tsv_row(idx_sent, audio_files, image_files, sent, word, file_base, language, words_data):
    """Build a single TSV row for the Anki deck."""
    audio_name = audio_files[idx_sent] if idx_sent < len(audio_files) else ""
    image_name = image_files[idx_sent] if idx_sent < len(image_files) else ""

    # Generate IPA with hybrid approach
    ai_ipa = sent.get("ipa", "")
    final_ipa = generate_ipa_hybrid(
        text=sent.get("sentence", ""),
        language=language,
        ai_ipa=ai_ipa
    )

    def safe_str(val):
        if val is None:
            return ""
        if isinstance(val, float):
            import pandas as pd
            if pd.isna(val):
                return ""
            return str(val)
        return str(val)

    # Format word explanations as HTML
    word_explanations_html = ""
    explanations = sent.get("word_explanations", [])
    if explanations and len(explanations) > 0:
        explanation_items = []
        for exp in explanations:
            if len(exp) >= 4:
                exp_word, pos, color, explanation = exp[0], exp[1], exp[2], exp[3]  # Use exp_word to avoid shadowing
                explanation_items.append(f'<div class="explanation-item"><span class="word-highlight" style="color: {color};"><strong>{exp_word}</strong></span> ({pos}): {explanation}</div>')
        if explanation_items:
            word_explanations_html = '<div class="word-explanations"><strong>Grammar Explanations:</strong><br>' + ''.join(explanation_items) + '</div>'

    words_data.append({
        "file_name": safe_str(file_base),
        "word": safe_str(word),
        "meaning": safe_str(sent.get("meaning", word)),
        "sentence": safe_str(sent.get("sentence", "")),
        "ipa": safe_str(final_ipa),
        "english": safe_str(sent.get("english_translation", "")),
        "audio": safe_str(f"[sound:{audio_name}]" if audio_name else ""),
        "image": safe_str(f'<img src="{image_name}">') if image_name else "",
        "image_keywords": safe_str(sent.get("image_keywords", "")),
        "colored_sentence": safe_str(sent.get("colored_sentence", sent.get("sentence", ""))),
        "word_explanations": word_explanations_html,  # Now formatted as HTML string
        "grammar_summary": safe_str(sent.get("grammar_summary", "")),
        "tags": "",
    })


def _create_error_summary(errors):
    """Create a human-readable summary of errors."""
    if not errors:
        return "No errors"

    critical = [e for e in errors if e.get('critical', False)]
    non_critical = [e for e in errors if not e.get('critical', False)]

    summary = []
    if critical:
        summary.append(f"{len(critical)} critical error(s)")
    if non_critical:
        summary.append(f"{len(non_critical)} non-critical issue(s)")

    return ", ".join(summary)


def generate_deck_progressive(
    word: str,
    language: str,
    gemini_api_key: str,
    google_custom_search_engine_id: str,
    output_dir: str,
    num_sentences: int = 10,
    min_length: int = 5,
    max_length: int = 20,
    difficulty: str = "intermediate",
    audio_speed: float = 0.8,
    voice: str = None,
    topics: list = None,
    native_language: str = "English",
    log_callback: callable = None,
    enriched_word_data: dict = None,
) -> dict:
    """
    Generate deck for a single word with detailed progress callbacks.
    Returns word data dict with all components for that word.
    """
    try:
        errors = []

        # Generate unique ID for this word generation to prevent filename conflicts
        word_unique_id = _generate_unique_id()

        # Create output directories
        output_path = Path(output_dir)
        media_dir = output_path / "media"
        media_dir.mkdir(parents=True, exist_ok=True)

        # PASS 1: Smart Sentences
        if log_callback:
            log_callback(f"<b>🔤 PASS 1/6: Smart Sentences</b>")
            log_callback(f"Generating contextual sentences with pronunciation and visual cues for '{word}'...")

        # Extract consolidated meaning string from enriched word data
        consolidated_meaning = None
        if enriched_word_data:
            if isinstance(enriched_word_data, str):
                # New consolidated string format - use directly
                consolidated_meaning = enriched_word_data
            elif isinstance(enriched_word_data, dict):
                # Legacy dictionary format - extract meaning field
                consolidated_meaning = enriched_word_data.get('meaning', None)

        meaning, sentences = generate_sentences(word, language, num_sentences, min_length, max_length, difficulty, gemini_api_key, topics, native_language, consolidated_meaning)
        if sentences is None or not sentences:
            raise Exception(f"Failed to generate sentences for '{word}'")

        if log_callback:
            log_callback(f"✅ Generated {len(sentences)} sentences for '{word}'")

        # PASS 2: Quality Validation
        if log_callback:
            log_callback(f"<b>✅ PASS 2/6: Quality Validation</b>")
            log_callback(f"Ensuring natural speech patterns and adding translations for '{word}'...")

        # Quality validation is handled within generate_sentences
        if log_callback:
            log_callback(f"✅ Quality validation completed for '{word}'")

        # PASS 3: Grammar Analysis
        if log_callback:
            log_callback(f"<b>🎨 PASS 3/6: Grammar Analysis</b>")
            log_callback(f"Breaking down sentence structure with grammar analysis for '{word}'...")

        # Grammar analysis using the grammar processor
        logger.info(f"Starting grammar analysis for '{word}' in {language}")
        if get_grammar_processor:
            logger.info("get_grammar_processor is available")
            try:
                grammar_processor = get_grammar_processor()
                logger.info("Got grammar processor instance")
                # Get language code for analyzer
                from language_registry import get_language_registry
                registry = get_language_registry()
                language_code = registry.get_iso_code(language)
                logger.info(f"Language code for {language}: {language_code}")
                
                grammar_results = grammar_processor.batch_analyze_grammar_and_color(
                    sentences=[s['sentence'] for s in sentences],
                    target_words=[word] * len(sentences),
                    language=language,
                    gemini_api_key=gemini_api_key,
                    language_code=language_code
                )
                
                # Update sentences with grammar analysis results
                for i, result in enumerate(grammar_results):
                    sentences[i]['colored_sentence'] = result.get('colored_sentence', '')
                    sentences[i]['word_explanations'] = result.get('word_explanations', [])
                    sentences[i]['grammar_summary'] = result.get('grammar_summary', '')
                
                if log_callback:
                    log_callback(f"✅ Grammar analysis completed for {len(sentences)} sentences")
                logger.info(f"Grammar analysis completed successfully for {len(sentences)} sentences")
            except Exception as e:
                logger.error(f"Grammar analysis failed for '{word}': {e}")
                if log_callback:
                    log_callback(f"⚠️ Grammar analysis failed for '{word}': {e}")
                # Continue without grammar analysis
        else:
            logger.warning("get_grammar_processor is None")
            if log_callback:
                log_callback("ℹ️ Grammar processor not available, skipping grammar analysis")

        # Ensure all sentences have colored_sentence (fallback to basic highlighting)
        for i in range(len(sentences)):
            if 'colored_sentence' not in sentences[i] or not sentences[i]['colored_sentence']:
                # Basic fallback: highlight target word in red
                sentence = sentences[i]['sentence']
                words = sentence.split()
                colored_words = []
                for w in words:
                    if w.lower().strip('.,!?;:"\'') == word.lower():
                        colored_words.append(f"<span style='color: #FF6B6B; font-weight: bold;'>{w}</span>")
                    else:
                        colored_words.append(w)
                sentences[i]['colored_sentence'] = ' '.join(colored_words)
            if 'word_explanations' not in sentences[i]:
                sentences[i]['word_explanations'] = []
            if 'grammar_summary' not in sentences[i]:
                sentences[i]['grammar_summary'] = ''

        # PASS 4: Audio Generation
        if log_callback:
            log_callback(f"<b>🔊 PASS 4/6: Audio Generation</b>")
            log_callback(f"Creating natural-sounding pronunciations with {audio_speed}x speed for '{word}'...")

        v = voice or _voice_for_language(language)
        audio_filenames = generate_audio([s['sentence'] for s in sentences], v, str(media_dir), batch_name=word, rate=audio_speed, unique_id=word_unique_id)

        if log_callback:
            log_callback(f"✅ Generated {len(audio_filenames)} audio files for '{word}'")

        # PASS 5: Visual Media
        if log_callback:
            log_callback(f"<b>🖼️ PASS 5/6: Visual Media</b>")
            log_callback(f"Finding and downloading images from Pixabay for memory reinforcement for '{word}'...")

        queries = [s.get('image_keywords', f"{word}, language, learning") for s in sentences]
        used_image_urls = set()
        
        # Generate images using Pixabay (always free tier)
        try:
            # Get Pixabay API key (required)
            pixabay_api_key = st.session_state.get('pixabay_api_key', None)
            if not pixabay_api_key:
                raise ValueError("Pixabay API key is required for image generation")

            image_filenames, used_image_urls = generate_images_pixabay(
                queries, str(media_dir), batch_name=word,
                num_images=1, pixabay_api_key=pixabay_api_key, used_image_urls=used_image_urls, unique_id=word_unique_id
            )
            if log_callback:
                log_callback(f"✅ Downloaded {len(image_filenames)} images from Pixabay for '{word}'")
        except Exception as e:
            logger.warning(f"Image generation failed for '{word}': {e}")
            image_filenames = []
            if log_callback:
                log_callback(f"⚠️ Image generation failed for '{word}': {e}")

        # PASS 6: Word Assembly
        if log_callback:
            log_callback(f"<b>📦 PASS 6/6: Word Assembly</b>")
            log_callback(f"Combining all components into final word data for '{word}'...")

        word_data = {
            'word': word,
            'meaning': meaning,
            'sentences': sentences,
            'audio_files': audio_filenames,
            'image_files': image_filenames,
            'unique_id': word_unique_id  # Store unique ID for consistent filenames
        }

        if log_callback:
            log_callback(f"✅ Word '{word}' assembly completed - {len(sentences)} sentences, {len(audio_filenames)} audio files, {len(image_filenames)} images")

        return {
            'success': True,
            'word_data': word_data,
            'audio_files': audio_filenames,
            'image_files': image_filenames,
            'errors': errors
        }

    except Exception as e:
        error_msg = f"Failed to process word '{word}': {e}"
        logger.error(error_msg)
        return {
            'success': False,
            'word_data': {
                'word': word,
                'meaning': '',
                'sentences': [],
                'audio_files': ["" for _ in range(num_sentences)],
                'image_files': ["" for _ in range(num_sentences)],
                'unique_id': word_unique_id  # Include unique ID even in error case
            },
            'audio_files': [],
            'image_files': [],
            'errors': [{'error': str(e)}]
        }


def create_apkg_from_word_data(
    words_data: list,
    media_dir: str,
    output_apkg_path: str,
    language: str,
    deck_name: str = None
) -> bool:
    """
    Convert word data to card format and create APKG file.
    """
    try:
        # Set default deck name to language if not provided
        if deck_name is None:
            deck_name = language
        # Convert word data to card data format
        cards_data = []
        for word_data in words_data:
            word = word_data['word']
            meaning = word_data['meaning']
            sentences = word_data['sentences']
            audio_files = word_data['audio_files']
            image_files = word_data['image_files']
            unique_id = word_data.get('unique_id', '')  # Get unique ID if available

            for idx_sent, sent in enumerate(sentences):
                file_base = f"{word}_{idx_sent+1:02d}"
                if unique_id:
                    file_base = f"{file_base}_{unique_id}"  # Add unique ID if available
                audio_name = audio_files[idx_sent] if idx_sent < len(audio_files) else ""
                image_name = image_files[idx_sent] if idx_sent < len(image_files) else ""

                # Generate IPA (simplified)
                final_ipa = sent.get("ipa", "")

                # Format word explanations as HTML
                word_explanations_html = ""
                explanations = sent.get("word_explanations", [])
                if explanations and len(explanations) > 0:
                    explanation_items = []
                    for exp in explanations:
                        if len(exp) >= 4:
                            exp_word, pos, color, explanation = exp[0], exp[1], exp[2], exp[3]  # Use exp_word to avoid shadowing
                            explanation_items.append(f'<div class="explanation-item"><span class="word-highlight" style="color: {color};"><strong>{exp_word}</strong></span> ({pos}): {explanation}</div>')
                    if explanation_items:
                        word_explanations_html = '<div class="word-explanations"><strong>Grammar Explanations:</strong><br>' + ''.join(explanation_items) + '</div>'

                cards_data.append({
                    "file_name": file_base,
                    "word": word,
                    "meaning": meaning,
                    "sentence": sent.get("sentence", ""),
                    "ipa": final_ipa,
                    "english": sent.get("english_translation", ""),
                    "audio": f"[sound:{audio_name}]" if audio_name else "",
                    "image": f'<img src="{image_name}">' if image_name else "",
                    "image_keywords": sent.get("image_keywords", ""),
                    "colored_sentence": sent.get("colored_sentence", sent.get("sentence", "")),
                    "word_explanations": word_explanations_html,
                    "grammar_summary": sent.get("grammar_summary", ""),
                    "tags": "",
                })

        # Create the APKG file
        return create_apkg_export(
            cards_data,
            media_dir,
            output_apkg_path,
            language,
            deck_name
        )

    except Exception as e:
        logger.error(f"Error creating APKG from word data: {e}")
        return False


def generate_ipa_hybrid(text: str, language: str, ai_ipa: str = "") -> str:
    """Generate IPA using hybrid approach (AI + fallback)."""
    return ai_ipa or ""


# ============================================================================
# LEGACY COMPATIBILITY
# ============================================================================

# For backward compatibility, expose all functions at module level
__all__ = [
    # Main orchestrators
    'generate_complete_deck',
    'generate_deck_progressive',
    'create_apkg_from_word_data',
    # Sentence generation
    'generate_sentences', 'generate_word_meaning',
    # Audio generation
    'generate_audio', '_voice_for_language',
    # Image generation
    'generate_images_pixabay',
    # Deck export
    'create_anki_tsv', 'create_apkg_export',
    # Utilities
    'estimate_api_costs', 'parse_csv_upload'
]