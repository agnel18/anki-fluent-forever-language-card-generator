# zh_analyzer_documentation.md - Chinese Simplified Analyzer Technical Documentation
# Version: 2026-01-19 (Following Hindi Gold Standard Template)

## Overview
The Chinese Simplified Grammar Analyzer (`ZhAnalyzer`) implements comprehensive grammar analysis for Chinese Simplified (ç®€ä½“ä¸­æ–‡) following domain-driven design principles. It serves as the gold standard implementation for analytic languages and provides detailed grammatical breakdown for language learning applications.

## Architecture

### Clean Architecture Implementation
```
languages/chinese_simplified/
â”œâ”€â”€ zh_analyzer.py              # Main Facade (Clean Architecture entry point)
â”œâ”€â”€ zh_grammar_concepts.md      # Linguistic research documentation
â”œâ”€â”€ zh_analyzer_documentation.md # Technical implementation details
â”œâ”€â”€ domain/                     # Domain layer (business logic)
â”‚   â”œâ”€â”€ zh_config.py           # Configuration management
â”‚   â”œâ”€â”€ zh_prompt_builder.py   # AI prompt generation
â”‚   â”œâ”€â”€ zh_response_parser.py  # Response parsing and fallbacks
â”‚   â”œâ”€â”€ zh_validator.py        # Quality validation
â”‚   â”œâ”€â”€ zh_fallbacks.py        # Rule-based error recovery
â”‚   â””â”€â”€ zh_patterns.py         # Linguistic pattern recognition
â”œâ”€â”€ infrastructure/            # Infrastructure layer (external concerns)
â”‚   â””â”€â”€ data/                  # Configuration files
â”‚       â”œâ”€â”€ zh_grammatical_roles.yaml
â”‚       â”œâ”€â”€ zh_common_classifiers.yaml
â”‚       â”œâ”€â”€ zh_aspect_markers.yaml
â”‚       â”œâ”€â”€ zh_structural_particles.yaml
â”‚       â”œâ”€â”€ zh_modal_particles.yaml
â”‚       â”œâ”€â”€ zh_word_meanings.json
â”‚       â””â”€â”€ zh_patterns.yaml
â””â”€â”€ tests/                     # Test layer
    â””â”€â”€ test_zh_analyzer.py    # Comprehensive test suite
```

### Key Design Patterns

#### 1. Facade Pattern
- **ZhAnalyzer** serves as single entry point
- Orchestrates domain components
- Provides clean public API
- Hides complexity from clients

#### 2. Domain-Driven Design
- **Domain Layer**: Pure business logic
- **Infrastructure Layer**: External dependencies (files, APIs)
- **Dependency Injection**: Components receive dependencies
- **Separation of Concerns**: Each component has single responsibility

#### 3. Strategy Pattern
- **Fallback System**: Multiple recovery strategies
- **Validation Approaches**: Different validation heuristics
- **Parsing Methods**: Various JSON extraction techniques

## Component Details

### ZhAnalyzer (Main Facade)
**Location**: `zh_analyzer.py`
**Purpose**: Orchestrates all analysis components
**Key Methods**:
- `analyze_grammar()`: Single sentence analysis
- `batch_analyze_grammar()`: Multiple sentence analysis
- `get_color_scheme()`: UI color configuration

**Integration Points**:
- Called by `sentence_generator.py` for Pass 3
- Returns `GrammarAnalysis` objects
- Handles 8-sentence batches for efficiency

### Domain Components

#### ZhConfig
**Location**: `domain/zh_config.py`
**Purpose**: Configuration management and color schemes
**Responsibilities**:
- Load YAML/JSON configuration files
- Define grammatical role mappings
- Provide complexity-appropriate color schemes
- Store language-specific patterns

**Configuration Files**:
- `zh_grammatical_roles.yaml`: Role definitions
- `zh_common_classifiers.yaml`: Classifier lists
- `zh_aspect_markers.yaml`: Aspect particle definitions
- `zh_structural_particles.yaml`: Structural particle definitions
- `zh_modal_particles.yaml`: Modal particle definitions
- `zh_word_meanings.json`: Pre-defined word meanings
- `zh_patterns.yaml`: Validation patterns

#### ZhPromptBuilder
**Location**: `domain/zh_prompt_builder.py`
**Purpose**: Generate AI prompts using Jinja2 templates
**Key Features**:
- Template-based prompt generation
- Complexity-aware instructions
- Chinese-specific grammatical categories
- Batch and single sentence support

#### ZhResponseParser
**Location**: `domain/zh_response_parser.py`
**Purpose**: Parse AI responses and apply fallbacks
**Fallback Hierarchy**:
1. Primary: Successful AI parsing
2. Secondary: Pattern-based recovery
3. Tertiary: Rule-based fallbacks
4. Quaternary: Basic character-based fallbacks

#### ZhValidator
**Location**: `domain/zh_validator.py`
**Purpose**: Validate results and calculate confidence scores
**Validation Heuristics**:
- Word count matching
- Role distribution analysis
- Pattern recognition (aspect markers, classifiers)
- Confidence scoring with multi-factor assessment

#### ZhFallbacks
**Location**: `domain/zh_fallbacks.py`
**Purpose**: Rule-based error recovery
**Strategies**:
- Dictionary lookup for known words
- Character-based role guessing
- Pattern matching for particles and classifiers
- Contextual default assignments

#### ZhPatterns
**Location**: `domain/zh_patterns.py`
**Purpose**: Regex-based linguistic pattern recognition
**Pattern Categories**:
- Aspect markers (äº†, ç€, è¿‡)
- Modal particles (å—, å‘¢, å§)
- Structural particles (çš„, åœ°, å¾—)
- Classifiers (ä¸ª, æœ¬, æ¯)
- Han character validation

## Chinese-Specific Features

### Analytic Language Handling
Unlike Indo-European languages, Chinese lacks inflectional morphology:
- **No Tense**: Time reference through context and particles
- **No Number/Gender**: No agreement requirements
- **No Case**: Word order determines grammatical relations

### Aspect System
Chinese uses particles for aspect rather than tense:
- **äº† (le)**: Perfective aspect (completed action)
- **ç€ (zhe)**: Progressive/durative aspect (ongoing action)
- **è¿‡ (guo)**: Experiential aspect (experienced action)

### Classifier System
Obligatory measure words categorize nouns:
- **ä¸ª (gÃ¨)**: General classifier
- **æœ¬ (bÄ›n)**: For books, bound objects
- **æ¯ (bÄ“i)**: For containers
- **åª (zhÄ«)**: For animals, one of a pair

### Particle System
Complex particle usage for grammatical functions:
- **Structural Particles**: çš„ (possessive), åœ° (adverbial), å¾— (complement)
- **Modal Particles**: å— (question), å‘¢ (continuation), å§ (suggestion)
- **Aspect Particles**: äº†, ç€, è¿‡

### Topic-Comment Structure
Primary sentence pattern differs from SVO:
- **Topic**: What the sentence is about
- **Comment**: What is said about the topic
- Example: è¿™æœ¬ä¹¦å¾ˆæœ‰æ„æ€ (This book is very interesting)

## Integration with Main Application

### Pass 3 Integration
The analyzer integrates with the 6-step language learning pipeline:

1. **Input**: Sentence from `sentence_generator.py`
2. **Analysis**: Grammar breakdown with AI + fallbacks
3. **Output**: `GrammarAnalysis` object with:
   - `word_explanations`: [[word, role, color, meaning], ...]
   - `color_scheme`: Complexity-appropriate colors
   - `confidence_score`: Quality indicator
   - `html_output`: Colored sentence display

### Batch Processing
- **Batch Size**: 8 sentences (optimal balance)
- **Token Limit**: 4000 max_tokens (prevents JSON truncation)
- **Error Handling**: Per-sentence fallbacks
- **Performance**: <5 second response times

### Color Coding Philosophy
- **Progressive Disclosure**: More roles at higher complexity
- **Consistency**: Same colors for same roles across levels
- **Accessibility**: High contrast, colorblind-friendly
- **Language-Appropriate**: Colors reflect Chinese grammatical concepts

## Testing Strategy

### Test Categories
- **Unit Tests**: Individual component testing
- **Integration Tests**: Full analyzer workflow
- **Performance Tests**: Response time validation
- **Accuracy Tests**: Grammar analysis quality
- **Edge Cases**: Error conditions and boundary cases

### Test Coverage
- **Components**: All domain components tested
- **Workflows**: Single and batch analysis
- **Fallbacks**: Error recovery mechanisms
- **Configuration**: Color schemes and settings
- **Patterns**: Linguistic pattern recognition

### Quality Gates
- **Linguistic Accuracy**: Respects Chinese analytic structure
- **Aspect Correctness**: Proper äº†/ç€/è¿‡ validation
- **Classifier Appropriateness**: Correct measure word usage
- **Word Order**: LTR explanations matching sentence order
- **Particle Recognition**: Accurate particle classification
- **Performance**: <5 second batch processing times
- **Test Coverage**: >90% accuracy on test sentences

## Performance Characteristics

### Response Times
- **Single Sentence**: <2 seconds
- **Batch (8 sentences)**: <5 seconds
- **Fallback Analysis**: <0.5 seconds

### Memory Usage
- **Configuration**: ~50KB (loaded once)
- **Per Analysis**: ~10KB additional
- **Batch Processing**: Linear scaling with sentence count

### Scalability
- **Concurrent Requests**: Thread-safe design
- **Resource Limits**: Automatic cleanup
- **Error Recovery**: Graceful degradation

## Error Handling

### AI API Failures
- **Timeout**: 30-second limit with fallback
- **Rate Limiting**: Exponential backoff
- **Invalid Responses**: Comprehensive JSON validation
- **Network Issues**: Retry logic with fallbacks

### Configuration Errors
- **Missing Files**: Graceful defaults
- **Invalid YAML/JSON**: Error logging with fallbacks
- **Version Mismatches**: Backward compatibility

### Linguistic Edge Cases
- **Unsegmented Text**: Character-level fallback
- **Mixed Scripts**: Han character validation
- **Compound Words**: Recognition and treatment as units
- **Ambiguous Particles**: Context-based disambiguation

## Future Enhancements

### Planned Improvements
- **Word Segmentation**: Integration with Jieba or similar
- **Tone Integration**: Include tonal information in IPA
- **Corpus-Based Validation**: Statistical validation methods
- **Multi-Dialect Support**: Cantonese, Taiwanese extensions

### Research Areas
- **Aspect Disambiguation**: Context-aware aspect marker analysis
- **Classifier Prediction**: Automatic classifier selection
- **Collocation Recognition**: Multi-word unit identification
- **Pragmatic Analysis**: Discourse-level grammatical features

## Maintenance Guidelines

### Code Organization
- **Domain Logic**: Keep in domain/ folder
- **Configuration**: External files in infrastructure/data/
- **Tests**: Comprehensive coverage in tests/
- **Documentation**: Update with code changes

### Version Control
- **Semantic Versioning**: Major.Minor.Patch
- **Breaking Changes**: Major version bumps
- **Backward Compatibility**: Maintain for 2 versions

### Monitoring
- **Performance Metrics**: Response times and error rates
- **Accuracy Tracking**: Regular quality assessments
- **User Feedback**: Integration with improvement pipeline

## Conclusion

The Chinese Simplified Grammar Analyzer represents a comprehensive implementation of domain-driven design for analytic languages. It provides accurate, efficient, and maintainable grammar analysis while serving as a gold standard for implementing analyzers for other Sino-Tibetan languages.

The modular architecture ensures scalability, the comprehensive fallback system guarantees reliability, and the extensive testing provides confidence in production deployment.
