"""Causal tests for pure SM-2 engine (F04-P1)."""

from datetime import date

import pytest

from app.exceptions import SpacedRepetitionInputError
from app.services.spaced_repetition.sm2_constants import (
    EF_DECREMENT_ON_FAILURE,
    EF_INCREMENT_FAST_CORRECT,
    INITIAL_EASE_FACTOR,
    INTERVAL_AFTER_FIRST_SUCCESS_DAYS,
    INTERVAL_AFTER_LAPSE_DAYS,
    INTERVAL_AFTER_SECOND_SUCCESS_DAYS,
    INTERVAL_AFTER_THIRD_SUCCESS_DAYS,
    MIN_EASE_FACTOR,
)
from app.services.spaced_repetition.sm2_engine import (
    SM2TransitionInput,
    apply_sm2_transition,
    derive_quality_from_attempt,
)


def test_first_successful_review_schedules_one_day():
    d0 = date(2026, 3, 1)
    r = apply_sm2_transition(None, 5, d0)
    assert r.repetition_count == 1
    assert r.interval_days == INTERVAL_AFTER_FIRST_SUCCESS_DAYS
    assert r.next_review_date == date(2026, 3, 2)
    assert r.ease_factor == round(INITIAL_EASE_FACTOR + EF_INCREMENT_FAST_CORRECT, 2)
    assert r.last_quality == 5


def test_second_successful_review_schedules_three_days():
    d1 = date(2026, 3, 5)
    prev = SM2TransitionInput(ease_factor=2.6, interval_days=1, repetition_count=1)
    r = apply_sm2_transition(prev, 4, d1)
    assert r.repetition_count == 2
    assert r.interval_days == INTERVAL_AFTER_SECOND_SUCCESS_DAYS
    assert r.next_review_date == date(2026, 3, 8)


def test_third_successful_review_schedules_seven_days():
    d = date(2026, 4, 1)
    prev = SM2TransitionInput(ease_factor=2.5, interval_days=3, repetition_count=2)
    r = apply_sm2_transition(prev, 5, d)
    assert r.repetition_count == 3
    assert r.interval_days == INTERVAL_AFTER_THIRD_SUCCESS_DAYS
    assert r.next_review_date == date(2026, 4, 8)


def test_fourth_plus_uses_interval_times_ease():
    d = date(2026, 5, 1)
    prev = SM2TransitionInput(ease_factor=2.0, interval_days=7, repetition_count=3)
    r = apply_sm2_transition(prev, 3, d)
    assert r.repetition_count == 4
    assert r.interval_days == max(1, round(7 * 2.0))
    assert r.next_review_date == date(2026, 5, 15)


def test_fast_correct_raises_ease_slow_correct_unchanged():
    d = date(2026, 1, 10)
    prev = SM2TransitionInput(ease_factor=2.5, interval_days=1, repetition_count=1)
    fast = apply_sm2_transition(prev, 5, d)
    assert fast.ease_factor == round(2.5 + EF_INCREMENT_FAST_CORRECT, 2)
    slow = apply_sm2_transition(prev, 3, d)
    assert slow.ease_factor == 2.5


def test_failure_resets_interval_and_drops_ease():
    d = date(2026, 2, 1)
    prev = SM2TransitionInput(ease_factor=2.5, interval_days=7, repetition_count=3)
    r = apply_sm2_transition(prev, 0, d)
    assert r.repetition_count == 0
    assert r.interval_days == INTERVAL_AFTER_LAPSE_DAYS
    assert r.next_review_date == date(2026, 2, 2)
    assert r.ease_factor == round(2.5 - EF_DECREMENT_ON_FAILURE, 2)


def test_failure_clamps_ease_at_minimum():
    d = date(2026, 2, 1)
    prev = SM2TransitionInput(
        ease_factor=MIN_EASE_FACTOR, interval_days=3, repetition_count=2
    )
    r = apply_sm2_transition(prev, 1, d)
    assert r.ease_factor == MIN_EASE_FACTOR


def test_derive_quality_fast_slow_incorrect():
    assert derive_quality_from_attempt(False, 5.0) == 0
    assert derive_quality_from_attempt(True, 30.0) == 5
    assert derive_quality_from_attempt(True, 90.0) == 4
    assert derive_quality_from_attempt(True, 150.0) == 3


def test_derive_quality_zero_or_invalid_time_falls_back_to_slow_path():
    assert derive_quality_from_attempt(True, 0.0) == 3
    assert derive_quality_from_attempt(True, -1.0) == 3
    assert derive_quality_from_attempt(True, float("nan")) == 3
    assert derive_quality_from_attempt(True, None) == 3


def test_invalid_quality_raises():
    with pytest.raises(SpacedRepetitionInputError):
        apply_sm2_transition(None, 6, date(2026, 1, 1))


def test_apply_sm2_transition_deterministic_repeat():
    prev = SM2TransitionInput(ease_factor=2.5, interval_days=1, repetition_count=0)
    d = date(2026, 6, 1)
    a = apply_sm2_transition(prev, 4, d)
    b = apply_sm2_transition(prev, 4, d)
    assert a == b
