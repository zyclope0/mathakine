"""Unit tests for exercise_ai_service — pure data contracts.

Couvre les invariants structurels de ``DIFFICULTY_RANGES`` (Lot A — calibration
de difficulté à la génération). Les plages numériques injectées dans le prompt
LLM doivent respecter une monotonie stricte pour éviter l'ancrage bas observé
sur les plages chevauchantes précédentes.
"""

from __future__ import annotations

from app.core.difficulty_tier import (
    build_exercise_generation_profile,
    clamp_difficulty_for_type,
)
from app.services.exercises.exercise_ai_service import (
    _HIGH_DIFFICULTY_DIRECTIVE_ATOMIC,
    _HIGH_DIFFICULTY_DIRECTIVE_MULTISTEP,
    DIFFICULTY_RANGES,
    _non_triviality_hint,
    _persist_exercise_ai_sync,
    build_exercise_difficulty_info,
    build_exercise_system_prompt,
)

_ORDERED_LEVELS = ("INITIE", "PADAWAN", "CHEVALIER", "MAITRE", "GRAND_MAITRE")

_EXERCISE_TYPES = (
    "addition",
    "soustraction",
    "multiplication",
    "division",
    "fractions",
    "geometrie",
    "texte",
    "mixte",
    "divers",
)


def test_difficulty_ranges_five_levels_exact() -> None:
    assert set(DIFFICULTY_RANGES.keys()) == set(_ORDERED_LEVELS)
    assert len(DIFFICULTY_RANGES) == 5


def test_difficulty_ranges_strictly_monotonic_min() -> None:
    # Contrainte : min_{i+1} == max_i pour les 4 transitions consécutives.
    for prev, nxt in zip(_ORDERED_LEVELS, _ORDERED_LEVELS[1:]):
        prev_max = DIFFICULTY_RANGES[prev]["max"]
        nxt_min = DIFFICULTY_RANGES[nxt]["min"]
        assert nxt_min == prev_max, (
            f"transition {prev} -> {nxt} : min attendu == max précédent "
            f"({prev_max}) ; observé : {nxt_min}"
        )


def test_difficulty_ranges_strictly_monotonic_max() -> None:
    # max_{i+1} > max_i : les plafonds progressent strictement.
    for prev, nxt in zip(_ORDERED_LEVELS, _ORDERED_LEVELS[1:]):
        prev_max = DIFFICULTY_RANGES[prev]["max"]
        nxt_max = DIFFICULTY_RANGES[nxt]["max"]
        assert nxt_max > prev_max, (
            f"transition {prev} -> {nxt} : max attendu strictement supérieur "
            f"({prev_max}) ; observé : {nxt_max}"
        )


def test_difficulty_ranges_desc_non_empty_and_distinct() -> None:
    descs = [DIFFICULTY_RANGES[level]["desc"] for level in _ORDERED_LEVELS]
    for level, desc in zip(_ORDERED_LEVELS, descs):
        assert isinstance(desc, str)
        assert desc.strip(), f"desc vide pour {level}"
    assert len(set(descs)) == 5, "les 5 descriptions doivent être distinctes"


def test_difficulty_ranges_min_strictly_positive_for_all_levels() -> None:
    # Garde-fou additionnel : aucun niveau ne doit autoriser min <= 0
    # (plages numériques côté exercices, pas de signed).
    for level in _ORDERED_LEVELS:
        assert DIFFICULTY_RANGES[level]["min"] >= 1


def test_difficulty_ranges_max_strictly_greater_than_min_per_level() -> None:
    # Intra-niveau : max > min, évite un niveau dégénéré min == max.
    for level in _ORDERED_LEVELS:
        entry = DIFFICULTY_RANGES[level]
        assert (
            entry["max"] > entry["min"]
        ), f"{level} : max ({entry['max']}) doit être > min ({entry['min']})"


def test_openai_prompt_difficulty_info_uses_type_specific_local_limits() -> None:
    addition_info = build_exercise_difficulty_info("addition", "CHEVALIER")
    division_info = build_exercise_difficulty_info("division", "CHEVALIER")

    assert addition_info["min"] == 50
    assert addition_info["max"] == 200
    assert addition_info["desc"] == "nombres 50-200"
    assert division_info["min_divisor"] == 5
    assert division_info["max_divisor"] == 15
    assert division_info["desc"] == "diviseur 5-15, quotient attendu 8-20"


# ---------------------------------------------------------------------------
# Lot C — guidance non-trivialité conditionnelle au type
# ---------------------------------------------------------------------------


def test_non_triviality_empty_for_initie_and_padawan() -> None:
    for et in _EXERCISE_TYPES:
        for diff in ("INITIE", "PADAWAN", "initie", " padawan "):
            assert _non_triviality_hint(et, diff) == ""


def test_non_triviality_atomic_addition_grand_maitre() -> None:
    assert (
        _non_triviality_hint("addition", "GRAND_MAITRE")
        == _HIGH_DIFFICULTY_DIRECTIVE_ATOMIC
    )


def test_non_triviality_narrative_texte_chevalier() -> None:
    assert (
        _non_triviality_hint("texte", "CHEVALIER")
        == _HIGH_DIFFICULTY_DIRECTIVE_MULTISTEP["CHEVALIER"]
    )


def test_non_triviality_narrative_mixte_maitre() -> None:
    assert (
        _non_triviality_hint("mixte", "MAITRE")
        == _HIGH_DIFFICULTY_DIRECTIVE_MULTISTEP["MAITRE"]
    )


def test_non_triviality_unknown_type_returns_empty_hint() -> None:
    assert _non_triviality_hint("unknown_future_type", "GRAND_MAITRE") == ""


def test_system_prompt_includes_directive_when_chevalier_texte() -> None:
    prompt = build_exercise_system_prompt(
        "texte",
        "CHEVALIER",
        "9-11",
        {"desc": "test desc"},
        "",
        calibration_desc="calibration test",
    )
    assert "- Exigence de difficulté :" in prompt
    assert _HIGH_DIFFICULTY_DIRECTIVE_MULTISTEP["CHEVALIER"] in prompt


def test_system_prompt_has_no_directive_for_initie() -> None:
    prompt = build_exercise_system_prompt(
        "texte",
        "INITIE",
        "9-11",
        {"desc": "test desc"},
        "",
        calibration_desc="calibration test",
    )
    assert "Exigence de difficulté" not in prompt


# ---------------------------------------------------------------------------
# Lot E — intensité cognitive (orthogonal au tier F42)
# ---------------------------------------------------------------------------


def test_chevalier_maitre_grand_maitre_produce_distinct_system_prompts_for_group_9_11() -> (
    None
):
    """Même tranche d'âge et même bande F42 (consolidation) : prompts distincts."""
    prompts: list[str] = []
    for diff in ("CHEVALIER", "MAITRE", "GRAND_MAITRE"):
        profile = build_exercise_generation_profile("ADDITION", "9-11", diff)
        assert profile["difficulty_tier"] == 6
        prompts.append(
            build_exercise_system_prompt(
                "ADDITION",
                diff,
                "9-11",
                DIFFICULTY_RANGES[diff],
                "",
                calibration_desc=profile["calibration_desc"],
                cognitive_hint=profile.get("cognitive_hint") or "",
            )
        )
    assert len(set(prompts)) == 3


def test_atomic_addition_prompt_does_not_receive_multistep_cognitive_hint() -> None:
    profile = build_exercise_generation_profile("ADDITION", "9-11", "CHEVALIER")
    prompt = build_exercise_system_prompt(
        "ADDITION",
        "CHEVALIER",
        "9-11",
        DIFFICULTY_RANGES["CHEVALIER"],
        "",
        calibration_desc=profile["calibration_desc"],
        cognitive_hint=profile.get("cognitive_hint") or "",
    )
    assert "- Intensité cognitive attendue :" in prompt
    assert "deux étapes minimum" not in prompt
    assert "données à organiser" not in prompt
    assert "opération unique" in prompt


def test_multistep_texte_prompt_keeps_multistep_cognitive_hint() -> None:
    profile = build_exercise_generation_profile("texte", "9-11", "CHEVALIER")
    prompt = build_exercise_system_prompt(
        "texte",
        "CHEVALIER",
        "9-11",
        DIFFICULTY_RANGES["CHEVALIER"],
        "",
        calibration_desc=profile["calibration_desc"],
        cognitive_hint=profile.get("cognitive_hint") or "",
    )
    assert "deux étapes minimum" in prompt
    assert _HIGH_DIFFICULTY_DIRECTIVE_MULTISTEP["CHEVALIER"] in prompt


def test_system_prompt_contains_cognitive_hint_line_when_intensity_set() -> None:
    profile = build_exercise_generation_profile("ADDITION", "9-11", "PADAWAN")
    hint = profile["cognitive_hint"]
    assert hint
    prompt = build_exercise_system_prompt(
        "ADDITION",
        "PADAWAN",
        "9-11",
        DIFFICULTY_RANGES["PADAWAN"],
        "",
        calibration_desc=profile["calibration_desc"],
        cognitive_hint=hint or "",
    )
    assert "- Intensité cognitive attendue :" in prompt
    assert hint in prompt


# ---------------------------------------------------------------------------
# Lot F — clamp runtime utilisé dans generate_exercise_stream
# ---------------------------------------------------------------------------


def test_addition_grand_maitre_prompt_built_on_effective_chevalier() -> None:
    """Le prompt addition+GRAND_MAITRE doit être construit sur CHEVALIER (clamp)."""
    effective, reason = clamp_difficulty_for_type("addition", "GRAND_MAITRE")
    assert effective == "CHEVALIER"
    assert reason is not None

    profile = build_exercise_generation_profile("addition", "9-11", effective)
    prompt = build_exercise_system_prompt(
        "addition",
        effective,
        "9-11",
        build_exercise_difficulty_info("addition", effective),
        "",
        calibration_desc=profile["calibration_desc"],
        cognitive_hint=profile.get("cognitive_hint") or "",
    )
    assert "Niveau : CHEVALIER" in prompt
    assert "nombres 50-200" in prompt
    assert "GRAND_MAITRE" not in prompt


def test_geometrie_grand_maitre_prompt_stays_grand_maitre() -> None:
    """geometrie + GRAND_MAITRE reste GRAND_MAITRE (plafond = GRAND_MAITRE)."""
    effective, reason = clamp_difficulty_for_type("geometrie", "GRAND_MAITRE")
    assert effective == "GRAND_MAITRE"
    assert reason is None

    profile = build_exercise_generation_profile("geometrie", "15-17", effective)
    prompt = build_exercise_system_prompt(
        "geometrie",
        effective,
        "15-17",
        build_exercise_difficulty_info("geometrie", effective),
        "",
        calibration_desc=profile["calibration_desc"],
        cognitive_hint=profile.get("cognitive_hint") or "",
    )
    assert "Niveau : GRAND_MAITRE" in prompt
    assert "nombres 1000-10000" in prompt


def test_persisted_difficulty_uses_effective_after_clamp() -> None:
    """La difficulté persistée reflète le clamp (parité avec le prompt)."""
    effective, _ = clamp_difficulty_for_type("addition", "GRAND_MAITRE")
    persisted = {
        "exercise_type": "addition",
        "age_group": "9-11",
        "difficulty": effective,
    }
    assert persisted["difficulty"] == "CHEVALIER"


# ---------------------------------------------------------------------------
# Lot J — compact_mode pour familles o-series (prompt condensé)
# ---------------------------------------------------------------------------


def test_build_exercise_system_prompt_verbose_by_default_three_bullets() -> None:
    """Mode par défaut (non o-series) : 3 bullets séparés pour les directives."""
    prompt = build_exercise_system_prompt(
        "mixte",
        "CHEVALIER",
        "9-11",
        DIFFICULTY_RANGES["CHEVALIER"],
        "",
        calibration_desc="cal description",
        cognitive_hint="cog hint text",
    )
    assert "- Calibrage pédagogique : cal description" in prompt
    assert "- Intensité cognitive attendue : cog hint text" in prompt
    # mixte + CHEVALIER → directive non-trivialité présente (multi-étapes).
    assert "- Exigence de difficulté :" in prompt
    # Mode verbose : pas de ligne fusionnée.
    assert "- Directives pédagogiques :" not in prompt


def test_build_exercise_system_prompt_compact_mode_merges_directives() -> None:
    """Mode compact (o-series) : une seule ligne ``Directives pédagogiques``."""
    prompt = build_exercise_system_prompt(
        "mixte",
        "CHEVALIER",
        "9-11",
        DIFFICULTY_RANGES["CHEVALIER"],
        "",
        calibration_desc="cal description",
        cognitive_hint="cog hint text",
        compact_mode=True,
    )
    # Fusion : une seule ligne contenant les 3 clauses.
    assert "- Directives pédagogiques :" in prompt
    assert "calibrage=cal description" in prompt
    assert "intensité=cog hint text" in prompt
    assert "exigence=" in prompt
    # Bullets verbeux absents en mode compact.
    assert "- Calibrage pédagogique :" not in prompt
    assert "- Intensité cognitive attendue :" not in prompt
    assert "- Exigence de difficulté :" not in prompt


def test_compact_mode_omits_empty_clauses_cleanly() -> None:
    """Mode compact sans cognitive ni non-trivialité : ligne réduite sans séparateurs flottants."""
    prompt = build_exercise_system_prompt(
        "addition",
        "INITIE",  # pas de directive non-trivialité
        "6-8",
        DIFFICULTY_RANGES["INITIE"],
        "",
        calibration_desc="cal description",
        cognitive_hint="",  # vide
        compact_mode=True,
    )
    assert "- Directives pédagogiques : calibrage=cal description" in prompt
    # Aucun pipe flottant ``| |`` et pas d'intensité/exigence à vide.
    assert "| intensité=" not in prompt
    assert "| exigence=" not in prompt
    assert "| |" not in prompt


def test_compact_mode_empty_directives_produces_no_line() -> None:
    """Si tout est vide, aucune ligne de directives n'est émise."""
    prompt = build_exercise_system_prompt(
        "addition",
        "INITIE",
        "6-8",
        DIFFICULTY_RANGES["INITIE"],
        "",
        calibration_desc="",
        cognitive_hint="",
        compact_mode=True,
    )
    assert "- Directives pédagogiques :" not in prompt


def test_persist_exercise_ai_sync_forwards_runtime_difficulty_tier(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class _FakeSession:
        pass

    class _FakeSessionContext:
        def __enter__(self) -> _FakeSession:
            return _FakeSession()

        def __exit__(self, exc_type, exc, tb) -> bool:
            return False

    def fake_sync_db_session() -> _FakeSessionContext:
        return _FakeSessionContext()

    def fake_create_generated_exercise(**kwargs):
        captured.update(kwargs)
        return {"id": 1234}

    monkeypatch.setattr(
        "app.services.exercises.exercise_ai_service.sync_db_session",
        fake_sync_db_session,
    )
    monkeypatch.setattr(
        "app.services.exercises.exercise_ai_service.EnhancedServerAdapter.create_generated_exercise",
        fake_create_generated_exercise,
    )

    exercise_id = _persist_exercise_ai_sync(
        {
            "exercise_type": "mixte",
            "age_group": "9-11",
            "difficulty": "MAITRE",
            "difficulty_tier": 6,
            "title": "Titre",
            "question": "Question longue ?",
            "correct_answer": "42",
            "choices": ["40", "41", "42", "43"],
            "explanation": "Explication",
            "hint": "Indice",
            "tags": "ai,generated",
        },
        "fr",
    )

    assert exercise_id == 1234
    assert captured["difficulty_tier"] == 6
