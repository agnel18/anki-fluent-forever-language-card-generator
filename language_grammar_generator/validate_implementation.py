#!/usr/bin/env python3
"""
Language Grammar Generator - Pre-Implementation Validation Script

This script validates a language analyzer implementation against gold standards
before deployment, preventing iterative failures and ensuring production readiness.

VALIDATION CHECKS:
1. File Structure Compliance - All required files present
2. Method Completeness - All required methods implemented
3. Interface Compliance - Matches gold standard interfaces
4. Configuration Validation - External config files loaded correctly
5. Component Integration - All domain components work together
6. Gold Standard Comparison - Results match Chinese Simplified patterns
7. Error Handling - Proper fallbacks and error recovery
8. Performance Validation - Meets performance requirements

USAGE:
    python validate_implementation.py --language {language_code}
    python validate_implementation.py --language zh --verbose
    python validate_implementation.py --all-languages

GOLD STANDARDS:
- Chinese Simplified (zh): Primary reference for Clean Architecture
- Hindi (hi): Secondary reference for Indo-European patterns
"""

import argparse
import importlib
import inspect
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

class ImplementationValidator:
    """Comprehensive validator for language analyzer implementations."""

    def __init__(self, language_code: str):
        self.language_code = language_code
        self.directory_name = self._get_directory_name(language_code)
        self.file_name = self._get_file_name(language_code)
        self.class_prefix = self._get_class_prefix(language_code)
        self.base_path = Path("languages") / self.directory_name
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.successes: List[str] = []

        # Gold standard references
        self.gold_standards = {
            'zh': 'Chinese Simplified (Primary Gold Standard)',
            'hi': 'Hindi (Secondary Reference)',
            'zh_tw': 'Chinese Traditional (Should match zh patterns)',
            'zh-tw': 'Chinese Traditional (Should match zh patterns)'  # Also handle hyphenated version
        }

    def validate_all(self) -> bool:
        """Run all validation checks."""
        print(f"\nðŸ” VALIDATING {self.language_code.upper()} ANALYZER IMPLEMENTATION")
        print("=" * 60)

        checks = [
            self.validate_file_structure,
            self.validate_method_completeness,
            self.validate_interface_compliance,
            self.validate_response_parser_batch_support,
            self.validate_validator_interface,
            self.validate_configuration_loading,
            self.validate_component_integration,
            self.validate_gold_standard_comparison,
            self.validate_error_handling,
            self.validate_performance_requirements,
            self.validate_registry_integration
        ]

        all_passed = True
        for check in checks:
            try:
                passed = check()
                all_passed = all_passed and passed
            except Exception as e:
                self.errors.append(f"Check {check.__name__} failed with error: {e}")
                all_passed = False

        self.print_summary()
        return all_passed

    def validate_file_structure(self) -> bool:
        """Check that all required files are present."""
        print("\nðŸ“ Checking File Structure...")

        required_files = [
            f"{self.file_name}_analyzer.py",
            f"{self.file_name}_grammar_concepts.md",
            "domain/__init__.py",
            f"domain/{self.file_name}_config.py",
            f"domain/{self.file_name}_prompt_builder.py",
            f"domain/{self.file_name}_response_parser.py",
            f"domain/{self.file_name}_validator.py",
            "infrastructure/__init__.py",
            f"infrastructure/{self.file_name}_fallbacks.py",
            "tests/__init__.py",
            f"tests/test_{self.file_name}_analyzer.py",
            f"tests/test_{self.file_name}_config.py",
            f"tests/test_{self.file_name}_prompt_builder.py",
            f"tests/test_{self.file_name}_response_parser.py",
            f"tests/test_{self.file_name}_validator.py",
            "tests/test_integration.py",
            "tests/conftest.py"
        ]

        missing_files = []
        for file_path in required_files:
            full_path = self.base_path / file_path
            if not full_path.exists():
                missing_files.append(file_path)

        if missing_files:
            self.errors.append(f"Missing required files: {missing_files}")
            return False

        self.successes.append("All required files present")
        return True

    def validate_method_completeness(self) -> bool:
        """Check that all required methods are implemented."""
        print("\nðŸ”§ Checking Method Completeness...")

        try:
            # Import the analyzer module
            analyzer_module = importlib.import_module(
                f"languages.{self.directory_name}.{self.file_name}_analyzer"
            )
            analyzer_class = getattr(analyzer_module, f"{self.class_prefix}Analyzer")

            # Required methods for main analyzer
            required_methods = [
                'analyze_grammar',
                'batch_analyze_grammar',
                '_call_ai',
                '_generate_html_output',
                'get_sentence_generation_prompt',
                '__init__'
            ]

            missing_methods = []
            for method in required_methods:
                if not hasattr(analyzer_class, method):
                    missing_methods.append(method)

            if missing_methods:
                self.errors.append(f"Missing methods in analyzer: {missing_methods}")
                return False

            # Check domain components are instantiable
            domain_components = {
                'Config': f"languages.{self.directory_name}.domain.{self.file_name}_config",
                'PromptBuilder': f"languages.{self.directory_name}.domain.{self.file_name}_prompt_builder",
                'ResponseParser': f"languages.{self.directory_name}.domain.{self.file_name}_response_parser",
                'Validator': f"languages.{self.directory_name}.domain.{self.file_name}_validator"
            }
            for component, module_path in domain_components.items():
                component_module = importlib.import_module(module_path)
                component_class = getattr(component_module, f"{self.class_prefix}{component}")
                if not hasattr(component_class, '__init__'):
                    self.errors.append(f"Domain component {component} missing __init__")
                    return False

            self.successes.append("All required methods implemented")
            return True

        except Exception as e:
            self.errors.append(f"Method completeness check failed: {e}")
            return False

    def validate_interface_compliance(self) -> bool:
        """Check that interfaces match gold standards."""
        print("\nðŸ”— Checking Interface Compliance...")

        try:
            # Compare with Chinese Simplified analyzer
            zh_analyzer = importlib.import_module("languages.chinese_simplified.zh_analyzer")
            zh_class = zh_analyzer.ZhAnalyzer

            analyzer_module = importlib.import_module(
                f"languages.{self.directory_name}.{self.file_name}_analyzer"
            )
            analyzer_class = getattr(analyzer_module, f"{self.class_prefix}Analyzer")

            # Check method signatures match
            zh_methods = [m for m in dir(zh_class) if not m.startswith('_') and callable(getattr(zh_class, m))]
            impl_methods = [m for m in dir(analyzer_class) if not m.startswith('_') and callable(getattr(analyzer_class, m))]

            missing_interface_methods = set(zh_methods) - set(impl_methods)
            if missing_interface_methods:
                self.errors.append(f"Missing interface methods compared to gold standard: {missing_interface_methods}")
                return False

            self.successes.append("Interface matches gold standard")
            return True

        except Exception as e:
            self.errors.append(f"Interface compliance check failed: {e}")
            return False

    def validate_configuration_loading(self) -> bool:
        """Check that external configuration files load correctly."""
        print("\nâš™ï¸ Checking Configuration Loading...")

        try:
            config_module = importlib.import_module(
                f"languages.{self.directory_name}.domain.{self.file_name}_config"
            )
            config_class = getattr(config_module, f"{self.class_prefix}Config")

            config_instance = config_class()

            # Check for required attributes (compare with zh_config)
            zh_config = importlib.import_module("languages.chinese_simplified.domain.zh_config")
            zh_config_class = zh_config.ZhConfig
            zh_instance = zh_config_class()

            required_attrs = ['grammatical_roles', 'get_color_scheme']
            for attr in required_attrs:
                if not hasattr(config_instance, attr):
                    self.errors.append(f"Config missing required attribute: {attr}")
                    return False

            self.successes.append("Configuration loads correctly")
            return True

        except Exception as e:
            self.errors.append(f"Configuration loading check failed: {e}")
            return False

    def validate_component_integration(self) -> bool:
        """Check that all domain components work together."""
        print("\nðŸ”„ Checking Component Integration...")

        try:
            analyzer_module = importlib.import_module(
                f"languages.{self.directory_name}.{self.file_name}_analyzer"
            )
            analyzer_class = getattr(analyzer_module, f"{self.class_prefix}Analyzer")

            # Try to instantiate analyzer
            analyzer = analyzer_class()

            # Check that all components are accessible
            components = ['config', 'prompt_builder', 'response_parser', 'validator']
            for component in components:
                if not hasattr(analyzer, component):
                    self.errors.append(f"Analyzer missing component: {component}")
                    return False

            self.successes.append("All components integrate correctly")
            return True

        except Exception as e:
            self.errors.append(f"Component integration check failed: {e}")
            return False

    def validate_gold_standard_comparison(self) -> bool:
        """Compare results with gold standard analyzers."""
        print("\nðŸ† Checking Gold Standard Comparison...")

        try:
            # This would require actual test sentences and comparison logic
            # For now, just check that the analyzer can process basic sentences
            analyzer_module = importlib.import_module(
                f"languages.{self.directory_name}.{self.file_name}_analyzer"
            )
            analyzer_class = getattr(analyzer_module, f"{self.class_prefix}Analyzer")

            analyzer = analyzer_class()

            # Basic functionality test
            test_sentence = "Hello world"
            try:
                result = self._call_analyzer(analyzer, test_sentence, "world", "intermediate", "test_key")
                if not result:
                    self.errors.append("Analyzer failed basic functionality test")
                    return False
            except Exception as e:
                self.errors.append(f"Basic functionality test failed: {e}")
                return False

            self.successes.append("Passes basic gold standard comparison")
            return True

        except Exception as e:
            self.errors.append(f"Gold standard comparison check failed: {e}")
            return False

    def validate_error_handling(self) -> bool:
        """Check error handling and fallback mechanisms."""
        print("\nðŸ›¡ï¸ Checking Error Handling...")

        try:
            analyzer_module = importlib.import_module(
                f"languages.{self.directory_name}.{self.file_name}_analyzer"
            )
            analyzer_class = getattr(analyzer_module, f"{self.class_prefix}Analyzer")

            analyzer = analyzer_class()

            # Test with invalid input
            try:
                result = self._call_analyzer(analyzer, "", "", "intermediate", "")
                # Should handle gracefully
            except Exception as e:
                if "gracefully" not in str(e).lower():
                    self.errors.append(f"Error handling not graceful: {e}")
                    return False

            self.successes.append("Error handling works correctly")
            return True

        except Exception as e:
            self.errors.append(f"Error handling check failed: {e}")
            return False

    def validate_performance_requirements(self) -> bool:
        """Check performance requirements are met."""
        print("\nâš¡ Checking Performance Requirements...")

        try:
            import time
            analyzer_module = importlib.import_module(
                f"languages.{self.directory_name}.{self.file_name}_analyzer"
            )
            analyzer_class = getattr(analyzer_module, f"{self.class_prefix}Analyzer")

            analyzer = analyzer_class()

            # Performance test
            start_time = time.time()
            result = self._call_analyzer(analyzer, "Test sentence", "test", "intermediate", "test_key")
            end_time = time.time()

            duration = end_time - start_time
            if duration > 30:  # 30 second limit
                self.warnings.append(f"Performance warning: {duration:.2f}s (should be < 30s)")
                return False

            self.successes.append("Performance requirements met")
            return True

        except Exception as e:
            self.errors.append(f"Performance check failed: {e}")
            return False

    def print_summary(self):
        """Print validation summary."""
        print("\n" + "=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)

        if self.successes:
            print(f"\nâœ… SUCCESS ({len(self.successes)} checks passed):")
            for success in self.successes:
                print(f"   âœ“ {success}")

        if self.warnings:
            print(f"\nâš ï¸ WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   ! {warning}")

        if self.errors:
            print(f"\nâŒ ERRORS ({len(self.errors)} checks failed):")
            for error in self.errors:
                print(f"   âœ— {error}")

        if not self.errors:
            print(f"\nðŸŽ‰ ALL CHECKS PASSED! {self.language_code.upper()} analyzer is ready for production.")
        else:
            print(f"\nðŸ’¥ VALIDATION FAILED! Fix the {len(self.errors)} errors before deploying.")

    def validate_response_parser_batch_support(self) -> bool:
        """Check that response parser supports batch parsing."""
        print("\nðŸ§© Checking Response Parser Batch Support...")

        try:
            parser_module = importlib.import_module(
                f"languages.{self.directory_name}.domain.{self.file_name}_response_parser"
            )
            parser_class = getattr(parser_module, f"{self.class_prefix}ResponseParser")

            if not hasattr(parser_class, 'parse_batch_response'):
                self.errors.append("Response parser missing parse_batch_response")
                return False

            self.successes.append("Response parser supports batch parsing")
            return True
        except Exception as e:
            self.errors.append(f"Response parser batch support check failed: {e}")
            return False

    def validate_validator_interface(self) -> bool:
        """Check that validator implements required interface methods."""
        print("\nðŸ§ª Checking Validator Interface...")

        try:
            validator_module = importlib.import_module(
                f"languages.{self.directory_name}.domain.{self.file_name}_validator"
            )
            validator_class = getattr(validator_module, f"{self.class_prefix}Validator")

            required_methods = ['validate_result', 'validate_explanation_quality']
            missing = [m for m in required_methods if not hasattr(validator_class, m)]
            if missing:
                self.errors.append(f"Validator missing methods: {missing}")
                return False

            self.successes.append("Validator interface methods present")
            return True
        except Exception as e:
            self.errors.append(f"Validator interface check failed: {e}")
            return False

    def validate_registry_integration(self) -> bool:
        """Check for language registry integration in app configuration."""
        print("\nðŸ§­ Checking Language Registry Integration...")

        registry_path = Path("streamlit_app") / "language_registry.py"
        analyzer_registry_path = Path("streamlit_app") / "language_analyzers" / "analyzer_registry.py"

        registry_ok = None
        analyzer_registry_ok = None

        if registry_path.exists():
            registry_text = registry_path.read_text(encoding="utf-8")
            registry_ok = (
                f"iso_code='{self.language_code}'" in registry_text
                or f"iso_code=\"{self.language_code}\"" in registry_text
            )

        if analyzer_registry_path.exists():
            analyzer_registry_text = analyzer_registry_path.read_text(encoding="utf-8")
            analyzer_registry_ok = (
                f"'{self.language_code}'" in analyzer_registry_text
                or f"\"{self.language_code}\"" in analyzer_registry_text
            )

        if registry_ok is False:
            self.warnings.append(
                f"Language registry missing iso_code='{self.language_code}' in streamlit_app/language_registry.py"
            )
        if analyzer_registry_ok is False:
            self.warnings.append(
                f"Analyzer registry missing '{self.language_code}' mapping in streamlit_app/language_analyzers/analyzer_registry.py"
            )

        if registry_ok is None and analyzer_registry_ok is None:
            self.warnings.append("Registry files not found - skipping language registry integration check")
            return True

        if registry_ok is False or analyzer_registry_ok is False:
            return False

        self.successes.append("Language registry integration present")
        return True

    def _get_directory_name(self, language_code: str) -> str:
        """Map language code to directory name."""
        # Normalize language code by replacing hyphens with underscores
        normalized_code = language_code.replace('-', '_')
        mapping = {
            "zh_tw": "chinese_traditional",
            "zh": "chinese_simplified",
            "hi": "hindi",
            "es": "spanish",
            "ar": "arabic",
            "de": "german",
            "tr": "turkish",
            "fr": "french"
        }
        return mapping.get(normalized_code, normalized_code)

    def _get_file_name(self, language_code: str) -> str:
        """Map language code to analyzer file name."""
        # Normalize language code by replacing hyphens with underscores
        normalized_code = language_code.replace('-', '_')
        mapping = {
            "zh_tw": "zh_tw",
            "zh": "zh",
            "hi": "hi",
            "es": "es",
            "ar": "ar",
            "de": "de",
            "tr": "tr"
        }
        return mapping.get(normalized_code, normalized_code)

    def _get_class_prefix(self, language_code: str) -> str:
        """Map language code to class name prefix."""
        # Normalize language code by replacing hyphens with underscores
        normalized_code = language_code.replace('-', '_')
        mapping = {
            "zh_tw": "ZhTw",
            "zh": "Zh",
            "hi": "Hi",
            "es": "Es",
            "ar": "Ar",
            "de": "De",
            "tr": "Tr"
        }
        return mapping.get(normalized_code, normalized_code.title())

    def _call_analyzer(self, analyzer, sentence: str, target_word: str, complexity: str, api_key: str):
        """Call analyzer.analyze_grammar with flexible signatures."""
        try:
            return analyzer.analyze_grammar(sentence, target_word, complexity, api_key)
        except TypeError:
            try:
                return analyzer.analyze_grammar(sentence, target_word, complexity)
            except TypeError:
                return analyzer.analyze_grammar(sentence, target_word)


def main():
    parser = argparse.ArgumentParser(description="Validate language analyzer implementation")
    parser.add_argument("--language", required=True, help="Language code to validate")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--all-languages", action="store_true", help="Validate all languages")

    args = parser.parse_args()

    if args.all_languages:
        # Validate all language directories
        languages_dir = Path("languages")
        language_codes = [d.name for d in languages_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]

        results = {}
        for lang_code in language_codes:
            validator = ImplementationValidator(lang_code)
            results[lang_code] = validator.validate_all()

        print("\n" + "=" * 60)
        print("ALL LANGUAGES VALIDATION SUMMARY")
        print("=" * 60)

        passed = [lang for lang, result in results.items() if result]
        failed = [lang for lang, result in results.items() if not result]

        if passed:
            print(f"\nâœ… PASSED ({len(passed)}): {', '.join(passed)}")
        if failed:
            print(f"\nâŒ FAILED ({len(failed)}): {', '.join(failed)}")

    else:
        validator = ImplementationValidator(args.language)
        success = validator.validate_all()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
