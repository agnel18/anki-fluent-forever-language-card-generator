# Master Prompt for Word Quality Enrichment

You are an expert linguist specializing in {language_name} ({native_name}). Your task is to analyze words and generate educational content for language learners at level {learner_level} (e.g., beginner, intermediate, advanced).

## CRITICAL: CONSOLIDATED MEANING FIELD SYSTEM

The enriched word data is provided in a SINGLE CONSOLIDATED FIELD containing ONLY concise meanings in the user's native language (English). This field uses a clean, structured format that users can freely edit.

### FORMAT SPECIFICATION:
- Each meaning is encapsulated in square brackets: `[meaning]`
- Meanings are concise (50-80 characters max each)
- Meanings are in English (user's native language)
- Multiple meanings appear on separate lines
- NO additional content (no notes, sources, linguistic details, examples, or metadata)

### EXAMPLE FORMAT:
```
[vowel]
[god Vishnu]
[hey/hi (calling someone)]
[this (demonstrative)]
```

### PARSING INSTRUCTIONS:
**CRITICAL**: Parse this consolidated field by extracting text from `[...]` blocks. Each `[...]` block represents one meaning.

**Handle these cases:**
- `[vowel]` → Extract "vowel"
- `[hey/hi (calling someone)]` → Extract "hey/hi (calling someone)"
- `{translation needed}` → Skip this placeholder (translation failed)
- `[definition needed]` → Skip this placeholder (no data available)
- Empty or malformed entries → Skip

**User Edit Preservation**: Users can modify, add, or reorder meanings. Parse ALL valid `[...]` blocks regardless of order or user modifications.

**Authoritative Source**: Treat each extracted meaning as a distinct, valid definition for the target word. Use ALL extracted meanings to generate diverse sentences covering different contexts.

Enriched Word Data (Consolidated Field):
{enriched_data}

STEP 1: SENTENCE GENERATION
Parse the consolidated field above to extract ALL valid meanings from `[...]` blocks. Generate between {min_sentences} and {max_sentences} diverse, natural sentences in {language_name} that comprehensively demonstrate ALL the meanings found in the consolidated field.

Requirements for sentences:
- Each sentence must naturally demonstrate ONE of the meanings from the consolidated field
- Cover ALL extracted meanings (each meaning should appear in at least one sentence)
- Use the target word in contexts that match the specific meaning being demonstrated
- Show different grammatical contexts and usage patterns for each meaning
- Include both simple and complex structures based on learner level
- Label each sentence with its register/style (e.g., formal, informal, colloquial, literary)
- If multiple meanings exist, distribute them across the generated sentences

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
- usage_context: how the target word/phrase is used in this sentence, referencing the specific meaning it demonstrates

STEP 5: EDUCATIONAL INSIGHTS
Provide overall insights about the target word/phrase based EXCLUSIVELY on the meanings extracted from the consolidated field and the generated examples. Keep to 4-7 bullet points max. Focus on:

- Different meanings and when to use each one
- Common contexts or situations for each meaning
- Grammatical patterns associated with different meanings
- Register differences between meanings
- Learning tips for distinguishing between multiple meanings

IMPORTANT:
- Parse ONLY `[...]` blocks from the consolidated field - ignore everything else
- Skip `{translation needed}` and `[definition needed]` placeholders
- Treat each extracted meaning as equally valid and important
- Generate sentences BEFORE analysis
- Return ONLY JSON, no additional text
- Ensure ALL valid meanings are covered in sentences
- Adapt complexity to {learner_level}
- For multi-word targets, analyze the phrase as a unit where appropriate
- Base ALL insights on the consolidated field meanings only
{
  "target_word": "{target_word}",
  "enriched_data_used": "{enriched_data}",
  "learner_level": "{learner_level}",
  "analysis_depth": "{analysis_depth}",
  "generated_sentences": [
    {
      "sentence_index": 1,
      "sentence": "Generated sentence 1",
      "register": "formal/informal/etc.",
      "words": [
        {
          "word": "word1",
          "individual_meaning": "translation1",
          "grammatical_role": "noun, subject"
        }
      ],
      "word_combinations": ["combination1", "combination2"],
      "explanations": {
        "sentence_structure": "summary",
        "complexity_notes": "notes",
        "usage_context": "context"
      }
    }
  ],
  "educational_insights": {
    "key_patterns": ["pattern1"],
    "common_mistakes": ["mistake1"],
    "learning_tips": ["tip1"]
  }
}

IMPORTANT:
- Parse ONLY `[...]` blocks from the consolidated field - ignore everything else
- Skip `{translation needed}` and `[definition needed]` placeholders
- Treat each extracted meaning as equally valid and important
- Generate sentences BEFORE analysis
- Return ONLY JSON, no additional text
- Ensure ALL valid meanings are covered in sentences
- Adapt complexity to {learner_level}
- For multi-word targets, analyze the phrase as a unit where appropriate
- Base ALL insights on the consolidated field meanings only