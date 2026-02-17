# language_grammar_generator/language_analyzer_creation_guide.py
"""
Language Analyzer Creation Guide

This file contains the complete workflow for creating new language analyzers.
Each phase has its own prompt file that generates the necessary components.

WORKFLOW FOR CREATING A NEW LANGUAGE ANALYZER:

1. Phase 1: Research & Planning
   - Run phase1_research_prompt.py
   - Generate comprehensive linguistic research
   - Output: {language}_grammar_concepts.md

2. Phase 2: Directory Structure & Core Files
   - Run phase2_directory_structure_prompt.py
   - Create complete file structure and basic implementations
   - Output: Full directory structure with core files

3. Phase 3: Domain Components
   - Run phase3_domain_components_prompt.py
   - Create config, prompt_builder, response_parser, validator
   - CRITICAL: Customize AI prompts for the specific language
   - Output: Complete domain layer

4. Phase 4: Infrastructure Components
   - Run phase4_infrastructure_prompt.py
   - Create fallbacks, AI service, circuit breaker
   - Output: Infrastructure layer components

5. Phase 5: Configuration Files
   - Run phase5_configuration_files_prompt.py
   - Create YAML/JSON configuration files
   - Output: All external configuration files

6. Phase 6: Testing & Integration
   - Run phase6_testing_integration_prompt.py
   - Create tests and integrate with registries
   - Output: Test suites and registry updates

7. Phase 7: Documentation & Deployment
   - Run phase7_documentation_deployment_prompt.py
   - Create documentation and deployment materials
   - Output: Production-ready documentation

USAGE EXAMPLE:
For Spanish (es):

1. Run phase1 with LANGUAGE_NAME="Spanish", LANGUAGE_CODE="es"
2. Run phase2 with language_folder="spanish", language_code="es"
3. Run phase3 with Spanish-specific grammatical roles
4. Continue through all phases...

CRITICAL REMINDERS:
- Each language requires customized AI prompts in Phase 3
- Adapt grammatical roles and patterns for each language's unique features
- Test thoroughly at each phase before proceeding
- Follow the French analyzer as the gold standard
- Include the French system prompt as a template in Phase 3

FRENCH SYSTEM PROMPT TEMPLATE (include in Phase 3):

You are an expert linguist specializing in French grammar analysis. Your task is to analyze French sentences and provide detailed grammatical breakdowns that help language learners understand sentence structure.

## ANALYSIS REQUIREMENTS

For each French sentence, provide a word-by-word grammatical analysis with these exact specifications:

### OUTPUT FORMAT
Return a JSON object with exactly this structure:
{{
  "sentence": "the original sentence",
  "words": [
    {{
      "word": "exact word from sentence",
      "grammatical_role": "one of: noun|verb|pronoun|adjective|adverb|determiner|preposition|conjunction|auxiliary_verb|modal_verb|reflexive_pronoun|possessive_pronoun|demonstrative_pronoun|relative_pronoun|indefinite_pronoun|personal_pronoun|interjection|other",
      "individual_meaning": "specific explanation of this word's grammatical function and meaning in the sentence"
    }}
  ],
  "explanations": {{
    "overall_structure": "brief explanation of sentence structure",
    "key_features": "notable French grammatical features"
  }}
}}

[REST OF FRENCH-SPECIFIC PROMPT CONTENT...]

REMEMBER: Each language is unique - customize prompts accordingly!
"""

# Import all phase prompts for easy access
from .phase1_research_prompt import PHASE1_RESEARCH_PROMPT
from .phase2_directory_structure_prompt import PHASE2_DIRECTORY_PROMPT
from .phase3_domain_components_prompt import PHASE3_DOMAIN_COMPONENTS_PROMPT
from .phase4_infrastructure_prompt import PHASE4_INFRASTRUCTURE_PROMPT
from .phase5_configuration_files_prompt import PHASE5_CONFIGURATION_PROMPT
from .phase6_testing_integration_prompt import PHASE6_TESTING_INTEGRATION_PROMPT
from .phase7_documentation_deployment_prompt import PHASE7_DOCUMENTATION_DEPLOYMENT_PROMPT

# Phase execution order
PHASES = [
    ("Research & Planning", PHASE1_RESEARCH_PROMPT, "phase1_research_prompt.py"),
    ("Directory Structure", PHASE2_DIRECTORY_PROMPT, "phase2_directory_structure_prompt.py"),
    ("Domain Components", PHASE3_DOMAIN_COMPONENTS_PROMPT, "phase3_domain_components_prompt.py"),
    ("Infrastructure", PHASE4_INFRASTRUCTURE_PROMPT, "phase4_infrastructure_prompt.py"),
    ("Configuration Files", PHASE5_CONFIGURATION_PROMPT, "phase5_configuration_files_prompt.py"),
    ("Testing & Integration", PHASE6_TESTING_INTEGRATION_PROMPT, "phase6_testing_integration_prompt.py"),
    ("Documentation & Deployment", PHASE7_DOCUMENTATION_DEPLOYMENT_PROMPT, "phase7_documentation_deployment_prompt.py"),
]

def get_phase_prompt(phase_number: int) -> str:
    """Get the prompt for a specific phase."""
    if 1 <= phase_number <= len(PHASES):
        return PHASES[phase_number - 1][1]
    raise ValueError(f"Invalid phase number: {phase_number}")

def list_phases():
    """List all available phases."""
    print("Language Analyzer Creation Phases:")
    for i, (name, _, filename) in enumerate(PHASES, 1):
        print(f"{i}. {name} ({filename})")