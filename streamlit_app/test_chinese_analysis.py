#!/usr/bin/env python3
"""
Test the grammar analyzer integration with actual API call
"""


import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
except ImportError:
    pass

from services.generation.grammar_processor import GrammarProcessor

def load_api_key():
    """Load API key from environment variables."""
    api_key = os.environ.get('GOOGLE_API_KEY') or os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("Could not load API key from environment")
    return api_key

def test_chinese_analyzer():
    print("Testing Chinese grammar analyzer integration...")

    # Test sentence in Chinese
    sentence = "我喜欢学习中文。"
    word = "学习"
    language = "Chinese (Simplified)"

    google_api_key = load_api_key()
    if not google_api_key:
        print("Could not load GOOGLE API key")
        return

    try:
        processor = GrammarProcessor()
        
        # Check if analyzer is loaded
        from language_registry import get_language_registry
        registry = get_language_registry()
        language_code = registry.get_iso_code(language)
        print(f"Language code for '{language}': {language_code}")
        
        analyzer = processor._get_analyzer(language_code) if hasattr(processor, '_get_analyzer') else None
        print(f"Analyzer found: {type(analyzer).__name__ if analyzer else 'None'}")
        
        result = processor.analyze_grammar_and_color(
            sentence=sentence,
            word=word,
            language=language,
            gemini_api_key=google_api_key
        )

        print("✓ Analysis successful!")
        print(f"Colored sentence: {result['colored_sentence']}")
        print(f"Grammar summary: {result['grammar_summary']}")
        print(f"Number of word explanations: {len(result['word_explanations'])}")

        # Check if it looks like Chinese-specific analysis
        summary_lower = result['grammar_summary'].lower()
        if any(term in summary_lower for term in ["subject", "verb", "topic", "comment", "particle", "aspect"]):
            print("✓ Appears to be using Chinese-specific analysis")
        else:
            print("? Grammar summary doesn't show obvious Chinese-specific features")

    except Exception as e:
        print(f"✗ Analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_chinese_analyzer()