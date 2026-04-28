"""Guard test — prompt système ne doit pas dépasser MAX_PROMPT_CHARS chars.

Baseline mesuré le 2026-04-28 avant implémentation :
  min=7074 chars, max=8776 chars (chess/9-11).
Budget post-implémentation : 11 000 chars (+25 %).
Si un type dépasse, consolider les nouvelles sections dans challenge_prompt_sections.py.
"""
import pytest

from app.services.challenges.challenge_prompt_composition import (
    AGE_GROUP_PARAMS,
    challenge_system_prompt_stats,
)
from app.services.challenges.challenge_stream_service import VALID_CHALLENGE_TYPES

# Age groups derived from AGE_GROUP_PARAMS to stay in sync automatically.
AGE_GROUPS = list(AGE_GROUP_PARAMS.keys())

# Seuil = baseline_max(8776) × 1.25, arrondi au millier supérieur
MAX_PROMPT_CHARS = 11_000

# Cartesian product expressed as explicit tuples so pytest IDs are readable.
_PARAMS = [
    (ct, ag)
    for ct in VALID_CHALLENGE_TYPES
    for ag in AGE_GROUPS
]


@pytest.mark.parametrize("challenge_type,age_group", _PARAMS)
def test_system_prompt_size_budget(challenge_type: str, age_group: str) -> None:
    """Le prompt système ne doit pas dépasser MAX_PROMPT_CHARS caractères."""
    stats = challenge_system_prompt_stats(challenge_type, age_group)
    assert stats["chars"] >= 5_000, (
        f"Prompt trop court — {challenge_type}/{age_group} : "
        f"{stats['chars']} chars < 5000 minimum. "
        "Vérifier qu'aucune section n'est vide ou manquante."
    )
    assert stats["chars"] <= MAX_PROMPT_CHARS, (
        f"Prompt trop long — {challenge_type}/{age_group} : "
        f"{stats['chars']} chars > {MAX_PROMPT_CHARS} limite. "
        "Réduire les nouvelles sections ou consolider dans challenge_prompt_sections.py."
    )
