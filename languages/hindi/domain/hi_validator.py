# languages/hindi/domain/hi_validator.py
import logging
from typing import Dict, Any, List
from .hi_config import HiConfig

logger = logging.getLogger(__name__)

class HiValidator:
    """Validates parsed grammar analysis results."""
    
    def __init__(self, config: HiConfig):
        self.config = config
    
    def validate_result(self, result: Dict[str, Any], sentence: str) -> Dict[str, Any]:
        """Validate and enhance result with confidence scores."""
        confidence = self._calculate_confidence(result, sentence)
        result['confidence'] = confidence
        
        if confidence < 0.5:
            logger.warning(f"Low confidence ({confidence}) for sentence: {sentence}")
        
        return result
    
    def _calculate_confidence(self, result: Dict[str, Any], sentence: str) -> float:
        """Calculate confidence score based on various heuristics."""
        score = 1.0
        
        # Check if words match sentence
        word_explanations = result.get('word_explanations', [])
        sentence_words = sentence.split()
        
        if len(word_explanations) != len(sentence_words):
            score *= 0.8
        
        # Check role distribution
        roles = [item[1] for item in word_explanations if len(item) > 1]
        if not roles:
            return 0.0
        
        # Penalize too many 'other' roles
        other_count = roles.count('other')
        if other_count / len(roles) > 0.5:
            score *= 0.7
        
        # Check for known patterns
        if self._has_valid_patterns(word_explanations):
            score *= 1.1
        else:
            score *= 0.9
        
        return min(max(score, 0.0), 1.0)
    
    def _has_valid_patterns(self, word_explanations: List[List[str]]) -> bool:
        """Check if result has valid Hindi grammar patterns."""
        # Simplified: check for subject-verb-object, postpositions, etc.
        roles = [item[1] for item in word_explanations if len(item) > 1]
        
        # Must have at least one noun and one verb
        has_noun = any(role in ['noun', 'pronoun'] for role in roles)
        has_verb = 'verb' in roles
        
        return has_noun and has_verb