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
            # Extract JSON from response
            json_data = self._extract_json(response)
            if not json_data:
                raise ValueError("No valid JSON found in response")

            # Validate basic structure
            self._validate_structure(json_data)

            # Parse and validate word analyses
            parsed_analysis = self._parse_analysis(json_data, complexity)

            # Add validation summary
            parsed_analysis['validation_summary'] = self._create_validation_summary(parsed_analysis)

            logger.debug(f"Successfully parsed response with {len(parsed_analysis.get('analysis', []))} words")
            return parsed_analysis

        except Exception as e:
            logger.error(f"Failed to parse response: {e}")
            return self._create_error_response(response, str(e))

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

    def _validate_structure(self, json_data: Dict[str, Any]) -> None:
        """
        Validate that JSON has required structure for Turkish analysis.

        TURKISH REQUIRED STRUCTURE:
        - analysis: array of word analyses
        - sentence_structure: string description
        - linguistic_features: array of features
        - validation: validation results
        """
        required_keys = ['analysis', 'sentence_structure', 'linguistic_features', 'validation']
        for key in required_keys:
            if key not in json_data:
                raise ValueError(f"Missing required key: {key}")

        if not isinstance(json_data['analysis'], list):
            raise ValueError("Analysis must be a list")

        # Validate each word has required fields
        for i, word_data in enumerate(json_data['analysis']):
            required_word_keys = ['word', 'grammatical_role', 'individual_meaning']
            for key in required_word_keys:
                if key not in word_data:
                    raise ValueError(f"Word {i}: Missing required key {key}")

    def _parse_analysis(self, json_data: Dict[str, Any], complexity: str) -> Dict[str, Any]:
        """
        Parse and enhance analysis with Turkish-specific validation.

        TURKISH ENHANCEMENT FEATURES:
        - Morphological decomposition validation
        - Vowel harmony checking
        - Case marker identification
        - Color assignment based on grammatical role
        """
        analysis = []

        for word_data in json_data['analysis']:
            enhanced_word = self._enhance_word_analysis(word_data, complexity)
            analysis.append(enhanced_word)

        return {
            'analysis': analysis,
            'sentence_structure': json_data.get('sentence_structure', ''),
            'linguistic_features': json_data.get('linguistic_features', []),
            'validation': json_data.get('validation', {}),
            'raw_response': json_data
        }

    def _enhance_word_analysis(self, word_data: Dict[str, Any], complexity: str) -> Dict[str, Any]:
        """
        Enhance individual word analysis with Turkish-specific features.

        TURKISH WORD ENHANCEMENT:
        - Assign colors based on grammatical role
        - Add morphological validation
        - Include Turkish-specific metadata
        """
        enhanced = dict(word_data)

        # Assign color based on grammatical role
        role = word_data.get('grammatical_role', '')
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
        role = word_data.get('grammatical_role', '')
        validation['role_valid'] = role in self.config.grammatical_roles

        # Check for Turkish-specific features
        validation['has_morphology'] = 'morphology' in word_data
        validation['has_case_info'] = 'case' in word_data or 'morphology' in word_data

        return validation

    def _create_validation_summary(self, parsed_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create summary of validation results."""
        analysis = parsed_analysis.get('analysis', [])
        if not analysis:
            return {'valid': False, 'reason': 'no_analysis_results'}

        total_words = len(analysis)
        valid_roles = sum(1 for word in analysis if word.get('turkish_validation', {}).get('role_valid', False))
        valid_morphology = sum(1 for word in analysis if word.get('morphology_validation', {}).get('has_root', False))

        return {
            'total_words': total_words,
            'valid_roles_ratio': valid_roles / total_words,
            'valid_morphology_ratio': valid_morphology / total_words,
            'overall_valid': valid_roles == total_words
        }

    def _create_error_response(self, response: str, error: str) -> Dict[str, Any]:
        """Create error response when parsing fails."""
        return {
            'analysis': [],
            'sentence_structure': 'Error parsing response',
            'linguistic_features': [],
            'validation': {'parsing_error': error},
            'validation_summary': {'valid': False, 'reason': error},
            'raw_response': response
        }
        return {
            'morphology': {
                'max_suffixes': self.config.morphological_features['agglutination']['max_suffixes'],
                'require_root': True,
                'require_suffixes': True,
            },
            'vowel_harmony': {
                'enabled': self.config.morphological_features['vowel_harmony']['enabled'],
                'back_vowels': set(self.config.morphological_features['vowel_harmony']['back_vowels']),
                'front_vowels': set(self.config.morphological_features['vowel_harmony']['front_vowels']),
            },
            'cases': {
                'markers': self._get_all_case_markers(),
                'functions': self._get_case_functions(),
            },
            'categories': {
                level: set(categories)
                for level, categories in self.config.grammatical_categories.items()
            }
        }

    def _get_all_case_markers(self) -> Dict[str, List[str]]:
        """Get all case markers from config."""
        markers = {}
        for case_name, case_info in self.config.morphological_features['cases'].items():
            case_markers = case_info.get('markers', [])
            if isinstance(case_markers, str):
                case_markers = [case_markers]
            markers[case_name] = case_markers
        return markers

    def _get_case_functions(self) -> Dict[str, str]:
        """Get case functions mapping."""
        return {
            case_name: case_info.get('function', case_name)
            for case_name, case_info in self.config.morphological_features['cases'].items()
        }

    def _extract_json(self, response: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from AI response, handling various formats."""

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

        # Look for JSON between curly braces
        brace_pattern = r'\{.*\}'
        match = re.search(brace_pattern, response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

        return None

    def _validate_json_structure(self, json_data: Dict[str, Any], complexity: str) -> None:
        """Validate that JSON has required structure."""

        required_keys = ['analysis', 'sentence_structure', 'linguistic_features', 'validation']
        for key in required_keys:
            if key not in json_data:
                raise ValueError(f"Missing required key: {key}")

        # Validate analysis array
        if not isinstance(json_data['analysis'], list):
            raise ValueError("Analysis must be a list")

        # Validate each word analysis
        for i, word_data in enumerate(json_data['analysis']):
            required_word_keys = ['word', 'morphology', 'category', 'role', 'color', 'complexity']
            for key in required_word_keys:
                if key not in word_data:
                    raise ValueError(f"Word {i}: Missing required key {key}")

    def _parse_word_analysis(self, word_data: Dict[str, Any], complexity: str) -> Dict[str, Any]:
        """Parse individual word analysis."""

        # Extract morphology
        morphology = word_data.get('morphology', {})
        if isinstance(morphology, str):
            morphology = {'raw': morphology}

        # Validate and enhance morphology
        morphology = self._validate_morphology(morphology, word_data['word'])

        # Validate category
        category = self._validate_category(word_data['category'], complexity)

        # Validate color
        color = self._validate_color(word_data.get('color', ''), category, complexity)

        # Create validation dict
        validation = word_data.get('validation', {})
        validation.update(self._perform_word_validation(word_data, complexity))

        return TurkishAnalysisResult(
            word=word_data['word'],
            morphology=morphology,
            category=category,
            role=word_data.get('role', ''),
            color=color,
            complexity=complexity,
            validation=validation
        )

    def _validate_morphology(self, morphology: Dict[str, Any], word: str) -> Dict[str, Any]:
        """Validate and enhance morphological analysis."""

        enhanced = dict(morphology)  # Copy

        # Ensure root exists
        if 'root' not in enhanced:
            # Try to extract root (simple heuristic: remove common suffixes)
            enhanced['root'] = self._extract_root(word)

        # Ensure suffixes exist
        if 'suffixes' not in enhanced:
            enhanced['suffixes'] = self._extract_suffixes(word, enhanced['root'])

        # Validate vowel harmony in suffixes
        if self.validation_rules['vowel_harmony']['enabled']:
            enhanced['harmony_validation'] = self._validate_vowel_harmony(
                enhanced['root'], enhanced['suffixes']
            )

        return enhanced

    def _extract_root(self, word: str) -> str:
        """Simple root extraction heuristic."""
        # Remove common case markers and possessive suffixes
        # This is a simplified approach - real implementation would use morphological analyzer
        common_suffixes = [
            'im', 'ım', 'um', 'üm',  # 1sg possessive
            'in', 'ın', 'un', 'ün',  # 2sg possessive
            'i', 'ı', 'u', 'ü',      # 3sg possessive/accusative
            'e', 'a',                # dative
            'de', 'da',              # locative
            'den', 'dan',            # ablative
            'in', 'ın', 'un', 'ün',  # genitive
            'ler', 'lar',           # plural
            'mı', 'mi', 'mu', 'mü', # question
        ]

        root = word
        for suffix in sorted(common_suffixes, key=len, reverse=True):
            if root.endswith(suffix):
                root = root[:-len(suffix)]
                break

        return root if root else word

    def _extract_suffixes(self, word: str, root: str) -> List[Dict[str, Any]]:
        """Extract suffixes from word."""
        if word == root:
            return []

        remaining = word[len(root):]
        suffixes = []

        # Simple suffix splitting (would be more sophisticated in real implementation)
        # This is a placeholder - real morphological analysis would be complex
        suffixes.append({
            'form': remaining,
            'meaning': 'unknown',  # Would need morphological dictionary
            'harmony': 'to_be_validated'
        })

        return suffixes

    def _validate_vowel_harmony(self, root: str, suffixes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate vowel harmony in morphological analysis."""

        if not root or not suffixes:
            return {'valid': True, 'reason': 'no_suffixes_to_check'}

        last_vowel = self._get_last_vowel(root)
        if not last_vowel:
            return {'valid': True, 'reason': 'no_vowel_in_root'}

        harmony_issues = []

        for suffix_data in suffixes:
            suffix = suffix_data.get('form', '')
            if not suffix:
                continue

            first_vowel = self._get_first_vowel(suffix)
            if first_vowel:
                is_harmonious = self._check_vowel_harmony(last_vowel, first_vowel)
                if not is_harmonious:
                    harmony_issues.append({
                        'suffix': suffix,
                        'expected_harmony': self._get_expected_harmony(last_vowel),
                        'actual_vowel': first_vowel
                    })

        return {
            'valid': len(harmony_issues) == 0,
            'issues': harmony_issues,
            'root_vowel': last_vowel
        }

    def _get_last_vowel(self, word: str) -> Optional[str]:
        """Get last vowel in word."""
        vowels = set(self.validation_rules['vowel_harmony']['back_vowels'] +
                    self.validation_rules['vowel_harmony']['front_vowels'])

        for char in reversed(word):
            if char in vowels:
                return char
        return None

    def _get_first_vowel(self, word: str) -> Optional[str]:
        """Get first vowel in word."""
        vowels = set(self.validation_rules['vowel_harmony']['back_vowels'] +
                    self.validation_rules['vowel_harmony']['front_vowels'])

        for char in word:
            if char in vowels:
                return char
        return None

    def _check_vowel_harmony(self, root_vowel: str, suffix_vowel: str) -> bool:
        """Check if suffix vowel harmonizes with root vowel."""
        back_vowels = self.validation_rules['vowel_harmony']['back_vowels']
        front_vowels = self.validation_rules['vowel_harmony']['front_vowels']

        root_is_back = root_vowel in back_vowels
        suffix_is_back = suffix_vowel in back_vowels

        return root_is_back == suffix_is_back

    def _get_expected_harmony(self, root_vowel: str) -> str:
        """Get expected harmony type for root vowel."""
        back_vowels = self.validation_rules['vowel_harmony']['back_vowels']
        return 'back' if root_vowel in back_vowels else 'front'

    def _validate_category(self, category: str, complexity: str) -> str:
        """Validate grammatical category."""
        valid_categories = self.validation_rules['categories'].get(complexity, set())
        if category not in valid_categories:
            # Try to map to valid category or use default
            return 'unknown'
        return category

    def _validate_color(self, color: str, category: str, complexity: str) -> str:
        """Validate and provide color for category."""
        if color and color.startswith('#'):
            return color

        # Get color from config
        return self.config.get_color_for_category(category, complexity)

    def _perform_word_validation(self, word_data: Dict[str, Any], complexity: str) -> Dict[str, bool]:
        """Perform validation checks on word analysis."""
        validation = {}

        # Check morphology completeness
        morphology = word_data.get('morphology', {})
        validation['morphology_complete'] = (
            'root' in morphology and
            'suffixes' in morphology
        )

        # Check category validity
        category = word_data.get('category', '')
        validation['category_valid'] = category in self.validation_rules['categories'].get(complexity, set())

        # Check color format
        color = word_data.get('color', '')
        validation['color_valid'] = bool(re.match(r'^#[0-9A-Fa-f]{6}$', color))

        return validation

    def _validate_analysis(self, analysis: Dict[str, Any], complexity: str) -> None:
        """Perform overall analysis validation."""
        # Additional validation logic can be added here
        pass

    def _create_error_analysis(self, response: str, error: str, complexity: str) -> Dict[str, Any]:
        """Create error analysis when parsing fails."""
        return {
            'analysis': [],
            'sentence_structure': 'Error parsing response',
            'linguistic_features': [],
            'validation': {'parsing_error': error},
            'validation_summary': {'valid': False, 'reason': error},
            'raw_response': response
        }

    def get_validation_summary(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Get summary of validation results."""
        analysis_list = analysis.get('analysis', [])
        if not analysis_list:
            return {'valid': False, 'reason': 'no_analysis_results'}

        total_words = len(analysis_list)
        morphology_complete = sum(1 for r in analysis_list if r.get('morphology_validation', {}).get('has_root', False))
        categories_valid = sum(1 for r in analysis_list if r.get('turkish_validation', {}).get('role_valid', False))
        colors_valid = sum(1 for r in analysis_list if r.get('color', '').startswith('#'))

        return {
            'total_words': total_words,
            'morphology_completeness': morphology_complete / total_words if total_words > 0 else 0,
            'category_accuracy': categories_valid / total_words if total_words > 0 else 0,
            'color_validity': colors_valid / total_words if total_words > 0 else 0,
            'overall_valid': all([
                morphology_complete == total_words,
                categories_valid == total_words,
                colors_valid == total_words
            ])
        }