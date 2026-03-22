"""
Contrat POST + JSON pour la génération IA en streaming (IA6).
"""

from unittest.mock import patch

import pytest


@pytest.mark.asyncio
async def test_generate_ai_exercise_stream_post_rejects_unknown_field(padawan_client):
    """Champ inconnu → 422 JSON (extra=forbid)."""
    client = padawan_client["client"]
    resp = await client.post(
        "/api/exercises/generate-ai-stream",
        json={
            "exercise_type": "addition",
            "age_group": "6-8",
            "prompt": "",
            "unexpected": True,
        },
    )
    assert resp.status_code == 422
    data = resp.json()
    assert "error" in data or "detail" in data


@pytest.mark.asyncio
async def test_generate_ai_exercise_stream_post_accepts_minimal_body(padawan_client):
    """Corps minimal + mock stream → 200 event-stream."""
    client = padawan_client["client"]

    async def fake_stream(*args, **kwargs):
        yield 'data: {"type":"status","message":"ok"}\n\n'

    with patch(
        "app.services.exercises.exercise_ai_service.generate_exercise_stream",
        new=fake_stream,
    ):
        resp = await client.post(
            "/api/exercises/generate-ai-stream",
            json={"exercise_type": "addition", "age_group": "6-8", "prompt": ""},
        )
    assert resp.status_code == 200
    assert "text/event-stream" in resp.headers.get("content-type", "")


@pytest.mark.asyncio
async def test_generate_ai_challenge_stream_post_rejects_unknown_field(padawan_client):
    client = padawan_client["client"]
    resp = await client.post(
        "/api/challenges/generate-ai-stream",
        json={
            "challenge_type": "sequence",
            "age_group": "9-11",
            "prompt": "",
            "nope": 1,
        },
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_generate_ai_challenge_stream_post_accepts_minimal_body(padawan_client):
    client = padawan_client["client"]

    async def fake_stream(*args, **kwargs):
        yield 'data: {"type":"status","message":"x"}\n\n'

    with patch(
        "app.services.challenges.challenge_ai_service.generate_challenge_stream",
        new=fake_stream,
    ):
        resp = await client.post(
            "/api/challenges/generate-ai-stream",
            json={"challenge_type": "sequence", "age_group": "9-11", "prompt": ""},
        )
    assert resp.status_code == 200
    assert "text/event-stream" in resp.headers.get("content-type", "")


@pytest.mark.asyncio
async def test_generate_ai_exercise_stream_get_no_longer_supported(padawan_client):
    client = padawan_client["client"]
    resp = await client.get(
        "/api/exercises/generate-ai-stream",
        params={"exercise_type": "addition", "age_group": "6-8"},
    )
    assert resp.status_code == 405


@pytest.mark.asyncio
async def test_generate_ai_challenge_stream_get_no_longer_supported(padawan_client):
    client = padawan_client["client"]
    resp = await client.get(
        "/api/challenges/generate-ai-stream",
        params={"challenge_type": "sequence", "age_group": "9-11"},
    )
    assert resp.status_code == 405
