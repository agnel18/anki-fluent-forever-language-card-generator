#!/usr/bin/env python3
"""
Hindi Analyzer Failure Batching QA System
Accumulates failures across batches and processes them in optimized groups of 10
"""

import sys
import time
import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from streamlit_app.language_analyzers.analyzers.hi_analyzer import HiAnalyzer

class FailureBatchManager:
    """Manages failure accumulation and batching across QA testing sessions"""

    def __init__(self, failure_threshold: int = 10):
        self.failure_threshold = failure_threshold
        self.failure_queue: List[Dict[str, Any]] = []
        self.session_stats = {
            'primary_batches': 0,
            'failure_batches': 0,
            'individual_retries': 0,
            'total_api_calls': 0,
            'words_processed': 0,
            'words_successful': 0,
            'words_failed': 0
        }

    def add_failures(self, failures: List[Dict[str, Any]]) -> None:
        """Add failed words to the accumulation queue"""
        self.failure_queue.extend(failures)
        self.session_stats['words_failed'] += len(failures)

    def should_process_failure_batch(self) -> bool:
        """Check if we have enough failures to process a batch"""
        return len(self.failure_queue) >= self.failure_threshold

    def get_failure_batch(self) -> List[Dict[str, Any]]:
        """Get next batch of failures to process (up to threshold)"""
        if not self.should_process_failure_batch():
            return []

        # Take first N failures
        batch = self.failure_queue[:self.failure_threshold]
        # Remove them from queue
        self.failure_queue = self.failure_queue[self.failure_threshold:]

        return batch

    def get_remaining_failures(self) -> List[Dict[str, Any]]:
        """Get any remaining failures that didn't reach threshold"""
        return self.failure_queue.copy()

    def update_stats(self, primary_successful: int, primary_failed: int,
                    failure_batch_successful: int = 0, individual_successful: int = 0) -> None:
        """Update session statistics"""
        self.session_stats['words_successful'] += primary_successful + failure_batch_successful + individual_successful
        # Note: words_failed is updated in add_failures()

    def get_efficiency_metrics(self) -> Dict[str, float]:
        """Calculate current efficiency metrics"""
        total_words = self.session_stats['words_processed']
        total_api_calls = self.session_stats['total_api_calls']

        if total_api_calls == 0:
            return {'api_efficiency': 0.0}

        return {
            'api_efficiency': round(total_words / total_api_calls, 2),
            'success_rate': round(self.session_stats['words_successful'] / total_words, 3) if total_words > 0 else 0.0,
            'failure_rate': round(self.session_stats['words_failed'] / total_words, 3) if total_words > 0 else 0.0
        }

def test_single_word(word: str, analyzer: HiAnalyzer, api_key: str) -> Dict[str, Any]:
    """Test a single word and return results (copied from existing implementation)"""
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

def create_batch_prompt(words: List[str], is_failure_batch: bool = False) -> str:
    """Create optimized batch prompt for primary or failure batches - Phase 11 Enhanced"""
    if is_failure_batch:
        # Specialized prompt for words that failed analysis - Enhanced for Phase 11
        prompt = f"""Analyze the grammatical roles of these {len(words)} Hindi words that previously failed analysis. These words need special attention for accurate categorization.

Words to analyze: {', '.join(words)}

CRITICAL HINDI GRAMMAR GUIDANCE:
- Postpositions (में, से, को, का, पर, तक, के, ने) = "postposition" (NOT "preposition" or "other")
- Pronouns (मैं, तू, यह, वह, ये, वे, कौन) = "pronoun"
- Question words (क्या, कौन, कैसे, क्यों, कहाँ) = "pronoun" or "other" based on function
- Conjunctions (और, पर, लेकिन, या, क्योंकि) = "conjunction"
- Interjections (अरे, हाय, वाह, ओह) = "interjection"

For EACH word, create a meaningful, natural Hindi sentence and analyze its grammatical role.

Return a JSON array where each object has:
- word: the Hindi word (exact match required)
- sentence: a meaningful sentence using the word naturally
- grammatical_role: USE ONLY - noun, verb, adjective, adverb, pronoun, postposition, conjunction, interjection, particle, other
- confidence_score: 0.0-1.0 (be conservative - use 0.9+ only for obvious cases)
- analysis_details: brief explanation of the grammatical role and usage context

IMPORTANT: Pay special attention to postpositions and pronouns - these are commonly misclassified."""
    else:
        # Enhanced primary batch prompt - Phase 11 improvements
        prompt = f"""Analyze the grammatical roles of these {len(words)} Hindi words for language learning. Focus on accurate categorization and natural sentence creation.

Words to analyze: {', '.join(words)}

HINDI GRAMMAR CLASSIFICATION RULES:
- Postpositions (में, से, को, का, पर, तक, के, ने, की, का) → "postposition"
- Personal pronouns (मैं, तू, यह, वह, ये, वे, हम, तुम, आप) → "pronoun"
- Question pronouns (क्या, कौन, कैसे, क्यों, कहाँ, कब, कितना) → "pronoun"
- Conjunctions (और, पर, लेकिन, या, क्योंकि, इसलिए, फिर) → "conjunction"
- Interjections (अरे, हाय, वाह, ओह, अहा) → "interjection"
- Verbs (खाना, जाना, करना, होना, देना, लेना) → "verb"
- Nouns (घर, पानी, किताब, आदमी, औरत) → "noun"
- Adjectives (अच्छा, बड़ा, लाल, तेज) → "adjective"
- Adverbs (तेजी से, धीरे, बहुत, कम) → "adverb"

For EACH word, create a meaningful, natural Hindi sentence and determine its grammatical role.

Return a JSON array where each object has:
- word: the Hindi word (exact string match required)
- sentence: a natural Hindi sentence using the word appropriately
- grammatical_role: specific category from the list above
- confidence_score: 0.0-1.0 (use 0.85-0.95 for most cases, reserve 0.95+ for very clear cases)
- analysis_details: brief explanation of the grammatical role and contextual usage

Focus on creating sentences that clearly demonstrate the word's grammatical function."""

    return prompt

def process_batch(words: List[str], analyzer: HiAnalyzer, api_key: str,
                 is_failure_batch: bool = False) -> Dict[str, Any]:
    """Process a batch of words and return results"""
    import groq

    try:
        client = groq.Groq(api_key=api_key)
        prompt = create_batch_prompt(words, is_failure_batch)

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Updated to supported model
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=4000
        )

        raw_response = response.choices[0].message.content

        # Parse JSON response
        try:
            # Try to extract JSON from markdown or direct JSON
            import re
            json_match = re.search(r'```(?:json)?\s*\n(.*?)\n```', raw_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try direct JSON
                json_match = re.search(r'\[.*\]', raw_response, re.DOTALL)
                json_str = json_match.group(0) if json_match else raw_response

            parsed_results = json.loads(json_str)

            # Validate and structure results
            successful = []
            failed = []

            for result in parsed_results:
                word = result.get('word', '')
                confidence = result.get('confidence_score', 0.0)

                if confidence >= 0.85 and word in words:
                    successful.append({
                        'word': word,
                        'sentence': result.get('sentence', f'यह {word} है।'),
                        'grammatical_role': result.get('grammatical_role', 'other'),
                        'confidence_score': confidence,
                        'analysis_details': result.get('analysis_details', ''),
                        'success': True
                    })
                else:
                    failed.append({
                        'word': word,
                        'sentence': result.get('sentence', f'यह {word} है।'),
                        'grammatical_role': result.get('grammatical_role', 'other'),
                        'confidence_score': confidence,
                        'analysis_details': result.get('analysis_details', ''),
                        'success': False
                    })

            return {
                'successful': successful,
                'failed': failed,
                'success_count': len(successful),
                'fail_count': len(failed),
                'total_count': len(words),
                'success_rate': len(successful) / len(words) if words else 0,
                'raw_response': raw_response,
                'is_failure_batch': is_failure_batch
            }

        except (json.JSONDecodeError, AttributeError) as e:
            return {
                'successful': [],
                'failed': [{'word': w, 'error': f'JSON parsing failed: {str(e)}', 'success': False} for w in words],
                'success_count': 0,
                'fail_count': len(words),
                'total_count': len(words),
                'success_rate': 0.0,
                'raw_response': raw_response,
                'is_failure_batch': is_failure_batch,
                'error': f'Failed to parse JSON response: {str(e)}'
            }

    except Exception as e:
        return {
            'successful': [],
            'failed': [{'word': w, 'error': str(e), 'success': False} for w in words],
            'success_count': 0,
            'fail_count': len(words),
            'total_count': len(words),
            'success_rate': 0.0,
            'is_failure_batch': is_failure_batch,
            'error': str(e)
        }

def process_failure_batch_individual(failures: List[Dict[str, Any]], analyzer: HiAnalyzer,
                                   api_key: str, batch_manager: FailureBatchManager) -> Dict[str, Any]:
    """Process remaining failures individually"""
    print(f"\n🔄 Processing {len(failures)} remaining failures individually...")

    successful = []
    still_failed = []

    for i, failure in enumerate(failures, 1):
        word = failure['word']
        print(f"  {i}/{len(failures)}: Retrying '{word}'...")

        result = test_single_word(word, analyzer, api_key)
        batch_manager.session_stats['individual_retries'] += 1
        batch_manager.session_stats['total_api_calls'] += 1

        if result['success']:
            successful.append(result)
            print(f"    ✅ SUCCESS: {word} -> {result.get('grammatical_role', 'unknown')}")
        else:
            still_failed.append(result)
            error_msg = result.get('error', 'Unknown error')
            print(f"    ❌ STILL FAILED: {word} -> {error_msg}")

        # Small delay to be respectful to API
        time.sleep(0.5)

    return {
        'successful': successful,
        'still_failed': still_failed,
        'success_count': len(successful),
        'fail_count': len(still_failed)
    }

def run_failure_batching_qa(word_list: List[str], analyzer: HiAnalyzer, api_key: str,
                           batch_size: int = 30, failure_threshold: int = 20) -> Dict[str, Any]:
    """Run comprehensive QA with failure batching optimization"""

    batch_manager = FailureBatchManager(failure_threshold)
    all_results = {
        'primary_batches': [],
        'failure_batches': [],
        'individual_retries': {'successful': [], 'still_failed': []},
        'session_stats': batch_manager.session_stats
    }

    print("🚀 Starting Failure Batching QA System")
    print(f"📊 Processing {len(word_list)} words in batches of {batch_size}")
    print(f"🎯 Failure threshold: {failure_threshold} words")
    print("=" * 60)

    # Process words in primary batches
    for i in range(0, len(word_list), batch_size):
        batch_words = word_list[i:i+batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (len(word_list) + batch_size - 1) // batch_size

        print(f"\n🔄 Primary Batch {batch_num}/{total_batches}: {len(batch_words)} words")

        # Process primary batch
        batch_result = process_batch(batch_words, analyzer, api_key, is_failure_batch=False)
        batch_manager.session_stats['primary_batches'] += 1
        batch_manager.session_stats['total_api_calls'] += 1
        batch_manager.session_stats['words_processed'] += len(batch_words)

        # Record results
        all_results['primary_batches'].append({
            'batch_num': batch_num,
            'words': batch_words,
            'results': batch_result
        })

        # Update stats
        batch_manager.update_stats(
            primary_successful=batch_result['success_count'],
            primary_failed=batch_result['fail_count']
        )

        # Add failures to queue
        batch_manager.add_failures(batch_result['failed'])

        # Display batch results
        success_rate = batch_result['success_rate']
        print(f"  ✅ Success: {batch_result['success_count']}/{batch_result['total_count']} ({success_rate:.1%})")
        print(f"  📊 Failures queued: {len(batch_manager.failure_queue)}/{failure_threshold}")

        # Check if we should process failure batch
        if batch_manager.should_process_failure_batch():
            failure_batch_words = batch_manager.get_failure_batch()
            failure_words = [f['word'] for f in failure_batch_words]

            print(f"\n🎯 Processing Failure Batch: {len(failure_words)} words")

            # Process failure batch
            failure_result = process_batch(failure_words, analyzer, api_key, is_failure_batch=True)
            batch_manager.session_stats['failure_batches'] += 1
            batch_manager.session_stats['total_api_calls'] += 1

            # Record failure batch results
            all_results['failure_batches'].append({
                'triggered_by_batch': batch_num,
                'words': failure_words,
                'results': failure_result
            })

            # Update stats
            batch_manager.update_stats(
                primary_successful=0,
                primary_failed=0,
                failure_batch_successful=failure_result['success_count']
            )

            # Add any new failures from failure batch to queue
            batch_manager.add_failures(failure_result['failed'])

            # Display failure batch results
            f_success_rate = failure_result['success_rate']
            print(f"  ✅ Failure Batch Success: {failure_result['success_count']}/{failure_result['total_count']} ({f_success_rate:.1%})")
            print(f"  📊 Remaining failures queued: {len(batch_manager.failure_queue)}")

    # Process any remaining failures individually
    remaining_failures = batch_manager.get_remaining_failures()
    if remaining_failures:
        print(f"\n🔄 Processing {len(remaining_failures)} remaining failures individually...")
        individual_results = process_failure_batch_individual(remaining_failures, analyzer, api_key, batch_manager)
        all_results['individual_retries'] = individual_results

        # Update final stats
        batch_manager.update_stats(
            primary_successful=0,
            primary_failed=0,
            individual_successful=individual_results['success_count']
        )

    # Calculate final metrics
    final_metrics = batch_manager.get_efficiency_metrics()
    all_results['final_metrics'] = final_metrics
    all_results['session_stats'] = batch_manager.session_stats

    return all_results

def generate_comprehensive_report(results: Dict[str, Any], word_list: List[str], 
                                batch_size: int = 30, failure_threshold: int = 20) -> Dict[str, Any]:
    """Generate comprehensive QA report with failure batching analysis"""

    stats = results['session_stats']
    metrics = results['final_metrics']

    # Compile all successful results
    all_successful = []
    all_failed = []

    # From primary batches
    for batch in results['primary_batches']:
        all_successful.extend(batch['results']['successful'])
        # Note: primary failures are processed in failure batches

    # From failure batches
    for batch in results['failure_batches']:
        all_successful.extend(batch['results']['successful'])

    # From individual retries
    all_successful.extend(results['individual_retries']['successful'])
    all_failed.extend(results['individual_retries']['still_failed'])

    # Calculate comprehensive statistics
    total_words = len(word_list)
    final_successful = len(all_successful)
    final_failed = len(all_failed)
    final_success_rate = final_successful / total_words if total_words > 0 else 0

    # API efficiency analysis
    primary_api_calls = stats['primary_batches']
    failure_api_calls = stats['failure_batches']
    individual_api_calls = stats['individual_retries']
    total_api_calls = stats['total_api_calls']
    api_efficiency = metrics['api_efficiency']

    report = {
        'timestamp': datetime.now().isoformat(),
        'test_type': 'failure_batching_qa',
        'word_list_size': total_words,
        'batch_size': batch_size,
        'failure_threshold': failure_threshold,

        'summary': {
            'total_words_tested': total_words,
            'final_successful': final_successful,
            'final_failed': final_failed,
            'final_success_rate': round(final_success_rate, 3),
            'api_calls': {
                'primary_batches': primary_api_calls,
                'failure_batches': failure_api_calls,
                'individual_retries': individual_api_calls,
                'total_calls': total_api_calls,
                'api_efficiency': api_efficiency
            },
            'processing_stats': {
                'primary_batches_processed': len(results['primary_batches']),
                'failure_batches_processed': len(results['failure_batches']),
                'individual_retries_performed': stats['individual_retries']
            }
        },

        'results': {
            'successful': all_successful,
            'failed': all_failed
        },

        'batch_details': {
            'primary_batches': results['primary_batches'],
            'failure_batches': results['failure_batches']
        },

        'efficiency_analysis': {
            'traditional_approach': {
                'api_calls': total_words,  # 1 call per word
                'efficiency': 1.0
            },
            'current_system': {
                'api_calls': total_api_calls,
                'efficiency': api_efficiency,
                'improvement': round(api_efficiency - 1.0, 2)
            }
        }
    }

    return report

def save_report(report: Dict[str, Any], output_file: str) -> None:
    """Save comprehensive report to JSON file"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"💾 Report saved to: {output_file}")
    except Exception as e:
        print(f"❌ Error saving report: {e}")

def main():
    """Main failure batching QA function"""
    print("🚀 Hindi Analyzer Failure Batching QA System")
    print("=" * 60)

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

    # Load top 1000 Hindi single words from frequency list
    try:
        with open('top_1000_hindi_single_words.json', 'r', encoding='utf-8') as f:
            test_words = json.load(f)
        print(f"✅ Loaded {len(test_words)} single words from frequency list")
    except FileNotFoundError:
        print("⚠️  Single word frequency list not found, using test subset")
        # Fallback to test subset
        test_words = [
            'मैं', 'खाना', 'खाता', 'अच्छा', 'तेजी', 'में', 'और', 'अरे', 'को', 'काम',
            'पानी', 'पीता', 'बड़ा', 'धीरे', 'से', 'पर', 'का', 'है', 'नहीं', 'सब',
            'दो', 'तीन', 'चार', 'पाँच', 'छह', 'सात', 'आठ', 'नौ', 'दस', 'बीस',
            'तीस', 'चालीस', 'पचास', 'साठ', 'सत्तर', 'अस्सी', 'नब्बे', 'सौ', 'हज़ार', 'लाख',
            'करोड़', 'आना', 'पैसा', 'रुपया', 'टका', 'पैसे', 'दाम', 'कीमत', 'महँगा', 'सस्ता',
            'खरीदना', 'बेचना', 'लेना', 'देना', 'देना', 'लाना', 'ले जाना', 'भेजना', 'मिलना', 'पाना',
            'खोजना', 'ढूँढना', 'पाना', 'गँवाना', 'छोड़ना', 'रखना', 'उठाना', 'बैठना', 'खड़ा होना', 'लेटना',
            'सोना', 'जागना', 'आना', 'जाना', 'चलना', 'दौड़ना', 'कूदना', 'उड़ना', 'तैरना', 'चढ़ना',
            'उतरना', 'घूमना', 'मिलना', 'बताना', 'पूछना', 'कहना', 'सुनना', 'देखना', 'सोचना', 'समझना',
            'जानना', 'भूलना', 'याद करना', 'सीखना', 'पढ़ना', 'लिखना', 'गाना', 'नाचना', 'खेलना', 'काम करना'
        ]

    print(f"📊 Testing {len(test_words)} words with failure batching optimization")

    # Run failure batching QA
    start_time = time.time()
    results = run_failure_batching_qa(test_words, analyzer, api_key,
                                     batch_size=30, failure_threshold=20)
    end_time = time.time()

    # Generate comprehensive report
    print("\n📋 Generating comprehensive QA report...")
    report = generate_comprehensive_report(results, test_words, batch_size=30, failure_threshold=20)

    # Display final results
    summary = report['summary']
    efficiency = report['efficiency_analysis']['current_system']

    print("\n🎯 FAILURE BATCHING QA RESULTS:")
    print(f"  Total Words: {summary['total_words_tested']}")
    print(f"  Final Success: {summary['final_successful']}/{summary['total_words_tested']} ({summary['final_success_rate']:.1%})")
    print(f"  API Calls: {summary['api_calls']['total_calls']} ({summary['api_calls']['primary_batches']} primary + {summary['api_calls']['failure_batches']} failure + {summary['api_calls']['individual_retries']} individual)")
    print(f"  API Efficiency: {efficiency['efficiency']:.1f}x (words per API call)")
    print(f"  Improvement: {efficiency['improvement']:.1f}x over individual testing")
    print(f"  Processing Time: {end_time - start_time:.1f} seconds")

    if summary['final_failed'] > 0:
        print(f"\n⚠️  {summary['final_failed']} words still failing after all retry attempts")
    else:
        print("\n🎉 All words successfully analyzed!")

    # Save report
    timestamp = int(time.time())
    output_file = f"failure_batching_qa_results_{timestamp}.json"
    save_report(report, output_file)

    print("\n✅ Failure Batching QA completed!")
    print(f"📄 Full report saved to: {output_file}")

if __name__ == "__main__":
    main()