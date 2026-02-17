# Language Analyzer Creation Prompts

This directory contains AI prompts for creating complete language analyzers following the Clean Architecture pattern established by the French analyzer.

## Directory Structure

```
language_grammar_generator/
├── phase1_research_prompt.py           # Research and planning
├── phase2_directory_structure_prompt.py # Directory structure and core files
├── phase3_domain_components_prompt.py   # Domain layer (config, prompts, parsing)
├── phase4_infrastructure_prompt.py      # Infrastructure layer (AI service, fallbacks)
├── phase5_configuration_files_prompt.py # YAML/JSON configuration files
├── phase6_testing_integration_prompt.py # Tests and registry integration
├── phase7_documentation_deployment_prompt.py # Documentation and deployment
└── language_analyzer_creation_guide.py  # Master guide and utilities
```

## Usage Workflow

### For Each New Language:

1. **Phase 1: Research & Planning**
   - Run the research prompt to understand the language
   - Generate linguistic analysis and implementation roadmap
   - Output: Comprehensive research document

2. **Phase 2: Directory Structure**
   - Create complete file structure following Clean Architecture
   - Generate main analyzer facade and basic components
   - Output: Full directory with core files

3. **Phase 3: Domain Components** ⭐ **MOST IMPORTANT**
   - Create config, prompt_builder, response_parser, validator
   - **CRITICAL**: Customize AI prompts for the specific language
   - Include language-specific grammatical roles and analysis patterns
   - Output: Complete domain layer with customized prompts

4. **Phase 4: Infrastructure**
   - Implement AI service integration and circuit breaker patterns
   - Create fallback systems for error recovery
   - Output: Production-ready infrastructure components

5. **Phase 5: Configuration Files**
   - Generate YAML/JSON files with language-specific data
   - Include grammatical roles, word meanings, patterns
   - Output: All external configuration files

6. **Phase 6: Testing & Integration**
   - Create comprehensive test suites
   - Integrate with language registries
   - Add sentence generation support
   - Output: Test suites and registry updates

7. **Phase 7: Documentation & Deployment**
   - Generate documentation and deployment materials
   - Create production readiness checklists
   - Output: Complete deployment package

## Critical Customization Points

### Phase 3: Domain Components (Most Critical)

Each language requires customized AI prompts. Use the French system prompt as a template and adapt for each language's specific features:

**French Example:**
- Grammatical roles: noun, verb, auxiliary_verb, personal_pronoun, reflexive_pronoun, etc.
- Features: gender agreement, elision, complex prepositions
- Verb conjugations: person/number/tense recognition

**Adapt for each language:**
- Define language-specific grammatical roles
- Include unique morphological features
- Specify agreement patterns (gender, case, number, etc.)
- Add script-specific considerations

### Language-Specific Variables

When running each prompt, replace these variables:

- `{LANGUAGE_NAME}`: Full language name (e.g., "Spanish", "German")
- `{LANGUAGE_CODE}`: ISO language code (e.g., "es", "de")
- `{LANGUAGE_FAMILY}`: Linguistic family (e.g., "Romance", "Germanic")
- `{SCRIPT_TYPE}`: Writing system (e.g., "alphabetic", "logographic")
- `{WORD_ORDER}`: Typical word order (e.g., "SVO", "SOV")
- `{language_folder}`: Directory name (e.g., "spanish", "german")
- `{language_code}`: Same as LANGUAGE_CODE

## Quality Standards

### Must Follow:
- ✅ Clean Architecture principles
- ✅ French analyzer as gold standard
- ✅ Prevention-at-source patterns
- ✅ No artificial confidence boosting
- ✅ Comprehensive error handling
- ✅ External configuration files
- ✅ Three complexity levels (beginner/intermediate/advanced)

### Language-Specific Requirements:
- ✅ Customized AI prompts for grammar analysis
- ✅ Language-appropriate grammatical roles
- ✅ Script-specific text processing
- ✅ Cultural/linguistic feature support
- ✅ Proper fallback patterns

## Example: Creating Spanish Analyzer

```bash
# Phase 1: Research
python -c "from phase1_research_prompt import PHASE1_RESEARCH_PROMPT; print(PHASE1_RESEARCH_PROMPT.format(LANGUAGE_NAME='Spanish', LANGUAGE_CODE='es', LANGUAGE_FAMILY='Romance', SCRIPT_TYPE='alphabetic', WORD_ORDER='SVO'))"

# Phase 2: Structure
python -c "from phase2_directory_structure_prompt import PHASE2_DIRECTORY_PROMPT; print(PHASE2_DIRECTORY_PROMPT.format(LANGUAGE_NAME='Spanish', LANGUAGE_CODE='es', language_folder='spanish', language_code='es'))"

# Phase 3: Domain (with Spanish-specific customizations)
# ... customize AI prompt for Spanish grammar ...

# Continue through all phases...
```

## French System Prompt Template

Include this in Phase 3 and adapt for each language:

```
You are an expert linguist specializing in [LANGUAGE] grammar analysis. Your task is to analyze [LANGUAGE] sentences and provide detailed grammatical breakdowns that help language learners understand sentence structure.

## ANALYSIS REQUIREMENTS

For each [LANGUAGE] sentence, provide a word-by-word grammatical analysis with these exact specifications:

### OUTPUT FORMAT
Return a JSON object with exactly this structure:
{{
  "sentence": "the original sentence",
  "words": [
    {{
      "word": "exact word from sentence",
      "grammatical_role": "one of: [LIST LANGUAGE-SPECIFIC ROLES HERE]",
      "individual_meaning": "specific explanation of this word's grammatical function and meaning in the sentence"
    }}
  ],
  "explanations": {{
    "overall_structure": "brief explanation of sentence structure",
    "key_features": "notable [LANGUAGE] grammatical features"
  }}
}}

[ADAPT REMAINING SECTIONS FOR THE SPECIFIC LANGUAGE]
```

## Success Criteria

- [ ] All 7 phases completed successfully
- [ ] Language analyzer integrates with existing registries
- [ ] Grammar analysis produces specific, contextual explanations
- [ ] Sentence generation respects character limits
- [ ] All tests pass without artificial confidence boosting
- [ ] Clean Architecture principles maintained
- [ ] Production-ready documentation provided

Remember: **Each language is unique** - thoroughly customize the AI prompts and configuration for each language's specific grammatical features and learner needs.