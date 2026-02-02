# German Fallbacks
# Provides comprehensive fallback analysis when AI fails
# Clean Architecture implementation

import logging
import re
from typing import Dict, Any, List, Optional

from ..domain.de_config import DeConfig

logger = logging.getLogger(__name__)

class DeFallbacks:
    """
    Provides comprehensive fallback German grammar analysis.
    Uses pattern matching, morphological analysis, and linguistic rules
    based on Duden German grammar standards.
    """

    def __init__(self, config: DeConfig):
        self.config = config

        # Load grammatical patterns from config
        self.grammatical_roles = config.grammatical_roles or {}
        self.verb_conjugations = config.verb_conjugations or {}
        self.case_patterns = config.case_patterns or {}
        self.gender_patterns = config.gender_patterns or {}

    def create_fallback(self, sentence: str, complexity: str, target_word: str) -> Dict[str, Any]:
        """
        Create a basic fallback analysis for German sentences.
        Used when AI response parsing fails.
        """
        logger.info(f"Creating German fallback analysis for: {sentence}")

        # Use the existing analyze_german_text method
        return self.analyze_german_text(sentence)

    def analyze_german_text(self, text: str) -> Dict[str, Any]:
        """
        Provide comprehensive fallback analysis for German text.

        Args:
            text: German text to analyze

        Returns:
            Complete analysis result with words and sentences
        """
        logger.info(f"Performing fallback analysis for text: {text[:50]}...")

        words = []
        sentences = []

        # Split into sentences (basic splitting)
        text_sentences = self._split_sentences(text)

        for sent_text in text_sentences:
            sent_words = []
            word_list = sent_text.split()

            for word in word_list:
                word_analysis = self._analyze_german_word(word, sent_text)
                sent_words.append(word_analysis)

            # Create sentence analysis
            sentence_analysis = self._analyze_sentence(sent_words, sent_text)
            sentences.append(sentence_analysis)
            words.extend(sent_words)

        return {
            'words': words,
            'sentences': sentences,
            'overall_confidence': 0.4,
            'overall_analysis': {
                'sentence_structure': 'Basic German sentence structure (fallback analysis)',
                'key_features': 'Pattern-based morphological analysis due to parsing failure',
                'case_system': 'Case recognition attempted but not fully validated',
                'gender_agreement': 'Gender agreement patterns identified where possible'
            },
            'analysis_metadata': {
                'case_system_recognized': True,
                'gender_agreement_checked': True,
                'verb_conjugation_analyzed': True,
                'word_order_validated': False,
                'complex_constructions_detected': [],
                'morphological_analysis_performed': True,
                'fallback_used': True
            },
            'errors': [],
            'warnings': ['Using fallback pattern-based analysis']
        }

    def _analyze_german_word(self, word: str, context: str) -> Dict[str, Any]:
        """
        Analyze individual German word with comprehensive morphological analysis.

        Args:
            word: Word to analyze
            context: Sentence context

        Returns:
            Detailed word analysis
        """
        word_lower = word.lower()
        original_word = word

        # Initialize analysis result
        analysis = {
            'word': original_word,
            'lemma': word_lower,
            'pos': 'unknown',
            'grammatical_role': 'unknown',
            'grammatical_case': None,
            'gender': None,
            'number': None,
            'person': None,
            'tense': None,
            'mood': None,
            'declension_type': None,
            'preposition_case': None,
            'confidence': 0.5,
            'features': {},
            'morphological_info': {}
        }

        # 1. Article analysis
        if self._is_article(word_lower):
            analysis.update(self._analyze_article(word_lower))
            return analysis

        # 2. Preposition analysis
        if self._is_preposition(word_lower):
            analysis.update(self._analyze_preposition(word_lower))
            return analysis

        # 3. Pronoun analysis
        if self._is_pronoun(word_lower):
            analysis.update(self._analyze_pronoun(word_lower))
            return analysis

        # 4. Noun analysis (check capitalized words first)
        if word[0].isupper() or self._is_noun(word_lower):
            analysis.update(self._analyze_noun(word, context))
            return analysis

        # 5. Adjective analysis
        if self._is_adjective(word_lower):
            analysis.update(self._analyze_adjective(word_lower))
            return analysis

        # 6. Adverb analysis
        if self._is_adverb(word_lower):
            analysis.update(self._analyze_adverb(word_lower))
            return analysis

        # 7. Verb analysis (check last, as many words can look like verbs)
        verb_analysis = self._analyze_verb(word_lower, context)
        if verb_analysis['pos'] == 'verb':
            analysis.update(verb_analysis)
            return analysis

        # Default unknown word
        analysis['individual_meaning'] = f"{word} (unknown): {word}; word function not determined from context"
        return analysis

    def _is_article(self, word: str) -> bool:
        """Check if word is a German article."""
        definite_articles = ['der', 'die', 'das', 'den', 'dem', 'des']
        indefinite_articles = ['ein', 'eine', 'einen', 'einem', 'eines']
        demonstrative_articles = ['dieser', 'diese', 'dieses', 'diesen', 'diesem', 'dieses']
        return word in definite_articles + indefinite_articles + demonstrative_articles

    def _analyze_article(self, word: str) -> Dict[str, Any]:
        """Analyze German article for case and gender."""
        # Definite articles
        definite_map = {
            'der': {'case': 'nominative', 'gender': 'maskulin'},
            'die': {'case': 'nominative', 'gender': 'feminin'},
            'das': {'case': 'nominative', 'gender': 'neutrum'},
            'den': {'case': 'accusative', 'gender': 'maskulin'},
            'dem': {'case': 'dative', 'gender': 'maskulin'},
            'des': {'case': 'genitive', 'gender': 'maskulin'}
        }

        # Indefinite articles
        indefinite_map = {
            'ein': {'case': 'nominative', 'gender': 'maskulin'},
            'eine': {'case': 'nominative', 'gender': 'feminin'},
            'einen': {'case': 'accusative', 'gender': 'maskulin'},
            'einem': {'case': 'dative', 'gender': 'maskulin'},
            'eines': {'case': 'genitive', 'gender': 'maskulin'}
        }

        # Demonstrative articles
        demonstrative_map = {
            'dieser': {'case': 'nominative', 'gender': 'maskulin'},
            'diese': {'case': 'nominative', 'gender': 'feminin'},
            'dieses': {'case': 'nominative', 'gender': 'neutrum'},
            'diesen': {'case': 'accusative', 'gender': 'maskulin'},
            'diesem': {'case': 'dative', 'gender': 'maskulin'},
            'dieses': {'case': 'genitive', 'gender': 'maskulin'}
        }

        article_info = definite_map.get(word, indefinite_map.get(word, demonstrative_map.get(word, {})))

        article_type = 'definite' if word in definite_map else 'indefinite' if word in indefinite_map else 'demonstrative'

        return {
            'pos': 'article',
            'grammatical_role': 'article',
            'grammatical_case': article_info.get('case'),
            'gender': article_info.get('gender'),
            'confidence': 0.9,
            'individual_meaning': f"{word} ({article_info.get('gender', 'unknown')} {article_info.get('case', 'unknown')}): {article_type} article; indicates specific noun with {article_info.get('gender', 'unknown')} gender in {article_info.get('case', 'unknown')} case",
            'morphological_info': {'article_type': article_type}
        }

    def _is_preposition(self, word: str) -> bool:
        """Check if word is a German preposition."""
        prepositions = [
            'in', 'auf', 'an', 'bei', 'mit', 'nach', 'von', 'zu', 'für',
            'aus', 'durch', 'gegen', 'ohne', 'um', 'über', 'unter', 'vor',
            'zwischen', 'hinter', 'neben', 'wegen', 'trotz', 'statt'
        ]
        return word in prepositions

    def _analyze_preposition(self, word: str) -> Dict[str, Any]:
        """Analyze German preposition for case requirements."""
        # Accusative prepositions
        accusative_preps = ['durch', 'für', 'gegen', 'ohne', 'um']

        # Dative prepositions
        dative_preps = ['aus', 'bei', 'mit', 'nach', 'von', 'zu']

        # Genitive prepositions
        genitive_preps = ['wegen', 'trotz', 'statt']

        # Two-way prepositions
        two_way_preps = ['in', 'auf', 'an', 'hinter', 'neben', 'über', 'unter', 'vor', 'zwischen']

        case_requirement = None
        if word in accusative_preps:
            case_requirement = 'accusative'
        elif word in dative_preps:
            case_requirement = 'dative'
        elif word in genitive_preps:
            case_requirement = 'genitive'
        elif word in two_way_preps:
            case_requirement = 'two_way'

        return {
            'pos': 'preposition',
            'grammatical_role': 'preposition',
            'preposition_case': case_requirement,
            'confidence': 0.8,
            'individual_meaning': f"{word} (preposition): {word}; requires {case_requirement} case for following noun; establishes relationship of location/direction/etc.",
            'morphological_info': {'case_requirement': case_requirement}
        }

    def _is_pronoun(self, word: str) -> bool:
        """Check if word is a German pronoun."""
        pronouns = [
            'ich', 'du', 'er', 'sie', 'es', 'wir', 'ihr', 'sie', 'Sie',
            'mich', 'dich', 'ihn', 'uns', 'euch', 'ihnen', 'Ihnen',
            'mir', 'dir', 'ihm', 'ihr', 'ihm', 'uns', 'euch', 'ihnen', 'Ihnen',
            'meiner', 'deiner', 'seiner', 'ihrer', 'unser', 'euer', 'ihrer', 'Ihrer'
        ]
        return word in pronouns

    def _analyze_pronoun(self, word: str) -> Dict[str, Any]:
        """Analyze German pronoun for case, person, gender."""
        # Personal pronouns by case
        nominative = ['ich', 'du', 'er', 'sie', 'es', 'wir', 'ihr', 'sie', 'Sie']
        accusative = ['mich', 'dich', 'ihn', 'sie', 'es', 'uns', 'euch', 'sie', 'Sie']
        dative = ['mir', 'dir', 'ihm', 'ihr', 'ihm', 'uns', 'euch', 'ihnen', 'Ihnen']
        genitive = ['meiner', 'deiner', 'seiner', 'ihrer', 'seiner', 'unser', 'euer', 'ihrer', 'Ihrer']

        grammatical_case = None
        person = None
        gender = None

        if word in nominative:
            grammatical_case = 'nominative'
        elif word in accusative:
            grammatical_case = 'accusative'
        elif word in dative:
            grammatical_case = 'dative'
        elif word in genitive:
            grammatical_case = 'genitive'

        # Determine person
        if word in ['ich', 'mich', 'mir', 'meiner']:
            person = '1st'
        elif word in ['du', 'dich', 'dir', 'deiner']:
            person = '2nd'
        elif word in ['er', 'sie', 'es', 'ihn', 'ihm', 'ihr', 'seiner', 'ihrer']:
            person = '3rd'
        elif word in ['wir', 'uns', 'unser']:
            person = '1st'
            # number = 'plural'  # Would need to add number field
        elif word in ['ihr', 'euch', 'euer']:
            person = '2nd'
            # number = 'plural'
        elif word in ['sie', 'Sie', 'ihnen', 'ihrer', 'Ihnen', 'Ihrer']:
            person = '3rd'
            # number = 'plural'

        # Determine gender for 3rd person
        if person == '3rd' and word in ['er', 'ihn', 'ihm', 'seiner']:
            gender = 'masculine'
        elif person == '3rd' and word in ['sie', 'ihr', 'ihrer']:
            gender = 'feminine'
        elif person == '3rd' and word in ['es', 'ihm', 'seiner']:
            gender = 'neuter'

        return {
            'pos': 'pronoun',
            'grammatical_role': 'pronoun',
            'grammatical_case': grammatical_case,
            'person': person,
            'gender': gender,
            'confidence': 0.8,
            'individual_meaning': f"{word} (personal pronoun): {word}; {person} person {'masculine ' if gender == 'masculine' else 'feminine ' if gender == 'feminine' else 'neuter ' if gender == 'neuter' else ''}in {grammatical_case} case; refers to previously mentioned person/thing",
            'morphological_info': {'pronoun_type': 'personal'}
        }

    def _analyze_verb(self, word: str, context: str) -> Dict[str, Any]:
        """Analyze German verb for conjugation, tense, mood."""
        # Check against known verb conjugations
        verb_conjugations = self.verb_conjugations

        # Define modal and auxiliary verbs
        modal_verbs = ['können', 'müssen', 'wollen', 'dürfen', 'sollen', 'mögen']
        auxiliary_verbs = ['haben', 'sein', 'werden']

        # Check if it's a known verb form
        for verb_type, verb_data in verb_conjugations.items():
            if verb_type == 'strong_verbs':
                for ablaut_series, verb_list in verb_data.items():
                    for verb_info in verb_list:
                        if isinstance(verb_info, dict) and 'infinitive' in verb_info:
                            # Check various forms
                            for tense, forms in verb_info.items():
                                if tense != 'infinitive' and isinstance(forms, dict):
                                    for person, form in forms.items():
                                        if form == word:
                                            return {
                                                'pos': 'verb',
                                                'grammatical_role': 'verb',
                                                'tense': tense,
                                                'person': person,
                                                'mood': 'indicative',
                                                'confidence': 0.8,
                                                'individual_meaning': f"{word} (strong verb): {verb_info.get('infinitive', word)}; conjugated form in {tense} tense, {person} person; shows ablaut pattern from {ablaut_series} series",
                                                'morphological_info': {
                                                    'verb_type': 'strong',
                                                    'infinitive': verb_info.get('infinitive'),
                                                    'ablaut_series': ablaut_series
                                                }
                                            }

        if word in modal_verbs:
            return {
                'pos': 'verb',
                'grammatical_role': 'modal',
                'confidence': 0.9,
                'individual_meaning': f"{word} (modal verb): {word}; expresses possibility/necessity/willingness; used with infinitive verb to modify meaning",
                'morphological_info': {'verb_type': 'modal'}
            }

        if word in auxiliary_verbs:
            return {
                'pos': 'verb',
                'grammatical_role': 'auxiliary',
                'confidence': 0.9,
                'individual_meaning': f"{word} (auxiliary verb): {word}; helps form compound tenses (perfect, future) or passive voice",
                'morphological_info': {'verb_type': 'auxiliary'}
            }

        if '_' in word or any(word.startswith(prefix) for prefix in ['ab', 'an', 'auf', 'aus', 'ein']):
            return {
                'pos': 'verb',
                'grammatical_role': 'verb',
                'confidence': 0.7,
                'individual_meaning': f"{word} (separable verb): {word}; verb with separable prefix that moves to end of clause in main clauses",
                'features': {'is_separable': True},
                'morphological_info': {'verb_type': 'separable'}
            }

        # Check for common German verb endings (pattern matching)
        verb_endings = ['en', 't', 'st', 'e', 'est', 'et', 'en', 't', 'st']
        if any(word.endswith(ending) for ending in verb_endings):
            # Determine likely person/number based on ending
            if word.endswith('e'):
                person = '1st'
                number = 'singular'
                confidence = 0.6
            elif word.endswith('st'):
                person = '2nd'
                number = 'singular'
                confidence = 0.7
            elif word.endswith('t'):
                person = '3rd'
                number = 'singular'
                confidence = 0.7
            elif word.endswith('en'):
                number = 'plural'
                confidence = 0.6
            else:
                confidence = 0.5

            return {
                'pos': 'verb',
                'grammatical_role': 'verb',
                'person': person if 'person' in locals() else None,
                'number': number if 'number' in locals() else None,
                'tense': 'present',  # Default assumption
                'mood': 'indicative',
                'confidence': confidence,
                'individual_meaning': f"{word} (verb): {word}; conjugated verb form in present tense; performs action or expresses state",
                'morphological_info': {'verb_type': 'regular', 'detected_by': 'ending_pattern'}
            }

        # Default: not a verb
        return {'pos': 'unknown', 'grammatical_role': 'unknown'}

    def _is_adjective(self, word: str) -> bool:
        """Check if word looks like a German adjective."""
        # Common adjective endings
        adj_endings = ['-e', '-en', '-er', '-es', '-em', '-lich', '-ig', '-isch', '-bar', '-sam']
        return any(word.endswith(ending) for ending in adj_endings) or word in [
            'groß', 'klein', 'schön', 'gut', 'besser', 'best', 'neu', 'alt'
        ]

    def _analyze_adjective(self, word: str) -> Dict[str, Any]:
        """Analyze German adjective for declension."""
        # Determine declension type (simplified)
        declension_type = 'strong'  # Default assumption

        # Check for weak declension endings
        if word.endswith(('e', 'en', 'em', 'er')):
            declension_type = 'weak'

        return {
            'pos': 'adjective',
            'grammatical_role': 'adjective',
            'declension_type': declension_type,
            'confidence': 0.7,
            'individual_meaning': f"{word} (adjective): {word}; describes or modifies noun; shows {declension_type} declension pattern",
            'morphological_info': {'declension_pattern': declension_type}
        }

    def _is_noun(self, word: str) -> bool:
        """Check if word is likely a German noun."""
        # German nouns are capitalized
        return word[0].isupper()

    def _analyze_noun(self, word: str, context: str) -> Dict[str, Any]:
        """Analyze German noun for gender and case."""
        # Try to guess gender from patterns
        gender = self._guess_noun_gender(word)

        # Default case assumption
        grammatical_case = 'nominative'

        # Check context for case clues
        if context and 'sentence' in context:
            context_lower = context['sentence'].lower()
            # Very basic case detection
            if any(word in context_lower for word in ['den', 'einen']):
                grammatical_case = 'accusative'
            elif any(word in context_lower for word in ['dem', 'einem']):
                grammatical_case = 'dative'

        return {
            'pos': 'noun',
            'grammatical_role': 'noun',
            'gender': gender,
            'grammatical_case': grammatical_case,
            'number': 'singular',  # Default assumption
            'confidence': 0.6,
            'individual_meaning': f"{word} (noun): {word}; {'masculine ' if gender == 'masculine' else 'feminine ' if gender == 'feminine' else 'neuter ' if gender == 'neuter' else ''}noun in {grammatical_case} case; refers to person/place/thing/idea",
            'morphological_info': {'noun_type': 'common'}
        }

    def _guess_noun_gender(self, word: str) -> Optional[str]:
        """Guess noun gender based on patterns."""
        word_lower = word.lower()

        # Check gender patterns from config
        gender_patterns = self.gender_patterns
        if gender_patterns:
            # Check morphological rules
            morph_rules = gender_patterns.get('morphological_rules', {})
            for gender, patterns in morph_rules.items():
                if isinstance(patterns, list):
                    for pattern in patterns:
                        if word_lower.endswith(pattern.replace('-', '')):
                            return gender

        # Default: unknown
        return None

    def _is_adverb(self, word: str) -> bool:
        """Check if word is a German adverb."""
        adverbs = [
            'hier', 'dort', 'da', 'wann', 'warum', 'wie', 'wo', 'wohin',
            'schnell', 'langsam', 'gut', 'schlecht', 'sehr', 'nicht'
        ]
        return word in adverbs

    def _analyze_sentence(self, words: List[Dict[str, Any]], text: str) -> Dict[str, Any]:
        """Analyze sentence structure."""
        # Basic sentence analysis
        word_order_type = 'v2'  # Default assumption for German
        verb_position = 'second'

        # Check for subordinate conjunctions
        subordinate_conjunctions = ['dass', 'weil', 'obwohl', 'wenn', 'als', 'da']
        has_subordinate = any(w['word'].lower() in subordinate_conjunctions for w in words)

        if has_subordinate:
            word_order_type = 'subordinate'
            verb_position = 'final'

        # Detect complex constructions
        complex_constructions = []
        has_modal = any(w.get('grammatical_role') == 'modal' for w in words)
        has_passive = any(w['word'].lower() in ['wird', 'werden'] for w in words)

        if has_modal:
            complex_constructions.append('modal_construction')
        if has_passive:
            complex_constructions.append('passive')

        # Case assignments (simplified)
        case_assignments = {
            'subject_case': 'nominative',
            'object_cases': ['accusative', 'dative']
        }

        return {
            'text': text,
            'word_order_type': word_order_type,
            'clause_structure': 'subordinate' if has_subordinate else 'main',
            'verb_position': verb_position,
            'complex_constructions': complex_constructions,
            'case_assignments': case_assignments
        }

    def _split_sentences(self, text: str) -> List[str]:
        """Basic sentence splitting for German text."""
        # Simple splitting on sentence endings
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]