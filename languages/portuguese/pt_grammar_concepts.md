# Portuguese Grammar Concepts and Implementation Guide

## Executive Summary

Portuguese is a Romance language in the Indo-European family, the sixth most-spoken language in the world with approximately 260 million speakers across Portugal, Brazil, Angola, Mozambique, Cape Verde, Guinea-Bissau, São Tomé and Príncipe, East Timor, and Macau. As a highly inflected fusional language with complex grammatical gender, rich verbal morphology, and an intricate clitic pronoun system, Portuguese poses several distinctive challenges for automated analysis. Most notable are: (1) the **clitic placement system** (proclisis vs enclisis vs *mesoclisis* — a near-unique Romance feature), (2) the **personal infinitive** (an inflected non-finite form not found in most Romance siblings), (3) the **ser/estar copula split**, and (4) significant **Brazilian (BR) vs European (PT) divergences** in pronouns, clitic placement, and progressive aspect.

This analyzer follows the Clean Architecture pattern established by the French v2.0 gold standard, with external configuration files, lazy `_call_ai()` imports (per project Coding Conventions), 5-level fallback parsing, and an 85%+ confidence threshold for production deployment. Both Brazilian and European Portuguese are supported as a single analyzer with register-aware disambiguation.

## Language Overview

### Classification and Status
- **Language Family:** Indo-European
- **Branch:** Italic > Romance > Western Romance > Ibero-Romance > West Iberian > Galician-Portuguese
- **Script Type:** Alphabetic (Latin script with diacritics)
- **Writing Direction:** Left-to-right (LTR)
- **ISO 639-1:** `pt` (with regional variants `pt-BR`, `pt-PT`, `pt-AO`, `pt-MZ`)
- **Official Status:** Official language in 9 countries (CPLP — Community of Portuguese Language Countries)
- **Global Speakers:** ~260 million (~232 million native, ~28 million L2)

### Geographic and Cultural Context
- **Primary Regions:** Brazil (~211M), Portugal (~10M), Angola (~30M, mostly L2), Mozambique (~30M, mostly L2), plus Cape Verde, Guinea-Bissau, São Tomé and Príncipe, East Timor, Macau
- **Cultural Significance:** Language of bossa nova, fado, lusophone literature (Pessoa, Saramago, Machado de Assis, Drummond), and a major UN/EU/Mercosul/AU language
- **Dialectal Variation:** Brazilian Portuguese (BR) and European Portuguese (PT) differ in phonology, lexicon, syntax (especially clitic placement and progressive aspect), and orthography (post-2009 Acordo Ortográfico has converged some spelling). African varieties trend toward PT norms with substrate influence.
- **Modern Usage:** Brazil dominates internet content, music, and media; Portugal anchors traditional/literary register and EU institutional Portuguese.

### Script and Writing System
- **Character Set:** 26 Latin letters plus diacritics: á, â, ã, à, é, ê, í, ó, ô, õ, ú, ç
- **Special Letters:** `ã`, `õ` (nasal vowels — orthographically distinctive), `ç` (cedilla)
- **Capitalization:** Standard Latin rules; days/months lowercase (segunda-feira, janeiro)
- **Punctuation:** Standard Western punctuation; em-dash (—) used for direct speech in literary text instead of quotation marks
- **Challenges:** Nasal vowel handling (ã, õ, am, em, im, om, um), tilde-over-vowel disambiguation, ç vs c+e/i, Acordo Ortográfico variants (acção/ação, óptimo/ótimo, facto/fato)

## Grammatical Structure Analysis

### Word Order and Sentence Structure

#### Basic Word Order
Portuguese is canonically **SVO**, but rich verbal morphology allows pro-drop and considerable flexibility, especially in literary/written register and in BR colloquial speech.

- **Declarative:** O gato come o peixe (The cat eats the fish)
- **Pro-drop:** Como o peixe (I eat the fish — subject pronoun omitted; verb morphology indicates 1sg)
- **Questions:** Same word order with rising intonation; or fronted wh-word
  - Yes/no: Você fala português? (Do you speak Portuguese?) — BR
  - Yes/no: Falas português? (Do you speak Portuguese?) — PT, pro-drop
  - Wh: Onde mora o João? / Onde é que o João mora? (Where does João live?)
- **Negation:** Pre-verbal `não` (Eu não falo francês — I don't speak French); double negation common (Ninguém fez nada — Nobody did anything)
- **Complex Sentences:** Relative clauses with `que`, `quem`, `cujo`, `o qual`; subordinate clauses introduced by `que`, `se`, `quando`, `porque`, `embora`, `apesar de`

#### Constituent Order Examples
1. **Simple declarative (BR):** As crianças brincam no parque (The children play in the park)
2. **Pro-drop with subjunctive:** Espero que venhas amanhã (I hope you come tomorrow)
3. **Question (PT):** Aonde vão as crianças? (Where are the children going?)
4. **Negation:** Eu não compreendo (I don't understand)
5. **Relative clause:** O homem que fala português (The man who speaks Portuguese)
6. **Cleft (very common in PT):** É o João que fez isso (It's João who did that)

### Morphological System

#### Inflection Types
- **Nominal Inflection:** Gender (masculine/feminine), number (singular/plural), augmentative/diminutive (-inho/-zinho/-ão)
  - Gender: o gato (m), a gata (f); o livro (m), a mesa (f)
  - Plural: regular -s (livro → livros); -ões/-ães/-ãos for words in -ão (pão → pães, mão → mãos, irmão → irmãos); -is for -al/-el/-ol/-ul (animal → animais)
- **Verbal Inflection:** Person (1/2/3), number (sg/pl), tense (present, preterite, imperfect, pluperfect, future, conditional), mood (indicative, subjunctive, imperative, personal infinitive), aspect, voice (active, passive)
  - 6 persons × 2 numbers, but BR colloquial collapses to 4 (eu/você/ele/a gente/vocês/eles)
  - Synthetic future and conditional in formal register; periphrastic `ir + infinitive` in BR colloquial
- **Adjectival Inflection:** Gender and number agreement with head noun
  - bonito/bonita/bonitos/bonitas (handsome - m.sg/f.sg/m.pl/f.pl)
  - Invariable adjectives in -e or -al: feliz/felizes, simples/simples

#### Morphological Complexity
- **Fusional:** Verb endings encode person + number + tense + mood simultaneously (`falávamos` = 1pl + imperfect + indicative of `falar`)
- **Three Conjugation Classes:** -ar (1st, ~80% of verbs, e.g., falar), -er (2nd, e.g., comer), -ir (3rd, e.g., partir), plus the irregular -or class (pôr and derivatives — compor, dispor, propor)
- **Irregular Verbs:** ~50 highly irregular verbs include ser, estar, ter, haver, ir, vir, pôr, fazer, dizer, ver, vir, querer, poder, saber, dar, trazer, caber, ler, crer
- **Stem Changes:** Vowel raising (e→i, o→u) in some -ir verbs (sentir → sinto; dormir → durmo); hard/soft consonant alternation (ficar → fique, pagar → pague, começar → comece)
- **Derivational:** Rich prefix/suffix system (des-, in-, re-, pre-, anti-, -mente, -ção, -dade, -agem, -mento, -inho/-zinho diminutives, -ão augmentatives)

## Grammatical Categories

### Open Classes (Content Words)

#### Nouns
- **Common vs. Proper:** Capitalization marks proper; some compounds hyphenated (couve-flor, guarda-chuva)
- **Gender:** Grammatical (m/f), with ~85% predictability from endings (-o/m, -a/f, -agem/f, -dade/f, -ção/f, -ema/m, -ista/either) but many exceptions (o dia, o mapa, o problema, a mão, a tribo)
- **Number:** Singular/plural; complex plural rules for -ão (three patterns), -al/-el/-il/-ol/-ul, -m/-ns
- **Diminutive/Augmentative:** Productive morphology (casinha = little house; casarão = big house); often expresses affect, not just size

#### Verbs
- **Main Verbs:** Action and state verbs with full conjugation across 3 conjugations + irregular pôr group
- **Auxiliary Verbs:** ter (perfect tenses), haver (literary perfect, existential), ir (periphrastic future), estar (progressive)
- **Modal Verbs:** poder, dever, querer, saber, ter de / ter que (debitive — must/have to), haver de
- **Reflexive/Pronominal Verbs:** lavar-se, sentar-se, lembrar-se de, queixar-se de
- **Copulas:** ser (essential/identifying), estar (transient/locational) — grammaticalized contrast

#### Adjectives
- **Attributive:** Agree in gender and number with head noun
- **Predicative:** Follow ser, estar, ficar, parecer; agree with subject
- **Comparative:** mais/menos + adj + (do) que; irregular: melhor (better), pior (worse), maior (bigger), menor (smaller)
- **Superlative:** o/a mais + adj; synthetic absolute: -íssimo (lindíssimo, facílimo, máximo)
- **Position:** Most adjectives postnominal (uma casa grande); evaluative/affective adjectives prenominal (uma grande casa = a great house, vs uma casa grande = a big house) — semantic shift parallels French BANGS

#### Adverbs
- **Manner:** -mente suffix attached to feminine adjective (rápida → rapidamente); chains drop -mente on all but last (lenta e cuidadosamente)
- **Time/Place:** ontem, hoje, amanhã, agora, aqui/cá, ali/lá, aí
- **Degree:** muito, pouco, bastante, tão, demasiado, demais
- **Note:** `cá`/`lá` carry deictic + pragmatic load (closer/further from speaker, often emotionally charged)

### Closed Classes (Function Words)

#### Pronouns
- **Personal Subject:** eu, tu (PT, BR informal-rural), você (BR ubiquitous, PT formal/distancing), ele/ela, nós, a gente (BR colloquial 1pl), vós (archaic in both), vocês, eles/elas
- **Direct Object Clitics:** me, te, o/a, nos, vos, os/as
- **Indirect Object Clitics:** me, te, lhe, nos, vos, lhes
- **Reflexive Clitics:** me, te, se, nos, vos, se
- **Disjunctive (after preposition):** mim, ti, ele/ela, nós, vós, eles/elas; **comigo, contigo, consigo, conosco/connosco, convosco** (with-pronoun fusions)
- **Possessive:** meu/minha/meus/minhas, teu/tua/teus/tuas, seu/sua/seus/suas, nosso/nossa/nossos/nossas, vosso/vossa, dele/dela/deles/delas (BR prefers `o livro dele` over `o seu livro` to avoid ambiguity)
- **Demonstrative (3-way deictic):** este/esta/estes/estas (proximal), esse/essa/esses/essas (medial), aquele/aquela/aqueles/aquelas (distal); neuter isto/isso/aquilo
- **Relative:** que (most common), quem (with humans/preposition), cujo/cuja/cujos/cujas (possessive), o qual/a qual/os quais/as quais (formal/disambiguating), onde (locative)
- **Indefinite:** alguém, ninguém, algo, nada, tudo, todo/toda/todos/todas, cada, alguns/algumas, nenhum/nenhuma, qualquer
- **Interrogative:** quem, que, qual/quais, quanto/quanta/quantos/quantas, onde, como, quando, por que / porquê

#### Determiners
- **Definite Articles:** o, a, os, as
- **Indefinite Articles:** um, uma, uns, umas
- **Possessive (with article in PT, often without in BR):** o meu livro (PT) / meu livro (BR)
- **Demonstrative:** este/esse/aquele series (with all gender/number forms)
- **Note:** Portuguese has **no partitive article** (unlike French). Bare nouns express partitive: "Quero pão" (I want some bread).

#### Contractions (CRITICAL — extremely frequent, must be tokenized)
Contractions of preposition + article/pronoun are obligatory and very common:
- **a + article:** ao (a+o), à (a+a), aos, às
- **de + article:** do, da, dos, das
- **em + article:** no, na, nos, nas
- **por + article:** pelo, pela, pelos, pelas
- **de + demonstrative:** deste, desta, desse, dessa, daquele, daquela, disto, disso, daquilo
- **em + demonstrative:** neste, nesta, nesse, nessa, naquele, naquela, nisto, nisso, naquilo
- **a + demonstrative:** àquele, àquela, àquilo
- **de + ele/ela/eles/elas:** dele, dela, deles, delas
- **em + ele/ela/eles/elas:** nele, nela, neles, nelas
- **de + um/uma:** dum, duma, duns, dumas (PT; BR uses "de um")

The analyzer **must split contractions** into their component grammatical roles for accurate analysis (e.g., `do` → preposition + definite_article).

#### Prepositions
- **Simple:** a, de, em, por, para, com, sem, sob, sobre, entre, até, desde, contra, ante, perante, após
- **Complex:** apesar de, em vez de, ao lado de, por causa de, antes de, depois de, em frente de
- **Por vs Para:** Major learner challenge — `por` (cause/agent/route/duration) vs `para` (purpose/destination/recipient)

#### Conjunctions
- **Coordinating:** e, ou, mas, porém, contudo, todavia, ou…ou, nem…nem
- **Subordinating (indicative):** que, porque, pois, visto que, já que, quando, enquanto, assim que, logo que
- **Subordinating (subjunctive triggers):** embora, ainda que, mesmo que, a fim de que, para que, sem que, antes que, contanto que, desde que, caso

#### Particles and Discourse Markers
- **Negation:** não (default); reinforcers nem, sequer, jamais, nunca
- **Affirmation/Confirmation:** sim, claro, pois (PT confirmation), né? (BR tag question, from "não é?")
- **Discourse:** então, pois, , aí (BR sequencer), tipo (BR colloquial), olha, escuta
- **Pragmatic:** , (deictic + pragmatic — proximity/distance from speaker's deixis); pois é (PT — "yeah, indeed")

## Language-Specific Features

### Unique Grammatical Phenomena

#### 1. The Clitic Pronoun System (HIGH PRIORITY)
Portuguese clitic pronouns (me, te, se, lhe, lhes, nos, vos, o, a, os, as) attach to verbs in three positions, governed by syntactic and stylistic rules:

- **Proclisis (before the verb):**
  - After negation: Não me viu (He didn't see me)
  - After certain adverbs: Já lhe disse, Sempre te ajudo, Talvez o veja
  - After subordinating conjunctions: Disse que me viu
  - After interrogatives/exclamatives: Quem te viu?
  - After indefinites: Alguém me chamou
  - **BR colloquial: proclisis is the default**, even sentence-initial: "Me chamou ontem"
- **Enclisis (after the verb, hyphenated):**
  - Default in PT for affirmative declaratives: Viu-me (He saw me), Disse-lhe a verdade
  - Imperative affirmative: Diga-me, Deixa-o
  - Sentence-initial in PT formal register
- **Mesoclisis (inside future/conditional verb forms — extremely rare, formal/literary, PT only):**
  - dar-lhe-ei (I will give him) ← darei + lhe inserted
  - falar-te-ia (I would speak to you) ← falaria + te inserted
  - **Effectively obsolete in BR; surviving in formal PT writing only.** The analyzer should recognize but flag as advanced/literary.

**Object clitic transformations** (when `o/a/os/as` follow certain verb endings):
- Verb ending in -r/-s/-z: -lo/-la/-los/-las (vê-lo, fá-lo, fi-lo)
- Verb ending in nasal (-m, -ão, -õe): -no/-na/-nos/-nas (viram-no, dão-no)

**BR/PT divergence on placement is the single most distinctive syntactic split** between the two registers.

#### 2. Ser vs Estar (Copula Distinction)
Portuguese grammaticalizes the permanent/transient distinction more strictly than Spanish:
- **Ser** — inherent identity, profession, origin, time, possession, passive voice (with past participle)
  - Ele é médico (He is a doctor — profession)
  - Sou brasileiro (I am Brazilian — origin)
  - O livro é meu (The book is mine — possession)
- **Estar** — transient state, location, ongoing condition, progressive aspect
  - Ele está cansado (He is tired — transient)
  - Estou em casa (I am at home — location)
  - Estou estudando (I am studying — BR progressive)

**Edge cases for AI:** Adjectives shift meaning by copula choice — "É chato" (he is boring) vs "Está chato" (he is being annoying right now). Permanent locations of immovables can take `ser` in PT ("A torre é em Lisboa") but `ficar` is preferred in BR.

#### 3. Personal Infinitive (Infinitivo Pessoal) — Romance Rarity
A non-finite verb form that **inflects for person and number** — unique to Portuguese (and Galician). Forms: -, -es, -, -mos, -des, -em (regular verbs).
- **Use:** Where English uses gerund/infinitive in subordinate clauses with explicit subject
- **Examples:**
  - É importante **estudarmos** todos os dias (It's important that we study every day)
  - Vou comprar pão para os meninos **comerem** (I'll buy bread for the boys to eat)
  - Ao **chegarmos**, vimos o problema (Upon arriving [we], we saw the problem)
- **AI must distinguish** personal infinitive from impersonal infinitive: "É importante estudar" (impersonal) vs "É importante estudarmos" (personal — explicit 1pl subject embedded in form).

#### 4. Synthetic vs Periphrastic Future and Conditional
- **Synthetic future:** falarei, falarás, falará, falaremos, falareis, falarão (formal, written)
- **Periphrastic future (BR colloquial dominant):** vou falar, vai falar, vamos falar (ir + infinitive)
- **Synthetic conditional:** falaria, falarias, falaria, falaríamos, falaríeis, falariam
- **Periphrastic conditional:** ia falar (informal)

The analyzer should accept both as future/conditional and tag the **register** (formal-synthetic vs colloquial-periphrastic).

#### 5. Subjunctive Mood — Three Tenses Plus Future Subjunctive
Portuguese uniquely retains a productive **future subjunctive** (largely lost in other Romance languages):
- **Present subjunctive:** que eu fale, que tu fales (used after triggers — querer que, esperar que, embora, para que)
- **Imperfect subjunctive:** se eu falasse (counterfactual conditionals: Se eu fosse rico…)
- **Future subjunctive:** quando eu falar, se eu puder, como (you) quiser — used in temporal/conditional clauses about future events. Has same forms as personal infinitive for regular verbs but different for irregulars (puder ≠ poder, fizer ≠ fazer, vier ≠ vir, for ≠ ir/ser).

**AI must disambiguate** future subjunctive from personal infinitive in regular verbs (formal context: subjunctive after `quando/se/enquanto`, infinitive after `para`/`ao`).

#### 6. BR/PT Divergences (CRITICAL for analyzer)

| Feature | Brazilian Portuguese (BR) | European Portuguese (PT) |
|---------|---------------------------|--------------------------|
| 2sg pronoun | você + 3sg verb | tu + 2sg verb (PT north); você (PT formal) |
| 1pl colloquial | a gente + 3sg | nós + 1pl |
| Clitic placement default | Proclisis (Me chamou) | Enclisis (Chamou-me) |
| Mesoclisis | Effectively absent | Marginal/literary only |
| Progressive | estar + gerund (estou fazendo) | estar a + infinitive (estou a fazer) |
| Future tense | Periphrastic (vou fazer) | Both, synthetic preserved |
| Diminutive | -inho dominant | -inho/-zinho |
| Object clitic doubling | Common in topicalization | Rarer |
| Spelling (post-AO 1990) | ato, ótimo, ação | ato, ótimo, ação (mostly converged) |
| Lexicon | trem, ônibus, café da manhã, geladeira, celular | comboio, autocarro, pequeno-almoço, frigorífico, telemóvel |

**Disambiguation strategy:** detect register from cues (`você` + `gerund` → BR; `tu` + enclisis + `a + infinitivo` → PT) and tag analysis accordingly.

#### 7. Debitive Construction: ter de / ter que
- `ter de + infinitive` (formal, PT-leaning) — strict obligation
- `ter que + infinitive` (BR colloquial dominant) — same meaning, more flexible
- Distinct from `ter` as auxiliary (perfect tenses): `Tenho falado` (I have been speaking)

#### 8. Nominal Augmentative/Diminutive Productivity
Highly productive and pragmatically rich:
- Diminutive -inho/-zinha: casinha (little house), cafezinho (espresso/affectionate coffee), tchauzinho (cute bye)
- Augmentative -ão: carrão (big car), portão (gate, lexicalized), problemão (huge problem)
- Often expresses **affect** rather than literal size — `bonitinho` (cute, not "small handsome")

## Pedagogical Considerations

### Learning Difficulty Assessment

#### Difficulty Factors
- **Clitic placement:** Different rules in BR vs PT; mesoclisis is famously confusing
- **Verb conjugation:** ~50 highly irregular verbs; six tenses × six persons + subjunctive + personal infinitive
- **Ser vs Estar:** Idiomatic, with semantic shifts depending on copula
- **Por vs Para:** Both translate as "for"/"by"; usage is idiomatic
- **Subjunctive triggers:** Long list of conjunctions and matrix verbs require subjunctive
- **Nasal vowels:** Phonological challenge that affects spelling recognition (não/nao, irmão/irmãos)

#### Learner Profiles
- **Beginner:** Present indicative, common nouns, agreement basics, ser/estar, articles, simple questions, definite/indefinite articles, contractions (do, no)
- **Intermediate:** Preterite/imperfect distinction, future, conditional, reflexive verbs, common subjunctive triggers, possessive pronouns, basic clitic placement, periphrastic future
- **Advanced:** Future subjunctive, personal infinitive, mesoclisis (recognition), passive voice, complex clitic placement, register switching BR/PT, literary tenses (mais-que-perfeito simples)

### Common Learning Challenges

#### Frequent Error Patterns
- **Clitic placement:** Mixing BR proclisis with PT enclisis contexts; forgetting hyphenation in enclisis
- **Ser/Estar confusion:** Translating English "to be" without semantic analysis
- **Por vs Para:** Treating as interchangeable
- **Gender of -ema/-ema/-a nouns:** problema, sistema, mapa, dia all masculine (Greek origin)
- **Por que / Por quê / Porque / Porquê:** Four spellings with distinct uses (interrogative open, interrogative final, causal conjunction, nominal)
- **Future subjunctive vs personal infinitive:** Identical forms for regular verbs, distinct for irregulars
- **Contractions:** Forgetting obligatory contraction (de + o = do, NEVER "de o")

#### Conceptual Difficulties
- **Tense vs Aspect:** Pretérito perfeito (completed: falei) vs imperfeito (ongoing/habitual: falava) — parallel to French passé composé / imparfait
- **Mood Selection:** Subjunctive in subordinate clauses for non-factuality, opinion, emotion, doubt
- **Register Variation:** BR colloquial vs BR formal vs PT — three implicit standards
- **Pro-drop:** When to express vs omit subject pronouns (pragmatic emphasis vs default omission)
- **Clitic climbing:** In compound tenses (vou-te dizer / te vou dizer / vou dizer-te — all attested, register-conditioned)

## Technical Implementation Planning

### Complexity Hierarchy (Beginner → Intermediate → Advanced)

#### Beginner Level (9 roles)
- noun, verb, adjective, pronoun, preposition, conjunction, adverb, article, numeral

#### Intermediate Level (+12 roles, total 21)
- personal_pronoun, possessive_pronoun, demonstrative_pronoun, reflexive_pronoun
- definite_article, indefinite_article
- contraction (a+o=ao, de+o=do, em+o=no, por+o=pelo, de+ele=dele — VERY common)
- auxiliary_verb (ter, haver, ir, estar)
- copula (with `ser_vs_estar` sub-tag)
- modal_verb (poder, dever, querer, saber)
- particle (não, sim, , , pois)
- pronominal_verb (verbs with intrinsic se: lembrar-se, queixar-se)

#### Advanced Level (+13 roles, total 34)
- relative_pronoun (que, quem, cujo, o qual, onde)
- indefinite_pronoun (alguém, ninguém, algo, nada, tudo)
- interrogative_pronoun (quem, que, qual, quanto, onde, como, quando)
- subordinating_conjunction (que, porque, embora, ainda que, caso)
- gerund (-ndo: falando, comendo, partindo)
- past_participle (-do: falado, comido, partido — also irregular: feito, dito, visto, posto)
- personal_infinitive (inflected: falarmos, comerem)
- clitic_pronoun (with placement annotation: proclitic / enclitic / mesoclitic)
- mesoclitic (rare; flag for literary/formal PT)
- subjunctive_marker (verb form tag: present_subj, imperfect_subj, future_subj)
- conditional (synthetic falaria; or periphrastic ia falar)
- interjection (oxalá, tomara, nossa, caramba, puxa)
- debitive (ter de / ter que + infinitive)

### AI Prompting Strategy

#### Prompt Complexity Levels
- **Beginner:** Focus on gender/number agreement, present indicative -ar/-er/-ir, articles, contractions (do/no/ao), ser vs estar basics
- **Intermediate:** Add preterite/imperfect, future periphrastic (vou + inf), reflexive verbs, possessives, basic subjunctive (espero que…), common clitic positions
- **Advanced:** Include all subjunctive tenses (esp. future subjunctive), personal infinitive, mesoclisis recognition, passive voice, full clitic placement rules, BR/PT register tagging

#### Language-Specific Prompting Requirements
- **Always tag register:** Output should include `register: BR | PT | neutral`
- **Tokenize contractions:** Split `do` → de + o; `pelo` → por + o; `naquele` → em + aquele in word-level analysis
- **Distinguish ser vs estar:** Tag copula instances with `copula_type: ser | estar` and explanatory note
- **Annotate clitic position:** For each clitic, tag `clitic_position: proclitic | enclitic | mesoclitic` and the trigger
- **Personal infinitive flag:** When -mos/-em endings appear on infinitive stems, check for explicit subject and tag `personal_infinitive: true`
- **Future subjunctive flag:** Recognize forms following `se / quando / enquanto / como / conforme` referencing future
- **Por/Para distinction:** Always tag with semantic role (cause, agent, route, duration vs purpose, recipient, destination)

### Data Structure Design

#### Output Format Requirements
- **Grammatical Role Mapping:** Use the exact role labels from the complexity hierarchy above so they survive `grammar_processor.py` pass-through (per Coding Conventions, language-specific concepts must NOT be re-mapped through `_map_pos_to_category()`)
- **Morphological Analysis:** Gender (m/f), number (sg/pl), person (1/2/3), tense (present/preterite/imperfect/pluperfect/future/conditional), mood (indicative/subjunctive/imperative/personal_infinitive), aspect (perfect/imperfective/progressive)
- **Agreement Encoding:** Links between agreeing elements (article-noun, noun-adjective, subject-verb, past_participle-subject in passives)
- **Confidence Scoring:** Based on conjugation regularity, agreement correctness, contraction tokenization success, register consistency
- **HTML Output:** Color-coded spans per role; clitic pronouns get a distinct color (e.g., #E91E63) and a `data-position` attribute

#### Validation Rules
- **Required Fields:** Gender for nouns; conjugation class for verbs; tense + mood for finite verbs; person+number for personal infinitive; clitic_position for clitics
- **Quality Thresholds:** ≥0.85 confidence on well-formed sentences; correct ser/estar identification; correct contraction split
- **Fallback Mechanisms:** 5-level fallback parsing (Direct JSON → Markdown → Repair → Text Pattern → Rule-based)

#### Portuguese-Specific Processing Challenges
- **Contraction Tokenization:** Pre-process to split obligatory contractions (do, no, ao, pelo, dele, naquele, etc.) into preposition + article/pronoun before role assignment
- **Clitic-Verb Hyphen Handling:** Recognize hyphenated forms (viu-me, dá-lho, dar-lhe-ei) as verb + clitic compound, not unknown words
- **Object Clitic Phonological Variants:** vê-lo (vê + o), fá-lo (faz + o), viram-no (viram + o) — recognize allomorphs
- **BR/PT Register Detection:** Use cues (você + gerund, ter que, vou + inf → BR; tu + enclisis, estar a + inf, ter de → PT)
- **Future Subjunctive vs Personal Infinitive Disambiguation:** For regular verbs, identical forms — disambiguate by syntactic context (after se/quando = subjunctive; after para/sem/ao = personal infinitive)
- **Por que / Porque / Por quê / Porquê:** Four-way disambiguation based on position and function
- **Nasal Vowel Normalization:** Optionally normalize ã/õ for fuzzy matching but preserve in output
- **Spelling Variants (pre/post AO 1990):** Accept both `acção/ação`, `óptimo/ótimo`, `facto/fato` for input; output normalized post-AO form

## AI Analysis Requirements

### Grammatical Roles AI Must Identify
The AI must use the **exact role labels** from the complexity hierarchy (e.g., `clitic_pronoun`, `personal_infinitive`, `mesoclitic`, `copula`, `contraction`, `debitive`) so they pass through `grammar_processor._convert_analyzer_output_to_explanations()` unchanged with their language-specific colors.

### Confidence Scoring Criteria
| Construct | Confidence Boost | Confidence Penalty |
|-----------|------------------|--------------------|
| Regular -ar/-er/-ir verb correctly conjugated | +0.05 | — |
| Contraction correctly split | +0.05 | -0.10 if missed |
| Clitic position correctly identified | +0.10 | -0.15 if mis-positioned |
| Ser/estar correctly distinguished | +0.10 | -0.15 if confused |
| Personal infinitive recognized | +0.10 | -0.05 if missed |
| Future subjunctive disambiguated | +0.10 | -0.10 if confused with infinitive |
| BR/PT register tagged | +0.05 | — |
| Past participle agreement (passive) correct | +0.05 | -0.10 if wrong |

Base confidence per word: 0.70. Production threshold: 0.85.

### Common Learner Errors and Misanalyses to Avoid
- **Don't confuse `seu/sua` with English "your"** — in BR `seu` more often = his/her/their; use `dele/dela/deles/delas` for clarity
- **Don't tag `a gente` as a noun** — it's a 1pl pronoun in BR colloquial despite the article + noun morphology
- **Don't tag `você` as a 3rd-person pronoun** — semantically 2nd person, syntactically 3sg agreement; tag as `personal_pronoun` with `semantic_person: 2`
- **Don't miss the personal infinitive ending** — -mos/-em on what looks like an infinitive is the inflected form
- **Don't mis-tag enclisis as misspelling** — viu-me, dar-lhe are well-formed PT; never lemmatize away the hyphen

## Production-Ready Features

### APKG Output Formatting Requirements
- HTML spans per word with `class="role-{role_name}"` and CSS color-coding from the role config
- Tooltip on hover showing morphological analysis (gender, number, tense, person, mood)
- Clitic pronouns: distinct visual treatment with positional annotation (proclitic before/enclitic after/mesoclitic-inserted)
- Contractions: dual-color span showing preposition + article components

### Error Handling Patterns
- **Lazy AI imports:** `_call_ai()` method must use lazy imports of `streamlit_app.shared_utils` (per Coding Conventions; module-level imports break `unittest.mock.patch()` and cause E2E test contamination)
- **Circuit breaker:** Implement per-call exception capture, fall back to rule-based analysis on persistent failure
- **5-level fallback parsing:** Direct JSON → Markdown code block → JSON repair → Text pattern → Rule-based
- **Graceful degradation:** Even with rule-based fallback, return at minimum POS tagging for each word

### Performance Requirements
- **Sub-2-second analysis** per sentence (10–20 tokens) on Gemini 2.5 Flash
- **Caching:** External word_meanings.json for high-frequency vocabulary (top 5000 words)
- **Batched analysis:** When processing multiple sentences (typical card generation: 5–10 sentences), use batch prompt to reduce API calls

### Integration Points with BaseGrammarAnalyzer
The Portuguese analyzer must implement the 4 abstract methods from `BaseGrammarAnalyzer`:
- `get_grammar_prompt(complexity, sentence, target_word) -> str`
- `parse_grammar_response(ai_response, complexity, sentence) -> Dict`
- `get_color_scheme(complexity) -> Dict[str, str]`
- `validate_analysis(parsed_data, original_sentence) -> float` (≥0.85 for production)

Plus `batch_analyze_grammar` and `_generate_html_output` following the Japanese facade pattern.

## Quality Assurance Framework

### Gold Standard Patterns for Validation
Reference test sentences spanning all difficulty levels and capturing Portuguese-specific phenomena:

| Difficulty | Sentence | Tests |
|-----------|----------|-------|
| Beginner | O gato come o peixe | SVO, articles, present indicative |
| Beginner | Eu sou brasileiro | Pro-drop optional, ser+adjective |
| Intermediate | Estou estudando português (BR) / Estou a estudar português (PT) | Progressive aspect BR/PT split |
| Intermediate | Não me viu ontem | Proclisis after negation, preterite |
| Intermediate | Vou ao parque amanhã | Periphrastic future, contraction `ao` |
| Advanced | É importante estudarmos todos os dias | Personal infinitive 1pl |
| Advanced | Quando puder, te ligo | Future subjunctive (puder ≠ poder), proclisis |
| Advanced | Dar-lhe-ei o livro amanhã | Mesoclisis (PT formal/literary) |
| Advanced | Se eu fosse rico, viajaria pelo mundo | Imperfect subjunctive + conditional + contraction `pelo` |
| Advanced | Espero que ele esteja bem | Subjunctive trigger + estar |

### Confidence Threshold Requirements
- **Production:** ≥0.85 average confidence on the gold-standard test sentence corpus
- **Per-word minimum:** 0.70 base; aggregate ≥0.85
- **Sentence-level rejection:** If overall confidence <0.70, fall back to rule-based and tag `analysis_quality: low`

### Cross-Linguistic Consistency Requirements
- **Compare against French v2.0:** Match French's depth on agreement cascade, mood detection, and morphological feature reporting
- **Match Spanish patterns where applicable:** Both share Iberian Romance traits (ser/estar, subjunctive triggers, similar pronoun systems)
- **Distinguish from Spanish:** Personal infinitive, future subjunctive, mesoclisis are Portuguese-specific — don't borrow Spanish analyzer logic blindly
- **Output schema parity:** Use same JSON shape as French analyzer (sentence, target_word, language_code, complexity_level, grammatical_elements, explanations, color_scheme, html_output, confidence_score, word_explanations, is_rtl=false, text_direction='ltr')

## Implementation Risks and Challenges

### Technical Complexity
- **Clitic placement is context-dependent** — proclisis triggers (negation, subordinators, certain adverbs) require parsing the preceding context, not just lexical lookup
- **Mesoclisis tokenization** — the verb is split (dar-**lhe**-ei) and may be misread as separate tokens; pre-tokenization must recognize the pattern
- **Future subjunctive vs personal infinitive ambiguity** — for regular verbs, forms are identical; disambiguation depends on semantic and syntactic context
- **Contraction cascade** — single token `daquilo` = de + a + aquilo (3 components); analyzer must handle multi-step splits

### Linguistic Challenges
- **BR/PT register fluidity** — many speakers code-switch; sentences may be mixed-register
- **Spelling variants** — pre-AO 1990 forms still appear in older texts; analyzer must accept both
- **Lexical divergence** — same concept, different word (trem/comboio); requires register-aware lemmatization
- **Verbal periphrases** — many alternative forms (vou fazer / farei / hei de fazer / estou para fazer); all map to "future" with register tags

### AI Prompting Challenges
- **Disambiguation of identical forms** — future subjunctive vs personal infinitive vs imperative
- **Clitic-position justification** — AI must explain WHY proclisis/enclisis applies (the trigger), not just label it
- **Por/Para semantic role** — many idiomatic uses don't fit cleanly into cause/purpose dichotomy

### Quality Assurance Needs
- **Test corpus must cover both BR and PT** — separate test files for each register, plus mixed/neutral
- **Edge cases:** Mesoclisis, archaic mais-que-perfeito simples (`falara` = had spoken), passive with `ser` vs `estar` (`foi feito` vs `está feito`)
- **Performance under batch load:** 5–10 sentence batches must complete in <10 seconds total

## Implementation Roadmap

### Phase 1: Core Infrastructure
1. Create directory structure following Japanese/French pattern: `pt_analyzer.py`, `domain/`, `infrastructure/`, `tests/`
2. Implement basic facade with Clean Architecture and **lazy imports in `_call_ai()`** (mandatory per Coding Conventions)
3. Set up external configuration files: `pt_config.yaml`, `pt_grammatical_roles.yaml`, `pt_patterns.yaml`, `pt_word_meanings.json`
4. Create domain components: pt_config.py, pt_prompt_builder.py, pt_response_parser.py, pt_validator.py, pt_fallbacks.py

### Phase 2: Grammatical Role System
1. Define role hierarchy (34 roles total across beginner/intermediate/advanced)
2. Implement complexity-based filtering
3. Create color scheme: nouns blue, verbs red, adjectives green, clitics pink (#E91E63), copula amber (with ser/estar sub-distinction), contractions purple, personal_infinitive distinct teal, mesoclitic distinct magenta
4. Set up role mapping for AI response processing — **NO re-mapping through `_map_pos_to_category()`**

### Phase 3: Portuguese-Specific Features
1. **Implement Contraction Tokenizer:** Split obligatory contractions before role assignment
2. **Add Clitic Placement Detector:** Identify proclitic/enclitic/mesoclitic positions and triggers
3. **Create Ser/Estar Disambiguator:** Tag every copula instance with type and rationale
4. **Implement Personal Infinitive Recognition:** Detect inflected non-finite forms with subject
5. **Add Future Subjunctive Detector:** Disambiguate from personal infinitive in regular verbs by context
6. **Handle Object Clitic Allomorphy:** Recognize -lo/-no/-la/-na variants
7. **BR/PT Register Tagging:** Detect register cues and annotate output
8. **Por/Para Semantic Role Tagger**

### Phase 4: Quality Assurance
1. Comprehensive test suite covering all conjugation classes, agreement patterns, clitic positions, BR/PT register
2. Fallback mechanisms for unknown verbs, archaic forms, complex clitic clusters
3. Validate against gold-standard sentences (10+ from above table, expanded to 30+)
4. Test all three complexity levels (beginner, intermediate, advanced) per E2E pipeline test requirement
5. Performance testing: <2s per sentence

### Phase 5: Integration and Deployment
1. Register analyzer in `analyzer_registry.py` (`portuguese → pt`)
2. Update languages.yaml UI translations if needed (already includes `pt`)
3. Run `validate_implementation.py --language pt --verbose`
4. Run `compare_with_gold_standard.py --language pt --reference fr --detailed`
5. End-to-end pipeline test in `tests/test_end_to_end_pipeline.py` with mocked Gemini, asserting all three difficulty levels
6. Deploy and monitor confidence scores in production
