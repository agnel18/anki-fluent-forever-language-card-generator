#!/usr/bin/env python3
"""
Debug the repetition removal logic
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from languages.german.domain.de_response_parser import DeResponseParser
from languages.german.domain.de_config import DeConfig

def debug_repetition():
    """Debug the repetition removal"""

    # Create parser
    config = DeConfig()
    parser = DeResponseParser(config)

    # Test data
    test_data = {
        'words': [{
            'word': 'Wie',
            'grammatical_role': 'verb',
            'individual_meaning': 'Wie (verb): Wie (verb): How; used to inquire about the method or process of calculation'
        }]
    }

    print("BEFORE processing:")
    print(f"individual_meaning: '{test_data['words'][0]['individual_meaning']}'")

    # Process
    result = parser._validate_and_normalize_comprehensive(test_data, "Test sentence with Wie in it")

    print("\nAFTER processing:")
    print(f"individual_meaning: '{result['words'][0]['individual_meaning']}'")
    print(f"meaning: '{result['words'][0]['meaning']}'")

if __name__ == '__main__':
    debug_repetition()