#!/usr/bin/env python3
"""
Quick test to verify grammar analyzer integration
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from sentence_generator import analyze_grammar_and_color, LANGUAGE_NAME_TO_CODE
from streamlit_app.language_analyzers.analyzer_registry import get_analyzer

def test_integration():
    print("Testing grammar analyzer integration...")

    # Test language mapping
    test_languages = ["Chinese (Simplified)", "Spanish", "Hindi", "English"]
    for lang in test_languages:
        code = LANGUAGE_NAME_TO_CODE.get(lang)
        print(f"{lang} -> {code}")
        if code:
            analyzer = get_analyzer(code)
            print(f"  Analyzer available: {analyzer is not None}")
            if analyzer:
                print(f"  Analyzer class: {type(analyzer).__name__}")

    # Test with a simple Chinese sentence (without API call)
    print("\nTesting analyzer lookup for Chinese...")
    analyzer = get_analyzer("zh")
    if analyzer:
        print(f"✓ Chinese analyzer loaded: {type(analyzer).__name__}")
        print(f"✓ Language code: {analyzer.language_code}")
        print(f"✓ Has analyze_grammar method: {hasattr(analyzer, 'analyze_grammar')}")
        print(f"✓ Has get_color_scheme method: {hasattr(analyzer, 'get_color_scheme')}")
    else:
        print("✗ Chinese analyzer not found")

if __name__ == "__main__":
    test_integration()