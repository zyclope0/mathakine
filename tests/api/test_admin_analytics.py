"""
Tests de l'endpoint admin GET /api/admin/analytics/edtech.
"""

import pytest


@pytest.mark.asyncio
async def test_admin_analytics_edtech_archiviste(archiviste_client):
    """GET /api/admin/analytics/edtech — archiviste a accès."""
    client = archiviste_client["client"]
    response = await client.get("/api/admin/analytics/edtech")
    assert response.status_code == 200
    data = response.json()
    assert "period" in data
    assert "since" in data
    assert "aggregates" in data
    assert "events" in data
    assert isinstance(data["events"], list)


@pytest.mark.asyncio
async def test_admin_analytics_edtech_period_param(archiviste_client):
    """GET /api/admin/analytics/edtech?period=30d — filtre période."""
    client = archiviste_client["client"]
    response = await client.get("/api/admin/analytics/edtech?period=30d")
    assert response.status_code == 200
    data = response.json()
    assert data.get("period") == "30d"


@pytest.mark.asyncio
async def test_admin_analytics_forbidden_padawan(padawan_client):
    """GET /api/admin/analytics/edtech — padawan interdit."""
    client = padawan_client["client"]
    response = await client.get("/api/admin/analytics/edtech")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_analytics_event_post_and_visible(padawan_client, archiviste_client):
    """POST /api/analytics/event enregistre l'événement, visible dans admin."""
    # Padawan envoie un événement
    client = padawan_client["client"]
    payload = {
        "event": "quick_start_click",
        "payload": {"type": "challenge", "guided": True, "targetId": 42},
    }
    response = await client.post("/api/analytics/event", json=payload)
    assert response.status_code == 200
    assert response.json().get("ok") is True

    # Archiviste vérifie que l'événement apparaît
    admin_client = archiviste_client["client"]
    admin_response = await admin_client.get("/api/admin/analytics/edtech")
    assert admin_response.status_code == 200
    data = admin_response.json()
    events = data.get("events", [])
    matching = [e for e in events if e.get("event") == "quick_start_click"]
    assert len(matching) >= 1
    assert any(
        (m.get("payload") or {}).get("type") == "challenge"
        and (m.get("payload") or {}).get("targetId") == 42
        for m in matching
    )
