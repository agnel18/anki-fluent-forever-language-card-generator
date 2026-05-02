# languages/latvian/domain/lv_prompt_builder.py
"""
Latvian Prompt Builder — Domain Component

Builds AI prompts for Latvian grammar analysis.
Latvian-specific: highlights 7-case system, gender agreement,
definite/indefinite adjective forms, and the debitive mood.
"""

import logging
from typing import List, Optional

from .lv_config import LvConfig

logger = logging.getLogger(__name__)


class LvPromptBuilder:
    """Builds prompts for Latvian grammar analysis using Gemini AI."""

    def __init__(self, config: LvConfig):
        self.config = config

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def build_single_prompt(
        self, sentence: str, target_word: str, complexity: str
    ) -> str:
        """Build a prompt for analysing one Latvian sentence."""
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
        """Build a prompt for analysing multiple Latvian sentences."""
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
            "LATVIAN-SPECIFIC RULES:\n"
            "1. Latvian has 7 grammatical cases. Always note the case of each noun/adjective/pronoun.\n"
            "2. Latvian has only 2 genders: masculine and feminine. Always identify the gender.\n"
            "3. Adjectives have DEFINITE (noteiktā/long) and INDEFINITE (nenoteiktā/short) forms. "
            "   Use 'adjective_definite' or 'adjective_indefinite' accordingly.\n"
            "4. Latvian has NO articles — definiteness is conveyed by adjective form and context.\n"
            "5. Reflexive verbs end in -ties or -ās — label these as 'reflexive_verb'.\n"
        )
        if complexity in ("intermediate", "advanced"):
            base += (
                "6. The DEBITIVE mood uses 'jā-' prefix + verb and expresses obligation "
                "   (e.g., 'Man jāraksta' = I must write). Label debitive verbs as 'debitive'.\n"
                "7. Common prepositions govern specific cases — include the case governed in the explanation.\n"
            )
        if complexity == "advanced":
            base += (
                "8. Latvian has 4 PARTICIPLE types: present active (-ošs/-oša), past active (-is/-usi), "
                "   present passive (-ams/-ama), past passive (-ts/-ta). Label as 'participle'.\n"
                "9. Verbal prefixes (aiz-, ap-, at-, ie-, iz-, no-, pa-, par-, pār-, pie-, sa-, uz-) "
                "   can change a verb's aspect and/or meaning. Note the prefix if present.\n"
                "10. Verbal nouns (-šana suffix) are 'verbal_noun'.\n"
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
                f'Analyze this Latvian sentence: "{sentences[0]}"\n\n'
                f'Target vocabulary word: "{target_word}"\n\n'
                "Return a single JSON object in the exact schema shown."
            )
            schema_note = (
                "Return a single JSON object with exactly the keys shown in the schema below."
            )

        prompt = f"""You are an expert Latvian linguistics professor analyzing Latvian grammar for language learners.

COMPLEXITY LEVEL: {complexity}
LANGUAGE: Latvian (Latviešu valoda)
FAMILY: Indo-European, Baltic branch
SCRIPT: Latin with diacritics (LTR)

{sentence_instruction}

{special_notes}

GRAMMATICAL ROLES to use at this level:
{roles_str}

{schema_note}

JSON SCHEMA:
{{
  "sentence": "<the original sentence>",
  "overall_structure": "<brief description of sentence structure, e.g. 'Subject-Verb-Object with locative phrase'>",
  "sentence_structure": "<same as overall_structure — include both keys>",
  "word_explanations": [
    {{
      "word": "<exact word from sentence>",
      "grammatical_role": "<grammatical role from the allowed roles list>",
      "color": "<hex color for this role>",
      "meaning": "<English meaning + grammatical info, e.g. 'māja (house) — nominative singular feminine'>",
      "case": "<case if applicable, e.g. nominative, genitive, dative, accusative, instrumental, locative, vocative>",
      "gender": "<masculine or feminine, if applicable>",
      "number": "<singular or plural, if applicable>",
      "tense": "<present/past/future if verb>",
      "definite_form": "<true/false if adjective — true=definite/long form, false=indefinite/short form>"
    }}
  ],
  "grammar_notes": "<key grammar points for learners at {complexity} level>",
  "confidence": <float 0.0 to 1.0>
}}

IMPORTANT:
- Every word in the sentence MUST appear in word_explanations (including punctuation if attached to a word).
- For punctuation tokens use role "other" and color "#808080".
- Use the EXACT color values from this mapping:
  noun=#FFAA00, verb=#4ECDC4, adjective=#FF44FF, adjective_definite=#FF44FF,
  adjective_indefinite=#CC33CC, adverb=#FF6347, pronoun=#9370DB,
  personal_pronoun=#9370DB, reflexive_pronoun=#DDA0DD, demonstrative=#B8860B,
  relative_pronoun=#9370DB, indefinite_pronoun=#8B7EC8,
  preposition=#4444FF, conjunction=#AAAAAA, subordinating_conjunction=#888888,
  auxiliary=#00CED1, reflexive_verb=#20B2AA, participle=#FF8C00,
  debitive=#FF1493, numeral=#3CB371, particle=#20B2AA,
  interjection=#FF69B4, verbal_noun=#DAA520, other=#808080
- Confidence should be ≥ 0.85 for a complete, correct analysis.
- Return ONLY valid JSON — no markdown, no prose before or after.
"""
        return prompt
