#!/usr/bin/env python3
"""
Generate Language Analyzers for Tier 1 Languages
Uses AI to create analyzers based on Chinese gold standard.
"""

import os
import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from language_analyzers.analyzer_generator import AnalyzerGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Generate analyzers for Tier 1 languages."""

    # Tier 1 languages (highest priority)
    languages = [
        {
            "name": "Spanish",
            "code": "es",
            "family": "Romance",
            "script_type": "alphabetic",
            "complexity": "medium"
        },
        {
            "name": "French",
            "code": "fr",
            "family": "Romance",
            "script_type": "alphabetic",
            "complexity": "medium"
        },
        {
            "name": "German",
            "code": "de",
            "family": "Germanic",
            "script_type": "alphabetic",
            "complexity": "high"
        },
        {
            "name": "Japanese",
            "code": "ja",
            "family": "Japonic",
            "script_type": "mixed",
            "complexity": "high"
        },
        {
            "name": "Korean",
            "code": "ko",
            "family": "Koreanic",
            "script_type": "alphabetic",
            "complexity": "high"
        },
        {
            "name": "Arabic",
            "code": "ar",
            "family": "Afro-Asiatic",
            "script_type": "abjad",
            "complexity": "high"
        },
        {
            "name": "Hindi",
            "code": "hi",
            "family": "Indo-European",
            "script_type": "abugida",
            "complexity": "medium"
        }
    ]

    # Get Groq API key from environment
    groq_api_key = os.getenv('GROQ_API_KEY')
    if not groq_api_key:
        logger.error("GROQ_API_KEY environment variable not set")
        sys.exit(1)

    generator = AnalyzerGenerator(groq_api_key)

    for lang in languages:
        logger.info(f"Generating analyzer for {lang['name']} ({lang['code']})")

        # Generate analyzer code
        code = generator.generate_analyzer(
            language_name=lang["name"],
            language_code=lang["code"],
            family=lang["family"],
            script_type=lang["script_type"],
            complexity=lang["complexity"]
        )

        if not code:
            logger.error(f"Failed to generate code for {lang['name']}")
            continue

        # Validate code
        if not generator.validate_analyzer_code(code):
            logger.warning(f"Generated code for {lang['name']} failed validation")
            # Save anyway for manual review
            generator.save_analyzer(lang["code"], code)
            continue

        # Save analyzer
        if generator.save_analyzer(lang["code"], code):
            logger.info(f"Successfully generated analyzer for {lang['name']}")
        else:
            logger.error(f"Failed to save analyzer for {lang['name']}")

if __name__ == "__main__":
    main()