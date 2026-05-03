# languages/english/domain/en_fallbacks.py
"""
English Fallbacks — Domain Component

Rule-based fallback grammar analysis for English. Used when AI response is
unavailable or unparseable.

Output mirrors the German / Latvian fallback contract: each word gets a
multi-clause `individual_meaning` explanation (function in sentence + morphology
+ English-specific feature) so cards never display single-word stubs.

The fallback ALWAYS sets `is_fallback: True` so EnValidator caps confidence
at 0.3 regardless of explanation quality (per CLAUDE.md "Rich-explanation
contract").

Core design:
  - Closed-class lexicon for articles, demonstratives, pronouns by case,
    possessive determiners, possessive pronouns, reflexives, interrogatives,
    relatives, modals, auxiliaries (be/have/do), copula, prepositions,
    coordinating + subordinating conjunctions, particles.
  - Pronoun cases are NEVER flattened: I/me/my/mine are 4 different forms,
    each with its own role + case.
  - Conservative `-ing` / `-ed` heuristics that name the ambiguity rather
    than confidently mistagging.
"""

import logging
import re
from typing import Any, Dict, List, Tuple

from .en_config import EnConfig

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Closed-class lexicons.
#
# These are the source of truth for fallback POS tagging. The values include
# enough morphological detail to produce a multi-clause individual_meaning.
# ---------------------------------------------------------------------------

_ARTICLES = {
    "a":   ("indefinite", "Indefinite article 'a' (used before consonant onsets); marks the following noun as non-specific or first-mentioned. Articles are a closed class in English with no inflection."),
    "an":  ("indefinite", "Indefinite article 'an' (used before vowel onsets); marks the following noun as non-specific. The choice 'a' vs. 'an' is purely phonological."),
    "the": ("definite", "Definite article 'the'; marks the following noun as specific or already known to speaker and hearer. Used with both singular and plural, count and mass nouns."),
}

_DEMONSTRATIVES = {
    "this":  ("singular", "near", "Demonstrative — points to a singular referent NEAR the speaker. Functions as a determiner when followed by a noun ('this book') and as a pronoun when standing alone ('this is mine')."),
    "that":  ("singular", "far",  "Demonstrative — points to a singular referent FAR from the speaker. Ambiguous on the surface: also serves as a relative pronoun (after a noun + clause) and as a complementizer/subordinating conjunction (after a verb of saying/thinking)."),
    "these": ("plural",   "near", "Demonstrative — points to plural referents NEAR the speaker."),
    "those": ("plural",   "far",  "Demonstrative — points to plural referents FAR from the speaker."),
}

# Personal pronouns by case. Latin-letter keys are lowercased.
# Format: (role, case, person, number, gender, explanation)
_PERSONAL_PRONOUNS: Dict[str, Tuple[str, str, str, str, str, str]] = {
    # Nominative (subject)
    "i":    ("personal_pronoun", "nominative", "1", "singular", "",          "1st-person singular subject pronoun. Always capitalised in writing. The nominative case form — used as the subject of a finite verb."),
    "we":   ("personal_pronoun", "nominative", "1", "plural",   "",          "1st-person plural subject pronoun. The nominative case form."),
    "you":  ("personal_pronoun", "nominative", "2", "singular", "",          "2nd-person pronoun (singular or plural). English collapses the historical thou/you distinction; case is identical for nominative and accusative."),
    "he":   ("personal_pronoun", "nominative", "3", "singular", "masculine", "3rd-person singular masculine subject pronoun. Nominative case."),
    "she":  ("personal_pronoun", "nominative", "3", "singular", "feminine",  "3rd-person singular feminine subject pronoun. Nominative case."),
    "it":   ("personal_pronoun", "nominative", "3", "singular", "neuter",    "3rd-person singular neuter pronoun. Nominative or accusative (no case distinction). Also serves as expletive subject in 'it is raining' / 'it is obvious that ...'."),
    "they": ("personal_pronoun", "nominative", "3", "plural",   "",          "3rd-person plural subject pronoun. Increasingly used as singular non-binary pronoun; case is the nominative form."),
    # Accusative (object)
    "me":   ("personal_pronoun", "accusative", "1", "singular", "",          "1st-person singular object pronoun. Accusative case — used as direct object, indirect object, or after a preposition."),
    "us":   ("personal_pronoun", "accusative", "1", "plural",   "",          "1st-person plural object pronoun. Accusative case."),
    "him":  ("personal_pronoun", "accusative", "3", "singular", "masculine", "3rd-person singular masculine object pronoun. Accusative case — direct/indirect object or object of a preposition."),
    "her":  ("personal_pronoun", "accusative", "3", "singular", "feminine",  "3rd-person singular feminine object pronoun OR genitive determiner — same surface form. As object pronoun: 'I saw her'; as possessive determiner: 'her book'."),
    "them": ("personal_pronoun", "accusative", "3", "plural",   "",          "3rd-person plural object pronoun. Accusative case."),
}

# Possessive determiners: pre-noun ('my book'). Distinct from possessive pronouns.
_POSSESSIVE_DETERMINERS: Dict[str, Tuple[str, str, str]] = {
    "my":    ("1", "singular", "1st-person singular possessive determiner. Precedes a noun ('my book') — distinct from the possessive pronoun 'mine' which stands alone. Genitive determiner case."),
    "your":  ("2", "singular", "2nd-person possessive determiner. Precedes a noun ('your book') — distinct from the possessive pronoun 'yours'. Genitive determiner case."),
    "his":   ("3", "singular", "3rd-person singular masculine possessive determiner. SURFACE-IDENTICAL to the possessive pronoun 'his' — distinguished by syntactic position (before a noun = determiner; standing alone = pronoun)."),
    "its":   ("3", "singular", "3rd-person singular neuter possessive determiner. Note: 'it's' (with apostrophe) is the contraction 'it is' — different word."),
    "our":   ("1", "plural",   "1st-person plural possessive determiner. Precedes a noun — distinct from the possessive pronoun 'ours'."),
    "their": ("3", "plural",   "3rd-person plural possessive determiner. Precedes a noun — distinct from the possessive pronoun 'theirs'. Note: distinct from the contraction 'they're' (= they are)."),
}

# Possessive pronouns: stand alone ('that book is mine').
_POSSESSIVE_PRONOUNS: Dict[str, Tuple[str, str, str]] = {
    "mine":   ("1", "singular", "1st-person singular possessive pronoun. Stands alone ('that book is mine') — distinct from the possessive determiner 'my'."),
    "yours":  ("2", "singular", "2nd-person possessive pronoun. Stands alone ('that book is yours')."),
    # 'his' is in _POSSESSIVE_DETERMINERS — it is structurally ambiguous; we tag by position.
    "hers":   ("3", "singular", "3rd-person singular feminine possessive pronoun. Stands alone — distinct from the possessive determiner 'her'."),
    "ours":   ("1", "plural",   "1st-person plural possessive pronoun. Stands alone."),
    "theirs": ("3", "plural",   "3rd-person plural possessive pronoun. Stands alone."),
}

_REFLEXIVE_PRONOUNS: Dict[str, Tuple[str, str, str]] = {
    "myself":     ("1", "singular", "1st-person singular reflexive pronoun. Refers back to the clause subject; also used intensively ('I did it myself')."),
    "yourself":   ("2", "singular", "2nd-person singular reflexive pronoun."),
    "yourselves": ("2", "plural",   "2nd-person plural reflexive pronoun."),
    "himself":    ("3", "singular", "3rd-person singular masculine reflexive pronoun."),
    "herself":    ("3", "singular", "3rd-person singular feminine reflexive pronoun."),
    "itself":     ("3", "singular", "3rd-person singular neuter reflexive pronoun."),
    "ourselves":  ("1", "plural",   "1st-person plural reflexive pronoun."),
    "themselves": ("3", "plural",   "3rd-person plural reflexive pronoun."),
}

# Interrogatives — clause-initial in a question ('Who is here?').
# Note: who/which/whose are SURFACE-AMBIGUOUS with relative pronouns; we
# tag as interrogative if the word starts a clause, else as relative.
_INTERROGATIVES_REL = {
    "who":   "wh-word — interrogative pronoun (in a question, asking for a person) or relative pronoun (introducing a relative clause modifying a person). Subject case (cf. accusative 'whom').",
    "whom":  "wh-word — accusative case of 'who'. Used as object of a verb or preposition in formal English.",
    "whose": "wh-word — possessive/genitive form. Functions as an interrogative pronoun ('Whose is this?') or relative pronoun ('the man whose car is red').",
    "which": "wh-word — interrogative pronoun (asking for a thing/choice from a known set) or relative pronoun (introducing a relative clause modifying a non-human noun).",
    "what":  "wh-word — interrogative pronoun ('what is that?') or wh-determiner ('what book?'). Does NOT serve as a relative pronoun in standard English.",
}

_INTERROGATIVE_ADVERBS = {
    "where": "Interrogative/relative adverb of place. In a question ('Where are you?'); in a relative clause ('the place where I live').",
    "when":  "Interrogative/relative adverb of time. In a question ('When did you arrive?'); in a relative clause ('the day when we met').",
    "why":   "Interrogative adverb of reason ('Why did you go?').",
    "how":   "Interrogative adverb of manner/degree ('How did it happen?', 'how big').",
}

_MODALS = {
    "can":    ("ability/permission",  "Modal verb 'can'. Expresses ABILITY ('I can swim') or PERMISSION ('You can go'). Defective paradigm — no -s, no infinitive, no participles. Takes a bare-infinitive complement."),
    "could":  ("ability/possibility/polite", "Modal verb 'could'. Past of 'can' OR present-tense polite/hypothetical possibility ('Could you help?'). Defective paradigm; bare-infinitive complement."),
    "will":   ("volition/futurity",  "Modal verb 'will'. Expresses VOLITION or FUTURITY (the closest English has to a future-tense marker). Defective paradigm."),
    "would":  ("hypothetical/habitual_past", "Modal verb 'would'. Past of 'will' OR hypothetical/conditional ('I would go if I could') OR habitual past ('we would visit her every summer')."),
    "shall":  ("futurity/obligation", "Modal verb 'shall'. Formal/legal futurity in 1st person, or obligation in 2nd/3rd ('you shall not pass')."),
    "should": ("obligation/advice",  "Modal verb 'should'. Expresses ADVICE or weak OBLIGATION. Past of 'shall'."),
    "may":    ("permission/possibility", "Modal verb 'may'. Expresses PERMISSION ('you may go') or POSSIBILITY ('it may rain')."),
    "might":  ("possibility",        "Modal verb 'might'. Expresses tentative POSSIBILITY. Past of 'may' but also free-standing."),
    "must":   ("obligation/strong_inference", "Modal verb 'must'. Expresses strong OBLIGATION ('you must go') or strong INFERENCE ('she must be tired')."),
    "ought":  ("obligation/advice",  "Modal verb 'ought'. The only English modal that retains 'to' before its infinitive complement: 'ought to leave'."),
}

_BE_FORMS = {
    "be":    ("infinitive",    "", "be — infinitive of the copula/auxiliary 'be'. Used after modals, after 'to', and in imperatives. As copula links a subject to a predicate; as auxiliary forms the progressive (be + V-ing) and passive (be + past_participle)."),
    "am":    ("present", "1", "1st-person singular present of 'be'. Copula or progressive/passive auxiliary."),
    "is":    ("present", "3", "3rd-person singular present of 'be'. Copula or progressive/passive auxiliary."),
    "are":   ("present", "",  "Present of 'be' for 2nd-person and all plural subjects. Copula or progressive/passive auxiliary."),
    "was":   ("past",    "",  "Past of 'be' for 1st-person singular and 3rd-person singular subjects."),
    "were":  ("past",    "",  "Past of 'be' for 2nd-person and all plural subjects. Also the surviving subjunctive form ('if I were you')."),
    "been":  ("past_participle", "", "Past participle of 'be'. Appears after 'have' to form perfect aspects ('has been') and combines with -ing for perfect progressive."),
    "being": ("present_participle", "", "Present participle / gerund of 'be'. Appears after auxiliary 'be' ('is being asked' = passive progressive) or as a gerund ('being late is bad')."),
}

_HAVE_FORMS = {
    "have":   ("infinitive_or_present", "", "have — base form. Functions as auxiliary forming the perfect aspect (have + past_participle) or as a lexical verb meaning 'possess'."),
    "has":    ("present", "3", "3rd-person singular present of 'have'. As auxiliary forms the present perfect ('has eaten'); as lexical verb means 'possesses'."),
    "had":    ("past", "", "Past tense AND past participle of 'have'. As auxiliary forms the past perfect ('had eaten'); as lexical verb the simple past ('had a dog')."),
    "having": ("present_participle", "", "Present participle / gerund of 'have'. Used in perfect-participle clauses ('having eaten, he left') or as a gerund ('having a dog is fun')."),
}

_DO_FORMS = {
    "do":    ("infinitive_or_present", "", "do — base form. As auxiliary supports negation/inversion/emphasis when the main verb is lexical ('do you know?'). As lexical verb means 'perform'."),
    "does":  ("present", "3", "3rd-person singular present of 'do'. As auxiliary used in present-tense questions, negations, and emphasis ('does she know?', 'she does NOT know')."),
    "did":   ("past", "", "Past of 'do'. As auxiliary used in past-tense questions, negations, and emphasis."),
    "doing": ("present_participle", "", "Present participle / gerund of 'do'."),
    "done":  ("past_participle", "", "Past participle of 'do'. Appears after 'have' for perfect aspect ('have done')."),
}

# Common prepositions (about ~30) — for the disambiguation rule against
# the phrasal-verb-particle reading we look at the immediate right
# context (object NP can or cannot move past it).
_PREPOSITIONS = {
    "of", "in", "on", "at", "by", "for", "with", "from", "to", "into",
    "onto", "upon", "through", "between", "among", "against", "before",
    "after", "during", "since", "until", "till", "beside", "behind",
    "beyond", "despite", "except", "without", "about", "across",
    "along", "around", "down", "up", "off", "out", "over", "under",
    "near", "above", "below", "toward", "towards",
}

# Particle-only words (when not used as preposition).
_COMMON_PARTICLES = {
    "up", "down", "in", "out", "on", "off", "away", "back", "over",
    "through", "around", "about",
}

_COORDINATING_CONJUNCTIONS = {
    "for":  "FANBOYS coordinating conjunction 'for' (= because; rare in modern English). SURFACE-AMBIGUOUS with the preposition 'for'.",
    "and":  "FANBOYS coordinating conjunction 'and'. Joins constituents of equal rank.",
    "nor":  "FANBOYS coordinating conjunction 'nor'. Used after a negative clause: 'not X nor Y'.",
    "but":  "FANBOYS coordinating conjunction 'but'. Introduces a contrast.",
    "or":   "FANBOYS coordinating conjunction 'or'. Introduces an alternative.",
    "yet":  "FANBOYS coordinating conjunction 'yet'. Introduces a concessive contrast.",
    "so":   "FANBOYS coordinating conjunction 'so'. Introduces a consequence.",
}

_SUBORDINATING_CONJUNCTIONS = {
    "because":  "Subordinating conjunction. Introduces a causal subordinate clause.",
    "although": "Subordinating conjunction. Introduces a concessive subordinate clause.",
    "though":   "Subordinating conjunction. Concessive (= 'although'); also serves as an adverb meaning 'however'.",
    "since":    "SURFACE-AMBIGUOUS — temporal subordinating conjunction ('since I arrived') or causal ('since you asked'). Also a preposition ('since 1990').",
    "while":    "Subordinating conjunction. Temporal ('while I was reading') or concessive ('while X is true, Y is also true').",
    "if":       "Subordinating conjunction. Introduces a conditional subordinate clause.",
    "unless":   "Subordinating conjunction. Introduces a negative conditional ('unless X' = 'if not X').",
    "until":    "Subordinating conjunction (also a preposition). Introduces a temporal clause indicating an endpoint.",
    "when":     "Subordinating conjunction (also an interrogative/relative adverb). Introduces a temporal clause.",
    "whenever": "Subordinating conjunction. Introduces a generalized temporal clause.",
    "where":    "Subordinating conjunction (also interrogative/relative). Introduces a locative clause.",
    "whereas":  "Subordinating conjunction. Introduces a contrastive clause.",
    "before":   "Subordinating conjunction (also a preposition). Introduces a temporal clause indicating priority.",
    "after":    "Subordinating conjunction (also a preposition). Introduces a temporal clause indicating posteriority.",
    "as":       "SURFACE-AMBIGUOUS — subordinating conjunction (causal/temporal/comparative) or preposition.",
}

# Common irregular past / past-participle forms (fast-path for fallback).
_IRREGULAR_PAST = {
    "went":  ("go", "past"),
    "gone":  ("go", "past_participle"),
    "ate":   ("eat", "past"),
    "eaten": ("eat", "past_participle"),
    "took":  ("take", "past"),
    "taken": ("take", "past_participle"),
    "saw":   ("see", "past"),
    "seen":  ("see", "past_participle"),
    "gave":  ("give", "past"),
    "given": ("give", "past_participle"),
    "came":  ("come", "past"),
    "made":  ("make", "past_or_pp"),
    "ran":   ("run", "past"),
    "run":   ("run", "base_or_pp"),
    "wrote": ("write", "past"),
    "written": ("write", "past_participle"),
    "broke": ("break", "past"),
    "broken": ("break", "past_participle"),
    "spoke": ("speak", "past"),
    "spoken": ("speak", "past_participle"),
    "knew":  ("know", "past"),
    "known": ("know", "past_participle"),
    "thought": ("think", "past_or_pp"),
    "felt":  ("feel", "past_or_pp"),
    "told":  ("tell", "past_or_pp"),
    "said":  ("say", "past_or_pp"),
    "got":   ("get", "past_or_pp"),
    "gotten": ("get", "past_participle"),
    "left":  ("leave", "past_or_pp"),
    "found": ("find", "past_or_pp"),
    "kept":  ("keep", "past_or_pp"),
    "lost":  ("lose", "past_or_pp"),
    "put":   ("put", "any"),
    "cut":   ("cut", "any"),
    "hit":   ("hit", "any"),
    "let":   ("let", "any"),
    "set":   ("set", "any"),
}


class EnFallbacks:
    """Rule-based fallback analysis for English grammar."""

    def __init__(self, config: EnConfig):
        self.config = config

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def create_fallback(self, sentence: str, complexity: str) -> Dict[str, Any]:
        """Create a basic rule-based grammar analysis with rich explanations.

        Always sets `is_fallback: True` so the validator caps confidence at 0.3.
        """
        tokens = sentence.split()
        # Lowercased, punctuation-stripped tokens for context-sensitive lookups.
        lower_tokens = [t.strip(".,!?;:\"'()[]" ).lower() for t in tokens]

        word_explanations = []
        for i, token in enumerate(tokens):
            clean = token.strip(".,!?;:\"'()[]")
            (
                role, individual_meaning, case, number, person,
                tense, aspect, voice,
            ) = self._classify_word(
                clean, complexity,
                prev_lower=lower_tokens[i - 1] if i > 0 else "",
                next_lower=lower_tokens[i + 1] if i + 1 < len(lower_tokens) else "",
                position=i,
                lower_tokens=lower_tokens,
            )

            display_role = self._soften_role(role, complexity)
            color = self.config.get_color_for_role(display_role, complexity)

            # Punctuation-only tokens get a brief description.
            is_punct = clean == ""
            if is_punct:
                display_role = "other"
                color = self.config.get_color_for_role("other", complexity)
                individual_meaning = "Punctuation token; structures the clause boundary."
                case = number = person = tense = aspect = voice = ""

            display = f"{token} ({display_role}): {individual_meaning}"

            word_explanations.append({
                "word": token,
                "role": display_role,
                "color": color,
                "meaning": display,
                "individual_meaning": individual_meaning,
                "case": case,
                "number": number,
                "person": person,
                "tense": tense,
                "aspect": aspect,
                "voice": voice,
            })

        return {
            "word_explanations": word_explanations,
            "overall_structure": "English sentence (rule-based fallback analysis).",
            "sentence_structure": "English sentence (rule-based fallback analysis).",
            "tense_aspect": "",
            "voice": "",
            "explanations": {
                item["word"]: item["meaning"] for item in word_explanations
            },
            "elements": {item["word"]: item["role"] for item in word_explanations},
            "grammar_notes": (
                "Rule-based fallback — AI unavailable. POS tags inferred from "
                "closed-class lexicons + suffix heuristics; categorical ambiguity "
                "(to / -ing / -ed / that / who-which / particle vs. preposition) "
                "is acknowledged in the per-word explanations rather than guessed."
            ),
            "is_fallback": True,
            "confidence": 0.3,
        }

    # ------------------------------------------------------------------
    # Per-word classification
    # ------------------------------------------------------------------

    def _classify_word(
        self,
        word: str,
        complexity: str,
        prev_lower: str = "",
        next_lower: str = "",
        position: int = 0,
        lower_tokens: List[str] = None,
    ) -> Tuple[str, str, str, str, str, str, str, str]:
        """Classify a single word.

        Returns (role, individual_meaning, case, number, person, tense, aspect, voice).
        """
        if not word:
            return ("other", "Token with no content.", "", "", "", "", "", "")

        lower = word.lower()
        lower_tokens = lower_tokens or []

        # --- 1. Articles -------------------------------------------------
        if lower in _ARTICLES:
            kind, expl = _ARTICLES[lower]
            return ("article", f"'{word}': {expl}", "", "", "", "", "", "")

        # --- 2. Demonstratives (this/that/these/those) ------------------
        # Note: 'that' is 4-way ambiguous. We make a context-sensitive call:
        #   - between a noun-ish word and a verb/clause → relative_pronoun
        #   - after a verb of saying/thinking, before a clause → subordinating_conjunction
        #   - immediately followed by a noun → demonstrative determiner
        #   - else (standing alone) → demonstrative pronoun
        if lower in _DEMONSTRATIVES:
            number, deixis, base_expl = _DEMONSTRATIVES[lower]
            if lower == "that":
                # Context-sensitive handling.
                think_say_verbs = {
                    "think", "thinks", "thought", "say", "says", "said",
                    "know", "knows", "knew", "believe", "believes", "believed",
                    "hope", "hopes", "hoped", "claim", "claims", "claimed",
                    "feel", "feels", "felt", "see", "sees", "saw",
                }
                # Heuristic: if the previous word is a verb of saying/thinking, treat as complementizer.
                if prev_lower in think_say_verbs:
                    return (
                        "subordinating_conjunction",
                        f"'that' — subordinating conjunction (complementizer). Follows a verb of saying/thinking ('{prev_lower}') and introduces a propositional complement clause. Distinct from the demonstrative reading (which requires no preceding clause-licensing verb) and from the relative pronoun reading (which would follow a noun phrase).",
                        "", "", "", "", "", "",
                    )
                # Heuristic: if next word is a noun-shaped token, treat as determiner.
                if next_lower and self._looks_like_noun(next_lower):
                    return (
                        "demonstrative",
                        f"'that' — demonstrative determiner. Directly precedes the noun '{next_lower}' and modifies it (specifying which one). Distinct from the demonstrative pronoun reading (which would stand alone), the relative-pronoun reading (after a noun + clause), and the complementizer reading (after a verb of saying/thinking).",
                        "", number, "", "", "", "",
                    )
                # Default: ambiguous — flag both readings.
                return (
                    "demonstrative",
                    f"'that' — surface-ambiguous: demonstrative determiner / pronoun, relative pronoun, or subordinating conjunction (complementizer). In this fallback path we tag it as a demonstrative; the AI path uses positional context to disambiguate. {base_expl}",
                    "", number, "", "", "", "",
                )
            return ("demonstrative", f"'{word}' — {base_expl}", "", number, "", "", "", "")

        # --- 3. Personal pronouns ---------------------------------------
        if lower in _PERSONAL_PRONOUNS:
            role, case, person, number, gender, expl = _PERSONAL_PRONOUNS[lower]
            # Special case for 'her' which is also a possessive determiner.
            # If the next token looks like a noun, prefer the determiner reading.
            if lower == "her" and next_lower and self._looks_like_noun(next_lower):
                return (
                    "possessive_determiner",
                    f"'her' — 3rd-person singular feminine possessive determiner (genitive determiner case). Precedes the noun '{next_lower}' and marks possession. SURFACE-IDENTICAL to the accusative pronoun 'her' — distinguished by syntactic position (before a noun = determiner; as object of a verb/preposition = pronoun).",
                    "genitive_determiner", "singular", "3", "", "", "",
                )
            return (role, f"'{word}' — {expl}", case, number, person, "", "", "")

        # --- 4. Reflexive pronouns --------------------------------------
        if lower in _REFLEXIVE_PRONOUNS:
            person, number, expl = _REFLEXIVE_PRONOUNS[lower]
            return ("reflexive_pronoun", f"'{word}' — {expl}", "reflexive", number, person, "", "", "")

        # --- 5. Possessive pronouns (mine, yours, hers, ours, theirs) ---
        if lower in _POSSESSIVE_PRONOUNS:
            person, number, expl = _POSSESSIVE_PRONOUNS[lower]
            return ("possessive_pronoun", f"'{word}' — {expl}", "genitive_pronoun", number, person, "", "", "")

        # --- 6. Possessive determiners (my, your, his, its, our, their)
        if lower in _POSSESSIVE_DETERMINERS:
            person, number, expl = _POSSESSIVE_DETERMINERS[lower]
            # 'his' is surface-ambiguous (determiner vs. possessive pronoun) —
            # we prefer the determiner reading if the next word is a noun, else
            # the pronoun reading.
            if lower == "his" and next_lower and not self._looks_like_noun(next_lower):
                return (
                    "possessive_pronoun",
                    f"'his' — 3rd-person singular masculine possessive pronoun. Stands alone (the next word '{next_lower or '∅'}' is not a noun). SURFACE-IDENTICAL to the determiner 'his' — distinguished by syntactic position.",
                    "genitive_pronoun", "singular", "3", "", "", "",
                )
            return ("possessive_determiner", f"'{word}' — {expl}", "genitive_determiner", number, person, "", "", "")

        # --- 7. Interrogatives / relative pronouns ----------------------
        if lower in _INTERROGATIVES_REL:
            base_expl = _INTERROGATIVES_REL[lower]
            # If the word is the first token of the (sub)clause → interrogative;
            # otherwise default to relative_pronoun. We approximate "clause-initial"
            # as position 0 in the sentence.
            if position == 0:
                return ("interrogative_pronoun", f"'{word}' — {base_expl} Here at the start of the sentence — interrogative reading.", "", "", "", "", "", "")
            return ("relative_pronoun", f"'{word}' — {base_expl} Mid-sentence position; relative-pronoun reading more likely.", "", "", "", "", "", "")

        if lower in _INTERROGATIVE_ADVERBS:
            return ("adverb", f"'{word}' — {_INTERROGATIVE_ADVERBS[lower]}", "", "", "", "", "", "")

        # --- 8. Modal verbs ---------------------------------------------
        if lower in _MODALS:
            modality, expl = _MODALS[lower]
            return ("modal_verb", f"'{word}' — {expl} Modality flavour: {modality}.", "", "", "", "", "", "")

        # --- 9. Auxiliaries: be / have / do -----------------------------
        if lower in _BE_FORMS:
            tense, person, expl = _BE_FORMS[lower]
            return ("auxiliary", f"'{word}' — {expl}", "", "", person, tense, "", "")
        if lower in _HAVE_FORMS:
            tense, person, expl = _HAVE_FORMS[lower]
            return ("auxiliary", f"'{word}' — {expl}", "", "", person, tense, "", "")
        if lower in _DO_FORMS:
            tense, person, expl = _DO_FORMS[lower]
            return ("auxiliary", f"'{word}' — {expl}", "", "", person, tense, "", "")

        # --- 10. Conjunctions -------------------------------------------
        if lower in _COORDINATING_CONJUNCTIONS:
            return ("coordinating_conjunction", f"'{word}' — {_COORDINATING_CONJUNCTIONS[lower]}", "", "", "", "", "", "")
        if lower in _SUBORDINATING_CONJUNCTIONS:
            return ("subordinating_conjunction", f"'{word}' — {_SUBORDINATING_CONJUNCTIONS[lower]}", "", "", "", "", "", "")

        # --- 11. Particle 'not' / negation ------------------------------
        if lower in {"not", "n't"}:
            return (
                "particle",
                f"'{word}' — negative particle. Marks sentential or constituent negation; in finite clauses appears after the (first) auxiliary or in do-support constructions.",
                "", "", "", "", "", "",
            )

        # --- 12. The infinitive marker / preposition 'to' ---------------
        if lower == "to":
            # Diagnostic: if the next word is a base-form lexical verb
            # (not a noun, not an article, not a preposition) → infinitive marker.
            if next_lower and self._looks_like_base_verb(next_lower):
                return (
                    "infinitive_marker",
                    f"'to' — infinitive marker (a particle), NOT a preposition. Diagnostic: the next word '{next_lower}' is a base-form verb. Together 'to {next_lower}' is an infinitive verb phrase.",
                    "", "", "", "", "", "",
                )
            # Otherwise: preposition.
            return (
                "preposition",
                f"'to' — preposition (directional / dative). Diagnostic: the next word '{next_lower or '∅'}' is not a base-form verb. Heads a prepositional phrase.",
                "", "", "", "", "", "",
            )

        # --- 13. Particle vs. preposition for up/down/in/out/on/off etc.
        if lower in _COMMON_PARTICLES:
            # If the previous token is a verb (heuristic: -ed / -ing / common verb form),
            # we lean toward phrasal-verb particle. We can't apply the full movement
            # test here without parsing — so we acknowledge ambiguity in the explanation.
            if prev_lower and self._looks_like_verb_form(prev_lower):
                return (
                    "phrasal_verb_particle",
                    f"'{word}' — phrasal-verb particle (after the verb '{prev_lower}'). SURFACE-AMBIGUOUS with the preposition '{word}' — the diagnostic (movement test: can the object appear between verb and particle?) requires more context than the rule-based fallback can determine. Default reading after a verb is the phrasal-particle reading.",
                    "", "", "", "", "", "",
                )
            # Default: treat as preposition (more common surface use).
            return (
                "preposition",
                f"'{word}' — preposition. SURFACE-AMBIGUOUS with the phrasal-verb-particle reading; here we default to preposition because there is no preceding verb in immediate context.",
                "", "", "", "", "", "",
            )

        # --- 14. Other prepositions -------------------------------------
        if lower in _PREPOSITIONS:
            return (
                "preposition",
                f"'{word}' — preposition. Heads a prepositional phrase whose object follows; English prepositions assign accusative case to pronoun objects.",
                "", "", "", "", "", "",
            )

        # --- 15. Irregular past forms (fast-path) -----------------------
        if lower in _IRREGULAR_PAST:
            lemma, kind = _IRREGULAR_PAST[lower]
            return self._irregular_verb_to_role(word, lower, lemma, kind, prev_lower)

        # --- 16. Conservative -ing / -ed disambiguation -----------------
        if lower.endswith("ing") and len(lower) > 4:
            return self._classify_ing(word, prev_lower, next_lower)

        if lower.endswith("ed") and len(lower) > 3:
            return self._classify_ed(word, prev_lower)

        # --- 17. Adverbs ending in -ly ----------------------------------
        if lower.endswith("ly") and len(lower) > 3:
            return (
                "adverb",
                f"'{word}' — manner / sentence adverb. The -ly suffix derives an adverb from an adjective base; modifies a verb, an adjective, another adverb, or the whole clause.",
                "", "", "", "", "", "",
            )

        # --- 18. Comparative / superlative ------------------------------
        if lower.endswith("est") and len(lower) > 3:
            return (
                "superlative",
                f"'{word}' — superlative form (-est). Marks the highest degree of the adjectival/adverbial property among a comparison set. Periphrastic equivalent: 'most {lower[:-3]}'.",
                "", "", "", "", "", "",
            )
        if lower.endswith("er") and len(lower) > 3 and not lower.endswith("ever"):
            # Could be comparative ('bigger') OR an agent noun ('teacher', 'runner').
            # We acknowledge ambiguity rather than confidently pick.
            return (
                "comparative",
                f"'{word}' — likely a comparative adjective/adverb (-er suffix). SURFACE-AMBIGUOUS with agent-noun -er ('teacher', 'runner', 'writer'); the rule-based fallback cannot fully disambiguate without more context.",
                "", "", "", "", "", "",
            )

        # --- 19. Open-class default — noun ------------------------------
        if word[0].isupper() and position > 0:
            return (
                "noun",
                f"'{word}' — likely a proper noun (capitalised mid-sentence). Refers to a specific, uniquely identifiable entity; English does not inflect proper nouns for case.",
                "", "singular", "", "", "", "",
            )
        return (
            "noun",
            f"'{word}' — likely an open-class noun (the rule-based fallback defaults to noun for unknown content words). English nouns are uninflected for case and gender; only number ({lower} → {lower}s? plural form not analysed) and possessive -'s mark them morphologically.",
            "", "singular", "", "", "", "",
        )

    # ------------------------------------------------------------------
    # Sub-classifiers
    # ------------------------------------------------------------------

    def _irregular_verb_to_role(
        self, word: str, lower: str, lemma: str, kind: str, prev_lower: str,
    ) -> Tuple[str, str, str, str, str, str, str, str]:
        """Tag an irregular verb form."""
        if kind == "past":
            return (
                "verb",
                f"'{word}' — irregular simple past tense of '{lemma}'. Diagnostic: the form is not 'have/has/had + V', so this is the past-tense reading rather than the past-participle reading.",
                "", "", "", "past", "simple", "active",
            )
        if kind == "past_participle":
            aspect = "perfect" if prev_lower in {"have", "has", "had"} else (
                "passive_or_perfect" if prev_lower in {"is", "am", "are", "was", "were", "be", "been", "being"}
                else "perfect_or_passive"
            )
            return (
                "past_participle",
                f"'{word}' — irregular past participle of '{lemma}'. After '{prev_lower or '∅'}', the construction is {aspect}.",
                "", "", "", "", aspect, "",
            )
        if kind in ("past_or_pp", "any", "base_or_pp"):
            # Disambiguate from context.
            if prev_lower in {"have", "has", "had"}:
                return (
                    "past_participle",
                    f"'{word}' — past participle of '{lemma}', forming the perfect aspect after '{prev_lower}'.",
                    "", "", "", "", "perfect", "active",
                )
            if prev_lower in {"is", "am", "are", "was", "were", "be", "been", "being"}:
                return (
                    "past_participle",
                    f"'{word}' — past participle of '{lemma}' after a be-form ('{prev_lower}'); likely passive voice.",
                    "", "", "", "", "passive", "passive",
                )
            if kind == "base_or_pp":
                return (
                    "verb",
                    f"'{word}' — base form / past participle of '{lemma}' (irregular, both forms identical). Standalone reading: base form / simple-present non-3sg.",
                    "", "", "", "present", "simple", "active",
                )
            return (
                "verb",
                f"'{word}' — irregular past or past participle of '{lemma}' — surface-identical. The standalone reading is simple past tense.",
                "", "", "", "past", "simple", "active",
            )
        return (
            "verb",
            f"'{word}' — irregular form of '{lemma}'.",
            "", "", "", "", "", "",
        )

    def _classify_ing(
        self, word: str, prev_lower: str, next_lower: str,
    ) -> Tuple[str, str, str, str, str, str, str, str]:
        """Classify an -ing form. Acknowledges ambiguity."""
        be_forms = {"is", "am", "are", "was", "were", "being", "been"}
        if prev_lower in be_forms:
            voice = "passive" if next_lower and self._looks_like_past_participle(next_lower) else "active"
            return (
                "present_participle",
                f"'{word}' — present participle (-ing form) after the be-auxiliary '{prev_lower}'. Together they form the progressive aspect ({voice} voice).",
                "", "", "", "", "progressive", voice,
            )
        # Gerund vs. adjectival -ing depends on syntactic position; we name the ambiguity.
        if next_lower and self._looks_like_noun(next_lower):
            return (
                "adjective",
                f"'{word}' — likely an adjectival/attributive -ing form modifying the noun '{next_lower}' (e.g. 'running water'). SURFACE-AMBIGUOUS with the gerund (-ing as noun) and present participle (after be-aux) readings.",
                "", "", "", "", "", "",
            )
        return (
            "gerund",
            f"'{word}' — likely a gerund (-ing form functioning as a noun). SURFACE-AMBIGUOUS with the present-participle reading (which would follow a be-auxiliary). The previous word '{prev_lower or '∅'}' is not a be-form, so we lean toward the gerund reading.",
            "", "", "", "", "", "",
        )

    def _classify_ed(
        self, word: str, prev_lower: str,
    ) -> Tuple[str, str, str, str, str, str, str, str]:
        """Classify an -ed form. Acknowledges ambiguity."""
        if prev_lower in {"have", "has", "had"}:
            return (
                "past_participle",
                f"'{word}' — past participle (-ed form) after the have-auxiliary '{prev_lower}'. Together they form the perfect aspect.",
                "", "", "", "", "perfect", "active",
            )
        if prev_lower in {"is", "am", "are", "was", "were", "be", "been", "being"}:
            return (
                "past_participle",
                f"'{word}' — past participle (-ed form) after the be-auxiliary '{prev_lower}'. Together they form the passive voice (or be + adjectival -ed).",
                "", "", "", "", "", "passive",
            )
        return (
            "verb",
            f"'{word}' — likely simple past tense (-ed form). SURFACE-AMBIGUOUS with the past-participle reading (which would follow have/be) and the adjectival past-participle reading (which would precede a noun, e.g. 'broken window'). The previous word '{prev_lower or '∅'}' is not an auxiliary, so we lean toward the simple past tense.",
            "", "", "", "past", "simple", "active",
        )

    # ------------------------------------------------------------------
    # Heuristics
    # ------------------------------------------------------------------

    @staticmethod
    def _looks_like_noun(word: str) -> bool:
        """Cheap heuristic: looks like a noun (not a function word, not an obvious verb)."""
        if not word:
            return False
        if word in _ARTICLES or word in _DEMONSTRATIVES:
            return False
        if word in _PERSONAL_PRONOUNS or word in _MODALS:
            return False
        if word in _BE_FORMS or word in _HAVE_FORMS or word in _DO_FORMS:
            return False
        if word in _PREPOSITIONS:
            return False
        if word in _COORDINATING_CONJUNCTIONS or word in _SUBORDINATING_CONJUNCTIONS:
            return False
        if word in {"not", "n't", "to"}:
            return False
        # Ends with -ly → adverb, not noun.
        if word.endswith("ly") and len(word) > 3:
            return False
        return True

    @staticmethod
    def _looks_like_base_verb(word: str) -> bool:
        """Cheap heuristic: a bare-infinitive verb. Used for `to + V` detection."""
        if not word:
            return False
        if word in _ARTICLES or word in _DEMONSTRATIVES:
            return False
        if word in _PERSONAL_PRONOUNS or word in _POSSESSIVE_DETERMINERS:
            return False
        if word in _PREPOSITIONS:
            return False
        # -ed and -ing forms are not base forms.
        if word.endswith("ed") and len(word) > 3:
            return False
        if word.endswith("ing") and len(word) > 4:
            return False
        # 3sg -s form is not base.
        if word.endswith("s") and len(word) > 2:
            # But many bare nouns also end in -s (e.g. 'glass'); we don't reject
            # outright. Lean conservatively: not a base verb.
            return False
        return True

    @staticmethod
    def _looks_like_verb_form(word: str) -> bool:
        """Heuristic: looks like a finite verb (for phrasal-particle detection)."""
        if not word:
            return False
        if word in _BE_FORMS or word in _HAVE_FORMS or word in _DO_FORMS:
            return True
        if word in _IRREGULAR_PAST:
            return True
        if word.endswith("ed") and len(word) > 3:
            return True
        if word.endswith("ing") and len(word) > 4:
            return True
        # 3sg -s.
        if word.endswith("s") and len(word) > 2 and word not in _PREPOSITIONS:
            return True
        return False

    @staticmethod
    def _looks_like_past_participle(word: str) -> bool:
        """Heuristic for passive-voice detection inside -ing classification."""
        if not word:
            return False
        if word in _IRREGULAR_PAST and _IRREGULAR_PAST[word][1] in {"past_participle", "past_or_pp", "any"}:
            return True
        if word.endswith("ed") or word.endswith("en"):
            return True
        return False

    # ------------------------------------------------------------------
    # Role softening per complexity
    # ------------------------------------------------------------------

    @staticmethod
    def _soften_role(role: str, complexity: str) -> str:
        """Map fine-grained roles to the simpler ones used at lower complexity.

        At ``beginner`` the prompt's role list is simple
        (noun/verb/adjective/pronoun/preposition/conjunction/adverb/article/auxiliary);
        we collapse fine-grained roles to those.

        At ``intermediate`` we keep most of the fine-grained vocabulary but
        still soften advanced-only roles.
        """
        if complexity == "beginner":
            beginner_map = {
                "personal_pronoun":        "pronoun",
                "reflexive_pronoun":       "pronoun",
                "demonstrative":           "pronoun",
                "relative_pronoun":        "pronoun",
                "indefinite_pronoun":      "pronoun",
                "interrogative_pronoun":   "pronoun",
                "possessive_pronoun":      "pronoun",
                "possessive_determiner":   "pronoun",
                "subordinating_conjunction": "conjunction",
                "coordinating_conjunction":  "conjunction",
                "modal_verb":              "verb",
                "infinitive_marker":       "particle",
                "infinitive":              "verb",
                "gerund":                  "noun",
                "present_participle":      "verb",
                "past_participle":         "verb",
                "phrasal_verb":            "verb",
                "phrasal_verb_particle":   "particle",
                "comparative":             "adjective",
                "superlative":             "adjective",
                "determiner":              "article",
            }
            return beginner_map.get(role, role)
        if complexity == "intermediate":
            intermediate_map = {
                # Keep most fine-grained roles, but flatten advanced-only ones.
                "relative_pronoun":          "pronoun",
                "interrogative_pronoun":     "pronoun",
                "indefinite_pronoun":        "pronoun",
                "subordinating_conjunction": "conjunction",
                "coordinating_conjunction":  "conjunction",
                "comparative":               "adjective",
                "superlative":               "adjective",
                "phrasal_verb":              "verb",
            }
            return intermediate_map.get(role, role)
        return role
