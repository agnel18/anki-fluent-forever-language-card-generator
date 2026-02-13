---

## Additional Learnings from French Analyzer Implementation

### JSON Parsing Robustness Best Practices

Based on the French analyzer implementation, here are critical learnings for robust JSON parsing in AI responses:

#### 1. **Token Limits Matter**
- **Finding:** 2000 tokens caused response truncation leading to malformed JSON
- **Solution:** Use 4000 tokens minimum for complex linguistic analysis
- **Impact:** Prevents JSON parsing failures and fallback to basic analysis

#### 2. **Regex-Based JSON Cleaning**
```python
def _clean_json_response(self, response: str) -> str:
    """Clean malformed JSON from AI responses using regex patterns"""
    # Fix missing commas between key-value pairs
    response = re.sub(r'"\s*\n\s*"', '",\n"', response)
    response = re.sub(r'"\s+"', '", "', response)
    
    # Fix trailing commas before closing braces/brackets
    response = re.sub(r',(\s*[}\]])', r'\1', response)
    
    # Fix unquoted keys (common AI mistake)
    response = re.sub(r'(\w+):', r'"\1":', response)
    
    return response
```

#### 3. **Multi-Level Fallback Strategy**
1. **Primary:** Direct JSON parsing
2. **Secondary:** Extract from markdown code blocks
3. **Tertiary:** Regex extraction between braces
4. **Final:** Fallback to basic analysis with error logging

#### 4. **Prompt Simplification**
- **Complex batch prompts** increase parsing failure risk
- **Simple, focused prompts** improve JSON structure reliability
- **Clear JSON schema** in prompts reduces AI hallucinations

#### 5. **Error Recovery Patterns**
```python
try:
    # Primary parsing attempt
    result = self._parse_json_response(ai_response)
except Exception as e:
    logger.warning(f"Primary parsing failed: {e}")
    try:
        # Secondary cleaning and parsing
        cleaned = self._clean_json_response(ai_response)
        result = self._parse_json_response(cleaned)
    except Exception as e2:
        logger.error(f"Secondary parsing failed: {e2}")
        # Final fallback
        result = self._create_fallback_analysis(sentence, target_word, complexity)
```

#### 6. **Testing for Edge Cases**
- Test with truncated responses (simulate 2000 token limit)
- Test with explanatory text mixed with JSON
- Test with malformed JSON structures
- Validate fallback analysis quality

#### 7. **Monitoring and Alerts**
- Track JSON parsing success rates
- Alert when fallback analysis usage exceeds 5%
- Log parsing failures for pattern analysis
- Monitor token usage vs. parsing success correlation