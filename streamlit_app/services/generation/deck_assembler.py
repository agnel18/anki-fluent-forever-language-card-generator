"""
Deck Assembler Service

Handles final assembly and coordination of generated content into complete decks.
Extracted from sentence_generator.py for better separation of concerns.
"""

import logging
from typing import Dict, Any, List, Optional

from services.generation.content_generator import get_content_generator
from services.generation.grammar_processor import get_grammar_processor
from services.generation.media_processor import get_media_processor

logger = logging.getLogger(__name__)


class DeckAssembler:
    """
    Service for assembling complete learning decks from generated content.
    """

    def __init__(self):
        self.content_generator = get_content_generator()
        self.grammar_processor = get_grammar_processor()
        self.media_processor = get_media_processor()

    def assemble_complete_deck(
        self,
        word: str,
        language: str,
        num_sentences: int,
        groq_api_key: str,
        enriched_meaning: str = "",
        language_code: Optional[str] = None,
        voice: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Assemble a complete learning deck for a word.

        Args:
            word: Target word
            language: Language name
            num_sentences: Number of sentences to generate
            groq_api_key: API key for AI generation
            enriched_meaning: Pre-enriched meaning data
            language_code: ISO language code
            voice: Voice for audio generation
            **kwargs: Additional parameters

        Returns:
            Complete deck data dictionary
        """
        logger.info(f"Assembling complete deck for word '{word}' in {language}")

        try:
            # Step 1: Generate core content (sentences, meaning, keywords)
            content_result = self.content_generator.generate_word_meaning_sentences_and_keywords(
                word=word,
                language=language,
                num_sentences=num_sentences,
                groq_api_key=groq_api_key,
                enriched_meaning=enriched_meaning,
                **kwargs
            )

            sentences = content_result['sentences']
            keywords_list = content_result['keywords']

            # Step 2: Generate media (IPA, audio, images)
            media_result = self.media_processor.process_media_for_sentences(
                sentences=sentences,
                keywords_list=keywords_list,
                language=language,
                voice=voice
            )

            # Step 3: Analyze grammar for each sentence
            grammar_results = self.grammar_processor.batch_analyze_grammar_and_color(
                sentences=sentences,
                target_words=[word] * len(sentences),
                language=language,
                groq_api_key=groq_api_key,
                language_code=language_code
            )

            # Step 4: Assemble final deck
            deck = self._assemble_deck_data(
                word=word,
                language=language,
                content_result=content_result,
                media_result=media_result,
                grammar_results=grammar_results
            )

            logger.info(f"Successfully assembled deck with {len(sentences)} sentences")
            return deck

        except Exception as e:
            logger.error(f"Error assembling deck: {e}")
            return self._create_error_deck(word, language, num_sentences)

    def _assemble_deck_data(
        self,
        word: str,
        language: str,
        content_result: Dict[str, Any],
        media_result: Dict[str, Any],
        grammar_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Assemble all data into final deck format."""

        sentences = content_result['sentences']
        keywords_list = content_result['keywords']
        ipa_list = media_result['ipa']
        audio_list = media_result['audio']
        image_list = media_result['images']

        # Create sentence data with all components
        sentence_data = []
        for i, sentence in enumerate(sentences):
            sentence_info = {
                'sentence': sentence,
                'keywords': keywords_list[i] if i < len(keywords_list) else "",
                'ipa': ipa_list[i] if i < len(ipa_list) else "",
                'audio_file': audio_list[i] if i < len(audio_list) else "",
                'image_file': image_list[i] if i < len(image_list) else "",
                'grammar_analysis': grammar_results[i] if i < len(grammar_results) else {}
            }
            sentence_data.append(sentence_info)

        # Assemble complete deck
        deck = {
            'word': word,
            'language': language,
            'meaning': content_result.get('meaning', ''),
            'restrictions': content_result.get('restrictions', ''),
            'sentences': sentence_data,
            'total_sentences': len(sentences),
            'generation_timestamp': self._get_timestamp(),
            'status': 'completed'
        }

        return deck

    def _get_timestamp(self) -> str:
        """Get current timestamp for deck metadata."""
        from datetime import datetime
        return datetime.now().isoformat()

    def _create_error_deck(self, word: str, language: str, num_sentences: int) -> Dict[str, Any]:
        """Create error fallback deck when assembly fails."""
        logger.warning(f"Creating error fallback deck for {word}")

        fallback_sentences = []
        for i in range(num_sentences):
            fallback_sentences.append({
                'sentence': f"This is a sample sentence with {word}.",
                'keywords': f"{word}, language, learning",
                'ipa': "",
                'audio_file': "",
                'image_file': "",
                'grammar_analysis': {
                    'colored_sentence': f"This is a sample sentence with <span style='color: #FF6B6B'>{word}</span>.",
                    'word_explanations': [[word, "noun", "#FF6B6B", f"Target word: {word}"]],
                    'grammar_summary': f"Basic sentence structure in {language}"
                }
            })

        return {
            'word': word,
            'language': language,
            'meaning': word,
            'restrictions': 'No specific grammatical restrictions.',
            'sentences': fallback_sentences,
            'total_sentences': num_sentences,
            'generation_timestamp': self._get_timestamp(),
            'status': 'error_fallback'
        }

    def validate_deck(self, deck: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate assembled deck for completeness and correctness.

        Args:
            deck: Assembled deck data

        Returns:
            Validation result with status and issues
        """
        issues = []

        # Check required fields
        required_fields = ['word', 'language', 'sentences', 'total_sentences']
        for field in required_fields:
            if field not in deck:
                issues.append(f"Missing required field: {field}")

        # Check sentences
        if 'sentences' in deck:
            sentences = deck['sentences']
            if not isinstance(sentences, list):
                issues.append("Sentences must be a list")
            elif len(sentences) == 0:
                issues.append("No sentences generated")
            else:
                # Check each sentence has required fields
                for i, sentence in enumerate(sentences):
                    required_sentence_fields = ['sentence', 'keywords']
                    for field in required_sentence_fields:
                        if field not in sentence:
                            issues.append(f"Sentence {i} missing field: {field}")

        # Check word appears in sentences
        if 'word' in deck and 'sentences' in deck:
            word = deck['word'].lower()
            for i, sentence in enumerate(deck['sentences']):
                if word not in sentence.get('sentence', '').lower():
                    issues.append(f"Word '{word}' not found in sentence {i}")

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'severity': 'critical' if len(issues) > 0 else 'none'
        }


# Global instance for backward compatibility
_deck_assembler = None

def get_deck_assembler() -> DeckAssembler:
    """Get global deck assembler instance."""
    global _deck_assembler
    if _deck_assembler is None:
        _deck_assembler = DeckAssembler()
    return _deck_assembler