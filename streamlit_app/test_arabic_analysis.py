#!/usr/bin/env python3
"""
Integration test for Arabic grammatical analysis using real API calls.
Tests the Arabic analyzer with user-provided sentences to ensure gold standard quality explanations.
"""

import sys
import os
import json
import pytest
from pathlib import Path
from streamlit_app.shared_utils import get_gemini_api, get_gemini_model

# Add the current directory to Python path for imports
current_dir = Path(__file__).parent

# Add the project root directory to Python path for imports
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

# Try to import the Arabic analyzer directly
try:
    from languages.arabic.ar_analyzer import ArAnalyzer
    print("✓ Successfully imported ArAnalyzer")
except ImportError as e:
    print(f"✗ Failed to import ArAnalyzer: {e}")
    sys.exit(1)

# Try to load API key from multiple possible locations
def load_api_key():
    """Load API key from various possible locations."""
    possible_paths = [
        current_dir / "user_secrets.json",
        current_dir.parent / "user_secrets.json",
        Path("user_secrets.json"),
        Path("../user_secrets.json"),
    ]

    for path in possible_paths:
        if path.exists():
            try:
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

def test_arabic_analyzer_quality():
    """Test Arabic analyzer with user-provided sentences for gold standard quality."""

    # Load API key
    api_key = load_api_key()
    if not api_key:
        pytest.skip("No API key available for Arabic analyzer quality test")

    # Configure Gemini API with the API key
    try:
        api = get_gemini_api()
        api.configure(api_key=api_key)
        api.generate_content(
            model=get_gemini_model(),
            contents="Hello"
        )
        print("✓ Gemini API configured successfully")
    except Exception as e:
        pytest.fail(f"Failed to configure Gemini API: {e}")

    # Initialize analyzer
    try:
        analyzer = ArAnalyzer()
        print("✓ ArAnalyzer initialized successfully")
    except Exception as e:
        pytest.fail(f"Failed to initialize ArAnalyzer: {e}")

    # User-provided test sentences with target words
    test_cases = [
        {
            "sentence": "يجب أن نحترمَ عاداتِ أجدادِنا.",
            "target_word": "نحترمَ"  # The verb "we respect"
        },
        {
            "sentence": "نتمنى أن يعودَ العيدُ بالفرحِ والبركاتِ.",
            "target_word": "نتمنى"  # The verb "we wish"
        }
    ]

    print("\n" + "="*60)
    print("TESTING ARABIC GRAMMATICAL ANALYSIS")
    print("="*60)

    all_passed = True

    for i, test_case in enumerate(test_cases, 1):
        sentence = test_case["sentence"]
        target_word = test_case["target_word"]

        print(f"\n--- Test Sentence {i} ---")
        print(f"Arabic: {sentence}")
        print(f"Target Word: {target_word}")

        try:
            # Analyze the sentence with the API key
            result = analyzer.analyze_grammar(sentence, target_word, gemini_api_key=api_key)
            print("✓ Analysis completed successfully")

            # Debug: Show raw AI response if available
            if hasattr(analyzer, '_last_ai_response'):
                print(f"  Raw AI Response: {analyzer._last_ai_response[:500]}...")
            
            # Check if result has expected structure
            if not result:
                print("✗ Analysis result is None")
                all_passed = False
                continue

            # Check for words in different possible locations
            words_found = []

            # Try grammatical_elements first
            if hasattr(result, 'grammatical_elements') and result.grammatical_elements:
                if 'words' in result.grammatical_elements:
                    words_found = result.grammatical_elements['words']
                elif 'tokens' in result.grammatical_elements:
                    words_found = result.grammatical_elements['tokens']

            # Try word_explanations (used in fallback)
            if not words_found and hasattr(result, 'word_explanations') and result.word_explanations:
                words_found = result.word_explanations

            if not words_found:
                print("✗ No words/tokens found in result")
                print(f"  Available attributes: {[attr for attr in dir(result) if not attr.startswith('_')]}")
                all_passed = False
                continue

            print(f"✓ Found {len(words_found)} words in analysis")

            for word_info in words_found:
                if isinstance(word_info, list) and len(word_info) >= 4:
                    # Fallback format: [word, role, color, explanation]
                    word = word_info[0]
                    role = word_info[1]
                    meaning = word_info[3]
                elif isinstance(word_info, dict):
                    # Normal format
                    word = word_info.get('word', '')
                    role = word_info.get('role', '')
                    meaning = word_info.get('meaning', '')
                else:
                    # Handle other formats
                    word = str(word_info)
                    role = "unknown"
                    meaning = "unknown"

                print(f"\n  Word: '{word}'")
                print(f"  Role: {role}")
                print(f"  Meaning: {meaning}")

                # Quality checks for gold standard Arabic analysis
                # Should include both word meaning AND sentence function
                if not meaning or len(meaning.strip()) < 20:
                    print("  ✗ Meaning too short - needs detailed explanation")
                    all_passed = False
                elif not any(keyword in meaning.lower() for keyword in [
                    "means", "expresses", "expressing", "refers to", "used as", "introduces", "marks", "connects",
                    "functions as", "serves as", "indicates", "indicating", "main verb", "causes", "governed by", "renders",
                    "conjugated", "case", "mood", "subject", "object", "preposition"
                ]):
                    print("  ✗ Meaning lacks semantic content or functional explanation")
                    all_passed = False
                else:
                    print("  ✓ Meaning includes both semantic content and syntactic function")

            # Show HTML output if available
            if hasattr(result, 'html_output') and result.html_output:
                print(f"\n  HTML Output Length: {len(result.html_output)} characters")

        except Exception as e:
            print(f"✗ Analysis failed for sentence {i}: {e}")
            all_passed = False

    print("\n" + "="*60)
    if all_passed:
        print("✓ ALL TESTS PASSED - Arabic analyzer produces gold standard quality!")
    else:
        print("✗ SOME TESTS FAILED - Arabic analyzer needs improvement")
    print("="*60)

    assert all_passed, "Arabic analyzer quality checks failed"

if __name__ == "__main__":
    success = test_arabic_analyzer_quality()
    sys.exit(0 if success else 1)