#!/usr/bin/env python3
"""
Test script for Spanish analyzer word explanations.
Tests the current prompts to identify any repetition issues.
"""

import sys
import os
import json
from pathlib import Path

# Add the project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Add streamlit_app to path for imports
sys.path.insert(0, str(project_root / "streamlit_app"))

# Import Spanish analyzer
from languages.spanish.es_analyzer import EsAnalyzer

# Load API key
def load_api_key():
    secrets_path = Path("streamlit_app/user_secrets.json")
    with open(secrets_path, 'r') as f:
        secrets = json.load(f)
    return secrets.get('google_api_key')

def test_spanish_word_explanations():
    """Test Spanish analyzer with a sample sentence"""
    api_key = load_api_key()

    # Create analyzer
    analyzer = EsAnalyzer()

    # Sample Spanish sentence
    sentence = "El hombre va a la casa."
    target_word = "hombre"
    complexity = "intermediate"

    print(f"Testing Spanish analyzer with sentence: '{sentence}'")
    print(f"Target word: '{target_word}'")
    print(f"Complexity: {complexity}")
    print("-" * 50)

    try:
        # Analyze
        result = analyzer.analyze_grammar(sentence, target_word, complexity, api_key)

        print("Analysis Result:")
        print(json.dumps(result.__dict__ if hasattr(result, '__dict__') else result, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_spanish_word_explanations()