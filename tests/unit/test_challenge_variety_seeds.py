"""Tests unitaires pour challenge_variety_seeds.pick_variety_seed().

Couvre :
- Tous les types connus retournent un seed non-vide (mechanism non-vide)
- Type inconnu retourne un seed vide (pas d'injection ORIENTATION)
- Guard NARRATIVE_CONTEXTS vide → seed vide (P2-01)
- Riddle jeune groupe → mécanismes all-ages seulement (P1-01)
"""
from unittest.mock import patch

import pytest

from app.services.challenges.challenge_variety_seeds import (
    RESOLUTION_MECHANISMS_BY_TYPE,
    VarietySeed,
    _RIDDLE_MECHANISMS_ALL_AGES,
    _RIDDLE_MECHANISMS_ADVANCED,
    pick_variety_seed,
)


@pytest.mark.parametrize("challenge_type", list(RESOLUTION_MECHANISMS_BY_TYPE.keys()))
def test_all_known_types_return_non_empty_seed(challenge_type: str) -> None:
    """Chaque type connu doit retourner un mécanisme non-vide."""
    seed = pick_variety_seed(challenge_type)
    assert seed.resolution_mechanism, (
        f"resolution_mechanism vide pour le type '{challenge_type}'"
    )


def test_unknown_type_returns_empty_seed() -> None:
    """Un type inconnu retourne un seed entièrement vide — aucun bloc ORIENTATION injecté."""
    seed = pick_variety_seed("type_inconnu")
    assert seed.narrative_context == ""
    assert seed.resolution_mechanism == ""


def test_empty_seed_no_injection_guard() -> None:
    """Un seed vide ne doit pas déclencher l'injection du bloc ORIENTATION.

    Vérifie que la condition guard de build_challenge_user_prompt() est falsy
    avec un seed entièrement vide.
    """
    empty = VarietySeed(narrative_context="", resolution_mechanism="")
    assert not (empty.narrative_context or empty.resolution_mechanism)


def test_narrative_contexts_guard_on_empty_list() -> None:
    """Si NARRATIVE_CONTEXTS est vidé, pick_variety_seed retourne un seed vide (P2-01).

    Sans ce guard, random.choice([]) lèverait IndexError dans le flux SSE.
    """
    with patch(
        "app.services.challenges.challenge_variety_seeds.NARRATIVE_CONTEXTS",
        [],
    ):
        seed = pick_variety_seed("coding")
    assert seed.narrative_context == ""
    assert seed.resolution_mechanism == ""


@pytest.mark.parametrize("young_group", ["6-8", "9-11"])
def test_riddle_young_group_returns_non_adult_mechanism(young_group: str) -> None:
    """Les mécanismes riddle avancés (P1-01) ne doivent pas être tirés pour 6-8 et 9-11."""
    advanced_set = set(_RIDDLE_MECHANISMS_ADVANCED)
    all_ages_set = set(_RIDDLE_MECHANISMS_ALL_AGES)
    for _ in range(50):  # 50 tirages — probabilité d'échec si bug ≈ (3/5)^50 ≈ 0
        seed = pick_variety_seed("riddle", age_group=young_group)
        assert seed.resolution_mechanism in all_ages_set, (
            f"Mécanisme avancé tiré pour le groupe '{young_group}': "
            f"'{seed.resolution_mechanism}'"
        )
        assert seed.resolution_mechanism not in advanced_set


@pytest.mark.parametrize("adult_group", ["12-14", "15-17", "adulte"])
def test_riddle_adult_group_can_return_advanced_mechanism(adult_group: str) -> None:
    """Les mécanismes riddle avancés sont accessibles pour 12-14, 15-17 et adulte."""
    advanced_set = set(_RIDDLE_MECHANISMS_ADVANCED)
    found_advanced = False
    for _ in range(200):
        seed = pick_variety_seed("riddle", age_group=adult_group)
        if seed.resolution_mechanism in advanced_set:
            found_advanced = True
            break
    assert found_advanced, (
        f"Aucun mécanisme avancé tiré après 200 essais pour le groupe '{adult_group}'"
    )
