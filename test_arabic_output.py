#!/usr/bin/env python3
"""
Test Arabic analyzer output to see what's happening
"""

import os
import sys
sys.path.append('.')

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not available, use environment variables

from languages.arabic.ar_analyzer import ArAnalyzer
from streamlit_app.shared_utils import get_gemini_api, get_gemini_model

def test_arabic_output():
    """Test Arabic analyzer with a simple sentence"""

    # Initialize analyzer
    analyzer = ArAnalyzer()

    # Test sentence
    sentence = "هي تأكل الموز والبطيخ."
    target_word = "تأكل"
    complexity = "intermediate"

    print("=" * 60)
    print("ARABIC ANALYZER TEST")
    print("=" * 60)
    print(f"Sentence: {sentence}")
    print(f"Target word: {target_word}")
    print(f"Complexity: {complexity}")
    print()

    # Get API key from environment
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ No GEMINI_API_KEY found in environment")
        return

    print("🔄 Analyzing sentence...")

    try:
        # Get the prompt that will be sent to AI
        prompt = analyzer.prompt_builder.build_batch_prompt([sentence], target_word, complexity)
        print("\n" + "="*60)
        print("PROMPT SENT TO AI:")
        print("="*60)
        print(prompt)
        print("="*60 + "\n")

        # Analyze the sentence
        # Add debug logging to see what the parser is doing
        import logging
        logging.basicConfig(level=logging.DEBUG)
        
        result = analyzer.analyze_grammar(sentence, target_word, complexity, api_key)

        print("✅ Analysis completed!")
        print()

        # Let's also show what the AI actually returned
        print("RAW AI RESPONSE:")
        print("-" * 16)
        # We need to call the AI directly to see the raw response
        api = get_gemini_api()
        api.configure(api_key=api_key)
        response = api.generate_content(
            model=get_gemini_model(),
            contents=prompt
        )
        raw_ai_response = response.text
        print(raw_ai_response)
        print()

        print("GRAMMAR ANALYSIS RESULTS:")
        print("-" * 30)

        print(f"Language: {result.language_code}")
        print(f"Sentence: {result.sentence}")
        print(f"Target Word: {result.target_word}")
        print(f"Complexity: {result.complexity_level}")
        print(f"Confidence: {result.confidence_score}")
        print()

        print("WORD EXPLANATIONS:")
        print("-" * 20)
        for i, exp in enumerate(result.word_explanations, 1):
            word, role, color, meaning = exp
            print(f"{i}. {word}")
            print(f"   Role: {role}")
            print(f"   Color: {color}")
            print(f"   Meaning: {meaning}")
            print()

        print("HTML OUTPUT:")
        print("-" * 12)
        print(result.html_output)
        print()

        print("EXPLANATIONS:")
        print("-" * 12)
        if hasattr(result, 'explanations') and result.explanations:
            for key, value in result.explanations.items():
                print(f"{key}: {value}")
        else:
            print("No explanations available")

    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_arabic_output()