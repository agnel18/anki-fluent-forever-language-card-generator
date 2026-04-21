from .zh_types import ValidationResult, ParseResult


from typing import List, Dict, Any
from .zh_config import ZhConfig

class ZhValidator:
    """
    Validates parsed Chinese grammar analysis results using dataclasses for type safety.
    """
    def __init__(self, config: ZhConfig):
        self.config: ZhConfig = config

    def validate_result(self, parse_result, sentence: str) -> ValidationResult:
        # Accept both ParseResult objects and dicts
        success = getattr(parse_result, 'success', None)
        fallback_used = getattr(parse_result, 'fallback_used', None)
        confidence = getattr(parse_result, 'confidence', None)
        # If dict, fallback to key access
        if success is None and isinstance(parse_result, dict):
            success = parse_result.get('success', True)
        if fallback_used is None and isinstance(parse_result, dict):
            fallback_used = parse_result.get('fallback_used', False)
        if confidence is None and isinstance(parse_result, dict):
            confidence = parse_result.get('confidence', 0.3)

        if not success or fallback_used:
            return ValidationResult(is_valid=False, confidence_score=confidence, issues=["Fallback or failed parse"], suggestions=["Check sentence structure or try a simpler sentence."])
        # Use _calculate_confidence if possible
        if hasattr(parse_result, 'sentences'):
            confidence = self._calculate_confidence(parse_result, sentence)
        is_valid = confidence >= 0.5
        issues = [] if is_valid else ["Low confidence"]
        return ValidationResult(is_valid=is_valid, confidence_score=confidence, issues=issues, suggestions=[])

    def _calculate_confidence(self, parse_result: ParseResult, sentence: str) -> float:
        score = 1.0
        if not parse_result.sentences:
            return 0.0
        word_explanations = []
        for sent in parse_result.sentences:
            for word in sent.words:
                word_explanations.append([word.word, word.grammatical_role, word.individual_meaning])
        if len(word_explanations) == 0:
            return 0.0
        roles = [item[1] for item in word_explanations if len(item) > 1]
        if not roles:
            return 0.0
        other_count = roles.count('other')
        if other_count / len(roles) > 0.5:
            score *= 0.7
        if self._has_valid_patterns(roles):
            score *= 1.1
        else:
            score *= 0.9
        has_aspect = any(role in ['aspect_marker'] for role in roles)
        has_classifier = any(role in ['classifier'] for role in roles)
        has_particles = any(role in ['particle', 'modal_particle', 'structural_particle'] for role in roles)
        if has_aspect or has_classifier or has_particles:
            score *= 1.05
        return min(max(score, 0.0), 1.0)

    def _has_valid_patterns(self, roles: list) -> bool:
        has_noun = any(role in ['noun', 'pronoun'] for role in roles)
        has_verb = 'verb' in roles
        has_particles = any(role in ['particle', 'aspect_marker', 'modal_particle', 'structural_particle'] for role in roles)
        return has_noun and (has_verb or has_particles)


    def validate_explanation_quality(self, result) -> dict:
        """Validate the quality and comprehensiveness of explanations in the analysis result (ParseResult or dict)."""
        quality_score = 1.0
        issues = []

        # Handle both ParseResult and dict
        if hasattr(result, 'sentences'):
            # ParseResult/dataclass path
            word_explanations = []
            for sent in getattr(result, 'sentences', []):
                for word in getattr(sent, 'words', []):
                    word_explanations.append([getattr(word, 'word', ''), getattr(word, 'grammatical_role', ''), '', getattr(word, 'individual_meaning', '')])
            explanations = getattr(result, 'explanations', {}) if hasattr(result, 'explanations') else {}
        else:
            # dict path
            word_explanations = result.get('word_explanations', []) if isinstance(result, dict) else []
            explanations = result.get('explanations', {}) if isinstance(result, dict) else {}

        for i, explanation in enumerate(word_explanations):
            if len(explanation) < 4:
                quality_score *= 0.8
                issues.append(f"Word explanation {i} missing meaning component")
                continue
            word, role, color, meaning = explanation[:4]
            if len(str(meaning).strip()) < 10:
                quality_score *= 0.9
                issues.append(f"Word '{word}' has too brief explanation: '{meaning}'")
            relationship_keywords = ['relates to', 'connects to', 'with', 'and', 'relationship', 'function']
            has_relationship = any(keyword in str(meaning).lower() for keyword in relationship_keywords)
            if not has_relationship and len(word_explanations) > 1:
                quality_score *= 0.95
                issues.append(f"Word '{word}' explanation lacks relationship context")

        if not explanations:
            quality_score *= 0.7
            issues.append("Missing overall explanations section")
        else:
            overall_structure = explanations.get('overall_structure', '') if isinstance(explanations, dict) else ''
            if len(str(overall_structure).strip()) < 20:
                quality_score *= 0.9
                issues.append("Overall structure explanation too brief")
            key_features = explanations.get('key_features', '') if isinstance(explanations, dict) else ''
            if len(str(key_features).strip()) < 15:
                quality_score *= 0.9
                issues.append("Key features explanation too brief")
            chinese_features = ['aspect', 'classifier', 'particle', 'topic-comment', 'measure word']
            has_chinese_specific = any(feature in (str(overall_structure) + str(key_features)).lower() for feature in chinese_features)
            if not has_chinese_specific:
                quality_score *= 0.9
                issues.append("Explanations lack Chinese-specific grammatical features")

        quality_score = min(max(quality_score, 0.0), 1.0)
        return {
            'quality_score': quality_score,
            'issues': issues,
            'recommendations': self._generate_quality_recommendations(issues)
        }

    def _has_valid_patterns(self, word_explanations: List[List[str]]) -> bool:
        """Check if result has valid Chinese grammar patterns."""
        roles = [item[1] for item in word_explanations if len(item) > 1]

        # Must have at least one noun/verb (basic requirement)
        has_noun = any(role in ['noun', 'pronoun'] for role in roles)
        has_verb = 'verb' in roles

        # Chinese-specific: check for particles (very common)
        has_particles = any(role in ['particle', 'aspect_marker', 'modal_particle', 'structural_particle'] for role in roles)

        # Basic validity: has content words and possibly function words
        return has_noun and (has_verb or has_particles)

    def validate_explanation_quality(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the quality and comprehensiveness of explanations in the analysis result."""
        quality_score = 1.0
        issues = []

        # Check word explanations for comprehensiveness
        word_explanations = result.get('word_explanations', [])
        for i, explanation in enumerate(word_explanations):
            if len(explanation) < 4:
                quality_score *= 0.8
                issues.append(f"Word explanation {i} missing meaning component")
                continue

            word, role, color, meaning = explanation[:4]

            # Check if meaning is detailed enough (not just brief)
            if len(meaning.strip()) < 10:
                quality_score *= 0.9
                issues.append(f"Word '{word}' has too brief explanation: '{meaning}'")

            # Check for relationship explanations
            relationship_keywords = ['relates to', 'connects to', 'with', 'and', 'relationship', 'function']
            has_relationship = any(keyword in meaning.lower() for keyword in relationship_keywords)
            if not has_relationship and len(word_explanations) > 1:
                quality_score *= 0.95
                issues.append(f"Word '{word}' explanation lacks relationship context")

        # Check overall explanations section
        explanations = result.get('explanations', {})
        if not explanations:
            quality_score *= 0.7
            issues.append("Missing overall explanations section")
        else:
            # Check for comprehensive structural analysis
            overall_structure = explanations.get('overall_structure', '')
            if len(overall_structure.strip()) < 20:
                quality_score *= 0.9
                issues.append("Overall structure explanation too brief")

            # Check for key features explanation
            key_features = explanations.get('key_features', '')
            if len(key_features.strip()) < 15:
                quality_score *= 0.9
                issues.append("Key features explanation too brief")

            # Check for Chinese-specific content
            chinese_features = ['aspect', 'classifier', 'particle', 'topic-comment', 'measure word']
            has_chinese_specific = any(feature in (overall_structure + key_features).lower()
                                     for feature in chinese_features)
            if not has_chinese_specific:
                quality_score *= 0.9
                issues.append("Explanations lack Chinese-specific grammatical features")

        # Ensure quality score is within bounds
        quality_score = min(max(quality_score, 0.0), 1.0)

        return {
            'quality_score': quality_score,
            'issues': issues,
            'recommendations': self._generate_quality_recommendations(issues)
        }

    def _generate_quality_recommendations(self, issues: List[str]) -> List[str]:
        """Generate recommendations based on identified quality issues."""
        recommendations = []

        if any('brief' in issue.lower() for issue in issues):
            recommendations.append("Expand explanations to provide more detailed analysis of word functions and relationships")

        if any('relationship' in issue.lower() for issue in issues):
            recommendations.append("Include how each word relates to adjacent words and contributes to sentence meaning")

        if any('chinese-specific' in issue.lower() for issue in issues):
            recommendations.append("Emphasize Chinese grammatical features like aspect markers, classifiers, and particles")

        if any('missing' in issue.lower() for issue in issues):
            recommendations.append("Ensure all words have complete grammatical analysis including role, color, and detailed meaning")

        if not recommendations:
            recommendations.append("Analysis quality is good - consider adding more advanced linguistic details")

        return recommendations
