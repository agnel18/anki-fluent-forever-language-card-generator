#!/usr/bin/env python3
"""
Test German analyzer with sentences containing "mein"
"""

import sys
import os
import json
# Add the languages directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from languages.german.de_analyzer import DeAnalyzer
from languages.german.domain.de_config import DeConfig

def load_api_key():
    """Load API key from user_secrets.json"""
    secrets_path = os.path.join(os.path.dirname(__file__), '..', '..', 'streamlit_app', 'user_secrets.json')
    try:
        with open(secrets_path, 'r') as f:
            secrets = json.load(f)
            return secrets.get('google_api_key')
    except Exception as e:
        print(f"Could not load API key: {e}")
        return None

def test_mein_sentences():
    """Test German analyzer with sentences containing 'mein'"""

    # Load API key
    api_key = load_api_key()
    if not api_key:
        print("No API key found. Using fallback analysis.")
        api_key = None

    # Create analyzer
    config = DeConfig()
    analyzer = DeAnalyzer(config)

    # Test sentences with 'mein'
    sentences = [
        'Mein Hund ist groß.',
        'Ich esse mein Frühstück.',
        'Mein Bruder wohnt in Berlin.'
    ]

    print('=== GERMAN ANALYZER TEST: Sentences with "mein" ===\n')

    for i, sentence in enumerate(sentences, 1):
        print(f'Sentence {i}: "{sentence}"')
        try:
            # Use API key if available
            result = analyzer.analyze_grammar(sentence, 'mein', 'intermediate', api_key)
            print(f'Language: {result.language_code}')
            print(f'Confidence: {result.confidence_score:.2f}')
            print(f'Complexity Level: {result.complexity_level}')
            print()

            # Show detailed grammatical elements
            print('GRAMMATICAL ELEMENTS:')
            if isinstance(result.grammatical_elements, list):
                for i, element in enumerate(result.grammatical_elements):
                    if isinstance(element, dict):
                        details = []
                        for key, value in element.items():
                            if key != 'word':  # Skip word as it's redundant
                                details.append(f'{key}: {value}')
                        print(f'  {i+1}. {element.get("word", "N/A")}: {", ".join(details)}')
                    else:
                        print(f'  {i+1}. {element}')
            elif isinstance(result.grammatical_elements, dict):
                for element_type, elements in result.grammatical_elements.items():
                    print(f'  {element_type.upper()}:')
                    for element in elements:
                        if isinstance(element, dict):
                            details = []
                            for key, value in element.items():
                                if key != 'word':  # Skip word as it's redundant
                                    details.append(f'{key}: {value}')
                            print(f'    - {element.get("word", "N/A")}: {", ".join(details)}')
                        else:
                            print(f'    - {element}')
                    print()
            print()

            # Show explanations
            print('EXPLANATIONS:')
            for explanation_type, explanation in result.explanations.items():
                print(f'  {explanation_type.upper()}: {explanation}')
            print()

            # Show word-by-word analysis
            print('WORD ANALYSIS:')
            for word_info in result.word_explanations:
                if len(word_info) >= 4:
                    word, role, color, meaning = word_info[0], word_info[1], word_info[2], word_info[3]
                    print(f'  {word}: {role} (color: {color})')
                    if meaning:
                        print(f'    Meaning: {meaning}')
                else:
                    print(f'  {word_info}')
            print()

            # Show HTML output preview
            print(f'HTML Output preview: {result.html_output[:200]}...')
            print()
            print('=' * 80)
            print()

        except Exception as e:
            print(f'Error analyzing sentence: {e}')
            print()

if __name__ == '__main__':
    test_mein_sentences()