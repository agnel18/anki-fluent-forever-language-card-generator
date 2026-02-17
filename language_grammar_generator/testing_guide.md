# Testing Guide
## Comprehensive Testing Strategy Following Gold Standard Patterns

**Primary Gold Standard:** [French v2.0](languages/french/fr_analyzer.py) - Enterprise reliability benchmark
**Secondary Reference:** [Chinese Simplified](languages/chinese_simplified/zh_analyzer.py)
**Critical:** Test against French v2.0 gold standard - enterprise reliability, 5-level fallbacks, comprehensive monitoring
**Prerequisites:** Study French v2.0 enterprise patterns before testing
**Architecture:** Follow [Architecture Guide](architecture_guide.md) with French v2.0 compliance
**Time Estimate:** 1-2 weeks for gold standard compliant test suite

## ðŸŽ¯ Testing Philosophy - French v2.0 Gold Standard Compliance

### Quality Assurance Principles - Match French v2.0
- **Gold Standard Comparison:** All tests compare with French v2.0 Clean Architecture results
- **External Configuration Testing:** Test YAML/JSON file loading (French v2.0 pattern)
- **Integrated Fallback Testing:** Test fallbacks within domain layer (French v2.0 pattern)
- **Natural Validation Testing:** No tests for artificial confidence boosting (removed)
- **Component Isolation:** Test components separately like French v2.0
- **Facade Pattern Testing:** Test complete Clean Architecture orchestration
- **Jinja2 Template Testing:** Test template-based prompt generation

### Testing Pyramid - French v2.0 Validation
```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  (Few tests, high value)
â”‚ Gold Standard   â”‚  Compare with French v2.0
â”‚ Compliance      â”‚  Clean Architecture validation
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ System Tests    â”‚  End-to-end facade workflow
â”‚ Integration     â”‚  Domain component orchestration
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Unit Tests      â”‚  Individual domain components
â”‚                 â”‚  (Many tests, fast)
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

## ðŸš€ Automated Testing Framework

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
# Compare with French v2.0 and Chinese Simplified
python language_grammar_generator/compare_with_gold_standard.py --language {language_code}

# Detailed comparison with export
python language_grammar_generator/compare_with_gold_standard.py --language {language_code} --detailed --export-results
```

## ðŸ§ª Testing Framework Setup - French v2.0 Structure

### 1. Directory Structure - Like French v2.0
```
languages/{language}/tests/
â”œâ”€â”€ __init__.py
â”œâ”€â”€ conftest.py                    # Pytest configuration
â”œâ”€â”€ test_{language}_analyzer.py    # Main facade tests (Clean Architecture)
â”œâ”€â”€ test_{language}_config.py      # External config loading tests (YAML/JSON)
â”œâ”€â”€ test_{language}_prompt_builder.py  # Jinja2 template tests
â”œâ”€â”€ test_{language}_response_parser.py # Response parsing with integrated fallbacks
â”œâ”€â”€ test_{language}_validator.py   # NATURAL validation tests (NO boosting)
â”œâ”€â”€ test_{language}_integration.py # Facade orchestration tests
â”œâ”€â”€ test_{language}_performance.py # Performance vs French v2.0
â”œâ”€â”€ test_gold_standard_comparison.py # Compare with French v2.0
â”œâ”€â”€ fixtures/
â”‚   â”œâ”€â”€ sample_sentences.json     # Test sentences
â”‚   â”œâ”€â”€ expected_outputs.json     # Expected results like gold standards
â”‚   â””â”€â”€ mock_responses.json       # Mock AI responses
â””â”€â”€ utils/
    â””â”€â”€ test_helpers.py           # Gold standard test helpers
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
    return {Language}Config()  # Loads from YAML like French/Chinese

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
    â”œâ”€â”€ test_helpers.py           # Test utilities
    â””â”€â”€ linguistic_validators.py  # Linguistic validation helpers
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

## ðŸ§© Unit Testing

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

    def test_robust_json_parsing_markdown_blocks(self, analyzer):
        """Test robust JSON parsing with markdown code blocks"""
        parser = analyzer.response_parser

        # Test response wrapped in markdown code block
        markdown_response = '''Here's my analysis:

```json
{{
  "words": [
    {{
      "word": "test",
      "grammatical_role": "noun",
      "meaning": "test word"
    }}
  ],
  "explanations": {{
    "overall_structure": "Simple test",
    "key_features": "Basic structure"
  }}
}}
```

This should work correctly.'''

        result = parser.parse_response(markdown_response, "beginner", "Test sentence", "test")

        assert 'word_explanations' in result
        assert 'explanations' in result
        assert len(result['word_explanations']) == 1
        assert result['explanations']['overall_structure'] == "Simple test"

    def test_robust_json_parsing_inline_json(self, analyzer):
        """Test robust JSON parsing with JSON embedded in explanatory text"""
        parser = analyzer.response_parser

        # Test JSON embedded in explanatory text
        inline_response = '''Let me analyze this sentence for you.

The grammatical breakdown is: {
  "words": [
    {
      "word": "test",
      "grammatical_role": "noun",
      "meaning": "test subject"
    },
    {
      "word": "runs",
      "grammatical_role": "verb",
      "meaning": "action verb"
    }
  ],
  "explanations": {
    "overall_structure": "Subject-verb sentence",
    "key_features": "Present tense"
  }
}

I hope this helps!'''

        result = parser.parse_response(inline_response, "beginner", "Test sentence", "test")

        assert 'word_explanations' in result
        assert 'explanations' in result
        assert len(result['word_explanations']) == 2
        assert result['explanations']['overall_structure'] == "Subject-verb sentence"

    def test_robust_json_parsing_ai_text_prefix(self, analyzer):
        """Test robust JSON parsing with AI explanatory text prefix"""
        parser = analyzer.response_parser

        # Test response starting with explanatory text then JSON
        ai_response = '''Based on my analysis, here is the grammatical breakdown:

{
  "words": [
    {
      "word": "The",
      "grammatical_role": "determiner",
      "meaning": "Definite article"
    }
  ],
  "explanations": {
    "overall_structure": "Simple sentence",
    "key_features": "Article usage"
  }
}

This analysis considers language-specific features.'''

        result = parser.parse_response(ai_response, "beginner", "Test sentence", "test")

        assert 'word_explanations' in result
        assert 'explanations' in result
        assert len(result['word_explanations']) == 1
        assert "Simple sentence" in result['explanations']['overall_structure']

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

## ðŸ”— Integration Testing

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

## ðŸ§  Linguistic Accuracy Testing

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

## âš¡ Performance Testing

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

## ðŸŽ¯ Content Generation Testing - Critical Addition

### Overview - Why This Was Missing
Content generation testing was not included in the original comprehensive test suite, which led to Arabic sentence generation falling back to English samples. This section adds the missing test coverage for:

- Language-specific sentence generation prompts
- Content generator integration with language analyzers
- AI response parsing for different languages
- Fallback mechanism validation

### 1. Content Generation Test Structure
```
languages/{language}/tests/
â”œâ”€â”€ test_content_generation.py      # Language-specific content generation
â”œâ”€â”€ test_content_integration.py     # Content generator + analyzer integration
â””â”€â”€ fixtures/
    â”œâ”€â”€ content_generation_samples.json
    â””â”€â”€ content_generation_expected.json
```

### 2. Language-Specific Content Generation Tests

**File:** `tests/test_{language}_content_generation.py`
```python
import pytest
from unittest.mock import patch, MagicMock
from streamlit_app.services.generation.content_generator import ContentGenerator
from streamlit_app.language_analyzers.analyzer_registry import get_analyzer

class Test{Language}ContentGeneration:
    """Test language-specific content generation integration"""

    @pytest.fixture
    def content_generator(self):
        """Create content generator for testing"""
        return ContentGenerator()

    @pytest.fixture
    def analyzer(self):
        """Get language analyzer"""
        return get_analyzer('{language_code}')

    def test_analyzer_has_sentence_generation_prompt(self, analyzer):
        """Test that analyzer provides sentence generation prompts"""
        assert analyzer is not None, "Analyzer should be available"

        prompt = analyzer.get_sentence_generation_prompt(
            word="test_word",
            language="{Language}",
            num_sentences=3,
            enriched_meaning="test meaning",
            max_length=15,
            difficulty="intermediate"
        )

        assert prompt is not None, "Should provide custom sentence generation prompt"
        assert isinstance(prompt, str), "Prompt should be a string"
        assert len(prompt) > 100, "Prompt should be substantial"

        # Language-specific validations
        assert "{Language}" in prompt, "Should reference correct language"
        assert "test_word" in prompt, "Should include target word"

    def test_prompt_contains_language_specific_instructions(self, analyzer):
        """Test that prompts include language-specific requirements"""
        prompt = analyzer.get_sentence_generation_prompt(
            word="test",
            language="{Language}",
            num_sentences=3
        )

        # Check for language-specific requirements
        # (Customize these assertions based on language requirements)
        assert "Arabic" in prompt or "Hindi" in prompt or "Chinese" in prompt, "Should specify language"

    @pytest.mark.parametrize("difficulty", ["beginner", "intermediate", "advanced"])
    def test_prompt_varies_by_difficulty(self, analyzer, difficulty):
        """Test that prompts adapt to difficulty levels"""
        prompt = analyzer.get_sentence_generation_prompt(
            word="test",
            language="{Language}",
            num_sentences=3,
            difficulty=difficulty
        )

        assert difficulty in prompt, f"Should include {difficulty} difficulty level"

    def test_prompt_handles_missing_parameters(self, analyzer):
        """Test prompt generation with minimal parameters"""
        prompt = analyzer.get_sentence_generation_prompt(
            word="test",
            language="{Language}",
            num_sentences=2
        )

        assert prompt is not None, "Should handle missing optional parameters"
        assert "test" in prompt, "Should include target word"

    def test_prompt_integration_with_content_generator(self, content_generator, analyzer):
        """Test that content generator uses analyzer prompts"""
        # Mock the AI call to avoid actual API calls
        with patch.object(content_generator, '_get_client') as mock_get_client:
            mock_client = MagicMock()
            mock_get_client.return_value = mock_client

            # Mock successful AI response
            mock_response = MagicMock()
            mock_response.text = '''
MEANING: test (a test word)
RESTRICTIONS: No specific restrictions
SENTENCES:
1. Test sentence one.
2. Test sentence two.
3. Test sentence three.
TRANSLATIONS:
1. Translation one.
2. Translation two.
3. Translation three.
IPA:
1. /test/
2. /test/
3. /test/
KEYWORDS:
1. test, word, language
2. test, word, language
3. test, word, language
'''
            mock_client.generate_content.return_value = mock_response

            # Test content generation
            result = content_generator.generate_word_meaning_sentences_and_keywords(
                word="test",
                language="{Language}",
                num_sentences=3,
                gemini_api_key="test_key"
            )

            # Verify it used custom prompt (not generic)
            assert result is not None, "Should generate content successfully"
            assert 'sentences' in result, "Should include sentences"
            assert len(result['sentences']) == 3, "Should generate requested number of sentences"
```

### 3. Content Generator Integration Tests

**File:** `tests/test_content_integration.py`
```python
import pytest
from unittest.mock import patch, MagicMock
from streamlit_app.services.generation.content_generator import ContentGenerator
from streamlit_app.language_analyzers.analyzer_registry import get_analyzer

class TestContentGeneratorIntegration:
    """Test content generator integration with language analyzers"""

    @pytest.fixture
    def content_generator(self):
        return ContentGenerator()

    def test_language_analyzer_discovery(self, content_generator):
        """Test that content generator can find language analyzers"""
        # Test various language codes
        test_languages = ['ar', 'hi', 'zh', 'es', 'fr']

        for lang_code in test_languages:
            analyzer = get_analyzer(lang_code)
            if analyzer:  # Some languages might not have analyzers yet
                assert hasattr(analyzer, 'get_sentence_generation_prompt'), \
                    f"Analyzer {lang_code} should have sentence generation prompt method"

    def test_fallback_to_generic_prompt(self, content_generator):
        """Test fallback when no language-specific analyzer available"""
        # Use a language that doesn't have an analyzer
        with patch.object(content_generator, '_get_client') as mock_get_client:
            mock_client = MagicMock()
            mock_get_client.return_value = mock_client

            mock_response = MagicMock()
            mock_response.text = '''
MEANING: nonexistent (a made-up word)
RESTRICTIONS: No restrictions
SENTENCES:
1. This is a sample sentence with nonexistent.
2. Another sample sentence with nonexistent.
3. Third sample sentence with nonexistent.
TRANSLATIONS:
1. Translation one.
2. Translation two.
3. Translation three.
IPA:
1. /test/
2. /test/
3. /test/
KEYWORDS:
1. test, word, language
2. test, word, language
3. test, word, language
'''
            mock_client.generate_content.return_value = mock_response

            result = content_generator.generate_word_meaning_sentences_and_keywords(
                word="nonexistent",
                language="NonExistentLanguage",
                num_sentences=3,
                gemini_api_key="test_key"
            )

            assert result is not None, "Should still generate content with generic prompt"
            assert len(result['sentences']) == 3, "Should generate sentences even with fallback"

    def test_arabic_specific_prompt_used(self, content_generator):
        """Test that Arabic analyzer provides Arabic-specific prompts"""
        analyzer = get_analyzer('ar')
        assert analyzer is not None, "Arabic analyzer should be available"

        prompt = analyzer.get_sentence_generation_prompt(
            word="ÙƒØªØ§Ø¨",
            language="Arabic",
            num_sentences=3
        )

        # Verify Arabic-specific content
        assert "Arabic" in prompt, "Should specify Arabic language"
        assert "Modern Standard Arabic" in prompt, "Should specify MSA"
        assert "RTL" in prompt, "Should mention RTL text direction"
        assert "sun letters" in prompt, "Should mention Arabic definite article rules"
        assert "root-based morphology" in prompt, "Should mention Arabic morphology"

    def test_prompt_parameter_passing(self, content_generator):
        """Test that all parameters are correctly passed to prompts"""
        analyzer = get_analyzer('ar')

        prompt = analyzer.get_sentence_generation_prompt(
            word="test_word",
            language="Arabic",
            num_sentences=5,
            enriched_meaning="test (a test meaning)",
            max_length=20,
            difficulty="advanced",
            topics=["education", "technology"]
        )

        assert "test_word" in prompt, "Should include target word"
        assert "5" in prompt, "Should include number of sentences"
        assert "20" in prompt, "Should include max length"
        assert "advanced" in prompt, "Should include difficulty"
        assert "education" in prompt and "technology" in prompt, "Should include topics"

    @pytest.mark.parametrize("language,expected_features", [
        ("Arabic", ["RTL", "sun letters", "root-based morphology"]),
        ("Hindi", ["Devanagari", "gender agreement", "case marking"]),
        ("Chinese", ["characters", "tones", "measure words"]),
    ])
    def test_language_specific_prompt_features(self, language, expected_features):
        """Test that each language includes its specific linguistic features"""
        from streamlit_app.shared_utils import LANGUAGE_NAME_TO_CODE

        lang_code = LANGUAGE_NAME_TO_CODE.get(language, language.lower()[:2])
        analyzer = get_analyzer(lang_code)

        if analyzer:  # Skip if analyzer not implemented yet
            prompt = analyzer.get_sentence_generation_prompt(
                word="test",
                language=language,
                num_sentences=3
            )

            for feature in expected_features:
                assert feature in prompt, f"Language {language} prompt should include {feature}"

    def test_content_generation_error_handling(self, content_generator):
        """Test error handling in content generation"""
        # Test with invalid API key
        with pytest.raises(ValueError, match="API key"):
            content_generator.generate_word_meaning_sentences_and_keywords(
                word="test",
                language="Arabic",
                num_sentences=3,
                gemini_api_key="invalid_key"
            )

    def test_ai_response_parsing_robustness(self, content_generator):
        """Test that content generator handles various AI response formats"""
        test_responses = [
            # Standard format
            '''MEANING: test (a test)
RESTRICTIONS: none
SENTENCES:
1. Sentence one.
2. Sentence two.
TRANSLATIONS:
1. Translation one.
2. Translation two.
IPA:
1. /test/
2. /test/
KEYWORDS:
1. test, word, language
2. test, word, language''',

            # Malformed but recoverable
            '''MEANING: test (a test)
SENTENCES:
1. Sentence one.
TRANSLATIONS:
1. Translation one.''',

            # Minimal response
            '''MEANING: test
SENTENCES:
1. Test sentence.'''
        ]

        for response_text in test_responses:
            with patch.object(content_generator, '_get_client') as mock_get_client:
                mock_client = MagicMock()
                mock_get_client.return_value = mock_client

                mock_response = MagicMock()
                mock_response.text = response_text
                mock_client.generate_content.return_value = mock_response

                result = content_generator.generate_word_meaning_sentences_and_keywords(
                    word="test",
                    language="Arabic",
                    num_sentences=1,
                    gemini_api_key="test_key"
                )

                assert result is not None, f"Should handle response format: {response_text[:50]}..."
                assert 'meaning' in result, "Should extract meaning"
```

### 4. Fallback Mechanism Testing

**File:** `tests/test_fallback_mechanisms.py`
```python
import pytest
from unittest.mock import patch, MagicMock
from streamlit_app.services.generation.content_generator import ContentGenerator

class TestFallbackMechanisms:
    """Test content generation fallback mechanisms"""

    @pytest.fixture
    def content_generator(self):
        return ContentGenerator()

    def test_fallback_to_english_samples(self, content_generator):
        """Test fallback to English samples when parsing fails"""
        with patch.object(content_generator, '_get_client') as mock_get_client:
            mock_client = MagicMock()
            mock_get_client.return_value = mock_client

            # Mock a response that will fail parsing
            mock_response = MagicMock()
            mock_response.text = "This is not a valid structured response"
            mock_client.generate_content.return_value = mock_response

            result = content_generator.generate_word_meaning_sentences_and_keywords(
                word="ÙƒØªØ§Ø¨",
                language="Arabic",
                num_sentences=3,
                gemini_api_key="test_key"
            )

            # Should still return a result with fallback sentences
            assert result is not None, "Should provide fallback result"
            assert 'sentences' in result, "Should include sentences"
            assert len(result['sentences']) == 3, "Should generate requested number of sentences"

            # Check that fallback sentences contain the word
            for sentence in result['sentences']:
                assert "ÙƒØªØ§Ø¨" in sentence, "Fallback sentences should contain target word"

    def test_fallback_keywords_generation(self, content_generator):
        """Test fallback keyword generation"""
        with patch.object(content_generator, '_get_client') as mock_get_client:
            mock_client = MagicMock()
            mock_get_client.return_value = mock_client

            mock_response = MagicMock()
            mock_response.text = "Invalid response format"
            mock_client.generate_content.return_value = mock_response

            result = content_generator.generate_word_meaning_sentences_and_keywords(
                word="test_word",
                language="Arabic",
                num_sentences=2,
                gemini_api_key="test_key"
            )

            assert 'keywords' in result, "Should include keywords"
            assert len(result['keywords']) == 2, "Should have keywords for each sentence"

            # Check fallback keyword format
            for keyword_set in result['keywords']:
                assert isinstance(keyword_set, str), "Keywords should be strings"
                assert len(keyword_set.split(',')) == 3, "Should have 3 keywords per sentence"

    def test_partial_parsing_fallback(self, content_generator):
        """Test fallback when only some sections parse successfully"""
        with patch.object(content_generator, '_get_client') as mock_get_client:
            mock_client = MagicMock()
            mock_get_client.return_value = mock_client

            # Response with valid meaning but invalid sentences
            mock_response = MagicMock()
            mock_response.text = '''MEANING: test (a test word)
RESTRICTIONS: No restrictions
SENTENCES:
This is not properly formatted sentence data
'''
            mock_client.generate_content.return_value = mock_response

            result = content_generator.generate_word_meaning_sentences_and_keywords(
                word="test",
                language="Arabic",
                num_sentences=2,
                gemini_api_key="test_key"
            )

            # Should have meaning but fallback sentences
            assert result['meaning'] == 'test (a test word)', "Should parse meaning correctly"
            assert len(result['sentences']) == 2, "Should provide fallback sentences"

    def test_language_specific_fallback_behavior(self, content_generator):
        """Test that fallbacks maintain language-specific expectations"""
        # Test that even in fallback, the system tries to maintain language context
        with patch.object(content_generator, '_get_client') as mock_get_client:
            mock_client = MagicMock()
            mock_get_client.return_value = mock_client

            mock_response = MagicMock()
            mock_response.text = "Completely invalid response"
            mock_client.generate_content.return_value = mock_response

            result = content_generator.generate_word_meaning_sentences_and_keywords(
                word="ÙƒØªØ§Ø¨",
                language="Arabic",
                num_sentences=1,
                gemini_api_key="test_key"
            )

            # The word should still appear in Arabic script in fallback
            sentence = result['sentences'][0]
            assert "ÙƒØªØ§Ø¨" in sentence, "Fallback should preserve Arabic word"

### 5. Content Generation Performance Tests

**File:** `tests/test_content_generation_performance.py`
```python
import pytest
import time
from streamlit_app.services.generation.content_generator import ContentGenerator

class TestContentGenerationPerformance:
    """Test content generation performance"""

    @pytest.fixture
    def content_generator(self):
        return ContentGenerator()

    def test_content_generation_speed(self, content_generator):
        """Test that content generation completes within time limits"""
        with patch.object(content_generator, '_get_client') as mock_get_client:
            mock_client = MagicMock()
            mock_get_client.return_value = mock_client

            mock_response = MagicMock()
            mock_response.text = '''
MEANING: test (a test)
RESTRICTIONS: none
SENTENCES:
1. Test sentence one.
2. Test sentence two.
TRANSLATIONS:
1. Translation one.
2. Translation two.
IPA:
1. /test/
2. /test/
KEYWORDS:
1. test, word, language
2. test, word, language
'''
            mock_client.generate_content.return_value = mock_response

            start_time = time.time()
            result = content_generator.generate_word_meaning_sentences_and_keywords(
                word="test",
                language="Arabic",
                num_sentences=2,
                gemini_api_key="test_key"
            )
            end_time = time.time()

            duration = end_time - start_time
            assert duration < 5.0, f"Content generation took {duration:.2f}s, should be < 5.0s"

    def test_analyzer_prompt_retrieval_speed(self):
        """Test that analyzer prompt retrieval is fast"""
        from streamlit_app.language_analyzers.analyzer_registry import get_analyzer

        analyzers_to_test = ['ar', 'hi', 'zh']  # Test implemented analyzers

        for lang_code in analyzers_to_test:
            analyzer = get_analyzer(lang_code)
            if analyzer:
                start_time = time.time()
                prompt = analyzer.get_sentence_generation_prompt(
                    word="test",
                    language="TestLanguage",
                    num_sentences=3
                )
                end_time = time.time()

                duration = end_time - start_time
                assert duration < 0.1, f"Prompt retrieval for {lang_code} took {duration:.3f}s, should be < 0.1s"
```

### 6. Content Generation Test Fixtures

**File:** `tests/fixtures/content_generation_samples.json`
```json
{
  "arabic": {
    "words": [
      {
        "word": "ÙƒØªØ§Ø¨",
        "meaning": "book (a written work)",
        "expected_sentences": 3,
        "language_features": ["RTL", "Arabic script", "sun letters"]
      },
      {
        "word": "Ù…Ø¯Ø±Ø³Ø©",
        "meaning": "school (place of learning)",
        "expected_sentences": 4,
        "language_features": ["feminine noun", "case marking"]
      }
    ]
  },
  "hindi": {
    "words": [
      {
        "word": "à¤•à¤¿à¤¤à¤¾à¤¬",
        "meaning": "book (written material)",
        "expected_sentences": 3,
        "language_features": ["Devanagari", "gender agreement"]
      }
    ]
  }
}
```

**File:** `tests/fixtures/content_generation_expected.json`
```json
{
  "arabic_ÙƒØªØ§Ø¨": {
    "meaning": "book (a written work)",
    "sentences_should_contain_arabic": true,
    "sentences_should_not_contain": ["This is a sample sentence"],
    "translations_should_be_english": true,
    "ipa_should_be_phonetic": true,
    "keywords_should_be_english": true
  }
}
```

### 7. Integration with Existing Test Framework

Add to `language_grammar_generator/run_all_tests.py`:
```python
def run_content_generation_tests(language_code: str):
    """Run content generation tests for a language"""
    test_files = [
        f"languages/{language_code}/tests/test_content_generation.py",
        f"languages/{language_code}/tests/test_content_integration.py",
        f"languages/{language_code}/tests/test_fallback_mechanisms.py",
        f"languages/{language_code}/tests/test_content_generation_performance.py"
    ]

    # Run tests if files exist
    for test_file in test_files:
        if os.path.exists(test_file):
            run_pytest_file(test_file)
```

## ðŸš€ CI/CD Integration

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

## ðŸ“Š Test Results Analysis

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
        report += "ðŸŽ‰ All files meet coverage requirements!\n"

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

**Remember:** All tests must follow gold standard patterns from [French v2.0](languages/french/fr_analyzer.py) and [Chinese Simplified](languages/chinese_simplified/zh_analyzer.py). Focus on natural validation testing, component isolation, and gold standard comparison - no artificial confidence boosting tests.
- [ ] **Mock Management:** Proper mocking of external dependencies
- [ ] **Flaky Test Detection:** Automated detection of unreliable tests
- [ ] **Test Documentation:** Clear test naming and documentation

## ðŸš¨ Common Testing Pitfalls

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

## ðŸ§ª Word Meanings Dictionary Testing (Sino-Tibetan Languages)

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
        essential_words = ["ä¸€", "äºŒ", "ä¸‰", "å¦‚æžœ", "å› ç‚º", "ç­”æ¡ˆ"]  # Adapt for language
        
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
            ("ä¸‰", "three (numeral)"),  # Numeral
            ("å¦‚æžœ", "if (conjunction)"),  # Conjunction
            ("ç­”æ¡ˆ", "answer, solution (noun)"),  # Compound noun
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
        ("ä¸‰", "numeral"),  # Should identify as numeral
        ("å¦‚æžœ", "conjunction"),  # Should identify as conjunction
        ("ç­”æ¡ˆ", "noun"),  # Should identify as noun
    ])
    def test_word_meanings_grammatical_roles(self, fallbacks, word, expected_contains):
        """Test that word meanings provide correct grammatical role identification"""
        result = fallbacks._analyze_word(word)
        role = result['grammatical_role']
        
        assert expected_contains in role, f"'{word}' role '{role}' should contain '{expected_contains}'"
```

---

**ðŸŽ¯ Ready to start testing?** Begin with unit tests for individual components, then progress to integration and performance testing. Remember: comprehensive testing prevents production issues!

**Need help with testing?** Refer to the [Troubleshooting Guide](troubleshooting_guide.md) for common test issues, or the [Architecture Guide](architecture_guide.md) for component interaction patterns.

**ðŸ“Š Pro tip:** Aim for 80%+ test coverage and <500ms response times for optimal user experience.</content>
<parameter name="filePath">d:\Language Learning\LanguagLearning\language_grammar_generator\testing_guide.md
