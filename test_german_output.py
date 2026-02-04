#!/usr/bin/env python3
"""
Test script for German analyzer word explanations.
Tests the updated prompts that prevent repetition at source.
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

# Import German analyzer
from languages.german.de_analyzer import DeAnalyzer

# Load API key
def load_api_key():
    secrets_path = Path("streamlit_app/user_secrets.json")
    with open(secrets_path, 'r') as f:
        secrets = json.load(f)
    return secrets.get('google_api_key')

def test_german_word_explanations():
    """Test German analyzer with a sample sentence"""
    api_key = load_api_key()

    # Create analyzer
    analyzer = DeAnalyzer()

    # Sample German sentence
    sentence = "Der Mann geht in das Haus."
    target_word = "Mann"
    complexity = "intermediate"

    print(f"Testing German analyzer with sentence: '{sentence}'")
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
    test_german_word_explanations()