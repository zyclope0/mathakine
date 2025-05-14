"""
Endpoints API pour la gestion des utilisateurs
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any, List, Optional

from app.api.deps import get_db_session, get_current_user, get_current_gardien_or_archiviste, get_current_archiviste
from app.schemas.user import User, UserCreate, UserUpdate
from app.services.auth_service import create_user, get_user_by_id, update_user
from app.core.logging_config import get_logger
from app.models.user import User as UserModel, UserRole

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
    current_user: User = Depends(get_current_archiviste)
) -> None:
    """
    Supprimer un utilisateur par ID.
    
    Cette opération supprime également automatiquement toutes les données associées
    grâce aux relations cascade définies dans les modèles.
    Seul un Archiviste peut supprimer un utilisateur.
    """
    from sqlalchemy.exc import SQLAlchemyError
    import logging
    import traceback

    logger = logging.getLogger(__name__)
    logger.info(f"Tentative de suppression de l'utilisateur {user_id} par {current_user.username}")

    # Vérifier qu'on ne tente pas de supprimer l'utilisateur courant
    if current_user.id == user_id:
        logger.warning(f"Tentative de suppression de son propre compte par {current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous ne pouvez pas supprimer votre propre compte"
        )

    try:
        # Vérifier si l'utilisateur existe
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            logger.warning(f"Tentative de suppression d'un utilisateur inexistant (ID: {user_id})")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )

        # Supprimer l'utilisateur (les données associées seront supprimées automatiquement 
        # grâce aux relations cascade)
        db.delete(user)
        db.commit()
        
        logger.info(f"Utilisateur {user.username} (ID: {user_id}) supprimé avec succès par {current_user.username}")
        return None

    except SQLAlchemyError as sqla_error:
        db.rollback()
        error_msg = str(sqla_error)
        stack_trace = traceback.format_exc()
        logger.error(f"Erreur SQL lors de la suppression de l'utilisateur {user_id}: {error_msg}")
        logger.error(f"Stack trace: {stack_trace}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur de base de données: {error_msg}"
        )
    except Exception as e:
        db.rollback()
        stack_trace = traceback.format_exc()
        logger.error(f"Erreur lors de la suppression de l'utilisateur {user_id}: {str(e)}")
        logger.error(f"Stack trace: {stack_trace}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la suppression de l'utilisateur: {str(e)}"
        )


@router.get("/{user_id}/stats", response_model=dict)
def get_user_stats(
    *,
    db: Session = Depends(get_db_session),
    user_id: int,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Récupérer les statistiques d'un utilisateur.
    L'utilisateur peut voir ses propres statistiques, les Gardiens/Archivistes peuvent voir celles des autres.
    """
    # Vérifier si l'utilisateur demande ses propres statistiques ou s'il a les droits
    if current_user.id != user_id and current_user.role not in ["gardien", "archiviste"]:
        logger.warning(f"Tentative d'accès non autorisé aux statistiques de l'utilisateur {user_id} par {current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas accès à ces statistiques"
        )
    
    # Vérifier si l'utilisateur demandé existe
    user = get_user_by_id(db, user_id)
    if user is None:
        logger.warning(f"Tentative d'accès aux statistiques d'un utilisateur inexistant (ID: {user_id})")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    # Récupérer les tentatives d'exercices de l'utilisateur
    from app.models.attempt import Attempt
    attempts = db.query(Attempt).filter(Attempt.user_id == user_id).all()
    
    # Calculer les statistiques d'exercices
    total_attempts = len(attempts)
    correct_attempts = sum(1 for attempt in attempts if attempt.is_correct)
    success_rate = (correct_attempts / total_attempts * 100) if total_attempts > 0 else 0
    
    # Statistiques de tentatives par exercice
    from sqlalchemy import func, Integer
    from app.models.exercise import Exercise
    
    # Compter le nombre d'exercices distincts tentés
    exercise_count = db.query(func.count(func.distinct(Attempt.exercise_id))). \
        filter(Attempt.user_id == user_id).scalar() or 0
    
    # Statistiques par type d'exercice
    stats_by_type = {}
    
    exercise_types = db.query(Exercise.exercise_type, func.count(Attempt.id), func.sum(func.cast(Attempt.is_correct, Integer))).\
        join(Attempt, Attempt.exercise_id == Exercise.id).\
        filter(Attempt.user_id == user_id).\
        group_by(Exercise.exercise_type).all()
    
    for exercise_type, count, correct in exercise_types:
        stats_by_type[exercise_type] = {
            "total": count,
            "correct": correct or 0,  # Gérer les valeurs None
            "success_rate": (correct / count * 100) if count > 0 and correct is not None else 0
        }
    
    # Statistiques des défis logiques
    from app.models.logic_challenge import LogicChallenge, LogicChallengeAttempt
    
    # Récupérer les tentatives de défis logiques de l'utilisateur
    logic_attempts = db.query(LogicChallengeAttempt).filter(LogicChallengeAttempt.user_id == user_id).all()
    
    # Calculer les statistiques de défis logiques
    total_logic_attempts = len(logic_attempts)
    correct_logic_attempts = sum(1 for attempt in logic_attempts if attempt.is_correct)
    logic_success_rate = (correct_logic_attempts / total_logic_attempts * 100) if total_logic_attempts > 0 else 0
    
    # Compter le nombre de défis logiques distincts tentés
    logic_challenge_count = db.query(func.count(func.distinct(LogicChallengeAttempt.challenge_id))). \
        filter(LogicChallengeAttempt.user_id == user_id).scalar() or 0
    
    # Statistiques par type de défi logique
    logic_stats_by_type = {}
    
    logic_types = db.query(LogicChallenge.challenge_type, func.count(LogicChallengeAttempt.id), 
                          func.sum(func.cast(LogicChallengeAttempt.is_correct, Integer))).\
        join(LogicChallengeAttempt, LogicChallengeAttempt.challenge_id == LogicChallenge.id).\
        filter(LogicChallengeAttempt.user_id == user_id).\
        group_by(LogicChallenge.challenge_type).all()
    
    for challenge_type, count, correct in logic_types:
        logic_stats_by_type[challenge_type] = {
            "total": count,
            "correct": correct or 0,
            "success_rate": (correct / count * 100) if count > 0 and correct is not None else 0
        }
    
    # Préparation des statistiques de défis logiques
    logic_challenge_stats = {
        "total_challenges_attempted": logic_challenge_count,
        "total_attempts": total_logic_attempts,
        "correct_attempts": correct_logic_attempts,
        "success_rate": logic_success_rate,
        "stats_by_type": logic_stats_by_type
    }
    
    logger.info(f"Récupération des statistiques pour l'utilisateur {user.username}")
    
    return {
        "user_id": user_id,
        "username": user.username,
        "total_exercises_attempted": exercise_count,
        "total_attempts": total_attempts,
        "correct_attempts": correct_attempts,
        "success_rate": success_rate,
        "stats_by_type": stats_by_type,
        "logic_challenge_stats": logic_challenge_stats
    }
