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


def generate_smart_choices(
    operation_type: str,
    num1: int,
    num2: int,
    correct_result: int,
    age_group_or_difficulty: str,
) -> list[str]:
    """Génère des choix de réponses avec des erreurs typiques selon l'opération."""
    choices = [str(correct_result)]

    op = operation_type.upper()
    if op == "ADDITION":
        choices.extend(
            [
                str(correct_result + random.randint(1, 3)),
                str(correct_result - random.randint(1, 2)),
                (
                    str(num1 * num2)
                    if num1 * num2 != correct_result
                    else str(correct_result + 5)
                ),
            ]
        )
    elif op == "SUBTRACTION":
        choices.extend(
            [
                str(num2 - num1) if num2 != num1 else str(correct_result + 3),
                str(correct_result + random.randint(1, 3)),
                (
                    str(num1 + num2)
                    if num1 + num2 != correct_result
                    else str(correct_result - 2)
                ),
            ]
        )
    elif op == "MULTIPLICATION":
        choices.extend(
            [
                str(num1 + num2),
                str(correct_result + num1),
                str(max(1, correct_result - num2)),
            ]
        )
    elif op == "DIVISION":
        choices.extend(
            [
                str(correct_result + 1),
                str(max(1, correct_result - 1)),
                str(num1 - num2) if num1 > num2 else str(correct_result + 2),
            ]
        )

    derived = get_difficulty_from_age_group(age_group_or_difficulty)
    if derived in [DifficultyLevels.CHEVALIER, DifficultyLevels.MAITRE]:
        margin = max(1, int(correct_result * 0.1))
        if len(choices) > 1:
            choices[1] = str(correct_result + margin)
        if len(choices) > 2:
            choices[2] = str(max(1, correct_result - margin))

    unique = []
    for c in choices:
        try:
            if c not in unique and int(c) > 0:
                unique.append(c)
        except (ValueError, TypeError):
            pass

    while len(unique) < 4:
        new = str(correct_result + random.randint(-3, 5))
        if new not in unique:
            try:
                if int(new) > 0:
                    unique.append(new)
            except (ValueError, TypeError):
                pass

    random.shuffle(unique)
    return unique[:4]
