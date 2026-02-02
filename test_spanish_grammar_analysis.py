#!/usr/bin/env python3
"""
Test script to run grammar analysis on a Spanish sentence using the EsAnalyzer.
"""

import sys
import os
import json
import logging
from pathlib import Path

# Add the streamlit_app directory to the path
sys.path.insert(0, str(Path(__file__).parent / "streamlit_app"))

from languages.spanish.es_analyzer import EsAnalyzer

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

def test_spanish_grammar_analysis():
    """Test grammar analysis for a Spanish sentence."""
    logger.info("Starting Spanish grammar analysis test")

    # Get API key
    api_key = get_api_key()
    if not api_key:
        logger.error("No API key found - falling back to basic analysis")
        api_key = None
    else:
        # Set the API key in environment for the analyzer to use
        os.environ["GOOGLE_API_KEY"] = api_key
        logger.info("API key set in environment")

    # Initialize the Spanish analyzer
    try:
        analyzer = EsAnalyzer()
        logger.info("Spanish analyzer initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Spanish analyzer: {e}")
        return

    # Test sentence
    sentence = "Nosotros cultivamos tomates y pimientos en el jardín"
    target_word = "Nosotros"  # The word we're focusing on
    complexity = "intermediate"

    logger.info(f"Analyzing sentence: '{sentence}'")
    logger.info(f"Target word: '{target_word}'")
    logger.info(f"Complexity: '{complexity}'")
    logger.info(f"API Key: {'Available' if api_key else 'Not available (fallback mode)'}")

    try:
        # Run the grammar analysis
        result = analyzer.analyze_grammar(sentence, target_word, complexity, gemini_api_key=api_key)

        logger.info("\n" + "="*80)
        logger.info("GRAMMAR ANALYSIS RESULTS")
        logger.info("="*80)

        logger.info("\n" + "="*80)
        logger.info("GRAMMAR ANALYSIS RESULTS")
        logger.info("="*80)

        # Basic information
        logger.info(f"Sentence: {result.sentence}")
        logger.info(f"Target Word: {result.target_word}")
        logger.info(f"Language: {result.language_code}")
        logger.info(f"Complexity Level: {result.complexity_level}")
        logger.info(f"Confidence Score: {result.confidence_score:.3f}")
        logger.info(f"Text Direction: {result.text_direction}")
        logger.info(f"Is RTL: {result.is_rtl}")

        # Grammatical elements
        logger.info(f"\nGrammatical Elements:")
        for role, elements in result.grammatical_elements.items():
            logger.info(f"  {role.title()}: {len(elements)} elements")
            for elem in elements[:3]:  # Show first 3 elements
                logger.info(f"    - {elem.get('word', 'N/A')}: {elem.get('grammatical_role', 'N/A')}")

        # Explanations
        logger.info(f"\nOverall Analysis:")
        for key, explanation in result.explanations.items():
            logger.info(f"  {key.title()}: {explanation}")

        # Word explanations
        logger.info(f"\nWord Explanations ({len(result.word_explanations)} words):")
        for i, word_info in enumerate(result.word_explanations, 1):
            if isinstance(word_info, list) and len(word_info) >= 4:
                word, role, color, meaning = word_info[0], word_info[1], word_info[2], word_info[3]
            elif isinstance(word_info, dict):
                word = word_info.get('word', 'N/A')
                role = word_info.get('grammatical_role', 'N/A')
                meaning = word_info.get('meaning', 'N/A')
                color = 'N/A'
            else:
                word = role = meaning = color = 'N/A'
            logger.info(f"  {i}. '{word}' ({role}): {meaning}")

        # Color scheme
        logger.info(f"\nColor Scheme:")
        for role, color in result.color_scheme.items():
            logger.info(f"  {role.title()}: {color}")

        # HTML Output (first 200 characters)
        logger.info(f"\nHTML Output (first 200 chars):")
        html_preview = result.html_output[:200] + "..." if len(result.html_output) > 200 else result.html_output
        logger.info(f"  {html_preview}")

        # Full HTML if it's not too long
        if len(result.html_output) <= 500:
            logger.info(f"\nFull HTML Output:")
            logger.info(f"  {result.html_output}")

        logger.info("\n" + "="*80)
        logger.info("ANALYSIS COMPLETE")
        logger.info("="*80)

    except Exception as e:
        logger.error(f"Error in grammar analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_spanish_grammar_analysis()