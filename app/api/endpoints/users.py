"""
Endpoints API pour la gestion des utilisateurs
"""
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy import Integer, desc, func
from sqlalchemy.orm import Session

from app.api.deps import (get_current_active_user, get_current_archiviste,
                          get_current_gardien_or_archiviste, get_current_user,
                          get_db_session)
from app.core.constants import Messages, UserRoles
from app.core.logging_config import get_logger
from app.core.messages import SystemMessages, UserMessages
from app.models.attempt import Attempt
from app.models.exercise import Exercise
from app.models.logic_challenge import LogicChallenge, LogicChallengeAttempt
from app.models.progress import Progress
from app.models.user import User as UserModel
from app.models.user import UserRole
from app.models.user_session import UserSession as UserSessionModel
from app.schemas.progress import ProgressDetail, ProgressResponse
from app.schemas.user import (User, UserCreate, UserInDB, UserPasswordUpdate,
                              UserUpdate)
from app.schemas.user_session import UserSession, UserSessionRevoke
from app.services.auth_service import (create_user, get_user_by_id,
                                       update_user, update_user_password)
from app.services.user_service import UserService

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
    # Requête réelle à la base de données avec le bon modèle
    users_db = db.query(UserModel).offset(skip).limit(limit).all()
    
    # Convertir en schémas Pydantic en gérant les valeurs None
    users_response = []
    for user_db in users_db:
        # Créer un dictionnaire avec les valeurs corrigées
        user_dict = {
            "id": user_db.id,
            "username": user_db.username,
            "email": user_db.email,
            "full_name": user_db.full_name,
            "role": user_db.role,
            "is_active": user_db.is_active,
            "created_at": user_db.created_at or datetime.now(timezone.utc),
            "updated_at": user_db.updated_at or datetime.now(timezone.utc),
            "grade_level": user_db.grade_level,
            "learning_style": user_db.learning_style,
            "preferred_difficulty": user_db.preferred_difficulty,
            "preferred_theme": user_db.preferred_theme or "spatial",  # Valeur par défaut si None
            "accessibility_settings": user_db.accessibility_settings
        }
        users_response.append(user_dict)
    
    logger.info(f"Liste des utilisateurs récupérée par {current_user.username}")
    return users_response


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


@router.put("/me/password", status_code=200)
def update_user_password_me(
    *,
    db: Session = Depends(get_db_session),
    password_update: UserPasswordUpdate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Mettre à jour le mot de passe de l'utilisateur actuellement connecté.
    """
    try:
        update_user_password(
            db=db,
            user=current_user,
            current_password=password_update.current_password,
            new_password=password_update.new_password
        )
        logger.info(f"Mot de passe mis à jour pour l'utilisateur {current_user.username}")
        return {"message": "Mot de passe mis à jour avec succès"}
    except HTTPException:
        raise  # Re-lancer l'exception HTTPException telle quelle
    except Exception as password_update_error:
        logger.error(f"Erreur lors de la mise à jour du mot de passe pour {current_user.username}: {str(password_update_error)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de la mise à jour du mot de passe"
        )


@router.get("/me/sessions", response_model=List[UserSession])
def get_user_sessions(
    *,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Récupérer toutes les sessions actives de l'utilisateur actuellement connecté.
    """
    try:
        # Récupérer toutes les sessions actives de l'utilisateur
        sessions = db.query(UserSessionModel).filter(
            UserSessionModel.user_id == current_user.id,
            UserSessionModel.is_active == True,
            UserSessionModel.expires_at > datetime.now(timezone.utc)
        ).order_by(UserSessionModel.last_activity.desc()).all()
        
        logger.debug(f"Récupération de {len(sessions)} sessions actives pour {current_user.username}")
        
        # Convertir en schéma Pydantic
        session_list = []
        for session in sessions:
            session_dict = {
                "id": session.id,
                "device_info": session.device_info,
                "ip_address": str(session.ip_address) if session.ip_address else None,
                "user_agent": session.user_agent,
                "location_data": session.location_data,
                "is_active": session.is_active,
                "last_activity": session.last_activity,
                "created_at": session.created_at,
                "expires_at": session.expires_at,
                "is_current": False  # TODO: Détecter la session actuelle via le token
            }
            session_list.append(session_dict)
        
        return session_list
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des sessions pour {current_user.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des sessions"
        )


@router.delete("/me/sessions/{session_id}", response_model=UserSessionRevoke)
def revoke_user_session(
    *,
    db: Session = Depends(get_db_session),
    session_id: int = Path(..., description="ID de la session à révoquer"),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Révoquer une session spécifique de l'utilisateur actuellement connecté.
    L'utilisateur ne peut révoquer que ses propres sessions.
    """
    try:
        # Récupérer la session
        session = db.query(UserSessionModel).filter(
            UserSessionModel.id == session_id,
            UserSessionModel.user_id == current_user.id
        ).first()
        
        if not session:
            logger.warning(f"Tentative de révocation d'une session inexistante ou non autorisée: session_id={session_id}, user={current_user.username}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session non trouvée ou vous n'avez pas l'autorisation de la révoquer"
            )
        
        # Marquer la session comme inactive
        session.is_active = False
        db.commit()
        
        logger.info(f"Session {session_id} révoquée pour l'utilisateur {current_user.username}")
        
        return UserSessionRevoke(
            success=True,
            message="Session révoquée avec succès"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erreur lors de la révocation de la session {session_id} pour {current_user.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la révocation de la session"
        )


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
    
    # Calculer les vraies statistiques depuis la base de données
    logger.info(f"Récupération de la progression des défis pour l'utilisateur {user.username}")
    
    # Nombre total de défis actifs dans le système
    total_challenges = db.query(LogicChallenge).filter(
        LogicChallenge.is_active == True,
        LogicChallenge.is_archived == False
    ).count()
    
    # Récupérer toutes les tentatives de l'utilisateur
    all_attempts = db.query(LogicChallengeAttempt).filter(
        LogicChallengeAttempt.user_id == user_id
    ).all()
    
    # Identifier les défis complétés (au moins une tentative correcte)
    completed_challenge_ids = set()
    challenge_stats = {}
    
    for attempt in all_attempts:
        challenge_id = attempt.challenge_id
        
        if challenge_id not in challenge_stats:
            challenge_stats[challenge_id] = {
                "attempts": 0,
                "correct_attempts": 0,
                "best_time": None,
                "times": []
            }
        
        challenge_stats[challenge_id]["attempts"] += 1
        
        if attempt.is_correct:
            challenge_stats[challenge_id]["correct_attempts"] += 1
            completed_challenge_ids.add(challenge_id)
            
            if attempt.time_spent:
                if challenge_stats[challenge_id]["best_time"] is None:
                    challenge_stats[challenge_id]["best_time"] = attempt.time_spent
                else:
                    challenge_stats[challenge_id]["best_time"] = min(
                        challenge_stats[challenge_id]["best_time"],
                        attempt.time_spent
                    )
        
        if attempt.time_spent:
            challenge_stats[challenge_id]["times"].append(attempt.time_spent)
    
    # Calculer le success_rate global
    total_attempts = len(all_attempts)
    correct_attempts = sum(1 for a in all_attempts if a.is_correct)
    success_rate = correct_attempts / total_attempts if total_attempts > 0 else 0.0
    
    # Calculer le temps moyen
    all_times = [a.time_spent for a in all_attempts if a.time_spent]
    average_time = sum(all_times) / len(all_times) if all_times else 0.0
    
    # Construire la liste des défis complétés avec détails
    challenges_list = []
    if completed_challenge_ids:
        completed_challenges = db.query(LogicChallenge).filter(
            LogicChallenge.id.in_(completed_challenge_ids)
        ).all()
        
        for challenge in completed_challenges:
            stats = challenge_stats.get(challenge.id, {})
            challenges_list.append({
                "id": challenge.id,
                "title": challenge.title,
                "is_completed": True,
                "attempts": stats.get("attempts", 0),
                "best_time": round(stats.get("best_time", 0), 2) if stats.get("best_time") else None
            })
    
    return {
        "completed_challenges": len(completed_challenge_ids),
        "total_challenges": total_challenges,
        "success_rate": round(success_rate, 2),
        "average_time": round(average_time, 1),
        "challenges": challenges_list
    }


@router.get("/me/progress", response_model=List[ProgressResponse])
def get_user_progress_me(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db_session)
) -> Any:
    """
    Récupère tous les progrès de l'utilisateur actuel.
    """
    # Récupérer l'utilisateur actuel
    user_id = current_user.id
    
    # Récupérer tous les progrès de l'utilisateur
    progress_records = db.query(Progress).filter(Progress.user_id == user_id).all()
    
    # Convertir en liste de réponses
    result = []
    for record in progress_records:
        result.append({
            "exercise_type": record.exercise_type,
            "difficulty": record.difficulty,
            "total_attempts": record.total_attempts,
            "correct_attempts": record.correct_attempts,
            "average_time": record.average_time,
            "completion_rate": record.completion_rate or record.calculate_completion_rate(),
            "mastery_level": record.mastery_level,
            "last_updated": record.last_updated.isoformat() if record.last_updated else None
        })
    
    return result


@router.get("/me/progress/{exercise_type}", response_model=ProgressDetail)
def get_user_progress_by_type_me(
    exercise_type: str = Path(..., description="Type d'exercice à consulter"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db_session)
) -> Any:
    """
    Récupère les progrès de l'utilisateur actuel pour un type d'exercice spécifique.
    """
    # Récupérer l'utilisateur actuel
    user_id = current_user.id
    
    # Récupérer le progrès pour le type d'exercice spécifique
    progress = db.query(Progress).filter(
        Progress.user_id == user_id,
        Progress.exercise_type == exercise_type
    ).first()
    
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aucun progrès trouvé pour le type d'exercice '{exercise_type}'"
        )
    
    # Récupérer des statistiques supplémentaires
    recent_attempts = db.query(Attempt).join(
        Exercise, Attempt.exercise_id == Exercise.id
    ).filter(
        Attempt.user_id == user_id,
        Exercise.exercise_type == exercise_type
    ).order_by(desc(Attempt.created_at)).limit(5).all()
    
    recent_attempts_data = []
    for attempt in recent_attempts:
        exercise = db.query(Exercise).filter(Exercise.id == attempt.exercise_id).first()
        if exercise:
            recent_attempts_data.append({
                "exercise_id": attempt.exercise_id,
                "exercise_title": exercise.title,
                "is_correct": attempt.is_correct,
                "time_spent": attempt.time_spent,
                "date": attempt.created_at.isoformat() if attempt.created_at else None
            })
    
    # Construire la réponse détaillée
    return {
        "exercise_type": progress.exercise_type,
        "difficulty": progress.difficulty,
        "total_attempts": progress.total_attempts,
        "correct_attempts": progress.correct_attempts,
        "average_time": progress.average_time,
        "completion_rate": progress.completion_rate or progress.calculate_completion_rate(),
        "mastery_level": progress.mastery_level,
        "streak": progress.streak,
        "highest_streak": progress.highest_streak,
        "strengths": progress.strengths,
        "areas_to_improve": progress.areas_to_improve,
        "recent_attempts": recent_attempts_data,
        "last_updated": progress.last_updated.isoformat() if progress.last_updated else None
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
    
    # Calculer les vraies statistiques depuis la base de données
    logger.info(f"Récupération de la progression globale pour l'utilisateur {user.username}")
    
    # Récupérer toutes les tentatives de l'utilisateur avec jointure sur exercises
    attempts_query = db.query(Attempt, Exercise).join(
        Exercise, Attempt.exercise_id == Exercise.id
    ).filter(
        Attempt.user_id == user_id
    ).order_by(Attempt.created_at).all()
    
    if not attempts_query:
        # Utilisateur sans tentatives
        return {
            "total_attempts": 0,
            "correct_attempts": 0,
            "accuracy": 0.0,
            "average_time": 0.0,
            "exercises_completed": 0,
            "highest_streak": 0,
            "current_streak": 0,
            "by_category": {}
        }
    
    # Stats globales
    total_attempts = len(attempts_query)
    correct_attempts = sum(1 for attempt, _ in attempts_query if attempt.is_correct)
    accuracy = correct_attempts / total_attempts if total_attempts > 0 else 0.0
    
    # Temps moyen (seulement les tentatives avec time_spent)
    times = [attempt.time_spent for attempt, _ in attempts_query if attempt.time_spent]
    average_time = sum(times) / len(times) if times else 0.0
    
    # Exercices uniques complétés (au moins une tentative correcte)
    completed_exercise_ids = set()
    for attempt, exercise in attempts_query:
        if attempt.is_correct:
            completed_exercise_ids.add(exercise.id)
    exercises_completed = len(completed_exercise_ids)
    
    # Calcul des streaks (séquences de réussites consécutives)
    streaks = []
    current_streak = 0
    for attempt, _ in attempts_query:
        if attempt.is_correct:
            current_streak += 1
        else:
            if current_streak > 0:
                streaks.append(current_streak)
            current_streak = 0
    # Ajouter le dernier streak s'il existe
    if current_streak > 0:
        streaks.append(current_streak)
    
    highest_streak = max(streaks) if streaks else 0
    current_streak_value = streaks[-1] if streaks else 0
    
    # Grouper par catégorie (exercise_type)
    by_category = {}
    category_attempts = {}
    
    for attempt, exercise in attempts_query:
        exercise_type = exercise.exercise_type or "unknown"
        
        if exercise_type not in category_attempts:
            category_attempts[exercise_type] = {
                "total": 0,
                "correct": 0,
                "completed_ids": set()
            }
        
        category_attempts[exercise_type]["total"] += 1
        if attempt.is_correct:
            category_attempts[exercise_type]["correct"] += 1
            category_attempts[exercise_type]["completed_ids"].add(exercise.id)
    
    # Construire le dictionnaire by_category
    for exercise_type, stats in category_attempts.items():
        total = stats["total"]
        correct = stats["correct"]
        by_category[exercise_type] = {
            "completed": len(stats["completed_ids"]),
            "accuracy": round(correct / total, 2) if total > 0 else 0.0
        }
    
    return {
        "total_attempts": total_attempts,
        "correct_attempts": correct_attempts,
        "accuracy": round(accuracy, 2),
        "average_time": round(average_time, 1),
        "exercises_completed": exercises_completed,
        "highest_streak": highest_streak,
        "current_streak": current_streak_value,
        "by_category": by_category
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
    import traceback

    from sqlalchemy.exc import SQLAlchemyError

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
    except Exception as user_db_error:
        db.rollback()
        stack_trace = traceback.format_exc()
        logger.error(f"Erreur lors de la suppression de l'utilisateur {user_id}: {str(user_db_error)}")
        logger.error(f"Stack trace: {stack_trace}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la suppression de l'utilisateur: {str(user_db_error)}"
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
    attempts = db.query(Attempt).filter(Attempt.user_id == user_id).all()
    
    # Calculer les statistiques d'exercices
    total_attempts = len(attempts)
    correct_attempts = sum(1 for attempt in attempts if attempt.is_correct)
    success_rate = (correct_attempts / total_attempts * 100) if total_attempts > 0 else 0
    
    # Statistiques de tentatives par exercice
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


@router.get("/me/statistics", response_model=Dict[str, Any])
def get_user_statistics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db_session)
) -> Any:
    """
    Récupère les statistiques globales de l'utilisateur actuel.
    """
    # Récupérer l'utilisateur actuel
    user_id = current_user.id
    
    # Récupérer les statistiques de tentatives
    attempts_count = db.query(func.count(Attempt.id)).filter(Attempt.user_id == user_id).scalar() or 0
    correct_attempts = db.query(func.count(Attempt.id)).filter(
        Attempt.user_id == user_id, 
        Attempt.is_correct == True
    ).scalar() or 0
    
    # Calculer le taux de réussite
    success_rate = 0
    if attempts_count > 0:
        success_rate = (correct_attempts / attempts_count) * 100
    
    # Récupérer le temps moyen par exercice
    avg_time = db.query(func.avg(Attempt.time_spent)).filter(Attempt.user_id == user_id).scalar() or 0
    
    # Récupérer les statistiques de progression par type d'exercice
    progress_records = db.query(Progress).filter(Progress.user_id == user_id).all()
    
    # Organiser les données de progression par type d'exercice
    progress_by_type = {}
    for record in progress_records:
        progress_by_type[record.exercise_type] = {
            "mastery_level": record.mastery_level,
            "total_attempts": record.total_attempts,
            "correct_attempts": record.correct_attempts,
            "completion_rate": record.completion_rate or record.calculate_completion_rate(),
            "average_time": record.average_time
        }
    
    # Tentatives récentes (les 5 dernières)
    recent_attempts = db.query(Attempt).filter(
        Attempt.user_id == user_id
    ).order_by(desc(Attempt.created_at)).limit(5).all()
    
    recent_attempts_data = []
    for attempt in recent_attempts:
        exercise = db.query(Exercise).filter(Exercise.id == attempt.exercise_id).first()
        if exercise:
            recent_attempts_data.append({
                "exercise_id": attempt.exercise_id,
                "exercise_title": exercise.title,
                "exercise_type": exercise.exercise_type,
                "is_correct": attempt.is_correct,
                "time_spent": attempt.time_spent,
                "date": attempt.created_at.isoformat() if attempt.created_at else None
            })
    
    # Assembler toutes les statistiques
    statistics = {
        "global": {
            "total_attempts": attempts_count,
            "correct_attempts": correct_attempts,
            "success_rate": success_rate,
            "average_time": float(avg_time) if avg_time else 0
        },
        "progress_by_type": progress_by_type,
        "recent_attempts": recent_attempts_data
    }
    
    return statistics
