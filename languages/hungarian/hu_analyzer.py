# languages/hungarian/hu_analyzer.py
"""
Hungarian Grammar Analyzer - Clean Architecture Facade

Implements the Hungarian grammar analyzer following the French v2.0 gold standard.
Orchestrates domain components for grammar analysis of Hungarian text.

HUNGARIAN-SPECIFIC FEATURES:
- Agglutinative morphology: extensive suffixing with vowel harmony
- 18 grammatical cases expressed by suffixes on nouns
- Definite vs indefinite verb conjugation (two paradigms)
- Preverbs (igekötők): meg-, el-, ki-, be-, fel-, le-, vissza-, össze-
- Postpositions instead of prepositions
- Possessive suffixes on nouns
- Flexible word order with topic-focus structure
- No grammatical gender
"""

import logging
import re
import time
from typing import Dict, List, Any, Optional
from pathlib import Path

from streamlit_app.language_analyzers.base_analyzer import BaseGrammarAnalyzer, LanguageConfig, GrammarAnalysis

from .domain.hu_config import HuConfig
from .domain.hu_prompt_builder import HuPromptBuilder
from .domain.hu_response_parser import HuResponseParser
from .domain.hu_validator import HuValidator
from .infrastructure.hu_fallbacks import HuFallbacks

logger = logging.getLogger(__name__)


class HuAnalyzer(BaseGrammarAnalyzer):
    """
    Grammar analyzer for Hungarian — Clean Architecture.

    Hungarian is agglutinative (Uralic/Finno-Ugric family) with SVO default order,
    Latin script with diacritics, and extensive case suffixing with vowel harmony.
    """

    VERSION = "1.0"
    LANGUAGE_CODE = "hu"
    LANGUAGE_NAME = "Hungarian"

    def __init__(self):
        self.hu_config = HuConfig()
        self.hu_fallbacks = HuFallbacks(self.hu_config)
        self.prompt_builder = HuPromptBuilder(self.hu_config)
        self.response_parser = HuResponseParser(self.hu_config, self.hu_fallbacks)
        self.validator = HuValidator(self.hu_config)

        config = LanguageConfig(
            code="hu",
            name="Hungarian",
            native_name="magyar",
            family="Uralic",
            script_type="latin_extended",
            complexity_rating="high",
            key_features=[
                'agglutinative_morphology', 'vowel_harmony', '18_grammatical_cases',
                'definite_indefinite_conjugation', 'preverbs', 'postpositions',
                'possessive_suffixes', 'topic_focus_structure', 'no_grammatical_gender'
            ],
            supported_complexity_levels=['beginner', 'intermediate', 'advanced']
        )
        super().__init__(config)

    def analyze_grammar(self, sentence: str, target_word: str, complexity: str, gemini_api_key: str) -> GrammarAnalysis:
        """Analyze grammar for a single Hungarian sentence."""
        try:
            start_time = time.time()

            logger.info(f"Hungarian Analysis: Starting for '{sentence[:50]}...' (complexity: {complexity})")

            prompt = self.prompt_builder.build_single_prompt(sentence, target_word, complexity)
            ai_response = self._call_ai(prompt, gemini_api_key)
            result = self.response_parser.parse_response(ai_response, complexity, sentence, target_word)
            validated_result = self.validator.validate_result(result, sentence)

            # Explanation quality check
            quality_validation = self.validator.validate_explanation_quality(validated_result)
            validated_result['explanation_quality'] = quality_validation

            base_confidence = validated_result.get('confidence', 0.5)
            quality_score = quality_validation.get('quality_score', 1.0)
            adjusted_confidence = min(base_confidence * quality_score, 1.0)
            validated_result['confidence'] = adjusted_confidence

            html_output = self._generate_html_output(validated_result, sentence, complexity)

            analysis_result = GrammarAnalysis(
                sentence=sentence,
                target_word=target_word,
                language_code=self.language_code,
                complexity_level=complexity,
                grammatical_elements=validated_result.get('elements', {}),
                explanations=validated_result.get('explanations', {}),
                word_explanations=validated_result.get('word_explanations', []),
                color_scheme=self.get_color_scheme(complexity),
                html_output=html_output,
                confidence_score=adjusted_confidence
            )

            processing_time = time.time() - start_time
            logger.info(f"Hungarian Analysis: Completed in {processing_time:.2f}s, confidence: {adjusted_confidence:.2f}")

            return analysis_result

        except Exception as e:
            logger.error(f"Analysis failed for '{sentence}': {e}")
            fallback_result = self.hu_fallbacks.create_fallback(sentence, complexity)
            html_output = self._generate_html_output(fallback_result, sentence, complexity)
            return GrammarAnalysis(
                sentence=sentence,
                target_word=target_word or "",
                language_code=self.language_code,
                complexity_level=complexity,
                grammatical_elements=fallback_result.get('elements', {}),
                explanations=fallback_result.get('explanations', {}),
                color_scheme=self.get_color_scheme(complexity),
                html_output=html_output,
                confidence_score=fallback_result.get('confidence', 0.3),
                word_explanations=fallback_result.get('word_explanations', [])
            )

    def batch_analyze_grammar(self, sentences: List[str], target_word: str, complexity: str, gemini_api_key: str) -> List[GrammarAnalysis]:
        """Analyze grammar for multiple Hungarian sentences."""
        logger.info(f"Batch analyze: {len(sentences)} sentences")
        try:
            prompt = self.prompt_builder.build_batch_prompt(sentences, target_word, complexity)
            ai_response = self._call_ai(prompt, gemini_api_key)
            results = self.response_parser.parse_batch_response(ai_response, sentences, complexity, target_word)

            grammar_analyses = []
            for result, sentence in zip(results, sentences):
                validated_result = self.validator.validate_result(result, sentence)
                html_output = self._generate_html_output(validated_result, sentence, complexity)

                grammar_analyses.append(GrammarAnalysis(
                    sentence=sentence,
                    target_word=target_word or "",
                    language_code=self.language_code,
                    complexity_level=complexity,
                    grammatical_elements=validated_result.get('elements', {}),
                    explanations=validated_result.get('explanations', {}),
                    color_scheme=self.get_color_scheme(complexity),
                    html_output=html_output,
                    confidence_score=validated_result.get('confidence', 0.0),
                    word_explanations=validated_result.get('word_explanations', [])
                ))

            return grammar_analyses
        except Exception as e:
            logger.error(f"Batch analysis failed: {e}")
            fallback_analyses = []
            for sentence in sentences:
                fallback_result = self.hu_fallbacks.create_fallback(sentence, complexity)
                html_output = self._generate_html_output(fallback_result, sentence, complexity)
                fallback_analyses.append(GrammarAnalysis(
                    sentence=sentence,
                    target_word=target_word or "",
                    language_code=self.language_code,
                    complexity_level=complexity,
                    grammatical_elements=fallback_result.get('elements', {}),
                    explanations=fallback_result.get('explanations', {}),
                    color_scheme=self.get_color_scheme(complexity),
                    html_output=html_output,
                    confidence_score=fallback_result.get('confidence', 0.3),
                    word_explanations=fallback_result.get('word_explanations', [])
                ))
            return fallback_analyses

    def _call_ai(self, prompt: str, gemini_api_key: str) -> str:
        """Call Google Gemini AI for Hungarian grammar analysis."""
        # LAZY IMPORT — critical for analyzer registry discovery
        from streamlit_app.shared_utils import get_gemini_model, get_gemini_fallback_model, get_gemini_api

        max_retries = 3
        base_delay = 1.0

        for attempt in range(max_retries):
            try:
                api = get_gemini_api()
                api.configure(api_key=gemini_api_key)

                try:
                    response = api.generate_content(
                        model=get_gemini_model(),
                        contents=prompt,
                        config={'max_output_tokens': 20000, 'temperature': 0.1}
                    )
                    return response.text.strip()

                except Exception as primary_error:
                    logger.warning(f"Primary model failed (attempt {attempt + 1}): {str(primary_error)[:200]}")
                    try:
                        response = api.generate_content(
                            model=get_gemini_fallback_model(),
                            contents=prompt,
                            config={'max_output_tokens': 20000, 'temperature': 0.1}
                        )
                        return response.text.strip()

                    except Exception as fallback_error:
                        logger.warning(f"Fallback model also failed (attempt {attempt + 1}): {str(fallback_error)[:200]}")
                        if attempt < max_retries - 1:
                            delay = base_delay * (2 ** attempt)
                            time.sleep(delay)
                        else:
                            raise fallback_error

            except Exception as e:
                logger.error(f"All models failed on attempt {attempt + 1}: {str(e)[:200]}")
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    time.sleep(delay)
                else:
                    return '{"error": "AI service unavailable", "sentence": "error"}'

        return '{"error": "AI service unavailable", "sentence": "error"}'

    def get_color_scheme(self, complexity: str) -> Dict[str, str]:
        """Return color scheme for Hungarian grammatical elements."""
        return self.hu_config.get_color_scheme(complexity)

    def get_grammar_prompt(self, complexity: str, sentence: str, target_word: str) -> str:
        """Generate Hungarian-specific AI prompt for grammar analysis."""
        return self.prompt_builder.build_single_prompt(sentence, target_word, complexity)

    def parse_grammar_response(self, ai_response: str, complexity: str, sentence: str) -> Dict[str, Any]:
        """Parse AI response into standardized grammar analysis format."""
        return self.response_parser.parse_response(ai_response, complexity, sentence)

    def validate_analysis(self, parsed_data: Dict[str, Any], original_sentence: str) -> float:
        """Validate analysis quality and return confidence score."""
        result = self.validator.validate_result(parsed_data, original_sentence)
        return result.get('confidence', 0.0)

    def _generate_html_output(self, parsed_data: Dict[str, Any], sentence: str, complexity: str) -> str:
        """
        Generate HTML output for Hungarian text with inline color styling for Anki.

        Hungarian uses spaces between words, so we color each word based on
        the word_explanations from AI analysis.
        """
        explanations = parsed_data.get('word_explanations', [])
        color_scheme = self.get_color_scheme(complexity)

        if not explanations:
            return sentence

        # Build HTML by iterating through word explanations in order
        html_parts = []
        covered = 0  # Track position in original sentence

        for exp in explanations:
            if len(exp) < 3:
                continue

            word = exp[0]
            role = exp[1]
            category = self._map_grammatical_role_to_category(role)
            color = color_scheme.get(category, color_scheme.get('other', '#AAAAAA'))

            # Find word in sentence starting from current position
            idx = sentence.find(word, covered)
            if idx == -1:
                idx = sentence.find(word)

            if idx != -1:
                # Add any uncovered characters before this word (spaces, etc.)
                if idx > covered:
                    uncovered = sentence[covered:idx]
                    html_parts.append(uncovered)

                # Add the colored word
                html_parts.append(f'<span style="color: {color}; font-weight: bold;">{word}</span>')
                covered = idx + len(word)
            else:
                html_parts.append(f'<span style="color: {color}; font-weight: bold;">{word}</span>')

        # Add any remaining characters
        if covered < len(sentence):
            remaining = sentence[covered:]
            html_parts.append(remaining)

        return ''.join(html_parts)

    def _map_grammatical_role_to_category(self, role: str) -> str:
        """Map specific grammatical roles to color categories."""
        hierarchy = self.hu_config.grammatical_roles.get('role_hierarchy', {})
        return hierarchy.get(role, role)
