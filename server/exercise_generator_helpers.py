"""
Helpers pour la génération d'exercices.

Fonctions pures partagées entre generate_simple_exercise et generate_ai_exercise :
- init_exercise_context  — normalisation + lookup limites
- build_base_exercise_data — structure dict commune
- default_addition_fallback — fallback addition quand le type n'est pas géré
- generate_smart_choices — choix MCQ avec erreurs typiques

Extrait de exercise_generator.py — Phase 3, item 3.4b.
"""

import os
import random
from typing import Any, Dict, Tuple

from app.core.constants import (
    DIFFICULTY_LIMITS,
    DifficultyLevels,
    Tags,
    normalize_age_group,
)
from app.core.messages import ExerciseMessages
from server.exercise_generator_validators import (
    get_difficulty_from_age_group,
    normalize_exercise_type,
)


def init_exercise_context(
    exercise_type: str, age_group: str
) -> Tuple[str, str, str, Dict[str, Any]]:
    """Normalise les paramètres et récupère les limites de difficulté.

    Returns:
        (normalized_type, normalized_age_group, derived_difficulty, type_limits)
    """
    normalized_type = normalize_exercise_type(exercise_type)
    normalized_age_group = normalize_age_group(age_group)
    derived_difficulty = get_difficulty_from_age_group(normalized_age_group)

    difficulty_config = DIFFICULTY_LIMITS.get(
        derived_difficulty, DIFFICULTY_LIMITS[DifficultyLevels.PADAWAN]
    )
    type_limits = difficulty_config.get(
        normalized_type, difficulty_config.get("default", {"min": 1, "max": 10})
    )
    return normalized_type, normalized_age_group, derived_difficulty, type_limits


def build_base_exercise_data(
    normalized_type: str,
    normalized_age_group: str,
    derived_difficulty: str,
    *,
    ai_generated: bool,
) -> Dict[str, Any]:
    """Construit la structure de base commune à tout exercice généré."""
    tags = (
        Tags.AI + "," + Tags.GENERATIVE + "," + Tags.STARWARS
        if ai_generated
        else Tags.ALGORITHMIC
    )
    return {
        "exercise_type": normalized_type,
        "age_group": normalized_age_group,
        "difficulty": derived_difficulty,
        "ai_generated": ai_generated,
        "tags": tags,
    }


def default_addition_fallback(
    exercise_data: Dict[str, Any],
    type_limits: Dict[str, Any],
    *,
    ai_generated: bool,
) -> Dict[str, Any]:
    """Fallback : génère un exercice d'addition par défaut.

    Utilisé quand le type normalisé ne correspond à aucun générateur dédié.
    """
    min_val = type_limits.get("min", 1)
    max_val = type_limits.get("max", 10)
    num1 = random.randint(min_val, max_val)
    num2 = random.randint(min_val, max_val)
    result = num1 + num2

    exercise_data.update(
        {
            "title": ExerciseMessages.TITLE_DEFAULT,
            "question": ExerciseMessages.QUESTION_ADDITION.format(num1=num1, num2=num2),
            "correct_answer": str(result),
            "choices": [str(result), str(result - 1), str(result + 1), str(result + 2)],
            "num1": num1,
            "num2": num2,
            "explanation": (
                f"Pour additionner {num1} et {num2}, il faut calculer leur somme, "
                f"donc {num1} + {num2} = {result}."
            ),
        }
    )
    return apply_test_title(exercise_data)


def apply_test_title(exercise_data: Dict[str, Any]) -> Dict[str, Any]:
    """Prefix titles in test mode so cleanup can detect them."""
    if os.environ.get("TESTING", "").lower() in ("1", "true", "yes"):
        title = exercise_data.get("title")
        if title and "test" not in str(title).lower():
            exercise_data["title"] = f"Test {title}"
    return exercise_data


def _is_plausible_wrong(correct: int, wrong: int) -> bool:
    """
    Un choix erroné est plausible s'il est dans une fourchette réaliste.
    Évite les réponses absurdes (ex: 16M pour une addition dont le résultat est 10k).
    """
    if wrong <= 0:
        return False
    if correct <= 0:
        return True
    ratio = wrong / correct
    return 0.2 <= ratio <= 5.0


def _plausible_offset(correct: int) -> int:
    """Génère un décalage plausible pour une erreur typique (carry, etc.)."""
    if correct <= 10:
        return random.choice([-2, -1, 1, 2])
    if correct <= 100:
        return random.choice([-5, -2, -1, 1, 2, 5])
    # Grands nombres : erreurs de retenue (1, 10, 100)
    magnitude = 10 ** min(3, len(str(correct)) - 1)
    offset = random.choice(
        [-magnitude, -magnitude // 10, -1, 1, magnitude // 10, magnitude]
    )
    return max(1 - correct, offset)  # Éviter les négatifs si possible


def _invert_digits(n: int) -> int:
    """Inverse les chiffres d'un entier (ex: 48 → 84). Utile pour INITIE."""
    s = str(n)
    if len(s) >= 2:
        return int(s[::-1])
    return n + 1


def _magnitude_offset(correct: int, pct: float) -> int:
    """
    Génère un offset en % du résultat, arrondi à l'entier non nul.
    Ex: _magnitude_offset(48, 0.10) → 5 (±10 %)
    """
    val = max(1, round(abs(correct) * pct))
    return val


def _calibrated_distractors(
    correct: int,
    num1: int,
    num2: int,
    op: str,
    difficulty: str,
) -> list[int]:
    """
    Génère 3 distracteurs calibrés selon la difficulté et l'opération.

    Fondements scientifiques :
    - INITIE  : Hattie & Timperley (2007) — erreurs de comptage (±1/±2) + inversion
                chiffres → misconceptions réelles des débutants (Butler 2010).
    - PADAWAN : Sweller (1988) CLT — erreurs de retenue (+10/-10) + confusion
                d'opération (ex: additionner au lieu de multiplier).
    - CHEVALIER: ±10% du résultat → l'élève doit discriminer des voisins proches,
                 activant la mémoire de travail (Haladyna & Downing 1993).
    - MAITRE   : ±5% du résultat + off-by-one sur facteurs → erreurs subtiles.
    - GRAND_MAITRE: ±2-3% → discrimination quasi-syntaxique (voisins très proches).
    """
    c = correct

    if difficulty == DifficultyLevels.INITIE:
        inv = _invert_digits(c)
        d1 = c + 1
        d2 = max(1, c - 1)
        d3 = inv if inv != c else c + 2
        return [d1, d2, d3]

    if difficulty == DifficultyLevels.PADAWAN:
        # Erreur de retenue (+10/-10) + confusion d'opération
        d1 = c + 10
        d2 = max(1, c - 10)
        if op == "MULTIPLICATION":
            # Confusion addition (num1+num2 au lieu de num1×num2)
            d3 = num1 + num2 if num1 + num2 != c else c + random.randint(3, 7)
        elif op == "DIVISION":
            # Confusion soustraction (num1-num2 au lieu de num1÷num2)
            d3 = max(1, num1 - num2) if num1 - num2 != c else c + 3
        else:
            d3 = c + random.choice([-2, 2])
        return [d1, d2, max(1, d3)]

    if difficulty == DifficultyLevels.CHEVALIER:
        margin = _magnitude_offset(c, 0.10)
        d1 = c + margin
        d2 = max(1, c - margin)
        # Propriété inverse (ex: num2/num1 pour division)
        if op == "DIVISION" and num1 != 0:
            d3 = max(1, num2 // num1) if num1 > 0 and num2 // num1 != c else c + margin + 1
        else:
            d3 = c + random.choice([margin + 1, -(margin + 1)])
            d3 = max(1, d3)
        return [d1, d2, d3]

    if difficulty == DifficultyLevels.MAITRE:
        margin = _magnitude_offset(c, 0.05)
        margin = max(1, margin)
        d1 = c + margin
        d2 = max(1, c - margin)
        # Off-by-one sur facteur (ex: (num1±1)*num2 ou num1*(num2±1))
        if op == "MULTIPLICATION":
            d3 = (num1 + 1) * num2 if (num1 + 1) * num2 != c else (num1 - 1) * num2
            d3 = max(1, d3)
        elif op == "DIVISION":
            d3 = max(1, c + 1) if c + 1 != d1 else max(1, c - 2)
        else:
            d3 = c + margin + 1
        return [d1, d2, max(1, d3)]

    # GRAND_MAITRE — ±2-3 %, voisins très proches
    margin = max(1, _magnitude_offset(c, 0.025))
    d1 = c + margin
    d2 = max(1, c - margin)
    d3 = c + margin + 1
    return [d1, d2, d3]


def generate_smart_choices(
    operation_type: str,
    num1: int,
    num2: int,
    correct_result: int,
    age_group_or_difficulty: str,
) -> list[str]:
    """
    Génère 4 choix de réponses (1 correct + 3 distracteurs) calibrés selon le niveau.

    Les distracteurs représentent des erreurs typiques de raisonnement
    (misconceptions-based distractors) adaptées à chaque niveau de difficulté.

    Fondements :
    - Butler (2010) Testing effect : seuls les distracteurs fondés sur des
      misconceptions réelles renforcent la rétention.
    - Haladyna & Downing (1993) : 3 distracteurs homogènes en plausibilité
      sont plus efficaces que 4 distracteurs hétérogènes.
    - Sweller (1988) CLT : à bas niveau, les distracteurs trop proches
      surchargent ; à haut niveau, trop éloignés ne challengent pas.
    """
    op = operation_type.upper()
    derived = get_difficulty_from_age_group(age_group_or_difficulty)

    # Obtenir les 3 distracteurs calibrés
    raw_distractors = _calibrated_distractors(correct_result, num1, num2, op, derived)

    # Fallback opération-spécifique si calibrated_distractors retourne des valeurs
    # identiques ou non plausibles (pour les cas edge comme correct_result=1)
    op_fallback = []
    if op == "ADDITION":
        op_fallback = [
            correct_result + random.randint(1, 3),
            max(1, correct_result - random.randint(1, 2)),
            correct_result + _plausible_offset(correct_result),
        ]
    elif op == "SUBTRACTION":
        cand_sub = num2 - num1 if num2 != num1 else correct_result + 3
        cand_add = num1 + num2
        op_fallback = [
            cand_sub if cand_sub > 0 else correct_result + 2,
            correct_result + random.randint(1, 3),
            (
                cand_add
                if cand_add != correct_result
                and _is_plausible_wrong(correct_result, cand_add)
                else correct_result + _plausible_offset(correct_result)
            ),
        ]
    elif op == "MULTIPLICATION":
        cand_add = num1 + num2
        op_fallback = [
            (
                cand_add
                if cand_add != correct_result
                and _is_plausible_wrong(correct_result, cand_add)
                else correct_result + _plausible_offset(correct_result)
            ),
            (
                correct_result + num1
                if _is_plausible_wrong(correct_result, correct_result + num1)
                else correct_result + _plausible_offset(correct_result)
            ),
            max(1, correct_result + _plausible_offset(correct_result)),
        ]
    elif op == "DIVISION":
        cand_sub = num1 - num2 if num1 > num2 else correct_result + 2
        op_fallback = [
            correct_result + 1,
            max(1, correct_result - 1),
            (
                cand_sub
                if cand_sub != correct_result
                and cand_sub > 0
                and _is_plausible_wrong(correct_result, cand_sub)
                else correct_result + _plausible_offset(correct_result)
            ),
        ]

    # Sanitization : partir du résultat correct + distracteurs calibrés + fallbacks
    unique: list[str] = [str(correct_result)]
    for candidate in raw_distractors + op_fallback:
        c_str = str(candidate)
        if c_str == str(correct_result) or c_str in unique:
            continue
        try:
            val = int(c_str)
            if val > 0 and _is_plausible_wrong(correct_result, val):
                unique.append(c_str)
                if len(unique) == 4:
                    break
        except (ValueError, TypeError):
            pass

    # Compléter avec des offsets plausibles génériques si toujours < 4
    attempts = 0
    while len(unique) < 4 and attempts < 20:
        attempts += 1
        offset = _plausible_offset(correct_result)
        new_val = max(1, correct_result + offset)
        new_str = str(new_val)
        if new_str not in unique and _is_plausible_wrong(correct_result, new_val):
            unique.append(new_str)

    random.shuffle(unique)
    return unique[:4]
