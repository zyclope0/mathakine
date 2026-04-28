"""Guard test — prompt système ne doit pas dépasser MAX_PROMPT_CHARS chars.

Baseline mesuré le 2026-04-28 avant implémentation :
  min=7074 chars, max=8776 chars (chess/9-11).
Budget post-implémentation : 11 000 chars (+25 %).
Si un type dépasse, consolider les nouvelles sections dans challenge_prompt_sections.py.
"""
import pytest

from app.services.challenges.challenge_prompt_composition import (
    challenge_system_prompt_stats,
)

CHALLENGE_TYPES = [
    "sequence", "pattern", "visual", "puzzle", "graph",
    "riddle", "deduction", "probability", "coding", "chess",
]
AGE_GROUPS = ["6-8", "9-11", "12-14", "15-17", "adulte"]

# Seuil = baseline_max(8776) × 1.25, arrondi au millier supérieur
MAX_PROMPT_CHARS = 11_000


@pytest.mark.parametrize("challenge_type", CHALLENGE_TYPES)
@pytest.mark.parametrize("age_group", AGE_GROUPS)
def test_system_prompt_size_budget(challenge_type: str, age_group: str) -> None:
    """Le prompt système ne doit pas dépasser MAX_PROMPT_CHARS caractères."""
    stats = challenge_system_prompt_stats(challenge_type, age_group)
    assert stats["chars"] <= MAX_PROMPT_CHARS, (
        f"Prompt trop long — {challenge_type}/{age_group} : "
        f"{stats['chars']} chars > {MAX_PROMPT_CHARS} limite. "
        "Réduire les nouvelles sections ou consolider dans challenge_prompt_sections.py."
    )
