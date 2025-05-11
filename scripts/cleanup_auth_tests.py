#!/usr/bin/env python
"""
[TEST_AUTH_JWT] Script de nettoyage pour les tests d'authentification JWT.
Ce script supprime tous les utilisateurs créés pendant les tests d'authentification.
Les utilisateurs à supprimer sont identifiés par leur nom commençant par "test_jedi_auth".
"""
import os
import sys

# Ajouter le répertoire parent au chemin Python pour pouvoir importer l'application
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import or_
from app.db.base import get_db
from app.models.user import User


def cleanup_auth_test_users():
    """
    Supprime tous les utilisateurs créés pendant les tests d'authentification.
    """
    print("[TEST_AUTH_JWT] Début du nettoyage des utilisateurs de test d'authentification...")
    
    db = next(get_db())
    
    # Recherche des utilisateurs dont le nom commence par "test_jedi_auth"
    test_users = db.query(User).filter(
        or_(
            User.username.like("test_jedi_auth%"),
            User.email.like("%@mathakine.com")
        )
    ).all()
    
    if not test_users:
        print("[TEST_AUTH_JWT] Aucun utilisateur de test d'authentification trouvé.")
        return
    
    # Afficher les utilisateurs trouvés
    print(f"[TEST_AUTH_JWT] {len(test_users)} utilisateurs de test trouvés :")
    for user in test_users:
        print(f"  - {user.username} ({user.email})")
    
    # Demander confirmation avant suppression
    confirm = input("[TEST_AUTH_JWT] Voulez-vous supprimer ces utilisateurs ? (o/n) : ")
    if confirm.lower() != 'o':
        print("[TEST_AUTH_JWT] Opération annulée.")
        return
    
    # Supprimer les utilisateurs
    for user in test_users:
        db.delete(user)
    
    db.commit()
    print(f"[TEST_AUTH_JWT] {len(test_users)} utilisateurs de test ont été supprimés avec succès.")


if __name__ == "__main__":
    cleanup_auth_test_users() 