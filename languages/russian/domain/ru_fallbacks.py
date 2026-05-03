# languages/russian/domain/ru_fallbacks.py
"""
Russian Fallbacks — Domain Component

Rule-based fallback grammar analysis for Russian, used when AI is
unavailable or unparseable.

The fallback emits **multi-clause `individual_meaning` text per word
(≥30 chars typical, never POS-only stubs)**, marks `is_fallback: True` on
the result so the validator caps confidence at 0.3, and uses Cyrillic-aware
suffix heuristics for open-class words. Closed-class lookup tables cover:

  - Personal pronouns (all 6 cases × 6 persons + the n-prefixed
    after-preposition forms него/неё/него/них)
  - Reflexive себя in 5 oblique cases
  - Possessive determiners (мой/твой/его/её/наш/ваш/их/свой) + key
    case-forms
  - Demonstratives этот/эта/это/эти, тот/та/то/те + declined forms
  - Interrogative/relative: кто/что/где/когда/как/почему/зачем/чей/какой/
    который + declensions
  - Negative pronouns/adverbs: никто/ничто/никогда/никуда/нигде/...
  - Modals: могу/может/хочу/хочет/должен/нужно/надо/нельзя/можно
  - Particles: бы (conditional), не (negation), ни (emphatic neg), же
    (contrastive), ли (Q), ведь, разве, неужели
  - быть paradigm: быть/был/была/было/были/будет/будут/есть/нет
  - 30+ prepositions with their governed cases
  - Coordinating + subordinating conjunctions

Open-class fallback uses suffix heuristics (Cyrillic) for case/gender on
nouns and adjectives, and perfectivising-prefix heuristic for verb aspect.
Heuristics are explicitly acknowledged in the explanation text so cards
expose the uncertainty.
"""

import logging
import re
from typing import Any, Dict, List, Optional, Tuple

from .ru_config import RuConfig

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Closed-class lexicons.
# ---------------------------------------------------------------------------

# Personal pronouns — full 6-case × 6-person paradigm + the n-prefixed
# after-preposition allomorphs (них / нём / нему / неё / ней / ним / ними /
# него — the historical n- prefix appears on 3rd-person forms after a
# governing preposition).
# Format: lower → (case, person_num_label, individual_meaning)
_PERSONAL_PRONOUNS: Dict[str, Tuple[str, str, str]] = {
    # 1sg я
    "я":     ("nominative",   "1sg",   "Personal pronoun 'я' (I), 1st-person singular, nominative case. Subject pronoun; Russian is pro-drop, so an explicit я is mildly emphatic."),
    "меня":  ("genitive",     "1sg",   "Personal pronoun 'меня' (me), 1st-person singular, genitive (or accusative — syncretic). Used as object after most prepositions of source/possession and as direct object of the negated verb."),
    "мне":   ("dative",       "1sg",   "Personal pronoun 'мне' (to me), 1st-person singular, dative case. Indirect object / experiencer; 'мне' is also the dative used in impersonal 'мне нравится' constructions."),
    "мной":  ("instrumental", "1sg",   "Personal pronoun 'мной' (by me / with me), 1st-person singular, instrumental case. Marks instrument, agent of passive, or accompaniment."),
    "мною":  ("instrumental", "1sg",   "Personal pronoun 'мною' (by me), 1st-person singular instrumental — bookish/literary variant of 'мной'."),
    # 2sg ты
    "ты":    ("nominative",   "2sg",   "Personal pronoun 'ты' (you, sg.), 2nd-person singular, nominative. Informal singular subject pronoun."),
    "тебя":  ("genitive",     "2sg",   "Personal pronoun 'тебя' (you), 2nd-person singular, genitive (or accusative — syncretic). Direct or genitive object."),
    "тебе":  ("dative",       "2sg",   "Personal pronoun 'тебе' (to you), 2nd-person singular, dative case. Indirect object or experiencer."),
    "тобой": ("instrumental", "2sg",   "Personal pronoun 'тобой' (by you / with you), 2nd-person singular, instrumental case."),
    "тобою": ("instrumental", "2sg",   "Personal pronoun 'тобою' — bookish instrumental variant of 'тобой'."),
    # 3sg.m он
    "он":    ("nominative",   "3sg.m", "Personal pronoun 'он' (he/it), 3rd-person singular masculine, nominative. Refers to a masculine antecedent (animate or inanimate)."),
    "его":   ("genitive",     "3sg.m", "Personal pronoun 'его' (him / its), 3rd-person singular masculine genitive (or accusative — syncretic). Note: 'его' is also the invariant 3rd-person possessive determiner ('his') — context disambiguates."),
    "ему":   ("dative",       "3sg.m", "Personal pronoun 'ему' (to him), 3rd-person singular masculine, dative case."),
    "им":    ("instrumental", "3sg",   "Personal pronoun 'им', instrumental case. Either 3rd-person singular masculine ('by him') OR 3rd-person plural dative ('to them') — disambiguated by context."),
    "ним":   ("instrumental", "3sg.m", "Personal pronoun 'ним' (by him), 3rd-person singular masculine instrumental, n-prefixed after a preposition (e.g. 'с ним')."),
    "нём":   ("prepositional","3sg.m", "Personal pronoun 'нём' (about him / it), 3rd-person singular masculine/neuter, prepositional case. Always n-prefixed because a preposition (о, в, на, при) precedes it."),
    "нему":  ("dative",       "3sg.m", "Personal pronoun 'нему' (to him), 3rd-person singular masculine dative — n-prefixed allomorph after a preposition (e.g. 'к нему')."),
    "него":  ("genitive",     "3sg.m", "Personal pronoun 'него' (him / of him), 3rd-person singular masculine genitive/accusative — n-prefixed allomorph after a preposition (e.g. 'у него', 'без него')."),
    # 3sg.f она
    "она":   ("nominative",   "3sg.f", "Personal pronoun 'она' (she/it), 3rd-person singular feminine, nominative."),
    "её":    ("genitive",     "3sg.f", "Personal pronoun 'её' (her), 3rd-person singular feminine, genitive/accusative (syncretic). Also functions as the invariant 3rd-person feminine possessive determiner ('her')."),
    "ей":    ("dative",       "3sg.f", "Personal pronoun 'ей' (to her), 3rd-person singular feminine, dative case (also instrumental in some uses)."),
    "ею":    ("instrumental", "3sg.f", "Personal pronoun 'ею' (by her), 3rd-person singular feminine instrumental — bookish/literary variant of 'ей'."),
    "ней":   ("dative",       "3sg.f", "Personal pronoun 'ней' (to her / about her / by her), 3rd-person singular feminine, n-prefixed after a preposition (case = dative / instrumental / prepositional, disambiguated by the preposition)."),
    "неё":   ("genitive",     "3sg.f", "Personal pronoun 'неё' (her / of her), 3rd-person singular feminine genitive/accusative — n-prefixed allomorph after a preposition (e.g. 'у неё', 'без неё')."),
    # 3sg.n оно
    "оно":   ("nominative",   "3sg.n", "Personal pronoun 'оно' (it), 3rd-person singular neuter, nominative. Used for neuter antecedents."),
    # 1pl мы
    "мы":    ("nominative",   "1pl",   "Personal pronoun 'мы' (we), 1st-person plural, nominative. Plural subject pronoun."),
    "нас":   ("genitive",     "1pl",   "Personal pronoun 'нас' (us), 1st-person plural, genitive/accusative/prepositional (syncretic)."),
    "нам":   ("dative",       "1pl",   "Personal pronoun 'нам' (to us), 1st-person plural, dative."),
    "нами":  ("instrumental", "1pl",   "Personal pronoun 'нами' (by us / with us), 1st-person plural, instrumental case."),
    # 2pl вы (also formal-2sg)
    "вы":    ("nominative",   "2pl",   "Personal pronoun 'вы' (you, pl. or formal sg.), 2nd-person plural, nominative. Also the formal singular subject pronoun."),
    "вас":   ("genitive",     "2pl",   "Personal pronoun 'вас' (you), 2nd-person plural genitive/accusative/prepositional (syncretic)."),
    "вам":   ("dative",       "2pl",   "Personal pronoun 'вам' (to you), 2nd-person plural, dative."),
    "вами":  ("instrumental", "2pl",   "Personal pronoun 'вами' (by you / with you), 2nd-person plural, instrumental."),
    # 3pl они
    "они":   ("nominative",   "3pl",   "Personal pronoun 'они' (they), 3rd-person plural, nominative."),
    "их":    ("genitive",     "3pl",   "Personal pronoun 'их' (them / of them), 3rd-person plural, genitive/accusative (syncretic). Also the invariant 3rd-person plural possessive determiner ('their')."),
    "им__pl": ("dative",      "3pl",   "Personal pronoun 'им' (to them), 3rd-person plural, dative case."),
    "ими":   ("instrumental", "3pl",   "Personal pronoun 'ими' (by them / with them), 3rd-person plural, instrumental."),
    "них":   ("genitive",     "3pl",   "Personal pronoun 'них' (them / of them / about them), 3rd-person plural, n-prefixed after a preposition (case = genitive / accusative / prepositional, disambiguated by the preposition)."),
    "ним__pl":("dative",      "3pl",   "Personal pronoun 'ним' (to them), 3rd-person plural, dative — n-prefixed after a preposition."),
    "ними":  ("instrumental", "3pl",   "Personal pronoun 'ними' (by them / with them), 3rd-person plural, instrumental — n-prefixed after a preposition."),
}

# Reflexive себя (no nominative form).
_REFLEXIVE_PRONOUNS: Dict[str, Tuple[str, str]] = {
    "себя":  ("genitive",     "Reflexive pronoun 'себя' (oneself), genitive or accusative form (syncretic). Refers back to the clause subject; 'Он любит себя' = 'He loves himself'."),
    "себе":  ("dative",       "Reflexive pronoun 'себе' (to/for oneself), dative or prepositional case. 'Она купила себе книгу' = 'She bought herself a book'."),
    "собой": ("instrumental", "Reflexive pronoun 'собой' (with/by oneself), instrumental case. 'Он гордится собой' = 'He is proud of himself'."),
    "собою": ("instrumental", "Reflexive pronoun 'собою' — bookish/literary instrumental variant of 'собой'."),
}

# Possessive determiners — мой/твой/его/её/наш/ваш/их/свой and the most
# common case-forms. Static lookup keyed on lowercase surface form.
# Value: (person_label, individual_meaning_template)
_POSSESSIVE_DETERMINERS: Dict[str, str] = {
    # 1sg мой
    "мой":   "Possessive determiner 'мой' (my), masculine singular nominative. Declines like an adjective and agrees with the head noun in case, gender, and number.",
    "моя":   "Possessive determiner 'моя' (my), feminine singular nominative. Agrees with a feminine head noun.",
    "моё":   "Possessive determiner 'моё' (my), neuter singular nominative.",
    "мои":   "Possessive determiner 'мои' (my), nominative plural (any gender).",
    "моего": "Possessive determiner 'моего' (my), genitive/accusative singular masculine/neuter — animate-acc and gen are syncretic.",
    "моей":  "Possessive determiner 'моей' (my), genitive/dative/instrumental/prepositional singular feminine.",
    "моему": "Possessive determiner 'моему' (my), dative singular masculine/neuter.",
    "моим":  "Possessive determiner 'моим' (my), instrumental singular masculine/neuter OR dative plural.",
    "моём":  "Possessive determiner 'моём' (my), prepositional singular masculine/neuter.",
    "моих":  "Possessive determiner 'моих' (my), genitive / accusative-animate / prepositional plural.",
    "моими": "Possessive determiner 'моими' (my), instrumental plural.",
    "моим__pl": "Possessive determiner 'моим' (my), dative plural.",
    # 2sg твой
    "твой":  "Possessive determiner 'твой' (your, sg. informal), masculine singular nominative. Agrees with the head noun.",
    "твоя":  "Possessive determiner 'твоя' (your, sg.), feminine singular nominative.",
    "твоё":  "Possessive determiner 'твоё' (your, sg.), neuter singular nominative.",
    "твои":  "Possessive determiner 'твои' (your, sg.), nominative plural.",
    "твоего":"Possessive determiner 'твоего' (your, sg.), genitive/animate-acc singular masculine/neuter.",
    "твоей": "Possessive determiner 'твоей' (your, sg.), genitive/dative/instrumental/prepositional singular feminine.",
    "твоему":"Possessive determiner 'твоему' (your, sg.), dative singular masculine/neuter.",
    "твоим": "Possessive determiner 'твоим' (your, sg.), instrumental singular masculine/neuter.",
    "твоём": "Possessive determiner 'твоём' (your, sg.), prepositional singular masculine/neuter.",
    "твоих": "Possessive determiner 'твоих' (your, sg.), genitive / animate-acc / prepositional plural.",
    "твоими":"Possessive determiner 'твоими' (your, sg.), instrumental plural.",
    # 1pl наш
    "наш":   "Possessive determiner 'наш' (our), masculine singular nominative. Agrees with the head noun in case, gender, and number.",
    "наша":  "Possessive determiner 'наша' (our), feminine singular nominative.",
    "наше":  "Possessive determiner 'наше' (our), neuter singular nominative.",
    "наши":  "Possessive determiner 'наши' (our), nominative plural.",
    "нашего":"Possessive determiner 'нашего' (our), genitive/animate-acc singular masculine/neuter.",
    "нашей": "Possessive determiner 'нашей' (our), genitive/dative/instrumental/prepositional singular feminine.",
    "нашему":"Possessive determiner 'нашему' (our), dative singular masculine/neuter.",
    "нашим": "Possessive determiner 'нашим' (our), instrumental singular masculine/neuter.",
    "нашем": "Possessive determiner 'нашем' (our), prepositional singular masculine/neuter.",
    "наших": "Possessive determiner 'наших' (our), genitive / animate-acc / prepositional plural.",
    "нашими":"Possessive determiner 'нашими' (our), instrumental plural.",
    # 2pl ваш
    "ваш":   "Possessive determiner 'ваш' (your, pl. or formal sg.), masculine singular nominative. Agrees with the head noun.",
    "ваша":  "Possessive determiner 'ваша' (your, pl.), feminine singular nominative.",
    "ваше":  "Possessive determiner 'ваше' (your, pl.), neuter singular nominative.",
    "ваши":  "Possessive determiner 'ваши' (your, pl.), nominative plural.",
    "вашего":"Possessive determiner 'вашего' (your, pl.), genitive/animate-acc singular masculine/neuter.",
    "вашей": "Possessive determiner 'вашей' (your, pl.), genitive/dative/instrumental/prepositional singular feminine.",
    "вашему":"Possessive determiner 'вашему' (your, pl.), dative singular masculine/neuter.",
    "вашим": "Possessive determiner 'вашим' (your, pl.), instrumental singular masculine/neuter.",
    "вашем": "Possessive determiner 'вашем' (your, pl.), prepositional singular masculine/neuter.",
    "ваших": "Possessive determiner 'ваших' (your, pl.), genitive / animate-acc / prepositional plural.",
    "вашими":"Possessive determiner 'вашими' (your, pl.), instrumental plural.",
    # Reflexive свой — used when the possessor is coreferent with the subject.
    "свой":  "Reflexive possessive determiner 'свой' (one's own), masculine singular nominative. Required when the possessor is the same as the clause subject — contrast 'его' for a different possessor.",
    "своя":  "Reflexive possessive determiner 'своя' (one's own), feminine singular nominative.",
    "своё":  "Reflexive possessive determiner 'своё' (one's own), neuter singular nominative.",
    "свои":  "Reflexive possessive determiner 'свои' (one's own), nominative plural.",
    "своего":"Reflexive possessive determiner 'своего' (one's own), genitive/animate-acc singular masculine/neuter.",
    "своей": "Reflexive possessive determiner 'своей' (one's own), genitive/dative/instrumental/prepositional singular feminine.",
    "своему":"Reflexive possessive determiner 'своему' (one's own), dative singular masculine/neuter.",
    "своим": "Reflexive possessive determiner 'своим' (one's own), instrumental singular masculine/neuter.",
    "своём": "Reflexive possessive determiner 'своём' (one's own), prepositional singular masculine/neuter.",
    "своих": "Reflexive possessive determiner 'своих' (one's own), genitive / animate-acc / prepositional plural.",
    "своими":"Reflexive possessive determiner 'своими' (one's own), instrumental plural.",
    "свою":  "Reflexive possessive determiner 'свою' (one's own), accusative singular feminine.",
    "мою":   "Possessive determiner 'мою' (my), accusative singular feminine.",
    "твою":  "Possessive determiner 'твою' (your, sg.), accusative singular feminine.",
    "нашу":  "Possessive determiner 'нашу' (our), accusative singular feminine.",
    "вашу":  "Possessive determiner 'вашу' (your, pl.), accusative singular feminine.",
}

# Demonstratives: этот / эта / это / эти, тот / та / то / те + key declined
# forms.
_DEMONSTRATIVES: Dict[str, str] = {
    # этот (proximal)
    "этот":   "Demonstrative 'этот' (this), masculine singular nominative. Declines like an adjective and agrees with the head noun in case, gender, and number.",
    "эта":    "Demonstrative 'эта' (this), feminine singular nominative.",
    "это":    "Demonstrative / deictic 'это'. As a determiner with a neuter noun: 'this' (neuter sg. nom.). As a free-standing copular substitute: 'this is / it is X' (invariant).",
    "эти":    "Demonstrative 'эти' (these), nominative plural.",
    "этого":  "Demonstrative 'этого' (this), genitive / animate-accusative singular masculine/neuter.",
    "этой":   "Demonstrative 'этой' (this), genitive/dative/instrumental/prepositional singular feminine.",
    "этому":  "Demonstrative 'этому' (this), dative singular masculine/neuter.",
    "этим":   "Demonstrative 'этим', instrumental singular masculine/neuter OR dative plural.",
    "этом":   "Demonstrative 'этом' (this), prepositional singular masculine/neuter.",
    "этих":   "Demonstrative 'этих' (these), genitive / animate-accusative / prepositional plural.",
    "этими":  "Demonstrative 'этими' (these), instrumental plural.",
    "эту":    "Demonstrative 'эту' (this), accusative singular feminine.",
    # тот (distal)
    "тот":    "Demonstrative 'тот' (that), masculine singular nominative.",
    "та":     "Demonstrative 'та' (that), feminine singular nominative.",
    "то":     "Demonstrative 'то' (that), neuter singular nominative — also serves as the antecedent in correlative constructions ('то, что...' = 'that which...').",
    "те":     "Demonstrative 'те' (those), nominative plural.",
    "того":   "Demonstrative 'того' (that), genitive / animate-accusative singular masculine/neuter.",
    "той":    "Demonstrative 'той' (that), genitive/dative/instrumental/prepositional singular feminine.",
    "тому":   "Demonstrative 'тому' (that), dative singular masculine/neuter.",
    "тем":    "Demonstrative 'тем', instrumental singular masculine/neuter OR dative plural.",
    "том":    "Demonstrative 'том' (that), prepositional singular masculine/neuter.",
    "тех":    "Demonstrative 'тех' (those), genitive / animate-accusative / prepositional plural.",
    "теми":   "Demonstrative 'теми' (those), instrumental plural.",
    "ту":     "Demonstrative 'ту' (that), accusative singular feminine.",
    # такой
    "такой":  "Demonstrative-quality 'такой' (such, this kind of), masculine singular nominative. Adjectival paradigm.",
    "такая":  "Demonstrative-quality 'такая' (such), feminine singular nominative.",
    "такое":  "Demonstrative-quality 'такое' (such), neuter singular nominative.",
    "такие":  "Demonstrative-quality 'такие' (such), nominative plural.",
}

# Interrogative / relative pronouns and their declensions.
_INTERROGATIVES: Dict[str, str] = {
    # кто
    "кто":   "Interrogative/relative pronoun 'кто' (who), nominative case — animate-only. Always takes masculine singular agreement even with female referents. As an interrogative it heads a wh-question; as a relative it introduces a clause with antecedent 'тот'.",
    "кого":  "Interrogative/relative pronoun 'кого' (whom / of whom), genitive or accusative case (syncretic for animate). Direct object or genitive complement of a question/relative clause.",
    "кому":  "Interrogative/relative pronoun 'кому' (to whom), dative case.",
    "кем":   "Interrogative/relative pronoun 'кем' (by whom / with whom), instrumental case.",
    "ком":   "Interrogative/relative pronoun 'ком' (about whom), prepositional case (always after о/об: 'о ком').",
    # что
    "что":   "Token 'что' has TWO readings: (a) interrogative/relative pronoun 'что' (what), nominative or accusative case (inanimate, syncretic) — questioned over or used as object; (b) complementizer 'что' (that) — introduces a finite subordinate clause after a verb of speech/cognition. Disambiguate by clausal function.",
    "чего":  "Interrogative/relative pronoun 'чего' (of what), genitive case.",
    "чему":  "Interrogative/relative pronoun 'чему' (to what), dative case.",
    "чем":   "Interrogative/relative pronoun 'чем' (by what / with what), instrumental case — also a comparative conjunction ('than') and a question word ('how, why').",
    "чём":   "Interrogative/relative pronoun 'чём' (about what), prepositional case (always after о/об).",
    # какой / который / чей
    "какой": "Interrogative/relative pronoun 'какой' (what kind / which), masculine singular nominative. Adjectival paradigm; agrees with the head noun.",
    "какая": "Interrogative/relative pronoun 'какая' (what kind), feminine singular nominative.",
    "какое": "Interrogative/relative pronoun 'какое' (what kind), neuter singular nominative.",
    "какие": "Interrogative/relative pronoun 'какие' (what kind), nominative plural.",
    "какого":"Interrogative/relative pronoun 'какого', genitive / animate-acc singular masculine/neuter.",
    "какой_f":"Interrogative/relative pronoun 'какой', genitive/dative/instrumental/prepositional feminine sg.",
    "которой":"Relative pronoun 'которой' (which), feminine singular oblique case (gen/dat/inst/prep).",
    "который":"Relative pronoun 'который' (which / who), masculine singular nominative. Agrees with the antecedent in gender and number; takes its case from its function in the relative clause.",
    "которая":"Relative pronoun 'которая' (which / who), feminine singular nominative.",
    "которое":"Relative pronoun 'которое' (which), neuter singular nominative.",
    "которые":"Relative pronoun 'которые' (which / who), nominative plural.",
    "которого":"Relative pronoun 'которого', genitive / animate-acc singular masculine/neuter.",
    "которому":"Relative pronoun 'которому', dative singular masculine/neuter.",
    "которым":"Relative pronoun 'которым', instrumental singular masculine/neuter or dative plural.",
    "котором":"Relative pronoun 'котором', prepositional singular masculine/neuter.",
    "которых":"Relative pronoun 'которых', genitive / animate-acc / prepositional plural.",
    "которыми":"Relative pronoun 'которыми', instrumental plural.",
    "чей":   "Interrogative/relative pronoun 'чей' (whose), masculine singular nominative. Adjectival paradigm.",
    "чья":   "Interrogative/relative pronoun 'чья' (whose), feminine singular nominative.",
    "чьё":   "Interrogative/relative pronoun 'чьё' (whose), neuter singular nominative.",
    "чьи":   "Interrogative/relative pronoun 'чьи' (whose), nominative plural.",
}

# Wh-adverbs.
_WH_ADVERBS: Dict[str, str] = {
    "где":     "Interrogative/relative adverb 'где' (where — static location). Used in questions and relative clauses of place.",
    "куда":    "Interrogative/relative adverb 'куда' (where to — direction). Distinct from 'где'; pairs with motion verbs.",
    "откуда":  "Interrogative/relative adverb 'откуда' (where from — source). Pairs with motion verbs of departure.",
    "когда":   "Interrogative/relative/subordinator 'когда' (when). As an interrogative it heads a wh-question; as a subordinator it introduces a temporal clause.",
    "как":     "Token 'как' has multiple readings: (a) interrogative adverb 'how' in questions; (b) comparator 'as, like' introducing similes; (c) temporal subordinator 'as, when'. Disambiguate by syntactic role.",
    "почему":  "Interrogative adverb 'почему' (why — reason / cause). Heads questions about cause.",
    "зачем":   "Interrogative adverb 'зачем' (for what purpose). Heads questions about purpose, contrast with 'почему'.",
    "сколько": "Interrogative/quantifier 'сколько' (how much / how many). Governs genitive plural of count nouns and genitive singular of mass nouns.",
}

# Negative pronouns and adverbs (n-words).
_NEGATIVE_PRONOUNS: Dict[str, str] = {
    "никто":   "Negative pronoun 'никто' (nobody), nominative — animate. Requires preverbal 'не' (negative concord): 'Никто не пришёл'.",
    "никого":  "Negative pronoun 'никого' (nobody), genitive/accusative case. Requires preverbal 'не'.",
    "никому":  "Negative pronoun 'никому' (to nobody), dative case.",
    "никем":   "Negative pronoun 'никем' (by nobody), instrumental case.",
    "ничто":   "Negative pronoun 'ничто' (nothing), nominative — inanimate.",
    "ничего":  "Negative pronoun 'ничего' (nothing / of nothing), genitive case — also the canonical genitive of negation form.",
    "ничему":  "Negative pronoun 'ничему' (to nothing), dative.",
    "ничем":   "Negative pronoun 'ничем' (by nothing / with nothing), instrumental.",
    "никакой": "Negative pronoun 'никакой' (no kind, none), masculine singular nominative. Adjectival paradigm.",
    "ничей":   "Negative pronoun 'ничей' (nobody's), masculine singular nominative.",
    "никогда": "Negative adverb 'никогда' (never). Requires preverbal 'не'.",
    "нигде":   "Negative adverb 'нигде' (nowhere — static).",
    "никуда":  "Negative adverb 'никуда' (to nowhere — direction).",
    "ниоткуда":"Negative adverb 'ниоткуда' (from nowhere — source).",
    "никак":   "Negative adverb 'никак' (in no way / not at all).",
    "негде":   "Negative-quantifier predicative 'негде' (there is nowhere [to do X]) — used with an infinitive: 'мне негде сидеть'.",
    "некогда": "Negative-quantifier predicative 'некогда' (there is no time [to do X]) — used with an infinitive.",
    "некого":  "Negative pronoun 'некого' (there is nobody [to do X to]), genitive/accusative — special construction with dative experiencer + infinitive.",
    "нечего":  "Negative pronoun 'нечего' (there is nothing [to do]), genitive — special construction with dative experiencer + infinitive.",
}

# Modal predicatives + modal verbs.
_MODALS: Dict[str, str] = {
    "могу":    "Modal verb 'могу' (I can / I am able), 1st-person singular present — lemma 'мочь' (imperfective).",
    "можешь":  "Modal verb 'можешь' (you can), 2nd-person singular present — lemma 'мочь'.",
    "может":   "Modal verb 'может' (he/she/it can), 3rd-person singular present — lemma 'мочь'. Also the impersonal predicative 'может быть' (maybe).",
    "можем":   "Modal verb 'можем' (we can), 1st-person plural present — lemma 'мочь'.",
    "можете":  "Modal verb 'можете' (you can, pl./formal), 2nd-person plural present — lemma 'мочь'.",
    "могут":   "Modal verb 'могут' (they can), 3rd-person plural present — lemma 'мочь'.",
    "хочу":    "Modal verb 'хочу' (I want), 1st-person singular present — lemma 'хотеть' (mixed conjugation, irregular).",
    "хочешь":  "Modal verb 'хочешь' (you want), 2nd-person singular present — lemma 'хотеть'.",
    "хочет":   "Modal verb 'хочет' (he/she wants), 3rd-person singular present — lemma 'хотеть'.",
    "хотим":   "Modal verb 'хотим' (we want), 1st-person plural — lemma 'хотеть'.",
    "хотите":  "Modal verb 'хотите' (you want, pl.), 2nd-person plural — lemma 'хотеть'.",
    "хотят":   "Modal verb 'хотят' (they want), 3rd-person plural — lemma 'хотеть'.",
    "должен":  "Modal predicative 'должен' (must, obliged) — short-form adjective, masculine singular. Feminine 'должна', neuter 'должно', plural 'должны'. Takes infinitive complement.",
    "должна":  "Modal predicative 'должна' (must), feminine singular short-form.",
    "должно":  "Modal predicative 'должно' (must), neuter singular short-form.",
    "должны":  "Modal predicative 'должны' (must), plural short-form.",
    "нужно":   "Modal predicative 'нужно' (it is necessary / one needs). Impersonal — logical subject in dative: 'мне нужно идти'.",
    "надо":    "Modal predicative 'надо' (it is necessary, one must) — colloquial equivalent of 'нужно', impersonal with dative experiencer.",
    "нельзя":  "Modal predicative 'нельзя' (one cannot / it is forbidden). Impersonal, with dative experiencer + infinitive.",
    "можно":   "Modal predicative 'можно' (it is possible / one may). Impersonal, with dative experiencer + infinitive.",
}

# Particles — fully separated, NOT lumped under a single 'particle' role at
# advanced complexity (per the Phase-1 spec).
_PARTICLES: Dict[str, Tuple[str, str]] = {
    "бы":     ("conditional_particle", "Conditional / aspectual particle 'бы'. Combines with a past-tense verb to form the conditional ('Я бы пошёл' = 'I would go'). Clitic-like — typically attaches after a fronted constituent."),
    "б":      ("conditional_particle", "Conditional particle 'б' — short variant of 'бы', used after a vowel ('Я б знал…')."),
    "не":     ("negation_particle",    "Negation particle 'не' (not). Placed immediately before the negated constituent. Triggers genitive of negation on direct objects in some contexts."),
    "ни":     ("negation_particle",    "Emphatic / scalar negative particle 'ни' (not even, not a single). Required after negative pronouns ('никто ни о чём') and in scalar minimisers."),
    "же":     ("particle",             "Contrastive emphasis particle 'же' (after all, then). Marks topic-shift, contradiction, or emphatic identification."),
    "ли":     ("particle",             "Interrogative particle 'ли' (whether / yes-no Q marker). Fronts the verb + ли in formal yes-no questions: 'Идёшь ли ты?'"),
    "ведь":   ("particle",             "Discourse particle 'ведь' (after all / you know). Appeals to shared knowledge."),
    "разве":  ("particle",             "Interrogative particle 'разве' — introduces a rhetorical or surprise question ('разве он пришёл?')."),
    "неужели":("particle",             "Interrogative particle 'неужели' — expresses disbelief or surprise ('неужели правда?')."),
    "вот":    ("particle",             "Demonstrative discourse particle 'вот' (here is / behold). Often introduces a referent in spoken Russian."),
    "уж":     ("particle",             "Intensifying particle 'уж' (already / really). Emphasises the predicate."),
    "только": ("particle",             "Restrictive focus particle 'только' (only, just)."),
    "даже":   ("particle",             "Scalar focus particle 'даже' (even)."),
    "именно": ("particle",             "Identifying focus particle 'именно' (precisely, exactly)."),
}

# Forms of быть.
_BYT_PARADIGM: Dict[str, str] = {
    "быть":   "Infinitive of 'быть' (to be) — the only Russian copula. Present tense is silent in standard Russian; past and future are overt.",
    "был":    "Past tense of 'быть' (was), masculine singular. Predicate complement after past 'быть' takes instrumental ('он был студентом').",
    "была":   "Past tense of 'быть' (was), feminine singular.",
    "было":   "Past tense of 'быть' (was), neuter singular — also the impersonal copula in past ('было холодно').",
    "были":   "Past tense of 'быть' (were), plural.",
    "буду":   "Future tense of 'быть' (I will be), 1st-person singular. Combines with imperfective infinitive to form the periphrastic imperfective future ('буду читать').",
    "будешь": "Future tense of 'быть' (you will be), 2nd-person singular.",
    "будет":  "Future tense of 'быть' (he/she/it will be), 3rd-person singular.",
    "будем":  "Future tense of 'быть' (we will be), 1st-person plural.",
    "будете": "Future tense of 'быть' (you will be, pl.), 2nd-person plural.",
    "будут":  "Future tense of 'быть' (they will be), 3rd-person plural.",
    "есть":   "Existential / emphatic 'есть' (there is, exists). The 3rd-person present of 'быть'; survives in existential and emphatic identification ('у меня есть книга'). Also a homograph of 'есть' = 'to eat' (lemma есть/съесть).",
    "нет":    "Negative existential 'нет' (there is no — governs genitive). An unanalysed contraction of 'не есть'; complement is in genitive ('книги нет' = 'there is no book').",
}

# Conjunctions: coordinating + subordinating.
_COORDINATING: Dict[str, str] = {
    "и":      "Coordinating conjunction 'и' (and). Joins phrases or clauses of equal status; can also function as a focus particle ('also, even').",
    "а":      "Coordinating conjunction 'а' (and / but — contrastive). Marks a soft contrast or topic shift, less adversative than 'но'.",
    "но":     "Coordinating conjunction 'но' (but). Marks a strong adversative contrast.",
    "или":    "Coordinating conjunction 'или' (or). Offers an alternative.",
    "либо":   "Coordinating conjunction 'либо' (or — emphatic alternative). Often paired: 'либо…либо…'.",
    "да":     "Coordinating conjunction 'да' (and — colloquial / literary). Also affirmative answer particle 'yes' (homograph).",
    "тоже":   "Coordinating adverb 'тоже' (also, too). Used when the subject is the same kind of entity.",
    "также":  "Coordinating adverb 'также' (also, in addition). More bookish than 'тоже'; used when adding a new predicate.",
}

_SUBORDINATING: Dict[str, str] = {
    "что__sub":  "Subordinating conjunction (complementizer) 'что' (that). Introduces a finite subordinate clause after a verb of speech/cognition. Distinct from interrogative pronoun 'что'.",
    "чтобы":  "Subordinating conjunction 'чтобы' (so that, in order to / for X to). Triggers either subjunctive (past + бы implicit) or infinitive complement.",
    "если":   "Subordinating conjunction 'если' (if). Introduces a conditional clause; combined with 'бы' for counterfactuals.",
    "пока":   "Subordinating conjunction 'пока' (while / until). Temporal subordinator.",
    "хотя":   "Subordinating conjunction 'хотя' (although, even though). Concessive.",
    "поскольку":"Subordinating conjunction 'поскольку' (since, because). Causal — formal.",
    "ибо":    "Subordinating conjunction 'ибо' (for, because) — literary/archaic.",
    "словно": "Subordinating conjunction 'словно' (as if, as though). Comparative.",
    "будто":  "Subordinating conjunction 'будто' (as if, supposedly). Comparative / reportative.",
}

# Prepositions with governed cases.
_PREPOSITIONS: Dict[str, Tuple[str, str]] = {
    "в":     ("acc/prep",     "in / into. Governs accusative for motion (в школу — to school) or prepositional for location (в школе — at school)."),
    "во":    ("acc/prep",     "in / into — variant of 'в' before consonant clusters."),
    "на":    ("acc/prep",     "on / onto / at. Governs accusative for motion (на работу) or prepositional for location (на работе)."),
    "под":   ("acc/inst",     "under. Governs accusative for motion (под стол) or instrumental for location (под столом)."),
    "над":   ("instrumental", "above / over. Governs instrumental."),
    "перед": ("instrumental", "in front of / before. Governs instrumental."),
    "за":    ("acc/inst",     "behind / for. Governs accusative for motion or duration (за час) or instrumental for static location."),
    "между": ("instrumental", "between / among. Governs instrumental (sometimes genitive in fixed phrases)."),
    "с":     ("gen/inst",     "from / off (genitive: с горы) OR with (instrumental: с другом). Disambiguate by case of complement."),
    "со":    ("gen/inst",     "from / off / with — variant of 'с' before consonant clusters."),
    "у":     ("genitive",     "at the place of / by / near (also marks possession: 'у меня есть'). Governs genitive."),
    "к":     ("dative",       "toward / to (a person). Governs dative."),
    "ко":    ("dative",       "toward / to — variant of 'к' before consonant clusters."),
    "от":    ("genitive",     "from (a source). Governs genitive."),
    "из":    ("genitive",     "out of / from. Governs genitive."),
    "до":    ("genitive",     "until / up to / before. Governs genitive."),
    "около": ("genitive",     "near / about. Governs genitive."),
    "вокруг":("genitive",     "around. Governs genitive."),
    "после": ("genitive",     "after. Governs genitive."),
    "без":   ("genitive",     "without. Governs genitive."),
    "для":   ("genitive",     "for (the benefit of). Governs genitive."),
    "из-за": ("genitive",     "because of / from behind. Governs genitive."),
    "из-под":("genitive",     "from under. Governs genitive."),
    "через": ("accusative",   "across / through / in (time-from-now). Governs accusative."),
    "по":    ("dat/acc/prep", "along / by / according to (dative); up to / including (accusative); after (prepositional). Disambiguate by complement case."),
    "о":     ("prepositional","about (topic). Governs prepositional."),
    "об":    ("prepositional","about — variant of 'о' before vowels."),
    "обо":   ("prepositional","about — variant of 'о' before pronouns: 'обо мне'."),
    "при":   ("prepositional","at / in the presence of / attached to. Governs prepositional."),
    "ради":  ("genitive",     "for the sake of. Governs genitive."),
    "против":("genitive",     "against / opposite. Governs genitive."),
    "вместо":("genitive",     "instead of. Governs genitive."),
    "благодаря":("dative",    "thanks to. Governs dative."),
    "согласно":("dative",     "in accordance with. Governs dative."),
    "вопреки":("dative",      "despite / contrary to. Governs dative."),
    "среди": ("genitive",     "among. Governs genitive."),
    "вдоль": ("genitive",     "along. Governs genitive."),
    "мимо":  ("genitive",     "past / by. Governs genitive."),
}

# Animate masculine nouns frequently encountered — used so the fallback can
# correctly state "accusative — animate masculines take the genitive form for
# accusative" when relevant. Lemma → (gloss).
_ANIMATE_MASCULINES = {
    "мальчик", "отец", "врач", "друг", "брат", "сын", "муж", "учитель",
    "студент", "человек", "мужчина", "ребёнок", "ребенок", "сосед",
    "папа", "дедушка", "дядя", "юноша", "пёс", "пес", "кот", "конь",
}


class RuFallbacks:
    """Rule-based fallback analysis for Russian grammar."""

    def __init__(self, config: RuConfig):
        self.config = config

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def create_fallback(self, sentence: str, complexity: str) -> Dict[str, Any]:
        """Create a basic rule-based grammar analysis with rich explanations.

        Sets `is_fallback: True` on the result so the validator caps
        confidence at 0.3 (CLAUDE.md fallback contract).
        """
        words = sentence.split()
        word_explanations: List[Dict[str, Any]] = []

        for word in words:
            clean = word.strip(".,!?;:\"'()[]«»…—-")
            role, individual_meaning, case, gender, number = self._classify_word(
                clean, complexity
            )

            display_role = self._soften_role(role, complexity)
            color = self.config.get_color_for_role(display_role, complexity)

            # Punctuation-only tokens get a brief description.
            is_punct = clean == ""
            if is_punct:
                display_role = "other"
                color = self.config.get_color_for_role("other", complexity)
                individual_meaning = (
                    "Punctuation token; structures the clause boundary."
                )

            display = f"{word} ({display_role}): {individual_meaning}"

            word_explanations.append({
                "word": word,
                "role": display_role,
                "color": color,
                "meaning": display,
                "individual_meaning": individual_meaning,
                "case": case,
                "gender": gender,
                "number": number,
                "tense": "",
                "aspect": "",
            })

        return {
            "word_explanations": word_explanations,
            "overall_structure": "Russian sentence (rule-based fallback analysis).",
            "sentence_structure": "Russian sentence (rule-based fallback analysis).",
            "explanations": {
                item["word"]: item["meaning"] for item in word_explanations
            },
            "elements": {
                item["word"]: item["role"] for item in word_explanations
            },
            "grammar_notes": (
                "Rule-based fallback — AI unavailable. Closed-class words come "
                "from lookup tables (full coverage of personal pronouns, "
                "possessives, demonstratives, prepositions with governed cases, "
                "modals, particles, быть-paradigm, conjunctions). Open-class "
                "words rely on Cyrillic suffix heuristics for case/gender/aspect "
                "and may be incorrect."
            ),
            "confidence": 0.3,
            "is_fallback": True,
        }

    # Compatibility shim — older callers may invoke `analyze_with_rules`.
    def analyze_with_rules(
        self, sentence: str, target_word: str, complexity: str
    ) -> Dict[str, Any]:
        return self.create_fallback(sentence, complexity)

    # ------------------------------------------------------------------
    # Per-word classification
    # ------------------------------------------------------------------

    def _classify_word(
        self, word: str, complexity: str
    ) -> Tuple[str, str, str, str, str]:
        """Classify a single word.

        Returns (role, individual_meaning, case, gender, number).
        Order of checks is critical — closed-class lookups always win over
        suffix heuristics so мой/твой/они/её etc. are not misclassified.
        """
        if not word:
            return "other", "Token with no content.", "", "", ""

        lower = word.lower()

        # --- 1. Particles (must precede other lookups; particles are short) -
        if lower in _PARTICLES:
            role, expl = _PARTICLES[lower]
            return role, expl, "", "", ""

        # --- 2. быть paradigm ----------------------------------------------
        if lower in _BYT_PARADIGM:
            return "auxiliary", _BYT_PARADIGM[lower], "", "", ""

        # --- 3. Personal pronouns ------------------------------------------
        # 'их' / 'им' / 'ним' have collisions with 3pl-dative — handle
        # syncretism by preferring the simpler entry.
        if lower in _PERSONAL_PRONOUNS:
            case, person_num, expl = _PERSONAL_PRONOUNS[lower]
            gender = "masculine" if ".m" in person_num else (
                "feminine" if ".f" in person_num else (
                    "neuter" if ".n" in person_num else ""
                )
            )
            number = "plural" if "pl" in person_num else "singular"
            return "personal_pronoun", expl, case, gender, number

        # --- 4. Reflexive себя ---------------------------------------------
        if lower in _REFLEXIVE_PRONOUNS:
            case, expl = _REFLEXIVE_PRONOUNS[lower]
            return "reflexive_pronoun", expl, case, "", ""

        # --- 5. Possessive determiners -------------------------------------
        if lower in _POSSESSIVE_DETERMINERS:
            return "possessive_determiner", _POSSESSIVE_DETERMINERS[lower], "", "", ""

        # --- 6. Demonstratives ---------------------------------------------
        if lower in _DEMONSTRATIVES:
            return "demonstrative", _DEMONSTRATIVES[lower], "", "", ""

        # --- 7. Wh-pronouns / interrogatives -------------------------------
        if lower in _INTERROGATIVES:
            # 'который' family is relative; 'кто/что/какой/чей' are
            # interrogative (also relative in some contexts).
            role = (
                "relative_pronoun"
                if lower.startswith("котор")
                else "interrogative_pronoun"
            )
            return role, _INTERROGATIVES[lower], "", "", ""

        # --- 8. Wh-adverbs -------------------------------------------------
        if lower in _WH_ADVERBS:
            return "adverb", _WH_ADVERBS[lower], "", "", ""

        # --- 9. Negative pronouns / adverbs --------------------------------
        if lower in _NEGATIVE_PRONOUNS:
            role = "negative_pronoun"
            return role, _NEGATIVE_PRONOUNS[lower], "", "", ""

        # --- 10. Modals ----------------------------------------------------
        if lower in _MODALS:
            return "modal_verb", _MODALS[lower], "", "", ""

        # --- 11. Conjunctions ----------------------------------------------
        if lower in _COORDINATING:
            return "coordinating_conjunction", _COORDINATING[lower], "", "", ""
        # Subordinating 'что' — handled separately because 'что' is also a
        # pronoun. The fallback prefers the pronoun reading; a real parser
        # would disambiguate by clausal context.
        if lower in _SUBORDINATING:
            return "subordinating_conjunction", _SUBORDINATING[lower], "", "", ""

        # --- 12. Prepositions ----------------------------------------------
        if lower in _PREPOSITIONS:
            governs, gloss = _PREPOSITIONS[lower]
            expl = (
                f"Preposition '{word}' meaning '{gloss}'. Governs the {governs} case — "
                f"the noun phrase that follows must take that case."
            )
            return "preposition", expl, "", "", ""

        # --- 13. Reflexive verbs (-ся / -сь) -------------------------------
        if (lower.endswith("ся") and len(word) > 3) or (
            lower.endswith("сь") and len(word) > 3
        ):
            expl = (
                f"Reflexive verb '{word}'. The -ся / -сь clitic marks reflexivity in one of "
                f"five canonical readings (true reflexive / reciprocal / passive / middle / "
                f"lexicalized intransitive); without context the subtype cannot be determined "
                f"by rule and the AI explanation is needed."
            )
            return "reflexive_verb", expl, "", "", ""

        # --- 14. Gerunds ---------------------------------------------------
        # Present gerund -я / -а after consonant; past gerund -в / -вши.
        if re.search(r"(вши|в)$", lower) and len(word) > 4:
            return "gerund", (
                f"Past gerund (verbal adverb) '{word}', from a perfective stem + -в/-вши "
                f"(прочитав = 'having read'). Uninflected; subject must coincide with the "
                f"main-clause subject."
            ), "", "", ""

        # --- 15. Participles -----------------------------------------------
        if re.search(r"(ущий|ющий|ащий|ящий|ущая|ющая|ущее|ющее|ущие|ющие)$", lower):
            return "present_active_participle", (
                f"Present active participle '{word}', formed from an imperfective stem + "
                f"-ущ/-ющ/-ащ/-ящ. Declines like a long-form adjective and agrees with the "
                f"noun it modifies in case, gender, and number."
            ), "", "", ""
        if re.search(r"(вший|вшая|вшее|вшие|ший)$", lower):
            return "past_active_participle", (
                f"Past active participle '{word}', formed from a verb stem + -вш/-ш. "
                f"Declines like a long-form adjective; modifies the noun whose action it describes."
            ), "", "", ""
        if re.search(r"(емый|емая|емое|емые|имый|имая|имое|имые)$", lower):
            return "present_passive_participle", (
                f"Present passive participle '{word}', formed from imperfective transitive "
                f"stem + -ем/-им. Rare in modern speech; appears in formal/written register."
            ), "", "", ""
        if re.search(r"(нный|нная|нное|нные|тый|тая|тое|тые|анный|енный|ённый)$", lower):
            return "past_passive_participle", (
                f"Past passive participle '{word}', formed from a perfective transitive stem + "
                f"-нн/-енн/-ённ/-т. Used in passive constructions (often in short form) and as "
                f"a noun-modifying adjective."
            ), "", "", ""

        # --- 16. Verbal nouns (-ние / -тие) --------------------------------
        if re.search(r"(ние|тие)$", lower) and len(word) > 4:
            return "verbal_noun", (
                f"Verbal noun '{word}'. The -ние / -тие suffix derives a neuter action noun "
                f"from a verb stem (e.g. чтение = 'reading')."
            ), "nominative", "neuter", "singular"

        # --- 17. Adjectives (long form) ------------------------------------
        # Hard-stem long-form adjective endings.
        if re.search(r"(ый|ий|ой)$", lower) and len(word) > 3:
            return "adjective", (
                f"Long-form adjective '{word}', nominative singular masculine. Declines for "
                f"case × gender × number; used both attributively and predicatively."
            ), "nominative", "masculine", "singular"
        if re.search(r"(ая|яя)$", lower) and len(word) > 3:
            return "adjective", (
                f"Long-form adjective '{word}', nominative singular feminine. Agrees with a "
                f"feminine head noun."
            ), "nominative", "feminine", "singular"
        if re.search(r"(ое|ее)$", lower) and len(word) > 3:
            return "adjective", (
                f"Long-form adjective '{word}', nominative singular neuter. Agrees with a "
                f"neuter head noun."
            ), "nominative", "neuter", "singular"
        if re.search(r"(ые|ие)$", lower) and len(word) > 3:
            return "adjective", (
                f"Long-form adjective '{word}', nominative plural. Agrees with a plural head "
                f"noun in case (here nominative)."
            ), "nominative", "", "plural"

        # --- 18. Verbs (conjugated) ----------------------------------------
        # Present-tense / perfective-future endings.
        # Note: bare -у / -ю are EXCLUDED because they collide with the
        # feminine accusative singular noun ending (книгу, школу, маму). For
        # 1sg present we rely on -аю/-яю/-ую/-ою/-ею and the -у-after-stem
        # patterns; words like читаю / пишу still match via the longer endings.
        # Past-tense endings -л/-ла/-ло/-ли (with optional -ся/-сь).
        verb_match = re.search(
            r"(ешь|ёшь|ет|ёт|ем|ём|ете|ёте|ут|ют|ишь|ит|им|ите|ат|ят|"
            r"аю|яю|ую|ою|ею|ую)$",
            lower,
        )
        past_match = re.search(r"(л|ла|ло|ли)$", lower)
        if verb_match and len(word) > 2:
            aspect = self._guess_aspect(lower)
            expl = (
                f"Verb '{word}'. Conjugated finite form (Russian conjugates by person and "
                f"number; aspect is lexical). Heuristic aspect guess: {aspect} — based on "
                f"prefix/suffix shape; AI explanation needed for tense and exact lemma."
            )
            return "verb", expl, "", "", ""
        if past_match and len(word) > 3:
            gender = (
                "masculine" if lower.endswith("л") else
                "feminine" if lower.endswith("ла") else
                "neuter" if lower.endswith("ло") else ""
            )
            number = "plural" if lower.endswith("ли") else "singular"
            aspect = self._guess_aspect(lower)
            expl = (
                f"Verb '{word}'. Past-tense form (-л / -ла / -ло / -ли); past tense in Russian "
                f"agrees with the subject in gender (singular) or number (plural), NOT in "
                f"person. Heuristic aspect guess: {aspect} — based on prefix shape."
            )
            return "verb", expl, "", gender, number

        # --- 19. Numerals --------------------------------------------------
        if lower in {"один", "одна", "одно", "одни"}:
            gender = (
                "masculine" if lower == "один" else
                "feminine" if lower == "одна" else
                "neuter" if lower == "одно" else ""
            )
            number = "plural" if lower == "одни" else "singular"
            expl = (
                f"Numeral 'один' (one), {gender} {number} nominative — declines like an "
                f"adjective and agrees with the counted noun."
            )
            return "numeral", expl, "nominative", gender, number
        if lower in {"два", "две", "три", "четыре"}:
            expl = (
                f"Numeral '{word}'. In nominative or accusative-inanimate, governs GENITIVE "
                f"SINGULAR on the counted noun (two/three/four + gen.sg) — a classic Russian "
                f"agreement quirk."
            )
            return "numeral", expl, "nominative", "", ""
        if lower in {
            "пять", "шесть", "семь", "восемь", "девять", "десять",
            "одиннадцать", "двенадцать", "пятнадцать", "двадцать",
            "сто", "тысяча", "миллион",
        }:
            expl = (
                f"Numeral '{word}'. In nominative or accusative-inanimate, governs GENITIVE "
                f"PLURAL on the counted noun (5+ → gen.pl: пять столов, десять книг)."
            )
            return "numeral", expl, "nominative", "", ""

        # --- 20. Nouns (Cyrillic suffix heuristics) ------------------------
        if lower in _ANIMATE_MASCULINES or any(
            lower.startswith(stem) for stem in _ANIMATE_MASCULINES
        ):
            expl = (
                f"Noun '{word}', likely animate masculine singular. For animate masculines the "
                f"accusative is shaped like the genitive (e.g. 'вижу мальчика') — a key "
                f"animacy-driven syncretism."
            )
            return "noun", expl, "nominative", "masculine", "singular"

        # Consonant-final → masc nom sg
        if re.search(r"[бвгджзйклмнпрстфхцчшщ]$", lower) and len(word) > 1:
            expl = (
                f"Noun '{word}', heuristically masculine singular nominative (2nd declension). "
                f"Most consonant-final Russian nouns are masculine; case must be confirmed by "
                f"context."
            )
            return "noun", expl, "nominative", "masculine", "singular"
        # -ь → could be masculine or 3rd-decl feminine — flag ambiguity.
        if lower.endswith("ь") and len(word) > 1:
            expl = (
                f"Noun '{word}' ending in -ь. Could be masculine (2nd decl., e.g. день, словарь) "
                f"or feminine 3rd-declension (ночь, дверь, мать). Ambiguous without lookup; "
                f"defaulting to masculine singular nominative."
            )
            return "noun", expl, "nominative", "masculine", "singular"
        if re.search(r"(а|я)$", lower) and len(word) > 1:
            expl = (
                f"Noun '{word}', heuristically feminine singular nominative (1st declension, "
                f"-а/-я ending). Note: a few -а/-я nouns referring to people are masculine "
                f"(мужчина, дядя) — ambiguity must be resolved lexically."
            )
            return "noun", expl, "nominative", "feminine", "singular"
        if re.search(r"(у|ю)$", lower) and len(word) > 2:
            expl = (
                f"Noun '{word}', heuristically feminine singular ACCUSATIVE (1st declension, "
                f"-у/-ю ending — the canonical feminine accusative singular form, e.g. "
                f"книгу < книга, школу < школа). Direct object of a transitive verb."
            )
            return "noun", expl, "accusative", "feminine", "singular"
        if re.search(r"(о|е|ё)$", lower) and len(word) > 1:
            expl = (
                f"Noun '{word}', heuristically neuter singular nominative (-о/-е/-ё ending, "
                f"2nd declension)."
            )
            return "noun", expl, "nominative", "neuter", "singular"
        if re.search(r"(ы|и)$", lower) and len(word) > 1:
            expl = (
                f"Noun '{word}', heuristically nominative plural (-ы/-и ending). Gender depends "
                f"on the singular form, which cannot be inferred from the plural alone."
            )
            return "noun", expl, "nominative", "", "plural"

        # --- 21. Default fallback ------------------------------------------
        return (
            "other",
            f"Word '{word}' — POS could not be determined by the rule-based fallback.",
            "", "", "",
        )

    # ------------------------------------------------------------------
    # Aspect heuristic
    # ------------------------------------------------------------------

    def _guess_aspect(self, lower: str) -> str:
        """Heuristically guess perfective vs. imperfective from prefix/suffix.

        Russian aspect is lexical, but a few prefixes (по-, на-, про-, за-,
        пере-, вы-, с-, у-) commonly perfectivise their imperfective bases,
        and the -ива-/-ыва- suffix imperfectivises perfectives. The fallback
        explicitly admits this is heuristic.
        """
        for pref in self.config.perfective_prefixes:
            if lower.startswith(pref) and len(lower) > len(pref) + 2:
                # -ива/-ыва imperfective derived from a perfective is the
                # canonical exception.
                if "ыва" in lower or "ива" in lower:
                    return "imperfective (heuristic, -ыва/-ива suffix overrides prefix)"
                return f"perfective (heuristic, '{pref}-' prefix)"
        if "ыва" in lower or "ива" in lower:
            return "imperfective (heuristic, -ыва/-ива suffix)"
        return "imperfective (default)"

    # ------------------------------------------------------------------
    # Morphological feature extraction (compat shim)
    # ------------------------------------------------------------------

    def _identify_part_of_speech(self, word: str, sentence: str) -> str:
        role, _, _, _, _ = self._classify_word(word, "intermediate")
        return role

    def _extract_morphological_features(self, word: str) -> Dict[str, str]:
        role, _, case, gender, number = self._classify_word(word, "intermediate")
        return {"role": role, "case": case, "gender": gender, "number": number}

    # ------------------------------------------------------------------
    # Role softening per complexity
    # ------------------------------------------------------------------

    @staticmethod
    def _soften_role(role: str, complexity: str) -> str:
        """Map a fine-grained role to the simpler one used at lower complexity."""
        if complexity == "advanced":
            return role
        if complexity == "intermediate":
            inter_map = {
                "imperfective_verb": "verb",
                "perfective_verb": "verb",
                "present_active_participle": "verb",
                "past_active_participle": "verb",
                "present_passive_participle": "verb",
                "past_passive_participle": "verb",
                "gerund": "verb",
                "verbal_noun": "noun",
                "coordinating_conjunction": "conjunction",
                "subordinating_conjunction": "conjunction",
                "aspectual_particle": "particle",
                "conditional_particle": "particle",
                "negation_particle": "particle",
                "negative_pronoun": "pronoun",
                "interrogative_pronoun": "pronoun",
                "indefinite_pronoun": "pronoun",
                "relative_pronoun": "pronoun",
                "copula": "verb",
            }
            return inter_map.get(role, role)
        # beginner — collapse most fine-grained roles to the basic POS set.
        beginner_map = {
            "imperfective_verb": "verb",
            "perfective_verb": "verb",
            "infinitive": "verb",
            "imperative": "verb",
            "modal_verb": "verb",
            "auxiliary": "verb",
            "copula": "verb",
            "reflexive_verb": "verb",
            "short_adjective": "adjective",
            "comparative": "adjective",
            "superlative": "adjective",
            "personal_pronoun": "pronoun",
            "possessive_pronoun": "pronoun",
            "possessive_determiner": "pronoun",
            "reflexive_pronoun": "pronoun",
            "demonstrative": "pronoun",
            "relative_pronoun": "pronoun",
            "interrogative_pronoun": "pronoun",
            "indefinite_pronoun": "pronoun",
            "negative_pronoun": "pronoun",
            "coordinating_conjunction": "conjunction",
            "subordinating_conjunction": "conjunction",
            "aspectual_particle": "particle",
            "conditional_particle": "particle",
            "negation_particle": "particle",
            "participle": "verb",
            "present_active_participle": "verb",
            "past_active_participle": "verb",
            "present_passive_participle": "verb",
            "past_passive_participle": "verb",
            "gerund": "verb",
            "verbal_noun": "noun",
        }
        return beginner_map.get(role, role)
