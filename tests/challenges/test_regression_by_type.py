"""
Golden regression tests for challenge validation (Phase 3A).

Each JSON fixture in tests/fixtures/challenges/ describes one challenge payload
and its expected validation outcome. The test is parametrized: adding a new fixture
file automatically adds a new test case.

Fixture format:
  {
    "challenge": { ...full challenge dict... },
    "expected_valid": true | false,
    "expected_error_codes": ["code1", "code2"]   # stable codes from challenge_validation_error_codes
  }
"""

from __future__ import annotations

import json
from glob import glob
from pathlib import Path

import pytest

from app.services.challenges.challenge_contract_policy import RESPONSE_MODES
from app.services.challenges.challenge_validation_error_codes import (
    classify_challenge_validation_errors,
)
from app.services.challenges.challenge_validator import validate_challenge_logic

_FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "challenges"


def _load_fixture_ids() -> list[str]:
    ids = [Path(p).stem for p in sorted(glob(str(_FIXTURES_DIR / "*.json")))]
    if not ids:
        raise RuntimeError(
            f"Aucune fixture trouvée dans {_FIXTURES_DIR} — dossier manquant ou vide ?"
        )
    return ids


@pytest.mark.parametrize("fixture_name", _load_fixture_ids())
def test_challenge_regression(fixture_name: str) -> None:
    """Each fixture must produce exactly the expected validity and error codes."""
    fixture_path = _FIXTURES_DIR / f"{fixture_name}.json"
    data = json.loads(fixture_path.read_text(encoding="utf-8"))

    expected_codes: list[str] = list(data["expected_error_codes"])

    # P1-1: interdire validation_unknown dans les attentes — un golden test ne doit pas
    # figer un trou de classification ; ajouter une règle dans
    # challenge_validation_error_codes plutôt que d'épingler le fallback.
    assert "validation_unknown" not in expected_codes, (
        f"[{fixture_name}] expected_error_codes contient 'validation_unknown' : "
        "ajouter une règle dans challenge_validation_error_codes plutôt que figer le fallback."
    )

    challenge = data["challenge"]

    # P1-0 : response_mode doit être absent ou appartenir au contrat RESPONSE_MODES.
    rm = challenge.get("response_mode")
    if rm is not None:
        assert rm in RESPONSE_MODES, (
            f"[{fixture_name}] response_mode={rm!r} invalide — "
            f"valeurs acceptées : {RESPONSE_MODES}"
        )
    is_valid, errors = validate_challenge_logic(challenge)

    assert is_valid == data["expected_valid"], (
        f"[{fixture_name}] is_valid attendu={data['expected_valid']}, "
        f"obtenu={is_valid}. Erreurs brutes: {errors}"
    )

    actual_codes = classify_challenge_validation_errors(
        errors, challenge.get("challenge_type", "")
    )

    # P1-2: dédup explicite (invariant documenté de classify_challenge_validation_errors).
    assert len(actual_codes) == len(
        set(actual_codes)
    ), f"[{fixture_name}] doublons dans les codes : {actual_codes}"

    # P1-2: comparer en liste ordonnée — l'ordre est un invariant documenté.
    # Le runtime ne doit pas non plus produire 'validation_unknown' (garde-fou côté output).
    assert "validation_unknown" not in actual_codes, (
        f"[{fixture_name}] le classifieur retourne validation_unknown — "
        f"erreurs brutes: {errors}"
    )
    assert actual_codes == expected_codes, (
        f"[{fixture_name}] error_codes attendus={expected_codes}, "
        f"obtenus={actual_codes}. Erreurs brutes: {errors}"
    )
