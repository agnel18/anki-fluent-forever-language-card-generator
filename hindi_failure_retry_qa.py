#!/usr/bin/env python3
"""
Hindi Analyzer Failure-Only Retry QA System
Retries failed words from batch testing individually for comprehensive QA coverage
"""

import sys
import time
import json
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from streamlit_app.language_analyzers.analyzers.hi_analyzer import HiAnalyzer

def test_single_word(word, analyzer, api_key):
    """Test a single word and return results"""
    try:
        # Create a more meaningful sentence with the word
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

        result = analyzer.analyze_grammar(
            sentence=sentence,
            target_word=word,
            complexity="beginner",
            groq_api_key=api_key
        )

        # Check confidence score
        if result.confidence_score < 0.85:
            return {
                'word': word,
                'sentence': sentence,
                'error': f'Analysis confidence too low: {result.confidence_score}',
                'success': False
            }

        # Find the target word in grammatical_elements
        word_data = None
        actual_role = None
        actual_color = None

        for role, words in result.grammatical_elements.items():
            for word_info in words:
                if isinstance(word_info, dict) and word_info.get('word') == word:
                    word_data = word_info
                    actual_role = role
                    # Get color from color scheme
                    category = analyzer._map_grammatical_role_to_category(role) if hasattr(analyzer, '_map_grammatical_role_to_category') else role.lower()
                    actual_color = result.color_scheme.get(category, '#888888')
                    break
            if word_data:
                break

        if word_data:
            explanation = result.explanations.get(word, f"{actual_role}")
            return {
                'word': word,
                'sentence': sentence,
                'grammatical_role': actual_role,
                'color': actual_color,
                'explanation': explanation,
                'confidence': result.confidence_score,
                'success': True
            }
        else:
            return {
                'word': word,
                'sentence': sentence,
                'error': 'Word not found in grammatical elements',
                'confidence': result.confidence_score,
                'success': False
            }

    except Exception as e:
        return {
            'word': word,
            'sentence': sentence if 'sentence' in locals() else f"यह {word} है।",
            'error': str(e),
            'success': False
        }

def load_batch_results(json_file_path):
    """Load batch test results from JSON file"""
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading batch results: {e}")
        return None

def retry_failed_words(failed_words, analyzer, api_key):
    """Retry failed words individually"""
    print(f"\n🔄 Retrying {len(failed_words)} failed words individually...")

    retry_results = []
    successful_retries = []
    still_failed = []

    for i, word_data in enumerate(failed_words, 1):
        word = word_data['word']
        print(f"  {i}/{len(failed_words)}: Retrying '{word}'...")

        # Use the individual test function
        result = test_single_word(word, analyzer, api_key)

        retry_results.append(result)

        if result['success']:
            successful_retries.append(result)
            print(f"    ✅ SUCCESS: {word} -> {result.get('grammatical_role', 'unknown')}")
        else:
            still_failed.append(result)
            error_msg = result.get('error', 'Unknown error')
            print(f"    ❌ STILL FAILED: {word} -> {error_msg}")

        # Small delay to be respectful to API
        time.sleep(0.5)

    return retry_results, successful_retries, still_failed

def generate_comprehensive_report(batch_results, retry_results, successful_retries, still_failed):
    """Generate comprehensive QA report combining batch and retry results"""

    # Combine successful results
    all_successful = batch_results['successful'] + successful_retries

    # Calculate final statistics
    total_words = len(batch_results['successful']) + len(batch_results['failed'])
    final_successful = len(all_successful)
    final_failed = len(still_failed)
    final_success_rate = final_successful / total_words if total_words > 0 else 0

    # API efficiency metrics
    batch_api_calls = 1  # One batch call for all words
    retry_api_calls = len(retry_results)  # One call per retry
    total_api_calls = batch_api_calls + retry_api_calls
    api_efficiency = total_words / total_api_calls if total_api_calls > 0 else 0

    report = {
        'timestamp': datetime.now().isoformat(),
        'test_type': 'failure_retry_qa',
        'batch_results_file': batch_results.get('source_file', 'unknown'),
        'summary': {
            'total_words_tested': total_words,
            'batch_successful': len(batch_results['successful']),
            'batch_failed': len(batch_results['failed']),
            'batch_success_rate': batch_results['success_rate'],
            'retries_attempted': len(retry_results),
            'retries_successful': len(successful_retries),
            'retries_failed': len(still_failed),
            'final_successful': final_successful,
            'final_failed': final_failed,
            'final_success_rate': round(final_success_rate, 3),
            'api_calls': {
                'batch_calls': batch_api_calls,
                'retry_calls': retry_api_calls,
                'total_calls': total_api_calls,
                'api_efficiency': round(api_efficiency, 2)
            }
        },
        'successful_results': all_successful,
        'failed_results': still_failed,
        'retry_details': retry_results,
        'failure_analysis': {
            'batch_failures': batch_results['failed'],
            'retry_successes': successful_retries,
            'persistent_failures': still_failed
        }
    }

    return report

def save_report(report, output_file):
    """Save comprehensive report to JSON file"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"💾 Report saved to: {output_file}")
    except Exception as e:
        print(f"❌ Error saving report: {e}")

def main():
    """Main failure retry QA function"""
    print("🚀 Hindi Analyzer Failure-Only Retry QA System")
    print("=" * 50)

    # Get API key
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("❌ GROQ_API_KEY environment variable not set")
        return

    # Initialize analyzer
    try:
        analyzer = HiAnalyzer()
        print("✅ Hindi Analyzer initialized")
    except Exception as e:
        print(f"❌ Failed to initialize analyzer: {e}")
        return

    # Load latest batch results
    batch_files = list(Path('.').glob('20_word_batch_qa_results_*.json'))
    if not batch_files:
        print("❌ No batch results files found")
        return

    # Get most recent batch file
    latest_batch_file = max(batch_files, key=lambda f: f.stat().st_mtime)
    print(f"📂 Loading batch results from: {latest_batch_file}")

    batch_results = load_batch_results(latest_batch_file)
    if not batch_results:
        return

    batch_results['source_file'] = str(latest_batch_file)

    # Extract failed words
    failed_words = batch_results['failed']
    print(f"📊 Batch testing found {len(failed_words)} failed words")

    if not failed_words:
        print("✅ No failed words to retry - all batch tests passed!")
        return

    # Retry failed words individually
    retry_results, successful_retries, still_failed = retry_failed_words(
        failed_words, analyzer, api_key
    )

    # Generate comprehensive report
    print("\n📋 Generating comprehensive QA report...")
    report = generate_comprehensive_report(
        batch_results, retry_results, successful_retries, still_failed
    )

    # Display summary
    summary = report['summary']
    print("\n🎯 COMPREHENSIVE QA RESULTS:")
    print(f"  Total Words: {summary['total_words_tested']}")
    print(f"  Batch Success: {summary['batch_successful']}/{summary['total_words_tested']} ({summary['batch_success_rate']:.1%})")
    print(f"  Retry Success: {summary['retries_successful']}/{summary['retries_attempted']} ({summary['retries_successful']/summary['retries_attempted']:.1%} of retries)")
    print(f"  Final Success: {summary['final_successful']}/{summary['total_words_tested']} ({summary['final_success_rate']:.1%})")
    print(f"  API Efficiency: {summary['api_calls']['api_efficiency']:.1f}x (words per API call)")

    if still_failed:
        print(f"\n⚠️  {len(still_failed)} words still failing after retry:")
        for failure in still_failed:
            error = failure.get('error', 'Unknown error')
            print(f"    - {failure['word']}: {error}")
    else:
        print("\n🎉 All words now passing after retry!")

    # Save report
    timestamp = int(time.time())
    output_file = f"comprehensive_qa_results_{timestamp}.json"
    save_report(report, output_file)

    print("\n✅ Failure-only retry QA completed!")
    print(f"📄 Full report saved to: {output_file}")

if __name__ == "__main__":
    main()