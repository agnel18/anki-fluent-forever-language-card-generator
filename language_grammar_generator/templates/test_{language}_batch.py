#!/usr/bin/env python3
"""
Batch processing test for LANGUAGE_NAME_PLACEHOLDER analyzer.
Tests the LANGUAGE_NAME_PLACEHOLDER analyzer with multiple sentences in batch mode.
"""

import sys
import os
import json
import logging
from pathlib import Path

# Add the current directory to Python path for imports
current_dir = Path(__file__).parent

# Add the project root directory to Python path for imports
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

# Set up logging to file
logging.basicConfig(
    filename='LANGUAGE_PLACEHOLDER_batch_test.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# NOTE: Uncomment and replace placeholders when using this template for a specific language
# Try to import the LANGUAGE_NAME_PLACEHOLDER analyzer directly
# try:
#     from languages.LANGUAGE_PLACEHOLDER.LANGUAGE_PLACEHOLDER_analyzer import LANGUAGE_NAME_PLACEHOLDERAnalyzer
#     from languages.LANGUAGE_PLACEHOLDER.domain.LANGUAGE_PLACEHOLDER_config import LANGUAGE_NAME_PLACEHOLDERConfig
#     print("✓ Successfully imported LANGUAGE_NAME_PLACEHOLDERAnalyzer")
# except ImportError as e:
#     print(f"✗ Failed to import LANGUAGE_NAME_PLACEHOLDERAnalyzer: {e}")
#     sys.exit(1)

# Placeholder for analyzer import - replace with actual import when using template
LANGUAGE_NAME_PLACEHOLDERAnalyzer = None

# Try to load API key from multiple possible locations
def load_api_key():
    """Load API key from various possible locations."""
    possible_paths = [
        current_dir / "user_secrets.json",
        current_dir.parent / "user_secrets.json",
        Path("user_secrets.json"),
        Path("../user_secrets.json"),
        Path(".env"),
        Path("../.env"),
    ]

    for path in possible_paths:
        if path.exists():
            try:
                if path.name == ".env":
                    # Load .env file
                    from dotenv import load_dotenv
                    load_dotenv(path)
                    api_key = os.getenv('GEMINI_API_KEY')
                    if api_key:
                        print(f"✓ Loaded API key from {path}")
                        return api_key
                else:
                    # Load JSON file
                    with open(path, 'r', encoding='utf-8') as f:
                        secrets = json.load(f)
                        api_key = secrets.get('GEMINI_API_KEY') or secrets.get('GOOGLE_API_KEY') or secrets.get('google_api_key')
                        if api_key:
                            print(f"✓ Loaded API key from {path}")
                            return api_key
            except Exception as e:
                print(f"✗ Error reading {path}: {e}")
                continue

    print("✗ Could not find API key in any expected location")
    return None

def test_LANGUAGE_PLACEHOLDER_batch_processing():
    """Test LANGUAGE_NAME_PLACEHOLDER analyzer batch processing with multiple sentences."""

    # Load API key
    api_key = load_api_key()
    if not api_key:
        return False

    # Configure Gemini API with the API key
    try:
        from streamlit_app.shared_utils import get_gemini_api, get_gemini_model
        api = get_gemini_api()
        api.configure(api_key=api_key)
        api.generate_content(model=get_gemini_model(), contents="Hello")
        print("✓ Gemini API configured successfully")
    except Exception as e:
        print(f"✗ Failed to configure Gemini API: {e}")
        return False

    # Initialize analyzer
    try:
        if LANGUAGE_NAME_PLACEHOLDERAnalyzer is None:
            print("✗ LANGUAGE_NAME_PLACEHOLDERAnalyzer not imported - update template with actual import")
            return False
        analyzer = LANGUAGE_NAME_PLACEHOLDERAnalyzer()
        print("✓ LANGUAGE_NAME_PLACEHOLDERAnalyzer initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize LANGUAGE_NAME_PLACEHOLDERAnalyzer: {e}")
        return False

    # Test sentences - replace with actual LANGUAGE_NAME_PLACEHOLDER sentences
    sentences = [
        "{Test sentence 1 in LANGUAGE_NAME_PLACEHOLDER.}",
        "{Test sentence 2 in LANGUAGE_NAME_PLACEHOLDER.}",
        "{Test sentence 3 in LANGUAGE_NAME_PLACEHOLDER.}"
    ]

    target_word = "{target_word}"
    complexity = "intermediate"

    print("Testing LANGUAGE_NAME_PLACEHOLDER batch analysis...")
    print(f"Sentences: {sentences}")
    print(f"Target word: {target_word}")
    print(f"Complexity: {complexity}")
    print()

    try:
        # Perform batch analysis
        results = analyzer.batch_analyze_grammar(sentences, target_word, complexity, api_key)

        print(f"✓ Got {len(results)} results")
        print()

        success_count = 0
        for i, result in enumerate(results):
            print(f"Result {i+1}:")
            print(f"  Sentence: {result.sentence}")
            print(f"  Target word: {result.target_word}")
            print(f"  Language: {result.language_code}")
            print(f"  Complexity: {result.complexity_level}")
            print(f"  Confidence: {result.confidence_score}")
            print(f"  Word explanations: {len(result.word_explanations)}")

            # Check if explanations are specific (not generic fallbacks)
            has_specific_explanations = False
            for exp in result.word_explanations:
                if len(exp) >= 4:
                    word, role, color, meaning = exp
                    # Check if meaning contains specific grammatical terms (not generic)
                    if not any(generic in meaning.lower() for generic in [
                        "a thing, person, or concept",
                        "a word that describes",
                        "other word",
                        "basic analysis"
                    ]):
                        has_specific_explanations = True
                        print(f"    ✓ '{word}' - {role}: {meaning[:100]}...")
                        break

            if has_specific_explanations:
                success_count += 1
                print("  ✓ Contains specific grammatical explanations")
            else:
                print("  ⚠ Contains generic explanations only")
            print()

        # Test results
        if success_count == len(results):
            print(f"🎉 SUCCESS: All {len(results)} sentences produced specific explanations!")
            return True
        elif success_count > 0:
            print(f"⚠ PARTIAL SUCCESS: {success_count}/{len(results)} sentences produced specific explanations")
            return True
        else:
            print("❌ FAILURE: All sentences produced generic explanations")
            return False

    except Exception as e:
        print(f"❌ Error during batch analysis: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("="*60)
    print("LANGUAGE_NAME_PLACEHOLDER BATCH PROCESSING TEST")
    print("="*60)

    success = test_LANGUAGE_PLACEHOLDER_batch_processing()

    print("="*60)
    if success:
        print("✓ BATCH PROCESSING TEST PASSED")
    else:
        print("✗ BATCH PROCESSING TEST FAILED")
    print("="*60)