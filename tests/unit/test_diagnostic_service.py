"""Tests ciblés diagnostic — pending storage (I7) + façade diagnostic_service."""

import time

import pytest

from app.core.constants import ExerciseTypes
from app.services.diagnostic import diagnostic_pending_storage
from app.services.diagnostic.diagnostic_service import (
    apply_answer_and_advance,
    check_answer,
    create_session,
    delete_pending_state,
    get_pending_state,
    load_pending_state,
    store_pending_state,
)


@pytest.fixture
def force_memory_pending(monkeypatch):
    """Force le fallback memoire (pas de Redis) pour des tests deterministes."""
    monkeypatch.setattr(
        diagnostic_pending_storage, "_get_pending_state_redis_client", lambda: None
    )
    diagnostic_pending_storage._pending_state_memory.clear()


def test_store_load_delete_pending_roundtrip(force_memory_pending):
    ref = store_pending_state({"correct_answer": "42", "exercise_type": "ADDITION"})
    assert isinstance(ref, str) and len(ref) > 10
    loaded = load_pending_state(ref)
    assert loaded == {"correct_answer": "42", "exercise_type": "ADDITION"}
    delete_pending_state(ref)
    assert load_pending_state(ref) is None


def test_pending_expires_from_memory(force_memory_pending, monkeypatch):
    ref = store_pending_state({"correct_answer": "1"})
    # Expirer immediatement
    past = time.time() - 1
    diagnostic_pending_storage._pending_state_memory[ref] = (
        past,
        {"correct_answer": "1"},
    )
    assert load_pending_state(ref) is None


def test_get_pending_state_from_signed_state_shape(force_memory_pending):
    ref = store_pending_state({"correct_answer": "7"})
    state = {"session": create_session(), "pending_ref": ref}
    assert get_pending_state(state)["correct_answer"] == "7"


def test_check_answer_compares_pending(force_memory_pending):
    ref = store_pending_state({"correct_answer": " 12 "})
    state = {"session": create_session(), "pending_ref": ref}
    assert check_answer(state, "12") is True
    assert check_answer(state, "13") is False


def test_apply_answer_and_advance_clears_pending(force_memory_pending):
    ref = store_pending_state({"correct_answer": "3"})
    state = {"session": create_session(), "pending_ref": ref}
    apply_answer_and_advance(state, ExerciseTypes.ADDITION, is_correct=True)
    assert state.get("pending_ref") is None
    assert load_pending_state(ref) is None


def test_diagnostic_service_reexports_pending_api():
    """Les handlers utilisent diagnostic_service.store_pending_state, etc."""
    from app.services.diagnostic import diagnostic_service as ds

    assert ds.store_pending_state is store_pending_state
    assert ds.get_pending_state is get_pending_state


def test_get_latest_score_includes_f42_projection(db_session):
    from app.core.constants import AgeGroups, DifficultyLevels
    from app.core.security import get_password_hash
    from app.models.diagnostic_result import DiagnosticResult
    from app.models.user import User, UserRole
    from app.services.diagnostic.diagnostic_service import get_latest_score
    from app.utils.db_helpers import get_enum_value
    from tests.utils.test_helpers import unique_email, unique_username

    user = User(
        username=unique_username(),
        email=unique_email(),
        hashed_password=get_password_hash("Test123!Ab"),
        role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
        age_group="6-8",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    dr = DiagnosticResult(
        user_id=user.id,
        triggered_from="onboarding",
        scores={
            "addition": {
                "level": 1,
                "difficulty": DifficultyLevels.PADAWAN,
                "correct": 1,
                "total": 2,
            },
        },
        questions_asked=2,
    )
    db_session.add(dr)
    db_session.commit()

    out = get_latest_score(db_session, user.id)
    assert out is not None
    assert out["canonical_age_group_f42"] == AgeGroups.GROUP_6_8
    assert "scores_f42" in out
    assert out["scores_f42"]["addition"]["pedagogical_band"] == "learning"
    assert out["scores_f42"]["addition"]["difficulty_tier"] == 2
    assert out["scores"]["addition"]["difficulty"] == DifficultyLevels.PADAWAN
