# 🌍 Language Analyzer Template: Chinese Example

**Complete Specification for Automated Language Analyzer Generation**  
**Version:** 2026-01-06 (Chinese Reference Implementation)

---

## 🎯 OVERVIEW

This document provides the complete, detailed specification required to generate a **production‑ready automated language analyzer**. Chinese (Modern Standard Mandarin) is used as the **reference implementation**, demonstrating exactly what linguistic information must be defined when adding any new language.

### Template Structure

1. Language Configuration
2. Grammatical Categories (20 total)
3. Hierarchical Mapping Logic (children‑first)
4. Language‑Specific Features
5. AI Prompt Constraints
6. Complexity Rating Justification
7. Script Type Implications
8. Example Sentence Analysis

---

## 📋 LANGUAGE CONFIGURATION

```python
PythonLanguageConfig(
    code="zh",                           # ISO 639-1 code
    name="Chinese",                      # English name
    native_name="中文",                  # Native script name
    family="Sino-Tibetan",               # Language family
    script_type="logographic",           # Writing system type
    complexity_rating="low",             # Morphological complexity
    key_features=[
        'classifiers',                   # Measure words for noun quantification
        'aspect_particles',              # Markers for verbal aspect (no tense)
        'topic_comment',                 # Topic-prominent sentence structure
        'serial_verbs',                  # Verb chains without conjunctions
        'coverbs',                       # Verb-derived prepositions
        'tonal_system'                   # Lexical tones distinguish meaning
    ],
    supported_complexity_levels=["beginner", "intermediate", "advanced"]
)
```

---

## 📚 GRAMMATICAL CATEGORIES (20 CATEGORIES)

### Content Words (实词 / Shící)

| Category | Color | Description | Examples |
|--------|------|-------------|----------|
| noun | #FFAA00 | Entities, people, places, concepts | 人, 书, 水 |
| locative_noun | #FFAA00 | Spatial / directional nouns | 上, 里 |
| time_noun | #FFAA00 | Temporal nouns | 今天, 早上 |
| verb | #44FF44 | Actions, states, processes | 吃, 跑, 是 |
| adjective | #FF44FF | Qualities / stative verbs | 大, 红, 高兴 |
| adverb | #44FFFF | Modifiers of verbs/adjectives | 很, 常常, 已经 |
| numeral | #FFFF44 | Numbers / quantities | 一, 两, 第一 |
| classifier | #FFFF44 | Measure words | 个, 本, 条 |
| interjection | #FFD700 | Emotions, exclamations | 哎呀, 哇 |
| onomatopoeia | #FFD700 | Sound imitation | 汪汪, 叮咚 |

---

### Pronouns (代词 / Dàicí)

| Category | Color | Description | Examples |
|-------|------|-------------|----------|
| pronoun | #FF4444 | General pronoun | 我, 这 |
| personal_pronoun | #FF4444 | I / you / he | 我, 你, 他 |
| demonstrative_pronoun | #FF4444 | This / that | 这, 那 |
| interrogative_pronoun | #FF4444 | Who / what | 谁, 什么 |
| indefinite_pronoun | #FF4444 | Someone / anything | 有人, 什么 |

---

### Function Words (虚词 / Xūcí)

| Category | Color | Description | Examples |
|--------|------|-------------|----------|
| modal_verb | #44FF44 | Ability / necessity | 可以, 必须, 会 |
| directional_verb | #44FF44 | Direction complements | 来, 去, 起来 |
| coverb | #4444FF | Verb‑derived prepositions | 在, 从, 用 |
| conjunction | #888888 | Logical connectors | 和, 但是, 或 |
| particle | #AA44FF | Grammatical markers | 的, 了, 着 |
| other | #AAAAAA | Unclassified | Foreign names |

---

## 🔄 HIERARCHICAL MAPPING LOGIC (CRITICAL)

### Core Principle: **CHILDREN‑FIRST Categorization**

Specific grammatical subtypes **must be checked before parent categories** to prevent misclassification.

```python
def _map_grammatical_role_to_category(self, grammatical_role: str) -> str:
    role_lower = grammatical_role.lower().strip()

    # STEP 1: PREPROCESSING - Fix AI hallucinations
    if role_lower == "co verb":
        role_lower = "coverb"
    elif role_lower == "m measure_word":
        role_lower = "classifier"
    elif role_lower == "aux modal":
        role_lower = "modal_verb"
    elif role_lower == "direction complement":
        role_lower = "directional_verb"
    elif role_lower == "aspect particle":
        role_lower = "particle"

    # STEP 2: LANGUAGE-SPECIFIC CHILDREN (Highest Priority)
    # 1. Modal verbs BEFORE main verbs
    if any(keyword in role_lower for keyword in [
        'modal', 'auxiliary', 'modal_verb', 'auxiliary_verb', '能', '可以', '必须', '会', '应该'
    ]):
        return 'modal_verb'

    # 2. Directional verbs BEFORE main verbs
    if any(keyword in role_lower for keyword in [
        'directional', 'directional_verb', 'direction complement', '来', '去', '起来', '下去', '进来'
    ]):
        return 'directional_verb'

    # STEP 3: PRONOUN SUBTYPES (Before general pronoun)
    if any(keyword in role_lower for keyword in [
        'personal', 'personal_pronoun', 'first_person', 'second_person', 'third_person', '我', '你', '他', '她', '它', '我们', '你们', '他们'
    ]):
        return 'personal_pronoun'

    elif any(keyword in role_lower for keyword in [
        'demonstrative', 'demonstrative_pronoun', '这', '那', '这些', '那些'
    ]):
        return 'demonstrative_pronoun'

    elif any(keyword in role_lower for keyword in [
        'interrogative', 'interrogative_pronoun', 'question', '谁', '什么', '哪', '怎么', '为什么'
    ]):
        return 'interrogative_pronoun'

    elif any(keyword in role_lower for keyword in [
        'indefinite', 'indefinite_pronoun', '有人', '什么', '任何', '每个'
    ]):
        return 'indefinite_pronoun'

    # STEP 4: FUNCTION WORD SUBTYPES
    # 3. Coverbs BEFORE prepositions
    if any(keyword in role_lower for keyword in [
        'coverb', 'prepositional_verb', '在', '从', '到', '用', '给', '对', '向', '往'
    ]):
        return 'coverb'

    # 4. Particles BEFORE conjunctions
    if any(keyword in role_lower for keyword in [
        'particle', 'aspect_particle', 'structural_particle', '了', '着', '过', '的', '得', '地'
    ]):
        return 'particle'

    # STEP 5: SPECIAL CATEGORIES
    # 5. Classifiers BEFORE numerals
    if any(keyword in role_lower for keyword in [
        'classifier', 'measure_word', 'counter', '个', '本', '张', '只', '条', '把'
    ]):
        return 'classifier'

    # 6. Locative nouns BEFORE general nouns
    if any(keyword in role_lower for keyword in [
        'locative', 'locative_noun', 'spatial', '上', '下', '里', '外', '前', '后'
    ]):
        return 'locative_noun'

    # 7. Time nouns BEFORE general nouns
    if any(keyword in role_lower for keyword in [
        'time', 'time_noun', 'temporal', '今天', '昨天', '明天', '早上', '晚上', '年', '月', '日'
    ]):
        return 'time_noun'

    # 8. Onomatopoeia BEFORE interjections
    if any(keyword in role_lower for keyword in [
        'onomatopoeia', 'sound_imitation', '汪汪', '叮咚', '哗啦'
    ]):
        return 'onomatopoeia'

    # STEP 6: PARENT CATEGORIES (Lowest Priority - Checked Last)
    if any(keyword in role_lower for keyword in ['pronoun', '代词', '代']):
        return 'pronoun'

    if any(keyword in role_lower for keyword in ['verb', '动词', '动']):
        return 'verb'

    if any(keyword in role_lower for keyword in ['adjective', '形容词', '形']):
        return 'adjective'

    if any(keyword in role_lower for keyword in ['noun', '名词', '名']):
        return 'noun'

    if any(keyword in role_lower for keyword in ['adverb', '副词', '副']):
        return 'adverb'

    if any(keyword in role_lower for keyword in ['numeral', '数词', '数', '数字']):
        return 'numeral'

    # AI-generated roles that need mapping
    if 'subject' in role_lower:
        return 'pronoun'  # Subjects are typically pronouns in Chinese
    elif 'negation' in role_lower or 'determiner' in role_lower:
        return 'other'  # Negation particles and determiners

    return 'other'  # Default fallback
```

---

## 🎯 LANGUAGE‑SPECIFIC FEATURES (6)

### 1. Classifiers
Mandatory measure words used with numerals and demonstratives (一本书).

### 2. Aspect Particles
Particles express completion, duration, or experience (了, 着, 过).

### 3. Topic‑Comment Structure
Topic may differ from grammatical subject.

### 4. Serial Verbs
Multiple verbs chained without conjunctions (去买东西).

### 5. Coverbs
Verb‑origin prepositions with dual behavior (用手吃).

### 6. Tonal System
Four tones + neutral tone distinguish lexical meaning.

---

## 🤖 AI PROMPT CONSTRAINTS

### Batch Processing Prompt Structure
```python
grammatical_role: EXACTLY ONE category from this list:
noun, locative_noun, time_noun, verb, adjective, adverb, numeral, classifier,
pronoun, personal_pronoun, demonstrative_pronoun, interrogative_pronoun,
indefinite_pronoun, modal_verb, directional_verb, coverb, conjunction, particle,
interjection, onomatopoeia, other

CRITICAL REQUIREMENTS:
- grammatical_role MUST be EXACTLY one word from the allowed list
- Examples: "noun", "verb", "coverb" (not "common noun", "main verb", "prepositional verb")
- No prefixes, suffixes, or spaces in category names
- No synonyms or variations (e.g., not "measure_word" for "classifier")
```

### AI Response Format
```json
{
  "batch_results": [
    {
      "sentence_index": 1,
      "sentence": "我正在看书",
      "words": [
        {"word": "我", "individual_meaning": "I", "grammatical_role": "personal_pronoun"},
        {"word": "正", "individual_meaning": "ongoing", "grammatical_role": "adverb"},
        {"word": "在", "individual_meaning": "at", "grammatical_role": "coverb"},
        {"word": "看", "individual_meaning": "read", "grammatical_role": "verb"},
        {"word": "书", "individual_meaning": "book", "grammatical_role": "noun"}
      ]
    }
  ]
}
```

---

## 📊 COMPLEXITY RATING JUSTIFICATION

### Morphology: Low
- No inflections
- No verb conjugation
- Grammar via particles and order

### Script: High
- Logographic characters
- Thousands required for literacy

### Syntax: Medium
- SVO default
- Topic‑comment flexibility

**Overall Rating: LOW**

---

## 🔤 SCRIPT TYPE IMPLICATIONS

### Logographic Script (Hanzi / 汉字)

**Characteristics:**
- **Morpheme-Based**: Each character represents a morpheme (smallest meaningful unit)
- **Compound Characters**: Many words are multi-character compounds (e.g., 学校 xuéxiào "school")
- **Radical-Phonetic System**: Characters combine semantic radicals (hints) with phonetic components
- **No Alphabetic Segmentation**: Words are not separated by spaces in traditional writing
- **Pronunciation**: Handled by separate IPA service (not part of grammar analysis)

**Analysis Implications:**
- **Word Segmentation Challenge**: AI must identify word boundaries in continuous text
- **Character vs. Word**: Single characters can be words (e.g., 人 rén "person") or parts of compounds
- **Semantic Hints**: Radicals provide meaning clues (e.g., 手 radical in 看 "look" suggests hand-related action)
- **Teaching Aid**: Characters reinforce morphological awareness; pronunciation handled separately
- **Tokenization**: Requires specialized segmentation algorithms for accurate word identification

**Example Analysis:**
- **Character**: 看 (kàn) = 手 (hand) + 目 (eye) → "observe/look"
- **Compound**: 学校 = 学 (learn) + 校 (school) → "school"
- **Segmentation**: "我在学校学习" → 我 在 学校 学习 (not character-by-character)

**Challenges for Learners:**
- **Visual Memory**: Thousands of characters needed for literacy
- **Homophones**: Same pronunciation, different meanings (e.g., 书 shū "book" vs. 树 shù "tree")
- **Stroke Order**: Writing complexity affects motor learning

---

## 📝 EXAMPLE SENTENCE ANALYSIS

### Sentence 1: Basic Structure
**我吃了一本书**  
*"I ate a book"* (demonstrative example)

| Word | Meaning | Category | Color | Explanation |
|----|-------|----------|-------|-------------|
| 我 | I | personal_pronoun | 🔴 Red | First person pronoun |
| 吃 | eat | verb | 🟢 Green | Main action verb |
| 了 | completed | particle | 🟣 Purple | Perfective aspect particle |
| 一 | one | numeral | 🟡 Yellow | Cardinal number |
| 本 | book classifier | classifier | 🟡 Yellow | Measure word for books |
| 书 | book | noun | 🟠 Orange | Common noun |

### Sentence 2: With Aspect and Direction
**他正在往学校跑**  
*"He is running toward school"*

| Word | Meaning | Category | Color | Explanation |
|----|-------|----------|-------|-------------|
| 他 | he | personal_pronoun | 🔴 Red | Third person pronoun |
| 正 | currently | adverb | 🔵 Blue | Time adverb for ongoing action |
| 在 | at/ongoing | coverb | 🔵 Blue | Coverb indicating location/aspect |
| 往 | toward | coverb | 🔵 Blue | Directional coverb |
| 学校 | school | noun | 🟠 Orange | Compound noun |
| 跑 | run | verb | 🟢 Green | Main verb |

### Sentence 3: Modal and Classifier Usage
**我必须买三张票**  
*"I must buy three tickets"*

| Word | Meaning | Category | Color | Explanation |
|----|--------|-------|----------|-------|-------------|
| 我 | wǒ | I | personal_pronoun | 🔴 Red | First person pronoun |
| 必须 | bìxū | must | modal_verb | 🟢 Green | Modal expressing necessity |
| 买 | mǎi | buy | verb | 🟢 Green | Main verb |
| 三 | sān | three | numeral | 🟡 Yellow | Cardinal number |
| 张 | zhāng | ticket classifier | classifier | 🟡 Yellow | Measure word for flat objects |
| 票 | piào | ticket | noun | 🟠 Orange | Common noun |

### Hierarchical Categorization Demonstration

1. **Check language-specific children first**: "必须" → `modal_verb` ✓ (before general `verb`)
2. **Check function word subtypes**: "在", "往" → `coverb` ✓ (before `preposition`)
3. **Check pronoun subtypes**: "我", "他" → `personal_pronoun` ✓
4. **Check special categories**: "张", "本" → `classifier` ✓ (before `numeral`)
5. **Check parent categories**: "学校", "票" → `noun`, "买", "跑" → `verb`

### HTML Output Structure
```html
<span class="grammar-personal_pronoun">我</span>
<span class="grammar-verb">吃</span>
<span class="grammar-particle">了</span>
<span class="grammar-numeral">一</span>
<span class="grammar-classifier">本</span>
<span class="grammar-noun">书</span>
```

### Color-Coded Result
**🔴我** **🟢吃** **🟣了** **🟡一** **🟡本** **🟠书**

---

## 🚀 IMPLEMENTATION CHECKLIST

### Pre‑Generation
- Language config defined
- 20 categories present
- Hierarchy implemented
- Prompt constraints enforced

### Post‑Generation
- Analyzer loads
- Batch size respected (≤8 sentences)
- HTML output renders in Anki
- Real‑world sentence testing

---

**End of Chinese Reference Specification**

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

This Chinese template ensures consistent, high-quality analyzer generation across all 77 languages! 🌟

