"""
Compatibility shim for content generation tests.

Exposes a ContentGenerator class at top-level so tests can patch
`content_generator.ContentGenerator` without reaching into package paths.
"""

from typing import Any, Dict, List, Optional

from streamlit_app.services.generation.content_generator import get_content_generator


class ContentGenerator:
    """Compatibility wrapper around the modular content generator service."""

    def __init__(self) -> None:
        self._impl = get_content_generator()

    def generate_sentences(
        self,
        word: str,
        language: str,
        difficulty: str = "intermediate",
        api_key: Optional[str] = None,
        context: Optional[str] = None,
        num_sentences: int = 2,
        min_length: int = 5,
        max_length: int = 20,
        topics: Optional[List[str]] = None,
        enriched_meaning: str = "",
    ) -> List[Dict[str, Any]]:
        """Generate sentence dictionaries compatible with legacy tests."""
        if context and not topics:
            topics = [context]

        result = self._impl.generate_word_meaning_sentences_and_keywords(
            word=word,
            language=language,
            num_sentences=num_sentences,
            gemini_api_key=api_key,
            enriched_meaning=enriched_meaning,
            min_length=min_length,
            max_length=max_length,
            difficulty=difficulty,
            topics=topics,
        )

        sentences = result.get("sentences", [])
        translations = result.get("translations", [])
        restrictions = result.get("restrictions", "")
        validation_warnings = result.get("validation_warnings", [])

        items: List[Dict[str, Any]] = []
        for idx, sentence in enumerate(sentences):
            warning_info = {}
            if idx < len(validation_warnings):
                warning_info = validation_warnings[idx]

            items.append(
                {
                    "sentence": sentence,
                    "translation": translations[idx] if idx < len(translations) else "",
                    "grammar_explanation": restrictions,
                    "validation_warning": warning_info,
                }
            )

        return items
