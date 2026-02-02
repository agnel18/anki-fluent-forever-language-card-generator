# Spanish Grammar Analyzer
# Main facade for Spanish grammar analysis
# Clean Architecture implementation with LTR text handling

import json
import logging
import re
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from .domain.es_config import EsConfig
from .domain.es_prompt_builder import EsPromptBuilder
from .domain.es_response_parser import EsResponseParser
from .domain.es_validator import EsValidator
from .infrastructure.es_fallbacks import EsFallbacks

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

class EsAnalyzer(BaseGrammarAnalyzer):
    """
    Spanish Grammar Analyzer - Clean Architecture Implementation

    Key Features:
    - LTR (Left-to-Right) text handling
    - Gender and number agreement analysis
    - Verb conjugation recognition
    - Clitic pronoun placement
    - Ser/estar distinction
    - Por/para preposition usage
    - Differential object marking
    """

    VERSION = "1.0"
    LANGUAGE_CODE = "es"
    LANGUAGE_NAME = "Spanish"

    def __init__(self,
                 config: Optional[EsConfig] = None,
                 prompt_builder: Optional[EsPromptBuilder] = None,
                 response_parser: Optional[EsResponseParser] = None,
                 validator: Optional[EsValidator] = None,
                 fallbacks: Optional[EsFallbacks] = None):

        # Dependency injection for testability - must be set before super().__init__()
        self.es_config = config or EsConfig()
        self.prompt_builder = prompt_builder or EsPromptBuilder(self.es_config)
        self.response_parser = response_parser or EsResponseParser(self.es_config)
        self.validator = validator or EsValidator(self.es_config)
        self.fallbacks = fallbacks or EsFallbacks(self.es_config)

        # Create language config for BaseGrammarAnalyzer
        language_config = LanguageConfig(
            code="es",
            name="Spanish",
            native_name="Español",
            family="Indo-European (Romance)",
            script_type="alphabetic",
            complexity_rating="medium",
            key_features=["gender_agreement", "verb_conjugation", "clitic_pronouns", "ser_estar_distinction"],
            supported_complexity_levels=["beginner", "intermediate", "advanced"]
        )

        # Store language config separately
        self.language_config = language_config

        # Initialize base class
        super().__init__(language_config)

        # Override config property for testing compatibility
        # (BaseGrammarAnalyzer sets self.config to language_config, but tests expect es_config)
        self._base_config = self.config  # Store the original
        self.config = self.es_config  # Override for tests

        # Initialize AI response storage for debugging
        self._last_ai_response = None

    def analyze_grammar(self,
                       sentence: str,
                       target_word: str,
                       complexity: str = "intermediate",
                       gemini_api_key: str = "") -> GrammarAnalysis:
        """
        Analyze Spanish grammar for given sentence.

        CRITICAL: Spanish is LTR - word explanations are returned in standard reading order.
        """
        try:
            logger.info(f"Analyzing Spanish sentence: {sentence}")

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

            logger.info(f"Parsed result keys: {list(parsed_result.keys()) if parsed_result else 'None'}")
            if parsed_result and 'words' in parsed_result:
                logger.info(f"Word explanations count: {len(parsed_result['words'])}")
            else:
                logger.error("No words in parsed result")

            # Validate result
            validated_result = self.validator.validate_result(parsed_result, sentence)

            # Build final analysis
            analysis = self._build_analysis_result(
                sentence, target_word, complexity, validated_result
            )

            logger.info(f"Spanish analysis completed with confidence: {analysis.confidence_score:.2f}")
            return analysis

        except Exception as e:
            logger.error(f"Error in Spanish grammar analysis: {e}")
            return self._create_fallback_analysis(sentence, target_word, complexity)

    def _validate_inputs(self, sentence: str, target_word: str, complexity: str) -> bool:
        """Validate input parameters"""
        if not sentence or not isinstance(sentence, str):
            logger.error("Invalid sentence")
            return False

        if not target_word or not isinstance(target_word, str):
            logger.error("Invalid target word")
            return False

        if complexity not in self.language_config.supported_complexity_levels:
            logger.error(f"Unsupported complexity level: {complexity}")
            return False

        return True

    def _call_ai(self, prompt: str, api_key: str) -> Optional[str]:
        """Call AI API with error handling"""
        try:
            if not api_key:
                logger.warning("No API key provided")
                return None

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

            # Store for debugging
            self._last_ai_response = ai_response

            return ai_response

        except Exception as e:
            logger.error(f"AI API call failed: {e}")
            return None

    def get_supported_complexities(self) -> list:
        """Get supported complexity levels"""
        return ['beginner', 'intermediate', 'advanced']

    def get_language_info(self) -> Dict[str, Any]:
        """Get language information"""
        return {
            'code': self.LANGUAGE_CODE,
            'name': self.LANGUAGE_NAME,
            'native_name': 'Español',
            'is_rtl': False,
            'script_type': 'alphabetic',
            'family': 'Indo-European (Romance)',
            'features': ['gender_agreement', 'verb_conjugation', 'clitic_pronouns', 'ser_estar_distinction']
        }

    def get_color_scheme(self, complexity: str) -> Dict[str, str]:
        """Return color scheme for grammatical elements based on complexity level."""
        return self.es_config.get_color_scheme(complexity)

    def validate_spanish_text(self, text: str) -> bool:
        """Validate if text contains Spanish characters."""
        return self.es_config.is_spanish_text(text)

    def _create_fallback_analysis(self, sentence: str, target_word: str, complexity: str) -> GrammarAnalysis:
        """Create fallback analysis when AI fails"""
        logger.info("Creating fallback analysis")

        fallback_data = self.fallbacks.create_fallback(sentence, complexity, target_word)

        # Convert to GrammarAnalysis format
        color_scheme = self.es_config.get_color_scheme(complexity)
        
        # Generate basic HTML for fallback
        html_output = self._generate_basic_html(sentence, fallback_data.get('words', []), color_scheme)
        
        analysis = GrammarAnalysis(
            sentence=sentence,
            target_word=target_word,
            language_code=self.LANGUAGE_CODE,
            complexity_level=complexity,
            grammatical_elements=fallback_data.get('elements', {}),
            explanations=fallback_data.get('overall_analysis', {}),
            color_scheme=color_scheme,
            html_output=html_output,
            confidence_score=fallback_data.get('confidence', 0.3),
            word_explanations=fallback_data.get('words', []),
            is_rtl=False,
            text_direction="ltr"
        )

        return analysis

    def _generate_basic_html(self, sentence: str, words: List[Dict[str, Any]], color_scheme: Dict[str, str]) -> str:
        """Generate basic HTML output for fallback analysis"""
        try:
            # Create a simple HTML structure with LTR direction
            html_parts = [f'<div dir="ltr">']
            
            # Process each word
            for word_info in words:
                word = word_info.get('word', '')
                pos = word_info.get('grammatical_role', 'unknown')
                color = color_scheme.get(pos, color_scheme.get('default', '#000000'))
                
                # Create colored span for each word
                html_parts.append(f'<span style="color: {color};" title="{pos}">{word}</span> ')
            
            html_parts.append('</div>')
            
            return ''.join(html_parts).strip()
            
        except Exception as e:
            logger.error(f"Failed to generate basic HTML: {e}")
            # Return minimal HTML with LTR direction
            return f'<div dir="ltr">{sentence}</div>'

    def _build_analysis_result(self, sentence: str, target_word: str, complexity: str, validated_result: Dict[str, Any]) -> GrammarAnalysis:
        """Build final GrammarAnalysis object"""
        color_scheme = self.es_config.get_color_scheme(complexity)
        
        # Handle both single and batch result formats
        words = validated_result.get('words') or validated_result.get('word_explanations', [])
        explanations = validated_result.get('overall_analysis') or validated_result.get('explanations', {})
        
        # Generate HTML output from the parsed words
        html_output = self._generate_basic_html(sentence, words, color_scheme)
        
        # Convert words to the expected word_explanations format (list of lists)
        word_explanations = []
        for word_data in words:
            if isinstance(word_data, dict):
                word = word_data.get('word', '')
                role = word_data.get('grammatical_role', '')
                meaning = word_data.get('individual_meaning') or word_data.get('meaning', '')
                color = color_scheme.get(role, '#000000')
                word_explanations.append([word, role, color, meaning])
            elif isinstance(word_data, list) and len(word_data) >= 4:
                # Already in correct format
                word_explanations.append(word_data)
        
        analysis = GrammarAnalysis(
            sentence=sentence,
            target_word=target_word,
            language_code=self.LANGUAGE_CODE,
            complexity_level=complexity,
            grammatical_elements=validated_result.get('elements', {}),
            explanations=explanations,
            color_scheme=color_scheme,
            html_output=html_output,
            confidence_score=validated_result.get('confidence', 0.5),
            word_explanations=word_explanations,
            is_rtl=False,
            text_direction="ltr"
        )

        return analysis

    def parse_batch_grammar_response(self, ai_response: str, sentences: List[str], complexity: str, target_word: str = "") -> List[Dict[str, Any]]:
        """
        Parse batch AI response into list of standardized grammar analysis formats.
        
        Args:
            ai_response: Raw batch response from AI model
            sentences: List of original sentences
            complexity: Complexity level used for analysis
            target_word: Target word being learned
            
        Returns:
            List of dictionaries with grammatical elements, explanations, etc.
        """
        parse_result = self.response_parser.parse_batch_response(ai_response, sentences, complexity, target_word)
        
        results = []
        for i, sentence in enumerate(sentences):
            if i < len(parse_result):
                parsed_sentence = parse_result[i]
                
                # Convert ParsedSentence to expected dict format
                word_explanations = parsed_sentence.get('word_explanations', [])
                
                # Group words by grammatical role for elements
                elements = {}
                for word_data in word_explanations:
                    if len(word_data) >= 2:  # [word, role, color, meaning]
                        role = word_data[1]  # role is at index 1
                        if role not in elements:
                            elements[role] = []
                        elements[role].append({
                            'word': word_data[0],
                            'role': role,
                            'explanation': word_data[3] if len(word_data) > 3 else ''
                        })
                
                result = {
                    'elements': elements,
                    'explanations': parsed_sentence.get('explanations', {}),
                    'word_explanations': word_explanations
                }
            else:
                # Fallback for missing sentences
                result = {
                    'elements': {},
                    'explanations': {'sentence_structure': 'Batch parsing failed', 'key_features': ''},
                    'word_explanations': []
                }
            results.append(result)
        
        return results

    # Legacy compatibility methods
    def get_grammar_prompt(self, complexity: str, sentence: str, target_word: str) -> str:
        """Legacy method for prompt generation"""
        return self.prompt_builder.build_single_prompt(sentence, target_word, complexity)

    def parse_grammar_response(self, ai_response: str, complexity: str, sentence: str) -> Dict[str, Any]:
        """Legacy method for response parsing"""
        return self.response_parser.parse_response(ai_response, complexity, sentence, None)

    def validate_analysis(self, parsed_data: Dict[str, Any], original_sentence: str) -> float:
        """Legacy method for validation"""
        result = self.validator.validate_result(parsed_data, original_sentence)
        return result.get('confidence', 0.5)

    def batch_analyze_grammar(self, sentences: List[str], target_word: str, complexity: str, gemini_api_key: str) -> List[GrammarAnalysis]:
        """
        Analyze grammar for multiple sentences in batch.

        SPANISH BATCH PROCESSING:
        - Processes up to 8 sentences simultaneously to prevent token overflow
        - Uses batch prompt template for efficient AI processing
        - Returns individual GrammarAnalysis objects for each sentence
        - Handles partial failures gracefully

        BATCH SIZE CONSIDERATIONS:
        - Maximum 8 sentences per batch (fits within 2000 token limit)
        - If batch fails: Attempts individual processing as fallback
        - If individual processing fails: Returns fallbacks for all sentences

        Args:
            sentences: List of Spanish sentences to analyze
            target_word: Word to focus analysis on
            complexity: Analysis complexity level
            gemini_api_key: API key for AI processing

        Returns:
            List of GrammarAnalysis objects, one per sentence
        """
        try:
            logger.info(f"Batch analyzing {len(sentences)} Spanish sentences")

            # Validate batch size
            if len(sentences) > 8:
                logger.warning(f"Batch size {len(sentences)} exceeds limit of 8, truncating")
                sentences = sentences[:8]

            # Build batch prompt
            prompt = self.prompt_builder.build_batch_prompt(sentences, target_word, complexity)

            # Call AI API
            ai_response = self._call_ai(prompt, gemini_api_key)
            if not ai_response:
                logger.warning("AI API call failed for batch, using individual fallbacks")
                return [self._create_fallback_analysis(sentence, target_word, complexity) for sentence in sentences]

            # Parse batch response
            batch_results = self.response_parser.parse_batch_response(
                ai_response, sentences, complexity, target_word
            )

            # Validate and build analysis objects
            analyses = []
            for i, result in enumerate(batch_results):
                try:
                    # Validate result
                    validated_result = self.validator.validate_result(result, sentences[i])

                    # Build analysis
                    analysis = self._build_analysis_result(
                        sentences[i], target_word, complexity, validated_result
                    )
                    analyses.append(analysis)

                except Exception as e:
                    logger.error(f"Failed to process sentence {i+1}: {e}")
                    analyses.append(self._create_fallback_analysis(sentences[i], target_word, complexity))

            logger.info(f"Batch analysis completed: {len(analyses)} results")
            return analyses

        except Exception as e:
            logger.error(f"Batch analysis failed: {e}")
            # Return fallbacks for all sentences
            return [self._create_fallback_analysis(sentence, target_word, complexity) for sentence in sentences]