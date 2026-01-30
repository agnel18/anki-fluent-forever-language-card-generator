#!/usr/bin/env python3
"""
Test script for Arabic analyzer batch processing
"""

import sys
import os
import logging
sys.path.append(os.path.join(os.path.dirname(__file__), 'streamlit_app'))

# Set up logging to file
logging.basicConfig(
    filename='arabic_test.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from languages.arabic.ar_analyzer import ArAnalyzer
from languages.arabic.domain.ar_config import ArConfig

def test_arabic_batch():
    """Test Arabic batch analysis with debug logging"""

    # Initialize analyzer
    config = ArConfig()
    analyzer = ArAnalyzer(config)

    # Test sentences - 3 new Arabic sentences
    sentences = [
        "المعلم يشرح الدرس بوضوح",
        "الطبيب يفحص المريض بعناية",
        "الطالب يكتب الواجب بسرعة"
    ]

    target_word = "المعلم"
    complexity = "intermediate"

    print("Testing Arabic batch analysis with REAL API key...")
    print(f"Sentences: {sentences}")
    print(f"Target word: {target_word}")
    print(f"Complexity: {complexity}")
    print()

    try:
        # Perform batch analysis with REAL API key
        results = analyzer.batch_analyze_grammar(sentences, target_word, complexity, "AIzaSyCGUyM-Bhoev4VkgzizRF1vyuzWXORse0U")

        print(f"Got {len(results)} results")
        print()

        for i, result in enumerate(results):
            print(f"Result {i+1}:")
            print(f"  Sentence: {result.sentence}")
            print(f"  Target word: {result.target_word}")
            print(f"  Language: {result.language_code}")
            print(f"  Complexity: {result.complexity_level}")
            print(f"  Confidence: {result.confidence_score}")
            print(f"  Word explanations: {len(result.word_explanations)}")

            # Show first few word explanations
            explanations = result.word_explanations
            for j, exp in enumerate(explanations[:3]):  # Show first 3
                if len(exp) >= 4:
                    word, role, color, meaning = exp
                    print(f"    {j+1}. '{word}' - {role}: {meaning}")

            if len(explanations) > 3:
                print(f"    ... and {len(explanations) - 3} more")

            print()

    except Exception as e:
        print(f"Error during batch analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_arabic_batch()