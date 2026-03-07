"""
Tests unitaires F35 — Redaction des URLs DB dans les logs.
"""

import pytest

from app.db.base import redact_database_url_for_log


def test_redact_postgres_url_with_password():
    """URL PostgreSQL avec user/password : password et username masqués."""
    url = "postgresql://myuser:secret123@db-host:5432/mathakine"
    result = redact_database_url_for_log(url)
    assert "secret" not in result
    assert "myuser" not in result
    assert "db-host" in result
    assert "5432" in result
    assert "mathakine" in result
    assert "<redacted>" in result


def test_redact_postgres_url_without_password():
    """URL PostgreSQL sans password : username masqué."""
    url = "postgresql://myuser@localhost:5432/test_db"
    result = redact_database_url_for_log(url)
    assert "myuser" not in result
    assert "localhost" in result
    assert "test_db" in result


def test_redact_url_with_query_params():
    """Query params ne doivent pas apparaître."""
    url = "postgresql://u:p@host/db?sslmode=require&password=leak"
    result = redact_database_url_for_log(url)
    assert "sslmode" not in result
    assert "password" not in result
    assert "leak" not in result
    assert "?" not in result


def test_redact_sqlite_url():
    """URL SQLite : chemin masqué."""
    url = "sqlite:///path/to/sensitive.db"
    result = redact_database_url_for_log(url)
    assert result == "sqlite://[redacted]"
    assert "sensitive" not in result
    assert "path" not in result


def test_redact_invalid_url():
    """URL invalide : fallback sûr."""
    result = redact_database_url_for_log("not-a-valid-url://")
    assert result == "[redacted-db-url]"


def test_redact_empty_url():
    """URL vide : fallback sûr."""
    assert redact_database_url_for_log("") == "[redacted-db-url]"
    assert redact_database_url_for_log("   ") == "[redacted-db-url]"


def test_redact_none_or_non_string():
    """None ou non-string : fallback sûr."""
    assert redact_database_url_for_log(None) == "[redacted-db-url]"
    assert redact_database_url_for_log(123) == "[redacted-db-url]"
