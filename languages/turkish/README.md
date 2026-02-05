# Turkish Language Analyzer

## Overview

The Turkish Language Analyzer implements comprehensive morphological analysis for Turkish (Türkçe), a member of the Turkic language family. This analyzer follows the prevention-at-source methodology established in the German and Spanish gold standard implementations.

## Key Linguistic Features

### Agglutination
Turkish is an agglutinative language where words are formed by adding suffixes to root words:
- **ev** (house) + **im** (my) + **de** (at) + **ki** (that is in) = **evimdeki** (that is in my house)

### Vowel Harmony
Suffix vowels harmonize with the last vowel of the root word:
- **Back vowels**: a, ı, o, u
- **Front vowels**: e, i, ö, ü
- Example: "ev" (back) + "de" (back) = "evde"

### Case System
Six grammatical cases clarify syntactic roles:
- Nominative: subject (no marker)
- Accusative: direct object (-i/ı/u/ü)
- Dative: indirect object (-e/a)
- Locative: location (-de/da)
- Ablative: source (-den/dan)
- Genitive: possession (-in/ın/un/ün)

### Word Order
Subject-Object-Verb (SOV) but flexible due to case markers.

## Architecture

Following Clean Architecture principles:

```
turkish/
├── domain/                 # Business logic
│   ├── tr_config.py       # Configuration & linguistic rules
│   ├── tr_prompt_builder.py # Prevention-at-source prompts
│   ├── tr_response_parser.py # AI response parsing
│   └── tr_validator.py    # Analysis validation
├── infrastructure/        # External dependencies
│   └── tr_analyzer_infrastructure.py
├── tests/                 # Unit tests
├── tr_analyzer.py         # Main analyzer class
├── tr_demo.py            # Demonstration script
└── tr_grammar_concepts.md # Linguistic documentation
```

## Usage

### Basic Usage

```python
from languages.turkish import TurkishAnalyzer

analyzer = TurkishAnalyzer()
result = analyzer.analyze("Merhaba dünya!")

if result.success:
    print(analyzer.format_analysis_result(result))
else:
    print(f"Analysis failed: {result.error_message}")
```

### Complexity Levels

```python
# Beginner level (basic categories)
result = analyzer.analyze_beginner("Ben kitap okuyorum.")

# Intermediate level (cases, possession)
result = analyzer.analyze_intermediate("Kitabı Ali'ye verdim.")

# Advanced level (full morphology)
result = analyzer.analyze_advanced("Annemin gönderdiği mektupları okuyordum.")
```

### Analysis Result

```python
{
  "analysis": [
    {
      "word": "evimdeki",
      "morphology": {
        "root": "ev",
        "suffixes": [
          {"form": "im", "meaning": "my", "harmony": "back"},
          {"form": "de", "meaning": "at", "harmony": "back"},
          {"form": "ki", "meaning": "that_is_in", "harmony": "back"}
        ]
      },
      "category": "noun",
      "role": "modifier",
      "color": "#FFAA00",
      "complexity": "intermediate"
    }
  ],
  "sentence_structure": "Possessive construction with locative case",
  "linguistic_features": ["agglutination", "vowel_harmony"],
  "validation": {
    "vowel_harmony_correct": true,
    "morphology_complete": true
  }
}
```

## Configuration

### Color Scheme

```python
color_scheme = analyzer.get_color_scheme('beginner')
# {'noun': '#FFAA00', 'verb': '#4ECDC4', 'adjective': '#FF44FF', ...}
```

### Grammatical Categories

```python
categories = analyzer.get_grammatical_categories('intermediate')
# ['noun', 'verb', 'adjective', 'pronoun', 'adverb', 'postposition',
#  'conjunction', 'interjection', 'numeral', 'case_marker', 'possessive']
```

## Validation

The analyzer includes comprehensive validation:

```python
validation = analyzer.validate_setup()
if validation['overall_valid']:
    print("Analyzer is properly configured")
```

## Testing

Run the test suite:

```bash
python languages/turkish/tests/tr_analyzer_tests.py
```

## Demonstration

Run the demonstration script:

```bash
python languages/turkish/tr_demo.py
```

## Implementation Notes

### Prevention-at-Source Methodology

Following the gold standard from German/Spanish analyzers:

1. **Explicit Rules**: Linguistic rules stated upfront in prompts
2. **Common Error Prevention**: Addresses known AI analysis pitfalls
3. **Validation Integration**: Built-in validation of AI responses
4. **Morphological Focus**: Emphasizes decomposition over surface analysis

### Vowel Harmony Implementation

- Automatic suffix selection based on root vowels
- Validation of harmony in AI responses
- Correction suggestions for harmony violations

### Case System Handling

- Marker identification and function assignment
- Consistency validation between cases and syntactic roles
- Word order flexibility support

## Dependencies

- `google-generativeai`: For AI analysis
- `jinja2`: For prompt templating
- `dataclasses`: For structured data
- `pathlib`: For file operations
- `json`: For configuration and results

## Configuration Files

The analyzer supports external configuration files:

- `tr_grammar_rules.yaml`: Grammar rules and exceptions
- `tr_analysis_patterns.yaml`: Analysis patterns
- `tr_exception_words.yaml`: Special case words
- `tr_test_sentences.yaml`: Test sentences for validation

## Future Enhancements

- Morphological dictionary integration
- Advanced verb conjugation analysis
- Loanword handling improvements
- Performance optimizations
- Additional complexity levels

## References

- Turkish language grammar resources
- Gold standard implementations (German, Spanish, Chinese)
- Linguistic research on agglutination and vowel harmony
- Clean Architecture principles