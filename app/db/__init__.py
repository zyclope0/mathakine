"""
Module de base de données pour Mathakine.
Ce module contient les composants de base pour la gestion des transactions et l'accès à la base de données.
"""

from app.db.base import Base, get_db, SessionLocal, engine
from app.db.transaction import TransactionManager
from app.db.adapter import DatabaseAdapter

__all__ = [
    "Base",
    "get_db",
    "SessionLocal",
    "engine",
    "TransactionManager",
    "DatabaseAdapter",
]
