"""
Helpers pour la génération d'exercices : génération des choix de réponses MCQ.

Extrait de exercise_generator.py (PR découpage #2) — fonctions pures pour MCQ.
"""

import random

from app.core.constants import DifficultyLevels
from server.exercise_generator_validators import get_difficulty_from_age_group


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
