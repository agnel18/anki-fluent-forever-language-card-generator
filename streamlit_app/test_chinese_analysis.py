#!/usr/bin/env python3
"""
Test the grammar analyzer integration with actual API call
"""

import sys
import os
import json
sys.path.append(os.path.dirname(__file__))

from services.generation.grammar_processor import GrammarProcessor

def load_api_key():
    """Load API key from user_secrets.json"""
    try:
        with open('user_secrets.json', 'r') as f:
            secrets = json.load(f)
            return secrets.get('groq_api_key')
    except Exception as e:
        print(f"Failed to load API key: {e}")
        return None

def test_chinese_analyzer():
    print("Testing Chinese grammar analyzer integration...")

    # Test sentence in Chinese
    sentence = "我喜欢学习中文。"
    word = "学习"
    language = "Chinese (Simplified)"

    groq_api_key = load_api_key()
    if not groq_api_key:
        print("Could not load GROQ API key")
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
            groq_api_key=groq_api_key
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