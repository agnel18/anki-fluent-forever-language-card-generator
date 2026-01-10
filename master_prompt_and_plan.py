# Master Prompt with Detailed Phased Plan of Action
# This file combines the improved master prompt template with the comprehensive phased plan
# for implementing the hybrid word data enrichment system.

# IMPROVED MASTER PROMPT TEMPLATE
MASTER_PROMPT_TEMPLATE = """
You are an expert linguist specializing in {language_name} ({native_name}). Your task is to analyze words and generate educational content for language learners at level {learner_level} (e.g., beginner, intermediate, advanced).

FIRST: Use the provided enriched word data to understand the word's context, meanings, and usage patterns.

Enriched Word Data:
{enriched_data}

STEP 1: SENTENCE GENERATION
Using the enriched data above, generate between {min_sentences} and {max_sentences} diverse, natural sentences in {language_name} that demonstrate the target word's (or phrase's) different meanings, usages, and variations. Ensure sentences are natural, varied in complexity appropriate to the learner level, and cover different contexts (formal/informal, everyday situations, etc.). If the target is a multi-word expression, treat it as a unit.

Requirements for sentences:
- Each sentence must use the target word/phrase naturally
- Show different grammatical contexts where possible
- Include both simple and complex structures based on learner level
- Cover the major meanings and usages from the enriched data
- Label each sentence with its register/style (e.g., formal, informal, colloquial, literary)

Generated Sentences:
1. [Sentence 1] ({register1})
2. [Sentence 2] ({register2})
...
{last_sentence_index}. [Sentence {last_sentence_index}] ({register_last})

STEP 2: WORD-BY-WORD ANALYSIS
For EACH generated sentence, provide word-by-word analysis at depth '{analysis_depth}' (light, medium, full). Analyze in the order words appear. For 'light', focus only on content words, auxiliaries, and the target; group function words. For 'medium' or 'full', cover all words.

For each word (or grouped words) in every sentence:
- word: exact word/group as it appears
- individual_meaning: English translation/meaning (MANDATORY)
- grammatical_role: One or more from: {allowed_roles}, or 'functional element', 'discourse marker', etc. (flexible based on language)

STEP 3: WORD COMBINATIONS
Identify 1-3 key meaningful word combinations, phrases, or collocations in each sentence, especially involving the target word/phrase.

STEP 4: EXPLANATIONS
For each sentence, provide:
- sentence_structure: brief grammatical summary
- complexity_notes: notes about structures used, tailored to learner level
- usage_context: how the target word/phrase is used in this sentence

STEP 5: EDUCATIONAL INSIGHTS
Provide overall insights about the target word/phrase based on the enriched data and generated examples. Keep to 4-7 bullet points max.

Return ONLY valid JSON in this format:
{{
  "target_word": "{target_word}",
  "enriched_data_used": "{enriched_data}",
  "learner_level": "{learner_level}",
  "analysis_depth": "{analysis_depth}",
  "generated_sentences": [
    {{
      "sentence_index": 1,
      "sentence": "Generated sentence 1",
      "register": "formal/informal/etc.",
      "words": [
        {{
          "word": "word1",
          "individual_meaning": "translation1",
          "grammatical_role": "noun, subject"
        }}
      ],
      "word_combinations": ["combination1", "combination2"],
      "explanations": {{
        "sentence_structure": "summary",
        "complexity_notes": "notes",
        "usage_context": "context"
      }}
    }}
  ],
  "educational_insights": {{
    "key_patterns": ["pattern1"],
    "common_mistakes": ["mistake1"],
    "learning_tips": ["tip1"]
  }}
}}

IMPORTANT:
- Use the enriched data to ensure accuracy
- Generate sentences BEFORE analysis
- Return ONLY JSON, no additional text
- Ensure major meanings are covered in sentences
- Adapt complexity to {learner_level}
- For multi-word targets, analyze the phrase as a unit where appropriate
"""

# DETAILED PHASED PLAN OF ACTION
# This plan outlines the step-by-step implementation of the hybrid word data enrichment system,
# starting with the word analysis system (fetching + fallbacks), then scaling to 5000 words per language.

## OVERVIEW
# Objective: Enhance AI prompts with enriched word data (meanings, usages, variations) before Step 1 (sentence generation)
# to reduce hallucinations and improve educational quality in the language learning app.
# Scope: 5 languages (Arabic, Chinese Simplified/Traditional, Hindi, Spanish), 5000 words each.
# Approach: Hybrid (programmatic fetching + manual curation), DB-first for common words, fallbacks for custom.
# Timeline: 14 weeks total.
# Success Criteria: 90% DB hit rate, <2s response time, positive user feedback on output quality.

## PHASE 1: SYSTEM DEVELOPMENT (Weeks 1-3)
# 1.1 Build word_data_fetcher.py module
#     - Functions: fetch_from_main_source(word, lang), fetch_from_fallbacks(word, lang), aggregate_data(sources)
#     - Handle APIs: Shabdkosh (Hindi), Almaany (Arabic), MDBG (Chinese), WordReference (Spanish), Wiktionary (universal fallback)
#     - Error handling: Retry logic, timeouts, fallback chains
#     - Output: Dict with meaning, usages (list), variations (list)
# 1.2 Create curation UI (Streamlit page)
#     - Display fetched data for review
#     - Allow approve/reject/edit
#     - Save validated data to DB
# 1.3 Set up DB schema (SQLite/PostgreSQL)
#     - Tables: words (id, word, lang_code, enriched_data JSON, validated bool, last_updated)
#     - Indexes for fast lookups
# 1.4 Test on samples (10 words per language)
#     - Verify fetching, fallbacks, aggregation
#     - Check data quality (accuracy, completeness)
# Deliverables: Fetcher module, curation UI, DB schema, test reports.

## PHASE 2: SYSTEM REFINEMENT AND PILOT (Weeks 4-6)
# 2.1 Pilot with Hindi (100-500 words)
#     - Batch fetch, curate 20-30%, measure success rate (>90%)
#     - Identify issues (e.g., API limits, data conflicts)
# 2.2 Refine system
#     - Add caching (Redis for fetched data)
#     - Improve aggregation (majority vote for conflicts)
#     - Optimize performance (<1s per fetch)
# 2.3 Expand to all 5 languages (sample batches)
#     - Test source compatibility
#     - Update config for language-specific sources
# 2.4 Manual curation guidelines
#     - Rules: Flag inconsistencies, prioritize main sources, add missing usages
# Deliverables: Refined fetcher, pilot data, curation guidelines.

## PHASE 3: DB POPULATION (Weeks 7-12)
# 3.1 Audit and expand word lists
#     - Check existing frequency lists (77 Languages folder)
#     - Add words to reach 5000 per language (use corpora like Leipzig)
# 3.2 Batch population
#     - For each language: Fetch 5000 words, curate incrementally
#     - Parallel processing for speed
#     - Handle gaps (e.g., low-resource words use fallbacks)
# 3.3 Quality assurance
#     - Random sampling: Review 10% of DB entries
#     - Update stale data periodically
# 3.4 Fallback integration
#     - For DB misses: Trigger fetcher, cache result
# Deliverables: Populated DBs (25,000 entries), QA reports.

## PHASE 4: INTEGRATION AND DEPLOYMENT (Weeks 13-14)
# 4.1 Update analyzers
#     - Modify get_batch_grammar_prompt in language analyzers
#     - Add DB lookup + fetcher fallback
#     - Integrate master prompt template
# 4.2 End-to-end testing
#     - Run batches, generate Anki cards
#     - Measure: Hit rate, latency, output quality
# 4.3 Deploy and monitor
#     - Roll out to app
#     - User feedback collection
#     - Maintenance: Update DB quarterly
# Deliverables: Updated app, test results, maintenance plan.

## RESOURCES NEEDED
# - Human: 1 Developer (full-time), 1-2 Curators (part-time)
# - Technical: Python (requests, asyncio), DB (SQLite), APIs (free tiers)
# - Budget: $0-100 (premium APIs if needed)
# - Tools: Git, pytest, Streamlit

## RISKS AND MITIGATIONS
# - API failures: Fallbacks + caching
# - Data quality: Curation + validation rules
# - Performance: Async fetching + DB optimization
# - Scope creep: Stick to 5000 words, defer extras

## NEXT STEPS
# - Start Phase 1: Build fetcher module
# - Pilot with Hindi
# - Iterate based on results

# This plan ensures a robust, scalable system. Ready to begin implementation?