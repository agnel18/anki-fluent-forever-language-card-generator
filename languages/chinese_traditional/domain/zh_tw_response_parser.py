# languages/chinese_traditional/domain/zh_tw_response_parser.py
"""
Response parsing for Chinese Traditional AI analysis results.
Handles parsing and validation of Gemini AI responses for Chinese Traditional grammar analysis.
"""

import json
import re
import logging
from typing import Dict, List, Any, Optional, Tuple

from .zh_tw_config import ZhTwConfig

logger = logging.getLogger(__name__)


class ZhTwResponseParser:
    """
    Parses and validates AI responses for Chinese Traditional grammar analysis.

    Handles:
    - JSON parsing from AI responses
    - Validation of grammatical roles
    - Word order verification
    - Traditional character validation
    - Compound word processing
    """

    def __init__(self, config: ZhTwConfig):
        self.config = config
        self.allowed_roles = set(self.config.grammatical_roles.keys())

    def parse_batch_response(self, ai_response: str, sentences: List[str]) -> Dict[str, Any]:
        """
        Parse batch analysis response from AI.

        Args:
            ai_response: Raw AI response string
            sentences: Original sentences being analyzed

        Returns:
            Parsed and validated analysis results
        """

        try:
            # Extract JSON from response
            json_data = self._extract_json_from_response(ai_response)

            if not json_data or 'batch_results' not in json_data:
                logger.warning("Invalid response format, attempting fallback parsing")
                logger.debug(f"AI Response that failed parsing: {ai_response[:500]}...")  # Log first 500 chars
                json_data = self._fallback_parse(ai_response)

            # Validate and clean the results
            validated_results = self._validate_batch_results(json_data, sentences)

            return {
                'success': True,
                'results': validated_results,
                'metadata': {
                    'parser_version': '1.0',
                    'language': 'zh-tw',
                    'sentences_count': len(sentences)
                }
            }

        except Exception as e:
            logger.error(f"Failed to parse batch response: {e}")
            return {
                'success': False,
                'error': str(e),
                'fallback_results': self._generate_fallback_results(sentences)
            }

    def _extract_json_from_response(self, response: str) -> Optional[Dict[str, Any]]:
        """
        Extract JSON from AI response, handling various formats.

        Args:
            response: AI response string

        Returns:
            Parsed JSON data or None
        """

        # Try direct JSON parsing first
        try:
            return json.loads(response.strip())
        except json.JSONDecodeError:
            pass

        # Look for JSON code blocks
        json_patterns = [
            r'```json\s*(\{.*?\})\s*```',
            r'```\s*(\{.*?\})\s*```',
            r'(\{[^{}]*\{[^{}]*\}[^{}]*\})',  # Nested JSON
            r'(\{[^{}]*\})'  # Simple JSON
        ]

        for pattern in json_patterns:
            matches = re.findall(pattern, response, re.DOTALL)
            for match in matches:
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue

        # Try to find JSON-like content
        start_idx = response.find('{')
        end_idx = response.rfind('}')

        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            try:
                json_str = response[start_idx:end_idx + 1]
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass

        return None

    def _validate_batch_results(self, json_data: Dict[str, Any], sentences: List[str]) -> List[Dict[str, Any]]:
        """
        Validate and clean batch analysis results.

        Args:
            json_data: Parsed JSON data
            sentences: Original sentences

        Returns:
            Validated results
        """

        validated_results = []

        if 'batch_results' not in json_data:
            logger.warning("No batch_results in response")
            return self._generate_fallback_results(sentences)

        for i, result in enumerate(json_data['batch_results']):
            if i >= len(sentences):
                break

            validated_result = self._validate_single_result(result, sentences[i], i + 1)
            validated_results.append(validated_result)

        return validated_results

    def _validate_single_result(self, result: Dict[str, Any], sentence: str, sentence_index: int) -> Dict[str, Any]:
        """
        Validate a single sentence analysis result.

        Args:
            result: Single result from batch
            sentence: Original sentence
            sentence_index: Sentence number

        Returns:
            Validated result
        """

        validated = {
            'sentence_index': sentence_index,
            'original_sentence': sentence,
            'words': [],
            'word_combinations': result.get('word_combinations', []),
            'validation_issues': []
        }

        words = result.get('words', [])
        if not words:
            validated['validation_issues'].append('No words found in analysis')
            return validated

        # Validate each word
        for word_data in words:
            validated_word = self._validate_word(word_data)
            validated['words'].append(validated_word)

        # Additional validations
        self._validate_word_order(validated, sentence)
        self._validate_traditional_characters(validated)

        return validated

    def _validate_word(self, word_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate individual word analysis.

        Args:
            word_data: Word data from AI

        Returns:
            Validated word data
        """

        validated = {
            'word': word_data.get('word', ''),
            'individual_meaning': word_data.get('individual_meaning', ''),
            'grammatical_role': word_data.get('grammatical_role', 'noun'),
            'validation_status': 'valid'
        }

        # Validate grammatical role
        if validated['grammatical_role'] not in self.allowed_roles:
            validated['validation_status'] = 'invalid_role'
            validated['original_role'] = validated['grammatical_role']
            validated['grammatical_role'] = 'noun'  # Default fallback
            validated['validation_notes'] = f"Invalid role '{validated['original_role']}', defaulted to noun"

        # Validate required fields
        if not validated['word'].strip():
            validated['validation_status'] = 'missing_word'

        if not validated['individual_meaning'].strip():
            validated['validation_status'] = 'missing_meaning'

        return validated

    def _validate_word_order(self, result: Dict[str, Any], sentence: str) -> None:
        """
        Validate that words appear in sentence order.

        Args:
            result: Analysis result to validate
            sentence: Original sentence
        """

        # This is a simplified validation - in practice, you'd need
        # more sophisticated word segmentation for Chinese
        words_in_result = [w['word'] for w in result['words']]
        words_concat = ''.join(words_in_result)

        # Check if the concatenation roughly matches the sentence
        # (allowing for some AI interpretation differences)
        if len(words_concat) > len(sentence) * 1.5:
            result['validation_issues'].append('Word concatenation too long - possible over-segmentation')

    def _validate_traditional_characters(self, result: Dict[str, Any]) -> None:
        """
        Validate that analysis uses Traditional Chinese characters.

        Args:
            result: Analysis result to validate
        """

        # Simplified check for Traditional vs Simplified characters
        # This is a basic implementation - a full validator would be more comprehensive
        traditional_indicators = ['臺', '體', '學', '說', '點', '們', '還', '時', '間', '電']
        simplified_indicators = ['台', '体', '学', '说', '点', '们', '还', '时', '间', '电']

        sentence = result.get('original_sentence', '')
        has_traditional = any(char in sentence for char in traditional_indicators)
        has_simplified = any(char in sentence for char in simplified_indicators)

        if has_simplified and not has_traditional:
            result['validation_issues'].append('Sentence appears to use Simplified characters instead of Traditional')

    def _fallback_parse(self, response: str) -> Dict[str, Any]:
        """
        Fallback parsing when JSON extraction fails.

        Args:
            response: AI response string

        Returns:
            Basic parsed structure
        """

        # This would implement more sophisticated fallback parsing
        # For now, return empty structure
        return {'batch_results': []}

    def _generate_fallback_results(self, sentences: List[str]) -> List[Dict[str, Any]]:
        """
        Generate basic fallback results when parsing fails.

        Args:
            sentences: Original sentences

        Returns:
            Basic fallback analysis
        """

        fallback_results = []
        for i, sentence in enumerate(sentences):
            fallback_results.append({
                'sentence_index': i + 1,
                'original_sentence': sentence,
                'words': [{
                    'word': sentence,  # Treat whole sentence as one "word"
                    'individual_meaning': 'Sentence analysis failed - please check manually',
                    'grammatical_role': 'noun',
                    'validation_status': 'fallback'
                }],
                'word_combinations': [],
                'validation_issues': ['AI response parsing failed, using fallback analysis']
            })

        return fallback_results

    def parse_validation_response(self, ai_response: str) -> Dict[str, Any]:
        """
        Parse validation response from AI.

        Args:
            ai_response: Validation response

        Returns:
            Parsed validation results
        """

        try:
            json_data = self._extract_json_from_response(ai_response)
            return json_data if json_data else {'validation_passed': False, 'issues': ['Parse failed']}
        except Exception as e:
            return {'validation_passed': False, 'issues': [str(e)]}