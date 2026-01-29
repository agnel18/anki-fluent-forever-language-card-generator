#!/usr/bin/env python3
"""
Test script to generate 4 sentences with random database words for Arabic.
This will help diagnose why Arabic sentence generation constantly falls back to sample sentences.
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

def get_random_arabic_words(count=4):
    """Get random Arabic words from the database."""
    try:
        # Get all words (or a large sample)
        words, total = get_words_paginated('Arabic', page=1, per_page=1000)

        if not words:
            logger.error("No Arabic words found in database")
            return []

        # Select random words
        selected_words = random.sample(words, min(count, len(words)))
        word_strings = [w['word'] for w in selected_words]

        logger.info(f"Selected {len(word_strings)} random Arabic words: {word_strings}")
        return word_strings

    except Exception as e:
        logger.error(f"Error getting random Arabic words: {e}")
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

def test_arabic_sentence_generation():
    """Test sentence generation for Arabic with random database words."""
    logger.info("Starting Arabic sentence generation test")

    # Get API key
    api_key = get_api_key()
    if not api_key:
        logger.error("No API key found in user_secrets.json")
        return

    # Get random words
    words = get_random_arabic_words(4)
    if not words:
        logger.error("Could not get random words")
        return

    logger.info(f"Testing sentence generation for words: {words}")

    # Generate sentences for each word
    results = []
    for i, word in enumerate(words, 1):
        logger.info(f"\n--- Testing word {i}: '{word}' ---")

        try:
            result = generate_word_meaning_sentences_and_keywords(
                word=word,
                language="Arabic",
                num_sentences=4,
                min_length=3,
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
            is_fallback = any("sample sentence" in s.lower() for s in sentences)
            logger.info(f"  Using fallback sentences: {is_fallback}")
            
            results.append({
                'word': word,
                'result': result,
                'is_fallback': is_fallback
            })

        except Exception as e:
            logger.error(f"Error generating for word '{word}': {e}")
            results.append({
                'word': word,
                'error': str(e),
                'is_fallback': True
            })

    # Summary
    logger.info("\n" + "="*50)
    logger.info("SUMMARY")
    logger.info("="*50)

    total_words = len(results)
    fallback_count = sum(1 for r in results if r.get('is_fallback', False))
    error_count = sum(1 for r in results if 'error' in r)

    logger.info(f"Total words tested: {total_words}")
    logger.info(f"Words with fallback sentences: {fallback_count}")
    logger.info(f"Words with errors: {error_count}")
    logger.info(f"Success rate: {((total_words - fallback_count - error_count) / total_words * 100):.1f}%")

    if fallback_count > 0:
        logger.warning("Arabic sentence generation is falling back to sample sentences!")
        logger.warning("This indicates issues with:")
        logger.warning("1. AI API calls failing")
        logger.warning("2. Response parsing failing")
        logger.warning("3. Arabic-specific prompt issues")
    else:
        logger.info("Arabic sentence generation appears to be working correctly!")

if __name__ == "__main__":
    test_arabic_sentence_generation()