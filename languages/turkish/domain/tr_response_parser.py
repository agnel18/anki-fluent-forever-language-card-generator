# languages/turkish/domain/tr_response_parser.py
"""
Turkish Response Parser - Domain Component

TURKISH RESPONSE PARSING:
This component handles parsing AI responses for Turkish grammar analysis.
It validates JSON structure and extracts grammatical information.

RESPONSIBILITIES:
1. Parse JSON responses from AI analysis
2. Validate response structure and content
3. Extract word-level grammatical information
4. Handle parsing errors gracefully
5. Provide validation feedback

TURKISH-SPECIFIC VALIDATION:
- Morphological structure validation
- Vowel harmony checking
- Case marker identification
- Agglutination analysis
- Turkish grammatical category validation

USAGE FOR TURKISH:
1. Parse AI responses into structured format
2. Validate Turkish-specific grammatical features
3. Extract morphological decomposition
4. Check vowel harmony compliance
5. Identify case system usage

INTEGRATION:
- Called by main analyzer after AI response
- Receives configuration from TrConfig
- Returns structured analysis results
- Error handling prevents crashes from malformed responses
"""

import json
import re
import logging
from typing import Dict, List, Any, Optional
from .tr_config import TrConfig
from .tr_fallbacks import TrFallbacks

logger = logging.getLogger(__name__)


class TurkishAnalysisResult(Dict[str, Any]):
    """Represents a single word's analysis result."""
    pass


class TrResponseParser:
    """
    Parses and validates Turkish language analysis responses.

    TURKISH PARSING FEATURES:
    - JSON extraction from various response formats
    - Morphological validation for agglutination
    - Vowel harmony verification
    - Case system identification
    - Turkish grammatical category validation
    """

    def __init__(self, config: TrConfig):
        """
        Initialize response parser with configuration.

        TURKISH CONFIGURATION INTEGRATION:
        - Access to grammatical roles and categories
        - Morphological features for validation
        - Color schemes for visualization
        """
        self.config = config
        self.fallbacks = TrFallbacks(config)

    def parse_response(self, response: str, complexity: str, sentence: str, target_word: str) -> Dict[str, Any]:
        """
        Parse AI response into structured Turkish analysis.

        TURKISH PARSING PROCESS:
        1. Extract JSON from response text
        2. Validate required structure
        3. Parse individual word analyses
        4. Validate Turkish-specific features
        5. Return structured result or error
        """
        try:
            json_data = self._extract_json(response)
            if not json_data:
                raise ValueError("No valid JSON found in response")

            if isinstance(json_data, dict) and 'batch_results' in json_data:
                batch_results = json_data.get('batch_results', [])
                if not batch_results:
                    raise ValueError("Empty batch_results in response")
                json_data = batch_results[0]

            return self._parse_batch_item(json_data, sentence, complexity, target_word)
        except Exception as e:
            logger.error(f"Failed to parse response: {e}")
            return self.fallbacks.create_fallback(sentence, complexity)

    def parse_batch_response(self, ai_response: str, sentences: List[str], complexity: str, target_word: str = None) -> List[Dict[str, Any]]:
        """
        Parse batch response with per-result fallbacks.

        TURKISH BATCH PROCESSING:
        - Handles multiple Turkish sentences efficiently
        - Applies per-sentence validation and fallbacks
        - Returns consistent results for all input sentences
        """
        try:
            json_data = self._extract_json(ai_response)
            if not json_data:
                raise ValueError("No valid JSON found in batch response")

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
                        results.append(self._parse_batch_item(item, sentences[i], complexity, target_word))
                    except Exception as e:
                        logger.warning(f"Batch item {i} failed: {e}")
                        results.append(self.fallbacks.create_fallback(sentences[i], complexity))
                else:
                    results.append(self.fallbacks.create_fallback(sentences[i], complexity))

            while len(results) < len(sentences):
                results.append(self.fallbacks.create_fallback(sentences[len(results)], complexity))

            return results
        except Exception as e:
            logger.error(f"Batch parsing failed: {e}")
            return [self.fallbacks.create_fallback(s, complexity) for s in sentences]

    def _parse_batch_item(self, item: Dict[str, Any], sentence: str, complexity: str, target_word: str = None) -> Dict[str, Any]:
        """Parse a single batch item into standard Turkish analysis format."""
        if 'analysis' not in item and 'words' not in item:
            raise ValueError("Batch item missing analysis data")

        words_data = item.get('analysis') or item.get('words', [])
        if not isinstance(words_data, list):
            raise ValueError("Batch item analysis must be a list")
        if not words_data:
            raise ValueError("Batch item contains no word analyses")

        word_explanations = []
        elements = {}

        for word_data in words_data:
            enhanced_word = self._enhance_word_analysis(word_data, complexity)
            word = enhanced_word.get('word', '')
            role = enhanced_word.get('grammatical_role') or enhanced_word.get('role') or 'other'
            role = self._normalize_role(role)
            if target_word and word == target_word:
                role = 'target_word'
            role = self._map_role(role)
            meaning = enhanced_word.get('individual_meaning') or enhanced_word.get('meaning') or role
            color = enhanced_word.get('color') or self._get_color_for_role(role, complexity)

            word_explanations.append([word, role, color, meaning])

            if role not in elements:
                elements[role] = []
            elements[role].append(enhanced_word)

        return {
            'word_explanations': word_explanations,
            'elements': elements,
            'explanations': item.get('explanations', {}),
            'confidence': item.get('confidence', 0.8),
            'sentence': sentence,
            'target_word': target_word,
            'is_fallback': False
        }

    def _normalize_role(self, role: str) -> str:
        """Normalize role names to a consistent format."""
        if not role:
            return 'other'
        return role.strip().lower().replace(' ', '_')

    def _map_role(self, role: str) -> str:
        """Map role to standardized role set from configuration."""
        if role == 'target_word':
            return role
        return self.config.grammatical_roles.get(role, role)

    def _extract_json(self, response: str) -> Optional[Dict[str, Any]]:
        """
        Extract JSON from AI response, handling various formats.

        TURKISH RESPONSE FORMATS:
        - Direct JSON object
        - JSON code blocks (```json)
        - JSON within text markers
        """
        # Try direct JSON parsing
        try:
            return json.loads(response.strip())
        except json.JSONDecodeError:
            pass

        # Look for JSON code blocks
        json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        match = re.search(json_pattern, response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        # Look for JSON between curly braces (last resort)
        brace_pattern = r'\{.*\}'
        match = re.search(brace_pattern, response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

        return None


    def _enhance_word_analysis(self, word_data: Dict[str, Any], complexity: str) -> Dict[str, Any]:
        """
        Enhance individual word analysis with Turkish-specific features.

        TURKISH WORD ENHANCEMENT:
        - Assign colors based on grammatical role
        - Add morphological validation
        - Include Turkish-specific metadata
        """
        enhanced = dict(word_data)

        # Assign color based on grammatical role unless already provided
        role = word_data.get('grammatical_role') or word_data.get('role', '')
        if 'color' in word_data and word_data['color']:
            enhanced['color'] = word_data['color']
        else:
            enhanced['color'] = self._get_color_for_role(role, complexity)

        # Add morphological validation if morphology present
        if 'morphology' in word_data:
            enhanced['morphology_validation'] = self._validate_morphology(word_data['morphology'])

        # Add Turkish-specific validation
        enhanced['turkish_validation'] = self._validate_turkish_features(word_data)

        return enhanced

    def _get_color_for_role(self, role: str, complexity: str) -> str:
        """Get color for grammatical role."""
        color_scheme = self.config.get_color_scheme(complexity)
        return color_scheme.get(role, color_scheme.get('other', '#808080'))

    def _validate_morphology(self, morphology: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate morphological analysis for Turkish features.

        TURKISH MORPHOLOGICAL VALIDATION:
        - Root identification
        - Suffix sequence validation
        - Vowel harmony checking
        - Case marker recognition
        """
        validation = {
            'has_root': 'root' in morphology,
            'has_suffixes': 'suffixes' in morphology,
            'vowel_harmony_valid': True,
            'case_markers_valid': True
        }

        # Check vowel harmony if both root and suffixes present
        if validation['has_root'] and validation['has_suffixes']:
            validation['vowel_harmony_valid'] = self._check_vowel_harmony(
                morphology['root'], morphology['suffixes']
            )

        # Check case markers
        if 'case' in morphology:
            validation['case_markers_valid'] = self._validate_case_marker(morphology['case'])

        return validation

    def _check_vowel_harmony(self, root: str, suffixes: List[str]) -> bool:
        """
        Check vowel harmony between root and suffixes.

        TURKISH VOWEL HARMONY RULES:
        - Back vowels: a, o, u
        - Front vowels: e, ö, ü
        - Suffixes must harmonize with root's last vowel
        """
        if not root or not suffixes:
            return True

        # Get last vowel of root
        root_vowel = self._get_last_vowel(root)
        if not root_vowel:
            return True

        # Check harmony for each suffix
        for suffix in suffixes:
            suffix_vowel = self._get_first_vowel(suffix)
            if suffix_vowel and not self._harmonizes(root_vowel, suffix_vowel):
                return False

        return True

    def _get_last_vowel(self, word: str) -> Optional[str]:
        """Get last vowel in word."""
        vowels = set('aeıioöuü')
        for char in reversed(word.lower()):
            if char in vowels:
                return char
        return None

    def _get_first_vowel(self, word: str) -> Optional[str]:
        """Get first vowel in word."""
        vowels = set('aeıioöuü')
        for char in word.lower():
            if char in vowels:
                return char
        return None

    def _harmonizes(self, root_vowel: str, suffix_vowel: str) -> bool:
        """Check if two vowels harmonize."""
        back_vowels = set('aou')
        front_vowels = set('eıöü')

        root_is_back = root_vowel in back_vowels
        suffix_is_back = suffix_vowel in back_vowels

        return root_is_back == suffix_is_back

    def _validate_case_marker(self, case: str) -> bool:
        """Validate case marker."""
        valid_cases = {'nominative', 'accusative', 'dative', 'locative', 'ablative', 'genitive'}
        return case.lower() in valid_cases

    def _validate_turkish_features(self, word_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate Turkish-specific features in word analysis.

        TURKISH FEATURE VALIDATION:
        - Grammatical role validity
        - Morphological completeness
        - Linguistic feature recognition
        """
        validation = {}

        # Check grammatical role
        role = word_data.get('grammatical_role') or word_data.get('role', '')
        validation['role_valid'] = role in self.config.grammatical_roles

        # Check for Turkish-specific features
        validation['has_morphology'] = 'morphology' in word_data
        validation['has_case_info'] = 'case' in word_data or 'morphology' in word_data

        return validation
