# languages/malayalam/ml_analyzer.py
"""
Malayalam Grammar Analyzer - Clean Architecture Facade

Implements the Malayalam grammar analyzer following the French v2.0 gold standard.
Orchestrates domain components for grammar analysis of Malayalam text.

MALAYALAM-SPECIFIC FEATURES:
- Agglutinative morphology: Rich case system with suffixes
- SOV word order: Subject-Object-Verb sentence structure
- Malayalam script: Unique Dravidian script (left-to-right)
- Postpositions: Not prepositions (follows the noun)
- No grammatical gender: Only natural gender distinctions
- 3-level honorific system: informal/polite/formal
- Sandhi rules: Phonological joining at morpheme boundaries
- Rich verbal participle system: Conjunctive, conditional, concessive, simultaneous
- 7 grammatical cases: Nominative, accusative, dative, genitive, instrumental, locative, sociative
"""

import logging
import re
import time
from typing import Dict, List, Any, Optional
from pathlib import Path

from streamlit_app.language_analyzers.base_analyzer import BaseGrammarAnalyzer, LanguageConfig, GrammarAnalysis

from .domain.ml_config import MlConfig
from .domain.ml_prompt_builder import MlPromptBuilder
from .domain.ml_response_parser import MlResponseParser
from .domain.ml_fallbacks import MlFallbacks
from .domain.ml_validator import MlValidator

logger = logging.getLogger(__name__)


class MlAnalyzer(BaseGrammarAnalyzer):
    """
    Grammar analyzer for Malayalam — Clean Architecture.

    Malayalam is agglutinative (Dravidian family) with SOV word order,
    rich case system, and postpositional grammar.
    """

    VERSION = "1.0"
    LANGUAGE_CODE = "ml"
    LANGUAGE_NAME = "Malayalam"

    def __init__(self):
        self.ml_config = MlConfig()
        self.ml_fallbacks = MlFallbacks(self.ml_config)
        self.prompt_builder = MlPromptBuilder(self.ml_config)
        self.response_parser = MlResponseParser(self.ml_config, self.ml_fallbacks)
        self.validator = MlValidator(self.ml_config)

        config = LanguageConfig(
            code="ml",
            name="Malayalam",
            native_name="മലയാളം",
            family="Dravidian",
            script_type="abugida",
            complexity_rating="high",
            key_features=[
                'agglutinative_morphology', 'sov_word_order', 'case_system',
                'postpositions', 'no_grammatical_gender', 'honorific_system',
                'sandhi_rules', 'verbal_participles', 'converbs'
            ],
            supported_complexity_levels=['beginner', 'intermediate', 'advanced']
        )
        super().__init__(config)

    def analyze_grammar(self, sentence: str, target_word: str, complexity: str, gemini_api_key: str) -> GrammarAnalysis:
        """Analyze grammar for a single Malayalam sentence."""
        try:
            start_time = time.time()

            logger.info(f"Malayalam Analysis: Starting for '{sentence[:50]}...' (complexity: {complexity})")

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
            logger.info(f"Malayalam Analysis: Completed in {processing_time:.2f}s, confidence: {adjusted_confidence:.2f}")

            return analysis_result

        except Exception as e:
            logger.error(f"Analysis failed for '{sentence}': {e}")
            fallback_result = self.ml_fallbacks.create_fallback(sentence, complexity)
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
        """Analyze grammar for multiple Malayalam sentences."""
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
                fallback_result = self.ml_fallbacks.create_fallback(sentence, complexity)
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
        
    def get_sentence_generation_prompt(self, word: str, language: str, num_sentences: int,
                                     enriched_meaning: str = "", min_length: int = 6,
                                     max_length: int = 10, difficulty: str = "intermediate",
                                     topics: Optional[List[str]] = None) -> Optional[str]:
        """
        Malayalam-specific sentence generation prompt.
        Modeled exactly after Hindi gold standard for high-quality natural sentences.
        """
        # Build context instruction based on topics
        if topics:
            context_instruction = f"- CRITICAL REQUIREMENT: ALL sentences MUST relate to these specific topics: {', '.join(topics)}. Force the word usage into these contexts even if it requires creative interpretation. Do NOT use generic contexts."
        else:
            context_instruction = "- Use diverse real-life contexts: family, school, travel, food, daily life, emotions, work, social situations, nature, festivals, temple, market"

        # Build meaning instruction based on enriched data
        if enriched_meaning and enriched_meaning != 'N/A':
            if enriched_meaning.startswith('{') and enriched_meaning.endswith('}'):
                context_lines = enriched_meaning[1:-1].split('\n')
                definitions = []
                for line in context_lines:
                    line = line.strip()
                    if line.startswith('Definition'):
                        def_text = line.split(':', 1)[1].strip() if ':' in line else line
                        def_text = def_text.split(' | ')[0].strip()
                        definitions.append(def_text)
                if definitions:
                    meaning_summary = '; '.join(definitions[:4])
                    enriched_meaning_instruction = f'Analyze this linguistic data for "{word}" and generate a brief, clean English meaning that encompasses ALL the meanings. Data: {meaning_summary}. IMPORTANT: Consider all meanings and provide a comprehensive meaning.'
                else:
                    enriched_meaning_instruction = f'Analyze this linguistic context for "{word}" and generate a brief, clean English meaning. Context: {enriched_meaning[:200]}. IMPORTANT: Return ONLY the English meaning.'
            else:
                enriched_meaning_instruction = f'Use this pre-reviewed meaning for "{word}": "{enriched_meaning}". Generate a clean English meaning based on this.'
        else:
            enriched_meaning_instruction = f'Provide a brief English meaning for "{word}".'

        # Custom prompt for Malayalam (Dravidian agglutinative language)
        prompt = f"""You are a native-level expert linguist in Malayalam (മലയാളം).

Your task: Generate a complete learning package for the Malayalam word "{word}" in ONE response.

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
Examples: case markers (ന്, ല്, etc.), verb conjugation rules, postpositions, sandhi, honorific level.
If no restrictions apply, state "No specific grammatical restrictions."
IMPORTANT: Keep the entire restrictions summary under 60 characters total.

===========================
STEP 2: SENTENCES
===========================
Generate exactly {num_sentences} highly natural, idiomatic sentences in Malayalam for the word "{word}".

QUALITY RULES:
- Every sentence must use proper Malayalam script (മലയാളം)
- Grammar, morphology, and sandhi must be correct
- The target word "{word}" MUST be used correctly according to restrictions
- Each sentence must be between {min_length} and {max_length} words long
- COUNT words precisely; if outside the range, regenerate internally
- Difficulty: {difficulty}

VARIETY REQUIREMENTS:
- Use different case markers, verb conjugations, and postpositions where appropriate
- Include different sentence types (declarative, interrogative, negative, etc.)
- Show natural spoken-style Malayalam when possible
{context_instruction}

===========================
STEP 3: ENGLISH TRANSLATIONS
===========================
For EACH sentence above, provide a natural, fluent English translation.
- Translation should be natural English, not literal word-for-word

===========================
STEP 4: IPA
===========================
For EACH sentence above, provide accurate IPA transcription.
- Use standard IPA symbols (including retroflex sounds like ṟ, ɭ, etc.)

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
1. [sentence 1 in Malayalam script]
2. [sentence 2 in Malayalam script]
...

TRANSLATIONS:
1. [natural English translation for sentence 1]
...

IPA:
1. [IPA for sentence 1]
...

KEYWORDS:
1. [keyword1, keyword2, keyword3]
...

IMPORTANT:
- Return ONLY the formatted text, no extra explanation
- Sentences must be in proper Malayalam script only
- Ensure exactly {num_sentences} sentences, translations, IPA, and keywords"""

        return prompt        

    def _call_ai(self, prompt: str, gemini_api_key: str) -> str:
        """Call Google Gemini AI for Malayalam grammar analysis."""
        # LAZY IMPORTS — never at module level
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
        """Return color scheme for Malayalam grammatical elements."""
        return self.ml_config.get_color_scheme(complexity)

    def get_grammar_prompt(self, complexity: str, sentence: str, target_word: str) -> str:
        """Generate Malayalam-specific AI prompt for grammar analysis."""
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
        Generate HTML output for Malayalam text with inline color styling for Anki.

        Malayalam uses spaces between words, so we can match words
        from word_explanations to the sentence text.
        """
        explanations = parsed_data.get('word_explanations', [])
        color_scheme = self.get_color_scheme(complexity)

        if not explanations:
            return sentence

        html_parts = []
        covered = 0

        for exp in explanations:
            if len(exp) < 3:
                continue

            word = exp[0]
            role = exp[1]
            category = self._map_grammatical_role_to_category(role)
            color = color_scheme.get(category, color_scheme.get('other', '#AAAAAA'))

            idx = sentence.find(word, covered)
            if idx == -1:
                idx = sentence.find(word)

            if idx != -1:
                if idx > covered:
                    uncovered = sentence[covered:idx]
                    default_color = color_scheme.get('other', '#AAAAAA')
                    html_parts.append(f'<span style="color: {default_color}; font-weight: bold;">{uncovered}</span>')

                html_parts.append(f'<span style="color: {color}; font-weight: bold;">{word}</span>')
                covered = idx + len(word)
            else:
                html_parts.append(f'<span style="color: {color}; font-weight: bold;">{word}</span>')

        if covered < len(sentence):
            remaining = sentence[covered:]
            default_color = color_scheme.get('other', '#AAAAAA')
            html_parts.append(f'<span style="color: {default_color}; font-weight: bold;">{remaining}</span>')

        return ''.join(html_parts)



    def _map_grammatical_role_to_category(self, role: str) -> str:
        """Map specific grammatical roles to color categories."""
        hierarchy = self.ml_config.grammatical_roles.get('role_hierarchy', {})
        return hierarchy.get(role, role)
