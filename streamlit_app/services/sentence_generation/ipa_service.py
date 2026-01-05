# IPA Service for Sentence Generation
# Handles IPA (International Phonetic Alphabet) generation and validation

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class IPAService:
    """
    Service for generating and validating IPA (International Phonetic Alphabet) transcriptions.
    Uses Epitran library for accurate phonetic transcription with AI fallback.
    """

    def __init__(self):
        self.language_map = {
            "Chinese (Simplified)": "cmn-Hans",  # Mandarin IPA (not Pinyin)
            "Chinese (Traditional)": "cmn-Hant",
            "Mandarin Chinese": "cmn-Hans",
            "English": "eng-Latn",
            "Spanish": "spa-Latn",
            "French": "fra-Latn",
            "German": "deu-Latn",
            "Italian": "ita-Latn",
            "Portuguese": "por-Latn",
            "Russian": "rus-Cyrl",
            "Japanese": "jpn-Hrgn",  # Hepburn romanization to IPA
            "Korean": "kor-Hang",   # Hangul to IPA
            "Hindi": "hin-Deva",
            "Arabic": "ara-Arab",
        }

    def generate_ipa_hybrid(self, text: str, language: str, ai_ipa: str = "") -> str:
        """
        Generate IPA using Epitran library for accurate phonetic transcription.
        Falls back to AI-generated IPA if Epitran fails or language not supported.
        Ensures output is official IPA only (no Pinyin, romanization).

        Args:
            text: Text to transliterate to IPA
            language: Language name
            ai_ipa: AI-generated IPA fallback

        Returns:
            IPA transcription string, or empty string if generation fails
        """
        if not text:
            return ""

        try:
            import epitran

            epi_code = self.language_map.get(language)
            if epi_code:
                epi = epitran.Epitran(epi_code)
                ipa = epi.transliterate(text)
                if ipa and ipa != text:
                    # Use the comprehensive validation from generation_utils
                    from generation_utils import validate_ipa_output
                    is_valid, _ = validate_ipa_output(ipa, language)
                    if is_valid:
                        return ipa

            # Fallback to AI IPA if Epitran fails or validation fails
            if ai_ipa:
                from generation_utils import validate_ipa_output
                is_valid, _ = validate_ipa_output(ai_ipa, language)
                if is_valid:
                    return ai_ipa

            # If no valid IPA, return empty (will be handled upstream)
            return ""

        except Exception as e:
            logger.warning(f"Epitran IPA generation failed for '{text}' in {language}: {e}")
            # Try AI fallback if available and valid
            if ai_ipa:
                from generation_utils import validate_ipa_output
                is_valid, _ = validate_ipa_output(ai_ipa, language)
                if is_valid:
                    return ai_ipa
            return ""