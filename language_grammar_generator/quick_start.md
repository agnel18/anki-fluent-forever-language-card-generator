# Quick Start Guide
## Language Grammar Analyzer Implementation (Beginner Level)

**For:** Simple languages with basic grammatical structures  
**Primary Gold Standard:** Study [Chinese Simplified](languages/chinese_simplified/zh_analyzer.py) - Clean Architecture pattern  
**Secondary Reference:** [Hindi](languages/hindi/hi_analyzer.py)  
**Time Estimate:** 2-3 days for complete implementation  
**Critical:** Follow Chinese Simplified Clean Architecture - external configuration, integrated fallbacks, no artificial confidence boosting

## ðŸŽ¯ When to Use This Guide

Choose this guide if your target language has:
- âœ… Simple word order (SVO, SOV, V2)
- âœ… Basic inflection (regular verbs, simple cases)
- âœ… Limited morphological complexity
- âœ… Standard grammatical categories (noun, verb, adjective, etc.)

**Not suitable for:**
- âŒ Complex morphology (Arabic, Sanskrit, German)
- âŒ Free word order (Russian, Latin)
- âŒ Tonal languages with complex particles (Chinese, Thai) - Use Sino-Tibetan guide instead
- âŒ Agglutinative languages (Turkish, Japanese, Korean)

## ðŸš€ Step-by-Step Implementation

### Step 1: Research Phase (4 hours)

#### 1.1 Create Grammar Concepts Document
Create `{language}_grammar_concepts.md` in your language directory:

```markdown
# {Language} Grammar Concepts

## Basic Word Order
- Subject-Verb-Object (SVO) or Subject-Object-Verb (SOV)

## Grammatical Categories
- Nouns: [examples]
- Verbs: [examples]
- Adjectives: [examples]
- Basic particles/prepositions: [examples]

## Key Features
- [List 3-5 most important grammatical features]

## Simple Examples
1. "The cat eats fish" â†’ [breakdown]
2. "I see the big house" â†’ [breakdown]
```

#### 1.2 Study Chinese Simplified Gold Standard
**CRITICAL:** Before implementing, study the Chinese Simplified analyzer structure:

```python
# Chinese Simplified Clean Architecture Pattern
class ZhAnalyzer(BaseGrammarAnalyzer):
    def __init__(self):
        # 1. Initialize domain components
        self.zh_config = ZhConfig()           # Loads external YAML/JSON
        self.prompt_builder = ZhPromptBuilder(self.zh_config)
        self.response_parser = ZhResponseParser(self.zh_config)
        self.validator = ZhValidator(self.zh_config)
        self.fallbacks = ZhFallbacks(self.zh_config)  # Integrated in domain
        
        # 2. Create language config
        config = LanguageConfig(...)
        super().__init__(config)
```

#### 1.3 Identify Core Grammatical Roles (Follow Chinese Simplified Pattern)
Map your language to standard categories:
```python
GRAMMATICAL_ROLES = {
    'noun': 'noun',
    'verb': 'verb',
    'adjective': 'adjective',
    'adverb': 'adverb',
    'pronoun': 'pronoun',
    'preposition': 'preposition',  # or 'postposition'
    'conjunction': 'conjunction',
    'determiner': 'determiner'
}
```

### Step 2: Setup Directory Structure (30 minutes)

Create the standard analyzer structure:
```
languages/{language}/
â”œâ”€â”€ {language}_analyzer.py          # Main analyzer (facade)
â”œâ”€â”€ {language}_grammar_concepts.md  # Research document
â”œâ”€â”€ domain/
â”‚   â”œâ”€â”€ {language}_config.py        # Configuration
â”‚   â”œâ”€â”€ {language}_prompt_builder.py # AI prompt generation
â”‚   â”œâ”€â”€ {language}_response_parser.py # AI response parsing
â”‚   â””â”€â”€ {language}_validator.py     # Quality validation
â”œâ”€â”€ infrastructure/
â”‚   â””â”€â”€ {language}_fallbacks.py     # Fallback mechanisms
â””â”€â”€ tests/
    â”œâ”€â”€ __init__.py
    â”œâ”€â”€ conftest.py                 # Pytest configuration
    â”œâ”€â”€ test_{language}_analyzer.py # Main facade tests
    â”œâ”€â”€ test_{language}_config.py   # Configuration tests
    â”œâ”€â”€ test_{language}_prompt_builder.py
    â”œâ”€â”€ test_{language}_response_parser.py
    â”œâ”€â”€ test_{language}_validator.py
    â”œâ”€â”€ test_integration.py         # Integration tests
    â”œâ”€â”€ test_system.py              # System tests (auto-generated)
    â”œâ”€â”€ test_performance.py         # Performance tests (auto-generated)
    â”œâ”€â”€ test_gold_standard_comparison.py # Gold standard tests (auto-generated)
    â””â”€â”€ test_regression.py          # Regression tests (auto-generated)
```

### Step 2.5: Pre-Implementation Validation

**CRITICAL:** Before implementing any code, validate your setup:

```bash
# Validate that all required files are created
python language_grammar_generator/validate_implementation.py --language {language_code}

# This will catch missing files and structural issues early
```

### Step 3: Implement Configuration (1 hour)

Copy and modify the config template:

```python
# languages/{language}/domain/{language}_config.py
from ..zh_config import ZhConfig  # Use as reference

class {Language}Config(ZhConfig):
    """Configuration for {Language} analyzer"""

    def __init__(self):
        super().__init__()
        # Override with language-specific settings
        self.language_code = '{code}'
        self.language_name = '{Language}'

        # Simple color scheme for basic categories
        self.grammatical_colors = {
            'noun': '#FFAA00',
            'verb': '#4ECDC4',
            'adjective': '#FF44FF',
            'adverb': '#9370DB',
            'pronoun': '#FFEAA7',
            'preposition': '#4444FF',
            'conjunction': '#AAAAAA',
            'determiner': '#FFD700'
        }
```

### Step 4: Implement Prompt Builder (2 hours)

Create simple prompts for basic analysis:

```python
# languages/{language}/domain/{language}_prompt_builder.py
from .zh_prompt_builder import ZhPromptBuilder

class {Language}PromptBuilder(ZhPromptBuilder):
    """Builds prompts for {Language} grammar analysis"""

    def build_single_prompt(self, sentence: str, target_word: str, complexity: str) -> str:
        """Simple prompt for basic grammatical analysis"""
        return f"""Analyze this {self.config.language_name} sentence: {sentence}

Target word: {target_word}

Identify the grammatical role of each word:
- noun, verb, adjective, adverb, pronoun, preposition, conjunction, determiner

Return JSON:
{{
  "words": [
    {{"word": "word1", "grammatical_role": "noun", "meaning": "brief explanation"}},
    {{"word": "word2", "grammatical_role": "verb", "meaning": "brief explanation"}}
  ],
  "explanations": {{
    "overall_structure": "Basic sentence structure",
    "key_features": "Main grammatical features used"
  }}
}}

Be accurate and provide clear explanations."""
```

### Step 5: Implement Response Parser (1 hour)

Handle AI responses with **robust JSON parsing** - AI models often wrap JSON in explanatory text:

```python
# languages/{language}/domain/{language}_response_parser.py
import json
import re
from .zh_response_parser import ZhResponseParser

class {Language}ResponseParser(ZhResponseParser):
    """Parses AI responses for {Language} analysis with robust JSON extraction"""

    def parse_response(self, ai_response: str, complexity: str, sentence: str, target_word: str) -> dict:
        """Parse and validate AI response with robust JSON extraction"""
        try:
            # Robust JSON extraction - handles markdown blocks, explanatory text, etc.
            json_data = self._extract_json(ai_response)
            if not json_data:
                return self.fallbacks.create_fallback(sentence, complexity)

            # Basic validation
            if 'words' not in json_data and 'batch_results' not in json_data:
                return self.fallbacks.create_fallback(sentence, complexity)

            return json_data

        except Exception as e:
            # Use fallback for parsing errors
            return self.fallbacks.create_fallback(sentence, complexity)

    def _extract_json(self, ai_response: str) -> dict:
        """Extract JSON from AI response with multiple fallback methods"""
        try:
            cleaned_response = ai_response.strip()

            # Method 1: Direct parsing if starts with JSON
            if cleaned_response.startswith(('{', '[')):
                return json.loads(cleaned_response)

            # Method 2: Extract from markdown code blocks
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', cleaned_response, re.DOTALL | re.IGNORECASE)
            if json_match:
                return json.loads(json_match.group(1))

            # Method 3: Extract JSON between curly braces
            brace_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
            if brace_match:
                return json.loads(brace_match.group(0))

            # Method 4: Try entire response
            return json.loads(cleaned_response)

        except json.JSONDecodeError:
            return None
```

### Step 6: Implement Validator (1 hour)

Basic quality checks:

```python
# languages/{language}/domain/{language}_validator.py
from .zh_validator import ZhValidator

class {Language}Validator(ZhValidator):
    """Validates {Language} analysis results"""

    def validate_result(self, result: dict, sentence: str) -> dict:
        """Basic validation with confidence scoring"""
        confidence = 0.8  # Start with high confidence for simple languages

        word_explanations = result.get('word_explanations', [])

        # Check for minimum requirements
        if len(word_explanations) == 0:
            confidence = 0.1

        # Check for explanations
        if 'explanations' not in result:
            confidence *= 0.7

        result['confidence'] = confidence
        return result
```

### Step 7: Create Main Analyzer (1 hour)

Implement the facade pattern:

```python
# languages/{language}/{language}_analyzer.py
from streamlit_app.language_analyzers.base_analyzer import BaseGrammarAnalyzer, LanguageConfig
from .domain.{language}_config import {Language}Config
from .domain.{language}_prompt_builder import {Language}PromptBuilder
from .domain.{language}_response_parser import {Language}ResponseParser
from .domain.{language}_validator import {Language}Validator

class {Language}Analyzer(BaseGrammarAnalyzer):
    """Grammar analyzer for {Language}"""

    VERSION = "1.0"
    LANGUAGE_CODE = "{code}"
    LANGUAGE_NAME = "{Language}"

    def __init__(self):
        """Initialize with domain components"""
        self.config = {Language}Config()
        self.prompt_builder = {Language}PromptBuilder(self.config)
        self.response_parser = {Language}ResponseParser(self.config)
        self.validator = {Language}Validator(self.config)

        language_config = LanguageConfig(
            code="{code}",
            name="{Language}",
            native_name="{Native Name}",
            family="{Language Family}",
            script_type="alphabetic",  # or "logographic", "abugida", etc.
            complexity_rating="low",   # low, medium, high
            key_features=['basic_word_order', 'simple_inflection'],
            supported_complexity_levels=['beginner', 'intermediate']
        )

        super().__init__(language_config)

    def analyze_grammar(self, sentence: str, target_word: str, complexity: str, gemini_api_key: str):
        """Main analysis method - delegate to components"""
        # Implementation following the pattern from Hindi/Chinese analyzers
        pass

    # Implement required abstract methods
    def get_grammar_prompt(self, complexity: str, sentence: str, target_word: str) -> str:
        return self.prompt_builder.build_single_prompt(sentence, target_word, complexity)

    def parse_grammar_response(self, ai_response: str, complexity: str, sentence: str) -> dict:
        return self.response_parser.parse_response(ai_response, complexity, sentence, None)

    def validate_analysis(self, parsed_data: dict, original_sentence: str) -> float:
        result = self.validator.validate_result(parsed_data, original_sentence)
        return result.get('confidence', 0.5)
```

### Step 8: Create Basic Tests (1 hour)

Implement essential test coverage:

```python
# languages/{language}/tests/test_{language}_analyzer.py
import pytest
from ..{language}_analyzer import {Language}Analyzer

class Test{Language}Analyzer:
    """Basic tests for {Language} analyzer"""

    @pytest.fixture
    def analyzer(self):
        return {Language}Analyzer()

    def test_initialization(self, analyzer):
        """Test analyzer initializes correctly"""
        assert analyzer.language_code == "{code}"
        assert analyzer.language_name == "{Language}"

    def test_simple_sentence_analysis(self, analyzer):
        """Test analysis of a simple sentence"""
        # This will need a valid API key for full testing
        # For now, test the prompt generation
        prompt = analyzer.get_grammar_prompt("beginner", "Test sentence", "test")
        assert isinstance(prompt, str)
        assert len(prompt) > 0

    def test_color_scheme(self, analyzer):
        """Test color scheme generation"""
        colors = analyzer.get_color_scheme("beginner")
        assert isinstance(colors, dict)
        assert 'noun' in colors
```

### Step 9: Integration Testing (2 hours)

Test end-to-end functionality:

```python
# languages/{language}/tests/test_{language}_integration.py
import pytest
from ..{language}_analyzer import {Language}Analyzer

class Test{Language}Integration:
    """Integration tests for {Language} analyzer"""

    @pytest.fixture
    def analyzer(self):
        return {Language}Analyzer()

    def test_full_analysis_workflow(self, analyzer):
        """Test complete analysis workflow"""
        # Requires valid API key
        # Test with mock responses for CI/CD
        pass

    def test_error_handling(self, analyzer):
        """Test error handling and fallbacks"""
        # Test with invalid inputs
        # Test API failures
        pass
```

## âœ… Success Criteria

### Code Quality
- [ ] All domain components implemented
- [ ] Clean separation of concerns
- [ ] Proper error handling and fallbacks
- [ ] Comprehensive docstrings

### Functionality
- [ ] Single sentence analysis works
- [ ] Batch processing supported
- [ ] HTML output generation
- [ ] Color-coded grammatical roles

### Testing
- [ ] Unit tests pass (>80% coverage)
- [ ] Integration tests pass
- [ ] Error scenarios handled
- [ ] Performance within limits

### Quality
- [ ] Linguistic accuracy validated
- [ ] Confidence scoring works
- [ ] Fallback mechanisms functional
- [ ] Documentation complete

## ðŸš¨ Common Pitfalls

### 1. Over-Engineering
**Problem:** Trying to handle complex grammar in simple implementation
**Solution:** Keep it simple, focus on core grammatical roles

### 2. Poor AI Prompts
**Problem:** Vague or incomplete prompts leading to poor analysis
**Solution:** Use clear, specific instructions with examples

### 3. Missing Validation
**Problem:** No quality checks on AI responses
**Solution:** Always implement confidence scoring and fallbacks

### 4. Inadequate Testing
**Problem:** Insufficient test coverage leading to iterative failures
**Solution:** Use comprehensive automated testing framework

## ðŸ§ª Comprehensive Testing Workflow

### Step 1: Continuous Validation During Implementation

**After Each Component:**
```bash
# Test component creation
python -c "from languages.{language_code}.domain.{language_code}_config import {LanguageCode}Config; c = {LanguageCode}Config(); print('âœ“ Config works')"

# Test analyzer instantiation
python -c "from languages.{language_code}.{language_code}_analyzer import {LanguageCode}Analyzer; a = {LanguageCode}Analyzer(); print('âœ“ Analyzer works')"
```

### Step 2: Pre-Deployment Validation
```bash
# Validate complete implementation
python language_grammar_generator/validate_implementation.py --language {language_code}

# Run comprehensive test suite
python language_grammar_generator/run_all_tests.py --language {language_code} --coverage

# Compare with gold standards
python language_grammar_generator/compare_with_gold_standard.py --language {language_code} --detailed
```

### Step 3: Gold Standard Quality Testing
```bash
# Test explanation quality with real API calls
python streamlit_app/test_<language>_analysis.py

# Validate semantic + syntactic explanations
python -m pytest streamlit_app/test_<language>_analysis.py::test_<language>_analyzer_quality -v
```

### Step 4: Sentence Generation Testing
```bash
# Test AI-powered sentence generation
python test_<language>_sentences.py

# Validate no fallback to sample sentences
python -m pytest tests/test_sentence_generator.py -k <language> -v
```

### Step 3: Troubleshooting Failed Tests

**âŒ Method Missing Errors:**
```bash
# Check implemented methods
python -c "import inspect; from languages.{language_code}.{language_code}_analyzer import {LanguageCode}Analyzer; print([m for m in dir({LanguageCode}Analyzer) if not m.startswith('_')])"
```

**âŒ Configuration Loading Errors:**
```bash
# Test config loading
python -c "from languages.{language_code}.domain.{language_code}_config import {LanguageCode}Config; c = {LanguageCode}Config(); print('Roles:', len(c.grammatical_roles))"
```

**âŒ Component Integration Errors:**
```bash
# Test component integration
python -c "
from languages.{language_code}.{language_code}_analyzer import {LanguageCode}Analyzer
try:
    a = {LanguageCode}Analyzer()
    print('âœ“ All components integrated')
except Exception as e:
    print(f'âœ— Error: {e}')
"
```

**âŒ Gold Standard Comparison Failures:**
```bash
# Get detailed comparison
python language_grammar_generator/compare_with_gold_standard.py --language {language_code} --detailed --export-results
```

### Step 4: Final Deployment Checklist
- [ ] Pre-implementation validation passes
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] All system tests pass
- [ ] Gold standard quality tests pass (semantic + syntactic explanations)
- [ ] Sentence generation tests pass (no fallback to samples)
- [ ] Performance requirements met
- [ ] Gold standard comparison passes
- [ ] Regression tests pass
- [ ] Documentation updated

**ðŸš¨ DO NOT DEPLOY UNTIL ALL CHECKS PASS!**

## ðŸŽ¯ Next Steps

### Level 2 (Intermediate)
Once basic implementation works, enhance with:
- More grammatical categories
- Intermediate complexity prompts
- Enhanced validation
- Better error handling

### Level 3 (Advanced)
For production readiness:
- Performance optimization
- Advanced AI prompting
- Comprehensive monitoring
- Enterprise deployment

## ðŸ“ž Need Help?

- **Reference Implementation:** Check `hi_analyzer.py` for gold standard
- **Similar Languages:** Look at analyzers in same language family
- **Testing Issues:** Run existing test suites for patterns
- **AI Problems:** Review prompt engineering in `ai_prompting_guide.md`

---

**ðŸŽ‰ Congratulations!** You've implemented a basic language analyzer. Test thoroughly and consider moving to [Level 2 Implementation](implementation_guide.md) for enhanced features!</content>
<parameter name="filePath">d:\Language Learning\LanguagLearning\language_grammar_generator\quick_start.md
