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

    def parse_response(self, ai_response: str, sentence: str, complexity: str) -> Dict[str, Any]:
        """
        Parse single sentence analysis response from AI.

        Args:
            ai_response: Raw AI response string
            sentence: Original sentence being analyzed
            complexity: Complexity level

        Returns:
            Parsed and validated analysis results
        """
        try:
            # Extract JSON from response
            json_data = self._extract_json_from_response(ai_response)

            if not json_data:
                logger.warning("Invalid response format, using fallback")
                return self._create_fallback(sentence, complexity)

            # Transform to standard format
            result = self._transform_to_standard_format(json_data, complexity)

            # Add metadata
            result['metadata'] = {
                'parser_version': '1.0',
                'language': 'zh-tw',
                'complexity': complexity
            }

            return result

        except Exception as e:
            logger.error(f"Failed to parse response: {e}")
            return self._create_fallback(sentence, complexity)

    def parse_batch_response(self, ai_response: str, sentences: List[str], complexity: str, target_word: str = None) -> List[Dict[str, Any]]:
        """Parse batch response with per-result fallbacks."""
        logger.info(f"DEBUG: Raw AI batch response: {ai_response[:1000]}")
        try:
            json_data = self._extract_json_from_response(ai_response)

            # Check if this looks like an error response
            if isinstance(json_data, dict) and json_data.get('sentence') == 'error':
                raise ValueError("AI returned error response")

            if isinstance(json_data, list):
                batch_results = json_data
            else:
                batch_results = json_data.get('batch_results', [])

            # If no valid batch results, treat as error
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
                        results.append(self._create_fallback(sentences[i], complexity))
                else:
                    results.append(self._create_fallback(sentences[i], complexity))

            # If we don't have results for all sentences, add fallbacks
            while len(results) < len(sentences):
                results.append(self._create_fallback(sentences[len(results)], complexity))

            return results
        except Exception as e:
            logger.error(f"Batch parsing failed: {e}")
            return [self._create_fallback(s, complexity) for s in sentences]
        """Parse single response with fallbacks and explanations extraction."""
        logger.info(f"DEBUG: Raw AI response for sentence '{sentence}': {ai_response[:500]}")
        try:
            json_data = self._extract_json_from_response(ai_response)

            # Check if this looks like an error response
            if isinstance(json_data, dict) and json_data.get('sentence') == 'error':
                raise ValueError("AI returned error response")

            return self._transform_to_standard_format(json_data, complexity, target_word)
        except Exception as e:
            logger.warning(f"Parsing failed for sentence '{sentence}': {e}")
            # Create fallback result with explanations
            fallback_result = self._create_fallback(sentence, complexity)
            return self._transform_to_standard_format(fallback_result, complexity, target_word)
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
            'explanations': result.get('explanations', {}),  # Extract explanations field
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

    def _transform_to_standard_format(self, data: Dict[str, Any], complexity: str, target_word: str = None) -> Dict[str, Any]:
        """Transform parsed data to standard format with explanations extraction."""
        words = data.get('words', [])
        elements = {}
        word_explanations = []
        colors = self._get_color_scheme(complexity)

        for word_data in words:
            word = word_data.get('word', '')
            role = word_data.get('grammatical_role', 'other')
            if target_word and word == target_word:
                role = 'target_word'
            # Map role using config
            standard_role = role  # Keep the role name
            color = self.config.grammatical_roles.get(standard_role, '#AAAAAA')
            explanation = word_data.get('individual_meaning', standard_role)
            
            # Use word meanings dictionary if explanation is generic
            if self._is_generic_explanation(explanation):
                dict_meaning = self.config.word_meanings.get(word, '')
                if dict_meaning:
                    explanation = dict_meaning
                else:
                    # Fallback to role-based explanation
                    explanation = f"{word} ({standard_role})"
            
            word_explanations.append([word, standard_role, color, explanation])

            if standard_role not in elements:
                elements[standard_role] = []
            elements[standard_role].append(word_data)

        explanations = data.get('explanations', {})
        
        # Generate overall_structure and key_features if missing
        if not explanations.get('overall_structure'):
            roles = [exp[1] for exp in word_explanations if len(exp) > 1]
            role_counts = {}
            for role in roles:
                role_counts[role] = role_counts.get(role, 0) + 1
            overall = f"Sentence with {', '.join([f'{count} {role}' + ('s' if count > 1 else '') for role, count in role_counts.items()])}"
            explanations['overall_structure'] = overall
            explanations['key_features'] = f"Demonstrates {len(set(roles))} grammatical categories"

        return {
            'sentence': data.get('sentence', ''),
            'elements': elements,
            'explanations': explanations,  # Extract explanations field
            'word_explanations': word_explanations
        }

    def _is_generic_explanation(self, explanation: str) -> bool:
        """Check if an explanation is generic and should be replaced with dictionary meaning."""
        generic_patterns = [
            "a word that describes a noun",
            "a word that describes a verb", 
            "a word that describes an adjective",
            "a particle",
            "an interjection",
            "other",
            "noun in zh-tw grammar",
            "verb in zh-tw grammar",
            "adjective in zh-tw grammar"
        ]
        return any(pattern in explanation.lower() for pattern in generic_patterns)

    def _create_fallback(self, sentence: str, complexity: str) -> Dict[str, Any]:
        """Create fallback analysis result."""
        return {
            'sentence': sentence,
            'words': [{
                'word': sentence,
                'individual_meaning': 'Fallback analysis - sentence parsing failed',
                'grammatical_role': 'noun'
            }],
            'explanations': {
                'overall_structure': 'Fallback analysis due to parsing error',
                'key_features': 'Unable to analyze sentence structure'
            }
        }
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