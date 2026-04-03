# Japanese Grammar Concepts — Linguistic Research Document

> **Phase 1 Output** — Research reference for the Japanese grammar analyzer.

---

## 1. Language Overview

| Property | Value |
|----------|-------|
| **Language** | Japanese (日本語) |
| **Code** | `ja` |
| **Family** | Japonic |
| **Script** | Mixed: Hiragana, Katakana, Kanji (CJK) |
| **Word Order** | SOV (Subject–Object–Verb) |
| **Text Direction** | LTR (horizontal), top-to-bottom (vertical) |
| **Morphology** | Agglutinative |
| **Writing System** | Logographic + Syllabary (no spaces between words) |

---

## 2. Writing Systems

### 2.1 Hiragana (ひらがな)
- 46 basic characters + diacritics (dakuten, handakuten)
- Used for native Japanese words, grammatical particles, verb/adjective endings
- Key particles: は (wa/topic), が (ga/subject), を (wo/object), に (ni/location/direction), で (de/means/location), の (no/possession), から (kara/from), まで (made/until), へ (e/toward), と (to/and/with), も (mo/also), よ (yo/emphasis), ね (ne/confirmation), か (ka/question)

### 2.2 Katakana (カタカナ)
- 46 basic characters + diacritics
- Used for foreign loanwords (gairaigo), onomatopoeia, emphasis, technical terms
- Examples: コンピュータ (computer), テレビ (television), パン (bread)

### 2.3 Kanji (漢字)
- ~2,136 jōyō kanji (commonly used); ~3,000+ in daily use
- Each kanji has on'yomi (Chinese reading) and kun'yomi (Japanese reading)
- Used for content words: nouns, verb stems, adjective stems

---

## 3. Core Grammar Features

### 3.1 Particles (助詞 — joshi)
The most critical feature of Japanese grammar. Particles are postpositional markers.

| Particle | Function | Example |
|----------|----------|---------|
| は (wa) | Topic marker | 私**は**学生です (As for me, [I] am a student) |
| が (ga) | Subject marker | 雨**が**降る (Rain falls) |
| を (wo/o) | Object marker | 本**を**読む (Read a book) |
| に (ni) | Direction/time/indirect obj | 学校**に**行く (Go to school) |
| で (de) | Means/location of action | 電車**で**行く (Go by train) |
| の (no) | Possession/nominalization | 私**の**本 (My book) |
| と (to) | And/with/quotation | 友達**と**行く (Go with a friend) |
| から (kara) | From (source) | 東京**から**来た (Came from Tokyo) |
| まで (made) | Until/to (limit) | 5時**まで** (Until 5 o'clock) |
| へ (e) | Toward (direction) | 日本**へ**行く (Go toward Japan) |
| も (mo) | Also/too | 私**も**行く (I also go) |
| よ (yo) | Emphasis/assertion | いい**よ** (It's good, I tell you) |
| ね (ne) | Confirmation/agreement | いい天気です**ね** (Nice weather, isn't it?) |
| か (ka) | Question marker | 学生です**か** (Are you a student?) |

### 3.2 Verb Conjugation (動詞の活用)
Japanese verbs conjugate for tense, politeness, negation, and mood — but NOT for person or number.

**Verb Groups:**
- **Group 1 (五段動詞 godan):** u-verbs — 書く(kaku), 読む(yomu), 話す(hanasu)
- **Group 2 (一段動詞 ichidan):** ru-verbs — 食べる(taberu), 見る(miru), 起きる(okiru)
- **Group 3 (不規則動詞):** Irregular — する(suru/to do), 来る(kuru/to come)

**Key Conjugation Forms:**
| Form | Example (食べる) | Usage |
|------|-----------------|-------|
| Dictionary | 食べる | Plain present/future |
| Masu (polite) | 食べます | Polite present/future |
| Te-form | 食べて | Connecting, requests |
| Ta-form (past) | 食べた | Plain past |
| Nai-form (neg) | 食べない | Plain negative |
| Potential | 食べられる | Can eat |
| Passive | 食べられる | Is eaten |
| Causative | 食べさせる | Make/let eat |
| Conditional | 食べれば | If [one] eats |
| Volitional | 食べよう | Let's eat / intend to eat |

### 3.3 Adjective Types
- **い-adjectives (i-adjectives):** 大きい(ōkii/big), 高い(takai/tall/expensive) — conjugate directly
- **な-adjectives (na-adjectives):** 静か(shizuka/quiet), きれい(kirei/beautiful) — require な before nouns

### 3.4 Politeness Levels (敬語 keigo)
| Level | Style | Example |
|-------|-------|---------|
| Casual (タメ口) | Plain form | 食べる |
| Polite (丁寧語) | です/ます | 食べます |
| Humble (謙譲語) | Self-lowering | いただく |
| Honorific (尊敬語) | Other-elevating | 召し上がる |

### 3.5 Sentence-Final Particles
- よ (yo) — assertion/new information
- ね (ne) — seeking agreement
- か (ka) — question
- の (no) — explanation/seeking explanation
- わ (wa) — soft assertion (feminine)
- ぞ (zo) — strong assertion (masculine)
- な (na) — prohibition / self-reflection

### 3.6 Counters (助数詞)
Japanese uses counter words with numbers:
- 個 (ko) — small objects
- 人 (nin/ri) — people
- 本 (hon) — long cylindrical objects
- 枚 (mai) — flat objects
- 匹 (hiki) — small animals
- 台 (dai) — machines/vehicles
- つ (tsu) — general counter (native Japanese numbers)

---

## 4. Grammatical Roles for Analysis

### Beginner Level
- **noun** (名詞) — 学生, 本, 日本
- **verb** (動詞) — 食べる, 行く, する
- **adjective** (形容詞) — 大きい, きれいな
- **particle** (助詞) — は, が, を, に, で
- **adverb** (副詞) — とても, まだ, もう
- **copula** (繋辞) — です, だ

### Intermediate Level
All beginner + :
- **i_adjective** (い形容詞)
- **na_adjective** (な形容詞)
- **auxiliary_verb** (助動詞) — ます, た, ない, れる
- **counter** (助数詞) — 個, 人, 本
- **conjunction** (接続詞) — しかし, そして, でも
- **topic_particle** — は
- **subject_particle** — が
- **object_particle** — を

### Advanced Level
All intermediate + :
- **honorific_verb** (尊敬動詞)
- **humble_verb** (謙譲動詞)
- **te_form** (て形)
- **potential_verb** (可能動詞)
- **passive_verb** (受身動詞)
- **causative_verb** (使役動詞)
- **conditional_form** (条件形)
- **volitional_form** (意志形)
- **sentence_final_particle** — よ, ね, か
- **nominalizer** — の, こと
- **quotation_particle** — と

---

## 5. Key Challenges for Analyzer

1. **No spaces between words** — Must use character-level tokenization or morphological analysis
2. **Mixed scripts** — Kanji + Hiragana + Katakana can appear in a single word
3. **Context-dependent readings** — Same kanji can have multiple readings
4. **Particle は vs. は** — Topic marker は reads "wa", not "ha"
5. **Verb stem + suffix agglutination** — Multiple suffixes can attach (食べさせられなかった = was not made to eat)
6. **Politeness interleaving** — Politeness markers embedded in verb forms
7. **Omitted subjects** — Japanese frequently omits the subject when clear from context

---

## 6. Color Scheme Design

### Beginner
| Role | Color | Hex |
|------|-------|-----|
| noun | Orange | #FFAA00 |
| verb | Green | #44FF44 |
| adjective | Magenta | #FF44FF |
| particle | Blue | #4444FF |
| adverb | Cyan | #44FFFF |
| copula | Purple | #AA44FF |
| other | Gray | #AAAAAA |

### Intermediate
Adds: i_adjective (#FF44FF), na_adjective (#FF88CC), auxiliary_verb (#228B22), counter (#FFD700), conjunction (#888888), topic_particle (#1E90FF), subject_particle (#4169E1), object_particle (#6495ED)

### Advanced
Adds: honorific_verb (#006400), humble_verb (#2E8B57), te_form (#32CD32), potential_verb (#3CB371), passive_verb (#66CDAA), causative_verb (#8FBC8F), sentence_final_particle (#FF6347), nominalizer (#CD853F), quotation_particle (#DEB887)
