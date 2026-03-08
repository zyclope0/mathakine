"""
Tests pour DELETE /api/admin/users/{user_id}.
Suppression définitive d'un utilisateur par un admin (cascade en base).
"""

from app.models.user import User
from tests.utils.test_helpers import adapted_dict_to_user


async def test_admin_delete_user_archiviste(archiviste_client, db_session, mock_user):
    """DELETE /api/admin/users/{id} — archiviste peut supprimer un autre utilisateur."""
    client = archiviste_client["client"]
    admin_id = archiviste_client["user_id"]

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

    user_data = mock_user()
    user = adapted_dict_to_user(user_data, db_session)
    db_session.add(user)
    db_session.commit()
    user_id = user.id

    response = await client.delete(f"/api/admin/users/{user_id}")
    assert response.status_code == 403
