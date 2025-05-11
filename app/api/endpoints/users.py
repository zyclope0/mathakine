"""
Endpoints API pour la gestion des utilisateurs
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any, List

from app.api.deps import get_db_session, get_current_user, get_current_gardien_or_archiviste
from app.schemas.user import User, UserCreate, UserUpdate
from app.services.auth_service import create_user, get_user_by_id, update_user
from app.core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter()

# Dictionnaire pour simuler l'état des tentatives
_challenges_progress = {}

@router.get("/", response_model=List[User])
def get_users(
    db: Session = Depends(get_db_session),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_gardien_or_archiviste)
) -> Any:
    """
    Récupérer tous les utilisateurs.
    Accessible uniquement aux Gardiens et Archivistes.
    """
    # Requête réelle à la base de données
    users = db.query(User).offset(skip).limit(limit).all()
    logger.info(f"Liste des utilisateurs récupérée par {current_user.username}")
    return users


@router.post("/", response_model=User, status_code=201)
def create_new_user(
    *,
    db: Session = Depends(get_db_session),
    user_in: UserCreate,
) -> Any:
    """
    Créer un nouvel utilisateur.
    Endpoint public pour l'inscription.
    """
    # Utiliser le service d'authentification pour créer l'utilisateur
    user = create_user(db, user_in)
    logger.info(f"Nouvel utilisateur créé: {user.username}")
    return user


@router.get("/me", response_model=User)
def get_user_me(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Récupérer les informations de l'utilisateur actuellement connecté.
    """
    logger.debug(f"Récupération des informations personnelles par {current_user.username}")
    return current_user


@router.get("/{user_id}", response_model=User)
def get_user(
    *,
    db: Session = Depends(get_db_session),
    user_id: int,
    current_user: User = Depends(get_current_gardien_or_archiviste)
) -> Any:
    """
    Récupérer un utilisateur par ID.
    Accessible uniquement aux Gardiens et Archivistes.
    """
    user = get_user_by_id(db, user_id)
    if user is None:
        logger.warning(f"Tentative d'accès à un utilisateur inexistant (ID: {user_id}) par {current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    logger.info(f"Récupération des informations de l'utilisateur {user.username} par {current_user.username}")
    return user


@router.put("/me", response_model=User)
def update_user_me(
    *,
    db: Session = Depends(get_db_session),
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Mettre à jour les informations de l'utilisateur actuellement connecté.
    """
    user = update_user(db, current_user, user_in)
    logger.info(f"Utilisateur {current_user.username} a mis à jour ses informations")
    return user


@router.put("/{user_id}", response_model=User)
def update_user_by_id(
    *,
    db: Session = Depends(get_db_session),
    user_id: int,
    user_in: UserUpdate,
    current_user: User = Depends(get_current_gardien_or_archiviste)
) -> Any:
    """
    Mettre à jour un utilisateur par ID.
    Accessible uniquement aux Gardiens et Archivistes.
    """
    user = get_user_by_id(db, user_id)
    if user is None:
        logger.warning(f"Tentative de mise à jour d'un utilisateur inexistant (ID: {user_id}) par {current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    user = update_user(db, user, user_in)
    logger.info(f"Utilisateur {user.username} mis à jour par {current_user.username}")
    return user


@router.get("/{user_id}/challenges/progress", response_model=dict)
def get_user_challenges_progress(
    *,
    db: Session = Depends(get_db_session),
    user_id: int,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Récupérer la progression des défis logiques pour un utilisateur.
    L'utilisateur peut voir sa propre progression, les Gardiens/Archivistes peuvent voir celle des autres.
    """
    # Vérifier si l'utilisateur demande sa propre progression ou s'il a les droits
    if current_user.id != user_id and current_user.role not in ["gardien", "archiviste"]:
        logger.warning(f"Tentative d'accès non autorisé à la progression de l'utilisateur {user_id} par {current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas accès à cette progression"
        )
    
    # Vérifier si l'utilisateur demandé existe
    user = get_user_by_id(db, user_id)
    if user is None:
        logger.warning(f"Tentative d'accès à la progression d'un utilisateur inexistant (ID: {user_id})")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    # TODO: Remplacer par un service réel de suivi de progression
    logger.info(f"Récupération de la progression des défis pour l'utilisateur {user.username}")
    return {
        "completed_challenges": 3,
        "total_challenges": 10,
        "success_rate": 0.8,
        "average_time": 45.5,
        "challenges": [
            {
                "id": 1,
                "title": "Défi de séquence logique",
                "is_completed": True,
                "attempts": 2,
                "best_time": 35.2
            },
            {
                "id": 2,
                "title": "Défi de reconnaissance de motifs",
                "is_completed": True,
                "attempts": 1,
                "best_time": 42.8
            },
            {
                "id": 3,
                "title": "Défi d'énigme",
                "is_completed": True,
                "attempts": 3,
                "best_time": 58.6
            }
        ]
    }


@router.get("/{user_id}/progress", response_model=dict)
def get_user_progress(
    *,
    db: Session = Depends(get_db_session),
    user_id: int,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Récupérer la progression globale d'un utilisateur.
    L'utilisateur peut voir sa propre progression, les Gardiens/Archivistes peuvent voir celle des autres.
    """
    # Vérifier si l'utilisateur demande sa propre progression ou s'il a les droits
    if current_user.id != user_id and current_user.role not in ["gardien", "archiviste"]:
        logger.warning(f"Tentative d'accès non autorisé à la progression de l'utilisateur {user_id} par {current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas accès à cette progression"
        )
    
    # Vérifier si l'utilisateur demandé existe
    user = get_user_by_id(db, user_id)
    if user is None:
        logger.warning(f"Tentative d'accès à la progression d'un utilisateur inexistant (ID: {user_id})")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    # TODO: Remplacer par un service réel de suivi de progression
    logger.info(f"Récupération de la progression globale pour l'utilisateur {user.username}")
    return {
        "total_attempts": 15,
        "correct_attempts": 12,
        "accuracy": 0.8,
        "average_time": 23.5,
        "exercises_completed": 10,
        "highest_streak": 8,
        "current_streak": 3,
        "by_category": {
            "addition": {
                "completed": 5,
                "accuracy": 0.9
            },
            "multiplication": {
                "completed": 3,
                "accuracy": 0.7
            },
            "division": {
                "completed": 2,
                "accuracy": 0.8
            }
        }
    }


@router.delete("/{user_id}", status_code=204, response_model=None)
def delete_user(
    *,
    db: Session = Depends(get_db_session),
    user_id: int,
):
    """
    Supprimer un utilisateur.
    """
    # Placeholder function - implement actual user deletion
    return None
