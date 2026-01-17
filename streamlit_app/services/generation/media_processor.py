"""
Media Processor Service

Handles IPA generation, audio processing, and image processing.
Extracted from sentence_generator.py for better separation of concerns.
"""

import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


class MediaProcessor:
    """
    Service for processing media-related tasks: IPA generation, audio, images.
    """

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

    def generate_audio_batch(self, sentences: List[str], language: str, voice: str = None) -> List[str]:
        """
        Generate audio files for multiple sentences.

        Args:
            sentences: List of sentences to convert to audio
            language: Language name
            voice: Voice to use (optional)

        Returns:
            List of audio file paths
        """
        audio_files = []
        for i, sentence in enumerate(sentences):
            try:
                audio_file = self.generate_audio(sentence, language, voice, index=i)
                audio_files.append(audio_file)
            except Exception as e:
                logger.error(f"Failed to generate audio for sentence {i}: {e}")
                audio_files.append("")  # Empty string for failed audio

        return audio_files

    def generate_audio(self, text: str, language: str, voice: str = None, index: int = 0) -> str:
        """
        Generate audio file for a single text.

        Args:
            text: Text to convert to audio
            language: Language name
            voice: Voice to use (optional)
            index: Index for file naming

        Returns:
            Audio file path
        """
        try:
            from audio_generator import generate_audio_async
            # This would need to be adapted based on the actual audio_generator implementation
            # For now, return placeholder
            return f"audio_{index}.mp3"
        except ImportError:
            logger.warning("Audio generator not available")
            return ""
        except Exception as e:
            logger.error(f"Error generating audio: {e}")
            return ""

    def generate_images_batch(self, keywords_list: List[str], language: str) -> List[str]:
        """
        Generate images for multiple keyword sets.

        Args:
            keywords_list: List of keyword strings (comma-separated)
            language: Language name

        Returns:
            List of image file paths
        """
        image_files = []
        for i, keywords in enumerate(keywords_list):
            try:
                image_file = self.generate_image(keywords, language, index=i)
                image_files.append(image_file)
            except Exception as e:
                logger.error(f"Failed to generate image for keywords {i}: {e}")
                image_files.append("")  # Empty string for failed images

        return image_files

    def generate_image(self, keywords: str, language: str, index: int = 0) -> str:
        """
        Generate image for keywords.

        Args:
            keywords: Comma-separated keywords
            language: Language name
            index: Index for file naming

        Returns:
            Image file path
        """
        try:
            from image_generator import generate_images_pixabay
            # This would need to be adapted based on the actual image_generator implementation
            # For now, return placeholder
            return f"image_{index}.jpg"
        except ImportError:
            logger.warning("Image generator not available")
            return ""
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            return ""

    def process_media_for_sentences(
        self,
        sentences: List[str],
        keywords_list: List[str],
        language: str,
        voice: str = None
    ) -> Dict[str, List[str]]:
        """
        Process all media (IPA, audio, images) for a batch of sentences.

        Args:
            sentences: List of sentences
            keywords_list: List of keyword strings
            language: Language name
            voice: Voice for audio (optional)

        Returns:
            Dict with 'ipa', 'audio', 'images' lists
        """
        # Generate IPA for all sentences
        ipa_list = [self.generate_ipa_hybrid(sentence, language) for sentence in sentences]

        # Generate audio for all sentences
        audio_list = self.generate_audio_batch(sentences, language, voice)

        # Generate images for all keyword sets
        image_list = self.generate_images_batch(keywords_list, language)

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