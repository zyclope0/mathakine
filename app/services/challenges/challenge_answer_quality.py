"""
Qualité des réponses / distracteurs pour défis (validation backend).

Les défis restent souvent en saisie libre ; lorsque le générateur fournit ``choices``,
on applique des garde-fous pour éviter QCM triviaux (doublons, bonne réponse absente).
"""

from __future__ import annotations

from typing import Any, List, Sequence


def _norm_choice(s: Any) -> str:
    return " ".join(str(s).strip().lower().split())


def validate_challenge_choices(
    challenge_type: str,
    correct_answer: str,
    choices: Any,
) -> List[str]:
    """
    Valide une liste de choix (QCM) si elle est fournie.

    Si ``choices`` est absent, vide ou null : pas de validation QCM (comportement historique).
    Si une liste non vide est fournie : exige un mini-QCM défendable.
    """
    errors: List[str] = []
    if choices is None:
        return errors
    if isinstance(choices, str):
        return errors  # format inattendu, ignoré pour ne pas bloquer le flux
    if not isinstance(choices, list):
        errors.append("choices doit être une liste de chaînes si fourni")
        return errors
    if len(choices) == 0:
        return errors

    str_choices: List[str] = [str(c).strip() for c in choices if c is not None]
    str_choices = [c for c in str_choices if c]
    if len(str_choices) < 3:
        errors.append(
            "QCM : fournir au moins 3 options textuelles distinctes et plausibles "
            "(sinon omettre le champ choices pour une réponse libre)."
        )
        return errors

    normalized = [_norm_choice(c) for c in str_choices]
    if any(not n for n in normalized):
        errors.append(
            "QCM : chaque choix doit être une chaîne non vide une fois normalisée"
        )
        return errors

    if len(set(normalized)) < len(normalized):
        errors.append(
            "QCM : des options sont en doublon (ou quasi-identiques après normalisation) — "
            "chaque distracteur doit être distinct."
        )

    ca = _norm_choice(correct_answer)
    if not ca:
        errors.append("correct_answer vide : impossible de valider les choix")
        return errors

    # La bonne réponse doit correspondre à une option (égalité normalisée ou contenue)
    matches = [i for i, n in enumerate(normalized) if n == ca or ca in n or n in ca]
    if not matches:
        errors.append(
            "QCM : correct_answer ne correspond à aucune entrée de choices "
            "(après normalisation). Aligner la bonne réponse sur une option exacte."
        )

    # Bonne réponse beaucoup plus longue que tous les distracteurs = mise en évidence
    ca_raw_len = len(str(correct_answer).strip())
    other_lens = [
        len(c) for c in str_choices if _norm_choice(c) != ca and _norm_choice(c)
    ]
    if other_lens and ca_raw_len > max(other_lens) * 4:
        errors.append(
            "QCM : correct_answer est beaucoup plus longue que les distracteurs — "
            "formulations de longueur comparable, ou réponse libre sans choices."
        )

    _ = challenge_type  # réservé pour règles spécifiques par type (futur)
    return errors
