"""
Tests pour le middleware d'authentification deny-by-default.

Règle projet : nouveau comportement de sécurité → test de non-régression.
"""

import pytest

from server.middleware import _is_auth_public


class TestIsAuthPublic:
    """Tests pour _is_auth_public (whitelist deny-by-default)."""

    def test_health_get_public(self):
        assert _is_auth_public("/health", "GET") is True

    def test_metrics_get_public(self):
        assert _is_auth_public("/metrics", "GET") is True

    def test_auth_login_post_public(self):
        assert _is_auth_public("/api/auth/login", "POST") is True

    def test_auth_csrf_get_public(self):
        assert _is_auth_public("/api/auth/csrf", "GET") is True

    def test_users_post_register_public(self):
        assert _is_auth_public("/api/users/", "POST") is True
        assert _is_auth_public("/api/users", "POST") is True

    def test_users_get_admin_not_public(self):
        assert _is_auth_public("/api/users/", "GET") is False

    def test_exercises_list_get_public(self):
        assert _is_auth_public("/api/exercises", "GET") is True

    def test_exercises_detail_get_public(self):
        assert _is_auth_public("/api/exercises/1", "GET") is True
        assert _is_auth_public("/api/exercises/42", "GET") is True

    def test_exercises_attempt_post_not_public(self):
        assert _is_auth_public("/api/exercises/1/attempt", "POST") is False

    def test_users_me_get_not_public(self):
        assert _is_auth_public("/api/users/me", "GET") is False

    def test_challenges_list_get_not_public(self):
        assert _is_auth_public("/api/challenges", "GET") is False

    def test_leaderboard_get_requires_auth(self):
        assert _is_auth_public("/api/users/leaderboard", "GET") is False
