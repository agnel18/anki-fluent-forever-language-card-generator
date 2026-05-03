# languages/russian/domain/ru_prompt_builder.py
"""
Russian Prompt Builder — Domain Component

Builds AI prompts for Russian grammar analysis.
Russian-specific: mandates case + gender + number + animacy on every
nominal, aspect + tense + person + number on every finite verb, governed
case on every preposition, and disambiguation reasoning for the canonical
ambiguity tokens (что, как, это, один, свой/его, себя/-ся).

The prompt requests `individual_meaning` (multi-sentence per-word
explanation) — NOT a flat `meaning` field. The response parser preserves
`individual_meaning` and formats display as
``f"{word} ({role}): {individual_meaning}"``.
"""

import logging
from typing import List, Optional

from .ru_config import RuConfig

logger = logging.getLogger(__name__)


class RuPromptBuilder:
    """Builds prompts for Russian grammar analysis using Gemini AI."""

    def __init__(self, config: RuConfig):
        self.config = config

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def build_single_prompt(
        self, sentence: str, target_word: str, complexity: str
    ) -> str:
        """Build a prompt for analysing one Russian sentence."""
        roles = self._get_roles_for_complexity(complexity)
        special_notes = self._get_special_notes(complexity)
        return self._format_prompt(
            sentences=[sentence],
            target_word=target_word,
            complexity=complexity,
            roles=roles,
            special_notes=special_notes,
            batch=False,
        )

    def build_batch_prompt(
        self, sentences: List[str], target_words, complexity: str
    ) -> str:
        """Build a prompt for analysing multiple Russian sentences.

        ``target_words`` may be a single string (same target for all
        sentences) or a list-like of per-sentence targets.
        """
        if isinstance(target_words, (list, tuple)):
            target_word = target_words[0] if target_words else ""
        else:
            target_word = target_words or ""
        roles = self._get_roles_for_complexity(complexity)
        special_notes = self._get_special_notes(complexity)
        return self._format_prompt(
            sentences=sentences,
            target_word=target_word,
            complexity=complexity,
            roles=roles,
            special_notes=special_notes,
            batch=True,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_roles_for_complexity(self, complexity: str) -> List[str]:
        default_roles = self.config._get_default_roles()
        level = default_roles.get(complexity, default_roles["intermediate"])
        return list(level.keys())

    def _get_special_notes(self, complexity: str) -> str:
        base = (
            "RUSSIAN-SPECIFIC RULES (mandatory for every analysis):\n"
            "1. Russian has 6 grammatical cases: nominative (Им.), genitive (Род.), "
            "   dative (Дат.), accusative (Вин.), instrumental (Тв.), prepositional (Предл.). "
            "   ALWAYS state the case of every noun, adjective, pronoun, numeral, and participle.\n"
            "2. Russian has 3 genders: masculine, feminine, neuter (plus a small `common` set "
            "   like сирота/судья). State gender on every nominal.\n"
            "3. Animacy is grammatically visible on masculine accusative singular and on every "
            "   plural accusative — animate masc-acc takes the genitive form (вижу мальчика), "
            "   inanimate masc-acc takes the nominative form (вижу стол). State animacy on every "
            "   masc-acc and every pl-acc.\n"
            "4. Aspect is LEXICAL but mandatory: every verb is imperfective (несовершенный вид) "
            "   or perfective (совершенный вид). State the aspect on every verb. Note: present-tense "
            "   conjugation of a perfective stem yields PERFECTIVE FUTURE (напишу = 'I will write'), "
            "   NOT a present.\n"
            "5. The reflexive clitic -ся / -сь is polysemous. Subtypes: true reflexive (умывается), "
            "   reciprocal (целуются), passive (книга пишется), middle/spontaneous (дверь открылась), "
            "   lexicalized intransitive (смеяться, бояться, нравиться). Identify the subtype in "
            "   `individual_meaning`.\n"
            "6. Every preposition GOVERNS a specific case (or two with a meaning split — в/на take "
            "   acc for motion-into vs. prep for static location). State the governed case on every "
            "   preposition.\n"
            "7. Russian has NO articles. Definiteness is conveyed by word order, demonstratives, "
            "   or context — do NOT introduce phantom 'the/a' tokens.\n"
            "8. The present-tense copula быть is SILENT in standard Russian (Он студент = 'He [is] "
            "   a student'). Do NOT emit a phantom есть/copula token unless есть actually appears in "
            "   the sentence. The em-dash in writing (Москва — столица) is orthographic, not lexical.\n"
        )
        if complexity in ("intermediate", "advanced"):
            base += (
                "9. Distinguish reflexive possessive свой from non-reflexive его/её/их based on "
                "   subject-coreference: свой is required when the possessor IS the clause subject; "
                "   его/её/их refers to a different person.\n"
                "10. Genitive of negation: under не, direct objects can shift from accusative to "
                "    genitive (Я не вижу книги). Mark the case shift in `individual_meaning`.\n"
                "11. Numerals 2/3/4 govern genitive singular (два стола, три книги, четыре окна); "
                "    numerals 5+ govern genitive plural (пять столов, десять книг). State the "
                "    induced case in the noun's `individual_meaning`.\n"
                "12. Mood: indicative is unmarked; imperative uses -й/-и/-ь endings; conditional "
                "    uses past tense + the clitic particle бы.\n"
                "13. Predicate instrumental: after past or future of быть (был/была/будет), profession/"
                "    state predicates take instrumental (Он был врачом).\n"
                "14. Verbs of motion split into determinate (one-way / in progress: иду, еду, лечу) "
                "    vs. indeterminate (multidirectional / habitual: хожу, езжу, летаю); identify the "
                "    subtype where present.\n"
            )
        if complexity == "advanced":
            base += (
                "15. Russian has 4 PARTICIPLE types — present active (-ущ/-ющ/-ащ/-ящ), past active "
                "    (-вш/-ш), present passive (-ем/-им), past passive (-нн/-енн/-ённ/-т). All "
                "    decline as long-form adjectives. Tag each token with the precise participle role.\n"
                "16. Gerunds (деепричастия) are uninflected verbal adverbs: present -я/-а (читая), "
                "    past -в/-вши (прочитав). Tag as `gerund`.\n"
                "17. Split the particle bucket: ли (interrogative), бы (conditional / "
                "    aspectual_particle), не (negation_particle), ни (negation_particle, emphatic), "
                "    же (contrastive emphasis particle), вот / ведь / уж (discourse particles).\n"
                "18. Disambiguate что: pronoun ('what' — subject/object of own clause) vs. "
                "    complementizer ('that' — introduces a finite subordinate clause).\n"
                "19. Disambiguate как: interrogative adverb ('how'), comparator ('as, like'), "
                "    temporal subordinator ('when, as').\n"
                "20. Disambiguate это: invariant deictic / copular substitute ('this is X') vs. "
                "    declined demonstrative determiner (этот/эта/это/эти form-set).\n"
            )
        return base

    def _format_prompt(
        self,
        sentences: List[str],
        target_word: str,
        complexity: str,
        roles: List[str],
        special_notes: str,
        batch: bool,
    ) -> str:
        roles_str = ", ".join(roles)

        if batch:
            sentences_block = "\n".join(
                f'{i+1}. "{s}"' for i, s in enumerate(sentences)
            )
            sentence_instruction = (
                f"Analyze ALL {len(sentences)} sentences below:\n{sentences_block}\n\n"
                f'The target vocabulary word to highlight is: "{target_word}"\n\n'
                "Return a JSON ARRAY (one object per sentence) in the exact schema shown."
            )
            schema_note = (
                "Return a JSON ARRAY with one object per sentence. "
                "Each object must have exactly the keys shown in the schema below."
            )
        else:
            sentence_instruction = (
                f'Analyze this Russian sentence: "{sentences[0]}"\n\n'
                f'Target vocabulary word: "{target_word}"\n\n'
                "Return a single JSON object in the exact schema shown."
            )
            schema_note = (
                "Return a single JSON object with exactly the keys shown in the schema below."
            )

        prompt = f"""You are an expert Russian linguistics professor analyzing Russian grammar for language learners.

COMPLEXITY LEVEL: {complexity}
LANGUAGE: Russian (Русский язык)
FAMILY: Indo-European, East Slavic
SCRIPT: Cyrillic (LTR)

{sentence_instruction}

{special_notes}

GRAMMATICAL ROLES to use at this level:
{roles_str}

{schema_note}

JSON SCHEMA:
{{
  "sentence": "<the original sentence>",
  "overall_structure": "<2-3 sentence description: subject, predicate, clauses, key constructions, information structure if marked>",
  "sentence_structure": "<same as overall_structure — include both keys>",
  "word_explanations": [
    {{
      "word": "<exact word from sentence (Cyrillic)>",
      "grammatical_role": "<grammatical role from the allowed roles list>",
      "color": "<hex color for this role>",
      "individual_meaning": "<COMPREHENSIVE multi-sentence explanation — see CRITICAL section below>",
      "case": "<nominative | genitive | dative | accusative | instrumental | prepositional, if applicable>",
      "gender": "<masculine | feminine | neuter | common, if applicable>",
      "number": "<singular | plural, if applicable>",
      "animacy": "<animate | inanimate, REQUIRED for masc-acc and pl-acc nominals>",
      "aspect": "<imperfective | perfective | bi-aspectual, REQUIRED on every verb>",
      "tense": "<present | past | future, if verb>",
      "person": "<1 | 2 | 3, if verb or personal pronoun>",
      "mood": "<indicative | imperative | conditional, if verb>",
      "voice": "<active | passive | reflexive_true | reflexive_reciprocal | reflexive_middle | reflexive_inherent>",
      "governed_case": "<the case this preposition governs, if preposition>",
      "lemma": "<dictionary form / lemma of the word>"
    }}
  ],
  "grammar_notes": "<key grammar points for learners at {complexity} level>",
  "confidence": <float 0.0 to 1.0>
}}

CRITICAL: Provide COMPREHENSIVE explanations for EVERY word in the `individual_meaning` field.
Each `individual_meaning` MUST be 1-3 full sentences (typically 25-75 words) and MUST cover:
  - The word's grammatical function in THIS sentence (subject, direct object, modifier of which
    noun, head of which prepositional phrase, etc.). Russian word order is free — derive function
    from CASE, not position.
  - Its morphology — for nouns/adjectives/pronouns/numerals: name the case + gender + number
    (+ animacy where it applies, i.e. masc-acc and pl-acc). For verbs: aspect + tense + person +
    number + mood; if past tense, also gender. For prepositions: the governed case. For
    adjectives: long form vs. short form (predicative).
  - Its lemma / dictionary form when the surface form is inflected.
  - Any Russian-specific feature relevant to that word: aspectual partner (e.g. "perfective of
    писать"); reflexive subtype for -ся verbs; participle type; verb-of-motion determinate vs.
    indeterminate; predicate instrumental triggered by past/future быть; genitive of negation;
    numeral-induced case (gen-sg after 2/3/4, gen-pl after 5+).
  - For ambiguous tokens — что (pronoun vs. complementizer), как (adverb vs. comparator vs.
    subordinator), это (deictic vs. demonstrative), один (numeral vs. indefinite-article-like),
    свой (reflexive possessive — must be subject-coreferent) — explicitly state which reading
    applies and why.

EXAMPLE — for the sentence "Я читаю интересную книгу.":
  "Я"        → "Personal pronoun, 1st-person singular, nominative case. Subject of the verb
                читаю; Russian is pro-drop so the explicit pronoun is mildly emphatic here."
  "читаю"    → "Imperfective verb, 1st-conjugation, present tense, 1st-person singular,
                indicative mood. Lemma читать ('to read'); the perfective partner is прочитать.
                Imperfective marks the action as ongoing or habitual ('I am reading' /
                'I read'). Governs an accusative direct object (книгу)."
  "интересную" → "Long-form adjective, accusative singular feminine. Agrees with the head noun
                  книгу in case, gender, and number. Lemma интересный ('interesting'); the
                  long form is used attributively here."
  "книгу"    → "Noun, accusative singular feminine, 1st declension (lemma книга, hard stem).
                Direct object of читаю. Inanimate, so the accusative is shaped like the
                nominative endings of the 1st declension (here -у)."
  "."        → "Sentence-final period; ends the declarative clause."

EXAMPLE — for the sentence "Я написал письмо.":
  "Я"        → "Personal pronoun, 1st-person singular, nominative case. Subject."
  "написал"  → "Perfective verb, past tense, masculine singular. Lemma написать (perfective
                of писать). The на- prefix perfectivises the imperfective stem писать; perfective
                aspect signals the action is completed and bounded ('I wrote and finished'). Past
                tense is marked by -л + masculine ∅ ending (gender is read off the past form,
                not person)."
  "письмо"   → "Noun, accusative singular neuter, 2nd declension (lemma письмо, 'letter').
                Direct object of написал. Inanimate neuter — accusative is identical to
                nominative."
  "."        → "Sentence-final period."

EXAMPLE — for the sentence "Дверь открылась.":
  "Дверь"    → "Noun, nominative singular feminine, 3rd declension (soft-sign feminine; lemma
                дверь). Subject of the clause."
  "открылась" → "Reflexive verb, perfective past, feminine singular. Lemma открыться
                 ('to open' — middle/spontaneous reflexive; the non-reflexive partner открыть
                 is transitive). The -ся here is the MIDDLE / spontaneous subtype — the door
                 opened by itself, no external agent expressed. Past -ла marks feminine
                 singular agreement with subject Дверь."
  "."        → "Sentence-final period."

EXAMPLE — for the sentence "Мы идём в школу.":
  "Мы"       → "Personal pronoun, 1st-person plural, nominative. Subject of идём."
  "идём"     → "Imperfective DETERMINATE verb of motion, present tense, 1st-person plural,
                indicative. Lemma идти. Determinate verbs of motion describe a unidirectional
                action in progress ('we are going [right now, toward a destination]'); the
                indeterminate counterpart ходить would describe habitual or multidirectional
                going."
  "в"        → "Preposition meaning 'to / into'. Here governs the ACCUSATIVE case (motion
                into a goal). Contrast: в школе with prepositional case = 'at school' (static
                location)."
  "школу"    → "Noun, accusative singular feminine, 1st declension (lemma школа). Goal of the
                motion verb идём, governed by the directional preposition в. Accusative because
                в expresses direction-into here, not location-in."
  "."        → "Sentence-final period."

IMPORTANT:
- Every word in the sentence MUST appear in word_explanations, including punctuation tokens.
- For punctuation tokens use role "other", color "#808080", and a brief individual_meaning like
  "Sentence-final period; ends the declarative clause."
- DO NOT emit single-word stubs like "Я (pronoun)" or "читаю (verb)". The individual_meaning
  MUST be a full sentence with case/gender/number on nominals and aspect/tense/person/number on
  verbs.
- DO NOT label adjectives, determiners, or pronouns as "noun". мой/твой/наш/ваш/свой are
  `possessive_determiner` (or `possessive_pronoun`); этот/тот are `demonstrative`; который is
  `relative_pronoun`.
- Use the EXACT color values from this mapping:
  noun=#FFAA00, verb=#4ECDC4, imperfective_verb=#4ECDC4, perfective_verb=#4ECDC4,
  infinitive=#4ECDC4, imperative=#4ECDC4,
  modal_verb=#00CED1, auxiliary=#00CED1, copula=#00CED1, reflexive_verb=#20B2AA,
  adjective=#FF44FF, short_adjective=#CC33CC, comparative=#FF44FF, superlative=#FF44FF,
  adverb=#FF6347,
  pronoun=#9370DB, personal_pronoun=#9370DB, possessive_pronoun=#9370DB,
  possessive_determiner=#9370DB, reflexive_pronoun=#DDA0DD, demonstrative=#B8860B,
  relative_pronoun=#9370DB, interrogative_pronoun=#9370DB,
  indefinite_pronoun=#8B7EC8, negative_pronoun=#8B7EC8,
  preposition=#4444FF,
  conjunction=#AAAAAA, coordinating_conjunction=#AAAAAA, subordinating_conjunction=#888888,
  particle=#20B2AA, aspectual_particle=#FF1493, conditional_particle=#FF1493,
  negation_particle=#FF6347,
  numeral=#3CB371, interjection=#FF69B4,
  participle=#FF8C00, present_active_participle=#FF8C00, past_active_participle=#FF8C00,
  present_passive_participle=#FF8C00, past_passive_participle=#FF8C00,
  gerund=#FFA500, verbal_noun=#DAA520, other=#808080
- Confidence should be ≥ 0.85 for a complete, correct analysis.
- Return ONLY valid JSON — no markdown, no prose before or after.
"""
        return prompt
