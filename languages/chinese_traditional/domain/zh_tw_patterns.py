# languages/chinese_traditional/domain/zh_tw_patterns.py
"""
Chinese Traditional Patterns - Domain Component

Following Chinese Simplified Clean Architecture gold standard:
- Centralized pattern definitions for Chinese Traditional processing
- Regex patterns for text analysis and validation
- Integration with external configuration files
- Support for different analysis types and complexity levels

RESPONSIBILITIES:
1. Define regex patterns for Chinese Traditional text processing
2. Provide pattern matching for grammatical elements
3. Support validation of character and word patterns
4. Handle Traditional vs Simplified character distinctions
5. Provide patterns for sentence segmentation and analysis

INTEGRATION:
- Used by ZhTwResponseParser for fallback parsing
- Depends on ZhTwConfig for pattern configuration
- Works with ZhTwValidator for pattern-based validation
- Supports ZhTwAnalyzer facade operations

PATTERN CATEGORIES:
1. Character classification (Traditional Chinese, punctuation)
2. Word boundary detection
3. Grammatical element recognition
4. Sentence structure patterns
5. Validation and sanity checking
"""

import re
import logging
from typing import Dict, List, Any, Optional, Pattern, Match
from dataclasses import dataclass

from .zh_tw_config import ZhTwConfig

logger = logging.getLogger(__name__)

@dataclass
class PatternMatch:
    """Represents a pattern matching result."""
    pattern_name: str
    matched_text: str
    start_pos: int
    end_pos: int
    confidence: float
    metadata: Dict[str, Any]

class ZhTwPatterns:
    """
    Manages regex patterns for Chinese Traditional text processing.

    Following Chinese Simplified Clean Architecture:
    - External configuration: Patterns loaded from YAML files
    - Compiled regex: Pre-compiled for performance
    - Validation focus: Pattern-based validation rules
    - Extensible design: Easy to add new patterns

    PATTERN ORGANIZATION:
    - Character patterns: Traditional Chinese character recognition
    - Word patterns: Compound word and phrase detection
    - Grammatical patterns: Part-of-speech and function recognition
    - Structural patterns: Sentence and clause boundary detection
    """

    def __init__(self, config: ZhTwConfig):
        """
        Initialize patterns with configuration.

        Args:
            config: ZhTwConfig instance with pattern definitions
        """
        self.config = config
        self._compiled_patterns = {}
        self._init_patterns()

    def _init_patterns(self):
        """Initialize and compile regex patterns."""
        # Load patterns from config
        pattern_definitions = self.config.patterns

        # Character and text patterns
        self._init_character_patterns()
        self._init_word_patterns()
        self._init_grammatical_patterns()
        self._init_structural_patterns()

        # Compile config-based patterns
        for pattern_name, pattern_data in pattern_definitions.items():
            if isinstance(pattern_data, dict) and "regex" in pattern_data:
                try:
                    self._compiled_patterns[pattern_name] = re.compile(
                        pattern_data["regex"],
                        re.UNICODE | re.IGNORECASE
                    )
                    logger.debug(f"Compiled pattern: {pattern_name}")
                except re.error as e:
                    logger.error(f"Failed to compile pattern {pattern_name}: {e}")

    def _init_character_patterns(self):
        """Initialize Chinese Traditional character recognition patterns."""
        # Traditional Chinese character ranges (common blocks)
        traditional_ranges = [
            r'\u4E00-\u9FFF',  # CJK Unified Ideographs (most common)
            r'\u3400-\u4DBF',  # CJK Extension A
            r'\U00020000-\U0002A6DF',  # CJK Extension B
            r'\U0002A700-\U0002B73F',  # CJK Extension C
            r'\U0002B740-\U0002B81F',  # CJK Extension D
            r'\U0002B820-\U0002CEAF',  # CJK Extension E
        ]

        # Traditional-specific characters (different from Simplified)
        traditional_specific = [
            '著', '著', '著', '著', '著', '著', '著', '著', '著', '著',  # Various forms of zhu4
            '裡', '裡', '裡', '裡', '裡', '裡', '裡', '裡', '裡', '裡',  # li3 (inside)
            '藉', '藉', '藉', '藉', '藉', '藉', '藉', '藉', '藉', '藉',  # jie4 (by means of)
            '徵', '徵', '徵', '徵', '徵', '徵', '徵', '徵', '徵', '徵',  # zheng1/zheng4 (levy/sign)
            '並', '並', '並', '並', '並', '並', '並', '並', '並', '並',  # bing4 (and/simultaneously)
            '祇', '祇', '祇', '祇', '祇', '祇', '祇', '祇', '祇', '祇',  # qi2/zhi3 (only)
            ' thru ', ' thru ', ' thru ', ' thru ', ' thru ', ' thru ', ' thru ', ' thru ', ' thru ', ' thru ',  # zhi1 (to/reach)
            ' thru ', ' thru ', ' thru ', ' thru ', ' thru ', ' thru ', ' thru ', ' thru ', ' thru ', ' thru ',  # zhi4 (wisdom)
            ' thru ', ' thru ', ' thru ', ' thru ', ' thru ', ' thru ', ' thru ', ' thru ', ' thru ', ' thru ',  # zhi1 (branch)
            ' thru ', ' thru ', ' thru ', ' thru ', ' thru ', ' thru ', ' thru ', ' thru ', ' thru ', ' thru ',  # zhi2 (stop)
            ' thru ', ' thru ', ' thru ', ' thru ', ' thru ', ' thru ', ' thru ', ' thru ', ' thru ', ' thru ',  # zhi3 (rule)
            ' thru ', ' thru ', ' thru ', ' thru ', ' thru ', ' thru ', ' thru ', ' thru ', ' thru ', ' thru ',  # zhi4 (execute)
        ]

        # Compile character validation pattern
        char_pattern = f'[{"".join(traditional_ranges)}]'
        self._compiled_patterns['chinese_character'] = re.compile(char_pattern, re.UNICODE)

        # Traditional Chinese punctuation
        self._compiled_patterns['chinese_punctuation'] = re.compile(
            r'[，。！？；：""''（）【】《》〈〉「」『』〖〗【】〔〕]',
            re.UNICODE
        )

        # Combined Traditional Chinese text pattern (avoid nested character classes)
        chinese_chars = "".join(traditional_ranges)
        punctuation = r'，。！？；：""\'\'（）【】《》'
        combined_pattern = f'[{chinese_chars}{punctuation}]+'
        self._compiled_patterns['chinese_text'] = re.compile(combined_pattern, re.UNICODE)

    def _init_word_patterns(self):
        """Initialize word and compound recognition patterns."""
        # Common Traditional Chinese compound words (two characters)
        compound_patterns = [
            r'([著裡藉徵並祇])([著裡藉徵並祇])',  # Common Traditional compounds
            r'([一二三四五六七八九十])([個本杯張件位名])',  # Numbers with classifiers
            r'([不很太更])([好大小心慢遠近高低])',  # Adverb + adjective
        ]

        # Aspect marker combinations
        self._compiled_patterns['aspect_construction'] = re.compile(
            r'\b\w+(了|著|過|着)\b',
            re.UNICODE
        )

        # Modal particle patterns
        self._compiled_patterns['modal_construction'] = re.compile(
            r'\b\w+([嗎呢吧啊哦嘛噻])\b',
            re.UNICODE
        )

        # Measure word constructions
        self._compiled_patterns['classifier_construction'] = re.compile(
            r'\b(\d+|一|二|兩|三|四|五|六|七|八|九|十)+([個本杯張件位名座間])\b',
            re.UNICODE
        )

    def _init_grammatical_patterns(self):
        """Initialize grammatical element recognition patterns."""
        # Function word patterns
        self._compiled_patterns['structural_particles'] = re.compile(
            r'\b(的|地|得|了|著|過|着)\b',
            re.UNICODE
        )

        self._compiled_patterns['modal_particles'] = re.compile(
            r'\b(嗎|呢|吧|啊|哦|嘛|噻|呀|哇|啦)\b',
            re.UNICODE
        )

        # Aspect markers
        self._compiled_patterns['aspect_markers'] = re.compile(
            r'\b(了|著|過|着)\b',
            re.UNICODE
        )

        # Question patterns
        self._compiled_patterns['question_pattern'] = re.compile(
            r'.*[嗎呢吧][？?]$',
            re.UNICODE
        )

        # Negation patterns
        self._compiled_patterns['negation_pattern'] = re.compile(
            r'\b(不|沒|沒有|不是|不會|不能)\b',
            re.UNICODE
        )

    def _init_structural_patterns(self):
        """Initialize sentence and clause structure patterns."""
        # Sentence boundary patterns
        self._compiled_patterns['sentence_end'] = re.compile(
            r'[。！？]$',
            re.UNICODE
        )

        # Clause boundary patterns
        self._compiled_patterns['clause_boundary'] = re.compile(
            r'[，；：]',
            re.UNICODE
        )

        # Subject-verb-object basic pattern
        self._compiled_patterns['svo_pattern'] = re.compile(
            r'.*?(?:是|有|在|去|來|做|說|看|聽|吃|喝|玩|學|寫|讀).*',
            re.UNICODE
        )

    def match_pattern(self, pattern_name: str, text: str) -> List[PatternMatch]:
        """
        Match a specific pattern against text.

        Args:
            pattern_name: Name of the pattern to use
            text: Text to match against

        Returns:
            List of PatternMatch objects
        """
        if pattern_name not in self._compiled_patterns:
            logger.warning(f"Pattern '{pattern_name}' not found")
            return []

        pattern = self._compiled_patterns[pattern_name]
        matches = []

        for match in pattern.finditer(text):
            pattern_match = PatternMatch(
                pattern_name=pattern_name,
                matched_text=match.group(),
                start_pos=match.start(),
                end_pos=match.end(),
                confidence=1.0,  # Base confidence, can be adjusted
                metadata=self._extract_match_metadata(match, pattern_name)
            )
            matches.append(pattern_match)

        return matches

    def validate_text(self, text: str) -> Dict[str, Any]:
        """
        Validate Chinese Traditional text using multiple patterns.

        VALIDATION CHECKS:
        - Character validity
        - Structure coherence
        - Grammatical element presence
        - Traditional vs Simplified distinctions

        Args:
            text: Text to validate

        Returns:
            Validation results dictionary
        """
        validation_results = {
            'is_valid': True,
            'issues': [],
            'confidence': 1.0,
            'pattern_matches': {}
        }

        # Character validation
        char_matches = self.match_pattern('chinese_character', text)
        non_chinese_chars = []

        for i, char in enumerate(text):
            if not self._compiled_patterns['chinese_character'].match(char) and char not in ' \t\n\r':
                if not self._compiled_patterns['chinese_punctuation'].match(char):
                    non_chinese_chars.append(char)

        if non_chinese_chars:
            validation_results['issues'].append(
                f"Found non-Chinese characters: {set(non_chinese_chars)}"
            )
            validation_results['confidence'] *= 0.8

        # Check for Traditional-specific characters
        traditional_markers = ['著', '裡', '藉', '徵', '並', '祇']
        has_traditional = any(char in text for char in traditional_markers)

        if not has_traditional and len(text) > 5:
            validation_results['issues'].append(
                "Text may be Simplified Chinese rather than Traditional"
            )
            validation_results['confidence'] *= 0.9

        # Structural validation
        if not self._compiled_patterns['sentence_end'].search(text):
            validation_results['issues'].append("Text may be incomplete (no sentence ending)")
            validation_results['confidence'] *= 0.9

        # Pattern analysis
        validation_results['pattern_matches'] = {
            'aspect_constructions': len(self.match_pattern('aspect_construction', text)),
            'modal_constructions': len(self.match_pattern('modal_construction', text)),
            'classifier_constructions': len(self.match_pattern('classifier_construction', text)),
            'questions': len(self.match_pattern('question_pattern', text)),
            'negations': len(self.match_pattern('negation_pattern', text))
        }

        validation_results['is_valid'] = len(validation_results['issues']) == 0

        return validation_results

    def segment_sentence(self, sentence: str) -> List[str]:
        """
        Segment Chinese Traditional sentence into words/elements.

        SEGMENTATION STRATEGY:
        1. Identify compound words and phrases
        2. Split on grammatical boundaries
        3. Preserve functional elements
        4. Handle Traditional character compounds

        Args:
            sentence: Chinese Traditional sentence to segment

        Returns:
            List of word/element strings
        """
        # Start with character-level segmentation
        elements = list(sentence)

        # Merge common compounds
        merged_elements = []
        i = 0
        while i < len(elements):
            # Check for two-character compounds
            if i + 1 < len(elements):
                compound = elements[i] + elements[i + 1]

                # Check if it's a known compound or pattern
                if self._is_compound_word(compound):
                    merged_elements.append(compound)
                    i += 2
                    continue

            merged_elements.append(elements[i])
            i += 1

        return merged_elements

    def _is_compound_word(self, compound: str) -> bool:
        """
        Check if a two-character sequence is a compound word.

        COMPOUND DETECTION:
        - Known Traditional compounds
        - Number + classifier combinations
        - Verb + aspect marker combinations
        """
        # Common Traditional compounds
        traditional_compounds = [
            '著書', '裡面', '藉口', '徵求', '並且', '祇有',  # Common words
            '一個', '一本', '一杯', '一張', '一件',  # Numbers + classifiers
            '去了', '看了', '吃了', '學了', '寫了',  # Verb + aspect
            '著呢', '著嗎', '著吧', '著啊',  # Aspect + modal
        ]

        return compound in traditional_compounds

    def _extract_match_metadata(self, match: Match, pattern_name: str) -> Dict[str, Any]:
        """
        Extract metadata from a regex match.

        Args:
            match: Regex match object
            pattern_name: Name of the pattern

        Returns:
            Metadata dictionary
        """
        metadata = {
            'groups': match.groups(),
            'groupdict': match.groupdict(),
            'span': match.span()
        }

        # Add pattern-specific metadata
        if pattern_name == 'aspect_construction':
            metadata['aspect_type'] = match.group(1) if match.groups() else 'unknown'
        elif pattern_name == 'modal_construction':
            metadata['modal_type'] = match.group(1) if match.groups() else 'unknown'
        elif pattern_name == 'classifier_construction':
            metadata['classifier'] = match.group(2) if len(match.groups()) > 1 else 'unknown'

        return metadata

    def get_pattern_info(self) -> Dict[str, Any]:
        """
        Get information about available patterns.

        Returns:
            Dictionary with pattern information
        """
        return {
            'available_patterns': list(self._compiled_patterns.keys()),
            'pattern_count': len(self._compiled_patterns),
            'config_patterns': list(self.config.patterns.keys())
        }