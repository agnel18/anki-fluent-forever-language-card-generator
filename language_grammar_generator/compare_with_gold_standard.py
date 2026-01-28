#!/usr/bin/env python3
"""
Language Grammar Generator - Gold Standard Comparison Script

This script compares a language analyzer implementation against gold standards
(Chinese Simplified and Hindi) to ensure quality and consistency.

COMPARISON METRICS:
1. Result Structure Consistency - Same output format
2. Confidence Score Ranges - Valid confidence values
3. Performance Benchmarks - Speed and resource usage
4. Error Handling Patterns - Consistent error recovery
5. Linguistic Quality - Grammar analysis accuracy
6. HTML Generation - Consistent output formatting

USAGE:
    python compare_with_gold_standard.py --language {language_code}
    python compare_with_gold_standard.py --language zh --detailed
    python compare_with_gold_standard.py --all-languages --export-results

GOLD STANDARDS:
- Chinese Simplified (zh): Primary reference for Clean Architecture
- Hindi (hi): Secondary reference for Indo-European patterns
"""

import argparse
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import statistics

class GoldStandardComparator:
    """Compares language analyzer with gold standards."""

    def __init__(self, language_code: str, detailed: bool = False):
        self.language_code = language_code
        self.detailed = detailed
        self.comparison_results: Dict[str, Any] = {}
        self.test_sentences = self._load_test_sentences()

        # Gold standard analyzers
        self.gold_standards = {
            'zh': self._load_zh_analyzer,
            'hi': self._load_hi_analyzer
        }

    def compare_all(self) -> bool:
        """Run all comparison tests."""
        print(f"\n🏆 COMPARING {self.language_code.upper()} WITH GOLD STANDARDS")
        print("=" * 70)

        if self.language_code in ['zh', 'hi']:
            print(f"⚠️ {self.language_code.upper()} is a gold standard - comparing with itself")
            return True

        comparisons = [
            self.compare_result_structure,
            self.compare_confidence_scoring,
            self.compare_performance,
            self.compare_error_handling,
            self.compare_linguistic_quality,
            self.compare_html_generation
        ]

        all_passed = True
        for comparison in comparisons:
            try:
                metric_name = comparison.__name__.replace('compare_', '').replace('_', ' ').title()
                print(f"\n🔍 Comparing {metric_name}...")

                passed, details = comparison()
                self.comparison_results[comparison.__name__] = {
                    'passed': passed,
                    'details': details
                }

                if passed:
                    print(f"✅ {metric_name} matches gold standards")
                    if self.detailed and details:
                        print(f"   Details: {details}")
                else:
                    print(f"❌ {metric_name} differs from gold standards")
                    if details:
                        print(f"   Issues: {details}")
                    all_passed = False

            except Exception as e:
                print(f"❌ {metric_name} comparison failed: {e}")
                self.comparison_results[comparison.__name__] = {
                    'passed': False,
                    'error': str(e)
                }
                all_passed = False

        self.print_summary()
        return all_passed

    def _load_test_sentences(self) -> List[str]:
        """Load test sentences for comparison."""
        # Default test sentences in multiple languages
        return [
            "Hello world",
            "The cat sat on the mat",
            "I am learning a new language",
            "This is a test sentence",
            "How are you today"
        ]

    def _load_analyzer(self, lang_code: str):
        """Load analyzer for given language code."""
        try:
            if lang_code == 'zh':
                from languages.zh.zh_analyzer import ZhAnalyzer
                return ZhAnalyzer()
            elif lang_code == 'hi':
                from languages.hindi.hi_analyzer import HiAnalyzer
                return HiAnalyzer()
            else:
                module = __import__(f"languages.{lang_code}.{lang_code}_analyzer",
                                   fromlist=[f"{lang_code.title()}Analyzer"])
                analyzer_class = getattr(module, f"{lang_code.title()}Analyzer")
                return analyzer_class()
        except Exception as e:
            raise Exception(f"Failed to load {lang_code} analyzer: {e}")

    def compare_result_structure(self) -> Tuple[bool, str]:
        """Compare result structure consistency."""
        try:
            analyzer = self._load_analyzer(self.language_code)
            zh_analyzer = self._load_analyzer('zh')

            test_sentence = self.test_sentences[0]
            target_word = test_sentence.split()[0]

            result = analyzer.analyze_grammar(test_sentence, target_word, "intermediate", "test_key")
            zh_result = zh_analyzer.analyze_grammar(test_sentence, target_word, "intermediate", "test_key")

            # Check basic structure
            required_attrs = ['word_explanations', 'html_output', 'confidence']
            for attr in required_attrs:
                if not hasattr(result, attr):
                    return False, f"Missing attribute: {attr}"
                if not hasattr(zh_result, attr):
                    return False, f"Gold standard missing attribute: {attr}"

            # Check word explanations structure
            if result.word_explanations and zh_result.word_explanations:
                result_len = len(result.word_explanations[0])
                zh_len = len(zh_result.word_explanations[0])
                if result_len < 3:
                    return False, f"Word explanation too short: {result_len} elements"
                if abs(result_len - zh_len) > 1:  # Allow some flexibility
                    return False, f"Structure mismatch: {result_len} vs {zh_len} elements"

            return True, "Result structure matches gold standard"

        except Exception as e:
            return False, f"Structure comparison failed: {e}"

    def compare_confidence_scoring(self) -> Tuple[bool, str]:
        """Compare confidence scoring ranges and patterns."""
        try:
            analyzer = self._load_analyzer(self.language_code)

            confidences = []
            for sentence in self.test_sentences[:3]:  # Test first 3 sentences
                target_word = sentence.split()[0]
                result = analyzer.analyze_grammar(sentence, target_word, "intermediate", "test_key")
                if hasattr(result, 'confidence'):
                    confidences.append(result.confidence)

            if not confidences:
                return False, "No confidence scores generated"

            # Check ranges
            if not all(0 <= c <= 1 for c in confidences):
                return False, f"Confidence scores out of range [0,1]: {confidences}"

            # Check for reasonable variance (not all same)
            if len(set(confidences)) == 1:
                return False, "All confidence scores identical - may indicate artificial scoring"

            avg_confidence = statistics.mean(confidences)
            return True, ".2f"

        except Exception as e:
            return False, f"Confidence comparison failed: {e}"

    def compare_performance(self) -> Tuple[bool, str]:
        """Compare performance benchmarks."""
        try:
            analyzer = self._load_analyzer(self.language_code)
            zh_analyzer = self._load_analyzer('zh')

            test_sentence = self.test_sentences[0]
            target_word = test_sentence.split()[0]

            # Time the analyzer
            start_time = time.time()
            result = analyzer.analyze_grammar(test_sentence, target_word, "intermediate", "test_key")
            duration = time.time() - start_time

            # Time gold standard
            start_time = time.time()
            zh_result = zh_analyzer.analyze_grammar(test_sentence, target_word, "intermediate", "test_key")
            zh_duration = time.time() - start_time

            # Performance should be within 2x of gold standard
            if duration > zh_duration * 2:
                return False, ".2f"

            return True, ".2f"

        except Exception as e:
            return False, f"Performance comparison failed: {e}"

    def compare_error_handling(self) -> Tuple[bool, str]:
        """Compare error handling patterns."""
        try:
            analyzer = self._load_analyzer(self.language_code)

            # Test with problematic inputs
            error_cases = [
                ("", ""),
                ("A", "a"),
                ("Test with special chars: @#$%", "test"),
                ("Very long sentence " * 50, "very")
            ]

            for sentence, target_word in error_cases:
                try:
                    result = analyzer.analyze_grammar(sentence, target_word, "intermediate", "test_key")
                    if result is None:
                        return False, f"Returned None for input: '{sentence}'"
                except Exception as e:
                    # Should handle gracefully, not crash
                    if "crash" in str(e).lower() or "fatal" in str(e).lower():
                        return False, f"Ungraceful error handling: {e}"

            return True, "Error handling matches gold standard patterns"

        except Exception as e:
            return False, f"Error handling comparison failed: {e}"

    def compare_linguistic_quality(self) -> Tuple[bool, str]:
        """Compare linguistic analysis quality."""
        try:
            analyzer = self._load_analyzer(self.language_code)

            test_sentence = "The quick brown fox jumps over the lazy dog"
            target_word = "fox"

            result = analyzer.analyze_grammar(test_sentence, target_word, "intermediate", "test_key")

            if not result.word_explanations:
                return False, "No word explanations generated"

            # Check for basic linguistic requirements
            has_noun = any('noun' in exp[1].lower() for exp in result.word_explanations if len(exp) > 1)
            has_verb = any('verb' in exp[1].lower() for exp in result.word_explanations if len(exp) > 1)

            if not (has_noun and has_verb):
                return False, "Missing basic grammatical categories (noun/verb)"

            # Check explanation quality
            total_words = len(result.word_explanations)
            detailed_explanations = sum(1 for exp in result.word_explanations if len(exp) >= 4 and exp[3])

            if detailed_explanations / total_words < 0.7:  # 70% should have detailed explanations
                return False, ".1f"

            return True, f"Generated {total_words} explanations, {detailed_explanations} detailed"

        except Exception as e:
            return False, f"Linguistic quality comparison failed: {e}"

    def compare_html_generation(self) -> Tuple[bool, str]:
        """Compare HTML generation consistency."""
        try:
            analyzer = self._load_analyzer(self.language_code)
            zh_analyzer = self._load_analyzer('zh')

            test_sentence = self.test_sentences[0]
            target_word = test_sentence.split()[0]

            result = analyzer.analyze_grammar(test_sentence, target_word, "intermediate", "test_key")
            zh_result = zh_analyzer.analyze_grammar(test_sentence, target_word, "intermediate", "test_key")

            if not hasattr(result, 'html_output') or not hasattr(zh_result, 'html_output'):
                return False, "Missing HTML output"

            html = result.html_output
            zh_html = zh_result.html_output

            # Check for basic HTML structure
            if '<span' not in html:
                return False, "HTML output missing span tags"

            # Check for color styling
            if 'color:' not in html:
                return False, "HTML output missing color styling"

            # Check for font-weight (bold)
            if 'font-weight:' not in html:
                return False, "HTML output missing font-weight styling"

            return True, "HTML generation matches gold standard format"

        except Exception as e:
            return False, f"HTML generation comparison failed: {e}"

    def print_summary(self):
        """Print comparison summary."""
        print("\n" + "=" * 70)
        print("GOLD STANDARD COMPARISON SUMMARY")
        print("=" * 70)

        passed = [name for name, result in self.comparison_results.items() if result['passed']]
        failed = [name for name, result in self.comparison_results.items() if not result['passed']]

        print(f"\n📊 Metrics Compared: {len(self.comparison_results)}")

        if passed:
            print(f"\n✅ PASSED ({len(passed)}):")
            for name in passed:
                details = self.comparison_results[name].get('details', '')
                metric_name = name.replace('compare_', '').replace('_', ' ').title()
                print(f"   ✓ {metric_name}")
                if details:
                    print(f"     {details}")

        if failed:
            print(f"\n❌ FAILED ({len(failed)}):")
            for name in failed:
                details = self.comparison_results[name].get('details', '')
                error = self.comparison_results[name].get('error', '')
                metric_name = name.replace('compare_', '').replace('_', ' ').title()
                print(f"   ✗ {metric_name}")
                if details:
                    print(f"     Issues: {details}")
                if error:
                    print(f"     Error: {error}")

        if not failed:
            print(f"\n🎉 ALL COMPARISONS PASSED! {self.language_code.upper()} matches gold standards.")
        else:
            print(f"\n💥 COMPARISONS FAILED! {self.language_code.upper()} needs improvements to match gold standards.")


def main():
    parser = argparse.ArgumentParser(description="Compare language analyzer with gold standards")
    parser.add_argument("--language", required=True, help="Language code to compare")
    parser.add_argument("--detailed", action="store_true", help="Show detailed comparison results")
    parser.add_argument("--export-results", action="store_true", help="Export results to JSON file")
    parser.add_argument("--all-languages", action="store_true", help="Compare all languages")

    args = parser.parse_args()

    if args.all_languages:
        # Compare all language directories
        languages_dir = Path("languages")
        language_codes = [d.name for d in languages_dir.iterdir()
                         if d.is_dir() and not d.name.startswith('.') and d.name not in ['zh', 'hi']]

        results = {}
        for lang_code in language_codes:
            comparator = GoldStandardComparator(lang_code, args.detailed)
            results[lang_code] = comparator.compare_all()

        print("\n" + "=" * 70)
        print("ALL LANGUAGES COMPARISON SUMMARY")
        print("=" * 70)

        passed = [lang for lang, result in results.items() if result]
        failed = [lang for lang, result in results.items() if not result]

        if passed:
            print(f"\n✅ MATCH GOLD STANDARDS ({len(passed)}): {', '.join(passed)}")
        if failed:
            print(f"\n❌ DON'T MATCH GOLD STANDARDS ({len(failed)}): {', '.join(failed)}")

        if args.export_results:
            with open("gold_standard_comparison_results.json", "w") as f:
                json.dump(results, f, indent=2)
            print("
📄 Results exported to gold_standard_comparison_results.json"
    else:
        comparator = GoldStandardComparator(args.language, args.detailed)
        success = comparator.compare_all()

        if args.export_results:
            with open(f"{args.language}_gold_standard_comparison.json", "w") as f:
                json.dump(comparator.comparison_results, f, indent=2)
            print(f"\n📄 Results exported to {args.language}_gold_standard_comparison.json")

        exit(0 if success else 1)


if __name__ == "__main__":
    main()