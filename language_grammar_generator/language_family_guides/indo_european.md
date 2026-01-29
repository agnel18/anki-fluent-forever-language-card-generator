# Indo-European Language Family Guide
## Implementation Strategies for IE Languages

**Prerequisites:** Complete [Research Guide](research_guide.md), [Architecture Guide](architecture_guide.md), [Implementation Guide](implementation_guide.md)  
**Purpose:** Language-specific implementation patterns for Indo-European languages  
**Time Estimate:** 2-4 hours per language implementation  
**Scope:** English, Spanish, French, German, Italian, Portuguese, Russian, Hindi, Bengali

## 📚 Family Overview

### Linguistic Characteristics
- **Morphology:** Fusional to agglutinative patterns
- **Syntax:** Subject-Verb-Object (SVO) dominant
- **Word Order:** Relatively fixed compared to other families
- **Case Systems:** Vary from none (English) to complex (German, Russian)
- **Gender Systems:** Grammatical gender in many languages
- **Tense/Aspect:** Rich verbal systems with tense and aspect distinctions

### Common Grammatical Categories
```
Universal IE Categories:
├── Nouns (with case/gender/number)
├── Verbs (tense/aspect/mood/person/number)
├── Adjectives (agreement with nouns)
├── Pronouns (personal/demonstrative/possessive)
├── Prepositions/Postpositions
├── Conjunctions
└── Determiners (articles/definite/indefinite)
```

## 🇬🇧 English Implementation

### Language-Specific Configuration

```python
# languages/english/english_config.py
class EnglishConfig:
    def __init__(self):
        self.language_code = "en"
        self.language_name = "English"

        # English grammatical roles (simplified for educational purposes)
        self.grammatical_roles = {
            # Parts of speech
            'noun': 'noun',
            'verb': 'verb',
            'adjective': 'adjective',
            'adverb': 'adverb',
            'pronoun': 'pronoun',
            'preposition': 'preposition',
            'conjunction': 'conjunction',
            'determiner': 'determiner',
            'interjection': 'interjection',

            # English-specific categories
            'auxiliary_verb': 'auxiliary_verb',
            'modal_verb': 'modal_verb',
            'gerund': 'gerund',
            'infinitive': 'infinitive'
        }

        # Complexity-based color schemes
        self._setup_color_schemes()

    def _setup_color_schemes(self):
        """Setup color schemes for different complexity levels"""

        # Beginner level - basic parts of speech
        self.beginner_colors = {
            'noun': '#FF6B6B',        # Red
            'verb': '#4ECDC4',        # Teal
            'adjective': '#45B7D1',   # Blue
            'adverb': '#FFA07A',      # Light Salmon
            'pronoun': '#98D8C8',     # Mint
            'preposition': '#F7DC6F', # Yellow
            'conjunction': '#BB8FCE', # Light Purple
            'determiner': '#85C1E9'   # Light Blue
        }

        # Intermediate level - adds complexity
        self.intermediate_colors = dict(self.beginner_colors)
        self.intermediate_colors.update({
            'auxiliary_verb': '#F8C471',  # Orange
            'modal_verb': '#82E0AA',      # Light Green
            'gerund': '#F1948A',         # Light Coral
            'infinitive': '#AED6F1'      # Light Sky Blue
        })

        # Advanced level - full grammatical analysis
        self.advanced_colors = dict(self.intermediate_colors)
        self.advanced_colors.update({
            'interjection': '#D7BDE2'  # Light Lavender
        })

    def get_color_scheme(self, complexity):
        """Get color scheme for complexity level"""
        if complexity == 'beginner':
            return self.beginner_colors
        elif complexity == 'intermediate':
            return self.intermediate_colors
        else:  # advanced
            return self.advanced_colors

    def get_grammatical_roles(self, complexity):
        """Get grammatical roles for complexity level"""
        if complexity == 'beginner':
            return {k: v for k, v in self.grammatical_roles.items()
                   if k in ['noun', 'verb', 'adjective', 'adverb', 'pronoun',
                           'preposition', 'conjunction', 'determiner']}
        elif complexity == 'intermediate':
            return {k: v for k, v in self.grammatical_roles.items()
                   if k not in ['interjection']}
        else:  # advanced
            return self.grammatical_roles
```

### English-Specific Prompt Templates

```python
# languages/english/english_prompt_builder.py
class EnglishPromptBuilder:
    def __init__(self):
        self.config = EnglishConfig()
        self.prompt_cache = {}

    def build_single_prompt(self, sentence, target_word, complexity):
        """Build analysis prompt for English sentence"""

        cache_key = self._generate_cache_key(sentence, target_word, complexity)
        if cache_key in self.prompt_cache:
            return self.prompt_cache[cache_key]

        roles = self.config.get_grammatical_roles(complexity)
        roles_list = list(roles.keys())

        target_instruction = ""
        if target_word:
            target_instruction = f"\nSPECIAL FOCUS: Pay particular attention to the word '{target_word}' and its grammatical function."

        prompt = f"""
You are a linguistics expert specializing in English grammar analysis.

TASK: Analyze this English sentence with {complexity} complexity:
"{sentence}"{target_instruction}

GRAMMATICAL CATEGORIES ({complexity} level):
{chr(10).join(f"- {role.replace('_', ' ').title()}: {self._get_role_description(role)}" for role in roles_list)}

REQUIREMENTS:
1. Identify EVERY word's grammatical role using ONLY the categories listed above
2. For each word, provide a clear explanation of its grammatical function
3. Maintain the exact word order from the original sentence
4. Be linguistically precise and educationally helpful
5. Use English terminology consistently

OUTPUT FORMAT:
{{
  "words": [
    {{
      "word": "exact_word_from_sentence",
      "grammatical_role": "exact_category_from_list",
      "meaning": "detailed_grammatical_explanation"
    }}
  ],
  "explanations": {{
    "overall_structure": "comprehensive_sentence_analysis",
    "key_features": "important_grammatical_concepts_demonstrated"
  }}
}}

Analyze the sentence now:"""

        self.prompt_cache[cache_key] = prompt
        return prompt

    def _get_role_description(self, role):
        """Get description for grammatical role"""
        descriptions = {
            'noun': 'person, place, thing, or idea',
            'verb': 'action or state of being',
            'adjective': 'describes or modifies a noun',
            'adverb': 'modifies verb, adjective, or another adverb',
            'pronoun': 'replaces a noun',
            'preposition': 'shows relationship between words',
            'conjunction': 'connects clauses or words',
            'determiner': 'introduces a noun (articles, demonstratives, possessives)',
            'auxiliary_verb': 'helps main verb (be, have, do)',
            'modal_verb': 'expresses possibility, necessity, or permission (can, may, must)',
            'gerund': 'verb form ending in -ing used as a noun',
            'infinitive': 'base verb form with "to" (to eat, to run)',
            'interjection': 'expresses emotion or sudden feeling (wow, oh, hey)'
        }
        return descriptions.get(role, role.replace('_', ' '))

    def _generate_cache_key(self, sentence, target_word, complexity):
        """Generate cache key for prompt"""
        import hashlib
        key_string = f"{sentence}|{target_word or ''}|{complexity}"
        return hashlib.md5(key_string.encode()).hexdigest()
```

### English Response Parser

```python
# languages/english/english_response_parser.py
import json
import re

class EnglishResponseParser:
    def __init__(self):
        self.config = EnglishConfig()

    def parse_response(self, response_text, sentence, complexity):
        """Parse AI response into standardized format with ROBUST JSON EXTRACTION"""

        try:
            # ROBUST JSON EXTRACTION - handles various AI response formats
            json_data = self._extract_json(response_text)
            if not json_data:
                return self._create_fallback_response(sentence, complexity)

            parsed = json_data

            # Validate structure
            if 'words' not in parsed:
                raise ValueError("Missing 'words' array in response")

            # Process word explanations
            word_explanations = []
            colors = self.config.get_color_scheme(complexity)

            for word_info in parsed['words']:
                word = word_info.get('word', '')
                role = word_info.get('grammatical_role', '')
                meaning = word_info.get('meaning', '')

                # Get color for role
                color = colors.get(role, '#808080')  # Default gray

                word_explanations.append((word, role, color, meaning))

            # Process explanations
            explanations = parsed.get('explanations', {})
            overall_structure = explanations.get('overall_structure', '')
            key_features = explanations.get('key_features', '')

            # Calculate confidence (simplified)
            confidence = self._calculate_confidence(word_explanations, sentence)

            return {
                'word_explanations': word_explanations,
                'explanations': {
                    'overall_structure': overall_structure,
                    'key_features': key_features
                },
                'confidence_score': confidence,
                'sentence': sentence,
                'complexity': complexity
            }

        except Exception as e:
            # Fallback parsing for malformed responses
            return self._fallback_parse(response_text, sentence, complexity)

    def _extract_json(self, response_text: str) -> dict:
        """Extract JSON from AI response with robust parsing"""
        try:
            cleaned_response = response_text.strip()

            # Method 1: Direct parsing if starts with JSON
            if cleaned_response.startswith(('{', '[')):
                return json.loads(cleaned_response)

            # Method 2: Extract from markdown code blocks
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', cleaned_response, re.DOTALL | re.IGNORECASE)
            if json_match:
                return json.loads(json_match.group(1))

            # Method 3: Extract JSON between curly braces
            brace_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
            if brace_match:
                return json.loads(brace_match.group(0))

            # Method 4: Try entire response
            return json.loads(cleaned_response)

        except json.JSONDecodeError:
            return None

    def _calculate_confidence(self, word_explanations, sentence):
        """Calculate confidence score for analysis"""

        if not word_explanations:
            return 0.0

        # Check word coverage
        sentence_words = sentence.split()
        analyzed_words = len(word_explanations)
        coverage_ratio = min(analyzed_words / len(sentence_words), 1.0)

        # Check role validity
        valid_roles = set(self.config.get_grammatical_roles('advanced').keys())
        valid_count = sum(1 for _, role, _, _ in word_explanations if role in valid_roles)
        validity_ratio = valid_count / analyzed_words if analyzed_words > 0 else 0

        # Combine metrics
        confidence = (coverage_ratio * 0.6) + (validity_ratio * 0.4)

        return round(confidence, 2)

    def _fallback_parse(self, response_text, sentence, complexity):
        """Fallback parsing for non-JSON responses"""

        # Simple word-by-word analysis
        words = sentence.split()
        colors = self.config.get_color_scheme(complexity)

        word_explanations = []
        for word in words:
            # Basic role assignment (simplified)
            role = self._guess_basic_role(word)
            color = colors.get(role, '#808080')
            meaning = f"Basic analysis: {role.replace('_', ' ')}"

            word_explanations.append((word, role, color, meaning))

        return {
            'word_explanations': word_explanations,
            'explanations': {
                'overall_structure': 'Fallback analysis due to parsing error',
                'key_features': 'Basic word-level analysis performed'
            },
            'confidence_score': 0.3,
            'sentence': sentence,
            'complexity': complexity
        }

    def _guess_basic_role(self, word):
        """Basic role guessing for fallback"""
        word_lower = word.lower().strip('.,!?')

        # Very basic heuristics
        if word_lower in ['the', 'a', 'an', 'this', 'that', 'these', 'those']:
            return 'determiner'
        elif word_lower in ['i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them']:
            return 'pronoun'
        elif word_lower in ['and', 'but', 'or', 'so', 'because', 'although']:
            return 'conjunction'
        elif word_lower in ['in', 'on', 'at', 'to', 'from', 'with', 'by']:
            return 'preposition'
        elif word_lower.endswith('ing'):
            return 'gerund'
        elif word_lower in ['is', 'am', 'are', 'was', 'were', 'be', 'been', 'being']:
            return 'verb'
        else:
            return 'noun'  # Default assumption
```

### English Validator

```python
# languages/english/english_validator.py
class EnglishValidator:
    def __init__(self):
        self.config = EnglishConfig()

    def validate_analysis(self, result):
        """Validate analysis result for English"""

        validation_result = {
            'is_valid': True,
            'issues': [],
            'confidence_score': result.get('confidence_score', 0),
            'quality_metrics': {}
        }

        word_explanations = result.get('word_explanations', [])

        # Check word coverage
        sentence_words = result.get('sentence', '').split()
        if len(word_explanations) != len(sentence_words):
            validation_result['issues'].append({
                'type': 'coverage',
                'severity': 'warning',
                'message': f'Word count mismatch: {len(word_explanations)} analyzed vs {len(sentence_words)} in sentence'
            })

        # Check role validity
        valid_roles = set(self.config.get_grammatical_roles('advanced').keys())
        invalid_roles = []

        for word, role, color, meaning in word_explanations:
            if role not in valid_roles:
                invalid_roles.append(f"'{word}': '{role}'")

        if invalid_roles:
            validation_result['issues'].append({
                'type': 'invalid_roles',
                'severity': 'error',
                'message': f'Invalid grammatical roles: {", ".join(invalid_roles[:3])}'
            })
            validation_result['is_valid'] = False

        # Check for empty meanings
        empty_meanings = [word for word, role, color, meaning in word_explanations if not meaning.strip()]
        if empty_meanings:
            validation_result['issues'].append({
                'type': 'empty_meanings',
                'severity': 'warning',
                'message': f'Words without explanations: {", ".join(empty_meanings[:3])}'
            })

        # Calculate quality metrics
        validation_result['quality_metrics'] = {
            'word_coverage': len(word_explanations) / len(sentence_words) if sentence_words else 0,
            'role_validity': 1 - (len(invalid_roles) / len(word_explanations)) if word_explanations else 0,
            'explanation_completeness': 1 - (len(empty_meanings) / len(word_explanations)) if word_explanations else 0
        }

        # Adjust confidence based on validation
        if not validation_result['is_valid']:
            validation_result['confidence_score'] *= 0.7

        return validation_result
```

### English Analyzer (Main Facade)

```python
# languages/english/english_analyzer.py
from .english_config import EnglishConfig
from .english_prompt_builder import EnglishPromptBuilder
from .english_response_parser import EnglishResponseParser
from .english_validator import EnglishValidator

class EnglishAnalyzer:
    """Main analyzer for English grammar analysis"""

    def __init__(self):
        self.config = EnglishConfig()
        self.prompt_builder = EnglishPromptBuilder()
        self.response_parser = EnglishResponseParser()
        self.validator = EnglishValidator()

        # Initialize AI service (will be injected)
        self.ai_service = None

    def analyze_grammar(self, sentence, target_word, complexity, api_key):
        """Analyze English sentence grammar"""

        try:
            # Build analysis prompt
            prompt = self.prompt_builder.build_single_prompt(sentence, target_word, complexity)

            # Get AI response
            if not self.ai_service:
                from infrastructure.english_ai_service import EnglishAIService
                self.ai_service = EnglishAIService()

            response = self.ai_service.get_analysis(prompt, api_key)

            # Parse response
            result = self.response_parser.parse_response(response, sentence, complexity)

            # Validate result
            validation = self.validator.validate_analysis(result)

            # Update result with validation info
            result['validation'] = validation

            # Adjust confidence based on validation
            if not validation['is_valid']:
                result['confidence_score'] *= 0.8

            return result

        except Exception as e:
            # Return error result
            return {
                'word_explanations': [],
                'explanations': {
                    'overall_structure': f'Analysis failed: {str(e)}',
                    'key_features': 'Error occurred during processing'
                },
                'confidence_score': 0.0,
                'sentence': sentence,
                'complexity': complexity,
                'error': str(e)
            }
```

## 🇪🇸 Spanish Implementation

### Spanish-Specific Features

```python
# languages/spanish/spanish_config.py
class SpanishConfig:
    def __init__(self):
        self.language_code = "es"
        self.language_name = "Spanish"

        # Spanish grammatical roles
        self.grammatical_roles = {
            # Parts of speech
            'noun': 'sustantivo',
            'verb': 'verbo',
            'adjective': 'adjetivo',
            'adverb': 'adverbio',
            'pronoun': 'pronombre',
            'preposition': 'preposición',
            'conjunction': 'conjunción',
            'determiner': 'determinante',
            'interjection': 'interjección',

            # Spanish-specific categories
            'article': 'artículo',
            'reflexive_verb': 'verbo_reflejo',
            'past_participle': 'participio',
            'gerund': 'gerundio',
            'imperative': 'imperativo',
            'subjunctive': 'subjuntivo'
        }

        # Gender and number (important in Spanish)
        self.genders = ['masculine', 'feminine', 'neuter']
        self.numbers = ['singular', 'plural']

        self._setup_color_schemes()

    def _setup_color_schemes(self):
        """Setup color schemes with Spanish-specific colors"""

        # Beginner level
        self.beginner_colors = {
            'sustantivo': '#FF6B6B',      # Red - nouns
            'verbo': '#4ECDC4',          # Teal - verbs
            'adjetivo': '#45B7D1',       # Blue - adjectives
            'adverbio': '#FFA07A',       # Light Salmon - adverbs
            'pronombre': '#98D8C8',      # Mint - pronouns
            'preposición': '#F7DC6F',    # Yellow - prepositions
            'conjunción': '#BB8FCE',     # Light Purple - conjunctions
            'determinante': '#85C1E9',   # Light Blue - determiners
            'artículo': '#AED6F1'        # Light Sky Blue - articles
        }

        # Intermediate level - adds verb forms
        self.intermediate_colors = dict(self.beginner_colors)
        self.intermediate_colors.update({
            'verbo_reflejo': '#F8C471',   # Orange - reflexive verbs
            'participio': '#82E0AA',      # Light Green - past participles
            'gerundio': '#F1948A',       # Light Coral - gerunds
            'imperativo': '#D7BDE2'      # Light Lavender - imperative
        })

        # Advanced level - adds subjunctive
        self.advanced_colors = dict(self.intermediate_colors)
        self.advanced_colors.update({
            'subjuntivo': '#FAD7A0',     # Light Orange - subjunctive
            'interjección': '#D2B4DE'    # Light Purple - interjections
        })
```

### Spanish Verb Conjugation Awareness

```python
# languages/spanish/spanish_prompt_builder.py
class SpanishPromptBuilder:
    def __init__(self):
        self.config = SpanishConfig()

    def build_single_prompt(self, sentence, target_word, complexity):
        """Build Spanish-specific analysis prompt"""

        roles = self.config.get_grammatical_roles(complexity)

        prompt = f"""
Eres un experto lingüista especializado en análisis gramatical del español.

TAREA: Analiza esta oración en español con complejidad {complexity}:
"{sentence}"

CATEGORÍAS GRAMATICALES (nivel {complexity}):
{chr(10).join(f"- {role}: {self._get_spanish_role_description(role)}" for role in roles.keys())}

CONSIDERACIONES ESPECÍFICAS DEL ESPAÑOL:
1. Género y número: Los sustantivos, adjetivos y determinantes deben concordar
2. Verbos: Identificar tiempo, modo, persona y número
3. Artículos: El, la, los, las (determinados); un, una, unos, unas (indeterminados)
4. Verbos reflexivos: Se conjugan con pronombre reflexivo (me, te, se, nos, os, se)
5. Subjuntivo: Aparece en cláusulas subordinadas de duda, emoción, etc.

REQUISITOS:
1. Identificar el rol gramatical de CADA palabra usando SOLO las categorías listadas
2. Explicar la función gramatical en español
3. Mantener el orden exacto de palabras de la oración original
4. Ser lingüísticamente preciso y educativo

FORMATO DE SALIDA:
{{
  "words": [
    {{
      "word": "palabra_exacta_de_la_oración",
      "grammatical_role": "categoría_exacta_de_la_lista",
      "meaning": "explicación_gramatical_detallada_en_español"
    }}
  ],
  "explanations": {{
    "overall_structure": "análisis_completo_de_la_oración",
    "key_features": "conceptos_gramaticales_importantes_demostrados"
  }}
}}

Analiza la oración ahora:"""

        return prompt

    def _get_spanish_role_description(self, role):
        """Get Spanish description for grammatical role"""
        descriptions = {
            'sustantivo': 'persona, lugar, cosa o idea',
            'verbo': 'acción o estado (conjugado en tiempo, modo, persona y número)',
            'adjetivo': 'describe o modifica sustantivos (concuerda en género y número)',
            'adverbio': 'modifica verbos, adjetivos u otros adverbios',
            'pronombre': 'sustituye a un sustantivo',
            'preposición': 'indica relación entre palabras',
            'conjunción': 'une oraciones o palabras',
            'determinante': 'introduce sustantivos (artículos, demostrativos, posesivos)',
            'artículo': 'determinado (el, la, los, las) o indeterminado (un, una, unos, unas)',
            'verbo_reflejo': 'verbo que se conjuga con pronombre reflexivo',
            'participio': 'forma verbal terminada en -ado/-ido, usado en tiempos compuestos',
            'gerundio': 'forma verbal terminada en -ando/-iendo',
            'imperativo': 'forma verbal que expresa mandato o petición',
            'subjuntivo': 'modo verbal que expresa duda, deseo, hipótesis',
            'interjección': 'expresa emoción o sensación repentina'
        }
        return descriptions.get(role, role.replace('_', ' '))
```

## 🇫🇷 French Implementation

### French-Specific Features

```python
# languages/french/french_config.py
class FrenchConfig:
    def __init__(self):
        self.language_code = "fr"
        self.language_name = "French"

        # French grammatical roles
        self.grammatical_roles = {
            # Parts of speech
            'noun': 'nom',
            'verb': 'verbe',
            'adjective': 'adjectif',
            'adverb': 'adverbe',
            'pronoun': 'pronom',
            'preposition': 'préposition',
            'conjunction': 'conjonction',
            'determiner': 'déterminant',
            'interjection': 'interjection',

            # French-specific categories
            'article': 'article',
            'partitive_article': 'article_partitif',
            'reflexive_verb': 'verbe_pronominal',
            'past_participle': 'participe_passé',
            'present_participle': 'participe_présent',
            'imperative': 'impératif',
            'subjunctive': 'subjonctif',
            'conditional': 'conditionnel'
        }

        # French gender and number
        self.genders = ['masculine', 'feminine']
        self.numbers = ['singular', 'plural']

        # Liaison and elision rules
        self.liaison_words = ['les', 'des', 'mes', 'tes', 'ses', 'nos', 'vos', 'leurs']
        self.elision_words = ['le', 'la', 'je', 'me', 'te', 'se', 'ce', 'ne', 'de', 'que']

        self._setup_color_schemes()
```

## 🇩🇪 German Implementation

### German Case System

```python
# languages/german/german_config.py
class GermanConfig:
    def __init__(self):
        self.language_code = "de"
        self.language_name = "German"

        # German grammatical roles with case awareness
        self.grammatical_roles = {
            # Parts of speech
            'noun': 'nomen',
            'verb': 'verb',
            'adjective': 'adjektiv',
            'adverb': 'adverb',
            'pronoun': 'pronomen',
            'preposition': 'präposition',
            'conjunction': 'konjunktion',
            'determiner': 'determinant',
            'interjection': 'interjektion',

            # German-specific categories
            'article': 'artikel',
            'reflexive_verb': 'reflexivverb',
            'separable_prefix': 'trennbares_präfix',
            'inseparable_prefix': 'untrennbares_präfix',
            'past_participle': 'partizip_perfekt',
            'present_participle': 'partizip_präsens',
            'imperative': 'imperativ',
            'subjunctive': 'konjunktiv'
        }

        # German cases (critical for analysis)
        self.cases = ['nominativ', 'akkusativ', 'dativ', 'genitiv']

        # Gender system
        self.genders = ['masculine', 'feminine', 'neuter']

        # Strong/weak adjective inflection
        self.adjective_types = ['strong', 'weak', 'mixed']

        self._setup_color_schemes()
```

## 🇮🇹 Italian Implementation

### Italian Romance Features

```python
# languages/italian/italian_config.py
class ItalianConfig:
    def __init__(self):
        self.language_code = "it"
        self.language_name = "Italian"

        # Italian grammatical roles
        self.grammatical_roles = {
            # Parts of speech
            'noun': 'nome',
            'verb': 'verbo',
            'adjective': 'aggettivo',
            'adverb': 'avverbio',
            'pronoun': 'pronome',
            'preposition': 'preposizione',
            'conjunction': 'congiunzione',
            'determiner': 'determinante',
            'interjection': 'interiezione',

            # Italian-specific categories
            'article': 'articolo',
            'reflexive_verb': 'verbo_riflessivo',
            'past_participle': 'participio_passato',
            'gerund': 'gerundio',
            'imperative': 'imperativo',
            'subjunctive': 'congiuntivo',
            'conditional': 'condizionale',
            'superlative': 'superlativo'
        }

        # Italian gender and number
        self.genders = ['masculine', 'feminine']
        self.numbers = ['singular', 'plural']

        self._setup_color_schemes()
```

## 🇵🇹 Portuguese Implementation

### Portuguese Variants (European vs Brazilian)

```python
# languages/portuguese/portuguese_config.py
class PortugueseConfig:
    def __init__(self, variant="european"):
        self.variant = variant  # "european" or "brazilian"
        self.language_code = "pt"
        self.language_name = "Portuguese"

        # Base grammatical roles
        self.grammatical_roles = {
            # Parts of speech
            'noun': 'substantivo',
            'verb': 'verbo',
            'adjective': 'adjetivo',
            'adverb': 'advérbio',
            'pronoun': 'pronome',
            'preposition': 'preposição',
            'conjunction': 'conjunção',
            'determiner': 'determinante',
            'interjection': 'interjeição',

            # Portuguese-specific categories
            'article': 'artigo',
            'reflexive_verb': 'verbo_reflexivo',
            'past_participle': 'particípio',
            'gerund': 'gerúndio',
            'imperative': 'imperativo',
            'subjunctive': 'conjuntivo',
            'personal_infinitive': 'infinitivo_pessoal'
        }

        # Variant-specific adjustments
        if variant == "brazilian":
            # Brazilian Portuguese features
            self.grammatical_roles.update({
                'object_pronoun': 'pronome_objeto',  # More clitic pronoun usage
                'mesoclisis': 'mesóclise'  # Pronoun placement in future subjunctive
            })

        self._setup_color_schemes()
```

## 🇷🇺 Russian Implementation

### Russian Case System and Aspects

```python
# languages/russian/russian_config.py
class RussianConfig:
    def __init__(self):
        self.language_code = "ru"
        self.language_name = "Russian"

        # Russian grammatical roles with case system
        self.grammatical_roles = {
            # Parts of speech
            'noun': 'существительное',
            'verb': 'глагол',
            'adjective': 'прилагательное',
            'adverb': 'наречие',
            'pronoun': 'местоимение',
            'preposition': 'предлог',
            'conjunction': 'союз',
            'determiner': 'определитель',
            'interjection': 'междометие',

            # Russian-specific categories
            'aspect': 'вид',  # Perfective/imperfective
            'case': 'падеж',  # Nominative, genitive, dative, accusative, instrumental, prepositional
            'reflexive_verb': 'возвратный_глагол',
            'past_participle': 'причастие',
            'gerund': 'деепричастие',
            'imperative': 'повелительное_наклонение',
            'conditional': 'сослагательное_наклонение'
        }

        # Russian cases (6 cases)
        self.cases = [
            'именительный',  # Nominative
            'родительный',   # Genitive
            'дательный',     # Dative
            'винительный',   # Accusative
            'творительный',  # Instrumental
            'предложный'     # Prepositional
        ]

        # Verbal aspects
        self.aspects = ['совершенный', 'несовершенный']  # Perfective, imperfective

        # Gender system
        self.genders = ['masculine', 'feminine', 'neuter']

        self._setup_color_schemes()
```

## 🇮🇳 Hindi Implementation

### Hindi Devanagari Script and Postpositions

```python
# languages/hindi/hindi_config.py
class HindiConfig:
    def __init__(self):
        self.language_code = "hi"
        self.language_name = "Hindi"

        # Hindi grammatical roles
        self.grammatical_roles = {
            # Parts of speech
            'noun': 'संज्ञा',
            'verb': 'क्रिया',
            'adjective': 'विशेषण',
            'adverb': 'क्रियाविशेषण',
            'pronoun': 'सर्वनाम',
            'postposition': 'विभक्ति',  # Hindi uses postpositions instead of prepositions
            'conjunction': 'संयोजक',
            'determiner': 'निर्धारक',
            'interjection': 'विस्मयादिबोधक',

            # Hindi-specific categories
            'gender_marker': 'लिंग_चिह्न',
            'case_marker': 'कारक_चिह्न',
            'aspect_marker': 'क्रियादिश',
            'compound_verb': 'समासिक_क्रिया',
            'participle': 'क्रियापद',
            'infinitive': 'क्रियारूप',
            'honorific': 'सम्मान_सूचक'
        }

        # Hindi cases (through postpositions)
        self.postpositions = [
            'का/की/के',    # Genitive (of)
            'को',          # Dative/Accusative (to)
            'से',          # Instrumental/Ablative (from, by, with)
            'में',         # Locative (in, at)
            'पर',          # Locative (on, upon)
            'ने'           # Ergative (by - for transitive subjects)
        ]

        # Gender and number
        self.genders = ['masculine', 'feminine', 'neuter']
        self.numbers = ['singular', 'plural']

        # Honorific levels
        self.honorifics = ['आप', 'तुम', 'तू']  # Formal, informal, intimate

        self._setup_color_schemes()
```

## 🇧🇩 Bengali Implementation

### Bengali Script and Complex Verb System

```python
# languages/bengali/bengali_config.py
class BengaliConfig:
    def __init__(self):
        self.language_code = "bn"
        self.language_name = "Bengali"

        # Bengali grammatical roles
        self.grammatical_roles = {
            # Parts of speech
            'noun': 'বিশেষ্য',
            'verb': 'ক্রিয়া',
            'adjective': 'বিশেষণ',
            'adverb': 'ক্রিয়া_বিশেষণ',
            'pronoun': 'সর্বনাম',
            'postposition': 'অব্যয়',
            'conjunction': 'সংযোজক',
            'determiner': 'নির্দেশক',
            'interjection': 'আবেগ_সূচক',

            # Bengali-specific categories
            'compound_verb': 'যৌগিক_ক্রিয়া',
            'causative_verb': 'প্রযোজক_ক্রিয়া',
            'participle': 'ক্রিয়াপদ',
            'infinitive': 'অসমাপিকা',
            'classifier': 'পরিমাপক',
            'honorific_verb': 'সম্মান_সূচক_ক্রিয়া',
            'echo_word': 'প্রতিধ্বনি_শব্দ'
        }

        # Complex verb structures
        self.verb_types = [
            'simple_verb',      # Simple verbs
            'compound_verb',    # Verb + auxiliary
            'causative_verb',   # Make someone do something
            'conjunctive_verb', # Verb + verb compounds
            'desiderative_verb' # Want to do something
        ]

        self._setup_color_schemes()
```

## 🛠️ Implementation Template

### Language Implementation Checklist

```python
# Template for implementing a new IE language
class LanguageImplementationTemplate:
    """Template for implementing Indo-European language analyzers"""

    def __init__(self):
        # 1. Language-specific configuration
        self.config = self._create_config()

        # 2. Prompt builder with language-specific rules
        self.prompt_builder = self._create_prompt_builder()

        # 3. Response parser with language validation
        self.response_parser = self._create_response_parser()

        # 4. Validator with language-specific rules
        self.validator = self._create_validator()

        # 5. AI service integration
        self.ai_service = None

    def _create_config(self):
        """Create language-specific configuration"""
        # Implement grammatical roles, color schemes, language rules
        pass

    def _create_prompt_builder(self):
        """Create prompt builder with language-specific templates"""
        # Implement prompt generation with language rules
        pass

    def _create_response_parser(self):
        """Create response parser with language validation"""
        # Implement response parsing and validation
        pass

    def _create_validator(self):
        """Create validator with language-specific rules"""
        # Implement validation logic
        pass

    def analyze_grammar(self, sentence, target_word, complexity, api_key):
        """Main analysis method following facade pattern"""
        # Implement analysis workflow
        pass
```

### Testing Template

```python
# Template for language-specific tests
def test_language_implementation():
    """Test template for new language implementations"""

    # Test sentences for different complexities
    test_cases = {
        'beginner': [
            "Simple sentence.",
            "Basic structure test."
        ],
        'intermediate': [
            "More complex sentence with advanced grammar.",
            "Intermediate level analysis required."
        ],
        'advanced': [
            "Complex sentence requiring deep grammatical analysis.",
            "Advanced linguistic features demonstrated here."
        ]
    }

    analyzer = LanguageAnalyzer()

    for complexity, sentences in test_cases.items():
        for sentence in sentences:
            result = analyzer.analyze_grammar(sentence, "", complexity, "test_key")

            # Validate result structure
            assert 'word_explanations' in result
            assert 'explanations' in result
            assert 'confidence_score' in result
            assert result['confidence_score'] > 0.5

            # Validate word coverage
            words_in_sentence = len(sentence.split())
            words_analyzed = len(result['word_explanations'])
            assert abs(words_in_sentence - words_analyzed) <= 1

    print("✅ All language implementation tests passed")
```

## 📊 Quality Metrics

### Language-Specific Quality Benchmarks

| Language | Target Confidence | Min Coverage | Max Response Time |
|----------|------------------|--------------|-------------------|
| English  | 0.85            | 95%         | 3.0s             |
| Spanish  | 0.82            | 93%         | 3.5s             |
| French   | 0.80            | 92%         | 4.0s             |
| German   | 0.78            | 90%         | 4.5s             |
| Italian  | 0.82            | 93%         | 3.5s             |
| Portuguese| 0.81           | 92%         | 3.8s             |
| Russian  | 0.75            | 88%         | 5.0s             |
| Hindi    | 0.72            | 85%         | 5.5s             |
| Bengali  | 0.70            | 83%         | 6.0s             |

### Implementation Priority

1. **High Priority**: English, Spanish, French (widely used, simpler grammar)
2. **Medium Priority**: German, Italian, Portuguese (complex but Romance language patterns)
3. **Lower Priority**: Russian, Hindi, Bengali (very complex grammar systems)

## 🚀 Getting Started

### Quick Implementation for New IE Language

1. **Copy English template** as starting point
2. **Update configuration** with language-specific roles and colors
3. **Modify prompts** for language-specific grammar rules
4. **Adjust parser** for language-specific response validation
5. **Test extensively** with native speaker validation
6. **Tune AI models** for optimal performance

### Recommended Development Order

```
1. English (baseline implementation)
2. Spanish (similar Romance structure)
3. French (additional complexity)
4. German (case system introduction)
5. Italian/Portuguese (Romance variations)
6. Russian (Cyrillic, complex cases)
7. Hindi/Bengali (Devanagari, postpositions)
```

---

**🎯 Next Steps**: Choose your first language to implement. Start with English for the complete working example, then Spanish for Romance language patterns.

**📚 Resources**: Each language section includes complete code examples. Use the implementation template for consistent structure across all IE languages.

**🔧 Customization**: Adapt the configurations and prompts based on your specific linguistic requirements and target audience complexity levels.</content>
<parameter name="filePath">d:\Language Learning\LanguagLearning\language_grammar_generator\language_family_guides\indo_european.md