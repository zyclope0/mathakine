"""
Dépendances communes pour les API
"""
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.base import get_db
from typing import Generator




def get_db_session() -> Generator[Session, None, None]:
    """
    Dépendance pour obtenir une session de base de données.
    """
    db = get_db()
    try:
        yield from db
    finally:
        pass  # La fermeture est gérée dans get_db
