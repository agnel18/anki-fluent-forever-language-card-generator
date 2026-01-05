# Comprehensive Test Suite for Chinese Grammar Analyzer
# Tests all aspects of the ZhAnalyzer implementation

import sys
import os
import json
import time
from typing import Dict, Any

# Add the parent directory to the path to import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from language_analyzers.analyzer_registry import get_analyzer

class ChineseAnalyzerTester:
    """Comprehensive test suite for the Chinese grammar analyzer"""

    def __init__(self):
        self.analyzer = None
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }

    def setup(self):
        """Initialize the analyzer"""
        try:
            self.analyzer = get_analyzer('zh')
            if self.analyzer is None:
                raise Exception("Failed to load Chinese analyzer")
            print("✓ Analyzer loaded successfully")
            return True
        except Exception as e:
            self._log_error(f"Setup failed: {e}")
            return False

    def test_prompt_generation(self):
        """Test prompt generation for all complexity levels"""
        print("\n--- Testing Prompt Generation ---")

        test_sentences = [
            "我爱学习中文",  # Basic sentence
            "他正在吃饭",    # Progressive aspect
            "这是我的书",    # Possession
            "我们一起去公园吧", # Suggestion particle
            "这个问题很难回答"  # Complex structure
        ]

        target_words = ["爱", "正在", "的", "吧", "很难"]

        for level in ['beginner', 'intermediate', 'advanced']:
            print(f"\nTesting {level} level:")

            for sentence, target in zip(test_sentences, target_words):
                try:
                    prompt = self.analyzer.get_grammar_prompt(level, sentence, target)

                    # Validate prompt structure
                    assert isinstance(prompt, str), f"Prompt should be string, got {type(prompt)}"
                    assert len(prompt) > 50, f"Prompt too short: {len(prompt)} chars"
                    assert sentence in prompt, f"Sentence not found in prompt: {sentence}"
                    assert target in prompt, f"Target word not found in prompt: {target}"

                    # Check for JSON structure in prompt
                    assert '"elements"' in prompt, "JSON elements structure missing"
                    assert '"explanations"' in prompt, "JSON explanations structure missing"

                    print(f"  ✓ {level}: '{sentence}' -> {len(prompt)} chars")

                except Exception as e:
                    self._log_error(f"Prompt generation failed for {level} level: {e}")
                    return False

        return True

    def test_color_schemes(self):
        """Test color scheme generation"""
        print("\n--- Testing Color Schemes ---")

        for level in ['beginner', 'intermediate', 'advanced']:
            try:
                colors = self.analyzer.get_color_scheme(level)

                assert isinstance(colors, dict), f"Colors should be dict, got {type(colors)}"
                assert len(colors) > 0, f"No colors returned for {level}"

                # Check for expected grammatical elements (Chinese-specific categories)
                expected_elements = ['noun', 'verb', 'pronoun', 'other']  # Core elements that should always be present
                for element in expected_elements:
                    assert element in colors, f"Missing color for {element} in {level}"

                # Validate color format (hex codes)
                for element, color in colors.items():
                    assert color.startswith('#'), f"Invalid color format for {element}: {color}"
                    assert len(color) == 7, f"Invalid color length for {element}: {color}"

                print(f"  ✓ {level}: {len(colors)} color mappings")

            except Exception as e:
                self._log_error(f"Color scheme test failed for {level}: {e}")
                return False

        return True

    def test_validation_logic(self):
        """Test analysis validation logic"""
        print("\n--- Testing Validation Logic ---")

        # Test cases with different confidence levels
        test_cases = [
            # High confidence case
            {
                'data': {
                    'elements': {
                        'particles': [{'word': '的', 'function': 'possessive'}],
                        'nouns': [{'word': '猫', 'function': 'subject'}],
                        'verbs': [{'word': '睡觉', 'function': 'main verb'}],
                        'prepositions': [{'word': '在', 'function': 'location'}]
                    },
                    'explanations': {
                        'particles': 'Possessive particle',
                        'sentence_structure': 'Subject-verb-object'
                    }
                },
                'sentence': '猫在睡觉',
                'expected_min_confidence': 0.7
            },
            # Low confidence case (missing elements)
            {
                'data': {'elements': {}, 'explanations': {}},
                'sentence': 'test',
                'expected_max_confidence': 0.6
            }
        ]

        for i, case in enumerate(test_cases):
            try:
                confidence = self.analyzer.validate_analysis(case['data'], case['sentence'])

                assert 0.0 <= confidence <= 1.0, f"Confidence out of range: {confidence}"

                if 'expected_min_confidence' in case:
                    assert confidence >= case['expected_min_confidence'], \
                        f"Confidence too low: {confidence} < {case['expected_min_confidence']}"

                if 'expected_max_confidence' in case:
                    assert confidence <= case['expected_max_confidence'], \
                        f"Confidence too high: {confidence} > {case['expected_max_confidence']}"

                print(f"  ✓ Validation case {i+1}: confidence = {confidence:.2f}")

            except Exception as e:
                self._log_error(f"Validation test failed for case {i+1}: {e}")
                return False

        return True

    def test_edge_cases(self):
        """Test edge cases and error handling"""
        print("\n--- Testing Edge Cases ---")

        edge_cases = [
            # Empty strings
            ("", "爱"),
            ("我爱学习", ""),
            # Very long sentence
            ("这是一个非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常长的中文句子用来测试分析器的健壮性", "非常"),
            # Special characters
            ("你好！这是测试。", "好"),
            # Numbers and symbols
            ("我有5本书和3个苹果", "5"),
        ]

        for sentence, target in edge_cases:
            try:
                prompt = self.analyzer.get_grammar_prompt('beginner', sentence, target)
                assert isinstance(prompt, str), "Prompt should be string"
                print(f"  ✓ Edge case: '{sentence[:20]}...' -> {len(prompt)} chars")

            except Exception as e:
                self._log_error(f"Edge case failed for '{sentence}': {e}")
                return False

        return True

    def test_language_config(self):
        """Test language configuration integrity"""
        print("\n--- Testing Language Configuration ---")

        try:
            config = self.analyzer.config

            # Check required attributes
            required_attrs = ['code', 'name', 'native_name', 'family', 'script_type',
                            'complexity_rating', 'key_features', 'supported_complexity_levels']

            for attr in required_attrs:
                assert hasattr(config, attr), f"Missing config attribute: {attr}"

            # Validate specific values
            assert config.code == 'zh', f"Wrong language code: {config.code}"
            assert 'Chinese' in config.name, f"Wrong language name: {config.name}"
            assert config.script_type == 'logographic', f"Wrong script type: {config.script_type}"

            # Check key features
            assert isinstance(config.key_features, list), "Key features should be list"
            assert len(config.key_features) > 0, "No key features defined"

            # Check complexity levels
            assert isinstance(config.supported_complexity_levels, list), "Complexity levels should be list"
            assert 'beginner' in config.supported_complexity_levels, "Beginner level missing"

            print(f"  ✓ Config valid: {config.name} ({config.native_name})")
            print(f"  ✓ Features: {', '.join(config.key_features)}")
            print(f"  ✓ Complexity levels: {', '.join(config.supported_complexity_levels)}")

        except Exception as e:
            self._log_error(f"Configuration test failed: {e}")
            return False

        return True

    def test_performance(self):
        """Test performance characteristics"""
        print("\n--- Testing Performance ---")

        test_sentence = "我爱学习中文"
        test_word = "爱"

        # Test prompt generation speed
        start_time = time.time()
        iterations = 100

        for _ in range(iterations):
            prompt = self.analyzer.get_grammar_prompt('beginner', test_sentence, test_word)
            colors = self.analyzer.get_color_scheme('beginner')

        end_time = time.time()
        avg_time = (end_time - start_time) / iterations * 1000  # ms

        print(f"  ✓ Average generation time: {avg_time:.2f} ms per call")
        assert avg_time < 10.0, f"Too slow: {avg_time} ms per call"

        return True

    def run_all_tests(self):
        """Run the complete test suite"""
        print("🚀 Starting Comprehensive Chinese Analyzer Tests")
        print("=" * 60)

        if not self.setup():
            return False

        tests = [
            self.test_language_config,
            self.test_prompt_generation,
            self.test_color_schemes,
            self.test_validation_logic,
            self.test_edge_cases,
            self.test_performance,
        ]

        for test in tests:
            try:
                if test():
                    self.test_results['passed'] += 1
                else:
                    self.test_results['failed'] += 1
                    break
            except Exception as e:
                self._log_error(f"Test {test.__name__} crashed: {e}")
                self.test_results['failed'] += 1
                break

        self._print_results()
        return self.test_results['failed'] == 0

    def _log_error(self, message: str):
        """Log an error message"""
        print(f"❌ {message}")
        self.test_results['errors'].append(message)

    def _print_results(self):
        """Print test results summary"""
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)

        passed = self.test_results['passed']
        failed = self.test_results['failed']
        total = passed + failed

        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")

        if self.test_results['errors']:
            print(f"\n❌ Errors ({len(self.test_results['errors'])}):")
            for error in self.test_results['errors']:
                print(f"  • {error}")

        if failed == 0:
            print("\n🎉 ALL TESTS PASSED! Chinese analyzer is production-ready.")
        else:
            print(f"\n⚠️  {failed} test(s) failed. Please review and fix issues.")

def main():
    """Main test runner"""
    tester = ChineseAnalyzerTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()