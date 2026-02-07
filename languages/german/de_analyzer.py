# German Grammar Analyzer
# Main facade for German grammar analysis
# Clean Architecture implementation with case system and gender agreement

import json
import logging
import re
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from .domain.de_config import DeConfig
from .domain.de_prompt_builder import DePromptBuilder
from .domain.de_response_parser import DeResponseParser
from .domain.de_validator import DeValidator
from .infrastructure.de_fallbacks import DeFallbacks

# Import BaseGrammarAnalyzer
import sys
import os
# Try different import paths
try:
    from language_analyzers.base_analyzer import BaseGrammarAnalyzer, GrammarAnalysis, LanguageConfig
    from shared_utils import get_gemini_model, get_gemini_fallback_model, get_gemini_api
except ImportError:
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'streamlit_app'))
        from language_analyzers.base_analyzer import BaseGrammarAnalyzer, GrammarAnalysis, LanguageConfig
        from shared_utils import get_gemini_model, get_gemini_fallback_model, get_gemini_api
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

class DeAnalyzer(BaseGrammarAnalyzer):
    """
    German Grammar Analyzer - Clean Architecture Implementation

    Key Features:
    - Case system (Nominativ, Akkusativ, Dativ, Genitiv)
    - Gender agreement (maskulin, feminin, neutrum)
    - V2 word order in main clauses
    - Complex verb conjugation (stark/schwach/gemischt)
    - Compound noun formation
    - Adjective declension (stark/schwach/gemischt)
    - Preposition case requirements
    - Modal and auxiliary verb systems
    - Subjunctive mood (Konjunktiv I/II)
    """

    VERSION = "1.0"
    LANGUAGE_CODE = "de"
    LANGUAGE_NAME = "German"

    def __init__(self,
                 config: Optional[DeConfig] = None,
                 prompt_builder: Optional[DePromptBuilder] = None,
                 response_parser: Optional[DeResponseParser] = None,
                 validator: Optional[DeValidator] = None,
                 fallbacks: Optional[DeFallbacks] = None):

        # Dependency injection for testability - must be set before super().__init__()
        self.de_config = config or DeConfig()
        self.prompt_builder = prompt_builder or DePromptBuilder(self.de_config)
        self.response_parser = response_parser or DeResponseParser(self.de_config)
        self.validator = validator or DeValidator(self.de_config)
        self.fallbacks = fallbacks or DeFallbacks(self.de_config)

        # Create language config for BaseGrammarAnalyzer
        language_config = LanguageConfig(
            code="de",
            name="German",
            native_name="Deutsch",
            family="Indo-European (Germanic)",
            script_type="alphabetic",
            complexity_rating="high",
            key_features=["case_system", "gender_agreement", "v2_word_order", "complex_morphology"],
            supported_complexity_levels=["beginner", "intermediate", "advanced"]
        )

        # Store language config separately
        self.language_config = language_config

        # Initialize base class
        super().__init__(language_config)

        # Override config property for testing compatibility
        self.config = self.de_config

        logger.info("German analyzer initialized with Duden grammar standards")

    def analyze_grammar(self, sentence: str, target_word: str, complexity: str, gemini_api_key: str) -> GrammarAnalysis:
        """
        Analyze German grammar using AI with comprehensive case/gender analysis.

        GERMAN ANALYSIS FEATURES:
        - Case determination (Nominativ/Akkusativ/Dativ/Genitiv)
        - Gender identification (maskulin/feminin/neutrum)
        - Agreement validation (article-noun, adjective-noun)
        - Word order analysis (V2 principle)
        - Compound word recognition
        - Verb conjugation analysis
        """
        try:
            logger.info(f"Analyzing German sentence: {sentence}")
            logger.info(f"Target word: {target_word}, Complexity: {complexity}")

            # Build prompt for AI
            prompt = self.prompt_builder.build_single_prompt(sentence, target_word, complexity)

            # Call AI API
            ai_response = self._call_ai(prompt, gemini_api_key)
            if not ai_response:
                logger.warning("AI API call failed, using fallback")
                fallback_result = self.fallbacks.create_fallback(sentence, complexity, target_word)
                return self._build_analysis_result(sentence, target_word, complexity, fallback_result)

            # Parse AI response
            parsed_result = self.response_parser.parse_response(ai_response, complexity, sentence, target_word)

            # Validate result
            validated_result = self.validator.validate_result(parsed_result, sentence)

            # Build final analysis
            analysis = self._build_analysis_result(sentence, target_word, complexity, validated_result)

            logger.info(f"German analysis completed with confidence: {validated_result.get('confidence', 0.5):.2f}")
            return analysis

        except Exception as e:
            logger.error(f"German analysis failed: {e}")
            # Return fallback analysis
            fallback_result = self.fallbacks.create_fallback(sentence, complexity, target_word)
            return self._build_analysis_result(sentence, target_word, complexity, fallback_result)

    def _call_ai(self, prompt: str, api_key: str) -> Optional[str]:
        """Call Gemini AI for German analysis"""
        try:
            # Configure API
            api = get_gemini_api()
            api.configure(api_key=api_key)

            # Try primary model first
            try:
                response = api.generate_content(
                    model=get_gemini_model(),
                    contents=prompt
                )
                return response.text.strip()
            except Exception as primary_error:
                logger.warning(f"Primary model {get_gemini_model()} failed: {primary_error}")
                # Fallback to preview model
                response = api.generate_content(
                    model=get_gemini_fallback_model(),
                    contents=prompt
                )
                return response.text.strip()

        except Exception as e:
            logger.error(f"AI call failed: {e}")
            return None

    def _build_analysis_result(self, sentence: str, target_word: str, complexity: str, validated_result: Dict[str, Any]) -> GrammarAnalysis:
        """Build final GrammarAnalysis object with German-specific features"""
        color_scheme = self.de_config.get_color_scheme(complexity)

        # Handle both single and batch result formats
        words = validated_result.get('words') or validated_result.get('word_explanations', [])
        explanations = validated_result.get('overall_analysis') or validated_result.get('explanations', {})

        # Generate HTML output from the parsed words
        html_output = self._generate_html_output(sentence, words, color_scheme)

        # Convert words to the expected word_explanations format (list of lists)
        word_explanations = []
        for word_data in words:
            if isinstance(word_data, dict):
                word = word_data.get('word', '')
                role = word_data.get('grammatical_role', '')
                case = word_data.get('grammatical_case', '')
                gender = word_data.get('gender', '')
                meaning = word_data.get('individual_meaning') or word_data.get('meaning', '')

                # Include case and gender in color determination
                color = self._get_german_color(role, case, gender, color_scheme)

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

    def _generate_html_output(self, sentence: str, words: List[Dict[str, Any]], color_scheme: Dict[str, str]) -> str:
        """Generate HTML output for German sentences with case/gender tooltips"""
        try:
            # Create a simple HTML structure with LTR direction
            html_parts = [f'<div dir="ltr" lang="de">']

            # Create word-to-data mapping for quick lookup
            word_map = {word_data.get('word', ''): word_data for word_data in words}

            # Process each word in the original sentence
            sentence_words = sentence.split()
            for word in sentence_words:
                word_data = word_map.get(word)

                if word_data:
                    role = word_data.get('grammatical_role', 'unknown')
                    case = word_data.get('grammatical_case', '')
                    gender = word_data.get('gender', '')

                    # Get color with German-specific logic
                    color = self._get_german_color(role, case, gender, color_scheme)

                    # Create tooltip with German grammar info
                    tooltip_parts = [role]
                    if case:
                        case_name = self.de_config.get_case_name(case)
                        tooltip_parts.append(f"Case: {case_name}")
                    if gender:
                        gender_name = self.de_config.get_gender_name(gender)
                        tooltip_parts.append(f"Gender: {gender_name}")

                    tooltip = " | ".join(tooltip_parts)

                    # Create colored span
                    html_parts.append(f'<span style="color: {color};" title="{tooltip}">{word}</span> ')
                else:
                    # Word not analyzed, use default color
                    html_parts.append(f'<span style="color: {color_scheme.get("default", "#000000")};">{word}</span> ')

            html_parts.append('</div>')

            return ''.join(html_parts).strip()

        except Exception as e:
            logger.error(f"Failed to generate German HTML: {e}")
            # Return minimal HTML with LTR direction
            return f'<div dir="ltr" lang="de">{sentence}</div>'

    def _get_german_color(self, role: str, case: str, gender: str, color_scheme: Dict[str, str]) -> str:
        """Get color for German words considering case and gender"""
        # Base color from role
        color = color_scheme.get(role, color_scheme.get('default', '#000000'))

        # Special handling for German-specific elements
        if role == 'article':
            # Articles have different colors based on case/gender
            if case == 'nominativ':
                if gender == 'maskulin':
                    color = '#FFD700'  # Gold
                elif gender == 'feminin':
                    color = '#FF69B4'  # HotPink
                elif gender == 'neutrum':
                    color = '#87CEEB'  # SkyBlue
            elif case == 'akkusativ':
                color = '#FFA500'  # Orange
            elif case == 'dativ':
                color = '#9370DB'  # MediumPurple
            elif case == 'genitiv':
                color = '#DC143C'  # Crimson

        return color

    def parse_batch_grammar_response(self, ai_response: str, sentences: List[str], complexity: str, target_word: str = "") -> List[Dict[str, Any]]:
        """
        Parse batch AI response into list of standardized German grammar analysis formats.

        Args:
            ai_response: Raw batch response from AI model
            sentences: List of original German sentences
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
        Analyze grammar for multiple German sentences in batch.

        GERMAN BATCH PROCESSING:
        - Processes up to 8 sentences simultaneously to prevent token overflow
        - Uses batch prompt template for efficient AI processing with case/gender analysis
        - Returns individual GrammarAnalysis objects for each sentence
        - Handles German-specific V2 word order and agreement patterns

        BATCH SIZE CONSIDERATIONS:
        - Maximum 8 sentences per batch (fits within 2000 token limit)
        - If batch fails: Attempts individual processing as fallback
        - If individual processing fails: Returns fallbacks for all sentences

        Args:
            sentences: List of German sentences to analyze
            target_word: Word to focus analysis on
            complexity: Analysis complexity level
            gemini_api_key: API key for AI processing

        Returns:
            List of GrammarAnalysis objects, one per sentence
        """
        try:
            logger.info(f"Batch analyzing {len(sentences)} German sentences")

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

    def _create_fallback_analysis(self, sentence: str, target_word: str, complexity: str) -> GrammarAnalysis:
        """Create fallback analysis when batch processing fails"""
        fallback_result = self.fallbacks.create_fallback(sentence, complexity, target_word)
        return self._build_analysis_result(sentence, target_word, complexity, fallback_result)

    def get_sentence_generation_prompt(self, word: str, language: str, num_sentences: int,
                                     enriched_meaning: str = "", min_length: int = 3,
                                     max_length: int = 15, difficulty: str = "intermediate",
                                     topics: Optional[List[str]] = None) -> Optional[str]:
        """
        Get German-specific sentence generation prompt to ensure proper response formatting.
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

        # Custom prompt for German to ensure proper formatting
        prompt = f"""You are a native-level expert linguist in German.

Your task: Generate a complete learning package for the German word "{word}" in ONE response.

===========================
STEP 1: WORD MEANING
===========================
{enriched_meaning_instruction}
Format: Return exactly one line like "house (a building where people live)" or "he (male pronoun, used as subject)"
IMPORTANT: Keep the entire meaning under 75 characters total.

===========================
WORD-SPECIFIC RESTRICTIONS
===========================
Based on the meaning above, identify any grammatical constraints for "{word}".
Examples: case requirements (nominative/accusative/dative/genitive), gender agreement, separable verbs.
If no restrictions apply, state "No specific grammatical restrictions."
IMPORTANT: Keep the entire restrictions summary under 60 characters total.

===========================
STEP 2: SENTENCES
===========================
Generate exactly {num_sentences} highly natural, idiomatic sentences in German for the word "{word}".

QUALITY RULES:
- Every sentence must sound like native German
- Grammar, syntax, spelling, and case usage must be correct
- The target word "{word}" MUST be used correctly according to restrictions
- Each sentence must be between {min_length} and {max_length} words long
- COUNT words precisely; if outside the range, regenerate internally
- Difficulty: {difficulty}

VARIETY REQUIREMENTS:
- Use different cases (nominative, accusative, dative, genitive) if applicable
- Use different tenses and verb forms if applicable
- Use different sentence types: declarative, interrogative, imperative
- Include separable verbs in correct forms when applicable
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
- Use standard IPA symbols for German pronunciation
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
1. [sentence 1 in German]
2. [sentence 2 in German]
3. [sentence 3 in German]
4. [sentence 4 in German]

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
- Sentences must be in German only
- Ensure exactly {num_sentences} sentences, translations, IPA, and keywords"""

        return prompt

    def get_color_scheme(self, complexity: str) -> Dict[str, str]:
        """Get color scheme for given complexity level"""
        return self.de_config.get_color_scheme(complexity)