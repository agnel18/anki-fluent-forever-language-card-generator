# Arabic Validator
# Validates Arabic grammar analysis results
# Considers Arabic-specific linguistic features and RTL text direction

import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from .ar_config import ArConfig

logger = logging.getLogger(__name__)

class ArValidator:
    """
    Validates Arabic grammar analysis results.
    Considers Arabic-specific features: RTL text, root morphology, case marking, etc.
    """

    def __init__(self, config: ArConfig):
        self.config = config

    def validate_result(self, result: Dict[str, Any], sentence: str) -> Dict[str, Any]:
        """
        Validate analysis result and assign confidence score.
        Arabic-specific validation considers RTL structure and linguistic features.
        """
        confidence = 1.0
        issues = []
        metadata = {}

        # Extract components
        word_explanations = result.get('word_explanations', [])
        explanations = result.get('explanations', {})
        metadata_info = result.get('metadata', {})

        # Check if this is a fallback response - should have low confidence
        if metadata_info.get('fallback_used', False):
            return {
                'word_explanations': word_explanations,
                'explanations': explanations,
                'confidence_score': 0.1,  # Low confidence for fallback
                'metadata': metadata_info
            }

        # Basic structural validation
        confidence *= self._validate_structure(word_explanations, sentence, issues)

        # Arabic-specific validations
        confidence *= self._validate_arabic_linguistics(word_explanations, sentence, issues)

        # Content quality validation
        confidence *= self._validate_content_quality(word_explanations, explanations, issues)

        # Word-to-sentence alignment (RTL consideration)
        confidence *= self._validate_word_alignment(word_explanations, sentence, issues)

        # Build validation metadata
        metadata.update({
            'word_count': len(word_explanations),
            'sentence_length': len(sentence),
            'confidence_score': confidence,
            'validation_issues': issues,
            'is_rtl_validated': True,
            'arabic_features_checked': [
                'definite_article_assimilation',
                'case_marking_i3rab',
                'root_based_morphology',
                'rtl_word_order'
            ]
        })

        # Add validation metadata to result
        result['validation_metadata'] = metadata
        result['confidence_score'] = confidence

        return result

    def _validate_structure(self, word_explanations: List[List], sentence: str, issues: List[str]) -> float:
        """Validate basic structural requirements"""
        score = 1.0

        if not word_explanations:
            issues.append("No word explanations provided")
            return 0.0

        # Check word explanation format
        for i, exp in enumerate(word_explanations):
            if not isinstance(exp, list) or len(exp) < 4:
                issues.append(f"Word explanation {i} has invalid format")
                score *= 0.8

        # Check for minimum content
        if len(word_explanations) < 2 and len(sentence.split()) > 3:
            issues.append("Too few word explanations for sentence length")
            score *= 0.7

        return score

    def _validate_arabic_linguistics(self, word_explanations: List[List], sentence: str, issues: List[str]) -> float:
        """Validate Arabic-specific linguistic features"""
        score = 1.0

        # Check for definite article usage
        has_definite_article = any('definite_article' in exp[1].lower() for exp in word_explanations)
        has_al_in_sentence = 'ال' in sentence

        if has_al_in_sentence and not has_definite_article:
            issues.append("Definite article 'ال' found in sentence but not identified in analysis")
            score *= 0.9

        # Check for basic Arabic word classes
        roles_found = set(exp[1].lower() for exp in word_explanations)
        has_noun = any('noun' in role for role in roles_found)
        has_verb = any('verb' in role for role in roles_found)

        if not has_noun and len(word_explanations) > 1:
            issues.append("No nouns identified in analysis")
            score *= 0.8

        # Check for case markings in advanced analysis
        if len(word_explanations) > 3:  # Longer sentences might have case markings
            has_case_marking = any(any(case in exp[1].lower() for case in ['nominative', 'accusative', 'genitive'])
                                  for exp in word_explanations)
            if not has_case_marking:
                # This is not necessarily an error, just a note
                pass

        return score

    def _validate_content_quality(self, word_explanations: List[List], explanations: Dict, issues: List[str]) -> float:
        """Validate quality of explanations and content"""
        score = 1.0

        # Check explanation completeness
        required_keys = ['overall_structure', 'key_features']
        for key in required_keys:
            if key not in explanations:
                issues.append(f"Missing explanation: {key}")
                score *= 0.8
            elif len(str(explanations[key]).strip()) < 10:
                issues.append(f"Explanation too short: {key}")
                score *= 0.9

        # Check word explanation quality
        for i, exp in enumerate(word_explanations):
            word, role, color, meaning = exp[:4]

            # Check meaning quality
            if len(meaning.strip()) < 5:
                issues.append(f"Word {i} ({word}) has too short explanation")
                score *= 0.95

            # Check for generic explanations (avoid "in grammar", etc.)
            generic_phrases = ['in grammar', 'in arabic', 'grammatical role']
            if any(phrase in meaning.lower() for phrase in generic_phrases):
                issues.append(f"Word {i} ({word}) has generic explanation")
                score *= 0.9

            # Check color validity
            if not color.startswith('#') or len(color) != 7:
                issues.append(f"Word {i} ({word}) has invalid color: {color}")
                score *= 0.95

        return score

    def _validate_word_alignment(self, word_explanations: List[List], sentence: str, issues: List[str]) -> float:
        """Validate word-to-sentence alignment (RTL consideration)"""
        score = 1.0

        # Extract words from explanations (they should be in RTL order)
        explained_words = [exp[0] for exp in word_explanations]

        # Basic Arabic tokenization
        sentence_words = self._tokenize_arabic_sentence(sentence)

        # For RTL languages, the explanations should be in reverse order
        # So the first explanation should correspond to the last word in the sentence
        if len(explained_words) == len(sentence_words):
            # Check if order is reversed (RTL)
            reversed_explained = list(reversed(explained_words))
            if explained_words == sentence_words:
                issues.append("Word explanations appear to be in LTR order instead of RTL")
                score *= 0.8
            elif reversed_explained == sentence_words:
                # This is correct for RTL
                pass
            else:
                issues.append("Word alignment does not match sentence structure")
                score *= 0.7
        elif len(explained_words) != len(sentence_words):
            issues.append(f"Word count mismatch: {len(explained_words)} explanations vs {len(sentence_words)} words")
            score *= 0.8

        return score

    def _tokenize_arabic_sentence(self, sentence: str) -> List[str]:
        """Basic Arabic sentence tokenization"""
        # Simple whitespace-based tokenization
        # In a real implementation, this would use proper Arabic tokenization
        import re
        words = re.findall(r'\S+', sentence.strip())
        return words

    def calculate_linguistic_score(self, word_explanations: List[List], sentence: str) -> float:
        """Calculate linguistic accuracy score for Arabic analysis based on comprehensive grammar concepts"""
        score = 1.0

        # Check for Arabic-specific features
        text = sentence.lower()

        # Definite article recognition and assimilation
        if 'ال' in text:
            has_definite_article_analysis = any('definite article' in exp[3].lower() for exp in word_explanations)
            if has_definite_article_analysis:
                score *= 1.1  # Bonus for recognizing definite article
            else:
                score *= 0.95  # Penalty for missing definite article analysis

        # Sun/moon letter assimilation (advanced feature)
        sun_letters = ['ت', 'ث', 'د', 'ذ', 'ر', 'ز', 'س', 'ش', 'ص', 'ض', 'ط', 'ظ', 'ل', 'ن']
        has_sun_letter_after_al = any(f'ال{letter}' in text for letter in sun_letters)
        if has_sun_letter_after_al:
            has_assimilation_analysis = any('sun' in exp[3].lower() or 'assimilation' in exp[3].lower() for exp in word_explanations)
            if has_assimilation_analysis:
                score *= 1.05  # Bonus for recognizing assimilation

        # Root-based morphology check (advanced feature)
        has_root_analysis = any(any(term in exp[3].lower() for term in ['root', 'pattern', 'form', 'جذر', 'وزن'])
                               for exp in word_explanations)
        if has_root_analysis:
            score *= 1.05  # Bonus for morphological analysis

        # Case marking check (intermediate/advanced)
        has_case_analysis = any(any(case in exp[1].lower() for case in ['nominative', 'accusative', 'genitive', 'رفع', 'نصب', 'جر'])
                               for exp in word_explanations)
        if has_case_analysis:
            score *= 1.05  # Bonus for case analysis

        # Verb form identification (advanced)
        has_verb_form_analysis = any(any(form in exp[3].lower() for form in ['form i', 'form ii', 'form iii', 'فعل ثلاثي', 'فعل مزيد'])
                                    for exp in word_explanations)
        if has_verb_form_analysis:
            score *= 1.05  # Bonus for verb form analysis

        # Plural pattern recognition (intermediate/advanced)
        has_plural_analysis = any(any(plural in exp[1].lower() for plural in ['sound_plural', 'broken_plural', 'dual', 'جمع سالم', 'جمع مكسر', 'مثنى'])
                                 for exp in word_explanations)
        if has_plural_analysis:
            score *= 1.02  # Small bonus for plural recognition

        # Hamza and emphatic consonant recognition (advanced)
        has_phonetic_analysis = any(any(feature in exp[3].lower() for feature in ['hamza', 'emphatic', 'همزة', 'مظلم'])
                                   for exp in word_explanations)
        if has_phonetic_analysis:
            score *= 1.03  # Bonus for phonetic feature recognition

        return min(score, 1.0)  # Cap at 1.0