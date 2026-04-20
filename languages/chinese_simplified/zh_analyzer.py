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

logger = logging.getLogger(__name__)

class ZhAnalyzer(BaseGrammarAnalyzer):
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

    def batch_analyze_grammar(self, sentences: List[str], target_word: str, complexity: str, gemini_api_key: str) -> List[GrammarAnalysis]:
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
                    language_code=self.LANGUAGE_CODE,
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
                fallback_result = self.response_parser.fallbacks.create_fallback(sentence, complexity)
                html_output = self._generate_html_output(fallback_result, sentence, complexity)
                fallback_analyses.append(GrammarAnalysis(
                            sentence=sentence,
                            target_word=target_word or "",
                            language_code=self.LANGUAGE_CODE,
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

    def batch_analyze_grammar(self, sentences: List[str], target_word: str, complexity: str, gemini_api_key: str) -> List[GrammarAnalysis]:
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
                    word_explanations=validated_result.get('word_explanations', [])
                ))
            return grammar_analyses
        except Exception as e:
            logger.error(f"Batch analysis failed: {e}")
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
                    word_explanations=fallback_result.get('word_explanations', [])
                ))
            return fallback_analyses

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
        elif 'adjective' in role:
            return 'adjective'
        elif any(x in role for x in ['particle', 'structural']):
            return 'particle'
        elif 'aspect' in role:
            return 'aspect_marker'
        elif 'modal' in role:
            return 'modal_particle'
        elif any(x in role for x in ['numeral', 'number']):
            return 'numeral'
        else:
            return 'other'