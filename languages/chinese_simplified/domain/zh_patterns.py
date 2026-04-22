"""
Chinese Simplified Patterns - Domain Component

Following Chinese Traditional Clean Architecture gold standard:
- Centralized pattern definitions for Chinese Simplified processing
- Regex patterns for text analysis and validation
- Integration with external configuration files
- Support for different analysis types and complexity levels

RESPONSIBILITIES:
1. Define regex patterns for Chinese Simplified text processing
2. Provide pattern matching for grammatical elements
3. Support validation of character and word patterns
4. Handle Simplified vs Traditional character distinctions
5. Provide patterns for sentence segmentation and analysis

INTEGRATION:
- Used by ZhResponseParser for fallback parsing
- Depends on ZhConfig for pattern configuration
- Works with ZhValidator for pattern-based validation
- Supports ZhAnalyzer facade operations

PATTERN CATEGORIES:
1. Character classification (Simplified Chinese, punctuation)
2. Word boundary detection
3. Grammatical element recognition
4. Sentence structure patterns
5. Validation and sanity checking
"""

import re
import logging
from typing import Dict, List, Any, Optional, Pattern, Match
from dataclasses import dataclass

from .zh_config import ZhConfig

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

class ZhPatterns:
    """
    Manages regex patterns for Chinese Simplified text processing.

    Following Chinese Traditional Clean Architecture gold standard.
    """

    def __init__(self, config: ZhConfig):
        """
        Initialize patterns with configuration.
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
        """Initialize Chinese Simplified character recognition patterns."""
        # CJK Unified Ideographs (covers both Simplified and Traditional)
        chinese_ranges = [
            r'\u4E00-\u9FFF',  # CJK Unified Ideographs
            r'\u3400-\u4DBF',  # CJK Extension A
        ]

        # Compile character validation pattern
        char_pattern = f'[{"".join(chinese_ranges)}]'
        self._compiled_patterns['chinese_character'] = re.compile(char_pattern, re.UNICODE)

        # Chinese punctuation (same for Simplified/Traditional)
        self._compiled_patterns['chinese_punctuation'] = re.compile(
            r'[，。！？；：""''（）【】《》〈〉「」『』〖〗〔〕]',
            re.UNICODE
        )

        # Combined Chinese text pattern
        chinese_chars = "".join(chinese_ranges)
        punctuation = r'，。！？；：""\'\'（）【】《》'
        combined_pattern = f'[{chinese_chars}{punctuation}]+'
        self._compiled_patterns['chinese_text'] = re.compile(combined_pattern, re.UNICODE)

    def _init_word_patterns(self):
        """Initialize word and compound recognition patterns (Simplified)."""
        # Aspect marker combinations
        self._compiled_patterns['aspect_construction'] = re.compile(
            r'\b\w+(了|着|过)\b',
            re.UNICODE
        )

        # Modal particle patterns
        self._compiled_patterns['modal_construction'] = re.compile(
            r'\b\w+([吗呢吧啊哦嘛啦呀哇])\b',
            re.UNICODE
        )

        # Measure word constructions
        self._compiled_patterns['classifier_construction'] = re.compile(
            r'\b(\d+|一|二|两|三|四|五|六|七|八|九|十)+([个本杯张件位名座间])\b',
            re.UNICODE
        )

    def _init_grammatical_patterns(self):
        """Initialize grammatical element recognition patterns (Simplified)."""
        # Function word patterns
        self._compiled_patterns['structural_particles'] = re.compile(
            r'\b(的|地|得|了|着|过)\b',
            re.UNICODE
        )

        self._compiled_patterns['modal_particles'] = re.compile(
            r'\b(吗|呢|吧|啊|哦|嘛|啦|呀|哇)\b',
            re.UNICODE
        )

        # Aspect markers
        self._compiled_patterns['aspect_markers'] = re.compile(
            r'\b(了|着|过)\b',
            re.UNICODE
        )

        # Question patterns
        self._compiled_patterns['question_pattern'] = re.compile(
            r'.*[吗呢吧][？?]$',
            re.UNICODE
        )

        # Negation patterns
        self._compiled_patterns['negation_pattern'] = re.compile(
            r'\b(不|没|没有|不是|不会|不能)\b',
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
            r'.*?(?:是|有|在|去|来|做|说|看|听|吃|喝|玩|学|写|读).*',
            re.UNICODE
        )

    def match_pattern(self, pattern_name: str, text: str) -> List[PatternMatch]:
        """Match a specific pattern against text."""
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
                confidence=1.0,
                metadata=self._extract_match_metadata(match, pattern_name)
            )
            matches.append(pattern_match)

        return matches

    def validate_text(self, text: str) -> Dict[str, Any]:
        """Validate Chinese Simplified text using multiple patterns."""
        validation_results = {
            'is_valid': True,
            'issues': [],
            'confidence': 1.0,
            'pattern_matches': {}
        }

        # Character validation
        non_chinese_chars = []
        for char in text:
            if not self._compiled_patterns['chinese_character'].match(char) and char not in ' \t\n\r':
                if not self._compiled_patterns['chinese_punctuation'].match(char):
                    non_chinese_chars.append(char)

        if non_chinese_chars:
            validation_results['issues'].append(
                f"Found non-Chinese characters: {set(non_chinese_chars)}"
            )
            validation_results['confidence'] *= 0.8

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
        """Segment Chinese Simplified sentence into words/elements."""
        # Remove punctuation first
        clean_sentence = re.sub(r'[。！？，、；：「」『』（）《》〈〉【】]', '', sentence)

        # Start with character-level segmentation
        elements = list(clean_sentence)

        # Merge common compounds
        merged_elements = []
        i = 0
        while i < len(elements):
            if i + 1 < len(elements):
                compound = elements[i] + elements[i + 1]
                if self._is_compound_word(compound):
                    merged_elements.append(compound)
                    i += 2
                    continue
            merged_elements.append(elements[i])
            i += 1

        return merged_elements

    def _is_compound_word(self, compound: str) -> bool:
        """Check if a two-character sequence is a compound word (Simplified)."""
        simplified_compounds = [
            '着书', '里面', '借口', '征求', '并且', '只有',  # Common words
            '一个', '一本', '一杯', '一张', '一件',          # Numbers + classifiers
            '去了', '看了', '吃了', '学了', '写了',          # Verb + aspect
            '着呢', '着吗', '着吧', '着啊',                  # Aspect + modal
        ]
        return compound in simplified_compounds

    def _extract_match_metadata(self, match: Match, pattern_name: str) -> Dict[str, Any]:
        """Extract metadata from a regex match."""
        metadata = {
            'groups': match.groups(),
            'groupdict': match.groupdict(),
            'span': match.span()
        }

        if pattern_name == 'aspect_construction':
            metadata['aspect_type'] = match.group(1) if match.groups() else 'unknown'
        elif pattern_name == 'modal_construction':
            metadata['modal_type'] = match.group(1) if match.groups() else 'unknown'
        elif pattern_name == 'classifier_construction':
            metadata['classifier'] = match.group(2) if len(match.groups()) > 1 else 'unknown'

        return metadata

    def get_pattern_info(self) -> Dict[str, Any]:
        """Get information about available patterns."""
        return {
            'available_patterns': list(self._compiled_patterns.keys()),
            'pattern_count': len(self._compiled_patterns),
            'config_patterns': list(self.config.patterns.keys())
        }