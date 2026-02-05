# Turkish Grammar Concepts
## Linguistic Analysis for Turkish Language Analyzer

**Language:** Turkish (Türkçe)
**Family:** Turkic (Altaic)
**Script:** Latin alphabet (LTR)
**Key Features:** Agglutination, vowel harmony, SOV word order, no grammatical gender

## 🎯 Core Linguistic Features

### 1. Agglutination (Primary Feature)
**Definition:** Words are formed by adding suffixes to root words, each carrying specific grammatical meaning.

**Examples:**
- **ev** (house) + **im** (my) + **de** (at) + **ki** (that is in) = **evimdeki** (that is in my house)
- **gel** (come) + **iyor** (continuous) + **um** (I) = **geliyorum** (I am coming)

**Implications for Analysis:**
- Word boundaries are morphological, not just orthographic
- Each morpheme carries specific grammatical information
- Complex words can have 5-10 morphemes

### 2. Vowel Harmony (Phonological Rule)
**Definition:** Vowels in suffixes harmonize with the last vowel of the root word.

**Two Types:**
- **Front/Back Harmony:** a/ı/o/u (back) ↔ e/i/ö/ü (front)
- **Rounded/Unrounded Harmony:** a/o/u (rounded) ↔ e/i (unrounded)

**Examples:**
- **ev** (house, back vowel) + **de** (at, back vowel) = **evde** (at home)
- **kitap** (book, back vowel) + **da** (at, back vowel) = **kitapta** (in the book)
- **şehir** (city, front vowel) + **de** (at, front vowel) = **şehirde** (in the city)

### 3. Word Order (SOV - Subject-Object-Verb)
**Basic Structure:** Subject + Object + Verb

**Examples:**
- **Ben kitap okuyorum.** (I book read-PRESENT-1SG) = "I am reading a book."
- **Ali'ye mektup yazdım.** (Ali-DAT letter wrote-1SG) = "I wrote a letter to Ali."

**Implications:**
- Case markers are crucial for understanding grammatical roles
- Word order is flexible but meaning changes with case usage

### 4. Case System (6 Cases)
**Nominative:** Subject case (no marker)
**Accusative:** Direct object (-i/-ı/-u/-ü)
**Dative:** Indirect object (-e/-a)
**Locative:** Location (-de/-da)
**Ablative:** Source (-den/-dan)
**Genitive:** Possession (-in/-ın/-un/-ün)

**Examples:**
- **ev** (house-NOM) - **evi** (house-ACC) - **eve** (house-DAT)
- **kitap** (book-NOM) - **kitabı** (book-ACC) - **kitaba** (book-DAT)

### 5. Verb Conjugation (Complex System)
**Personal Endings:** 6 persons × 2 numbers = 12 forms
**Tense/Aspect/Mood:** Present, past, future, conditional, imperative, etc.

**Examples:**
- **gel-mek** (to come)
  - **geliyorum** (I am coming) - Present continuous
  - **geldim** (I came) - Simple past
  - **geleceğim** (I will come) - Future
  - **gelirdim** (I would come) - Past conditional

### 6. Noun Possession (Possessive Suffixes)
**Examples:**
- **ev** (house) + **im** (my) = **evim** (my house)
- **kitap** (book) + **ın** (your) = **kitabın** (your book)
- **araba** (car) + **sı** (his/her/its) = **arabası** (his/her/its car)

### 7. Question Formation
**Question Particle:** **mı/mi/mu/mü** added to focused element

**Examples:**
- **Kitap okuyorsun.** (You are reading a book.) → **Kitap mı okuyorsun?** (Are you reading a book?)
- **Ali geldi.** (Ali came.) → **Ali mi geldi?** (Did Ali come?)

## 📊 Grammatical Categories for Analysis

### Word Classes (Primary)
- **Noun (isim):** Person, place, thing, abstract concept
- **Verb (fiil):** Action, state, occurrence
- **Adjective (sıfat):** Describes nouns
- **Pronoun (zamir):** Replaces nouns
- **Adverb (zarf):** Describes verbs, adjectives, other adverbs
- **Postposition (edat):** Shows relationships (like prepositions)
- **Conjunction (bağlaç):** Connects clauses/sentences
- **Interjection (ünlem):** Express emotion
- **Numeral (sayı):** Numbers and quantifiers

### Morphological Categories (Secondary - Advanced)
- **Case:** Nominative, accusative, dative, locative, ablative, genitive
- **Possession:** 1st/2nd/3rd person, singular/plural
- **Tense:** Present, past, future, conditional
- **Aspect:** Simple, continuous, perfect
- **Mood:** Indicative, imperative, conditional, optative
- **Voice:** Active, passive, reflexive, reciprocal, causative

## 🔍 Analysis Complexity Levels

### Beginner Level
**Focus:** Basic word classes, simple sentences
**Include:** Noun, verb, adjective, pronoun, basic postpositions
**Exclude:** Complex morphology, advanced cases, compound tenses

### Intermediate Level
**Focus:** Case system, possession, basic verb conjugation
**Include:** All basic categories + cases + possession + present/past tenses
**Exclude:** Advanced verb forms, complex aspect combinations

### Advanced Level
**Focus:** Full morphological analysis, complex verb forms
**Include:** All categories + advanced morphology + compound verbs + complex syntax
**Exclude:** None - show full linguistic depth

## 🎨 Color Scheme Recommendations

Based on German/Spanish analyzer patterns:

```python
'beginner': {
    'noun': '#FFAA00',      # Orange
    'verb': '#4ECDC4',      # Teal
    'adjective': '#FF44FF', # Magenta
    'pronoun': '#9370DB',   # Medium Purple
    'postposition': '#4444FF', # Blue
    'conjunction': '#AAAAAA', # Gray
    'default': '#708090'    # Slate Gray
},
'intermediate': {
    # Add cases and possession
    'case_marker': '#FFD700',   # Gold
    'possessive': '#FF6347',    # Tomato
},
'advanced': {
    # Add morphological details
    'tense_marker': '#32CD32',  # Lime Green
    'aspect_marker': '#FF69B4', # Hot Pink
    'mood_marker': '#00CED1',   # Dark Turquoise
}
```

## 📝 Sample Sentences for Testing

### Beginner
- **Ben kitap okuyorum.** (I am reading a book.)
- **Ali eve gitti.** (Ali went home.)

### Intermediate
- **Kitabı Ali'ye verdim.** (I gave the book to Ali.)
- **Evimde yemek yiyorum.** (I am eating food at my house.)

### Advanced
- **Annemin gönderdiği mektupları okuyordum.** (I was reading the letters that my mother sent.)
- **Yarın gideceğimiz yer hazır mı?** (Is the place we will go tomorrow ready?)

## 🔗 Related Research

- **Agglutination:** Study of suffix chains and meaning composition
- **Vowel Harmony:** Phonological rules and exceptions
- **Word Order Flexibility:** Case marking vs. position-based grammar
- **Turkish Language Reform (1928):** Transition from Arabic to Latin script

## 🎯 Implementation Priorities

1. **Agglutination Handling:** Morphological analysis of compound words
2. **Vowel Harmony:** Suffix selection based on root vowels
3. **Case System:** Accurate case marker identification
4. **Verb Morphology:** Complex tense/aspect/mood combinations
5. **Possession:** Possessive suffix analysis

## 🆕 **Advanced Linguistic Features**

### 8. Compound Verbs
**Definition:** Complex verb constructions formed by combining multiple roots.

**Examples:**
- **yap-mak** (do) + **et-mek** (make) = **yap-et-mek** (cause to do)
  - **yaptırmak** (have something done)
- **başla-mak** (begin) + **et-mek** = **başlatmak** (cause to begin)
- **gör-mek** (see) + **ün-mek** = **görünmek** (appear)

**Analysis Challenge:** Multi-root verbs require decomposition of both roots and suffixes.

### 9. Reduplication
**Definition:** Word repetition for emphasis or different meanings.

**Examples:**
- **büyük büyük** (very big, emphasis)
- **yavaş yavaş** (slowly, gradual action)
- **az az** (little by little)

### 10. Clitics and Enclitics
**Definition:** Function words that attach to other words.

**Examples:**
- **Question Particle:** **mı/mi/mu/mü** (attached to focused element)
- **Emphatic Particle:** **da/de** (also, even)
- **Optative Particle:** **ki** (wish, that)

### 11. Loanword Integration
**Definition:** Arabic, Persian, French, and English loanwords in Turkish.

**Challenges:**
- Many loanwords don't follow vowel harmony rules
- Examples: **banka** (bank), **otel** (hotel), **komputer** (computer)
- Analysis must handle both native and foreign phonological patterns

## 🔄 **Morphological Parsing Strategy**

### Child-Before-Parent Analysis
**Critical for Turkish:** Morphological analysis must proceed **right-to-left** (suffixes before roots).

**Example Analysis of "evimdeki":**
```
evimdeki
   ↓
ki (relative) + de (locative) + im (possessive) + ev (root)
   ↓
Process suffixes first: ki → de → im → ev (root last)
```

**Implementation:**
1. Identify rightmost bound morpheme
2. Check vowel harmony with preceding element
3. Repeat until root reached
4. Validate entire morphological chain

## 📊 **Enhanced Complexity Levels**

### Beginner Level (Basic Communication)
**Focus:** Core vocabulary and simple structures
**Include:** Basic nouns, verbs, adjectives, present tense
**Exclude:** Complex morphology, advanced cases, compound verbs

### Intermediate Level (Functional Fluency)
**Focus:** Case system, possession, tense variations
**Include:** All basic + cases + possession + past/future tenses
**Exclude:** Advanced verb forms, complex compounds

### Advanced Level (Native-like Proficiency)
**Focus:** Full morphological analysis, complex constructions
**Include:** All features + compound verbs + advanced morphology
**Exclude:** None - complete linguistic analysis

## 🎨 **Enhanced Color Scheme**

```python
'beginner': {
    'noun': '#FFAA00',      # Orange
    'verb': '#4ECDC4',      # Teal
    'adjective': '#FF44FF', # Magenta
    'pronoun': '#9370DB',   # Medium Purple
    'postposition': '#4444FF', # Blue
    'conjunction': '#AAAAAA', # Gray
    'default': '#708090'    # Slate Gray
},
'intermediate': {
    'case_marker': '#FFD700',   # Gold
    'possessive': '#FF6347',    # Tomato
    'question_particle': '#FF1493', # Deep Pink
    'tense_marker': '#32CD32',  # Lime Green
},
'advanced': {
    'aspect_marker': '#FF69B4', # Hot Pink
    'mood_marker': '#00CED1',   # Dark Turquoise
    'negation': '#DC143C',      # Crimson
    'plural': '#8A2BE2',        # Blue Violet
    'compound_verb': '#FF8C00', # Dark Orange
}
```

## 📝 **Enhanced Sample Sentences**

### Beginner
- **Merhaba dünya!** (Hello world!)
- **Ben kitap okuyorum.** (I am reading a book.)
- **Ali eve gitti.** (Ali went home.)

### Intermediate
- **Kitabı Ali'ye verdim.** (I gave the book to Ali.)
- **Evimde yemek yiyorum.** (I am eating food at my house.)
- **Annemin mektubunu okudum.** (I read my mother's letter.)

### Advanced
- **Annemin gönderdiği mektupları okuyordum.** (I was reading the letters my mother sent.)
- **Yarın gideceğimiz yer hazır mı?** (Is the place we will go tomorrow ready?)
- **Arkadaşımın bana verdiği kitabı okuyorum.** (I am reading the book my friend gave me.)
- **Başarıyla tamamlamış olduğum projeyi sunacağım.** (I will present the project I have successfully completed.)

## 🔍 **Analysis Implementation Notes**

### Prevention-at-Source Strategy
**Turkish-Specific Rules:**
- Always decompose agglutinated words before analysis
- Validate vowel harmony in all suffix chains
- Identify case markers and their grammatical functions
- Handle compound verbs as multi-root constructions
- Account for loanword exceptions to harmony rules

### Common AI Analysis Errors to Prevent
1. **Treating compound words as single units**
2. **Ignoring vowel harmony violations**
3. **Misidentifying case functions**
4. **Missing morphological boundaries**
5. **Incorrect compound verb analysis**

### Quality Validation Checks
- Morphological decomposition completeness
- Vowel harmony rule compliance
- Case marker function accuracy
- Compound verb root identification
- Loanword handling appropriateness