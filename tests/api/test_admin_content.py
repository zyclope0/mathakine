"""
Tests des endpoints API admin content (LOT 6).
Exercises, challenges, export — preuve minimale pour les mutations.
"""

import uuid

import pytest

from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.utils.db_helpers import get_enum_value

# ── F42 boundary: exercises ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_admin_exercise_post_sets_difficulty_tier(archiviste_client):
    """POST /api/admin/exercises — difficulty_tier calculé et renvoyé (F42)."""
    client = archiviste_client["client"]
    payload = {
        "title": "Exercice F42 tier test",
        "question": "Combien font 4+5?",
        "correct_answer": "9",
        "exercise_type": "addition",
        "difficulty": "INITIE",
        "age_group": "6-8",
    }
    resp = await client.post("/api/admin/exercises", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    # age_group=6-8 + difficulty=INITIE → tier 1 (age_band=0 × ped_band=0 + 1)
    assert data.get("difficulty_tier") == 1


@pytest.mark.asyncio
async def test_admin_exercise_put_updates_difficulty_tier(archiviste_client):
    """PUT /api/admin/exercises/{id} — difficulty_tier recalculé quand difficulty/age_group changent."""
    client = archiviste_client["client"]
    create_resp = await client.post(
        "/api/admin/exercises",
        json={
            "title": "Exercice F42 PUT tier",
            "question": "1+1?",
            "correct_answer": "2",
            "exercise_type": "addition",
            "difficulty": "INITIE",
            "age_group": "6-8",
        },
    )
    assert create_resp.status_code == 201
    ex_id = create_resp.json()["id"]
    assert create_resp.json()["difficulty_tier"] == 1

    put_resp = await client.put(
        f"/api/admin/exercises/{ex_id}",
        json={"difficulty": "CHEVALIER", "age_group": "12-14"},
    )
    assert put_resp.status_code == 200
    data = put_resp.json()
    # age_group=12-14 + difficulty=CHEVALIER → tier 9 (age_band=2 × 3 + ped_band=2 + 1)
    assert data.get("difficulty_tier") == 9


@pytest.mark.asyncio
async def test_admin_exercise_list_includes_difficulty_tier(archiviste_client):
    """GET /api/admin/exercises — list items exposent difficulty_tier (F42)."""
    client = archiviste_client["client"]
    await client.post(
        "/api/admin/exercises",
        json={
            "title": "Exercice F42 list tier",
            "question": "2+2?",
            "correct_answer": "4",
            "exercise_type": "addition",
            "difficulty": "PADAWAN",
            "age_group": "9-11",
        },
    )
    resp = await client.get("/api/admin/exercises")
    assert resp.status_code == 200
    items = resp.json().get("items", [])
    assert len(items) > 0
    # Every item must carry difficulty_tier key (may be None for legacy data)
    for item in items:
        assert "difficulty_tier" in item


@pytest.mark.asyncio
async def test_admin_challenge_list_includes_difficulty_tier_and_rating(
    archiviste_client,
):
    """GET /api/admin/challenges — list items exposent difficulty_tier et difficulty_rating (F42)."""
    client = archiviste_client["client"]
    await client.post(
        "/api/admin/challenges",
        json={
            "title": "Défi F42 list tier",
            "description": "Test list tier.",
            "age_group": "GROUP_10_12",
            "difficulty_rating": 3.0,
        },
    )
    resp = await client.get("/api/admin/challenges")
    assert resp.status_code == 200
    items = resp.json().get("items", [])
    assert len(items) > 0
    for item in items:
        assert "difficulty_tier" in item
        assert "difficulty_rating" in item


@pytest.mark.asyncio
async def test_admin_exercises_post_nominal(archiviste_client):
    """POST /api/admin/exercises — création d'un exercice."""
    client = archiviste_client["client"]
    payload = {
        "title": "Exercice admin LOT6",
        "question": "Combien font 3+2?",
        "correct_answer": "5",
        "exercise_type": "addition",
        "difficulty": "initie",
        "age_group": "6-8",
    }
    response = await client.post("/api/admin/exercises", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data.get("title") == payload["title"]
    assert data.get("question") == payload["question"]
    assert data.get("correct_answer") == payload["correct_answer"]
    assert "id" in data


@pytest.mark.asyncio
async def test_admin_exercises_duplicate_nominal(archiviste_client):
    """POST /api/admin/exercises/{exercise_id}/duplicate — crée une copie."""
    client = archiviste_client["client"]
    # Créer un exercice source
    create_payload = {
        "title": "Exercice à dupliquer LOT6.1",
        "question": "Combien font 3+2?",
        "correct_answer": "5",
        "exercise_type": "addition",
        "difficulty": "initie",
        "age_group": "6-8",
    }
    create_resp = await client.post("/api/admin/exercises", json=create_payload)
    assert create_resp.status_code == 201
    exercise_id = create_resp.json()["id"]

    # Dupliquer
    dup_resp = await client.post(f"/api/admin/exercises/{exercise_id}/duplicate")
    assert dup_resp.status_code == 201
    data = dup_resp.json()
    assert data.get("id") != exercise_id
    assert "(copie)" in (data.get("title") or "")
    assert data.get("question") == create_payload["question"]
    assert data.get("correct_answer") == create_payload["correct_answer"]


@pytest.mark.asyncio
async def test_admin_exercises_put_nominal(archiviste_client):
    """PUT /api/admin/exercises/{exercise_id} — mise à jour complète."""
    client = archiviste_client["client"]
    # Créer un exercice
    create_payload = {
        "title": "Exercice à modifier LOT6.1",
        "question": "Question initiale",
        "correct_answer": "42",
        "exercise_type": "addition",
        "difficulty": "initie",
        "age_group": "6-8",
    }
    create_resp = await client.post("/api/admin/exercises", json=create_payload)
    assert create_resp.status_code == 201
    exercise_id = create_resp.json()["id"]

    # Mettre à jour
    put_payload = {"title": "Titre modifié", "question": "Question modifiée"}
    put_resp = await client.put(f"/api/admin/exercises/{exercise_id}", json=put_payload)
    assert put_resp.status_code == 200
    data = put_resp.json()
    assert data.get("id") == exercise_id
    assert data.get("title") == put_payload["title"]
    assert data.get("question") == put_payload["question"]


@pytest.mark.asyncio
async def test_admin_exercises_patch_nominal(archiviste_client):
    """PATCH /api/admin/exercises/{exercise_id} — toggle is_archived."""
    client = archiviste_client["client"]
    # Créer un exercice
    create_payload = {
        "title": "Exercice à archiver LOT6.1",
        "question": "Combien font 1+1?",
        "correct_answer": "2",
        "exercise_type": "addition",
        "difficulty": "initie",
        "age_group": "6-8",
    }
    create_resp = await client.post("/api/admin/exercises", json=create_payload)
    assert create_resp.status_code == 201
    exercise_id = create_resp.json()["id"]

    # Archiver
    patch_resp = await client.patch(
        f"/api/admin/exercises/{exercise_id}", json={"is_archived": True}
    )
    assert patch_resp.status_code == 200
    data = patch_resp.json()
    assert data.get("id") == exercise_id
    assert data.get("is_archived") is True


@pytest.mark.asyncio
async def test_admin_challenges_post_nominal(archiviste_client):
    """POST /api/admin/challenges — création d'un défi."""
    client = archiviste_client["client"]
    payload = {
        "title": "Défi admin LOT6",
        "description": "Description du défi de test admin.",
    }
    response = await client.post("/api/admin/challenges", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data.get("title") == payload["title"]
    assert data.get("description") == payload["description"]
    assert "id" in data


@pytest.mark.asyncio
async def test_admin_challenges_post_difficulty_rating_sets_tier(archiviste_client):
    """POST /api/admin/challenges — difficulty_rating explicite → tier F42 cohérent."""
    client = archiviste_client["client"]
    payload = {
        "title": "Défi admin F42 difficulty_rating",
        "description": "Description avec difficulté explicite.",
        "age_group": "GROUP_10_12",
        "difficulty_rating": 4.0,
    }
    response = await client.post("/api/admin/challenges", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["difficulty_rating"] == 4.0
    assert data["difficulty_tier"] == 6


@pytest.mark.asyncio
async def test_admin_challenge_get_nominal(archiviste_client):
    """GET /api/admin/challenges/{challenge_id} — détail pour édition (B2 boundary)."""
    client = archiviste_client["client"]
    create_payload = {
        "title": "Défi pour GET LOT6",
        "description": "Description du défi pour test GET.",
    }
    create_resp = await client.post("/api/admin/challenges", json=create_payload)
    assert create_resp.status_code == 201
    challenge_id = create_resp.json()["id"]

    get_resp = await client.get(f"/api/admin/challenges/{challenge_id}")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data.get("id") == challenge_id
    assert data.get("title") == create_payload["title"]
    assert data.get("description") == create_payload["description"]


@pytest.mark.asyncio
async def test_admin_challenge_get_404(archiviste_client):
    """GET /api/admin/challenges/{challenge_id} — 404 si non trouvé."""
    client = archiviste_client["client"]
    response = await client.get("/api/admin/challenges/999999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_admin_challenges_duplicate_nominal(archiviste_client):
    """POST /api/admin/challenges/{challenge_id}/duplicate — crée une copie."""
    client = archiviste_client["client"]
    create_payload = {
        "title": "Défi à dupliquer LOT6.2",
        "description": "Description du défi à dupliquer.",
    }
    create_resp = await client.post("/api/admin/challenges", json=create_payload)
    assert create_resp.status_code == 201
    challenge_id = create_resp.json()["id"]

    dup_resp = await client.post(f"/api/admin/challenges/{challenge_id}/duplicate")
    assert dup_resp.status_code == 201
    data = dup_resp.json()
    assert data.get("id") != challenge_id
    assert "(copie)" in (data.get("title") or "")
    assert data.get("description") == create_payload["description"]


@pytest.mark.asyncio
async def test_admin_challenges_put_nominal(archiviste_client):
    """PUT /api/admin/challenges/{challenge_id} — mise à jour complète."""
    client = archiviste_client["client"]
    create_payload = {
        "title": "Défi à modifier LOT6.2",
        "description": "Description initiale.",
    }
    create_resp = await client.post("/api/admin/challenges", json=create_payload)
    assert create_resp.status_code == 201
    challenge_id = create_resp.json()["id"]

    put_payload = {
        "title": "Titre modifié LOT6.2",
        "description": "Description modifiée.",
    }
    put_resp = await client.put(
        f"/api/admin/challenges/{challenge_id}", json=put_payload
    )
    assert put_resp.status_code == 200
    data = put_resp.json()
    assert data.get("id") == challenge_id
    assert data.get("title") == put_payload["title"]
    assert data.get("description") == put_payload["description"]


@pytest.mark.asyncio
async def test_admin_challenges_put_updates_difficulty_rating_and_tier(
    archiviste_client,
):
    """PUT /api/admin/challenges/{id} — difficulty_rating appliqué → tier F42 cohérent."""
    client = archiviste_client["client"]
    create_resp = await client.post(
        "/api/admin/challenges",
        json={
            "title": "Défi PUT difficulty_rating micro-lot",
            "description": "Init.",
            "age_group": "GROUP_10_12",
            "difficulty_rating": 2.0,
        },
    )
    assert create_resp.status_code == 201
    challenge_id = create_resp.json()["id"]

    put_resp = await client.put(
        f"/api/admin/challenges/{challenge_id}",
        json={
            "title": "Défi PUT difficulty_rating micro-lot",
            "description": "Init.",
            "age_group": "GROUP_10_12",
            "difficulty_rating": 5.0,
        },
    )
    assert put_resp.status_code == 200
    data = put_resp.json()
    assert data["difficulty_rating"] == 5.0
    assert data["difficulty_tier"] == 6


@pytest.mark.asyncio
async def test_admin_challenges_patch_nominal(archiviste_client):
    """PATCH /api/admin/challenges/{challenge_id} — toggle is_archived."""
    client = archiviste_client["client"]
    create_payload = {
        "title": "Défi à archiver LOT6.2",
        "description": "Description pour archivage.",
    }
    create_resp = await client.post("/api/admin/challenges", json=create_payload)
    assert create_resp.status_code == 201
    challenge_id = create_resp.json()["id"]

    patch_resp = await client.patch(
        f"/api/admin/challenges/{challenge_id}",
        json={"is_archived": True},
    )
    assert patch_resp.status_code == 200
    data = patch_resp.json()
    assert data.get("id") == challenge_id
    assert data.get("is_archived") is True


@pytest.mark.asyncio
async def test_admin_export_overview(archiviste_client):
    """GET /api/admin/export?type=overview — export CSV overview."""
    client = archiviste_client["client"]
    response = await client.get("/api/admin/export?type=overview&period=all")
    assert response.status_code == 200
    assert "text/csv" in response.headers.get("content-type", "")
    content = response.text
    assert "metric" in content or "value" in content or "total" in content.lower()


@pytest.mark.asyncio
async def test_admin_f43_account_progression_observability(
    archiviste_client, db_session
):
    """GET /api/admin/observability/f43-account-progression — F43-A1 read-only."""
    client = archiviste_client["client"]
    baseline = await client.get("/api/admin/observability/f43-account-progression")
    assert baseline.status_code == 200
    baseline_data = baseline.json()

    unique = uuid.uuid4().hex[:8]
    adapted_role = get_enum_value(UserRole, UserRole.PADAWAN.value, db_session)
    user = User(
        username=f"f43_api_{unique}",
        email=f"f43_api_{unique}@test.com",
        hashed_password=get_password_hash("secret"),
        role=adapted_role,
        is_active=True,
        total_points=1000,
        current_level=99,
        jedi_rank="grand_master",
    )
    db_session.add(user)
    db_session.commit()

    resp = await client.get("/api/admin/observability/f43-account-progression")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("schema") == "f43_account_progression_v1"
    assert (
        data.get("total_active_users") == baseline_data.get("total_active_users", 0) + 1
    )
    assert isinstance(data.get("by_current_level"), dict)
    assert isinstance(data.get("by_jedi_rank"), dict)
    assert (
        data["by_current_level"].get("6", 0)
        == baseline_data["by_current_level"].get("6", 0) + 1
    )
    assert (
        data["by_jedi_rank"].get("explorer", 0)
        == baseline_data["by_jedi_rank"].get("explorer", 0) + 1
    )
