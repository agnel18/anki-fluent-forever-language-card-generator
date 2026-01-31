import sys
sys.path.append('.')
import json
import warnings

# Suppress FutureWarnings (including google.generativeai deprecation)
warnings.filterwarnings("ignore", category=FutureWarning)

import google.generativeai as genai
from shared_utils import get_gemini_model

# Test the generic grammar analysis prompt with Arabic
sentence = 'الكلب في الحديقة'
word = 'في'

# Configure Gemini
genai.configure(api_key='AIzaSyCGUy...uzWXORse0U')  # Using the key from logs

prompt = f'''You are a linguistics expert specializing in Arabic grammar analysis for language learners.

TASK: Analyze this Arabic sentence and provide grammatical coloring information.

SENTENCE: "{sentence}"
TARGET WORD: "{word}"

INSTRUCTIONS:
1. Break down the sentence into individual words/tokens
2. For each word, identify its part of speech (POS) category
3. Assign an appropriate color based on POS
4. Provide a brief explanation for each word's grammatical role

COLOR CATEGORIES (use these exact names):
- noun (red): people, places, things, ideas
- verb (teal): actions, states, occurrences
- adjective (blue): descriptions of nouns
- adverb (green): modify verbs, adjectives, other adverbs
- pronoun (yellow): replace nouns (he, she, it, they, etc.)
- preposition (plum): show relationships (in, on, at, with, etc.)
- conjunction (mint): connect clauses (and, but, or, because, etc.)
- article (light yellow): determiners (the, a, an)
- interjection (light red): exclamations (oh, wow, hey)
- other (gray): numbers, punctuation, unclassified words

OUTPUT FORMAT: Return ONLY a valid JSON object with this exact structure:
{{
  "colored_sentence": "<span style='color: #COLOR1'>word1</span> <span style='color: #COLOR2'>word2</span> ...",
  "word_explanations": [
    ["word1", "pos_category", "#COLOR1", "brief explanation of grammatical role"],
    ["word2", "pos_category", "#COLOR2", "brief explanation of grammatical role"],
    ...
  ],
  "grammar_summary": "Brief summary of the sentence's grammatical structure"
}}

IMPORTANT:
- Return ONLY valid JSON, no extra text
- Use the exact color codes from the categories above
- Ensure the colored_sentence contains the original sentence with proper HTML span tags
- Each word_explanations entry must have exactly 4 elements: [word, pos, color, explanation]'''

try:
    model = genai.GenerativeModel(get_gemini_model())
    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=0.3,
            max_output_tokens=1500,
        )
    )

    response_text = response.text.strip()
    print(f'Response length: {len(response_text)}')
    print(f'Response: {repr(response_text)}')

    if response_text:
        try:
            result = json.loads(response_text)
            print('JSON parsed successfully')
            print(f'Keys: {list(result.keys())}')
        except json.JSONDecodeError as e:
            print(f'JSON parse error: {e}')
    else:
        print('Empty response')

except Exception as e:
    print(f'Error: {e}')