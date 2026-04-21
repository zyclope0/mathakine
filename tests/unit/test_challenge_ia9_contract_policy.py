"""IA9 — politique contrat défis (choices, response_mode, symétrie canonique)."""

from __future__ import annotations

from app.models.logic_challenge import LogicChallengeType
from app.services.challenges.challenge_ai_service import normalize_generated_challenge
from app.services.challenges.challenge_api_mapper import (
    challenge_to_detail_dict,
    challenge_to_list_item,
    resolve_challenge_response_mode,
)
from app.services.challenges.challenge_contract_policy import (
    EASY_QCM_MAX_DIFFICULTY_EXCLUSIVE,
    apply_visual_contract_normalization,
    compute_response_mode,
    filter_choices_for_persistence,
    normalize_symmetry_visual_data,
    sanitize_choices_for_delivery,
    validate_choices_policy,
    validate_symmetry_canonical,
)
from app.services.challenges.challenge_validator import validate_challenge_logic


def test_validate_choices_policy_deduction_forbids_qcm() -> None:
    err = validate_choices_policy(
        "DEDUCTION",
        3.0,
        ["a", "b", "c"],
    )
    assert err and "n'accepte pas" in err[0].lower()


def test_validate_choices_policy_coding_allows_valid_qcm_artifact() -> None:
    err = validate_choices_policy(
        "CODING",
        4.3,
        ["THE SPICE MUST FLOW", "FEAR IS THE MIND KILLER", "DESERT POWER"],
    )
    assert err == []


def test_validate_choices_policy_sequence_high_difficulty_forbids_qcm() -> None:
    err = validate_choices_policy(
        "SEQUENCE",
        4.0,
        ["121", "127", "128", "133"],
    )
    assert err and "réponse" in err[0].lower()


def test_validate_choices_policy_riddle_high_difficulty_forbids_qcm() -> None:
    err = validate_choices_policy(
        "RIDDLE",
        4.0,
        ["324", "432", "423", "342"],
    )
    assert err and "riddle" in err[0].lower()


def test_validate_choices_policy_visual_qcm_only_below_difficulty_2() -> None:
    assert not validate_choices_policy(
        "VISUAL",
        1.5,
        ["r1", "r2", "r3"],
    )
    err = validate_choices_policy(
        "VISUAL",
        2.5,
        ["r1", "r2", "r3"],
    )
    assert err and str(EASY_QCM_MAX_DIFFICULTY_EXCLUSIVE) in err[0]


def test_filter_choices_strips_visual_when_difficulty_high() -> None:
    assert (
        filter_choices_for_persistence(
            "visual",
            3.0,
            ["a", "b", "c"],
        )
        is None
    )


def test_compute_response_mode_visual_prefers_interactive_without_qcm() -> None:
    vd = {"type": "symmetry", "symmetry_line": "vertical", "layout": [{"side": "left"}]}
    assert compute_response_mode("VISUAL", vd, 3.0, None) == "interactive_visual"


def test_compute_response_mode_single_choice_when_choices_allowed() -> None:
    ch = ["8", "9", "10", "11"]
    assert (
        compute_response_mode("SEQUENCE", {"sequence": [1, 2, 3]}, 1.5, ch)
        == "single_choice"
    )


def test_compute_response_mode_sequence_high_difficulty_stays_grid_without_qcm() -> (
    None
):
    assert (
        compute_response_mode("SEQUENCE", {"sequence": [1, 2, 3, "?"]}, 4.0, None)
        == "interactive_grid"
    )


def test_normalize_symmetry_sets_type_and_symmetry_line() -> None:
    vd = normalize_symmetry_visual_data(
        {
            "symmetry_line": "vertical",
            "layout": [{"side": "LEFT", "shape": "cercle"}],
        }
    )
    assert vd.get("type") == "symmetry"
    assert vd.get("symmetry_line") == "vertical"
    assert vd["layout"][0]["side"] == "left"


def test_normalize_symmetry_converts_row_based_layout() -> None:
    """Sentry #111221704 — OpenAI génère parfois un layout row-based au lieu du format plat canonique."""
    vd = normalize_symmetry_visual_data(
        {
            "type": "symmetry",
            "symmetry_line": "vertical",
            "layout": [
                {
                    "row": 1,
                    "left": ["carré rouge", "triangle bleu"],
                    "right": ["triangle vert", "carré vert"],
                },
                {
                    "row": 2,
                    "left": ["pentagone vert", "cercle sable"],
                    "right": ["cercle rouge", "?"],
                },
            ],
        }
    )
    layout = vd.get("layout", [])
    sides = {item.get("side") for item in layout if isinstance(item, dict)}
    assert (
        "left" in sides and "right" in sides
    ), "les deux côtés doivent être présents après conversion"
    shapes = [item.get("shape") for item in layout if isinstance(item, dict)]
    assert "?" in shapes, "la cellule question doit être présente après conversion"
    question_items = [
        item for item in layout if isinstance(item, dict) and item.get("question")
    ]
    assert question_items, "au moins un item doit avoir question=True"


def test_normalize_symmetry_converts_grouped_side_elements_layout() -> None:
    vd = normalize_symmetry_visual_data(
        {
            "type": "symmetry",
            "symmetry_line": "vertical",
            "layout": [
                {
                    "side": "left",
                    "elements": [
                        "triangle rouge",
                        "carré vert",
                        "pentagone bleu",
                        "?",
                    ],
                },
                {
                    "side": "right",
                    "elements": [
                        "nonagone rouge",
                        "octogone vert",
                        "?",
                        "hexagone jaune",
                    ],
                },
            ],
        }
    )

    layout = vd.get("layout", [])
    assert len(layout) == 8
    assert layout[0] == {
        "side": "left",
        "shape": "triangle rouge",
        "position": 1,
    }
    question_items = [
        item for item in layout if isinstance(item, dict) and item.get("question")
    ]
    assert len(question_items) == 2
    assert {item.get("position") for item in question_items} == {3, 4}


def test_normalize_coding_visual_data_canonicalizes_cipher_text_alias() -> None:
    vd = apply_visual_contract_normalization(
        "coding",
        {
            "type": "substitution",
            "cipher_text": "HMNWJEIBE DS PNWER",
            "partial_key": {"rule_type": "keyword"},
        },
    )

    assert vd["encoded_message"] == "HMNWJEIBE DS PNWER"
    assert "cipher_text" not in vd


def test_normalize_coding_visual_data_nests_root_substitution_partial_key() -> None:
    vd = apply_visual_contract_normalization(
        "coding",
        {
            "type": "substitution",
            "rule_type": "keyword",
            "keyword_length": 7,
            "theme_clue": "astronomie",
            "mapping_known": {"G": "A", "A": "B"},
            "encoded_message": "KGTCEKGTDLGJ JNBDL DS OUM",
        },
    )

    assert vd["partial_key"] == {
        "keyword_length": 7,
        "theme_clue": "astronomie",
        "mapping_known": {"G": "A", "A": "B"},
        "rule_type": "keyword",
    }
    assert "keyword_length" not in vd
    assert "theme_clue" not in vd
    assert "mapping_known" not in vd


def test_validate_challenge_logic_accepts_root_substitution_partial_key_aliases() -> (
    None
):
    ok, errors = validate_challenge_logic(
        {
            "challenge_type": "CODING",
            "title": "Le mot-clé perdu de l'astronome",
            "description": "d" * 12,
            "question": "Décode le message.",
            "correct_answer": "MATHEMATICAL LOGIC IS FUN",
            "solution_explanation": "e" * 12,
            "difficulty_rating": 4.1,
            "visual_data": {
                "type": "substitution",
                "rule_type": "keyword",
                "keyword_length": 7,
                "theme_clue": "astronomie",
                "mapping_known": {"G": "A", "A": "B"},
                "encoded_message": "KGTCEKGTDLGJ JNBDL DS OUM",
            },
        }
    )

    assert ok, errors


def test_validate_symmetry_canonical_rejects_bad_side_values() -> None:
    vd = {
        "type": "symmetry",
        "symmetry_line": "vertical",
        "layout": [{"side": "north", "shape": "x"}],
    }
    err = validate_symmetry_canonical(vd)
    assert err and "side" in err[0].lower()


def test_validate_challenge_logic_rejects_visual_choices_at_high_difficulty() -> None:
    data = {
        "challenge_type": "VISUAL",
        "title": "Symétrie",
        "description": "d" * 12,
        "difficulty_rating": 3.0,
        "correct_answer": "cercle bleu",
        "solution_explanation": "e" * 12,
        "choices": ["a", "b", "c"],
        "visual_data": {
            "type": "symmetry",
            "symmetry_line": "vertical",
            "layout": [
                {"side": "left", "shape": "cercle", "question": False},
                {"side": "right", "shape": "?", "question": True},
            ],
        },
    }
    ok, errors = validate_challenge_logic(data)
    assert not ok
    assert any("choices" in e.lower() or "qcm" in e.lower() for e in errors)


class _FakeChallenge:
    def __init__(self, **kw: object) -> None:
        for k, v in kw.items():
            setattr(self, k, v)


def test_challenge_api_mapper_serializes_challenge_type_as_string() -> None:
    c = _FakeChallenge(
        id=4049,
        title="Le tirage incertain",
        description="d",
        challenge_type=LogicChallengeType.PROBABILITY,
        age_group="ADULT",
        difficulty=None,
        tags=None,
        difficulty_rating=3.8,
        estimated_time_minutes=10,
        success_rate=0.0,
        view_count=0,
        is_active=True,
        is_archived=False,
        difficulty_tier=11,
        question="q",
        correct_answer="10/27",
        choices=None,
        solution_explanation="s",
        visual_data={"urns": {"A": {"red": 5, "blue": 5}}},
        hints=[],
        generation_parameters={"response_mode": "open_text"},
    )

    assert challenge_to_list_item(c)["challenge_type"] == "probability"
    assert challenge_to_detail_dict(c)["challenge_type"] == "probability"


def test_resolve_challenge_response_mode_from_generation_parameters() -> None:
    c = _FakeChallenge(
        challenge_type="visual",
        difficulty_rating=3.0,
        visual_data={},
        choices=[],
        generation_parameters={"response_mode": "interactive_visual"},
    )
    assert resolve_challenge_response_mode(c) == "interactive_visual"


def test_resolve_challenge_response_mode_recomputes_when_missing_gp() -> None:
    c = _FakeChallenge(
        challenge_type="visual",
        difficulty_rating=3.0,
        visual_data={"type": "symmetry", "layout": [{"side": "left"}]},
        choices=["a", "b", "c"],
        generation_parameters={},
    )
    assert resolve_challenge_response_mode(c) == "interactive_visual"


def test_sanitize_choices_for_delivery_rejects_invalid_qcm() -> None:
    assert sanitize_choices_for_delivery("sequence", 3.0, ["8", "9"], "8") == []
    assert (
        sanitize_choices_for_delivery("sequence", 3.0, ["8", "9", "10", "11"], "42")
        == []
    )


def test_sanitize_choices_for_delivery_keeps_valid_qcm() -> None:
    out = sanitize_choices_for_delivery("sequence", 3.0, ["8", "9", "10", "11"], "10")
    assert out == ["8", "9", "10", "11"]


def test_sanitize_choices_for_delivery_strips_equivalent_probability_qcm() -> None:
    assert (
        sanitize_choices_for_delivery(
            "probability",
            3.8,
            ["5/18", "16/45", "10/27", "50/135"],
            "10/27",
        )
        == []
    )


def test_sanitize_choices_for_delivery_keeps_distinct_probability_qcm() -> None:
    assert sanitize_choices_for_delivery(
        "probability",
        3.8,
        ["5/18", "16/45", "10/27", "11/27"],
        "10/27",
    ) == ["5/18", "16/45", "10/27", "11/27"]


def test_normalize_generated_probability_strips_invalid_qcm_and_uses_text() -> None:
    normalized = normalize_generated_challenge(
        {
            "title": "Le tirage incertain",
            "description": "Trois urnes sont choisies au hasard.",
            "question": "Probabilite d'obtenir deux couleurs differentes.",
            "correct_answer": "10/27",
            "solution_explanation": "Calcul par probabilites totales.",
            "difficulty_rating": 4.4,
            "visual_data": {
                "urns": {
                    "A": {"red": 5, "blue": 5},
                    "B": {"red": 8, "blue": 2},
                    "C": {"red": 1, "blue": 9},
                },
                "total_per_urn": 10,
                "urn_selection": "equiprobable",
                "draws_without_replacement": 2,
                "question": "Probabilite d'obtenir deux couleurs differentes.",
            },
            "choices": ["5/18", "16/45", "10/27", "50/135"],
        },
        "probability",
        "adulte",
    )

    assert normalized["difficulty_rating"] == 3.8
    assert normalized["choices"] == []
    assert normalized["response_mode"] == "open_text"


def test_sanitize_choices_for_delivery_strips_sequence_qcm_when_high_difficulty() -> (
    None
):
    assert (
        sanitize_choices_for_delivery(
            "sequence", 4.0, ["121", "127", "128", "133"], "128"
        )
        == []
    )


def test_sanitize_choices_for_delivery_strips_riddle_qcm_when_high_difficulty() -> None:
    assert (
        sanitize_choices_for_delivery(
            "riddle", 4.0, ["324", "432", "423", "342"], "432"
        )
        == []
    )


def test_sanitize_choices_for_delivery_keeps_valid_coding_qcm_artifact() -> None:
    out = sanitize_choices_for_delivery(
        "coding",
        4.3,
        [
            "THE SPICE MUST FLOW",
            "FEAR IS THE MIND KILLER",
            "DESERT POWER AWAITS",
            "LONG LIVE THE FIGHTERS",
        ],
        "THE SPICE MUST FLOW",
    )
    assert out == [
        "THE SPICE MUST FLOW",
        "FEAR IS THE MIND KILLER",
        "DESERT POWER AWAITS",
        "LONG LIVE THE FIGHTERS",
    ]


def test_resolve_overrides_stale_gp_single_choice_when_qcm_invalid() -> None:
    c = _FakeChallenge(
        challenge_type="sequence",
        difficulty_rating=3.0,
        correct_answer="10",
        visual_data={"sequence": [1, 2, 3]},
        choices=["8", "9"],
        generation_parameters={"response_mode": "single_choice"},
    )
    assert resolve_challenge_response_mode(c) == "interactive_grid"


def test_resolve_coding_keeps_open_text_even_when_valid_choices_exist() -> None:
    c = _FakeChallenge(
        challenge_type="coding",
        difficulty_rating=4.3,
        correct_answer="THE SPICE MUST FLOW",
        visual_data={
            "type": "substitution",
            "encoded_message": "SFA ROGNA KTRS BJMW",
            "rule_type": "keyword",
        },
        choices=[
            "THE SPICE MUST FLOW",
            "FEAR IS THE MIND KILLER",
            "DESERT POWER AWAITS",
        ],
        generation_parameters={"response_mode": "single_choice"},
    )
    assert resolve_challenge_response_mode(c) == "open_text"
