"""
Chinese Simplified Grammar Analyzer - Clean Architecture Facade
"""


import logging
import re
from typing import Dict, List, Any, Optional

from streamlit_app.language_analyzers.base_analyzer import BaseGrammarAnalyzer, LanguageConfig, GrammarAnalysis

from .domain.zh_config import ZhConfig
from .domain.zh_prompt_builder import ZhPromptBuilder
from .domain.zh_response_parser import ZhResponseParser
from .domain.zh_validator import ZhValidator
from .domain.zh_types import AnalysisRequest, AnalysisResult, BatchAnalysisResult, ParsedWord, ParsedSentence, ParseResult, ValidationResult

logger = logging.getLogger(__name__)

class ZhAnalyzer(BaseGrammarAnalyzer):
    def _parse_result_to_dict(self, parse_result):
        """Convert ParseResult to dict with all expected keys for downstream compatibility."""
        if hasattr(parse_result, 'sentences'):
            sentences = parse_result.sentences
            if sentences:
                sent = sentences[0]
                # word_explanations: list of [word, role, color, meaning]
                word_explanations = [
                    [w.word, w.grammatical_role, '', w.individual_meaning] for w in sent.words
                ]
                return {
                    'sentence': sent.sentence,
                    'words': [
                        {'word': w.word, 'grammatical_role': w.grammatical_role, 'individual_meaning': w.individual_meaning}
                        for w in sent.words
                    ],
                    'overall_structure': getattr(sent, 'overall_structure', ''),
                    'key_features': getattr(sent, 'key_features', ''),
                    'word_explanations': word_explanations,
                    'explanations': {
                        'overall_structure': getattr(sent, 'overall_structure', ''),
                        'key_features': getattr(sent, 'key_features', ''),
                    },
                    'confidence': getattr(sent, 'confidence', 1.0),
                }
            else:
                return {'sentence': '', 'words': [], 'overall_structure': '', 'key_features': '', 'word_explanations': [], 'explanations': {}, 'confidence': 0.0}
        return parse_result if isinstance(parse_result, dict) else {}

    def analyze_grammar(
        self,
        sentence: str,
        target_word: str,
        complexity: str,
        gemini_api_key: str
    ) -> AnalysisResult:
        """Full pipeline: prompt → AI call → parse → validate → HTML output, with robust fallback and explanation quality validation."""
        try:
            prompt = self.get_grammar_prompt(complexity, sentence, target_word)
            ai_response = self._call_ai(prompt, gemini_api_key)
            parsed = self.parse_grammar_response(ai_response, complexity, sentence)
            validated = self.validator.validate_result(parsed, sentence)
            # Always convert to dict if dataclass
            from dataclasses import asdict, is_dataclass
            if is_dataclass(validated):
                validated = asdict(validated)
            # Explanation quality validation (Traditional gold standard)
            quality_validation = self.validator.validate_explanation_quality(validated) if hasattr(self.validator, 'validate_explanation_quality') else None
            if quality_validation:
                validated['explanation_quality'] = quality_validation
                base_confidence = validated.get('confidence', 0.5)
                quality_score = quality_validation.get('quality_score', 1.0)
                adjusted_confidence = min(base_confidence * quality_score, 1.0)
                validated['confidence'] = adjusted_confidence
                if quality_validation.get('issues'):
                    logger.info(f"Explanation quality issues for '{sentence}': {quality_validation['issues']}")
            if not validated.get('word_explanations'):
                logger.warning("AI/parse returned empty word_explanations, using fallback.")
                fallback = self.response_parser.fallbacks.create_fallback(sentence, complexity)
                validated = self.validator.validate_result(fallback, sentence)
                if is_dataclass(validated):
                    validated = asdict(validated)
            html_output = self._generate_html_output(validated, sentence, complexity)
            result = AnalysisResult(
                success=True,
                sentence=sentence,
                words=validated.get('words', []),
                overall_structure=validated.get('overall_structure', ""),
                key_features=validated.get('key_features', ""),
                confidence=validated.get('confidence', 0.0),
                validation_issues=validated.get('issues', []),
                validation_suggestions=validated.get('suggestions', []),
                error_message=None,
                fallback_used=False
            )
            result.explanation_quality = validated.get('explanation_quality', {})
            result.processing_time = 0.0
            result.word_explanations = validated.get('word_explanations', [])
            result.confidence_score = result.confidence
            result.target_word = target_word
            return result
        except Exception as e:
            logger.error(f"analyze_grammar failed: {e}")
            fallback = self.response_parser.fallbacks.create_fallback(sentence, complexity)
            validated = self.validator.validate_result(fallback, sentence)
            from dataclasses import asdict, is_dataclass
            if is_dataclass(validated):
                validated = asdict(validated)
            html_output = self._generate_html_output(validated, sentence, complexity)
            result = AnalysisResult(
                success=False,
                sentence=sentence,
                words=validated.get('words', []),
                overall_structure=validated.get('overall_structure', ""),
                key_features=validated.get('key_features', ""),
                confidence=validated.get('confidence', 0.3),
                validation_issues=validated.get('issues', []),
                validation_suggestions=validated.get('suggestions', []),
                error_message=str(e),
                fallback_used=True
            )
            result.explanation_quality = validated.get('explanation_quality', {})
            result.processing_time = 0.0
            result.word_explanations = validated.get('word_explanations', [])
            result.confidence_score = result.confidence
            result.target_word = target_word
            return result
    # === ABSTRACT METHODS REQUIRED BY BASE CLASS ===
    def get_grammar_prompt(self, complexity: str, sentence: str, target_word: str) -> str:
        return self.prompt_builder.build_single_prompt(sentence, target_word, complexity)

    def parse_grammar_response(self, ai_response: str, complexity: str, sentence: str) -> Dict[str, Any]:
        return self.response_parser.parse_response(ai_response, complexity, sentence, None)

    def validate_analysis(self, parsed_data: Dict[str, Any], original_sentence: str) -> float:
        return self.validator.validate_result(parsed_data, original_sentence)['confidence']

    def get_color_scheme(self, complexity: str) -> Dict[str, str]:
        return self.zh_config.get_color_scheme(complexity)
    VERSION = "1.0"
    LANGUAGE_CODE = "zh"
    LANGUAGE_NAME = "Chinese Simplified"

    def __init__(self):
        logger.info("DEBUG: ZhAnalyzer __init__ called")
        self.zh_config = ZhConfig()
        self.config = self.zh_config  # For gold standard compatibility
        self.language_name = "Chinese Simplified"
        self.language_code = "zh"
        self.supported_levels = ['beginner', 'intermediate', 'advanced']
        self.prompt_builder = ZhPromptBuilder(self.zh_config)
        self.response_parser = ZhResponseParser(self.zh_config)
        self.validator = ZhValidator(self.zh_config)

    def get_sentence_generation_prompt(self, word, language, num_sentences, enriched_meaning="", min_length=3, max_length=15, difficulty="intermediate", topics=None):
        return self.prompt_builder.get_sentence_generation_prompt(
            word=word,
            language=language,
            num_sentences=num_sentences,
            enriched_meaning=enriched_meaning,
            min_length=min_length,
            max_length=max_length,
            difficulty=difficulty,
            topics=topics
        )
        def _call_ai(self, prompt: str, gemini_api_key: str) -> str:
            logger.debug(f"_call_ai called with prompt: {prompt[:200]}...")
            try:
                # LAZY IMPORTS for all shared_utils
                from streamlit_app.shared_utils import get_gemini_model, get_gemini_fallback_model, get_gemini_api
                api = get_gemini_api()
                api.configure(api_key=gemini_api_key)
                try:
                    response = api.generate_content(
                        model=get_gemini_model(),
                        contents=prompt,
                        config={'max_output_tokens': 20000}
                    )
                    ai_response = response.text.strip()
                except Exception as primary_error:
                    logger.warning(f"Primary model failed: {primary_error}")
                    response = api.generate_content(
                        model=get_gemini_fallback_model(),
                        contents=prompt,
                        config={'max_output_tokens': 20000}
                    )
                    ai_response = response.text.strip()
                logger.debug(f"AI response received: {ai_response[:500]}...")
                return ai_response
            except Exception as e:
                logger.error(f"AI call failed: {e}")
                return '{"sentence": "error", "words": []}'

        def _generate_html_output(self, parsed_data: Dict[str, Any], sentence: str, complexity: str) -> str:
            """Gold-standard HTML generator for color-coded sentence display."""
            explanations = parsed_data.get('word_explanations', [])
            logger.debug(f"DEBUG Chinese HTML Gen - Input explanations count: {len(explanations)}")
            logger.debug(f"DEBUG Chinese HTML Gen - Input sentence: '{sentence}'")
            logger.debug(f"DEBUG Chinese HTML Gen - Complexity level: {complexity}")
            color_scheme = self.get_color_scheme(complexity)
            sorted_explanations = sorted(explanations, key=lambda x: sentence.find(str(x[0])) if len(x) >= 1 else len(sentence))
            html_parts = []
            i = 0
            sentence_len = len(sentence)
            while i < sentence_len:
                matched = False
                for exp in sorted_explanations:
                    if not exp or len(exp) < 1:
                        continue
                    word = str(exp[0])
                    word_len = len(word)
                    if i + word_len <= sentence_len and sentence[i:i + word_len] == word:
                        color = exp[2] if len(exp) >= 3 and isinstance(exp[2], str) and exp[2].startswith('#') else '#AAAAAA'
                        safe_word_display = word.replace('{', '{{').replace('}', '}}')
                        colored_word = f'<span style="color: {color}; font-weight: bold;">{safe_word_display}</span>'
                        html_parts.append(colored_word)
                        logger.debug(f"DEBUG Chinese HTML Gen - Replaced '{word}' with color '{color}' (role: {exp[1] if len(exp) >= 2 else 'unknown'})")
                        i += word_len
                        matched = True
                        break
                if not matched:
                    default_color = color_scheme.get('default', '#000000')
                    html_parts.append(f'<span style="color: {default_color}; font-weight: bold;">{sentence[i]}</span>')
                    i += 1
            html = ''.join(html_parts)
            logger.debug("DEBUG Chinese HTML Gen - Final HTML result: " + html)
            return html

    def _call_ai(self, prompt: str, gemini_api_key: str) -> str:
        logger.debug(f"_call_ai called with prompt: {prompt[:200]}...")
        try:
            # LAZY IMPORTS for all shared_utils
            from streamlit_app.shared_utils import get_gemini_model, get_gemini_fallback_model, get_gemini_api
            api = get_gemini_api()
            api.configure(api_key=gemini_api_key)
            try:
                response = api.generate_content(
                    model=get_gemini_model(),
                    contents=prompt,
                    config={'max_output_tokens': 20000}
                )
                ai_response = response.text.strip()
            except Exception as primary_error:
                logger.warning(f"Primary model failed: {primary_error}")
                response = api.generate_content(
                    model=get_gemini_fallback_model(),
                    contents=prompt,
                    config={'max_output_tokens': 20000}
                )
                ai_response = response.text.strip()
            logger.debug(f"AI response received: {ai_response[:500]}...")
            return ai_response
        except Exception as e:
            logger.error(f"AI call failed: {e}")
            return '{"sentence": "error", "words": []}'

            def _generate_html_output(self, parsed_data: Dict[str, Any], sentence: str, complexity: str) -> str:
                """Gold-standard HTML generator for color-coded sentence display."""
                explanations = parsed_data.get('word_explanations', [])
                logger.debug(f"DEBUG Chinese HTML Gen - Input explanations count: {len(explanations)}")
                logger.debug(f"DEBUG Chinese HTML Gen - Input sentence: '{sentence}'")
                logger.debug(f"DEBUG Chinese HTML Gen - Complexity level: {complexity}")
                color_scheme = self.get_color_scheme(complexity)
                sorted_explanations = sorted(explanations, key=lambda x: sentence.find(str(x[0])) if len(x) >= 1 else len(sentence))
                html_parts = []
                i = 0
                sentence_len = len(sentence)
                while i < sentence_len:
                    matched = False
                    for exp in sorted_explanations:
                        if not exp or len(exp) < 1:
                            continue
                        word = str(exp[0])
                        word_len = len(word)
                        if i + word_len <= sentence_len and sentence[i:i + word_len] == word:
                            color = exp[2] if len(exp) >= 3 and isinstance(exp[2], str) and exp[2].startswith('#') else '#AAAAAA'
                            safe_word_display = word.replace('{', '{{').replace('}', '}}')
                            colored_word = f'<span style="color: {color}; font-weight: bold;">{safe_word_display}</span>'
                            html_parts.append(colored_word)
                            logger.debug(f"DEBUG Chinese HTML Gen - Replaced '{word}' with color '{color}' (role: {exp[1] if len(exp) >= 2 else 'unknown'})")
                            i += word_len
                            matched = True
                            break
                    if not matched:
                        default_color = color_scheme.get('default', '#000000')
                        html_parts.append(f'<span style="color: {default_color}; font-weight: bold;">{sentence[i]}</span>')
                        i += 1
                html = ''.join(html_parts)
                logger.debug("DEBUG Chinese HTML Gen - Final HTML result: " + html)
                return html

    # batch_analyze_grammar is already implemented above as part of the BatchAnalysisResult logic. Remove duplicate.

    def _call_ai(self, prompt: str, gemini_api_key: str) -> str:
        logger.debug(f"_call_ai called with prompt: {prompt[:200]}...")
        try:
            from streamlit_app.shared_utils import get_gemini_model, get_gemini_fallback_model, get_gemini_api
            api = get_gemini_api()
            api.configure(api_key=gemini_api_key)
            try:
                response = api.generate_content(
                    model=get_gemini_model(),
                    contents=prompt,
                    config={'max_output_tokens': 20000}
                )
                ai_response = response.text.strip()
            except Exception as primary_error:
                logger.warning(f"Primary model failed: {primary_error}")
                response = api.generate_content(
                    model=get_gemini_fallback_model(),
                    contents=prompt,
                    config={'max_output_tokens': 20000}
                )
                ai_response = response.text.strip()
            logger.debug(f"AI response received: {ai_response[:500]}...")
            return ai_response
        except Exception as e:
            logger.error(f"AI call failed: {e}")
            return '{"sentence": "error", "words": []}'

    def _generate_html_output(self, parsed_data: Dict[str, Any], sentence: str, complexity: str) -> str:
        """Gold-standard HTML generator."""
        explanations = parsed_data.get('word_explanations', [])
        logger.debug(f"DEBUG Chinese HTML Gen - Input explanations count: {len(explanations)}")
        logger.debug(f"DEBUG Chinese HTML Gen - Input sentence: '{sentence}'")
        logger.debug(f"DEBUG Chinese HTML Gen - Complexity level: {complexity}")

        color_scheme = self.get_color_scheme(complexity)
        sorted_explanations = sorted(explanations, key=lambda x: sentence.find(str(x[0])) if len(x) >= 1 else len(sentence))

        html_parts = []
        i = 0
        sentence_len = len(sentence)

        while i < sentence_len:
            matched = False
            for exp in sorted_explanations:
                if not exp or len(exp) < 1:
                    continue
                word = str(exp[0])
                word_len = len(word)

                if i + word_len <= sentence_len and sentence[i:i + word_len] == word:
                    color = exp[2] if len(exp) >= 3 and isinstance(exp[2], str) and exp[2].startswith('#') else '#AAAAAA'
                    safe_word_display = word.replace('{', '{{').replace('}', '}}')
                    colored_word = f'<span style="color: {color}; font-weight: bold;">{safe_word_display}</span>'
                    html_parts.append(colored_word)
                    logger.debug(f"DEBUG Chinese HTML Gen - Replaced '{word}' with color '{color}' (role: {exp[1] if len(exp) >= 2 else 'unknown'})")
                    i += word_len
                    matched = True
                    break

            if not matched:
                default_color = color_scheme.get('default', '#000000')
                html_parts.append(f'<span style="color: {default_color}; font-weight: bold;">{sentence[i]}</span>')
                i += 1

        html = ''.join(html_parts)
        logger.debug("DEBUG Chinese HTML Gen - Final HTML result: " + html)
        return html

    def _map_grammatical_role_to_category(self, grammatical_role: str) -> str:
        """Robust mapping (kept for HTML fallback)."""
        if not grammatical_role:
            return 'other'
        role = grammatical_role.lower().strip()
        role = re.sub(r'\s*\([^)]*\)', '', role).strip()

        if 'pronoun' in role or 'demonstrative' in role:
            return 'pronoun'
        elif any(x in role for x in ['classifier', 'measure word', 'measure']):
            return 'classifier'
        elif 'noun' in role:
            return 'noun'
        elif any(x in role for x in ['adverb', 'negation']):
            return 'adverb'
        elif 'verb' in role or 'copula' in role:
            return 'verb'
        