"""
Test de stabilité admin/auth (LOT 4.5).

Exécute la batterie admin + auth 3 fois de suite pour garantir
l'absence de flakiness liée à la collision fixtures/cleanup.

IMPORTANT - AUTH_SESSION_DB_VISIBILITY_STABILIZATION:
Ce test NE DOIT PAS être utilisé comme gate de validation.
Il lance pytest en subprocess depuis un pytest déjà couvert, ce qui crée:
- contention sur .coverage (INTERNALERROR)
- résultats non fiables comme preuve
Pour la validation, utiliser la batterie cible SANS ce fichier.
"""

import subprocess
import sys

import pytest


@pytest.mark.slow
def test_admin_auth_suite_stable_3_runs():
    """Batterie admin+auth doit passer 3 fois consécutives sans échec."""
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "--tb=no",
        "--no-header",
        "-x",
        "tests/api/test_admin_ai_stats.py",
        "tests/api/test_admin_analytics.py",
        "tests/api/test_admin_badges.py",
        "tests/api/test_admin_users_delete.py",
        "tests/api/test_feedback_endpoints.py",
        "tests/api/test_auth_flow.py",
    ]
    for run in range(1, 4):
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        assert (
            result.returncode == 0
        ), f"Run {run}/3 échoué:\n{result.stdout}\n{result.stderr}"
