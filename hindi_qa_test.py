#!/usr/bin/env python3
"""
Hindi Analyzer Quality Assurance Test
Tests 20 balanced words across grammatical categories
"""

import sys
import time
import json
import os
from pathlib import Path

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

def main():
    # Test words organized by category
    test_words = {
        'postpositions': ['से', 'में', 'को', 'पर'],
        'verbs': ['होना', 'करना', 'खाना', 'देना'],
        'nouns': ['परीक्षा', 'मेहनत', 'खाना', 'काम'],
        'pronouns': ['मैं', 'तुम', 'यह', 'वह'],
        'other_particles': ['ही', 'भी', 'और', 'नहीं']
    }

    # Expected results
    expected_roles = {
        'postpositions': 'postposition',
        'verbs': 'verb',
        'nouns': 'noun',
        'pronouns': 'pronoun',
        'other_particles': 'adverb'  # Most particles are adverbs in Hindi
    }

    expected_colors = {
        'postpositions': '#4444FF',  # Blue
        'verbs': '#44FF44',          # Green
        'nouns': '#FFAA00',          # Orange
        'pronouns': '#FF4444',       # Red
        'other_particles': '#44FFFF' # Cyan (adverb color)
    }

    print("🔍 Hindi Analyzer Quality Assurance Test")
    print("=" * 50)
    print(f"Testing {sum(len(words) for words in test_words.values())} words across {len(test_words)} categories")
    print()

    # Get API key from environment or prompt
    api_key = os.getenv('GROQ_API_KEY', '').strip()
    if not api_key:
        api_key = input("Enter Groq API key: ").strip()
    if not api_key:
        print("❌ No API key provided")
        return

    # Initialize analyzer
    analyzer = HiAnalyzer()

    results = []
    total_tests = 0
    correct_classifications = 0
    correct_colors = 0

    # Test each category
    for category, words in test_words.items():
        print(f"\n📂 Testing {category.upper()} ({len(words)} words)")
        print("-" * 30)

        for word in words:
            total_tests += 1
            print(f"Testing: {word} ... ", end="", flush=True)

            result = test_single_word(word, analyzer, api_key)
            results.append(result)

            if result['success']:
                actual_role = result['grammatical_role']
                actual_color = result['color']
                expected_role = expected_roles[category]
                expected_color = expected_colors[category]

                # Check classification
                role_correct = actual_role == expected_role
                if category == 'other_particles':
                    # For particles, accept 'adverb' or other particle roles
                    role_correct = actual_role in ['adverb', 'particle', 'interrogative particle', 'conjunction', 'interjection']

                # Check color
                color_correct = actual_color == expected_color

                if role_correct:
                    correct_classifications += 1
                    print("✅", end="")
                else:
                    print("❌", end="")

                if color_correct:
                    correct_colors += 1
                    print("🎨", end="")
                else:
                    print("💔", end="")

                print(f" | Role: {actual_role} | Color: {actual_color}")

                if not role_correct:
                    print(f"   Expected role: {expected_role}")
                if not color_correct:
                    print(f"   Expected color: {expected_color}")

            else:
                print(f"❌ FAILED: {result.get('error', 'Unknown error')}")

            # Rate limiting
            time.sleep(2)

    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)

    accuracy = (correct_classifications / total_tests) * 100 if total_tests > 0 else 0
    color_accuracy = (correct_colors / total_tests) * 100 if total_tests > 0 else 0

    print(f"Total words tested: {total_tests}")
    print(".1f")
    print(".1f")

    # Category breakdown
    print("\n📈 CATEGORY BREAKDOWN")
    print("-" * 30)

    category_results = {}
    for result in results:
        if not result['success']:
            continue
        # Find which category this word belongs to
        for cat, words in test_words.items():
            if result['word'] in words:
                if cat not in category_results:
                    category_results[cat] = {'total': 0, 'correct': 0, 'color_correct': 0}
                category_results[cat]['total'] += 1

                expected_role = expected_roles[cat]
                actual_role = result['grammatical_role']
                role_correct = actual_role == expected_role
                if cat == 'other_particles':
                    role_correct = actual_role in ['other', 'particle', 'interrogative particle', 'conjunction', 'interjection']

                expected_color = expected_colors[cat]
                actual_color = result['color']
                color_correct = actual_color == expected_color

                if role_correct:
                    category_results[cat]['correct'] += 1
                if color_correct:
                    category_results[cat]['color_correct'] += 1
                break

    for category, stats in category_results.items():
        cat_accuracy = (stats['correct'] / stats['total']) * 100 if stats['total'] > 0 else 0
        cat_color_accuracy = (stats['color_correct'] / stats['total']) * 100 if stats['total'] > 0 else 0
        print(f"{category.capitalize()}: {stats['correct']}/{stats['total']} ({cat_accuracy:.1f}%) classifications, {stats['color_correct']}/{stats['total']} ({cat_color_accuracy:.1f}%) colors")

    # Save detailed results
    with open('hindi_qa_test_results.json', 'w', encoding='utf-8') as f:
        json.dump({
            'summary': {
                'total_tests': total_tests,
                'accuracy': accuracy,
                'color_accuracy': color_accuracy,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            },
            'category_results': category_results,
            'detailed_results': results
        }, f, ensure_ascii=False, indent=2)

    print(f"\n📄 Detailed results saved to hindi_qa_test_results.json")

    # Final assessment
    if accuracy >= 85:
        print("✅ PASSED: Analyzer meets 85% accuracy target")
    else:
        print("❌ FAILED: Analyzer below 85% accuracy target")

    if color_accuracy >= 85:
        print("✅ PASSED: Color consistency maintained")
    else:
        print("❌ FAILED: Color consistency issues detected")

if __name__ == "__main__":
    main()