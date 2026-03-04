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


def generate_smart_choices(
    operation_type: str,
    num1: int,
    num2: int,
    correct_result: int,
    age_group_or_difficulty: str,
) -> list[str]:
    """
    Génère des choix de réponses avec des erreurs typiques selon l'opération.
    Garde-fou : aucun choix absurde (ex: num1*num2 pour une addition de grands nombres).
    """
    choices = [str(correct_result)]

    op = operation_type.upper()
    if op == "ADDITION":
        # Ne JAMAIS utiliser num1*num2 pour l'addition : absurde dès que result > 100
        cand1 = correct_result + random.randint(1, 3)
        cand2 = max(1, correct_result - random.randint(1, 2))
        cand3 = (
            str(num1 * num2)
            if num1 * num2 != correct_result
            and _is_plausible_wrong(correct_result, num1 * num2)
            else str(correct_result + _plausible_offset(correct_result))
        )
        choices.extend([str(cand1), str(cand2), cand3])
    elif op == "SUBTRACTION":
        # num1+num2 est absurde pour une soustraction (trop grand)
        cand_sub = num2 - num1 if num2 != num1 else correct_result + 3
        cand_add = num1 + num2
        cand3 = (
            str(cand_add)
            if cand_add != correct_result
            and _is_plausible_wrong(correct_result, cand_add)
            else str(correct_result + _plausible_offset(correct_result))
        )
        choices.extend(
            [
                str(cand_sub) if cand_sub > 0 else str(correct_result + 2),
                str(correct_result + random.randint(1, 3)),
                cand3,
            ]
        )
    elif op == "MULTIPLICATION":
        # num1+num2 est absurde pour une multiplication de grands nombres
        cand_add = num1 + num2
        cand3 = (
            str(cand_add)
            if cand_add != correct_result
            and _is_plausible_wrong(correct_result, cand_add)
            else str(correct_result + _plausible_offset(correct_result))
        )
        choices.extend(
            [
                cand3,
                (
                    str(correct_result + num1)
                    if _is_plausible_wrong(correct_result, correct_result + num1)
                    else str(correct_result + _plausible_offset(correct_result))
                ),
                (
                    str(max(1, correct_result - num2))
                    if _is_plausible_wrong(
                        correct_result, max(1, correct_result - num2)
                    )
                    else str(max(1, correct_result + _plausible_offset(correct_result)))
                ),
            ]
        )
    elif op == "DIVISION":
        cand_sub = num1 - num2 if num1 > num2 else correct_result + 2
        cand3 = (
            str(cand_sub)
            if cand_sub != correct_result
            and cand_sub > 0
            and _is_plausible_wrong(correct_result, cand_sub)
            else str(correct_result + _plausible_offset(correct_result))
        )
        choices.extend(
            [
                str(correct_result + 1),
                str(max(1, correct_result - 1)),
                cand3,
            ]
        )

    derived = get_difficulty_from_age_group(age_group_or_difficulty)
    if derived in [DifficultyLevels.CHEVALIER, DifficultyLevels.MAITRE]:
        margin = max(1, int(correct_result * 0.1))
        if len(choices) > 1:
            choices[1] = str(correct_result + margin)
        if len(choices) > 2:
            choices[2] = str(max(1, correct_result - margin))

    # Sanitization : garder uniquement les choix plausibles (jamais de 16M pour 10k)
    unique = [str(correct_result)]
    for c in choices:
        if c == str(correct_result):
            continue
        try:
            val = int(c)
            if val > 0 and _is_plausible_wrong(correct_result, val) and c not in unique:
                unique.append(c)
        except (ValueError, TypeError):
            pass

    # Compléter avec des erreurs plausibles si besoin (uniquement des mauvaises réponses)
    while len(unique) < 4:
        offset = _plausible_offset(correct_result)
        new = str(max(1, correct_result + offset))
        if new not in unique and new != str(correct_result):
            try:
                if int(new) > 0 and _is_plausible_wrong(correct_result, int(new)):
                    unique.append(new)
            except (ValueError, TypeError):
                pass

    random.shuffle(unique)
    return unique[:4]
