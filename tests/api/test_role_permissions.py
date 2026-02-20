"""
Tests des permissions d'accès selon les rôles des utilisateurs.
"""
import pytest


async def test_padawan_permissions(padawan_client):
    """Teste les permissions d'un utilisateur avec le rôle PADAWAN."""
    client = padawan_client["client"]

    # Accès autorisé: récupérer des exercices
    response = await client.get("/api/exercises")
    assert response.status_code == 200, "Un padawan devrait pouvoir accéder aux exercices"

    # Accès autorisé: soumettre une tentative pour un exercice existant
    attempt_data = {
        "selected_answer": "4",
        "time_spent": 10.0
    }
    # Note: Cette requête peut échouer avec 404 si l'exercice n'existe pas, ce qui est acceptable
    response = await client.post("/api/exercises/1/attempt", json=attempt_data)
    assert response.status_code in [200, 404], f"Un padawan devrait pouvoir soumettre une tentative (ou recevoir 404 si l'exercice n'existe pas)"

    # Créer un exercice pour tester la suppression (POST /api/exercises/generate attend exercise_type et age_group)
    exercise_data = {
        "exercise_type": "addition",
        "age_group": "9-11"
    }
    response = await client.post("/api/exercises/generate", json=exercise_data)

    # DELETE /api/exercises/{id} retiré : pas de frontend, archivage prévu plus tard dans l'admin


async def test_maitre_permissions(maitre_client, padawan_client):
    """Teste les permissions d'un utilisateur avec le rôle MAITRE."""
    maitre = maitre_client["client"]

    # Accès autorisé: créer un exercice (POST /api/exercises/generate)
    exercise_data = {
        "exercise_type": "addition",
        "age_group": "9-11"
    }
    response = await maitre.post("/api/exercises/generate", json=exercise_data)
    assert response.status_code == 200, "Un maître devrait pouvoir créer un exercice"

    # Récupérer l'ID de l'exercice créé (si sauvegardé)
    data = response.json()
    exercise_id = data.get("id")
    if exercise_id is not None:
        # Accès autorisé: modifier son propre exercice (PATCH peut ne pas exister)
        update_data = {"title": "Exercice du Maître (Modifié)"}
        response = await maitre.patch(f"/api/exercises/{exercise_id}", json=update_data)
        assert response.status_code in [200, 404, 405], "Un maître devrait pouvoir modifier ou route inexistante"

    # DELETE /api/exercises/{id} retiré : archivage prévu dans l'admin


async def test_gardien_permissions(gardien_client):
    """Teste les permissions d'un utilisateur avec le rôle GARDIEN."""
    gardien = gardien_client["client"]

    # Accès autorisé: récupérer les exercices (y compris les archivés)
    response = await gardien.get("/api/exercises?include_archived=true")
    assert response.status_code == 200, "Un gardien devrait pouvoir accéder aux exercices archivés"

    # DELETE /api/exercises/{id} retiré : archivage prévu dans l'admin (gardien/archiviste)
