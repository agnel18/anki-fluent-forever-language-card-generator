# languages/LANGUAGE_PLACEHOLDER/LANGUAGE_PLACEHOLDER_config.py
"""
Language-specific configuration for LANGUAGE_NAME_PLACEHOLDER analyzer.
Defines grammatical roles, color schemes, and language rules.
"""

class LanguageConfig:
    """
    Configuration class for LANGUAGE_NAME_PLACEHOLDER grammatical analysis.

    Defines:
    - Grammatical roles and categories
    - Color schemes for different complexity levels
    - Language-specific rules and constraints
    """

    def __init__(self):
        # Basic language information
        self.language_code = "LANG_CODE_PLACEHOLDER"  # ISO language code
        self.language_name = "LANGUAGE_NAME_PLACEHOLDER"   # Full language name

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

        # Role hierarchy and complexity filtering (Arabic Analyzer Innovation)
        self.role_hierarchy = self._create_role_hierarchy()
        self.complexity_role_filters = self._create_complexity_filters()

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
        """Get grammatical roles for complexity level with hierarchy filtering"""
        all_roles = self.grammatical_roles

        if complexity == 'advanced':
            return all_roles

        # Use complexity filtering with role hierarchy (Arabic Analyzer Innovation)
        filtered_roles = {}
        for role_key, display_name in all_roles.items():
            if self.should_show_role(role_key, complexity):
                filtered_roles[role_key] = display_name

        return filtered_roles

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
        """Get color for grammatical role with hierarchy inheritance"""
        colors = self.get_color_scheme(complexity)

        # First try direct role match
        if role in colors:
            return colors[role]

        # Try parent role for color inheritance (Arabic Analyzer Innovation)
        parent_role = self.get_parent_role(role)
        if parent_role in colors:
            return colors[parent_role]

        # Default fallback
        return '#808080'  # Default gray

    def _create_role_hierarchy(self) -> Dict[str, str]:
        """
        Create role hierarchy mapping for color inheritance (Arabic Analyzer Innovation)
        
        Maps specific grammatical roles to their parent categories for:
        - Color inheritance: Specific roles use parent colors for visual consistency
        - Complexity filtering: Parent roles shown when specific roles are too advanced
        - Educational progression: General → Specific as learner advances
        """
        return {
            # Verb subtypes inherit verb color
            'perfect_verb': 'verb',
            'imperfect_verb': 'verb',
            'imperative_verb': 'verb',
            'active_participle': 'verb',
            'passive_participle': 'verb',
            'reflexive_verb': 'verb',
            'auxiliary_verb': 'verb',
            'modal_verb': 'verb',
            'gerund': 'verb',
            'infinitive': 'verb',
            
            # Noun subtypes inherit noun color
            'proper_noun': 'noun',
            'common_noun': 'noun',
            'abstract_noun': 'noun',
            'concrete_noun': 'noun',
            'countable_noun': 'noun',
            'uncountable_noun': 'noun',
            'compound_noun': 'noun',
            
            # Adjective subtypes inherit adjective color
            'comparative_adjective': 'adjective',
            'superlative_adjective': 'adjective',
            'possessive_adjective': 'adjective',
            
            # Adverb subtypes inherit adverb color
            'manner_adverb': 'adverb',
            'place_adverb': 'adverb',
            'time_adverb': 'adverb',
            'degree_adverb': 'adverb',
            
            # Pronoun subtypes inherit pronoun color
            'personal_pronoun': 'pronoun',
            'demonstrative_pronoun': 'pronoun',
            'interrogative_pronoun': 'pronoun',
            'relative_pronoun': 'pronoun',
            'indefinite_pronoun': 'pronoun',
            
            # Preposition subtypes inherit preposition color
            'simple_preposition': 'preposition',
            'compound_preposition': 'preposition',
            
            # Conjunction subtypes inherit conjunction color
            'coordinating_conjunction': 'conjunction',
            'subordinating_conjunction': 'conjunction',
            
            # Determiner subtypes inherit determiner color
            'definite_article': 'determiner',
            'indefinite_article': 'determiner',
            'demonstrative_determiner': 'determiner',
            'possessive_determiner': 'determiner',
            
            # Language-specific morphological features
            'classifier': 'other',
            'aspect_marker': 'other',
            'structural_particle': 'other',
            'discourse_particle': 'other',
            'case_marker': 'other',
            'tense_marker': 'other',
            'mood_marker': 'other',
            'number_marker': 'other',
            'gender_marker': 'other'
        }

    def _create_complexity_filters(self) -> Dict[str, set]:
        """
        Create complexity-based role filtering (Arabic Analyzer Innovation)
        
        Defines which grammatical roles are appropriate for each complexity level:
        - beginner: Basic parts of speech only
        - intermediate: Common specific roles added
        - advanced: All morphological and language-specific features
        """
        return {
            'beginner': {
                'noun', 'verb', 'adjective', 'adverb', 'pronoun', 
                'preposition', 'conjunction', 'determiner', 'interjection'
            },
            'intermediate': {
                # Basic roles
                'noun', 'verb', 'adjective', 'adverb', 'pronoun',
                'preposition', 'conjunction', 'determiner', 'interjection',
                # Common specific roles
                'perfect_verb', 'imperfect_verb', 'active_participle', 'passive_participle',
                'reflexive_verb', 'auxiliary_verb', 'modal_verb',
                'comparative_adjective', 'superlative_adjective',
                'personal_pronoun', 'demonstrative_pronoun', 'interrogative_pronoun',
                'definite_article', 'indefinite_article',
                'coordinating_conjunction', 'subordinating_conjunction'
            },
            'advanced': set()  # Allow all roles for advanced learners
        }

    def should_show_role(self, role: str, complexity: str) -> bool:
        """
        Check if a grammatical role should be displayed at given complexity level
        
        Logic:
        - Advanced: Show all roles
        - Other levels: Show role if directly allowed OR if its parent role is allowed
        - This enables progressive disclosure while maintaining color consistency
        """
        if complexity == 'advanced':
            return True
        
        allowed_roles = self.complexity_role_filters.get(complexity, set())
        return role in allowed_roles or self.get_parent_role(role) in allowed_roles

    def get_parent_role(self, role: str) -> str:
        """
        Get the parent role for color inheritance and complexity filtering
        
        Returns the parent category for specific grammatical roles.
        Used for:
        - Color inheritance: Specific roles use parent colors
        - Complexity filtering: Parent roles shown when specific roles are too advanced
        """
        return self._create_role_hierarchy().get(role, role)

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