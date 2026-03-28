"""
Pure SM-2 transition logic (F04 — intervals J+1, J+3, J+7 then × ease factor).

Deterministic: no I/O, no DB. Invalid quality raises SpacedRepetitionInputError.
"""

import math
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional

from app.exceptions import SpacedRepetitionInputError
from app.services.spaced_repetition.sm2_constants import (
    EF_DECREMENT_ON_FAILURE,
    EF_INCREMENT_FAST_CORRECT,
    INITIAL_EASE_FACTOR,
    INTERVAL_AFTER_FIRST_SUCCESS_DAYS,
    INTERVAL_AFTER_LAPSE_DAYS,
    INTERVAL_AFTER_SECOND_SUCCESS_DAYS,
    INTERVAL_AFTER_THIRD_SUCCESS_DAYS,
    MAX_EASE_FACTOR,
    MIN_EASE_FACTOR,
    QUALITY_FAST_CORRECT_THRESHOLD_SEC,
    QUALITY_INCORRECT,
    QUALITY_SLOW_CORRECT_THRESHOLD_SEC,
)


@dataclass(frozen=True)
class SM2TransitionInput:
    """Prior scheduling state before applying one review (quality)."""

    ease_factor: float
    interval_days: int
    repetition_count: int


@dataclass(frozen=True)
class SM2TransitionResult:
    """State after one SM-2 step."""

    ease_factor: float
    interval_days: int
    repetition_count: int
    next_review_date: date
    last_quality: int


def _clamp_ease(ef: float) -> float:
    rounded = round(ef, 2)
    return max(MIN_EASE_FACTOR, min(MAX_EASE_FACTOR, rounded))


def derive_quality_from_attempt(is_correct: bool, time_spent_seconds: float) -> int:
    """
    Map exercise attempt outcome to SM-2 quality 0–5.

    Incorrect -> 0. Correct: fast -> 5, slow -> 3, otherwise -> 4.
    Negative or NaN time is treated as slow path (quality 3 if correct).
    """
    if not is_correct:
        return QUALITY_INCORRECT
    try:
        t = float(time_spent_seconds)
    except (TypeError, ValueError):
        t = QUALITY_SLOW_CORRECT_THRESHOLD_SEC
    if t < 0 or math.isnan(t):
        t = QUALITY_SLOW_CORRECT_THRESHOLD_SEC
    if t <= QUALITY_FAST_CORRECT_THRESHOLD_SEC:
        return 5
    if t >= QUALITY_SLOW_CORRECT_THRESHOLD_SEC:
        return 3
    return 4


def apply_sm2_transition(
    previous: Optional[SM2TransitionInput],
    quality: int,
    review_date: date,
) -> SM2TransitionResult:
    """
    Apply one SM-2 scheduling step.

    ``review_date`` is the calendar day the review happened (UTC date in production).

    ``previous`` None means first interaction for this SR card.
    """
    if quality < 0 or quality > 5:
        raise SpacedRepetitionInputError(
            f"quality must be between 0 and 5, got {quality}"
        )

    ease = (
        float(previous.ease_factor)
        if previous is not None
        else float(INITIAL_EASE_FACTOR)
    )
    repetition = int(previous.repetition_count) if previous is not None else 0
    interval = int(previous.interval_days) if previous is not None else 1

    if quality < 3:
        new_ease = _clamp_ease(ease - EF_DECREMENT_ON_FAILURE)
        new_repetition = 0
        new_interval = INTERVAL_AFTER_LAPSE_DAYS
        next_d = review_date + timedelta(days=new_interval)
        return SM2TransitionResult(
            ease_factor=new_ease,
            interval_days=new_interval,
            repetition_count=new_repetition,
            next_review_date=next_d,
            last_quality=quality,
        )

    if quality >= 4:
        new_ease = _clamp_ease(ease + EF_INCREMENT_FAST_CORRECT)
    else:
        new_ease = _clamp_ease(ease)

    if repetition == 0:
        new_interval = INTERVAL_AFTER_FIRST_SUCCESS_DAYS
    elif repetition == 1:
        new_interval = INTERVAL_AFTER_SECOND_SUCCESS_DAYS
    elif repetition == 2:
        new_interval = INTERVAL_AFTER_THIRD_SUCCESS_DAYS
    else:
        new_interval = max(1, round(interval * new_ease))

    new_repetition = repetition + 1
    next_d = review_date + timedelta(days=new_interval)
    return SM2TransitionResult(
        ease_factor=new_ease,
        interval_days=new_interval,
        repetition_count=new_repetition,
        next_review_date=next_d,
        last_quality=quality,
    )
