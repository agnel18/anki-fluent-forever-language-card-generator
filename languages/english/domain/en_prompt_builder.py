# languages/english/domain/en_prompt_builder.py
"""
English Prompt Builder — Domain Component

Builds AI prompts for English grammar analysis.
English-specific: highlights analytic morphology, auxiliary stacks,
phrasal verbs, and categorical ambiguity (to / -ing / -ed / that / who-which).
"""

import logging
from typing import List, Optional

from .en_config import EnConfig

logger = logging.getLogger(__name__)


class EnPromptBuilder:
    """Builds prompts for English grammar analysis using Gemini AI."""

    def __init__(self, config: EnConfig):
        self.config = config

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def build_single_prompt(
        self, sentence: str, target_word: str, complexity: str
    ) -> str:
        """Build a prompt for analysing one English sentence."""
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
        self, sentences: List[str], target_word: str, complexity: str
    ) -> str:
        """Build a prompt for analysing multiple English sentences."""
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
        """Disambiguation rules English analyzers MUST surface in their reasoning."""
        base = (
            "ENGLISH-SPECIFIC RULES:\n"
            "1. English has minimal inflectional morphology — most grammar is carried by "
            "   word order and function words (auxiliary verbs, articles, prepositions).\n"
            "2. Mark articles (a / an / the) distinctly from other determiners "
            "   (this / that / some / each).\n"
            "3. For pronouns, identify the case explicitly: nominative (I, he, she, we, they, who), "
            "   accusative (me, him, her, us, them, whom), genitive determiner (my, his, her, our, their), "
            "   genitive pronoun (mine, his, hers, ours, theirs), reflexive (myself, himself, ...).\n"
            "4. Disambiguate `to`: if followed by a base verb → infinitive_marker (particle); "
            "   if followed by a noun phrase → preposition.\n"
        )
        if complexity in ("intermediate", "advanced"):
            base += (
                "5. Disambiguate `-ing` forms:\n"
                "   - After be-aux (is/am/are/was/were/being) → present_participle (verb, progressive aspect).\n"
                "   - As subject or object of another verb (or after a preposition) → gerund (noun).\n"
                "   - Before a noun in attributive position (running water) → adjectival -ing form (adjective).\n"
                "6. Disambiguate `-ed` / `-en` forms:\n"
                "   - After have-aux (have/has/had) → past_participle, perfect aspect (verb).\n"
                "   - After be-aux (is/was/being/been) + by-phrase → past_participle, passive voice (verb).\n"
                "   - Before a noun in attributive position (broken window) → adjectival past participle (adjective).\n"
                "   - Otherwise as the main predicate → past tense (verb).\n"
                "7. Modal verbs (can/could/will/would/shall/should/may/might/must/ought) are DEFECTIVE — "
                "   no -s, no infinitive, no participles. Always tag as modal_verb. Name the modal sense: "
                "   ability / permission / obligation / possibility / volition.\n"
                "8. Auxiliary stack ordering is rigid: MODAL > HAVE > BE.PROGRESSIVE > BE.PASSIVE > MAIN. "
                "   Identify the contribution of each: have→perfect, be+ing→progressive, be+pp→passive.\n"
                "9. Name aspect explicitly: simple / progressive / perfect / perfect_progressive. "
                "   Name voice: active / passive.\n"
            )
        if complexity == "advanced":
            base += (
                "10. Disambiguate `that`:\n"
                "    - Followed directly by a noun (that book) → demonstrative determiner.\n"
                "    - Standing alone as subject or object (that is mine) → demonstrative pronoun.\n"
                "    - After a noun, introducing a clause (the book that I read) → relative_pronoun.\n"
                "    - After a verb of saying/thinking, introducing a clause (I think that he's right) "
                "      → subordinating_conjunction (complementizer).\n"
                "11. Disambiguate `who/which/whose`:\n"
                "    - Clause-initial in a question → interrogative_pronoun.\n"
                "    - After a noun phrase, introducing a clause → relative_pronoun.\n"
                "12. Phrasal-verb particle vs. preposition: apply the movement test. If the object can move "
                "    BETWEEN the verb and the candidate (pick the box up) → phrasal_verb_particle. If it cannot "
                "    (*look the chimney up) → preposition.\n"
                "13. Mark coordinating (FANBOYS: for/and/nor/but/or/yet/so) vs. subordinating "
                "    (because/although/if/when/since/...) conjunctions distinctly.\n"
                "14. Comparatives (-er / more X) and superlatives (-est / most X) get their own roles.\n"
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
                f'Analyze this English sentence: "{sentences[0]}"\n\n'
                f'Target vocabulary word: "{target_word}"\n\n'
                "Return a single JSON object in the exact schema shown."
            )
            schema_note = (
                "Return a single JSON object with exactly the keys shown in the schema below."
            )

        prompt = f"""You are an expert English linguistics professor analyzing English grammar for language learners.

COMPLEXITY LEVEL: {complexity}
LANGUAGE: English
FAMILY: Indo-European, West Germanic
SCRIPT: Latin (LTR)

{sentence_instruction}

{special_notes}

GRAMMATICAL ROLES to use at this level:
{roles_str}

{schema_note}

JSON SCHEMA:
{{
  "sentence": "<the original sentence>",
  "overall_structure": "<2-3 sentence description: subject, predicate, clause type, key constructions, tense+aspect+voice>",
  "sentence_structure": "<same as overall_structure — include both keys>",
  "tense_aspect": "<global summary: simple_present / past_progressive / present_perfect / etc.>",
  "voice": "<active or passive>",
  "word_explanations": [
    {{
      "word": "<exact word from sentence>",
      "grammatical_role": "<grammatical role from the allowed roles list>",
      "color": "<hex color for this role>",
      "individual_meaning": "<COMPREHENSIVE multi-sentence explanation of this word's grammatical function, morphology, and contribution to the sentence — see CRITICAL section below>",
      "tense": "<present / past — for verbs only>",
      "aspect": "<simple / progressive / perfect / perfect_progressive — for verbs only>",
      "voice": "<active / passive — for verbs only>",
      "case": "<nominative / accusative / genitive_determiner / genitive_pronoun / reflexive — for pronouns only>",
      "number": "<singular / plural>",
      "person": "<1 / 2 / 3 — for verbs and pronouns>",
      "degree": "<positive / comparative / superlative — for adjectives/adverbs>",
      "modality": "<ability / permission / obligation / possibility / volition — for modals>",
      "syntactic_function": "<subject / direct_object / indirect_object / complement / modifier_of_X / head_of_pp_X / ...>",
      "is_phrasal_verb_part": <true or false>,
      "lemma": "<dictionary form / lemma of the word>"
    }}
  ],
  "grammar_notes": "<key grammar points for learners at {complexity} level>",
  "confidence": <float 0.0 to 1.0>
}}

CRITICAL: Provide COMPREHENSIVE explanations for EVERY word in the `individual_meaning` field.
Each `individual_meaning` MUST be 1-3 full sentences (typically 25-75 words) and MUST cover:
  - The word's grammatical function in THIS sentence (subject of X, direct object of Y, modifier of noun Z, head of the prepositional phrase 'in the kitchen', etc.).
  - Its morphology — for nouns name number (sg/pl) and any -'s genitive; for verbs name tense + aspect + voice + person/number agreement; for pronouns name person + number + case; for adjectives/adverbs name degree (positive / comparative / superlative).
  - Its lemma when the surface form is inflected (e.g. "ate is the simple past of `eat`").
  - For AMBIGUOUS tokens (`to`, `-ing` forms, `-ed`/`-en` forms, `that`, `who/which`, particles vs. prepositions) include an EXPLICIT disambiguation note explaining WHY this reading wins over the alternative.

WORKED EXAMPLES (use these as a template — match this depth in your output):

EXAMPLE 1 — `to` (infinitive marker vs. preposition):
  Sentence: "I want to run in the park."
  "to" → "Infinitive marker — a particle, NOT a preposition. The next word `run` is a base-form verb, which is the diagnostic for the infinitive reading; if it had been followed by a noun phrase (e.g. 'to the park') it would be a preposition. Here `to run` is the infinitival complement of `want`."
  "in" → "Preposition. Followed by the noun phrase `the park`, not a base verb, so this is the preposition reading of the surface form. Heads the prepositional phrase 'in the park', which modifies the verb 'run' (locative)."

EXAMPLE 2 — `-ing` form (gerund vs. present participle):
  Sentence: "Running is fun, but she is running now."
  "Running" (sentence-initial) → "Gerund — an -ing form functioning as a noun. It is the SUBJECT of the verb `is` (with predicate `fun`), and a noun is the only category that can fill that slot. Distinct from a present participle, which would have to follow a be-auxiliary."
  "running" (after `is`) → "Present participle. The auxiliary `is` (be-form) immediately precedes it, which is the diagnostic for be+V-ing → progressive aspect. Together `is running` is the simple-present progressive of the lexical verb `run` (3rd-person singular subject `she`)."

EXAMPLE 3 — `that` (4-way ambiguity):
  Sentence: "The book that I read says that he saw that man, and that is mine."
  "that" (first, after `book`) → "Relative pronoun. It immediately follows the noun phrase `The book` and introduces a relative clause modifying that noun. Distinct from a complementizer (which would follow a verb of saying/thinking) and from a demonstrative (which would not introduce a clause)."
  "that" (second, after `says`) → "Subordinating conjunction (complementizer). It follows the verb `says` and introduces the propositional complement clause `he saw that man`. This is the COMPLEMENTIZER reading, distinct from the relative-pronoun reading because no preceding noun is being modified."
  "that" (third, before `man`) → "Demonstrative determiner. It directly precedes the noun `man` and modifies it (specifying which man). Distinct from a demonstrative pronoun, which would stand alone as subject or object."
  "that" (fourth, before `is mine`) → "Demonstrative pronoun. Stands alone as the SUBJECT of `is mine`; no following noun for it to modify. Distinct from the determiner reading because it does not modify any other word."

EXAMPLE 4 — phrasal verb (`look up`):
  Sentence: "I looked up the word."
  "looked" → "Lexical verb, simple past tense, head of the phrasal verb `look up` (which means 'consult/search for', non-compositional). Takes `the word` as its direct object. Tagged as phrasal_verb_part because its meaning is non-compositional with `up`."
  "up" → "Phrasal-verb particle, NOT a preposition. Diagnostic: the object `the word` can grammatically appear BEFORE the particle (`I looked the word up`), which is impossible for a true preposition (cf. *I looked the chimney up). Together `look up` forms the phrasal verb meaning 'consult'."

IMPORTANT:
- Every word in the sentence MUST appear in word_explanations (including punctuation if attached to a word).
- For punctuation tokens use role "other", color "#808080", and a brief individual_meaning like "Sentence-final period; ends the declarative clause."
- DO NOT emit single-word stubs like "to (particle)" or "the (article)". The individual_meaning MUST be a full sentence.
- DO NOT collapse pronoun cases — `I/me/my/mine/myself` are FIVE DIFFERENT FORMS. Tag each one with its specific case.
- Use the EXACT color values from this mapping:
  noun=#FFAA00, verb=#4ECDC4, adjective=#FF44FF, adverb=#FF6347,
  pronoun=#9370DB, personal_pronoun=#9370DB, reflexive_pronoun=#DDA0DD,
  demonstrative=#B8860B, relative_pronoun=#9370DB,
  indefinite_pronoun=#8B7EC8, interrogative_pronoun=#9370DB,
  preposition=#4444FF, conjunction=#AAAAAA,
  subordinating_conjunction=#888888, coordinating_conjunction=#AAAAAA,
  auxiliary=#00CED1, modal_verb=#9370DB,
  article=#FFD700, determiner=#B8860B, possessive_determiner=#B8860B,
  possessive_pronoun=#9370DB,
  particle=#20B2AA, phrasal_verb_particle=#20B2AA, phrasal_verb=#20B2AA,
  infinitive_marker=#FF8C00, infinitive=#FFA500, gerund=#FFA500,
  present_participle=#FF7F50, past_participle=#FF6347,
  comparative=#FF44FF, superlative=#FF44FF,
  numeral=#3CB371, interjection=#FF69B4, other=#808080
- Confidence should be ≥ 0.85 for a complete, correct analysis.
- Return ONLY valid JSON — no markdown, no prose before or after.
"""
        return prompt
