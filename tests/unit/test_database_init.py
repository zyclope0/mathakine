"""
Tests pour server.database (init_database, get_database_url).

Règle projet : tests systématiques — nouvelle implémentation → test de non-régression.
Refactor 22/02/2026 : config unifiée + init basculé sur SQLAlchemy.
"""

import pytest

from app.core.config import settings
from server.database import get_database_url, init_database


def test_get_database_url_unified_with_settings():
    """
    get_database_url() doit retourner settings.SQLALCHEMY_DATABASE_URL.
    Garantit que init_database et l'app utilisent la même URL (respect TESTING, TEST_DATABASE_URL).
    """
    url = get_database_url()
    assert url
    assert url == settings.SQLALCHEMY_DATABASE_URL


def test_init_database_completes_successfully():
    """
    init_database() doit s'exécuter sans erreur.
    Depuis 22/02/2026 : no-op (DDL géré par Alembic au build).
    """
    init_database()
    # Pas d'assert explicite : le test passe si aucune exception n'est levée
