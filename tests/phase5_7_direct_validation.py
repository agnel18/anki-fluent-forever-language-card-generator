#!/usr/bin/env python3
# Phase 5.7: Grammatical Analysis Order Standardization - Direct Mapping Test
# Hindi Analyzer Hierarchical Categorization Validation
# Created: January 4, 2026

"""
Direct test of the _map_grammatical_role_to_category method to validate
children-first hierarchical categorization without requiring API calls.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from languages.hindi.hi_analyzer import HiAnalyzer

def test_hierarchical_categorization():
    """Test the children-first hierarchical categorization by directly testing the mapping method"""

    print("🧪 Phase 5.7: Grammatical Analysis Order Standardization - Direct Mapping Test")
    print("=" * 80)

    # Initialize analyzer
    analyzer = HiAnalyzer()

    # Track results
    total_tests = 0
    passed_tests = 0
    failed_tests = []

    # Test specific overlapping cases directly - CRITICAL HIERARCHY VALIDATION
    overlap_test_cases = [
        # 1. Auxiliary verb vs main verb (auxiliary_verb → verb)
        ("सहायक क्रिया", "auxiliary_verb", "Hindi: Auxiliary verb before main verb"),
        ("auxiliary_verb", "auxiliary_verb", "English: auxiliary_verb keyword"),
        ("auxiliary", "auxiliary_verb", "English: auxiliary keyword"),

        # 2. Postposition vs preposition (postposition → preposition)
        ("संबंधबोधक", "postposition", "Hindi: Postposition before preposition"),
        ("postposition", "postposition", "English: postposition keyword"),
        ("postpositional", "postposition", "English: postpositional variant"),

        # 3. Particle vs conjunction (particle → conjunction)
        ("निपात", "particle", "Hindi: Particle before conjunction"),
        ("particle", "particle", "English: particle keyword"),
        ("emphasis_particle", "particle", "English: emphasis particle"),
        ("modal_particle", "particle", "English: modal particle"),

        # 4. Ideophone vs interjection (ideophone → interjection)
        ("अनुकरण शब्द", "ideophone", "Hindi: Ideophone before interjection"),
        ("ideophone", "ideophone", "English: ideophone keyword"),

        # 5. Specific pronoun subtypes vs general pronoun
        ("व्यक्तिवाचक सर्वनाम", "personal_pronoun", "Hindi: Personal pronoun before general"),
        ("निदर्शक सर्वनाम", "demonstrative_pronoun", "Hindi: Demonstrative pronoun before general"),
        ("प्रश्नवाचक सर्वनाम", "interrogative_pronoun", "Hindi: Interrogative pronoun before general"),
        ("संबंधवाचक सर्वनाम", "relative_pronoun", "Hindi: Relative pronoun before general"),
        ("अनिश्चयवाचक सर्वनाम", "indefinite_pronoun", "Hindi: Indefinite pronoun before general"),
        ("निजवाचक सर्वनाम", "reflexive_pronoun", "Hindi: Reflexive pronoun before general"),

        # 6. General categories (checked after specific ones)
        ("सर्वनाम", "pronoun", "Hindi: General pronoun (after specific types)"),
        ("समुच्चयबोधक", "conjunction", "Hindi: General conjunction (after particles)"),
        ("विस्मयादिबोधक", "interjection", "Hindi: General interjection (after ideophones)"),

        # 7. Other categories in hierarchy
        ("ध्वन्यात्मक शब्द", "onomatopoeia", "Hindi: Onomatopoeia before interjection"),
        ("दोहराव शब्द", "echo_word", "Hindi: Echo word"),
        ("संख्यावाचक विशेषण", "numeral_adjective", "Hindi: Numeral adjective before general adjective"),
        ("क्रिया विशेषण", "adverb", "Hindi: Adverb"),
        ("विशेषण", "adjective", "Hindi: General adjective (after numeral)"),
        ("संज्ञा", "noun", "Hindi: Noun"),
        ("क्रिया", "verb", "Hindi: Main verb (after auxiliary)"),

        # 8. AI-generated roles that need mapping
        ("subject", "pronoun", "AI: subject role → pronoun"),
        ("negation", "other", "AI: negation role → other"),
        ("determiner", "other", "AI: determiner role → other"),
    ]

    print(f"Testing {len(overlap_test_cases)} grammatical role mappings...")
    print("-" * 80)

    for grammatical_role, expected_category, description in overlap_test_cases:
        total_tests += 1

        try:
            actual_category = analyzer._map_grammatical_role_to_category(grammatical_role)

            if actual_category == expected_category:
                print(f"✅ PASS: '{grammatical_role}' → {actual_category}")
                print(f"   {description}")
                passed_tests += 1
            else:
                print(f"❌ FAIL: '{grammatical_role}' → {actual_category} (expected {expected_category})")
                print(f"   {description}")
                failed_tests.append(f"'{grammatical_role}': Expected '{expected_category}', Got '{actual_category}'")

        except Exception as e:
            print(f"❌ ERROR: Exception testing '{grammatical_role}': {str(e)}")
            failed_tests.append(f"'{grammatical_role}': Exception - {str(e)}")

    # Summary
    print("\n" + "=" * 80)
    print("📊 HIERARCHICAL CATEGORIZATION VALIDATION SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {len(failed_tests)}")

    if failed_tests:
        print("\n❌ FAILED TESTS:")
        for failure in failed_tests:
            print(f"  - {failure}")
        print("\n🔧 HIERARCHY ISSUES DETECTED - REVIEW _map_grammatical_role_to_category METHOD")
    else:
        print("\n🎉 ALL HIERARCHICAL CATEGORIZATION TESTS PASSED!")
        print("✅ Children-first hierarchy is working correctly")
        print("✅ Grammatical analysis order prevents concept overlap")

    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    print(f"Success Rate: {success_rate:.1f}%")

    # Return success status
    return len(failed_tests) == 0

def test_specific_master_prompt_examples():
    """Test the specific examples mentioned in the master prompt"""

    print("\n🔍 TESTING MASTER PROMPT EXAMPLES")
    print("=" * 50)

    analyzer = HiAnalyzer()
    master_examples = [
        ("सहायक क्रिया", "auxiliary_verb", "Auxiliary verb (होना as 'is' vs main verb 'become')"),
        ("संबंधबोधक", "postposition", "Postposition (से as 'from')"),
        ("निपात", "particle", "Particle (तो as 'then' vs conjunction 'so')"),
        ("अनुकरण शब्द", "ideophone", "Ideophone (धड़ाम as 'thud' vs interjection)"),
    ]

    all_passed = True

    for grammatical_role, expected_category, description in master_examples:
        try:
            actual_category = analyzer._map_grammatical_role_to_category(grammatical_role)

            if actual_category == expected_category:
                print(f"✅ PASS: {description}")
            else:
                print(f"❌ FAIL: {description}")
                print(f"   Expected: {expected_category}, Got: {actual_category}")
                all_passed = False

        except Exception as e:
            print(f"❌ ERROR: {description} - {str(e)}")
            all_passed = False

    if all_passed:
        print("\n🎉 ALL MASTER PROMPT EXAMPLES PASSED!")
    else:
        print("\n❌ SOME MASTER PROMPT EXAMPLES FAILED!")

    return all_passed

if __name__ == "__main__":
    print("Starting Phase 5.7 Direct Mapping Validation...")

    # Run comprehensive mapping test
    comprehensive_passed = test_hierarchical_categorization()

    # Run specific master prompt examples
    master_passed = test_specific_master_prompt_examples()

    # Final result
    print("\n" + "=" * 80)
    if comprehensive_passed and master_passed:
        print("🎉 PHASE 5.7 VALIDATION: SUCCESS")
        print("✅ Children-first hierarchical categorization implemented correctly")
        print("✅ Grammatical analysis order standardization complete")
        print("🚀 Ready to proceed to Phase 5.6 (8-sentence batch processing)")
        sys.exit(0)
    else:
        print("❌ PHASE 5.7 VALIDATION: FAILED")
        print("🔧 Fix the hierarchical categorization issues in hi_analyzer.py")
        print("   Review the _map_grammatical_role_to_category method")
        sys.exit(1)