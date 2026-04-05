from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import patch

from app.services.auth.auth_session_service import get_current_user_payload


@contextmanager
def _fake_sync_db_session():
    yield object()


def test_get_current_user_payload_returns_none_for_inactive_user():
    inactive_user = SimpleNamespace(is_active=False)

    with (
        patch(
            "app.services.auth.auth_session_service.sync_db_session",
            _fake_sync_db_session,
        ),
        patch(
            "app.services.auth.auth_session_service.get_user_by_username",
            return_value=inactive_user,
        ),
    ):
        payload = get_current_user_payload("bossdesmath", {"sub": "bossdesmath"})

    assert payload is None
