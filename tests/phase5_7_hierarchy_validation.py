#!/usr/bin/env python3
# Phase 5.7: Grammatical Analysis Order Standardization - Validation Script
# Hindi Analyzer Hierarchical Categorization Test
# Created: January 4, 2026

"""
Validation script for Phase 5.7: Grammatical Analysis Order Standardization

This script tests the children-first hierarchical categorization in the Hindi analyzer
to ensure that overlapping grammatical categories are classified correctly.

TEST METHODOLOGY:
1. Load test sentences with known overlapping categories
2. Run Hindi analyzer on each sentence
3. Extract grammatical classifications for key words
4. Compare against expected classifications
5. Report pass/fail status and any mismatches

EXPECTED BEHAVIOR:
- Auxiliary verbs should be classified as 'auxiliary_verb' not 'verb'
- Postpositions should be classified as 'postposition' not 'preposition'
- Particles should be classified as 'particle' not 'conjunction'
- Ideophones should be classified as 'ideophone' not 'interjection'
- Specific pronoun subtypes should take precedence over general 'pronoun'
"""

import sys
import os
import json
from typing import Dict, List, Tuple

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from languages.hindi.hi_analyzer import HiAnalyzer
from tests.phase5_7_hierarchy_test_sentences import TEST_SENTENCES, EXPECTED_CLASSIFICATIONS

def test_hierarchical_categorization():
    """Test the children-first hierarchical categorization"""

    print("🧪 Phase 5.7: Grammatical Analysis Order Standardization - Validation")
    print("=" * 70)

    # Initialize analyzer
    analyzer = HiAnalyzer()

    # Track results
    total_tests = 0
    passed_tests = 0
    failed_tests = []

    # Test each sentence
    for i, sentence in enumerate(TEST_SENTENCES, 1):
        print(f"\n📝 Test Sentence {i}: '{sentence}'")
        print("-" * 50)

        try:
            # Analyze the sentence (using intermediate complexity for comprehensive analysis)
            analysis = analyzer.analyze_sentence(sentence, complexity="intermediate")

            if not analysis or 'words' not in analysis:
                print(f"❌ ERROR: Failed to analyze sentence {i}")
                failed_tests.append(f"Sentence {i}: Analysis failed")
                continue

            # Check classifications for words that have expected categories
            sentence_words = [word['word'] for word in analysis['words']]
            print(f"Analyzed words: {sentence_words}")

            # Find words that are in our expected classifications
            tested_words = []
            for expected_word, expected_category in EXPECTED_CLASSIFICATIONS.items():
                if expected_word in sentence:
                    tested_words.append((expected_word, expected_category))

            if not tested_words:
                print(f"ℹ️  No words from expected classifications found in sentence {i}")
                continue

            # Test each expected word
            sentence_passed = True
            for word, expected_category in tested_words:
                # Find the word in the analysis results
                word_data = None
                for w in analysis['words']:
                    if w['word'] == word:
                        word_data = w
                        break

                if not word_data:
                    print(f"❌ ERROR: Word '{word}' not found in analysis results")
                    sentence_passed = False
                    continue

                # Get the actual category
                actual_category = word_data.get('category', 'unknown')

                print(f"  🔍 Word: '{word}' | Expected: {expected_category} | Actual: {actual_category}")

                if actual_category == expected_category:
                    print(f"  ✅ PASS: Correct classification")
                    passed_tests += 1
                else:
                    print(f"  ❌ FAIL: Incorrect classification")
                    failed_tests.append(f"Sentence {i}, Word '{word}': Expected '{expected_category}', Got '{actual_category}'")
                    sentence_passed = False

                total_tests += 1

            if sentence_passed and tested_words:
                print(f"✅ Sentence {i}: PASSED")
            elif tested_words:
                print(f"❌ Sentence {i}: FAILED")

        except Exception as e:
            print(f"❌ ERROR: Exception in sentence {i}: {str(e)}")
            failed_tests.append(f"Sentence {i}: Exception - {str(e)}")

    # Summary
    print("\n" + "=" * 70)
    print("📊 VALIDATION SUMMARY")
    print("=" * 70)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {len(failed_tests)}")

    if failed_tests:
        print("\n❌ FAILED TESTS:")
        for failure in failed_tests:
            print(f"  - {failure}")
    else:
        print("\n🎉 ALL TESTS PASSED! Hierarchical categorization is working correctly.")

    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    print(f"Success Rate: {success_rate:.1f}%")
    # Return success status
    return len(failed_tests) == 0

def test_specific_overlap_cases():
    """Test specific known overlap cases mentioned in the master prompt"""

    print("\n🔍 TESTING SPECIFIC OVERLAP CASES FROM MASTER PROMPT")
    print("=" * 60)

    analyzer = HiAnalyzer()
    overlap_tests = [
        ("राम खाना खा रहा है", "रहा", "auxiliary_verb", "Auxiliary verb vs main verb"),
        ("मैं स्कूल से आया", "से", "postposition", "Postposition vs preposition"),
        ("वह पढ़ता है तो समझता है", "तो", "particle", "Particle vs conjunction"),
        ("दरवाजा धड़ाम बंद हुआ", "धड़ाम", "ideophone", "Ideophone vs interjection"),
    ]

    all_passed = True

    for sentence, word, expected_category, description in overlap_tests:
        print(f"\n🧪 {description}")
        print(f"   Sentence: '{sentence}'")
        print(f"   Testing word: '{word}' (expected: {expected_category})")

        try:
            analysis = analyzer.analyze_sentence(sentence, complexity="intermediate")

            if not analysis or 'words' not in analysis:
                print("   ❌ FAIL: Analysis failed")
                all_passed = False
                continue

            # Find the word
            word_data = None
            for w in analysis['words']:
                if w['word'] == word:
                    word_data = w
                    break

            if not word_data:
                print("   ❌ FAIL: Word not found in analysis")
                all_passed = False
                continue

            actual_category = word_data.get('category', 'unknown')

            if actual_category == expected_category:
                print(f"   ✅ PASS: Correctly classified as '{actual_category}'")
            else:
                print(f"   ❌ FAIL: Classified as '{actual_category}' instead of '{expected_category}'")
                all_passed = False

        except Exception as e:
            print(f"   ❌ FAIL: Exception - {str(e)}")
            all_passed = False

    if all_passed:
        print("\n🎉 ALL OVERLAP CASES PASSED!")
    else:
        print("\n❌ SOME OVERLAP CASES FAILED!")

    return all_passed

if __name__ == "__main__":
    print("Starting Phase 5.7 Hierarchical Categorization Validation...")

    # Run comprehensive test
    comprehensive_passed = test_hierarchical_categorization()

    # Run specific overlap tests
    overlap_passed = test_specific_overlap_cases()

    # Final result
    print("\n" + "=" * 70)
    if comprehensive_passed and overlap_passed:
        print("🎉 PHASE 5.7 VALIDATION: SUCCESS")
        print("✅ Children-first hierarchical categorization is working correctly")
        print("✅ Grammatical analysis order standardization complete")
        print("🚀 Ready to proceed to Phase 5.6 (8-sentence batch processing)")
        sys.exit(0)
    else:
        print("❌ PHASE 5.7 VALIDATION: FAILED")
        print("🔧 Fix the hierarchical categorization issues before proceeding")
        sys.exit(1)