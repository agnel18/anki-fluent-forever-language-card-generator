#!/usr/bin/env python3
"""
Test script to generate sentences with random database words for LANGUAGE_NAME_PLACEHOLDER.
This will help diagnose why LANGUAGE_NAME_PLACEHOLDER sentence generation falls back to sample sentences.
"""

import sys
import os
import random
import logging
from pathlib import Path

# Add the streamlit_app directory to the path
sys.path.insert(0, str(Path(__file__).parent / "streamlit_app"))

from db_manager import get_words_paginated
from sentence_generator import generate_word_meaning_sentences_and_keywords

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_random_LANGUAGE_PLACEHOLDER_words(count=4):
    """Get random LANGUAGE_NAME_PLACEHOLDER words from the database."""
    try:
        # Get all words (or a large sample)
        words, total = get_words_paginated('LANGUAGE_NAME_PLACEHOLDER', page=1, per_page=1000)

        if not words:
            logger.error("No LANGUAGE_NAME_PLACEHOLDER words found in database")
            return []

        # Select random words
        selected_words = random.sample(words, min(count, len(words)))
        word_strings = [w['word'] for w in selected_words]

        logger.info(f"Selected {len(word_strings)} random LANGUAGE_NAME_PLACEHOLDER words: {word_strings}")
        return word_strings

    except Exception as e:
        logger.error(f"Error getting random LANGUAGE_NAME_PLACEHOLDER words: {e}")
        return []

def get_api_key():
    """Load API key from user_secrets.json"""
    try:
        secrets_path = Path(__file__).parent / "streamlit_app" / "user_secrets.json"
        if secrets_path.exists():
            import json
            with open(secrets_path, "r", encoding="utf-8") as f:
                user_secrets = json.load(f)
            return user_secrets.get("google_api_key", "")
    except Exception:
        pass
    return ""

def test_LANGUAGE_PLACEHOLDER_sentence_generation():
    """Test sentence generation for LANGUAGE_NAME_PLACEHOLDER with random database words."""
    logger.info("Starting LANGUAGE_NAME_PLACEHOLDER sentence generation test")

    # Get API key
    api_key = get_api_key()
    if not api_key:
        logger.error("No API key found in user_secrets.json")
        return

    # Get random words
    words = get_random_LANGUAGE_PLACEHOLDER_words(4)
    if not words:
        logger.error("Could not get random words")
        return

    logger.info(f"Testing sentence generation for words: {words}")

    # Generate sentences for each word
    results = []
    fallback_count = 0

    for i, word in enumerate(words, 1):
        logger.info(f"\n--- Testing word {i}: '{word}' ---")

        try:
            result = generate_word_meaning_sentences_and_keywords(
                word=word,
                    language="LANGUAGE_NAME_PLACEHOLDER",
                max_length=15,
                difficulty="intermediate",
                gemini_api_key=api_key
            )

            logger.info(f"Result for '{word}':")
            logger.info(f"  Meaning: {result.get('meaning', 'N/A')}")
            logger.info(f"  Restrictions: {result.get('restrictions', 'N/A')}")
            logger.info(f"  Sentences: {result.get('sentences', [])}")
            logger.info(f"  Translations: {result.get('translations', [])}")
            logger.info(f"  IPA: {result.get('ipa', [])}")
            logger.info(f"  Keywords: {result.get('keywords', [])}")

            # Check if it's using fallback sentences
            sentences = result.get('sentences', [])
            is_fallback = False

            if sentences:
                # Check for common fallback indicators
                sentences_text = ' '.join(sentences).lower()
                if any(indicator in sentences_text for indicator in [
                    'sample sentence', 'example sentence', 'placeholder',
                    'test sentence', 'dummy text'
                ]):
                    is_fallback = True
                    fallback_count += 1
                    logger.warning(f"Word '{word}' is using fallback sentences!")
                else:
                    logger.info(f"Word '{word}' generated real sentences successfully")
            else:
                is_fallback = True
                fallback_count += 1
                logger.warning(f"Word '{word}' has no sentences generated")

            results.append({
                'word': word,
                'result': result,
                'is_fallback': is_fallback
            })

        except Exception as e:
            logger.error(f"Error generating sentences for '{word}': {e}")
            results.append({
                'word': word,
                'error': str(e),
                'is_fallback': True
            })
            fallback_count += 1

    # Summary
    total_words = len(words)
    success_count = total_words - fallback_count

    logger.info(f"\n{'='*60}")
    logger.info("SENTENCE GENERATION TEST SUMMARY")
    logger.info(f"{'='*60}")
    logger.info(f"Total words tested: {total_words}")
    logger.info(f"Successful AI generation: {success_count}")
    logger.info(f"Fallback sentences used: {fallback_count}")
    logger.info(f"Success rate: {(success_count/total_words)*100:.1f}%")

    if fallback_count > 0:
        logger.warning(f"LANGUAGE_NAME_PLACEHOLDER sentence generation is falling back to sample sentences for {fallback_count} words!")
        logger.info("This indicates the AI sentence generation needs improvement.")
        return False
    else:
        logger.info(f"LANGUAGE_NAME_PLACEHOLDER sentence generation appears to be working correctly!")
        return True

if __name__ == "__main__":
    success = test_LANGUAGE_PLACEHOLDER_sentence_generation()
    sys.exit(0 if success else 1)