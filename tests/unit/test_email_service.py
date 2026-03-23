"""Tests — masquage PII dans les logs du service email."""

import pytest

from app.services.communication.email_service import _mask_email, _mask_user


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("user@domain.com", "u***@domain.com"),
        ("ab@x.org", "a***@x.org"),
    ],
)
def test_mask_email_masks_local_and_keeps_domain(raw, expected):
    assert _mask_email(raw) == expected


def test_mask_email_empty_or_no_at_returns_placeholder():
    assert _mask_email("") == "***"
    assert _mask_email("not-an-email") == "***"


def test_mask_user_masks_prefix():
    assert _mask_user("alice@gmail.com") == "al***"
    assert _mask_user("ab") == "ab***"
    assert _mask_user("x") == "x***"


def test_mask_user_empty_returns_placeholder():
    assert _mask_user("") == "***"
    assert _mask_user(None) == "***"
