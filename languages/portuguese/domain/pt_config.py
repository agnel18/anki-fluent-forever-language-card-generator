# languages/portuguese/domain/pt_config.py
"""
Portuguese Configuration — Domain Component

Portuguese (Português) is an Indo-European Romance language (Western Romance,
Ibero-Romance). This analyzer covers both Brazilian (BR) and European (PT)
varieties as a single unit with register tagging.

Distinctive Portuguese features encoded in this config:
  - Three-state clitic placement (proclitic / enclitic / mesoclitic)
  - Personal infinitive (inflected non-finite form unique among Romance)
  - Productive future subjunctive (largely lost elsewhere in Romance)
  - Ser / estar copula split (grammaticalized contrast)
  - Obligatory contraction of preposition + article/demonstrative/pronoun
    (do, no, ao, pelo, dele, naquele, daquilo, ...)
  - Object clitic phonological allomorphs (-lo / -no after -r/-s/-z and nasals)
  - Debitive 'ter de / ter que + infinitive'
  - BR/PT register divergences (você+gerund vs tu+enclisis+'estar a'+inf)

Color scheme is intentionally rich so that grammar_processor.py
(_convert_analyzer_output_to_explanations) can pass the Portuguese-specific
roles through with their distinct colors — copula, contraction,
personal_infinitive, mesoclitic, clitic_pronoun, gerund, past_participle,
subjunctive_marker each get a unique hex color (NOT collapsed into the
generic verb / pronoun categories).
"""

import json
import logging
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class PtConfig:
    """
    Configuration for Portuguese grammar analysis.
    Follows Clean Architecture pattern with external configuration files
    (loaded from infrastructure/data/) and graceful in-code fallbacks.
    """

    def __init__(self):
        self.language_code = "pt"
        self.language_name = "Portuguese"
        self.language_name_native = "Português"

        # Portuguese is LTR
        self.is_rtl = False
        self.text_direction = "ltr"

        # Script properties
        self.script_type = "alphabetic"

        # Load external configuration files (graceful fallbacks)
        config_dir = Path(__file__).parent.parent / "infrastructure" / "data"
        self.grammatical_roles = (
            self._load_yaml(config_dir / "pt_grammatical_roles.yaml")
            or self._get_default_roles()
        )
        self.patterns = self._load_yaml(config_dir / "pt_patterns.yaml") or {}
        self.word_meanings = (
            self._load_json(config_dir / "pt_word_meanings.json") or {}
        )
        self.contractions = (
            self._load_yaml(config_dir / "pt_contractions.yaml")
            or self._get_default_contractions()
        )
        self.verb_conjugations = (
            self._load_yaml(config_dir / "pt_verb_conjugations.yaml") or {}
        )
        self.preposition_patterns = (
            self._load_yaml(config_dir / "pt_preposition_patterns.yaml") or {}
        )

        # Voice configuration for Google Cloud Text-to-Speech
        self.voice_config = {
            "language_code": "pt-BR",  # Default to Brazilian (larger speaker base)
            "name": "pt-BR-Neural2-A",
            "ssml_gender": "FEMALE",
            "speaking_rate": 0.95,
            "pitch": 0.0,
        }

        # Color schemes for each complexity level
        self.color_schemes = self._load_color_schemes()

        # Linguistic feature flags
        self.linguistic_features = {
            "grammatical_gender": True,        # masculine / feminine
            "fusional_morphology": True,
            "ser_estar_split": True,           # two copulas with semantic contrast
            "personal_infinitive": True,       # inflected infinitive
            "future_subjunctive": True,
            "three_state_clitics": True,       # proclisis / enclisis / mesoclisis
            "obligatory_contractions": True,   # do, no, ao, pelo, dele, ...
            "clitic_allomorphs": True,         # -lo / -no after r/s/z / nasal
            "debitive_construction": True,     # ter de / ter que
            "br_pt_register_split": True,
            "pro_drop": True,
        }

        # Portuguese genders
        self.genders = ["masculine", "feminine"]

        # Three-way demonstrative deixis
        self.demonstrative_deixis = ["proximal", "medial", "distal"]

        # Clitic placement positions (Portuguese-specific three-state)
        self.clitic_positions = ["proclitic", "enclitic", "mesoclitic"]

        # Register variants
        self.registers = ["BR", "PT", "neutral"]

    # ------------------------------------------------------------------
    # Default grammatical roles (3-tier complexity, per pt_grammar_concepts.md)
    # ------------------------------------------------------------------

    def _get_default_roles(self) -> Dict[str, Any]:
        """
        Default grammatical roles for Portuguese, organized by complexity.
        These role labels are passed through grammar_processor.py UNCHANGED,
        preserving the language-specific color mappings.
        """
        beginner = {
            "noun": "noun (substantivo)",
            "verb": "verb (verbo)",
            "adjective": "adjective (adjetivo)",
            "pronoun": "pronoun (pronome)",
            "preposition": "preposition (preposição)",
            "conjunction": "conjunction (conjunção)",
            "adverb": "adverb (advérbio)",
            "article": "article (artigo)",
            "numeral": "numeral (numeral)",
        }
        intermediate = {
            **beginner,
            "personal_pronoun": "personal pronoun (pronome pessoal)",
            "possessive_pronoun": "possessive pronoun (pronome possessivo)",
            "demonstrative_pronoun": "demonstrative pronoun (pronome demonstrativo)",
            "reflexive_pronoun": "reflexive pronoun (pronome reflexivo)",
            "definite_article": "definite article (artigo definido)",
            "indefinite_article": "indefinite article (artigo indefinido)",
            "contraction": "contraction (contração — preposition + article/pronoun)",
            "auxiliary_verb": "auxiliary verb (verbo auxiliar — ter, haver, ir, estar)",
            "copula": "copula (cópula — ser / estar)",
            "modal_verb": "modal verb (verbo modal — poder, dever, querer, saber)",
            "particle": "particle (partícula — não, sim, cá, lá, pois)",
            "pronominal_verb": "pronominal verb (verbo pronominal — lembrar-se, queixar-se)",
        }
        advanced = {
            **intermediate,
            "relative_pronoun": "relative pronoun (pronome relativo — que, quem, cujo, o qual, onde)",
            "indefinite_pronoun": "indefinite pronoun (pronome indefinido — alguém, ninguém, tudo)",
            "interrogative_pronoun": "interrogative pronoun (pronome interrogativo — quem, qual, quanto)",
            "subordinating_conjunction": "subordinating conjunction (conjunção subordinativa)",
            "gerund": "gerund (gerúndio — falando, comendo, partindo)",
            "past_participle": "past participle (particípio passado — falado, feito, dito, visto)",
            "personal_infinitive": "personal infinitive (infinitivo pessoal — inflected -mos/-em)",
            "clitic_pronoun": "clitic pronoun (pronome clítico — me, te, se, lhe, o, a, lhes)",
            "mesoclitic": "mesoclitic (clítico inserted in future/conditional — dar-lhe-ei)",
            "subjunctive_marker": "subjunctive marker (marca de subjuntivo — present/imperfect/future subj.)",
            "conditional": "conditional (condicional — falaria / ia falar)",
            "interjection": "interjection (interjeição — oxalá, nossa, caramba)",
            "debitive": "debitive (debitivo — ter de / ter que + infinitive)",
        }
        return {
            "beginner": beginner,
            "intermediate": intermediate,
            "advanced": advanced,
        }

    # ------------------------------------------------------------------
    # Default obligatory contractions (preposition + article/dem./pronoun)
    # ------------------------------------------------------------------

    def _get_default_contractions(self) -> Dict[str, List[str]]:
        """
        Map of contracted surface forms to their components.
        Used at tokenization to split contractions into preposition + X.
        """
        return {
            # de + article
            "do":  ["de", "o"],
            "da":  ["de", "a"],
            "dos": ["de", "os"],
            "das": ["de", "as"],
            # em + article
            "no":  ["em", "o"],
            "na":  ["em", "a"],
            "nos": ["em", "os"],
            "nas": ["em", "as"],
            # a + article
            "ao":  ["a", "o"],
            "à":   ["a", "a"],
            "aos": ["a", "os"],
            "às":  ["a", "as"],
            # por + article
            "pelo":  ["por", "o"],
            "pela":  ["por", "a"],
            "pelos": ["por", "os"],
            "pelas": ["por", "as"],
            # de + ele/ela/eles/elas
            "dele":  ["de", "ele"],
            "dela":  ["de", "ela"],
            "deles": ["de", "eles"],
            "delas": ["de", "elas"],
            # em + ele/ela/eles/elas
            "nele":  ["em", "ele"],
            "nela":  ["em", "ela"],
            "neles": ["em", "eles"],
            "nelas": ["em", "elas"],
            # de + demonstrative
            "deste":   ["de", "este"],
            "desta":   ["de", "esta"],
            "destes":  ["de", "estes"],
            "destas":  ["de", "estas"],
            "desse":   ["de", "esse"],
            "dessa":   ["de", "essa"],
            "desses":  ["de", "esses"],
            "dessas":  ["de", "essas"],
            "daquele": ["de", "aquele"],
            "daquela": ["de", "aquela"],
            "daqueles":["de", "aqueles"],
            "daquelas":["de", "aquelas"],
            "disto":   ["de", "isto"],
            "disso":   ["de", "isso"],
            "daquilo": ["de", "aquilo"],
            # em + demonstrative
            "neste":   ["em", "este"],
            "nesta":   ["em", "esta"],
            "nestes":  ["em", "estes"],
            "nestas":  ["em", "estas"],
            "nesse":   ["em", "esse"],
            "nessa":   ["em", "essa"],
            "nesses":  ["em", "esses"],
            "nessas":  ["em", "essas"],
            "naquele": ["em", "aquele"],
            "naquela": ["em", "aquela"],
            "naqueles":["em", "aqueles"],
            "naquelas":["em", "aquelas"],
            "nisto":   ["em", "isto"],
            "nisso":   ["em", "isso"],
            "naquilo": ["em", "aquilo"],
            # a + distal demonstrative
            "àquele":  ["a", "aquele"],
            "àquela":  ["a", "aquela"],
            "àqueles": ["a", "aqueles"],
            "àquelas": ["a", "aquelas"],
            "àquilo":  ["a", "aquilo"],
            # com + pronoun (suppletive)
            "comigo":   ["com", "mim"],
            "contigo":  ["com", "ti"],
            "consigo":  ["com", "si"],
            "conosco":  ["com", "nós"],
            "connosco": ["com", "nós"],
            "convosco": ["com", "vós"],
            # de + um/uma (PT)
            "dum":  ["de", "um"],
            "duma": ["de", "uma"],
            "duns": ["de", "uns"],
            "dumas":["de", "umas"],
        }

    # ------------------------------------------------------------------
    # Color schemes — Portuguese-specific role differentiation
    # ------------------------------------------------------------------

    def _load_color_schemes(self) -> Dict[str, Dict[str, str]]:
        """
        Color schemes for Portuguese grammatical roles.

        Portuguese-distinctive roles get DEDICATED hex colors so that
        grammar_processor._convert_analyzer_output_to_explanations passes
        them through unchanged (per CLAUDE.md):

          - copula                #00B894  (teal-green — distinct from generic verb)
          - contraction           #FF7F50  (coral — visually marks fused word)
          - personal_infinitive   #6C5CE7  (electric purple — inflected non-finite)
          - mesoclitic            #FF1493  (deep pink — rare/literary)
          - clitic_pronoun        #E91E63  (pink-red — placement-sensitive pronoun)
          - gerund                #00CED1  (dark turquoise — -ndo)
          - past_participle       #FFA500  (orange — -do / irregular)
          - subjunctive_marker    #9C27B0  (purple — mood marker)
        """
        base = {
            # Core POS
            "noun":              "#FFAA00",  # orange
            "verb":              "#44FF44",  # green
            "adjective":         "#FF44FF",  # magenta
            "adverb":            "#44FFFF",  # cyan
            "pronoun":           "#FF4444",  # red
            "preposition":       "#4444FF",  # blue
            "conjunction":       "#888888",  # gray
            "interjection":      "#FFD700",  # gold
            "article":           "#AA44FF",  # purple
            "numeral":           "#3CB371",  # medium sea green
            # Pronoun subtypes
            "personal_pronoun":      "#FF4444",
            "possessive_pronoun":    "#B22222",  # firebrick
            "demonstrative_pronoun": "#FF6347",  # tomato
            "reflexive_pronoun":     "#DC143C",  # crimson
            "relative_pronoun":      "#FF4500",  # orange-red
            "indefinite_pronoun":    "#CD5C5C",  # indian red
            "interrogative_pronoun": "#DB7093",  # pale violet red
            # Article subtypes
            "definite_article":   "#AA44FF",
            "indefinite_article": "#9966CC",  # amethyst
            # Verb subtypes
            "auxiliary_verb": "#228B22",  # forest green
            "modal_verb":     "#32CD32",  # lime green
            "pronominal_verb":"#20B2AA",  # light sea green
            # ============================================================
            # Portuguese-specific roles — DISTINCT colors (do NOT collapse
            # into the generic categories above; grammar_processor passes
            # these through unchanged).
            # ============================================================
            "copula":              "#00B894",  # teal-green (ser/estar)
            "contraction":         "#FF7F50",  # coral (do, no, ao, pelo, ...)
            "personal_infinitive": "#6C5CE7",  # electric purple
            "mesoclitic":          "#FF1493",  # deep pink (rare/literary)
            "clitic_pronoun":      "#E91E63",  # pink-red
            "gerund":              "#00CED1",  # dark turquoise (-ndo)
            "past_participle":     "#FFA500",  # orange (-do / irregular)
            "subjunctive_marker":  "#9C27B0",  # purple (mood)
            "conditional":         "#7E57C2",  # deep purple
            "debitive":            "#D81B60",  # deep pink (ter de / ter que)
            "particle":            "#A1887F",  # warm gray-brown
            "subordinating_conjunction": "#777777",
            # Default
            "other": "#AAAAAA",
            "default": "#000000",
        }
        # Three identical color schemes — progressive disclosure happens at
        # the prompt-builder level via the role list returned for each
        # complexity tier, not at the color level.
        return {
            "beginner":     dict(base),
            "intermediate": dict(base),
            "advanced":     dict(base),
        }

    def get_color_scheme(self, complexity: str) -> Dict[str, str]:
        """Return color scheme for the given complexity level."""
        return self.color_schemes.get(complexity, self.color_schemes["intermediate"])

    def get_color_for_role(
        self, role: str, complexity: str = "intermediate"
    ) -> str:
        """Get the display color for a specific grammatical role."""
        scheme = self.get_color_scheme(complexity)
        return scheme.get(role, scheme.get("other", "#AAAAAA"))

    def get_role_label(
        self, role: str, complexity: str = "intermediate"
    ) -> str:
        """Get human-readable label for a grammatical role."""
        roles = self._get_default_roles() if not self.grammatical_roles else self.grammatical_roles
        # The YAML / default roles dict is keyed by complexity
        level_roles = roles.get(complexity, roles.get("intermediate", {}))
        if isinstance(level_roles, dict):
            return level_roles.get(role, role)
        return role

    # ------------------------------------------------------------------
    # File loaders (graceful fallbacks)
    # ------------------------------------------------------------------

    def _load_yaml(self, path: Path) -> Optional[Dict]:
        """Load YAML file if it exists, return None on failure."""
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f)
            except Exception as e:
                logger.warning(f"Failed to load YAML {path}: {e}")
        return None

    def _load_json(self, path: Path) -> Optional[Dict]:
        """Load JSON file if it exists, return None on failure."""
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load JSON {path}: {e}")
        return None
