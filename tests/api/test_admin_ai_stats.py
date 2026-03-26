"""
Tests des endpoints admin IA et config :
  GET /api/admin/ai-stats
  GET /api/admin/generation-metrics
  PUT /api/admin/config (LOT 5.1)
"""

import pytest

from app.models.user import User
from app.utils.generation_metrics import generation_metrics
from app.utils.token_tracker import token_tracker

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
    assert "by_workload" in stats
    assert "retention" in stats
    assert "cost_disclaimer_fr" in stats


@pytest.mark.asyncio
async def test_admin_ai_eval_harness_runs_archiviste(archiviste_client):
    """GET /api/admin/ai-eval-harness-runs — read-only, structure attendue."""
    client = archiviste_client["client"]
    response = await client.get("/api/admin/ai-eval-harness-runs?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "runs" in data
    assert "limit" in data
    assert "disclaimer_fr" in data
    assert isinstance(data["runs"], list)


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
async def test_admin_ai_stats_unknown_challenge_types_do_not_pollute_tracker(
    archiviste_client,
):
    """Lectures admin avec des clés libres ne doivent pas créer d'entrées en mémoire."""
    token_tracker._usage_history.clear()
    token_tracker._daily_totals.clear()
    before_keys = len(token_tracker._usage_history)
    client = archiviste_client["client"]
    for i in range(12):
        response = await client.get(
            f"/api/admin/ai-stats?challenge_type=admin_unknown_probe_{i}"
        )
        assert response.status_code == 200
    assert len(token_tracker._usage_history) == before_keys


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
    assert "by_workload" in summary
    assert "error_types" in summary
    assert "retention" in summary
    assert "metrics_disclaimer_fr" in summary


@pytest.mark.asyncio
async def test_admin_ai_metrics_expose_multi_workload_breakdown(archiviste_client):
    """Les endpoints admin exposent la ventilation chat / exercices / défis."""
    token_tracker._usage_history.clear()
    token_tracker._daily_totals.clear()
    generation_metrics._generation_history.clear()
    generation_metrics._validation_failures.clear()
    generation_metrics._auto_corrections.clear()
    generation_metrics._success_count.clear()
    generation_metrics._failure_count.clear()

    token_tracker.track_usage("assistant_chat:simple", 120, 60, model="gpt-5-mini")
    token_tracker.track_usage("exercise_ai:addition", 100, 50, model="o3")
    token_tracker.track_usage("sequence", 200, 100, model="o3")
    generation_metrics.record_generation(
        "assistant_chat:simple",
        success=False,
        validation_passed=False,
        duration_seconds=1.2,
        error_type="RateLimitError",
    )
    generation_metrics.record_generation(
        "exercise_ai:addition",
        success=True,
        validation_passed=True,
        duration_seconds=2.0,
    )
    generation_metrics.record_generation(
        "sequence",
        success=True,
        validation_passed=True,
        auto_corrected=True,
        duration_seconds=3.0,
    )

    client = archiviste_client["client"]
    stats_response = await client.get("/api/admin/ai-stats")
    metrics_response = await client.get("/api/admin/generation-metrics")

    assert stats_response.status_code == 200
    assert metrics_response.status_code == 200

    stats = stats_response.json()["stats"]
    summary = metrics_response.json()["summary"]

    assert "assistant_chat" in stats["by_workload"]
    assert "exercises_ai" in stats["by_workload"]
    assert "challenges_ai" in stats["by_workload"]
    assert "assistant_chat" in summary["by_workload"]
    assert "exercises_ai" in summary["by_workload"]
    assert "challenges_ai" in summary["by_workload"]
    assert summary["error_types"]["RateLimitError"] >= 1

    token_tracker._usage_history.clear()
    token_tracker._daily_totals.clear()
    generation_metrics._generation_history.clear()


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
