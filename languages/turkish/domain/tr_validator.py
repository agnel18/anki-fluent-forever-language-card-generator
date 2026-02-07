# languages/turkish/domain/tr_validator.py
"""
Turkish Validator - Domain Component

TURKISH VALIDATION:
This component validates Turkish grammar analysis results.
It checks for morphological accuracy, vowel harmony, and grammatical correctness.

RESPONSIBILITIES:
1. Validate morphological decomposition
2. Check vowel harmony compliance
3. Verify grammatical category assignments
4. Validate case system usage
5. Ensure analysis completeness

TURKISH-SPECIFIC VALIDATION:
- Agglutination structure validation
- Vowel harmony rules checking
- Case marker identification
- Turkish grammatical categories
- Morphological root and suffix validation

USAGE FOR TURKISH:
1. Validate AI-generated analysis results
2. Check Turkish linguistic feature accuracy
3. Identify morphological decomposition issues
4. Verify vowel harmony compliance
5. Validate case system applications

INTEGRATION:
- Called by main analyzer after parsing
- Receives configuration from TrConfig
- Returns validation results with issues
- Provides recommendations for improvement
"""

import re
import logging
from typing import Dict, List, Any, Optional
from .tr_config import TrConfig

logger = logging.getLogger(__name__)

class TrValidator:
    """
    Validates Turkish language analysis results.

    TURKISH VALIDATION FEATURES:
    - Morphological structure validation
    - Vowel harmony verification
    - Case system checking
    - Grammatical category validation
    - Color coding consistency
    """

    def __init__(self, config: TrConfig):
        """
        Initialize validator with configuration.

        TURKISH CONFIGURATION INTEGRATION:
        - Access to grammatical roles and categories
        - Morphological features for validation
        - Color schemes for consistency checking
        """
        self.config = config

    def validate_result(self, result: Dict[str, Any], sentence: str) -> Dict[str, Any]:
        """
        Validate analysis result and assign confidence score.
        Turkish-specific validation considers agglutination and vowel harmony.
        """
        if result.get('is_fallback', False):
            result['confidence'] = 0.3
            return result

        confidence = self._calculate_confidence(result, sentence)
        result['confidence'] = confidence

        if confidence < 0.5:
            logger.warning(f"Low confidence ({confidence}) for sentence: {sentence}")

        return result

    def validate_explanation_quality(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate quality of word explanations.
        Check for appropriate length, detail, and clarity.
        """
        quality_score = 1.0
        issues = []

        word_explanations = result.get('word_explanations', [])
        explanations = result.get('explanations', {})

        for word_exp in word_explanations:
            if len(word_exp) >= 4:
                meaning = word_exp[3]
                
                # Check meaning length (should be concise but informative)
                if len(meaning) < 5:
                    quality_score *= 0.9
                    issues.append(f"Very short explanation for '{word_exp[0]}'")
                elif len(meaning) > 75:
                    quality_score *= 0.8
                    issues.append(f"Explanation too long for '{word_exp[0]}'")
            else:
                quality_score *= 0.8
                issues.append("Word explanation missing required fields")

        if not explanations:
            quality_score *= 0.7
            issues.append("Missing overall explanations section")
        else:
            overall_structure = explanations.get('overall_structure', '')
            key_features = explanations.get('key_features', '')

            if len(overall_structure.strip()) < 20:
                quality_score *= 0.9
                issues.append("Overall structure explanation too brief")

            if len(key_features.strip()) < 15:
                quality_score *= 0.9
                issues.append("Key features explanation too brief")

            turkish_features = ['vowel harmony', 'case', 'agglutination', 'suffix', 'sov']
            combined = f"{overall_structure} {key_features}".lower()
            if not any(feature in combined for feature in turkish_features):
                quality_score *= 0.9
                issues.append("Explanations lack Turkish-specific grammatical features")

        quality_score = min(max(quality_score, 0.0), 1.0)

        return {
            'quality_score': quality_score,
            'issues': issues,
            'recommendations': self._generate_quality_recommendations(issues)
        }

    def _calculate_confidence(self, result: Dict[str, Any], sentence: str) -> float:
        """Calculate confidence score using Turkish-specific heuristics."""
        score = 1.0
        word_explanations = result.get('word_explanations', [])
        if not word_explanations:
            return 0.0

        roles = [item[1] for item in word_explanations if isinstance(item, list) and len(item) > 1]
        if not roles:
            return 0.0

        other_count = roles.count('other')
        if other_count / len(roles) > 0.5:
            score *= 0.7

        if self._has_valid_patterns(roles):
            score *= 1.1
        else:
            score *= 0.9

        has_case_markers = any(role in ['case_marker', 'possessive_suffix'] for role in roles)
        has_question = 'question_particle' in roles
        has_tense = 'tense_marker' in roles

        if has_case_markers or has_question or has_tense:
            score *= 1.05

        word_count = len(sentence.split()) if sentence else 0
        if word_count > 0 and len(word_explanations) / word_count < 0.5:
            score *= 0.8

        return min(max(score, 0.0), 1.0)

    def _has_valid_patterns(self, roles: List[str]) -> bool:
        """Check for basic Turkish grammatical patterns."""
        has_noun = any(role in ['noun', 'pronoun'] for role in roles)
        has_verb = 'verb' in roles
        has_case_or_suffix = any(role in ['case_marker', 'possessive_suffix', 'tense_marker'] for role in roles)
        return has_noun and (has_verb or has_case_or_suffix)

    def _generate_quality_recommendations(self, issues: List[str]) -> List[str]:
        """Generate recommendations based on quality issues."""
        recommendations = []

        if any('brief' in issue.lower() for issue in issues):
            recommendations.append("Expand explanations to clarify grammatical function and relationships")

        if any('missing' in issue.lower() for issue in issues):
            recommendations.append("Ensure explanations include overall structure and key features")

        if any('turkish-specific' in issue.lower() for issue in issues):
            recommendations.append("Emphasize vowel harmony, case markers, and agglutination in summaries")

        if not recommendations:
            recommendations.append("Analysis quality is good; consider adding more advanced Turkish details")

        return recommendations

    def validate_analysis(self, analysis_result: Dict[str, Any], complexity: str = 'beginner') -> Dict[str, Any]:
        """
        Validate Turkish analysis result.

        TURKISH VALIDATION PROCESS:
        1. Check analysis structure completeness
        2. Validate individual word analyses
        3. Check morphological accuracy
        4. Verify vowel harmony
        5. Validate grammatical categories
        6. Return validation summary with issues
        """
        issues = []
        analysis = analysis_result.get('analysis', [])

        # Validate overall structure
        issues.extend(self._validate_structure(analysis_result))

        # Validate each word
        for word_data in analysis:
            issues.extend(self._validate_word(word_data, complexity))

        # Create validation summary
        summary = self._create_validation_summary(issues, analysis)

        logger.debug(f"Validation completed with {len(issues)} issues found")
        return {
            'is_valid': len([i for i in issues if i['severity'] == 'error']) == 0,
            'issues': issues,
            'summary': summary,
            'recommendations': self._generate_recommendations(issues)
        }

    def _validate_structure(self, analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Validate overall analysis structure.

        TURKISH STRUCTURE REQUIREMENTS:
        - Must have analysis array
        - Must have sentence structure description
        - Must have linguistic features array
        """
        issues = []

        if 'analysis' not in analysis_result:
            issues.append({
                'severity': 'error',
                'category': 'structure',
                'message': 'Missing analysis array',
                'suggestion': 'Analysis must contain word-by-word breakdown'
            })

        if 'sentence_structure' not in analysis_result:
            issues.append({
                'severity': 'warning',
                'category': 'structure',
                'message': 'Missing sentence structure description',
                'suggestion': 'Include brief sentence structure analysis'
            })

        if 'linguistic_features' not in analysis_result:
            issues.append({
                'severity': 'info',
                'category': 'structure',
                'message': 'Missing linguistic features',
                'suggestion': 'List key Turkish linguistic features used'
            })

        return issues

    def _validate_word(self, word_data: Dict[str, Any], complexity: str) -> List[Dict[str, Any]]:
        """
        Validate individual word analysis.

        TURKISH WORD VALIDATION:
        - Check required fields presence
        - Validate grammatical role
        - Check morphological structure
        - Verify vowel harmony
        - Validate color coding
        """
        issues = []

        # Check required fields
        required_fields = ['word', 'grammatical_role', 'individual_meaning']
        for field in required_fields:
            if field not in word_data:
                issues.append({
                    'severity': 'error',
                    'category': 'structure',
                    'word': word_data.get('word', 'unknown'),
                    'message': f'Missing required field: {field}',
                    'suggestion': f'Include {field} in word analysis'
                })

        # Validate grammatical role
        role = word_data.get('grammatical_role', '')
        if role and role not in self.config.grammatical_roles:
            issues.append({
                'severity': 'error',
                'category': 'grammar',
                'word': word_data.get('word', 'unknown'),
                'message': f'Invalid grammatical role: {role}',
                'suggestion': f'Use one of: {", ".join(self.config.grammatical_roles.keys())}'
            })

        # Validate morphological features if present
        if 'morphology' in word_data:
            issues.extend(self._validate_morphology(word_data))

        # Validate Turkish-specific features
        issues.extend(self._validate_turkish_features(word_data))

        # Validate color format
        color = word_data.get('color', '')
        if color and not re.match(r'^#[0-9A-Fa-f]{6}$', color):
            issues.append({
                'severity': 'warning',
                'category': 'formatting',
                'word': word_data.get('word', 'unknown'),
                'message': f'Invalid color format: {color}',
                'suggestion': 'Use hex color format #RRGGBB'
            })

        return issues

    def _validate_morphology(self, word_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Validate morphological analysis for Turkish.

        TURKISH MORPHOLOGICAL VALIDATION:
        - Check root identification
        - Validate suffix structure
        - Check vowel harmony
        - Verify case markers
        """
        issues = []
        word = word_data.get('word', 'unknown')
        morphology = word_data['morphology']

        # Check for root
        if 'root' not in morphology:
            issues.append({
                'severity': 'warning',
                'category': 'morphology',
                'word': word,
                'message': 'Missing morphological root',
                'suggestion': 'Identify the root word in agglutinated form'
            })

        # Check for suffixes
        if 'suffixes' not in morphology:
            issues.append({
                'severity': 'info',
                'category': 'morphology',
                'word': word,
                'message': 'Missing suffix analysis',
                'suggestion': 'Break down agglutinated suffixes'
            })

        # Validate vowel harmony if both root and suffixes present
        if 'root' in morphology and 'suffixes' in morphology:
            harmony_issues = self._check_vowel_harmony(morphology['root'], morphology['suffixes'])
            issues.extend([{
                'severity': 'error',
                'category': 'morphology',
                'word': word,
                'message': issue['message'],
                'suggestion': issue['suggestion']
            } for issue in harmony_issues])

        return issues

    def _check_vowel_harmony(self, root: str, suffixes: List[str]) -> List[Dict[str, Any]]:
        """
        Check vowel harmony between root and suffixes.

        TURKISH VOWEL HARMONY RULES:
        - Back vowels: a, o, u
        - Front vowels: e, ö, ü
        - Suffix vowels must match root's last vowel harmony
        """
        issues = []

        if not root or not suffixes:
            return issues

        # Get last vowel of root
        root_vowel = self._get_last_vowel(root)
        if not root_vowel:
            return issues

        # Determine harmony type
        back_vowels = set('aou')
        root_is_back = root_vowel in back_vowels

        # Check each suffix
        for suffix in suffixes:
            if not suffix:
                continue

            suffix_vowel = self._get_first_vowel(suffix)
            if suffix_vowel:
                suffix_is_back = suffix_vowel in back_vowels
                if root_is_back != suffix_is_back:
                    issues.append({
                        'message': f'Vowel harmony violation in suffix "{suffix}"',
                        'suggestion': f'Use {"back" if root_is_back else "front"} harmony for suffix'
                    })

        return issues

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

    def _validate_turkish_features(self, word_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Validate Turkish-specific linguistic features.

        TURKISH FEATURE VALIDATION:
        - Check for agglutination indicators
        - Validate case system usage
        - Check word order patterns
        """
        issues = []
        word = word_data.get('word', 'unknown')

        # Check for potential agglutination (long words with multiple suffixes)
        if len(word) > 8 and 'morphology' not in word_data:
            issues.append({
                'severity': 'info',
                'category': 'linguistics',
                'word': word,
                'message': 'Long word may need morphological analysis',
                'suggestion': 'Consider agglutination breakdown for complex words'
            })

        # Check for case markers in meaning
        meaning = word_data.get('individual_meaning', '').lower()
        case_indicators = {
            'accusative': ['direct object', 'accusative'],
            'dative': ['to', 'dative', 'direction'],
            'locative': ['at', 'in', 'on', 'locative'],
            'ablative': ['from', 'ablative', 'source'],
            'genitive': ['of', 'possessive', 'genitive']
        }

        for case, indicators in case_indicators.items():
            if any(indicator in meaning for indicator in indicators):
                if 'case' not in word_data and 'morphology' not in word_data:
                    issues.append({
                        'severity': 'info',
                        'category': 'linguistics',
                        'word': word,
                        'message': f'Meaning suggests {case} case usage',
                        'suggestion': 'Consider case marker identification'
                    })
                break

        return issues

    def _create_validation_summary(self, issues: List[Dict[str, Any]], analysis: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create summary of validation results."""
        total_words = len(analysis)
        error_count = len([i for i in issues if i['severity'] == 'error'])
        warning_count = len([i for i in issues if i['severity'] == 'warning'])
        info_count = len([i for i in issues if i['severity'] == 'info'])

        # Count issues by category
        category_counts = {}
        for issue in issues:
            category = issue.get('category', 'unknown')
            category_counts[category] = category_counts.get(category, 0) + 1

        return {
            'total_words': total_words,
            'total_issues': len(issues),
            'errors': error_count,
            'warnings': warning_count,
            'info': info_count,
            'issues_by_category': category_counts,
            'error_rate': error_count / total_words if total_words > 0 else 0,
            'warning_rate': warning_count / total_words if total_words > 0 else 0
        }

    def _generate_recommendations(self, issues: List[Dict[str, Any]]) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []

        # Count issues by category
        category_counts = {}
        for issue in issues:
            category = issue.get('category', 'unknown')
            category_counts[category] = category_counts.get(category, 0) + 1

        # Generate category-specific recommendations
        if category_counts.get('morphology', 0) > 0:
            recommendations.append("Improve morphological decomposition of agglutinated words")

        if category_counts.get('grammar', 0) > 0:
            recommendations.append("Review grammatical role assignments for Turkish")

        if category_counts.get('linguistics', 0) > 0:
            recommendations.append("Enhance Turkish-specific linguistic feature recognition")

        if category_counts.get('structure', 0) > 0:
            recommendations.append("Ensure complete analysis structure with all required fields")

        # General recommendations based on error rates
        error_count = len([i for i in issues if i['severity'] == 'error'])
        if error_count > 0:
            recommendations.append("Fix critical errors before using analysis results")

        return recommendations
