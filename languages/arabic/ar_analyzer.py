# Arabic Grammar Analyzer
# Main facade for Arabic grammar analysis
# Clean Architecture implementation with RTL text handling

import logging
import re
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from languages.arabic.domain.ar_config import ArabicConfig
from languages.arabic.domain.ar_prompt_builder import ArabicPromptBuilder
from languages.arabic.domain.ar_response_parser import ArabicResponseParser
from languages.arabic.domain.ar_validator import ArabicValidator

# Import BaseGrammarAnalyzer
import sys
import os
# Try different import paths
try:
    from language_analyzers.base_analyzer import BaseGrammarAnalyzer, GrammarAnalysis, LanguageConfig
    from shared_utils import get_gemini_model, get_gemini_fallback_model
except ImportError:
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'streamlit_app'))
        from language_analyzers.base_analyzer import BaseGrammarAnalyzer, GrammarAnalysis, LanguageConfig
        from shared_utils import get_gemini_model, get_gemini_fallback_model
    except ImportError:
        # Fallback - define minimal classes if import fails
        @dataclass
        class LanguageConfig:
            code: str
            name: str
            native_name: str
            family: str
            script_type: str
            complexity_rating: str
            key_features: List[str]
            supported_complexity_levels: List[str]

        class BaseGrammarAnalyzer:
            def __init__(self, language_config):
                self.config = language_config
        class GrammarAnalysis:
            pass

logger = logging.getLogger(__name__)

@dataclass
class GrammarAnalysis:
    """Result of grammar analysis"""
    sentence: str
    target_word: str
    language_code: str
    complexity_level: str
    word_explanations: list
    explanations: Dict[str, str]
    confidence_score: float
    html_output: str
    color_scheme: Dict[str, str]
    is_rtl: bool = True
    text_direction: str = "rtl"

class ArAnalyzer(BaseGrammarAnalyzer):
    """
    Arabic Grammar Analyzer - Clean Architecture Implementation

    Key Features:
    - RTL (Right-to-Left) text handling
    - Root-based morphology analysis
    - Case marking (i'rab) recognition
    - Verb forms (abwab) identification
    - Definite article assimilation
    - Comprehensive Arabic linguistic features
    """

    VERSION = "1.0"
    LANGUAGE_CODE = "ar"
    LANGUAGE_NAME = "Arabic"

    def __init__(self,
                 config: Optional[ArabicConfig] = None,
                 prompt_builder: Optional[ArabicPromptBuilder] = None,
                 response_parser: Optional[ArabicResponseParser] = None,
                 validator: Optional[ArabicValidator] = None):

        # Dependency injection for testability - must be set before super().__init__()
        self.arabic_config = config or ArabicConfig()
        self.prompt_builder = prompt_builder or ArabicPromptBuilder(self.arabic_config)
        self.response_parser = response_parser or ArabicResponseParser(self.arabic_config)
        self.validator = validator or ArabicValidator(self.arabic_config)

        # Create language config for BaseGrammarAnalyzer
        language_config = LanguageConfig(
            code="ar",
            name="Arabic",
            native_name="العربية",
            family="Semitic",
            script_type="abjad",
            complexity_rating="high",
            key_features=["RTL text", "root-based morphology", "case marking", "verb forms"],
            supported_complexity_levels=["beginner", "intermediate", "advanced"]
        )

        # Store language config separately
        self.language_config = language_config

        # Initialize base class
        super().__init__(language_config)

        # Override config property for testing compatibility
        # (BaseGrammarAnalyzer sets self.config to language_config, but tests expect arabic_config)
        self._base_config = self.config  # Store the original
        self.config = self.arabic_config  # Override for tests

        # Validate configuration
        self._validate_setup()

    def get_grammar_prompt(self, complexity: str, sentence: str, target_word: str) -> str:
        """Generate Arabic-specific AI prompt for grammar analysis."""
        return self.prompt_builder.build_single_prompt(sentence, target_word, complexity)

    def parse_grammar_response(self, ai_response: str, complexity: str, sentence: str) -> Dict[str, Any]:
        """Parse AI response into standardized grammar analysis format."""
        # Parse using Arabic-specific parser
        parsed_result = self.response_parser.parse_response(
            ai_response, complexity, sentence, ""
        )

        # Convert to BaseGrammarAnalyzer format
        return {
            'grammatical_elements': parsed_result.get('grammatical_elements', {}),
            'explanations': parsed_result.get('explanations', {}),
            'color_scheme': parsed_result.get('color_scheme', {}),
            'html_output': parsed_result.get('html_output', ''),
            'confidence_score': parsed_result.get('confidence_score', 0.0),
            'word_explanations': parsed_result.get('word_explanations', [])
        }

    def _validate_setup(self):
        """Validate analyzer setup"""
        if not self.arabic_config.is_arabic_text("مرحبا"):  # Test Arabic text detection
            logger.warning("Arabic text detection may not be working properly")

    def analyze_grammar(self,
                       sentence: str,
                       target_word: str,
                       complexity: str = "intermediate",
                       gemini_api_key: str = "") -> GrammarAnalysis:
        """
        Analyze Arabic grammar for given sentence.

        CRITICAL: Arabic is RTL - word explanations are returned in reverse order
        for correct display in RTL reading direction.
        """
        try:
            logger.info(f"Analyzing Arabic sentence: {sentence}")

            # Validate inputs
            if not self._validate_inputs(sentence, target_word, complexity):
                return self._create_fallback_analysis(sentence, target_word, complexity)

            # Build prompt
            prompt = self.prompt_builder.build_single_prompt(sentence, target_word, complexity)

            # Call AI API
            ai_response = self._call_ai(prompt, gemini_api_key)
            if not ai_response:
                logger.warning("AI API call failed, using fallback")
                return self._create_fallback_analysis(sentence, target_word, complexity)

            # Parse response
            parsed_result = self.response_parser.parse_response(
                ai_response, complexity, sentence, target_word
            )

            # Validate result
            validated_result = self.validator.validate_result(parsed_result, sentence)

            # Build final analysis
            analysis = self._build_analysis_result(
                sentence, target_word, complexity, validated_result
            )

            logger.info(f"Arabic analysis completed with confidence: {analysis.confidence_score:.2f}")
            return analysis

        except Exception as e:
            logger.error(f"Error in Arabic grammar analysis: {e}")
            return self._create_fallback_analysis(sentence, target_word, complexity)

    def _validate_inputs(self, sentence: str, target_word: str, complexity: str) -> bool:
        """Validate input parameters"""
        if not sentence or not sentence.strip():
            logger.error("Empty sentence provided")
            return False

        if not target_word or not target_word.strip():
            logger.error("Empty target word provided")
            return False

        valid_complexities = ['beginner', 'intermediate', 'advanced']
        if complexity not in valid_complexities:
            logger.error(f"Invalid complexity: {complexity}")
            return False

        # Check if sentence contains Arabic text
        if not self.arabic_config.is_arabic_text(sentence):
            logger.warning("Sentence does not appear to contain Arabic text")

        return True

    def _call_ai(self, prompt: str, api_key: str) -> Optional[str]:
        """Call AI API for analysis"""
        if not api_key:
            logger.error("No API key provided")
            return None

        try:
            import google.generativeai as genai

            # Configure API
            genai.configure(api_key=api_key)

            # Try primary model first
            try:
                model = genai.GenerativeModel(get_gemini_model())
                response = model.generate_content(prompt)
                ai_response = response.text.strip()
            except Exception as primary_error:
                logger.warning(f"Primary model {get_gemini_model()} failed: {primary_error}")
                # Fallback to preview model
                model = genai.GenerativeModel(get_gemini_fallback_model())
                response = model.generate_content(prompt)
                ai_response = response.text.strip()

            return ai_response

        except Exception as e:
            logger.error(f"AI API call failed: {e}")
            return None

    def _select_model(self, prompt: str) -> str:
        """Select appropriate AI model based on prompt complexity"""
        # Use shared utility functions for model selection
        # Could add logic to use different models based on complexity
        return get_gemini_model()

    def _build_analysis_result(self,
                             sentence: str,
                             target_word: str,
                             complexity: str,
                             validated_result: Dict[str, Any]) -> GrammarAnalysis:
        """Build final GrammarAnalysis object"""

        # Get color scheme
        color_scheme = self.arabic_config.get_color_scheme(complexity)

        # Generate HTML output
        html_output = self._generate_html_output(
            sentence, validated_result['word_explanations'], color_scheme
        )

        # Extract explanations
        explanations = validated_result.get('explanations', {})

        return GrammarAnalysis(
            sentence=sentence,
            target_word=target_word,
            language_code=self.LANGUAGE_CODE,
            complexity_level=complexity,
            word_explanations=validated_result['word_explanations'],
            explanations=explanations,
            confidence_score=validated_result.get('confidence_score', 0.0),
            html_output=html_output,
            color_scheme=color_scheme,
            is_rtl=True,
            text_direction="rtl"
        )

    def _generate_html_output(self, sentence: str, word_explanations: List[List], color_scheme: Dict[str, str]) -> str:
        """Generate HTML output for Arabic text with inline word coloring and RTL support"""
        # For Arabic (RTL), generate colored sentence like other analyzers but with RTL direction

        # Create mapping of words to their explanations
        word_to_explanation = {}
        for exp in word_explanations:
            if len(exp) >= 4:
                word, role, color, meaning = exp
                # Clean word for consistent matching
                clean_word = re.sub(r'[.!?،؛:"\'()\[\]{}]', '', word)
                word_to_explanation[clean_word] = (word, role, color, meaning)

        # Split sentence into words (Arabic uses spaces like other languages)
        words_in_sentence = re.findall(r'\S+', sentence)

        html_parts = []
        html_parts.append('<div dir="rtl" style="font-family: Arial, sans-serif; text-align: right; direction: rtl;">')

        # Add the colored sentence
        html_parts.append('<p><strong>الجملة:</strong> ')
        sentence_parts = []

        for word in words_in_sentence:
            # Clean word for matching
            clean_word = re.sub(r'[.!?،؛:"\'()\[\]{}]', '', word)

            if clean_word in word_to_explanation:
                original_word, role, color, meaning = word_to_explanation[clean_word]
                # Escape curly braces and apply coloring
                safe_word = word.replace('{', '{{').replace('}', '}}')
                colored_word = f'<span style="color: {color}; font-weight: bold;" title="{role}: {meaning}">{safe_word}</span>'
                sentence_parts.append(colored_word)
            else:
                # Word without analysis
                safe_word = word.replace('{', '{{').replace('}', '}}')
                sentence_parts.append(f'<span style="color: #888888;">{safe_word}</span>')

        html_parts.append(' '.join(sentence_parts))
        html_parts.append('</p>')

        # Add word-by-word explanations in RTL reading order (same as sentence)
        # For RTL, explanations appear in the order they would be read
        html_parts.append('<div style="margin-top: 20px;">')
        html_parts.append('<strong>التحليل التفصيلي:</strong>')
        html_parts.append('<div style="direction: rtl; text-align: right;">')

        # Word explanations should be in RTL reading order (same as sentence)
        # Since word_explanations are in reading order, display them as-is
        for word, role, color, meaning in word_explanations:
            safe_word = word.replace('{', '{{').replace('}', '}}')
            html_parts.append(
                f'<div style="margin: 5px 0; padding: 5px; background-color: {color}20; border-radius: 3px;">'
                f'<strong style="color: {color};">{safe_word}</strong> - '
                f'<em>{role}</em>: {meaning}'
                f'</div>'
            )

        html_parts.append('</div>')
        html_parts.append('</div>')
        html_parts.append('</div>')

        return ''.join(html_parts)

    def _create_fallback_analysis(self,
                                sentence: str,
                                target_word: str,
                                complexity: str) -> GrammarAnalysis:
        """Create fallback analysis when main analysis fails"""
        logger.warning("Creating fallback analysis for Arabic")

        # Basic word tokenization
        words = sentence.split()
        color_scheme = self.arabic_config.get_color_scheme(complexity)

        # Create basic explanations (in reading order)
        word_explanations = []
        for word in words:  # Keep in reading order for RTL
            color = color_scheme.get('noun', '#708090')
            explanation = [word, 'noun (اسم)', color, 'Basic analysis - unable to perform detailed grammatical analysis']
            word_explanations.append(explanation)

        return GrammarAnalysis(
            sentence=sentence,
            target_word=target_word,
            language_code=self.LANGUAGE_CODE,
            complexity_level=complexity,
            word_explanations=word_explanations,
            explanations={
                'overall_structure': 'Basic sentence analysis (fallback mode)',
                'key_features': 'Unable to perform detailed Arabic grammatical analysis'
            },
            confidence_score=0.1,  # Low confidence for fallback
            html_output=self._generate_fallback_html(sentence, word_explanations),
            color_scheme=color_scheme,
            is_rtl=True,
            text_direction="rtl"
        )

    def _generate_fallback_html(self, sentence: str, word_explanations: list) -> str:
        """Generate fallback HTML output"""
        html = f'''
        <div dir="rtl" style="font-family: Arial, sans-serif; text-align: right;">
            <p><strong>تحليل أساسي للجملة:</strong> {sentence}</p>
            <p style="color: #ff6b6b;">⚠️ لم يتمكن النظام من إجراء تحليل نحوي مفصل</p>
            <p>الجملة تحتوي على {len(word_explanations)} كلمات</p>
        </div>
        '''
        return html

    # Public interface methods
    def get_supported_complexities(self) -> list:
        """Get supported complexity levels"""
        return ['beginner', 'intermediate', 'advanced']

    def get_language_info(self) -> Dict[str, Any]:
        """Get language information"""
        return {
            'code': self.LANGUAGE_CODE,
            'name': self.LANGUAGE_NAME,
            'native_name': self.arabic_config.language_name_native,
            'is_rtl': self.arabic_config.is_rtl,
            'script_type': self.arabic_config.script_type,
            'family': 'Afro-Asiatic (Semitic)',
            'features': list(self.arabic_config.linguistic_features.keys())
        }

    def batch_analyze_grammar(self, sentences: List[str], target_word: str, complexity: str, gemini_api_key: str) -> List[GrammarAnalysis]:
        """
        Batch analyze multiple Arabic sentences.

        For Arabic, we use the single sentence analysis approach since Arabic grammar
        analysis requires detailed per-sentence processing with RTL considerations.
        """
        results = []
        for sentence in sentences:
            try:
                analysis = self.analyze_grammar(sentence, target_word, complexity, gemini_api_key)
                results.append(analysis)
            except Exception as e:
                logger.error(f"Failed to analyze Arabic sentence: {e}")
                results.append(self._create_fallback_analysis(sentence, target_word, complexity))

        return results

    def validate_analysis(self, parsed_data: Dict[str, Any], original_sentence: str) -> float:
        """Validate Arabic grammar analysis quality (85% threshold required)"""
        try:
            words = parsed_data.get('word_explanations', [])
            elements = parsed_data.get('grammatical_elements', {})

            # Basic checks
            has_words = len(words) > 0
            has_elements = len(elements) > 0

            # Check Arabic script usage
            arabic_chars = sum(1 for char in original_sentence if 0x0600 <= ord(char) <= 0x06FF)
            arabic_ratio = arabic_chars / len(original_sentence) if original_sentence else 0

            # Word coverage
            sentence_words = original_sentence.split()
            analyzed_words = len(words)
            coverage = analyzed_words / len(sentence_words) if sentence_words else 0

            # Calculate confidence
            base_score = 0.8 if has_words else 0.5
            arabic_bonus = 0.1 if arabic_ratio > 0.5 else 0
            coverage_bonus = coverage * 0.1

            confidence = min(base_score + arabic_bonus + coverage_bonus, 1.0)
            return confidence

        except Exception as e:
            logger.error(f"Error validating Arabic analysis: {e}")
            return 0.0

    def get_color_scheme(self, complexity: str) -> Dict[str, str]:
        """Return color scheme for grammatical elements based on complexity level."""
        return self.arabic_config.get_color_scheme(complexity)

    def validate_arabic_text(self, text: str) -> bool:
        """Validate if text contains Arabic characters."""
        return self.arabic_config.is_arabic_text(text)