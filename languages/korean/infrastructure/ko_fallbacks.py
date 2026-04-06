# languages/korean/infrastructure/ko_fallbacks.py
"""
Korean Fallbacks - Infrastructure Component

Rule-based fallback analysis for when AI parsing fails.
Uses Hangul detection and common word/particle lists.
"""

import logging
import re
from typing import Dict, Any, List
from ..domain.ko_config import KoConfig

logger = logging.getLogger(__name__)


class KoFallbacks:
    """Provides fallback responses when AI parsing fails for Korean."""

    def __init__(self, config: KoConfig):
        self.config = config

    def create_fallback(self, sentence: str, complexity: str) -> Dict[str, Any]:
        """Create a basic fallback analysis for a Korean sentence."""
        logger.info(f"Creating fallback analysis for sentence: '{sentence}'")

        tokens = self._basic_tokenize(sentence)
        word_explanations = []
        elements = {}

        for token in tokens:
            meaning = self._lookup_meaning(token)
            role = self._guess_role(token)
            color = self._get_fallback_color(role, complexity)

            word_explanations.append([token, role, color, meaning])

            if role not in elements:
                elements[role] = []
            elements[role].append({'word': token, 'grammatical_role': role})

        result = {
            'sentence': sentence,
            'elements': elements,
            'explanations': {
                'overall_structure': 'Basic grammatical analysis (fallback)',
                'key_features': 'Korean particle and word type detection',
                'complexity_notes': 'Rule-based analysis without AI'
            },
            'word_explanations': word_explanations,
            'confidence': 0.3,
            'is_fallback': True
        }
        logger.info(f"Fallback created with {len(word_explanations)} word explanations")
        return result

    def _basic_tokenize(self, sentence: str) -> List[str]:
        """
        Basic Korean tokenization.

        Korean uses spaces between words, but particles are attached to nouns.
        This tokenizer splits on spaces and then attempts to separate
        common particles from their host words.
        """
        if not sentence:
            return []

        # Split on whitespace first
        raw_tokens = sentence.split()
        tokens = []

        for token in raw_tokens:
            # Strip punctuation
            stripped = token.strip('.,!?~…()「」')
            if not stripped:
                continue

            # Try to split trailing particles from noun
            split = self._split_particles(stripped)
            tokens.extend(split)

        return tokens

    def _split_particles(self, token: str) -> List[str]:
        """Split known particles from the end of words."""
        if len(token) <= 1:
            return [token]

        # Multi-character particles first (check longer ones first)
        multi_particles = ['에서', '까지', '부터', '밖에', '에게', '한테',
                          '처럼', '마다', '하고', '으로']
        for particle in multi_particles:
            if token.endswith(particle) and len(token) > len(particle):
                rest = token[:-len(particle)]
                if rest and self._is_hangul(rest[-1]):
                    return [rest, particle]

        # Single-character particles
        single_particles = {
            '은': 'topic_marker', '는': 'topic_marker',
            '이': 'subject_marker', '가': 'subject_marker',
            '을': 'object_marker', '를': 'object_marker',
            '에': 'locative_particle', '의': 'possessive_particle',
            '도': 'particle', '만': 'particle',
            '와': 'comitative_particle', '과': 'comitative_particle',
            '로': 'instrumental_particle',
        }

        if token[-1] in single_particles and len(token) > 1:
            rest = token[:-1]
            if rest and self._is_hangul(rest[-1]):
                return [rest, token[-1]]

        return [token]

    def _is_hangul(self, char: str) -> bool:
        """Check if a character is a Hangul syllable."""
        cp = ord(char)
        return 0xAC00 <= cp <= 0xD7AF

    def _lookup_meaning(self, word: str) -> str:
        """Look up word meaning from config."""
        # Check common words
        common = self.config.word_meanings.get('common_words', {})
        if word in common:
            entry = common[word]
            if isinstance(entry, dict):
                return entry.get('meaning', str(entry))
            return str(entry)

        # Check particles
        particles = self.config.word_meanings.get('particles', {})
        if word in particles:
            entry = particles[word]
            if isinstance(entry, dict):
                return entry.get('meaning', str(entry))
            return str(entry)

        return self._generate_fallback_explanation(word)

    def _guess_role(self, word: str) -> str:
        """Guess grammatical role based on Korean word characteristics."""
        if not word:
            return 'other'

        word_stripped = word.strip('.,!?~…()「」')
        if not word_stripped:
            return 'other'

        # Check particles first
        particles_map = self.config.word_meanings.get('particles', {})
        if word_stripped in particles_map:
            entry = particles_map[word_stripped]
            if isinstance(entry, dict):
                return entry.get('role', 'particle')
            return 'particle'

        # Check common words
        common = self.config.word_meanings.get('common_words', {})
        if word_stripped in common:
            entry = common[word_stripped]
            if isinstance(entry, dict):
                return entry.get('role', 'noun')
            return 'noun'

        # Known topic markers
        if word_stripped in ('은', '는'):
            return 'topic_marker'
        if word_stripped in ('이', '가'):
            return 'subject_marker'
        if word_stripped in ('을', '를'):
            return 'object_marker'
        if word_stripped in ('에', '에서'):
            return 'locative_particle'
        if word_stripped == '의':
            return 'possessive_particle'
        if word_stripped in ('와', '과', '하고', '이랑', '랑'):
            return 'comitative_particle'
        if word_stripped in ('로', '으로'):
            return 'instrumental_particle'
        if word_stripped == '께서':
            return 'honorific_particle'
        if word_stripped in ('도', '만', '부터', '까지', '밖에', '마다', '처럼', '보다'):
            return 'particle'

        # Copula forms
        copula_forms = {'이다', '입니다', '이에요', '예요', '이야', '입니까',
                       '아니다', '아닙니다', '아니에요', '아니야'}
        if word_stripped in copula_forms:
            return 'copula'

        # Verb/adjective endings
        if word_stripped.endswith(('습니다', 'ㅂ니다', '어요', '아요', '해요')):
            return 'verb'
        if word_stripped.endswith(('했다', '았다', '었다', '였다')):
            return 'verb'
        if word_stripped.endswith('다') and len(word_stripped) >= 2:
            return 'verb'

        # Conjunctions
        conjunctions = {'그리고', '그러나', '그래서', '하지만', '그런데', '또는',
                       '그렇지만', '그러므로', '따라서', '왜냐하면'}
        if word_stripped in conjunctions:
            return 'conjunction'

        # Interjections
        interjections = {'네', '아니요', '예', '아', '어', '와', '아이고',
                        '감사합니다', '안녕하세요', '죄송합니다'}
        if word_stripped in interjections:
            return 'interjection'

        # Adverbs
        adverbs = {'아주', '매우', '많이', '조금', '잘', '못', '안', '또',
                  '아직', '벌써', '항상', '자주', '가끔', '오늘', '내일',
                  '어제', '지금', '빨리', '천천히', '정말', '진짜', '너무'}
        if word_stripped in adverbs:
            return 'adverb'

        # Pronouns
        pronouns = {'나', '저', '너', '당신', '우리', '그', '그녀', '이것',
                    '그것', '저것', '여기', '거기', '저기', '누구', '무엇', '뭐',
                    '어디', '이분', '그분', '저분'}
        if word_stripped in pronouns:
            return 'pronoun'

        # Default: if it's all hangul, assume noun
        if all(self._is_hangul(c) for c in word_stripped):
            return 'noun'

        return 'other'

    def _get_fallback_color(self, role: str, complexity: str) -> str:
        """Get color for fallback role based on complexity."""
        colors = self.config.get_color_scheme(complexity)
        return colors.get(role, '#AAAAAA')

    def _generate_fallback_explanation(self, word: str) -> str:
        """Generate a basic explanation for an unknown word."""
        role = self._guess_role(word)
        role_descriptions = {
            'noun': 'a noun (명사)',
            'verb': 'a verb (동사)',
            'adjective': 'an adjective (형용사)',
            'adverb': 'an adverb (부사)',
            'particle': 'a grammatical particle (조사)',
            'topic_marker': '은/는 — topic marker particle',
            'subject_marker': '이/가 — subject marker particle',
            'object_marker': '을/를 — object marker particle',
            'locative_particle': '에/에서 — location/direction particle',
            'possessive_particle': '의 — possessive particle',
            'instrumental_particle': '(으)로 — means/direction particle',
            'comitative_particle': '와/과/하고 — and/with particle',
            'honorific_particle': '께서 — honorific subject marker',
            'copula': '이다/입니다 — copula (to be)',
            'auxiliary_verb': 'auxiliary/helping verb (보조 동사)',
            'conjunction': 'a conjunction (접속사)',
            'counter': 'a counter/classifier (단위 명사)',
            'pronoun': 'a pronoun (대명사)',
            'interjection': 'an interjection (감탄사)',
            'honorific_verb': 'honorific verb form (존경어)',
            'humble_verb': 'humble verb form (겸양어)',
            'connective_ending': 'connective ending (연결 어미)',
        }
        return role_descriptions.get(role, f"a {role.replace('_', ' ')}")
