# Generation Orchestrator Service
# Handles the high-level orchestration of deck generation process

import logging
import time
from typing import Dict, List, Any, Optional
import pathlib

# Remove the circular import - will import locally where needed
# from core_functions import generate_sentences
from deck_exporter import create_apkg_export
from .file_manager import FileManager
from .log_manager import LogManager

logger = logging.getLogger(__name__)


class GenerationOrchestrator:
    """
    Service for orchestrating the complete deck generation process.
    Coordinates between different passes and services for end-to-end generation.
    """

    def __init__(self, file_manager: FileManager, log_manager: LogManager):
        self.file_manager = file_manager
        self.log_manager = log_manager

    def generate_deck_progressive(
        self,
        selected_words: List[str],
        selected_lang: str,
        groq_api_key: str,
        pixabay_api_key: str,
        num_sentences: int,
        min_length: int,
        max_length: int,
        difficulty: str,
        audio_speed: float,
        voice: str,
        output_dir: str,
        enable_topics: bool = False,
        selected_topics: Optional[List[str]] = None,
        update_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Generate a complete Anki deck progressively with real-time updates.

        Args:
            selected_words: List of words to generate
            selected_lang: Target language
            groq_api_key: Groq API key
            pixabay_api_key: Pixabay API key
            num_sentences: Number of sentences per word
            min_length/max_length: Sentence length constraints
            difficulty: Learning difficulty level
            audio_speed: Audio playback speed
            voice: TTS voice selection
            output_dir: Output directory path
            enable_topics: Whether to use topic-focused generation
            selected_topics: List of topics for focused generation
            update_callback: Callback function for real-time UI updates

        Returns:
            Dict with generation results
        """
        results = {
            'words_data': [],
            'audio_files': [],
            'image_files': [],
            'errors': [],
            'partial_success': True,
            'pass1_results': []
        }

        # Process each word individually for real-time updates
        for word_idx, word in enumerate(selected_words):
            try:
                self.log_manager.log_message(f"<b>🔄 Processing word {word_idx + 1}/{len(selected_words)}: '{word}'</b>")

                # Generate sentences for this word
                topics = selected_topics if enable_topics and selected_topics else None
                native_language = "English"  # Could be made configurable

                # Import here to avoid circular dependency
                from core_functions import generate_sentences

                meaning, sentences = generate_sentences(
                    word=word,
                    language=selected_lang,
                    num_sentences=num_sentences,
                    min_length=min_length,
                    max_length=max_length,
                    difficulty=difficulty,
                    groq_api_key=groq_api_key,
                    topics=topics,
                    native_language=native_language
                )

                # Store Pass 1 results for UI display
                pass1_result = {
                    'word': word,
                    'meaning': meaning,
                    'sentences': sentences
                }
                results['pass1_results'].append(pass1_result)

                # Continue with Pass 2-6 processing (audio, images, etc.)
                # This would be expanded to include all passes
                word_data = {
                    'word': word,
                    'meaning': meaning,
                    'sentences': sentences,
                    # Add audio, images, etc. here
                }
                results['words_data'].append(word_data)

                if update_callback:
                    update_callback(f"✅ Completed word: {word}")

            except Exception as e:
                error_msg = f"Failed to generate content for word '{word}': {str(e)}"
                self.log_manager.log_message(f"<b>❌ {error_msg}</b>")
                results['errors'].append(error_msg)
                results['partial_success'] = False

        # Finalize deck assembly
        self.log_manager.log_message("<b>📦 FINAL PASS: Deck Assembly</b>")
        self.log_manager.log_message("Combining all word components into a professional Anki deck...")

        try:
            output_path = pathlib.Path(output_dir)
            media_dir = output_path / "media"
            apkg_file_path = output_path / f"{selected_lang}.apkg"

            # Create the final APKG file
            success = create_apkg_export(
                results['words_data'],
                str(media_dir),
                str(apkg_file_path),
                selected_lang,
                selected_lang
            )

            if success and apkg_file_path.exists():
                apkg_path = str(apkg_file_path)

                # Load the APKG file for download
                if not self.file_manager.load_apkg_file(apkg_path):
                    raise Exception("Failed to load created APKG file for download")

                result = {
                    'success': True,
                    'apkg_path': apkg_path,
                    'tsv_path': str(output_path / "ANKI_IMPORT.tsv"),
                    'media_dir': str(media_dir),
                    'output_dir': output_dir,
                    'errors': results['errors'],
                    'partial_success': results['partial_success']
                }

                self.log_manager.log_message("<b>✅ Deck assembly completed successfully!</b>")
                self.log_manager.log_message(f"Created Anki deck with {len(results['words_data'])} words")

                return result
            else:
                raise Exception("Failed to create APKG file")

        except Exception as e:
            error_msg = f"Deck assembly failed: {str(e)}"
            self.log_manager.log_message(f"<b>❌ {error_msg}</b>")
            results['errors'].append(error_msg)
            results['partial_success'] = False

            return {
                'success': False,
                'errors': results['errors'],
                'partial_success': False
            }