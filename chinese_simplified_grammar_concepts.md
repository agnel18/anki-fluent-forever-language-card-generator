# Chinese Simplified Grammar Concepts

## Language Overview
**Language**: Chinese Simplified (中文简体)
**Language Code**: zh
**Language Family**: Sino-Tibetan
**Script Type**: Logographic (Han characters) + Pinyin romanization
**Morphological Type**: Analytic (isolating) - minimal inflection, relies on word order and particles
**Word Order**: Subject-Verb-Object (SVO) with topic-comment structure
**Complexity Rating**: High (due to character-based analysis and tonal aspects)

## Linguistic Research Sources
**Primary Sources:**
- Huang Borong & Liao Xudong. 《现代汉语》 (Modern Chinese Grammar)
- Li Charles N. & Thompson Sandra A. "Mandarin Chinese: A Functional Reference Grammar"
- Chappell Hilary. "Sinitic Grammar: Synchronic and Diachronic Perspectives"
- Modern typological works on isolating languages

**Key Linguistic Features:**
- **Topic-Comment Structure**: Sentences organized around topics rather than subjects
- **Measure Words/Classifiers**: Required for counting nouns (个, 本, 杯, etc.)
- **Aspect System**: Perfective (了), durative (着), experiential (过)
- **Coverbs/Prepositions**: Verbs used prepositionally (在, 对, 给)
- **Modal Particles**: Sentence-final particles (吗, 呢, 吧, 了)
- **Resultative Compounds**: Verb + verb constructions (吃完, 看懂)

## Morphological Structure
**Type**: Analytic/Isolating
- Words are morphologically simple
- No inflection for case, number, gender, tense
- Grammatical relationships expressed through:
  - Word order
  - Particles and markers
  - Compound word formation
  - Classifier usage

**Word Formation**:
- **Monosyllabic**: Single characters (我, 你, 他)
- **Disyllabic Compounds**: Most common (学生, 学习, 朋友)
- **Polysyllabic**: Less common but exist (图书馆, 现代化)

## Syntactic Features
**Basic Word Order**: SVO (Subject-Verb-Object)
**Topic-Comment**: Topic + Comment structure common
**Modifier Position**: Modifiers precede modified elements
**Serial Verbs**: Multiple verbs in sequence without conjunctions

**Sentence Types**:
- **Declarative**: Subject + Verb + Object (+ particles)
- **Interrogative**: Yes-no (V-not-V), wh-questions, tag questions
- **Imperative**: Verb + object (+ particles)
- **Existential**: 有 + noun (+ location)

## Script and Orthography
**Primary Script**: Han characters (logographic)
- Each character represents a morpheme
- Characters combine to form compound words
- No alphabet - characters must be learned individually

**Romanization**: Hanyu Pinyin
- Used for pronunciation guides
- Includes tone marks (ā, á, ǎ, à)
- Essential for input methods and learning

**Character Types**:
- **Simple Characters**: Single component
- **Compound Characters**: Multiple radicals
- **Phono-semantic**: Sound + meaning components

## Unique Grammatical Categories (实词/虚词 Distinction)

### Content Words (实词 / Shící) - Independent Meaning
1. **Noun (名词)**: People, places, things, concepts
2. **Verb (动词)**: Actions, states, changes
3. **Adjective (形容词)**: Qualities, descriptions
4. **Numeral (数词)**: Numbers, quantities
5. **Measure Word/Classifier (量词)**: Counting units (个, 本, 杯, 张)
6. **Pronoun (代词)**: Replacements for nouns
7. **Time Word (时间词)**: Time expressions (今天, 明天, 现在)
8. **Locative Word (处所词)**: Location/direction (这里, 那里, 上, 下)

### Function Words (虚词 / Xūcí) - Structural/Grammatical
9. **Aspect Particle (体词)**: Aspect markers (了, 着, 过)
10. **Modal Particle (语气词)**: Sentence mood (吗, 呢, 吧, 啊)
11. **Structural Particle (结构词)**: Relationship markers (的, 地, 得)
12. **Preposition/Coverb (介词/趋向词)**: Relationships (在, 对, 给, 从)
13. **Conjunction (连词)**: Connectors (和, 但是, 因为)
14. **Adverb (副词)**: Verb/adjective modifiers (很, 不, 都)
15. **Interjection (叹词)**: Emotions/exclamations (啊, 哦, 唉)
16. **Onomatopoeia (拟声词)**: Sound imitation (砰, 哗啦)

## Most Frequent Grammatical Markers (5-12 Key Patterns)

### 1. Aspect Particles (Most Common)
- **了 (le)**: Perfective aspect - completed actions
- **着 (zhe)**: Durative aspect - ongoing states
- **过 (guo)**: Experiential aspect - experienced actions

### 2. Modal Particles (Sentence-Final)
- **吗 (ma)**: Yes-no questions
- **呢 (ne)**: Topic continuation, confirmation
- **吧 (ba)**: Suggestion, assumption
- **啊 (a)**: Exclamation, realization

### 3. Structural Particles
- **的 (de)**: Attribution/possession
- **地 (de)**: Adverbial modification
- **得 (de)**: Resultative complement

### 4. Measure Words/Classifiers (Top 10)
- **个 (gè)**: General classifier
- **本 (běn)**: Books, notebooks
- **杯 (bēi)**: Cups, glasses
- **张 (zhāng)**: Flat objects (paper, table)
- **只 (zhī)**: Animals, one of a pair
- **辆 (liàng)**: Vehicles
- **家 (jiā)**: Businesses, families
- **位 (wèi)**: People (polite)
- **条 (tiáo)**: Long thin objects
- **件 (jiàn)**: Items, matters

### 5. Prepositions/Coverbs
- **在 (zài)**: Location, progressive aspect
- **对 (duì)**: Towards, regarding
- **给 (gěi)**: To, for (benefactive)
- **从 (cóng)**: From
- **到 (dào)**: To, until

## Validation Patterns (3-6 Simple Checks)

### 1. Required Particles Present
- Check for aspect particles in appropriate contexts
- Verify modal particles at sentence end for questions
- Ensure structural particles (的/地/得) are correctly used

### 2. Script/Character Set Validation
- Verify all characters are valid Han characters
- Check for proper Pinyin romanization format
- Validate tone marks are present when expected

### 3. Measure Word Agreement
- Ensure nouns requiring measure words have appropriate classifiers
- Check number + measure word + noun sequences
- Validate common measure word + noun combinations

### 4. Tone Markers (Tonal Language)
- Verify Pinyin includes tone marks (ā/á/ǎ/à)
- Check for neutral tone indicators where appropriate
- Validate tone sandhi patterns (common changes)

### 5. Word Order Patterns
- Basic SVO structure validation
- Topic-comment structure recognition
- Modifier + modified element ordering

### 6. Compound Word Formation
- Validate common disyllabic compounds
- Check resultative verb compounds (V1 + V2)
- Verify directional complement patterns

## Architecture Decision
**Inheritance Strategy**: Inherit directly from `BaseGrammarAnalyzer`
- **Reasoning**: No other Sino-Tibetan languages planned in next 3 months
- **Implementation**: All Chinese-specific logic in `ZhAnalyzer` class
- **Avoid**: Creating `SinoTibetanAnalyzer` base class prematurely

## Grammatical Role Mapping (Color-Coded Categories)
```python
GRAMMATICAL_ROLES = {
    # Content Words (实词)
    "noun": "#FFAA00",                    # Orange - People/places/things/concepts
    "verb": "#44FF44",                    # Green - Actions/states/changes
    "adjective": "#FF44FF",               # Magenta - Qualities/descriptions
    "numeral": "#FFFF44",                 # Yellow - Numbers/quantities
    "measure_word": "#FFD700",            # Gold - Classifiers (个, 本, 杯)
    "pronoun": "#FF4444",                 # Red - Replacements for nouns
    "time_word": "#FFA500",               # Orange-red - Time expressions
    "locative_word": "#FF8C00",           # Dark orange - Location/direction

    # Function Words (虚词)
    "aspect_particle": "#8A2BE2",         # Purple - Aspect markers (了, 着, 过)
    "modal_particle": "#DA70D6",          # Plum - Tone/mood particles (吗, 呢, 吧)
    "structural_particle": "#9013FE",     # Violet - Structural particles (的, 地, 得)
    "preposition": "#4444FF",             # Blue - Prepositions/coverbs
    "conjunction": "#888888",             # Gray - Connectors
    "adverb": "#44FFFF",                  # Cyan - Modifies verbs/adjectives
    "interjection": "#FFD700",            # Gold - Emotions/exclamations
    "onomatopoeia": "#FFD700"             # Gold - Sound imitation
}
```

## Pattern Implementation Strategy
**Focus**: 5-12 most frequent markers only
- **Aspect particles**: 了, 着, 过 (regex patterns for position and context)
- **Modal particles**: 吗, 呢, 吧, 啊 (sentence-final position)
- **Structural particles**: 的, 地, 得 (context-dependent patterns)
- **Top measure words**: 个, 本, 杯, 张, 只 (noun agreement patterns)
- **Common coverbs**: 在, 对, 给, 从, 到 (prepositional usage)

**Avoid**: Full morphological parsing, complex tone analysis, complete character decomposition

## Validation Logic Implementation
**Simple Checks Only**:
1. **Particle Position**: Aspect/modal particles in correct positions
2. **Character Validation**: All characters are valid Han characters
3. **Measure Word Presence**: Required classifiers for count nouns
4. **Tone Mark Validation**: Pinyin includes proper tone marks
5. **Basic Word Order**: SVO structure maintained
6. **Compound Recognition**: Common disyllabic compounds identified

## Prompt Adaptation Strategy
**Chinese-Specific Prompts**:
- Use Chinese grammatical terminology (实词/虚词, 体词, 语气词)
- Include Pinyin romanization for pronunciation
- Reference topic-comment structure
- Support English explanations alongside Chinese terms
- Include measure word examples
- Cover aspect particle distinctions

## Implementation Plan
1. **Class Structure**: `ZhAnalyzer(BaseGrammarAnalyzer)`
2. **Pattern Initialization**: 8-10 key regex patterns for markers
3. **Validation Methods**: 4-5 simple validation checks
4. **Prompt Generation**: Chinese-specific batch prompts
5. **HTML Generation**: Character-based coloring with compound support
6. **Testing**: Comprehensive test suite with Chinese examples

## Success Criteria
- **Authentic**: True to Chinese grammatical structures, not English impositions
- **Character-Aware**: Proper handling of Han characters and Pinyin
- **Aspect-Accurate**: Correct distinction between 了/着/过
- **Measure Word Support**: Proper classifier validation
- **Topic-Comment Recognition**: Handle Chinese sentence patterns
- **Efficient**: Optimized for character-based processing
- **Maintainable**: Clear separation of concerns, comprehensive documentation