# English Grammar Concepts and Implementation Guide

## Executive Summary

English is a West Germanic language in the Indo-European family, spoken natively by ~380 million people and as a second language by an additional ~1.1 billion — the most widely studied L2 globally. Compared with its Indo-European cousins, modern English has shed almost all of its Old English inflectional morphology: case marking on nouns is gone, grammatical gender is gone, and verb agreement is reduced to a single 3rd-person-singular `-s` in the present tense. What replaced this morphological richness is **strict SVO word order** and a **rich auxiliary verb system** that carries tense, aspect, mood, voice, and polarity information. This makes English structurally **analytic-leaning** with **fusional fragments** (irregular plurals, irregular past tenses, the surviving I/me / he/him pronoun case distinction).

This analyzer follows the German/French Clean Architecture contract — domain components for config, prompt building, response parsing, validation, and rule-based fallbacks; infrastructure for AI service, circuit breaker, caching; external YAML/JSON data files; and a 5-level fallback parsing chain. The analyzer must hit ≥0.85 confidence on AI output and emit `is_fallback: True` whenever the rule-based fallback is used so the validator can cap confidence at 0.3.

The central analytical challenges for English are not morphological — they are **categorial ambiguity** (the same surface form can be 3-5 different parts of speech) and **construction recognition** (phrasal verbs, modal sequences, perfect/progressive aspect chains). The prompt builder, response parser, and validator must all be designed around disambiguating: `to` (infinitive marker vs. preposition), `-ing` forms (present participle vs. gerund vs. deverbal adjective), `-ed` forms (past tense vs. past participle vs. adjective), `that` (4-way ambiguity), relative vs. interrogative `who/which`, and phrasal-verb particles vs. true prepositions.

## Language Overview

### Classification and Status
- **Language Family:** Indo-European
- **Branch:** Germanic (West Germanic, Anglo-Frisian)
- **Script Type:** Alphabetic (Latin script, no diacritics in native vocabulary)
- **Writing Direction:** Left-to-right
- **Official Status:** Official or de-facto official in 67 countries; primary working language of the UN, EU institutions, ICAO, IMO, IOC, and most international scientific publishing
- **Global Speakers:** ~380M native, ~1.1B L2 — total reach >1.5B

### Geographic and Cultural Context
- **Primary Regions:** UK, Ireland, USA, Canada, Australia, New Zealand, South Africa, large portions of South Asia, West Africa, East Africa, the Caribbean
- **Cultural Significance:** Lingua franca of business, science, aviation, computing, popular media, and academic publishing
- **Dialectal Variation:** Major standard varieties (General American, Received Pronunciation, General Australian, Standard Canadian, Standard Indian English, Standard Scottish English) plus thousands of regional dialects and creoles
- **Modern Usage:** Dominant language of the internet (~60% of web content) and the default L2 in most national education systems

### Script and Writing System
- **Character Set:** 26 Latin letters; no diacritics in native words (loanwords like `café`, `naïve`, `résumé` may retain them but are commonly written without)
- **Capitalization:** Sentence-initial, proper nouns, the pronoun `I`, and (in some titles) all major words
- **Punctuation:** Standard Western — period, comma, semicolon, colon, question mark, exclamation mark, apostrophe (possessive + contraction), single/double quotes, em/en dashes
- **Challenges:** Spelling is **not** phonemic (cf. *though, through, thought, tough, cough, bough*); silent letters are pervasive; homographs are abundant (`read` /riːd/ present vs. /rɛd/ past, `wind` /wɪnd/ vs. /waɪnd/, `lead` metal vs. verb)

## Grammatical Structure Analysis

### Word Order and Sentence Structure

#### Basic Word Order
English follows **strict** Subject-Verb-Object order in declaratives. Word-order rigidity compensates for the loss of case marking — moving "the dog" and "the cat" around in *The dog bit the cat* changes the meaning, unlike in inflected languages.

- **Declarative:** *The cat eats the fish.* (S V O)
- **Yes/no questions:** **subject-auxiliary inversion** — *Does the cat eat the fish?* (Aux S V O), *Is she reading?* (Aux S V), *Have they arrived?*
- **Wh-questions:** wh-fronting + auxiliary inversion — *What does the cat eat?*, *Where are you going?* — except when the wh-word is the subject, in which case there is no inversion: *Who ate the fish?*
- **Negation:** insertion of `not` after the (first) auxiliary or do-support — *She does not eat fish.*, *He hasn't arrived.*, *You can't go.*
- **Imperatives:** verb-initial, subject elided — *Eat your dinner.*, *Don't move.*
- **Embedded clauses:** complementizer `that` (often droppable) — *I think (that) she's right.*

#### Quasi-V2 Pattern: Subject-Auxiliary Inversion
English has lost full V2 word order but retains it in:
1. Yes/no questions: *Are you ready?*
2. Wh-questions (non-subject): *Where did he go?*
3. Negative-initial fronting: *Never have I seen such a thing.*
4. Conditional inversion: *Had I known...* (= *if I had known...*)
5. So-inversion: *So tired was she that she fell asleep.*

The analyzer must mark the inverted auxiliary distinctly from a canonical-position auxiliary.

#### Constituent Order Examples
1. **Simple declarative:** *The students study English.* (Det N V Det N → S V O)
2. **Yes/no question:** *Do the students study English?* (Aux Det N V Det N)
3. **Wh-question:** *Why are you studying English?* (Wh Aux S V O)
4. **Negation:** *They are not studying English.*
5. **Relative clause:** *The book that I read* / *The book I read* (relative pronoun optional in object position)
6. **Subordinate clause:** *Although it was raining, we went out.*
7. **Cleft:** *It was John who broke the window.*

### Morphological System

English morphology is **fragmentary** — extensive paradigms exist for a small handful of categories, while the rest of the language is uninflected.

#### Inflection Types

##### Nominal Inflection
- **Number:** singular vs. plural
  - Regular: `-s` / `-es` (cat→cats, bus→buses, box→boxes)
  - Y→ies: city→cities (consonant + y)
  - F→ves (some): leaf→leaves, knife→knives, half→halves (but: roof→roofs, chief→chiefs)
  - Voicing alternation: house /haʊs/ → houses /haʊzɪz/
  - Mutated plurals (i-umlaut survivals): man→men, woman→women, foot→feet, tooth→teeth, goose→geese, mouse→mice, louse→lice
  - -en plurals: ox→oxen, child→children, brother→brethren (archaic religious)
  - Zero plurals: sheep, deer, fish, aircraft, species, series
  - Foreign-pattern plurals: criterion→criteria, phenomenon→phenomena, datum→data, alumnus→alumni, cactus→cacti/cactuses, index→indices/indexes, analysis→analyses, crisis→crises
- **Possessive (genitive):** `-'s` (singular: *the cat's tail*) and `-s'` / `-'s` (plural: *the cats' tails*) — written as a clitic, attaches to the **end** of a noun phrase (*the King of Spain's daughter*), so technically **phrasal**, not strictly morphological
- **Case:** **lost** for nouns; survives only on personal/relative pronouns (see below)
- **Gender:** **lost** for nouns; survives only as semantic gender on 3rd-singular pronouns (he/she/it)

##### Pronominal Inflection (the strongest case-system survival)
| Person/Number | Nom | Acc/Obj | Genitive (det) | Genitive (pron) | Reflexive |
|---|---|---|---|---|---|
| 1sg | I | me | my | mine | myself |
| 2 | you | you | your | yours | yourself/yourselves |
| 3sg.m | he | him | his | his | himself |
| 3sg.f | she | her | her | hers | herself |
| 3sg.n | it | it | its | — | itself |
| 1pl | we | us | our | ours | ourselves |
| 3pl | they | them | their | theirs | themselves |
| Relative/interrog | who | whom | whose | whose | — |

The `who`/`whom` distinction is fading in colloquial English but still required in formal registers and is a flagship POS-tagging test case.

##### Verbal Inflection
A regular English lexical verb has only **four** distinct forms:
1. **Base / infinitive / non-3sg-present:** *walk* (used after `to`, modals, in imperatives, and in non-3sg present)
2. **3sg present:** *walks* (the only surviving present-tense agreement marker)
3. **Past tense:** *walked*
4. **Past participle:** *walked* (homophonous with past for regular verbs, distinct for many irregulars)
5. **Present participle / gerund:** *walking* (one form serves both functions)

Irregular verbs may distinguish past from past participle (e.g., *go / went / gone*, *speak / spoke / spoken*, *break / broke / broken*, *eat / ate / eaten*, *write / wrote / written*, *take / took / taken*, *give / gave / given*, *see / saw / seen*, *do / did / done*, *come / came / come*, *run / ran / run*).

The verb `be` is **highly suppletive**: am / is / are / was / were / been / being.

##### Tense + Aspect Combinations (8 finite forms)
| | Simple | Progressive | Perfect | Perfect Progressive |
|---|---|---|---|---|
| **Present** | walks | is walking | has walked | has been walking |
| **Past** | walked | was walking | had walked | had been walking |

Plus future, expressed periphrastically:
- `will` + base: *will walk*
- `be going to` + base: *is going to walk*
- present progressive (futurate): *is walking* (planned future)
- simple present (scheduled future): *the train leaves at 6*

The "future tense" is therefore not strictly a tense — English has only present and past as morphological tenses; futurity is encoded with auxiliaries.

##### Adjectival Inflection
- **Comparative `-er`:** big→bigger, happy→happier, tall→taller (mostly 1-2 syllable adjectives)
- **Superlative `-est`:** big→biggest, happy→happiest, tall→tallest
- **Periphrastic comparative/superlative:** longer adjectives use `more` / `most` (more beautiful, most beautiful)
- **Suppletive comparison:** good/better/best, bad/worse/worst, far/farther/farthest~further/furthest, little/less/least, much-many/more/most
- **Agreement:** **none** — adjectives are completely uninflected for gender, number, or case (a stark contrast with French/German)

#### Morphological Complexity
- **Predominantly Analytic:** grammatical relations expressed by word order and function words
- **Fusional Remnants:** plural -s, possessive -'s, 3sg -s, past -ed, participle -en, comparative -er/-est, pronoun case
- **Suppletive paradigms:** be, go (went), good/better, person/people
- **Derivational Morphology:** Highly productive — prefixes (un-, re-, pre-, dis-, mis-, anti-, over-, under-), suffixes (-ation, -ity, -ness, -ment, -ly, -able, -ful, -less, -ize, -ify, -er/-or, -ist)
- **Compounding:** Both endocentric (blackbird, software, bookshop) and exocentric (pickpocket, redhead); productive for nouns
- **Conversion (zero-derivation):** N→V (to email, to friend, to google), V→N (a run, a walk, a buy), Adj→V (to dry, to clean, to slow) — major source of POS ambiguity

## Grammatical Categories

### Open Classes (Content Words)

#### Nouns
- **Common vs. Proper:** Distinguished by capitalization (book vs. London, Mary vs. mary)
- **Count vs. Mass (non-count):** Critical distinction governing article and quantifier choice
  - Count: *a book / books / many books / few books*
  - Mass: *(some) water / much water / little water* — no plural, no `a/an`
  - Coercion: *two coffees* (= cups of coffee), *the wines of France* (= varieties)
- **Number:** Singular / plural — see morphology section
- **Concrete vs. Abstract:** Affects collocation (truth, beauty, freedom vs. table, river)
- **Collective:** Family, team, government — variable verb agreement (BrE plural verb common, AmE singular default)
- **Gender:** Lost; survives only as semantic property influencing pronoun choice

#### Verbs
The English verb is the heart of the morphological system and the densest source of grammatical information.

##### By Function
- **Lexical (main) verbs:** carry the principal semantic content (*eat, run, think*)
- **Auxiliary verbs:** be, have, do — carry tense/aspect/voice/polarity, can also serve as lexical verbs
  - *be* — auxiliary for progressive (*is running*) and passive (*is eaten*); copula (*is happy*)
  - *have* — auxiliary for perfect (*has eaten*); lexical "possess" (*I have a dog*)
  - *do* — auxiliary for negation/questions/emphasis in simple present/past (*does he eat?*, *don't run*, *I DO know!*); lexical "perform" (*do the dishes*)
- **Modal verbs:** can, could, will, would, shall, should, may, might, must, ought (to), dare, need
  - **Defective paradigm:** no -s in 3sg (*she can*, never **she cans*), no infinitive (no *to can*), no participles
  - **Take bare infinitive:** *can swim*, not *can to swim* (except `ought to` which keeps `to`)
  - **Dual modals:** AmE/Southern *might could*, *may can* (dialectal)

##### By Transitivity
- **Intransitive:** sleep, arrive, exist (no direct object)
- **Transitive:** eat (X), build (X), see (X)
- **Ditransitive:** give (X) (Y), tell (X) (Y), send (X) (Y) — *I gave her a book / I gave a book to her* (dative alternation)
- **Copular / linking:** be, become, seem, appear, feel, look, taste, smell, sound, get (with adjective)
- **Phrasal:** verb + particle — see Language-Specific Features

##### By Regularity
- **Regular (~85% of verbs):** -ed for past and past participle
- **Irregular (~200 high-frequency verbs):** strong (sing/sang/sung), weak with vowel change (think/thought), suppletive (go/went/gone), unchanging (cut/cut/cut, hit/hit/hit, put/put/put)

#### Adjectives
- **Attributive:** before the noun — *a red car, an old man*
- **Predicative:** after a copula — *the car is red, he seems tired*
- **Postpositive (rare):** *something nice, the people responsible, attorney general, court martial*
- **Comparative / Superlative:** see morphology
- **Order of Stacked Adjectives (royal order):** opinion → size → age → shape → color → origin → material → purpose — *a beautiful little old round red Italian wooden dining table*
- **Past-participle adjectives:** *broken window, frozen lake, written agreement* — must be distinguished from passive verb forms
- **Present-participle adjectives:** *running water, boiling kettle, exciting news* — must be distinguished from progressive verb forms

#### Adverbs
- **Manner:** quickly, slowly, carefully (often `-ly`); also: well, fast, hard
- **Temporal:** now, then, today, yesterday, soon, already, still, yet, ever, never, often, always, sometimes, recently
- **Locative:** here, there, everywhere, nowhere, inside, outside, abroad, home, upstairs
- **Degree:** very, quite, rather, fairly, extremely, too, enough, almost, hardly, barely
- **Sentence (disjuncts):** clearly, obviously, fortunately, frankly, hopefully — modify the whole proposition
- **Conjunctive (linking adverbs):** however, therefore, moreover, furthermore, consequently, nevertheless
- **Focus:** only, even, just, also, too — pick out a constituent
- **Negation:** not, never, no, nowhere, neither

### Closed Classes (Function Words)

#### Pronouns (sub-types)
- **Personal:** I, you, he, she, it, we, they (and object forms me, him, her, us, them)
- **Possessive (used alone):** mine, yours, his, hers, ours, theirs — *that book is mine*
- **Reflexive / intensive:** myself, yourself, himself, herself, itself, ourselves, yourselves, themselves — *I hurt myself / I did it myself*
- **Reciprocal:** each other, one another
- **Demonstrative:** this, that, these, those (also function as determiners)
- **Interrogative:** who, whom, whose, which, what
- **Relative:** who, whom, whose, which, that — also `Ø` (zero relative in object position: *the man (that/Ø) I saw*)
- **Indefinite:** someone, somebody, something; anyone, anybody, anything; everyone, everybody, everything; no one, nobody, nothing; one, none, all, some, any, each, every, either, neither, both, several, many, few, much

#### Determiners (sub-types)
- **Articles:** definite `the`, indefinite `a/an`, zero article `Ø` (mass/plural generic: *I like cats*, *Water is wet*)
- **Demonstrative:** this, that, these, those
- **Possessive:** my, your, his, her, its, our, their (compare with possessive pronouns mine, yours, etc.)
- **Quantifier:** some, any, no, every, each, all, both, half, much, many, several, few, little, enough
- **Numeric:** cardinal (one, two, three), ordinal (first, second, third)
- **Wh-determiners:** which, what, whose

In contrast with French/German, English has **no agreement** between determiner and noun beyond number and definiteness — choice of `a` vs. `an` is purely phonological (consonant vs. vowel onset) and has no grammatical meaning.

#### Prepositions
- **Simple (one word):** in, on, at, of, for, with, by, from, to, about, into, onto, upon, through, between, among, against, before, after, during, since, until, beside, behind, beyond, despite, except
- **Complex (multi-word):** in front of, on top of, in spite of, instead of, because of, due to, according to, as well as, with regard to, by means of, in addition to
- **Stranded prepositions:** *Who are you talking to?* / *the man I was talking about* — preposition appears at the clause edge separated from its noun phrase. This is a major contrast with French/German.
- **Case assignment:** prepositions take the **objective/accusative** case for pronouns — *to him* (not *to he*), *between you and me* (formally) but *between you and I* (often heard, prescriptively wrong)

#### Conjunctions
- **Coordinating (FANBOYS):** for, and, nor, but, or, yet, so — link constituents of equal rank
- **Correlative:** both…and, either…or, neither…nor, not only…but also, whether…or
- **Subordinating:** because, although, though, even though, since (causal/temporal — ambiguous!), while (temporal/concessive), if, unless, until, when, whenever, where, wherever, whereas, before, after, as, as if, as though, so that, in order that, provided that
- **Complementizers:** that (declarative complement), if/whether (interrogative complement), for (infinitival complement: *for him to win*)

#### Particles
A heterogeneous class — function words that don't fit cleanly elsewhere:
- **Infinitive marker:** `to` (always when introducing an infinitive: *to run, to be, to have eaten*) — surface-identical to the preposition `to`
- **Phrasal-verb particle:** up, down, in, out, on, off, away, back, over, through, around — surface-identical to prepositions but behave differently:
  - Particles can move past direct objects (*pick up the box / pick the box up* — both OK)
  - Prepositions cannot (*look up the chimney / *look the chimney up*)
- **Negative particle:** `not` / `n't` (clitic form: *isn't, won't, doesn't*)
- **Discourse / pragmatic particles:** well, oh, like, you know, I mean, anyway

#### Interjections
- ouch, ow, hey, hi, hello, oh, ah, wow, yikes, oops, alas, hooray, hmm, um, uh, eh, yeah, nope, please, thanks

## Language-Specific Features

### Unique Grammatical Phenomena

#### Phrasal Verbs (a major analytical challenge)
A phrasal verb is `verb + particle` (and sometimes verb + particle + preposition) that has a **non-compositional meaning**:
- *give up* (≠ give + up; means surrender/quit)
- *take off* (≠ take + off; departs, of an aircraft)
- *make up* (= invent / reconcile / apply cosmetics — context-dependent)
- *look up* (a word in a dictionary) vs. *look up* (the chimney — literal)
- *put up with* (= tolerate; verb + particle + preposition)
- *run into* (= encounter)

**Test for particle vs. preposition:**
1. **Movement test:** Can the noun appear between verb and particle? *I picked up the box / I picked the box up* (✓ particle); *I looked up the chimney / *I looked the chimney up* (✗ preposition, so particle reading rules out)
2. **Pronoun obligatorily moves:** *I picked it up* (✓), **I picked up it* (✗ — true of particles)
3. **Stress:** particles often bear more stress than prepositions (`pick UP the box` vs. `look up the CHIMNEY`)

The analyzer must tag the particle-vs-preposition distinction; `give-up.particle` and `up.preposition` look identical on the surface.

#### Auxiliary Verb Stacking (the perfect-progressive-passive chain)
Up to four auxiliaries can stack in a single verb phrase:

| Form | Example |
|---|---|
| Modal + perfect + progressive + passive | *The work might have been being done* |
| Modal + perfect + passive | *The work might have been done* |
| Perfect + progressive | *Has been walking* |
| Perfect + passive | *Has been done* |
| Progressive + passive | *Is being done* |

Each auxiliary contributes a specific feature:
- Modal → modality
- `have` (+ past participle) → perfect aspect
- `be` (+ -ing) → progressive aspect
- `be` (+ past participle) → passive voice

The order is rigid: **MODAL > HAVE > BE.PROG > BE.PASS > MAIN**. Any violation is ungrammatical (*has might been walking*).

#### Do-Support
A defining feature of English. When the main verb is a lexical verb (not be, not an auxiliary, not a modal) and the clause requires:
- **Negation:** *I do not run* (not **I run not*)
- **Interrogation:** *Does she run?* (not **Runs she?*)
- **Emphasis:** *I DO know!*
- **Verb-phrase ellipsis:** *He runs faster than I do.*
- **Tag questions:** *She runs, doesn't she?*

…then `do/does/did` is inserted to bear tense and inversion, leaving the main verb in its base form. With auxiliaries or modals, do-support is not used (*Is she running?* not **Does she be running?*).

#### Get-Passive
Alongside the be-passive (*the window was broken*), English has a **get-passive** (*the window got broken*), with subtly different semantics — get-passive is more colloquial, often implies adversity or change of state, and tolerates fewer agent phrases.

#### The English Genitive (the "Saxon genitive" / 's)
A clitic, not a true case marker:
- Attaches to the end of a noun **phrase**, not the head noun: *the King of Spain's daughter* (= the daughter of the King of Spain), *somebody else's problem*
- Two genitives: 's-genitive (*Mary's book*) vs. of-genitive (*the book of Mary*) — the former is preferred for animates, the latter for inanimates and for emphasis
- **Double genitive:** *a friend of mine*, *that book of John's*

#### Dummy / Expletive Subjects
English requires a syntactic subject even when there is no semantic subject:
- Weather expletive: *It is raining*, *It is cold*
- Existential expletive: *There is a book on the table*, *There are three dogs*
- Anticipatory `it`: *It is obvious that he is lying*, *It is hard to say*

Other languages (Spanish, Italian) drop the subject entirely (*Llueve* = "it rains").

#### Tag Questions
A grammatical fingerprint of English: a **declarative + reversed-polarity tag** seeking confirmation:
- *You're coming, aren't you?*
- *He doesn't know, does he?*
- *They've been there, haven't they?*

Tag construction rules: copy the auxiliary (or use do-support), reverse polarity, use a pronominal subject. Modal+perfect tags are particularly tricky (*She might have left, mightn't she?* / *…hasn't she?* — speakers vary).

#### Conditional Sentences (zero, first, second, third)
Distinct conditional patterns:
- **Zero:** *If water boils, it evaporates.* (general truth)
- **First:** *If it rains, I will stay.* (real future)
- **Second:** *If it rained, I would stay.* (hypothetical present/future)
- **Third:** *If it had rained, I would have stayed.* (counterfactual past)
- **Mixed:** *If I had studied, I would be a doctor now.* (counterfactual past, present consequence)

The second/third conditionals use the **subjunctive `were`** (*If I were you*) — one of the few surviving subjunctive forms.

#### Reported (Indirect) Speech and Backshift
Tense in reported speech shifts back one step from the original:
- *"I am tired"* → *He said he was tired.*
- *"I will go"* → *He said he would go.*
- *"I have eaten"* → *He said he had eaten.*

This is mechanical in English and a source of POS-tagging interest because it changes morphological tense without changing event time.

#### Polysemy / Conversion
A massive POS-ambiguity engine. The same surface form can be:
- N and V: *run, walk, drink, smile, dance, dream, hope, fish, water, book, mail*
- N and Adj: *iron* (the metal / iron will)
- V and Adj: many participles (*broken, frozen, written, spoken*)
- Adv and Adj: *fast, hard, late, early, well*
- Adj and Det: *this, that, these, those, all, some, any, each, every*

Resolution requires syntactic context.

## Pedagogical Considerations

### Learning Difficulty Assessment

#### Difficulty Factors for L2 Learners
- **Phrasal verbs:** Vast inventory, often unpredictable meaning, must be memorized
- **Articles:** the/a/an/Ø — particularly hard for speakers of article-less languages (Russian, Mandarin, Japanese, Korean, Hindi)
- **Tense + aspect combinations:** present perfect vs. simple past distinction is famously hard
- **Modal verbs:** subtle modal semantics (*might / may / could / can* for possibility)
- **Pronunciation–spelling mismatch:** silent letters, irregular spelling
- **Word stress:** unmarked in writing, contrastive (*REcord* N vs. *reCORD* V)
- **Prepositions:** highly idiomatic (*on Monday* but *in March*; *interested in* but *fond of*)

#### Easier Aspects for L2 Learners
- **Minimal verb agreement:** only 3sg `-s`
- **No grammatical gender**
- **No noun cases**
- **No adjective agreement**
- **Strict word order** (predictable structure)

#### Learner Profiles
- **Beginner (A1–A2):** Basic SVO sentences, present simple, present progressive, common irregular plurals, definite/indefinite articles, basic prepositions, can/will/must
- **Intermediate (B1–B2):** Past tenses, present/past perfect, all modals, conditionals 1-2, passive voice, relative clauses, common phrasal verbs, gerund vs. infinitive complement
- **Advanced (C1–C2):** Conditional 3 + mixed, perfect progressive aspects, subjunctive, inversion, cleft sentences, advanced phrasal verbs, idioms, register variation

### Common Learning Challenges

#### Frequent Error Patterns
- **Article drop / over-insertion:** **He is teacher* (should be *a teacher*); **the life is short* (should be *life is short*)
- **3sg agreement omission:** **she go* for *she goes*
- **Past tense overregularization:** **goed, breaked, runned*
- **Tense confusion:** present-perfect vs. simple-past (*I have seen him yesterday* — wrong; should be *I saw him yesterday*)
- **Preposition errors:** **depend of* (→ *depend on*), **married with* (→ *married to*)
- **Word order in embedded questions:** **I don't know what is it* (→ *I don't know what it is*)
- **Phrasal-verb word order:** **pick up it* (→ *pick it up*)

#### Conceptual Difficulties
- **Aspect:** progressive (-ing) vs. simple — speakers of Slavic languages often struggle with the inverse mapping
- **Definiteness:** when to use the/a/Ø — particularly for speakers of article-less languages
- **Gerund vs. infinitive complement:** *I enjoy swimming* (gerund) vs. *I want to swim* (infinitive) — verb-specific
- **Modal subtlety:** *must* (obligation) vs. *have to* (external obligation), *should* (advice) vs. *ought to* (slightly stronger)
- **Phrasal-verb meaning:** non-compositional, must be lexicalized
- **Stranded prepositions:** unavailable in many other languages

## Technical Implementation Planning

### AI Prompting Strategy

#### Prompt Complexity Levels

##### Beginner
Roles to surface: **noun, verb, adjective, pronoun, preposition, conjunction, adverb, article (det subset), auxiliary**.
- Focus on basic SVO structure
- Identify subject/object/verb roles explicitly
- Mark articles vs. other determiners
- Tag the auxiliary in basic progressive (*is running*) and perfect (*has eaten*) constructions
- Avoid advanced terminology (no "gerund", no "phrasal verb", no "subjunctive")

##### Intermediate
Add roles: **modal_verb, particle (infinitive `to` + phrasal-verb particle), determiner (vs. article subset), demonstrative_pronoun, possessive_pronoun, possessive_determiner, present_participle (-ing), past_participle (-ed/-en), gerund, infinitive**.
- Explicitly mark modal verbs and explain their semantic flavor (ability/permission/obligation/possibility)
- Distinguish particle `to` (infinitive marker) from preposition `to` (directional)
- Distinguish present participle (in *is running*) from gerund (in *running is fun*) from adjectival -ing (*running water*)
- Distinguish past tense from past participle (in passive or perfect)
- Surface aspect explicitly: simple / progressive / perfect / perfect-progressive

##### Advanced
Add roles: **relative_pronoun, subordinating_conjunction, coordinating_conjunction, interrogative_pronoun, reflexive_pronoun, indefinite_pronoun, comparative, superlative, phrasal_verb, gerund_phrase**.
- Identify relative clauses and resolve antecedents
- Mark coordinating vs. subordinating conjunctions
- Detect phrasal verbs (verb + particle non-compositional combinations) and distinguish from verb + preposition
- Mark subjunctive uses (*if I were*, *I suggest he leave*)
- Tag inversion patterns (*never have I seen…*)
- Identify ellipsis (do-support in tags and VP-ellipsis: *He runs faster than I do*)

#### Language-Specific Prompting
- **Mandate disambiguation reasoning:** the prompt must require the model to *justify* POS choices for ambiguous tokens (`to`, `-ing` words, `-ed` words, `that`, `who/which`, particles vs. prepositions). The validator looks for explicit justification in `individual_meaning`.
- **Aspect must be named:** simple / progressive / perfect / perfect-progressive — not just "verb"
- **Voice must be named:** active vs. passive
- **Modal flavor must be characterized:** ability / permission / obligation / possibility / volition
- **Phrasal-verb identification:** when the verb + particle combine non-compositionally, both tokens must be tagged with a `phrasal_verb_part` linkage, not as `verb + preposition`
- **Subject / object role:** prompt should ask for the syntactic function (subject, direct object, indirect object, complement, modifier-of-X) in the `individual_meaning` field

### Data Structure Design

#### Output Format Requirements
- **Grammatical Role Mapping:** noun, verb, adjective, adverb, pronoun, determiner, preposition, conjunction, particle, auxiliary, modal_verb, interjection — plus the intermediate/advanced subtypes listed above
- **Morphological Analysis:** number (sg/pl), case (nom/acc/gen) for pronouns only, tense (pres/past), aspect (simple/prog/perf/perf-prog), voice (active/passive), modality (for modal verbs), comparative/superlative degree, person (1/2/3) for verbs and pronouns
- **`individual_meaning` field (REQUIRED):** Multi-sentence per-word explanation. Must include:
  1. The grammatical role
  2. Tense/aspect/case where applicable
  3. The word's syntactic function in *this* sentence (e.g., "subject of `eat`", "direct object of `gave`", "modifier of `book`", "head of the prepositional phrase `in the kitchen`")
  4. For ambiguous tokens, an explicit disambiguation note
- **Confidence Scoring:** 0.0–1.0 per token; aggregate sentence confidence is the mean. Penalize ambiguity: if a token is one of `{to, -ing forms, -ed forms, that, who, which, particle/preposition surface forms}` and the prompt's reasoning trace doesn't disambiguate explicitly, drop confidence to <0.85.

#### Validation Rules
- **Required Fields:** role, individual_meaning (≥30 chars per word in fallback path)
- **Quality Thresholds:**
  - Production confidence ≥ 0.85 (else trigger repair)
  - Fallback path always reports `is_fallback: True` and is capped at 0.3 confidence regardless of content quality
  - Multi-clause explanations (no POS-only stubs like *"verb"* — must read like *"3rd-person-singular present-tense form of `eat`, the main predicate, taking `the cat` as its subject and `the fish` as its direct object"*)
- **Fallback Mechanisms:** 5-level parsing chain — (1) direct JSON, (2) markdown code-block-wrapped JSON, (3) JSON repair (fix common issues: trailing commas, unquoted keys, smart quotes), (4) text-pattern extraction (regex over `WORD: ROLE — explanation` lines), (5) rule-based morphological fallback (use suffix patterns, capitalization, position to assign best-guess POS)

#### English-Specific Processing Challenges
- **Disambiguation of `to`:** if the next word is a verb in base form, tag as infinitive marker (particle); else as preposition
- **Disambiguation of `-ing` forms:**
  - After `be`-aux → present participle (verb)
  - As subject or object of another verb → gerund (noun)
  - Before a noun in attributive position → adjectival participle (adjective)
- **Disambiguation of `-ed` forms:**
  - After `have`-aux → past participle (verb)
  - After `be`-aux → past participle in passive (verb)
  - Before a noun in attributive position → adjectival participle (adjective)
  - Otherwise → past tense (verb)
- **Disambiguation of `that`:**
  - Followed directly by a noun → demonstrative determiner (*that book*)
  - Standing alone as subject/object → demonstrative pronoun (*that is mine*)
  - After a noun, introducing a clause → relative pronoun (*the book that I read*)
  - After a verb of saying/thinking, introducing a clause → subordinating conjunction (*I think that he's right*)
- **`who/which`:** interrogative if clause-initial in a question; relative if following a noun phrase
- **Phrasal-verb particle vs. preposition:** apply the movement test (does pronoun precede the candidate?)
- **Capitalization detection:** sentence-initial words may be common nouns or proper nouns — context required
- **Contraction expansion:** `don't = do + not`, `won't = will + not`, `'s` (= is / has / possessive), `'d` (= would / had), `'ll` (= will / shall), `'ve` (= have), `'re` (= are), `'m` (= am)
- **Homograph resolution:** `read` (present /riːd/ vs. past /rɛd/), `lead` (verb vs. noun "metal"), `wind` (noun /wɪnd/ vs. verb /waɪnd/), `tear` (rip vs. cry-drop), `bow` (weapon vs. bend-down)

## Production-Ready Features

### JSON Schema Compliance
The analyzer's output must include for every analyzed token:
```
{
  "word": str,
  "role": str,                  // canonical POS or sub-type
  "individual_meaning": str,    // ≥30 chars, multi-clause
  "tense": str?,                // present | past
  "aspect": str?,               // simple | progressive | perfect | perfect_progressive
  "voice": str?,                // active | passive
  "case": str?,                 // nom | acc | gen — pronouns only
  "number": str?,               // singular | plural
  "person": str?,               // 1 | 2 | 3
  "degree": str?,               // positive | comparative | superlative
  "modality": str?,             // ability | permission | obligation | possibility | volition
  "syntactic_function": str?,   // subject | direct_object | indirect_object | complement | modifier_of_X | …
  "is_phrasal_verb_part": bool?,
  "phrasal_verb_partner_idx": int?,  // index of partner token if part of a phrasal verb
  "confidence": float            // 0.0–1.0
}
```

Plus sentence-level fields:
```
{
  "sentence_structure": str,    // free-text overview, e.g., "SVO declarative with present progressive"
  "tense_aspect": str,          // global tense/aspect summary
  "voice": str,                 // global voice
  "is_fallback": bool,          // True iff rule-based fallback was used
  "confidence": float
}
```

### APKG Output and HTML Color Coding
The analyzer's color scheme (`get_color_scheme(complexity)`) must declare HTML hex colors for each role at each complexity level. The grammar processor consumes these colors and emits `<span style="color: …">word</span>` markup for the front of each Anki card. **Critical invariant:** the analyzer's POS labels and colors must NOT be remapped by `grammar_processor._convert_analyzer_output_to_explanations()` — it passes them through verbatim. Pick distinct, accessible colors for the open-class POS (noun = saturated blue, verb = saturated red, adjective = green, adverb = orange) and softer colors for closed-class items (preposition = teal, conjunction = purple, particle = brown, auxiliary = light red, modal = darker red).

### Lazy Imports — CRITICAL
The analyzer module must NOT have `from streamlit_app.shared_utils import …` at module level. The analyzer registry uses `importlib.import_module()` for discovery, and module-level imports of `shared_utils` capture function references at import time, which makes them un-mockable by `unittest.mock.patch()` and causes cross-test contamination in E2E pipeline tests. Move all `streamlit_app.shared_utils` imports inside the `_call_ai()` method body. (See CLAUDE.md "Coding Conventions — Analyzer imports".)

### 5-Level Fallback Parsing Chain (in `en_response_parser.py`)
1. **Direct JSON parse** — `json.loads(response)` — fastest path
2. **Markdown code-block extraction** — strip leading/trailing ```json fences and reparse
3. **JSON repair** — fix trailing commas, unquoted keys, smart quotes, missing commas; reparse
4. **Text-pattern extraction** — regex over plain-text formats like `WORD: ROLE — explanation`
5. **Rule-based morphological fallback** — `en_fallbacks.py` consumes the original sentence, applies suffix patterns (`-ing`, `-ed`, `-ly`, `-tion`, `-ness`, `-er`, `-est`), POS lookup tables (article list, modal list, pronoun list, preposition list), and position heuristics. Output sets `is_fallback: True` so the validator caps confidence at 0.3 regardless of explanation quality.

## Quality Assurance

### Confidence Targets
- **Production threshold:** ≥ 0.85 sentence-level mean confidence required for non-repair acceptance
- **Repair trigger:** if confidence < 0.85, the response parser triggers an AI repair pass at temperature=0.4 (per the project's repair contract); repair is only accepted if it raises confidence
- **Fallback cap:** any output with `is_fallback: True` is hard-capped at 0.3 confidence — explanation quality cannot lift this

### Rule-Based Fallback Quality Bar
The rule-based fallback (`en_fallbacks.py`) must NEVER emit POS-only stubs. Every word's `individual_meaning` must be ≥30 characters and read as multi-clause natural-English prose. Pattern:
> *"This is a {role}; in the present sentence it functions as the {syntactic_function}. {Optional morphological note: tense/aspect/case/etc.}"*

Examples:
- *eat*: *"This is a verb in the simple present tense; it serves as the main predicate of the sentence and takes 'the cat' as its subject and 'the fish' as its direct object."*
- *the*: *"This is the definite article; it specifies the noun 'cat' as a particular, identifiable referent."*
- *quickly*: *"This is a manner adverb derived from the adjective 'quick' by the -ly suffix; it modifies the verb 'ran' and answers the question 'how?'"*

### Test Coverage Requirements
The `tests/` directory must include unit tests for each domain component, integration tests, and a Phase 8 E2E mock for all three difficulty levels (beginner / intermediate / advanced) wired into `tests/test_end_to_end_pipeline.py` following the Latvian pattern (`_run_full_pipeline(data, f"english_{difficulty}", tmp_path)` parameterized).

### Disambiguation Test Cases (mandatory)
The validator and tests must explicitly cover:
1. *I want to run.* — `to` = infinitive marker (particle); `run` = base verb (infinitive)
2. *I drove to school.* — `to` = preposition; `school` = object of preposition
3. *Running is fun.* — `Running` = gerund (noun); `is` = copula
4. *She is running.* — `running` = present participle (verb); progressive aspect
5. *The running water is cold.* — `running` = adjectival participle modifying `water`
6. *She walked home.* — `walked` = past tense verb
7. *She has walked home.* — `walked` = past participle (perfect aspect)
8. *The well-walked path.* — `walked` = adjectival past participle
9. *That book is mine.* — `That` = demonstrative determiner
10. *I know that.* — `that` = demonstrative pronoun
11. *The book that I read.* — `that` = relative pronoun
12. *I think that he's right.* — `that` = subordinating conjunction (complementizer)
13. *Who is at the door?* — `Who` = interrogative pronoun
14. *The man who came.* — `who` = relative pronoun
15. *Look up the word.* — `up` = phrasal-verb particle
16. *Look up the chimney.* — `up` = preposition

A test fails if the analyzer assigns the wrong category to any of these in the absence of an explicit disambiguation justification.

## Implementation Risks and Challenges

### Technical Complexity
- **Categorial ambiguity:** The same surface form often spans 3-5 POS classes — far more pervasive than in inflected languages where morphology disambiguates
- **Phrasal-verb detection:** Requires lexical knowledge (which V+P combinations are non-compositional) plus the movement test on direct objects
- **Auxiliary chain parsing:** Up to four stacked auxiliaries (modal + have + be + be + main) — must correctly extract tense, aspect, voice
- **Contraction expansion:** Tokenizer must split `don't` into `do + n't` (or `do + not`) and tag each piece independently
- **Homograph resolution:** `read`/`read`, `lead`/`lead`, `wind`/`wind`, `tear`/`tear` — pronunciation differs but spelling identical, so context required

### Linguistic Challenges
- **Idiomatic prepositions:** *interested in*, *fond of*, *jealous of*, *good at*, *afraid of* — must be tagged correctly even though logically interchangeable
- **Subjunctive recognition:** *if I were*, *I suggest he leave* — uninflected base form looks like indicative
- **Cleft / pseudo-cleft:** *It was John who broke the window*, *What I want is rest* — non-canonical word order
- **Stranded prepositions:** *the man I was talking about* — the preposition's object is fronted
- **Bare relatives:** *the book I read* — the relative pronoun is omitted, must be reconstructed for analysis

### AI Prompting Challenges
- **Disambiguation discipline:** GPT-style models often guess plausibly without showing reasoning — the prompt must mandate explicit reasoning in `individual_meaning`
- **Phrasal-verb consistency:** Models sometimes label `up` as preposition even when it's a particle — the validator must check the linkage
- **Aspect specificity:** Models sometimes default to "verb" without naming the aspect — the validator must reject this
- **Modal flavor:** Models sometimes treat all modals identically — the prompt must ask for the modal sense (ability vs. obligation vs. possibility vs. permission)

### Quality Assurance Needs
- **Comprehensive test corpus:** Sentences exercising the disambiguation matrix above + canonical and non-canonical constructions (questions, passives, clefts, relative clauses, conditionals, reported speech, tag questions)
- **Edge cases:** archaic/literary forms (*whom, whence, hither*), British vs. American spelling variants, dialect features
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
1. Create `languages/english/` scaffold mirroring `languages/german/` and `languages/french/`
2. Create `domain/`, `infrastructure/data/`, `tests/` subdirectories
3. Stub the 17 required files

### Phase 3: Domain Components (Opus)
1. `domain/en_config.py` — language config, role inventory per tier, color scheme, prompt templates
2. `domain/en_prompt_builder.py` — Jinja2-based AI prompt construction with explicit disambiguation instructions
3. `domain/en_response_parser.py` — 5-level fallback parsing
4. `domain/en_validator.py` — 0.85 threshold, natural scoring, fallback cap at 0.3
5. `domain/en_fallbacks.py` — rule-based morphological fallback (suffix patterns, lookup tables, position heuristics, multi-clause explanations)

### Phase 4: Infrastructure (Sonnet)
1. AI service shim with circuit breaker
2. Lazy import of `streamlit_app.shared_utils` inside `_call_ai`
3. Caching layer for repeated sentence analyses

### Phase 5: Configuration Files (Haiku)
1. `infrastructure/data/grammatical_roles.yaml` — full role inventory with parent links
2. `infrastructure/data/language_config.yaml` — high-level metadata
3. `infrastructure/data/patterns.yaml` — disambiguation rules, suffix patterns, lookup tables
4. `infrastructure/data/word_meanings.json` — high-frequency word → POS / meaning lookup for fallback

### Phase 6: Tests (Sonnet)
1. Unit tests for each domain component
2. Integration tests for the full pipeline
3. Disambiguation test suite (the 16 cases above + variants)

### Phase 7: Deployment Documentation (Haiku)
1. README and changelog
2. Registry integration guide

### Phase 8: E2E Pipeline (Sonnet)
1. Beginner / intermediate / advanced mock data
2. Wire into `tests/test_end_to_end_pipeline.py` per Latvian pattern
3. Generate `tests/reports/pipeline_report_english_{level}.txt` for each level

## Validation Checklist

- [ ] Confidence ≥ 0.85 on AI path; rule-based fallback hard-capped at 0.3
- [ ] `is_fallback: True` flag emitted by `en_fallbacks.py` and respected by validator
- [ ] All 16 disambiguation cases pass
- [ ] Lazy import of `streamlit_app.shared_utils` inside `_call_ai`
- [ ] Color scheme passes through grammar_processor verbatim (no remap)
- [ ] `individual_meaning` ≥30 chars, multi-clause, names role + tense/aspect/case + syntactic function
- [ ] 5-level fallback parsing chain implemented
- [ ] APKG-compatible HTML output
- [ ] All three difficulty levels exercised end-to-end
- [ ] Registry entry added (`folder_name → "en"` in `analyzer_registry.py`)
