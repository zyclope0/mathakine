"""
Helpers pour la génération d'exercices.

Fonctions pures partagées entre generate_simple_exercise et generate_ai_exercise.
"""

import os
import random
from typing import Any, Dict, Optional, Tuple

from app.core.constants import (
    DIFFICULTY_LIMITS,
    DifficultyLevels,
    Tags,
    normalize_age_group,
)
from app.core.difficulty_tier import build_exercise_generation_profile
from app.core.messages import ExerciseMessages
from app.utils.exercise_generator_validators import (
    get_difficulty_from_age_group,
    normalize_exercise_type,
)


def adjust_type_limits_for_f42_profile(
    type_limits: Dict[str, Any], f42_profile: dict
) -> Dict[str, Any]:
    """Apply a fine-grained F42 calibration to the base ``type_limits`` dict.

    Within a ``derived_difficulty`` bucket (e.g. PADAWAN covers tiers 4/5/6),
    three pedagogical bands exist: discovery (0), learning (1), consolidation (2).
    This helper scales numeric bounds *within* the legacy bucket so that:
      - band 0 (discovery): lower third of the range
      - band 1 (learning):  middle third  (identity — no change)
      - band 2 (consolidation): upper third of the range

    Pure function — mutates nothing, returns a new dict.
    """
    band = f42_profile.get("pedagogical_band", "learning")
    if band == "learning":
        # Middle of the legacy bucket — return as-is (no change)
        return type_limits

    adjusted: Dict[str, Any] = {}
    for key, value in type_limits.items():
        if not isinstance(value, int):
            adjusted[key] = value
            continue

        if band == "discovery":
            # Move toward the lower 60 % of the range
            # New max = original min + 60 % of span
            if key in ("max", "max1", "max2", "max_divisor", "max_result"):
                base_min = type_limits.get(
                    key.replace("max", "min"), type_limits.get("min", 1)
                )
                span = value - base_min
                adjusted[key] = base_min + max(1, int(span * 0.6))
            else:
                adjusted[key] = value
        else:
            # band == "consolidation": move toward the upper 60 % of the range
            # New min = original max - 60 % of span
            if key in ("min", "min1", "min2", "min_divisor", "min_result"):
                base_max = type_limits.get(
                    key.replace("min", "max"), type_limits.get("max", value * 2)
                )
                span = base_max - value
                adjusted[key] = value + max(0, int(span * 0.4))
            else:
                adjusted[key] = value

    return adjusted


def init_exercise_context(
    exercise_type: str,
    age_group: str,
    *,
    difficulty_override: Optional[str] = None,
    pedagogical_band_override: Optional[str] = None,
) -> Tuple[str, str, str, Dict[str, Any], dict]:
    """Normalise les paramètres et récupère les limites de difficulté.

    Returns:
        (normalized_type, normalized_age_group, derived_difficulty, type_limits, f42_profile)

    ``type_limits`` are already adjusted by ``adjust_type_limits_for_f42_profile``
    so that the F42 pedagogical band drives the numeric bounds before generation.
    ``f42_profile`` is also returned for callers that need the full profile.

    ``difficulty_override`` lets the orchestration layer enforce a runtime
    difficulty clamp without remapping the learner's age group.

    ``pedagogical_band_override`` (keyword-only) injects a mastery-resolved band
    (from :func:`resolve_adaptive_context`) so that learners with the same
    ``age_group`` but different mastery levels receive different calibration bounds.
    When absent, the legacy derivation ``age_group → derived_difficulty → band``
    is used unchanged (fully backward-compatible).
    """
    normalized_type = normalize_exercise_type(exercise_type)
    normalized_age_group = normalize_age_group(age_group)
    derived_difficulty = difficulty_override or get_difficulty_from_age_group(
        normalized_age_group
    )

    difficulty_config = DIFFICULTY_LIMITS.get(
        derived_difficulty, DIFFICULTY_LIMITS[DifficultyLevels.PADAWAN]
    )
    base_limits = difficulty_config.get(
        normalized_type, difficulty_config.get("default", {"min": 1, "max": 10})
    )
    f42_profile = build_exercise_generation_profile(
        normalized_type,
        normalized_age_group,
        derived_difficulty,
        pedagogical_band_override=pedagogical_band_override,
    )
    # Apply F42 calibration: bornes ajustées par la bande pédagogique F42.
    type_limits = adjust_type_limits_for_f42_profile(base_limits, f42_profile)
    return (
        normalized_type,
        normalized_age_group,
        derived_difficulty,
        type_limits,
        f42_profile,
    )


def build_base_exercise_data(
    normalized_type: str,
    normalized_age_group: str,
    derived_difficulty: str,
    *,
    ai_generated: bool,
) -> Dict[str, Any]:
    """Construit la structure de base commune à tout exercice généré."""
    tags = Tags.AI + "," + Tags.GENERATIVE if ai_generated else Tags.ALGORITHMIC
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
    """Fallback : génère un exercice d'addition par défaut."""
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
    """Un choix erroné est plausible s'il est dans une fourchette réaliste."""
    if wrong <= 0:
        return False
    if correct <= 0:
        return True
    ratio = wrong / correct
    return 0.2 <= ratio <= 5.0


def _plausible_offset(correct: int) -> int:
    """Génère un décalage plausible pour une erreur typique."""
    if correct <= 10:
        return random.choice([-2, -1, 1, 2])
    if correct <= 100:
        return random.choice([-5, -2, -1, 1, 2, 5])
    magnitude = 10 ** min(3, len(str(correct)) - 1)
    offset = random.choice(
        [-magnitude, -magnitude // 10, -1, 1, magnitude // 10, magnitude]
    )
    return max(1 - correct, offset)


def _invert_digits(n: int) -> int:
    """Inverse les chiffres d'un entier (ex: 48 → 84)."""
    s = str(n)
    if len(s) >= 2:
        return int(s[::-1])
    return n + 1


def _magnitude_offset(correct: int, pct: float) -> int:
    """Génère un offset en % du résultat."""
    val = max(1, round(abs(correct) * pct))
    return val


def _calibrated_distractors(
    correct: int,
    num1: int,
    num2: int,
    op: str,
    difficulty: str,
) -> list[int]:
    """Génère 3 distracteurs calibrés selon la difficulté et l'opération."""
    c = correct

    if difficulty == DifficultyLevels.INITIE:
        inv = _invert_digits(c)
        d1 = c + 1
        d2 = max(1, c - 1)
        d3 = inv if inv != c else c + 2
        return [d1, d2, d3]

    if difficulty == DifficultyLevels.PADAWAN:
        d1 = c + 10
        d2 = max(1, c - 10)
        if op == "MULTIPLICATION":
            d3 = num1 + num2 if num1 + num2 != c else c + random.randint(3, 7)
        elif op == "DIVISION":
            d3 = max(1, num1 - num2) if num1 - num2 != c else c + 3
        else:
            d3 = c + random.choice([-2, 2])
        return [d1, d2, max(1, d3)]

    if difficulty == DifficultyLevels.CHEVALIER:
        margin = _magnitude_offset(c, 0.10)
        d1 = c + margin
        d2 = max(1, c - margin)
        if op == "DIVISION" and num1 != 0:
            d3 = (
                max(1, num2 // num1)
                if num1 > 0 and num2 // num1 != c
                else c + margin + 1
            )
        else:
            d3 = c + random.choice([margin + 1, -(margin + 1)])
            d3 = max(1, d3)
        return [d1, d2, d3]

    if difficulty == DifficultyLevels.MAITRE:
        margin = _magnitude_offset(c, 0.05)
        margin = max(1, margin)
        d1 = c + margin
        d2 = max(1, c - margin)
        if op == "MULTIPLICATION":
            d3 = (num1 + 1) * num2 if (num1 + 1) * num2 != c else (num1 - 1) * num2
            d3 = max(1, d3)
        elif op == "DIVISION":
            d3 = max(1, c + 1) if c + 1 != d1 else max(1, c - 2)
        else:
            d3 = c + margin + 1
        return [d1, d2, max(1, d3)]

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
    *,
    derived_difficulty: Optional[str] = None,
) -> list[str]:
    """Génère 4 choix de réponses (1 correct + 3 distracteurs) calibrés.

    derived_difficulty : si fourni (INITIE, PADAWAN, …), évite de dériver depuis une
    chaîne ambiguë (ex. confondre un libellé de niveau avec un groupe d'âge).
    """
    op = operation_type.upper()
    derived = (
        derived_difficulty
        if derived_difficulty is not None
        else get_difficulty_from_age_group(age_group_or_difficulty)
    )

    if op == "SOUSTRACTION":
        op = "SUBTRACTION"

    raw_distractors = _calibrated_distractors(correct_result, num1, num2, op, derived)

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

    attempts = 0
    while len(unique) < 4 and attempts < 20:
        attempts += 1
        offset = _plausible_offset(correct_result)
        new_val = max(1, correct_result + offset)
        new_str = str(new_val)
        if new_str not in unique and _is_plausible_wrong(correct_result, new_val):
            unique.append(new_str)

    # Filet de sécurité : petits quotients (ex. 1) rejettent souvent les distracteurs
    # « plausibles » comme doublons — compléter avec des entiers distincts strictement.
    step = 1
    while len(unique) < 4:
        trial = correct_result + step
        step += 1
        if trial < 1:
            continue
        s = str(trial)
        if s not in unique:
            unique.append(s)

    random.shuffle(unique)
    return unique[:4]


def ensure_four_distinct_str_choices(correct: str, extras: list[str]) -> list[str]:
    """
    Garantit exactement 4 options QCM distinctes incluant la bonne réponse.

    Utilisé lorsque les distracteurs sont construits manuellement (géométrie, divers)
    pour éviter les doublons (ex. arrondis identiques).
    """
    c = str(correct).strip()
    out: list[str] = []
    seen: set[str] = set()
    for token in [c] + extras:
        t = str(token).strip()
        if not t or t in seen:
            continue
        seen.add(t)
        out.append(t)
        if len(out) >= 4:
            break

    step = 1
    while len(out) < 4:
        candidate: str
        try:
            v = float(str(c).replace(",", "."))
            if abs(v - int(v)) < 1e-9:
                n = int(v)
                candidate = str(n + step)
            else:
                candidate = f"{v + step * 0.01:.2f}"
        except ValueError:
            candidate = f"{c}|{step}"
        step += 1
        if candidate not in seen:
            seen.add(candidate)
            out.append(candidate)

    random.shuffle(out)
    return out
