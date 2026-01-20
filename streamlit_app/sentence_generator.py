# Sentence generation module
# Refactored to use modular services for better maintainability

import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

# Import the new modular services
from services.generation.content_generator import get_content_generator
from services.generation.grammar_processor import get_grammar_processor
from services.generation.media_processor import get_media_processor
from services.generation.deck_assembler import get_deck_assembler

# Legacy imports for backward compatibility
try:
    from language_analyzers.analyzer_registry import get_analyzer
    logger.info("Successfully imported analyzer registry")
except ImportError as e:
    logger.warning(f"Failed to import analyzer registry: {e}. Grammar analysis will be unavailable.")
    get_analyzer = None

# Import word data fetcher for enrichment
try:
    # Removed - now using user-provided enrichment data
    logger.info("Word enrichment now uses user input")
except ImportError as e:
    logger.warning(f"Word enrichment uses user input: {e}.")

# ============================================================================
# MAIN API FUNCTIONS - Now use modular services
# ============================================================================

def generate_word_meaning_sentences_and_keywords(
    word: str,
    language: str,
    num_sentences: int = 10,
    min_length: int = 5,
    max_length: int = 20,
    difficulty: str = "intermediate",
    groq_api_key: str = None,
    topics: Optional[List[str]] = None,
    enriched_meaning: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate word meaning, sentences, AND keywords using modular services.

    This function now delegates to the content_generator service for the core logic.

    Args:
        word: Target language word
        language: Language name (e.g., "Spanish", "Hindi")
        num_sentences: Number of sentences to generate (1-20)
        min_length: Minimum sentence length in words
        max_length: Maximum sentence length in words
        difficulty: "beginner", "intermediate", "advanced"
        groq_api_key: Groq API key
        topics: List of topics to focus sentence generation around (optional)
        enriched_meaning: Pre-reviewed word meaning from user (optional)

    Returns:
        Dict with keys:
        - meaning: English meaning string
        - restrictions: Grammatical restrictions string
        - sentences: List of generated sentences
        - keywords: List of keyword strings (one per sentence)
        - ipa: List of IPA transcriptions (one per sentence)
    """
    if not groq_api_key:
        raise ValueError("Groq API key required")

    logger.info(f"Generating content for word='{word}', language='{language}', num_sentences={num_sentences}")

    try:
        # Delegate to content generator service
        content_generator = get_content_generator()
        result = content_generator.generate_word_meaning_sentences_and_keywords(
            word=word,
            language=language,
            num_sentences=num_sentences,
            min_length=min_length,
            max_length=max_length,
            difficulty=difficulty,
            groq_api_key=groq_api_key,
            topics=topics,
            enriched_meaning=enriched_meaning
        )

        logger.info(f"Successfully generated content: {len(result.get('sentences', []))} sentences")
        return result

    except Exception as e:
        logger.error(f"Error in content generation: {e}")
        # Fallback: return basic structure
        return {
            'meaning': word,
            'restrictions': 'No specific grammatical restrictions.',
            'sentences': [f"This is a sample sentence with {word}."] * num_sentences,
            'keywords': [f"{word}, language, learning"] * num_sentences,
            'ipa': [""] * num_sentences
        }


def generate_complete_deck(
    word: str,
    language: str,
    num_sentences: int = 10,
    groq_api_key: str = None,
    enriched_meaning: str = "",
    language_code: Optional[str] = None,
    voice: str = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Generate a complete learning deck using all modular services.

    This is the main entry point for deck generation that coordinates:
    - Content generation (sentences, meaning, keywords)
    - Media processing (IPA, audio, images)
    - Grammar analysis and coloring
    - Final deck assembly

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
    if not groq_api_key:
        raise ValueError("Groq API key required")

    logger.info(f"Generating complete deck for word '{word}' in {language}")

    try:
        # Delegate to deck assembler service
        deck_assembler = get_deck_assembler()
        deck = deck_assembler.assemble_complete_deck(
            word=word,
            language=language,
            num_sentences=num_sentences,
            groq_api_key=groq_api_key,
            enriched_meaning=enriched_meaning,
            language_code=language_code,
            voice=voice,
            **kwargs
        )

        logger.info(f"Successfully generated complete deck with {len(deck.get('sentences', []))} sentences")
        return deck

    except Exception as e:
        logger.error(f"Error in complete deck generation: {e}")
        # Return error fallback deck
        return {
            'word': word,
            'language': language,
            'meaning': word,
            'restrictions': 'No specific grammatical restrictions.',
            'sentences': [{
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
            }] * num_sentences,
            'total_sentences': num_sentences,
            'generation_timestamp': "error_fallback",
            'status': 'error_fallback'
        }

# ============================================================================
# LEGACY COMPATIBILITY FUNCTIONS
# ============================================================================

def generate_sentences(
    word: str,
    language: str,
    num_sentences: int = 10,
    min_length: int = 5,
    max_length: int = 20,
    difficulty: str = "intermediate",
    groq_api_key: str = None,
    topics: Optional[List[str]] = None,
    native_language: str = "English",
    enriched_word_data: Optional[Any] = None,
) -> tuple[str, List[Dict[str, Any]]]:
    """
    Legacy compatibility function for generate_sentences.
    Returns tuple of (meaning, sentences_list) for backward compatibility.

    This function now uses the new modular services but maintains the old interface.
    """
    if not groq_api_key:
        raise ValueError("Groq API key required")

    logger.info(f"Generating sentences for word='{word}', language='{language}' (legacy interface)")

    try:
        # Use the new content generator service
        content_generator = get_content_generator()
        result = content_generator.generate_word_meaning_sentences_and_keywords(
            word=word,
            language=language,
            num_sentences=num_sentences,
            min_length=min_length,
            max_length=max_length,
            difficulty=difficulty,
            groq_api_key=groq_api_key,
            topics=topics,
            enriched_meaning=enriched_word_data if isinstance(enriched_word_data, str) else None
        )

        # Convert to legacy format: (meaning, sentences_list)
        meaning = result.get('meaning', word)
        sentences_list = []

        sentences = result.get('sentences', [])
        translations = result.get('translations', [])
        ipa_list = result.get('ipa', [])
        keywords_list = result.get('keywords', [])

        for i, sentence in enumerate(sentences):
            sentence_dict = {
                'sentence': sentence,
                'english_translation': translations[i] if i < len(translations) else sentence,
                'ipa': ipa_list[i] if i < len(ipa_list) else '',
                'context': 'general',  # Placeholder
                'image_keywords': keywords_list[i] if i < len(keywords_list) else '',
                'role_of_word': 'target',  # Placeholder
                'word': word,
                'meaning': meaning
            }
            sentences_list.append(sentence_dict)

        logger.info(f"Generated {len(sentences_list)} sentences using legacy interface")
        return meaning, sentences_list

    except Exception as e:
        logger.error(f"Error in legacy generate_sentences: {e}")
        # Return fallback in legacy format
        return word, []

def generate_word_meaning(
    word: str,
    language: str,
    groq_api_key: str = None,
) -> str:
    """
    Legacy compatibility function for generate_word_meaning.
    Returns string with meaning and brief explanation.

    This function now uses the new meaning service but maintains the old interface.
    """
    if not groq_api_key:
        raise ValueError("Groq API key required")

    logger.info(f"Generating meaning for word='{word}', language='{language}' (legacy interface)")

    try:
        # Use the new meaning service
        from services.sentence_generation.meaning_service import MeaningService
        meaning_service = MeaningService()
        return meaning_service.generate_word_meaning(
            word=word,
            language=language,
            groq_api_key=groq_api_key
        )
    except Exception as e:
        logger.error(f"Error in legacy generate_word_meaning: {e}")
        # Return fallback
        return word

# ============================================================================
# LEGACY FUNCTIONS - Kept for backward compatibility
# ============================================================================

def analyze_grammar_and_color(
    sentence: str,
    target_words: List[str],
    language: str,
    groq_api_key: str = None,
    language_code: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analyze grammar and color target words in a sentence.
    Delegates to grammar processor service.
    """
    grammar_processor = get_grammar_processor()
    return grammar_processor.analyze_grammar_and_color(
        sentence=sentence,
        target_words=target_words,
        language=language,
        groq_api_key=groq_api_key,
        language_code=language_code
    )

def _batch_analyze_grammar_and_color(
    sentences: List[str],
    target_words: List[str],
    language: str,
    groq_api_key: str = None,
    language_code: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Batch analyze grammar and color for multiple sentences.
    Delegates to grammar processor service.
    """
    grammar_processor = get_grammar_processor()
    return grammar_processor.batch_analyze_grammar_and_color(
        sentences=sentences,
        target_words=target_words,
        language=language,
        groq_api_key=groq_api_key,
        language_code=language_code
    )

# Legacy utility functions
def _convert_analyzer_output_to_explanations(grammar_result: Dict[str, Any], language: str) -> List[List[Any]]:
    """Convert analyzer output to explanations format - delegates to grammar processor."""
    grammar_processor = get_grammar_processor()
    return grammar_processor._convert_analyzer_output_to_explanations(grammar_result, language)

def _map_grammatical_role_to_color_category(role: str) -> str:
    """Map grammatical role to color category - delegates to grammar processor."""
    grammar_processor = get_grammar_processor()
    return grammar_processor._map_grammatical_role_to_color_category(role)

def _get_color_for_category(category: str, language: str) -> str:
    """Get color for grammatical category - delegates to grammar processor."""
    grammar_processor = get_grammar_processor()
    return grammar_processor._get_color_for_category(category, language)
