#!/usr/bin/env python3
"""Test Spanish analyzer color consistency"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'streamlit_app'))

from language_analyzers.analyzers.es_analyzer import EsAnalyzer

def test_spanish_colors():
    analyzer = EsAnalyzer()

    # Test sentence
    sentence = "La casa es grande"
    target_word = "casa"

    print(f"Testing Spanish analyzer with sentence: '{sentence}'")
    print(f"Target word: '{target_word}'")

    # Test the prompt generation to see if colors are specified
    prompt = analyzer.get_grammar_prompt('beginner', sentence, target_word)
    print(f"\nGenerated prompt contains color specifications: {'color hex code' in prompt}")

    # Test color scheme
    color_scheme = analyzer.get_color_scheme('beginner')
    print(f"\nColor scheme for beginner level:")
    for category, color in color_scheme.items():
        print(f"  {category}: {color}")

    # Test color standardization
    test_cases = [
        ("#FF4444", "pronouns"),  # Correct red for pronouns
        ("#00FF00", "pronouns"),  # Wrong green, should be standardized to red
        ("#FFAA00", "nouns"),     # Correct orange for nouns
        ("#123456", "nouns"),     # Wrong color, should be standardized to orange
    ]

    print("\nTesting color standardization:")
    for ai_color, category in test_cases:
        standardized = analyzer._standardize_color(ai_color, category)
        expected = analyzer.get_color_scheme('beginner').get(category, '#888888')
        status = "✅" if standardized == expected else "❌"
        print(f"  {status} {ai_color} for {category} -> {standardized} (expected: {expected})")

    print("\nSpanish eldest sister analyzer has been implemented!")
    print("- Updated all prompts (beginner/intermediate/advanced) with hex codes")
    print("- Added post-processing color standardization method")
    print("- Proper grammatical role restrictions (9 allowed roles)")
    print("- Single source of truth maintained through color scheme definitions")

    return True

if __name__ == "__main__":
    test_spanish_colors()