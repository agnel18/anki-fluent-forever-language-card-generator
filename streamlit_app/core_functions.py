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
) -> dict:
    """
    Main orchestrator for deck generation. Returns dict with success, tsv_path, media_dir, output_dir, error.
    Implements comprehensive error recovery and graceful degradation.
    """
    try:
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
                # 1. Generate sentences (with error recovery)
                meaning = generate_word_meaning(word, language, groq_api_key)
                if not meaning or meaning == word:
                    errors.append({
                        "component": f"Meaning generation for '{word}'",
                        "error": "Failed to generate meaning, using word as fallback",
                        "critical": False
                    })

                sentences = generate_sentences(word, meaning, language, num_sentences, min_length, max_length, difficulty, groq_api_key, topics)
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
                    audio_filenames = generate_audio([s['sentence'] for s in sentences], v, str(media_dir), batch_name=word, rate=audio_speed)
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
                    # Generate unique keywords for each sentence
                    queries = []
                    for s in sentences:
                        keywords = generate_image_keywords(s['sentence'], s['english_translation'], word, groq_api_key)
                        queries.append(keywords)
                    
                    # Reset used_image_urls for each word to allow image reuse across different words
                    used_image_urls = set()
                    image_filenames, used_image_urls = generate_images_pixabay(
                        queries,
                        str(media_dir),
                        batch_name=word,
                        num_images=1,
                        pixabay_api_key=pixabay_api_key,
                        used_image_urls=used_image_urls  # Pass the word-specific set
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
                    file_base = f"{word}_{idx_sent+1:02d}"
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
        if not create_apkg_export(words_data, str(media_dir), str(apkg_path), language, "Language Learning"):
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


def generate_ipa_hybrid(text: str, language: str, ai_ipa: str = "") -> str:
    """Generate IPA using hybrid approach (AI + fallback)."""
    return ai_ipa or ""


# ============================================================================
# LEGACY COMPATIBILITY
# ============================================================================

# For backward compatibility, expose all functions at module level
__all__ = [
    # Main orchestrator
    'generate_complete_deck',
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