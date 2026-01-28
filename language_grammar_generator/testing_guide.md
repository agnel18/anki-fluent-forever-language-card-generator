# Testing Guide
## Comprehensive Testing Strategy Following Gold Standard Patterns

**Primary Gold Standard:** [Chinese Simplified](languages/zh/zh_analyzer.py) - Clean Architecture benchmark
**Secondary Reference:** [Hindi](languages/hindi/hi_analyzer.py)
**Critical:** Test against Chinese Simplified gold standard - external configuration, integrated fallbacks, natural validation
**Prerequisites:** Study Chinese Simplified Clean Architecture before testing
**Architecture:** Follow [Architecture Guide](architecture_guide.md) with Chinese Simplified compliance
**Time Estimate:** 1-2 weeks for gold standard compliant test suite

## 🎯 Testing Philosophy - Chinese Simplified Gold Standard Compliance

### Quality Assurance Principles - Match Chinese Simplified
- **Gold Standard Comparison:** All tests compare with Chinese Simplified Clean Architecture results
- **External Configuration Testing:** Test YAML/JSON file loading (Chinese Simplified pattern)
- **Integrated Fallback Testing:** Test fallbacks within domain layer (Chinese Simplified pattern)
- **Natural Validation Testing:** No tests for artificial confidence boosting (removed)
- **Component Isolation:** Test components separately like Chinese Simplified
- **Facade Pattern Testing:** Test complete Clean Architecture orchestration
- **Jinja2 Template Testing:** Test template-based prompt generation

### Testing Pyramid - Chinese Simplified Validation
```
┌─────────────────┐  (Few tests, high value)
│ Gold Standard   │  Compare with Chinese Simplified
│ Compliance      │  Clean Architecture validation
├─────────────────┤
│ System Tests    │  End-to-end facade workflow
│ Integration     │  Domain component orchestration
├─────────────────┤
│ Unit Tests      │  Individual domain components
│                 │  (Many tests, fast)
└─────────────────┘
```

## 🚀 Automated Testing Framework

### Pre-Implementation Validation
```bash
# Validate implementation before testing
python language_grammar_generator/validate_implementation.py --language {language_code}
```

### Comprehensive Test Execution
```bash
# Run all tests with coverage
python language_grammar_generator/run_all_tests.py --language {language_code} --coverage

# Run tests in parallel for speed
python language_grammar_generator/run_all_tests.py --language {language_code} --parallel

# Test all languages
python language_grammar_generator/run_all_tests.py --all-languages
```

### Gold Standard Comparison
```bash
# Compare with Chinese Simplified and Hindi
python language_grammar_generator/compare_with_gold_standard.py --language {language_code}

# Detailed comparison with export
python language_grammar_generator/compare_with_gold_standard.py --language {language_code} --detailed --export-results
```

## 🧪 Testing Framework Setup - Chinese Simplified Structure

### 1. Directory Structure - Like Chinese Simplified
```
languages/{language}/tests/
├── __init__.py
├── conftest.py                    # Pytest configuration
├── test_{language}_analyzer.py    # Main facade tests (Clean Architecture)
├── test_{language}_config.py      # External config loading tests (YAML/JSON)
├── test_{language}_prompt_builder.py  # Jinja2 template tests
├── test_{language}_response_parser.py # Response parsing with integrated fallbacks
├── test_{language}_validator.py   # NATURAL validation tests (NO boosting)
├── test_{language}_integration.py # Facade orchestration tests
├── test_{language}_performance.py # Performance vs Chinese Simplified
├── test_gold_standard_comparison.py # Compare with Chinese Simplified
├── fixtures/
│   ├── sample_sentences.json     # Test sentences
│   ├── expected_outputs.json     # Expected results like gold standards
│   └── mock_responses.json       # Mock AI responses
└── utils/
    └── test_helpers.py           # Gold standard test helpers
```

### 2. Configuration - Gold Standard Test Setup
```python
# conftest.py - Test configuration like gold standards
import pytest
from languages.{language}.{language}_config import {Language}Config
from languages.{language}.{language}_analyzer import {Language}Analyzer

@pytest.fixture
def config():
    """Load config from external files like gold standards"""
    return {Language}Config()  # Loads from YAML like Hindi/Chinese

@pytest.fixture
def analyzer(config):
    """Create analyzer with injected dependencies like gold standards"""
    return {Language}Analyzer(
        config=config,
        prompt_builder=None,  # Injectable for testing
        parser=None,
        validator=None
    )

@pytest.fixture
def gold_standard_results():
    """Load gold standard test results for comparison"""
    import json
    with open("tests/fixtures/gold_standard_results.json") as f:
        return json.load(f)
```
    ├── test_helpers.py           # Test utilities
    └── linguistic_validators.py  # Linguistic validation helpers
```

### 2. Pytest Configuration

**File:** `tests/conftest.py`
```python
import pytest
import json
import os
from pathlib import Path

@pytest.fixture(scope="session")
def test_data_dir():
    """Path to test data directory"""
    return Path(__file__).parent / "fixtures"

@pytest.fixture(scope="session")
def sample_sentences(test_data_dir):
    """Load sample sentences for testing"""
    with open(test_data_dir / "sample_sentences.json", "r", encoding="utf-8") as f:
        return json.load(f)

@pytest.fixture(scope="session")
def expected_outputs(test_data_dir):
    """Load expected outputs for validation"""
    with open(test_data_dir / "expected_outputs.json", "r", encoding="utf-8") as f:
        return json.load(f)

@pytest.fixture(scope="session")
def mock_responses(test_data_dir):
    """Load mock AI responses"""
    with open(test_data_dir / "mock_responses.json", "r", encoding="utf-8") as f:
        return json.load(f)

@pytest.fixture
def analyzer():
    """Create analyzer instance for testing"""
    from ..{language}_analyzer import {Language}Analyzer
    return {Language}Analyzer()

@pytest.fixture
def config():
    """Create config instance for testing"""
    from ..domain.{language}_config import {Language}Config
    return {Language}Config()
```

### 3. Test Data Preparation

**File:** `tests/fixtures/sample_sentences.json`
```json
{
  "beginner": {
    "simple": [
      "The cat sits on the mat.",
      "I eat an apple.",
      "She reads a book."
    ],
    "with_target": [
      {"sentence": "The big cat sleeps.", "target": "cat"},
      {"sentence": "I drink water.", "target": "drink"},
      {"sentence": "They play games.", "target": "play"}
    ]
  },
  "intermediate": {
    "complex": [
      "The cat that chased the mouse ran away.",
      "Having finished dinner, she went to bed.",
      "Despite the rain, they continued playing."
    ]
  },
  "advanced": {
    "complex": [
      "The algorithm, having been optimized for performance, now processes data exponentially faster.",
      "Notwithstanding the committee's recommendations, the board decided to proceed with the merger.",
      "The phenomenon, albeit rare, occurs under specific quantum mechanical conditions."
    ]
  }
}
```

**File:** `tests/fixtures/expected_outputs.json`
```json
{
  "beginner_simple": {
    "sentence": "The cat sits on the mat.",
    "expected_roles": ["determiner", "noun", "verb", "preposition", "determiner", "noun"],
    "min_confidence": 0.8,
    "required_explanations": ["overall_structure", "key_features"]
  }
}
```

**File:** `tests/fixtures/mock_responses.json`
```json
{
  "valid_response": {
    "words": [
      {"word": "The", "grammatical_role": "determiner", "meaning": "Definite article indicating specificity"},
      {"word": "cat", "grammatical_role": "noun", "meaning": "Subject of the sentence, common noun"},
      {"word": "sits", "grammatical_role": "verb", "meaning": "Main verb in present tense"},
      {"word": "on", "grammatical_role": "preposition", "meaning": "Preposition indicating location"},
      {"word": "the", "grammatical_role": "determiner", "meaning": "Definite article"},
      {"word": "mat", "grammatical_role": "noun", "meaning": "Object of preposition, common noun"}
    ],
    "explanations": {
      "overall_structure": "Simple declarative sentence with Subject-Verb-Object structure",
      "key_features": "Present tense verb, definite articles, common nouns"
    }
  },
  "malformed_response": "This is not JSON",
  "incomplete_response": {
    "words": [
      {"word": "The", "grammatical_role": "determiner"}
    ]
  }
}
```

## 🧩 Unit Testing

### 1. Configuration Tests

**File:** `tests/test_{language}_config.py`
```python
import pytest

class Test{Language}Config:
    """Test configuration component"""

    def test_initialization(self, config):
        """Test config initializes with required attributes"""
        assert hasattr(config, 'language_code')
        assert hasattr(config, 'language_name')
        assert hasattr(config, 'grammatical_roles')
        assert isinstance(config.grammatical_roles, dict)

    def test_grammatical_roles_mapping(self, config):
        """Test grammatical roles are properly mapped"""
        roles = config.grammatical_roles

        # Should have basic universal roles
        assert 'noun' in roles.values()
        assert 'verb' in roles.values()

        # Should have language-specific roles
        # Add language-specific assertions here

    @pytest.mark.parametrize("complexity", ["beginner", "intermediate", "advanced"])
    def test_color_scheme_generation(self, config, complexity):
        """Test color scheme for different complexity levels"""
        colors = config.get_color_scheme(complexity)

        assert isinstance(colors, dict)
        assert len(colors) > 0

        # All colors should be valid hex codes
        for role, color in colors.items():
            assert color.startswith('#')
            assert len(color) == 7  # #RRGGBB format

    def test_complexity_progression(self, config):
        """Test that complexity levels build upon each other"""
        beginner = config.get_color_scheme('beginner')
        intermediate = config.get_color_scheme('intermediate')
        advanced = config.get_color_scheme('advanced')

        # Intermediate should have at least as many roles as beginner
        assert len(intermediate) >= len(beginner)

        # Advanced should have at least as many roles as intermediate
        assert len(advanced) >= len(intermediate)

    def test_prompt_templates(self, config):
        """Test prompt templates are properly configured"""
        assert hasattr(config, 'prompt_templates')
        templates = config.prompt_templates

        assert 'single' in templates
        assert 'batch' in templates

        # Templates should contain placeholders
        assert '{{sentence}}' in templates['single']
        assert '{{complexity}}' in templates['single']
```

### 2. Prompt Builder Tests

**File:** `tests/test_{language}_prompt_builder.py`
```python
import pytest

class Test{Language}PromptBuilder:
    """Test prompt building component"""

    def test_initialization(self, analyzer):
        """Test prompt builder initializes correctly"""
        builder = analyzer.prompt_builder
        assert hasattr(builder, 'config')
        assert hasattr(builder, 'single_template')
        assert hasattr(builder, 'batch_template')

    def test_single_prompt_generation(self, analyzer, sample_sentences):
        """Test single sentence prompt generation"""
        builder = analyzer.prompt_builder

        sentence = sample_sentences['beginner']['simple'][0]
        target_word = "cat"
        complexity = "beginner"

        prompt = builder.build_single_prompt(sentence, target_word, complexity)

        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert sentence in prompt
        assert target_word in prompt
        assert complexity in prompt
        assert analyzer.config.language_name in prompt

    def test_batch_prompt_generation(self, analyzer, sample_sentences):
        """Test batch prompt generation"""
        builder = analyzer.prompt_builder

        sentences = sample_sentences['beginner']['simple'][:2]
        target_word = "test"
        complexity = "beginner"

        prompt = builder.build_batch_prompt(sentences, target_word, complexity)

        assert isinstance(prompt, str)
        assert len(prompt) > 0
        for sentence in sentences:
            assert sentence in prompt

    def test_prompt_contains_grammatical_roles(self, analyzer):
        """Test prompt includes grammatical roles list"""
        builder = analyzer.prompt_builder

        prompt = builder.build_single_prompt("Test sentence", "test", "beginner")

        # Should contain some grammatical roles
        roles = analyzer.config.grammatical_roles
        for role_key in list(roles.keys())[:3]:  # Test first few roles
            assert role_key in prompt

    def test_fallback_prompt_generation(self, analyzer):
        """Test fallback prompt when main generation fails"""
        builder = analyzer.prompt_builder

        # Test with invalid inputs
        prompt = builder.build_single_prompt("", "", "invalid_complexity")

        assert isinstance(prompt, str)
        assert len(prompt) > 0  # Should still generate something

    @pytest.mark.parametrize("complexity", ["beginner", "intermediate", "advanced"])
    def test_complexity_specific_prompts(self, analyzer, complexity):
        """Test prompts vary by complexity level"""
        builder = analyzer.prompt_builder

        prompt = builder.build_single_prompt("Test sentence", "test", complexity)

        # Prompts should be different for different complexities
        beginner_prompt = builder.build_single_prompt("Test sentence", "test", "beginner")

        if complexity != "beginner":
            # For now, assume prompts are different (implement complexity-specific logic)
            pass  # Add specific assertions based on implementation
```

### 3. Response Parser Tests

**File:** `tests/test_{language}_response_parser.py`
```python
import pytest
import json

class Test{Language}ResponseParser:
    """Test response parsing component"""

    def test_initialization(self, analyzer):
        """Test parser initializes correctly"""
        parser = analyzer.response_parser
        assert hasattr(parser, 'config')

    def test_valid_response_parsing(self, analyzer, mock_responses):
        """Test parsing valid AI response"""
        parser = analyzer.response_parser

        response = json.dumps(mock_responses['valid_response'])
        result = parser.parse_response(response, "beginner", "Test sentence", "test")

        assert 'word_explanations' in result
        assert len(result['word_explanations']) > 0

        # Check structure of word explanations
        for word_exp in result['word_explanations']:
            assert len(word_exp) >= 4  # word, role, color, meaning
            assert isinstance(word_exp[0], str)  # word
            assert isinstance(word_exp[1], str)  # role
            assert word_exp[2].startswith('#')  # color
            assert isinstance(word_exp[3], str)  # meaning

    def test_malformed_response_handling(self, analyzer, mock_responses):
        """Test handling of malformed JSON responses"""
        parser = analyzer.response_parser

        # Should not crash, should return fallback
        result = parser.parse_response(mock_responses['malformed_response'], "beginner", "Test sentence", "test")

        # Should still return a valid structure
        assert isinstance(result, dict)

    def test_incomplete_response_handling(self, analyzer, mock_responses):
        """Test handling of incomplete responses"""
        parser = analyzer.response_parser

        response = json.dumps(mock_responses['incomplete_response'])
        result = parser.parse_response(response, "beginner", "Test sentence", "test")

        # Should handle gracefully
        assert isinstance(result, dict)

    def test_batch_response_parsing(self, analyzer, mock_responses):
        """Test parsing batch responses"""
        parser = analyzer.response_parser

        # Create mock batch response
        batch_response = {
            "batch_results": [
                mock_responses['valid_response'],
                mock_responses['valid_response']
            ]
        }

        response = json.dumps(batch_response)
        result = parser.parse_response(response, "beginner", "Test sentence", "test")

        # Should handle batch format
        assert isinstance(result, dict)

    def test_role_normalization(self, analyzer):
        """Test grammatical role normalization"""
        parser = analyzer.response_parser

        # Test with language-specific role that should be normalized
        test_response = {
            "words": [
                {"word": "test", "grammatical_role": "noun_term", "meaning": "test"}
            ],
            "explanations": {"overall_structure": "test", "key_features": "test"}
        }

        result = parser.parse_response(json.dumps(test_response), "beginner", "test sentence", "test")

        # Role should be normalized to universal form
        word_exp = result['word_explanations'][0]
        assert word_exp[1] == 'noun'  # Should be normalized

    def test_color_assignment(self, analyzer):
        """Test color assignment for grammatical roles"""
        parser = analyzer.response_parser

        response = json.dumps(mock_responses['valid_response'])
        result = parser.parse_response(response, "beginner", "Test sentence", "test")

        # All words should have valid colors
        for word_exp in result['word_explanations']:
            color = word_exp[2]
            assert color.startswith('#')
            assert len(color) == 7
```

### 4. Validator Tests

**File:** `tests/test_{language}_validator.py`
```python
import pytest

class Test{Language}Validator:
    """Test validation component"""

    def test_initialization(self, analyzer):
        """Test validator initializes correctly"""
        validator = analyzer.validator
        assert hasattr(validator, 'config')

    def test_high_confidence_result(self, analyzer, mock_responses):
        """Test validation of high-quality result"""
        validator = analyzer.validator

        # Mock a good result
        result = {
            'word_explanations': [
                ['The', 'determiner', '#FFAA00', 'Definite article'],
                ['cat', 'noun', '#4ECDC4', 'Subject noun'],
                ['sits', 'verb', '#FF44FF', 'Main verb']
            ],
            'explanations': {
                'overall_structure': 'Subject-verb sentence structure',
                'key_features': 'Present tense, definite article'
            }
        }

        validated = validator.validate_result(result, "The cat sits")

        assert 'confidence' in validated
        assert validated['confidence'] > 0.7  # Should be high confidence

    def test_low_confidence_result(self, analyzer):
        """Test validation of poor result"""
        validator = analyzer.validator

        # Mock a poor result
        result = {
            'word_explanations': [],  # Empty explanations
            'explanations': {}
        }

        validated = validator.validate_result(result, "Test sentence")

        assert 'confidence' in validated
        assert validated['confidence'] < 0.5  # Should be low confidence

    def test_word_count_validation(self, analyzer):
        """Test word count validation"""
        validator = analyzer.validator

        # Sentence with 4 words
        sentence = "The big cat sleeps"

        # Result with matching word count
        good_result = {
            'word_explanations': [
                ['The', 'determiner', '#FFAA00', 'test'],
                ['big', 'adjective', '#FF44FF', 'test'],
                ['cat', 'noun', '#4ECDC4', 'test'],
                ['sleeps', 'verb', '#9370DB', 'test']
            ],
            'explanations': {'overall_structure': 'test', 'key_features': 'test'}
        }

        # Result with mismatched word count
        bad_result = {
            'word_explanations': [
                ['The', 'determiner', '#FFAA00', 'test']
            ],  # Only 1 word explanation for 4-word sentence
            'explanations': {'overall_structure': 'test', 'key_features': 'test'}
        }

        good_confidence = validator.validate_result(good_result, sentence)['confidence']
        bad_confidence = validator.validate_result(bad_result, sentence)['confidence']

        assert good_confidence > bad_confidence  # Good result should have higher confidence

    def test_role_distribution_validation(self, analyzer):
        """Test grammatical role distribution validation"""
        validator = analyzer.validator

        sentence = "The cat sits"

        # Good distribution: has content words
        good_result = {
            'word_explanations': [
                ['The', 'determiner', '#FFAA00', 'test'],
                ['cat', 'noun', '#4ECDC4', 'test'],
                ['sits', 'verb', '#FF44FF', 'test']
            ],
            'explanations': {'overall_structure': 'test', 'key_features': 'test'}
        }

        # Bad distribution: no content words
        bad_result = {
            'word_explanations': [
                ['The', 'determiner', '#FFAA00', 'test'],
                ['cat', 'determiner', '#FFAA00', 'test'],
                ['sits', 'determiner', '#FFAA00', 'test']
            ],
            'explanations': {'overall_structure': 'test', 'key_features': 'test'}
        }

        good_confidence = validator.validate_result(good_result, sentence)['confidence']
        bad_confidence = validator.validate_result(bad_result, sentence)['confidence']

        assert good_confidence > bad_confidence

    def test_validation_metadata(self, analyzer):
        """Test validation metadata is added"""
        validator = analyzer.validator

        result = {
            'word_explanations': [['test', 'noun', '#FFAA00', 'test']],
            'explanations': {'overall_structure': 'test', 'key_features': 'test'}
        }

        validated = validator.validate_result(result, "test sentence")

        assert 'validation_metadata' in validated
        metadata = validated['validation_metadata']

        assert 'word_count' in metadata
        assert 'sentence_length' in metadata
        assert 'complexity_level' in metadata
        assert 'validation_timestamp' in metadata
```

## 🔗 Integration Testing

### 1. End-to-End Workflow Tests

**File:** `tests/test_{language}_integration.py`
```python
import pytest
from unittest.mock import patch, MagicMock

class Test{Language}Integration:
    """Integration tests for complete analyzer workflow"""

    def test_full_analysis_workflow(self, analyzer, mock_responses, monkeypatch):
        """Test complete analysis workflow with mocked AI"""
        # Mock the AI API call
        def mock_call_ai(prompt, api_key):
            return json.dumps(mock_responses['valid_response'])

        monkeypatch.setattr(analyzer, '_call_ai', mock_call_ai)

        result = analyzer.analyze_grammar(
            sentence="The cat sits on the mat",
            target_word="cat",
            complexity="beginner",
            gemini_api_key="mock_key"
        )

        # Verify result structure
        assert result.sentence == "The cat sits on the mat"
        assert result.target_word == "cat"
        assert result.language_code == analyzer.language_code
        assert result.complexity_level == "beginner"
        assert len(result.word_explanations) > 0
        assert result.confidence_score > 0
        assert result.html_output is not None

    def test_error_recovery_workflow(self, analyzer, monkeypatch):
        """Test error recovery and fallback mechanisms"""
        # Mock AI call to fail
        def mock_call_ai(prompt, api_key):
            raise Exception("API Error")

        monkeypatch.setattr(analyzer, '_call_ai', mock_call_ai)

        result = analyzer.analyze_grammar(
            sentence="Test sentence",
            target_word="test",
            complexity="beginner",
            gemini_api_key="mock_key"
        )

        # Should return fallback result
        assert result.sentence == "Test sentence"
        assert result.confidence_score < 0.5  # Low confidence for fallback
        assert len(result.word_explanations) > 0  # Should still have basic analysis

    @pytest.mark.parametrize("complexity", ["beginner", "intermediate", "advanced"])
    def test_complexity_level_integration(self, analyzer, complexity, mock_responses, monkeypatch):
        """Test integration with different complexity levels"""
        def mock_call_ai(prompt, api_key):
            return json.dumps(mock_responses['valid_response'])

        monkeypatch.setattr(analyzer, '_call_ai', mock_call_ai)

        result = analyzer.analyze_grammar(
            sentence="Test sentence",
            target_word="test",
            complexity=complexity,
            gemini_api_key="mock_key"
        )

        assert result.complexity_level == complexity

        # Color scheme should vary by complexity
        colors = result.color_scheme
        assert isinstance(colors, dict)
        assert len(colors) > 0

    def test_batch_processing_integration(self, analyzer, sample_sentences, monkeypatch):
        """Test batch processing integration"""
        # Mock batch AI response
        def mock_call_ai(prompt, api_key):
            batch_result = {
                "batch_results": [
                    mock_responses['valid_response'],
                    mock_responses['valid_response']
                ]
            }
            return json.dumps(batch_result)

        monkeypatch.setattr(analyzer, '_call_ai', mock_call_ai)

        # Test batch processing if implemented
        # This depends on whether batch processing is implemented
        pass  # Implement based on analyzer capabilities

    def test_component_interaction(self, analyzer, mock_responses, monkeypatch):
        """Test that all components work together correctly"""
        # Mock AI call
        def mock_call_ai(prompt, api_key):
            return json.dumps(mock_responses['valid_response'])

        monkeypatch.setattr(analyzer, '_call_ai', mock_call_ai)

        # Track component calls
        with patch.object(analyzer.prompt_builder, 'build_single_prompt') as mock_build, \
             patch.object(analyzer.response_parser, 'parse_response') as mock_parse, \
             patch.object(analyzer.validator, 'validate_result') as mock_validate:

            mock_build.return_value = "mock prompt"
            mock_parse.return_value = {'word_explanations': [], 'explanations': {}}
            mock_validate.return_value = {'confidence': 0.8}

            result = analyzer.analyze_grammar("test", "test", "beginner", "key")

            # Verify all components were called
            mock_build.assert_called_once()
            mock_parse.assert_called_once()
            mock_validate.assert_called_once()

    def test_performance_constraints(self, analyzer, mock_responses, monkeypatch):
        """Test performance meets requirements"""
        import time

        def mock_call_ai(prompt, api_key):
            time.sleep(0.1)  # Simulate API delay
            return json.dumps(mock_responses['valid_response'])

        monkeypatch.setattr(analyzer, '_call_ai', mock_call_ai)

        start_time = time.time()
        result = analyzer.analyze_grammar("test", "test", "beginner", "key")
        end_time = time.time()

        duration = end_time - start_time

        # Should complete within reasonable time (allowing for mock delay)
        assert duration < 1.0  # Less than 1 second
```

## 🧠 Linguistic Accuracy Testing

### 1. Linguistic Validation Framework

**File:** `tests/utils/linguistic_validators.py`
```python
import json
from typing import Dict, List, Any
from pathlib import Path

class LinguisticValidator:
    """Validate linguistic accuracy of analysis results"""

    def __init__(self, language_code: str):
        self.language_code = language_code
        self.validation_rules = self._load_validation_rules()

    def _load_validation_rules(self) -> Dict[str, Any]:
        """Load linguistic validation rules"""
        rules_file = Path(__file__).parent.parent / "fixtures" / "linguistic_rules.json"
        if rules_file.exists():
            with open(rules_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def validate_grammatical_roles(self, word_explanations: List[List[str]], sentence: str) -> Dict[str, Any]:
        """Validate grammatical role assignments"""
        issues = []
        score = 1.0

        # Check for impossible role combinations
        roles = [exp[1] for exp in word_explanations]

        # Language-specific validation rules
        if self.language_code == "en":
            score *= self._validate_english_roles(roles, issues)
        # Add other languages...

        # Check role distribution
        role_counts = {}
        for role in roles:
            role_counts[role] = role_counts.get(role, 0) + 1

        # Validate against expected distributions
        expected_distributions = self.validation_rules.get('role_distributions', {})
        for role, expected_ratio in expected_distributions.items():
            actual_ratio = role_counts.get(role, 0) / len(roles)
            if abs(actual_ratio - expected_ratio) > 0.2:  # 20% tolerance
                issues.append(f"Unexpected {role} ratio: {actual_ratio:.2f} (expected ~{expected_ratio:.2f})")
                score *= 0.9

        return {
            'score': score,
            'issues': issues,
            'role_distribution': role_counts
        }

    def _validate_english_roles(self, roles: List[str], issues: List[str]) -> float:
        """English-specific role validation"""
        score = 1.0

        # Check for basic sentence requirements
        has_subject = any(role in ['noun', 'pronoun'] for role in roles)
        has_verb = 'verb' in roles

        if not has_subject:
            issues.append("Missing subject (noun or pronoun)")
            score *= 0.7

        if not has_verb:
            issues.append("Missing main verb")
            score *= 0.8

        # Check for impossible combinations
        if roles.count('verb') > 3:  # Too many verbs
            issues.append("Too many verbs for sentence length")
            score *= 0.8

        return score

    def validate_explanations(self, explanations: Dict[str, str]) -> Dict[str, Any]:
        """Validate quality of explanations"""
        issues = []
        score = 1.0

        required_keys = ['overall_structure', 'key_features']
        for key in required_keys:
            if key not in explanations:
                issues.append(f"Missing explanation: {key}")
                score *= 0.8
            elif len(explanations[key].strip()) < 10:
                issues.append(f"Explanation too short: {key}")
                score *= 0.9

        return {
            'score': score,
            'issues': issues
        }

    def validate_word_alignment(self, word_explanations: List[List[str]], sentence: str) -> Dict[str, Any]:
        """Validate word-to-sentence alignment"""
        issues = []
        score = 1.0

        # Basic tokenization
        sentence_words = sentence.split()
        analyzed_words = [exp[0] for exp in word_explanations]

        # Check word count match
        if len(analyzed_words) != len(sentence_words):
            issues.append(f"Word count mismatch: {len(analyzed_words)} analyzed vs {len(sentence_words)} in sentence")
            score *= 0.8

        # Check word content match (basic)
        for i, (analyzed, expected) in enumerate(zip(analyzed_words, sentence_words)):
            if analyzed.lower() != expected.lower():
                issues.append(f"Word mismatch at position {i}: '{analyzed}' vs '{expected}'")
                score *= 0.95

        return {
            'score': score,
            'issues': issues,
            'alignment_score': 1.0 - (len(issues) * 0.1)
        }
```

### 2. Linguistic Accuracy Tests

**File:** `tests/test_{language}_linguistic_accuracy.py`
```python
import pytest
from .utils.linguistic_validators import LinguisticValidator

class Test{Language}LinguisticAccuracy:
    """Test linguistic accuracy of analysis results"""

    @pytest.fixture
    def linguistic_validator(self):
        return LinguisticValidator("{code}")

    def test_grammatical_role_accuracy(self, analyzer, sample_sentences, linguistic_validator, monkeypatch):
        """Test grammatical role assignments for accuracy"""
        # Mock AI to return controlled responses
        def mock_call_ai(prompt, api_key):
            # Return pre-validated correct analysis
            return json.dumps({
                "words": [
                    {"word": "The", "grammatical_role": "determiner", "meaning": "Definite article"},
                    {"word": "cat", "grammatical_role": "noun", "meaning": "Subject"},
                    {"word": "sits", "grammatical_role": "verb", "meaning": "Main verb"}
                ],
                "explanations": {
                    "overall_structure": "Subject-verb sentence",
                    "key_features": "Present tense, definite article"
                }
            })

        monkeypatch.setattr(analyzer, '_call_ai', mock_call_ai)

        result = analyzer.analyze_grammar("The cat sits", "cat", "beginner", "mock_key")

        # Validate linguistic accuracy
        validation = linguistic_validator.validate_grammatical_roles(
            result.word_explanations, result.sentence
        )

        assert validation['score'] > 0.7, f"Linguistic validation failed: {validation['issues']}"

    def test_explanation_quality(self, analyzer, linguistic_validator, monkeypatch):
        """Test quality of generated explanations"""
        def mock_call_ai(prompt, api_key):
            return json.dumps({
                "words": [{"word": "test", "grammatical_role": "noun", "meaning": "test"}],
                "explanations": {
                    "overall_structure": "Comprehensive sentence structure explanation with linguistic details",
                    "key_features": "Important grammatical features and patterns explained clearly"
                }
            })

        monkeypatch.setattr(analyzer, '_call_ai', mock_call_ai)

        result = analyzer.analyze_grammar("test sentence", "test", "beginner", "mock_key")

        validation = linguistic_validator.validate_explanations(result.explanations)

        assert validation['score'] > 0.8, f"Explanation validation failed: {validation['issues']}"

    def test_word_alignment_accuracy(self, analyzer, linguistic_validator, monkeypatch):
        """Test word-to-sentence alignment"""
        def mock_call_ai(prompt, api_key):
            return json.dumps({
                "words": [
                    {"word": "The", "grammatical_role": "determiner", "meaning": "test"},
                    {"word": "quick", "grammatical_role": "adjective", "meaning": "test"},
                    {"word": "brown", "grammatical_role": "adjective", "meaning": "test"},
                    {"word": "fox", "grammatical_role": "noun", "meaning": "test"}
                ],
                "explanations": {"overall_structure": "test", "key_features": "test"}
            })

        monkeypatch.setattr(analyzer, '_call_ai', mock_call_ai)

        result = analyzer.analyze_grammar("The quick brown fox", "fox", "beginner", "mock_key")

        validation = linguistic_validator.validate_word_alignment(
            result.word_explanations, result.sentence
        )

        assert validation['score'] > 0.8, f"Alignment validation failed: {validation['issues']}"

    @pytest.mark.parametrize("sentence,expected_score", [
        ("The cat sits", 0.9),  # Simple, correct
        ("Cat sits the", 0.3),  # Word order error
        ("The", 0.2),  # Too short
    ])
    def test_sentence_complexity_validation(self, analyzer, linguistic_validator, sentence, expected_score, monkeypatch):
        """Test validation of different sentence complexities"""
        def mock_call_ai(prompt, api_key):
            # Return basic analysis for any sentence
            words = sentence.split()
            word_explanations = [
                [word, "noun", "#FFAA00", f"Word: {word}"] for word in words
            ]
            return json.dumps({
                "words": [{"word": word, "grammatical_role": "noun", "meaning": f"Word: {word}"} for word in words],
                "explanations": {"overall_structure": "Basic analysis", "key_features": "Words identified"}
            })

        monkeypatch.setattr(analyzer, '_call_ai', mock_call_ai)

        result = analyzer.analyze_grammar(sentence, "", "beginner", "mock_key")

        # For now, just check that analysis completes
        assert result is not None
        assert len(result.word_explanations) > 0

        # Linguistic validation score should reflect sentence quality
        # (This is a simplified test - real validation would be more sophisticated)
```

## ⚡ Performance Testing

### 1. Performance Benchmarks

**File:** `tests/test_{language}_performance.py`
```python
import pytest
import time
from statistics import mean, stdev

class Test{Language}Performance:
    """Performance tests for analyzer"""

    @pytest.fixture
    def performance_sentences(self):
        """Sentences of varying complexity for performance testing"""
        return {
            'short': "The cat sits",
            'medium': "The quick brown fox jumps over the lazy dog",
            'long': "In a hole in the ground there lived a hobbit who was quite content with his peaceful life until one day he found a magical ring",
            'complex': "The algorithm, having been optimized for performance and thoroughly tested across multiple datasets, now processes information exponentially faster than previous implementations while maintaining backward compatibility."
        }

    def test_response_time_requirements(self, analyzer, performance_sentences, monkeypatch):
        """Test response time meets requirements"""
        def mock_call_ai(prompt, api_key):
            time.sleep(0.05)  # Simulate API delay
            return json.dumps({
                "words": [{"word": "test", "grammatical_role": "noun", "meaning": "test"}],
                "explanations": {"overall_structure": "test", "key_features": "test"}
            })

        monkeypatch.setattr(analyzer, '_call_ai', mock_call_ai)

        results = {}
        for name, sentence in performance_sentences.items():
            start_time = time.time()
            result = analyzer.analyze_grammar(sentence, "", "beginner", "mock_key")
            end_time = time.time()

            duration = end_time - start_time
            results[name] = duration

            # Assert maximum response times
            max_times = {
                'short': 0.5,    # 500ms
                'medium': 1.0,   # 1s
                'long': 2.0,     # 2s
                'complex': 3.0   # 3s
            }

            assert duration < max_times[name], f"{name} sentence too slow: {duration:.2f}s"

    def test_memory_usage_stability(self, analyzer, monkeypatch):
        """Test memory usage doesn't grow with repeated calls"""
        import psutil
        import os

        def mock_call_ai(prompt, api_key):
            return json.dumps({
                "words": [{"word": "test", "grammatical_role": "noun", "meaning": "test"}],
                "explanations": {"overall_structure": "test", "key_features": "test"}
            })

        monkeypatch.setattr(analyzer, '_call_ai', mock_call_ai)

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Make multiple calls
        for i in range(100):
            analyzer.analyze_grammar(f"Test sentence {i}", "test", "beginner", "mock_key")

        final_memory = process.memory_info().rss
        memory_growth = final_memory - initial_memory

        # Memory growth should be minimal (less than 10MB)
        assert memory_growth < 10 * 1024 * 1024, f"Excessive memory growth: {memory_growth / 1024 / 1024:.1f}MB"

    def test_concurrent_request_handling(self, analyzer, monkeypatch):
        """Test handling multiple concurrent requests"""
        import threading

        results = []
        errors = []

        def mock_call_ai(prompt, api_key):
            time.sleep(0.01)  # Small delay
            return json.dumps({
                "words": [{"word": "test", "grammatical_role": "noun", "meaning": "test"}],
                "explanations": {"overall_structure": "test", "key_features": "test"}
            })

        monkeypatch.setattr(analyzer, '_call_ai', mock_call_ai)

        def analyze_request(sentence_num):
            try:
                result = analyzer.analyze_grammar(f"Sentence {sentence_num}", "test", "beginner", "mock_key")
                results.append(result)
            except Exception as e:
                errors.append(e)

        # Start multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=analyze_request, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # All requests should succeed
        assert len(results) == 10
        assert len(errors) == 0

    def test_scalability_with_input_size(self, analyzer, monkeypatch):
        """Test performance scales appropriately with input size"""
        def mock_call_ai(prompt, api_key):
            # Response time proportional to input size
            input_length = len(prompt)
            time.sleep(min(input_length / 10000, 0.1))  # Max 100ms
            return json.dumps({
                "words": [{"word": "test", "grammatical_role": "noun", "meaning": "test"}],
                "explanations": {"overall_structure": "test", "key_features": "test"}
            })

        monkeypatch.setattr(analyzer, '_call_ai', mock_call_ai)

        sizes_and_times = []

        for words in [5, 10, 20, 50]:
            sentence = " ".join([f"word{i}" for i in range(words)])

            start_time = time.time()
            result = analyzer.analyze_grammar(sentence, "word1", "beginner", "mock_key")
            end_time = time.time()

            duration = end_time - start_time
            sizes_and_times.append((words, duration))

        # Performance should degrade gracefully
        # (Simple check: larger inputs shouldn't be disproportionately slower)
        small_time = sizes_and_times[0][1]
        large_time = sizes_and_times[-1][1]

        # Large input should be no more than 5x slower than small input
        assert large_time < small_time * 5, "Performance degradation too steep"
```

## 🚀 CI/CD Integration

### 1. Automated Test Pipeline

**File:** `.github/workflows/test_{language}_analyzer.yml`
```yaml
name: Test {Language} Analyzer

on:
  push:
    paths:
      - 'languages/{language}/**'
      - 'tests/**'
  pull_request:
    paths:
      - 'languages/{language}/**'
      - 'tests/**'

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov

    - name: Run unit tests
      run: |
        cd languages/{language}
        pytest tests/ -v --cov=. --cov-report=xml

    - name: Run integration tests
      run: |
        cd languages/{language}
        pytest tests/test_{language}_integration.py -v

    - name: Run performance tests
      run: |
        cd languages/{language}
        pytest tests/test_{language}_performance.py -v

    - name: Upload coverage reports
      uses: codecov/codecov-action@v3
      with:
        file: ./languages/{language}/coverage.xml

  quality:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: Install quality tools
      run: |
        pip install flake8 black isort mypy

    - name: Run linting
      run: |
        cd languages/{language}
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

    - name: Check formatting
      run: |
        cd languages/{language}
        black --check .
        isort --check-only .

    - name: Run type checking
      run: |
        cd languages/{language}
        mypy . --ignore-missing-imports
```

### 2. Test Coverage Requirements

**File:** `languages/{language}/pytest.ini`
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --strict-markers
    --strict-config
    --cov=.
    --cov-report=term-missing
    --cov-report=xml
    --cov-fail-under=80
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    performance: marks tests as performance tests
    linguistic: marks tests as linguistic accuracy tests
```

## 📊 Test Results Analysis

### 1. Coverage Analysis Script

**File:** `tests/analyze_coverage.py`
```python
#!/usr/bin/env python3
"""Analyze test coverage and generate reports"""

import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any

def analyze_coverage(coverage_file: str) -> Dict[str, Any]:
    """Analyze coverage report and generate insights"""
    tree = ET.parse(coverage_file)
    root = tree.getroot()

    total_lines = 0
    covered_lines = 0
    files_coverage = {}

    for package in root.findall('.//package'):
        for cls in package.findall('.//class'):
            filename = cls.get('filename')
            lines = int(cls.get('line-rate', '0').split('/')[1])
            hits = int(cls.get('line-rate', '0').split('/')[0])

            files_coverage[filename] = {
                'lines': lines,
                'covered': hits,
                'percentage': (hits / lines * 100) if lines > 0 else 0
            }

            total_lines += lines
            covered_lines += hits

    overall_coverage = (covered_lines / total_lines * 100) if total_lines > 0 else 0

    return {
        'overall_coverage': overall_coverage,
        'total_lines': total_lines,
        'covered_lines': covered_lines,
        'files': files_coverage,
        'uncovered_files': [f for f, data in files_coverage.items() if data['percentage'] < 80]
    }

def generate_coverage_report(analysis: Dict[str, Any]) -> str:
    """Generate human-readable coverage report"""
    report = f"""
# Test Coverage Analysis Report

## Overall Coverage: {analysis['overall_coverage']:.1f}%

**Total Lines:** {analysis['total_lines']}
**Covered Lines:** {analysis['covered_lines']}

## Files with Low Coverage (< 80%)

"""

    for filename in analysis['uncovered_files']:
        data = analysis['files'][filename]
        report += f"- **{filename}**: {data['percentage']:.1f}% ({data['covered']}/{data['lines']} lines)\n"

    if not analysis['uncovered_files']:
        report += "🎉 All files meet coverage requirements!\n"

    return report

if __name__ == "__main__":
    coverage_file = Path("coverage.xml")
    if coverage_file.exists():
        analysis = analyze_coverage(str(coverage_file))
        report = generate_coverage_report(analysis)
        print(report)

        # Save report
        with open("coverage_analysis.md", "w") as f:
            f.write(report)
    else:
        print("Coverage file not found. Run tests with coverage first.")
```

---

**Remember:** All tests must follow gold standard patterns from [Hindi](languages/hindi/hi_analyzer.py) and [Chinese Simplified](languages/zh/zh_analyzer.py). Focus on natural validation testing, component isolation, and gold standard comparison - no artificial confidence boosting tests.
- [ ] **Mock Management:** Proper mocking of external dependencies
- [ ] **Flaky Test Detection:** Automated detection of unreliable tests
- [ ] **Test Documentation:** Clear test naming and documentation

## 🚨 Common Testing Pitfalls

### 1. Insufficient Mocking
**Problem:** Tests depend on external APIs
**Prevention:** Mock all external dependencies (AI API, databases, etc.)

### 2. Brittle Tests
**Problem:** Tests fail with minor code changes
**Prevention:** Test behavior, not implementation details

### 3. Missing Edge Cases
**Problem:** Bugs discovered in production
**Prevention:** Comprehensive edge case testing

### 4. Slow Tests
**Problem:** CI/CD pipeline becomes bottleneck
**Prevention:** Fast unit tests, separate slow integration tests

### 5. Poor Test Data
**Problem:** Tests don't reflect real usage
**Prevention:** Use realistic, diverse test data

## 🧪 Word Meanings Dictionary Testing (Sino-Tibetan Languages)

### Word Meanings Quality Tests

**File:** `tests/test_{language}_word_meanings.py`
```python
import pytest
import json
from pathlib import Path

class TestWordMeanings:
    """Test word meanings dictionary for rich explanations"""

    def test_word_meanings_file_exists(self):
        """Test that word meanings JSON file exists"""
        meanings_file = Path("infrastructure/data/{language}_word_meanings.json")
        assert meanings_file.exists(), "Word meanings dictionary file must exist"

    def test_word_meanings_is_valid_json(self):
        """Test that word meanings file contains valid JSON"""
        meanings_file = Path("infrastructure/data/{language}_word_meanings.json")
        with open(meanings_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert isinstance(data, dict), "Word meanings must be a dictionary"
        assert len(data) > 0, "Word meanings dictionary must not be empty"

    def test_word_meanings_have_rich_explanations(self):
        """Test that word meanings provide specific explanations, not generic roles"""
        meanings_file = Path("infrastructure/data/{language}_word_meanings.json")
        with open(meanings_file, 'r', encoding='utf-8') as f:
            word_meanings = json.load(f)
        
        # Test essential vocabulary has rich meanings
        essential_words = ["一", "二", "三", "如果", "因為", "答案"]  # Adapt for language
        
        for word in essential_words:
            if word in word_meanings:
                meaning = word_meanings[word]
                # Should not contain generic patterns
                assert "in grammar" not in meaning, f"'{word}' has generic explanation: {meaning}"
                assert "in {language}" not in meaning, f"'{word}' has generic explanation: {meaning}"
                # Should have specific meaning
                assert len(meaning) > 10, f"'{word}' meaning too short: {meaning}"

    def test_config_loads_word_meanings(self, config):
        """Test that config loads word meanings from JSON file"""
        assert hasattr(config, 'word_meanings'), "Config must have word_meanings attribute"
        assert isinstance(config.word_meanings, dict), "word_meanings must be a dictionary"
        assert len(config.word_meanings) > 0, "word_meanings must not be empty"

    def test_fallbacks_use_word_meanings(self, fallbacks):
        """Test that fallbacks prioritize word meanings over generic explanations"""
        # Test with words that should have rich meanings
        test_cases = [
            ("三", "three (numeral)"),  # Numeral
            ("如果", "if (conjunction)"),  # Conjunction
            ("答案", "answer, solution (noun)"),  # Compound noun
        ]
        
        for word, expected_meaning in test_cases:
            result = fallbacks._analyze_word(word)
            actual_meaning = result['individual_meaning']
            
            # Should use rich meaning from dictionary, not generic fallback
            assert actual_meaning == expected_meaning, f"'{word}' should have meaning '{expected_meaning}', got '{actual_meaning}'"
            assert result['confidence'] == 'high', f"'{word}' should have high confidence from dictionary"

    def test_fallback_generic_only_when_no_dictionary(self, fallbacks):
        """Test that generic explanations are used only when word not in dictionary"""
        # Test with a word that shouldn't be in dictionary
        fake_word = "xyz_nonexistent_word_123"
        
        result = fallbacks._analyze_word(fake_word)
        meaning = result['individual_meaning']
        
        # Should use generic fallback explanation
        assert "in grammar" in meaning or "in {language}" in meaning, f"'{fake_word}' should use generic fallback, got: {meaning}"
        assert result['confidence'] == 'low', f"'{fake_word}' should have low confidence for generic fallback"

    @pytest.mark.parametrize("word,expected_contains", [
        ("三", "numeral"),  # Should identify as numeral
        ("如果", "conjunction"),  # Should identify as conjunction
        ("答案", "noun"),  # Should identify as noun
    ])
    def test_word_meanings_grammatical_roles(self, fallbacks, word, expected_contains):
        """Test that word meanings provide correct grammatical role identification"""
        result = fallbacks._analyze_word(word)
        role = result['grammatical_role']
        
        assert expected_contains in role, f"'{word}' role '{role}' should contain '{expected_contains}'"
```

---

**🎯 Ready to start testing?** Begin with unit tests for individual components, then progress to integration and performance testing. Remember: comprehensive testing prevents production issues!

**Need help with testing?** Refer to the [Troubleshooting Guide](troubleshooting_guide.md) for common test issues, or the [Architecture Guide](architecture_guide.md) for component interaction patterns.

**📊 Pro tip:** Aim for 80%+ test coverage and <500ms response times for optimal user experience.</content>
<parameter name="filePath">d:\Language Learning\LanguagLearning\language_grammar_generator\testing_guide.md