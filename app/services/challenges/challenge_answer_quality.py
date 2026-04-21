"""
Qualite des reponses / distracteurs pour defis (validation backend).

Les defis restent souvent en saisie libre ; lorsque le generateur fournit ``choices``,
on applique des garde-fous pour eviter QCM triviaux (doublons, bonne reponse absente).
"""

from __future__ import annotations

import re
from fractions import Fraction
from typing import Any, List, Optional


def _norm_choice(s: Any) -> str:
    return " ".join(str(s).strip().lower().split())


_LATEX_FRACTION_RE = re.compile(
    r"^\\(?:dfrac|frac|tfrac)\{([+-]?\d+(?:[.,]\d+)?)\}\{([+-]?\d+(?:[.,]\d+)?)\}$"
)
_SIMPLE_PROBABILITY_VALUE_RE = re.compile(
    r"^[+-]?\d+(?:[.,]\d+)?(?:/[+-]?\d+(?:[.,]\d+)?)?%?$"
)


def _parse_probability_choice_value(raw: Any) -> Optional[Fraction]:
    """
    Parse uniquement des valeurs de probabilite simples pour comparer les QCM.

    Conservative by design : les libelles textuels restent hors analyse, afin de ne
    pas rejeter des distracteurs valides contenant des explications.
    """
    if raw is None:
        return None

    text = str(raw).strip()
    if not text:
        return None

    text = text.strip("$").replace(" ", "").replace(",", ".")
    text = text.replace("\\left", "").replace("\\right", "")

    latex_match = _LATEX_FRACTION_RE.fullmatch(text)
    if latex_match:
        numerator = latex_match.group(1)
        denominator = latex_match.group(2)
        try:
            den = Fraction(denominator)
            return Fraction(numerator) / den if den != 0 else None
        except (ValueError, ZeroDivisionError):
            return None

    if not _SIMPLE_PROBABILITY_VALUE_RE.fullmatch(text):
        return None

    is_percent = text.endswith("%")
    if is_percent:
        text = text[:-1]

    try:
        if "/" in text:
            numerator, denominator = text.split("/", 1)
            den = Fraction(denominator)
            value = Fraction(numerator) / den if den != 0 else None
        else:
            value = Fraction(text)
    except (ValueError, ZeroDivisionError):
        return None

    if value is None:
        return None
    return value / 100 if is_percent else value


def _validate_probability_choice_equivalence(
    correct_answer: str,
    str_choices: List[str],
) -> List[str]:
    errors: List[str] = []
    parsed_choices: List[tuple[int, str, Fraction]] = []
    for index, choice in enumerate(str_choices):
        parsed = _parse_probability_choice_value(choice)
        if parsed is not None:
            parsed_choices.append((index, choice, parsed))

    if len(parsed_choices) < 2:
        return errors

    seen: dict[Fraction, tuple[int, str]] = {}
    equivalent_pairs: List[str] = []
    for index, choice, value in parsed_choices:
        previous = seen.get(value)
        if previous is None:
            seen[value] = (index, choice)
            continue
        equivalent_pairs.append(f"{previous[1]!r} et {choice!r}")

    if equivalent_pairs:
        errors.append(
            "QCM PROBABILITY : des options sont mathematiquement equivalentes "
            f"({'; '.join(equivalent_pairs)}). Un QCM ne doit pas contenir deux "
            "reponses correctes sous des formes differentes."
        )

    correct_value = _parse_probability_choice_value(correct_answer)
    if correct_value is not None:
        equivalent_correct = [
            choice for _index, choice, value in parsed_choices if value == correct_value
        ]
        if len(equivalent_correct) > 1:
            errors.append(
                "QCM PROBABILITY : plusieurs options sont equivalentes a "
                "correct_answer. Garder une seule forme de la bonne reponse, "
                "ou omettre choices pour une reponse libre."
            )

    return errors


def validate_challenge_choices(
    challenge_type: str,
    correct_answer: str,
    choices: Any,
) -> List[str]:
    """
    Valide une liste de choix (QCM) si elle est fournie.

    Si ``choices`` est absent, vide ou null : pas de validation QCM (comportement historique).
    Si une liste non vide est fournie : exige un mini-QCM defendable.
    """
    errors: List[str] = []
    if choices is None:
        return errors
    if isinstance(choices, str):
        return errors  # format inattendu, ignore pour ne pas bloquer le flux
    if not isinstance(choices, list):
        errors.append("choices doit etre une liste de chaines si fourni")
        return errors
    if len(choices) == 0:
        return errors

    str_choices: List[str] = [str(c).strip() for c in choices if c is not None]
    str_choices = [c for c in str_choices if c]
    if len(str_choices) < 3:
        errors.append(
            "QCM : fournir au moins 3 options textuelles distinctes et plausibles "
            "(sinon omettre le champ choices pour une reponse libre)."
        )
        return errors

    normalized = [_norm_choice(c) for c in str_choices]
    if any(not n for n in normalized):
        errors.append(
            "QCM : chaque choix doit etre une chaine non vide une fois normalisee"
        )
        return errors

    if len(set(normalized)) < len(normalized):
        errors.append(
            "QCM : des options sont en doublon (ou quasi-identiques apres normalisation) - "
            "chaque distracteur doit etre distinct."
        )

    if (challenge_type or "").strip().upper() == "PROBABILITY":
        errors.extend(
            _validate_probability_choice_equivalence(correct_answer, str_choices)
        )

    ca = _norm_choice(correct_answer)
    if not ca:
        errors.append("correct_answer vide : impossible de valider les choix")
        return errors

    # La bonne reponse doit correspondre a une option (egalite normalisee ou contenue).
    matches = [i for i, n in enumerate(normalized) if n == ca or ca in n or n in ca]
    if not matches:
        errors.append(
            "QCM : correct_answer ne correspond a aucune entree de choices "
            "(apres normalisation). Aligner la bonne reponse sur une option exacte."
        )

    # Bonne reponse beaucoup plus longue que tous les distracteurs = mise en evidence.
    ca_raw_len = len(str(correct_answer).strip())
    other_lens = [
        len(c) for c in str_choices if _norm_choice(c) != ca and _norm_choice(c)
    ]
    if other_lens and ca_raw_len > max(other_lens) * 4:
        errors.append(
            "QCM : correct_answer est beaucoup plus longue que les distracteurs - "
            "formulations de longueur comparable, ou reponse libre sans choices."
        )

    return errors
