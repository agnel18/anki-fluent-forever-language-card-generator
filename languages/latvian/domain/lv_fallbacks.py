# languages/latvian/domain/lv_fallbacks.py
"""
Latvian Fallbacks — Domain Component

Rule-based fallback grammar analysis for Latvian.
Used when AI response is unavailable or unparseable.

Output mirrors the German fallback contract: each word gets a multi-clause
`individual_meaning` explanation (function in sentence + morphology +
Latvian-specific feature) so cards never display single-word stubs.
"""

import logging
import re
from typing import Any, Dict, List, Tuple

from .lv_config import LvConfig

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lexicon — closed-class words and irregular forms.
#
# Values are (role, gender, number, case, individual_meaning) where applicable.
# Roles deliberately use the rich vocabulary (demonstrative, personal_pronoun,
# adjective_definite, ...) since lv_validator._VALID_ROLES accepts them at every
# complexity level and lv_config defines colors for them. The role label shown
# to the AI in the prompt is constrained per-complexity by lv_config; the
# fallback is not constrained and just picks the most informative tag.
# ---------------------------------------------------------------------------

_AUXILIARY = {
    "ir":     "3rd-person singular/plural present of 'būt' (to be); the copula linking subject and predicate.",
    "bija":   "3rd-person singular/plural past of 'būt' (to be); marks past-tense copula or auxiliary.",
    "būs":    "3rd-person singular/plural future of 'būt' (to be); future-tense copula.",
    "esmu":   "1st-person singular present of 'būt' (to be); copula with the subject 'es'.",
    "esi":    "2nd-person singular present of 'būt' (to be); copula with the subject 'tu'.",
    "esam":   "1st-person plural present of 'būt' (to be); copula with the subject 'mēs'.",
    "esat":   "2nd-person plural present of 'būt' (to be); copula with the subject 'jūs'.",
    "būtu":   "Conditional form of 'būt' (would be); marks the conditional/subjunctive mood.",
}

_CONJUNCTIONS = {
    "un":     ("coordinating", "and; joins phrases or clauses of equal status."),
    "bet":    ("coordinating", "but; introduces a contrast between two clauses."),
    "vai":    ("coordinating", "or / whether; offers an alternative or introduces a yes-no question."),
    "jo":     ("coordinating", "because; introduces a reason for the preceding clause."),
    "tāpēc":  ("coordinating", "therefore; signals a consequence of the preceding clause."),
    "taču":   ("coordinating", "however / yet; signals contrast or concession."),
    "tomēr":  ("coordinating", "nevertheless / still; concedes contrast with the previous statement."),
    "ka":     ("subordinating_conjunction", "that; introduces a complement clause."),
    "kad":    ("subordinating_conjunction", "when; introduces a temporal subordinate clause."),
    "ja":     ("subordinating_conjunction", "if; introduces a conditional clause."),
    "lai":    ("subordinating_conjunction", "so that / in order to; introduces a purpose clause."),
    "kaut":   ("subordinating_conjunction", "although / even though; introduces a concessive clause."),
    "gan":    ("particle", "emphatic particle; reinforces the asserted clause."),
}

_PREPOSITIONS = {
    "bez":    ("genitive",     "without"),
    "līdz":   ("genitive",     "until / up to"),
    "no":     ("genitive",     "from / out of"),
    "pēc":    ("genitive",     "after / according to"),
    "pie":    ("genitive",     "at / by / next to"),
    "priekš": ("genitive",     "for / for the benefit of"),
    "starp":  ("instrumental", "between / among"),
    "pret":   ("accusative",   "against / towards"),
    "ap":     ("accusative",   "around"),
    "caur":   ("accusative",   "through"),
    "gar":    ("accusative",   "along"),
    "pār":    ("accusative",   "over"),
    "par":    ("accusative",   "about / for / as"),
    "uz":     ("accusative",   "to / onto / on"),
    "aiz":    ("genitive",     "behind"),
    "iekš":   ("genitive",     "inside"),
    "pa":     ("dative",       "along / through (distributive)"),
    "ar":     ("instrumental", "with"),
}

# Personal pronouns with case + person + number for each form.
_PERSONAL_PRONOUNS = {
    "es":      ("nominative",   "1sg",  "I — 1st-person singular subject pronoun."),
    "tu":      ("nominative",   "2sg",  "you (sg.) — 2nd-person singular subject pronoun."),
    "viņš":    ("nominative",   "3sg.m","he — 3rd-person singular masculine subject pronoun."),
    "viņa":    ("nominative",   "3sg.f","she — 3rd-person singular feminine subject pronoun."),
    "mēs":     ("nominative",   "1pl",  "we — 1st-person plural subject pronoun."),
    "jūs":     ("nominative",   "2pl",  "you (pl.) — 2nd-person plural subject pronoun."),
    "viņi":    ("nominative",   "3pl.m","they (m.) — 3rd-person masculine plural subject pronoun."),
    "viņas":   ("nominative",   "3pl.f","they (f.) — 3rd-person feminine plural subject pronoun."),
    "man":     ("dative",       "1sg",  "to me — 1st-person singular dative; common in possession (`man ir`) and debitive constructions."),
    "tev":     ("dative",       "2sg",  "to you (sg.) — 2nd-person singular dative."),
    "viņam":   ("dative",       "3sg.m","to him — 3rd-person masculine singular dative."),
    "viņai":   ("dative",       "3sg.f","to her — 3rd-person feminine singular dative."),
    "mums":    ("dative",       "1pl",  "to us — 1st-person plural dative."),
    "jums":    ("dative",       "2pl",  "to you (pl.) — 2nd-person plural dative."),
    "mani":    ("accusative",   "1sg",  "me — 1st-person singular accusative direct-object pronoun."),
    "tevi":    ("accusative",   "2sg",  "you (sg.) — 2nd-person singular accusative direct-object pronoun."),
    "viņu":    ("accusative",   "3sg",  "him/her — 3rd-person singular accusative direct-object pronoun."),
}

_REFLEXIVE_PRONOUNS = {
    "sevi":    ("accusative", "Reflexive pronoun ('oneself'), accusative; refers back to the clause subject."),
    "sev":     ("dative",     "Reflexive pronoun ('to oneself'), dative; refers back to the clause subject."),
}

# Possessive determiners — Latvian declines these like adjectives and they
# agree with the head noun in case, gender, and number. The historical mistag
# of `mans/tava/savs` as nouns is exactly what this branch fixes.
_POSSESSIVE_DETERMINERS = {
    "mans": "1sg.m", "mana": "1sg.f", "manu": "1sg.acc",
    "mani": "1pl.m", "manas": "1pl.f", "manus": "1pl.acc",
    "tavs": "2sg.m", "tava": "2sg.f", "tavu": "2sg.acc",
    "tavi": "2pl.m", "tavas": "2pl.f", "tavus": "2pl.acc",
    "viņa": "3sg",   "viņu": "3sg.acc",
    "mūsu": "1pl",   "jūsu": "2pl",   "viņu": "3pl",
    "savs": "refl.m","sava": "refl.f", "savu": "refl.acc",
    "savi": "refl.pl.m","savas": "refl.pl.f","savus": "refl.pl.acc",
}

_DEMONSTRATIVES = {
    "šis":  ("nominative", "sg.m", "this (m.) — demonstrative singular masculine."),
    "šī":   ("nominative", "sg.f", "this (f.) — demonstrative singular feminine."),
    "šie":  ("nominative", "pl.m", "these (m.) — demonstrative plural masculine."),
    "šīs":  ("nominative", "pl.f", "these (f.) — demonstrative plural feminine."),
    "tas":  ("nominative", "sg.m", "that (m.) — demonstrative singular masculine."),
    "tā":   ("nominative", "sg.f", "that (f.) — demonstrative singular feminine."),
    "tie":  ("nominative", "pl.m", "those (m.) — demonstrative plural masculine."),
    "tās":  ("nominative", "pl.f", "those (f.) — demonstrative plural feminine."),
}

_INTERROGATIVES = {
    "kas":   "Interrogative/relative pronoun ('who/what'); subject of a question or relative clause.",
    "ko":    "Interrogative/relative pronoun ('whom/what'), accusative; direct object of a question or relative clause.",
    "kurš":  "Interrogative/relative pronoun ('which', m.); selects from a known set, agrees in gender/number/case with antecedent.",
    "kura":  "Interrogative/relative pronoun ('which', f.); selects from a known set, agrees in gender/number/case with antecedent.",
}

_ADVERBS = {
    "labi":     "well — manner adverb modifying the verb.",
    "ātri":     "quickly — manner adverb modifying the verb.",
    "lēni":     "slowly — manner adverb modifying the verb.",
    "ļoti":     "very — degree adverb intensifying the following adjective or adverb.",
    "diezgan":  "fairly / quite — degree adverb modifying the following adjective or adverb.",
    "gandrīz":  "almost — degree adverb modifying the following predicate.",
    "tagad":    "now — temporal adverb anchoring the action in the present.",
    "tad":      "then — temporal/sequential adverb.",
    "vienmēr":  "always — frequency adverb of universal quantification.",
    "nekad":    "never — frequency adverb of negation; pairs with the verb's negative prefix.",
    "šeit":     "here — locative adverb of place.",
    "tur":      "there — locative adverb of place.",
    "mājās":    "at home — locative adverb (frozen locative form of 'māja').",
    "jau":      "already — temporal/aspectual adverb.",
    "vēl":      "still / yet — temporal/aspectual adverb.",
    "tikai":    "only — restrictive focus adverb.",
    "arī":      "also / too — additive focus adverb.",
}

_NUMERALS = {
    "viens": "sg.m", "viena": "sg.f",
    "divi": "pl.m", "divas": "pl.f",
    "trīs": "pl", "četri": "pl.m", "četras": "pl.f",
    "pieci": "pl.m", "piecas": "pl.f",
    "seši": "pl.m", "sešas": "pl.f",
    "septiņi": "pl.m", "septiņas": "pl.f",
    "astoņi": "pl.m", "astoņas": "pl.f",
    "deviņi": "pl.m", "deviņas": "pl.f",
    "desmit": "indecl",
}


class LvFallbacks:
    """Rule-based fallback analysis for Latvian grammar."""

    def __init__(self, config: LvConfig):
        self.config = config

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def create_fallback(self, sentence: str, complexity: str) -> Dict[str, Any]:
        """Create a basic rule-based grammar analysis with rich explanations."""
        words = sentence.split()
        word_explanations = []

        for word in words:
            clean = word.strip(".,!?;:\"'()[]")
            role, individual_meaning, case, gender, number = self._classify_word(
                clean, complexity
            )

            # Soften role to match prompt's per-complexity vocabulary so role
            # tags shown to the user feel consistent with what the AI produces.
            display_role = self._soften_role(role, complexity)
            color = self.config.get_color_for_role(display_role, complexity)

            # Punctuation-only tokens get a brief description.
            is_punct = clean == ""
            if is_punct:
                display_role = "other"
                color = self.config.get_color_for_role("other", complexity)
                individual_meaning = "Punctuation token; structures the clause boundary."

            display = f"{word} ({display_role}): {individual_meaning}"

            word_explanations.append({
                "word": word,
                "role": display_role,
                "color": color,
                "meaning": display,
                "individual_meaning": individual_meaning,
                "case": case,
                "gender": gender,
                "number": number,
                "tense": "",
                "definite_form": "",
            })

        return {
            "word_explanations": word_explanations,
            "overall_structure": "Latvian sentence (rule-based fallback analysis).",
            "sentence_structure": "Latvian sentence (rule-based fallback analysis).",
            "explanations": {
                item["word"]: item["meaning"] for item in word_explanations
            },
            "elements": {item["word"]: item["role"] for item in word_explanations},
            "grammar_notes": (
                "Rule-based fallback — AI unavailable. POS tags inferred from "
                "closed-class lexicons + suffix heuristics; case/gender for open-class "
                "words is morphologically guessed and may be incorrect."
            ),
            "confidence": 0.35,
        }

    # ------------------------------------------------------------------
    # Per-word classification
    # ------------------------------------------------------------------

    def _classify_word(
        self, word: str, complexity: str
    ) -> Tuple[str, str, str, str, str]:
        """Classify a single word.

        Returns (role, individual_meaning, case, gender, number).
        Order of checks is critical:
          1. Empty / punctuation
          2. Closed-class lookups (auxiliary, conjunction, preposition, pronoun,
             possessive determiner, demonstrative, reflexive, interrogative,
             adverb, numeral) — these win over heuristics.
          3. Definite adjective (-ais/-ās/-ie endings on long-enough words)
          4. Reflexive verbs (-ties / -ās)
          5. Debitive verbs (jā- prefix)
          6. Participles + verbal nouns
          7. Indefinite adjectives + plain nouns (the historic confusion zone)
          8. Verbs (conjugated endings)
          9. Default to "other"
        """
        if not word:
            return "other", "Token with no content.", "", "", ""

        lower = word.lower()

        # --- 1. Closed-class lookups -------------------------------------
        if lower in _AUXILIARY:
            return "auxiliary", _AUXILIARY[lower], "", "", ""

        if lower in _CONJUNCTIONS:
            sub_role, expl = _CONJUNCTIONS[lower]
            role = "subordinating_conjunction" if sub_role == "subordinating_conjunction" else (
                "particle" if sub_role == "particle" else "conjunction"
            )
            return role, f"Conjunction '{word}': {expl}", "", "", ""

        if lower in _PREPOSITIONS:
            governs, gloss = _PREPOSITIONS[lower]
            expl = (
                f"Preposition '{word}' meaning '{gloss}'. Governs the {governs} case — "
                f"the noun phrase that follows must take {governs} form."
            )
            return "preposition", expl, "", "", ""

        if lower in _PERSONAL_PRONOUNS:
            case, person_num, expl = _PERSONAL_PRONOUNS[lower]
            gender = "masculine" if "m" in person_num else ("feminine" if "f" in person_num else "")
            number = "plural" if "pl" in person_num else "singular"
            return "personal_pronoun", expl, case, gender, number

        if lower in _REFLEXIVE_PRONOUNS:
            case, expl = _REFLEXIVE_PRONOUNS[lower]
            return "reflexive_pronoun", expl, case, "", ""

        if lower in _DEMONSTRATIVES:
            case, gender_num, expl = _DEMONSTRATIVES[lower]
            gender = "masculine" if ".m" in gender_num else ("feminine" if ".f" in gender_num else "")
            number = "plural" if "pl" in gender_num else "singular"
            return "demonstrative", expl, case, gender, number

        if lower in _POSSESSIVE_DETERMINERS:
            tag = _POSSESSIVE_DETERMINERS[lower]
            person = ("1st" if "1" in tag else "2nd" if "2" in tag else
                      "3rd" if "3" in tag else "reflexive" if "refl" in tag else "")
            gender = "masculine" if ".m" in tag else ("feminine" if ".f" in tag else "")
            number = "plural" if "pl" in tag else "singular"
            case = "accusative" if "acc" in tag else "nominative"
            person_label = f"{person} person " if person else ""
            expl = (
                f"Possessive determiner '{word}' ({person_label}possessive). Declines like an adjective "
                f"and agrees with the head noun in case, gender, and number — here {case} "
                f"{number}{(' ' + gender) if gender else ''}."
            )
            return "personal_pronoun", expl, case, gender, number

        if lower in _INTERROGATIVES:
            return "relative_pronoun", _INTERROGATIVES[lower], "", "", ""

        if lower in _ADVERBS:
            return "adverb", f"Adverb '{word}': {_ADVERBS[lower]}", "", "", ""

        if lower in _NUMERALS:
            tag = _NUMERALS[lower]
            gender = "masculine" if ".m" in tag else ("feminine" if ".f" in tag else "")
            number = "plural" if "pl" in tag else "singular"
            expl = (
                f"Numeral '{word}'. Latvian cardinal numerals 1–9 agree with the counted noun "
                f"in gender and case; '{word}' is "
                f"{number}{(' ' + gender) if gender else ''}."
            )
            return "numeral", expl, "nominative", gender, number

        # --- 2. Definite adjective (-ais/-ais/-ās/-ie endings) ----------
        # Move this BEFORE the noun rule so 'jaunais', 'labais', 'mazais' etc.
        # are not falsely tagged as masculine nouns. The check runs at every
        # complexity level (the previous gate `complexity != "beginner"` was
        # the source of the misclassification at beginner level).
        if re.search(r"(ais|ākais|ais)$", lower) and len(word) > 3:
            expl = (
                f"Definite (long-form) adjective '{word}', nominative singular masculine. "
                f"The definite ending -ais marks the modified noun as specific/known and the "
                f"adjective agrees with that noun in case, gender, and number."
            )
            return "adjective_definite", expl, "nominative", "masculine", "singular"
        if re.search(r"(ākā)$", lower) and len(word) > 3:
            expl = (
                f"Definite (long-form) adjective '{word}', nominative singular feminine. "
                f"The definite ending -ā/-ākā marks the noun as specific and agrees in case/gender/number."
            )
            return "adjective_definite", expl, "nominative", "feminine", "singular"
        if re.search(r"(ie|ās)$", lower) and len(word) > 3 and lower not in _DEMONSTRATIVES:
            # Long-form plural definite adjective.
            gender = "masculine" if lower.endswith("ie") else "feminine"
            expl = (
                f"Definite (long-form) plural adjective '{word}', nominative plural {gender}. "
                f"The plural definite ending agrees with the modified plural noun."
            )
            return "adjective_definite", expl, "nominative", gender, "plural"

        # --- 3. Reflexive verbs (-ties / -ās) ---------------------------
        if lower.endswith("ties") or (lower.endswith("ās") and len(word) > 3):
            expl = (
                f"Reflexive verb '{word}'. The -ties / -ās ending marks the verb as reflexive — "
                f"the action turns back on the subject (e.g. mācīties = 'to study' / 'teach oneself')."
            )
            return "reflexive_verb", expl, "", "", ""

        # --- 4. Debitive (jā- prefix) -----------------------------------
        if lower.startswith("jā") and len(word) > 2:
            expl = (
                f"Debitive verb '{word}'. The jā- prefix marks the debitive mood (necessity / "
                f"obligation, ‘must do X’); the logical subject of a debitive clause appears "
                f"in the dative (e.g. 'Man jāraksta' = 'I must write')."
            )
            return "debitive", expl, "", "", ""

        # --- 5. Advanced participles + verbal nouns ---------------------
        if re.search(r"(ošs|oša|ošu|ošam|ošai|oši|ošas)$", lower):
            return "participle", (
                f"Present active participle '{word}'. Formed from a verb stem + -ošs/-oša; "
                f"behaves as an adjective and agrees with its head noun in case/gender/number."
            ), "", "", ""
        if re.search(r"(āts|āta|ātu|ātam|ātai|āti|ātas)$", lower):
            return "participle", (
                f"Past passive participle '{word}'. Formed from verb stem + -ts/-ta; "
                f"used in passive constructions and as a noun-modifying adjective."
            ), "", "", ""
        if lower.endswith("šana") and len(word) > 4:
            return "verbal_noun", (
                f"Verbal noun '{word}'. The -šana suffix derives an action noun from a verb "
                f"stem (e.g. mācīšana = 'teaching/learning')."
            ), "nominative", "feminine", "singular"

        # --- 6. Verbs (conjugated endings) ------------------------------
        # Note: -ās is excluded from the verb endings here because it is more
        # often a reflexive verb / definite plural adjective, both handled
        # above.
        verb_match = re.search(
            r"(āju|āji|ājam|ājat|ājies|āsies|ē|ē|u|i|am|at|a)$", lower
        )
        if verb_match and len(word) > 2:
            expl = (
                f"Verb '{word}'. Conjugated form (Latvian conjugates by person and number "
                f"and inflects for tense and mood). Without context the lemma cannot be inferred precisely."
            )
            return "verb", expl, "", "", ""

        # --- 7. Indefinite adjectives + nouns ---------------------------
        # At this point the word is open-class. Use suffix heuristics, but
        # acknowledge ambiguity — both nouns and short-form adjectives can
        # share the same surface endings (-s/-a/-e). The label says "likely".
        if re.search(r"(s|š)$", lower) and len(word) > 2:
            # Short-form adjective candidate vs. masculine noun. Without
            # syntactic context we default to noun unless the sentence shape
            # strongly suggests a predicative adjective. Cards expose the
            # heuristic uncertainty in the explanation.
            expl = (
                f"Open-class word '{word}' ending in -s/-š — most likely a masculine "
                f"singular noun (nominative) or a short-form (indefinite) predicative adjective. "
                f"Latvian -s/-š is the canonical masculine nominative singular ending."
            )
            return "noun", expl, "nominative", "masculine", "singular"
        if re.search(r"(is|us)$", lower) and len(word) > 2:
            expl = (
                f"Noun '{word}', masculine singular (nominative). The -is/-us ending marks "
                f"the masculine nominative for several Latvian declension classes."
            )
            return "noun", expl, "nominative", "masculine", "singular"
        if re.search(r"(a|e)$", lower) and len(word) > 2:
            expl = (
                f"Noun '{word}', feminine singular (nominative). The -a/-e ending is the "
                f"canonical feminine nominative singular form (1st/5th declensions)."
            )
            return "noun", expl, "nominative", "feminine", "singular"

        return "other", f"Word '{word}' — POS could not be determined by rule-based fallback.", "", "", ""

    # ------------------------------------------------------------------
    # Role softening per complexity
    # ------------------------------------------------------------------

    @staticmethod
    def _soften_role(role: str, complexity: str) -> str:
        """Map a fine-grained role to the simpler one used at lower complexity.

        At ``beginner`` the prompt's role list is the simple set
        (noun/verb/adjective/pronoun/...); colors are still defined for the
        fine-grained labels. We map fine → simple at beginner so card POS
        labels stay consistent with the prompt vocabulary, but keep the
        fine-grained labels at intermediate/advanced.
        """
        if complexity != "beginner":
            return role
        beginner_map = {
            "adjective_definite":   "adjective",
            "adjective_indefinite": "adjective",
            "personal_pronoun":     "pronoun",
            "demonstrative":        "pronoun",
            "reflexive_pronoun":    "pronoun",
            "relative_pronoun":     "pronoun",
            "indefinite_pronoun":   "pronoun",
            "subordinating_conjunction": "conjunction",
            "reflexive_verb":       "verb",
            "participle":           "verb",
            "debitive":             "verb",
            "verbal_noun":          "noun",
            "auxiliary":            "verb",
            "particle":             "conjunction",
        }
        return beginner_map.get(role, role)
