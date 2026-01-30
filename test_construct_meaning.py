#!/usr/bin/env python3
"""
Quick test of Arabic analyzer _construct_meaning_from_ai_fields method
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'languages', 'arabic'))

from languages.arabic.domain.ar_config import ArConfig
from languages.arabic.domain.ar_response_parser import ArResponseParser

def test_construct_meaning():
    config = ArConfig()
    parser = ArResponseParser(config)

    # Test data similar to what AI might return
    test_cases = [
        {
            'grammatical_role': 'pronoun',
            'type': 'independent personal pronoun',
            'person': '1st',
            'number': 'singular',
            'case': 'nominative'
        },
        {
            'grammatical_role': 'verb',
            'type': 'imperfect_verb',
            'person': '3rd',
            'number': 'masculine singular',
            'case': 'nominative'
        },
        {
            'grammatical_role': 'noun',
            'number': 'singular',
            'case': 'accusative'
        }
    ]

    print("Testing _construct_meaning_from_ai_fields method:")
    print("=" * 50)

    for i, word_data in enumerate(test_cases, 1):
        meaning = parser._construct_meaning_from_ai_fields(word_data)
        print(f"Test {i}: {word_data}")
        print(f"Result: {meaning}")
        print()

if __name__ == "__main__":
    test_construct_meaning()