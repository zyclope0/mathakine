"""Tests causaux du harness IA7 (offline uniquement)."""

from __future__ import annotations

import json
from pathlib import Path

from app.evaluation.checks import (
    check_exercise_structural_minimal,
    check_local_exercise_business_truth,
)
from app.evaluation.corpus_loader import default_corpus_path, iter_cases, load_corpus
from app.evaluation.reporting import build_markdown_summary
from app.evaluation.runners import (
    dispatch_offline,
    run_fixture_challenge,
    run_fixture_exercise_openai_shape,
    run_openai_challenge_stream,
    run_openai_exercise_stream,
)
from app.evaluation.schemas import HarnessReport


def test_print_json_falls_back_to_ascii_on_unicode_encode_error(monkeypatch):
    """IA8b : même robustesse que --show-run / --list-persisted pour consoles cp1252."""
    from app.evaluation import ai_generation_harness as mod

    attempts = {"n": 0}

    def _fake_print(*_a, **_k):
        attempts["n"] += 1
        if attempts["n"] == 1:
            raise UnicodeEncodeError("cp1252", "\u2265", 0, 1, "codec")

    monkeypatch.setattr("builtins.print", _fake_print)
    mod._print_json({"note": "≥ symbole"})
    assert attempts["n"] == 2


def test_default_corpus_loads():
    data = load_corpus()
    assert "version" in data
    assert len(data.get("cases") or []) >= 8


def test_iter_cases_offline_excludes_live_only():
    data = load_corpus()
    cases = iter_cases(data, target="all", mode="offline")
    ids = {c["id"] for c in cases}
    assert "live_openai_exercise_addition" not in ids


def test_dispatch_offline_simple_generator():
    data = load_corpus()
    case = next(c for c in data["cases"] if c["id"] == "simple_addition_6_8")
    r = dispatch_offline(case)
    assert r.pipeline == "simple_generator"
    assert r.success
    assert r.structural_ok is True
    assert r.business_ok is True


def test_fixture_exercise_negative_expected_rejection():
    data = load_corpus()
    case = next(
        c for c in data["cases"] if c["id"] == "fixture_exercise_openai_bad_hint"
    )
    r = run_fixture_exercise_openai_shape(case)
    assert r.expected_success is False
    assert r.success is True
    assert r.business_ok is False


def test_build_markdown_summary_contains_pipeline_table():
    report = HarnessReport(
        mode="offline",
        target="all",
        corpus_path=str(default_corpus_path()),
        corpus_version=1,
        cases_total=2,
        cases_run=2,
        cases_passed=2,
        cases_failed=0,
        cases_skipped=0,
        results=[
            {
                "case_id": "a",
                "pipeline": "simple_generator",
                "success": True,
                "latency_ms": 10.0,
            },
            {
                "case_id": "b",
                "pipeline": "fixture_challenge",
                "success": False,
                "failure_reason": "x",
            },
        ],
        limitations_note="test",
    )
    md = build_markdown_summary(report)
    assert "simple_generator" in md
    assert "Synthèse par pipeline" in md


def test_corpus_json_syntax():
    p = Path(__file__).resolve().parents[1] / "fixtures" / "ai_eval" / "corpus.json"
    json.loads(p.read_text(encoding="utf-8"))


def test_structural_minimal_detects_missing_choices():
    ok, err = check_exercise_structural_minimal(
        {"title": "t", "question": "q", "correct_answer": "1"}
    )
    assert not ok
    assert any("choices" in e for e in err)


def test_local_business_truth_rejects_absurd_numeric_payload():
    """Structure minimale OK mais métier incohérent (réponse absente des choix)."""
    payload = {
        "title": "Addition",
        "question": "Combien font 2 et 2 ?",
        "correct_answer": "4",
        "choices": ["1", "2", "3", "5"],
        "explanation": "La somme de deux et deux est quatre, car on regroupe les unités.",
    }
    st_ok, _ = check_exercise_structural_minimal(payload)
    assert st_ok
    biz_ok, biz_err = check_local_exercise_business_truth(payload, "addition")
    assert not biz_ok
    assert "correct_answer_absente_des_choix" in biz_err


def test_local_numeric_truth_rejects_two_plus_two_equals_999_despite_clean_shape():
    """Même avec QCM cohérent sur la forme, 2+2≠999 si opérandes connues (num1/num2)."""
    payload = {
        "title": "Addition",
        "question": "Calcule 2 + 2",
        "correct_answer": "999",
        "choices": ["999", "4", "3", "5"],
        "explanation": (
            "Pour additionner 2 et 2, on calcule la somme des deux termes, ce qui donne 4."
        ),
        "num1": 2,
        "num2": 2,
    }
    st_ok, _ = check_exercise_structural_minimal(payload)
    assert st_ok
    biz_ok, biz_err = check_local_exercise_business_truth(payload, "addition")
    assert not biz_ok
    assert any("reponse_numerique_incoherente" in e for e in biz_err)


async def test_openai_exercise_stream_expected_success_false_mocked_no_network():
    """Sémantique live : cas négatif = succès si validateurs métier échouent (mock stream)."""
    import json
    from unittest.mock import patch

    exercise = {
        "title": "Titre valide pour exercice harness mock sans appel réseau",
        "question": "Calcule 1 + 1",
        "correct_answer": "2",
        "choices": ["2", "3", "4", "5"],
        "explanation": "X" * 42,
        "hint": "ab",
    }

    async def fake_stream(*_a, **_k):
        yield f"data: {json.dumps({'type': 'exercise', 'exercise': exercise})}\n\n"

    case = {
        "id": "live_ex_neg_mock",
        "exercise_type": "addition",
        "age_group": "9-11",
        "prompt": "",
        "expected_success": False,
    }
    with patch(
        "app.services.exercises.exercise_ai_service.generate_exercise_stream",
        fake_stream,
    ):
        r = await run_openai_exercise_stream(case)
    assert r.expected_success is False
    assert r.success is True
    assert r.business_ok is False


async def test_openai_challenge_stream_error_event_expected_failure_mocked():
    """Événement error SSE : pour expected_success=false, rejet observé → succès du cas."""
    import json
    from unittest.mock import patch

    async def fake_stream(*_a, **_k):
        yield f"data: {json.dumps({'type': 'error', 'message': 'mock_failure'})}\n\n"

    case = {
        "id": "live_ch_err_mock",
        "challenge_type": "sequence",
        "age_group": "9-11",
        "prompt": "",
        "expected_success": False,
    }
    with patch(
        "app.services.challenges.challenge_ai_service.generate_challenge_stream",
        fake_stream,
    ):
        r = await run_openai_challenge_stream(case)
    assert r.success is True
    assert r.expected_success is False


def test_corpus_contains_negative_challenge_case():
    data = load_corpus()
    neg = [
        c
        for c in data["cases"]
        if c.get("pipeline") == "fixture_challenge"
        and c.get("expected_success") is False
    ]
    assert len(neg) >= 1
    assert any(
        c.get("id") == "fixture_challenge_deduction_invalid_bijection" for c in neg
    )


def test_fixture_challenge_negative_expected_rejection():
    data = load_corpus()
    case = next(
        c
        for c in data["cases"]
        if c["id"] == "fixture_challenge_deduction_invalid_bijection"
    )
    r = run_fixture_challenge(case)
    assert r.expected_success is False
    assert r.success is True
    assert r.business_ok is False
    joined = " ".join(r.business_errors or []).lower()
    assert "même valeur" in joined or "bijection" in joined


def test_harness_report_to_dict_includes_run_uuid_when_set():
    r = HarnessReport(
        mode="offline",
        target="all",
        corpus_path="p",
        corpus_version=1,
        cases_total=0,
        cases_run=0,
        cases_passed=0,
        cases_failed=0,
        cases_skipped=0,
        results=[],
        limitations_note="x",
        run_uuid="550e8400-e29b-41d4-a716-446655440000",
    )
    d = r.to_dict()
    assert d["run_uuid"] == "550e8400-e29b-41d4-a716-446655440000"


def test_offline_runs_negative_challenge_fixture():
    data = load_corpus()
    case = next(
        c
        for c in data["cases"]
        if c["id"] == "fixture_challenge_deduction_invalid_bijection"
    )
    r = dispatch_offline(case)
    assert r.pipeline == "fixture_challenge"
    assert r.success is True
    assert r.expected_success is False
