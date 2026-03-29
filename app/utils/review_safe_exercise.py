"""
Sérialisation exercice pour contexte « révision » sans fuite de correction (F04).

Ne jamais inclure : correct_answer, explanation, hint.
"""

from typing import Any, Dict, List, Optional, Union

from app.models.exercise import Exercise


def exercise_to_review_safe_dict(exercise: Exercise) -> Dict[str, Any]:
    """
    Champs strictement nécessaires pour afficher l'énoncé / QCM sans spoiler.
    """
    choices_raw: Optional[Union[List[Any], Any]] = exercise.choices
    choices: Optional[List[Any]]
    if choices_raw is None:
        choices = None
    elif isinstance(choices_raw, list):
        choices = list(choices_raw)
    else:
        choices = None

    return {
        "id": exercise.id,
        "title": exercise.title,
        "question": exercise.question,
        "exercise_type": exercise.exercise_type,
        "difficulty": exercise.difficulty,
        "age_group": exercise.age_group,
        "difficulty_tier": exercise.difficulty_tier,
        "choices": choices,
        "image_url": exercise.image_url,
        "audio_url": exercise.audio_url,
    }
