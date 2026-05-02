# languages/portuguese/domain/pt_fallbacks.py
"""
Portuguese Fallbacks — Domain Component (Level 5 of the parsing cascade)

Rule-based fallback grammar analysis for Portuguese. Used when:
  - The AI response is empty / unparseable / an error sentinel
  - All four upstream parser levels (direct JSON, markdown, repaired,
    text patterns) fail

The fallback never crashes — it always returns a complete result dict
in the canonical normalized shape that PtValidator and the analyzer
facade expect. Quality is intentionally modest (confidence ≈ 0.35).

Portuguese-specific heuristics encoded:
  - Obligatory contractions (do, no, ao, pelo, dele, naquele, daquilo,
    comigo, etc.) → role='contraction' with contraction_parts populated
  - ser / estar conjugated forms → role='copula' with copula_type set
  - Clitic pronouns (me, te, se, lhe, lhes, nos, vos, o, a, os, as) →
    role='clitic_pronoun' (with crude position guess from hyphen presence)
  - Hyphenated verb-clitic forms (viu-me, dar-lhe-ei) → split tokens
  - -ndo gerund, -do past participle (incl. irregulars), -mente adverbs
  - Definite/indefinite articles, demonstratives (3-way deixis),
    possessives (incl. dele/dela contracted possessives), prepositions,
    coordinating + subordinating conjunctions
"""

import logging
import re
from typing import Any, Dict, List, Tuple

from .pt_config import PtConfig

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Closed-class lookup tables (lower-cased)
# ---------------------------------------------------------------------------

_DEFINITE_ARTICLES = {"o", "a", "os", "as"}
_INDEFINITE_ARTICLES = {"um", "uma", "uns", "umas"}

_PERSONAL_PRONOUNS_SUBJ = {
    "eu", "tu", "você", "ele", "ela", "nós", "vós", "vocês", "eles", "elas",
    "a gente",  # multi-word, handled at sentence level
}
# Disjunctive (after preposition)
_DISJUNCTIVE_PRONOUNS = {"mim", "ti", "si"}

# Object / reflexive clitics
_CLITIC_PRONOUNS = {
    "me", "te", "se", "lhe", "lhes", "nos", "vos",
    "o", "a", "os", "as",
    # -lo / -na allomorphs (only meaningful after verb hyphen — checked separately)
    "lo", "la", "los", "las", "no", "na",
}

_REFLEXIVE_CLITICS = {"me", "te", "se", "nos", "vos"}

_POSSESSIVE_PRONOUNS = {
    "meu", "minha", "meus", "minhas",
    "teu", "tua", "teus", "tuas",
    "seu", "sua", "seus", "suas",
    "nosso", "nossa", "nossos", "nossas",
    "vosso", "vossa", "vossos", "vossas",
    "dele", "dela", "deles", "delas",  # contracted possessive forms
}

_DEMONSTRATIVE_PRONOUNS = {
    "este", "esta", "estes", "estas",
    "esse", "essa", "esses", "essas",
    "aquele", "aquela", "aqueles", "aquelas",
    "isto", "isso", "aquilo",
}

_RELATIVE_PRONOUNS = {
    "que", "quem", "cujo", "cuja", "cujos", "cujas",
    "o qual", "a qual", "os quais", "as quais", "onde",
}

_INDEFINITE_PRONOUNS = {
    "alguém", "ninguém", "algo", "nada", "tudo",
    "todo", "toda", "todos", "todas",
    "cada", "alguns", "algumas",
    "nenhum", "nenhuma", "nenhuns", "nenhumas",
    "qualquer", "quaisquer",
    "outro", "outra", "outros", "outras",
}

_INTERROGATIVE_PRONOUNS = {
    "quem", "qual", "quais", "quanto", "quanta", "quantos", "quantas",
    "onde", "como", "quando", "porque", "porquê", "por que", "por quê",
}

_PREPOSITIONS = {
    "a", "de", "em", "por", "para", "com", "sem", "sob", "sobre",
    "entre", "até", "desde", "contra", "ante", "perante", "após", "trás",
    "conforme", "segundo",
}

_COORDINATING_CONJUNCTIONS = {
    "e", "ou", "mas", "porém", "contudo", "todavia", "nem", "ora",
}

_SUBORDINATING_CONJUNCTIONS = {
    "que", "porque", "pois", "quando", "enquanto", "se", "embora",
    "ainda", "mesmo", "caso", "conforme", "logo", "assim", "como",
    "antes", "depois", "desde",
    # Multi-word triggers handled at sentence level: "ainda que", "mesmo que",
    # "para que", "sem que", "antes que", "depois que", "assim que", "logo que",
    # "a fim de que", "contanto que", "desde que", "visto que", "já que"
}

_AUXILIARY_VERBS_FORMS = {
    # ter (perfect aux)
    "tenho", "tens", "tem", "temos", "tendes", "têm",
    "tinha", "tinhas", "tínhamos", "tínheis", "tinham",
    "tive", "tiveste", "teve", "tivemos", "tivestes", "tiveram",
    "terei", "terás", "terá", "teremos", "tereis", "terão",
    "ter",
    # haver (literary perfect, existential)
    "hei", "hás", "há", "havemos", "haveis", "hão",
    "havia", "havias", "havíamos", "havíeis", "haviam",
    "haver",
    # ir (periphrastic future + main verb)
    "vou", "vais", "vai", "vamos", "ides", "vão",
    "ia", "ias", "íamos", "íeis", "iam",
    # estar (progressive aux)
    "estou", "estás", "está", "estamos", "estais", "estão",
    "estava", "estavas", "estávamos", "estáveis", "estavam",
    "estive", "estiveste", "esteve", "estivemos", "estivestes", "estiveram",
    "estar",
}

# ser / estar copula forms (extracted separately so we can tag copula_type)
_SER_FORMS = {
    "sou", "és", "é", "somos", "sois", "são",
    "era", "eras", "éramos", "éreis", "eram",
    "fui", "foste", "foi", "fomos", "fostes", "foram",
    "serei", "serás", "será", "seremos", "sereis", "serão",
    "seria", "serias", "seríamos", "seríeis", "seriam",
    "seja", "sejas", "sejamos", "sejais", "sejam",
    "ser",
}
_ESTAR_FORMS = {
    "estou", "estás", "está", "estamos", "estais", "estão",
    "estava", "estavas", "estávamos", "estáveis", "estavam",
    "estive", "estiveste", "esteve", "estivemos", "estivestes", "estiveram",
    "estarei", "estarás", "estará", "estaremos", "estareis", "estarão",
    "estaria", "estarias", "estaríamos", "estaríeis", "estariam",
    "esteja", "estejas", "estejamos", "estejais", "estejam",
    "estar",
}

_MODAL_VERBS = {
    "poder", "dever", "querer", "saber", "haver de", "haver",
    "posso", "podes", "pode", "podemos", "podeis", "podem",
    "devo", "deves", "deve", "devemos", "deveis", "devem",
    "quero", "queres", "quer", "queremos", "quereis", "querem",
    "sei", "sabes", "sabe", "sabemos", "sabeis", "sabem",
}

_PARTICLES = {
    "não", "sim", "cá", "lá", "aí", "pois", "né", "tá",
    "ainda", "já", "também", "só", "talvez", "apenas",
}

_INTERJECTIONS = {
    "oxalá", "tomara", "nossa", "caramba", "puxa", "olha", "escuta",
    "ah", "oh", "eh", "viva",
}

_NUMERAL_WORDS = {
    "zero", "um", "dois", "três", "quatro", "cinco", "seis", "sete",
    "oito", "nove", "dez", "onze", "doze", "treze", "catorze", "quatorze",
    "quinze", "dezesseis", "dezessete", "dezoito", "dezenove", "vinte",
    "trinta", "quarenta", "cinquenta", "sessenta", "setenta", "oitenta",
    "noventa", "cem", "cento", "mil", "milhão", "milhões",
    "primeiro", "segundo", "terceiro", "quarto", "quinto",
}

# Common irregular past participles (surface forms that don't end in -do)
_IRREGULAR_PAST_PARTICIPLES = {
    "feito", "dito", "visto", "posto", "escrito", "aberto", "coberto",
    "ganho", "gasto", "pago", "vindo",
}


class PtFallbacks:
    """Rule-based fallback analysis for Portuguese grammar."""

    def __init__(self, config: PtConfig):
        self.config = config

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def create_fallback(self, sentence: str, complexity: str) -> Dict[str, Any]:
        """Create a basic rule-based grammar analysis for a Portuguese sentence."""
        logger.info(f"Creating Portuguese fallback for: '{sentence[:60]}'")

        tokens = self._tokenize(sentence)
        word_details: List[Dict[str, Any]] = []
        word_explanations: List[List[Any]] = []
        elements: Dict[str, List[Dict[str, Any]]] = {}

        for token in tokens:
            role, meaning, meta = self._classify_word(token, complexity)
            color = self.config.get_color_for_role(role, complexity)

            detail = {
                "word": token,
                "grammatical_role": role,
                "role": role,
                "color": color,
                "meaning": meaning,
                "gender": meta.get("gender", ""),
                "number": meta.get("number", ""),
                "person": meta.get("person", ""),
                "tense": meta.get("tense", ""),
                "mood": meta.get("mood", ""),
                "copula_type": meta.get("copula_type", ""),
                "clitic_position": meta.get("clitic_position", ""),
                "contraction_parts": meta.get("contraction_parts", []),
                "register": "",
                "is_target": False,
            }
            word_details.append(detail)
            word_explanations.append([token, role, color, meaning])
            elements.setdefault(role, []).append({
                "word": token,
                "grammatical_role": role,
                **{k: v for k, v in meta.items() if v},
            })

        overall = "Portuguese sentence (rule-based fallback)"

        return {
            "sentence": sentence,
            "register": "",
            "elements": elements,
            "explanations": {
                "overall_structure": overall,
                "sentence_structure": overall,
                "key_features": "Portuguese fallback — best-effort POS tagging",
                "complexity_notes": f"{complexity} (fallback)",
            },
            "overall_structure": overall,
            "sentence_structure": overall,
            "grammar_notes": "Rule-based fallback — AI analysis unavailable.",
            "word_explanations": word_explanations,
            "word_details": word_details,
            "confidence": 0.35,
            "is_fallback": True,
        }

    # ------------------------------------------------------------------
    # Tokenisation — handle hyphenated verb-clitic forms
    # ------------------------------------------------------------------

    def _tokenize(self, sentence: str) -> List[str]:
        """
        Split a Portuguese sentence into tokens.
        Hyphenated verb-clitic forms (viu-me, dá-lho, dar-lhe-ei) are split
        into separate tokens so each part can be analysed.
        Punctuation tokens are preserved as their own entries.
        """
        # First, split on whitespace
        raw_tokens = sentence.split()
        result: List[str] = []
        for raw in raw_tokens:
            # Strip and capture trailing punctuation
            trailing_punct = ""
            stripped = raw
            while stripped and stripped[-1] in ".,!?;:\"')]}":
                trailing_punct = stripped[-1] + trailing_punct
                stripped = stripped[:-1]
            leading_punct = ""
            while stripped and stripped[0] in "\"'([{¡¿":
                leading_punct = leading_punct + stripped[0]
                stripped = stripped[1:]

            if leading_punct:
                result.append(leading_punct)

            # Hyphenated verb-clitic form? Split if it looks like one.
            # Heuristic: token contains '-' and at least one segment is a
            # clitic pronoun.
            if "-" in stripped and self._looks_like_clitic_compound(stripped):
                parts = stripped.split("-")
                for i, part in enumerate(parts):
                    if part:
                        result.append(part)
            elif stripped:
                result.append(stripped)

            if trailing_punct:
                result.append(trailing_punct)
        return result

    def _looks_like_clitic_compound(self, token: str) -> bool:
        """Heuristic: does this hyphenated form contain a clitic pronoun?"""
        parts = [p.lower() for p in token.split("-") if p]
        if len(parts) < 2:
            return False
        clitic_set = _CLITIC_PRONOUNS | {"se"}
        # If any non-first segment is a clitic, treat as a verb-clitic form
        return any(p in clitic_set for p in parts[1:])

    # ------------------------------------------------------------------
    # Classification — single-token rule cascade
    # ------------------------------------------------------------------

    def _classify_word(
        self, word: str, complexity: str
    ) -> Tuple[str, str, Dict[str, Any]]:
        """Return (role, meaning, meta) for a single token."""
        meta: Dict[str, Any] = {}
        if not word or not word.strip():
            return "other", word, meta

        # Pure punctuation
        if all(not ch.isalnum() for ch in word):
            return "other", word, meta

        lower = word.lower().strip(".,!?;:\"'()[]{}")

        # 1. Contractions (highest priority — surface form is unique)
        if lower in self.config.contractions:
            parts = self.config.contractions[lower]
            meta["contraction_parts"] = list(parts)
            return (
                "contraction",
                f"{word} (contraction = {' + '.join(parts)})",
                meta,
            )

        # 2. Copula (ser / estar) — must come before generic auxiliary check
        if lower in _SER_FORMS:
            meta["copula_type"] = "ser"
            return "copula", f"{word} (ser — inherent/identifying copula)", meta
        if lower in _ESTAR_FORMS:
            meta["copula_type"] = "estar"
            return "copula", f"{word} (estar — transient/locational copula)", meta

        # 3. Articles
        if lower in _DEFINITE_ARTICLES:
            return (
                "definite_article" if complexity != "beginner" else "article",
                f"{word} (definite article)",
                meta,
            )
        if lower in _INDEFINITE_ARTICLES:
            return (
                "indefinite_article" if complexity != "beginner" else "article",
                f"{word} (indefinite article)",
                meta,
            )

        # 4. Pronouns (in priority order: clitic > personal > poss > dem > rel > indef)
        if complexity != "beginner" and lower in _CLITIC_PRONOUNS - {"o", "a", "os", "as"}:
            # Bare clitic without a verb context — best-guess proclitic
            meta["clitic_position"] = "proclitic"
            return "clitic_pronoun", f"{word} (object/reflexive clitic)", meta

        if lower in _PERSONAL_PRONOUNS_SUBJ or lower in _DISJUNCTIVE_PRONOUNS:
            return (
                "personal_pronoun" if complexity != "beginner" else "pronoun",
                f"{word} (personal pronoun)",
                meta,
            )

        if lower in _POSSESSIVE_PRONOUNS:
            return (
                "possessive_pronoun" if complexity != "beginner" else "pronoun",
                f"{word} (possessive pronoun)",
                meta,
            )

        if lower in _DEMONSTRATIVE_PRONOUNS:
            return (
                "demonstrative_pronoun" if complexity != "beginner" else "pronoun",
                f"{word} (demonstrative pronoun)",
                meta,
            )

        if complexity == "advanced" and lower in _RELATIVE_PRONOUNS:
            return "relative_pronoun", f"{word} (relative pronoun)", meta

        if complexity == "advanced" and lower in _INDEFINITE_PRONOUNS:
            return "indefinite_pronoun", f"{word} (indefinite pronoun)", meta

        # 5. Particles (não, sim, cá, lá, pois, ...)
        if complexity != "beginner" and lower in _PARTICLES:
            return "particle", f"{word} (particle)", meta

        # 6. Prepositions
        if lower in _PREPOSITIONS:
            return "preposition", f"{word} (preposition)", meta

        # 7. Conjunctions
        if lower in _COORDINATING_CONJUNCTIONS:
            return "conjunction", f"{word} (coordinating conjunction)", meta
        if complexity == "advanced" and lower in _SUBORDINATING_CONJUNCTIONS:
            return (
                "subordinating_conjunction",
                f"{word} (subordinating conjunction)",
                meta,
            )
        if lower in _SUBORDINATING_CONJUNCTIONS:
            return "conjunction", f"{word} (conjunction)", meta

        # 8. Modal verbs
        if complexity != "beginner" and lower in _MODAL_VERBS:
            return "modal_verb", f"{word} (modal verb)", meta

        # 9. Auxiliary verbs (ter, haver, ir, estar in aux uses)
        if complexity != "beginner" and lower in _AUXILIARY_VERBS_FORMS:
            return "auxiliary_verb", f"{word} (auxiliary verb)", meta

        # 10. Interjections
        if lower in _INTERJECTIONS:
            return (
                "interjection" if complexity != "beginner" else "other",
                f"{word} (interjection)",
                meta,
            )

        # 11. Numerals
        if word.isdigit() or lower in _NUMERAL_WORDS:
            return "numeral", f"{word} (numeral)", meta

        # 12. Past participles (irregular + -do regular)
        if complexity == "advanced":
            if lower in _IRREGULAR_PAST_PARTICIPLES:
                return "past_participle", f"{word} (irregular past participle)", meta
            if (
                len(lower) > 4
                and (lower.endswith("ado") or lower.endswith("ido"))
                and not lower.endswith("inho")  # diminutive false-positive
            ):
                return "past_participle", f"{word} (past participle)", meta

        # 13. Gerund (-ndo)
        if complexity == "advanced" and lower.endswith("ndo") and len(lower) > 4:
            return "gerund", f"{word} (gerund — progressive/adverbial)", meta

        # 14. Personal infinitive (regular -armos/-ermos/-irmos/-arem/-erem/-irem)
        if (
            complexity == "advanced"
            and (
                re.search(r"(armos|ermos|irmos|ardes|erdes|irdes|arem|erem|irem)$", lower)
                and len(lower) > 5
            )
        ):
            meta["mood"] = "personal_infinitive"
            return (
                "personal_infinitive",
                f"{word} (personal infinitive — inflected)",
                meta,
            )

        # 15. Manner adverb -mente
        if lower.endswith("mente") and len(lower) > 5:
            return "adverb", f"{word} (manner adverb)", meta

        # 16. Verbs — heuristics by infinitive ending and common conjugated endings
        if (
            re.search(r"(ar|er|ir|or)$", lower)
            and len(lower) >= 4
            and not lower.endswith("ar")  # "ar" alone is too short — needs len gate
            or re.search(
                r"(amos|emos|imos|aram|eram|iram|asse|esse|isse|ará|erá|irá|"
                r"aria|eria|iria|ava|avas|ávamos|aram)$",
                lower,
            )
        ):
            return "verb", f"{word} (verb)", meta

        # 17. Adjectives — common endings
        if re.search(
            r"(oso|osa|osos|osas|ivo|iva|ivos|ivas|ável|ível|áveis|íveis|"
            r"ado|ada|ados|adas|inho|inha|inhos|inhas|íssimo|íssima)$",
            lower,
        ):
            return "adjective", f"{word} (adjective)", meta

        # 18. Nouns — gendered endings give us a free gender guess
        if lower.endswith(("ção", "são", "agem", "dade", "tude", "ice")):
            meta["gender"] = "feminine"
            return "noun", f"{word} (feminine noun)", meta
        if lower.endswith(("mento", "tor", "dor", "or", "ema", "ama", "oma")):
            meta["gender"] = "masculine"
            return "noun", f"{word} (masculine noun)", meta
        if lower.endswith("a") and len(lower) > 2:
            meta["gender"] = "feminine"
            return "noun", f"{word} (likely feminine noun)", meta
        if lower.endswith("o") and len(lower) > 2:
            meta["gender"] = "masculine"
            return "noun", f"{word} (likely masculine noun)", meta
        if word and word[0].isupper() and len(word) > 2:
            return "noun", f"{word} (proper noun)", meta

        # 19. Default
        return "other", f"{word}", meta
