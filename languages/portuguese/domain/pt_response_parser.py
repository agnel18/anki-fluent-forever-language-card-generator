# languages/portuguese/domain/pt_response_parser.py
"""
Portuguese Response Parser — Domain Component

5-level fallback parsing strategy (per CLAUDE.md / French gold standard):
  Level 1: Direct JSON parsing
  Level 2: Markdown code-block extraction (```json ... ```)
  Level 3: JSON repair (truncated / malformed — close open structures)
  Level 4: Text-pattern extraction (word -> role pairs in unstructured text)
  Level 5: Rule-based fallback (delegated to PtFallbacks)

Portuguese-specific normalisation:
  - Reads 'grammatical_role' (canonical) but also accepts legacy 'role' / 'pos'
  - Preserves Portuguese-specific roles (copula, contraction, personal_infinitive,
    mesoclitic, clitic_pronoun, gerund, past_participle, subjunctive_marker)
    WITHOUT collapsing them — grammar_processor.py will pass them through
    with their dedicated colors.
  - Captures meta-fields: copula_type, clitic_position, contraction_parts,
    register, gender, number, person, tense, mood
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional

from .pt_config import PtConfig
from .pt_fallbacks import PtFallbacks

logger = logging.getLogger(__name__)


class PtResponseParser:
    """Parses AI grammar analysis responses for Portuguese."""

    def __init__(self, config: PtConfig, fallbacks: PtFallbacks):
        self.config = config
        self.fallbacks = fallbacks

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def parse_response(
        self,
        ai_response: str,
        complexity: str,
        sentence: str,
        target_word: str = "",
    ) -> Dict[str, Any]:
        """Parse a single-sentence AI response with 5-level fallback."""
        if not ai_response or not ai_response.strip():
            logger.warning("Empty AI response — using rule-based fallback")
            return self.fallbacks.create_fallback(sentence, complexity)

        parsed = self._try_parse(ai_response)
        if parsed is None:
            logger.warning(
                f"All parse levels failed for '{sentence[:40]}...' — using fallback"
            )
            return self.fallbacks.create_fallback(sentence, complexity)

        # Detect AI error sentinel
        if isinstance(parsed, dict) and parsed.get("sentence") == "error":
            logger.warning("AI returned error sentinel — using fallback")
            return self.fallbacks.create_fallback(sentence, complexity)

        # If the result is a list, take the first item (single-sentence path)
        if isinstance(parsed, list):
            parsed = parsed[0] if parsed else {}

        return self._normalize(parsed, sentence, complexity, target_word)

    def parse_batch_response(
        self,
        ai_response: str,
        sentences: List[str],
        complexity: str,
        target_word: str = "",
    ) -> List[Dict[str, Any]]:
        """Parse a batch AI response into per-sentence dicts."""
        if not ai_response or not ai_response.strip():
            logger.warning("Empty batch AI response — using fallbacks")
            return [
                self.fallbacks.create_fallback(s, complexity) for s in sentences
            ]

        parsed = self._try_parse(ai_response)

        # Detect AI error sentinel
        if (
            isinstance(parsed, dict)
            and parsed.get("sentence") == "error"
        ):
            logger.warning("AI returned error sentinel for batch — using fallbacks")
            return [
                self.fallbacks.create_fallback(s, complexity) for s in sentences
            ]

        # Allow multiple JSON shapes:
        #   - top-level list of dicts (Latvian-style)
        #   - dict with 'batch_results' (French-style)
        #   - single dict (single-sentence response)
        if isinstance(parsed, dict):
            batch = parsed.get("batch_results")
            if isinstance(batch, list):
                parsed = batch
            else:
                parsed = [parsed]
        elif not isinstance(parsed, list):
            parsed = None

        if parsed is None:
            logger.warning("Batch parse failed — using fallbacks for all")
            return [
                self.fallbacks.create_fallback(s, complexity) for s in sentences
            ]

        results: List[Dict[str, Any]] = []
        for i, sentence in enumerate(sentences):
            if i < len(parsed):
                try:
                    results.append(
                        self._normalize(parsed[i], sentence, complexity, target_word)
                    )
                except Exception as e:
                    logger.warning(f"Batch item {i} normalisation failed: {e}")
                    results.append(
                        self.fallbacks.create_fallback(sentence, complexity)
                    )
            else:
                results.append(self.fallbacks.create_fallback(sentence, complexity))
        return results

    # ------------------------------------------------------------------
    # 5-level parse cascade
    # ------------------------------------------------------------------

    def _try_parse(self, text: str) -> Optional[Any]:
        """Try all 5 parsing levels in order. Level 5 (rule-based) is the
        caller's responsibility — this function returns None to signal it."""
        for fn in (
            self._parse_direct_json,
            self._parse_markdown_json,
            self._parse_repaired_json,
            self._parse_text_patterns,
        ):
            try:
                result = fn(text)
            except Exception as e:
                logger.debug(f"Parser level {fn.__name__} raised: {e}")
                result = None
            if result is not None:
                logger.debug(f"Parsed AI response via {fn.__name__}")
                return result
        return None

    def _parse_direct_json(self, text: str) -> Optional[Any]:
        """Level 1: Try to parse the entire text as JSON."""
        try:
            return json.loads(text.strip())
        except (json.JSONDecodeError, ValueError):
            return None

    def _parse_markdown_json(self, text: str) -> Optional[Any]:
        """Level 2: Extract JSON from a markdown code block."""
        patterns = [
            r"```json\s*([\s\S]*?)\s*```",
            r"```\s*([\s\S]*?)\s*```",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                candidate = match.group(1).strip()
                try:
                    return json.loads(candidate)
                except (json.JSONDecodeError, ValueError):
                    # Try a cleaned variant
                    try:
                        return json.loads(self._clean_json_response(candidate))
                    except (json.JSONDecodeError, ValueError):
                        continue
        return None

    def _parse_repaired_json(self, text: str) -> Optional[Any]:
        """Level 3: Try to repair truncated/malformed JSON."""
        # Find the first { or [
        start = -1
        for i, ch in enumerate(text):
            if ch in "{[":
                start = i
                break
        if start < 0:
            return None

        candidate = text[start:].strip()

        # First try a basic clean
        try:
            return json.loads(self._clean_json_response(candidate))
        except (json.JSONDecodeError, ValueError):
            pass

        # Try closing truncated structures
        for suffix in ["}", "]", "}]", "}}", "]}", "\"}", "\"]}", "\"}]"]:
            try:
                return json.loads(candidate + suffix)
            except (json.JSONDecodeError, ValueError):
                continue
        return None

    def _parse_text_patterns(self, text: str) -> Optional[Any]:
        """Level 4: Extract word-role pairs from unstructured text."""
        word_explanations: List[Dict[str, Any]] = []
        patterns = [
            r'"([^"\n]+)"\s*[-:>]+\s*(\w+)',
            r"(\w+)\s*[-:>]+\s*(noun|verb|adjective|pronoun|adverb|preposition|conjunction|copula|contraction|clitic_pronoun|gerund|past_participle|personal_infinitive)",
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                for word, role in matches:
                    role_lower = role.lower()
                    color = self.config.get_color_for_role(role_lower)
                    word_explanations.append({
                        "word": word,
                        "grammatical_role": role_lower,
                        "color": color,
                        "meaning": word,
                    })
                if word_explanations:
                    return {
                        "word_explanations": word_explanations,
                        "overall_structure": "parsed via text patterns",
                        "sentence_structure": "parsed via text patterns",
                        "confidence": 0.4,
                    }
        return None

    def _clean_json_response(self, response: str) -> str:
        """Best-effort common AI-JSON repairs."""
        response = response.strip()
        # Strip leading/trailing markdown fences if any survived
        response = re.sub(r"^```(?:json)?\s*", "", response)
        response = re.sub(r"\s*```$", "", response)
        # Fix missing commas between adjacent key-value pairs on new lines
        response = re.sub(r'"\s*\n\s*"', '",\n"', response)
        # Remove trailing commas before } or ]
        response = re.sub(r",(\s*[}\]])", r"\1", response)
        return response.strip()

    # ------------------------------------------------------------------
    # Normalisation — convert AI dict into our standard internal shape
    # ------------------------------------------------------------------

    def _normalize(
        self,
        data: Dict[str, Any],
        sentence: str,
        complexity: str,
        target_word: str = "",
    ) -> Dict[str, Any]:
        """Normalise a parsed dict into a consistent structure."""
        if not isinstance(data, dict):
            return self.fallbacks.create_fallback(sentence, complexity)

        word_items = data.get("word_explanations") or data.get("words") or []
        if not isinstance(word_items, list):
            word_items = []

        normalized_words: List[Dict[str, Any]] = []
        word_explanations_list: List[List[Any]] = []
        elements: Dict[str, List[Dict[str, Any]]] = {}

        for item in word_items:
            if not isinstance(item, dict):
                continue
            word = str(item.get("word", "")).strip()
            if not word:
                continue

            # Read canonical 'grammatical_role' but accept legacy fallbacks
            role = str(
                item.get("grammatical_role")
                or item.get("role")
                or item.get("pos")
                or "other"
            ).strip().lower()

            # PRESERVE Portuguese-specific roles unchanged — do NOT collapse
            # them into generic categories (per CLAUDE.md grammar_processor
            # invariant). The color resolution below honours the role as-is.
            color = (
                item.get("color")
                or self.config.get_color_for_role(role, complexity)
            )

            meaning = str(
                item.get("meaning") or item.get("individual_meaning") or word
            ).strip()

            # Target-word flag — for downstream rendering only
            is_target = bool(target_word and word == target_word)

            normalized = {
                "word": word,
                "grammatical_role": role,
                # Keep legacy alias for downstream code that still reads 'role'
                "role": role,
                "color": color,
                "meaning": meaning,
                "gender": str(item.get("gender", "") or "").strip(),
                "number": str(item.get("number", "") or "").strip(),
                "person": str(item.get("person", "") or "").strip(),
                "tense": str(item.get("tense", "") or "").strip(),
                "mood": str(item.get("mood", "") or "").strip(),
                "copula_type": str(item.get("copula_type", "") or "").strip(),
                "clitic_position": str(item.get("clitic_position", "") or "").strip(),
                "contraction_parts": item.get("contraction_parts") or [],
                "register": str(item.get("register", "") or "").strip(),
                "is_target": is_target,
            }
            normalized_words.append(normalized)
            word_explanations_list.append([word, role, color, meaning])

            elements.setdefault(role, []).append({
                "word": word,
                "grammatical_role": role,
                **{k: normalized[k] for k in (
                    "gender", "number", "person", "tense", "mood",
                    "copula_type", "clitic_position",
                ) if normalized[k]},
            })

        # Overall structure — accept either key, populate both for downstream
        # compat (grammar_processor reads both — see CLAUDE.md).
        overall = (
            data.get("overall_structure")
            or data.get("sentence_structure")
            or "Portuguese sentence"
        )

        explanations = data.get("explanations")
        if not isinstance(explanations, dict):
            explanations = {
                "overall_structure": overall,
                "sentence_structure": overall,
                "key_features": data.get("grammar_notes", "")
                or data.get("key_features", ""),
                "complexity_notes": f"{complexity} level Portuguese analysis",
            }
        else:
            explanations.setdefault("overall_structure", overall)
            explanations.setdefault("sentence_structure", overall)

        return {
            "sentence": data.get("sentence") or sentence,
            "register": str(data.get("register", "") or "").strip(),
            "elements": elements,
            "explanations": explanations,
            "overall_structure": overall,
            "sentence_structure": overall,
            "grammar_notes": data.get("grammar_notes", ""),
            "word_explanations": word_explanations_list,
            "word_details": normalized_words,
            "confidence": float(data.get("confidence", 0.7) or 0.7),
        }
