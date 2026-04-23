# languages/japanese/domain/ja_response_parser.py
"""
Japanese Response Parser - Domain Component

Parses AI responses with 5-level fallback JSON extraction.
Handles Japanese-specific transformations.
"""

import json
import logging
import re
from typing import List, Dict, Any, Optional
from .ja_config import JaConfig
from .ja_fallbacks import JaFallbacks

logger = logging.getLogger(__name__)


class JaResponseParser:
    """Parses AI responses for Japanese grammar analysis."""

    def __init__(self, config: JaConfig, fallbacks: JaFallbacks):
        self.config = config
        self.fallbacks = fallbacks

    def parse_response(self, ai_response: str, complexity: str, sentence: str, target_word: str = None) -> Dict[str, Any]:
        """Parse single response with fallbacks."""
        try:
            json_data = self._extract_json(ai_response)

            if isinstance(json_data, dict) and json_data.get('sentence') == 'error':
                raise ValueError("AI returned error response")

            return self._transform_to_standard_format(json_data, complexity, target_word)
        except Exception as e:
            logger.warning(f"Parsing failed for sentence '{sentence}': {e}")
            return self.fallbacks.create_fallback(sentence, complexity)

    def parse_batch_response(self, ai_response: str, sentences: List[str], complexity: str, target_word: Optional[str] = None) -> List[Dict[str, Any]]:
        """Parse batch response and return list of dicts (exactly what zh_analyzer expects)."""
        logger.info(f"DEBUG: Raw AI batch response: {ai_response[:1000]}")
        try:
            json_data = self._extract_json(ai_response)

            if isinstance(json_data, dict) and json_data.get('sentence') == 'error':
                raise ValueError("AI returned error response")

            # Handle both list and {'batch_results': [...]} formats
            if isinstance(json_data, list):
                batch_results = json_data
            else:
                batch_results = json_data.get('batch_results', json_data.get('results', []))

            if not batch_results:
                raise ValueError("No valid batch results in AI response")

            results = []
            for i, item in enumerate(batch_results):
                if i < len(sentences):
                    try:
                        parsed = self._transform_to_standard_format(item, complexity, target_word)
                        results.append(parsed)
                    except Exception as e:
                        logger.warning(f"Batch item {i} failed: {e}")
                        results.append(self.fallbacks.create_fallback(sentences[i], complexity))

            # Pad if needed
            while len(results) < len(sentences):
                results.append(self.fallbacks.create_fallback(sentences[len(results)], complexity))

            return results

        except Exception as e:
            logger.error(f"Batch parsing failed: {e}")
            return [self.fallbacks.create_fallback(s, complexity) for s in sentences]

    def _extract_json(self, response: str) -> Dict[str, Any]:
        """Extract JSON from AI response using 5-level fallback parsing."""
        # LEVEL 1: Direct JSON parsing
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        # LEVEL 2: Markdown code block (```json ... ```)
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1).strip())
            except json.JSONDecodeError:
                pass

        # LEVEL 3: Generic markdown (``` ... ```)
        if "```" in response:
            try:
                cleaned = response.split("```")[1].split("```")[0].strip()
                return json.loads(cleaned)
            except (json.JSONDecodeError, IndexError):
                pass

        # LEVEL 4: JSON repair
        try:
            repaired = self._clean_json_response(response)
            return json.loads(repaired)
        except json.JSONDecodeError:
            pass

        # LEVEL 5: Extract from text
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                return json.loads(response[json_start:json_end])
        except json.JSONDecodeError:
            pass

        raise ValueError("Unable to extract valid JSON from AI response")

    def _clean_json_response(self, response: str) -> str:
        """Clean common issues in AI-generated JSON."""
        response = response.strip()
        response = re.sub(r'"\s*\n\s*"', '",\n"', response)
        response = re.sub(r'"\s+"', '", "', response)
        response = re.sub(r',(\s*[}\]])', r'\1', response)
        response = re.sub(r'(?<!")(\w+)(?!")\s*:', r'"\1":', response)
        return response

    def _transform_to_standard_format(self, data: Dict[str, Any], complexity: str, target_word: Optional[str] = None) -> Dict[str, Any]:
        """Transform parsed AI data into the exact format expected by zh_analyzer (rich explanations)."""
        words = data.get('words', [])
        word_explanations = []
        colors = self.config.get_color_scheme(complexity)

        for word_data in words:
            word = word_data.get('word', '').strip()
            if not word:
                continue

            raw_role = (word_data.get('grammatical_role') or 
                       word_data.get('role') or 
                       word_data.get('type') or 'other')

            # Target word special handling
            if target_word and word == target_word:
                standard_role = 'target_word'
            else:
                # Use config role hierarchy if available
                role_map = self.config.grammatical_roles.get('role_hierarchy', {})
                standard_role = role_map.get(raw_role, raw_role.lower().replace(" ", "_"))

            # === RICH EXPLANATION (this was missing) ===
            explanation = word_data.get('individual_meaning') or \
                         word_data.get('explanation') or \
                         word_data.get('meaning') or \
                         f"{word} is used in this sentence as a {standard_role.replace('_', ' ')}"

            # If explanation is still too generic, enrich it
            if len(explanation) < 30 and "word that describes" not in explanation.lower():
                explanation = f"{word} ({standard_role}): {explanation}"

            color = colors.get(standard_role, colors.get('other', '#AAAAAA'))

            # Format exactly as analyzer expects: [word, role, color, detailed_explanation]
            word_explanations.append([word, standard_role, color, explanation])

        return {
            'sentence': data.get('sentence', ''),
            'elements': {},  # not used by Chinese
            'explanations': data.get('explanations', {}),
            'word_explanations': word_explanations,
            'grammar_summary': data.get('overall_structure') or data.get('summary', f"Grammar analysis for ZH ({complexity})")
        }

    def _map_role_with_hierarchy(self, role: str) -> str:
        """Map role using hierarchy from config."""
        hierarchy = self.config.grammatical_roles.get('role_hierarchy', {})
        return hierarchy.get(role, role)

    def _build_japanese_explanation(self, word_data: Dict[str, Any], standard_role: str) -> str:
        """Build explanation with Japanese-specific details."""
        individual_meaning = word_data.get('individual_meaning', '')
        if individual_meaning:
            # Append reading info if available
            reading = word_data.get('reading', '')
            if reading and reading != word_data.get('word', ''):
                return f"{individual_meaning} [読み: {reading}]"
            return individual_meaning

        role_descriptions = self.config.grammatical_roles.get('role_descriptions', {})
        return role_descriptions.get(standard_role, f"a {standard_role.replace('_', ' ')}")

    def _get_color_scheme(self, complexity: str) -> Dict[str, str]:
        """Get color scheme based on complexity."""
        return self.config.get_color_scheme(complexity)
