"""
Tests des endpoints admin IA et config :
  GET /api/admin/ai-stats
  GET /api/admin/generation-metrics
  PUT /api/admin/config (LOT 5.1)
"""

import pytest

from app.models.user import User

# ─── PUT /api/admin/config (LOT 5.1) ───────────────────────────────────────────


@pytest.mark.asyncio
async def test_admin_config_put_nominal(archiviste_client):
    """PUT /api/admin/config — archiviste peut mettre à jour les paramètres."""
    client = archiviste_client["client"]
    response = await client.put(
        "/api/admin/config",
        json={"settings": {"maintenance_mode": False, "registration_enabled": True}},
    )
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_admin_config_put_forbidden_padawan(padawan_client):
    """PUT /api/admin/config — padawan interdit (403)."""
    client = padawan_client["client"]
    response = await client.put(
        "/api/admin/config",
        json={"settings": {"maintenance_mode": False}},
    )
    assert response.status_code == 403


# ─── /api/admin/ai-stats ──────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_admin_ai_stats_archiviste(archiviste_client):
    """GET /api/admin/ai-stats — archiviste a accès, structure correcte."""
    client = archiviste_client["client"]
    response = await client.get("/api/admin/ai-stats")
    assert response.status_code == 200
    data = response.json()
    assert "stats" in data
    assert "daily_summary" in data
    assert "days" in data
    assert data["days"] == 1
    stats = data["stats"]
    assert "total_tokens" in stats
    assert "total_cost" in stats
    assert "count" in stats


@pytest.mark.asyncio
async def test_admin_ai_stats_days_param(archiviste_client):
    """GET /api/admin/ai-stats?days=7 — paramètre days respecté."""
    client = archiviste_client["client"]
    response = await client.get("/api/admin/ai-stats?days=7")
    assert response.status_code == 200
    assert response.json()["days"] == 7


@pytest.mark.asyncio
async def test_admin_ai_stats_challenge_type_param(archiviste_client):
    """GET /api/admin/ai-stats?challenge_type=sequence — filtre par type accepté."""
    client = archiviste_client["client"]
    response = await client.get("/api/admin/ai-stats?challenge_type=sequence")
    assert response.status_code == 200
    data = response.json()
    assert "stats" in data
    assert "days" in data
    # by_type absent ou vide quand un type spécifique est filtré (pas de données en mémoire en test)
    assert data["stats"].get("by_type", {}) == {}


@pytest.mark.asyncio
async def test_admin_ai_stats_invalid_days(archiviste_client):
    """GET /api/admin/ai-stats?days=0 — jours invalides → 400."""
    client = archiviste_client["client"]
    response = await client.get("/api/admin/ai-stats?days=0")
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_admin_ai_stats_forbidden_padawan(padawan_client):
    """GET /api/admin/ai-stats — padawan interdit (403)."""
    client = padawan_client["client"]
    response = await client.get("/api/admin/ai-stats")
    assert response.status_code == 403


# ─── /api/admin/generation-metrics ───────────────────────────────────────────


@pytest.mark.asyncio
async def test_admin_generation_metrics_archiviste(archiviste_client):
    """GET /api/admin/generation-metrics — archiviste a accès, structure correcte."""
    client = archiviste_client["client"]
    response = await client.get("/api/admin/generation-metrics")
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "days" in data
    assert data["days"] == 1
    summary = data["summary"]
    assert "success_rate" in summary
    assert "validation_failure_rate" in summary
    assert "auto_correction_rate" in summary
    assert "average_duration" in summary
    assert "by_type" in summary


@pytest.mark.asyncio
async def test_admin_generation_metrics_days_param(archiviste_client):
    """GET /api/admin/generation-metrics?days=30 — paramètre days respecté."""
    client = archiviste_client["client"]
    response = await client.get("/api/admin/generation-metrics?days=30")
    assert response.status_code == 200
    assert response.json()["days"] == 30


@pytest.mark.asyncio
async def test_admin_generation_metrics_invalid_days(archiviste_client, db_session):
    """GET /api/admin/generation-metrics?days=400 — jours hors limite → 400."""
    # LOT 4.3: diagnostic — si archiviste supprimé avant requête → 401
    arch_id = archiviste_client["user_id"]
    arch_user = db_session.query(User).filter(User.id == arch_id).first()
    assert (
        arch_user is not None
    ), f"Fixture user archiviste (id={arch_id}) absent en DB avant requête — cause probable 401"

    client = archiviste_client["client"]
    response = await client.get("/api/admin/generation-metrics?days=400")
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_admin_generation_metrics_forbidden_padawan(padawan_client):
    """GET /api/admin/generation-metrics — padawan interdit (403)."""
    client = padawan_client["client"]
    response = await client.get("/api/admin/generation-metrics")
    assert response.status_code == 403
