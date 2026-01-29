# languages/{language}/{language}_config.py
"""
Language-specific configuration for {Language} analyzer.
Defines grammatical roles, color schemes, and language rules.
"""

class LanguageConfig:
    """
    Configuration class for {Language} grammatical analysis.

    Defines:
    - Grammatical roles and categories
    - Color schemes for different complexity levels
    - Language-specific rules and constraints
    """

    def __init__(self):
        # Basic language information
        self.language_code = "{lang_code}"  # ISO language code
        self.language_name = "{Language}"   # Full language name

        # Core grammatical roles (CUSTOMIZE THIS)
        self.grammatical_roles = {{
            # Universal categories (present in most languages)
            'noun': '{noun_term}',
            'verb': '{verb_term}',
            'adjective': '{adjective_term}',
            'adverb': '{adverb_term}',
            'pronoun': '{pronoun_term}',
            'preposition': '{preposition_term}',  # or 'postposition'
            'conjunction': '{conjunction_term}',
            'determiner': '{determiner_term}',
            'interjection': '{interjection_term}',

            # Language-specific categories (ADD AS NEEDED)
            # Examples for different language families:

            # Romance languages
            'reflexive_verb': 'verbo_reflejo',
            'past_participle': 'participio_pasado',
            'gerund': 'gerundio',
            'imperative': 'imperativo',
            'subjunctive': 'subjuntivo',

            # Germanic languages
            'auxiliary_verb': 'Hilfsverb',
            'separable_prefix': 'trennbares_Präfix',
            'inseparable_prefix': 'untrennbares_Präfix',
            'strong_verb': 'starkes_Verb',

            # Slavic languages
            'aspect': 'вид',  # Perfective/imperfective
            'case': 'падеж',  # Nominative, genitive, etc.
            'reflexive_verb': 'возвратный_глагол',

            # Sino-Tibetan languages
            'classifier': '量词',
            'aspect_marker': '体标记',
            'structural_particle': '结构助词',
            'discourse_particle': '语篇助词',

            # Afroasiatic languages
            'root': 'جذر',  # Root morpheme
            'pattern': 'وزن',  # Morphological pattern
            'ablaut': 'إعلال',  # Vowel change
        }}

        # Language-specific attributes (CUSTOMIZE)
        self.genders = ['masculine', 'feminine']  # Add 'neuter' if applicable
        self.numbers = ['singular', 'plural']
        self.cases = []  # Add cases if applicable: ['nominative', 'accusative', 'dative', 'genitive']
        self.aspects = []  # Add aspects if applicable: ['perfective', 'imperfective']
        self.moods = []  # Add moods if applicable: ['indicative', 'subjunctive', 'imperative']
        self.tenses = []  # Add tenses if applicable

        # Word order pattern (CUSTOMIZE)
        self.word_order = "{SVO}"  # SVO, SOV, VSO, etc.

        # Special characters or scripts (CUSTOMIZE)
        self.has_diacritics = {False}  # True for languages with accents/diacritics
        self.script_type = "latin"  # latin, cyrillic, arabic, devanagari, han, etc.
        self.special_characters = []  # List of special characters used

        self._setup_color_schemes()

    def _setup_color_schemes(self):
        """Setup color schemes for different complexity levels"""

        # Beginner level - basic parts of speech (8-10 categories)
        self.beginner_colors = {{
            # Core categories - use distinct, accessible colors
            '{noun_term}': '#FF6B6B',        # Red - nouns
            '{verb_term}': '#4ECDC4',        # Teal - verbs
            '{adjective_term}': '#45B7D1',   # Blue - adjectives
            '{adverb_term}': '#FFA07A',      # Light Salmon - adverbs
            '{pronoun_term}': '#98D8C8',     # Mint - pronouns
            '{preposition_term}': '#F7DC6F', # Yellow - prepositions
            '{conjunction_term}': '#BB8FCE', # Light Purple - conjunctions
            '{determiner_term}': '#85C1E9'   # Light Blue - determiners
        }}

        # Intermediate level - adds grammatical complexity (12-15 categories)
        self.intermediate_colors = dict(self.beginner_colors)
        self.intermediate_colors.update({{
            # Add intermediate-level categories
            'reflexive_verb': '#F8C471',     # Orange
            'auxiliary_verb': '#82E0AA',     # Light Green
            'past_participle': '#F1948A',    # Light Coral
            'gerund': '#D7BDE2',            # Light Lavender
            'imperative': '#AED6F1',         # Light Sky Blue
            'subjunctive': '#FAD7A0',        # Light Orange
        }})

        # Advanced level - full grammatical analysis (15+ categories)
        self.advanced_colors = dict(self.intermediate_colors)
        self.advanced_colors.update({{
            # Add advanced categories
            'aspect': '#E8DAEF',             # Very Light Purple
            'case': '#D5DBDB',               # Light Gray
            'classifier': '#FCF3CF',         # Very Light Yellow
            'aspect_marker': '#D1F2EB',      # Very Light Teal
            'structural_particle': '#FDEDEC', # Very Light Red
            'discourse_particle': '#F2F3F4',  # Very Light Gray
            '{interjection_term}': '#D7BDE2' # Light Lavender
        }})

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
        all_roles = self.grammatical_roles

        if complexity == 'beginner':
            # Return only basic roles for beginners
            basic_keys = ['noun', 'verb', 'adjective', 'adverb', 'pronoun',
                         'preposition', 'conjunction', 'determiner']
            return {{k: v for k, v in all_roles.items() if k in basic_keys}}

        elif complexity == 'intermediate':
            # Exclude most advanced roles
            exclude_keys = ['interjection', 'aspect', 'case', 'classifier',
                           'aspect_marker', 'structural_particle', 'discourse_particle']
            return {{k: v for k, v in all_roles.items() if k not in exclude_keys}}

        else:  # advanced
            return all_roles

    def get_language_specific_rules(self):
        """Get language-specific grammatical rules"""
        rules = {{
            'word_order': self.word_order,
            'gender_system': self.genders,
            'number_system': self.numbers,
            'script_type': self.script_type,
            'has_diacritics': self.has_diacritics,
        }}

        # Add optional systems
        if self.cases:
            rules['case_system'] = self.cases
        if self.aspects:
            rules['aspect_system'] = self.aspects
        if self.moods:
            rules['mood_system'] = self.moods
        if self.tenses:
            rules['tense_system'] = self.tenses
        if self.special_characters:
            rules['special_characters'] = self.special_characters

        return rules

    def validate_grammatical_role(self, role, complexity):
        """Validate if a grammatical role is valid for given complexity"""
        valid_roles = set(self.get_grammatical_roles(complexity).keys())
        return role in valid_roles

    def get_role_display_name(self, role_key, complexity='advanced'):
        """Get display name for grammatical role"""
        roles = self.get_grammatical_roles(complexity)
        return roles.get(role_key, role_key.replace('_', ' ').title())

    def get_color_for_role(self, role, complexity):
        """Get color for grammatical role"""
        colors = self.get_color_scheme(complexity)
        return colors.get(role, '#808080')  # Default gray

    def get_complexity_requirements(self):
        """Get requirements for each complexity level"""
        return {{
            'beginner': {{
                'max_sentence_length': 15,  # words
                'required_roles': ['noun', 'verb', 'adjective', 'adverb', 'pronoun'],
                'excluded_features': ['subjunctive', 'aspect', 'case', 'classifier']
            }},
            'intermediate': {{
                'max_sentence_length': 25,
                'required_roles': ['noun', 'verb', 'adjective', 'adverb', 'pronoun',
                                 'preposition', 'conjunction', 'determiner'],
                'excluded_features': ['complex_aspect', 'rare_cases']
            }},
            'advanced': {{
                'max_sentence_length': 50,
                'required_roles': list(self.grammatical_roles.keys()),
                'excluded_features': []  # All features included
            }}
        }}