"""
Tests de l'endpoint admin GET /api/admin/analytics/edtech.
"""

import pytest

from app.models.edtech_event import EdTechEvent
from app.models.user import User


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
async def test_analytics_event_post_and_visible(
    padawan_client, archiviste_client, db_session
):
    """POST /api/analytics/event enregistre l'événement, visible dans admin."""
    # LOT 4.3: diagnostic — si fixture user supprimé avant requête → 401
    for role, client_fixture in [
        ("padawan", padawan_client),
        ("archiviste", archiviste_client),
    ]:
        uid = client_fixture["user_id"]
        u = db_session.query(User).filter(User.id == uid).first()
        assert (
            u is not None
        ), f"Fixture user {role} (id={uid}) absent en DB avant requête — cause probable 401"

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


@pytest.mark.asyncio
async def test_admin_analytics_edtech_excludes_negative_times(
    archiviste_client, db_session, padawan_client
):
    """Les temps négatifs (timeToFirstAttemptMs) sont exclus des agrégats."""
    from datetime import datetime, timedelta, timezone

    # LOT 4.3: diagnostic — si archiviste supprimé avant requête → 401
    arch_id = archiviste_client["user_id"]
    arch_user = db_session.query(User).filter(User.id == arch_id).first()
    assert (
        arch_user is not None
    ), f"Fixture user archiviste (id={arch_id}) absent en DB avant requête — cause probable 401"

    user_id = padawan_client["user_id"]
    since = datetime.now(timezone.utc) - timedelta(days=1)

    # Insérer des first_attempt avec temps négatif (données de test aberrantes)
    db_session.add(
        EdTechEvent(
            user_id=user_id,
            event="first_attempt",
            payload={"type": "exercise", "targetId": 1, "timeToFirstAttemptMs": -25000},
        )
    )
    db_session.add(
        EdTechEvent(
            user_id=user_id,
            event="first_attempt",
            payload={"type": "exercise", "targetId": 2, "timeToFirstAttemptMs": 5000},
        )
    )
    db_session.commit()

    client = archiviste_client["client"]
    response = await client.get("/api/admin/analytics/edtech?period=30d")
    assert response.status_code == 200
    data = response.json()
    fa = data.get("aggregates", {}).get("first_attempt", {})
    # Seul le temps positif (5000 ms) doit être inclus → moyenne = 5000
    assert fa.get("avg_time_to_first_attempt_ms") == 5000
