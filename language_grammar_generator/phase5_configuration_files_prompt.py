# language_grammar_generator/phase5_configuration_files_prompt.py
"""
Phase 5: Configuration Files Prompt

This prompt creates all external configuration files (YAML/JSON) for a language analyzer.
These files contain language-specific grammatical data and patterns.

UPDATED: Incorporates comprehensive configuration system from French analyzer v2.0 including:
- Hierarchical grammatical roles with complexity progression
- APKG-ready color schemes with accessibility compliance
- Confidence scoring thresholds and quality metrics
- Language-specific patterns and morphological features
- Validation rules and error detection patterns
"""

PHASE5_CONFIGURATION_PROMPT = """
You are a configuration management expert specializing in production-ready language analysis systems. Your task is to create all external configuration files for a language analyzer with comprehensive grammatical data and validation rules.

LANGUAGE: {LANGUAGE_NAME} ({LANGUAGE_CODE})
LANGUAGE FAMILY: {LANGUAGE_FAMILY}
SCRIPT: {SCRIPT_TYPE}

Create the complete set of configuration files in infrastructure/data/ with production-ready specifications:

1. HIERARCHICAL GRAMMATICAL ROLES YAML ({language_code}_grammatical_roles.yaml):
```yaml
# Production-ready grammatical role hierarchy with confidence scoring
beginner:
  core_pos:
    - noun: "person, place, thing, or idea"
    - verb: "action or state of being"
    - adjective: "describes nouns"
    - pronoun: "replaces nouns"
    - preposition: "shows relationships"
    - conjunction: "connects clauses"
  confidence_threshold: 0.85
  fallback_priority: ["noun", "verb", "adjective", "pronoun"]

intermediate:
  expanded_pos:
    - determiner: "specifies which noun (articles, demonstratives, possessives)"
    - adverb: "modifies verbs, adjectives, or other adverbs"
    - auxiliary: "helps form verb tenses and questions"
    - modal: "expresses possibility, necessity, permission"
    - interrogative: "used in questions (who, what, where, etc.)"
  morphological_features:
    - gender: "masculine, feminine, neuter"
    - number: "singular, plural"
    - tense: "present, past, future"
    - person: "1st, 2nd, 3rd"
  agreement_rules:
    - subject_verb: "pronoun and verb agreement"
    - adjective_noun: "adjective agreement with noun"
  confidence_threshold: 0.80
  fallback_priority: ["verb", "noun", "determiner", "adverb"]

advanced:
  complete_framework:
    - particle: "grammatical words with specific functions"
    - case_marker: "shows grammatical relationships"
    - aspect_marker: "expresses how actions unfold"
    - honorific: "shows respect or social status"
    - discourse_particle: "organizes conversation flow"
  complex_morphology:
    - derivational: "word formation through affixes"
    - inflectional: "grammatical changes (tense, case, number)"
    - compounding: "word formation by combining roots"
    - reduplication: "word repetition for emphasis"
  syntactic_structures:
    - relative_clauses: "embedded clauses modifying nouns"
    - complex_sentences: "multiple clauses with subordination"
    - passive_constructions: "object becomes subject"
  confidence_threshold: 0.75
  fallback_priority: ["verb", "noun", "particle", "case_marker"]

# Language-specific patterns and rules
language_patterns:
  word_order: "{WORD_ORDER}"  # SVO, SOV, VSO, etc.
  agreement_system: "{AGREEMENT_TYPE}"  # gender, case, both, none
  morphological_complexity: "{COMPLEXITY_LEVEL}"  # isolating, agglutinative, fusional
  script_direction: "{SCRIPT_DIRECTION}"  # ltr, rtl, ttb

# Error detection patterns
error_patterns:
  common_misanalyses:
    - pattern: "verb_confused_with_noun"
      description: "Verbs incorrectly classified as nouns"
      correction_rule: "check_for_inflectional_markers"
    - pattern: "agreement_errors"
      description: "Gender/number agreement mismatches"
      correction_rule: "validate_agreement_rules"
  confidence_adjustments:
    - low_confidence_trigger: 0.60
      adjustment_factor: -0.15
    - high_confidence_boost: 0.90
      adjustment_factor: +0.05
```

2. COMPREHENSIVE WORD MEANINGS JSON ({language_code}_word_meanings.json):
```json
{
  "grammatical_concepts": {
    "parts_of_speech": {
      "noun": "person, place, thing, or idea that can be subject or object",
      "verb": "word expressing action, state, or occurrence",
      "adjective": "word describing or modifying nouns",
      "adverb": "word modifying verbs, adjectives, or other adverbs",
      "pronoun": "word replacing a noun or noun phrase",
      "preposition": "word showing relationship between nouns",
      "conjunction": "word connecting clauses or sentences",
      "determiner": "word specifying which noun is being referred to",
      "interjection": "word expressing emotion or sudden burst of feeling"
    },
    "morphological_features": {
      "gender": "grammatical classification affecting word forms and agreement",
      "number": "distinction between singular and plural",
      "case": "word form changes based on grammatical function",
      "tense": "time reference of verb actions",
      "aspect": "how an action unfolds over time",
      "mood": "speaker's attitude toward the action",
      "voice": "relationship between subject and action",
      "person": "participant role in discourse (1st, 2nd, 3rd)"
    },
    "syntactic_structures": {
      "subject": "entity performing the action",
      "predicate": "information about the subject",
      "object": "entity affected by the action",
      "modifier": "word or phrase providing additional information",
      "complement": "word or phrase completing the meaning"
    }
  },
  "language_specific_features": {
    "{LANGUAGE_NAME}_unique_patterns": {
      "pattern_1": "description of unique grammatical pattern",
      "pattern_2": "description of another unique feature"
    }
  },
  "learner_difficulties": {
    "common_errors": [
      "error_pattern_1",
      "error_pattern_2"
    ],
    "teaching_strategies": [
      "strategy_1",
      "strategy_2"
    ]
  }
}
```

3. APKG COLOR SCHEMES JSON ({language_code}_color_schemes.json):
```json
{
  "grammatical_colors": {
    "pronouns": "#FF4444",
    "verbs": "#44FF44",
    "nouns": "#FFAA00",
    "adjectives": "#FF44FF",
    "adverbs": "#44FFFF",
    "determiners": "#AA44FF",
    "prepositions": "#4444FF",
    "conjunctions": "#44AAFF",
    "interjections": "#FF8844",
    "particles": "#AAFF44",
    "case_markers": "#FFAA88",
    "aspect_markers": "#88FFAA",
    "auxiliaries": "#F7DC6F",
    "modals": "#BB8FCE",
    "interrogatives": "#85C1E9",
    "other": "#888888"
  },
  "complexity_themes": {
    "beginner": {
      "background": "#F8F9FA",
      "text": "#212529",
      "highlight": "#FFE066"
    },
    "intermediate": {
      "background": "#F1F3F4",
      "text": "#3C4043",
      "highlight": "#81C784"
    },
    "advanced": {
      "background": "#FAFAFA",
      "text": "#202124",
      "highlight": "#64B5F6"
    }
  },
  "accessibility": {
    "high_contrast": true,
    "color_blind_friendly": true,
    "minimum_ratio": 4.5
  }
}
```

4. VALIDATION RULES JSON ({language_code}_validation_rules.json):
```json
{
  "confidence_scoring": {
    "structure_weight": 0.25,
    "content_weight": 0.30,
    "grammar_weight": 0.30,
    "completeness_weight": 0.15,
    "minimum_threshold": 0.70,
    "excellent_threshold": 0.85
  },
  "quality_checks": {
    "word_coverage": {
      "required": 100,
      "description": "All words in sentence must be analyzed"
    },
    "role_consistency": {
      "required": true,
      "description": "Grammatical roles must be consistent with language patterns"
    },
    "explanation_quality": {
      "minimum_length": 20,
      "description": "Explanations must be detailed enough for learning"
    }
  },
  "error_detection": {
    "impossible_patterns": [
      "verb_with_case_marker_only_for_nouns",
      "noun_with_tense_marker_only_for_verbs"
    ],
    "agreement_violations": [
      "gender_mismatch",
      "number_mismatch",
      "case_mismatch"
    ]
  }
}
```

KEY PRODUCTION REQUIREMENTS:
- **Completeness**: Cover all grammatical categories for {LANGUAGE_NAME}
- **Hierarchy**: Clear progression from beginner to advanced levels
- **APKG Ready**: Color schemes optimized for Anki card readability
- **Validation**: Comprehensive rules for quality assurance
- **Accessibility**: WCAG compliant color schemes and contrast ratios

ADAPT FOR {LANGUAGE_NAME}: Customize all configurations to reflect {LANGUAGE_NAME}'s specific grammatical system, morphological patterns, and learner challenges while maintaining the proven structure from the French analyzer.

3. PATTERNS YAML ({language_code}_patterns.yaml):
- Text validation regex patterns
- Word-level linguistic patterns
- Script and Unicode validation
- Diacritical mark patterns

4. LANGUAGE CONFIG YAML ({language_code}_language_config.yaml):
- Core language metadata
- Analysis complexity settings
- UI theming and colors
- API and performance configuration

5. ADDITIONAL LANGUAGE-SPECIFIC FILES:
- Case markers, verb conjugations, etc. (as needed)

KEY REQUIREMENTS:
- Comprehensive coverage of language features
- Complexity-appropriate role definitions
- Extensive word meanings database
- Valid regex patterns for validation
- Proper YAML/JSON formatting

Generate complete, validated configuration files.

CRITICAL: Adapt all content for {LANGUAGE_NAME} specific grammatical features, vocabulary, and linguistic patterns. Each language requires customized configuration data.
"""