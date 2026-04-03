# languages/japanese/domain/ja_fallbacks.py
"""
Japanese Fallbacks - Domain Component

Rule-based fallback analysis for when AI parsing fails.
Uses character type detection and common particle/word lists.
"""

import logging
import re
import unicodedata
from typing import Dict, Any, List
from .ja_config import JaConfig

logger = logging.getLogger(__name__)


class JaFallbacks:
    """Provides fallback responses when AI parsing fails for Japanese."""

    def __init__(self, config: JaConfig):
        self.config = config

    def create_fallback(self, sentence: str, complexity: str) -> Dict[str, Any]:
        """Create a basic fallback analysis for a Japanese sentence."""
        logger.info(f"Creating fallback analysis for sentence: '{sentence}'")

        # Tokenize Japanese sentence (basic approach using character types)
        tokens = self._basic_tokenize(sentence)
        word_explanations = []
        elements = {}

        for token in tokens:
            meaning = self.config.word_meanings.get('common_words', {}).get(
                token, self._generate_fallback_explanation(token)
            )
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
                'key_features': 'Japanese particle and word type detection',
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
        Basic Japanese tokenization by character type transitions.

        Splits on transitions between:
        - Kanji → Hiragana
        - Katakana → Hiragana
        - Hiragana particles (single-char common particles)

        This is a simplified approach — production would use MeCab/sudachi.
        """
        if not sentence:
            return []

        tokens = []
        current = ''

        for char in sentence:
            if char in ' 　\t\n':  # Whitespace
                if current:
                    tokens.append(current)
                    current = ''
                continue

            char_type = self._get_char_type(char)

            if not current:
                current = char
                continue

            prev_type = self._get_char_type(current[-1])

            # Split on type transitions (but keep kanji+hiragana verb readings together)
            if char_type != prev_type:
                # Exception: Don't split kanji followed by okurigana (hiragana verb endings)
                if prev_type == 'kanji' and char_type == 'hiragana':
                    # Check if this hiragana is a common particle
                    if char in 'はがをにでのともかよねへ' and len(current) > 0:
                        tokens.append(current)
                        current = char
                    else:
                        current += char
                elif prev_type == 'hiragana' and char_type == 'kanji':
                    tokens.append(current)
                    current = char
                elif prev_type == 'katakana' and char_type != 'katakana':
                    tokens.append(current)
                    current = char
                elif char_type == 'katakana' and prev_type != 'katakana':
                    tokens.append(current)
                    current = char
                else:
                    current += char
            else:
                current += char

        if current:
            tokens.append(current)

        # Post-process: split known particles from word endings
        result = []
        for token in tokens:
            split_tokens = self._split_particles(token)
            result.extend(split_tokens)

        return result

    def _split_particles(self, token: str) -> List[str]:
        """Split known single-character particles from the end of tokens."""
        if len(token) <= 1:
            return [token]

        # Common single-char particles that appear at token boundaries
        particles = {'は', 'が', 'を', 'に', 'で', 'の', 'と', 'も', 'か', 'よ', 'ね', 'へ'}

        # If the last character is a known particle and the rest is a word
        if token[-1] in particles and len(token) > 1:
            # Only split if the remaining part looks like a content word
            rest = token[:-1]
            if self._get_char_type(rest[-1]) == 'kanji' or len(rest) > 1:
                return [rest, token[-1]]

        return [token]

    def _get_char_type(self, char: str) -> str:
        """Determine the character type (kanji, hiragana, katakana, etc.)."""
        cp = ord(char)

        # Hiragana: U+3040–U+309F
        if 0x3040 <= cp <= 0x309F:
            return 'hiragana'

        # Katakana: U+30A0–U+30FF
        if 0x30A0 <= cp <= 0x30FF:
            return 'katakana'

        # CJK Unified Ideographs (Kanji): U+4E00–U+9FFF
        if 0x4E00 <= cp <= 0x9FFF:
            return 'kanji'

        # CJK Extension A
        if 0x3400 <= cp <= 0x4DBF:
            return 'kanji'

        # Punctuation (Japanese)
        if char in '。、！？「」『』（）・…～ー':
            return 'punctuation'

        # ASCII
        if cp < 128:
            if char.isalpha():
                return 'latin'
            if char.isdigit():
                return 'digit'
            return 'punctuation'

        return 'other'

    def _guess_role(self, word: str) -> str:
        """Guess grammatical role based on Japanese word characteristics."""
        if not word:
            return 'other'

        word_stripped = word.strip('。、！？「」『』（）')

        if not word_stripped:
            return 'other'

        # Known particles (single or multi-character)
        topic_particles = {'は'}
        subject_particles = {'が'}
        object_particles = {'を'}
        other_particles = {'に', 'で', 'の', 'と', 'から', 'まで', 'へ', 'も', 'より'}
        sentence_final = {'よ', 'ね', 'か', 'わ', 'ぞ', 'な', 'さ'}

        if word_stripped in topic_particles:
            return 'topic_particle'
        if word_stripped in subject_particles:
            return 'subject_particle'
        if word_stripped in object_particles:
            return 'object_particle'
        if word_stripped in other_particles:
            return 'particle'
        if word_stripped in sentence_final:
            return 'sentence_final_particle'

        # Copula
        if word_stripped in {'です', 'だ', 'である', 'でした', 'だった'}:
            return 'copula'

        # Common auxiliary suffixes
        if word_stripped in {'ます', 'ました', 'ません', 'ましょう', 'ない', 'なかった',
                            'られる', 'させる', 'たい', 'ている', 'てある'}:
            return 'auxiliary_verb'

        # Conjunctions
        conjunctions = {'しかし', 'そして', 'でも', 'けれども', 'だから', 'それで',
                       'ところが', 'または', 'そこで', 'すると', 'つまり'}
        if word_stripped in conjunctions:
            return 'conjunction'

        # Pronouns
        pronouns = {'私', 'わたし', '僕', 'ぼく', '俺', 'おれ', '彼', '彼女',
                    'あなた', '君', 'きみ', 'それ', 'これ', 'あれ', 'どれ',
                    'ここ', 'そこ', 'あそこ', 'どこ', '誰', 'だれ', '何', 'なに'}
        if word_stripped in pronouns:
            return 'pronoun'

        # Adverbs
        adverbs = {'とても', 'すごく', 'まだ', 'もう', 'よく', 'たくさん', 'ちょっと',
                  'いつも', '時々', 'ときどき', '全然', 'ぜんぜん', '少し', 'すこし',
                  'たぶん', 'きっと', 'ぜひ', '本当に', 'ほんとうに', 'もっと'}
        if word_stripped in adverbs:
            return 'adverb'

        # Interjections
        interjections = {'はい', 'いいえ', 'ええ', 'うん', 'ああ', 'おお', 'えっ',
                        'すみません', 'ありがとう', 'おはよう', 'こんにちは', 'こんばんは'}
        if word_stripped in interjections:
            return 'interjection'

        # Check character composition for further guessing
        has_kanji = any(self._get_char_type(c) == 'kanji' for c in word_stripped)
        has_hiragana = any(self._get_char_type(c) == 'hiragana' for c in word_stripped)
        has_katakana = any(self._get_char_type(c) == 'katakana' for c in word_stripped)

        # Katakana words are typically loanword nouns
        if has_katakana and not has_kanji and not has_hiragana:
            return 'noun'

        # い-adjective detection (ends with い and has kanji stem)
        if has_kanji and word_stripped.endswith('い') and len(word_stripped) >= 2:
            return 'i_adjective'

        # Verb detection — common verb endings
        verb_endings = ['る', 'う', 'く', 'す', 'つ', 'ぬ', 'ぶ', 'む',
                       'ます', 'ました', 'ません', 'った', 'んだ', 'ている',
                       'ない', 'なかった', 'よう', 'れる', 'せる']
        if has_kanji and any(word_stripped.endswith(e) for e in verb_endings):
            return 'verb'

        # If it has kanji, likely a noun (most common default in Japanese)
        if has_kanji:
            return 'noun'

        # Pure hiragana — could be particle, auxiliary, or common word
        if has_hiragana and not has_kanji:
            if len(word_stripped) <= 2:
                return 'particle'
            return 'adverb'

        # Punctuation
        if all(self._get_char_type(c) == 'punctuation' for c in word_stripped):
            return 'other'

        return 'other'

    def _normalize_text(self, text: str) -> str:
        """Normalize Japanese text for lookup."""
        if not text:
            return text
        return text.strip('。、！？「」『』（）・…～')

    def _get_fallback_color(self, role: str, complexity: str) -> str:
        """Get color for fallback role based on complexity."""
        colors = self.config.get_color_scheme(complexity)
        return colors.get(role, '#AAAAAA')

    def _generate_fallback_explanation(self, word: str) -> str:
        """Generate a basic explanation for an unknown word."""
        role = self._guess_role(word)
        role_descriptions = {
            'noun': 'a noun (名詞)',
            'verb': 'a verb (動詞)',
            'i_adjective': 'an い-adjective (い形容詞)',
            'na_adjective': 'a な-adjective (な形容詞)',
            'adjective': 'an adjective (形容詞)',
            'adverb': 'an adverb (副詞)',
            'particle': 'a grammatical particle (助詞)',
            'topic_particle': 'topic marker は — marks the topic of the sentence',
            'subject_particle': 'subject marker が — marks the grammatical subject',
            'object_particle': 'object marker を — marks the direct object',
            'copula': 'copula (繋辞) — equivalent to "is/am/are"',
            'auxiliary_verb': 'an auxiliary verb/suffix (助動詞)',
            'conjunction': 'a conjunction (接続詞)',
            'counter': 'a counter word (助数詞)',
            'pronoun': 'a pronoun (代名詞)',
            'sentence_final_particle': 'a sentence-final particle expressing mood',
            'honorific_verb': 'an honorific verb form (尊敬語)',
            'humble_verb': 'a humble verb form (謙譲語)',
            'interjection': 'an interjection (感動詞)',
            'other': 'a word in the sentence'
        }
        return role_descriptions.get(role, f'a {role.replace("_", " ")} in Japanese')
