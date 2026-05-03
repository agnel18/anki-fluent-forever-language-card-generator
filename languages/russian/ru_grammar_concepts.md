# Russian Grammar Concepts and Implementation Guide

## Executive Summary

Russian (русский язык) is an East Slavic language in the Indo-European family, spoken natively by ~150 million people and as an L2 by an additional ~108 million — the **6th most-spoken language in the world by total speakers** and a perennial top-10 most-studied L2. Unlike English, Russian retains and intensifies the inherited Indo-European fusional morphology: every nominal carries inflection for **case, gender, and number**, every finite verb carries inflection for **person, number, tense, aspect, and (in past) gender**, and word-class membership is signalled morphologically rather than positionally. Word order is technically free — almost any permutation of the major constituents is grammatical — but pragmatically constrained by **information structure** (theme/rheme, topic/focus). This makes Russian the classic textbook case of a "synthetic, free-word-order, pro-drop, null-copula present-tense" language.

This analyzer follows the German/Latvian Clean Architecture contract — domain components for config, prompt building, response parsing, validation, and rule-based fallbacks; infrastructure for AI service, circuit breaker, caching; external YAML/JSON data files; and a 5-level fallback parsing chain. The analyzer must hit ≥0.85 confidence on AI output and emit `is_fallback: True` whenever the rule-based fallback is used so the validator can cap confidence at 0.3.

The two pillars of Russian analytical complexity are the **case system** (6 cases × 3 genders × 2 numbers × 3 declension classes × hard/soft stem alternations ≈ 70+ noun ending slots) and the **aspectual system** (every verb belongs to an imperfective↔perfective pair; tense × aspect interact rather than stack). Adjective and pronoun agreement multiplies the morphological surface area further, while verbs of motion (14 indeterminate/determinate pairs) and the participial system (4 participle types, all declined like long-form adjectives) add specialty subsystems. The prompt builder, response parser, and validator must therefore be designed around mandatory case + gender + number + animacy labelling for every nominal, and mandatory aspect + tense + person + number labelling for every finite verb.

## Language Overview

### Classification and Status
- **Language Family:** Indo-European
- **Branch:** Balto-Slavic → Slavic → East Slavic
- **Closest Relatives:** Belarusian, Ukrainian (East Slavic); Polish, Czech, Slovak (West Slavic); Bulgarian, Serbo-Croatian, Slovene (South Slavic)
- **Script Type:** Alphabetic — Cyrillic, 33 letters (10 vowels + 21 consonants + 2 modifier letters ь/ъ that carry no sound but signal palatalization or hardness)
- **Writing Direction:** Left-to-right
- **Official Status:** Official language of the Russian Federation, Belarus, Kazakhstan, Kyrgyzstan; widely used in Ukraine, Moldova, Estonia, Latvia, Lithuania, Georgia, Armenia, Azerbaijan, Tajikistan, Turkmenistan, Uzbekistan; one of the six official UN languages; working language of the SCO, EAEU, CIS
- **Global Speakers:** ~150M native, ~108M L2 — total reach ~258M (6th globally by total speakers)

### Geographic and Cultural Context
- **Primary Regions:** Russian Federation, post-Soviet states (Belarus, Kazakhstan, Kyrgyzstan, Tajikistan, Uzbekistan, Turkmenistan, Armenia, Azerbaijan, Georgia, Moldova, Estonia, Latvia, Lithuania, Ukraine), large diasporas in Israel, Germany, USA, Brazil, Argentina, Canada, Australia
- **Cultural Significance:** Language of one of the world's largest literary canons (Pushkin, Lermontov, Gogol, Dostoevsky, Tolstoy, Chekhov, Bulgakov, Pasternak, Solzhenitsyn, Akhmatova, Mandelstam, Brodsky); historical lingua franca of Eastern Europe and Central/North Asia; major language of mathematics, theoretical physics, chess, ballet, cosmonautics
- **Dialectal Variation:** Northern, Southern, Central dialect zones; Standard Russian based on the Moscow variety; relatively low dialectal divergence compared with German or Italian; substantial sociolectal variation including official register (книжный язык), neutral (стандартный), colloquial (разговорный), substandard (просторечие), criminal jargon (феня)
- **Modern Usage:** Major language of the internet (~5% of web content, 2nd-most-used after English on the Russian web); core scientific publication language across Eurasia

### Script and Writing System
- **Character Set:** 33 Cyrillic letters
  - **10 vowels:** а, е, ё, и, о, у, ы, э, ю, я — split into "hard" (а, э, ы, о, у) and "soft" (я, е, и, ё, ю) series
  - **21 consonants:** б, в, г, д, ж, з, к, л, м, н, п, р, с, т, ф, х, ц, ч, ш, щ, й
  - **2 modifier letters (no phonetic value):** ь (мягкий знак, soft sign — palatalizes preceding consonant) and ъ (твёрдый знак, hard sign — separates iotated vowel from preceding consonant)
- **Capitalization:** Sentence-initial and proper nouns. Notably, days of the week, months, nationalities, and language names are NOT capitalized (понедельник, январь, русский, английский) — a contrast with English/German.
- **Punctuation:** Standard Western — period, comma, semicolon, colon, question mark, exclamation mark, em-dash (used for the absent present-tense copula: *Москва — столица России*, "Moscow [is] the capital of Russia"). Comma usage is rule-governed and dense — every subordinate clause is comma-bound, including most participial and gerund phrases.
- **Phonetic Orthography Rules:** Russian spelling is morphophonemic — it preserves morpheme identity over surface phonetics. Consequences:
  - **Vowel reduction (akan'e, ikan'e):** unstressed `о` is pronounced [ɐ]/[ə], unstressed `е/я` reduce to [ɪ]. Spelling does NOT reflect this.
  - **Final consonant devoicing:** word-final voiced obstruents (б/в/г/д/з/ж) devoice to [p/f/k/t/s/ʃ], spelled as if voiced. *хлеб* (bread) is pronounced [xlʲep].
  - **Stress is unpredictable and lexical** — not marked in normal text. Stress determines vowel reduction. Stress can shift across the paradigm: *окно́* (sg nom) → *о́кна* (pl nom). Dictionaries and learner materials mark stress with an acute accent.
  - **Spelling rules:** after к/г/х/ж/ш/щ/ч you write *и* not *ы*; after ж/ш/ц/ч/щ you write *а/у* not *я/ю*; after sibilants in certain positions *о* alternates with *е*. These constraints reshape inflectional endings (книги not *книгы; ножом, but чтением).

## Grammatical Structure Analysis

### Word Order and Sentence Structure

#### Basic Word Order
Russian is canonically **SVO** but the case system makes word order **almost completely free** at the syntactic level. The functional choice between SVO, SOV, OSV, OVS, VSO, VOS is driven by **information structure**:

- **Theme (given information) precedes rheme (new information).** New/focused material gravitates rightward.
- *Иван читает книгу.* (Ivan reads a book — neutral SVO; rhematic = "a book")
- *Книгу читает Иван.* (It is Ivan who is reading the book — rhematic = "Ivan", contrastive)
- *Иван книгу читает.* (Ivan is the one reading the book / Ivan, the book — he reads — colloquial topicalization)
- *Читает Иван книгу.* (Used in narrative or with focus on the action)

Because the noun's case (subject = nominative, direct object = accusative) is overtly marked, no ambiguity arises from reordering: *Маму любит сын* and *Сын любит маму* both unambiguously mean "the son loves mom" — the reading is fixed by case.

#### Yes/No Questions
- **Intonation only** (most common): *Ты идёшь?* — rising-falling pitch on the rhematic word
- **Particle ли** (formal, register-marked): *Идёшь ли ты?* — fronts the verb + ли after it
- **No do-support**, no auxiliary insertion, no inversion is required
- **Wh-questions:** wh-word fronted: *Кто пришёл?* (Who came?), *Что ты читаешь?* (What are you reading?), *Куда ты идёшь?* (Where are you going?), *Когда?* (When?), *Почему?* (Why?), *Как?* (How?), *Сколько?* (How much/many?)

#### Negation
- **Particle не** placed immediately before the negated constituent: *Я не читаю.* (I don't read.) / *Не я читаю.* (It's not I who reads.)
- **Genitive of negation:** under negation, direct objects can shift from accusative to genitive — *Я вижу книгу* (I see the book — acc) → *Я не вижу книги* (I don't see the/a book — gen). The genitive marks non-existence/non-affectedness; accusative under negation is also possible and less semantically loaded.
- **Genitive of negation with быть:** *Книги нет* (There's no book — gen sg of книга), *Студентов нет* (There are no students — gen pl). The verb form is **нет** (= не + есть), an unanalyzed negative existential.
- **Double/multiple negation is grammatical and required:** *Никто никогда ничего не говорит.* (Nobody ever says anything.) — every n-word + не. Unlike English, omitting не is ungrammatical.

#### Imperatives
- Verb-initial; subject ты/вы typically dropped: *Читай!* (sg, 2sg-informal), *Читайте!* (pl/formal)
- 1pl imperatives via davaj(te): *Давай(те) пойдём!* (Let's go!) or perfective future 1pl alone: *Пойдём!*
- 3rd-person via particles пусть/пускай: *Пусть он придёт!* (Let him come!)

#### Embedded Clauses
- Complementizer **что** (= "that"): *Я знаю, что он пришёл.* (I know that he came.) — comma obligatory
- Final-purpose **чтобы**: *Я пришёл, чтобы помочь.* (I came in order to help.)
- Conditional **если**: *Если будет дождь, я останусь.* (If it rains, I'll stay.)
- Temporal **когда**, **пока**, **как только** (when, while, as soon as)
- Causal **потому что**, **так как**, **поскольку** (because, since)

#### Pro-drop and Null Copula
- **Pro-drop:** subject pronouns are dropped freely whenever the verb's morphology disambiguates person/number: *Иду* (I'm going) — 1sg implicit. Compulsory pronoun appearance is a marked, often contrastive, choice.
- **Null copula in present:** the present-tense form of быть (to be) is **silent** in standard usage. *Он студент.* (He [is] a student.) An em-dash often substitutes in writing: *Москва — столица.* The 3sg form *есть* survives only in existential ("there is"), emphatic identification, and a few fixed expressions. Past and future of быть are fully overt: *Он был студентом* (he was a student — instrumental complement), *Он будет студентом* (he will be a student).

#### Constituent Order Examples
1. **Simple declarative SVO:** *Студенты изучают русский.* (The students study Russian.)
2. **Topicalized OVS:** *Русский изучают студенты.* (Russian — students study [it]. / It's students who study Russian.)
3. **Yes/no question (intonation):** *Студенты изучают русский?*
4. **Wh-question:** *Что изучают студенты?* (What do the students study?)
5. **Negation:** *Студенты не изучают русский.* (The students don't study Russian.)
6. **Genitive of negation:** *Я не вижу студентов.* (I don't see (any) students — gen pl)
7. **Relative clause:** *Студент, который изучает русский, ...* (The student who studies Russian, ...) — **который** declines for case + gender + number to agree with antecedent.
8. **Subordinate clause:** *Хотя был дождь, мы пошли гулять.* (Although it was raining, we went for a walk.)
9. **Cleft-like (no syntactic cleft, only intonation/word order):** *Это Иван разбил окно.* (It is Ivan who broke the window — *это* = "this/it" as deictic copula substitute.)

### Morphological System

Russian morphology is **densely fusional**. A single ending typically encodes 3-4 features simultaneously (e.g., -ом on a noun = masculine + singular + instrumental; -ого on an adjective = masculine + singular + genitive/animate-accusative + hard stem). The analyzer must decompose each surface form into this feature bundle.

#### Inflection Types

##### Nominal Inflection — The Core of Russian Difficulty

###### Cases (6)
| # | Russian Name | English Name | Core Function | Example Question |
|---|---|---|---|---|
| 1 | именительный (Им.) | nominative | subject; predicate of overt быть in present (rare) | кто? что? (who? what?) |
| 2 | родительный (Род.) | genitive | possession; absence/negation; partitive; after most prepositions of direction-from | кого? чего? |
| 3 | дательный (Дат.) | dative | indirect object; recipient; experiencer in impersonal constructions | кому? чему? |
| 4 | винительный (Вин.) | accusative | direct object; goal of motion (with в/на + acc); duration | кого? что? |
| 5 | творительный (Тв.) | instrumental | instrument; agent of passive; predicate-instrumental of past/future быть; route; time-of-day | кем? чем? |
| 6 | предложный (Предл.) | prepositional / locative | static location (с в/на); topic of speech (с о/об) — only after prepositions | о ком? о чём? где? |

Two minor cases survive in remnants: **vocative** (productive only as the colloquial "shortened" form Маш!, Мам!, Пап! — addressing close family/friends; the historical vocative is preserved in fixed religious formulae like Боже!, Господи!) and **partitive/secondary genitive** (-у/-ю variant for some masculines: *чашка чаю* "a cup of tea" alongside *аромат чая* "aroma of tea"). Most learner grammars treat these as colloquial subforms of the canonical 6.

###### Genders (3)
- **Masculine:** consonant-final (стол, дом, Иван), -й (трамвай), -ь (день, словарь — must be memorized)
- **Feminine:** -а/-я (книга, неделя), -ь (ночь, мать — must be memorized — distinct from masc -ь nouns by paradigm)
- **Neuter:** -о/-е/-ё (окно, поле, ружьё), -мя (10 nouns: имя, время, племя, бремя, темя, семя, стремя, пламя, знамя, вымя — all neuter, all decline irregularly)
- **Common gender (общий род):** ~50 nouns ending in -а/-я that take masculine or feminine agreement based on the actual referent: *сирота* (orphan), *судья* (judge), *коллега* (colleague). *Этот сирота* (this male orphan) vs. *Эта сирота* (this female orphan).

###### Animacy (subtype of masculine)
A grammatical feature visible only in:
- **Masculine singular accusative:** **animate masc acc = gen** (вижу мальчика, gen-shaped), **inanimate masc acc = nom** (вижу стол, nom-shaped). This is the single most-tested disambiguation in beginner Russian morphology.
- **Plural accusative (all genders):** **animate pl acc = gen pl**, **inanimate pl acc = nom pl**. (вижу студентов = gen-shaped; вижу столы = nom-shaped.)

The validator must require gender + animacy on every masculine accusative noun and on every plural accusative noun.

###### Numbers (2)
- Singular and plural. **No dual** (lost from Old East Slavic, vestigial in numerals 2/3/4 which take genitive singular, see "Numeral agreement").
- **Pluralia tantum** (plural-only): ножницы (scissors), штаны (pants), очки (glasses), сутки (24-hour day), часы (clock/watch), деньги (money), брюки (trousers), сани (sled). They take plural agreement and have no singular form.
- **Singularia tantum** (singular-only): молоко (milk), любовь (love), счастье (happiness), мебель (furniture), посуда (dishes), одежда (clothing), народ (people, the people).

###### Three Declension Classes
- **1st declension:** -а/-я feminines (книга, неделя) AND a small set of -а/-я masculines referring to people (мужчина, дядя, юноша, староста). Hard stem (-а) vs. soft stem (-я) yields ending alternations (книга/нога/мама vs. неделя/Таня/семья).
- **2nd declension:** consonant-final masculines (стол, дом, врач), -о/-е/-ё neuters (окно, поле). Soft-sign masculines like день, день, словарь pattern with this class but with soft-stem endings.
- **3rd declension:** -ь feminines (ночь, дверь, мать, дочь). The two kinship terms мать and дочь insert -ер- in oblique cases (дочери, дочерью, дочерям, ...).

###### Sample Paradigm — Hard Masculine (стол "table")
| Case | Singular | Plural |
|---|---|---|
| Nom | стол | столы |
| Gen | стола | столов |
| Dat | столу | столам |
| Acc (inanim) | стол | столы |
| Inst | столом | столами |
| Prep | (о) столе | (о) столах |

###### Sample Paradigm — Hard Feminine (книга "book")
| Case | Singular | Plural |
|---|---|---|
| Nom | книга | книги |
| Gen | книги | книг (∅ ending) |
| Dat | книге | книгам |
| Acc (inanim) | книгу | книги |
| Inst | книгой | книгами |
| Prep | (о) книге | (о) книгах |

###### Sample Paradigm — Soft Feminine 3rd-decl (ночь "night")
| Case | Singular | Plural |
|---|---|---|
| Nom | ночь | ночи |
| Gen | ночи | ночей |
| Dat | ночи | ночам |
| Acc (inanim) | ночь | ночи |
| Inst | ночью | ночами |
| Prep | (о) ночи | (о) ночах |

###### Genitive Plural — A Rogues' Gallery
Genitive plural is the morphological monster of Russian — multiple competing endings determined by gender, stem-final consonant, and historical accident:
- **-ов / -ев** for hard/soft masculines: столов, врачей (after sibilant + stress shift), музеев
- **Zero ending (∅)** with possible insertion of fleeting vowel for feminines and neuters: книга → книг, окно → окон (fleeting -о-), сестра → сестёр (fleeting -ё-), студентка → студенток (fleeting -о-)
- **-ей** for soft feminines and 3rd-declension feminines: ночей, дверей, мужей (masc), полей (neut)
- The choice is **lexicalized** and a major learner difficulty.

##### Adjectival Inflection
Russian adjectives have **two parallel paradigms**: **long form** (declined, full agreement, attributive + predicative) and **short form** (predicative-only, agreement in gender + number only, no case).

###### Long Form
- Agrees with its head noun in **case (6) × gender (3) × number (2) × hard/soft stem class** ≈ 20+ ending slots per adjective.
- Used both attributively (красная книга — "the red book") and predicatively (книга красная — "the book is red", more permanent/inherent than the short form).

###### Sample Hard-Stem Long-Form Paradigm — новый "new"
| Case | Masc sg | Neut sg | Fem sg | Pl (all genders) |
|---|---|---|---|---|
| Nom | новый | новое | новая | новые |
| Gen | нового | нового | новой | новых |
| Dat | новому | новому | новой | новым |
| Acc (inan) | новый | новое | новую | новые |
| Acc (anim) | нового | новое | новую | новых |
| Inst | новым | новым | новой | новыми |
| Prep | (о) новом | (о) новом | (о) новой | (о) новых |

Soft-stem adjectives (синий "blue") use the soft-vowel set throughout (синего, синему, синим, ...).

###### Short Form
- Predicative-only — never modifies a noun directly attributively.
- Agrees in gender + number only (no case). Forms: masc ∅, fem -а, neut -о, pl -ы (with stem changes possible — fleeting vowels, stress shifts).
- *Он молод.* (He is young.) / *Она молода.* / *Оно молодо.* / *Они молоды.*
- Semantically often more "temporary"/"contextual" than the long form: *Он больной* (he is a sick person, lexically) vs. *Он болен* (he is sick right now).
- Some adjectives lack short form (those denoting permanent attributes like nationality: русский), some lack long form (рад "glad", должен "must, owing").

###### Comparative
- Synthetic: *-ее / -ей* (новее, краснее), *-е* with stem-consonant alternation (старше, выше, тише, дороже)
- Periphrastic: *более* + adjective long form (более красивый "more beautiful")
- Suppletive: хороший → лучше; плохой → хуже; маленький → меньше; большой → больше
- Synthetic comparative is **uninflected** (a frozen form)

###### Superlative
- *самый* + long-form adjective (самый красивый — "the most beautiful")
- Synthetic *-ейший / -айший* (after sibilants): красивейший, величайший — high register, often emphatic rather than truly superlative
- *наи-* prefix on the comparative: наилучший (the best)

##### Pronominal Inflection

###### Personal Pronouns (full 6-case paradigm × 6 persons)
| | 1sg | 2sg | 3sg.m | 3sg.f | 3sg.n | 1pl | 2pl/formal-2sg | 3pl |
|---|---|---|---|---|---|---|---|---|
| Nom | я | ты | он | она | оно | мы | вы | они |
| Gen | меня | тебя | его | её | его | нас | вас | их |
| Dat | мне | тебе | ему | ей | ему | нам | вам | им |
| Acc | меня | тебя | его | её | его | нас | вас | их |
| Inst | мной | тобой | им | ей/ею | им | нами | вами | ими |
| Prep | (обо) мне | (о) тебе | (о) нём | (о) ней | (о) нём | (о) нас | (о) вас | (о) них |

Note the n- prefix on 3rd-person forms after a preposition: *с ним* (with him), *у неё* (at her place), *о них* (about them).

###### Reflexive Pronoun себя
- **No nominative form** — exists only in 5 oblique cases. Coreferent with the clause subject.
- Gen/Acc: себя — *Он любит себя.* (He loves himself.)
- Dat: себе — *Она купила себе книгу.* (She bought herself a book.)
- Inst: собой — *Он гордится собой.* (He's proud of himself.)
- Prep: (о) себе — *Я расскажу о себе.* (I'll tell about myself.)

###### Possessive Pronouns / Determiners
- 1sg/2sg/1pl/2pl: мой, твой, наш, ваш — fully decline like adjectives, agree with the **possessed**, not the possessor
- 3sg/3pl: его, её, их — **invariant** (do not decline; same form in all cases); agreement is with the possessor, captured by the (frozen) gender/number suffix
- **Reflexive possessive свой** — used when the possessor is coreferent with the clause subject. *Иван взял свою книгу.* (Ivan took **his (own)** book.) vs. *Иван взял его книгу.* (Ivan took **his (someone else's)** book.) The свой / его distinction is one of the trickiest disambiguations for L2 learners.

###### Demonstratives
- **этот** (this — proximal) and **тот** (that — distal). Both decline through 6 cases × 3 genders × 2 numbers like adjectives.
- *этот стол / эта книга / это окно / эти столы* — base forms
- Genitive: этого / этой / этого / этих
- Inst: этим / этой / этим / этими
- ...etc. Same patterns for тот / та / то / те.
- **Это** also functions as an invariant demonstrative pronoun ("this/it/that"): *Это книга.* (This [is] a book.) — predicate-fronting copular construction.

###### Interrogative / Relative Pronouns
- **кто** (who — animate) — declines through 6 cases: кто, кого, кому, кого, кем, (о) ком. Always takes masculine singular agreement even when referring to women: *Кто пришёл?* (Who came [masc sg form]?)
- **что** (what — inanimate / propositional) — что, чего, чему, что, чем, (о) чём. **Critical disambiguation:** что is also the complementizer ("that"). Distinguish by:
  - Pronoun what: subject/object of its own clause, can be questioned over.
  - Complementizer that: introduces a finite subordinate clause; cannot be questioned.
- **который** (which/who — relative) — full adjectival paradigm; agrees with antecedent in gender + number, takes case from its function in the relative clause.
- **какой** (what kind / which) — adjectival paradigm; interrogative or exclamative.
- **чей** (whose) — possessive interrogative; adjectival paradigm.

###### Indefinite Pronouns (composed with -то / -нибудь / -либо / кое-)
- **-то** ("some specific X but I don't recall / it's not relevant"): кто-то (someone — specific), что-то, какой-то, где-то
- **-нибудь** ("any X / some X or other — non-specific, often in questions/conditionals/futures"): кто-нибудь, что-нибудь, какой-нибудь, где-нибудь
- **-либо** (formal/literary equivalent of -нибудь): кто-либо, что-либо
- **кое-** ("a certain X — speaker has a referent in mind"): кое-кто, кое-что, кое-где
- The base wh-word (кто, что, какой, где, когда) declines normally, with the suffix attached.

###### Negative Pronouns (n-words)
- **никто** (nobody) — declines like кто; combines with не on the verb: *Никто не пришёл.*
- **ничто** (nothing) — declines like что; *Ничего не случилось.* (Nothing happened — gen of negation on ничего.)
- **никакой** (no kind) — adjectival paradigm; *Никакой книги нет.*
- **ничей** (nobody's) — adjectival paradigm
- **некого / нечего** (nobody / nothing — for) + dative + infinitive — special construction without a nominative form: *Мне некого спросить.* (There's nobody for me to ask.) / *Ему нечего делать.* (He has nothing to do.)
- **никогда / нигде / никуда / никак** — negative adverbs.

##### Verbal Inflection — The Second Pillar of Difficulty

###### Aspect — The Defining Feature
**Every verb belongs to an aspectual pair**: an imperfective (несовершенный вид, нсв) ↔ perfective (совершенный вид, св) partner. This is NOT an inflection — it is **lexical** — but it must be tagged on every verb because it determines tense interpretation.

- **Imperfective** describes ongoing, repeated, habitual, or unbounded action: писать (to write — process), читать (to read — process)
- **Perfective** describes completed, telic, single-event action: написать (to write [something to completion]), прочитать (to read [through])

Pair formation patterns (all idiosyncratic — must be lexicalized):
- **Prefixation:** писать → написать, читать → прочитать, делать → сделать, видеть → увидеть, слышать → услышать, говорить → сказать (suppletive!), знать → узнать
- **Suffix change:** давать → дать, вставать → встать, открывать → открыть, изучать → изучить
- **Stress shift only:** засыпа́ть (impf, "fall asleep, repeatedly/process") vs. засы́пать (impf, "pour into") — note: this is a homograph trap, not a true aspectual pair
- **Suppletion:** говорить ↔ сказать, брать ↔ взять, ловить ↔ поймать, класть ↔ положить, ложиться ↔ лечь, садиться ↔ сесть, становиться ↔ стать
- **Bi-aspectual verbs:** велеть, женить, использовать, организовать, обещать — same form serves both aspects; resolved by context.

The validator MUST tag every verb with its aspect.

###### Tense × Aspect Interaction (the system-defining table)

| | Imperfective | Perfective |
|---|---|---|
| **Past** | писал/-а/-о/-и (was writing, used to write, wrote-without-completion) | написал/-а/-о/-и (wrote-and-finished) |
| **Present** | пишу, пишешь, пишет, пишем, пишете, пишут (am writing) | **— (does not exist)** — perfective has no present-tense interpretation |
| **Future** | буду/будешь/.../будут писать (will be writing — periphrastic with быть-fut) | напишу, напишешь, напишет, напишем, напишете, напишут (will write — same conjugation pattern as imperfective present, but applied to perfective stem yields future meaning) |

Critical asymmetry: **present tense is imperfective-only**. Conjugating a perfective verb with present-tense endings yields **future** semantics. *Напишу* = "I will write [and finish]". *Пишу* = "I am writing / I write".

The future of imperfective verbs is **periphrastic**: the conjugated future of быть (буду, будешь, будет, будем, будете, будут) + the imperfective infinitive: *Я буду писать.* (I will be writing / I will write [as an ongoing activity].)

###### Person × Number × Gender Marking
- **Present (imperfective) and "perfective future" (= perfective conjugated with present endings):** marked for person (1/2/3) × number (sg/pl). Gender NOT marked.
- **Past tense (both aspects):** marked for **gender (m/f/n) × number (sg/pl)**, NOT person. Pronoun must usually appear to disambiguate person.
  - *я писал* (m) / *я писала* (f) — gender of the speaker visible.
  - *они писали* — plural, no gender distinction.
- **Future of imperfective:** auxiliary быть carries person/number; lexical verb is infinitive.

###### Conjugation Classes
- **1st conjugation:** thematic vowel -е/-ё in the 2sg/3sg/1pl/2pl. Endings: -у/-ю, -ешь/-ёшь, -ет/-ёт, -ем/-ём, -ете/-ёте, -ут/-ют. Examples: писать (пишу, пишешь, пишет, ...), читать (читаю, читаешь, ...), идти (иду, идёшь, идёт, ...).
- **2nd conjugation:** thematic vowel -и. Endings: -у/-ю, -ишь, -ит, -им, -ите, -ат/-ят. Examples: говорить (говорю, говоришь, говорит, ...), любить (люблю, любишь, любит, ...). Note the 1sg consonant mutation in many 2nd-conj verbs (любить → люблю, ходить → хожу, видеть → вижу).
- **Irregular verbs:** быть (есть, only 3sg in standard usage), есть (eat — irregular: ем, ешь, ест, едим, едите, едят), дать (perfective give — дам, дашь, даст, дадим, дадите, дадут), хотеть (mixed — хочу, хочешь, хочет, хотим, хотите, хотят).

###### Mood
- **Indicative:** unmarked; covers past/present/future across both aspects.
- **Imperative:** stem + -й (after vowel: читай!), -и (after consonant: пиши!), -ь (after soft consonant: режь!) for sg-informal; +те for pl/formal.
- **Conditional:** past tense + particle бы. *Я бы пошёл, если бы знал.* (I would have gone if I had known.) The particle бы is **clitic-like** — typically attaches to a fronted constituent (subject, wh-word, or first stressed word). Russian does not distinguish "would" from "would have"; the same form covers present-counterfactual, past-counterfactual, and hypothetical.

###### Voice
- **Active:** unmarked.
- **Passive:** typically formed via:
  - Reflexive *-ся* on imperfective: *Книга читается легко.* (The book reads easily.)
  - Short-form past passive participle on perfective: *Книга прочитана.* (The book has been read.) Agent in instrumental: *Книга прочитана студентом.*
  - Short-form present passive participle (rare, formal): *Закон уважаем всеми.* (The law is respected by all.)

###### Reflexive Verbs (-ся / -сь)
The clitic -ся (after consonant) / -сь (after vowel) attaches to the verb form. Functions:
1. **True reflexive:** action returns to subject — *умываться* (wash oneself), *одеваться* (dress oneself).
2. **Reciprocal:** two subjects act on each other — *встречаться* (to meet [each other]), *обниматься* (to embrace).
3. **Passive (with imperfective):** *Здесь продаются книги.* (Books are sold here.)
4. **Middle / autocausative:** spontaneous event — *Дверь открылась.* (The door opened [by itself].)
5. **Lexicalized intransitive:** verb has no non-reflexive partner in modern Russian — *смеяться* (to laugh), *бояться* (to fear), *нравиться* (to please/be liked), *улыбаться* (to smile), *становиться* (to become).
6. **Inherent passive of state:** *кажется, что...* (it seems that...) — impersonal -ся construction.

The validator must accept any of these labels but the meaning text must indicate which subtype is at play.

###### Verbs of Motion — A Self-Contained Subgrammar
Russian distinguishes **14 pairs** of imperfective verbs of motion based on the **determinate / indeterminate** distinction:
- **Determinate (направленный):** unidirectional, on the way, in progress toward a destination — идти (going [there now]), ехать (riding [there now], by vehicle), бежать, плыть, лететь, нести, везти, вести, гнать, тащить, катить, лезть, ползти, брести.
- **Indeterminate (ненаправленный):** multidirectional, habitual, capability, round-trip — ходить, ездить, бегать, плавать, летать, носить, возить, водить, гонять, таскать, катать, лазить, ползать, бродить.

Both are imperfective. Adding a prefix to either yields a perfective verb (the prefixed form's aspect/aktionsart depends on the prefix):
- по- + идти → пойти (perf, "set off / go" — initiation of motion)
- при- + идти → прийти (perf, "arrive")
- у- + идти → уйти (perf, "leave / depart")
- про- + ходить (note: indeterminate base!) → проходить (impf, "to pass through" — derived imperfective from perfective пройти)

The validator must tag each motion verb's role (determinate vs. indeterminate vs. prefixed-perfective vs. prefixed-imperfective) for advanced-level learners.

###### Participles (4 types — all decline as long-form adjectives)
1. **Present active participle (-ущ/-ющ/-ащ/-ящ):** *читающий* (the one who is reading) — formed from imperfective verbs only.
2. **Past active participle (-вш/-ш):** *читавший* (the one who was reading), *прочитавший* (the one who has read) — both aspects.
3. **Present passive participle (-ем/-им):** *читаемый* (being read) — formed from imperfective transitive verbs; rare in modern speech, more in writing.
4. **Past passive participle (-нн/-енн/-ённ/-т):** *прочитанный* (read [as an adjective]), *написанный* (written), *взятый* (taken) — formed from perfective transitive verbs; the **short form** of this participle is the principal means of forming the perfective passive.

Participles function attributively (modifying nouns) and form their own clauses (participial phrases bracketed by commas).

###### Gerunds (deepričastije, вербальные наречия) — invariable
Russian "gerunds" (деепричастия) are NOT noun-like (despite the English term) — they are **verbal adverbs**. Two forms:
- **Present gerund (-я / -а):** *читая* (while reading), *говоря* (while speaking) — from imperfective.
- **Past gerund (-в / -вши):** *прочитав* (having read), *написав* (having written) — from perfective.

They modify verbs, denote a secondary action with the same subject as the main clause, and never inflect: *Читая книгу, она улыбалась.* (While reading the book, she smiled.) The gerund's subject MUST coincide with the main-clause subject — a structural rule rigidly enforced in Russian (a "dangling gerund" is a serious style error).

##### Adjectival/Adverbial Inflection
- **Adverbs from adjectives:** generally take the form of the neuter short form: красивый → красиво, быстрый → быстро, хороший → хорошо, плохой → плохо. *Он быстро бежит.* (He runs quickly.)
- **Adverbs are completely uninflected.**
- **Comparative adverb** = comparative adjective form: *быстрее*, *лучше*.

#### Morphological Complexity
- **Highly fusional** — single endings encode multiple features simultaneously
- **Stress-conditioned alternations** — endings и/ы, и/е, о/е, я/а alternate by spelling rules + stem class
- **Mobile stress** — stress can shift across the inflectional paradigm in rule-bound but lexicalized patterns (окно́ → о́кна, голова́ → го́ловы)
- **Fleeting vowels (беглые гласные)** — о/е inserted/deleted between consonants depending on syllable count: окно (sg) → окон (gen pl, fleeting -о-), отец (nom) → отца (gen, deleted -е-)
- **Consonant alternations in conjugation:** к/ч (пеку → печёшь), г/ж (могу → можешь), х/ш, з/ж (везу → везёшь), с/ш (писать → пишу), т/ч (хотеть → хочу), д/ж (видеть → вижу), б/бл/п/пл/в/вл/м/мл (любить → люблю, спать → сплю)
- **Productive derivational morphology:** prefixes (especially aspectual: на-, про-, за-, по-, вы-, в-, у-, при-, до-, пере-, под-, от-, раз-, с-, без-, не-) and suffixes (-тель/-ник/-ист/-щик agentive, -ость/-ство/-изм abstractive, -ка diminutive/feminine-agentive, -ушка/-енька endearment, -ище augmentative)

## Grammatical Categories

### Open Classes (Content Words)

#### Nouns
- **Common vs. Proper:** Distinguished by capitalization (книга vs. Москва, Иван — names always capitalized; titles, days, months are NOT)
- **Count vs. Mass:** Count nouns inflect normally for plural (стол → столы); mass nouns (вода, хлеб, молоко) form plural only with semantic shift (вино → вина "varieties of wine"). Numerals 2/3/4 cause mass coercion ambiguity.
- **Number:** Singular / plural — see morphology section
- **Concrete vs. Abstract:** Affects gender assignment and agreement
- **Collective:** народ (people, the people), молодёжь (youth) — singular morphology, sometimes plural verb agreement informally
- **Gender:** masculine / feminine / neuter / common — assignment is mostly inflectionally predictable from the nom-sg ending, with a few hundred exceptions to memorize (especially -ь nouns)
- **Animacy:** masculine animate vs. inanimate (visible in acc sg); plural animate vs. inanimate (visible in acc pl)

#### Verbs
The Russian verb is the densest morphological structure in the language.

##### By Function
- **Lexical verbs:** carry semantic content (читать "read", идти "go", знать "know")
- **Auxiliary быть:** essential in past (был/была/было/были) and future (буду + impf inf), null in present
- **Modals:** мочь (can/be able), хотеть (want), должен (must — short-form adjective, not a verb!), нужно/надо (need — impersonal predicate), нельзя (must not / cannot — impersonal predicative), можно (it's possible — impersonal predicative)
- **Copular в/у-construction:** Russian uses **у меня есть книга** ("at me there-is book" = I have a book) for possession — there is no `to have` verb in standard Russian. The instrumental case marks predicates of past/future быть: *Он был студентом.* (He was a student.)

##### By Transitivity
- **Intransitive:** спать, идти, существовать
- **Transitive:** читать (что — acc), знать (что — acc)
- **Ditransitive:** дать (кому — dat, что — acc): *Я дал ему книгу.*
- **Verbs governing oblique cases (NOT acc):** important class — these verbs take a non-accusative direct object:
  - + gen: бояться, избегать, стесняться, добиваться, требовать, лишать
  - + dat: помогать, мешать, верить, советовать, удивляться, нравиться, принадлежать, звонить, отвечать, обещать, доверять, угрожать, завидовать
  - + inst: пользоваться (use), управлять (govern, drive), руководить, заниматься, восхищаться, гордиться, интересоваться, любоваться, владеть
  - The validator must tag the governed case for these verbs.

##### By Aspect
- **Imperfective only:** ongoing/habitual; includes all verbs of motion (in their bare-stem form), most stative verbs (быть, знать, любить, жить — though some have dialectal/semantic perfectives)
- **Perfective only:** rare — typically prefixed motion verbs of single event (поспать "have a nap")
- **Aspectual pairs:** the default — every common verb belongs to a pair
- **Bi-aspectual:** велеть, женить(ся), использовать, организовать, обещать — same form, both aspects (context-resolved)

#### Adjectives
- **Long form (declined):** красивый, новый, большой — agrees in 6 cases × 3 genders × 2 numbers
- **Short form (predicative):** красив, нов, велик — agrees in gender + number only (no case)
- **Comparative:** красивее, новее, больше (suppletive) — uninflected
- **Superlative:** самый красивый (analytic), красивейший (synthetic)
- **Order in the noun phrase:** typically determiner → quantifier → ordinal → adjective(s) → noun: *эти три моих новых русских словаря* ("these three new Russian dictionaries of mine")

#### Adverbs
- **Manner:** быстро, медленно, осторожно (mostly = neuter short adjective)
- **Temporal:** сейчас, теперь, тогда, всегда, никогда, иногда, часто, редко, давно, недавно, рано, поздно
- **Locative:** здесь, там, везде, нигде, дома (at home), внутри (inside), снаружи (outside)
- **Directional:** сюда (hither), туда (thither), отсюда, оттуда — distinct from locatives
- **Degree:** очень, весьма, довольно, слишком, почти, едва, чуть-чуть
- **Sentence (disjuncts):** конечно, разумеется, видимо, кажется, наверное
- **Conjunctive (linking):** однако, поэтому, кроме того, тем не менее, следовательно
- **Focus:** только, даже, тоже, также, именно
- **Negation:** не (preverbal), ни (emphatic/scalar)

### Closed Classes (Function Words)

#### Pronouns (sub-types)
- **Personal:** я, ты, он, она, оно, мы, вы, они — fully inflected (see paradigm table)
- **Reflexive:** себя — 5 oblique cases, no nominative
- **Possessive (declined):** мой, твой, наш, ваш, свой — adjectival paradigm
- **Possessive (invariant):** его, её, их — frozen genitive forms of 3rd-person personal pronouns
- **Demonstrative:** этот, тот, такой, столько (declined); это (invariant deictic)
- **Interrogative:** кто, что, какой, который, чей, сколько, где, куда, откуда, когда, зачем, почему, как
- **Relative:** который (most common), кто (with antecedent тот), что (with antecedent то), какой, чей
- **Indefinite:** -то / -нибудь / -либо / кое- series
- **Negative:** никто, ничто, никакой, ничей, никогда, нигде, никуда, никак; некого, нечего (special construction)
- **Universal:** весь (all — declined: весь, вся, всё, все), каждый (each), всякий (every kind), любой (any)

#### Determiners
Russian has **no articles** (no definite/indefinite distinction marked grammatically). Definiteness is conveyed by:
- Word order (definite tends to be sentence-initial as topic; indefinite sentence-final as rheme)
- Demonstratives (этот/тот) when emphatic
- Possessives
- Bare nouns (default — context-resolved)

This is a **major contrast with English/German** and a perennial L2 difficulty in both directions.

#### Prepositions
**Every Russian preposition governs a specific case** (or two, with a meaning split). The validator must tag the governed case.

| Preposition | Case(s) Governed | Meaning |
|---|---|---|
| в | acc (motion-into) / prep (location-in) | in, into |
| на | acc (motion-onto) / prep (location-on) | on, onto, at |
| под | inst (location) / acc (motion-under) | under |
| над | inst | above |
| перед | inst | in front of, before |
| за | inst (location-behind) / acc (motion-behind, time duration) | behind, beyond, for (purpose) |
| между | inst | between |
| с | gen (from-down/off) / inst (with-co) | from, off / with |
| у | gen | at the place of, by, near (also: possession marker) |
| к | dat | toward, to (a person) |
| от | gen | from (a source) |
| из | gen | out of, from |
| до | gen | until, up to, before |
| после | gen | after |
| во время | gen | during |
| без | gen | without |
| для | gen | for (the benefit of) |
| из-за | gen | because of, from behind |
| из-под | gen | from under |
| через | acc | across, through, in (time-from-now) |
| по | dat (along, by, according-to) / acc (up-to, including) / prep (after) | along, by, according to |
| о / об / обо | prep | about (topic) |
| при | prep | at, in the presence of, attached to |
| ради | gen | for the sake of |
| вокруг | gen | around |
| против | gen | against |
| вместо | gen | instead of |
| благодаря | dat | thanks to |
| согласно | dat | in accordance with |
| вопреки | dat | despite |

The в/на + acc vs. prep alternation (motion vs. location) is the single most-tested preposition disambiguation: *в школу* (acc — going to school) vs. *в школе* (prep — at school).

#### Conjunctions
- **Coordinating:** и (and), а (and/but — contrastive), но (but), или (or), либо…либо (either…or), да (and — colloquial/literary), не только…но и (not only…but also), ни…ни (neither…nor)
- **Subordinating (complementizer):** что (that), чтобы (so that, in order that, used with subjunctive sense)
- **Subordinating (causal):** потому что, так как, поскольку, оттого что, ибо (literary)
- **Subordinating (temporal):** когда, пока, как только, пока не, после того как, прежде чем
- **Subordinating (conditional):** если, если бы, раз
- **Subordinating (concessive):** хотя, хоть, несмотря на то что
- **Subordinating (comparative):** чем (than), как (as, like), словно, будто, как будто

#### Particles
A heterogeneous class — function words contributing pragmatic, modal, or scalar meaning:
- **Question particle:** ли (yes/no question, formal — fronts after the focused word)
- **Conditional / subjunctive:** бы (forms conditional with past tense)
- **Negation:** не (sentential or constituent negation)
- **Emphatic negation:** ни (scalar minimizer; required after negative pronouns; "even one")
- **Contrastive emphasis:** же (after all, in fact; emphasizes a topic-shift or contradiction)
- **Discourse:** вот (here is, behold), вон (over there), уж (already, intensifier), ведь (after all, you know), а (well — turn-initial), и (also, even — focus), даже (even), только (only), лишь (just/only — bookish), именно (precisely)
- **Modal/affective:** мол (allegedly, reported), де (allegedly, archaic), якобы (supposedly), пусть/пускай (let — 3rd-person imperative), давай(те) (let's — 1pl/2pl imperative formation)
- **Affirmative/Negative answer particles:** да (yes), нет (no), конечно (of course), ладно (OK)

The advanced complexity tier should split the particle category into individual roles (ли, бы, не, ни, же) with distinct color codes — they have radically different semantics.

#### Numerals
A morphological hybrid — numerals trigger specific case requirements on the noun they quantify:

- **1 (один, одна, одно, одни)** — adjective-like; agrees in gender + number + case with the noun. *одна книга, одного стола.*
- **2, 3, 4 (два/две, три, четыре)** — when in nominative or accusative-inanimate, **the noun goes into genitive singular**: *два стола, три книги, четыре окна.* In other cases, the numeral and noun match in case (двух столов, gen pl).
- **5–20, тысяча, миллион** — when in nominative or accusative-inanimate, **the noun goes into genitive plural**: *пять столов, десять книг, двадцать окон.* In other cases, all elements agree in case.
- **Higher complex numerals:** the LAST element controls noun case: *двадцать один стол* (21 + nom-sg), *двадцать две книги* (22 + gen-sg, since the last word is "two"), *двадцать пять столов* (25 + gen-pl, since the last word is "five").
- **Ordinals:** decline like adjectives: первый, второй, третий (irregular soft-stem), четвёртый, пятый, … *Я живу на третьем этаже.* (I live on the third floor.)

The validator MUST tag numeral-induced case shifts.

#### Interjections
- ой, ах, ох, эй, ура, увы, фу, бр, ого, ничего себе, господи, чёрт возьми

## Language-Specific Features

### Unique Grammatical Phenomena

#### The Aspect-Tense Interaction (the defining feature)
Russian conflates the imperfective/perfective distinction with the present/future/past distinction:
- Imperfective infinitive + present-tense conjugation → **present**
- Imperfective infinitive + past-tense morphology → **past imperfective** (process/habit/durative)
- Perfective infinitive + "present-tense" conjugation pattern → **perfective future** (future single completed event)
- Perfective infinitive + past-tense morphology → **past perfective** (completed past event)
- Imperfective infinitive + быть-future + imperfective infinitive → **periphrastic future imperfective** (will be doing)

Every finite verb token MUST be tagged with both aspect AND tense in the analyzer's output. This is non-negotiable for a learner-facing tool.

#### Genitive of Negation
Under sentential negation, a direct object that would canonically be in accusative may shift to **genitive**:
- *Я вижу книгу.* (I see the book — acc)
- *Я не вижу книги.* (I don't see the book — gen, neutral) / *Я не вижу книгу.* (I don't see the [specific] book — acc, more definite)

The genitive marks non-existence/non-affectedness; accusative under negation marks definite/specific objects. The choice is meaning-bearing and a major intermediate-level disambiguation.

#### Genitive of Quantity / Partitive
- After numerals 2/3/4: genitive singular (две книги, три стола)
- After numerals 5+: genitive plural (пять книг, десять столов)
- After quantifiers много, мало, несколько, немного: genitive plural (or genitive singular for mass nouns) — *много книг, много воды*
- Partitive (some-of): genitive — *выпей чаю / чая* (have some tea — partitive form of чай is the secondary genitive чаю or canonical чая)

#### Predicate Instrumental
After past or future of быть, profession/state predicates take **instrumental**:
- *Он был врачом.* (He was a doctor — врач in instr.)
- *Она будет учителем.* (She will be a teacher.)
- Present (with null copula): nominative is canonical: *Он врач.* But "Он есть врач" (with overt есть) is rare and emphatic.

After certain "becoming/considering" verbs the instrumental is also obligatory: становиться, оказаться, считаться, казаться, представляться, являться, делать (with becoming sense).

#### Instrumental of Means / Agent
- **Means:** *писать ручкой* (write with a pen)
- **Agent of passive:** *Книга написана автором.* (The book is written by the author.)
- **Route:** *идти лесом* (walk through the forest), *ехать поездом* (travel by train)
- **Manner:** *говорить шёпотом* (speak in a whisper)
- **Time of day:** *утром, днём, вечером, ночью* (in the morning/afternoon/evening/at night)

#### The Reflexive -ся Polysemy
The same morpheme -ся attaches to almost any verb stem, producing:
- True reflexive (умывается = washes self)
- Reciprocal (целуются = kiss each other)
- Passive (книга пишется — the book is being written)
- Middle/spontaneous (дверь открылась = the door opened)
- Inherent reflexivum tantum (смеяться, нравиться, бояться)

The disambiguation is contextual. The validator should accept any of these labels but require the meaning text to identify which.

#### Free Word Order with Information-Structure Encoding
The overt morphological case marking decouples grammatical relations from word position. Speakers exploit this for fine-grained focus/topic control:
- *Иван любит Машу.* (Ivan loves Masha — neutral, "tell me about Ivan")
- *Машу любит Иван.* (Masha is loved by Ivan / It's Masha that Ivan loves — focus on Иван)
- *Любит Иван Машу.* (Ivan does love Masha — emphatic, narrative)

For analyzer purposes, the syntactic-function tag (subject, direct object, etc.) must be derived from **case**, NOT from position. *Машу* is the direct object regardless of where it stands in the sentence.

#### Pro-drop and the Null Copula
- Subject pronouns are dropped when verb morphology disambiguates (*Иду* = "I'm going")
- Present-tense быть is silent: *Он студент* (He is a student) — the analyzer must NOT introduce a phantom verb token. The dash in writing (*Москва — столица*) is sometimes used as orthographic placeholder.

#### Negative Concord (Multiple Negation)
Russian requires negative concord — every negative pronoun/adverb in a sentence triggers preverbal не:
- *Никто никогда ничего не говорил никому.* (Nobody ever said anything to anyone — five n-words + не.)
- Omitting не is ungrammatical.

#### Numeral Concord Idiosyncrasy
The 2/3/4 vs. 5+ split (gen sg vs. gen pl noun) is unique among major European languages and a notorious learner error site. The validator must mark every numeral + noun phrase with the induced case.

#### Stress as a Lexical Feature
Stress placement is unpredictable, lexicalized, and movable across the paradigm. Minimal pairs:
- мука́ (flour) vs. му́ка (torment)
- замо́к (lock) vs. за́мок (castle)
- писа́ть (to write) vs. пи́сать (to pee — childish/vulgar)

Standard texts do not mark stress. The analyzer's HTML rendering may optionally render stressed vowels with U+0301 combining acute (especially for beginner output).

#### Vocative Remnants and Address Forms
The historical vocative is dead in standard Russian; the colloquial "shortened vocative" is alive: *Маш!* (Masha!), *Мам!* (Mom!), *Пап!* (Dad!), *Серёж!* (Seryozha!) — formed by deletion of the final -а/-я. Used only in direct address, only with familiar/intimate names.

#### Diminutives and Augmentatives
A productive system of suffixes encoding affect:
- Diminutive: -ка (книжка, девушка), -очка/-ечка (дочка→доченька, девочка), -ушка/-юшка (бабушка), -ик (домик)
- Augmentative: -ище (домище, ручища)
- Pejorative: -ишк (домишко — shabby house)

The diminutive-laden register is a hallmark of intimate/childish/affectionate speech. The analyzer's individual_meaning text should note diminutive status.

## Pedagogical Considerations

### Learning Difficulty Assessment

#### Difficulty Factors for L2 Learners
- **Cyrillic alphabet:** Quick to learn (~few hours), but trap letters (н = n, р = r, в = v, с = s, у = u, х = h, п = p, ё = yo) cause initial mis-readings
- **Cases:** 6 × 3 genders × 2 numbers × declension class × hard/soft = ~70+ surface ending slots; the largest single grammar challenge for English speakers
- **Aspect:** every verb double-coded; choosing the right partner in context is hard for both Romance/Germanic L1s and Sinitic L1s
- **Verbs of motion:** 14 indeterminate/determinate pairs × prefixation = combinatorial explosion
- **Numeral case agreement:** 2/3/4 gen-sg vs. 5+ gen-pl — counterintuitive
- **Genitive of negation:** when to use gen vs. acc under не
- **Stress:** unmarked, unpredictable, mobile across the paradigm
- **Free word order:** hard to learn what's "marked" vs. "neutral" — students overuse SVO and miss pragmatic cues
- **Reflexive свой vs. его/её/их:** subject-coreference is a non-obvious distinction
- **No articles:** speakers of article languages overproduce; speakers of article-less L1s (Mandarin, Japanese, Korean) cope better here

#### Easier Aspects for L2 Learners
- **Phonemic-ish orthography:** spelling is morphophonemic, mostly predictable from spelling
- **No tones**
- **No complex consonant clusters compared to Polish/Czech (Russian still has e.g. встрепенуться but milder than its West Slavic cousins)
- **Pro-drop and null copula** simplify many sentences
- **No complex tense system** beyond past/present/future + aspect

#### Learner Profiles
- **Beginner (A1–A2):** Cyrillic, 6-case nom + acc + prep paradigm in singular, present-tense imperfective conjugation, simple past, basic prepositions, possessives, demonstratives, common adjectives (long form), быть-past, numerals 1-100
- **Intermediate (B1–B2):** All 6 cases in singular and plural, perfective aspect introduction, imperative, conditional с бы, short-form adjectives, comparatives/superlatives, reflexive verbs, verbs of motion (basic determinate/indeterminate), modals, all common participles in passive recognition
- **Advanced (C1–C2):** All 4 participle types productively, gerunds, all 14 motion-verb pairs with full prefix derivations, predicate instrumental, instrumental of agent, genitive of negation distinction, full subordinate-clause repertoire (хотя, чтобы, если бы, ибо, дабы), bookish/literary register, archaic forms (wer ye old participles), aspectual triplets (положить/класть/полагать)

### Common Learning Challenges

#### Frequent Error Patterns
- **Wrong case after preposition:** **в школе** vs. **в школу** (must distinguish locative vs. directional)
- **Wrong aspect choice:** **Я написал письмо два часа* (perfective + duration — wrong; needs imperfective: писал)
- **Wrong gender on adjective:** **красивый книга* (should be красивая книга)
- **Genitive plural ending miscalculation:** **много студент* (should be студентов)
- **Numeral noun-case mismatch:** **пять столы* (should be пять столов — gen pl)
- **Subject-pronoun overuse:** Anglophone learners say *Я я думаю* or insert я redundantly
- **Wrong reflexive pronoun:** *Иван взял его книгу* (his someone-else's) when the speaker meant свою (his own)
- **Word order rigidity:** sticking to SVO when the discourse calls for OVS
- **Mis-using есть vs. null copula in present:** *Он есть студент* (wrong — should be *Он студент*)
- **Direction error in motion verbs:** *я хожу в Москву* (wrong, should be either *еду в Москву* or *часто бываю в Москве* — the indeterminate ходить doesn't take a direction here)
- **Negation case error:** failing to apply genitive of negation in *У меня нет книги*
- **Stress errors:** mispronouncing common pairs

#### Conceptual Difficulties
- **Aspect:** mapping it from one's L1 tense system; especially hard for L1 with no aspect (Romance, Germanic)
- **Definiteness without articles:** how to express "the book" vs. "a book" without articles
- **The 6-case system:** holding 70+ ending slots in productive memory
- **Genitive of negation:** semantic subtlety (existence/affectedness)
- **Predicate instrumental:** counterintuitive case for predicate nominals after past-быть
- **Свой / его-её-их:** the reflexive possessive's subject-coreference rule
- **Word order pragmatics:** when SVO is wrong and OVS is right
- **Verbs of motion:** the determinate/indeterminate distinction is opaque without lots of input
- **The role of -ся:** meaning depends entirely on the host verb
- **Imperative formation:** the -й / -и / -ь choice is stem-conditioned but has many micro-rules

## Technical Implementation Planning

### AI Prompting Strategy

#### Prompt Complexity Levels

##### Beginner
Roles to surface: **noun, verb, adjective, pronoun, preposition, conjunction, adverb, particle (lumped — covers ли/бы/не/ни/же at this level), numeral, interjection**.

Disambiguation requirements at this level:
- Identify case + gender + number for every noun and adjective
- Identify aspect + tense + person + number for every finite verb
- Identify which case each preposition governs
- Mark animacy on every masc-acc noun
- Identify pronouns by person/number/gender
- Avoid advanced terminology (no "participle", no "gerund", no "predicate instrumental")

##### Intermediate
Add roles: **personal_pronoun, possessive_pronoun, possessive_determiner, demonstrative, reflexive_verb, reflexive_pronoun (себя), short_adjective, comparative, superlative, infinitive, imperative, modal_predicate (можно/нужно/нельзя)**.

- Distinguish reflexive свой from его/её/их based on coreference
- Distinguish reflexive verb -ся subtypes (true reflexive / reciprocal / passive / inherent) — lump-tagged as reflexive_verb at this level but explained in individual_meaning
- Mark genitive of negation when present
- Mark numeral-induced case (2/3/4 gen-sg, 5+ gen-pl)
- Distinguish indicative from imperative from conditional (with бы)

##### Advanced
Add roles: **relative_pronoun (который), interrogative_pronoun (кто/что/какой/чей), indefinite_pronoun (-то/-нибудь/-либо/кое-), negative_pronoun (никто/ничто/некого/нечего), present_active_participle, past_active_participle, present_passive_participle, past_passive_participle, gerund (deepričastije — present and past), modal_verb (мочь, хотеть, должен), copula (overt быть when finite), verbal_noun (глагольное имя на -ние/-ение/-тие), particle_li, particle_by, particle_ne, particle_ni, particle_zhe**.

- Identify all 4 participle types
- Identify gerund (verbal adverb) and its subject-coreference
- Mark predicate instrumental, instrumental of agent, instrumental of means
- Distinguish reflexive -ся subtypes (true / reciprocal / passive / middle / inherent)
- Mark determinate vs. indeterminate motion verbs and their prefixed perfective derivations
- Split the particle bucket: ли (interrogative), бы (conditional), не (sentential negation), ни (emphatic/scalar negation), же (contrastive emphasis), вот, ведь, уж — each gets its own role
- Identify subordinate clause types (complementizer что, purpose чтобы, conditional если/если бы, temporal когда/пока, concessive хотя)

#### Language-Specific Prompting
- **Mandate case + gender + number on every nominal:** the prompt must insist on full feature bundles. Underspecified outputs (e.g., just "noun") trigger validation failure.
- **Mandate aspect + tense on every verb:** "verb" alone is rejected; "imperfective present 3sg" is the minimum acceptable label.
- **Mandate animacy on every masculine accusative:** explicit binary tag.
- **Mandate governed case on every preposition.**
- **Mandate aspect-pair partner (where known):** for advanced level, e.g., when tagging *написать*, also note "perfective of писать".
- **Disambiguation reasoning required for that-class ambiguities:** что (pronoun vs. complementizer), как (interrogative vs. comparator vs. like-conjunction), один (numeral vs. indefinite-article-like), это (pronoun vs. deictic copula).
- **Free-word-order awareness:** the prompt must NOT presume SVO; the analyzer reads grammatical relations from case, not position.
- **Reflexive pronoun coreference check:** for свой / себя, the prompt must identify the subject and confirm coreference.
- **Negative concord enforcement:** if any negative pronoun appears, the verb MUST carry не — the validator flags missing не as an analysis error.

### Data Structure Design

#### Output Format Requirements
- **Grammatical Role Mapping:** noun, verb, adjective, adverb, pronoun, preposition, conjunction, particle, numeral, interjection — plus the intermediate/advanced subtypes listed above
- **Morphological Analysis Fields:**
  - `case`: nom | gen | dat | acc | inst | prep
  - `gender`: m | f | n | common
  - `number`: sg | pl | pluralia_tantum | singularia_tantum
  - `animacy`: animate | inanimate (on m-acc and pl-acc nominals)
  - `aspect`: imperfective | perfective | bi-aspectual
  - `tense`: present | past | future
  - `person`: 1 | 2 | 3
  - `mood`: indicative | imperative | conditional
  - `voice`: active | passive | reflexive_middle | reflexive_reciprocal | reflexive_true | reflexive_inherent
  - `degree`: positive | comparative | superlative
  - `declension_class`: 1 | 2 | 3 (for nouns)
  - `stem_class`: hard | soft (for nouns and adjectives)
  - `governed_case`: case (for prepositions)
  - `motion_verb_type`: determinate | indeterminate | prefixed_perfective | prefixed_imperfective (for advanced)
  - `aspect_pair_partner`: lemma (where known)
  - `syntactic_function`: subject | direct_object | indirect_object | predicate_nominal | adjunct | modifier_of_X | head_of_PP

- **`individual_meaning` field (REQUIRED):** Multi-sentence per-word explanation. Must include:
  1. The grammatical role
  2. Full feature bundle (case + gender + number + animacy for nominals; aspect + tense + person + number + mood for verbs; governed case for prepositions)
  3. The word's syntactic function in *this* sentence (e.g., "subject of `читает`", "direct object of `написал`", "head of the prepositional phrase `в школе`")
  4. For ambiguous tokens (что, как, один, это, the бы-particle position, свой vs. его), an explicit disambiguation note
  5. For aspectual verbs: the aspectual partner (where known) and a one-clause explanation of the aspectual nuance ("perfective — denotes the completed action of writing, contrasted with imperfective писать")

- **Confidence Scoring:** 0.0–1.0 per token; aggregate sentence confidence is the mean. Penalize:
  - Missing case/gender/number on a nominal: -0.2
  - Missing aspect/tense on a finite verb: -0.2
  - Missing governed case on a preposition: -0.15
  - Missing animacy on m-acc / pl-acc: -0.1
  - Ambiguous token without disambiguation justification: -0.15

#### Validation Rules
- **Required Fields:** role, individual_meaning (≥30 chars per word in fallback path)
- **Quality Thresholds:**
  - Production confidence ≥ 0.85 (else trigger repair)
  - Fallback path always reports `is_fallback: True` and is capped at 0.3 confidence
  - Multi-clause explanations (no POS-only stubs)
  - Every nominal must carry case + gender + number; every finite verb must carry aspect + tense + person + number; every preposition must carry governed case
- **Fallback Mechanisms:** 5-level parsing chain — (1) direct JSON, (2) markdown code-block-wrapped JSON, (3) JSON repair (trailing commas, unquoted keys, smart quotes), (4) text-pattern extraction over `WORD: ROLE — explanation` lines, (5) rule-based morphological fallback (Cyrillic-aware suffix patterns, lookup tables for closed-class items, position heuristics)

#### Russian-Specific Processing Challenges
- **Disambiguation of что:**
  - Subject/object of its own clause, can be questioned over → **interrogative/relative pronoun** (what/which)
  - Introduces a finite subordinate clause after a verb of speech/cognition → **complementizer** (that)
- **Disambiguation of как:**
  - Wh-word in a question → **interrogative adverb** (how)
  - "Like, as" introducing a comparison → **comparator/conjunction**
  - "When, as" introducing a temporal clause → **subordinator**
- **Disambiguation of это:**
  - Standalone subject/predicate complement → **demonstrative pronoun** (this/it)
  - Predicate-fronting copular ("это книга" = "this is a book") → **deictic copula substitute**
  - In agreement with a noun → **demonstrative determiner** (этот/это/эта/эти form-set)
- **Disambiguation of один:**
  - Numeral "1" → counts an entity
  - Indefinite-article-like (one of, a certain) → introduces a referent
  - Pronoun "alone" — он один = he alone
- **Disambiguation of свой vs. его/её/их:** subject-coreference test — if the possessor is the same as the clause subject, use свой; else use его/её/их.
- **Disambiguation of себя vs. -ся:** себя is an autonomous pronoun (free-standing, declined for case); -ся is a verbal clitic (always attached to the verb).
- **Animacy detection:** for masculine acc nouns, compare the form to nom: if it equals the gen-shaped form, animate; if it equals the nom-shaped form, inanimate.
- **Aspect identification (rule-based fallback):** prefix table (по-, на-, про-, за-, у-, при-, до-, пере-, под-, от-, раз-, с-, вы- = often perfectivizing) + suffix patterns (-ива/-ыва = imperfectivizing); known suppletive pairs (говорить↔сказать, брать↔взять, ловить↔поймать, класть↔положить, ложиться↔лечь, садиться↔сесть, становиться↔стать); bi-aspectual list (велеть, женить, использовать, организовать, обещать).
- **Genitive of negation detection:** if не precedes a finite verb and the direct object is in genitive form, mark as genitive of negation.
- **Numeral concord detection:** for 2/3/4 + nominal, expect gen-sg; for 5+ + nominal, expect gen-pl; flag mismatches.
- **Reflexive -ся subtype classification:** lookup table for inherent reflexives (бояться, нравиться, смеяться, улыбаться, становиться); reciprocal subjects (plural with co-occurrence semantics: целоваться, обниматься, встречаться); middle/spontaneous (open-class); else true reflexive.
- **Vocative recognition:** -∅ vocative (Маш, Мам) is a colloquial register marker; tag the noun as vocative-shortened.
- **Predicate instrumental detection:** after past/future of быть, the complement should be in instrumental — flag if it isn't.

## Production-Ready Features

### JSON Schema Compliance
The analyzer's output must include for every analyzed token:
```
{
  "word": str,
  "lemma": str,                  // dictionary form
  "role": str,                   // canonical POS or sub-type
  "individual_meaning": str,     // ≥30 chars, multi-clause
  "case": str?,                  // nom | gen | dat | acc | inst | prep
  "gender": str?,                // m | f | n | common
  "number": str?,                // sg | pl
  "animacy": str?,               // animate | inanimate
  "aspect": str?,                // imperfective | perfective | bi-aspectual
  "tense": str?,                 // present | past | future
  "person": str?,                // 1 | 2 | 3
  "mood": str?,                  // indicative | imperative | conditional
  "voice": str?,                 // active | passive | reflexive_*
  "degree": str?,                // positive | comparative | superlative
  "governed_case": str?,         // for prepositions
  "motion_verb_type": str?,      // determinate | indeterminate | prefixed_*
  "aspect_pair_partner": str?,   // lemma of partner aspectual form
  "stress_position": int?,       // 1-indexed syllable, optional
  "syntactic_function": str?,    // subject | direct_object | …
  "confidence": float            // 0.0–1.0
}
```

Plus sentence-level fields:
```
{
  "sentence_structure": str,     // free-text overview, e.g., "SVO declarative, present imperfective, no overt subject (pro-drop), null copula"
  "tense_aspect": str,           // global tense/aspect summary
  "voice": str,                  // global voice
  "word_order": str,             // SVO | OVS | OSV | …
  "is_fallback": bool,           // True iff rule-based fallback was used
  "confidence": float
}
```

### APKG Output and HTML Color Coding
The analyzer's color scheme (`get_color_scheme(complexity)`) must declare HTML hex colors for each role at each complexity level. The grammar processor consumes these colors and emits `<span style="color: …">word</span>` markup for the front of each Anki card. **Critical invariant:** the analyzer's POS labels and colors must NOT be remapped by `grammar_processor._convert_analyzer_output_to_explanations()` — it passes them through verbatim. Suggested palette:
- noun = saturated blue (#1F77B4)
- verb = saturated red (#D62728)
- adjective = green (#2CA02C)
- adverb = orange (#FF7F0E)
- pronoun = purple (#9467BD)
- preposition = teal (#17BECF)
- conjunction = brown (#8C564B)
- particle = dark gray (#7F7F7F)
- numeral = gold (#BCBD22)
- participle = magenta (#E377C2)
- gerund = light pink (#F7B6D2)
- determinate motion verb = bright red (#E41A1C)
- indeterminate motion verb = darker red (#A50F15)
- particle_ne (negation) = black (#000000)
- particle_by (conditional) = dark purple (#5E3C99)
- particle_li (interrogative) = dark blue (#08306B)

Cyrillic glyphs render correctly across all major fonts (Anki uses system fonts; the renderer must specify a fallback that includes Cyrillic — DejaVu Sans, Arial, or Liberation Sans suffice).

### Lazy Imports — CRITICAL
The analyzer module must NOT have `from streamlit_app.shared_utils import …` at module level. The analyzer registry uses `importlib.import_module()` for discovery, and module-level imports of `shared_utils` capture function references at import time, which makes them un-mockable by `unittest.mock.patch()` and causes cross-test contamination in E2E pipeline tests. Move all `streamlit_app.shared_utils` imports inside the `_call_ai()` method body. (See CLAUDE.md "Coding Conventions — Analyzer imports".)

### `_extract_response_text` Null-Guard
The analyzer must defensively check for `None` `.text` attributes on the AI response object before using it. Pattern:
```python
def _extract_response_text(self, response) -> str:
    if response is None:
        return ""
    text = getattr(response, "text", None)
    if text is None:
        return ""
    return text
```

### 5-Level Fallback Parsing Chain (in `ru_response_parser.py`)
1. **Direct JSON parse** — `json.loads(response)` — fastest path
2. **Markdown code-block extraction** — strip leading/trailing ```json fences and reparse
3. **JSON repair** — fix trailing commas, unquoted keys, smart quotes, missing commas; reparse
4. **Text-pattern extraction** — regex over plain-text formats like `WORD: ROLE — explanation`
5. **Rule-based morphological fallback** — `ru_fallbacks.py` consumes the original sentence, applies Cyrillic suffix patterns (`-ть`/`-ти` infinitive, `-л(а/о/и)` past, `-ишь/-ешь/-ёшь` 2sg, `-ом/-ой/-ью` instr, `-у/-ю` acc-fem-sg, `-а/-я/-о/-е/-и/-ы` various ending hits), POS lookup tables (preposition list with governed case, particle list, conjunction list, modal/predicative list, pronoun paradigms), and morphological position heuristics. Output sets `is_fallback: True` so the validator caps confidence at 0.3 regardless of explanation quality.

## Quality Assurance

### Confidence Targets
- **Production threshold:** ≥ 0.85 sentence-level mean confidence required for non-repair acceptance
- **Repair trigger:** if confidence < 0.85, the response parser triggers an AI repair pass at temperature=0.4 (per the project's repair contract); repair is only accepted if it raises confidence
- **Fallback cap:** any output with `is_fallback: True` is hard-capped at 0.3 confidence — explanation quality cannot lift this

### Rule-Based Fallback Quality Bar
The rule-based fallback (`ru_fallbacks.py`) must NEVER emit POS-only stubs. Every word's `individual_meaning` must be ≥30 characters and read as multi-clause natural-English prose. Pattern:
> *"This is a {role} ({lemma}); {feature bundle: case + gender + number + animacy / aspect + tense + person + number}. In the present sentence it functions as the {syntactic_function}. {Optional disambiguation or aspectual nuance note.}"*

Examples:
- *читает*: *"This is a verb (lemma: читать), 3rd-person-singular present-tense imperfective indicative active. It serves as the main predicate of the sentence and takes 'студент' as its subject and 'книгу' as its direct object. The imperfective aspect indicates an ongoing or habitual action; perfective partner is прочитать."*
- *книгу*: *"This is a noun (lemma: книга), feminine inanimate accusative singular, 1st declension hard stem. It functions as the direct object of the verb 'читает', marking the entity being read."*
- *в школе*: (preposition в) *"This is the preposition в governing the prepositional case (here marking static location); together with 'школе' it heads the prepositional phrase serving as a locative adjunct."* / (noun школе) *"This is a noun (lemma: школа), feminine inanimate prepositional singular, 1st declension hard stem. It is the complement of the preposition в, jointly forming a locative adjunct meaning 'at school'."*
- *не вижу книги*: (verb вижу) *"This is a verb (lemma: видеть), 1st-person-singular present-tense imperfective indicative active, with consonant-mutation 1sg form (д→ж). Negated by preceding не."* / (noun книги) *"This is a noun (lemma: книга) in the genitive singular, feminine inanimate. The genitive form here marks the genitive of negation — under sentential negation with не, the direct object shifts from accusative to genitive, signalling non-existence/non-affectedness."*
- *бы*: *"This is the conditional/subjunctive particle бы, marking the clause as a hypothetical or counterfactual; combines with the past-tense form of the verb to form the Russian conditional construction. Particle attaches clitic-like, typically after a fronted constituent."*
- *этот*: *"This is the proximal demonstrative determiner этот, masculine singular nominative hard-stem, agreeing with its head noun. It indicates that the referent is close to the speaker/discourse-recent."*

### Closed-Class Lexicon Coverage Requirements
The fallback's lookup tables must cover at minimum:
- **Personal pronouns (full 6-case × 6-person paradigm):** 36 forms minimum, plus 5-case себя
- **Demonstratives:** этот / тот / такой / столько paradigms
- **Possessive determiners:** мой / твой / наш / ваш / свой full adjectival paradigms; invariant его / её / их
- **Interrogatives/Relatives:** кто / что full paradigms; который, какой, чей adjectival paradigms
- **Indefinites:** -то, -нибудь, -либо, кое- forms of кто/что/какой/где/когда
- **Negatives:** никто, ничто, никакой, ничей, никогда, нигде, никуда, никак, некого, нечего
- **Universal quantifiers:** весь paradigm; каждый, всякий, любой adjectival paradigms
- **30+ most-common prepositions** with governed case(s)
- **Conjunctions:** и, а, но, или, либо, что, чтобы, если, если бы, когда, пока, как, как только, потому что, так как, поскольку, хотя, несмотря на то что, чем
- **Particles:** не, ни, бы, ли, же, вот, вон, ведь, уж, лишь, только, даже, именно, конечно, разумеется, пусть, пускай, давай, давайте, ну
- **Modal predicatives:** можно, нельзя, нужно, надо, должно, стоит, следует, пора
- **Modal verbs:** мочь (могу, можешь, может, можем, можете, могут), хотеть (хочу, хочешь, хочет, хотим, хотите, хотят), уметь, желать, должен/должна/должно/должны (short-form adjective)
- **The быть paradigm:** есть, был, была, было, были, буду, будешь, будет, будем, будете, будут, быть (inf), будь (imp.sg), будьте (imp.pl), бывший (past act ppl), будучи (gerund)
- **Numerals:** один, два, три, четыре, пять-двадцать, тридцать, сорок, пятьдесят, шестьдесят, семьдесят, восемьдесят, девяносто, сто, двести, триста, четыреста, пятьсот, тысяча, миллион + ordinals первый-десятый

### Test Coverage Requirements
The `tests/` directory must include unit tests for each domain component, integration tests, and a Phase 8 E2E mock for all three difficulty levels (beginner / intermediate / advanced) wired into `tests/test_end_to_end_pipeline.py` following the Latvian pattern (`_run_full_pipeline(data, f"russian_{difficulty}", tmp_path)` parameterized).

### Disambiguation Test Cases (mandatory)
The validator and tests must explicitly cover:
1. *Я вижу мальчика.* — мальчика = masc anim acc sg (gen-shaped form because animate)
2. *Я вижу стол.* — стол = masc inan acc sg (nom-shaped form because inanimate)
3. *Я не вижу книги.* — книги = fem gen sg (genitive of negation) — distinct from acc книгу
4. *Он был врачом.* — врачом = predicate instrumental after past быть
5. *Письмо написано Иваном.* — Иваном = instrumental of agent in passive
6. *Он умывается.* — умывается = reflexive_true (-ся true reflexive)
7. *Они встречаются.* — встречаются = reflexive_reciprocal (-ся reciprocal)
8. *Книга легко читается.* — читается = reflexive_passive (-ся passive)
9. *Иван взял свою книгу.* — свою = reflexive_possessive (свой), coreferent with subject Иван
10. *Иван взял его книгу.* — его = invariant 3sg.m possessive; refers to a different person
11. *Что ты читаешь?* — что = interrogative pronoun (acc), object of читаешь
12. *Я знаю, что он пришёл.* — что = complementizer (subordinating conjunction)
13. *Я бы пошёл.* — бы = conditional particle, attaches after first stressed word
14. *Не я разбил окно.* — не = negation, scoping over я (constituent negation)
15. *Никто никогда ничего не говорит.* — negative concord: никто/никогда/ничего + не
16. *Два стола, пять столов.* — два + gen-sg vs. пять + gen-pl
17. *Прочитанная книга.* — прочитанная = past passive participle (long form, agreeing with книга)
18. *Книга прочитана.* — прочитана = past passive participle (short form, predicative)
19. *Читая книгу, она улыбалась.* — читая = present gerund (imperfective deepričastije), subject coreferent with она
20. *Я иду в школу* (motion now) vs. *Я хожу в школу* (habitually) — иду = determinate, хожу = indeterminate
21. *Я пошёл / пришёл / ушёл.* — пошёл (perf, set off) / пришёл (perf, arrived) / ушёл (perf, left)
22. *Я буду писать.* — periphrastic future imperfective (буду + impf inf)
23. *Я напишу.* — perfective future (perfective stem + present-pattern endings)
24. *Это книга.* — это = deictic copula substitute (predicate-fronting demonstrative)
25. *Эта книга интересная.* — эта = demonstrative determiner agreeing with книга

A test fails if the analyzer assigns the wrong category to any of these in the absence of an explicit disambiguation justification.

## Implementation Risks and Challenges

### Technical Complexity
- **Morphological recognition:** ~70+ noun ending slots × hundreds of stems = combinatorial space; requires lemmatization or extensive pattern matching
- **Aspect identification:** without a curated aspect-pair lexicon, perfective/imperfective is unrecoverable from surface alone (some pairs differ only by stress!)
- **Numeral concord:** must implement 2/3/4 vs. 5+ rule and propagate the case shift to the noun
- **Animacy detection:** requires lexical knowledge — cannot be inferred from form alone for masculine acc
- **Genitive-of-negation detection:** requires sentential scope analysis of не
- **Cyrillic tokenization:** must handle ё (often written as е), apostrophe-like ь/ъ, hyphenated compounds (кто-то, друг-друга)
- **Stress reconstruction:** if the renderer needs stress marks, must consult a stress dictionary (zaliznyak grammar dictionary or similar)

### Linguistic Challenges
- **Idiosyncratic prepositional government:** *скучаю по тебе* (dat) vs. *думаю о тебе* (prep) — must be tagged by lookup table
- **Idiomatic case requirements:** *ждать поезд (acc)* vs. *ждать поезда (gen)* — both grammatical, different aspectual nuance (definite known train vs. any train)
- **Subjunctive (чтобы + past):** *Я хочу, чтобы ты пришёл.* — past form пришёл inside чтобы-clause has subjunctive sense, not literal past
- **Mixed conditionals:** *Если бы я знал тогда, я бы был сейчас врачом.* (counterfactual past + present consequence)
- **Word-order ambiguity in case-syncretic forms:** when subject and object happen to have homophonous nom/acc (e.g., neuter sg, fem 3rd-decl), word order disambiguates: *Море видит небо* vs. *Небо видит море* — both grammatical but ambiguous, context-resolved
- **Aspectual triplets:** некоторые verbs have a perfective + two imperfectives (rendering punctual+iterative+habitual): *положить (perf) / класть (impf, single placement) / полагать (impf, abstract — "suppose")*

### AI Prompting Challenges
- **Feature-bundle discipline:** GPT-style models often produce "noun" without case+gender+number — the prompt must mandate the full bundle
- **Aspect specificity:** models default to "verb" without aspect — the validator must reject this
- **Disambiguation discipline:** что/как/один/это require explicit reasoning in individual_meaning
- **Free word order awareness:** models trained on English may impose SVO assumptions, mis-tagging OVS as ungrammatical
- **Reflexive coreference:** свой / себя require subject-tracking, often missed by surface models
- **Numeral concord:** models often miss the 2/3/4 vs. 5+ case-shift rule
- **Stress and orthography:** model output may use ё inconsistently; the validator should normalize ё→е for matching

### Quality Assurance Needs
- **Comprehensive test corpus:** sentences exercising all 6 cases × all 3 genders × singular and plural; aspect pairs in past, present, future contexts; all 4 participle types; gerunds; verbs of motion (determinate/indeterminate, prefixed); negative concord; numerals 1-4-5+ groups; predicate instrumental; genitive of negation; reflexive -ся subtypes; relative clauses with который; conditional with бы
- **Edge cases:** vocative shortenings (Маш, Мам); diminutives; bi-aspectual verbs; aspectual triplets; ё→е normalization; archaic/literary register (ибо, дабы, посему); fixed expressions retaining historical case (слава Богу — dat); Old Church Slavonic borrowings (бытие, ради, для-ради)
- **Performance:** end-to-end analysis must complete in <30 s per sentence (per project's `validate_implementation.py` perf check)
- **Cross-test isolation:** lazy `_call_ai` import (per CLAUDE.md) is mandatory to prevent E2E cross-test mock contamination

## Implementation Roadmap

### Phase 1: Core Infrastructure (this document)
1. Document the linguistic foundation (this file)
2. Define the role inventory at three complexity tiers
3. Specify disambiguation test cases
4. Specify the `individual_meaning` quality bar
5. Specify the 5-level fallback chain

### Phase 2: Directory Structure
1. Create `languages/russian/` scaffold mirroring `languages/german/` and `languages/latvian/`
2. Create `domain/`, `infrastructure/data/`, `tests/` subdirectories
3. Stub the 17 required files

### Phase 3: Domain Components (Opus)
1. `domain/ru_config.py` — language config, role inventory per tier, color scheme, prompt templates
2. `domain/ru_prompt_builder.py` — Jinja2-based AI prompt construction with explicit case + aspect feature-bundle requirements
3. `domain/ru_response_parser.py` — 5-level fallback parsing
4. `domain/ru_validator.py` — 0.85 threshold, natural scoring, fallback cap at 0.3, feature-bundle completeness checks
5. `domain/ru_fallbacks.py` — rule-based morphological fallback (Cyrillic suffix patterns, lookup tables for closed-class items, multi-clause explanations)

### Phase 4: Infrastructure (Sonnet)
1. AI service shim with circuit breaker
2. Lazy import of `streamlit_app.shared_utils` inside `_call_ai`
3. Caching layer for repeated sentence analyses

### Phase 5: Configuration Files (Haiku)
1. `infrastructure/data/grammatical_roles.yaml` — full role inventory with parent links
2. `infrastructure/data/language_config.yaml` — high-level metadata
3. `infrastructure/data/patterns.yaml` — disambiguation rules, suffix patterns, lookup tables (prepositions + governed case, particles, conjunctions, modal predicatives, motion verbs)
4. `infrastructure/data/word_meanings.json` — high-frequency word → POS / lemma / aspect-pair / gender / declension / animacy lookup for fallback
5. `infrastructure/data/aspect_pairs.json` — known imperfective↔perfective aspectual pairs
6. `infrastructure/data/motion_verbs.json` — 14 determinate/indeterminate pairs + common prefixed perfective derivations

### Phase 6: Tests (Sonnet)
1. Unit tests for each domain component
2. Integration tests for the full pipeline
3. Disambiguation test suite (the 25 cases above + variants)

### Phase 7: Deployment Documentation (Haiku)
1. README and changelog
2. Registry integration guide

### Phase 8: E2E Pipeline (Sonnet)
1. Beginner / intermediate / advanced mock data (matched to the role-tier vocabulary in `ru_config.py`)
2. Wire into `tests/test_end_to_end_pipeline.py` per Latvian pattern
3. Generate `tests/reports/pipeline_report_russian_{level}.txt` for each level

## Validation Checklist

- [ ] Confidence ≥ 0.85 on AI path; rule-based fallback hard-capped at 0.3
- [ ] `is_fallback: True` flag emitted by `ru_fallbacks.py` and respected by validator
- [ ] All 25 disambiguation cases pass
- [ ] Lazy import of `streamlit_app.shared_utils` inside `_call_ai`
- [ ] `_extract_response_text` null-guard for None .text
- [ ] Color scheme passes through grammar_processor verbatim (no remap)
- [ ] `individual_meaning` ≥30 chars, multi-clause, names role + case/gender/number/animacy (nominals) or aspect/tense/person/number (verbs) or governed case (prepositions) + syntactic function
- [ ] 5-level fallback parsing chain implemented
- [ ] APKG-compatible HTML output with Cyrillic-safe font fallback
- [ ] All three difficulty levels exercised end-to-end
- [ ] Registry entry added (`russian → "ru"` in `analyzer_registry.py`)
- [ ] Closed-class lookup coverage: 6-case personal pronoun paradigm × 6 persons; reflexive себя 5 oblique cases; этот/тот full paradigm; 30+ prepositions with governed case; particle inventory (не, ни, бы, ли, же, вот, ведь); conjunction inventory; быть paradigm; modal predicatives (можно/нужно/нельзя); 14 motion-verb pairs
- [ ] Aspect-pair lexicon ≥ 500 high-frequency pairs
- [ ] Cyrillic tokenizer handles ё/е normalization, ь/ъ, hyphenated compounds
- [ ] Numeral concord rule applied (2/3/4 + gen-sg, 5+ + gen-pl)
- [ ] Genitive-of-negation rule applied (не + finite verb + gen-shaped object → flag)
- [ ] Animacy tag required on every masc-acc and pl-acc nominal
- [ ] Predicate-instrumental rule applied (after past/future of быть)
