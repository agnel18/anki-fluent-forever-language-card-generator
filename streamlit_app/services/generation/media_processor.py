"""
Media Processor Service

Handles IPA generation, audio processing, and image processing.
Extracted from sentence_generator.py for better separation of concerns.
"""

import logging
from typing import Optional, List, Dict, Any
from pathlib import Path
import streamlit as st

logger = logging.getLogger(__name__)


class MediaProcessor:
    """
    Service for processing media-related tasks: IPA generation, audio, images.
    """

    def __init__(self):
        """Initialize media processor with output directories."""
        self.audio_output_dir = "output/audio"
        self.image_output_dir = "output/images"
        # Ensure directories exist
        Path(self.audio_output_dir).mkdir(parents=True, exist_ok=True)
        Path(self.image_output_dir).mkdir(parents=True, exist_ok=True)

    def generate_ipa_hybrid(self, text: str, language: str, ai_ipa: str = "") -> str:
        """
        Generate IPA using Epitran library for accurate phonetic transcription.
        Delegates to IPAService for consistent processing.

        Args:
            text: Text to convert to IPA
            language: Language name
            ai_ipa: AI-generated IPA fallback (optional)

        Returns:
            IPA transcription string
        """
        try:
            from services.sentence_generation import IPAService
            ipa_service = IPAService()
            return ipa_service.generate_ipa(text, language, ai_ipa)
        except ImportError:
            logger.warning("IPAService not available, using fallback")
            return self._ipa_fallback(text, ai_ipa)
        except Exception as e:
            logger.error(f"Error in IPA generation: {e}")
            return ai_ipa or text

    def _ipa_fallback(self, text: str, ai_ipa: str = "") -> str:
        """Fallback IPA generation when service is unavailable."""
        if ai_ipa:
            return ai_ipa
        # Very basic fallback - just return the original text
        return text

    def generate_audio_batch(self, sentences: List[str], language: str, voice: str = None, batch_name: str = "batch", unique_id: str = None) -> List[str]:
        """
        Generate audio files for multiple sentences.

        Args:
            sentences: List of sentences to convert to audio
            language: Language name
            voice: Voice to use (optional)
            batch_name: Prefix for filenames
            unique_id: Unique identifier for filename uniqueness

        Returns:
            List of audio file paths
        """
        audio_files = []
        for i, sentence in enumerate(sentences):
            try:
                audio_file = self.generate_audio(sentence, language, voice, index=i, batch_name=batch_name, unique_id=unique_id)
                audio_files.append(audio_file)
            except Exception as e:
                logger.error(f"Failed to generate audio for sentence {i}: {e}")
                audio_files.append("")  # Empty string for failed audio

        return audio_files

    def generate_audio(self, text: str, language: str, voice: str = None, index: int = 0, batch_name: str = "audio", unique_id: str = None) -> str:
        """
        Generate audio file for a single text.

        Args:
            text: Text to convert to audio
            language: Language name
            voice: Voice to use (optional)
            index: Index for file naming
            batch_name: Prefix for filename
            unique_id: Unique identifier for filename uniqueness

        Returns:
            Audio file path
        """
        try:
            import asyncio
            import os
            from pathlib import Path

            # Import audio generator
            from audio_generator import generate_audio_async, get_google_voices_for_language

            # Create output path with unique filename
            output_dir = Path("output/audio")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate unique filename following the pattern: {batch_name}_{index:02d}_{unique_id}.mp3
            unique_suffix = f"_{unique_id}" if unique_id else ""
            filename = f"{batch_name}_{index+1:02d}{unique_suffix}.mp3"
            output_path = output_dir / filename

            # Generate audio asynchronously
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(
                generate_audio_async(text, voice, str(output_path))
            )
            loop.close()

            return filename if success else ""
        except ImportError:
            logger.warning("Audio generator not available")
            return ""
        except Exception as e:
            logger.error(f"Error generating audio: {e}")
            return ""

    def generate_images_batch(self, keywords_list: List[str], language: str, batch_name: str = "batch", unique_id: str = None) -> List[str]:
        """
        Generate images for multiple keyword sets.

        Args:
            keywords_list: List of keyword strings (comma-separated)
            language: Language name
            batch_name: Prefix for filenames
            unique_id: Unique identifier for filename uniqueness

        Returns:
            List of image file paths
        """
        image_files = []
        for i, keywords in enumerate(keywords_list):
            try:
                image_file = self.generate_image(keywords, language, index=i, batch_name=batch_name, unique_id=unique_id)
                image_files.append(image_file)
            except Exception as e:
                logger.error(f"Failed to generate image for keywords {i}: {e}")
                image_files.append("")  # Empty string for failed images

        return image_files

    def generate_image(self, keywords: str, language: str, index: int = 0, batch_name: str = "batch", unique_id: str = None, image_quality: str = "free") -> str:
        """
        Generate image for keywords using Pixabay API.

        Args:
            keywords: Comma-separated keywords
            language: Language name
            index: Index for file naming
            batch_name: Prefix for filenames
            unique_id: Unique identifier for filename uniqueness
            image_quality: Ignored (always uses Pixabay)

        Returns:
            Image file path
        """
        try:
            # Get Pixabay API key (required)
            pixabay_api_key = getattr(st.session_state, 'pixabay_api_key', None)
            if not pixabay_api_key:
                logger.error("Pixabay API key is required for image generation")
                return ""

            logger.info(f"Generating Pixabay image for keywords: {keywords}")

            from image_generator import generate_images_pixabay

            image_files, _ = generate_images_pixabay(
                queries=[keywords],
                output_dir=self.image_output_dir,
                batch_name=batch_name,
                num_images=1,
                pixabay_api_key=pixabay_api_key,
                unique_id=unique_id,
            )

            if image_files and image_files[0]:
                logger.info(f"Successfully generated image: {image_files[0]}")
                return image_files[0]
            else:
                logger.error(f"No images generated for keywords: {keywords}")
                return ""

        except Exception as e:
            logger.error(f"Image generation failed for keywords '{keywords}': {e}")
            return ""
            return ""
        except Exception as e:
            logger.error(f"Error in hybrid image generation: {e}")
            return ""

    def process_media_for_sentences(
        self,
        sentences: List[str],
        keywords_list: List[str],
        language: str,
        voice: str = None,
        batch_name: str = "batch",
        unique_id: str = None
    ) -> Dict[str, List[str]]:
        """
        Process all media (IPA, audio, images) for a batch of sentences.

        Args:
            sentences: List of sentences
            keywords_list: List of keyword strings
            language: Language name
            voice: Voice for audio (optional)
            batch_name: Prefix for filenames
            unique_id: Unique identifier for filename uniqueness

        Returns:
            Dict with 'ipa', 'audio', 'images' lists
        """
        # Generate IPA for all sentences
        ipa_list = [self.generate_ipa_hybrid(sentence, language) for sentence in sentences]

        # Generate audio for all sentences
        audio_list = self.generate_audio_batch(sentences, language, voice, batch_name, unique_id)

        # Generate images for all keyword sets
        image_list = self.generate_images_batch(keywords_list, language, batch_name, unique_id)

        return {
            'ipa': ipa_list,
            'audio': audio_list,
            'images': image_list
        }


# Global instance for backward compatibility
_media_processor = None

def get_media_processor() -> MediaProcessor:
    """Get global media processor instance."""
    global _media_processor
    if _media_processor is None:
        _media_processor = MediaProcessor()
    return _media_processor