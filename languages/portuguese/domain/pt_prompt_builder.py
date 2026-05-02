# languages/portuguese/domain/pt_prompt_builder.py
"""
Portuguese Prompt Builder — Domain Component

Builds AI prompts for Portuguese grammar analysis. The prompts encode
Portuguese-specific design rules from pt_grammar_concepts.md (Phase 1):

  1. Three-state clitic placement (proclitic / enclitic / mesoclitic)
     and object-clitic allomorphs (-lo / -no after r/s/z and nasals).
  2. Contractions tokenized into preposition + article/pronoun (do, no,
     ao, pelo, dele, naquele, daquilo, ...).
  3. Ser vs estar tagged as copula with copula_type meta-field.
  4. Personal infinitive vs future subjunctive disambiguation by trigger:
     - after se / quando / enquanto / assim que / logo que → future_subjunctive
     - after para / sem / ao / antes de / depois de → personal_infinitive
  5. BR / PT register tagging (você+gerund vs tu+enclisis+'estar a'+inf).
  6. JSON schema uses 'grammatical_role' (per Latvian schema-alignment fix).
"""

import logging
from typing import List, Optional

from .pt_config import PtConfig

logger = logging.getLogger(__name__)


class PtPromptBuilder:
    """Builds prompts for Portuguese grammar analysis using Gemini AI."""

    def __init__(self, config: PtConfig):
        self.config = config

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def build_single_prompt(
        self, sentence: str, target_word: str, complexity: str
    ) -> str:
        """Build a prompt for analysing one Portuguese sentence."""
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
        """Build a prompt for analysing multiple Portuguese sentences."""
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
        """Return the list of role names allowed at this complexity level."""
        roles_dict = self.config.grammatical_roles or self.config._get_default_roles()
        level = roles_dict.get(complexity, roles_dict.get("intermediate", {}))
        if isinstance(level, dict):
            return list(level.keys())
        if isinstance(level, list):
            return list(level)
        return []

    def _get_special_notes(self, complexity: str) -> str:
        """Portuguese-specific analysis instructions, gated by complexity."""
        base = (
            "PORTUGUESE-SPECIFIC ANALYSIS RULES:\n"
            "1. CONTRACTIONS — Portuguese has obligatory contractions of preposition + "
            "article / demonstrative / pronoun. Whenever you see one, tag the surface "
            "form with grammatical_role='contraction' AND set 'contraction_parts' "
            "to the underlying components. Common examples:\n"
            "   do=de+o, da=de+a, dos=de+os, das=de+as,\n"
            "   no=em+o, na=em+a, nos=em+os, nas=em+as,\n"
            "   ao=a+o, à=a+a, aos=a+os, às=a+as,\n"
            "   pelo=por+o, pela=por+a, pelos=por+os, pelas=por+as,\n"
            "   dele=de+ele, dela=de+ela, deles=de+eles, delas=de+elas,\n"
            "   neste/nesta/nesse/nessa/naquele/naquela=em+demonstrative,\n"
            "   deste/desse/daquele/disto/disso/daquilo=de+demonstrative,\n"
            "   àquele/àquela/àquilo=a+distal_demonstrative,\n"
            "   comigo/contigo/consigo/conosco/convosco=com+pronoun.\n"
            "   NEVER tag a contraction as a plain article or preposition — always "
            "   use role='contraction'.\n"
            "\n"
            "2. SER vs ESTAR (COPULA) — Tag both with grammatical_role='copula'. "
            "   Set the meta field 'copula_type' to 'ser' or 'estar'. SER expresses "
            "   inherent identity / profession / origin / time / possession; ESTAR "
            "   expresses transient state / location / progressive aspect. The same "
            "   adjective shifts meaning by copula choice (é triste = inherently sad; "
            "   está triste = sad right now). Flag any apparent mismatch in 'notes'.\n"
            "\n"
            "3. CLITIC PLACEMENT — Portuguese has THREE clitic positions:\n"
            "   - PROCLITIC (before verb): after negation (não me viu), after certain "
            "     adverbs (já, sempre, talvez), after subordinating conjunctions "
            "     (que, porque), after interrogatives, after indefinites. BR colloquial "
            "     defaults to proclisis even sentence-initial.\n"
            "   - ENCLITIC (after verb, hyphenated): default in PT for affirmative "
            "     declaratives (viu-me), imperative affirmative (diga-me).\n"
            "   - MESOCLITIC (inside future/conditional verb forms): dar-lhe-ei, "
            "     falar-te-ia. Rare, formal/literary, PT only.\n"
            "   For each clitic, use grammatical_role='clitic_pronoun' (or "
            "   'mesoclitic' for the rare inserted variant) and set 'clitic_position' "
            "   to 'proclitic' / 'enclitic' / 'mesoclitic'.\n"
            "\n"
            "4. OBJECT-CLITIC ALLOMORPHS — Recognise -lo/-la/-los/-las after verb "
            "   endings -r, -s, -z (vê-lo = vê + o; fá-lo = faz + o; fi-lo = fiz + o), "
            "   and -no/-na/-nos/-nas after nasal endings -m / -ão / -õe (viram-no = "
            "   viram + o; dão-no = dão + o). Tokenise verb + clitic separately and "
            "   tag the clitic as 'clitic_pronoun' with placement='enclitic'.\n"
            "\n"
            "5. REGISTER TAGGING — Set 'register' to 'BR', 'PT', or 'neutral' on the "
            "   sentence and on individual words when cues exist:\n"
            "   - você + gerund (estou fazendo) → BR\n"
            "   - tu + 2sg verb + enclisis + 'estar a' + infinitive → PT\n"
            "   - mesoclisis is PT-formal-only\n"
            "   - 'a gente' as 1pl pronoun → BR colloquial\n"
            "   - 'ter que' → BR colloquial; 'ter de' → PT-leaning\n"
        )
        if complexity in ("intermediate", "advanced"):
            base += (
                "\n6. PRONOMINAL VERBS — Verbs lexicalised with 'se' (lembrar-se, "
                "   queixar-se, sentar-se). Tag the verb stem as 'pronominal_verb' "
                "   and the 'se' as 'reflexive_pronoun' or as part of the lemma "
                "   depending on the form.\n"
                "\n7. AUXILIARY vs MODAL — ter (perfect tenses) and ir (periphrastic "
                "   future) are 'auxiliary_verb'. poder, dever, querer, saber are "
                "   'modal_verb'. estar in progressive ('estou estudando') is "
                "   'auxiliary_verb' marking aspect.\n"
                "\n8. DEBITIVE — 'ter de + infinitive' (PT-leaning) and 'ter que + "
                "   infinitive' (BR colloquial) both express obligation. Tag the "
                "   construction head as 'debitive' rather than treating ter as a "
                "   plain auxiliary.\n"
            )
        if complexity == "advanced":
            base += (
                "\n9. PERSONAL INFINITIVE vs FUTURE SUBJUNCTIVE (CRITICAL) — These "
                "   are HOMOPHONOUS for regular -ar/-er/-ir verbs (e.g., 'falarmos' "
                "   could be either). Disambiguate by syntactic trigger:\n"
                "   - After SE / QUANDO / ENQUANTO / ASSIM QUE / LOGO QUE / COMO / "
                "     CONFORME / SEMPRE QUE → future subjunctive — tag with "
                "     grammatical_role='subjunctive_marker' and 'mood'='future_subjunctive'.\n"
                "   - After PARA / SEM / AO / ANTES DE / DEPOIS DE / APESAR DE → "
                "     personal infinitive — tag with grammatical_role='personal_infinitive'.\n"
                "   - For irregular verbs the forms differ (puder ≠ poder; fizer ≠ "
                "     fazer; vier ≠ vir; for ≠ ir/ser) — use that surface form as "
                "     the disambiguator.\n"
                "\n10. SUBJUNCTIVE TENSES — Use grammatical_role='subjunctive_marker' "
                "    and set 'mood' to one of: present_subjunctive (que eu fale), "
                "    imperfect_subjunctive (se eu falasse), future_subjunctive "
                "    (quando eu falar). Triggers: querer que, esperar que, embora, "
                "    para que, ainda que, mesmo que, caso, contanto que, antes que.\n"
                "\n11. GERUND vs PAST PARTICIPLE — '-ndo' forms (falando, comendo, "
                "    partindo) are 'gerund'. '-do' forms (falado, comido, partido) "
                "    and irregulars (feito, dito, visto, posto, escrito, aberto) are "
                "    'past_participle'. Past participles in passives agree with the "
                "    subject in gender/number; in compound tenses with 'ter/haver' "
                "    they are invariable.\n"
                "\n12. CONDITIONAL — Synthetic (falaria, faria) or periphrastic "
                "    (ia falar). Tag as 'conditional' with 'form' meta-field.\n"
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
        """Compose the final prompt string."""
        roles_str = ", ".join(roles) if roles else (
            "noun, verb, adjective, pronoun, preposition, conjunction, adverb, "
            "article, numeral"
        )

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
                f'Analyze this Portuguese sentence: "{sentences[0]}"\n\n'
                f'Target vocabulary word: "{target_word}"\n\n'
                "Return a single JSON object in the exact schema shown."
            )
            schema_note = (
                "Return a single JSON object with exactly the keys shown in the schema below."
            )

        prompt = f"""You are an expert Portuguese linguistics professor analyzing Portuguese grammar for language learners.

COMPLEXITY LEVEL: {complexity}
LANGUAGE: Portuguese (Português) — both Brazilian (BR) and European (PT) varieties
FAMILY: Indo-European, Romance, Ibero-Romance
SCRIPT: Latin with diacritics (LTR)

{sentence_instruction}

{special_notes}

GRAMMATICAL ROLES allowed at this level:
{roles_str}

{schema_note}

JSON SCHEMA:
{{
  "sentence": "<the original sentence>",
  "register": "<BR | PT | neutral>",
  "overall_structure": "<brief description of sentence structure, e.g. 'SVO declarative with proclitic clitic and contraction'>",
  "sentence_structure": "<same content as overall_structure — include both keys for compatibility>",
  "word_explanations": [
    {{
      "word": "<exact word/token from sentence>",
      "grammatical_role": "<role from the allowed list above — use exact string>",
      "color": "<hex color for this role>",
      "meaning": "<English meaning + grammatical info, e.g. 'casa (house) — feminine singular noun'>",
      "gender": "<masculine | feminine | (empty if N/A)>",
      "number": "<singular | plural | (empty)>",
      "person": "<1 | 2 | 3 | (empty)>",
      "tense": "<present | preterite | imperfect | pluperfect | future | conditional | (empty)>",
      "mood": "<indicative | subjunctive | present_subjunctive | imperfect_subjunctive | future_subjunctive | imperative | personal_infinitive | (empty)>",
      "copula_type": "<ser | estar | (empty if not a copula)>",
      "clitic_position": "<proclitic | enclitic | mesoclitic | (empty if not a clitic)>",
      "contraction_parts": ["<part1>", "<part2>"]
    }}
  ],
  "grammar_notes": "<key grammar points for learners at {complexity} level — emphasise Portuguese-specific features observed in this sentence>",
  "confidence": <float 0.0 to 1.0>
}}

CRITICAL OUTPUT REQUIREMENTS:
- Use the exact JSON KEY 'grammatical_role' (NOT 'role' or 'pos').
- Every visible token in the sentence MUST appear in word_explanations, INCLUDING contractions
  (the contraction itself gets one entry with role='contraction' and 'contraction_parts' populated).
- For punctuation tokens use grammatical_role='other' and color='#AAAAAA'.
- Use the EXACT color values from this Portuguese-specific mapping:
  noun=#FFAA00, verb=#44FF44, adjective=#FF44FF, adverb=#44FFFF,
  pronoun=#FF4444, personal_pronoun=#FF4444, possessive_pronoun=#B22222,
  demonstrative_pronoun=#FF6347, reflexive_pronoun=#DC143C,
  relative_pronoun=#FF4500, indefinite_pronoun=#CD5C5C,
  interrogative_pronoun=#DB7093, preposition=#4444FF, conjunction=#888888,
  subordinating_conjunction=#777777, interjection=#FFD700, article=#AA44FF,
  definite_article=#AA44FF, indefinite_article=#9966CC, numeral=#3CB371,
  auxiliary_verb=#228B22, modal_verb=#32CD32, pronominal_verb=#20B2AA,
  copula=#00B894, contraction=#FF7F50, personal_infinitive=#6C5CE7,
  mesoclitic=#FF1493, clitic_pronoun=#E91E63, gerund=#00CED1,
  past_participle=#FFA500, subjunctive_marker=#9C27B0, conditional=#7E57C2,
  debitive=#D81B60, particle=#A1887F, other=#AAAAAA
- Confidence should be ≥ 0.85 for a complete, correct analysis.
- Return ONLY valid JSON — no markdown fences, no prose before or after.
"""
        return prompt

    # ------------------------------------------------------------------
    # Sentence generation prompt — Portuguese-specific (Pass 1 of pipeline)
    # ------------------------------------------------------------------

    def get_sentence_generation_prompt(
        self,
        word: str,
        language: str,
        num_sentences: int,
        enriched_meaning: str = "",
        min_length: int = 3,
        max_length: int = 15,
        difficulty: str = "intermediate",
        topics: Optional[List[str]] = None,
    ) -> str:
        """
        Portuguese-specific sentence generation prompt mirroring the structured
        format used by french/japanese (MEANING / RESTRICTIONS / SENTENCES /
        TRANSLATIONS / IPA / KEYWORDS) with Portuguese-specific guidance.
        """
        if topics:
            context_instruction = (
                f"- CRITICAL REQUIREMENT: ALL sentences MUST relate to these specific "
                f"topics: {', '.join(topics)}. Force the word usage into these contexts "
                f"even if it requires creative interpretation. Do NOT use generic contexts."
            )
        else:
            context_instruction = (
                "- Use diverse real-life contexts: home, travel, food, emotions, work, "
                "social life, daily actions, cultural experiences (Brazil, Portugal, "
                "or lusophone diaspora)"
            )

        if enriched_meaning and enriched_meaning != "N/A":
            enriched_meaning_instruction = (
                f'Use this pre-reviewed meaning for "{word}": "{enriched_meaning}". '
                f"Generate a clean English meaning based on this."
            )
        else:
            enriched_meaning_instruction = (
                f'Provide a brief English meaning for "{word}".'
            )

        prompt = f"""You are a native-level expert linguist in Portuguese (Português), familiar with both Brazilian (BR) and European (PT) varieties.

Your task: Generate a complete learning package for the Portuguese word "{word}" in ONE response.

===========================
STEP 1: WORD MEANING
===========================
{enriched_meaning_instruction}
Format: Return exactly one line like "casa (a building where people live)" or "ele (third-person masculine singular pronoun)"
IMPORTANT: Keep the entire meaning under 75 characters total.

===========================
WORD-SPECIFIC RESTRICTIONS
===========================
Based on the meaning above, identify any grammatical constraints for "{word}".
Examples: gender (masculine/feminine), conjugation class (-ar/-er/-ir/-or), pronominal,
copula type (ser vs estar), clitic placement requirements, BR/PT register restrictions.
If no restrictions apply, state "No specific grammatical restrictions."
IMPORTANT: Keep the entire restrictions summary under 60 characters total.

===========================
STEP 2: SENTENCES
===========================
Generate exactly {num_sentences} highly natural, idiomatic sentences in Portuguese for the word "{word}".

QUALITY RULES:
- Every sentence must sound like native Portuguese (BR or PT — pick one consistently per sentence)
- Grammar, syntax, spelling, agreement, and accents must be correct
- The target word "{word}" MUST be used correctly according to the restrictions above
- Each sentence must be between {min_length} and {max_length} words long
- COUNT words precisely; if outside the range, regenerate internally
- Difficulty: {difficulty}

PORTUGUESE-SPECIFIC REQUIREMENTS:
- Use proper gender / number agreement (article — noun — adjective)
- Apply correct verb conjugations (person, number, tense, mood)
- Use ser vs estar correctly (inherent vs transient)
- Apply obligatory contractions (de+o=do, em+o=no, a+o=ao, por+o=pelo, de+ele=dele)
- Use clitic placement appropriate to register (BR proclisis vs PT enclisis)
- Mix tenses (present, preterite, imperfect, future, conditional, subjunctive) when difficulty allows
- For advanced difficulty, include at least one example with personal infinitive,
  future subjunctive, or pronominal verb when natural

VARIETY REQUIREMENTS:
- Vary register (formal vs colloquial; BR vs PT) across sentences
- Vary sentence types (declarative, interrogative, negative)
- Use different pronoun types (personal, possessive, demonstrative, reflexive)
- Use varied prepositions and contractions
{context_instruction}

===========================
STEP 3: ENGLISH TRANSLATIONS
===========================
For EACH sentence above, provide a natural, fluent English translation.
- Translation should be natural English, not literal word-for-word

===========================
STEP 4: IPA TRANSCRIPTION
===========================
For EACH sentence above, provide IPA phonetic transcription.
- Use standard IPA symbols for Portuguese pronunciation
- Mark nasal vowels (ã, õ, am, em, im, om, um) with the tilde diacritic
- Mark stress where non-default
- BR or PT pronunciation should match the variety used in the sentence

===========================
STEP 5: IMAGE KEYWORDS
===========================
For EACH sentence above, generate exactly 3 specific keywords for image search.
- Keywords should be concrete and specific
- Keywords in English only

===========================
OUTPUT FORMAT - FOLLOW EXACTLY
===========================
Return your response in this exact text format:

MEANING: [brief English meaning]

RESTRICTIONS: [grammatical restrictions]

SENTENCES:
1. [sentence 1 in Portuguese]
2. [sentence 2 in Portuguese]
...

TRANSLATIONS:
1. [natural English translation for sentence 1]
2. [natural English translation for sentence 2]
...

IPA:
1. [IPA transcription for sentence 1]
2. [IPA transcription for sentence 2]
...

KEYWORDS:
1. [keyword1, keyword2, keyword3]
2. [keyword1, keyword2, keyword3]
...

IMPORTANT:
- Return ONLY the formatted text, no extra explanation
- Sentences must be in Portuguese only
- Ensure exactly {num_sentences} sentences, translations, IPA transcriptions, and keywords
- Respect character limits for meaning and restrictions
"""
        return prompt
