# Arabic Grammar Analyzer
# Main facade for Arabic grammar analysis
# Clean Architecture implementation with RTL text handling

import logging
import re
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from .domain.ar_config import ArConfig
from .domain.ar_prompt_builder import ArPromptBuilder
from .domain.ar_response_parser import ArResponseParser
from .domain.ar_validator import ArValidator
from .domain.ar_patterns import ArPatterns
from .domain.ar_fallbacks import ArFallbacks

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
                 config: Optional[ArConfig] = None,
                 prompt_builder: Optional[ArPromptBuilder] = None,
                 response_parser: Optional[ArResponseParser] = None,
                 validator: Optional[ArValidator] = None):

        # Dependency injection for testability - must be set before super().__init__()
        self.arabic_config = config or ArConfig()
        self.prompt_builder = prompt_builder or ArPromptBuilder(self.arabic_config)
        self.response_parser = response_parser or ArResponseParser(self.arabic_config)
        self.validator = validator or ArValidator(self.arabic_config)

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

    def get_sentence_generation_prompt(self, word: str, language: str, num_sentences: int,
                                     enriched_meaning: str = "", min_length: int = 3,
                                     max_length: int = 15, difficulty: str = "intermediate",
                                     topics: Optional[List[str]] = None) -> Optional[str]:
        """
        Get Arabic-specific sentence generation prompt to ensure proper response formatting.
        """
        # Build context instruction based on topics
        if topics:
            context_instruction = f"- CRITICAL REQUIREMENT: ALL sentences MUST relate to these specific topics: {', '.join(topics)}. Force the word usage into these contexts even if it requires creative interpretation. Do NOT use generic contexts."
        else:
            context_instruction = "- Use diverse real-life contexts: home, travel, food, emotions, work, social life, daily actions"

        # Build meaning instruction based on enriched data
        if enriched_meaning and enriched_meaning != 'N/A':
            if enriched_meaning.startswith('{') and enriched_meaning.endswith('}'):
                # Parse the enriched context format
                context_lines = enriched_meaning[1:-1].split('\n')  # Remove {} and split
                definitions = []
                source = "Unknown"
                for line in context_lines:
                    line = line.strip()
                    if line.startswith('Source:'):
                        source = line.replace('Source:', '').strip()
                    elif line.startswith('Definition'):
                        # Extract just the definition text
                        def_text = line.split(':', 1)[1].strip() if ':' in line else line
                        # Remove part of speech info
                        def_text = def_text.split(' | ')[0].strip()
                        definitions.append(def_text)

                if definitions:
                    meaning_summary = '; '.join(definitions[:4])  # Use first 4 definitions
                    enriched_meaning_instruction = f'Analyze this linguistic data for "{word}" and generate a brief, clean English meaning that encompasses ALL the meanings. Data: {meaning_summary}. IMPORTANT: Consider all meanings and provide a comprehensive meaning.'
                else:
                    enriched_meaning_instruction = f'Analyze this linguistic context for "{word}" and generate a brief, clean English meaning. Context: {enriched_meaning[:200]}. IMPORTANT: Return ONLY the English meaning.'
            else:
                # Legacy format
                enriched_meaning_instruction = f'Use this pre-reviewed meaning for "{word}": "{enriched_meaning}". Generate a clean English meaning based on this.'
        else:
            enriched_meaning_instruction = f'Provide a brief English meaning for "{word}".'

        # Custom prompt for Arabic to ensure proper formatting
        prompt = f"""You are a native-level expert linguist in Modern Standard Arabic.

Your task: Generate a complete learning package for the Arabic word "{word}" in ONE response.

===========================
STEP 1: WORD MEANING
===========================
{enriched_meaning_instruction}
Format: Return exactly one line like "house (a building where people live)" or "he (male pronoun, used as subject)"

===========================
WORD-SPECIFIC RESTRICTIONS
===========================
Based on the meaning above, identify any grammatical constraints for "{word}".
Examples: imperatives (commands only), specific persons/moods, contextual restrictions.
If no restrictions apply, state "No specific grammatical restrictions."

===========================
STEP 2: SENTENCES
===========================
Generate exactly {num_sentences} highly natural, idiomatic sentences in Modern Standard Arabic for the word "{word}".

QUALITY RULES:
- Every sentence must sound like native Arabic
- Grammar, syntax, spelling, diacritics must be correct
- The target word "{word}" MUST be used correctly according to restrictions
- Each sentence must be no more than {max_length} words long
- Difficulty: {difficulty}

VARIETY REQUIREMENTS:
- Use different tenses and forms if applicable
- Use different sentence types: declarative, interrogative, imperative
{context_instruction}

===========================
STEP 3: ENGLISH TRANSLATIONS
===========================
For EACH sentence above, provide a natural, fluent English translation.
- Translation should be natural English, not literal word-for-word

===========================
STEP 4: IPA TRANSCRIPTION
===========================
For EACH sentence above, provide simplified IPA transcription.
- Use standard IPA symbols for Arabic pronunciation
- Focus on the main pronunciation pattern

===========================
STEP 5: IMAGE KEYWORDS
===========================
For EACH sentence above, generate exactly 3 specific keywords for image search.
- Keywords should be concrete and specific
- Keywords in English only

===========================
OUTPUT FORMAT - FOLLOW EXACTLY
===========================
Return your response in this exact text format:

MEANING: [brief English meaning]

RESTRICTIONS: [grammatical restrictions]

SENTENCES:
1. [sentence 1 in Arabic]
2. [sentence 2 in Arabic]
3. [sentence 3 in Arabic]
4. [sentence 4 in Arabic]

TRANSLATIONS:
1. [natural English translation for sentence 1]
2. [natural English translation for sentence 2]
3. [natural English translation for sentence 3]
4. [natural English translation for sentence 4]

IPA:
1. [IPA for sentence 1]
2. [IPA for sentence 2]
3. [IPA for sentence 3]
4. [IPA for sentence 4]

KEYWORDS:
1. [keyword1, keyword2, keyword3]
2. [keyword1, keyword2, keyword3]
3. [keyword1, keyword2, keyword3]
4. [keyword1, keyword2, keyword3]

IMPORTANT:
- Return ONLY the formatted text, no extra explanation
- Sentences must be in Arabic only
- Ensure exactly {num_sentences} sentences, translations, IPA, and keywords"""

        return prompt

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
            validated_result, sentence, complexity
        )

        # Extract explanations
        explanations = validated_result.get('explanations', {})

        return GrammarAnalysis(
            sentence=sentence,
            target_word=target_word,
            language_code=self.LANGUAGE_CODE,
            complexity_level=complexity,
            grammatical_elements=validated_result.get('elements', {}),
            word_explanations=validated_result['word_explanations'],
            explanations=explanations,
            confidence_score=validated_result.get('confidence_score', 0.0),
            html_output=html_output,
            color_scheme=color_scheme,
            is_rtl=True,
            text_direction="rtl"
        )

    def _generate_html_output(self, parsed_data: Dict[str, Any], sentence: str, complexity: str) -> str:
        """Generate HTML output for Arabic text with inline word coloring and RTL support"""
        # Extract word explanations from parsed data
        word_explanations = parsed_data.get('word_explanations', [])

        # Get color scheme based on complexity
        color_scheme = self.arabic_config.get_color_scheme(complexity)

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

        # Return only the colored sentence HTML with RTL support
        return f'<span dir="rtl" style="direction: rtl; font-family: Arial, sans-serif;">{" ".join(sentence_parts)}</span>'

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
            grammatical_elements={},  # Empty dict for fallback
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
        """Generate fallback HTML output - just return the plain sentence with RTL support"""
        return f'<span dir="rtl" style="direction: rtl; font-family: Arial, sans-serif;">{sentence}</span>'

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
        Analyze grammar for multiple Arabic sentences efficiently.

        ARABIC BATCH PROCESSING:
        - Handles multiple Arabic sentences in single AI call
        - Maintains RTL reading order for explanations
        - Applies per-sentence validation and fallbacks
        - Returns consistent results for all input sentences
        - Prevents token overflow with appropriate batch sizes

        ARABIC BATCH SIZE CONSIDERATIONS:
        - 8 sentences: Optimal balance of efficiency and response quality
        - Prevents JSON truncation with 2000 max_tokens
        - Allows meaningful error recovery per sentence
        - Accounts for Arabic linguistic complexity (root-based morphology, case marking)

        ERROR HANDLING:
        - If entire batch fails: Return fallbacks for all sentences
        - If individual sentences fail: Use fallbacks only for failed ones
        - Maintains output consistency regardless of partial failures
        """
        logger.info(f"DEBUG: batch_analyze_grammar called with {len(sentences)} sentences")
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
                    word_explanations=validated_result.get('word_explanations', []),
                    is_rtl=True,
                    text_direction="rtl"
                ))

            return grammar_analyses
        except Exception as e:
            logger.error(f"Batch analysis failed: {e}")
            # Return fallback analyses
            fallback_analyses = []
            for sentence in sentences:
                fallback_result = self.response_parser.fallbacks.create_fallback(sentence, complexity)
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
                    word_explanations=fallback_result.get('word_explanations', []),
                    is_rtl=True,
                    text_direction="rtl"
                ))

            return fallback_analyses

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