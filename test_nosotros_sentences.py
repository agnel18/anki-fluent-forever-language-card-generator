#!/usr/bin/env python3
"""
Test script to generate sentences for the Spanish word "Nosotros" with vegetables topic.
"""

import sys
import os
import json
import logging
from pathlib import Path

# Add the streamlit_app directory to the path
sys.path.insert(0, str(Path(__file__).parent / "streamlit_app"))

from sentence_generator import generate_word_meaning_sentences_and_keywords

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_api_key():
    """Load API key from user_secrets.json"""
    try:
        secrets_path = Path(__file__).parent / "streamlit_app" / "user_secrets.json"
        if secrets_path.exists():
            with open(secrets_path, "r", encoding="utf-8") as f:
                user_secrets = json.load(f)
            return user_secrets.get("google_api_key", "")
    except Exception as e:
        logger.error(f"Error loading API key: {e}")
    return ""

def test_spanish_sentence_generation():
    """Test sentence generation for Spanish word 'Nosotros' with vegetables topic."""
    logger.info("Starting Spanish sentence generation test for 'Nosotros'")

    # Get API key
    api_key = get_api_key()
    if not api_key:
        logger.error("No API key found in user_secrets.json")
        return

    word = "Nosotros"
    topics = ["vegetables"]

    logger.info(f"Testing sentence generation for word: '{word}' with topics: {topics}")

    try:
        result = generate_word_meaning_sentences_and_keywords(
            word=word,
            language="Spanish",
            num_sentences=4,
            min_length=8,
            max_length=17,
            difficulty="intermediate",
            gemini_api_key=api_key,
            topics=topics
        )

        logger.info("\n=== RESULTS ===")
        logger.info(f"Word: {word}")
        logger.info(f"Meaning: {result.get('meaning', 'N/A')}")
        logger.info(f"Restrictions: {result.get('restrictions', 'N/A')}")

        sentences = result.get('sentences', [])
        translations = result.get('translations', [])
        ipa = result.get('ipa', [])
        keywords = result.get('keywords', [])

        logger.info(f"\nGenerated {len(sentences)} sentences:")
        for i, sentence in enumerate(sentences, 1):
            logger.info(f"\n{i}. Sentence: {sentence}")
            if i <= len(translations):
                logger.info(f"   Translation: {translations[i-1]}")
            if i <= len(ipa):
                logger.info(f"   IPA: {ipa[i-1]}")
            if i <= len(keywords):
                logger.info(f"   Keyword: {keywords[i-1]}")

            # Count words in sentence
            word_count = len(sentence.split())
            logger.info(f"   Word count: {word_count}")

        # Summary
        logger.info("\n=== SUMMARY ===")
        logger.info(f"Total sentences generated: {len(sentences)}")
        if sentences:
            word_counts = [len(s.split()) for s in sentences]
            logger.info(f"Word count range: {min(word_counts)} - {max(word_counts)} words")
            logger.info(f"Average word count: {sum(word_counts) / len(word_counts):.1f} words")

    except Exception as e:
        logger.error(f"Error in sentence generation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_spanish_sentence_generation()