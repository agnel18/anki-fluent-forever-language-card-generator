# languages/hungarian/infrastructure/hu_fallbacks.py
"""
Hungarian Fallbacks - Infrastructure Component

Rule-based fallback analysis for when AI parsing fails.
Uses Hungarian word patterns, common suffixes, and word lists.
"""

import logging
import re
from typing import Dict, Any, List
from ..domain.hu_config import HuConfig

logger = logging.getLogger(__name__)


class HuFallbacks:
    """Provides fallback responses when AI parsing fails for Hungarian."""

    def __init__(self, config: HuConfig):
        self.config = config

    def create_fallback(self, sentence: str, complexity: str) -> Dict[str, Any]:
        """Create a basic fallback analysis for a Hungarian sentence."""
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
                'key_features': 'Hungarian case marker and word type detection',
                'complexity_notes': 'Rule-based analysis without AI'
            },
            'word_explanations': word_explanations,
            'confidence': 0.3,
            'is_fallback': True
        }
        logger.info(f"Fallback created with {len(word_explanations)} word explanations")
        return result

    def _basic_tokenize(self, sentence: str) -> List[str]:
        """Basic Hungarian tokenization — split on whitespace, strip punctuation."""
        if not sentence:
            return []

        raw_tokens = sentence.split()
        tokens = []

        for token in raw_tokens:
            stripped = token.strip('.,!?;:…()„"»«–—')
            if stripped:
                tokens.append(stripped)

        return tokens

    def _lookup_meaning(self, word: str) -> str:
        """Look up word meaning from config."""
        common = self.config.word_meanings.get('common_words', {})
        if word in common:
            entry = common[word]
            if isinstance(entry, dict):
                return entry.get('meaning', str(entry))
            return str(entry)

        # Try lowercase
        word_lower = word.lower()
        if word_lower in common:
            entry = common[word_lower]
            if isinstance(entry, dict):
                return entry.get('meaning', str(entry))
            return str(entry)

        return self._generate_fallback_explanation(word)

    def _generate_fallback_explanation(self, word: str) -> str:
        """Generate a basic explanation based on word morphology."""
        word_lower = word.lower()

        # Check for common case suffixes
        case_suffixes = [
            ('-ban', 'in (inessive case)'), ('-ben', 'in (inessive case)'),
            ('-ba', 'into (illative case)'), ('-be', 'into (illative case)'),
            ('-ból', 'out of (elative case)'), ('-ből', 'out of (elative case)'),
            ('-on', 'on (superessive case)'), ('-en', 'on (superessive case)'), ('-ön', 'on (superessive case)'),
            ('-ra', 'onto (sublative case)'), ('-re', 'onto (sublative case)'),
            ('-ról', 'from/about (delative case)'), ('-ről', 'from/about (delative case)'),
            ('-nak', 'for/to (dative case)'), ('-nek', 'for/to (dative case)'),
            ('-val', 'with (instrumental case)'), ('-vel', 'with (instrumental case)'),
            ('-nál', 'at (adessive case)'), ('-nél', 'at (adessive case)'),
            ('-hoz', 'to (allative case)'), ('-hez', 'to (allative case)'), ('-höz', 'to (allative case)'),
            ('-tól', 'away from (ablative case)'), ('-től', 'away from (ablative case)'),
            ('-ig', 'until (terminative case)'),
            ('-ért', 'for (causal-final case)'),
            ('-ként', 'as (essive-formal case)'),
        ]

        for suffix, desc in case_suffixes:
            if word_lower.endswith(suffix[1:]):  # Remove the dash
                stem = word[:len(word) - len(suffix) + 1]
                return f"{stem} + {suffix} ({desc})"

        if word_lower.endswith('t') and len(word_lower) > 2:
            return f"Possibly accusative case (noun + -t)"

        return f"Hungarian word"

    def _guess_role(self, word: str) -> str:
        """Guess grammatical role based on Hungarian word characteristics."""
        if not word:
            return 'other'

        word_lower = word.lower().strip('.,!?;:…()„"»«–—')
        if not word_lower:
            return 'other'

        # Check common words first
        common = self.config.word_meanings.get('common_words', {})
        if word_lower in common:
            entry = common[word_lower]
            if isinstance(entry, dict):
                return entry.get('role', 'noun')
            return 'noun'

        # Articles
        if word_lower in ('a', 'az'):
            return 'definite_article'
        if word_lower == 'egy':
            return 'indefinite_article'

        # Postpositions
        postpositions = [
            'mellett', 'alatt', 'felett', 'mögött', 'előtt', 'között',
            'után', 'miatt', 'helyett', 'nélkül', 'szerint', 'felé',
            'körül', 'ellen', 'számára', 'részére', 'fölött', 'alá',
            'fölé', 'mögé', 'elé', 'mellé', 'közé', 'alól', 'mögül',
            'elől', 'mellől', 'közül', 'keresztül', 'át', 'túl'
        ]
        if word_lower in postpositions:
            return 'postposition'

        # Conjunctions
        conjunctions = [
            'és', 'vagy', 'de', 'mert', 'hogy', 'ha', 'mint',
            'sem', 'is', 'pedig', 'tehát', 'viszont', 'illetve',
            'valamint', 'hiszen', 'ugyanis', 'ám', 'bár', 'noha',
            'amikor', 'amíg', 'mielőtt', 'miután', 'ahogy'
        ]
        if word_lower in conjunctions:
            return 'conjunction'

        # Pronouns
        pronouns = [
            'én', 'te', 'ő', 'mi', 'ti', 'ők',
            'engem', 'téged', 'őt', 'minket', 'titeket', 'őket',
            'nekem', 'neked', 'neki', 'nekünk', 'nektek', 'nekik',
            'ez', 'az', 'ezek', 'azok', 'aki', 'ami', 'amely',
            'ki', 'mi', 'melyik', 'ilyen', 'olyan', 'milyen',
            'valaki', 'valami', 'senki', 'semmi', 'mindenki', 'minden'
        ]
        if word_lower in pronouns:
            return 'pronoun'

        # Copula
        copula_forms = ['van', 'volt', 'lesz', 'lenne', 'legyen', 'nincs', 'sincs']
        if word_lower in copula_forms:
            return 'copula'

        # Common preverbs (when separated from verb)
        preverbs = ['meg', 'el', 'ki', 'be', 'fel', 'le', 'vissza',
                    'össze', 'szét', 'hozzá', 'ide', 'oda', 'rá',
                    'bele', 'neki', 'utána', 'alá', 'fölé']
        if word_lower in preverbs:
            return 'preverb'

        # Check case suffixes
        back_inessive = word_lower.endswith('ban')
        front_inessive = word_lower.endswith('ben')
        if (back_inessive or front_inessive) and len(word_lower) > 4:
            return 'noun'  # Noun with inessive case

        # Check for verb endings (common conjugation patterns)
        verb_endings_indef = ['ok', 'ek', 'ök', 'sz', 'unk', 'ünk', 'tok', 'tek', 'tök', 'nak', 'nek']
        verb_endings_def = ['om', 'em', 'öm', 'od', 'ed', 'öd', 'ja', 'je', 'juk', 'jük', 'játok', 'játék', 'ják', 'ik']

        for ending in verb_endings_def + verb_endings_indef:
            if word_lower.endswith(ending) and len(word_lower) > len(ending) + 1:
                return 'verb'

        # Past tense indicators
        if re.search(r't[aáeé][mk]?$', word_lower) and len(word_lower) > 3:
            return 'verb'

        # Accusative case (-t at end after vowel, or -at/-ot/-et/-öt)
        if word_lower.endswith('t') and len(word_lower) > 2:
            return 'noun'

        # Default to noun for unknown Hungarian words
        return 'noun'

    def _get_fallback_color(self, role: str, complexity: str) -> str:
        """Get color for a role at given complexity level."""
        colors = self.config.get_color_scheme(complexity)
        return colors.get(role, colors.get('other', '#AAAAAA'))
