# languages/hindi/domain/hi_response_parser.py
import json
import logging
from typing import List, Dict, Any
from .hi_config import HiConfig
from .hi_fallbacks import HiFallbacks

logger = logging.getLogger(__name__)

class HiResponseParser:
    """Parses AI responses, cleans data, and applies fallbacks."""
    
    def __init__(self, config: HiConfig):
        self.config = config
        self.fallbacks = HiFallbacks(config)
    
    def parse_response(self, ai_response: str, complexity: str, sentence: str, target_word: str = None) -> Dict[str, Any]:
        """Parse single response with fallbacks."""
        logger.info(f"DEBUG: Raw AI response for sentence '{sentence}': {ai_response[:500]}")
        try:
            json_data = self._extract_json(ai_response)
            
            # Check if this looks like an error response
            if isinstance(json_data, dict) and json_data.get('sentence') == 'error':
                raise ValueError("AI returned error response")
            
            return self._transform_to_standard_format(json_data, complexity, target_word)
        except Exception as e:
            logger.warning(f"Parsing failed for sentence '{sentence}': {e}")
            return self.fallbacks.create_fallback(sentence, complexity)
    
    def parse_batch_response(self, ai_response: str, sentences: List[str], complexity: str, target_word: str = None) -> List[Dict[str, Any]]:
        """Parse batch response with per-result fallbacks."""
        logger.info(f"DEBUG: Raw AI batch response: {ai_response[:1000]}")
        try:
            json_data = self._extract_json(ai_response)
            
            # Check if this looks like an error response
            if isinstance(json_data, dict) and json_data.get('sentence') == 'error':
                raise ValueError("AI returned error response")
            
            if isinstance(json_data, list):
                batch_results = json_data
            else:
                batch_results = json_data.get('batch_results', [])
            
            # If no valid batch results, treat as error
            if not batch_results:
                raise ValueError("No valid batch results in AI response")
                
            results = []
            for i, item in enumerate(batch_results):
                if i < len(sentences):
                    try:
                        parsed = self._transform_to_standard_format(item, complexity, target_word)
                        results.append(parsed)
                    except Exception as e:
                        logger.warning(f"Batch item {i} failed: {e}")
                        results.append(self.fallbacks.create_fallback(sentences[i], complexity))
                else:
                    results.append(self.fallbacks.create_fallback(sentences[i], complexity))
            
            # If we don't have results for all sentences, add fallbacks
            while len(results) < len(sentences):
                results.append(self.fallbacks.create_fallback(sentences[len(results)], complexity))
                
            return results
        except Exception as e:
            logger.error(f"Batch parsing failed: {e}")
            return [self.fallbacks.create_fallback(s, complexity) for s in sentences]
    
    def _extract_json(self, response: str) -> Dict[str, Any]:
        """Extract JSON from AI response."""
        logger.info(f"DEBUG: Extracting JSON from response: {response[:1000]}...")
        try:
            # Strip markdown if present
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            logger.info(f"DEBUG: Cleaned response: {response[:1000]}...")
            result = json.loads(response)
            logger.info(f"DEBUG: Parsed JSON: {result}")
            return result
        except Exception as e:
            logger.error(f"DEBUG: Failed to extract JSON from response: {e}")
            logger.error(f"DEBUG: Response that failed: {response}")
            raise
    
    def _transform_to_standard_format(self, data: Dict[str, Any], complexity: str, target_word: str = None) -> Dict[str, Any]:
        """Transform parsed data to standard format."""
        # Simplified: apply role mapping, etc. from config
        words = data.get('words', [])
        elements = {}
        word_explanations = []
        colors = self._get_color_scheme(complexity)
        
        for word_data in words:
            word = word_data.get('word', '')
            role = word_data.get('grammatical_role', 'other')
            if target_word and word == target_word:
                role = 'target_word'
            # Map role using config
            standard_role = self.config.grammatical_roles.get(role, role)
            color = colors.get(standard_role, '#AAAAAA')
            explanation = word_data.get('individual_meaning', standard_role)
            word_explanations.append([word, standard_role, color, explanation])
            
            if standard_role not in elements:
                elements[standard_role] = []
            elements[standard_role].append(word_data)
        
        return {
            'sentence': data.get('sentence', ''),
            'elements': elements,
            'explanations': data.get('explanations', {}),
            'word_explanations': word_explanations
        }
    
    def _get_color_scheme(self, complexity: str) -> Dict[str, str]:
        """Get color scheme based on complexity."""
        return self.config.get_color_scheme(complexity)