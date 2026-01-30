# LANGUAGE_NAME_PLACEHOLDER Grammar Analyzer

## Overview

This is a Clean Architecture implementation of a LANGUAGE_NAME_PLACEHOLDER grammatical analysis system. The analyzer uses external YAML/JSON configuration files and follows gold standard patterns established in the Arabic analyzer.

## Critical Requirements

### Sentence Generation Character Limits (UX Requirement)

**MANDATORY:** All sentence generation prompts must enforce strict character limits to prevent overwhelming users with verbose explanations.

**Character Limits:**
- **Word Explanations**: < 75 characters total (e.g., "house (building where people live)" = 32 chars)
- **Grammar Summaries**: < 60 characters total (e.g., "Irregular verb: go/went/gone" = 26 chars)

**Implementation Pattern:**
```python
# In sentence generation prompts
prompt = f"""
MEANING: [brief English meaning]
IMPORTANT: Keep the entire meaning under 75 characters total.

RESTRICTIONS: [grammatical restrictions]
IMPORTANT: Keep the entire restrictions summary under 60 characters total.
"""
```

**Why Required:**
- **UX Overload Prevention**: Long explanations reduce user engagement and completion rates
- **Mobile-Friendly**: Shorter explanations work better on mobile devices
- **Cognitive Load**: Users can process concise information more effectively
- **Consistent Experience**: Same limits across all languages prevent jarring differences

## Architecture

### Clean Architecture Components

```
languages/LANGUAGE_PLACEHOLDER/
├── domain/
│   ├── LANG_CODE_PLACEHOLDER_config.py          # Configuration management
│   ├── LANG_CODE_PLACEHOLDER_prompt_builder.py  # AI prompt generation
│   ├── LANG_CODE_PLACEHOLDER_response_parser.py # Response parsing & validation
│   └── LANG_CODE_PLACEHOLDER_validator.py       # Analysis validation
├── infrastructure/
│   ├── data/
│   │   ├── grammatical_roles.yaml    # Role definitions by complexity
│   │   ├── word_meanings.json        # Word meanings & concepts
│   │   ├── patterns.yaml            # Regex patterns & validation
│   │   └── language_config.yaml     # Core language settings
│   ├── LANG_CODE_PLACEHOLDER_ai_service.py     # AI service integration
│   └── LANG_CODE_PLACEHOLDER_circuit_breaker.py # Circuit breaker pattern
└── LANG_CODE_PLACEHOLDER_analyzer.py           # Main analyzer facade
```

## Configuration Files

### 1. grammatical_roles.yaml
Defines grammatical roles organized by complexity level:
- **beginner**: Basic parts of speech (noun, verb, adjective, etc.)
- **intermediate**: Additional categories (preposition, conjunction, etc.)
- **advanced**: Complete grammatical framework

### 2. word_meanings.json
Contains word meanings, grammatical concepts, and language-specific features:
- Common words and their translations
- Grammatical concepts and patterns
- Language-specific features and examples

### 3. patterns.yaml
Regex patterns for text validation and linguistic analysis:
- Text validation patterns
- Word-level patterns (nouns, verbs, etc.)
- Script and Unicode range validation
- Diacritical mark patterns

### 4. language_config.yaml
Core language settings and analysis parameters:
- Language metadata (code, name, script)
- Analysis complexity settings
- UI theming and colors
- API and performance configuration

## Usage

### Basic Analysis

```python
from languages.LANGUAGE_PLACEHOLDER.LANG_CODE_PLACEHOLDER_analyzer import LANGUAGE_NAME_PLACEHOLDERAnalyzer

# Initialize analyzer
analyzer = LANGUAGE_NAME_PLACEHOLDERAnalyzer()

# Analyze a sentence
result = analyzer.analyze_grammar(
    sentence="Example LANGUAGE_NAME_PLACEHOLDER sentence",
    target_word="target",
    complexity="intermediate",
    api_key="your_gemini_api_key"
)

print(result['word_explanations'])
print(result['confidence_score'])
```

### Batch Analysis

```python
sentences = ["Sentence 1", "Sentence 2", "Sentence 3"]
results = analyzer.analyze_batch(sentences, complexity="advanced")
```

### Language Information

```python
info = analyzer.get_language_info()
print(f"Supported complexities: {info['supported_complexities']}")
```

## Configuration Customization

### Adding New Grammatical Roles

1. Edit `grammatical_roles.yaml`:
```yaml
advanced:
  new_role:
    description: "Description of new role"
    examples: ["example1", "example2"]
    color: "#NEW_COLOR"
```

2. Update color scheme in `language_config.yaml`

### Modifying Patterns

1. Edit `patterns.yaml` with new regex patterns
2. Test patterns with sample text
3. Update validation rules as needed

### Language-Specific Rules

1. Add rules to `language_config.yaml` under `language_specific_rules`
2. Implement validation logic in `LANG_CODE_PLACEHOLDER_validator.py`
3. Update prompt templates in `LANG_CODE_PLACEHOLDER_prompt_builder.py`

## API Integration

### Gemini AI Setup

1. Get API key from Google AI Studio
2. Configure in analyzer or pass directly
3. Monitor usage and costs

### Circuit Breaker

The system includes automatic circuit breaker protection:
- Opens after 5 consecutive failures
- Attempts recovery after 60 seconds
- Requires 3 successes to fully close

## Performance Monitoring

### Metrics Tracked

- Analysis latency
- AI service response times
- Cache hit rates
- Error rates by complexity
- Circuit breaker state changes

### Cache Configuration

- Response caching for repeated prompts
- Configurable cache size and TTL
- Automatic cache invalidation

## Error Handling

### Common Issues

1. **Configuration File Missing**: Ensure all YAML/JSON files exist
2. **Invalid API Key**: Check Gemini API key validity
3. **Circuit Breaker Open**: Wait for automatic recovery or reset manually
4. **Unsupported Complexity**: Use only supported complexity levels

### Debugging

Enable verbose logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Testing

### Comprehensive Testing Framework

The LANGUAGE_NAME_PLACEHOLDER analyzer uses a comprehensive testing framework that includes:

#### 1. Unit Tests
Run domain component tests:
```bash
python -m pytest tests/test_LANG_CODE_PLACEHOLDER_config.py
python -m pytest tests/test_LANG_CODE_PLACEHOLDER_validator.py
```

#### 2. Integration Tests
Test full analysis pipeline:
```bash
python -m pytest tests/test_LANG_CODE_PLACEHOLDER_analyzer_integration.py
```

#### 3. Gold Standard Quality Tests
Test explanation quality with real API calls:
```bash
# Test gold standard explanation quality
python streamlit_app/test_LANGUAGE_PLACEHOLDER_analysis.py

# Run as pytest
python -m pytest streamlit_app/test_LANGUAGE_PLACEHOLDER_analysis.py::test_LANGUAGE_PLACEHOLDER_analyzer_quality -v
```
**Validates:**
- ✅ Semantic meaning accuracy
- ✅ Syntactic function explanation
- ✅ Detailed grammatical analysis
- ✅ Language-specific features
- ✅ Quality metrics (length, keywords)

#### 4. Batch Processing Tests
Test efficient multi-sentence analysis:
```bash
# Test batch processing with real API calls
python test_LANGUAGE_PLACEHOLDER_batch.py

# Run as pytest
python -m pytest tests/test_LANGUAGE_PLACEHOLDER_analyzer.py::TestLANGUAGE_NAME_PLACEHOLDERAnalyzer::test_batch_grammar_analysis -v
```
**Validates:**
- ✅ Batch processing efficiency (8 sentences per API call)
- ✅ Specific grammatical explanations (not generic fallbacks)
- ✅ Consistent results across all sentences
- ✅ Error handling and fallbacks
- ✅ Performance optimization

#### 5. Sentence Generation Tests
Test AI-powered sentence generation:
```bash
# Test sentence generation with database words
python test_LANGUAGE_PLACEHOLDER_sentences.py

# Run as pytest
python -m pytest tests/test_sentence_generator.py -k LANGUAGE_PLACEHOLDER -v
```
**Validates:**
- ✅ AI generation success (no fallback to samples)
- ✅ Sentence grammatical correctness
- ✅ Target word integration
- ✅ Cultural appropriateness
- ✅ Sentence diversity

#### 5. Automated Testing Pipeline
Run all tests with coverage:
```bash
# Validate implementation before deployment
python language_grammar_generator/validate_implementation.py --language LANG_CODE_PLACEHOLDER

# Run comprehensive test suite
python language_grammar_generator/run_all_tests.py --language LANG_CODE_PLACEHOLDER --coverage

# Compare with gold standards
python language_grammar_generator/compare_with_gold_standard.py --language LANG_CODE_PLACEHOLDER
```

### Test File Structure
```
tests/
├── test_LANG_CODE_PLACEHOLDER_analyzer.py       # Main facade tests
├── test_LANG_CODE_PLACEHOLDER_config.py         # Configuration validation
├── test_LANG_CODE_PLACEHOLDER_prompt_builder.py # AI prompt generation
├── test_LANG_CODE_PLACEHOLDER_response_parser.py # Response processing
├── test_LANG_CODE_PLACEHOLDER_validator.py      # Quality validation
├── test_integration.py               # Component interaction
└── test_system.py                    # End-to-end workflows

streamlit_app/
└── test_LANGUAGE_PLACEHOLDER_analysis.py       # Gold standard quality tests

test_LANGUAGE_PLACEHOLDER_sentences.py          # Sentence generation tests
```

## Development Guidelines

### Code Style

- Follow PEP 8 conventions
- Use type hints for all functions
- Include comprehensive docstrings
- Write tests for new features

### Configuration Management

- Keep configuration files version controlled
- Document all configuration options
- Validate configuration on startup
- Use environment variables for secrets

### Performance Considerations

- Cache frequently used prompts
- Batch similar analyses
- Monitor memory usage
- Optimize regex patterns

## Contributing

1. Follow the established Clean Architecture patterns
2. Update configuration files for new features
3. Add comprehensive tests
4. Update documentation
5. Ensure backward compatibility

## License

This project is licensed under the MIT License - see the LICENSE file for details.