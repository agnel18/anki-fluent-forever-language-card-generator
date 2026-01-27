# Sino-Tibetan Language Family Guide
## Chinese, Tibetan, Burmese Language Analyzers

**Gold Standards:** [Chinese Simplified](languages/zh/zh_analyzer.py) and [Chinese Traditional](languages/chinese_traditional/zh_tw_analyzer.py)  
**Key Characteristics:** Analytic languages, logographic scripts, rich character-based analysis  
**Critical Pattern:** Rich explanations with individual word meanings (not just grammatical roles)

## 🎯 Sino-Tibetan Language Characteristics

### Core Features
- **Analytic Structure**: No morphological inflection, word order determines grammar
- **Logographic Scripts**: Characters represent meaning/concepts, not sounds
- **Character-Based Analysis**: Individual characters have semantic and grammatical roles
- **Rich Contextual Meaning**: Each word requires explanation of meaning + grammatical function

### Implementation Challenges
- **Character Segmentation**: Proper word/character boundary identification
- **Meaning Extraction**: Individual meanings for each character/word
- **Color Coding**: Position-based coloring for logographic text
- **Rich Explanations**: Detailed explanations beyond basic grammatical roles

## 🏗️ Gold Standard Architecture

### Chinese Simplified Analyzer (Reference Implementation)
```python
class ZhAnalyzer(BaseGrammarAnalyzer):
    """
    Gold standard for Sino-Tibetan languages.
    Provides rich explanations for each character with individual meanings.
    """

    def analyze_grammar(self, sentence: str, target_word: str, complexity: str, api_key: str) -> GrammarAnalysis:
        """Main method providing rich character-by-character analysis"""
        # 1. AI call for detailed analysis
        ai_response = self._call_ai_model(prompt, api_key)

        # 2. Parse individual meanings
        parsed = self.response_parser.parse_response(ai_response, sentence, complexity)

        # 3. Generate HTML with colored explanations
        html = self._generate_html_output(parsed, sentence, complexity)

        return GrammarAnalysis(
            sentence=sentence,
            word_explanations=parsed.get('word_explanations', []),
            html_output=html,
            explanations=parsed.get('explanations', {})
        )

    def _generate_html_output(self, parsed_data: Dict[str, Any], sentence: str, complexity: str) -> str:
        """Generate colored HTML with individual character meanings"""
        explanations = parsed_data.get('word_explanations', [])
        color_scheme = self.get_color_scheme(complexity)

        # Position-based character replacement with colors and meanings
        html_parts = []
        i = 0
        while i < len(sentence):
            matched = False
            for exp in sorted_explanations:
                if len(exp) >= 4:  # [word, role, color, meaning]
                    word, role, color, meaning = exp[0], exp[1], exp[2], exp[3]
                    word_len = len(word)

                    if i + word_len <= len(sentence) and sentence[i:i + word_len] == word:
                        # Apply color and preserve meaning
                        colored_word = f'<span style="color: {color}; font-weight: bold;">{word}</span>'
                        html_parts.append(colored_word)
                        i += word_len
                        matched = True
                        break

            if not matched:
                html_parts.append(sentence[i])
                i += 1

        return ''.join(html_parts)
```

### Chinese Traditional Analyzer (Variant Implementation)
```python
class ZhTwAnalyzer(BaseGrammarAnalyzer):
    """
    Chinese Traditional variant following Simplified gold standard patterns.
    Demonstrates how to implement rich explanations for language variants.
    """

    def analyze_grammar(self, sentence: str, target_word: str, complexity: str, api_key: str) -> GrammarAnalysis:
        """Rich explanation workflow identical to Chinese Simplified"""
        # Same pattern as ZhAnalyzer but with Traditional character support
        # Use modular components: config, prompt_builder, response_parser, validator

        # 1. Build prompt with Traditional-specific context
        prompt = self.prompt_builder.build_single_prompt(sentence, target_word, complexity)

        # 2. Call AI for detailed analysis
        ai_response = self._call_ai_model(prompt, api_key)

        # 3. Parse response extracting individual_meaning
        parsed = self.response_parser.parse_response(ai_response, sentence, complexity)

        # 4. Generate HTML with rich explanations
        html = self._generate_html_output(parsed, sentence, complexity)

        return GrammarAnalysis(
            sentence=sentence,
            word_explanations=parsed.get('word_explanations', []),
            html_output=html,
            explanations=parsed.get('explanations', {})
        )
```

## 📋 Implementation Checklist

### Phase 1: Core Architecture Setup
- [ ] **Inherit from BaseGrammarAnalyzer** (not IndoEuropeanAnalyzer)
- [ ] **Implement modular components**: config, prompt_builder, response_parser, validator
- [ ] **Add rich explanation methods**: `analyze_grammar` and `_generate_html_output`
- [ ] **Import GrammarAnalysis** for structured return values

### Phase 2: Rich Explanation Implementation
- [ ] **analyze_grammar method**: AI workflow → parsing → HTML generation
- [ ] **_generate_html_output method**: Position-based character coloring with meanings
- [ ] **Word explanations format**: `[word, role, color, meaning]` tuples
- [ ] **Individual meanings**: Extract `individual_meaning` from AI responses

### Phase 3: Language-Specific Configuration
- [ ] **Character set handling**: Support for both simplified and traditional characters
- [ ] **Color schemes**: Grammatical role to color mapping
- [ ] **Prompt templates**: Language-specific AI prompting strategies
- [ ] **Validation rules**: Quality assessment for logographic analysis

### Phase 4: Testing and Validation
- [ ] **Rich explanation testing**: Verify individual meanings are extracted
- [ ] **HTML output testing**: Confirm proper coloring and positioning
- [ ] **Character boundary testing**: Ensure correct word segmentation
- [ ] **Cross-validation**: Compare with Chinese Simplified gold standard

## 🔧 Key Patterns Learned

### 1. Rich vs Basic Explanations
**❌ Before (Chinese Traditional):**
```
"pronoun in zh-tw grammar"
"verb in zh-tw grammar"
```

**✅ After (Gold Standard):**
```
"我 (I, me - first person singular pronoun)"
"喜歡 (to like, to be fond of - verb expressing preference)"
"吃 (to eat, to consume - verb of consumption)"
```

### 2. Modular Architecture Benefits
- **Separation of Concerns**: Config, prompts, parsing, validation in separate components
- **Testability**: Each component can be tested independently
- **Maintainability**: Changes to one aspect don't affect others
- **Reusability**: Components can be shared across language variants

### 3. Position-Based Coloring
- **Character-Level Coloring**: Individual characters get colors based on grammatical roles
- **Meaning Preservation**: HTML output maintains semantic information
- **Anki Compatibility**: Inline styles work in flashcard applications
- **Visual Clarity**: Colors help learners identify grammatical structures

### 4. AI Response Processing
- **Individual Meaning Extraction**: Parse `individual_meaning` from AI responses
- **Structured Output**: Convert AI responses to `word_explanations` arrays
- **Quality Validation**: Natural confidence scoring without artificial boosting
- **Fallback Handling**: Graceful degradation when AI calls fail

## 🎖️ Success Criteria

### Rich Explanation Quality
- [ ] Each word has detailed meaning explanation (not just grammatical role)
- [ ] Explanations are contextually appropriate for the sentence
- [ ] Colors accurately represent grammatical functions
- [ ] HTML output renders correctly in Anki and web interfaces

### Architectural Compliance
- [ ] Follows facade pattern with domain component orchestration
- [ ] Uses modular architecture (config, prompt_builder, response_parser, validator)
- [ ] Implements proper error handling and fallbacks
- [ ] Passes all quality validation checks

### Performance Standards
- [ ] AI calls complete within reasonable time limits
- [ ] HTML generation is efficient for long sentences
- [ ] Memory usage remains bounded for large texts
- [ ] Caching works effectively for repeated analyses

## 🚀 Advanced Optimizations

### Batch Processing
```python
def analyze_batch_response(self, ai_response: str, sentences: List[str], complexity: str) -> Dict[str, Any]:
    """Process multiple sentences efficiently"""
    # Parse batch response
    # Extract individual meanings for each sentence
    # Return structured results
```

### Caching Strategies
- **Semantic Similarity**: Cache based on meaning similarity, not exact text matches
- **Component-Level Caching**: Cache prompts, responses, and parsed results separately
- **Invalidation Rules**: Clear cache when language models or prompts change

### Quality Monitoring
- **Explanation Richness Scoring**: Measure detail level of explanations
- **Color Consistency**: Ensure grammatical roles map to consistent colors
- **User Feedback Integration**: Learn from user corrections and preferences

## 📚 Related Resources

- **[Chinese Simplified Analyzer](../zh/zh_analyzer.py)** - Primary gold standard
- **[Chinese Traditional Analyzer](../chinese_traditional/zh_tw_analyzer.py)** - Variant implementation
- **[Base Grammar Analyzer](../../streamlit_app/language_analyzers/base_analyzer.py)** - Foundation class
- **[Architecture Guide](../architecture_guide.md)** - Overall design patterns
- **[Implementation Guide](../implementation_guide.md)** - Step-by-step coding guide</content>
<parameter name="filePath">d:\Language Learning\LanguagLearning\language_grammar_generator\language_family_guides\sino_tibetan.md