# language_grammar_generator/phase1_research_prompt.py
"""
Phase 1: Research & Planning Prompt

This prompt generates comprehensive research documentation for a new language analyzer.
Run this first to establish the linguistic foundation for implementation.

UPDATED: Incorporates learnings from French analyzer v2.0 including:
- Advanced AI integration with robust parsing strategies
- Confidence scoring and quality validation systems
- Comprehensive grammatical role hierarchies
- APKG-ready output formatting with HTML color coding
- Production-ready error handling and fallback systems
"""

PHASE1_RESEARCH_PROMPT = """
You are a linguistics expert specializing in language analysis for educational applications. Your task is to research and plan a complete grammar analyzer for a new language, incorporating the latest advancements from production-ready implementations.

LANGUAGE: {LANGUAGE_NAME} ({LANGUAGE_CODE})
LANGUAGE FAMILY: {LANGUAGE_FAMILY}
SCRIPT TYPE: {SCRIPT_TYPE} (alphabetic/logographic/abugida)
WORD ORDER: {WORD_ORDER} (SVO/SOV/VSO/etc.)

Create a comprehensive research document that will serve as the foundation for implementing a production-ready analyzer. Include:

1. LANGUAGE OVERVIEW
- Linguistic classification and key features
- Writing system characteristics with RTL/LTR considerations
- Major grammatical categories and morphological complexity
- Language-specific challenges for automated analysis

2. ADVANCED GRAMMATICAL INVENTORY
- Complete hierarchical parts of speech (beginner → intermediate → advanced)
- Morphological features (gender, case, tense, aspect, mood, voice, etc.)
- Agreement systems and concord rules
- Derivational and inflectional morphology patterns
- Syntax patterns and word order variations
- Discourse markers and pragmatic particles

3. ENHANCED COMPLEXITY HIERARCHY
- Beginner level: Core parts of speech with basic morphology
- Intermediate level: Function words, basic agreement, compound tenses
- Advanced level: Full grammatical framework, complex embeddings, stylistic variations

4. AI ANALYSIS REQUIREMENTS
- Grammatical roles that AI must identify with high accuracy
- Language-specific parsing challenges and disambiguation rules
- Confidence scoring criteria for different grammatical constructs
- Common learner errors and misanalyses to avoid

5. PRODUCTION-READY FEATURES
- APKG output formatting requirements (HTML color coding, word explanations)
- Error handling patterns and fallback strategies
- Performance requirements and caching strategies
- Integration points with existing analyzer framework

6. QUALITY ASSURANCE FRAMEWORK
- Gold standard patterns for validation
- Confidence threshold requirements (target: 0.80+ for production)
- Error detection and recovery mechanisms
- Cross-linguistic consistency requirements

Format as a structured markdown document ready for implementation.

CRITICAL PRODUCTION REQUIREMENTS:
- Design for 95%+ parsing accuracy on well-formed sentences
- Include comprehensive fallback systems for edge cases
- Ensure APKG-ready output with detailed word explanations
- Plan for real-time performance (sub-2 second response times)
- Incorporate confidence scoring for reliability assessment

IMPORTANT: Each language is unique - adapt this research to the specific linguistic features of {LANGUAGE_NAME} while maintaining compatibility with the proven French analyzer architecture.
"""