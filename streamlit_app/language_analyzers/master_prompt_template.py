# Improved Master Prompt Template for Language Analysis with Enriched Word Data
# This template incorporates word meanings, usages, and variations before sentence generation
# to improve AI output quality and reduce hallucinations.
# Improvements: Reduced output length by limiting sentences (3-7), added difficulty scaling, 
# allowed more flexible grammatical roles, separated generation from deep analysis where possible,
# added handling for multi-word targets, included register/style labels, and made analysis tunable.

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
