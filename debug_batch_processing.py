#!/usr/bin/env python3
"""
Debug batch processing issues in failure batching QA
"""

import sys
import json
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from streamlit_app.language_analyzers.analyzers.hi_analyzer import HiAnalyzer

def debug_batch_processing():
    """Debug why batch processing is failing"""

    # Get API key
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("❌ GROQ_API_KEY not set")
        return

    # Initialize analyzer
    analyzer = HiAnalyzer()
    print("✅ Hindi Analyzer initialized")

    # Test words
    test_words = ['मैं', 'खाना', 'खाता', 'अच्छा', 'तेजी']

    print(f"🧪 Testing batch processing with {len(test_words)} words...")

    # Test the batch processing directly
    import groq

    try:
        client = groq.Groq(api_key=api_key)

        # Create batch prompt
        prompt = f"""Analyze the grammatical roles of these {len(test_words)} Hindi words. For natural language learning, it's important to understand how words function in context.

Words to analyze: {', '.join(test_words)}

For EACH word, create a meaningful sentence and determine its grammatical role.

Return a JSON array where each object has:
- word: the Hindi word
- sentence: a meaningful sentence using the word
- grammatical_role: specific grammatical category (noun, verb, adjective, adverb, pronoun, postposition, conjunction, interjection, particle, other)
- confidence_score: 0.0-1.0 based on certainty
- analysis_details: brief explanation of the grammatical role and usage

Focus on accuracy and contextual appropriateness."""

        print("📤 Sending batch request...")
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Updated to supported model
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=4000
        )

        raw_response = response.choices[0].message.content
        print("📥 Raw AI response:")
        print("=" * 50)
        print(raw_response[:1000] + "..." if len(raw_response) > 1000 else raw_response)
        print("=" * 50)

        # Try to parse JSON
        print("🔍 Attempting JSON parsing...")

        # Try markdown extraction first
        import re
        json_match = re.search(r'```(?:json)?\s*\n(.*?)\n```', raw_response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
            print("✅ Found markdown-wrapped JSON")
        else:
            # Try direct JSON
            json_match = re.search(r'\[.*\]', raw_response, re.DOTALL)
            json_str = json_match.group(0) if json_match else raw_response
            print("📝 Using direct JSON extraction")

        print("📄 Extracted JSON string:")
        print(json_str[:500] + "..." if len(json_str) > 500 else json_str)

        try:
            parsed_results = json.loads(json_str)
            print(f"✅ Successfully parsed {len(parsed_results)} results")

            # Analyze results
            successful = []
            failed = []

            for result in parsed_results:
                word = result.get('word', '')
                confidence = result.get('confidence_score', 0.0)

                if confidence >= 0.85 and word in test_words:
                    successful.append(result)
                    print(f"  ✅ {word}: {result.get('grammatical_role', 'unknown')} ({confidence})")
                else:
                    failed.append(result)
                    print(f"  ❌ {word}: {result.get('grammatical_role', 'unknown')} ({confidence}) - FAILED")

            print("\n📊 Batch Results:")
            print(f"  Successful: {len(successful)}/{len(test_words)}")
            print(f"  Failed: {len(failed)}/{len(test_words)}")

        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {e}")
            print("This explains why batch processing returned 0% success!")

    except Exception as e:
        print(f"❌ API call failed: {e}")

if __name__ == "__main__":
    debug_batch_processing()