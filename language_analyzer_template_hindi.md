# 🌍 Language Analyzer Template: Hindi Example
# Complete Specification for Automated Language Analyzer Generation
# Version: 2026-01-17 (Hindi Reference Implementation - Post-Fixes)

## 🎯 OVERVIEW

This document provides the **complete detailed specification** needed to generate a production-ready language analyzer. Using **Hindi** as the reference example, it shows exactly what linguistic information must be provided for each new language.

**Template Structure:**
1. Language Configuration
2. Grammatical Categories (15-25 categories)
3. Hierarchical Mapping Logic
4. Language-Specific Features
5. AI Prompt Constraints
6. Complexity Rating Justification
7. Script Type Implications
8. Example Sentence Analysis
9. **NEW:** Recent Improvements and Fixes

---

## 🔧 RECENT IMPROVEMENTS AND FIXES (2026-01-17)

### **IPA Romanization Support for Indic Languages**
**Problem Solved:** IPA validation was rejecting romanized Hindi transliterations, leaving IPA fields blank.

**Solution Implemented:**
- Added romanization support for Indic languages (Hindi, Bengali, Gujarati, etc.)
- Enhanced `validate_ipa_output()` to accept romanized text with diacritics
- Updated AI prompts to request romanization instead of strict IPA for learner-friendly languages

**Technical Details:**
```python
# Romanization allowed languages
romanization_allowed_languages = ['hi', 'ar', 'fa', 'ur', 'bn', 'pa', 'gu', 'or', 'ta', 'te', 'kn', 'ml', 'si']

# Enhanced validation for romanization
romanization_diacritics = 'āēīōūǖǎěǐǒǔǚñḍṭṅṇṃśṣḥḷḻṛṝṁ'
romanization_pattern = r'^[a-zA-Z\s\'' + romanization_diacritics + r'.,;:!?]+$'

if language in romanization_allowed_languages:
    if re.match(romanization_pattern, text.strip()):
        return True, text  # Accept romanized IPA
```

**Result:** Hindi sentences now display romanized IPA like "jātrā mēṁ upyōg hōnē vālī cīj." instead of blank fields.

### **Grammar Analysis JSON Truncation Fix**
**Problem Solved:** AI responses were truncated due to insufficient max_tokens, causing JSON parsing failures and generic fallback explanations.

**Solution Implemented:**
- Increased max_tokens from 1000 to 2000 in `hi_analyzer.py`
- Ensures complete JSON responses for 8-sentence batch processing
- Prevents fallback to generic "a word that describes a noun" explanations

**Technical Details:**
```python
# In hi_analyzer.py _call_ai method
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": prompt}],
    max_tokens=2000,  # Increased from 1000
    temperature=0.1
)
```

**Result:** Grammar analysis now provides detailed meanings like "यात्रा (noun): travel or journey" instead of generic descriptions.

---

## 📋 LANGUAGE CONFIGURATION

```python
LanguageConfig(
    code="hi",                           # ISO 639-1 code
    name="Hindi",                       # English name
    native_name="हिंदी",                # Native script name
    family="Indo-European",             # Language family
    script_type="abugida",              # Writing system type
    complexity_rating="medium",         # Morphological complexity
    key_features=[                      # 4-6 key linguistic features
        'postpositions',                # Word order: Subject-Object-Verb
        'gender_agreement',             # Masculine/feminine noun genders
        'case_marking',                 # Nominative/accusative/dative cases
        'verb_conjugation',             # Tense/person/number agreement
        'aspect_tense',                 # Perfective/imperfective aspects
        'honorifics'                    # Formal/informal verb forms
    ],
    supported_complexity_levels=["beginner", "intermediate", "advanced"]
)
```

---

## 📚 GRAMMATICAL CATEGORIES (20 Categories)

### Content Words (सार्थक शब्द / Real Words)
| Category | Color | Description | Examples |
|----------|-------|-------------|----------|
| `noun` | `#FFAA00` | People, places, things, concepts | रबर (rubber), किताब (book), पानी (water) |
| `adjective` | `#FF44FF` | Describes nouns (quality, size, color) | अच्छा (good), बड़ा (big), लाल (red) |
| `verb` | `#44FF44` | Actions, states, processes | करना (do), जाना (go), खाना (eat) |
| `adverb` | `#44FFFF` | Modifies verbs/adjectives (how, when, where) | जल्दी (quickly), कल (yesterday), यहां (here) |
| `onomatopoeia` | `#FFD700` | Sound imitation words | धड़ाम (thud), चहचह (chirp) |
| `ideophone` | `#FFD700` | Sensory imitation | चमचम (shine), धीरे-धीरे (slowly) |
| `echo_word` | `#FFD700` | Reduplicated forms | खाना-पीना (food-drink), उठना-बैठना (sitting-standing) |

### Pronouns (सर्वनाम / Pronouns)
| Category | Color | Description | Examples |
|----------|-------|-------------|----------|
| `pronoun` | `#FF4444` | General pronoun category | वह (he/she/it), ये (this/these) |
| `personal_pronoun` | `#FF4444` | I, you, he/she/it | मैं (I), तुम (you), वह (he/she) |
| `demonstrative_pronoun` | `#FF4444` | This, that, these, those | यह (this), वह (that), ये (these) |
| `interrogative_pronoun` | `#FF4444` | Who, what, which | कौन (who), क्या (what), कौन-सा (which) |
| `relative_pronoun` | `#FF4444` | Who, which, that (in relative clauses) | जो (who/which), जिसे (whom) |
| `indefinite_pronoun` | `#FF4444` | Someone, something, anyone | कोई (someone), कुछ (something) |
| `reflexive_pronoun` | `#FF4444` | Myself, yourself, himself | खुद (self), अपना (own) |

### Function Words (असार्थक शब्द / Function Words)
| Category | Color | Description | Examples |
|----------|-------|-------------|----------|
| `numeral_adjective` | `#FFFF44` | Numbers used as adjectives | एक (one), दो (two), पहला (first) |
| `auxiliary_verb` | `#44FF44` | Support main verbs (be, have, do) | है (is), था (was), होगा (will be) |
| `postposition` | `#4444FF` | Case markers, relationships | का (of), को (to), से (from) |
| `conjunction` | `#888888` | Connectors (and, but, or) | और (and), पर (but), या (or) |
| `interjection` | `#FFD700` | Emotions, exclamations | अरे (hey), हाय (alas), वाह (wow) |
| `particle` | `#AA44FF` | Emphasis, nuance, negation | भी (also), तो (then), नहीं (not) |
| `other` | `#AAAAAA` | Unclassified words | Foreign words, proper names |

---

## 🔄 HIERARCHICAL MAPPING LOGIC (CRITICAL)

### Core Principle: CHILDREN-FIRST Categorization
**Order matters!** Check specific subtypes BEFORE general parent categories to prevent overlap.

```python
def _map_grammatical_role_to_category(self, grammatical_role: str) -> str:
    """Map AI responses to categories using CHILDREN-FIRST HIERARCHY"""

    role_lower = grammatical_role.lower().strip()

    # STEP 1: PREPROCESSING - Fix AI hallucinations
    if role_lower == "po ostposition":
        role_lower = "postposition"
    elif role_lower == "v verb":
        role_lower = "verb"
    elif role_lower == "aux auxiliary_verb":
        role_lower = "auxiliary_verb"

    # STEP 2: LANGUAGE-SPECIFIC CHILDREN (Highest Priority)
    # 1. Auxiliary verbs BEFORE main verbs
    if any(keyword in role_lower for keyword in [
        'सहायक क्रिया', 'sahāyak kriyā', 'auxiliary_verb', 'auxiliary verb', 'auxiliary'
    ]):
        return 'auxiliary_verb'

    # STEP 3: PRONOUN SUBTYPES (Before general pronoun)
    if any(keyword in role_lower for keyword in [
        'व्यक्तिवाचक सर्वनाम', 'vyaktivācak sarvanām', 'personal_pronoun', 'personal pronoun', 'personal'
    ]):
        return 'personal_pronoun'

    elif any(keyword in role_lower for keyword in [
        'निदर्शक सर्वनाम', 'nidarśak sarvanām', 'demonstrative_pronoun', 'demonstrative pronoun', 'demonstrative'
    ]):
        return 'demonstrative_pronoun'

    elif any(keyword in role_lower for keyword in [
        'प्रश्नवाचक सर्वनाम', 'praśnavācak sarvanām', 'interrogative_pronoun', 'interrogative pronoun', 'interrogative'
    ]):
        return 'interrogative_pronoun'

    elif any(keyword in role_lower for keyword in [
        'संबंधवाचक सर्वनाम', 'sambandhavācak sarvanām', 'relative_pronoun', 'relative pronoun', 'relative'
    ]):
        return 'relative_pronoun'

    elif any(keyword in role_lower for keyword in [
        'अनिश्चयवाचक सर्वनाम', 'aniścayavācak sarvanām', 'indefinite_pronoun', 'indefinite pronoun', 'indefinite'
    ]):
        return 'indefinite_pronoun'

    elif any(keyword in role_lower for keyword in [
        'निजवाचक सर्वनाम', 'nijavācak sarvanām', 'reflexive_pronoun', 'reflexive pronoun', 'reflexive'
    ]):
        return 'reflexive_pronoun'

    # STEP 4: FUNCTION WORD SUBTYPES
    # 3. Postpositions BEFORE prepositions
    if any(keyword in role_lower for keyword in [
        'संबंधबोधक', 'sambandh bodhak', 'postposition', 'postpositional'
    ]):
        return 'postposition'

    # 4. Particles BEFORE conjunctions
    if any(keyword in role_lower for keyword in [
        'निपात', 'nipāt', 'particle', 'emphasis_particle', 'modal_particle'
    ]):
        return 'particle'

    # STEP 5: SPECIAL CATEGORIES
    # 5. Ideophones BEFORE interjections
    if any(keyword in role_lower for keyword in [
        'अनुकरण शब्द', 'anukaraṇ śabd', 'ideophone'
    ]):
        return 'ideophone'

    # 6. Echo words BEFORE general categories
    if any(keyword in role_lower for keyword in [
        'दोहराव शब्द', 'doharāv śabd', 'echo_word', 'echo'
    ]):
        return 'echo_word'

    # 7. Onomatopoeia BEFORE interjections
    if any(keyword in role_lower for keyword in [
        'ध्वन्यात्मक शब्द', 'dhvanyātmak śabd', 'onomatopoeia', 'onomatopoeic'
    ]):
        return 'onomatopoeia'

    # 8. Numeral adjectives BEFORE general adjectives
    if any(keyword in role_lower for keyword in [
        'संख्यावाचक विशेषण', 'saṅkhyāvācak viśeṣaṇ', 'numeral_adjective', 'numeral adjective', 'numeral'
    ]):
        return 'numeral_adjective'

    # STEP 6: PARENT CATEGORIES (Lowest Priority - Checked Last)
    if any(keyword in role_lower for keyword in ['सर्वनाम', 'sarvanām', 'pronoun']):
        return 'pronoun'

    if any(keyword in role_lower for keyword in ['क्रिया', 'kriyā', 'verb', 'main_verb']):
        return 'verb'

    if any(keyword in role_lower for keyword in ['विशेषण', 'viśeṣaṇ', 'adjective', 'descriptive_adjective']):
        return 'adjective'

    if any(keyword in role_lower for keyword in ['संज्ञा', 'saṅgyā', 'noun', 'proper_noun', 'common_noun']):
        return 'noun'

    if any(keyword in role_lower for keyword in ['क्रिया विशेषण', 'kriyā viśeṣaṇ', 'adverb', 'manner_adverb', 'time_adverb', 'place_adverb']):
        return 'adverb'

    # AI-generated roles that need mapping
    if 'subject' in role_lower:
        return 'pronoun'  # Subjects are typically pronouns in Hindi
    elif 'negation' in role_lower or 'determiner' in role_lower:
        return 'other'  # Negation particles and determiners

    return 'other'  # Default fallback
```

### Why This Hierarchy Matters

**Example:** Word "होना" (to be)
- As auxiliary verb: "है" (is) → `auxiliary_verb` (green)
- As main verb: "होना" (become) → `verb` (green, but different shade)

**Without hierarchy:** AI says "verb" → goes to general `verb` category
**With hierarchy:** Check `auxiliary_verb` first → correctly categorized

---

## 🎯 LANGUAGE-SPECIFIC FEATURES (6 Key Features)

### 1. Postpositions (संबंधबोधक / Case Markers)
- **Description**: Hindi uses postpositions instead of prepositions
- **Examples**: का (of), को (to), से (from), में (in), पर (on)
- **Impact**: Changes word order: "book of me" instead of "my book"
- **Teaching Challenge**: English learners struggle with SOV word order

### 2. Gender Agreement (लिंग सर्वसम्मति)
- **Description**: Nouns have masculine/feminine gender, adjectives agree
- **Examples**: अच्छा लड़का (good boy-M), अच्छी लड़की (good girl-F)
- **Impact**: Adjectives change form based on noun gender
- **Teaching Challenge**: No gender in English, complex agreement rules

### 3. Case Marking (कारक चिह्न)
- **Description**: Nouns marked for grammatical function (nominative, accusative, etc.)
- **Examples**: लड़का (boy-NOM), लड़के को (boy-ACC), लड़के से (boy-ABL)
- **Impact**: Postpositions indicate case relationships
- **Teaching Challenge**: English has minimal case marking

### 4. Verb Conjugation (क्रिया रूप)
- **Description**: Verbs conjugate for tense, aspect, person, number, gender
- **Examples**: करता है (does-M), करती है (does-F), करते हैं (do-plural)
- **Impact**: Rich morphological system with many forms
- **Teaching Challenge**: Regular and irregular verb patterns

### 5. Aspect-Tense System (काल पक्ष)
- **Description**: Complex perfective/imperfective aspects with tense
- **Examples**: कर रहा है (is doing - imperfective), कर दिया (did - perfective)
- **Impact**: Expresses completion vs ongoing action
- **Teaching Challenge**: English has simpler tense system

### 6. Honorifics (सम्मान सूचक)
- **Description**: Formal/informal verb forms based on social status
- **Examples**: जाता है (goes-formal), जाता (goes-informal)
- **Impact**: Social politeness affects grammar
- **Teaching Challenge**: Context-dependent formality levels

---

## 🤖 AI PROMPT CONSTRAINTS

### Batch Processing Prompt Structure
```python
grammatical_role: EXACTLY ONE category from this list:
noun, adjective, verb, adverb, pronoun, personal_pronoun, demonstrative_pronoun,
interrogative_pronoun, relative_pronoun, indefinite_pronoun, reflexive_pronoun,
postposition, conjunction, particle, auxiliary_verb, interjection, numeral_adjective,
onomatopoeia, ideophone, echo_word, other

CRITICAL REQUIREMENTS:
- grammatical_role MUST be EXACTLY one word from the allowed list
- Examples: "noun", "verb", "postposition" (not "common noun", "main verb")
- No prefixes, suffixes, or spaces in category names
```

### AI Response Format
```json
{
  "batch_results": [
    {
      "sentence_index": 1,
      "sentence": "मैं किताब पढ़ रहा हूं",
      "words": [
        {"word": "मैं", "individual_meaning": "I", "grammatical_role": "personal_pronoun"},
        {"word": "किताब", "individual_meaning": "book", "grammatical_role": "noun"},
        {"word": "पढ़", "individual_meaning": "read", "grammatical_role": "verb"},
        {"word": "रहा", "individual_meaning": "am (continuous)", "grammatical_role": "auxiliary_verb"},
        {"word": "हूं", "individual_meaning": "am", "grammatical_role": "auxiliary_verb"}
      ]
    }
  ]
}
```

---

## 📊 COMPLEXITY RATING JUSTIFICATION

### Why "Medium" Complexity?

**Morphological Complexity:**
- **High**: Complex case system (nominative, accusative, dative, ablative, locative)
- **High**: Gender agreement affects adjectives, verbs, pronouns
- **High**: Verb conjugation (tense × aspect × person × number × gender)

**Script Complexity:**
- **Medium**: Abugida script (Devanagari) - consonant-vowel combinations
- **Medium**: Diacritics for vowel modifications (matras)
- **Low**: Phonetic spelling (what you see is what you get)

**Syntactic Complexity:**
- **High**: Subject-Object-Verb word order (different from English SVO)
- **High**: Postpositional system (relationships marked after nouns)
- **Medium**: Complex aspect-tense system

**Overall Rating: MEDIUM**
- More complex than English (no cases/gender/agreement)
- Less complex than highly inflected languages (Finnish, Arabic, Russian)
- Balanced difficulty for language learners

---

## 🔤 SCRIPT TYPE IMPLICATIONS

### Abugida Script (Devanagari)
**Characteristics:**
- **Consonant-Vowel Syllables**: Each consonant has an inherent vowel (usually 'a')
- **Vowel Diacritics**: Matras modify the inherent vowel (ा, ि, ी, ु, ू, etc.)
- **No Standalone Vowels**: Vowels at word start have special forms (अ, आ, इ, etc.)

**Analysis Implications:**
- **Syllable-Based**: Words analyzed as consonant-vowel units
- **Implicit Vowels**: Unmarked consonants have inherent 'a' sound
- **Visual Parsing**: Script shows morphological boundaries clearly
- **Teaching Aid**: Script reinforces grammatical concepts

**Example Analysis:**
```
दे - द् (consonant) + े (vowel diacritic) = "de" (give)
व - व् (consonant) + inherent अ = "va" (or)
```

---

## 📝 EXAMPLE SENTENCE ANALYSIS

### Sample Sentence: "मैं अच्छी किताब पढ़ रहा हूं"
**Translation:** "I am reading a good book"

### Word-by-Word Breakdown:

| Word | Devanagari | Meaning | Category | Color | Explanation |
|------|------------|---------|----------|-------|-------------|
| मैं | मैं | I | `personal_pronoun` | 🔴 Red | First person singular pronoun |
| अच्छी | अच्छी | good (F) | `adjective` | 🟣 Magenta | Adjective agreeing with feminine noun |
| किताब | किताब | book | `noun` | 🟠 Orange | Common noun, feminine gender |
| पढ़ | पढ़ | read | `verb` | 🟢 Green | Main verb in present continuous |
| रहा | रहा | am (cont.) | `auxiliary_verb` | 🟢 Green | Auxiliary for continuous aspect |
| हूं | हूं | am | `auxiliary_verb` | 🟢 Green | Auxiliary verb "to be" |

### Hierarchical Categorization Demonstration:

1. **Check auxiliary verbs first**: "रहा", "हूं" → `auxiliary_verb` ✓
2. **Check pronoun subtypes**: "मैं" → `personal_pronoun` ✓
3. **Check parent categories**: "किताब" → `noun`, "अच्छी" → `adjective`, "पढ़" → `verb`

### HTML Output Structure:
```html
<span class="grammar-personal_pronoun">मैं</span>
<span class="grammar-adjective">अच्छी</span>
<span class="grammar-noun">किताब</span>
<span class="grammar-verb">पढ़</span>
<span class="grammar-auxiliary_verb">रहा</span>
<span class="grammar-auxiliary_verb">हूं</span>
```

### Color-Coded Result:
**🔴मैं** **🟣अच्छी** **🟠किताब** **🟢पढ़** **🟢रहा** **🟢हूं**

---

## 🚀 IMPLEMENTATION CHECKLIST

### Pre-Generation Requirements
- [x] Language configuration defined
- [x] 20 grammatical categories specified
- [x] Hierarchical mapping logic documented
- [x] Language-specific features identified
- [x] AI prompt constraints defined
- [x] Complexity rating justified
- [x] Script implications analyzed
- [x] Example sentence analyzed

### Post-Generation Validation
- [ ] Analyzer loads without errors
- [ ] All tests pass (configuration, prompts, colors, validation)
- [ ] Batch processing works (8 sentences/API call)
- [ ] HTML output renders correctly in Anki
- [ ] Integration with sentence generator successful
- [ ] End-to-end testing with real Anki decks

---

## 📋 TEMPLATE FOR NEW LANGUAGES

**Copy this structure for each new language:**

```
LANGUAGE: [Language Name]
FAMILY: [Language Family]
SCRIPT: [Script Type]
COMPLEXITY: [low/medium/high]

GRAMMATICAL CATEGORIES:
[List all categories with colors and examples]

HIERARCHICAL MAPPING LOGIC:
[Children-first logic with examples]

LANGUAGE-SPECIFIC FEATURES:
[List 4-6 key features]

AI PROMPT CONSTRAINTS:
[Exact allowed category list]

EXAMPLE SENTENCE ANALYSIS:
[Complete breakdown with categorization]
```

This Hindi template ensures consistent, high-quality analyzer generation across all 77 languages! 🌟</content>
<parameter name="filePath">d:\Language Learning\LanguagLearning\language_analyzer_template_hindi.md