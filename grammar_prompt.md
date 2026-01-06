# 🌍 Language Grammar Analyzer Generator - Master Prompt
# Version: 2026-01-06 (WORD-LEVEL ANALYSIS PIVOT)
# Reference: Hindi Gold Standard (hi_analyzer.py)

## 🚨 CRITICAL ISSUES - IMMEDIATE PRIORITY

### **Issue 4: Character-Level Analysis is Linguistically Incorrect for Chinese** ❌
**Problem:** Current Chinese analyzer treats characters as independent units, but Chinese characters are bound morphemes that only have meaning in word contexts. Western grammatical categories don't fit Chinese linguistics.

**Impact:** Produces pedagogically unsound analysis that misleads learners about Chinese grammar.

**Solution Required:** Pivot to word-level analysis with compounds-first ordering, using Chinese-appropriate grammatical categories.

## 🎯 IMMEDIATE ACTION PLAN

### **Phase 5: Word-Level Analysis Pivot (PASS 3)**
**Goal:** Transform Chinese analyzer from character-level to word-level analysis

**Steps:**
1. **Rewrite AI Prompts:** Change `get_batch_grammar_prompt()` to focus on words, not characters
2. **Update Parsing:** Modify `parse_batch_grammar_response()` for word-level processing
3. **Compounds-First Ordering:** Place compound words higher in explanations for beginner comprehension
4. **Chinese Categories:** Use linguistically appropriate categories (实词/虚词 distinction)
5. **Testing:** Validate word segmentation works reliably before full implementation

**Critical Constraint:** Abandon character-level analysis entirely. Focus on authentic Chinese word-level grammar.

## 📋 DETAILED RECOMMENDATIONS

## 🎯 MISSION
Generate comprehensive grammar analyzers for world languages using **one language at a time** approach:
- **Input**: Just language name (e.g., "Chinese Simplified", "Spanish", "Arabic")
- **Output**: Complete working analyzer with tests and documentation
- **Quality**: Research-backed linguistic accuracy with comprehensive categories
- **Efficiency**: Powerful reference backend reduces AI research workload
- **Scope**: Pass 3 only - grammar analysis with batch processing

## 📚 COMPREHENSIVE REFERENCE BACKEND

### Core Reference Files (Study These First)

**HINDI GOLD STANDARD (hi_analyzer.py):**
```python
# Complete working analyzer with 20+ categories
# Includes hierarchical categorization, batch processing, HTML generation
# Reference for all linguistic patterns and architectural decisions
```

**BASE CLASSES:**
- **BaseGrammarAnalyzer**: Abstract base with HTML generation and batch processing
- **IndoEuropeanAnalyzer**: Family-specific base class with common patterns

**PASS 3 INTEGRATION:**
- **BatchProcessor**: How analyzers integrate with 8-sentence batch processing
- **sentence_generator.py**: Pass 3 logic and analyzer calling patterns

### Linguistic Research Database (AI Can Reference)

**Language Families & Eldest Sisters:**
- **Sino-Tibetan**: Chinese (Simplified/Traditional) → Tibetan, Burmese
- **Indo-European**: Sanskrit → Hindi ✅, Bengali, Persian, English, Spanish, Russian
- **Afro-Asiatic**: Arabic → Hebrew, Amharic, Hausa
- **Niger-Congo**: Swahili → Zulu, Yoruba
- **Austronesian**: Malay → Indonesian, Tagalog, Maori

**Complete 77-Language Inventory by Family:**

| Family | Languages | Eldest Sister | Notes |
|--------|-----------|---------------|-------|
| **1. Sino-Tibetan** (8) | Chinese Simplified ✅, Chinese Traditional ✅, Tibetan, Burmese, Karen, Yi, Bai, Tujia | Chinese (logographic) | Character-based, tonal |
| **2. Indo-European** (23) | English, German, Dutch, Swedish, Danish, Norwegian, Icelandic, Spanish ✅, French, Italian, Portuguese, Romanian, Catalan, Russian ✅, Polish, Czech, Ukrainian, Bulgarian, Serbian, Hindi ✅, Bengali, Persian, Urdu, Punjabi, Gujarati, Marathi, Greek, Lithuanian, Latvian, Irish, Welsh, Breton, Armenian, Albanian | Sanskrit → Hindi, Spanish, Russian | Diverse scripts, inflectional |
| **3. Afro-Asiatic** (12) | Arabic ✅, Hebrew, Amharic, Hausa, Somali, Tigrinya, Berber, Coptic, Maltese | Arabic | Abugida, root-based morphology |
| **4. Niger-Congo** (15) | Swahili ✅, Zulu, Yoruba, Igbo, Hausa, Wolof, Bambara, Ewe, Tswana, Sesotho | Swahili | Tonal, agglutinative |
| **5. Austronesian** (7) | Malay ✅, Indonesian, Tagalog, Maori, Hawaiian, Malagasy, Javanese | Malay | Syllabic, reduplication |
| **6. Turkic** (6) | Turkish ✅, Uzbek, Kazakh, Kyrgyz, Tatar, Azerbaijani | Turkish | Agglutinative, vowel harmony |
| **7. Dravidian** (4) | Tamil ✅, Telugu, Kannada, Malayalam | Tamil | Retroflex consonants, diglossia |
| **8. Japonic** (2) | Japanese ✅, Ryukyuan | Japanese | Mixed script, honorifics |
| **9. Koreanic** (1) | Korean ✅ | Korean | Alphabet + Sino-Korean |
| **10. Tai-Kadai** (3) | Thai ✅, Lao, Zhuang | Thai | Tonal, analytic |
| **11. Hmong-Mien** (2) | Hmong, Mien | - | Tonal, monosyllabic |
| **12. Austroasiatic** (4) | Vietnamese ✅, Khmer, Mon, Khasi | Vietnamese | Monosyllabic, tonal |
| **13. Tibeto-Burman** (6) | Tibetan ✅, Burmese ✅, Karen, Yi ✅, Bai ✅, Tujia ✅ | (Covered in Sino-Tibetan) | Tonal, agglutinative |
| **14. Nubian** (1) | Nobiin | - | Endangered, tonal |
| **15. Basque** (1) | Basque ✅ | Basque (isolate) | Ergative-absolutive |
| **16. Na-Dene** (2) | Navajo, Apache | - | Tonal, complex consonants |
| **17. Eskimo-Aleut** (2) | Inuit, Aleut | - | Polysynthetic |
| **18. Australian Aboriginal** (3) | Pitjantjatjara, Warlpiri, Arrernte | - | Complex phonology |

**PROGRESS TRACKING:**
- ✅ **COMPLETED**: Hindi (Indo-European)
- 🔄 **IN PROGRESS**: Chinese Simplified (Sino-Tibetan)
- ⏳ **PENDING**: 75 languages across 18 families
- 🎯 **NEXT**: Chinese Traditional, then Spanish (Romance eldest sister)

**Script Types & Their Implications:**
- **Logographic** (Chinese): Character-based, no alphabet, tonal
- **Abugida** (Hindi, Arabic): Consonant-vowel combinations
- **Alphabet** (English, Spanish): Letter-based, phonetic
- **Abugida** (Russian, Greek): Complex vowel systems
- **Syllabic** (Japanese): Syllable-based writing

## 🎯 AUTOMATED GENERATION WORKFLOW

### Input Format
```
Generate analyzer for: [LANGUAGE_NAME]
Example: "Chinese Simplified", "Spanish", "Arabic Classical", "Japanese"
```

### AI Research Requirements
**BEFORE generating code, research:**
1. **Grammatical Categories**: Native categories (not English translations)
2. **Morphological Features**: Inflection, derivation, compounding
3. **Syntactic Patterns**: Word order, agreement, case systems
4. **Script Characteristics**: Writing system implications for analysis
5. **Unique Features**: Tones, measure words, honorifics, aspect markers
6. **Family Relationships**: How it relates to eldest sister language

### Category Determination Logic
**AI must determine appropriate categories based on:**
- Language family and script type
- Morphological complexity
- Syntactic features
- Pedagogical needs for language learners
- NOT limited to 20 - use as many as linguistically justified

### Child-First Hierarchical Logic (MANDATORY)
```python
def _map_grammatical_role_to_category(self, grammatical_role: str) -> str:
    """
    CHILDREN-FIRST HIERARCHICAL CATEGORIZATION (CRITICAL PATTERN)
    Order: Specific subtypes → General parent categories
    Prevents concept overlap in multi-category words
    """
    # 1. Language-specific children FIRST (e.g., measure words, aspect particles)
    # 2. Specific subtypes (personal/demonstrative/interrogative pronouns)
    # 3. General parent categories LAST (pronoun, verb, noun, etc.)
```

## 📝 AI PROMPT STRUCTURE FOR ANALYZER GENERATION

You are generating a language analyzer focused ONLY on Pass 3 grammar analysis.

**REFERENCE IMPLEMENTATION (Hindi):**
[Full hi_analyzer.py content with all methods and patterns]

**BASE CLASSES:**
[base_analyzer.py and indo_european_analyzer.py content]

**PASS 3 INTEGRATION:**
[batch_processor.py _parse_batch_response method]
[sentence_generator.py Pass 3 logic only]

**LINGUISTIC RESEARCH DATABASE:**
[Language families, script types, and research guidelines above]

**Generate analyzer for: [LANGUAGE_NAME]**

**Requirements:**
- Research [LANGUAGE_NAME] comprehensively using linguistic principles
- Create appropriate number of grammatical categories (not limited - be linguistically complete)
- Apply child-first hierarchical categorization logic (MANDATORY)
- Include language-specific features and script handling
- Maintain Pass 3 focus with batch processing (8 sentences/API call max)
- Generate complete working Python analyzer with tests
- **CRITICAL:** Support combination words as footer enhancement WITHOUT interfering with individual character/word coloring

**Output Structure:**
1. Complete analyzer Python file ([language_code]_analyzer.py)
2. Unit tests for the analyzer
3. Integration test cases
4. Documentation of linguistic choices and category decisions

**Quality Gates:**
- Must pass all existing test patterns
- Include comprehensive validation methods
- Handle edge cases and AI hallucinations
- Generate Anki-compatible HTML output

## 🎯 LANGUAGE-BY-LANGUAGE EXECUTION

### Current Priority Order
1. **Chinese Simplified** (Sino-Tibetan eldest sister - logographic)
2. **Chinese Traditional** (Sino-Tibetan variant - separate analyzer)
3. **Spanish** (Romance eldest sister - alphabetic)
4. **Arabic** (Afro-Asiatic eldest sister - abugida)
5. **Russian** (Slavic eldest sister - Cyrillic)
6. **Japanese** (Japonic isolate - mixed script)
7. **Continue with remaining 71 languages...**

### Validation Checklist Per Language
- [ ] **Linguistic Research**: Verify native categories, morphological features, and script implications
- [ ] **Category Determination**: Ensure 20+ categories with child-first hierarchical logic
- [ ] **Batch Processing**: Confirm 8-sentence/API call limit and HTML generation
- [ ] **Test Suite**: Generate and run unit tests for analyzer functionality
- [ ] **Anki Compatibility**: Validate HTML output renders correctly in Anki cards
- [ ] **Edge Cases**: Test AI hallucinations, complex sentences, and script-specific features
- [ ] **Integration**: Add to language selector and test end-to-end with sentence generator
- [ ] **Feedback Loop**: Test against real Anki decks and incorporate user/native speaker feedback

## 🚀 REFERENCE BACKEND POWER

**The goal**: Create such comprehensive reference materials that AI can generate production-ready analyzers with minimal research, focusing instead on applying proven patterns to new languages.

**Benefits:**
- **Consistency**: Same architectural patterns across all languages
- **Quality**: Research-backed linguistic decisions
- **Efficiency**: AI focuses on adaptation, not rediscovery
- **Scalability**: Template-based generation for 77 languages

### Feedback and Iteration Loop
- **Testing Against Real Data**: After generation, test analyzers against actual Anki deck creation workflows
- **User Feedback Integration**: Collect feedback from language learners and native speakers
- **Performance Metrics**: Monitor batch processing efficiency and API usage
- **Refinement**: Update this master prompt based on successful patterns and identified gaps
- **Version Control**: Maintain changelog for prompt improvements and analyzer updates

---

**EXECUTION**: Start with Chinese Simplified. Use this prompt with "Chinese Simplified" as input, and AI will generate complete analyzer with tests.

### Core Structure (hi_analyzer.py)
```python
# Hindi Grammar Analyzer
# Auto-generated analyzer for Hindi (हिंदी)
# Language Family: Indo-European
# Script Type: abugida
# Complexity Rating: medium

import re
import json
import logging
from typing import Dict, List, Any, Tuple

from ..family_base_analyzers.indo_european_analyzer import IndoEuropeanAnalyzer
from ..base_analyzer import GrammarAnalysis, LanguageConfig

class HiAnalyzer(IndoEuropeanAnalyzer):
    """Grammar analyzer for Hindi (हिंदी)."""

    VERSION = "1.0"
    LANGUAGE_CODE = "hi"
    LANGUAGE_NAME = "Hindi"

    def __init__(self):
        config = LanguageConfig(
            code="hi",
            name="Hindi",
            native_name="हिंदी",
            family="Indo-European",
            script_type="abugida",
            complexity_rating="medium",
            key_features=['postpositions', 'gender_agreement', 'case_marking', 'verb_conjugation', 'aspect_tense', 'honorifics'],
            supported_complexity_levels=['beginner', 'intermediate', 'advanced']
        )
        super().__init__(config)
```

### 20-Category Grammatical Classification System
```python
# CONTENT WORDS (सार्थक शब्द)
"noun": "#FFAA00"                    # Orange - Things/objects/people/places
"adjective": "#FF44FF"               # Magenta - Describes nouns
"verb": "#44FF44"                    # Green - Actions/states
"adverb": "#44FFFF"                  # Cyan - Modifies verbs/adjectives
"onomatopoeia": "#FFD700"            # Gold - Sound imitation
"ideophone": "#FFD700"               # Gold - Sensory imitation
"echo_word": "#FFD700"               # Gold - Reduplicated forms

# PRONOUNS (सर्वनाम)
"pronoun": "#FF4444"                 # Red - Replaces nouns
"personal_pronoun": "#FF4444"        # Red - I, you, he/she
"demonstrative_pronoun": "#FF4444"   # Red - This, that
"interrogative_pronoun": "#FF4444"   # Red - Who, what
"relative_pronoun": "#FF4444"        # Red - Who/which (relative)
"indefinite_pronoun": "#FF4444"      # Red - Someone, something
"reflexive_pronoun": "#FF4444"       # Red - Own, self

# FUNCTION WORDS (असार्थक शब्द)
"numeral_adjective": "#FFFF44"       # Yellow - Numbers, ordinals
"auxiliary_verb": "#44FF44"          # Green - Support main verbs
"postposition": "#4444FF"            # Blue - Relationships (postpositions)
"conjunction": "#888888"             # Gray - Connectors
"interjection": "#FFD700"            # Gold - Emotions/exclamations
"particle": "#AA44FF"                # Purple - Emphasis/nuance
"other": "#AAAAAA"                   # Light gray - Other
```

### Hierarchical Categorization (Children-First Logic)
```python
def _map_grammatical_role_to_category(self, grammatical_role: str) -> str:
    """Map grammatical role descriptions to color category names using Hindi grammar rules

    CHILDREN-FIRST HIERARCHICAL CATEGORIZATION (Phase 5.7)
    Order matters: Check specific/sub-categories first, then general/parent categories
    This prevents concept overlap in multi-category words
    """
    # Preprocess: Clean up common AI mistakes and normalize the input
    role_lower = grammatical_role.lower().strip()

    # CRITICAL HIERARCHY: Children-first categorization to prevent overlap
    # Order: specific subtypes → general parent categories

    # 1. Auxiliary verbs BEFORE main verbs (auxiliary_verb → verb)
    if any(keyword in role_lower for keyword in ['सहायक क्रिया', 'auxiliary_verb', 'auxiliary']):
        return 'auxiliary_verb'

    # 2. Specific pronoun subtypes BEFORE general pronoun
    if any(keyword in role_lower for keyword in ['personal_pronoun', 'personal']):
        return 'personal_pronoun'
    # ... [other specific pronoun types]

    # 3. Postpositions BEFORE prepositions (postposition → preposition)
    if any(keyword in role_lower for keyword in ['postposition', 'postpositional']):
        return 'postposition'

    # 4. Particles BEFORE conjunctions (particle → conjunction)
    if any(keyword in role_lower for keyword in ['particle', 'emphasis_particle']):
        return 'particle'

    # 5. Ideophones BEFORE interjections (ideophone → interjection)
    if any(keyword in role_lower for keyword in ['ideophone']):
        return 'ideophone'

    # PARENT CATEGORIES (checked after all children to prevent overlap)
    if any(keyword in role_lower for keyword in ['pronoun']):
        return 'pronoun'
    elif any(keyword in role_lower for keyword in ['verb']):
        return 'verb'
    # ... [other parent categories]
```

### Batch Processing Prompt Structure
```python
def get_batch_grammar_prompt(self, complexity: str, sentences: List[str], target_word: str, native_language: str = "English") -> str:
    """Generate Hindi-specific AI prompt for batch grammar analysis"""
    sentences_text = "\n".join(f"{i+1}. {sentence}" for i, sentence in enumerate(sentences))

    return f"""Analyze the grammar of these Hindi sentences and provide detailed word-by-word analysis for each one.

Target word: "{target_word}"
Language: Hindi
Complexity level: {complexity}
Analysis should be in {native_language}

Sentences to analyze:
{sentences_text}

For EACH word in EVERY sentence, provide:
- word: the exact word as it appears in the sentence
- individual_meaning: the English translation/meaning of this specific word (MANDATORY - do not leave empty)
- grammatical_role: EXACTLY ONE category from this list: noun, adjective, verb, adverb, pronoun, postposition, conjunction, particle, auxiliary_verb, interjection, other

Additionally, identify 1-2 key compound words/phrases per sentence:
- word_combinations: array of compounds with text, combined_meaning, grammatical_role

CRITICAL REQUIREMENTS:
- individual_meaning MUST be provided for EVERY word
- grammatical_role MUST be EXACTLY from the allowed list (one word only)
- word_combinations are OPTIONAL but enhance learning when present
- COMBINATION COLORS MUST NOT INTERFERE WITH INDIVIDUAL WORD COLORS
- Examples of correct grammatical_role:
  - "noun" (not "common noun" or "n noun")
  - "postposition" (not "po ostposition" or "postpositional")
  - "verb" (not "v verb" or "main verb")

Return JSON in this exact format:
{{
  "batch_results": [
    {{
      "sentence_index": 1,
      "sentence": "{sentences[0] if sentences else ''}",
      "words": [
        {{
          "word": "रबर",
          "individual_meaning": "rubber",
          "grammatical_role": "noun"
        }}
      ],
      "word_combinations": [
        {{
          "text": "हमारे घर",
          "combined_meaning": "our house",
          "grammatical_role": "compound_noun"
        }}
      ],
      "explanations": {{
        "sentence_structure": "Brief grammatical summary of the sentence",
        "complexity_notes": "Notes about grammatical structures used at {complexity} level"
      }}
    }}
  ]
}}

IMPORTANT:
- Analyze ALL {len(sentences)} sentences
- EVERY word MUST have individual_meaning (English translation)
- grammatical_role MUST be EXACTLY from the allowed list (one word only)
- Return ONLY the JSON object, no additional text
"""
```

## 🏛️ BASE CLASSES REFERENCE

### BaseGrammarAnalyzer (base_analyzer.py)
```python
class BaseGrammarAnalyzer(abc.ABC):
    """Abstract base class for language-specific grammar analyzers."""

    def get_batch_grammar_prompt(self, complexity: str, sentences: List[str], target_word: str, native_language: str = "English") -> str:
        """Generate language-specific AI prompt for batch grammar analysis."""

    def parse_batch_grammar_response(self, ai_response: str, sentences: List[str], complexity: str, native_language: str = "English") -> List[Dict[str, Any]]:
        """Parse batch AI response into list of standardized grammar analysis formats."""

    def _generate_html_output(self, parsed_data: Dict[str, Any], sentence: str, complexity: str) -> str:
        """Generate HTML output for Anki cards with color-coded elements"""
        colors = self.get_color_scheme(complexity)
        elements = parsed_data.get('elements', {})

        # Process each element type and color the words
        all_words = []
        for element_type, word_list in elements.items():
            color = colors.get(element_type, '#000000')
            for word_data in word_list:
                word = word_data.get('word', '').strip()
                if word:
                    all_words.append((word, element_type))

        # Sort by word length (longest first) to avoid partial matches
        all_words.sort(key=lambda x: len(x[0]), reverse=True)

        # Replace each word with colored version
        result = sentence
        for word, element_type in all_words:
            colored_span = f'<span class="grammar-{element_type}">{word}</span>'
            import re
            words_in_sentence = re.findall(r'\S+', result)
            for i, w in enumerate(words_in_sentence):
                if w == word:
                    words_in_sentence[i] = colored_span
            result = ' '.join(words_in_sentence)

        return result
```

### IndoEuropeanAnalyzer (indo_european_analyzer.py)
```python
class IndoEuropeanAnalyzer(BaseGrammarAnalyzer):
    """Base analyzer class for Indo-European languages."""

    def _get_beginner_prompt(self, sentence: str, target_word: str) -> str:
        """Generate beginner-level grammar analysis prompt for Indo-European languages"""
        base_prompt = f"""Analyze this ENTIRE {self.language_name} sentence WORD BY WORD: {sentence}

For EACH AND EVERY INDIVIDUAL WORD in the sentence, provide:
- Its individual meaning and pronunciation
- Its grammatical role and function in this context
- Gender/number/case information (if applicable)
- How it relates to other words in the sentence
- Why it's important for learners

Return a JSON object with detailed word analysis for ALL words in the sentence:
{{
  "words": [
    {{
      "word": "example_word",
      "individual_meaning": "translation/meaning",
      "pronunciation": "IPA_phonetic",
      "grammatical_role": "noun/verb/adjective/etc",
      "morphological_info": "gender/case/tense info",
      "syntactic_function": "subject/object/modifier",
      "importance": "learning significance"
    }}
  ]
}}
"""
        return base_prompt
```

## 🔄 PASS 3 INTEGRATION REFERENCE

### BatchProcessor._parse_batch_response (batch_processor.py)
```python
def _parse_batch_response(self, response_text: str, sentences: List[str], analyzer,
                        language: str, complexity_level: str, language_code: str,
                        native_language: str) -> List[Dict[str, Any]]:
    """Parse the batch response and convert to expected format."""
    try:
        if analyzer and hasattr(analyzer, 'parse_batch_grammar_response'):
            # Use analyzer's batch parsing method
            parsed_results = analyzer.parse_batch_grammar_response(response_text, sentences, complexity_level, native_language)

            # Generate HTML for each result using the analyzer's _generate_html_output method
            results_with_html = []
            for i, parsed_data in enumerate(parsed_results):
                sentence = parsed_data.get("sentence", sentences[i] if i < len(sentences) else "")

                # Generate colored sentence HTML
                if hasattr(analyzer, '_generate_html_output'):
                    colored_sentence = analyzer._generate_html_output(parsed_data, sentence, complexity_level)
                else:
                    colored_sentence = sentence

                # Ensure word_explanations are in the expected format
                word_explanations = parsed_data.get("word_explanations", [])

                # Get grammar summary
                grammar_summary = parsed_data.get("explanations", {}).get("sentence_structure",
                    f"This sentence uses {language_code} grammatical structures appropriate for {complexity_level} learners.")

                results_with_html.append({
                    "colored_sentence": colored_sentence,
                    "word_explanations": word_explanations,
                    "grammar_summary": grammar_summary,
                })

            return results_with_html
```

### sentence_generator.py Pass 3 Logic
```python
# PASS 3: Batch grammar analysis and coloring for ALL sentences
logger.info(f"PASS 3: Batch analyzing grammar for {len(final_sentences)} sentences...")
try:
    # Extract sentences for batch processing
    sentences_to_analyze = [s["sentence"] for s in final_sentences if s["sentence"]]

    if sentences_to_analyze:
        # Batch analyze grammar for all sentences at once
        batch_grammar_results = _batch_analyze_grammar_and_color(
            sentences=sentences_to_analyze,
            word=word,
            language=language,
            groq_api_key=groq_api_key,
            complexity_level=difficulty,
            native_language=native_language,
        )

        # Update final_sentences with batch results
        for i, grammar_result in enumerate(batch_grammar_results):
            if i < len(final_sentences):
                # Handle different analyzer output formats
                colored_sentence = grammar_result.get("colored_sentence", final_sentences[i]["sentence"])
                grammar_summary = grammar_result.get("grammar_summary", "")

                # Check if analyzer already provided word_explanations (preferred)
                if "word_explanations" in grammar_result and grammar_result["word_explanations"]:
                    word_explanations = grammar_result["word_explanations"]
                else:
                    # Fallback to conversion function
                    word_explanations = _convert_analyzer_output_to_explanations(grammar_result, language)

                final_sentences[i].update({
                    "colored_sentence": colored_sentence,
                    "word_explanations": word_explanations,
                    "grammar_summary": grammar_summary,
                })
```

## 🎯 GENERATION REQUIREMENTS FOR CHINESE ANALYZER

### Language Configuration
```python
config = LanguageConfig(
    code="zh",
    name="Chinese",
    native_name="中文",
    family="Sino-Tibetan",           # Eldest sister for Sino-Tibetan family
    script_type="logographic",       # Chinese characters (but word-level analysis)
    complexity_rating="high",        # Due to word segmentation and tones
    key_features=['word_segmentation', 'compounds_first', 'chinese_categories', 'aspect_system', 'topic_comment'],
    supported_complexity_levels=['beginner', 'intermediate', 'advanced']
)
```

### Chinese-Appropriate Grammatical Categories (实词/虚词)
```python
# CONTENT WORDS (实词 / Shící) - Independent meaning
"noun": "#FFAA00"                    # Orange - People/places/things/concepts
"verb": "#44FF44"                    # Green - Actions/states/changes
"adjective": "#FF44FF"               # Magenta - Qualities/descriptions
"numeral": "#FFFF44"                 # Yellow - Numbers/quantities
"measure_word": "#FFD700"            # Gold - Classifiers (个、只、本)
"pronoun": "#FF4444"                 # Red - Replaces nouns
"time_word": "#FFA500"               # Orange-red - Time expressions
"locative_word": "#FF8C00"           # Dark orange - Location/direction

# FUNCTION WORDS (虚词 / Xūcí) - Structural/grammatical
"aspect_particle": "#8A2BE2"         # Purple - Aspect markers (了、着、过)
"modal_particle": "#DA70D6"          # Plum - Tone/mood particles (吗、呢、吧)
"structural_particle": "#9013FE"     # Violet - Structural particles (的、地、得)
"preposition": "#4444FF"             # Blue - Prepositions/coverbs
"conjunction": "#888888"             # Gray - Connectors
"adverb": "#44FFFF"                  # Cyan - Modifies verbs/adjectives
"interjection": "#FFD700"            # Gold - Emotions/exclamations
"onomatopoeia": "#FFD700"            # Gold - Sound imitation
```

### Word-Level Analysis Architecture
```python
# PRIMARY: Word segmentation first
# SECONDARY: Character breakdowns as supplementary
# ORDERING: Compounds appear higher than individual characters

def get_batch_grammar_prompt(self, complexity: str, sentences: List[str], target_word: str, native_language: str = "English") -> str:
    return f"""
    Analyze Chinese sentences at the WORD level, not character level.
    
    For each sentence:
    1. Segment into words (compounds first)
    2. Analyze grammatical role using Chinese categories
    3. Provide compounds with higher priority in explanations
    
    Return word-level analysis, not character-by-character breakdown.
    """
```

## 📝 AI PROMPT STRUCTURE FOR ANALYZER GENERATION

You are generating a language analyzer focused ONLY on Pass 3 grammar analysis.

**REFERENCE IMPLEMENTATION (Hindi):**
[Full hi_analyzer.py content]

**BASE CLASSES:**
[base_analyzer.py and indo_european_analyzer.py content]

**PASS 3 INTEGRATION:**
[batch_processor.py _parse_batch_response method]
[sentence_generator.py Pass 3 logic only]

**Generate analyzer for: Chinese (zh)**

**Requirements:**
- 20 grammatical categories minimum (match Hindi structure but adapt for Chinese)
- Batch processing support (8 sentences/API call max)
- ENUM-constrained AI responses
- Context-aware categorization
- HTML generation for Anki compatibility
- Single responsibility: ONLY grammar analysis for Pass 3

**Chinese-Specific Adaptations:**
- **Logographic Script Handling**: Analyze individual characters (e.g., 我/wǒ = "I", 们/men = plural marker) rather than words
- **Tone System Integration**: Consider tonal changes in grammatical analysis (e.g., 不/bù as negation vs. 好/hǎo as adjective)
- **Measure Word System**: Classifiers like 个/gè (general), 本/běn (books), 只/zhī (animals) as separate category
- **Topic-Comment Structure**: Handle sentence patterns like "Topic + Comment" (e.g., "我喜欢苹果" = "As for me, I like apples")
- **Aspect Particles**: Distinguish perfective 了/le, durative 着/zhe, experiential 过/guo
- **Character Etymology**: Consider radical meanings for compound words (e.g., 妈妈/māma = mother, from 女/nǚ + 马/mǎ)
- **Combination Words**: Identify 2-3 character compounds (e.g., "我们" as "we") and add to Grammar Explanations WITHOUT interfering with individual character coloring

**Example Chinese Analysis:**
- Sentence: "我在图书馆学习。" (Wǒ zài túshūguǎn xuéxí.)
- Expected Categories: personal_pronoun (我), coverb (在), noun (图), noun (书), noun (馆), verb (学), verb (习)
- Grammar Explanations Output:
  ```
  我 (personal_pronoun): I/me (refers to speaker/listener/third person)
  在 (coverb): at/in (verb used like preposition)
  图 (noun): diagram/picture (person/place/thing/object)
  书 (noun): book (person/place/thing/object)
  馆 (noun): hall/building (person/place/thing/object)
  学 (verb): to study/learn (action/state/change)
  习 (verb): to practice (action/state/change)
  图书馆 (noun): library (compound noun)
  学习 (verb): to study (compound verb)
  ```
- HTML Output: Color-code each element for Anki visualization

**Output:** Complete Chinese analyzer Python file (zh_analyzer.py)

## 🎯 NEXT STEPS AFTER CHINESE

1. **Validate Chinese analyzer** against existing test patterns
2. **Apply same methodology** to Spanish (Romance family eldest sister)
3. **Expand to other families** using eldest sister logic:
   - Germanic: English → German, Dutch, Swedish
   - Romance: Spanish → French, Italian, Portuguese
   - Slavic: Russian → Polish, Czech, Ukrainian
   - etc.

---

**REMINDER**: Use Hindi analyzer as gold standard template, adapt categories and logic for Chinese linguistic features, maintain Pass 3 focus only.

**COMBINATION WORDS REQUIREMENT**: All analyzers must support compound word recognition as footer enhancement. Combination styling/colors MUST NOT interfere with individual character/word coloring. Process combinations separately and append as neutral-styled footer.</content>
<parameter name="filePath">d:\Language Learning\LanguagLearning\grammar_prompt.md