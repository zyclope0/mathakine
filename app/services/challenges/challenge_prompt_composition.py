"""
Composition modulaire du prompt système pour la génération IA des défis.

- Réduit le volume de tokens en n'injectant que le contrat ``visual_data`` et les
  rappels de validation **du type demandé**.
- Conserve les règles transverses (indices, LaTeX, JSON, difficulté, verrou de type)
  pour ne pas affaiblir la sécurité pédagogique ni le typage du défi.
"""

from __future__ import annotations

from typing import List

from app.services.challenges.challenge_prompt_sections import (
    TEXT_DIFFICULTY_RULES,
    TEXT_HINTS_RULES,
    TEXT_JSON_CONTRACT_TEMPLATE,
    TEXT_LATEX_RULES,
    TEXT_MATHLOG_CONTEXT,
    TEXT_PATTERN_EXAMPLES,
    TEXT_ROLE_HEADER,
    TEXT_TYPE_LOCK_TEMPLATE,
    TEXT_TYPES_COMPACT,
    TEXT_VAL_FINAL,
    TEXT_VAL_INTRO,
    TEXT_VISUAL_ADULT_RULE,
    TEXT_VISUAL_DATA_FALLBACK,
    VALIDATION_SECTION_BY_TYPE,
    VISUAL_DATA_SECTION_BY_TYPE,
)

# Paramètres de difficulté par groupe d'âge (affichage, complexité, etc.)
AGE_GROUP_PARAMS = {
    "6-8": {
        "complexity": "très simple",
        "numbers_max": 20,
        "steps": "1-2",
        "vocabulary": "élémentaire, mots simples",
        "display": "6-8 ans",
    },
    "9-11": {
        "complexity": "simple à moyen",
        "numbers_max": 100,
        "steps": "2-3",
        "vocabulary": "accessible aux enfants",
        "display": "9-11 ans",
    },
    "12-14": {
        "complexity": "moyen",
        "numbers_max": 500,
        "steps": "3-4",
        "vocabulary": "langage courant",
        "display": "12-14 ans",
    },
    "15-17": {
        "complexity": "moyen à complexe",
        "numbers_max": 1000,
        "steps": "4-5",
        "vocabulary": "langage précis",
        "display": "15-17 ans",
    },
    "adulte": {
        "complexity": "complexe",
        "numbers_max": 10000,
        "steps": "5+",
        "vocabulary": "langage technique possible",
        "display": "adultes",
    },
    "tous-ages": {
        "complexity": "simple à moyen",
        "numbers_max": 100,
        "steps": "2-3",
        "vocabulary": "accessible à tous",
        "display": "tous âges",
    },
}

_SUPPORTED_OUTPUT_LANGUAGES = {
    "fr": "français",
    "en": "anglais",
    "es": "espagnol",
    "de": "allemand",
    "it": "italien",
    "pt": "portugais",
}


def canonical_challenge_type_for_prompt(challenge_type: str) -> str:
    """Normalise le type pour lookup des sections (ex. spatial → visual)."""
    t = (challenge_type or "").strip().lower()
    if t == "spatial":
        return "visual"
    return t


def _age_group_block(params: dict) -> str:
    return (
        f"GROUPE D'ÂGE CIBLE : {params['display']}\n"
        f"- Complexité : {params['complexity']}\n"
        f"- Nombres : max {params['numbers_max']}\n"
        f"- Étapes de raisonnement : {params['steps']}\n"
        f"- Vocabulaire : {params['vocabulary']}"
    )


def build_challenge_system_prompt(challenge_type: str, age_group: str) -> str:
    """Assemble le prompt système : commun + sections spécifiques au type uniquement."""
    ct = canonical_challenge_type_for_prompt(challenge_type)
    params = AGE_GROUP_PARAMS.get(age_group, AGE_GROUP_PARAMS["9-11"])
    age_display = params["display"]

    parts: List[str] = [
        TEXT_ROLE_HEADER,
        TEXT_TYPE_LOCK_TEMPLATE.format(challenge_type=challenge_type),
        _age_group_block(params),
        TEXT_TYPES_COMPACT,
        TEXT_MATHLOG_CONTEXT,
        TEXT_HINTS_RULES,
        VISUAL_DATA_SECTION_BY_TYPE.get(ct, TEXT_VISUAL_DATA_FALLBACK),
    ]
    if age_group == "adulte" and ct == "visual":
        parts.append(TEXT_VISUAL_ADULT_RULE.strip())

    parts.append(TEXT_VAL_INTRO)
    type_validation = VALIDATION_SECTION_BY_TYPE.get(ct)
    if type_validation:
        parts.append(type_validation)
    parts.append(TEXT_VAL_FINAL)
    if ct == "pattern":
        parts.append(TEXT_PATTERN_EXAMPLES)

    parts.extend(
        [
            TEXT_LATEX_RULES,
            # ``ct`` = type canonique (ex. spatial → visual). Garde l'invariant
            # ``spatial`` et ``visual`` produisent le même tail, et le modèle
            # voit toujours le nom canonique dans la directive de priorité.
            TEXT_JSON_CONTRACT_TEMPLATE.format(
                age_display=age_display, challenge_type=ct
            ),
            TEXT_DIFFICULTY_RULES,
        ]
    )
    return "\n\n".join(parts)


def _output_language_from_locale(locale: str) -> str:
    lang = str(locale or "fr").split("-", 1)[0].split("_", 1)[0].lower()
    return _SUPPORTED_OUTPUT_LANGUAGES.get(lang, "français")


def build_challenge_user_prompt(
    challenge_type: str, age_group: str, prompt: str, locale: str = "fr"
) -> str:
    """Construit le prompt utilisateur pour la génération de défis."""
    params = AGE_GROUP_PARAMS.get(age_group, AGE_GROUP_PARAMS["9-11"])
    age_display = params["display"]
    output_language = _output_language_from_locale(locale)
    age_target_phrase = (
        "pour des adultes"
        if age_group == "adulte"
        else (
            "pour un public de tous âges"
            if age_group == "tous-ages"
            else f"pour des enfants/élèves de {age_display}"
        )
    )

    user_prompt = f"""Crée un défi mathélogique de type "{challenge_type}" {age_target_phrase}.

CONTRAINTES OBLIGATOIRES :
- Type de défi : {challenge_type} (pas un autre type !)
- Groupe d'âge : {age_display} (adapter la complexité et le vocabulaire)
- Le visual_data DOIT correspondre au type {challenge_type}
- La difficulté doit être adaptée à {age_display}

LANGUE DE SORTIE :
- Langue de l'interface : {locale or "fr"} → rédige les champs visibles en {output_language}.
- `correct_answer` doit être en {output_language} quand la réponse est un mot, une phrase ou un message décodé ; garde seulement les notations mathématiques/coordonnées/codes dans leur forme standard.
- Si la locale est ambiguë ou non prise en charge, utilise le français."""

    if prompt:
        user_prompt += f"""

DEMANDE PERSONNALISÉE DE L'UTILISATEUR (à respecter en priorité) :
{prompt}

Note : Respecte la demande ci-dessus tout en gardant le type "{challenge_type}" et le groupe d'âge {age_group}."""

    return user_prompt


def challenge_system_prompt_stats(challenge_type: str, age_group: str) -> dict:
    """Métadonnées de taille (chars / estimation tokens) pour mesure avant/après."""
    text = build_challenge_system_prompt(challenge_type, age_group)
    n = len(text)
    return {
        "chars": n,
        "approx_tokens": max(1, n // 4),
        "challenge_type": challenge_type,
        "age_group": age_group,
    }
