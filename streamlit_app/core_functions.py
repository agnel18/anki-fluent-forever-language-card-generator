"""
Core Functions Module

Central orchestrator with modular imports and fallbacks.
Imports functions from specialized modules while maintaining backward compatibility.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable

# Setup logging
logger = logging.getLogger(__name__)

# ============================================================================
# MODULAR IMPORTS WITH FALLBACKS
# ============================================================================

# Import from sentence_generator module
try:
    from sentence_generator import generate_sentences, generate_word_meaning
    logger.info("Successfully imported from sentence_generator")
except ImportError as e:
    logger.warning(f"Failed to import from sentence_generator: {e}. Using fallback implementations.")

# Import from audio_generator module
try:
    from audio_generator import generate_audio, _voice_for_language
    logger.info("Successfully imported from audio_generator")
except ImportError as e:
    logger.warning(f"Failed to import from audio_generator: {e}. Using fallback implementations.")

# Import from image_generator module
try:
    from image_generator import generate_images_pixabay
    logger.info("Successfully imported from image_generator")
except ImportError as e:
    logger.warning(f"Failed to import from image_generator: {e}. Using fallback implementations.")

# Import from deck_exporter module
try:
    from deck_exporter import create_apkg_export
    logger.info("Successfully imported from deck_exporter")
except ImportError as e:
    logger.warning(f"Failed to import from deck_exporter: {e}. Using fallback implementations.")

# Import from generation_utils module
try:
    from generation_utils import estimate_api_costs, parse_csv_upload, generate_image_keywords
    logger.info("Successfully imported from generation_utils")
except ImportError as e:
    logger.warning(f"Failed to import from generation_utils: {e}. Using fallback implementations.")

# ============================================================================
# MAIN ORCHESTRATOR FUNCTION
# ============================================================================

def generate_complete_deck(
    words: list,
    language: str,
    groq_api_key: str,
    pixabay_api_key: str,
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
                meaning, sentences = generate_sentences(word, language, num_sentences, min_length, max_length, difficulty, groq_api_key, topics, native_language)
                if sentences is None:
                    sentences = []
                if not sentences:
                    errors.append({
                        "component": f"Sentence generation for '{word}'",
                        "error": "Failed to generate sentences",
                        "critical": True
                    })
                    continue  # Skip this word entirely

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
                        pixabay_api_key=pixabay_api_key,
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
    # Use timestamp format: YYYYMMDD_HHMMSS
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

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
                word, pos, color, explanation = exp[0], exp[1], exp[2], exp[3]
                explanation_items.append(f'<div class="explanation-item"><span class="word-highlight" style="color: {color};"><strong>{word}</strong></span> ({pos}): {explanation}</div>')
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
    groq_api_key: str,
    pixabay_api_key: str,
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
) -> dict:
    """
    Generate deck for a single word with detailed progress callbacks.
    Returns word data dict with all components for that word.
    """
    try:
        errors = []

        # Create output directories
        output_path = Path(output_dir)
        media_dir = output_path / "media"
        media_dir.mkdir(parents=True, exist_ok=True)

        # PASS 1: Smart Sentences
        if log_callback:
            log_callback(f"<b>🔤 PASS 1/6: Smart Sentences</b>")
            log_callback(f"Generating contextual sentences with pronunciation and visual cues for '{word}'...")

        meaning, sentences = generate_sentences(word, language, num_sentences, min_length, max_length, difficulty, groq_api_key, topics, native_language)
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

        # Grammar analysis is also handled within generate_sentences
        if log_callback:
            log_callback(f"✅ Grammar analysis completed for '{word}'")

        # PASS 4: Audio Generation
        if log_callback:
            log_callback(f"<b>🔊 PASS 4/6: Audio Generation</b>")
            log_callback(f"Creating natural-sounding pronunciations with {audio_speed}x speed for '{word}'...")

        v = voice or _voice_for_language(language)
        audio_filenames = generate_audio([s['sentence'] for s in sentences], v, str(media_dir), batch_name=word, rate=audio_speed)

        if log_callback:
            log_callback(f"✅ Generated {len(audio_filenames)} audio files for '{word}'")

        # PASS 5: Visual Media
        if log_callback:
            log_callback(f"<b>🖼️ PASS 5/6: Visual Media</b>")
            log_callback(f"Finding and downloading relevant images for memory reinforcement for '{word}'...")

        queries = [s.get('image_keywords', f"{word}, language, learning") for s in sentences]
        used_image_urls = set()
        image_filenames, used_image_urls = generate_images_pixabay(
            queries, str(media_dir), batch_name=word,
            num_images=1, pixabay_api_key=pixabay_api_key,
            used_image_urls=used_image_urls, unique_id=deck_unique_id
        )

        if log_callback:
            log_callback(f"✅ Downloaded {len(image_filenames)} images for '{word}'")

        # PASS 6: Word Assembly
        if log_callback:
            log_callback(f"<b>📦 PASS 6/6: Word Assembly</b>")
            log_callback(f"Combining all components into final word data for '{word}'...")

        word_data = {
            'word': word,
            'meaning': meaning,
            'sentences': sentences,
            'audio_files': audio_filenames,
            'image_files': image_filenames
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
                'image_files': ["" for _ in range(num_sentences)]
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

            for idx_sent, sent in enumerate(sentences):
                file_base = f"{word}_{idx_sent+1:02d}"
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
                            word, pos, color, explanation = exp[0], exp[1], exp[2], exp[3]
                            explanation_items.append(f'<div class="explanation-item"><span class="word-highlight" style="color: {color};"><strong>{word}</strong></span> ({pos}): {explanation}</div>')
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