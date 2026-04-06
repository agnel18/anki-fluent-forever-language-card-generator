# languages/korean/domain/ko_response_parser.py
"""
Korean Response Parser - Domain Component

Parses AI responses with 5-level fallback JSON extraction.
Handles Korean-specific transformations.
"""

import json
import logging
import re
from typing import List, Dict, Any
from .ko_config import KoConfig

logger = logging.getLogger(__name__)


class KoResponseParser:
    """Parses AI responses for Korean grammar analysis."""

    def __init__(self, config: KoConfig, fallbacks):
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

    def parse_batch_response(self, ai_response: str, sentences: List[str], complexity: str, target_word: str = None) -> List[Dict[str, Any]]:
        """Parse batch response with per-result fallbacks."""
        try:
            json_data = self._extract_json(ai_response)

            if isinstance(json_data, dict) and json_data.get('sentence') == 'error':
                raise ValueError("AI returned error response")

            if isinstance(json_data, list):
                batch_results = json_data
            else:
                batch_results = json_data.get('batch_results', [])

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

    def _transform_to_standard_format(self, data: Dict[str, Any], complexity: str, target_word: str = None) -> Dict[str, Any]:
        """Transform parsed data to standard format with Korean-specific processing."""
        words = data.get('words', [])
        elements = {}
        word_explanations = []
        colors = self._get_color_scheme(complexity)

        for word_data in words:
            word = word_data.get('word', '')
            role = word_data.get('grammatical_role', 'other')

            if target_word and word == target_word:
                role = 'target_word'

            standard_role = self._map_role_with_hierarchy(role)
            color = colors.get(standard_role, '#AAAAAA')
            explanation = self._build_korean_explanation(word_data, standard_role)

            word_explanations.append([word, standard_role, color, explanation])

            if standard_role not in elements:
                elements[standard_role] = []
            elements[standard_role].append(word_data)

        return {
            'sentence': data.get('sentence', ''),
            'elements': elements,
            'explanations': data.get('explanations', {}),
            'word_explanations': word_explanations
        }

    def _map_role_with_hierarchy(self, role: str) -> str:
        """Map role using hierarchy from config."""
        hierarchy = self.config.grammatical_roles.get('role_hierarchy', {})
        return hierarchy.get(role, role)

    def _build_korean_explanation(self, word_data: Dict[str, Any], standard_role: str) -> str:
        """Build explanation with Korean-specific details."""
        individual_meaning = word_data.get('individual_meaning', '')
        if individual_meaning:
            # Append speech level info if available
            speech_level = word_data.get('speech_level')
            honorific = word_data.get('honorific')
            extras = []
            if speech_level and speech_level != 'null':
                extras.append(f"speech level: {speech_level}")
            if honorific and honorific not in ('null', 'false', False):
                extras.append("honorific")
            if extras:
                return f"{individual_meaning} [{', '.join(extras)}]"
            return individual_meaning

        role_descriptions = self.config.grammatical_roles.get('role_descriptions', {})
        return role_descriptions.get(standard_role, f"a {standard_role.replace('_', ' ')}")

    def _get_color_scheme(self, complexity: str) -> Dict[str, str]:
        """Get color scheme based on complexity."""
        return self.config.get_color_scheme(complexity)
