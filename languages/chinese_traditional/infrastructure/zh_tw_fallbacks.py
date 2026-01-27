# languages/chinese_traditional/infrastructure/zh_tw_fallbacks.py
"""
Fallback mechanisms for Chinese Traditional analyzer.
Provides error recovery and alternative analysis methods when AI analysis fails.
"""

import re
import logging
from typing import Dict, List, Any, Optional

from ..domain.zh_tw_config import ZhTwConfig

logger = logging.getLogger(__name__)


class ZhTwFallbacks:
    """
    Fallback analysis methods for Chinese Traditional.

    Provides rule-based analysis when AI analysis is unavailable or fails:
    - Pattern-based word segmentation
    - Rule-based grammatical role assignment
    - Dictionary-based meaning lookup
    - Basic sentence structure analysis
    """

    def __init__(self, config: ZhTwConfig):
        self.config = config
        self._initialize_fallback_data()

    def _initialize_fallback_data(self):
        """Initialize fallback analysis data."""

        # Basic word patterns for segmentation
        self.segmentation_patterns = [
            # Numbers with measure words
            r'(\d+)(個|本|杯|張|件|位|隻|頭|條|棵|顆|粒|滴|片|塊|座|棟|艘|輛|架)',
            # Time expressions
            r'(今天|昨天|明天|上午|下午|晚上|早上|中午|夜裡)',
            # Location words
            r'(這裡|那裡|哪裡|上面|下面|前面|後面|左邊|右邊|中間)',
            # Pronouns
            r'(我|你|他|她|它|我們|你們|他們|她們|它們|這|那|哪|誰|什麼|怎麼)',
            # Question particles
            r'(嗎|呢|吧|呀|啦|喲|麼)',
            # Aspect particles
            r'(了|著|過|起來|下去|出來|進來|回來|起來)',
            # Structural particles
            r'(的|地|得)',
            # Conjunctions (2+ characters)
            r'(如果|因為|所以|但是|雖然|而且|或者|而且|而且|以後|以前|現在|那麼|可是|並且|反而|反而)',
            # Prepositions
            r'(在|從|到|給|對|向|跟|被|讓|叫|比|往|朝|沿|順|按|照|靠|臨)',
            # Common compound words (2-3 characters)
            r'(答案|等於|所以|但是|如果|因為|雖然|而且|那麼|可是|並且|以後|以前|現在)',
            # Common nouns
            r'(學校|學生|老師|問題|時間|地方|事情|東西|朋友|家人|國家|城市|公司)',
            # Common verbs
            r'(學習|工作|玩耍|休息|吃飯|喝水|睡覺|起來|下去|出來|進來|回來)',
            # Numbers with Chinese numerals
            r'([一二三四五六七八九十百千萬]+)',
        ]

        # Basic dictionary for common words
        self.basic_dictionary = {
            # Pronouns
            '我': ('I/me', 'pronoun'),
            '你': ('you', 'pronoun'),
            '他': ('he/him', 'pronoun'),
            '她': ('she/her', 'pronoun'),
            '它': ('it', 'pronoun'),
            '我們': ('we/us', 'pronoun'),
            '你們': ('you (plural)', 'pronoun'),
            '他們': ('they/them (male)', 'pronoun'),
            '她們': ('they/them (female)', 'pronoun'),

            # Measure words
            '個': ('classifier for people/objects', 'measure_word'),
            '本': ('classifier for books', 'measure_word'),
            '杯': ('cup/glass', 'measure_word'),
            '張': ('classifier for flat objects', 'measure_word'),

            # Common verbs
            '是': ('to be', 'verb'),
            '有': ('to have', 'verb'),
            '吃': ('to eat', 'verb'),
            '喝': ('to drink', 'verb'),
            '看': ('to see/look/watch', 'verb'),
            '聽': ('to listen/hear', 'verb'),
            '說': ('to speak/say', 'verb'),
            '做': ('to do/make', 'verb'),
            '去': ('to go', 'verb'),
            '來': ('to come', 'verb'),

            # Common compound words
            '如果': ('if/whether - conditional conjunction', 'conjunction'),
            '因為': ('because - causal conjunction', 'conjunction'),
            '所以': ('therefore/so - result conjunction', 'conjunction'),
            '但是': ('but/however - contrast conjunction', 'conjunction'),
            '雖然': ('although/even though - concessive conjunction', 'conjunction'),
            '而且': ('moreover/furthermore - additive conjunction', 'conjunction'),
            '那麼': ('then/in that case - conjunctive adverb', 'conjunction'),
            '可是': ('but/however - contrast conjunction', 'conjunction'),
            '並且': ('and/moreover - additive conjunction', 'conjunction'),
            '以後': ('afterwards/later - time expression', 'adverb'),
            '以前': ('before/formerly - time expression', 'adverb'),
            '現在': ('now/currently - time expression', 'adverb'),

            # Math and common verbs
            '加': ('to add/plus', 'verb'),
            '等於': ('equals/is equal to', 'verb'),
            '就是': ('is exactly/is just', 'verb'),

            # Adverbs
            '就': ('then/precisely - adverb indicating immediacy', 'adverb'),

            # Nouns
            '答案': ('answer/solution', 'noun'),
            '問題': ('question/problem', 'noun'),
            '時間': ('time', 'noun'),
            '地方': ('place/location', 'noun'),
            '事情': ('thing/matter', 'noun'),
            '東西': ('thing/object', 'noun'),
            '朋友': ('friend', 'noun'),
            '家人': ('family member', 'noun'),
            '國家': ('country/nation', 'noun'),
            '城市': ('city', 'noun'),
            '公司': ('company', 'noun'),
        }

    def generate_fallback_analysis(self, sentence: str, target_word: str = "") -> Dict[str, Any]:
        """
        Generate fallback analysis when AI analysis fails.

        Args:
            sentence: The sentence to analyze
            target_word: Target word being learned (optional)

        Returns:
            Basic analysis result using rule-based methods
        """

        try:
            # Segment the sentence into words
            words = self._segment_sentence(sentence)

            # Analyze each word
            analyzed_words = []
            for word in words:
                analysis = self._analyze_word(word)
                analyzed_words.append(analysis)

            # Find word combinations
            combinations = self._find_combinations(words)

            return {
                'sentence_index': 1,
                'original_sentence': sentence,
                'words': analyzed_words,
                'word_combinations': combinations,
                'analysis_method': 'fallback_rule_based',
                'confidence': 'low'
            }

        except Exception as e:
            logger.error(f"Fallback analysis failed: {e}")
            return self._generate_minimal_fallback(sentence)

    def _segment_sentence(self, sentence: str) -> List[str]:
        """
        Improved word segmentation for Chinese sentences.
        Uses pattern matching to identify known words and phrases.

        Args:
            sentence: Chinese sentence

        Returns:
            List of words
        """

        # Remove punctuation for segmentation
        clean_sentence = re.sub(r'[，。！？；：""''（）《》【】]', '', sentence)

        if not clean_sentence:
            return []

        # Find all matches from all patterns
        all_matches = []
        for pattern in self.segmentation_patterns:
            matches = list(re.finditer(pattern, clean_sentence))
            all_matches.extend(matches)

        if not all_matches:
            # No patterns matched, fall back to character segmentation
            return list(clean_sentence)

        # Sort matches by start position
        all_matches.sort(key=lambda m: m.start())

        # Merge overlapping matches and extract words
        words = []
        last_end = 0

        for match in all_matches:
            # Add text before match as individual characters
            if match.start() > last_end:
                prefix = clean_sentence[last_end:match.start()]
                if prefix:
                    # Split prefix into individual characters
                    words.extend(list(prefix))

            # Add the matched word
            word = match.group()
            if word not in words:  # Avoid duplicates
                words.append(word)

            last_end = max(last_end, match.end())

        # Add remaining text
        if last_end < len(clean_sentence):
            suffix = clean_sentence[last_end:]
            if suffix:
                words.extend(list(suffix))

        return words

    def _split_unknown_text(self, text: str) -> List[str]:
        """
        Split unknown text into potential words.
        This is a very basic approach.

        Args:
            text: Text to split

        Returns:
            List of word candidates
        """

        # For now, treat as single words if short, split if long
        if len(text) <= 4:
            return [text] if text else []
        else:
            # Try to split into 2-3 character chunks
            chunks = []
            i = 0
            while i < len(text):
                chunk_size = min(3, len(text) - i)
                chunks.append(text[i:i + chunk_size])
                i += chunk_size
            return chunks

    def _analyze_word(self, word: str) -> Dict[str, Any]:
        """
        Analyze a single word using dictionary lookup and basic rules.

        Args:
            word: Word to analyze

        Returns:
            Analysis result
        """

        # Check config word meanings first (from JSON file)
        if word in self.config.word_meanings:
            meaning = self.config.word_meanings[word]
            role = self._guess_grammatical_role(word)
            return {
                'word': word,
                'individual_meaning': meaning,
                'grammatical_role': role,
                'confidence': 'high'
            }

        # Check basic dictionary as fallback
        if word in self.basic_dictionary:
            meaning, role = self.basic_dictionary[word]
            return {
                'word': word,
                'individual_meaning': meaning,
                'grammatical_role': role,
                'confidence': 'high'
            }

        # Rule-based analysis
        role = self._guess_grammatical_role(word)
        meaning = self._generate_fallback_explanation(word, role)

        return {
            'word': word,
            'individual_meaning': meaning,
            'grammatical_role': role,
            'confidence': 'low'
        }

    def _generate_fallback_explanation(self, word: str, role: str) -> str:
        """Generate a meaningful explanation for a word when no specific meaning is available."""
        role_descriptions = {
            'noun': 'a thing, person, or concept',
            'verb': 'an action or state of being',
            'adjective': 'a word that describes a noun',
            'pronoun': 'a word that replaces a noun',
            'particle': 'a grammatical function word',
            'aspect_particle': 'a marker indicating action completion, ongoing state, or experience',
            'modal_particle': 'a particle expressing mood, tone, or attitude',
            'structural_particle': 'a particle connecting elements in a sentence',
            'measure_word': 'a classifier used with numerals and nouns',
            'preposition': 'a word showing relationship or direction',
            'conjunction': 'a word connecting clauses or sentences',
            'interjection': 'an exclamation or sound',
            'numeral': 'a number',
            'interrogative': 'a question word',
            'other': 'a word in the sentence'
        }
        return role_descriptions.get(role, f'a {role} in Chinese Traditional')

    def _guess_grammatical_role(self, word: str) -> str:
        """
        Guess grammatical role based on word characteristics and patterns.
        Similar to Chinese Simplified but adapted for Traditional characters.
        """

        # Clean the word
        clean_word = word.strip('。！？，、；："''（）【】{}')

        # Aspect markers (very important in Chinese)
        if clean_word in ['了', '著', '過']:
            return 'aspect_particle'

        # Modal particles
        if clean_word in ['嗎', '呢', '吧', '啊', '呀', '啦', '嘛']:
            return 'modal_particle'

        # Structural particles
        if clean_word in ['的', '地', '得']:
            return 'structural_particle'

        # General particles
        if clean_word in ['了', '著', '過', '的', '地', '得', '嗎', '呢', '吧', '啊']:
            return 'particle'

        # Common classifiers (Traditional characters)
        traditional_classifiers = ['個', '本', '杯', '張', '件', '位', '隻', '頭', '條', '棵', '顆', '粒', '滴', '片', '塊', '座', '棟', '艘', '輛', '架']
        if clean_word in traditional_classifiers:
            return 'measure_word'

        # Pronouns (Traditional characters)
        if clean_word in ['我', '你', '他', '她', '它', '我們', '你們', '他們', '她們', '這', '那', '這些', '那些']:
            return 'pronoun'

        # Question words
        if clean_word in ['什麼', '誰', '哪裡', '什麼時候', '怎麼', '為什麼', '多少', '幾']:
            return 'interrogative'

        # Conjunctions
        if clean_word in ['和', '與', '或', '但是', '因為', '所以', '如果', '雖然']:
            return 'conjunction'

        # Prepositions
        if clean_word in ['在', '從', '到', '給', '對', '向', '跟', '被']:
            return 'preposition'

        # Numbers
        if clean_word.isdigit() or clean_word in ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '百', '千', '萬']:
            return 'numeral'

        # Interjections
        if clean_word in ['啊', '哦', '哎呀', '嗯', '唉']:
            return 'interjection'

        # Verb-like endings or common verbs (basic heuristics)
        if len(clean_word) >= 2 and any(clean_word.endswith(suffix) for suffix in ['了', '著', '過', '來', '去', '到']):
            return 'verb'

        # Adjective-like (basic heuristics - adjectives often end with 的 or are single syllable)
        if len(clean_word) == 1 or clean_word.endswith('的'):
            return 'adjective'

        # Default to noun for most other words (most common in Chinese)
        return 'noun'

    def _find_combinations(self, words: List[str]) -> List[Dict[str, Any]]:
        """
        Find potential word combinations in the sentence.

        Args:
            words: List of words

        Returns:
            List of compound word analyses
        """

        combinations = []

        # Look for common two-word combinations
        for i in range(len(words) - 1):
            pair = words[i] + words[i + 1]

            # Check if this forms a known compound
            if pair in self.basic_dictionary:
                meaning, role = self.basic_dictionary[pair]
                combinations.append({
                    'text': pair,
                    'combined_meaning': meaning,
                    'grammatical_role': role
                })

        return combinations

    def _generate_minimal_fallback(self, sentence: str) -> Dict[str, Any]:
        """
        Generate minimal fallback when all else fails.

        Args:
            sentence: Original sentence

        Returns:
            Minimal analysis result
        """

        return {
            'sentence_index': 1,
            'original_sentence': sentence,
            'words': [{
                'word': sentence,
                'individual_meaning': 'Analysis failed - please check sentence manually',
                'grammatical_role': 'noun',
                'confidence': 'none'
            }],
            'word_combinations': [],
            'analysis_method': 'minimal_fallback',
            'error': 'Complete analysis failure'
        }