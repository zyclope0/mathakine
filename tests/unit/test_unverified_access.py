"""Tests unitaires pour app.utils.unverified_access (get_unverified_access_scope)."""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest

from app.utils.unverified_access import get_unverified_access_scope


def test_verified_user_returns_full():
    """Utilisateur vérifié → always full."""
    user = MagicMock()
    user.is_email_verified = True
    user.created_at = datetime.now(timezone.utc) - timedelta(minutes=60)
    assert get_unverified_access_scope(user) == "full"


def test_unverified_within_grace_period_returns_full():
    """Non vérifié, < 45 min après création → full."""
    user = MagicMock()
    user.is_email_verified = False
    user.created_at = datetime.now(timezone.utc) - timedelta(minutes=10)
    assert get_unverified_access_scope(user) == "full"


def test_unverified_beyond_grace_period_returns_exercises_only():
    """Non vérifié, > 45 min après création → exercises_only."""
    user = MagicMock()
    user.is_email_verified = False
    user.created_at = datetime.now(timezone.utc) - timedelta(minutes=50)
    assert get_unverified_access_scope(user) == "exercises_only"


def test_unverified_at_grace_boundary():
    """À la limite : 45 min exactement → exercises_only (strictement inférieur pour full)."""
    user = MagicMock()
    user.is_email_verified = False
    user.created_at = datetime.now(timezone.utc) - timedelta(minutes=45)
    # elapsed >= grace_seconds (45*60) → exercises_only
    assert get_unverified_access_scope(user) == "exercises_only"


def test_unverified_just_over_boundary():
    """Juste au-delà de 45 min → exercises_only."""
    user = MagicMock()
    user.is_email_verified = False
    user.created_at = datetime.now(timezone.utc) - timedelta(minutes=45, seconds=1)
    assert get_unverified_access_scope(user) == "exercises_only"


def test_missing_created_at_returns_full():
    """created_at manquant ou None → full (fallback conservateur)."""

    class UserStub:
        is_email_verified = False
        created_at = None

    assert get_unverified_access_scope(UserStub()) == "full"
