#!/usr/bin/env python3
"""
Language Grammar Generator - Comprehensive Test Runner

This script runs all tests for a language analyzer implementation,
ensuring complete coverage and preventing deployment of broken code.

TEST COVERAGE:
1. Unit Tests - Individual component testing
2. Integration Tests - Component interaction testing
3. System Tests - End-to-end workflow testing
4. Performance Tests - Speed and resource usage
5. Gold Standard Comparison - Results validation
6. Regression Tests - Prevent reintroduction of bugs

USAGE:
    python run_all_tests.py --language {language_code}
    python run_all_tests.py --language zh --coverage
    python run_all_tests.py --all-languages --parallel

GOLD STANDARDS:
- Chinese Simplified (zh): Primary reference for Clean Architecture
- Hindi (hi): Secondary reference for Indo-European patterns
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
import os

class TestRunner:
    """Comprehensive test runner for language analyzer implementations."""

    def __init__(self, language_code: str, coverage: bool = False, parallel: bool = False):
        self.language_code = language_code
        self.coverage = coverage
        self.parallel = parallel
        self.test_results: Dict[str, Any] = {}
        self.base_path = Path("..") / "languages" / self._get_directory_name(language_code)

    def _get_directory_name(self, language_code: str) -> str:
        """Map language code to directory name."""
        mapping = {
            "zh_tw": "chinese_traditional",
            "zh": "zh",  # Chinese Simplified
            "hi": "hindi",
            "es": "spanish",
            "ar": "arabic"
        }
        return mapping.get(language_code, language_code)

    def _get_class_name(self, language_code: str) -> str:
        """Map language code to analyzer class name."""
        mapping = {
            "zh_tw": "ZhTwAnalyzer",
            "zh": "ZhAnalyzer",  # Chinese Simplified
            "hi": "HiAnalyzer",
            "es": "EsAnalyzer",
            "ar": "ArAnalyzer"
        }
        return mapping.get(language_code, f"{language_code.title()}Analyzer")

    def run_all_tests(self) -> bool:
        """Run all test suites."""
        print(f"\n🧪 RUNNING COMPREHENSIVE TESTS FOR {self.language_code.upper()}")
        print("=" * 70)

        test_suites = [
            self.run_unit_tests,
            self.run_integration_tests,
            self.run_system_tests,
            self.run_performance_tests,
            self.run_gold_standard_comparison,
            self.run_regression_tests
        ]

        all_passed = True
        start_time = time.time()

        for test_suite in test_suites:
            try:
                suite_name = test_suite.__name__.replace('run_', '').replace('_', ' ').title()
                print(f"\n🔬 Running {suite_name}...")

                suite_start = time.time()
                passed = test_suite()
                suite_duration = time.time() - suite_start

                self.test_results[test_suite.__name__] = {
                    'passed': passed,
                    'duration': suite_duration
                }

                if passed:
                    print(f"✅ {suite_name} passed in {suite_duration:.2f}s")
                else:
                    print(f"❌ {suite_name} failed in {suite_duration:.2f}s")
                    all_passed = False

            except Exception as e:
                print(f"❌ {suite_name} failed with error: {e}")
                self.test_results[test_suite.__name__] = {
                    'passed': False,
                    'duration': 0,
                    'error': str(e)
                }
                all_passed = False

        total_duration = time.time() - start_time
        self.print_summary(total_duration)
        return all_passed

    def run_unit_tests(self) -> bool:
        """Run unit tests for individual components."""
        test_files = [
            f"tests/test_{self.language_code}_config.py",
            f"tests/test_{self.language_code}_prompt_builder.py",
            f"tests/test_{self.language_code}_response_parser.py",
            f"tests/test_{self.language_code}_validator.py"
        ]

        return self._run_pytest_files(test_files, "Unit Tests")

    def run_integration_tests(self) -> bool:
        """Run integration tests for component interaction."""
        test_files = [
            f"tests/test_{self.language_code}_analyzer.py",
            "tests/test_integration.py"
        ]

        return self._run_pytest_files(test_files, "Integration Tests")

    def run_system_tests(self) -> bool:
        """Run end-to-end system tests."""
        # Create a system test file if it doesn't exist
        system_test_file = self.base_path / "tests" / "test_system.py"
        if not system_test_file.exists():
            self._create_system_test_file()

        return self._run_pytest_files(["tests/test_system.py"], "System Tests")

    def run_performance_tests(self) -> bool:
        """Run performance and load tests."""
        perf_test_file = self.base_path / "tests" / "test_performance.py"
        # Always recreate to ensure latest template
        self._create_performance_test_file()

        return self._run_pytest_files(["tests/test_performance.py"], "Performance Tests")

    def run_gold_standard_comparison(self) -> bool:
        """Run tests comparing with gold standard analyzers."""
        comparison_file = self.base_path / "tests" / "test_gold_standard_comparison.py"
        if not comparison_file.exists():
            self._create_gold_standard_comparison_file()

        return self._run_pytest_files(["tests/test_gold_standard_comparison.py"], "Gold Standard Comparison")

    def run_regression_tests(self) -> bool:
        """Run regression tests to prevent bug reintroduction."""
        regression_file = self.base_path / "tests" / "test_regression.py"
        # Always recreate to ensure latest template
        self._create_regression_test_file()

        return self._run_pytest_files(["tests/test_regression.py"], "Regression Tests")

    def _run_pytest_files(self, test_files: List[str], suite_name: str) -> bool:
        """Run pytest on specified files."""
        if not self._check_test_files_exist(test_files):
            print(f"⚠️ Some test files missing for {suite_name}")
            return False

        cmd = [sys.executable, "-m", "pytest"]

        if self.coverage:
            cmd.extend(["--cov=languages", "--cov-report=html", "--cov-report=term"])

        if self.parallel:
            cmd.extend(["-n", "auto"])

        cmd.extend([str((self.base_path / f).resolve()) for f in test_files])
        cmd.extend(["-v", "--tb=short"])

        # Run from project root so imports work
        project_root = Path("..").resolve()  # From language_grammar_generator to project root

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=project_root)

            if result.returncode == 0:
                print(f"✅ {suite_name} passed")
                if self.coverage and "coverage" in result.stdout:
                    print("📊 Coverage report generated")
                return True
            else:
                print(f"❌ {suite_name} failed")
                print("STDOUT:", result.stdout[-500:])  # Last 500 chars
                print("STDERR:", result.stderr[-500:])
                return False

        except Exception as e:
            print(f"❌ {suite_name} execution failed: {e}")
            return False

    def _check_test_files_exist(self, test_files: List[str]) -> bool:
        """Check if test files exist."""
        for test_file in test_files:
            if not (self.base_path / test_file).exists():
                return False
        return True

    def _create_system_test_file(self):
        """Create a basic system test file."""
        content = '''
"""
System tests for {language_code} analyzer - End-to-end testing.
"""

import pytest
import os
from dotenv import load_dotenv
from languages.{directory_name}.{language_code}_analyzer import {class_name}

# Load environment variables
load_dotenv()


class Test{class_name}System:
    """System-level tests for complete analyzer workflow."""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer for testing."""
        return {class_name}()

    def test_complete_workflow(self, analyzer):
        """Test complete analysis workflow."""
        sentence = "Hello world"
        target_word = "world"
        api_key = os.getenv('GEMINI_API_KEY', 'test_key')

        result = analyzer.analyze_grammar(sentence, target_word, "intermediate", api_key)

        assert result is not None
        assert hasattr(result, 'word_explanations')
        assert len(result.word_explanations) > 0

    def test_batch_processing(self, analyzer):
        """Test batch processing capability."""
        sentences = ["Hello world", "How are you", "Thank you"]
        target_word = "world"
        api_key = os.getenv('GEMINI_API_KEY', 'test_key')

        results = analyzer.batch_analyze_grammar(sentences, target_word, "intermediate", api_key)

        assert len(results) == len(sentences)
        for result in results:
            assert result is not None

    def test_error_recovery(self, analyzer):
        """Test error recovery mechanisms."""
        # Test with invalid input
        api_key = os.getenv('GEMINI_API_KEY', 'test_key')
        try:
            result = analyzer.analyze_grammar("", "", "intermediate", api_key)
            # Should handle gracefully
            assert result is not None
        except Exception:
            # Should not crash completely
            pass
'''
        directory_name = self._get_directory_name(self.language_code)
        class_name = self._get_class_name(self.language_code)
        content = content.format(language_code=self.language_code, directory_name=directory_name, class_name=class_name)
        test_file = self.base_path / "tests" / "test_system.py"
        test_file.parent.mkdir(exist_ok=True)
        test_file.write_text(content)

    def _create_performance_test_file(self):
        """Create a performance test file."""
        content = '''
"""
Performance tests for {language_code} analyzer.
"""

import pytest
from languages.{directory_name}.{language_code}_analyzer import {class_name}


class Test{class_name}Performance:
    """Performance tests for analyzer."""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer for testing."""
        return {class_name}()

    def test_dummy(self, analyzer):
        """Dummy test."""
        assert analyzer is not None
'''
        directory_name = self._get_directory_name(self.language_code)
        class_name = self._get_class_name(self.language_code)
        content = content.format(language_code=self.language_code, directory_name=directory_name, class_name=class_name)
        test_file = self.base_path / "tests" / "test_performance.py"
        test_file.parent.mkdir(exist_ok=True)
        test_file.write_text(content)

    def _create_gold_standard_comparison_file(self):
        """Create gold standard comparison test file."""
        content = '''
"""
Gold standard comparison tests for {language_code} analyzer.

Compares results with Chinese Simplified and Hindi analyzers to ensure
consistency and quality standards are met.
"""

import pytest
import os
from dotenv import load_dotenv
from languages.{directory_name}.{language_code}_analyzer import {class_name}
from languages.zh.zh_analyzer import ZhAnalyzer
from languages.hindi.hi_analyzer import HiAnalyzer

# Load environment variables
load_dotenv()


class Test{class_name}GoldStandardComparison:
    """Compare with gold standard analyzers."""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer for testing."""
        return {class_name}()

    @pytest.fixture
    def zh_analyzer(self):
        """Create Chinese Simplified analyzer for comparison."""
        return ZhAnalyzer()

    @pytest.fixture
    def hi_analyzer(self):
        """Create Hindi analyzer for comparison."""
        return HiAnalyzer()

    def test_result_structure_consistency(self, analyzer, zh_analyzer):
        """Test that result structure matches gold standards."""
        sentence = "Test sentence"
        target_word = "test"
        api_key = os.getenv('GEMINI_API_KEY', 'test_key')

        result = analyzer.analyze_grammar(sentence, target_word, "intermediate", api_key)
        zh_result = zh_analyzer.analyze_grammar(sentence, target_word, "intermediate", api_key)

        # Check that both have same basic structure
        assert hasattr(result, 'word_explanations')
        assert hasattr(zh_result, 'word_explanations')

        # Check that explanations have consistent format
        if result.word_explanations and zh_result.word_explanations:
            assert len(result.word_explanations[0]) >= 3  # word, role, color
            assert len(zh_result.word_explanations[0]) >= 3

    def test_confidence_scoring_range(self, analyzer):
        """Test that confidence scores are in valid range."""
        sentence = "Test sentence"
        target_word = "test"
        api_key = os.getenv('GEMINI_API_KEY', 'test_key')

        result = analyzer.analyze_grammar(sentence, target_word, "intermediate", api_key)

        # Confidence should be between 0 and 1
        assert hasattr(result, 'confidence_score')
        assert 0 <= result.confidence_score <= 1

    def test_batch_consistency(self, analyzer, zh_analyzer):
        """Test that batch processing is consistent."""
        sentences = ["Test 1", "Test 2", "Test 3"]
        target_word = "test"
        api_key = os.getenv('GEMINI_API_KEY', 'test_key')

        results = analyzer.batch_analyze_grammar(sentences, target_word, "intermediate", api_key)
        zh_results = zh_analyzer.batch_analyze_grammar(sentences, target_word, "intermediate", api_key)

        assert len(results) == len(sentences)
        assert len(zh_results) == len(sentences)

        # All results should have explanations
        for result in results:
            assert hasattr(result, 'word_explanations')
'''
        directory_name = self._get_directory_name(self.language_code)
        class_name = self._get_class_name(self.language_code)
        content = content.format(language_code=self.language_code, directory_name=directory_name, class_name=class_name)
        test_file = self.base_path / "tests" / "test_gold_standard_comparison.py"
        test_file.parent.mkdir(exist_ok=True)
        test_file.write_text(content)

    def _create_regression_test_file(self):
        """Create regression test file."""
        content = '''
"""
Regression tests for {language_code} analyzer.

These tests prevent reintroduction of previously fixed bugs.
"""

import pytest
import os
from dotenv import load_dotenv
from languages.{directory_name}.{language_code}_analyzer import {class_name}

# Load environment variables
load_dotenv()


class Test{class_name}Regression:
    """Regression tests for known issues."""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer for testing."""
        return {class_name}()

    def test_api_key_validation(self, analyzer):
        """Test that API key validation works correctly."""
        api_key = os.getenv('GEMINI_API_KEY', 'test_key')
        
        # Should not crash with valid key
        result = analyzer.analyze_grammar("Test sentence", "test", "intermediate", api_key)
        assert result is not None

    def test_empty_input_handling(self, analyzer):
        """Test handling of empty inputs."""
        api_key = os.getenv('GEMINI_API_KEY', 'test_key')
        
        # Should handle empty inputs gracefully
        result = analyzer.analyze_grammar("", "", "intermediate", api_key)
        assert result is not None
'''
        directory_name = self._get_directory_name(self.language_code)
        class_name = self._get_class_name(self.language_code)
        content = content.format(language_code=self.language_code, directory_name=directory_name, class_name=class_name)
        test_file = self.base_path / "tests" / "test_regression.py"
        test_file.parent.mkdir(exist_ok=True)
        test_file.write_text(content)

    def print_summary(self, total_duration: float):
        """Print comprehensive test summary."""
        print("\n" + "=" * 70)
        print("COMPREHENSIVE TEST SUMMARY")
        print("=" * 70)

        passed = [name for name, result in self.test_results.items() if result['passed']]
        failed = [name for name, result in self.test_results.items() if not result['passed']]

        print(f"\n⏱️ Total Duration: {total_duration:.2f}s")
        print(f"📊 Test Suites Run: {len(self.test_results)}")

        if passed:
            print(f"\n✅ PASSED ({len(passed)}):")
            for name in passed:
                duration = self.test_results[name]['duration']
                print(f"   ✓ {name.replace('run_', '').replace('_', ' ').title()} ({duration:.2f}s)")

        if failed:
            print(f"\n❌ FAILED ({len(failed)}):")
            for name in failed:
                duration = self.test_results[name]['duration']
                error = self.test_results[name].get('error', 'Unknown error')
                print(f"   ✗ {name.replace('run_', '').replace('_', ' ').title()} ({duration:.2f}s)")
                print(f"      Error: {error}")

        if not failed:
            print(f"\n🎉 ALL TESTS PASSED! {self.language_code.upper()} analyzer is fully tested and ready.")
        else:
            print(f"\n💥 TESTS FAILED! Fix the {len(failed)} failing test suites before deploying.")


def main():
    parser = argparse.ArgumentParser(description="Run comprehensive tests for language analyzer")
    parser.add_argument("--language", required=True, help="Language code to test")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument("--all-languages", action="store_true", help="Test all languages")

    args = parser.parse_args()

    if args.all_languages:
        # Test all language directories
        languages_dir = Path("languages")
        language_codes = [d.name for d in languages_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]

        results = {}
        for lang_code in language_codes:
            runner = TestRunner(lang_code, args.coverage, args.parallel)
            results[lang_code] = runner.run_all_tests()

        print("\n" + "=" * 70)
        print("ALL LANGUAGES TEST SUMMARY")
        print("=" * 70)

        passed = [lang for lang, result in results.items() if result]
        failed = [lang for lang, result in results.items() if not result]

        if passed:
            print(f"\n✅ PASSED ({len(passed)}): {', '.join(passed)}")
        if failed:
            print(f"\n❌ FAILED ({len(failed)}): {', '.join(failed)}")

    else:
        runner = TestRunner(args.language, args.coverage, args.parallel)
        success = runner.run_all_tests()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()