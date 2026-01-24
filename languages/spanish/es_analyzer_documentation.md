# Spanish Grammar Analyzer Documentation

## Overview

The Spanish Grammar Analyzer (`es_analyzer.py`) is a comprehensive linguistic analysis tool designed to parse and explain Spanish grammatical structures. It follows the gold standard established by the Hindi analyzer while adapting to Spanish's Romance language characteristics.

## Language Specifications

- **Language Code**: `es`
- **Language Name**: Spanish (español)
- **Language Family**: Indo-European > Romance
- **Script Type**: Latin alphabet with diacritics
- **Complexity Rating**: Medium
- **Word Order**: SVO (Subject-Verb-Object)
- **Key Features**: Verb conjugation, gender agreement, clitic pronouns, ser/estar distinction

## Grammatical Role Categories

### Beginner Level
- `noun`: Sustantivos (things/objects/people/places)
- `adjective`: Adjetivos (descriptions)
- `verb`: Verbos (actions/states)
- `adverb`: Adverbios (modifications)
- `pronoun`: Pronombres (replacements)
- `article`: Artículos (definite/indefinite markers)
- `preposition`: Preposiciones (relationships)
- `conjunction`: Conjunciones (connectors)
- `interjection`: Interjecciones (exclamations)
- `auxiliary`: Verbos auxiliares (helpers)
- `other`: Otros

### Intermediate Level
- All beginner roles plus:
- `personal_pronoun`: Pronombres personales (yo, tú, él/ella, etc.)
- `demonstrative_pronoun`: Pronombres demostrativos (este, ese, aquel)
- `possessive_pronoun`: Pronombres posesivos (mío, tuyo, suyo)
- `reflexive_pronoun`: Pronombres reflexivos (me, te, se)
- `numeral`: Numerales (números)
- `relative_pronoun`: Pronombres relativos (que, quien, cual)
- `interrogative_pronoun`: Pronombres interrogativos (qué, quién, cuál)

### Advanced Level
- All intermediate roles plus:
- `indefinite_pronoun`: Pronombres indefinidos (alguno, ninguno)
- `clitic`: Clíticos (pronombres átonos)
- `gerund`: Gerundio (-ando/-iendo forms)
- `past_participle`: Participio pasado (-ado/-ido forms)
- `infinitive`: Infinitivo (base verb forms)

## Color Coding Scheme

### Beginner Level Colors
- **Nouns** (#FFAA00): Orange - sustantivos
- **Verbs** (#44FF44): Green - verbos
- **Articles** (#FFD700): Gold - artículos
- **Prepositions** (#4444FF): Blue - preposiciones
- **Pronouns** (#FF4444): Red - pronombres
- **Adjectives** (#FF44FF): Magenta - adjetivos
- **Adverbs** (#44FFFF): Cyan - adverbios
- **Conjunctions** (#888888): Gray - conjunciones
- **Interjections** (#FFD700): Gold - interjecciones
- **Auxiliaries** (#44FF44): Green - auxiliares
- **Reflexives** (#FF6347): Tomato - reflexivos

### Intermediate Level Colors
- Inherits beginner colors plus:
- **Numerals** (#FFFF44): Yellow - numerales
- **Personal Pronouns** (#FF4444): Red - personales
- **Demonstrative Pronouns** (#FF4444): Red - demostrativos
- **Possessive Pronouns** (#FF4444): Red - posesivos

### Advanced Level Colors
- Inherits intermediate colors plus:
- **Clitics** (#FF6347): Tomato - clíticos
- **Gerunds** (#44FF44): Green - gerundios
- **Past Participles** (#44FF44): Green - participios
- **Infinitives** (#44FF44): Green - infinitivos

## Key Linguistic Features

### 1. Verb Conjugation System
Spanish features extensive verb conjugation across:
- **3 infinitive types**: -ar, -er, -ir
- **6 persons**: 1st, 2nd, 3rd singular/plural
- **Multiple tenses**: Present, preterite, imperfect, future, conditional
- **3 moods**: Indicative, subjunctive, imperative
- **Compound tenses**: Perfect forms with haber
- **Progressive forms**: Estar + gerund

### 2. Gender Agreement
- **Two genders**: Masculine, feminine
- **Agreement domains**: Articles, adjectives, pronouns, past participles
- **Number agreement**: Singular/plural
- **Special patterns**: -o/-a endings, exceptions (mano, día)

### 3. Clitic Pronouns
- **Direct objects**: lo, la, los, las
- **Indirect objects**: le, les
- **Reflexives**: me, te, se, nos, os
- **Placement rules**: Pre-verbal, enclitic with infinitives/gerunds
- **Sequences**: Complex ordering in multiple clitic constructions

### 4. Ser vs Estar Distinction
- **Ser**: Permanent characteristics, origin, possession, time/date
- **Estar**: Temporary states, location, progressive actions, conditions
- **Past participles**: Ser (passive/result), estar (ongoing state)

### 5. Prepositional System
- **Simple prepositions**: a, de, en, por, para, con, sin
- **Complex prepositions**: contractions (al = a+el, del = de+el)
- **Por vs Para**: Complex aspectual distinctions

## Implementation Details

### Pattern Recognition
The analyzer uses regex patterns for:
- **Verb endings**: Conjugation identification across tenses
- **Gender markers**: Masculine (-o, -os) vs feminine (-a, -as) patterns
- **Clitic detection**: Pronoun identification and placement
- **Ser/estar forms**: Copula verb recognition
- **Articles**: Definite/indefinite detection
- **Prepositions**: Relationship marker identification

### Validation Logic
- **Confidence threshold**: 85% minimum for acceptance
- **Spanish-specific checks**:
  - Gender agreement between adjectives and nouns
  - Verb conjugation pattern validation
  - Ser vs estar appropriate usage
  - Clitic pronoun placement
  - Latin alphabet with Spanish characters (á, é, í, ó, ú, ñ, ü, ¿, ¡)

### Word Ordering
- **LTR processing**: Left-to-right explanation ordering
- **Sentence position**: Explanations match word appearance order
- **Script direction**: Maintains reading direction for optimal learning

## Usage Examples

### Basic Analysis
```python
from streamlit_app.language_analyzers.analyzers.es_analyzer import EsAnalyzer

analyzer = EsAnalyzer()
sentence = "El gato negro duerme en la casa"
target_word = "duerme"

# Get analysis prompt
prompt = analyzer.get_grammar_prompt("intermediate", sentence, target_word)

# Parse AI response (simulated)
response = {
    "words": [
        {"word": "El", "individual_meaning": "The", "grammatical_role": "article"},
        {"word": "gato", "individual_meaning": "cat", "grammatical_role": "noun"},
        {"word": "negro", "individual_meaning": "black", "grammatical_role": "adjective"},
        {"word": "duerme", "individual_meaning": "sleeps", "grammatical_role": "verb"},
        {"word": "en", "individual_meaning": "in", "grammatical_role": "preposition"},
        {"word": "la", "individual_meaning": "the", "grammatical_role": "article"},
        {"word": "casa", "individual_meaning": "house", "grammatical_role": "noun"}
    ]
}

result = analyzer.parse_grammar_response(json.dumps(response), "intermediate", sentence)
```

### Batch Processing
```python
sentences = [
    "El perro ladra fuerte",
    "La casa es muy grande",
    "Me gusta el café caliente"
]

batch_prompt = analyzer.get_batch_grammar_prompt("intermediate", sentences, "ladra")
# Returns formatted prompt for AI batch analysis
```

## Testing

### Test Coverage
- **Initialization**: Proper setup and pattern loading
- **Role mapping**: Correct grammatical category assignment
- **Color schemes**: Appropriate color coding by complexity level
- **Validation**: Confidence scoring and Spanish-specific checks
- **Parsing**: JSON response handling and error recovery
- **Word ordering**: Sentence position-based explanation sorting

### Running Tests
```bash
cd /path/to/project
python -m pytest tests/test_es_analyzer.py -v
```

### Test Categories
- **Unit tests**: Individual method functionality
- **Integration tests**: End-to-end analysis workflows
- **Validation tests**: Confidence scoring accuracy
- **Pattern tests**: Linguistic pattern recognition
- **Error handling**: Robust failure recovery

## API Reference

### Class: EsAnalyzer

#### Methods

##### `__init__()`
Initialize Spanish analyzer with language configuration and patterns.

##### `get_grammar_prompt(complexity, sentence, target_word, native_language="English")`
Generate AI prompt for single sentence analysis.

**Parameters:**
- `complexity` (str): "beginner", "intermediate", or "advanced"
- `sentence` (str): Spanish sentence to analyze
- `target_word` (str): Word to emphasize in analysis
- `native_language` (str): Language for explanations

**Returns:** Formatted prompt string

##### `get_batch_grammar_prompt(complexity, sentences, target_word, native_language="English")`
Generate AI prompt for batch sentence analysis.

**Parameters:**
- `complexity` (str): Analysis complexity level
- `sentences` (List[str]): List of Spanish sentences
- `target_word` (str): Target word for emphasis
- `native_language` (str): Explanation language

**Returns:** Batch analysis prompt

##### `parse_grammar_response(ai_response, complexity, sentence)`
Parse AI JSON response into structured analysis.

**Parameters:**
- `ai_response` (str): JSON response from AI
- `complexity` (str): Analysis complexity level
- `sentence` (str): Original sentence

**Returns:** Dict with parsed analysis

##### `validate_analysis(parsed_data, original_sentence)`
Validate analysis quality and assign confidence score.

**Parameters:**
- `parsed_data` (Dict): Parsed analysis data
- `original_sentence` (str): Original input sentence

**Returns:** Float confidence score (0.0-1.0)

##### `get_color_scheme(complexity)`
Get color coding scheme for grammatical roles.

**Parameters:**
- `complexity` (str): Complexity level

**Returns:** Dict mapping roles to hex colors

##### `analyze_grammar(sentence, target_word, complexity, google_api_key)`
Complete grammar analysis with retry logic.

**Parameters:**
- `sentence` (str): Sentence to analyze
- `target_word` (str): Target word
- `complexity` (str): Complexity level
- `google_api_key` (str): API key for AI calls

**Returns:** GrammarAnalysis object

## Error Handling

### JSON Parsing Errors
- **Fallback**: Text-based parsing attempts
- **Recovery**: Graceful degradation to basic analysis
- **Logging**: Detailed error information for debugging

### Validation Failures
- **Retry Logic**: Up to 2 automatic retries for low confidence
- **Threshold**: 85% minimum confidence required
- **Fallback**: Partial results when possible

### Network/API Errors
- **Timeout Handling**: Configurable timeouts
- **Rate Limiting**: Built-in delays between retries
- **API Key Validation**: Secure key handling

## Performance Characteristics

### Processing Speed
- **Single sentences**: <2 seconds typical
- **Batch processing**: <10 seconds for 16 sentences
- **Memory usage**: Minimal, regex-based pattern matching

### Scalability
- **Concurrent requests**: Thread-safe implementation
- **Large batches**: Efficient processing with partial fallbacks
- **Memory efficiency**: Stream processing for large inputs

## Dependencies

### Required Packages
- `re`: Regular expression pattern matching
- `json`: JSON parsing and generation
- `logging`: Structured logging
- `typing`: Type hints for better code documentation

### Framework Dependencies
- `BaseGrammarAnalyzer`: Core analysis framework
- `IndoEuropeanAnalyzer`: European language base class
- `LanguageConfig`: Language configuration structure

## Future Enhancements

### Planned Features
- **Dialect support**: Regional variation handling (Spain vs Latin America)
- **Historical forms**: Archaic Spanish analysis
- **Poetic analysis**: Literary device recognition
- **Speech recognition**: Phonetic pattern integration

### Research Areas
- **Corpus-based validation**: Large-scale accuracy testing
- **Machine learning integration**: Statistical pattern recognition
- **Cross-language comparison**: Romance language parallels
- **Error pattern analysis**: Common AI mistake identification

## Contributing

### Code Standards
- **PEP 8**: Python style guide compliance
- **Type hints**: Full type annotation coverage
- **Documentation**: Comprehensive docstrings
- **Testing**: 90%+ test coverage requirement

### Development Workflow
1. **Fork repository**: Create feature branch
2. **Implement changes**: Follow existing patterns
3. **Add tests**: Comprehensive test coverage
4. **Update documentation**: API and usage guides
5. **Submit PR**: Code review and integration

## License

This Spanish Grammar Analyzer is part of the Language Learning application suite. See project LICENSE for usage terms and conditions.

## Contact

For questions, bug reports, or contributions:
- **Repository**: Language Learning project
- **Issue tracker**: GitHub issues
- **Documentation**: This document and inline code comments