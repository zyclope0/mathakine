"""Explicit SM-2 constants (F04 spec — Mathakine)."""

# Ease factor (SuperMemo-style bounds)
INITIAL_EASE_FACTOR: float = 2.5
MIN_EASE_FACTOR: float = 1.3
MAX_EASE_FACTOR: float = 3.0

EF_INCREMENT_FAST_CORRECT: float = 0.1
EF_DECREMENT_ON_FAILURE: float = 0.2

# First three successful review intervals (days), then interval × EF
INTERVAL_AFTER_FIRST_SUCCESS_DAYS: int = 1
INTERVAL_AFTER_SECOND_SUCCESS_DAYS: int = 3
INTERVAL_AFTER_THIRD_SUCCESS_DAYS: int = 7

# After a failed review (quality < 3), next review is this many days out
INTERVAL_AFTER_LAPSE_DAYS: int = 1

# Quality scale 0–5 (SM-2); derived from correctness + time (seconds)
QUALITY_INCORRECT: int = 0
QUALITY_FAST_CORRECT_THRESHOLD_SEC: float = 60.0
QUALITY_SLOW_CORRECT_THRESHOLD_SEC: float = 120.0
