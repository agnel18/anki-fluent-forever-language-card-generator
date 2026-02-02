"""
German Grammar Analyzer - Main Facade
Implements comprehensive German linguistic analysis based on Duden grammar standards.

This analyzer provides complete German grammar analysis including:
- Case system (Nominativ, Akkusativ, Dativ, Genitiv)
- Gender agreement (Masculine, Feminine, Neuter)
- Adjective declension (Strong, Weak, Mixed)
- Verb conjugation (Strong, Weak, Mixed, Modal, Auxiliary)
- Preposition case requirements
- Word order analysis (V2 principle, subordinate clauses)
- Complex constructions (Passive, Subjunctive, Relative clauses)
- Morphological analysis (Compounds, Separable verbs, Reflexives)

Based on: Duden Grammatik der deutschen Gegenwartssprache
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path

from .de_config import DeConfig
from .de_prompt_builder import DePromptBuilder
from .de_response_parser import DeResponseParser
from .de_validator import DeValidator
from ..infrastructure.de_fallbacks import DeFallbacks

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class GrammarAnalysisResult:
    """Complete grammar analysis result for German text."""
    text: str
    words: List[Dict[str, Any]]
    sentences: List[Dict[str, Any]]
    overall_confidence: float
    analysis_metadata: Dict[str, Any]
    errors: List[str]
    warnings: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary format."""
        return {
            "text": self.text,
            "words": self.words,
            "sentences": self.sentences,
            "overall_confidence": self.overall_confidence,
            "analysis_metadata": self.analysis_metadata,
            "errors": self.errors,
            "warnings": self.warnings
        }


@dataclass
class WordAnalysis:
    """Detailed analysis for a single word."""
    word: str
    lemma: str
    pos: str  # Part of speech
    grammatical_role: str
    case: Optional[str] = None
    gender: Optional[str] = None
    number: Optional[str] = None
    person: Optional[str] = None
    tense: Optional[str] = None
    mood: Optional[str] = None
    declension_type: Optional[str] = None
    preposition_case: Optional[str] = None
    confidence: float = 0.0
    features: Dict[str, Any] = None
    morphological_info: Dict[str, Any] = None

    def __post_init__(self):
        if self.features is None:
            self.features = {}
        if self.morphological_info is None:
            self.morphological_info = {}


class DeAnalyzer:
    """
    Main German Grammar Analyzer implementing Clean Architecture.

    This analyzer provides comprehensive German linguistic analysis including:
    - Morphological analysis (case, gender, number, person)
    - Syntactic analysis (word order, clause structure)
    - Agreement validation (subject-verb, article-noun, adjective-noun)
    - Complex construction recognition (passive, subjunctive, compounds)
    """

    def __init__(self, config: Optional[DeConfig] = None):
        """
        Initialize the German analyzer.

        Args:
            config: German configuration. If None, creates default config.
        """
        self.config = config or DeConfig()
        self.prompt_builder = DePromptBuilder(self.config)
        self.response_parser = DeResponseParser(self.config)
        self.validator = DeValidator(self.config)
        self.fallbacks = DeFallbacks(self.config)

        logger.info("German Grammar Analyzer initialized")

    def analyze_grammar(self, text: str, complexity: str = "intermediate", target_word: Optional[str] = None) -> GrammarAnalysisResult:
        """
        Perform complete grammar analysis on German text.

        Args:
            text: German text to analyze
            complexity: Analysis complexity level (beginner, intermediate, advanced)
            target_word: Optional target word to focus analysis on

        Returns:
            Complete grammar analysis result
        """
        logger.info(f"Starting grammar analysis for text: {text[:50]}...")

        try:
            # Step 1: Build AI prompt for analysis
            prompt = self.prompt_builder.build_single_prompt(text, target_word or "", complexity)
            logger.debug(f"Generated prompt with {len(prompt)} characters")

            # Step 2: Get AI analysis (placeholder - would integrate with actual AI service)
            ai_response = self._get_ai_analysis(prompt)
            logger.debug(f"Received AI response with {len(ai_response) if ai_response else 0} characters")

            # Step 3: Parse AI response
            if ai_response:
                parsed_result = self.response_parser.parse_response(ai_response, text)
                logger.debug(f"Parsed response with {len(parsed_result.get('words', []))} words")
            else:
                parsed_result = None
                logger.warning("No AI response received, using fallback analysis")

            # Step 4: Apply fallback analysis if needed
            if not parsed_result or not parsed_result.get('words'):
                logger.info("Applying fallback analysis")
                parsed_result = self.fallbacks.analyze_german_text(text)
                parsed_result['fallback_used'] = True
            else:
                parsed_result['fallback_used'] = False

            # Step 5: Validate and enhance analysis
            validated_result = self.validator.validate_analysis(parsed_result, text)
            logger.debug(f"Validation completed with confidence: {validated_result.get('overall_confidence', 0)}")

            # Step 6: Build final result
            result = self._build_analysis_result(text, validated_result, complexity)

            logger.info(f"Analysis completed with {len(result.words)} words analyzed")
            return result

        except Exception as e:
            logger.error(f"Error during grammar analysis: {e}")
            # Return minimal result with error
            return GrammarAnalysisResult(
                text=text,
                words=[],
                sentences=[],
                overall_confidence=0.0,
                analysis_metadata={"error": str(e)},
                errors=[str(e)],
                warnings=["Analysis failed, using minimal result"]
            )

    def analyze_word(self, word: str, context: Optional[str] = None) -> WordAnalysis:
        """
        Analyze a single German word with optional context.

        Args:
            word: German word to analyze
            context: Optional sentence context

        Returns:
            Detailed word analysis
        """
        logger.debug(f"Analyzing word: {word}")

        try:
            # Use fallback analysis for single words
            word_analysis = self.fallbacks.analyze_german_word(word, context)

            # Convert to WordAnalysis dataclass
            return WordAnalysis(
                word=word_analysis.get('word', word),
                lemma=word_analysis.get('lemma', word),
                pos=word_analysis.get('pos', 'unknown'),
                grammatical_role=word_analysis.get('grammatical_role', 'unknown'),
                case=word_analysis.get('case'),
                gender=word_analysis.get('gender'),
                number=word_analysis.get('number'),
                person=word_analysis.get('person'),
                tense=word_analysis.get('tense'),
                mood=word_analysis.get('mood'),
                declension_type=word_analysis.get('declension_type'),
                preposition_case=word_analysis.get('preposition_case'),
                confidence=word_analysis.get('confidence', 0.0),
                features=word_analysis.get('features', {}),
                morphological_info=word_analysis.get('morphological_info', {})
            )

        except Exception as e:
            logger.error(f"Error analyzing word {word}: {e}")
            return WordAnalysis(
                word=word,
                lemma=word,
                pos="unknown",
                grammatical_role="unknown",
                confidence=0.0
            )

    def get_supported_features(self) -> Dict[str, List[str]]:
        """
        Get list of supported grammatical features.

        Returns:
            Dictionary of supported features by category
        """
        return {
            "cases": ["nominative", "accusative", "dative", "genitive"],
            "genders": ["masculine", "feminine", "neuter"],
            "numbers": ["singular", "plural"],
            "persons": ["1st", "2nd", "3rd"],
            "tenses": ["present", "preterite", "perfect", "pluperfect", "future", "future_perfect"],
            "moods": ["indicative", "subjunctive", "imperative"],
            "verb_types": ["strong", "weak", "mixed", "modal", "auxiliary", "reflexive", "separable"],
            "adjective_declensions": ["strong", "weak", "mixed"],
            "preposition_types": ["accusative", "dative", "genitive", "two_way"],
            "complex_constructions": [
                "passive_voice", "subjunctive_mood", "relative_clauses",
                "reflexive_verbs", "separable_verbs", "modal_constructions",
                "compound_nouns", "double_infinitive"
            ]
        }

    def _get_ai_analysis(self, prompt: str) -> Optional[str]:
        """
        Get analysis from AI service.

        This is a placeholder that would integrate with actual AI services
        like OpenAI, Anthropic, or local models.

        Args:
            prompt: Analysis prompt

        Returns:
            AI response or None if failed
        """
        # Placeholder implementation
        # In real implementation, this would call an AI service
        logger.warning("AI analysis not implemented - using fallback")
        return None

    def _build_analysis_result(self, text: str, validated_result: Dict[str, Any],
                             complexity: str) -> GrammarAnalysisResult:
        """
        Build final GrammarAnalysisResult from validated data.

        Args:
            text: Original text
            validated_result: Validated analysis data
            complexity: Analysis complexity level

        Returns:
            Complete analysis result
        """
        # Extract word analyses
        words = []
        for word_data in validated_result.get('words', []):
            word_analysis = WordAnalysis(
                word=word_data.get('word', ''),
                lemma=word_data.get('lemma', ''),
                pos=word_data.get('pos', 'unknown'),
                grammatical_role=word_data.get('grammatical_role', 'unknown'),
                case=word_data.get('case'),
                gender=word_data.get('gender'),
                number=word_data.get('number'),
                person=word_data.get('person'),
                tense=word_data.get('tense'),
                mood=word_data.get('mood'),
                declension_type=word_data.get('declension_type'),
                preposition_case=word_data.get('preposition_case'),
                confidence=word_data.get('confidence', 0.0),
                features=word_data.get('features', {}),
                morphological_info=word_data.get('morphological_info', {})
            )
            words.append(word_analysis)

        # Extract sentence analyses
        sentences = validated_result.get('sentences', [])

        # Build metadata
        metadata = {
            "complexity_level": complexity,
            "analysis_version": "1.0",
            "fallback_used": validated_result.get('fallback_used', False),
            "validation_performed": True,
            "supported_features": self.get_supported_features(),
            "grammar_concepts_version": "comprehensive"
        }

        return GrammarAnalysisResult(
            text=text,
            words=words,
            sentences=sentences,
            overall_confidence=validated_result.get('overall_confidence', 0.0),
            analysis_metadata=metadata,
            errors=validated_result.get('errors', []),
            warnings=validated_result.get('warnings', [])
        )

    def get_grammar_concepts_summary(self) -> Dict[str, Any]:
        """
        Get summary of implemented German grammar concepts.

        Returns:
            Summary of supported grammar features
        """
        return {
            "case_system": {
                "implemented": ["nominative", "accusative", "dative", "genitive"],
                "complexity": "full_4_case_system"
            },
            "gender_system": {
                "implemented": ["masculine", "feminine", "neuter"],
                "agreement_patterns": ["article_noun", "adjective_noun", "pronoun_noun"]
            },
            "verb_system": {
                "conjugation_types": ["strong", "weak", "mixed", "modal", "auxiliary"],
                "ablaut_series": ["7_main_series"],
                "special_constructions": ["separable_verbs", "reflexive_verbs", "double_infinitive"]
            },
            "adjective_declension": {
                "types": ["strong", "weak", "mixed"],
                "endings": "complete_paradigm"
            },
            "preposition_system": {
                "types": ["accusative_only", "dative_only", "genitive_only", "two_way"],
                "contractions": "supported"
            },
            "word_order": {
                "v2_principle": "implemented",
                "subordinate_clauses": "verb_final",
                "scrambling": "recognized"
            },
            "complex_constructions": [
                "passive_voice", "subjunctive_mood", "relative_clauses",
                "compound_nouns", "modal_constructions"
            ],
            "morphological_features": [
                "umlaut_changes", "compound_formation", "derivation",
                "separable_prefixes", "case_marking"
            ]
        }