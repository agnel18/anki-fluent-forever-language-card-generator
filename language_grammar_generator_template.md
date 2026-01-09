# Language Grammar Analyzer Generator Template

## Overview
You are tasked with adapting the gold standard Hindi analyzer (hi_analyzer.py) to create a comprehensive grammar analyzer for **{language}** focused specifically on **Pass 3: Grammar Analysis** in the 6-step language learning deck generation process.

## Critical Process Requirement
**BEFORE BEGINNING ANY CODING**, you **MUST** first create a comprehensive **{language}_grammar_concepts.md** file that documents all linguistic research, grammatical structures, and implementation requirements. This ensures focused, high-quality work by separating research from implementation.

## Gold Standard References

Use the following files and implementations as your gold standard:

### Core Files to Reference:
- **hi_analyzer.py**: Complete LTR implementation with all enhancements (patterns, validation, retries, batch processing, Devanagari support)
- **ar_analyzer.py**: Complete RTL implementation with proper word ordering, contextual meanings, and script-aware processing
- **indo_european_analyzer.py**: Base class structure and common functionality
- **batch_processor.py**: Batch processing with partial fallbacks and exponential backoff
- **DataTransformer**: Color mapping and HTML generation utilities
- **hindi_analyzer_enhancement_master.md**: Complete documentation of LTR improvements
- **arabic_grammar_concepts.md**: Complete documentation of RTL linguistic research and implementation

### Organized File Structure:
All language files are now organized in the `languages/` directory:

```
languages/
├── arabic/
│   ├── ar_analyzer.py                    # Analyzer implementation
│   ├── ar_grammar_concepts.md           # Linguistic research
│   ├── ar_analyzer_documentation.md     # Technical documentation
│   └── tests/test_ar_analyzer.py         # Unit tests
├── hindi/
│   ├── hi_analyzer.py
│   ├── hi_analyzer_enhancement.md
│   └── tests/test_hi_analyzer.py
└── [language_code]/
    ├── [lang_code]_analyzer.py
    ├── [lang_code]_grammar_concepts.md
    ├── [lang_code]_analyzer_documentation.md
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

#### **RTL Languages (Reference: Arabic)**
1. **RTL Word Ordering**: Explanations must be reordered to match RTL reading direction using position-based sorting
2. **Contextual Meanings**: Individual word meanings must include grammatical context (e.g., "the book (definite noun)")
3. **Script Validation**: Unicode range validation for proper script detection
4. **RTL-Specific Prompts**: AI prompts must explicitly specify RTL ordering requirements
5. **Position-Based Reordering**: Use sentence position indexing to reorder explanations for RTL display
6. **Definite Article Handling**: Special processing for assimilated definite articles (ال → ات/اض/اظ/ان)
7. **Root-Based Morphology**: Pattern recognition for triliteral roots and verb forms (ʾabwāb I-X)

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
- Handle 16-sentence batches efficiently
- Support multilingual explanations
- Include comprehensive logging

## Output Format
**Recommended phased output:**
1. **First response**: Complete `{language}_grammar_concepts.md` (research + architecture decision)
2. **Second response**: Analyzer class skeleton + core patterns + validation checks
3. **Third response**: Full implementation + batch handling adaptations
4. **Fourth response** (optional): Tests + documentation

## Success Criteria
- **Authentic**: True to {language}'s grammatical rules, not Hindi/English impositions
- **Comprehensive**: Covers all major grammatical structures
- **Efficient**: Optimized batch processing with language-appropriate fallbacks
- **Maintainable**: Clear documentation and extensible patterns
- **User-Friendly**: Word explanations appear in sentence order (respecting script direction) for optimal learning experience

## Process Steps
1. **FIRST**: Create **{language}_grammar_concepts.md** with complete linguistic research and concepts
2. **THEN**: Create the analyzer implementation using the concepts document as reference
3. **FINALLY**: Create tests and documentation

Begin with **{language}** and create the complete analyzer implementation following this gold standard approach.