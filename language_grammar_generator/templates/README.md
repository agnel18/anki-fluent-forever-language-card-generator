# {Language} Grammar Analyzer

## Overview

This is a Clean Architecture implementation of a {Language} grammatical analysis system. The analyzer uses external YAML/JSON configuration files and follows gold standard patterns established in the Arabic analyzer.

## Architecture

### Clean Architecture Components

```
languages/{language}/
├── domain/
│   ├── {lang_code}_config.py          # Configuration management
│   ├── {lang_code}_prompt_builder.py  # AI prompt generation
│   ├── {lang_code}_response_parser.py # Response parsing & validation
│   └── {lang_code}_validator.py       # Analysis validation
├── infrastructure/
│   ├── data/
│   │   ├── grammatical_roles.yaml    # Role definitions by complexity
│   │   ├── word_meanings.json        # Word meanings & concepts
│   │   ├── patterns.yaml            # Regex patterns & validation
│   │   └── language_config.yaml     # Core language settings
│   ├── {lang_code}_ai_service.py     # AI service integration
│   └── {lang_code}_circuit_breaker.py # Circuit breaker pattern
└── {lang_code}_analyzer.py           # Main analyzer facade
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
from languages.{language}.{lang_code}_analyzer import {Language}Analyzer

# Initialize analyzer
analyzer = {Language}Analyzer()

# Analyze a sentence
result = analyzer.analyze_grammar(
    sentence="Example {Language} sentence",
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
2. Implement validation logic in `{lang_code}_validator.py`
3. Update prompt templates in `{lang_code}_prompt_builder.py`

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

### Unit Tests

Run domain component tests:
```bash
python -m pytest tests/test_{lang_code}_config.py
python -m pytest tests/test_{lang_code}_validator.py
```

### Integration Tests

Test full analysis pipeline:
```bash
python -m pytest tests/test_{lang_code}_analyzer_integration.py
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