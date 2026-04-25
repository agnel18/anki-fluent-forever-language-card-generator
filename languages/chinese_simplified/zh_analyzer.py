"""
Chinese Simplified Grammar Analyzer - Main Facade

v1.3 — batch_analyze_grammar returns List[GrammarAnalysis] (matches gold-standard pattern
       used by Japanese, Chinese Traditional, French, etc.). Previous dict return value
       was incompatible with grammar_processor.py's attribute access (.html_output),
       which silently routed every sentence through the generic fallback.
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from streamlit_app.language_analyzers.base_analyzer import BaseGrammarAnalyzer, LanguageConfig, GrammarAnalysis

from .domain.zh_config import ZhConfig
from .domain.zh_prompt_builder import ZhPromptBuilder
from .domain.zh_response_parser import ZhResponseParser
from .domain.zh_validator import ZhValidator
from .domain.zh_patterns import ZhPatterns
from .domain.zh_fallbacks import ZhFallbacks

logger = logging.getLogger(__name__)

# Unique marker so you can grep your runtime logs and prove this version is loaded.
_ZH_ANALYZER_VERSION = "1.3"
logger.info(f"[ZH_ANALYZER_BOOT] Loading zh_analyzer.py v{_ZH_ANALYZER_VERSION}")


@dataclass
class AnalysisRequest:
    sentence: str
    target_word: Optional[str] = None
    complexity: str = "intermediate"
    analysis_type: str = "single"


@dataclass
class AnalysisResult:
    success: bool
    sentence: str
    words: List[Dict[str, Any]]
    overall_structure: str
    key_features: str
    confidence: float
    validation_issues: List[str]
    validation_suggestions: List[str]
    error_message: Optional[str] = None
    fallback_used: bool = False


@dataclass
class BatchAnalysisResult:
    success: bool
    results: List[AnalysisResult]
    total_sentences: int
    average_confidence: float
    error_message: Optional[str] = None
    fallback_used: bool = False


class ZhAnalyzer(BaseGrammarAnalyzer):
    """Main analyzer facade for Chinese Simplified grammar analysis."""

    VERSION = _ZH_ANALYZER_VERSION
    LANGUAGE_CODE = "zh"
    LANGUAGE_NAME = "Chinese Simplified"

    def __init__(self):
        language_config = LanguageConfig(
            code="zh",
            name="Chinese (Simplified)",
            native_name="简体中文",
            family="Sino-Tibetan",
            script_type="logographic",
            complexity_rating="intermediate",
            key_features=["tonal_language", "character_based", "analytic_syntax"],
            supported_complexity_levels=["beginner", "intermediate", "advanced"]
        )

        self.zh_config = ZhConfig()
        self.prompt_builder = ZhPromptBuilder(self.zh_config)
        self.response_parser = ZhResponseParser(self.zh_config)
        self.validator = ZhValidator(self.zh_config)
        self.patterns = ZhPatterns(self.zh_config)
        self.fallbacks = ZhFallbacks(self.zh_config)

        super().__init__(language_config)

        logger.info(f"ZhAnalyzer v{_ZH_ANALYZER_VERSION} initialized with all domain components")

    # ===================================================================
    # CORE ANALYSIS METHODS
    # ===================================================================

    def analyze_grammar(self, sentence: str, target_word: str, complexity: str, gemini_api_key: str) -> GrammarAnalysis:
        """Analyze grammar for a single sentence."""
        if not sentence or not sentence.strip():
            logger.warning("Empty sentence provided to analyze_grammar")
            return GrammarAnalysis(word_explanations=[], confidence=0.0,
                                   explanation_quality={'quality_score': 0.0, 'issues': ['Empty sentence']},
                                   processing_time=0.0)

        if not target_word or not target_word.strip():
            logger.warning("Empty target_word provided to analyze_grammar")
            return GrammarAnalysis(word_explanations=[], confidence=0.0,
                                   explanation_quality={'quality_score': 0.0, 'issues': ['Empty target word']},
                                   processing_time=0.0)

        if not gemini_api_key or not gemini_api_key.strip():
            logger.warning("Empty API key provided to analyze_grammar")
            return GrammarAnalysis(word_explanations=[], confidence=0.0,
                                   explanation_quality={'quality_score': 0.0, 'issues': ['Invalid API key']},
                                   processing_time=0.0)

        try:
            prompt = self.get_grammar_prompt(complexity, sentence, target_word)
            ai_response = self._call_ai(prompt, gemini_api_key)
            parse_result = self.response_parser.parse_response(ai_response, complexity, sentence, target_word)

            result_dict = self._parse_result_to_dict(parse_result, sentence, complexity, target_word)

            validation = self.validator.validate_result(parse_result, sentence)
            base_confidence = self._get_confidence(validation, default=result_dict.get('confidence', 0.5))

            quality = self._safe_quality_check(result_dict)
            quality_score = quality.get('quality_score', 1.0) if isinstance(quality, dict) else 1.0
            adjusted_confidence = min(base_confidence * quality_score, 1.0)

            result_dict['confidence'] = adjusted_confidence
            result_dict['explanation_quality'] = quality
            result_dict['grammar_summary'] = self._build_grammar_summary(result_dict)

            if isinstance(quality, dict) and quality.get('issues'):
                logger.info(f"Explanation quality issues for '{sentence}': {quality['issues']}")

            html_output = self._generate_html_output(result_dict, sentence, complexity)

            return GrammarAnalysis(
                sentence=sentence,
                target_word=target_word or "",
                language_code=self.language_code,
                complexity_level=complexity,
                grammatical_elements=result_dict.get('elements', {}),
                explanations=result_dict.get('explanations', {}),
                color_scheme=self.get_color_scheme(complexity),
                html_output=html_output,
                confidence_score=adjusted_confidence,
                word_explanations=result_dict.get('word_explanations', [])
            )
        except Exception as e:
            logger.error(f"[zh v{_ZH_ANALYZER_VERSION}] Analysis failed for '{sentence}': {e}", exc_info=True)
            fallback_result = self.fallbacks.create_fallback(sentence, complexity)
            fallback_result['grammar_summary'] = self._build_grammar_summary(fallback_result)
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

    def batch_analyze_grammar(self, sentences: List[str], target_words: List[str] = None,
                              complexity: str = "intermediate", gemini_api_key: str = None,
                              target_word: str = "") -> List[GrammarAnalysis]:
        """Batch grammar analysis. Returns List[GrammarAnalysis] matching the gold-standard pattern."""
        # Normalize: accept both target_words list and legacy target_word kwarg
        if target_words is None:
            target_words = [target_word] * len(sentences) if target_word else [""] * len(sentences)
        elif len(target_words) < len(sentences):
            pad = target_word or (target_words[0] if target_words else "")
            target_words = list(target_words) + [pad] * (len(sentences) - len(target_words))

        logger.info(f"[zh v{_ZH_ANALYZER_VERSION}] Batch analyze: {len(sentences)} sentences for Chinese Simplified")
        try:
            primary_target = target_words[0] if target_words else ""
            prompt = self.prompt_builder.build_batch_analysis_prompt(sentences, primary_target, complexity)
            ai_response = self._call_ai(prompt, gemini_api_key)

            results = self.response_parser.parse_batch_response(ai_response, sentences, complexity, primary_target)

            grammar_analyses: List[GrammarAnalysis] = []
            for result_dict, sentence, tw in zip(results, sentences, target_words):
                if not isinstance(result_dict, dict):
                    result_dict = self.fallbacks.create_fallback(sentence, complexity)

                # Normalize the AI's explanation keys (sentence_structure / function_of_X)
                result_dict = self._normalize_explanations(result_dict, target_word=tw)

                validation = self.validator.validate_result(result_dict, sentence)
                quality = self._safe_quality_check(result_dict)

                base_conf = self._get_confidence(validation, default=result_dict.get('confidence', 0.5))
                quality_score = quality.get('quality_score', 1.0) if isinstance(quality, dict) else 1.0
                adjusted_conf = min(base_conf * quality_score, 1.0)

                result_dict['confidence'] = adjusted_conf
                result_dict['grammar_summary'] = self._build_grammar_summary(result_dict)
                html_output = self._generate_html_output(result_dict, sentence, complexity)

                grammar_analyses.append(GrammarAnalysis(
                    sentence=sentence,
                    target_word=tw or "",
                    language_code=self.language_code,
                    complexity_level=complexity,
                    grammatical_elements=result_dict.get('elements', {}),
                    explanations=result_dict.get('explanations', {}),
                    color_scheme=self.get_color_scheme(complexity),
                    html_output=html_output,
                    confidence_score=adjusted_conf,
                    word_explanations=result_dict.get('word_explanations', [])
                ))
            return grammar_analyses

        except Exception as e:
            logger.error(f"[zh v{_ZH_ANALYZER_VERSION}] Batch analysis failed: {e}", exc_info=True)
            fallback_analyses: List[GrammarAnalysis] = []
            for sentence, tw in zip(sentences, target_words):
                fb = self.fallbacks.create_fallback(sentence, complexity)
                fb['grammar_summary'] = self._build_grammar_summary(fb)
                html_output = self._generate_html_output(fb, sentence, complexity)
                fallback_analyses.append(GrammarAnalysis(
                    sentence=sentence,
                    target_word=tw or "",
                    language_code=self.language_code,
                    complexity_level=complexity,
                    grammatical_elements=fb.get('elements', {}),
                    explanations=fb.get('explanations', {}),
                    color_scheme=self.get_color_scheme(complexity),
                    html_output=html_output or f"<span>{sentence}</span>",
                    confidence_score=fb.get('confidence', 0.3),
                    word_explanations=fb.get('word_explanations', [])
                ))
            return fallback_analyses

    # ===================================================================
    # HELPERS
    # ===================================================================

    def _safe_quality_check(self, result_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Call validate_explanation_quality without trusting it not to crash."""
        try:
            quality = self.validator.validate_explanation_quality(result_dict)
            if isinstance(quality, dict):
                return quality
            # If somehow returned a dataclass-like, coerce
            if hasattr(quality, 'quality_score'):
                return {
                    'quality_score': float(getattr(quality, 'quality_score', 1.0)),
                    'issues': list(getattr(quality, 'issues', []) or []),
                }
        except Exception as e:
            logger.warning(f"validate_explanation_quality failed: {e}")
        return {'quality_score': 1.0, 'issues': []}

    def _normalize_explanations(self, result_dict: Dict[str, Any], target_word: str = "") -> Dict[str, Any]:
        """The AI sometimes returns 'sentence_structure' / 'function_of_X' instead of
        'overall_structure' / 'key_features'. Map them here so the grammar summary works."""
        explanations = result_dict.get('explanations') or {}
        if not isinstance(explanations, dict):
            return result_dict

        # Aliases the AI tends to produce
        if not explanations.get('overall_structure'):
            explanations['overall_structure'] = (
                explanations.get('sentence_structure')
                or explanations.get('structure')
                or explanations.get('overall')
                or ''
            )

        if not explanations.get('key_features'):
            # function_of_<target> or just function_of_*
            tw_key = f'function_of_{target_word}' if target_word else None
            features = ''
            if tw_key and tw_key in explanations:
                features = explanations[tw_key]
            else:
                for k, v in explanations.items():
                    if isinstance(k, str) and k.startswith('function_of_') and isinstance(v, str):
                        features = v
                        break
            features = features or explanations.get('features') or explanations.get('notes') or ''
            explanations['key_features'] = features

        result_dict['explanations'] = explanations
        return result_dict

    def _parse_result_to_dict(self, parse_result, sentence: str, complexity: str,
                              target_word: str = "") -> Dict[str, Any]:
        """Convert ParseResult dataclass into the dict format used by the rest of the pipeline."""
        if not getattr(parse_result, 'success', False) or not getattr(parse_result, 'sentences', None):
            return self.fallbacks.create_fallback(sentence, complexity)

        ps = parse_result.sentences[0]
        color_scheme = self.get_color_scheme(complexity)

        word_explanations: List[List[str]] = []
        elements: Dict[str, List[Dict[str, str]]] = {}
        for pw in ps.words:
            color = color_scheme.get(pw.grammatical_role, color_scheme.get('other', '#AAAAAA'))
            word_explanations.append([pw.word, pw.grammatical_role, color, pw.individual_meaning])
            elements.setdefault(pw.grammatical_role, []).append(
                {'word': pw.word, 'grammatical_role': pw.grammatical_role}
            )

        result_dict = {
            'sentence': ps.sentence or sentence,
            'elements': elements,
            'explanations': {
                'overall_structure': ps.overall_structure or '',
                'key_features': ps.key_features or '',
            },
            'word_explanations': word_explanations,
            'confidence': ps.confidence,
            'is_fallback': False,
        }
        return self._normalize_explanations(result_dict, target_word=target_word)

    @staticmethod
    def _get_confidence(validation, default: float = 0.5) -> float:
        """Safely extract confidence from a ValidationResult dataclass OR a dict."""
        if validation is None:
            return default
        if hasattr(validation, 'confidence_score'):
            try:
                return float(validation.confidence_score)
            except (TypeError, ValueError):
                return default
        if isinstance(validation, dict):
            for key in ('confidence_score', 'confidence'):
                if key in validation:
                    try:
                        return float(validation[key])
                    except (TypeError, ValueError):
                        pass
        return default

    def _build_grammar_summary(self, result_dict: Dict[str, Any]) -> str:
        """Build a meaningful Chinese-specific grammar summary."""
        explanations = result_dict.get('explanations', {}) or {}
        overall = (explanations.get('overall_structure') or '').strip()
        features = (explanations.get('key_features') or '').strip()

        parts = []
        if overall:
            parts.append(overall)
        if features and features.lower() != overall.lower():
            parts.append(features)

        if parts:
            return ' '.join(parts)

        word_explanations = result_dict.get('word_explanations', []) or []
        if not word_explanations:
            return "Chinese sentence analysis."

        roles = [exp[1] for exp in word_explanations if len(exp) > 1]
        descriptors = []
        if 'classifier' in roles:
            descriptors.append("uses a classifier (measure word) construction")
        if 'aspect_marker' in roles:
            descriptors.append("includes an aspect marker indicating action state")
        if 'modal_particle' in roles:
            descriptors.append("ends with a modal particle expressing tone")
        if 'structural_particle' in roles:
            descriptors.append("uses structural particles to connect elements")
        if 'preposition' in roles:
            descriptors.append("includes a prepositional phrase")

        if descriptors:
            return "This Chinese sentence " + ", and ".join(descriptors) + "."
        return "Chinese sentence with standard subject-verb-object structure."

    # ===================================================================
    # AI CALL & ABSTRACT METHOD IMPLEMENTATIONS
    # ===================================================================

    def _call_ai(self, prompt: str, gemini_api_key: str) -> str:
        """Call Google Gemini AI with primary -> fallback model strategy."""
        logger.info(f"DEBUG: _call_ai called with prompt: {prompt[:200]}...")
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
            logger.info(f"AI response received: {ai_response[:500]}...")
            return ai_response
        except Exception as e:
            logger.error(f"AI call failed: {e}")
            return '{"sentence": "error", "words": []}'

    def get_grammar_prompt(self, complexity: str, sentence: str, target_word: str) -> str:
        return self.prompt_builder.build_single_analysis_prompt(sentence, target_word, complexity)

    def get_color_scheme(self, complexity: str) -> Dict[str, str]:
        return self.zh_config.get_color_scheme(complexity)

    def parse_grammar_response(self, ai_response: str, complexity: str,
                               sentence: str, target_word: str = "") -> Dict[str, Any]:
        """Required by BaseGrammarAnalyzer — returns a DICT, not a dataclass."""
        parse_result = self.response_parser.parse_response(
            ai_response, complexity, sentence, target_word
        )
        return self._parse_result_to_dict(parse_result, sentence, complexity, target_word)

    def validate_analysis(self, parsed_data: Dict[str, Any], original_sentence: str) -> float:
        """Validate analysis quality and return confidence score (must return float)."""
        validation = self.validator.validate_result(parsed_data, original_sentence)
        return self._get_confidence(validation, default=0.0)

    # ===================================================================
    # HTML OUTPUT
    # ===================================================================

    def _generate_html_output(self, parsed_data: Dict[str, Any], sentence: str, complexity: str) -> str:
        """Generate colored HTML for Chinese Simplified sentences."""
        if not isinstance(parsed_data, dict):
            parsed_data = getattr(parsed_data, '__dict__', {}) if hasattr(parsed_data, '__dict__') else {}

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
                    html_parts.append(
                        f'<span style="color: {color_scheme.get("other", "#AAAAAA")}; font-weight: bold;">{uncovered}</span>'
                    )
                html_parts.append(f'<span style="color: {color}; font-weight: bold;">{word}</span>')
                covered = idx + len(word)
            else:
                html_parts.append(f'<span style="color: {color}; font-weight: bold;">{word}</span>')

        if covered < len(sentence):
            remaining = sentence[covered:]
            html_parts.append(
                f'<span style="color: {color_scheme.get("other", "#AAAAAA")}; font-weight: bold;">{remaining}</span>'
            )

        return ''.join(html_parts)

    def _map_grammatical_role_to_category(self, role: str) -> str:
        hierarchy = getattr(self.zh_config, 'grammatical_roles', {}).get('role_hierarchy', {})
        return hierarchy.get(role, role)

    # ===================================================================
    # ADDITIONAL METHODS
    # ===================================================================

    def get_sentence_generation_prompt(self, word, language, num_sentences, enriched_meaning="",
                                        min_length=3, max_length=15, difficulty="intermediate", topics=None):
        return self.prompt_builder.get_sentence_generation_prompt(
            word, language, num_sentences, enriched_meaning, min_length, max_length, difficulty, topics
        )

    def get_component_status(self) -> Dict[str, Any]:
        return {
            "version": _ZH_ANALYZER_VERSION,
            "config_loaded": bool(self.zh_config.grammatical_roles),
            "patterns_available": self.patterns.get_pattern_info() if hasattr(self.patterns, 'get_pattern_info') else True,
            "complexity_levels": ["beginner", "intermediate", "advanced"],
            "grammatical_roles_count": len(self.zh_config.grammatical_roles),
            "color_schemes": {level: len(self.get_color_scheme(level)) for level in ["beginner", "intermediate", "advanced"]}
        }
