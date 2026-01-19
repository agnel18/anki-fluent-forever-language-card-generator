# Language Grammar Analyzer Generator Template
# Version: 2026-01-17 (Updated with IPA Romanization, Token Limits, and Repository Cleanup)

## Overview
You are tasked with adapting the gold standard Hindi analyzer (hi_analyzer.py) to create a comprehensive grammar analyzer for **{language}** focused specifically on **Pass 3: Grammar Analysis** in the 6-step language learning deck generation process.

## Critical Process Requirement
**BEFORE BEGINNING ANY CODING**, you **MUST** first create a comprehensive **{language}_grammar_concepts.md** file that documents all linguistic research, grammatical structures, and implementation requirements. This ensures focused, high-quality work by separating research from implementation.

## 🔧 RECENT IMPROVEMENTS AND LESSONS LEARNED (2026-01-17)

### **IPA Romanization Support for Learner Languages**
**Lesson:** For Indic and Arabic-script languages, romanized transliterations are more pedagogically valuable than strict IPA for language learners.

**Implementation:**
- Add romanization support in `generation_utils.py` `validate_ipa_output()`
- Include language-specific diacritic sets for romanization validation
- Update AI prompts to request romanization for allowed languages
- Maintain strict IPA validation for phonetic languages (Chinese, European)

**Code Pattern:**
```python
romanization_allowed_languages = ['hi', 'ar', 'fa', 'ur', 'bn', 'pa', 'gu', 'or', 'ta', 'te', 'kn', 'ml', 'si']
romanization_diacritics = 'āēīōūǖǎěǐǒǔǚñḍṭṅṇṃśṣḥḷḻṛṝṁ'

if language in romanization_allowed_languages:
    romanization_pattern = r'^[a-zA-Z\s\'' + romanization_diacritics + r'.,;:!?]+$'
    if re.match(romanization_pattern, text.strip()):
        return True, text
```

### **Grammar Analysis Token Limits**
**Lesson:** AI responses for batch grammar analysis require higher token limits to prevent JSON truncation.

**Implementation:**
- Increase `max_tokens` from 1000 to 2000 in analyzer `_call_ai` methods
- Test with 8-sentence batches to ensure complete responses
- Monitor for JSON parsing failures and adjust accordingly

**Code Pattern:**
```python
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": prompt}],
    max_tokens=2000,  # Increased for batch processing
    temperature=0.1
)
```

### **Word Explanation Quality**
**Lesson:** Ensure AI provides detailed `individual_meaning` fields rather than generic descriptions.

**Implementation:**
- Explicitly require `individual_meaning` in AI prompts
- Test for meaningful explanations vs. generic fallbacks
- Validate that explanations match the target language's context

**Prompt Pattern:**
```python
For each word:
- individual_meaning: the English translation/meaning of this specific word (MANDATORY - do not leave empty)
- grammatical_role: EXACTLY ONE category from the allowed list
```

## Gold Standard References

Use the following files and implementations as your gold standard:

### Core Files to Reference:
- **hi_analyzer.py**: Complete LTR implementation with all enhancements (patterns, validation, retries, batch processing, Devanagari support, 2000 max_tokens for complete responses)
- **ar_analyzer.py**: Complete RTL implementation with proper word ordering, contextual meanings, and script-aware processing
- **indo_european_analyzer.py**: Base class structure and common functionality
- **batch_processor.py**: Batch processing with partial fallbacks and exponential backoff
- **DataTransformer**: Color mapping and HTML generation utilities
- **generation_utils.py**: IPA validation with romanization support for Indic languages
- **hindi_analyzer_enhancement_master.md**: Complete documentation of LTR improvements
- **arabic_grammar_concepts.md**: Complete documentation of RTL linguistic research and implementation

### Key Implementation Patterns:

#### **Token Limits & Response Handling**
```python
# Gold Standard: Increased token limits for complete responses
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": prompt}],
    max_tokens=2000,  # Critical: Prevents JSON truncation
    temperature=0.1
)
```

#### **IPA Romanization Support**
```python
# Gold Standard: Romanization for learner languages
romanization_allowed_languages = ['hi', 'ar', 'fa', 'ur', 'bn', 'pa', 'gu', 'or', 'ta', 'te', 'kn', 'ml', 'si']
romanization_diacritics = 'āēīōūǖǎěǐǒǔǚñḍṭṅṇṃśṣḥḷḻṛṝṁ'

if language in romanization_allowed_languages:
    romanization_pattern = r'^[a-zA-Z\s\'' + romanization_diacritics + r'.,;:!?]+$'
    if re.match(romanization_pattern, text.strip()):
        return True, text  # Accept romanized IPA
```

#### **Word Explanation Quality Assurance**
```python
# Gold Standard: Detailed meanings, not generic descriptions
For each word:
- individual_meaning: the English translation/meaning of this specific word (MANDATORY - do not leave empty)
- grammatical_role: EXACTLY ONE category from the allowed list
```

### Organized File Structure:
All language files are now organized in the `languages/` directory with a standardized structure. **ALL FILES MUST BE KEPT WITHIN THEIR RESPECTIVE LANGUAGE FOLDERS** for proper organization and maintainability.

```
languages/
├── arabic/                           # RTL Reference Implementation
│   ├── ar_analyzer.py               # Complete RTL analyzer with word reordering
│   ├── ar_grammar_concepts.md       # Linguistic research documentation
│   ├── ar_analyzer_documentation.md # Technical implementation details
│   ├── domain/                      # Domain-driven design components
│   │   ├── ar_config.py            # Language-specific configuration
│   │   ├── ar_prompt_builder.py    # AI prompt generation
│   │   ├── ar_response_parser.py   # Response parsing logic
│   │   ├── ar_fallbacks.py         # Fallback analysis patterns
│   │   └── ar_validator.py         # Validation rules
│   └── tests/
│       └── test_ar_analyzer.py     # Comprehensive test suite
│
├── hindi/                           # LTR Reference Implementation (GOLD STANDARD)
│   ├── hi_analyzer.py               # Main facade with comprehensive comments
│   ├── hi_analyzer_enhancement.md   # Recent improvements documentation
│   ├── domain/                      # Domain-driven design components
│   │   ├── hi_config.py            # Configuration with external file loading
│   │   ├── hi_prompt_builder.py    # Jinja2 template-based prompt building
│   │   ├── hi_response_parser.py   # JSON parsing with comprehensive fallbacks
│   │   ├── hi_fallbacks.py         # Rule-based error recovery
│   │   ├── hi_validator.py         # Confidence scoring and validation
│   │   └── hi_patterns.py          # Regex patterns for linguistic features
│   └── tests/
│       └── test_hi_analyzer.py     # Comprehensive test suite
│
├── [language_code]/                 # New Language Implementation Template
│   ├── [lang_code]_analyzer.py      # Main facade (COPY FROM hi_analyzer.py)
│   ├── [lang_code]_grammar_concepts.md  # Linguistic research (CREATE FIRST)
│   ├── [lang_code]_analyzer_documentation.md  # Technical implementation docs
│   ├── domain/                      # Domain-driven design components
│   │   ├── [lang_code]_config.py    # Language configuration (COPY FROM hi_config.py)
│   │   ├── [lang_code]_prompt_builder.py  # AI prompts (ADAPT FROM hi_prompt_builder.py)
│   │   ├── [lang_code]_response_parser.py # Response parsing (COPY FROM hi_response_parser.py)
│   │   ├── [lang_code]_fallbacks.py # Fallbacks (ADAPT FROM hi_fallbacks.py)
│   │   ├── [lang_code]_validator.py # Validation (COPY FROM hi_validator.py)
│   │   └── [lang_code]_patterns.py  # Patterns (ADAPT FROM hi_patterns.py)
│   └── tests/
│       └── test_[lang_code]_analyzer.py  # Test suite (ADAPT FROM test_hi_analyzer.py)
```

### CRITICAL ORGANIZATION RULE:
**ALL FILES FOR A LANGUAGE MUST BE CONTAINED WITHIN ITS LANGUAGE FOLDER.** No files should be placed outside the `languages/[language_code]/` directory structure. This ensures:

- **Clean separation**: Each language is self-contained
- **Easy maintenance**: Language-specific changes don't affect others
- **Scalability**: New languages can be added without conflicts
- **Version control**: Clear ownership and change tracking
- **Testing isolation**: Language tests run independently

### File Responsibilities (Domain-Driven Design):

#### **Main Facade Files:**
- **`[lang_code]_analyzer.py`**: Orchestrates all components, provides public API
- **`[lang_code]_grammar_concepts.md`**: Linguistic research documentation
- **`[lang_code]_analyzer_documentation.md`**: Technical implementation details

#### **Domain Components (in domain/ folder):**
- **`[lang_code]_config.py`**: Configuration loading and color schemes
- **`[lang_code]_prompt_builder.py`**: AI prompt generation with templates
- **`[lang_code]_response_parser.py`**: JSON parsing and fallback application
- **`[lang_code]_fallbacks.py`**: Rule-based error recovery
- **`[lang_code]_validator.py`**: Quality validation and confidence scoring
- **`[lang_code]_patterns.py`**: Regex patterns for linguistic features

#### **Test Files:**
- **`test_[lang_code]_analyzer.py`**: Unit tests for all components

### Directory Structure Best Practices:

#### **MANDATORY: Domain-Driven Design for ALL Languages**
**ALL NEW LANGUAGE IMPLEMENTATIONS MUST USE DOMAIN-DRIVEN DESIGN** with all files properly organized in language folders:

```
languages/[lang_code]/                    # Language container (MANDATORY)
├── [lang_code]_analyzer.py              # Main facade (COPY FROM hi_analyzer.py)
├── [lang_code]_grammar_concepts.md      # Linguistic research (CREATE FIRST)
├── [lang_code]_analyzer_documentation.md # Technical docs
├── domain/                              # Domain components (MANDATORY)
│   ├── __init__.py                      # Package initialization
│   ├── [lang_code]_config.py            # Configuration (COPY FROM hi_config.py)
│   ├── [lang_code]_prompt_builder.py    # AI prompts (ADAPT FROM hi_prompt_builder.py)
│   ├── [lang_code]_response_parser.py   # Response parsing (COPY FROM hi_response_parser.py)
│   ├── [lang_code]_fallbacks.py         # Fallbacks (ADAPT FROM hi_fallbacks.py)
│   ├── [lang_code]_validator.py         # Validation (COPY FROM hi_validator.py)
│   └── [lang_code]_patterns.py          # Patterns (ADAPT FROM hi_patterns.py)
├── infrastructure/                      # External data files
│   └── data/                            # YAML/JSON config files
│       ├── [lang_code]_grammatical_roles.yaml
│       ├── [lang_code]_common_postpositions.yaml
│       └── [lang_code]_word_meanings.json
└── tests/                               # Test suite
    └── test_[lang_code]_analyzer.py     # Unit tests
```

#### **File Organization Rules:**
1. **NO FILES OUTSIDE LANGUAGE FOLDERS**: All language-specific code must be in `languages/[lang_code]/`
2. **DOMAIN-DRIVEN DESIGN**: Separate business logic into domain components
3. **INFRASTRUCTURE SEPARATION**: External data files in infrastructure/data/
4. **TEST ISOLATION**: Tests in dedicated tests/ subfolder
5. **DOCUMENTATION**: Linguistic research and technical docs in language folder

#### **Deprecated: Simple Languages Structure**
The simple structure below is **DEPRECATED** - use domain-driven design for all languages:

```python
# DEPRECATED - DO NOT USE
languages/[lang_code]/
├── [lang_code]_analyzer.py  # All logic in main analyzer - NOT RECOMMENDED
├── [lang_code]_grammar_concepts.md
└── tests/test_[lang_code]_analyzer.py
```

### Key Gold Standard Features by Script Direction:

#### **LTR Languages (Reference: Hindi)**
1. **Comprehensive Pattern Recognition**: Regex-based linguistic patterns for language-specific features
2. **Enhanced Validation**: 85% confidence threshold with language-specific checks and automatic retries (up to 2x)
3. **Batch Processing**: Partial fallbacks, exponential backoff (1s base, 30s max), per-result validation
4. **Script-Aware Processing**: Proper handling of language-specific scripts and LTR writing direction
5. **Color-Coded HTML Output**: Language-appropriate color schemes with fallback handling
6. **Multilingual Support**: Native language explanations and parameterized prompts
7. **Robust Error Handling**: Logging, fallbacks, and graceful degradation
8. **Word Ordering**: Grammar explanations appear in sentence word order (LTR) for optimal user experience
9. **Token Limit Management**: 2000 max_tokens to prevent JSON truncation in batch responses
10. **IPA Integration**: Romanization support for Indic scripts when beneficial for learners

#### **RTL Languages (Reference: Arabic)**
1. **RTL Word Ordering**: Explanations must be reordered to match RTL reading direction using position-based sorting
2. **Contextual Meanings**: Individual word meanings must include grammatical context (e.g., "the book (definite noun)")
3. **Script Validation**: Unicode range validation for proper script detection
4. **RTL-Specific Prompts**: AI prompts must explicitly specify RTL ordering requirements
5. **Position-Based Reordering**: Use sentence position indexing to reorder explanations for RTL display
6. **Definite Article Handling**: Special processing for assimilated definite articles (ال → ات/اض/اظ/ان)
7. **Root-Based Morphology**: Pattern recognition for triliteral roots and verb forms (ʾabwāb I-X)
8. **Token Limit Management**: 2000 max_tokens for complete batch responses
9. **IPA Integration**: Romanization support for Arabic script languages

#### **Logographic Languages (Reference: Chinese Planning)**
1. **Character vs Word Analysis**: Decide between character-level or word-level analysis based on pedagogical needs
2. **Compound Word Recognition**: Identify and handle multi-character compounds as single units
3. **Tone Integration**: Include tone markers in validation and display
4. **Particle Recognition**: Special handling for aspect particles (了, 着, 过) and structural particles (的, 地, 得)
5. **Classifier System**: Recognition and categorization of measure words
6. **Token Limit Management**: 2000 max_tokens for complex character-based responses
7. **IPA Integration**: Strict IPA validation (no romanization) for tonal languages

#### **Agglutinative Languages (Reference: Turkish Planning)**
1. **Suffix Sequence Analysis**: Pattern recognition for agglutinated morphemes
2. **Harmony Rules**: Vowel harmony validation and generation
3. **Stem Recognition**: Identification of root words vs. derived forms
4. **Case Marker Detection**: Automatic recognition of case suffixes
5. **Token Limit Management**: 2000 max_tokens for morphologically complex responses
6. **IPA Integration**: Strict IPA validation for phonetic precision

### Development Workflow & Quality Assurance

#### **CRITICAL: File Organization Requirements**
**ALL FILES MUST BE CREATED WITHIN THE LANGUAGE FOLDER STRUCTURE:**
- Create folder: `languages/[language_code]/`
- Create subfolder: `languages/[language_code]/domain/`
- Create subfolder: `languages/[language_code]/infrastructure/data/`
- Create subfolder: `languages/[language_code]/tests/`
- **NO FILES should be created outside the language folder**

#### **Phase 1: Linguistic Research (MANDATORY FIRST STEP)**
Create `languages/[language_code]/[language_code]_grammar_concepts.md` FIRST:

```markdown
# [language_code]_grammar_concepts.md - Create This FIRST in languages/[language_code]/

## Language Overview
- Family: [Language family]
- Script: [Writing system and direction]
- Complexity: [Morphological complexity rating]

## Grammatical Categories
- [Category 1]: [Description and examples]
- [Category 2]: [Description and examples]
- etc.

## Key Features
- [Feature 1]: [Linguistic description]
- [Feature 2]: [Linguistic description]
- etc.

## Script-Specific Considerations
- [Special handling requirements]
- [Unicode ranges, diacritics, etc.]
```

#### **Phase 2: Implementation Planning**
1. **Choose Base Class**: `BaseGrammarAnalyzer` vs. `IndoEuropeanAnalyzer`
2. **Define Categories**: Language-appropriate grammatical roles
3. **Script Direction**: LTR/RTL implications for word ordering
4. **IPA Strategy**: Strict IPA vs. romanization based on learner needs
5. **Token Limits**: Set appropriate max_tokens for batch processing
6. **Create Folder Structure**: Set up all required directories

#### **Phase 3: Core Implementation**
Create `languages/[language_code]/[language_code]_analyzer.py` (copy from hi_analyzer.py):

```python
# languages/[language_code]/[language_code]_analyzer.py
"""
[Language Name] Grammar Analyzer - Clean Architecture Implementation
Based on Hindi analyzer gold standard.
"""

class [LangCode]Analyzer(IndoEuropeanAnalyzer):  # or BaseGrammarAnalyzer
    def __init__(self):
        # Initialize domain components from languages/[language_code]/domain/
        self.[lang_code]_config = [LangCode]Config()
        self.prompt_builder = [LangCode]PromptBuilder(self.[lang_code]_config)
        # ... etc
```
    
    def _call_ai(self, prompt: str, groq_api_key: str) -> str:
        # Gold Standard: 2000 max_tokens
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,  # Prevents JSON truncation
            temperature=0.1
        )
        return response.choices[0].message.content.strip()
```

#### **Phase 4: Testing & Validation**
```python
# Comprehensive test suite structure
def test_[lang_code]_analyzer():
    analyzer = [LangCode]Analyzer()
    
    # Test basic functionality
    result = analyzer.analyze_grammar("test sentence", "target", "intermediate", "api_key")
    assert result is not None
    assert len(result.word_explanations) > 0
    
    # Test batch processing
    sentences = ["sentence 1", "sentence 2", "sentence 3"]
    batch_results = analyzer.batch_analyze_grammar(sentences, "target", "intermediate", "api_key")
    assert len(batch_results) == len(sentences)
    
    # Test word ordering (LTR/RTL specific)
    # Test IPA integration
    # Test error handling
```

#### **Quality Gates**
- ✅ **Linguistic Accuracy**: Categories match language's actual grammar
- ✅ **Script Compliance**: Proper handling of writing direction and special characters
- ✅ **Batch Processing**: Handles 8-sentence batches without failures
- ✅ **Word Ordering**: Explanations appear in correct reading order
- ✅ **IPA Integration**: Appropriate validation (strict IPA or romanization)
- ✅ **Error Handling**: Graceful fallbacks and meaningful error messages
- ✅ **Performance**: <5 second response times for batch processing
- ✅ **Test Coverage**: >90% accuracy on test sentences

### Integration Points

#### **Pass 3 Integration**
- Analyzer called by `sentence_generator.py` for grammar analysis
- Results processed by `batch_processor.py` for HTML generation
- Word explanations must be in list format: `[word, role, color, meaning]`
- Colored sentences use span tags with grammar class names

#### **IPA Integration**
- `generation_utils.py` handles IPA generation and validation
- Romanization allowed for specified languages
- Fallback to placeholder if IPA generation fails

#### **File System Integration**
- Analyzers auto-discovered by `analyzer_registry.py`
- Configuration loaded from language-specific config files
- Tests run via pytest with standard naming conventions

## Target Language: {language}

### Linguistic Research Requirements
Conduct thorough research on **{language}** grammar using authoritative sources:

**Primary Sources by Language Family:**
- **Sino-Tibetan**: Huang Borong & Liao Xudong 《现代汉语》 + modern typological works
- **Indo-European**: Language-specific descriptive grammars (e.g., Spanish: Butt & Benjamin; Russian: Timberlake)
- **Afro-Asiatic**: Classical & Modern Standard Arabic grammars + root-based morphology references
- **Niger-Congo**: Reference descriptive grammars for tonal/agglutinative features
- **Austronesian**: Standard grammars for syllabic structures and reduplication
- **Turkic**: Agglutinative morphology references with vowel harmony
- **Dravidian**: Retroflex consonant grammars and diglossia studies
- **Japonic**: Kokugo references + typological descriptions
- **Koreanic**: Alphabet + Sino-Korean morphological studies
- **Tai-Kadai**: Tonal analytic grammar references
- **Austroasiatic**: Monosyllabic tonal grammar studies
- **Isolate Languages**: Language-specific comprehensive grammars

**Research Focus Areas:**
1. **Morphological Structure**: Inflectional vs. analytic vs. agglutinative patterns
2. **Syntactic Features**: Word order, case marking, agreement systems
3. **Script/Orthography**: Character sets, romanization systems, special handling needs
4. **Unique Grammatical Categories**: Language-specific roles (e.g., classifiers, aspect markers, honorifics)
5. **Validation Patterns**: Rule-based checks for grammatical accuracy

## Implementation Requirements

### 1. Fundamental Changes from Hindi (if Applicable)
**DO NOT** force Indo-European frameworks onto fundamentally different languages. Make changes as needed by the language here are some guidelines:

- **Analytic Languages** (Chinese, Vietnamese, Thai): Replace inflectional patterns with particle/classifier systems
- **Agglutinative Languages** (Turkish, Swahili, Japanese): Focus on suffix sequences and harmony rules
- **Tonal Languages** (Chinese, Thai, Vietnamese): Include tone markers in validation
- **RTL Languages** (Arabic, Hebrew, Persian): Implement right-to-left word ordering for explanations
- **Logographic/Syllabic Scripts**: Adapt script handling for character-based writing systems
- **Root-Based Morphology** (Arabic, Hebrew): Implement root-and-pattern validation
- **Polysynthetic Languages**: Handle complex word formation and incorporation

**Important Architecture Decision (MUST READ):**
- Do **NOT** create new family base classes (`SinoTibetanAnalyzer`, etc.) unless you already have 3+ very similar languages planned in the next 3 months **and** they share ≥70% of implementation patterns.
- Prefer keeping inheritance from `BaseGrammarAnalyzer` (or `IndoEuropeanAnalyzer` as pure skeleton) and doing **all** language-specific logic inside the concrete class.
- Premature family base classes almost always become maintenance nightmares.

### 2. Core Components to Implement

#### A. Language-Specific Patterns (`_initialize_patterns()`)
```python
def _initialize_patterns(self):
    """Initialize {language}-specific linguistic patterns"""
    # Example adaptations:
    # Chinese: aspect particles (了, 着, 过), classifiers (个, 本, 杯)
    # Arabic: root patterns, case endings (i'rab)
    # Turkish: suffix harmony, agglutination rules
    # Russian: case/number/gender inflection patterns
    # etc.
```

**Pattern Depth Guidance:**
- Implement regex/pattern checks **only** for the **5–12 most frequent and most distinctive** grammatical markers, particles, cases, classifiers, harmony rules, etc.
- Do **not** try to parse full morphology or complex sequences — leave that to the LLM + confidence-based validation.
- Example targets: most common particles (Chinese 了/着/过), case/postpositions (Russian/Turkish), classifiers (Thai/Chinese), basic honorifics (Japanese/Korean).

#### B. Grammatical Role Mapping (`GRAMMATICAL_ROLES`)
Define language-appropriate categories:
- **Analytic**: topic, comment, aspect_marker, classifier, particle
- **Agglutinative**: root, suffix_sequence, harmony_marker
- **Inflectional**: case, number, gender, tense, person
- **Tonal**: Include tone validation where applicable

#### C. Word Ordering Safeguard (`_reorder_explanations_by_sentence_position()`)
**CRITICAL REQUIREMENT**: Implement word explanation ordering to match sentence word order.

**LTR Reference (Hindi Implementation):**
```python
def _reorder_explanations_by_sentence_position(self, sentence: str, word_explanations: List[List]) -> List[List]:
    """
    Reorder word explanations to match the order they appear in the sentence.
    This ensures grammar explanations are displayed in sentence word order for better user experience.
    """
    if not word_explanations or not sentence:
        return word_explanations

    # Create a list to track word positions
    positioned_explanations = []

    for explanation in word_explanations:
        if len(explanation) >= 4:
            word = explanation[0]  # word is at index 0 in the list format
            if word:
                # Find all occurrences of this word in the sentence
                positions = []
                start = 0
                while True:
                    pos = sentence.find(word, start)
                    if pos == -1:
                        break
                    positions.append(pos)
                    start = pos + 1

                # Use the first occurrence position, or a high number if not found
                position = positions[0] if positions else float('inf')
                positioned_explanations.append((position, explanation))

    # Sort by position in sentence (LTR: ascending order)
    positioned_explanations.sort(key=lambda x: x[0])

    # Extract just the explanations
    sorted_explanations = [exp for _, exp in positioned_explanations]

    return sorted_explanations
```

**RTL Reference (Arabic Implementation - Gold Standard):**
```python
def _reorder_explanations_for_rtl(self, sentence: str, word_explanations: List) -> List:
    """
    Reorder word explanations to match Arabic RTL reading order.
    Arabic is read right-to-left, so explanations should match this order.
    """
    if not word_explanations or not sentence:
        return word_explanations

    # For Arabic (RTL), we need to reorder explanations to match the reading direction
    # Find position of each word in the sentence and sort from right to left
    positioned_explanations = []

    for explanation in word_explanations:
        if len(explanation) >= 4:
            word = explanation[0]  # word is at index 0
            if word:
                # Find all occurrences of this word in the sentence
                positions = []
                start = 0
                while True:
                    pos = sentence.find(word, start)
                    if pos == -1:
                        break
                    positions.append(pos)
                    start = pos + 1

                # Use the first occurrence position
                # For RTL, we'll sort by position ascending (left to right in string = right to left in reading)
                position = positions[0] if positions else float('inf')
                positioned_explanations.append((position, explanation))

    # Sort by position in ascending order (RTL reading: left to right in string = right to left in reading)
    positioned_explanations.sort(key=lambda x: x[0])

    # Extract just the explanations
    sorted_explanations = [exp for _, exp in positioned_explanations]

    return sorted_explanations
```

**RTL Prompt Requirements (Arabic Standard):**
```python
def get_batch_grammar_prompt(self, complexity: str, sentences: List[str], target_word: str, native_language: str = "English") -> str:
    # MUST include explicit RTL ordering instructions
    return f"""For EACH word in EVERY sentence, IN THE ORDER THEY APPEAR IN THE SENTENCE (right to left, as Arabic is read from right to left), provide:
- word: the exact word as it appears in the sentence
- individual_meaning: the {native_language} translation/meaning WITH CONTEXT (MANDATORY - provide detailed, contextual meanings like grammatical function + basic meaning)
- grammatical_role: EXACTLY ONE category from this list: {', '.join(allowed_roles)}

CRITICAL REQUIREMENTS:
- WORDS MUST BE LISTED IN THE EXACT ORDER THEY APPEAR IN THE SENTENCE (right to left for Arabic)
- individual_meaning MUST include BOTH the basic translation AND grammatical context
- grammatical_role MUST be EXACTLY from the allowed list (one word only)
- Do NOT group words by category - list them in sentence reading order
"""

    # For Arabic (RTL), we need to reorder explanations to match the reading direction
    positioned_explanations = []

    for explanation in word_explanations:
        if len(explanation) >= 4:
            word = explanation[0]  # word is at index 0
            if word:
                # Find all occurrences of this word in the sentence
                positions = []
                start = 0
                while True:
                    pos = sentence.find(word, start)
                    if pos == -1:
                        break
                    positions.append(pos)
                    start = pos + 1

                # Use the first occurrence position
                position = positions[0] if positions else float('inf')
                positioned_explanations.append((position, explanation))

    # Sort by position in descending order (RTL)
    positioned_explanations.sort(key=lambda x: x[0], reverse=True)

    # Extract just the explanations
    sorted_explanations = [exp for _, exp in positioned_explanations]

    return sorted_explanations
```

**Implementation Notes:**
- **Script Direction Awareness**: Consider the writing direction of the language
  - **LTR Languages** (English, Hindi, Chinese, Spanish): Sort by ascending position (left-to-right)
  - **RTL Languages** (Arabic, Hebrew, Persian): Sort by ascending position (left-to-right in string = right-to-left in reading)
- Call this method after building word_explanations in batch processing
- Use `sentence.find(word)` to locate word positions
- Acts as safeguard even if AI follows prompt instructions correctly

#### D. Validation Logic (`validate_analysis()`)
Implement language-specific checks:
- **Chinese**: Topic-comment structure, ba-construction, aspect marking
- **Arabic**: I'rab (case marking), root-pattern validation
- **Turkish**: Vowel harmony, agglutination sequence validation
- **Russian**: Case agreement, aspect pairing
- **Japanese**: Honorific levels, particle sequences

**Realistic Validation Depth:**
Focus on 3–6 simple, high-signal checks:
- Required particles/prefixes/suffixes present
- Basic script/character set validation
- Simple agreement checks (number/gender/person) where easy to detect
- Tone markers (if tonal language)
Do **not** implement full morphological parsing unless it is trivial.

#### E. Script Handling
- **Logographic** (Chinese): Han character + Pinyin support, LTR direction
- **Abugida** (Devanagari, Arabic): Consonant-vowel combinations
  - **Devanagari** (Hindi): LTR direction
  - **Arabic** (Arabic, Persian, Urdu): RTL direction - requires special word ordering logic
- **Alphabet** (Latin, Cyrillic): Standard handling, LTR direction
- **Mixed Scripts** (Japanese): Kanji + Kana + Romaji, LTR direction
- **RTL Scripts** (Hebrew, Arabic): Require reverse word ordering for explanations to match reading direction

### 4. Prompt Adaptation
Create language-specific prompts that:
- Use appropriate grammatical terminology
- Include language-specific examples
- Reference authentic linguistic structures
- Support native language explanations
- **CRITICAL: Ensure word explanations appear in sentence order (consider script direction)**

**Word Ordering Requirements:**
- Words MUST be listed in the EXACT order they appear in the sentence
- **LTR Languages** (English, Hindi, Chinese, Spanish): "IN THE ORDER THEY APPEAR IN THE SENTENCE (left to right)"
- **RTL Languages** (Arabic, Hebrew, Persian): "IN THE ORDER THEY APPEAR IN THE SENTENCE (right to left)"
- Include requirement: "WORDS MUST BE LISTED IN THE EXACT ORDER THEY APPEAR IN THE SENTENCE (no grouping by category)"
- Implement script-aware post-processing safeguard: `_reorder_explanations_by_sentence_position()` method

### 5. Testing and Validation
- Achieve >90% accuracy on test sentences
- Handle 8-sentence batches efficiently (not 16 - use 8 for consistency with gold standards)
- Support multilingual explanations
- Include comprehensive logging
- Test all Quality Gates before deployment

## Output Format
**Recommended phased output:**
1. **First response**: Complete `{language}_grammar_concepts.md` (research + architecture decision)
2. **Second response**: Analyzer class skeleton + core patterns + validation checks
3. **Third response**: Full implementation + batch handling adaptations (test with 8-sentence batches)
4. **Fourth response** (optional): Tests + documentation

## Success Criteria
- **Authentic**: True to {language}'s grammatical rules, not Hindi/English impositions
- **Comprehensive**: Covers all major grammatical structures
- **Efficient**: Optimized batch processing with language-appropriate fallbacks
- **Maintainable**: Clear documentation and extensible patterns
- **User-Friendly**: Word explanations appear in sentence order (respecting script direction) for optimal learning experience

### Quality Gates (Must Pass All Before Deployment)
- ✅ **Linguistic Accuracy**: Categories match language's actual grammar
- ✅ **Script Compliance**: Proper handling of writing direction and special characters
- ✅ **Batch Processing**: Handles 8-sentence batches without failures
- ✅ **Word Ordering**: Explanations appear in correct reading order
- ✅ **IPA Integration**: Appropriate validation (strict IPA or romanization)
- ✅ **Error Handling**: Graceful fallbacks and meaningful error messages
- ✅ **Performance**: <5 second response times for batch processing
- ✅ **Test Coverage**: >90% accuracy on test sentences

## Process Steps
1. **FIRST**: Create **{language}_grammar_concepts.md** with complete linguistic research and concepts
2. **THEN**: Create the analyzer implementation using the concepts document as reference
3. **FINALLY**: Create tests and documentation

### Repository Organization Note
- **MANDATORY FILE ORGANIZATION**: ALL language files MUST be contained within their respective `languages/[language_code]/` folders
- **Domain-Driven Design**: Use the standardized domain/ subfolder structure for all components
- **Infrastructure Separation**: External data files in `infrastructure/data/` subfolders
- **Active Code**: All current implementations in `languages/` directory with domain-driven design
- **Archived Files**: Old test files, debugging scripts, and backups moved to `old_20260117/` directory
- **File Structure**: Follow the standardized domain-driven design pattern for new analyzers
- **NO EXCEPTIONS**: Never place language-specific files outside their designated language folders

## Common Pitfalls to Avoid

### **Token Limit Issues**
- ❌ **Don't use 1000 max_tokens** - causes JSON truncation in batch responses
- ✅ **Always use 2000 max_tokens** for complete grammar analysis responses
- Test with 8-sentence batches to ensure no truncation occurs

### **IPA Validation Problems**
- ❌ **Don't force strict IPA on learner languages** - Indic/Arabic scripts benefit from romanization
- ✅ **Use romanization for**: hi, ar, fa, ur, bn, pa, gu, or, ta, te, kn, ml, si
- ✅ **Use strict IPA for**: Chinese, European languages, tonal languages
- Include proper diacritic validation patterns

### **Word Explanation Quality**
- ❌ **Don't accept generic descriptions** - "noun", "verb" without context
- ✅ **Require detailed individual_meaning** - include grammatical context and specific translation
- ✅ **Test for meaningful explanations** - validate against target language context

### **Word Ordering Issues**
- ❌ **Don't ignore script direction** - RTL languages need special handling
- ✅ **Implement position-based reordering** - `_reorder_explanations_by_sentence_position()`
- ✅ **Test with RTL languages** - ensure explanations match reading direction

### **Architecture Mistakes**
- ❌ **Don't create premature family base classes** - wait until you have 3+ similar languages planned
- ✅ **Prefer BaseGrammarAnalyzer inheritance** - keep language logic in concrete classes
- ✅ **Use domain-driven design** - separate concerns for complex languages

### **Testing Oversights**
- ❌ **Don't skip batch processing tests** - single sentence tests miss truncation issues
- ✅ **Test 8-sentence batches** - validate complete workflow
- ✅ **Include all Quality Gates** - comprehensive validation before deployment

Begin with **{language}** and create the complete analyzer implementation following this gold standard approach.