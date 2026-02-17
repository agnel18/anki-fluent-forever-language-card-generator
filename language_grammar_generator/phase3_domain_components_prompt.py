# language_grammar_generator/phase3_domain_components_prompt.py
"""
Phase 3: Domain Components Prompt

This prompt creates all domain components for a language analyzer following Clean Architecture principles.
This is where the AI prompts for grammar analysis are defined - customize for each language.

UPDATED: Incorporates advanced AI integration from French analyzer v2.0 including:
- Robust parsing with 5 fallback strategies for JSON extraction
- Confidence scoring system with grammatical validation
- Enhanced prompt engineering with language-specific instructions
- Comprehensive word explanation formatting for APKG output
- Production-ready error handling and validation
"""

PHASE3_DOMAIN_COMPONENTS_PROMPT = """
You are a domain-driven design expert specializing in production-ready language analysis systems. Your task is to create all domain components for a language analyzer following Clean Architecture principles, incorporating the latest proven patterns from successful implementations.

LANGUAGE: {LANGUAGE_NAME} ({LANGUAGE_CODE})
LANGUAGE FAMILY: {LANGUAGE_FAMILY}
SCRIPT: {SCRIPT_TYPE}

Create the complete domain layer with these production-ready components:

1. ENHANCED CONFIG COMPONENT ({language_code}_config.py):
- Language metadata with RTL/LTR support and script characteristics
- Hierarchical grammatical roles mapping (beginner → intermediate → advanced)
- HTML color schemes for APKG theming with accessibility compliance
- External file loading with validation (YAML/JSON)
- Language-specific patterns, agreement rules, and morphological features
- Confidence scoring thresholds and quality metrics

2. ADVANCED PROMPT BUILDER ({language_code}_prompt_builder.py):
- Jinja2 template-based prompt generation with dynamic complexity adaptation
- Single and batch analysis prompt templates with retry logic
- Language-specific grammatical role formatting and cultural context
- Complexity-specific prompt variations with fallback strategies
- Performance optimization with prompt caching and length management

3. ROBUST RESPONSE PARSER ({language_code}_response_parser.py):
- 5-level fallback parsing strategy:
  1. Direct JSON parsing
  2. Markdown code block extraction
  3. JSON repair and reconstruction
  4. Text pattern extraction
  5. Rule-based fallback analysis
- Confidence scoring integration with grammatical validation
- Error detection and recovery mechanisms
- Structured logging and performance monitoring

4. COMPREHENSIVE VALIDATOR ({language_code}_validator.py):
- Multi-dimensional confidence scoring (structure, content, grammar, completeness)
- Language-specific error detection patterns
- Word explanation quality validation
- APKG formatting compliance checking
- Performance metrics and quality benchmarking

5. INTELLIGENT FALLBACKS ({language_code}_fallbacks.py):
- Rule-based grammatical analysis using language-specific patterns
- Complexity-appropriate explanation generation
- Morphological analysis and agreement validation
- Integration with response parser for seamless fallback chains

PRODUCTION-READY AI PROMPT TEMPLATE FOR {LANGUAGE_NAME}:

You are an expert linguist specializing in {LANGUAGE_NAME} grammar analysis for educational applications. Your task is to analyze {LANGUAGE_NAME} sentences and provide detailed grammatical breakdowns that help language learners understand sentence structure, with production-ready accuracy and reliability.

## ANALYSIS REQUIREMENTS FOR {LANGUAGE_NAME}

For each {LANGUAGE_NAME} sentence, provide a word-by-word grammatical analysis with these exact specifications:

### CRITICAL OUTPUT FORMAT
Return a JSON object with exactly this structure:
{{
  "sentence": "the original sentence",
  "words": [
    {{
      "word": "exact word from sentence",
      "grammatical_role": "one of: [LIST {LANGUAGE_NAME}-SPECIFIC ROLES HERE BASED ON PHASE 1 RESEARCH]",
      "gender": "masculine/feminine/neuter/null (as applicable for {LANGUAGE_NAME})",
      "number": "singular/plural/null (as applicable for {LANGUAGE_NAME})",
      "person": "1st/2nd/3rd/null (as applicable for {LANGUAGE_NAME})",
      "tense": "present/past/future/etc/null (as applicable for {LANGUAGE_NAME})",
      "individual_meaning": "detailed explanation of this word's grammatical function, morphological features, agreement patterns, and meaning in context"
    }}
  ],
  "explanations": {{
    "overall_structure": "comprehensive analysis of sentence structure, word order, agreement patterns, and grammatical relationships",
    "key_features": "language-specific grammatical features demonstrated (gender agreement, case marking, verb conjugation patterns, etc.)",
    "complexity_notes": "complexity level assessment and learning objectives addressed"
  }}
}}

### QUALITY ASSURANCE REQUIREMENTS
- **Accuracy**: 95%+ grammatical role accuracy
- **Completeness**: Every word must be analyzed with appropriate grammatical role
- **Consistency**: Use consistent terminology throughout analysis
- **Educational Value**: Explanations must help learners understand {LANGUAGE_NAME} grammar patterns
- **APKG Compatibility**: Output must support HTML color coding and detailed word explanations

### {LANGUAGE_NAME}-SPECIFIC INSTRUCTIONS
[ADAPT THESE BASED ON PHASE 1 RESEARCH - INCLUDE LANGUAGE-SPECIFIC GRAMMAR RULES, AGREEMENT PATTERNS, MORPHOLOGICAL FEATURES, AND COMMON LEARNER DIFFICULTIES]

### ERROR PREVENTION
- Never invent grammatical roles not native to {LANGUAGE_NAME}
- Maintain consistent gender/number/person marking throughout analysis
- Provide accurate morphological breakdown for complex words
- Include cultural context where relevant for educational value

### CONFIDENCE SCORING INTEGRATION
The system will automatically calculate confidence scores based on:
- Structural completeness (all words analyzed)
- Grammatical role accuracy
- Explanation quality and educational value
- Consistency with {LANGUAGE_NAME} linguistic patterns

Generate production-ready domain components that integrate seamlessly with the existing analyzer framework and deliver consistent, high-quality grammatical analysis for language learning applications.
"""