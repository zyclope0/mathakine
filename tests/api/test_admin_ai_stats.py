"""
Tests des endpoints admin IA :
  GET /api/admin/ai-stats
  GET /api/admin/generation-metrics
"""

import pytest


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
async def test_admin_generation_metrics_invalid_days(archiviste_client):
    """GET /api/admin/generation-metrics?days=400 — jours hors limite → 400."""
    client = archiviste_client["client"]
    response = await client.get("/api/admin/generation-metrics?days=400")
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_admin_generation_metrics_forbidden_padawan(padawan_client):
    """GET /api/admin/generation-metrics — padawan interdit (403)."""
    client = padawan_client["client"]
    response = await client.get("/api/admin/generation-metrics")
    assert response.status_code == 403
