# languages/russian/domain/ru_validator.py
"""
Russian Validator — Domain Component

Validates grammar analysis results and returns a confidence score (0.0-1.0).
Target: ≥ 0.85 for production deployment.

Russian-specific quality gates:
  - Coverage of sentence tokens
  - Role validity (must come from the Russian role vocabulary)
  - Completeness (word + meaning + color populated)
  - Russian-feature presence (case/gender/number on nominals; aspect/tense
    on verbs; English OR Russian terms accepted — e.g. "genitive" or
    "родительный")
  - Stub detection (≥20-char body, body != word)
  - is_fallback short-circuit: fallback path is capped at confidence 0.3

Validators NEVER artificially boost — natural scoring only (CLAUDE.md).
"""

import logging
from typing import Any, Dict, List

from .ru_config import RuConfig

logger = logging.getLogger(__name__)


# Roles that MUST be present for a minimal valid analysis
_REQUIRED_ROLES = {"noun", "verb"}

# Valid Russian grammatical roles (superset across all complexity levels)
_VALID_ROLES = {
    # Open-class
    "noun", "verb", "imperfective_verb", "perfective_verb",
    "infinitive", "imperative", "modal_verb", "auxiliary", "copula",
    "reflexive_verb",
    "adjective", "short_adjective", "comparative", "superlative",
    "adverb",
    # Pronouns
    "pronoun", "personal_pronoun", "possessive_pronoun",
    "possessive_determiner", "reflexive_pronoun", "demonstrative",
    "relative_pronoun", "interrogative_pronoun", "indefinite_pronoun",
    "negative_pronoun",
    # Closed-class
    "preposition", "conjunction", "coordinating_conjunction",
    "subordinating_conjunction",
    "particle", "aspectual_particle", "conditional_particle",
    "negation_particle",
    "numeral", "interjection",
    # Verbal forms
    "participle", "present_active_participle", "past_active_participle",
    "present_passive_participle", "past_passive_participle",
    "gerund", "verbal_noun",
    "other",
}

_VALID_CASES = {
    "nominative", "genitive", "dative",
    "accusative", "instrumental", "prepositional", "locative", "",
}

_VALID_GENDERS = {"masculine", "feminine", "neuter", "common", ""}

# Russian feature vocabulary — accepted in either English or Russian.
# Validator checks `individual_meaning` (or fallback `meaning` body) for at
# least one of these terms on inflected words.
_RUSSIAN_FEATURE_KEYWORDS = [
    # Cases — English + Russian
    "case", "nominative", "именительный",
    "genitive", "родительный",
    "dative", "дательный",
    "accusative", "винительный",
    "instrumental", "творительный",
    "prepositional", "предложный", "locative",
    # Gender — English + Russian
    "gender", "masculine", "мужской",
    "feminine", "женский",
    "neuter", "средний",
    # Number
    "singular", "plural",
    # Animacy
    "animate", "inanimate",
    # Aspect — English + Russian
    "aspect", "imperfective", "несовершенный",
    "perfective", "совершенный",
    # Tense / person / mood
    "tense", "present", "past", "future",
    "person", "1st", "2nd", "3rd",
    "mood", "imperative", "conditional", "indicative",
    # Agreement / syntactic relations
    "agree", "agrees", "agreement", "governs",
    "subject", "object", "direct object", "indirect object",
    "predicate",
    # Lexical
    "lemma", "conjugation", "declension",
    # Russian-specific
    "reflexive", "reciprocal",
    "motion", "determinate", "indeterminate",
]


class RuValidator:
    """Validates Russian grammar analysis results."""

    def __init__(self, config: RuConfig):
        self.config = config

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def validate_result(
        self, result: Dict[str, Any], sentence: str
    ) -> Dict[str, Any]:
        """Validate and enrich the analysis result.

        Returns the result dict with a 'confidence' key set. If the result
        carries `is_fallback: True`, confidence is short-circuited to 0.3
        per CLAUDE.md fallback contract.
        """
        if not result or not isinstance(result, dict):
            return {"confidence": 0.0, "word_explanations": []}

        # Fallback short-circuit — never blesses fallback output above 0.3.
        if result.get("is_fallback") is True:
            result["confidence"] = 0.3
            return result

        confidence = self._calculate_confidence(result, sentence)
        result["confidence"] = confidence
        return result

    def validate_analysis(
        self, parsed_data: Dict[str, Any], original_sentence: str
    ) -> float:
        """Return confidence score for abstract method compliance."""
        result = self.validate_result(parsed_data, original_sentence)
        return result.get("confidence", 0.0)

    # ------------------------------------------------------------------
    # Confidence calculation
    # ------------------------------------------------------------------

    def _calculate_confidence(
        self, result: Dict[str, Any], sentence: str
    ) -> float:
        """Multi-dimensional confidence scoring."""
        scores: List[float] = []

        word_explanations = result.get("word_explanations", [])

        # 1. Coverage score: were all words accounted for?
        scores.append(self._score_coverage(word_explanations, sentence))

        # 2. Role validity: are roles from the valid set?
        scores.append(self._score_role_validity(word_explanations))

        # 3. Completeness: do explanations have required fields?
        scores.append(self._score_completeness(word_explanations))

        # 4. Russian-specific: case / gender / aspect presence where applicable
        scores.append(self._score_russian_features(word_explanations))

        # 5. Structure description present?
        has_structure = bool(
            result.get("overall_structure") or result.get("sentence_structure")
        )
        scores.append(0.9 if has_structure else 0.5)

        if not scores:
            return 0.5
        confidence = sum(scores) / len(scores)
        return round(min(max(confidence, 0.0), 1.0), 3)

    def _score_coverage(
        self, word_explanations: List[Dict], sentence: str
    ) -> float:
        """How well do the word_explanations cover the sentence tokens?"""
        if not word_explanations:
            return 0.2
        sentence_tokens = [
            w.strip(".,!?;:\"'()[]«»…—-") for w in sentence.split() if w.strip()
        ]
        explained_words = {
            item.get("word", "").strip(".,!?;:\"'()[]«»…—-").lower()
            for item in word_explanations
            if isinstance(item, dict)
        }
        if not sentence_tokens:
            return 0.5
        covered = sum(1 for t in sentence_tokens if t.lower() in explained_words)
        ratio = covered / len(sentence_tokens)
        if ratio >= 0.9:
            return 0.95
        elif ratio >= 0.7:
            return 0.75
        elif ratio >= 0.5:
            return 0.55
        return 0.3

    def _score_role_validity(self, word_explanations: List[Dict]) -> float:
        """What fraction of roles are from the valid role set?"""
        if not word_explanations:
            return 0.3
        valid_count = sum(
            1 for item in word_explanations
            if isinstance(item, dict) and item.get("role", "").lower() in _VALID_ROLES
        )
        ratio = valid_count / len(word_explanations)
        return 0.9 if ratio >= 0.9 else (0.7 if ratio >= 0.7 else 0.5)

    def _score_completeness(self, word_explanations: List[Dict]) -> float:
        """Are word, meaning, and color fields populated?"""
        if not word_explanations:
            return 0.3
        complete = sum(
            1 for item in word_explanations
            if isinstance(item, dict)
            and item.get("word")
            and item.get("meaning")
            and item.get("color")
        )
        ratio = complete / len(word_explanations)
        return 0.9 if ratio >= 0.9 else (0.7 if ratio >= 0.7 else 0.5)

    def _score_russian_features(self, word_explanations: List[Dict]) -> float:
        """Do nominal entries carry case/gender; do verb entries carry aspect?"""
        nominals = [
            item for item in word_explanations
            if isinstance(item, dict)
            and item.get("role", "") in {
                "noun", "adjective", "short_adjective", "pronoun",
                "personal_pronoun", "possessive_pronoun",
                "possessive_determiner", "demonstrative",
                "reflexive_pronoun", "relative_pronoun",
                "interrogative_pronoun", "indefinite_pronoun",
                "negative_pronoun", "numeral", "participle",
                "present_active_participle", "past_active_participle",
                "present_passive_participle", "past_passive_participle",
                "verbal_noun",
            }
        ]
        verbs = [
            item for item in word_explanations
            if isinstance(item, dict)
            and item.get("role", "") in {
                "verb", "imperfective_verb", "perfective_verb",
                "reflexive_verb", "modal_verb", "auxiliary",
                "infinitive", "imperative",
            }
        ]
        if not nominals and not verbs:
            return 0.85  # No relevant tokens — not penalised

        with_nominal_features = sum(
            1 for item in nominals if item.get("case", "").strip()
        )
        with_verb_features = sum(
            1 for item in verbs
            if item.get("aspect", "").strip() or item.get("tense", "").strip()
        )

        nom_ratio = with_nominal_features / len(nominals) if nominals else 1.0
        verb_ratio = with_verb_features / len(verbs) if verbs else 1.0
        avg_ratio = (nom_ratio + verb_ratio) / 2

        return 0.9 if avg_ratio >= 0.7 else (0.7 if avg_ratio >= 0.4 else 0.5)

    # ------------------------------------------------------------------
    # Quality / explanation depth report
    # ------------------------------------------------------------------

    def validate_explanation_quality(
        self, result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check explanation quality and return a quality report.

        Mirrors lv_validator.validate_explanation_quality — penalises shallow
        stubs and Russian-feature-poor explanations so confidence drops below
        the deployment threshold whenever the analyzer ships nonsense.

        Penalty structure (multiplicative onto a 1.0 base):
          - Missing meaning / color: -0.1 per issue
          - Invalid role: -0.05 per issue
          - "Stub" explanation (body < 20 chars OR body equals word): -0.2 each
          - Inflected word missing Russian-feature keywords: -0.05 each
        """
        word_explanations = result.get("word_explanations", [])
        issues: List[str] = []
        stub_count = 0
        feature_gap_count = 0

        inflected_roles = {
            "noun", "adjective", "short_adjective", "pronoun",
            "personal_pronoun", "possessive_pronoun",
            "possessive_determiner", "demonstrative",
            "reflexive_pronoun", "relative_pronoun",
            "interrogative_pronoun", "indefinite_pronoun",
            "negative_pronoun", "numeral",
            "verb", "imperfective_verb", "perfective_verb",
            "reflexive_verb", "modal_verb", "auxiliary", "infinitive",
            "imperative",
            "participle", "present_active_participle",
            "past_active_participle", "present_passive_participle",
            "past_passive_participle", "gerund", "verbal_noun",
        }

        for item in word_explanations:
            if not isinstance(item, dict):
                continue
            word = item.get("word", "?")
            role = item.get("role", "")
            meaning = (item.get("meaning") or "").strip()
            individual = (item.get("individual_meaning") or "").strip()

            if not meaning:
                issues.append(f"Missing meaning for '{word}'")
                continue
            if not item.get("color"):
                issues.append(f"Missing color for '{word}'")
            if role not in _VALID_ROLES:
                issues.append(f"Invalid role '{role}' for '{word}'")

            # Stub detection — strip "{word} ({role}):" prefix, then check
            # whether the residual body is meaningfully different from the
            # word itself and at least 20 chars long.
            stripped_prefix = f"{word} ({role}):".strip()
            body = (
                meaning[len(stripped_prefix):].strip()
                if meaning.startswith(stripped_prefix)
                else meaning
            )
            if len(body) < 20 or body.lower() == word.lower():
                stub_count += 1
                issues.append(
                    f"Stub explanation for '{word}' (body too short or empty)"
                )
                continue

            # Inflected-word feature check.
            if role in inflected_roles:
                explanation_text = (individual or body).lower()
                if not any(
                    kw in explanation_text for kw in _RUSSIAN_FEATURE_KEYWORDS
                ):
                    feature_gap_count += 1
                    issues.append(
                        f"Inflected word '{word}' ({role}) — explanation lacks "
                        f"case/gender/aspect/agreement detail"
                    )

        # Quality score combines all penalty types.
        score = 1.0
        score -= 0.1 * sum(1 for i in issues if i.startswith("Missing"))
        score -= 0.05 * sum(1 for i in issues if i.startswith("Invalid"))
        score -= 0.2 * stub_count
        score -= 0.05 * feature_gap_count
        quality_score = max(0.0, min(score, 1.0))

        return {
            "issues": issues,
            "quality_score": quality_score,
            "stub_count": stub_count,
            "feature_gap_count": feature_gap_count,
        }

    # ------------------------------------------------------------------
    # Helpers retained for stub-method compatibility
    # ------------------------------------------------------------------

    def _validate_word_explanations(self, word_explanations: list) -> bool:
        """Return True if there is at least one well-formed explanation."""
        if not word_explanations:
            return False
        for item in word_explanations:
            if not isinstance(item, dict):
                continue
            if (
                item.get("word")
                and item.get("role", "").lower() in _VALID_ROLES
                and item.get("meaning")
            ):
                return True
        return False
