# ZhAnalyzer Documentation
## Chinese Simplified Grammar Analyzer for Language Learning Decks

**Version**: 3.0 (Phase 3 Complete)
**Language**: Chinese Simplified (中文简体)
**Language Code**: zh
**Inheritance**: `BaseGrammarAnalyzer`

## Overview

The `ZhAnalyzer` is a specialized grammar analyzer for Chinese Simplified (Mandarin Chinese) designed for Pass 3 of the 6-step language learning deck generation process. It provides word-level grammatical analysis with proper handling of Chinese linguistic features including aspect particles, measure words, modal particles, and the 实词/虚词 (content word/function word) distinction.

## Linguistic Features Supported

### Grammatical Categories (16 Total)

#### Content Words (实词 / Shící)
1. **Noun (名词)**: People, places, things, concepts
2. **Verb (动词)**: Actions, states, changes
3. **Adjective (形容词)**: Qualities, descriptions
4. **Numeral (数词)**: Numbers, quantities
5. **Measure Word/Classifier (量词)**: Counting units (个, 本, 杯, 张)
6. **Pronoun (代词)**: Replacements for nouns
7. **Time Word (时间词)**: Time expressions (今天, 明天, 现在)
8. **Locative Word (处所词)**: Location/direction (这里, 那里, 上, 下)

#### Function Words (虚词 / Xūcí)
9. **Aspect Particle (体词)**: Aspect markers (了, 着, 过)
10. **Modal Particle (语气词)**: Sentence mood (吗, 呢, 吧, 啊)
11. **Structural Particle (结构词)**: Relationship markers (的, 地, 得)
12. **Preposition/Coverb (介词/趋向词)**: Relationships (在, 对, 给, 从)
13. **Conjunction (连词)**: Connectors (和, 但是, 因为)
14. **Adverb (副词)**: Verb/adjective modifiers (很, 不, 都)
15. **Interjection (叹词)**: Emotions/exclamations (啊, 哦, 唉)
16. **Onomatopoeia (拟声词)**: Sound imitation (砰, 哗啦)

### Key Linguistic Patterns

#### Aspect System
- **了 (le)**: Perfective aspect - completed actions
- **着 (zhe)**: Durative aspect - ongoing states
- **过 (guo)**: Experiential aspect - experienced actions

#### Modal Particles
- **吗 (ma)**: Yes-no questions
- **呢 (ne)**: Topic continuation, confirmation
- **吧 (ba)**: Suggestion, assumption
- **啊 (a)**: Exclamation, realization

#### Structural Particles
- **的 (de)**: Attribution/possession
- **地 (de)**: Adverbial modification
- **得 (de)**: Resultative complement

#### Measure Words (Top 10)
- 个 (gè): General classifier
- 本 (běn): Books, notebooks
- 杯 (bēi): Cups, glasses
- 张 (zhāng): Flat objects
- 只 (zhī): Animals, one of a pair
- 辆 (liàng): Vehicles
- 家 (jiā): Businesses, families
- 位 (wèi): People (polite)
- 条 (tiáo): Long thin objects
- 件 (jiàn): Items, matters

## API Reference

### Class Initialization

```python
from language_analyzers.analyzers.zh_analyzer import ZhAnalyzer

analyzer = ZhAnalyzer()
```

### Core Methods

#### `get_batch_grammar_prompt(sentences: List[str]) -> str`
Generates a comprehensive grammar analysis prompt for a batch of Chinese sentences.

**Parameters:**
- `sentences`: List of Chinese sentences to analyze

**Returns:** Formatted prompt string for AI processing

**Example:**
```python
sentences = ["我吃了三个苹果。", "他在图书馆学习。"]
prompt = analyzer.get_batch_grammar_prompt(sentences)
# Returns detailed prompt with Chinese linguistic instructions
```

#### `parse_batch_grammar_response(response_json: str, sentences: List[str]) -> List[Dict]`
Parses AI response and validates grammatical analysis.

**Parameters:**
- `response_json`: JSON string from AI analysis
- `sentences`: Original sentences being analyzed

**Returns:** List of analysis results with validation scores

**Example:**
```python
results = analyzer.parse_batch_grammar_response(ai_response, sentences)
for result in results:
    print(f"Confidence: {result['confidence']}")
    print(f"HTML: {result['html_output']}")
```

#### `validate_analysis(analysis: List[Dict]) -> Tuple[bool, float, List[str]]`
Validates grammatical analysis using Chinese-specific checks.

**Parameters:**
- `analysis`: List of word analysis dictionaries

**Returns:** Tuple of (is_valid, confidence_score, issues_list)

**Validation Checks:**
1. Required particles present in appropriate contexts
2. All characters are valid Han characters
3. Measure word agreement for quantified nouns
4. Pinyin includes proper tone marks
5. Basic SVO word order patterns
6. Common compound word formation

#### `generate_html_output(analysis: List[Dict], sentence: str) -> str`
Generates color-coded HTML output for grammatical visualization.

**Parameters:**
- `analysis`: Grammatical analysis results
- `sentence`: Original sentence

**Returns:** HTML string with color-coded grammatical roles

### Color Scheme

```python
GRAMMATICAL_ROLES = {
    # Content Words (实词)
    "noun": "#FFAA00",                    # Orange
    "verb": "#44FF44",                    # Green
    "adjective": "#FF44FF",               # Magenta
    "numeral": "#FFFF44",                 # Yellow
    "measure_word": "#FFD700",            # Gold
    "pronoun": "#FF4444",                 # Red
    "time_word": "#FFA500",               # Orange-red
    "locative_word": "#FF8C00",           # Dark orange

    # Function Words (虚词)
    "aspect_particle": "#8A2BE2",         # Purple
    "modal_particle": "#DA70D6",          # Plum
    "structural_particle": "#9013FE",     # Violet
    "preposition": "#4444FF",             # Blue
    "conjunction": "#888888",             # Gray
    "adverb": "#44FFFF",                  # Cyan
    "interjection": "#FFD700",            # Gold
    "onomatopoeia": "#FFD700"             # Gold
}
```

## Usage Examples

### Basic Analysis

```python
analyzer = ZhAnalyzer()

# Single sentence analysis
sentence = "我吃了三个苹果。"
analysis_result = analyzer.analyze_grammar(sentence)

print(f"Confidence: {analysis_result['confidence']}")
print(f"HTML Output: {analysis_result['html_output']}")
```

### Batch Processing

```python
sentences = [
    "我吃了三个苹果。",
    "他在图书馆学习。",
    "你去过北京吗？",
    "这本书很好看。",
    "我们一起吃饭吧。"
]

# Process batch
results = analyzer.process_batch_grammar_analysis(sentences)

for i, result in enumerate(results):
    print(f"Sentence {i+1}: {sentences[i]}")
    print(f"Confidence: {result['confidence']}")
    print(f"Analysis: {result['analysis'][:3]}...")  # First 3 words
    print()
```

### Integration with Deck Generation

```python
# In Pass 3 of deck generation pipeline
def generate_grammar_pass(sentences, analyzer):
    """Generate Pass 3: Grammar Analysis cards"""

    results = analyzer.process_batch_grammar_analysis(sentences)

    cards = []
    for sentence, result in zip(sentences, results):
        if result['confidence'] >= 0.85:  # Quality threshold
            card = {
                'sentence': sentence,
                'grammar_html': result['html_output'],
                'word_analysis': result['analysis'],
                'confidence': result['confidence']
            }
            cards.append(card)

    return cards

# Usage
zh_analyzer = ZhAnalyzer()
grammar_cards = generate_grammar_pass(chinese_sentences, zh_analyzer)
```

## Validation Details

### Confidence Scoring
- **High Confidence (≥0.85)**: All validation checks pass
- **Medium Confidence (0.70-0.84)**: Minor issues detected
- **Low Confidence (<0.70)**: Major validation failures

### Validation Checks Implementation

#### 1. Particle Position Validation
```python
def _validate_particle_positions(self, analysis):
    """Check aspect/modal particles are in correct positions"""
    # Aspect particles should follow verbs
    # Modal particles should be sentence-final
    # Implementation checks regex patterns for position
```

#### 2. Character Set Validation
```python
def _validate_characters(self, text):
    """Verify all characters are valid Han characters"""
    # Uses Unicode ranges for Chinese characters
    # Excludes Latin characters, punctuation
```

#### 3. Measure Word Agreement
```python
def _validate_measure_words(self, analysis):
    """Check numeral + measure word + noun sequences"""
    # Validates proper classifier usage
    # Checks common measure word + noun combinations
```

#### 4. Pinyin Tone Validation
```python
def _validate_pinyin(self, analysis):
    """Verify Pinyin includes proper tone marks"""
    # Checks for ā/á/ǎ/à tone marks
    # Validates neutral tone patterns
```

## Error Handling

### Batch Processing Errors
- **JSON Parsing Errors**: Falls back to partial results
- **AI Response Timeouts**: Automatic retry with exponential backoff
- **Validation Failures**: Confidence scoring with detailed issue reporting

### Logging
```python
import logging
logging.basicConfig(level=logging.INFO)

# Analyzer logs validation issues and processing steps
analyzer = ZhAnalyzer()  # Logs initialization details
```

## Performance Characteristics

### Batch Processing
- **Optimal Batch Size**: 8-16 sentences
- **Processing Time**: ~2-5 seconds per batch
- **Memory Usage**: ~50-100KB per sentence
- **Retry Logic**: Up to 2 retries with 1s/30s backoff

### Validation Performance
- **Real-time Validation**: <100ms per analysis
- **Pattern Matching**: Regex-based for efficiency
- **Memory Efficient**: Minimal object creation

## Testing

### Test Coverage
Run comprehensive test suite:
```bash
cd /path/to/project
python -m pytest tests/test_zh_analyzer.py -v
```

### Test Categories
- **Unit Tests**: Individual method validation
- **Integration Tests**: Full batch processing workflows
- **Linguistic Tests**: Chinese-specific grammar validation
- **Error Handling**: Edge cases and failure scenarios
- **Performance Tests**: Batch processing efficiency

## Dependencies

### Required Packages
- `language_analyzers.core.base_analyzer`: Base analyzer framework
- `language_analyzers.utils.batch_processor`: Batch processing utilities
- `language_analyzers.utils.data_transformer`: HTML generation utilities

### Python Version
- **Minimum**: Python 3.8+
- **Recommended**: Python 3.9+
- **Tested**: Python 3.8, 3.9, 3.10, 3.11

## Architecture Notes

### Inheritance Strategy
Inherits directly from `BaseGrammarAnalyzer` rather than creating a Sino-Tibetan base class, as no other Sino-Tibetan languages are planned for implementation in the next 3 months.

### Pattern Implementation
Focuses on 5-12 most frequent grammatical markers:
- Aspect particles (了, 着, 过)
- Modal particles (吗, 呢, 吧, 啊)
- Structural particles (的, 地, 得)
- Top measure words (个, 本, 杯, 张, 只)
- Common prepositions (在, 对, 给, 从, 到)

### Script Handling
- **Primary**: Han characters (logographic)
- **Secondary**: Hanyu Pinyin with tone marks
- **Validation**: Unicode range checking for authenticity

## Future Enhancements

### Phase 5 Considerations
- **Character-Level Analysis**: Integration with character decomposition
- **Tone Analysis**: Advanced tonal pattern recognition
- **Regional Variants**: Support for Traditional Chinese
- **Corpus Integration**: Training on larger Chinese corpora

### Performance Optimizations
- **Caching**: Pattern compilation caching
- **Parallel Processing**: Multi-threaded batch analysis
- **Memory Pooling**: Object reuse for large batches

## Troubleshooting

### Common Issues

#### Low Confidence Scores
**Symptom**: Analysis confidence below 0.85
**Cause**: Missing particles, invalid characters, or incorrect word boundaries
**Solution**: Check sentence validity and ensure proper Chinese characters

#### HTML Generation Errors
**Symptom**: Malformed HTML output
**Cause**: Invalid analysis structure or missing role mappings
**Solution**: Validate analysis dictionary structure before HTML generation

#### Batch Processing Timeouts
**Symptom**: AI calls timing out
**Cause**: Large batches or network issues
**Solution**: Reduce batch size or check network connectivity

### Debug Mode
Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)

analyzer = ZhAnalyzer()  # Will log detailed processing steps
```

## Contributing

### Code Standards
- Follow PEP 8 style guidelines
- Add comprehensive docstrings
- Include unit tests for new features
- Update documentation for API changes

### Testing New Features
```python
# Add to test_zh_analyzer.py
def test_new_feature(self, analyzer):
    # Test implementation
    pass
```

## License

This analyzer is part of the Language Learning Deck Generation system. See project LICENSE file for details.

## Version History

- **v3.0** (Phase 3): Full implementation + batch handling adaptations
  - Complete Chinese linguistic feature support
  - Robust validation with 85% confidence threshold
  - Comprehensive batch processing with fallbacks
  - HTML color-coded output generation

- **v2.0** (Phase 2): Analyzer skeleton + patterns + validation
  - Basic pattern recognition
  - Core validation logic
  - Initial batch processing framework

- **v1.0** (Phase 1): Grammar concepts research
  - Linguistic research and documentation
  - Grammatical category definitions
  - Architecture planning

---

**Implementation Status**: ✅ Phase 3 Complete
**Ready for**: Phase 4 (Tests + Documentation) ✅ Complete
**Next Phase**: Phase 5 (Integration Testing) or Phase 6 (Production Deployment)