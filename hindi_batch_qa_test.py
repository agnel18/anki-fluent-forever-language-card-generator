#!/usr/bin/env python3
"""
Hindi Analyzer Batch QA Test Prototype
Tests 10 words in a single API call for efficiency
"""

import sys
import time
import json
import os
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from streamlit_app.language_analyzers.analyzers.hi_analyzer import HiAnalyzer

def create_batch_prompt(words: List[str]) -> str:
    """Create a batch analysis prompt for multiple words"""

    # Create sentence contexts for each word
    word_contexts = []
    for i, word in enumerate(words):
        if word in ['से', 'में', 'को', 'पर']:
            # Postpositions need context
            sentences = {
                'से': 'मैं स्कूल से आया।',  # I came from school.
                'में': 'वह कमरे में है।',    # He is in the room.
                'को': 'मैं उसे किताब दी।',   # I gave him the book.
                'पर': 'किताब मेज पर है।'     # The book is on the table.
            }
            sentence = sentences.get(word, f"यह {word} है।")
        else:
            sentence = f"यह {word} है।"  # "This is {word}."

        word_contexts.append(f"Word {i+1}: '{word}' in sentence: '{sentence}'")

    contexts_text = "\n".join(word_contexts)

    prompt = f"""Analyze these 10 Hindi words, each in their own sentence context. For each word, provide a complete grammar analysis.

{contexts_text}

For EACH word, return a JSON object with:
- word: the word being analyzed
- sentence: the sentence context
- grammatical_role: EXACTLY one of: pronoun, noun, verb, adjective, adverb, postposition, conjunction, interjection, other
- confidence_score: number between 0-1
- analysis_details: brief explanation

Return your response as a JSON array of 10 analysis objects:

[
  {{
    "word": "मैं",
    "sentence": "मैं स्कूल जाता हूँ।",
    "grammatical_role": "pronoun",
    "confidence_score": 0.95,
    "analysis_details": "First person singular pronoun"
  }},
  {{
    "word": "खाना",
    "sentence": "यह खाना है।",
    "grammatical_role": "noun",
    "confidence_score": 0.92,
    "analysis_details": "Masculine noun meaning food"
  }}
]

IMPORTANT:
- Analyze EVERY word individually in its sentence context
- grammatical_role must be EXACTLY one of the 9 allowed values
- confidence_score should reflect your certainty (0.0 to 1.0)
- Return ONLY the JSON array, no additional text"""

    return prompt

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

def test_true_batch_words(words: List[str], analyzer: HiAnalyzer, api_key: str) -> Dict[str, Any]:
    """Test a batch of words in a TRUE single API call"""

    print(f"\n🧪 Testing TRUE batch of {len(words)} words: {', '.join(words)}")

    # Create batch prompt
    batch_prompt = create_batch_prompt(words)

    try:
        # Make TRUE single API call for the entire batch
        print("📡 Making TRUE single batch API call...")
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
            max_tokens=4000
        )

        raw_response = response.choices[0].message.content
        print(f"📄 Raw AI response length: {len(raw_response)} characters")

        # Parse the batch response
        batch_results = parse_batch_response(raw_response)

        if not batch_results:
            print("❌ Failed to parse batch response")
            return {
                'error': 'Failed to parse batch response',
                'raw_response': raw_response[:500] + "..." if len(raw_response) > 500 else raw_response
            }

        print(f"✅ Parsed {len(batch_results)} word analyses from batch response")

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

        print(f"✅ TRUE batch complete in {end_time - start_time:.1f}s")
        print(f"📊 Results: {len(successful)}/{len(words)} successful")

        if failed:
            print(f"❌ Failures: {', '.join([f['word'] for f in failed])}")

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
        print(f"❌ TRUE batch test failed: {e}")
        return {
            'error': str(e),
            'batch_size': len(words),
            'results': []
        }

def validate_batch_equivalence(words: List[str], analyzer: HiAnalyzer, api_key: str) -> Dict[str, Any]:
    """Validate that batch results are equivalent to individual results"""

    print(f"\n🔍 VALIDATING BATCH EQUIVALENCE for {len(words)} words...")

    # Test with TRUE batch
    batch_results = test_true_batch_words(words, analyzer, api_key)
    if 'error' in batch_results:
        return {'error': f'Batch test failed: {batch_results["error"]}'}

    # Test with individual calls (limited sample for validation)
    print("\n📊 Comparing with individual testing...")
    individual_results = test_individual_words(words[:5], analyzer, api_key)  # Test first 5 for validation

    # Compare results
    batch_word_results = {r['word']: r for r in batch_results['results']}
    individual_word_results = {r['word']: r for r in individual_results['results']}

    comparison = []
    matches = 0
    total_compared = 0

    for word in words[:5]:  # Only compare the words we tested individually
        if word in batch_word_results and word in individual_word_results:
            total_compared += 1
            batch_role = batch_word_results[word].get('grammatical_role', 'unknown')
            individual_role = individual_word_results[word].get('grammatical_role', 'unknown')

            match = batch_role == individual_role
            if match:
                matches += 1

            comparison.append({
                'word': word,
                'batch_role': batch_role,
                'individual_role': individual_role,
                'match': match
            })

    equivalence_rate = matches / total_compared if total_compared > 0 else 0

    print(f"🎯 Equivalence validation: {matches}/{total_compared} matches ({equivalence_rate:.1%})")

    return {
        'batch_results': batch_results,
        'individual_results': individual_results,
        'comparison': comparison,
        'equivalence_rate': equivalence_rate,
        'is_equivalent': equivalence_rate >= 0.95  # 95% threshold
    }

def test_individual_words(words: List[str], analyzer: HiAnalyzer, api_key: str) -> Dict[str, Any]:
    """Test words individually for comparison"""

    print(f"🔬 Testing {len(words)} words individually...")

    results = []
    for i, word in enumerate(words):
        print(f"  {i+1}/{len(words)}: {word}")
        time.sleep(1)  # Rate limiting

        # Create sentence context
        if word in ['से', 'में', 'को', 'पर']:
            sentences = {
                'से': 'मैं स्कूल से आया।',
                'में': 'वह कमरे में है।',
                'को': 'मैं उसे किताब दी।',
                'पर': 'किताब मेज पर है।'
            }
            sentence = sentences.get(word, f"यह {word} है।")
        else:
            sentence = f"यह {word} है।"

        try:
            result = analyzer.analyze_grammar(
                sentence=sentence,
                target_word=word,
                complexity="beginner",
                groq_api_key=api_key
            )

            # Extract grammatical role
            grammatical_elements = result.grammatical_elements
            grammatical_role = 'unknown'

            for category, words_list in grammatical_elements.items():
                for word_data in words_list:
                    if word_data.get('word') == word:
                        grammatical_role = word_data.get('grammatical_role', 'unknown')
                        break
                if grammatical_role != 'unknown':
                    break

            results.append({
                'word': word,
                'sentence': sentence,
                'grammatical_role': grammatical_role,
                'confidence_score': result.confidence_score,
                'analysis_details': f"Confidence: {result.confidence_score}",
                'success': result.confidence_score >= 0.85
            })

        except Exception as e:
            results.append({
                'word': word,
                'sentence': sentence,
                'error': str(e),
                'success': False
            })

    successful = [r for r in results if r.get('success', False)]
    failed = [r for r in results if not r.get('success', False)]

    return {
        'api_calls_used': len(words),
        'results': results,
        'successful': successful,
        'failed': failed,
        'success_rate': len(successful) / len(words)
    }

def main():
    """Run batch QA test with equivalence validation"""

    # Test words (balanced across categories)
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
        'काम'      # noun/verb homonym
    ]

    # Initialize analyzer
    analyzer = HiAnalyzer()

    # Get API key
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("❌ GROQ_API_KEY environment variable not set")
        return

    print("🚀 Starting Hindi Analyzer TRUE Batch QA Test with Equivalence Validation")
    print(f"📝 Testing {len(test_words)} words: {', '.join(test_words)}")

    # Run equivalence validation
    validation_results = validate_batch_equivalence(test_words, analyzer, api_key)

    if 'error' in validation_results:
        print(f"❌ Validation failed: {validation_results['error']}")
        return

    # Extract batch results
    batch_results = validation_results['batch_results']

    # Save comprehensive results
    output_file = f"true_batch_qa_results_{int(time.time())}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(validation_results, f, ensure_ascii=False, indent=2)

    print(f"\n💾 Comprehensive results saved to: {output_file}")

    # Summary
    if 'success_rate' in batch_results:
        print(".1%")
        print(f"🔄 API Efficiency: {batch_results['api_calls_used']} call for {len(test_words)} words")
        print(f"⚡ Time: {batch_results['time_taken']:.1f}s")

        equivalence_rate = validation_results.get('equivalence_rate', 0)
        print(".1%")

        if validation_results.get('is_equivalent', False):
            print("✅ BATCH EQUIVALENCE CONFIRMED - Ready for 20-word expansion!")
        else:
            print("⚠️ BATCH EQUIVALENCE NOT CONFIRMED - Need investigation before scaling")

        print(f"🎯 Next steps: {'✅ Scale to 20 words' if batch_results['success_rate'] >= 0.8 and validation_results.get('is_equivalent', False) else '⚠️ Investigate issues before expanding'}")

if __name__ == "__main__":
    main()