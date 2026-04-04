"""
Tests pour les mutations admin users (LOT 5 / 5.1) :
  DELETE /api/admin/users/{user_id}
  PATCH /api/admin/users/{user_id}
  POST /api/admin/users/{user_id}/send-reset-password
  POST /api/admin/users/{user_id}/resend-verification
"""

from app.models.user import User
from tests.utils.test_helpers import adapted_dict_to_user

# ─── PATCH /api/admin/users/{user_id} (LOT 5.1) ────────────────────────────────


async def test_admin_users_patch_nominal(archiviste_client, db_session, mock_user):
    """PATCH /api/admin/users/{id} — archiviste peut modifier is_active et role."""
    client = archiviste_client["client"]
    admin_id = archiviste_client["user_id"]

    user_data = mock_user()
    user = adapted_dict_to_user(user_data, db_session)
    db_session.add(user)
    db_session.commit()
    user_id = user.id

    assert user_id != admin_id

    response = await client.patch(
        f"/api/admin/users/{user_id}",
        json={"is_active": False, "role": "maitre"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["username"] == user.username
    assert data["is_active"] is False
    assert data["role"] == "enseignant"


# ─── POST send-reset-password (LOT 5.1) ──────────────────────────────────────


async def test_admin_users_send_reset_password_nominal(
    archiviste_client, db_session, mock_user
):
    """POST /api/admin/users/{id}/send-reset-password — cas nominal."""
    client = archiviste_client["client"]
    admin_id = archiviste_client["user_id"]

    user_data = mock_user()
    user = adapted_dict_to_user(user_data, db_session)
    user.is_active = True
    db_session.add(user)
    db_session.commit()
    user_id = user.id

    assert user_id != admin_id

    response = await client.post(f"/api/admin/users/{user_id}/send-reset-password")
    assert response.status_code == 200
    assert "réinitialisation" in response.json().get("message", "").lower()


# ─── POST resend-verification (LOT 5.1) ────────────────────────────────────────


async def test_admin_users_resend_verification_nominal(
    archiviste_client, db_session, mock_user
):
    """POST /api/admin/users/{id}/resend-verification — utilisateur non vérifié."""
    client = archiviste_client["client"]
    admin_id = archiviste_client["user_id"]

    user_data = mock_user()
    user = adapted_dict_to_user(user_data, db_session)
    user.is_email_verified = False
    db_session.add(user)
    db_session.commit()
    user_id = user.id

    assert user_id != admin_id

    response = await client.post(f"/api/admin/users/{user_id}/resend-verification")
    assert response.status_code == 200
    assert "vérification" in response.json().get("message", "").lower()


async def test_admin_users_resend_verification_already_verified(
    archiviste_client, db_session, mock_user
):
    """POST /api/admin/users/{id}/resend-verification — déjà vérifié."""
    client = archiviste_client["client"]
    admin_id = archiviste_client["user_id"]

    user_data = mock_user()
    user = adapted_dict_to_user(user_data, db_session)
    user.is_email_verified = True
    db_session.add(user)
    db_session.commit()
    user_id = user.id

    assert user_id != admin_id

    response = await client.post(f"/api/admin/users/{user_id}/resend-verification")
    assert response.status_code == 200
    assert "déjà vérifié" in response.json().get("message", "").lower()


# ─── DELETE /api/admin/users/{user_id} ───────────────────────────────────────


async def test_admin_delete_user_archiviste(archiviste_client, db_session, mock_user):
    """DELETE /api/admin/users/{id} — archiviste peut supprimer un autre utilisateur."""
    client = archiviste_client["client"]
    admin_id = archiviste_client["user_id"]

    # LOT 4.3: diagnostic — si archiviste supprimé avant requête → 401
    admin_user = db_session.query(User).filter(User.id == admin_id).first()
    assert (
        admin_user is not None
    ), f"Fixture user archiviste (id={admin_id}) absent en DB avant requête — cause probable 401"

    # Créer un utilisateur à supprimer
    user_data = mock_user()
    user = adapted_dict_to_user(user_data, db_session)
    db_session.add(user)
    db_session.commit()
    user_id = user.id

    assert user_id != admin_id

    response = await client.delete(f"/api/admin/users/{user_id}")
    assert response.status_code == 200
    assert "supprimé" in response.json().get("message", "").lower()

    # Vérifier que l'utilisateur n'existe plus
    deleted = db_session.query(User).filter(User.id == user_id).first()
    assert deleted is None


async def test_admin_delete_user_self_forbidden(archiviste_client):
    """DELETE /api/admin/users/{id} — un admin ne peut pas se supprimer lui-même."""
    client = archiviste_client["client"]
    admin_id = archiviste_client["user_id"]

    response = await client.delete(f"/api/admin/users/{admin_id}")
    assert response.status_code == 400
    assert "propre compte" in response.json().get("error", "").lower()


async def test_admin_delete_user_forbidden_padawan(
    padawan_client, db_session, mock_user
):
    """DELETE /api/admin/users/{id} — padawan interdit (403)."""
    client = padawan_client["client"]

    # LOT 4.3: diagnostic — si padawan supprimé avant requête → 401
    padawan_id = padawan_client["user_id"]
    padawan_user = db_session.query(User).filter(User.id == padawan_id).first()
    assert (
        padawan_user is not None
    ), f"Fixture user padawan (id={padawan_id}) absent en DB avant requête — cause probable 401"

    user_data = mock_user()
    user = adapted_dict_to_user(user_data, db_session)
    db_session.add(user)
    db_session.commit()
    user_id = user.id

    response = await client.delete(f"/api/admin/users/{user_id}")
    assert response.status_code == 403
