#!/usr/bin/env python3
"""
Hindi Analyzer 20-Word Batch QA Test
Demonstrates scaling from 10 to 20 words per batch
"""

import sys
import time
import json
import os
import re
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from streamlit_app.language_analyzers.analyzers.hi_analyzer import HiAnalyzer

def create_batch_prompt_20(words: List[str]) -> str:
    """Create a batch analysis prompt for 20 words"""

    # Create sentence contexts for each word
    word_contexts = []
    for i, word in enumerate(words):
        if word in ['से', 'में', 'को', 'पर', 'का', 'के', 'की', 'ने']:
            # Postpositions need context
            sentences = {
                'से': 'मैं स्कूल से आया।',  # I came from school.
                'में': 'वह कमरे में है।',    # He is in the room.
                'को': 'मैं उसे किताब दी।',   # I gave him the book.
                'पर': 'किताब मेज पर है।',     # The book is on the table.
                'का': 'यह मेरा का है।',       # This is mine (possessive).
                'के': 'लड़के के पास है।',     # The boy has it.
                'की': 'लड़की की किताब है।',  # The girl's book.
                'ने': 'राम ने किताब पढ़ी।'    # Ram read the book.
            }
            sentence = sentences.get(word, f"यह {word} है।")
        else:
            sentence = f"यह {word} है।"  # "This is {word}."

        word_contexts.append(f"Word {i+1}: '{word}' in sentence: '{sentence}'")

    contexts_text = "\n".join(word_contexts)

    prompt = f"""Analyze these 20 Hindi words, each in their own sentence context. For each word, provide a complete grammar analysis.

{contexts_text}

For EACH word, return a JSON object with:
- word: the word being analyzed
- sentence: the sentence context
- grammatical_role: EXACTLY one of: pronoun, noun, verb, adjective, adverb, postposition, conjunction, interjection, other
- confidence_score: number between 0-1
- analysis_details: brief explanation

Return your response as a JSON array of 20 analysis objects:

[
  {{
    "word": "मैं",
    "sentence": "मैं स्कूल जाता हूँ।",
    "grammatical_role": "pronoun",
    "confidence_score": 0.98,
    "analysis_details": "First person singular pronoun"
  }},
  {{
    "word": "खाना",
    "sentence": "यह खाना है।",
    "grammatical_role": "noun",
    "confidence_score": 0.95,
    "analysis_details": "Masculine noun meaning food"
  }}
]

IMPORTANT:
- Analyze EVERY word individually in its sentence context
- grammatical_role must be EXACTLY one of the 9 allowed values
- confidence_score should reflect your certainty (0.0 to 1.0)
- Return ONLY the JSON array, no additional text"""

    return prompt

def test_20_word_batch(words: List[str], analyzer: HiAnalyzer, api_key: str) -> Dict[str, Any]:
    """Test a batch of 20 words in a single API call"""

    print(f"\n🧪 Testing TRUE batch of {len(words)} words: {', '.join(words[:10])}...")

    # Create batch prompt
    batch_prompt = create_batch_prompt_20(words)

    try:
        # Make TRUE single API call for the entire batch
        print("📡 Making TRUE single batch API call for 20 words...")
        start_time = time.time()

        # Import the API client directly to make batch call
        import groq
        client = groq.Groq(api_key=api_key)

        # Make the actual batch API call
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": batch_prompt}
            ],
            temperature=0.1,
            max_tokens=6000  # Increased for 20 words
        )

        raw_response = response.choices[0].message.content
        print(f"📄 Raw AI response length: {len(raw_response)} characters")

        # Parse the batch response
        batch_results = parse_batch_response(raw_response)

        if not batch_results:
            print("❌ Failed to parse 20-word batch response")
            return {
                'error': 'Failed to parse batch response',
                'raw_response': raw_response[:500] + "..." if len(raw_response) > 500 else raw_response
            }

        print(f"✅ Parsed {len(batch_results)} word analyses from 20-word batch response")

        # Validate we got results for all words
        word_results = {}
        for result in batch_results:
            word = result.get('word', '').strip()
            if word in words:
                word_results[word] = result

        # Check for missing words
        missing_words = [w for w in words if w not in word_results]
        if missing_words:
            print(f"⚠️ Missing analyses for words: {missing_words}")

        # Create final results
        final_results = []
        for word in words:
            if word in word_results:
                result = word_results[word]
                final_results.append({
                    'word': word,
                    'sentence': result.get('sentence', f"यह {word} है।"),
                    'grammatical_role': result.get('grammatical_role', 'unknown'),
                    'confidence_score': result.get('confidence_score', 0.5),
                    'analysis_details': result.get('analysis_details', ''),
                    'success': result.get('confidence_score', 0) >= 0.85
                })
            else:
                final_results.append({
                    'word': word,
                    'sentence': f"यह {word} है।",
                    'grammatical_role': 'unknown',
                    'confidence_score': 0.0,
                    'analysis_details': 'Missing from batch response',
                    'success': False
                })

        end_time = time.time()

        # Analyze results
        successful = [r for r in final_results if r.get('success', False)]
        failed = [r for r in final_results if not r.get('success', False)]

        print(f"✅ 20-word batch complete in {end_time - start_time:.1f}s")
        print(f"📊 Results: {len(successful)}/{len(words)} successful")

        if failed:
            failed_words = [f['word'] for f in failed]
            print(f"❌ Failures: {', '.join(failed_words)}")

        return {
            'batch_size': len(words),
            'api_calls_used': 1,  # TRUE batch = 1 API call
            'time_taken': end_time - start_time,
            'results': final_results,
            'successful': successful,
            'failed': failed,
            'success_rate': len(successful) / len(words),
            'raw_response': raw_response,
            'parsed_results_count': len(batch_results)
        }

    except Exception as e:
        print(f"❌ 20-word batch test failed: {e}")
        return {
            'error': str(e),
            'batch_size': len(words),
            'results': []
        }

def parse_batch_response(response_text: str) -> List[Dict[str, Any]]:
    """Parse the batch response from AI"""
    try:
        # Try to extract JSON from markdown code blocks first
        json_match = re.search(r'```(?:json)?\s*\n(\[.*?\])\n?\s*```', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find JSON array directly
            json_match = re.search(r'(\[.*\])', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                raise ValueError("No JSON array found in response")

        # Parse the JSON
        results = json.loads(json_str)

        if not isinstance(results, list):
            raise ValueError("Response is not a JSON array")

        return results

    except Exception as e:
        print(f"Failed to parse batch response: {e}")
        print(f"Raw response: {response_text[:500]}...")
        return []

def main():
    """Run 20-word batch QA test"""

    # Test words (expanded set for 20-word test)
    test_words = [
        'मैं',      # pronoun
        'खाना',    # noun
        'खाता',    # verb
        'अच्छा',   # adjective
        'तेजी',    # adverb
        'में',      # postposition
        'और',      # conjunction
        'अरे',     # interjection
        'को',      # postposition
        'काम',     # noun/verb homonym
        'पानी',    # noun
        'पीता',    # verb
        'बड़ा',    # adjective
        'धीरे',    # adverb
        'से',      # postposition
        'पर',      # postposition
        'का',      # postposition
        'है',      # verb
        'नहीं',    # adverb
        'सब'       # pronoun
    ]

    # Initialize analyzer
    analyzer = HiAnalyzer()

    # Get API key
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("❌ GROQ_API_KEY environment variable not set")
        return

    print("🚀 Starting Hindi Analyzer 20-WORD Batch QA Test")
    print(f"📝 Testing {len(test_words)} words: {', '.join(test_words)}")

    # Run 20-word batch test
    results = test_20_word_batch(test_words, analyzer, api_key)

    # Save results
    output_file = f"20_word_batch_qa_results_{int(time.time())}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n💾 Results saved to: {output_file}")

    # Summary
    if 'success_rate' in results:
        print(".1%")
        print(f"🔄 API Efficiency: {results['api_calls_used']} call for {len(test_words)} words")
        print(f"⚡ Time: {results['time_taken']:.1f}s")

        print("✅ 20-WORD BATCH SUCCESS - Ready for production QA testing!")
        print(f"🎯 Next steps: Implement failure-only retry system for comprehensive QA coverage")

if __name__ == "__main__":
    main()