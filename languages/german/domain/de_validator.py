# German Validator
# Validates German grammar analysis results
# Clean Architecture implementation

import logging
from typing import Dict, Any, List, Optional, Tuple

from .de_config import DeConfig

logger = logging.getLogger(__name__)

class DeValidator:
    """
    Comprehensive validator for German grammar analysis results.
    Validates case consistency, gender agreement, verb conjugations, word order,
    and complex grammatical constructions based on Duden standards.
    """

    def __init__(self, config: DeConfig):
        self.config = config

    def validate_result(self, result: Dict[str, Any], sentence: str) -> Dict[str, Any]:
        """Validate analysis result and assign confidence score."""
        if result.get('is_fallback', False):
            result['confidence'] = 0.3
            return result

        confidence = self._calculate_confidence(result, sentence)
        result['confidence'] = confidence

        if confidence < 0.5:
            logger.warning(f"Low confidence ({confidence}) for sentence: {sentence}")

        return result

    def validate_explanation_quality(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate quality of word explanations for German."""
        quality_score = 1.0
        issues = []

        word_explanations = result.get('word_explanations', [])
        explanations = result.get('explanations', {})

        for word_exp in word_explanations:
            if len(word_exp) >= 4:
                meaning = word_exp[3]
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

            german_features = ['case', 'gender', 'v2', 'konjunktiv', 'declension']
            combined = f"{overall_structure} {key_features}".lower()
            if not any(feature in combined for feature in german_features):
                quality_score *= 0.9
                issues.append("Explanations lack German-specific grammatical features")

        quality_score = min(max(quality_score, 0.0), 1.0)

        return {
            'quality_score': quality_score,
            'issues': issues,
            'recommendations': self._generate_quality_recommendations(issues)
        }

    def _generate_quality_recommendations(self, issues: List[str]) -> List[str]:
        """Generate recommendations based on quality issues."""
        recommendations = []

        if any('brief' in issue.lower() for issue in issues):
            recommendations.append("Provide clearer explanations of German grammatical function")

        if any('missing' in issue.lower() for issue in issues):
            recommendations.append("Include overall structure and key features in explanations")

        if any('german-specific' in issue.lower() for issue in issues):
            recommendations.append("Highlight case, gender, and word order in summaries")

        if not recommendations:
            recommendations.append("Analysis quality is good; consider adding more German-specific details")

        return recommendations

    def _calculate_confidence(self, result: Dict[str, Any], sentence: str) -> float:
        """Calculate confidence score using German-specific heuristics."""
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

        has_noun = any(role in ['noun', 'pronoun'] for role in roles)
        has_verb = 'verb' in roles
        if has_noun and has_verb:
            score *= 1.05
        else:
            score *= 0.9

        word_count = len(sentence.split()) if sentence else 0
        if word_count > 0 and len(word_explanations) / word_count < 0.5:
            score *= 0.8

        return min(max(score, 0.0), 1.0)

    def validate_analysis(self, parsed_result: Dict[str, Any], original_text: str) -> Dict[str, Any]:
        """
        Validate comprehensive German grammar analysis.

        Args:
            parsed_result: Parsed analysis result
            original_text: Original German text

        Returns:
            Validated result with confidence scores and error/warning lists
        """
        if not parsed_result:
            return self._create_empty_validation_result()

        words = parsed_result.get('words', [])
        sentences = parsed_result.get('sentences', [])

        # Perform comprehensive validation
        validation_results = self._validate_german_specific(words, sentences, original_text)

        # Calculate detailed confidence
        confidence_details = self.calculate_detailed_confidence(words, sentences, validation_results)

        # Build final result
        validated_result = parsed_result.copy()
        validated_result.update({
            'overall_confidence': confidence_details['overall'],
            'validation_details': confidence_details,
            'errors': validation_results.get('errors', []),
            'warnings': validation_results.get('warnings', [])
        })

        return validated_result

    def _validate_german_specific(self, words: List[Dict[str, Any]],
                                sentences: List[Dict[str, Any]],
                                original_text: str) -> Dict[str, Any]:
        """
        Perform German-specific grammatical validation.

        Args:
            words: Analyzed words
            sentences: Analyzed sentences
            original_text: Original text

        Returns:
            Validation results with errors and warnings
        """
        errors = []
        warnings = []

        # Case system validation
        case_errors, case_warnings = self._validate_case_system(words)
        errors.extend(case_errors)
        warnings.extend(case_warnings)

        # Gender agreement validation
        gender_errors, gender_warnings = self._validate_gender_agreement(words)
        errors.extend(gender_errors)
        warnings.extend(gender_warnings)

        # Verb system validation
        verb_errors, verb_warnings = self._validate_verb_system(words)
        errors.extend(verb_errors)
        warnings.extend(verb_warnings)

        # Word order validation
        word_order_errors, word_order_warnings = self._validate_word_order(sentences, words)
        errors.extend(word_order_errors)
        warnings.extend(word_order_warnings)

        # Adjective declension validation
        adj_errors, adj_warnings = self._validate_adjective_declension(words)
        errors.extend(adj_errors)
        warnings.extend(adj_warnings)

        # Preposition case validation
        prep_errors, prep_warnings = self._validate_preposition_cases(words)
        errors.extend(prep_errors)
        warnings.extend(prep_warnings)

        # Complex constructions validation
        complex_errors, complex_warnings = self._validate_complex_constructions(words, sentences)
        errors.extend(complex_errors)
        warnings.extend(complex_warnings)

        return {
            'errors': errors,
            'warnings': warnings,
            'case_validation': len(case_errors) == 0,
            'gender_validation': len(gender_errors) == 0,
            'verb_validation': len(verb_errors) == 0,
            'word_order_validation': len(word_order_errors) == 0,
            'adjective_validation': len(adj_errors) == 0,
            'preposition_validation': len(prep_errors) == 0,
            'complex_construction_validation': len(complex_errors) == 0
        }

    def _validate_case_system(self, words: List[Dict[str, Any]]) -> Tuple[List[str], List[str]]:
        """Validate German case system consistency."""
        errors = []
        warnings = []

        # Check for case consistency in noun phrases
        noun_phrases = self._group_noun_phrases(words)

        for phrase in noun_phrases:
            article_case = None
            noun_case = None
            adjective_cases = []

            for word in phrase:
                role = word.get('grammatical_role')
                case = word.get('case')

                if role == 'article' and case:
                    article_case = case
                elif role == 'noun' and case:
                    noun_case = case
                elif role == 'adjective' and case:
                    adjective_cases.append(case)

            # Check case agreement
            if article_case and noun_case and article_case != noun_case:
                errors.append(f"Case mismatch in noun phrase: article ({article_case}) vs noun ({noun_case})")

            # Check adjective case agreement
            for adj_case in adjective_cases:
                if article_case and adj_case != article_case:
                    warnings.append(f"Adjective case ({adj_case}) doesn't match article case ({article_case})")

        # Check preposition case requirements
        prep_case_errors, prep_case_warnings = self._validate_preposition_cases(words)
        errors.extend(prep_case_errors)
        warnings.extend(prep_case_warnings)

        return errors, warnings

    def _validate_gender_agreement(self, words: List[Dict[str, Any]]) -> Tuple[List[str], List[str]]:
        """Validate gender agreement in noun phrases."""
        errors = []
        warnings = []

        noun_phrases = self._group_noun_phrases(words)

        for phrase in noun_phrases:
            article_gender = None
            noun_gender = None
            adjective_genders = []

            for word in phrase:
                role = word.get('grammatical_role')
                gender = word.get('gender')

                if role == 'article' and gender:
                    article_gender = gender
                elif role == 'noun' and gender:
                    noun_gender = gender
                elif role == 'adjective' and gender:
                    adjective_genders.append(gender)

            # Check gender agreement
            if article_gender and noun_gender and article_gender != noun_gender:
                errors.append(f"Gender mismatch: article ({article_gender}) vs noun ({noun_gender})")

            # Check adjective gender agreement
            for adj_gender in adjective_genders:
                expected_gender = article_gender or noun_gender
                if expected_gender and adj_gender != expected_gender:
                    warnings.append(f"Adjective gender ({adj_gender}) doesn't match expected ({expected_gender})")

        return errors, warnings

    def _validate_verb_system(self, words: List[Dict[str, Any]]) -> Tuple[List[str], List[str]]:
        """Validate verb conjugation and positioning."""
        errors = []
        warnings = []

        verbs = [w for w in words if w.get('pos') == 'verb' or w.get('grammatical_role') == 'verb']

        for verb in verbs:
            # Check verb positioning (V2 word order)
            verb_position = verb.get('position')
            if verb_position and verb_position not in ['second', 'final', 'first']:
                warnings.append(f"Unusual verb position: {verb_position} for verb '{verb.get('word', '')}'")

            # Check tense/mood combinations
            tense = verb.get('tense')
            mood = verb.get('mood')

            if tense and mood:
                if mood == 'subjunctive' and tense not in ['present', 'past', 'present_perfect']:
                    warnings.append(f"Subjunctive mood with unusual tense: {tense}")

            # Check separable verb analysis
            features = verb.get('features', {})
            if features.get('is_separable') and not features.get('prefix'):
                warnings.append(f"Separable verb '{verb.get('word', '')}' missing prefix analysis")

        return errors, warnings

    def _validate_word_order(self, sentences: List[Dict[str, Any]], words: List[Dict[str, Any]]) -> Tuple[List[str], List[str]]:
        """Validate German word order patterns."""
        errors = []
        warnings = []

        for sentence in sentences:
            word_order_type = sentence.get('word_order_type')
            verb_position = sentence.get('verb_position')

            # V2 word order validation
            if word_order_type == 'v2' and verb_position != 'second':
                errors.append("V2 word order requires verb in second position")

            # Subordinate clause validation
            if word_order_type == 'subordinate' and verb_position != 'final':
                errors.append("Subordinate clauses require verb-final position")

            # Complex constructions
            complex_constructions = sentence.get('complex_constructions', [])
            if 'relative_clause' in complex_constructions:
                warnings.append("Relative clause detected - check relative pronoun case")

            if 'passive' in complex_constructions:
                warnings.append("Passive construction detected - verify auxiliary verb usage")

        return errors, warnings

    def _validate_adjective_declension(self, words: List[Dict[str, Any]]) -> Tuple[List[str], List[str]]:
        """Validate adjective declension patterns."""
        errors = []
        warnings = []

        adjectives = [w for w in words if w.get('pos') == 'adjective' or w.get('grammatical_role') == 'adjective']

        for adj in adjectives:
            declension_type = adj.get('declension_type')
            case = adj.get('case')
            gender = adj.get('gender')

            if not declension_type:
                warnings.append(f"Adjective '{adj.get('word', '')}' missing declension type")
                continue

            # Validate declension type appropriateness
            if declension_type not in ['strong', 'weak', 'mixed']:
                errors.append(f"Invalid declension type: {declension_type}")

            # Check for required case/gender information
            if not case:
                warnings.append(f"Adjective '{adj.get('word', '')}' missing case information")

            if declension_type == 'strong' and not case:
                errors.append(f"Strong declension requires case information")

        return errors, warnings

    def _validate_preposition_cases(self, words: List[Dict[str, Any]]) -> Tuple[List[str], List[str]]:
        """Validate preposition case requirements."""
        errors = []
        warnings = []

        prepositions = [w for w in words if w.get('pos') == 'preposition' or w.get('grammatical_role') == 'preposition']

        for prep in prepositions:
            word = prep.get('word', '').lower()
            preposition_case = prep.get('preposition_case')

            # Check known preposition case requirements
            case_patterns = self.config.case_patterns
            if case_patterns:
                accusative_preps = case_patterns.get('accusative', {}).get('prepositions', {}).get('definite', [])
                dative_preps = case_patterns.get('dative', {}).get('prepositions', {}).get('definite', [])
                two_way_preps = case_patterns.get('two_way_prepositions', {}).get('prepositions', [])

                if word in accusative_preps and preposition_case != 'accusative':
                    errors.append(f"Preposition '{word}' requires accusative case")

                if word in dative_preps and preposition_case != 'dative':
                    errors.append(f"Preposition '{word}' requires dative case")

                if word in two_way_preps and not preposition_case:
                    warnings.append(f"Two-way preposition '{word}' - case depends on context")

        return errors, warnings

    def _validate_complex_constructions(self, words: List[Dict[str, Any]], sentences: List[Dict[str, Any]]) -> Tuple[List[str], List[str]]:
        """Validate complex grammatical constructions."""
        errors = []
        warnings = []

        # Check for modal verb + infinitive constructions
        modal_verbs = [w for w in words if w.get('grammatical_role') == 'modal']
        infinitives = [w for w in words if w.get('pos') == 'verb' and w.get('tense') == 'infinitive']

        if modal_verbs and infinitives:
            warnings.append("Modal verb + infinitive construction detected - check double infinitive in perfect tense")

        # Check for passive constructions
        for sentence in sentences:
            if 'passive' in sentence.get('complex_constructions', []):
                # Look for werden + past participle
                werden_verbs = [w for w in words if w.get('word', '').lower() == 'werden']
                past_participles = [w for w in words if w.get('tense') == 'past_participle']

                if not (werden_verbs and past_participles):
                    warnings.append("Passive construction detected but missing werden + past participle pattern")

        # Check for subjunctive mood usage
        subjunctive_verbs = [w for w in words if w.get('mood') == 'subjunctive']
        if subjunctive_verbs:
            warnings.append("Subjunctive mood detected - verify appropriate usage (indirect speech, hypothetical)")

        return errors, warnings

    def _group_noun_phrases(self, words: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Group words into noun phrases for validation."""
        phrases = []
        current_phrase = []

        for word in words:
            role = word.get('grammatical_role')

            if role in ['article', 'adjective', 'noun']:
                current_phrase.append(word)

                # If we hit a noun, this might end the phrase
                if role == 'noun':
                    phrases.append(current_phrase)
                    current_phrase = []
            else:
                # Non-noun-phrase word - save current phrase if exists
                if current_phrase:
                    phrases.append(current_phrase)
                    current_phrase = []

        # Add any remaining phrase
        if current_phrase:
            phrases.append(current_phrase)

        return phrases

    def calculate_detailed_confidence(self, words: List[Dict[str, Any]],
                                    sentences: List[Dict[str, Any]],
                                    validation_results: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate detailed confidence scores for different aspects of the analysis.

        Args:
            words: Analyzed words
            sentences: Analyzed sentences
            validation_results: Validation results

        Returns:
            Detailed confidence scores
        """
        base_confidence = 0.5

        # Word-level confidence
        word_confidences = [w.get('confidence', 0.5) for w in words]
        avg_word_confidence = sum(word_confidences) / len(word_confidences) if word_confidences else 0.5

        # Validation-based confidence adjustments
        validation_bonus = 0.0
        if validation_results.get('case_validation'):
            validation_bonus += 0.1
        if validation_results.get('gender_validation'):
            validation_bonus += 0.1
        if validation_results.get('verb_validation'):
            validation_bonus += 0.1
        if validation_results.get('word_order_validation'):
            validation_bonus += 0.1

        # Feature completeness bonus
        feature_bonus = 0.0
        german_features = ['case', 'gender', 'number', 'person', 'tense', 'mood']
        for word in words:
            for feature in german_features:
                if word.get(feature):
                    feature_bonus += 0.01  # Small bonus per feature

        # Complexity bonus
        complexity_bonus = 0.0
        if sentences:
            complexity_bonus += 0.1
        if any(w.get('features', {}).get('is_separable') for w in words):
            complexity_bonus += 0.05
        if any(w.get('mood') == 'subjunctive' for w in words):
            complexity_bonus += 0.05

        overall_confidence = min(1.0, base_confidence + avg_word_confidence * 0.3 +
                               validation_bonus + feature_bonus + complexity_bonus)

        return {
            'overall': round(overall_confidence, 2),
            'word_level': round(avg_word_confidence, 2),
            'validation': round(validation_bonus, 2),
            'features': round(feature_bonus, 2),
            'complexity': round(complexity_bonus, 2)
        }

    def _create_empty_validation_result(self) -> Dict[str, Any]:
        """Create empty validation result for failed analysis."""
        return {
            'words': [],
            'sentences': [],
            'overall_confidence': 0.0,
            'validation_details': {
                'overall': 0.0,
                'word_level': 0.0,
                'validation': 0.0,
                'features': 0.0,
                'complexity': 0.0
            },
            'errors': ['No analysis result to validate'],
            'warnings': []
        }

    def validate_result(self, result: Dict[str, Any], sentence: str) -> Dict[str, Any]:
        """
        Validate analysis result and calculate confidence score.
        German-specific validation includes case consistency, gender agreement, etc.
        """
        confidence = 0.8  # Start with high confidence for German (inflectional language)

        try:
            word_explanations = result.get('word_explanations') or result.get('words', [])

            # Check for minimum requirements
            if len(word_explanations) == 0:
                confidence = 0.1
                logger.warning("No word explanations found")

            # Check for explanations
            explanations_key = 'explanations' if 'explanations' in result else 'overall_analysis'
            if explanations_key not in result:
                confidence *= 0.7
                logger.warning("No explanations section found")

            # German-specific validations
            confidence *= self._validate_german_patterns(result, sentence)

            # Ensure confidence is within bounds
            confidence = max(0.0, min(1.0, confidence))

            result['confidence'] = confidence
            logger.info(f"German validation complete. Confidence: {confidence:.2f}")

        except Exception as e:
            logger.error(f"Error in German validation: {e}")
            result['confidence'] = 0.1

        return result

    def _validate_german_patterns(self, result: Dict[str, Any], sentence: str) -> float:
        """
        Validate German-specific linguistic patterns.
        Returns a multiplier for confidence score.
        """
        multiplier = 1.0

        try:
            words_data = result.get('words') or result.get('word_explanations', [])

            # Check for case consistency
            case_score = self._check_case_consistency(words_data)
            multiplier *= case_score

            # Check for gender agreement
            gender_score = self._check_gender_agreement(words_data)
            multiplier *= gender_score

            # Check for verb position (V2 word order)
            verb_score = self._check_verb_position(words_data, sentence)
            multiplier *= verb_score

            # Check for adjective declension
            adjective_score = self._check_adjective_declension(words_data)
            multiplier *= adjective_score

        except Exception as e:
            logger.error(f"Error in German pattern validation: {e}")
            multiplier *= 0.8  # Slight penalty for validation errors

        return multiplier

    def _check_case_consistency(self, words_data: List[Dict[str, Any]]) -> float:
        """Check for case consistency in German sentences"""
        score = 1.0

        # Look for articles and nouns with case information
        articles = [w for w in words_data if w.get('grammatical_role') == 'article']
        nouns = [w for w in words_data if w.get('grammatical_role') == 'noun']

        if len(articles) > 0 and len(nouns) > 0:
            # Basic check: if we have both, assume case consistency for now
            # In a full implementation, this would check actual case agreement
            score = 0.9  # Slight penalty for not doing detailed checking yet

        return score

    def _check_gender_agreement(self, words_data: List[Dict[str, Any]]) -> float:
        """Check for gender agreement between articles and nouns"""
        score = 1.0

        # Look for article-noun pairs
        articles = [w for w in words_data if w.get('grammatical_role') == 'article']
        nouns = [w for w in words_data if w.get('grammatical_role') == 'noun']

        if len(articles) > 0 and len(nouns) > 0:
            # Basic check: if we have both, assume agreement for now
            # In a full implementation, this would check actual gender agreement
            score = 0.9  # Slight penalty for not doing detailed checking yet

        return score

    def _check_verb_position(self, words_data: List[Dict[str, Any]], sentence: str) -> float:
        """Check for correct verb position (V2 word order in main clauses)"""
        score = 1.0

        verbs = [w for w in words_data if w.get('grammatical_role') == 'verb']
        if len(verbs) > 0:
            # Basic check: if we have verbs, assume correct position for now
            # In a full implementation, this would check actual V2 word order
            score = 0.9  # Slight penalty for not doing detailed checking yet

        return score

    def _check_adjective_declension(self, words_data: List[Dict[str, Any]]) -> float:
        """Check for proper adjective declension"""
        score = 1.0

        adjectives = [w for w in words_data if w.get('grammatical_role') == 'adjective']
        if len(adjectives) > 0:
            # Basic check: if we have adjectives, assume correct declension for now
            # In a full implementation, this would check actual declension patterns
            score = 0.9  # Slight penalty for not doing detailed checking yet

        return score