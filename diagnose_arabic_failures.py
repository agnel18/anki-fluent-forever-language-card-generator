#!/usr/bin/env python3
"""
Test script to diagnose remaining Arabic sentence generation failures.
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

def test_specific_arabic_words():
    """Test specific Arabic words that might be problematic."""
    logger.info("Testing specific Arabic words for sentence generation")

    # Get API key
    api_key = get_api_key()
    if not api_key:
        logger.error("No API key found in user_secrets.json")
        return

    # Test a variety of Arabic words that might be challenging
    test_words = [
        "أبي",      # possessive - worked before
        "تأخذ",     # verb - failed before
        "إن",       # particle - failed before
        "كبيرة",    # adjective - worked before
        "شيئا",     # indefinite noun - failed before
        "الذى",     # relative pronoun - failed before
        "جيداً",    # adverb - worked before
        "يتحدث",    # verb - failed before
        "في",       # preposition - might be simple
        "من",       # preposition - might be simple
        "على",      # preposition - might be complex
        "مع",       # preposition - might be simple
    ]

    logger.info(f"Testing {len(test_words)} Arabic words")

    results = []
    for i, word in enumerate(test_words, 1):
        logger.info(f"\n--- Testing word {i}/{len(test_words)}: '{word}' ---")

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

            sentences = result.get('sentences', [])
            is_fallback = any("sample sentence" in s.lower() for s in sentences)

            logger.info(f"Word: {word}")
            logger.info(f"Meaning: {result.get('meaning', 'N/A')}")
            logger.info(f"Restrictions: {result.get('restrictions', 'N/A')}")
            logger.info(f"Sentences: {len(sentences)}")
            logger.info(f"Using fallback: {is_fallback}")

            if is_fallback:
                logger.warning(f"FAILED: {word} fell back to sample sentences")
            else:
                logger.info(f"SUCCESS: {word} generated proper sentences")
                for j, sentence in enumerate(sentences[:2], 1):  # Show first 2 sentences
                    logger.info(f"  {j}. {sentence}")

            results.append({
                'word': word,
                'success': not is_fallback,
                'meaning': result.get('meaning', ''),
                'restrictions': result.get('restrictions', ''),
                'sentence_count': len(sentences)
            })

        except Exception as e:
            logger.error(f"ERROR with word '{word}': {e}")
            results.append({
                'word': word,
                'success': False,
                'error': str(e)
            })

    # Summary
    logger.info("\n" + "="*60)
    logger.info("DIAGNOSTIC SUMMARY")
    logger.info("="*60)

    successful = [r for r in results if r.get('success', False)]
    failed = [r for r in results if not r.get('success', False)]

    logger.info(f"Total words tested: {len(results)}")
    logger.info(f"Successful: {len(successful)} ({len(successful)/len(results)*100:.1f}%)")
    logger.info(f"Failed: {len(failed)} ({len(failed)/len(results)*100:.1f}%)")

    if failed:
        logger.info("\nFAILED WORDS:")
        for f in failed:
            logger.info(f"  - {f['word']}: {f.get('error', 'Used fallback sentences')}")

    if successful:
        logger.info("\nSUCCESSFUL WORDS:")
        for s in successful:
            logger.info(f"  - {s['word']}: {s['sentence_count']} sentences")

    # Analyze patterns
    logger.info("\nPATTERN ANALYSIS:")
    if failed:
        failed_words = [f['word'] for f in failed]
        logger.info(f"Failed words: {failed_words}")

        # Check for patterns in failed words
        verbs = [w for w in failed_words if any(char in w for char in ['ت', 'ي', 'ا', 'و'] if len(w) > 2)]
        particles = [w for w in failed_words if len(w) <= 3]
        possessives = [w for w in failed_words if 'ي' in w and len(w) > 3]

        logger.info(f"Possible verb forms in failures: {verbs}")
        logger.info(f"Possible particles in failures: {particles}")
        logger.info(f"Possible possessives in failures: {possessives}")

if __name__ == "__main__":
    test_specific_arabic_words()