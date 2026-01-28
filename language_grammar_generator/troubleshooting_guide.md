# Troubleshooting Guide
## Solutions for Common Language Analyzer Issues

**Gold Standards:** [Hindi](languages/hindi/hi_analyzer.py) and [Chinese Simplified](languages/zh/zh_analyzer.py)  
**Critical:** Compare with gold standards - no artificial confidence boosting  
**Prerequisites:** Study gold standards before troubleshooting  
**Purpose:** Systematic debugging following proven patterns  
**Time Estimate:** Varies by issue complexity

## 📚 LESSONS LEARNED FROM RECENT FIXES

### Critical Issues Fixed in Chinese Traditional Analyzer

#### Issue 1: Syntax Errors Preventing Analyzer Loading
**Symptoms:**
- "Failed to load analyzer zh-tw: f-string: unterminated string"
- Analyzer not discovered despite being implemented
- Generic fallback analysis used instead

**Root Cause:**
- Nested f-string syntax: `f'{count} {role}{"s" if count > 1 else ""}'`
- Python doesn't support nested f-strings

**Solution:**
```python
# ❌ BROKEN - Nested f-strings
f"Sentence with {', '.join([f'{count} {role}{"s" if count > 1 else ""}' for role, count in role_counts.items()])}"

# ✅ FIXED - String concatenation
f"Sentence with {', '.join([f'{count} {role}' + ('s' if count > 1 else '') for role, count in role_counts.items()])}"
```

#### Issue 2: Missing Method Implementations
**Symptoms:**
- Analyzer class exists but methods not called
- `get_grammar_prompt` and `parse_grammar_response` undefined
- Falls back to generic analysis

**Root Cause:**
- Incomplete implementation compared to gold standards
- Methods exist in base class but not overridden properly

**Solution:**
```python
# ✅ FIXED - Direct component usage
def analyze_grammar(self, sentence, target_word, complexity, api_key):
    prompt = self.prompt_builder.build_single_sentence_prompt(sentence, target_word, complexity)
    ai_response = self._call_ai_model(prompt, api_key)
    parsed_data = self.response_parser.parse_response(ai_response, sentence, complexity)
    # ... rest of implementation
```

#### Issue 3: AI Providing Repeated Meanings
**Symptoms:**
- All words of same grammatical role have identical meanings
- "我 (pronoun): 我: I; me; 你: you; 這: this" for every pronoun
- Generic role-based explanations instead of word-specific

**Root Cause:**
- AI prompt not emphasizing uniqueness
- Missing "MANDATORY: Provide UNIQUE meanings" instruction

**Solution:**
```python
# ✅ ENHANCED PROMPT
"CRITICAL: Provide UNIQUE, INDIVIDUAL meanings for EACH word. Do NOT repeat meanings across words."
"individual_meaning: UNIQUE {native_language} translation/meaning SPECIFIC to this exact word only (MANDATORY)"

# Example in prompt:
{"word": "我", "individual_meaning": "I, me (first person singular pronoun)"},
{"word": "你", "individual_meaning": "you (second person singular pronoun)"}
```

#### Issue 4: Generic Grammar Summaries
**Symptoms:**
- Summary always shows "Grammar analysis for ZH-TW"
- AI not providing `overall_structure` and `key_features`
- No fallback summary generation

**Root Cause:**
- Missing `explanations` field in AI response
- No automatic summary generation from word data

**Solution:**
```python
# ✅ FALLBACK SUMMARY GENERATION
def _transform_to_standard_format(self, data, complexity, target_word=None):
    # ... existing code ...
    
    # Generate overall_structure and key_features if missing
    if not explanations.get('overall_structure'):
        roles = [exp[1] for exp in word_explanations if len(exp) > 1]
        role_counts = {}
        for role in roles:
            role_counts[role] = role_counts.get(role, 0) + 1
        overall = f"Sentence with {', '.join([f'{count} {role}' + ('s' if count > 1 else '') for role, count in role_counts.items()])}"
        explanations['overall_structure'] = overall
        explanations['key_features'] = f"Demonstrates {len(set(roles))} grammatical categories"
```

#### Issue 5: TTS Voice Incompatibility
**Symptoms:**
- "Found 0 voices for language zh-TW"
- "Found 38 voices for language cmn-CN"
- Chinese Traditional cannot use TTS

**Root Cause:**
- Google TTS doesn't support "zh-TW" language code
- Only supports "cmn-CN" for Mandarin Chinese

**Solution:**
```python
# ✅ LANGUAGE CODE MAPPING
tts_language_map = {
    "zh-TW": "cmn-CN",  # Chinese Traditional uses same voices as Simplified
    "zh-tw": "cmn-CN",
}
if language_code and language_code in tts_language_map:
    language_code = tts_language_map[language_code]
```

### Key Takeaways from Fixes

1. **Syntax Validation:** Always test f-string syntax - avoid nested f-strings
2. **Complete Implementation:** Ensure all methods are properly implemented vs gold standards
3. **AI Prompt Engineering:** Use explicit instructions for uniqueness and specificity
4. **Robust Fallbacks:** Always provide meaningful fallbacks when AI fails
5. **Language Code Mapping:** Map incompatible codes to supported equivalents
6. **Component Architecture:** Use modular components directly, not through undefined base methods

## 🔍 Systematic Debugging Approach - Gold Standard Method

## 🔍 Systematic Debugging Approach - Gold Standard Method

### 1. Issue Classification Framework - Compare with Gold Standards
```
ISSUE TYPE → COMPARE WITH GOLD STANDARDS → SOLUTION STRATEGY

1. Analysis Quality Issues
   ↓
   Compare with Hindi/Chinese Simplified → Match gold standard patterns → Fix deviations

2. Performance Problems
   ↓
   Benchmark against gold standards → Identify bottlenecks → Apply gold standard optimizations

3. System Reliability Issues
   ↓
   Check gold standard error handling → Implement matching patterns → Test thoroughly

4. Deployment & Infrastructure Issues
   ↓
   Verify gold standard deployment → Match configuration → Deploy consistently
```

### 2. Diagnostic Checklist - Gold Standard Verification
- [ ] **Gold Standard Comparison:** Does implementation match Hindi/Chinese Simplified patterns?
- [ ] **Natural Validation:** No artificial confidence boosting (removed from all implementations)
- [ ] **Facade Pattern:** Clean component orchestration like gold standards?
- [ ] **External Config:** Loading from files like gold standards?
- [ ] **AI Integration:** Using allowed models (gemini-2.5-flash, gemini-3-flash-preview only)
- [ ] **Component Isolation:** Each component has single responsibility like gold standards?

## 🧪 Analysis Quality Issues - Compare with Gold Standards

### Issue 1: Inconsistent Quality vs Gold Standards

**Symptoms:**
- Results differ from Hindi/Chinese Simplified analyzers
- Artificial confidence boosting detected (should be removed)
- Complex patterns not matching simpler gold standard approaches

**Diagnostic Steps - Compare with Gold Standards:**
```python
# Compare with gold standard validation (NO artificial boosting)
def compare_with_gold_standard(result, gold_standard_result):
    """Check if your implementation matches gold standard patterns"""
    checks = {
        "natural_confidence": 0 <= result["confidence"] <= 1,  # No artificial boost
        "matches_gold_structure": result.keys() == gold_standard_result.keys(),
        "no_artificial_boosting": not has_artificial_boosting(result),  # Critical check
        "facade_pattern": uses_facade_pattern(),  # Like gold standards
    }
    return checks
```

**Root Causes & Solutions:**

#### ❌ Artificial Confidence Boosting (REMOVED from all implementations)
```python
# WRONG - This pattern was removed from Chinese Traditional
def bad_validate_result(self, result, sentence):
    confidence = result.get("confidence", 0.5)
    if some_condition:
        confidence = min(confidence * 1.5, 1.0)  # ARTIFICIAL BOOST - BAD
    return confidence

# CORRECT - Natural scoring like gold standards
def good_validate_result(self, result, sentence):
    checks = self._perform_quality_checks(result, sentence)
    return self._calculate_natural_confidence(checks)  # NATURAL - GOOD
```

**Solution Steps:**
1. **Study Gold Standards:** Read Hindi and Chinese Simplified analyzers thoroughly
2. **Remove Artificial Boosting:** Ensure NO confidence manipulation beyond natural scoring
3. **Match Facade Pattern:** Implement component orchestration like gold standards
4. **Test Against Gold Standards:** Verify results match proven implementations

### Issue 2: Component Coupling Issues

**Symptoms:**
- Components depend on concrete implementations
- Hard to test components in isolation
- Changes break multiple parts of system

**Diagnostic Steps:**
```python
# Check for tight coupling (compare with gold standards)
def check_component_isolation(analyzer):
    """Verify components are loosely coupled like gold standards"""
    checks = {
        "config_injection": hasattr(analyzer, 'config') and analyzer.config is not None,
        "builder_injection": hasattr(analyzer, 'prompt_builder'),
        "parser_injection": hasattr(analyzer, 'response_parser'),
        "validator_injection": hasattr(analyzer, 'validator'),
        "no_concrete_dependencies": not uses_concrete_classes(analyzer),  # Like gold standards
    }
    return checks
```

**Solution - Match Gold Standard Injection:**
```python
# CORRECT - Like gold standards
class LanguageAnalyzer:
    def __init__(self, config=None, prompt_builder=None, parser=None, validator=None):
        self.config = config or LanguageConfig()  # Injectable
        self.prompt_builder = prompt_builder or PromptBuilder(self.config)
        self.response_parser = parser or ResponseParser(self.config)
        self.validator = validator or Validator(self.config)

# WRONG - Tight coupling
class LanguageAnalyzer:
    def __init__(self):
        self.config = LanguageConfig()  # Can't replace for testing
        self.prompt_builder = PromptBuilder(self.config)  # Hard-coded
```

### Issue 3: Configuration Loading Problems

**Symptoms:**
- Language-specific settings not loading
- Hard-coded values in code
- Runtime configuration errors

**Diagnostic Steps:**
```python
# Check configuration loading (like gold standards)
def verify_config_loading(language_code):
    """Verify config loads from external files like gold standards"""
    try:
        config = load_language_config(language_code)  # Like hi_config/zh_config
        checks = {
            "external_loading": config.loaded_from_file,
            "language_specific": config.language_code == language_code,
            "no_hardcoded_values": not has_hardcoded_values(config),
            "yaml_structure": validates_yaml_structure(config),
        }
        return checks
    except Exception as e:
        return {"error": str(e)}
```

**Solution - Match Gold Standard Config:**
```python
# CORRECT - Like gold standards
class LanguageConfig:
    def __init__(self):
        # Load from external files (like Hindi/Chinese)
        self.grammatical_roles = self._load_yaml("grammatical_roles.yaml")
        self.color_schemes = self._load_yaml("color_schemes.yaml")
        self.prompt_templates = self._load_yaml("prompt_templates.yaml")

# WRONG - Hard-coded config
class LanguageConfig:
    def __init__(self):
        self.grammatical_roles = {"noun": "noun", "verb": "verb"}  # Hard-coded - BAD
        self.colors = {"noun": "#FF0000"}  # Hard-coded - BAD
```

### Issue 4: AI Integration Issues

**Symptoms:**
- Wrong AI model being used
- API rate limiting errors
- Inconsistent response formats

**Diagnostic Steps:**
```python
# Check AI integration (strict model restrictions like gold standards)
def verify_ai_integration():
    """Verify AI setup matches gold standards"""
    checks = {
        "allowed_models_only": uses_only_allowed_models(),  # gemini-2.5-flash, gemini-3-flash-preview
        "circuit_breaker": has_circuit_breaker(),
        "error_handling": has_comprehensive_error_handling(),
        "response_validation": validates_ai_responses(),
    }
    return checks

ALLOWED_MODELS = ["gemini-2.5-flash", "gemini-3-flash-preview"]  # STRICT
```

**Solution - Match Gold Standard AI Integration:**
```python
# CORRECT - Like gold standards
class AIService:
    ALLOWED_MODELS = ["gemini-2.5-flash", "gemini-3-flash-preview"]  # STRICT

    def call_ai(self, prompt, api_key, model="gemini-2.5-flash"):
        if model not in self.ALLOWED_MODELS:
            raise ValueError(f"Model {model} not allowed. Use: {self.ALLOWED_MODELS}")
        # Circuit breaker, retry logic, etc.
```

### Issue 4.5: Basic Explanations Instead of Rich Explanations (Chinese Gold Standard Issue)

**Symptoms:**
- Analyzer only shows grammatical roles: "noun in zh-tw grammar", "verb in zh-tw grammar"
- Missing individual word meanings and detailed explanations
- HTML output lacks rich contextual information
- Users see generic labels instead of specific meanings

**Root Cause:**
- Missing `analyze_grammar` method with rich explanation workflow
- Missing `_generate_html_output` method for detailed HTML generation
- Using base analyzer methods instead of gold standard patterns
- Not extracting `individual_meaning` from AI responses

**Diagnostic Steps:**
```python
def diagnose_rich_explanations():
    """Check if analyzer provides rich explanations like Chinese gold standards"""
    checks = {
        "has_analyze_grammar": hasattr(analyzer, 'analyze_grammar'),
        "has_generate_html": hasattr(analyzer, '_generate_html_output'),
        "returns_grammar_analysis": 'GrammarAnalysis' in str(type(result)),
        "has_word_explanations": len(result.word_explanations) > 0,
        "explanations_have_meaning": all(len(exp) >= 4 for exp in result.word_explanations),  # [word, role, color, meaning]
        "html_has_colors": '<span style="color:' in result.html_output,
    }
    return checks
```

**Solution - Implement Rich Explanation Pattern (Chinese Gold Standard):**
```python
# CORRECT - Like Chinese Simplified/Traditional gold standards
class LanguageAnalyzer(BaseGrammarAnalyzer):
    def analyze_grammar(self, sentence: str, target_word: str, complexity: str, api_key: str) -> GrammarAnalysis:
        """Rich explanation workflow - extract individual meanings"""
        # 1. Build prompt
        prompt = self.prompt_builder.build_single_prompt(sentence, target_word, complexity)

        # 2. Call AI for detailed analysis
        ai_response = self._call_ai_model(prompt, api_key)

        # 3. Parse individual meanings from response
        parsed = self.response_parser.parse_response(ai_response, sentence, complexity)

        # 4. Generate HTML with colored explanations
        html = self._generate_html_output(parsed, sentence, complexity)

        return GrammarAnalysis(
            sentence=sentence,
            word_explanations=parsed.get('word_explanations', []),
            html_output=html,
            explanations=parsed.get('explanations', {})
        )

    def _generate_html_output(self, parsed_data: Dict[str, Any], sentence: str, complexity: str) -> str:
        """Position-based coloring with individual meanings"""
        explanations = parsed_data.get('word_explanations', [])
        color_scheme = self.get_color_scheme(complexity)

        html_parts = []
        i = 0
        while i < len(sentence):
            matched = False
            for exp in sorted(explanations, key=lambda x: len(x[0]), reverse=True):
                if len(exp) >= 4:  # [word, role, color, meaning]
                    word, role, color, meaning = exp[0], exp[1], exp[2], exp[3]
                    word_len = len(word)

                    if i + word_len <= len(sentence) and sentence[i:i + word_len] == word:
                        # Apply color and preserve meaning for Anki compatibility
                        safe_word = word.replace('{', '{{').replace('}', '}}')
                        colored_word = f'<span style="color: {color}; font-weight: bold;">{safe_word}</span>'
                        html_parts.append(colored_word)
                        i += word_len
                        matched = True
                        break

            if not matched:
                html_parts.append(sentence[i])
                i += 1

        return ''.join(html_parts)
```

**Before vs After:**
```python
# ❌ BEFORE - Basic grammatical roles only
"noun in zh-tw grammar"
"verb in zh-tw grammar"

# ✅ AFTER - Rich explanations with meanings
"我 (I, me - first person singular pronoun)"
"喜歡 (to like, to be fond of - verb expressing preference)"
"吃 (to eat, to consume - verb of consumption)"
```

## ⚡ Performance Issues - Benchmark Against Gold Standards

### Issue 5: Slow Response Times

**Symptoms:**
- Analysis takes > 3 seconds
- Batch processing is slow
- Memory usage is high

**Diagnostic Steps:**
```python
# Benchmark against gold standards
def performance_comparison():
    """Compare performance with gold standards"""
    gold_standard_time = benchmark_gold_standard()  # Hindi/Chinese baseline
    your_time = benchmark_your_implementation()

    return {
        "gold_standard_baseline": gold_standard_time,
        "your_performance": your_time,
        "acceptable_ratio": your_time / gold_standard_time < 1.5,  # Within 50%
    }
```

**Solution - Apply Gold Standard Optimizations:**
```python
# CORRECT - Like gold standards
class PromptBuilder:
    def __init__(self, config):
        self.cache = {}  # Cache prompts like gold standards

    def build_single_prompt(self, sentence, target_word, complexity):
        cache_key = (sentence, target_word, complexity)
        if cache_key in self.cache:
            return self.cache[cache_key]  # Cache hit

        prompt = self._build_prompt(sentence, target_word, complexity)
        self.cache[cache_key] = prompt  # Cache for future use
        return prompt
```

## 🔧 System Reliability Issues - Match Gold Standard Error Handling

### Issue 6: Frequent Failures

**Symptoms:**
- High error rates
- Inconsistent results
- Poor error recovery

**Diagnostic Steps:**
```python
# Check error handling completeness
def error_handling_audit():
    """Audit error handling against gold standards"""
    checks = {
        "comprehensive_catch": catches_all_exceptions(),
        "fallback_mechanisms": has_fallbacks_like_gold_standards(),
        "graceful_degradation": degrades_gracefully(),
        "error_logging": logs_errors_properly(),
    }
    return checks
```

**Solution - Implement Gold Standard Error Handling:**
```python
# CORRECT - Like gold standards
class LanguageAnalyzer:
    def analyze_grammar(self, sentence, target_word, complexity, api_key):
        try:
            # Normal flow
            prompt = self.prompt_builder.build_single_prompt(...)
            response = self._call_ai(prompt, api_key)
            result = self.response_parser.parse_response(response, ...)
            validated = self.validator.validate_result(result, sentence)
            return self._generate_html_output(validated, ...)

        except AIError as e:
            # Fallback like gold standards
            return self._create_fallback_analysis(sentence, complexity)

        except ValidationError as e:
            # Recovery like gold standards
            return self._attempt_recovery(result, sentence)

        except Exception as e:
            # Last resort like gold standards
            logger.error(f"Unexpected error: {e}")
            return self._create_error_response(e, sentence)
```

## 🚀 Deployment Issues - Match Gold Standard Deployment

### Issue 7: Deployment Failures

**Symptoms:**
- Import errors in production
- Missing dependencies
- Configuration issues

**Diagnostic Steps:**
```python
# Deployment verification
def deployment_check():
    """Verify deployment matches gold standards"""
    checks = {
        "dependencies": all_dependencies_installed(),
        "imports": all_imports_work(),
        "config_files": config_files_exist_like_gold_standards(),
        "environment": environment_matches_gold_standards(),
    }
    return checks
```

**Solution - Match Gold Standard Deployment:**
```python
# requirements.txt - Like gold standards
google-generativeai==0.5.0
pyyaml==6.0.1
jinja2==3.1.3
pytest==7.4.3

# Directory structure - Like gold standards
languages/
├── hindi/
│   ├── hi_analyzer.py
│   ├── hi_config.py
│   └── ...
└── zh/
    ├── zh_analyzer.py
    ├── zh_config.py
    └── ...
```

## 🧪 Testing Issues - Follow Gold Standard Testing

### Issue 8: Test Failures

**Symptoms:**
- Tests don't match gold standard patterns
- Confidence boosting tests still present (should be removed)
- Component coupling prevents testing

**Diagnostic Steps:**
```python
# Test quality audit
def test_quality_check():
    """Verify tests follow gold standard patterns"""
    checks = {
        "no_boosting_tests": not has_confidence_boosting_tests(),  # Critical
        "component_isolation": tests_components_in_isolation(),
        "gold_standard_comparison": compares_with_gold_standards(),
        "natural_validation": tests_natural_validation_only(),
    }
    return checks
```

**Solution - Gold Standard Testing:**
```python
# CORRECT - Like gold standards
class TestLanguageAnalyzer:
    def test_natural_validation(self):
        """Test natural validation - NO artificial boosting"""
        validator = Validator(config)
        result = validator.validate_result(test_data, sentence)
        assert 0 <= result["final_confidence"] <= 1  # NATURAL range
        # NO tests for artificial confidence boosting

    def test_facade_orchestration(self):
        """Test component orchestration like gold standards"""
        analyzer = LanguageAnalyzer()
        result = analyzer.analyze_grammar(sentence, word, complexity, api_key)
        assert result["sentence"] == sentence
        assert "analysis" in result
```

## 📊 Monitoring & Metrics - Gold Standard Observability

### Issue 9: Lack of Visibility

**Symptoms:**
- Can't debug production issues
- No performance metrics
- Error tracking is poor

**Solution - Implement Gold Standard Monitoring:**
```python
# CORRECT - Like gold standards
def analyze_grammar(self, sentence, target_word, complexity, api_key):
    start_time = time.time()

    try:
        # Analysis logic
        result = self._perform_analysis(...)

        # Structured logging like gold standards
        logger.info("Analysis completed", extra={
            "language": self.config.language_code,
            "sentence_length": len(sentence),
            "confidence": result["confidence"],  # NATURAL confidence
            "processing_time": time.time() - start_time,
            "success": True
        })

        return result

    except Exception as e:
        logger.error("Analysis failed", extra={
            "language": self.config.language_code,
            "error_type": type(e).__name__,
            "sentence_length": len(sentence),
            "processing_time": time.time() - start_time,
            "success": False
        })
        raise
```

## 🎯 Quick Reference - Gold Standard Checklist

### Pre-Troubleshooting Checklist
- [ ] Studied [Hindi analyzer](languages/hindi/hi_analyzer.py) thoroughly?
- [ ] Studied [Chinese Simplified analyzer](languages/zh/zh_analyzer.py) thoroughly?
- [ ] Removed all artificial confidence boosting?
- [ ] Implemented facade pattern like gold standards?
- [ ] Using allowed AI models only?
- [ ] Loading config from external files?

### Issue Resolution Priority
1. **Compare with Gold Standards** - Does it match Hindi/Chinese Simplified?
2. **Remove Artificial Boosting** - Any confidence manipulation detected?
3. **Check Component Isolation** - Are components loosely coupled?
4. **Verify AI Integration** - Using correct models and error handling?
5. **Test Against Gold Standards** - Results match proven implementations?

### Emergency Fixes
```python
# If analysis is broken - compare with gold standard
def emergency_fix():
    """Copy working pattern from gold standards"""
    # 1. Copy facade pattern from Hindi analyzer
    # 2. Copy natural validation from Chinese Simplified
    # 3. Remove any artificial boosting
    # 4. Test against gold standards
    pass
```

---

**Remember:** When in doubt, compare with the gold standards ([Hindi](languages/hindi/hi_analyzer.py) and [Chinese Simplified](languages/zh/zh_analyzer.py)). They represent the proven working patterns - no artificial confidence boosting, clean facade orchestration, natural validation scoring.
```python
# Check confidence scoring
def diagnose_confidence_issues(sentence, complexity):
    analyzer = {Language}Analyzer()

    # Run multiple analyses
    results = []
    for i in range(5):
        result = analyzer.analyze_grammar(sentence, "", complexity, "api_key")
        results.append(result.confidence_score)

    avg_confidence = sum(results) / len(results)
    confidence_variance = statistics.variance(results)

    print(f"Average confidence: {avg_confidence:.2f}")
    print(f"Confidence variance: {confidence_variance:.4f}")

    # Check for consistency
    if confidence_variance > 0.1:
        print("WARNING: High variance in confidence scores")
        return "inconsistent_analysis"

    if avg_confidence < 0.7:
        return "low_confidence"
    else:
        return "acceptable_confidence"
```

**Root Causes & Solutions:**

#### Cause 1.1: Incorrect Model Selection
```python
# Check model selection logic
def verify_model_selection():
    from infrastructure.{language}_model_router import {Language}ModelRouter

    router = {Language}ModelRouter()

    test_cases = [
        ("Simple sentence.", "beginner"),
        ("Complex sentence with advanced grammar.", "advanced"),
        ("Medium complexity sentence.", "intermediate")
    ]

    for sentence, complexity in test_cases:
        model = router.select_model(sentence, complexity)
        print(f"'{sentence}' ({complexity}) → {model}")

        # Verify model appropriateness
        if complexity == "advanced" and "gemini-2.5-flash" not in model:
            print("ERROR: Advanced complexity should use gemini-2.5-flash")
        elif complexity == "beginner" and "gemini-3-flash-preview" not in model:
            print("WARNING: Beginner complexity could use faster model")
```

**Solution 1.1.1: Fix Model Selection Logic**
```python
# Update model router
def fix_model_selection():
    router = {Language}ModelRouter()

    # Adjust selection criteria
    if complexity == 'advanced':
        return GeminiModel.GEMINI_2_5_FLASH.value
    elif len(sentence) > 150:  # Longer sentences need more capable model
        return GeminiModel.GEMINI_2_5_FLASH.value
    else:
        return GeminiModel.GEMINI_3_FLASH_PREVIEW.value
```

#### Cause 1.2: Poor Prompt Engineering
```python
# Analyze prompt effectiveness
def analyze_prompt_quality():
    prompt_builder = {Language}PromptBuilder()

    test_prompts = [
        ("The cat sits.", "beginner"),
        ("The cat that chased the mouse ran away.", "intermediate"),
        ("Notwithstanding the committee's recommendations, the board proceeded.", "advanced")
    ]

    for sentence, complexity in test_prompts:
        prompt = prompt_builder.build_single_prompt(sentence, "", complexity)

        # Check prompt characteristics
        print(f"Complexity: {complexity}")
        print(f"Prompt length: {len(prompt)} characters")
        print(f"Contains language name: {'{language_name}' in prompt}")
        print(f"Contains grammatical roles: {'grammatical_roles' in prompt}")
        print(f"Contains complexity: {complexity in prompt}")
        print("-" * 50)
```

**Solution 1.2.1: Optimize Prompts**
```python
# Enhanced prompt template
def create_optimized_prompt_template():
    return """
You are a linguistics expert specializing in {language_name} grammar analysis.

TASK: Analyze this {language_name} sentence with {complexity} complexity:
"{sentence}"{target_word_instruction}

GRAMMATICAL FRAMEWORK ({complexity} level):
{grammatical_roles}

REQUIREMENTS:
1. Identify EVERY word's grammatical role using ONLY the provided categories
2. Provide clear, accurate explanations in English
3. Maintain word order and sentence structure
4. Be linguistically precise and comprehensive

OUTPUT FORMAT:
{{
  "words": [
    {{
      "word": "exact_word_from_sentence",
      "grammatical_role": "exact_category_from_list",
      "meaning": "detailed_grammatical_explanation"
    }}
  ],
  "explanations": {{
    "overall_structure": "comprehensive_sentence_analysis",
    "key_features": "important_grammatical_concepts_demonstrated"
  }}
}}

Analyze now with expert precision:"""
```

#### Cause 1.3: Language-Specific Issues
```python
# Check language configuration
def verify_language_config():
    config = {Language}Config()

    # Verify grammatical roles mapping
    roles = config.grammatical_roles
    print(f"Defined roles: {len(roles)}")

    # Check for language-specific roles
    language_specific = ['aspect_marker', 'classifier', 'particle']  # Adjust for language
    missing_roles = [role for role in language_specific if role not in roles]
    if missing_roles:
        print(f"WARNING: Missing language-specific roles: {missing_roles}")

    # Verify color scheme
    colors = config.get_color_scheme('advanced')
    print(f"Color categories: {len(colors)}")

    # Check role coverage
    covered_roles = set()
    for complexity in ['beginner', 'intermediate', 'advanced']:
        scheme = config.get_color_scheme(complexity)
        covered_roles.update(scheme.keys())

    uncovered_roles = set(roles.values()) - covered_roles
    if uncovered_roles:
        print(f"ERROR: Uncovered roles: {uncovered_roles}")
```

**Solution 1.3.1: Update Language Configuration**
```python
# Enhanced configuration
class Enhanced{Language}Config({Language}Config):
    def __init__(self):
        super().__init__()

        # Add missing language-specific roles
        self.grammatical_roles.update({
            'aspect_marker': 'aspect_marker',
            'classifier': 'classifier',
            'structural_particle': 'structural_particle',
            'discourse_particle': 'discourse_particle'
        })

        # Update color schemes
        self._update_color_schemes()

    def _update_color_schemes(self):
        """Update color schemes with better coverage"""
        advanced_colors = self.get_color_scheme('advanced')
        advanced_colors.update({
            'aspect_marker': '#9370DB',
            'classifier': '#FF8C00',
            'structural_particle': '#98FB98',
            'discourse_particle': '#F0E68C'
        })
```

### Issue 2: Incorrect Grammatical Roles

**Symptoms:**
- Words assigned wrong grammatical categories
- Consistent errors for specific word types
- Language-specific features misidentified

**Diagnostic Steps:**
```python
# Analyze role assignment patterns
def analyze_role_errors():
    analyzer = {Language}Analyzer()

    test_sentences = [
        "The big cat sleeps peacefully.",
        "She reads interesting books.",
        "They play games every day."
    ]

    role_errors = {}

    for sentence in test_sentences:
        result = analyzer.analyze_grammar(sentence, "", "beginner", "api_key")

        for word_info in result.word_explanations:
            word, role, color, meaning = word_info

            # Check for common errors
            if word.lower() in ['the', 'a', 'an'] and role != 'determiner':
                role_errors[f"{word}_determiner"] = role_errors.get(f"{word}_determiner", 0) + 1
            elif word.lower() in ['big', 'interesting', 'peacefully'] and role not in ['adjective', 'adverb']:
                role_errors[f"{word}_modifier"] = role_errors.get(f"{word}_modifier", 0) + 1

    print("Role assignment errors:")
    for error_type, count in role_errors.items():
        print(f"  {error_type}: {count} occurrences")
```

**Root Causes & Solutions:**

#### Cause 2.1: Prompt Ambiguity
**Solution:** Make prompts more specific about role definitions
```python
# Enhanced prompt with explicit definitions
def create_explicit_role_prompt():
    return """
GRAMMATICAL ROLES (with definitions):

Nouns: Words that name people, places, things, or ideas
- Common nouns: general names (cat, book, city)
- Proper nouns: specific names (London, Microsoft)

Verbs: Words that express actions or states
- Action verbs: physical/mental actions (run, think, eat)
- State verbs: conditions or states (be, seem, have)

Adjectives: Words that describe or modify nouns
- Size: big, small, large
- Color: red, blue, green
- Quality: interesting, beautiful, difficult

Adverbs: Words that modify verbs, adjectives, or other adverbs
- Manner: quickly, slowly, carefully
- Time: now, then, yesterday
- Place: here, there, everywhere

Determiners: Words that introduce nouns
- Articles: the, a, an
- Demonstratives: this, that, these, those
- Possessives: my, your, his, her

Prepositions: Words that show relationships
- Location: in, on, at, under
- Time: before, after, during
- Direction: to, from, toward

Pronouns: Words that replace nouns
- Personal: I, you, he, she, it, we, they
- Possessive: my, your, his, her, its, our, their
- Demonstrative: this, that, these, those

Conjunctions: Words that connect clauses or sentences
- Coordinating: and, but, or, so
- Subordinating: because, although, when, if

{language_specific_roles}

For each word in: "{sentence}"
Select the MOST APPROPRIATE role from the list above.
"""
```

#### Cause 2.2: Training Data Bias
**Solution:** Diversify test sentences and provide more examples
```python
# Comprehensive test suite
def create_diverse_test_suite():
    return {
        'simple_declarative': [
            "The cat sits on the mat.",
            "I eat breakfast every morning.",
            "She reads books in the library."
        ],
        'questions': [
            "Where is the cat?",
            "What are you eating?",
            "How does she read so quickly?"
        ],
        'complex_sentences': [
            "The cat that chased the mouse up the tree is now sleeping peacefully.",
            "Although it was raining heavily, they continued playing soccer.",
            "Having finished their homework, the students went to the park."
        ],
        'passive_voice': [
            "The book was read by the student.",
            "The cake has been eaten by the children.",
            "The letter will be written by tomorrow."
        ],
        'conditional': [
            "If it rains, we will stay home.",
            "She would help if she could.",
            "Unless you hurry, we will be late."
        ]
    }
```

## ⚡ Performance Issues

### Issue 3: Slow Response Times (> 5 seconds)

**Symptoms:**
- Analysis takes too long to complete
- UI becomes unresponsive
- Multiple concurrent requests cause timeouts

**Diagnostic Steps:**
```python
# Performance profiling
def profile_analysis_performance():
    analyzer = {Language}Analyzer()

    test_sentences = [
        ("Short sentence.", "beginner"),
        ("This is a medium length sentence with several words.", "intermediate"),
        ("This is a much longer and more complex sentence that contains advanced grammatical structures and vocabulary requiring deeper linguistic analysis.", "advanced")
    ]

    import time

    for sentence, complexity in test_sentences:
        print(f"Testing: {complexity} complexity")

        start_time = time.time()
        result = analyzer.analyze_grammar(sentence, "", complexity, "api_key")
        end_time = time.time()

        duration = end_time - start_time
        print(".2f")

        # Profile components
        if hasattr(analyzer, 'performance_monitor'):
            metrics = analyzer.performance_monitor.get_current_metrics()
            print(f"  AI request time: {metrics.get('average_ai_latency', 'N/A')}")
            print(f"  Parsing time: {metrics.get('average_parse_time', 'N/A')}")
```

**Root Causes & Solutions:**

#### Cause 3.1: Inefficient Model Selection
**Solution:** Implement intelligent model routing
```python
# Smart model selection
def optimize_model_selection():
    router = {Language}ModelRouter()

    def select_optimal_model(sentence, complexity):
        # Fast path for simple analysis
        if complexity == 'beginner' and len(sentence.split()) <= 10:
            return GeminiModel.GEMINI_3_FLASH_PREVIEW.value

        # Quality path for complex analysis
        if complexity == 'advanced' or len(sentence) > 100:
            return GeminiModel.GEMINI_2_5_FLASH.value

        # Balanced approach for medium complexity
        return GeminiModel.GEMINI_2_5_FLASH.value

    router.select_model = select_optimal_model
```

#### Cause 3.2: Prompt Inefficiency
**Solution:** Optimize prompt length and caching
```python
# Prompt optimization
def optimize_prompts():
    prompt_builder = {Language}PromptBuilder()

    def build_optimized_prompt(sentence, target_word, complexity):
        # Check cache first
        cache_key = prompt_builder._generate_cache_key(sentence, target_word, complexity)
        if cache_key in prompt_builder.prompt_cache:
            return prompt_builder.prompt_cache[cache_key]

        # Build minimal effective prompt
        prompt_parts = [
            f"Analyze {complexity} grammar:",
            f'Sentence: "{sentence}"',
            "Roles: noun, verb, adjective, adverb, pronoun, preposition, conjunction",
            "Return JSON with word roles and explanations."
        ]

        prompt = '\n'.join(prompt_parts)

        # Cache for future use
        prompt_builder.prompt_cache[cache_key] = prompt

        return prompt

    prompt_builder.build_single_prompt = build_optimized_prompt
```

#### Cause 3.3: Resource Constraints
**Solution:** Implement resource monitoring and scaling
```python
# Resource monitoring
def monitor_system_resources():
    import psutil
    import threading
    import time

    def resource_monitor():
        while True:
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent

            if cpu > 80:
                print(f"WARNING: High CPU usage: {cpu}%")
            if memory > 85:
                print(f"WARNING: High memory usage: {memory}%")
            if disk > 90:
                print(f"WARNING: Low disk space: {disk}%")

            time.sleep(60)  # Check every minute

    monitor_thread = threading.Thread(target=resource_monitor, daemon=True)
    monitor_thread.start()
```

### Issue 4: High Memory Usage

**Symptoms:**
- Application consumes excessive RAM
- Frequent garbage collection pauses
- Out of memory errors

**Diagnostic Steps:**
```python
# Memory profiling
def profile_memory_usage():
    import tracemalloc
    import gc

    tracemalloc.start()

    analyzer = {Language}Analyzer()

    # Take initial snapshot
    snapshot1 = tracemalloc.take_snapshot()

    # Run analysis
    result = analyzer.analyze_grammar("Test sentence for memory profiling.", "", "beginner", "api_key")

    # Take second snapshot
    snapshot2 = tracemalloc.take_snapshot()

    # Compare snapshots
    stats = snapshot2.compare_to(snapshot1, 'lineno')

    print("Memory usage by line:")
    for stat in stats[:10]:  # Top 10 memory users
        print(f"  {stat.filename}:{stat.lineno}: {stat.size_diff / 1024:.1f} KB")

    # Check cache size
    if hasattr(analyzer, 'prompt_builder'):
        cache_size = len(analyzer.prompt_builder.prompt_cache)
        print(f"Prompt cache size: {cache_size} entries")

    # Force garbage collection
    gc.collect()
    print(f"GC collected {gc.get_stats()[0].collected} objects")
```

**Root Causes & Solutions:**

#### Cause 4.1: Cache Memory Leaks
**Solution:** Implement cache size limits and cleanup
```python
# Cache management
def implement_cache_limits():
    prompt_builder = {Language}PromptBuilder()

    # Set cache size limit
    MAX_CACHE_SIZE = 1000

    def add_to_cache(key, value):
        if len(prompt_builder.prompt_cache) >= MAX_CACHE_SIZE:
            # Remove oldest entries (simple LRU)
            oldest_keys = list(prompt_builder.prompt_cache.keys())[:100]
            for old_key in oldest_keys:
                del prompt_builder.prompt_cache[old_key]

        prompt_builder.prompt_cache[key] = value

    prompt_builder._add_to_cache = add_to_cache
```

#### Cause 4.2: Large Response Objects
**Solution:** Implement response compression and streaming
```python
# Response optimization
def optimize_response_size():
    parser = {Language}ResponseParser()

    def create_compact_response(result, sentence, complexity):
        # Remove unnecessary fields for storage
        compact = {
            'word_explanations': result.get('word_explanations', []),
            'explanations': result.get('explanations', {}),
            'confidence': result.get('confidence', 0.5),
            'sentence': sentence,
            'complexity': complexity
        }

        # Compress explanations if too long
        for key, explanation in compact['explanations'].items():
            if len(explanation) > 500:
                compact['explanations'][key] = explanation[:500] + "..."

        return compact

    parser._create_standard_format = create_compact_response
```

## 🔧 System Reliability Issues

### Issue 5: Circuit Breaker Activation

**Symptoms:**
- Service becomes unavailable during high load
- Requests fail with "circuit breaker open" errors
- Recovery takes longer than expected

**Diagnostic Steps:**
```python
# Circuit breaker analysis
def analyze_circuit_breaker():
    from infrastructure.{language}_circuit_breaker import {Language}CircuitBreaker

    breaker = {Language}CircuitBreaker()

    # Check current state
    state = breaker.get_state()
    print(f"Circuit breaker state: {state}")

    # Simulate failures
    for i in range(6):  # Exceed threshold
        try:
            breaker.call(lambda: (_ for _ in ()).throw(Exception("Test failure")))
        except Exception as e:
            print(f"Call {i+1}: {e}")

    print(f"Final state: {breaker.get_state()}")

    # Test recovery
    import time
    print("Waiting for recovery timeout...")
    time.sleep(breaker.recovery_timeout + 1)

    try:
        breaker.call(lambda: "success")
        print("Recovery successful")
    except Exception as e:
        print(f"Recovery failed: {e}")
```

**Root Causes & Solutions:**

#### Cause 5.1: Overly Aggressive Thresholds
**Solution:** Tune circuit breaker parameters
```python
# Optimized circuit breaker configuration
def tune_circuit_breaker():
    # For AI service - be more tolerant of failures
    circuit_breaker = {Language}CircuitBreaker(
        failure_threshold=10,  # Allow more failures
        recovery_timeout=120,  # Longer recovery time
        expected_exception=(Exception, ConnectionError, TimeoutError)
    )

    return circuit_breaker
```

#### Cause 5.2: Slow Recovery Detection
**Solution:** Implement health checks and gradual recovery
```python
# Health check integration
def implement_health_checks():
    circuit_breaker = {Language}CircuitBreaker()

    def health_check_call():
        # Perform actual health check
        try:
            # Quick AI API test
            response = requests.get("https://generativelanguage.googleapis.com/v1/models",
                                  params={"key": "test_key"}, timeout=5)
            return response.status_code == 200
        except:
            return False

    def call_with_health_check(func, *args, **kwargs):
        if circuit_breaker.state == CircuitBreakerState.HALF_OPEN:
            # In half-open state, do health check first
            if not health_check_call():
                raise CircuitBreakerOpenException("Health check failed")

        return circuit_breaker.call(func, *args, **kwargs)

    return call_with_health_check
```

### Issue 6: Cache Ineffectiveness

**Symptoms:**
- Low cache hit rates (< 50%)
- Cache misses for similar requests
- Memory usage growing without performance benefit

**Diagnostic Steps:**
```python
# Cache analysis
def analyze_cache_effectiveness():
    cache = AdvancedCache()

    # Check cache statistics
    stats = cache.get_cache_stats()
    print(f"Cache stats: {stats}")

    # Test cache keys for similar sentences
    test_sentences = [
        "The cat sits on the mat.",
        "The cat is sitting on the mat.",
        "A cat sits on a mat.",
        "The feline sits on the rug."
    ]

    keys = []
    for sentence in test_sentences:
        key = cache.get_semantic_key(sentence, "", "beginner")
        keys.append(key)
        print(f"'{sentence}' → {key[:16]}...")

    # Check key uniqueness
    unique_keys = len(set(keys))
    print(f"Unique keys: {unique_keys}/{len(keys)}")

    if unique_keys == len(keys):
        print("WARNING: No semantic similarity detected")
```

**Root Causes & Solutions:**

#### Cause 6.1: Poor Semantic Key Generation
**Solution:** Implement better similarity detection
```python
# Enhanced semantic caching
def improve_semantic_caching():
    cache = AdvancedCache()

    def generate_semantic_key(sentence, target_word, complexity):
        # Normalize sentence
        normalized = sentence.lower().strip()

        # Remove punctuation and extra spaces
        import re
        normalized = re.sub(r'[^\w\s]', '', normalized)
        normalized = ' '.join(normalized.split())

        # Create semantic fingerprint
        words = set(normalized.split())
        word_count = len(words)

        # Include sentence structure hints
        has_question = '?' in sentence
        has_passive = any(word in words for word in ['is', 'was', 'were', 'been', 'being'])

        # Create composite key
        key_components = [
            f"words:{sorted(words)[:5]}",  # First 5 words alphabetically
            f"count:{word_count}",
            f"question:{has_question}",
            f"passive:{has_passive}",
            f"complexity:{complexity}",
            f"target:{target_word or ''}"
        ]

        key_string = '|'.join(key_components)
        return hashlib.md5(key_string.encode()).hexdigest()

    cache.get_semantic_key = generate_semantic_key
```

#### Cause 6.2: Cache Size Management
**Solution:** Implement intelligent cache eviction
```python
# Smart cache eviction
def implement_cache_eviction():
    cache = AdvancedCache()

    def smart_cache_set(key, value, ttl=None):
        # Check cache size before adding
        current_size = cache.redis.dbsize()

        if current_size > 5000:  # Max cache size
            # Remove least recently used items
            # This is a simplified implementation
            old_keys = cache.redis.keys("semantic:*")
            if len(old_keys) > 1000:
                cache.redis.delete(*old_keys[:500])

        cache.set(key, value, ttl)

    cache.smart_set = smart_cache_set
```

## 🚀 Deployment Issues

### Issue 7: Container Startup Failures

**Symptoms:**
- Containers fail to start in Kubernetes
- Health checks fail immediately
- Logs show import errors or missing dependencies

**Diagnostic Steps:**
```bash
# Container debugging
docker run --rm -it language-analyzer:latest /bin/bash

# Inside container, test basic functionality
python -c "from languages.{language}.{language}_analyzer import {Language}Analyzer; print('Import successful')"

# Check dependencies
pip list | grep -E "(streamlit|google|jinja2)"

# Test AI service initialization
python -c "
from infrastructure.{language}_ai_service import {Language}AIService
service = {Language}AIService()
print('AI service initialized')
"
```

**Root Causes & Solutions:**

#### Cause 7.1: Missing Dependencies
**Solution:** Update Dockerfile with all required packages
```dockerfile
# Enhanced Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir \
    streamlit \
    google-generativeai \
    jinja2 \
    redis \
    prometheus_client \
    psutil

# Create non-root user
RUN useradd --create-home --shell /bin/bash analyzer

# Copy application
COPY languages/{language}/ /app/languages/{language}/
COPY streamlit_app/ /app/streamlit_app/

# Set permissions
RUN chown -R analyzer:analyzer /app
USER analyzer

WORKDIR /app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "from languages.{language}.{language}_analyzer import {Language}Analyzer; print('OK')"

CMD ["streamlit", "run", "streamlit_app/app_v3.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### Cause 7.2: Configuration Issues
**Solution:** Implement configuration validation
```python
# Configuration validator
def validate_deployment_config():
    """Validate all required configuration is present"""

    required_env_vars = [
        'GEMINI_API_KEY',
        'ENVIRONMENT',
        'LOG_LEVEL'
    ]

    missing_vars = []
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        raise ValueError(f"Missing required environment variables: {missing_vars}")

    # Validate API key format
    api_key = os.getenv('GEMINI_API_KEY', '')
    if not api_key.startswith(('AIza', 'GOOGLE_API_KEY')):
        raise ValueError("Invalid API key format")

    # Test AI service connectivity
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        models = genai.list_models()
        if not models:
            raise ValueError("Cannot connect to Gemini API")
    except Exception as e:
        raise ValueError(f"AI service connection failed: {e}")

    print("✅ All configuration validated successfully")
```

### Issue 8: High Error Rates in Production

**Symptoms:**
- Increased 5xx errors in monitoring
- Circuit breaker frequently activating
- User-facing timeouts and failures

**Diagnostic Steps:**
```bash
# Production error analysis
kubectl logs deployment/language-analyzer --tail=100

# Check metrics
kubectl exec -it deployment/language-analyzer -- curl http://localhost:8501/metrics

# Analyze error patterns
# Look for common error messages in logs
grep "ERROR" application.log | tail -20

# Check resource usage
kubectl top pods
```

**Root Causes & Solutions:**

#### Cause 8.1: Resource Exhaustion
**Solution:** Implement resource limits and horizontal scaling
```yaml
# Enhanced deployment with resource limits
apiVersion: apps/v1
kind: Deployment
metadata:
  name: language-analyzer
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: analyzer
        image: language-analyzer:latest
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        env:
        - name: GOMEMLIMIT
          value: "900Mi"  # Go memory limit for better GC
```

#### Cause 8.2: Database/Redis Connection Issues
**Solution:** Implement connection pooling and retry logic
```python
# Redis connection management
def create_resilient_redis_connection():
    import redis
    from redis.retry import Retry
    from redis.backoff import ExponentialBackoff

    retry = Retry(ExponentialBackoff(), 3)

    return redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        password=os.getenv('REDIS_PASSWORD'),
        decode_responses=True,
        retry=retry,
        retry_on_timeout=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        health_check_interval=30
    )
```

## 📊 Monitoring and Alerting Issues

### Issue 9: Missing Metrics or Alerts

**Symptoms:**
- No visibility into system performance
- Issues discovered through user reports
- Reactive rather than proactive monitoring

**Diagnostic Steps:**
```bash
# Check monitoring stack
# Prometheus
curl http://prometheus:9090/-/healthy

# Grafana
curl http://grafana:3000/api/health

# Application metrics
curl http://localhost:8501/metrics

# Alert manager
curl http://alertmanager:9093/-/healthy
```

**Root Causes & Solutions:**

#### Cause 9.1: Incomplete Metrics Setup
**Solution:** Implement comprehensive metrics collection
```python
# Enhanced metrics setup
def setup_comprehensive_metrics():
    from prometheus_client import Counter, Histogram, Gauge, Info, CollectorRegistry

    registry = CollectorRegistry()

    # Business metrics
    ANALYSIS_REQUESTS = Counter(
        'analysis_requests_total',
        'Total analysis requests',
        ['language', 'complexity', 'status'],
        registry=registry
    )

    ANALYSIS_DURATION = Histogram(
        'analysis_duration_seconds',
        'Analysis duration',
        ['language', 'complexity'],
        buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0),
        registry=registry
    )

    # System metrics
    ACTIVE_CONNECTIONS = Gauge(
        'active_connections',
        'Number of active connections',
        registry=registry
    )

    QUEUE_SIZE = Gauge(
        'queue_size',
        'Current queue size',
        registry=registry
    )

    # Error tracking
    ERROR_COUNTER = Counter(
        'errors_total',
        'Total errors by type',
        ['error_type', 'component'],
        registry=registry
    )

    return {
        'analysis_requests': ANALYSIS_REQUESTS,
        'analysis_duration': ANALYSIS_DURATION,
        'active_connections': ACTIVE_CONNECTIONS,
        'queue_size': QUEUE_SIZE,
        'errors': ERROR_COUNTER
    }
```

#### Cause 9.2: Insufficient Alerting Rules
**Solution:** Implement comprehensive alerting
```yaml
# Enhanced alerting rules
groups:
  - name: language_analyzer_critical
    rules:
      - alert: ServiceDown
        expr: up{job="language-analyzer"} == 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Language analyzer service is down"
          description: "Service has been down for 5 minutes"

      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | printf \"%.2f\" }}%"

      - alert: SlowResponses
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Slow response times"
          description: "95th percentile response time is {{ $value | printf \"%.2f\" }}s"

      - alert: LowQualityScore
        expr: analysis_quality_score < 0.6
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Declining analysis quality"
          description: "Average quality score dropped to {{ $value | printf \"%.2f\" }}"

      - alert: HighResourceUsage
        expr: (1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage"
          description: "Memory usage is {{ $value | printf \"%.2f\" }}%"
```

## 🎯 Quick Reference Solutions

### Most Common Issues & Fixes

| Issue | Quick Diagnosis | Quick Fix |
|-------|----------------|-----------|
| Low confidence | Check model selection | Use gemini-2.5-flash for complex analysis |
| Slow responses | Profile components | Implement caching and model optimization |
| Memory leaks | Monitor cache size | Set cache limits and implement cleanup |
| Circuit breaker | Check failure thresholds | Tune parameters for AI service tolerance |
| Poor cache hits | Analyze cache keys | Improve semantic key generation |
| Container failures | Check logs | Fix missing dependencies in Dockerfile |
| High error rates | Analyze error patterns | Implement retry logic and fallbacks |
| Missing metrics | Check Prometheus targets | Fix metrics endpoint configuration |

### Emergency Response Checklist

1. **Service Down**
   - Check pod status: `kubectl get pods`
   - View logs: `kubectl logs deployment/language-analyzer`
   - Restart deployment: `kubectl rollout restart deployment/language-analyzer`

2. **High Error Rate**
   - Check circuit breaker status
   - Review recent deployments
   - Rollback if necessary: `kubectl rollout undo deployment/language-analyzer`

3. **Performance Degradation**
   - Check resource usage: `kubectl top pods`
   - Scale up: `kubectl scale deployment language-analyzer --replicas=5`
   - Clear cache if needed

4. **AI Service Issues**
   - Check API quota and limits
   - Verify API key validity
   - Switch to alternative model if available

### Issue X: Generic Word Explanations in Sino-Tibetan Languages (Word Meanings Dictionary Missing)

**Symptoms:**
- Sino-Tibetan analyzers provide generic explanations like "numeral in zh-tw grammar"
- Missing specific word meanings like "three (numeral)" or "if (conjunction)"
- Fallback quality is poor compared to Chinese Simplified/Traditional gold standards
- Users see grammatical roles instead of helpful word meanings

**Root Cause:**
- Missing external word meanings dictionary JSON file
- Fallbacks not checking word_meanings before generic explanations
- Config not loading word meanings from external file

**Diagnostic Steps:**
```python
def diagnose_word_meanings():
    """Check if Sino-Tibetan analyzer has word meanings dictionary"""
    checks = {
        "has_word_meanings_file": Path("infrastructure/data/{language}_word_meanings.json").exists(),
        "config_loads_meanings": hasattr(config, 'word_meanings') and isinstance(config.word_meanings, dict),
        "fallbacks_check_meanings": fallbacks_prioritize_word_meanings(),
        "rich_explanations": test_fallback_provides_rich_meanings(),
    }
    return checks

def test_fallback_provides_rich_meanings():
    """Test that fallbacks provide specific meanings, not generic roles"""
    test_words = ["三", "如果", "答案"]  # Chinese numerals and compound words
    for word in test_words:
        result = fallbacks._analyze_word(word)
        if "in grammar" in result['individual_meaning']:  # Generic fallback
            return False
    return True  # All words have specific meanings
```

**Solution - Implement Word Meanings Dictionary Pattern:**
```python
# 1. Create word meanings JSON file
# File: infrastructure/data/{language}_word_meanings.json
{
  "一": "one (numeral)",
  "二": "two (numeral)",
  "三": "three (numeral)",
  "如果": "if (conjunction)",
  "因為": "because (conjunction)",
  "答案": "answer, solution (noun)",
  "等於": "equals, equal to (verb/mathematical term)"
}

# 2. Load in config (like Chinese Traditional)
class LanguageConfig:
    def __init__(self):
        config_dir = Path(__file__).parent.parent / "infrastructure" / "data"
        self.word_meanings = self._load_json(config_dir / "{language}_word_meanings.json")
    
    def _load_json(self, path: Path) -> Dict[str, Any]:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load word meanings: {e}")
            return {}

# 3. Use in fallbacks (prioritize dictionary)
class LanguageFallbacks:
    def _analyze_word(self, word: str) -> Dict[str, Any]:
        # Check word meanings first (provides rich explanations)
        if word in self.config.word_meanings:
            meaning = self.config.word_meanings[word]  # "three (numeral)"
            role = self._guess_grammatical_role(word)
            return {
                'word': word,
                'individual_meaning': meaning,  # Rich meaning!
                'grammatical_role': role,
                'confidence': 'high'
            }
        
        # Generic fallback only if no dictionary entry
        role = self._guess_grammatical_role(word)
        meaning = self._generate_fallback_explanation(word, role)  # "numeral in grammar"
        return {
            'word': word,
            'individual_meaning': meaning,
            'grammatical_role': role,
            'confidence': 'low'
        }
```

**Before vs After:**
```python
# ❌ BEFORE - Generic grammatical roles
"三": "numeral in zh-tw grammar"
"如果": "conjunction in zh-tw grammar"
"答案": "noun in zh-tw grammar"

# ✅ AFTER - Rich word meanings
"三": "three (numeral)"
"如果": "if (conjunction)"
"答案": "answer, solution (noun)"
```

**Solution Steps:**
1. **Create Word Meanings JSON**: Essential vocabulary with specific English meanings
2. **Update Config Class**: Load JSON file in initialization
3. **Update Fallbacks**: Check word_meanings before generic explanations
4. **Test Rich Quality**: Verify dictionary provides specific meanings over generic roles
5. **Compare with Gold Standards**: Match Chinese Simplified/Traditional fallback quality

### Issue X: Generic Word Explanations in Sino-Tibetan Languages (Word Meanings Dictionary Missing)

**Symptoms:**
- Sino-Tibetan analyzers provide generic explanations like "numeral in zh-tw grammar"
- Missing specific word meanings like "three (numeral)" or "if (conjunction)"
- Fallback quality is poor compared to Chinese Simplified/Traditional gold standards
- Users see grammatical roles instead of helpful word meanings

**Root Cause:**
- Missing external word meanings dictionary JSON file
- Fallbacks not checking word_meanings before generic explanations
- Config not loading word meanings from external file
- AI prompt not emphasizing uniqueness and specificity enough

**Diagnostic Steps:**
```python
def diagnose_word_meanings():
    """Check if Sino-Tibetan analyzer has word meanings dictionary"""
    checks = {
        "has_word_meanings": hasattr(config, 'word_meanings') and bool(config.word_meanings),
        "word_meanings_loaded": len(config.word_meanings) > 0,
        "response_parser_uses_dict": 'word_meanings' in str(response_parser._transform_to_standard_format),
        "generic_explanation_detection": hasattr(response_parser, '_is_generic_explanation'),
    }
    return checks

def test_fallback_provides_rich_meanings():
    """Test that fallbacks provide specific meanings, not generic roles"""
    analyzer = LanguageAnalyzer()
    result = analyzer.analyze_grammar("我爱你", "爱", "intermediate", "api_key")
    
    generic_count = 0
    for word, role, color, meaning in result.word_explanations:
        if "word that describes" in meaning or "in zh-tw grammar" in meaning:
            generic_count += 1
    
    return generic_count == 0  # All words have specific meanings
```

**Solution - Implement Word Meanings Dictionary Pattern:**
```python
# 1. Create word meanings JSON file
# File: infrastructure/data/{language}_word_meanings.json
{
  "我": "I, me (first person singular pronoun)",
  "你": "you (second person singular pronoun)",
  "他": "he, him (third person masculine singular pronoun)",
  "是": "to be, is, am, are (copula verb)",
  "的": "possessive/attributive particle (links attribute to noun)",
  "了": "particle indicating completed action (perfective aspect marker)",
  "吗": "question particle (interrogative modal particle)",
  "不": "not (negation adverb)",
  "很": "very (degree adverb)",
  "在": "at, in, on (preposition/locative)",
  "有": "to have, there is/are (existential verb)",
  "这": "this (demonstrative pronoun)",
  "那": "that (demonstrative pronoun)",
  "一": "one (numeral)",
  "二": "two (numeral)",
  "三": "three (numeral)"
}

# 2. Load in config (like Chinese Traditional)
class LanguageConfig:
    def __init__(self):
        config_dir = Path(__file__).parent.parent / "infrastructure" / "data"
        self.word_meanings = self._load_json(config_dir / "{language}_word_meanings.json")

# 3. Use in response parser (prioritize dictionary over generic AI responses)
class LanguageResponseParser:
    def _transform_to_standard_format(self, data, complexity, target_word=None):
        for word_data in words:
            explanation = word_data.get('individual_meaning', standard_role)
            
            # Use word meanings dictionary if explanation is generic
            if self._is_generic_explanation(explanation):
                dict_meaning = self.config.word_meanings.get(word, '')
                if dict_meaning:
                    explanation = dict_meaning
                else:
                    # Fallback to role-based explanation
                    explanation = f"{word} ({standard_role})"
    
    def _is_generic_explanation(self, explanation: str) -> bool:
        """Check if an explanation is generic and should be replaced."""
        generic_patterns = [
            "a word that describes a noun",
            "a word that describes a verb", 
            "a word that describes an adjective",
            "a particle",
            "an interjection",
            "other",
            "noun in zh-tw grammar",
            "verb in zh-tw grammar",
            "adjective in zh-tw grammar"
        ]
        return any(pattern in explanation.lower() for pattern in generic_patterns)

# 4. Enhance AI prompt for specificity
def build_prompt():
    return """
For EACH word... provide:
- individual_meaning: SPECIFIC translation/meaning of this EXACT word (MANDATORY - UNIQUE for each word, not generic category descriptions)

CRITICAL REQUIREMENTS:
- individual_meaning MUST be SPECIFIC and UNIQUE for EACH word - provide the actual meaning/translation, NOT generic descriptions like "a word that describes a noun"
"""
```

**Before vs After:**
```python
# ❌ BEFORE - Generic grammatical roles
"媽": "adjective in zh-tw grammar"
"教": "adjective in zh-tw grammar"  
"我": "other"
"怎麼": "interjection"
"麼": "adjective in zh-tw grammar"
"煮": "adjective in zh-tw grammar"
"飯": "noun"

# ✅ AFTER - Rich word meanings
"媽": "mother, mom (noun)"
"教": "to teach (verb)"
"我": "I, me (first person singular pronoun)"
"怎麼": "how (interrogative pronoun)"
"麼": "question particle (interrogative modal particle)"
"煮": "to cook, to boil (verb)"
"飯": "meal, rice, food (noun)"
```

**Solution Steps:**
1. **Create Word Meanings JSON**: Essential vocabulary with specific English meanings
2. **Update Config Class**: Load JSON file in initialization  
3. **Update Response Parser**: Check for generic explanations and substitute with dictionary meanings
4. **Enhance AI Prompt**: Emphasize uniqueness and specificity in meanings
5. **Test Rich Quality**: Verify dictionary provides specific meanings over generic roles
6. **Compare with Gold Standards**: Match Chinese Simplified fallback quality

---

**Remember:** When in doubt, compare with the gold standards ([Hindi](languages/hindi/hi_analyzer.py) and [Chinese Simplified](languages/zh/zh_analyzer.py)). They represent the proven working patterns - no artificial confidence boosting, clean facade orchestration, natural validation scoring.

---

# LESSONS LEARNED FROM RECENT FIXES

## Chinese Traditional Analyzer Fixes (2024)

### 1. F-String Syntax Validation
**Problem:** Nested f-strings causing syntax errors that prevent analyzer loading
```python
# ❌ BROKEN - Nested f-strings
f"Error in {f'processing {word}'}"

# ✅ FIXED - Single f-string
f"Error in processing {word}"
```

**Prevention:** Always validate f-string syntax before deployment. Use Pylance syntax checking to catch these errors early.

### 2. Complete Method Implementation
**Problem:** Missing `parse_response` method in response parser, causing analyzer to fail
```python
# ❌ MISSING - Method not implemented
class ZhTwResponseParser:
    # parse_response method missing!
    pass

# ✅ FIXED - Complete implementation
class ZhTwResponseParser:
    def parse_response(self, response: str) -> Dict[str, Any]:
        # Full implementation here
        return parsed_data
```

**Prevention:** Ensure all abstract methods are implemented. Compare with gold standards (Hindi/Chinese Simplified) to verify completeness.

### 3. AI Prompt Engineering for Uniqueness
**Problem:** AI providing repeated generic meanings instead of unique individual explanations
```python
# ❌ WEAK PROMPT - Leads to repetition
"Analyze this Chinese Traditional word"

# ✅ STRONG PROMPT - Enforces uniqueness
"Provide UNIQUE, INDIVIDUAL meanings for each word. Each word must have its own specific meaning, not generic category labels."
```

**Prevention:** Use explicit instructions with examples. Include "UNIQUE" and "INDIVIDUAL" requirements. Add mandatory fields like "individual_meaning".

### 4. Fallback Summary Generation
**Problem:** Generic "Grammar analysis for ZH-TW" summaries instead of rich sentence structure analysis
```python
# ❌ GENERIC - No real content
"Grammar analysis for ZH-TW"

# ✅ RICH - Generated from word data
"Subject-Verb-Object structure with time adverbial '昨天' (yesterday) modifying the verb phrase '去學校' (go to school)"
```

**Prevention:** Implement `_transform_to_standard_format()` to generate `overall_structure` from `word_explanations` when AI response lacks it.

### 5. TTS Language Code Mapping
**Problem:** TTS voice loading failures for "zh-TW" due to incompatible language codes
```python
# ❌ FAILS - zh-TW not supported
voice = get_voice_for_language("zh-TW")

# ✅ WORKS - Map to compatible code
language_map = {"zh-TW": "cmn-CN"}
voice = get_voice_for_language(language_map.get(lang, lang))
```

**Prevention:** Add language code mapping in `audio_generator.py` for TTS compatibility. Test voice loading for all supported languages.

### 6. Component Isolation Pattern
**Problem:** Analyzer calling undefined base methods instead of using modular components
```python
# ❌ WRONG - Calling undefined methods
self.build_single_sentence_prompt()  # Method doesn't exist!

# ✅ CORRECT - Use component directly
self.prompt_builder.build_single_sentence_prompt()
```

**Prevention:** Follow domain-driven design. Use `self.config`, `self.prompt_builder`, `self.response_parser`, etc. directly.

### 7. Syntax Error Prevention
**Problem:** Pylance detecting malformed try blocks with duplicate statements
```python
# ❌ BROKEN - Duplicate try statements
try:
    # code
try:  # Second try without except/finally
    # more code

# ✅ FIXED - Proper structure
try:
    # code
except Exception as e:
    # handle error
```

**Prevention:** Run Pylance syntax validation before committing. Fix all "Try statement must have at least one except or finally clause" errors.

### Key Takeaways
- **Always validate syntax** with Pylance before deployment
- **Compare with gold standards** (Hindi/Chinese Simplified) for proven patterns
- **Use explicit AI prompts** with uniqueness requirements and examples
- **Implement robust fallbacks** that generate meaningful content from available data
- **Map incompatible language codes** for TTS and other services
- **Follow modular architecture** - use components directly, not through undefined base methods
- **Document fixes comprehensively** to prevent future regressions

These fixes resolved: repeated word meanings, generic grammar summaries, TTS voice loading failures, and multiple syntax errors in the Chinese Traditional analyzer.