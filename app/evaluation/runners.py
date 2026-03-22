"""Exécution des cas du corpus (offline / live)."""

from __future__ import annotations

import contextlib
import json
import random
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from unittest.mock import patch

from app.evaluation.checks import (
    challenge_difficulty_signals,
    check_challenge_fixture,
    check_exercise_openai_shape,
    check_exercise_structural_minimal,
    check_local_exercise_business_truth,
    exercise_choices_signals,
)
from app.evaluation.schemas import CaseResult

FIXTURES_DIR = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "ai_eval"

PEDAGOGICAL_LIMITATION = (
    "Distinction explicite : structure + règles métier codées + heuristiques difficulté. "
    "Pas de mesure de qualité pédagogique globale (clarté, charge cognitive, biais)."
)


def _normalize_harness_eval_model(
    raw: Optional[str],
) -> Tuple[Optional[str], Optional[str]]:
    """
    Retourne (model_id_normalisé, message_erreur).

    ``None`` = pas d’override (comportement produit inchangé pour ce run).
    """
    if raw is None:
        return None, None
    s = str(raw).strip()
    if not s:
        return None, None
    from app.core.ai_generation_policy import (
        ExerciseAIModelNotAllowedError,
        assert_exercise_ai_model_allowed,
        normalize_exercise_ai_model_id,
    )

    try:
        nid = normalize_exercise_ai_model_id(s)
        assert_exercise_ai_model_allowed(nid)
        return nid, None
    except ExerciseAIModelNotAllowedError as e:
        return None, str(e)
    except ValueError as e:
        return None, str(e)


def _load_json_fixture(name: str) -> Dict[str, Any]:
    path = FIXTURES_DIR / name
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _expected_success(case: Dict[str, Any]) -> bool:
    return bool(case.get("expected_success", True))


def run_simple_generator(case: Dict[str, Any]) -> CaseResult:
    cid = case["id"]
    exp = _expected_success(case)
    seed = int(case.get("rng_seed", 0))
    random.seed(seed)
    t0 = time.perf_counter()
    from app.generators.exercise_generator import generate_simple_exercise

    try:
        payload = generate_simple_exercise(case["exercise_type"], case["age_group"])
    except Exception as e:
        return CaseResult(
            case_id=cid,
            pipeline="simple_generator",
            success=False,
            failure_reason=f"exception:{e}",
            latency_ms=(time.perf_counter() - t0) * 1000,
            pedagogical_note=PEDAGOGICAL_LIMITATION,
            rationale=case.get("rationale"),
            expected_success=exp,
        )
    latency = (time.perf_counter() - t0) * 1000
    st_ok, st_err = check_exercise_structural_minimal(payload)
    biz_ok, biz_err = check_local_exercise_business_truth(
        payload, str(case.get("exercise_type", ""))
    )
    if exp:
        success = st_ok and biz_ok
    else:
        success = not (st_ok and biz_ok)
    reasons: List[str] = []
    if not st_ok:
        reasons.append("structural:" + ",".join(st_err))
    if not biz_ok:
        reasons.append("business:" + ",".join(biz_err))
    failure_reason: Optional[str] = None
    if exp and not success:
        failure_reason = "; ".join(reasons) if reasons else "validation_failed"
    if not exp and not success:
        failure_reason = "negative_case_passed_validation_unexpectedly"
    return CaseResult(
        case_id=cid,
        pipeline="simple_generator",
        success=success,
        failure_reason=failure_reason,
        latency_ms=latency,
        structural_ok=st_ok,
        structural_errors=st_err,
        business_ok=biz_ok,
        business_errors=biz_err,
        choices_flags=exercise_choices_signals(
            str(payload.get("exercise_type", case["exercise_type"])),
            str(payload.get("correct_answer", "")),
            payload.get("choices"),
        ),
        rationale=case.get("rationale"),
        pedagogical_note=PEDAGOGICAL_LIMITATION,
        expected_success=exp,
    )


def run_template_exercise_generator(case: Dict[str, Any]) -> CaseResult:
    cid = case["id"]
    exp = _expected_success(case)
    seed = int(case.get("rng_seed", 0))
    random.seed(seed)
    t0 = time.perf_counter()
    from app.generators.exercise_generator import generate_ai_exercise

    try:
        payload = generate_ai_exercise(case["exercise_type"], case["age_group"])
    except Exception as e:
        return CaseResult(
            case_id=cid,
            pipeline="template_exercise_generator",
            success=False,
            failure_reason=f"exception:{e}",
            latency_ms=(time.perf_counter() - t0) * 1000,
            rationale=case.get("rationale"),
            pedagogical_note=PEDAGOGICAL_LIMITATION,
            expected_success=exp,
        )
    latency = (time.perf_counter() - t0) * 1000
    st_ok, st_err = check_exercise_structural_minimal(payload)
    biz_ok, biz_err = check_local_exercise_business_truth(
        payload, str(case.get("exercise_type", ""))
    )
    if exp:
        success = st_ok and biz_ok
    else:
        success = not (st_ok and biz_ok)
    reasons = []
    if not st_ok:
        reasons.append("structural:" + ",".join(st_err))
    if not biz_ok:
        reasons.append("business:" + ",".join(biz_err))
    failure_reason = None
    if exp and not success:
        failure_reason = "; ".join(reasons) if reasons else "validation_failed"
    if not exp and not success:
        failure_reason = "negative_case_passed_validation_unexpectedly"
    return CaseResult(
        case_id=cid,
        pipeline="template_exercise_generator",
        success=success,
        failure_reason=failure_reason,
        latency_ms=latency,
        structural_ok=st_ok,
        structural_errors=st_err,
        business_ok=biz_ok,
        business_errors=biz_err,
        choices_flags=exercise_choices_signals(
            str(payload.get("exercise_type", case["exercise_type"])),
            str(payload.get("correct_answer", "")),
            payload.get("choices"),
        ),
        rationale=case.get("rationale"),
        pedagogical_note=PEDAGOGICAL_LIMITATION,
        expected_success=exp,
    )


def run_fixture_exercise_openai_shape(case: Dict[str, Any]) -> CaseResult:
    cid = case["id"]
    exp = _expected_success(case)
    name = case["fixture"]
    t0 = time.perf_counter()
    raw = _load_json_fixture(name)
    latency = (time.perf_counter() - t0) * 1000
    et = str(raw.get("exercise_type", "addition"))
    biz_ok, biz_err = check_exercise_openai_shape(
        exercise_type=et,
        title=str(raw.get("title", "")),
        question=str(raw.get("question", "")),
        correct_answer=str(raw.get("correct_answer", "")),
        choices=raw.get("choices"),
        explanation=str(raw.get("explanation", "")),
        hint=str(raw.get("hint", "")),
    )
    st_ok, st_err = check_exercise_structural_minimal(raw)
    if exp:
        success = st_ok and biz_ok
    else:
        success = not (st_ok and biz_ok)
    reasons: List[str] = []
    if not st_ok:
        reasons.append("structural:" + ",".join(st_err))
    if not biz_ok:
        reasons.append("business:" + ",".join(biz_err))
    failure_reason: Optional[str] = None
    if exp and not success:
        failure_reason = "; ".join(reasons) if reasons else "validation_failed"
    if not exp and not success:
        failure_reason = "negative_case_passed_validation_unexpectedly"
    return CaseResult(
        case_id=cid,
        pipeline="fixture_exercise_openai_shape",
        success=success,
        failure_reason=failure_reason,
        latency_ms=latency,
        structural_ok=st_ok,
        structural_errors=st_err,
        business_ok=biz_ok,
        business_errors=biz_err,
        choices_flags=exercise_choices_signals(
            et, str(raw.get("correct_answer", "")), raw.get("choices")
        ),
        rationale=case.get("rationale"),
        pedagogical_note=PEDAGOGICAL_LIMITATION,
        expected_success=exp,
    )


def run_fixture_challenge(case: Dict[str, Any]) -> CaseResult:
    cid = case["id"]
    exp = _expected_success(case)
    name = case["fixture"]
    t0 = time.perf_counter()
    data = _load_json_fixture(name)
    latency = (time.perf_counter() - t0) * 1000
    biz_ok, biz_err = check_challenge_fixture(data)
    diff = challenge_difficulty_signals(data)
    ch_choices: Dict[str, Any] = {}
    try:
        from app.services.challenges.challenge_answer_quality import (
            validate_challenge_choices,
        )

        ct = str(data.get("challenge_type", "")).upper()
        ca = str(data.get("correct_answer", ""))
        ch = data.get("choices")
        qcm_err = validate_challenge_choices(ct, ca, ch)
        ch_choices = {"validate_challenge_choices_errors": list(qcm_err or [])}
    except Exception as e:
        ch_choices = {"validate_challenge_choices_errors": [f"skip:{e}"]}

    qcm = ch_choices.get("validate_challenge_choices_errors") or []
    validators_pass = biz_ok and len(qcm) == 0
    if exp:
        success = validators_pass
    else:
        success = not validators_pass
    fail_parts: List[str] = []
    if not biz_ok:
        fail_parts.append("challenge_logic:" + ",".join(biz_err[:5]))
    if qcm:
        fail_parts.append("choices:" + ",".join(str(x) for x in qcm[:3]))
    failure_reason: Optional[str] = None
    if exp and not success:
        failure_reason = "; ".join(fail_parts) if fail_parts else "validation_failed"
    if not exp and not success:
        failure_reason = "negative_case_passed_validation_unexpectedly"
    return CaseResult(
        case_id=cid,
        pipeline="fixture_challenge",
        success=success,
        failure_reason=failure_reason,
        latency_ms=latency,
        structural_ok=True,
        business_ok=biz_ok,
        business_errors=biz_err,
        difficulty_flags=diff,
        choices_flags=ch_choices,
        rationale=case.get("rationale"),
        pedagogical_note=PEDAGOGICAL_LIMITATION,
        expected_success=exp,
    )


def _parse_sse_chunks(chunks: List[str]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for block in chunks:
        for line in block.split("\n"):
            line = line.strip()
            if line.startswith("data: "):
                try:
                    out.append(json.loads(line[6:]))
                except json.JSONDecodeError:
                    out.append({"type": "parse_error", "raw": line[:120]})
    return out


async def run_openai_exercise_stream(
    case: Dict[str, Any],
    model_override: Optional[str] = None,
) -> CaseResult:
    cid = case["id"]
    exp = _expected_success(case)
    from app.services.exercises.exercise_ai_service import generate_exercise_stream
    from app.utils.exercise_generator_validators import (
        normalize_and_validate_exercise_params,
    )

    override_norm, override_err = _normalize_harness_eval_model(model_override)
    if override_err:
        return CaseResult(
            case_id=cid,
            pipeline="openai_exercise_stream",
            success=False,
            failure_reason=f"eval_model_invalid:{override_err}",
            eval_model=str(model_override).strip() if model_override else None,
            rationale=case.get("rationale"),
            pedagogical_note=PEDAGOGICAL_LIMITATION,
            expected_success=exp,
        )

    ex_t, ag, dd = normalize_and_validate_exercise_params(
        case["exercise_type"], case["age_group"]
    )
    t0 = time.perf_counter()
    chunks: List[str] = []
    try:

        def _fake_persist(*_a: Any, **_k: Any) -> int:
            return 424242

        with contextlib.ExitStack() as stack:
            stack.enter_context(
                patch(
                    "app.services.exercises.exercise_ai_service._persist_exercise_ai_sync",
                    _fake_persist,
                )
            )
            if override_norm is not None:
                stack.enter_context(
                    patch(
                        "app.services.exercises.exercise_ai_service.resolve_exercise_ai_model",
                        lambda: override_norm,
                    )
                )
            async for event in generate_exercise_stream(
                exercise_type=ex_t,
                age_group=ag,
                derived_difficulty=dd,
                prompt=str(case.get("prompt", "")),
                locale="fr",
                user_id=None,
            ):
                chunks.append(event)
    except Exception as e:
        return CaseResult(
            case_id=cid,
            pipeline="openai_exercise_stream",
            success=False,
            failure_reason=f"exception:{e}",
            latency_ms=(time.perf_counter() - t0) * 1000,
            eval_model=override_norm,
            rationale=case.get("rationale"),
            pedagogical_note=PEDAGOGICAL_LIMITATION,
            expected_success=exp,
        )
    latency = (time.perf_counter() - t0) * 1000
    events = _parse_sse_chunks(chunks)
    exercise_obj: Optional[Dict[str, Any]] = None
    err_msg: Optional[str] = None
    for ev in events:
        if ev.get("type") == "exercise":
            exercise_obj = ev.get("exercise")
        if ev.get("type") == "error":
            err_msg = str(ev.get("message", "error"))

    if not exercise_obj:
        if err_msg:
            if exp:
                return CaseResult(
                    case_id=cid,
                    pipeline="openai_exercise_stream",
                    success=False,
                    failure_reason=err_msg,
                    latency_ms=latency,
                    eval_model=override_norm,
                    rationale=case.get("rationale"),
                    pedagogical_note=PEDAGOGICAL_LIMITATION,
                    expected_success=exp,
                )
            return CaseResult(
                case_id=cid,
                pipeline="openai_exercise_stream",
                success=True,
                failure_reason=None,
                latency_ms=latency,
                eval_model=override_norm,
                rationale=case.get("rationale"),
                pedagogical_note=PEDAGOGICAL_LIMITATION,
                expected_success=exp,
            )
        return CaseResult(
            case_id=cid,
            pipeline="openai_exercise_stream",
            success=False,
            failure_reason="no_exercise_event",
            latency_ms=latency,
            eval_model=override_norm,
            rationale=case.get("rationale"),
            pedagogical_note=PEDAGOGICAL_LIMITATION,
            expected_success=exp,
        )

    biz_ok, biz_err = check_exercise_openai_shape(
        exercise_type=ex_t,
        title=str(exercise_obj.get("title", "")),
        question=str(exercise_obj.get("question", "")),
        correct_answer=str(exercise_obj.get("correct_answer", "")),
        choices=exercise_obj.get("choices"),
        explanation=str(exercise_obj.get("explanation", "")),
        hint=str(exercise_obj.get("hint", "")),
    )
    st_ok, st_err = check_exercise_structural_minimal(exercise_obj)
    validators_pass = st_ok and biz_ok
    if exp:
        success = validators_pass
    else:
        success = not validators_pass
    fail_parts: List[str] = []
    if not st_ok:
        fail_parts.append("structural:" + ",".join(st_err))
    if not biz_ok:
        fail_parts.append("business:" + ",".join(biz_err))
    failure_reason: Optional[str] = None
    if exp and not success:
        failure_reason = "; ".join(fail_parts) if fail_parts else "validation_failed"
    if not exp and not success:
        failure_reason = "negative_case_passed_validation_unexpectedly"
    return CaseResult(
        case_id=cid,
        pipeline="openai_exercise_stream",
        success=success,
        failure_reason=failure_reason,
        latency_ms=latency,
        structural_ok=st_ok,
        structural_errors=st_err,
        business_ok=biz_ok,
        business_errors=biz_err,
        choices_flags=exercise_choices_signals(
            ex_t,
            str(exercise_obj.get("correct_answer", "")),
            exercise_obj.get("choices"),
        ),
        eval_model=override_norm,
        rationale=case.get("rationale"),
        pedagogical_note=PEDAGOGICAL_LIMITATION,
        expected_success=exp,
    )


async def run_openai_challenge_stream(
    case: Dict[str, Any],
    model_override: Optional[str] = None,
) -> CaseResult:
    cid = case["id"]
    exp = _expected_success(case)
    override_norm, override_err = _normalize_harness_eval_model(model_override)
    if override_err:
        return CaseResult(
            case_id=cid,
            pipeline="openai_challenge_stream",
            success=False,
            failure_reason=f"eval_model_invalid:{override_err}",
            eval_model=str(model_override).strip() if model_override else None,
            rationale=case.get("rationale"),
            pedagogical_note=PEDAGOGICAL_LIMITATION,
            expected_success=exp,
        )

    from app.services.challenges.challenge_ai_service import generate_challenge_stream

    ct = str(case.get("challenge_type", "sequence")).lower()
    ag = str(case.get("age_group", "9-11"))
    prompt = str(case.get("prompt", ""))
    t0 = time.perf_counter()
    chunks: List[str] = []

    def _fake_persist_challenge(
        normalized_challenge: Dict[str, Any],
        user_id: Optional[int],
        challenge_type: str,
        model: str = "unknown",
    ) -> Dict[str, Any]:
        return {
            "id": 424242,
            "title": normalized_challenge.get("title", ""),
            "description": normalized_challenge.get("description", ""),
            "challenge_type": challenge_type,
            "age_group": ag,
            "question": normalized_challenge.get("question"),
            "correct_answer": normalized_challenge.get("correct_answer"),
            "solution_explanation": normalized_challenge.get("solution_explanation"),
            "hints": normalized_challenge.get("hints") or [],
            "visual_data": normalized_challenge.get("visual_data") or {},
            "difficulty_rating": normalized_challenge.get("difficulty_rating", 3.0),
            "choices": normalized_challenge.get("choices") or [],
        }

    try:
        with contextlib.ExitStack() as stack:
            stack.enter_context(
                patch(
                    "app.services.challenges.challenge_ai_service._persist_challenge_sync",
                    _fake_persist_challenge,
                )
            )
            if override_norm is not None:
                stack.enter_context(
                    patch(
                        "app.services.challenges.challenge_ai_model_policy.resolve_challenge_ai_model",
                        lambda _challenge_type: override_norm,
                    )
                )
            async for event in generate_challenge_stream(
                challenge_type=ct,
                age_group=ag,
                prompt=prompt,
                user_id=1,
                locale="fr",
            ):
                chunks.append(event)
    except Exception as e:
        return CaseResult(
            case_id=cid,
            pipeline="openai_challenge_stream",
            success=False,
            failure_reason=f"exception:{e}",
            latency_ms=(time.perf_counter() - t0) * 1000,
            eval_model=override_norm,
            rationale=case.get("rationale"),
            pedagogical_note=PEDAGOGICAL_LIMITATION,
            expected_success=exp,
        )
    latency = (time.perf_counter() - t0) * 1000
    events = _parse_sse_chunks(chunks)
    ch_obj: Optional[Dict[str, Any]] = None
    err_msg: Optional[str] = None
    for ev in events:
        if ev.get("type") == "challenge":
            ch_obj = ev.get("challenge")
        if ev.get("type") == "error":
            err_msg = str(ev.get("message", "error"))

    if not ch_obj:
        if err_msg:
            if exp:
                return CaseResult(
                    case_id=cid,
                    pipeline="openai_challenge_stream",
                    success=False,
                    failure_reason=err_msg,
                    latency_ms=latency,
                    eval_model=override_norm,
                    rationale=case.get("rationale"),
                    pedagogical_note=PEDAGOGICAL_LIMITATION,
                    expected_success=exp,
                )
            return CaseResult(
                case_id=cid,
                pipeline="openai_challenge_stream",
                success=True,
                failure_reason=None,
                latency_ms=latency,
                eval_model=override_norm,
                rationale=case.get("rationale"),
                pedagogical_note=PEDAGOGICAL_LIMITATION,
                expected_success=exp,
            )
        return CaseResult(
            case_id=cid,
            pipeline="openai_challenge_stream",
            success=False,
            failure_reason="no_challenge_event",
            latency_ms=latency,
            eval_model=override_norm,
            rationale=case.get("rationale"),
            pedagogical_note=PEDAGOGICAL_LIMITATION,
            expected_success=exp,
        )

    data = {
        "challenge_type": (
            ch_obj.get("challenge_type", ct).upper()
            if isinstance(ch_obj.get("challenge_type"), str)
            else str(ch_obj.get("challenge_type", ct)).upper()
        ),
        "title": ch_obj.get("title", ""),
        "description": ch_obj.get("description", "") or ch_obj.get("question", ""),
        "correct_answer": ch_obj.get("correct_answer", ""),
        "solution_explanation": ch_obj.get("solution_explanation", ""),
        "visual_data": ch_obj.get("visual_data") or {},
        "difficulty_rating": float(ch_obj.get("difficulty_rating") or 3.0),
        "choices": ch_obj.get("choices"),
    }
    biz_ok, biz_err = check_challenge_fixture(data)
    diff = challenge_difficulty_signals(data)
    ch_choices_live: Dict[str, Any] = {}
    try:
        from app.services.challenges.challenge_answer_quality import (
            validate_challenge_choices,
        )

        ct_u = str(data.get("challenge_type", "")).upper()
        ca_s = str(data.get("correct_answer", ""))
        qcm_err = validate_challenge_choices(ct_u, ca_s, data.get("choices"))
        ch_choices_live = {"validate_challenge_choices_errors": list(qcm_err or [])}
    except Exception as e:
        ch_choices_live = {"validate_challenge_choices_errors": [f"skip:{e}"]}

    qcm_live = ch_choices_live.get("validate_challenge_choices_errors") or []
    validators_pass = biz_ok and len(qcm_live) == 0
    if exp:
        success = validators_pass
    else:
        success = not validators_pass
    fail_parts_ch: List[str] = []
    if not biz_ok:
        fail_parts_ch.append("challenge_logic:" + ",".join(biz_err[:8]))
    if qcm_live:
        fail_parts_ch.append("choices:" + ",".join(str(x) for x in qcm_live[:3]))
    failure_reason_ch: Optional[str] = None
    if exp and not success:
        failure_reason_ch = (
            "; ".join(fail_parts_ch) if fail_parts_ch else "validation_failed"
        )
    if not exp and not success:
        failure_reason_ch = "negative_case_passed_validation_unexpectedly"
    return CaseResult(
        case_id=cid,
        pipeline="openai_challenge_stream",
        success=success,
        failure_reason=failure_reason_ch,
        latency_ms=latency,
        structural_ok=True,
        business_ok=biz_ok,
        business_errors=biz_err,
        difficulty_flags=diff,
        choices_flags=ch_choices_live,
        eval_model=override_norm,
        rationale=case.get("rationale"),
        pedagogical_note=PEDAGOGICAL_LIMITATION,
        expected_success=exp,
    )


def dispatch_offline(case: Dict[str, Any]) -> CaseResult:
    pipe = case["pipeline"]
    if pipe == "simple_generator":
        return run_simple_generator(case)
    if pipe == "template_exercise_generator":
        return run_template_exercise_generator(case)
    if pipe == "fixture_exercise_openai_shape":
        return run_fixture_exercise_openai_shape(case)
    if pipe == "fixture_challenge":
        return run_fixture_challenge(case)
    if pipe in ("openai_exercise_stream", "openai_challenge_stream"):
        return CaseResult(
            case_id=case["id"],
            pipeline=pipe,
            success=False,
            live_skipped=True,
            skip_reason="live_only_pipeline_in_offline_mode",
            rationale=case.get("rationale"),
            expected_success=_expected_success(case),
        )
    return CaseResult(
        case_id=case.get("id", "?"),
        pipeline=str(pipe),
        success=False,
        failure_reason="unknown_pipeline",
        expected_success=_expected_success(case),
    )


async def dispatch_live(case: Dict[str, Any]) -> CaseResult:
    pipe = case["pipeline"]
    mo = case.get("eval_model")
    mo_s = str(mo).strip() if mo is not None else ""
    override = mo_s if mo_s else None
    if pipe == "openai_exercise_stream":
        return await run_openai_exercise_stream(case, model_override=override)
    if pipe == "openai_challenge_stream":
        return await run_openai_challenge_stream(case, model_override=override)
    return dispatch_offline(case)
