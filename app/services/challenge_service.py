"""
Service pour la gestion des challenges logiques (SQLAlchemy ORM).

Ce service remplace challenge_service_translations.py qui utilisait du raw SQL.
Utilise uniquement SQLAlchemy ORM pour la maintenabilité.

Créé : Phase 4 (20 Nov 2025)
"""
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from loguru import logger
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.models.logic_challenge import (AgeGroup, LogicChallenge,
                                        LogicChallengeAttempt,
                                        LogicChallengeType)


def create_challenge(
    db: Session,
    title: str,
    description: str,
    challenge_type: str,
    age_group: str,
    correct_answer: str,
    solution_explanation: str,
    question: Optional[str] = None,
    hints: Optional[List[str]] = None,
    visual_data: Optional[Dict] = None,
    difficulty_rating: float = 3.0,
    estimated_time_minutes: int = 10,
    tags: Optional[str] = None,
    creator_id: Optional[int] = None,
) -> LogicChallenge:
    """
    Créer un nouveau challenge.
    
    Args:
        db: Session SQLAlchemy
        title: Titre du challenge
        description: Description détaillée
        challenge_type: Type (SEQUENCE, PATTERN, SPATIAL, etc.)
        age_group: Groupe d'âge (GROUP_10_12, GROUP_13_15, etc.)
        correct_answer: Réponse correcte
        solution_explanation: Explication de la solution
        question: Question spécifique (optionnel)
        hints: Liste d'indices (optionnel)
        visual_data: Données de visualisation (optionnel)
        difficulty_rating: Difficulté 1-5 (défaut: 3.0)
        estimated_time_minutes: Temps estimé (défaut: 10)
        tags: Tags séparés par virgules (optionnel)
        creator_id: ID du créateur (optionnel)
    
    Returns:
        LogicChallenge créé
    """
    # Définir explicitement created_at pour éviter les valeurs NULL
    now = datetime.now(timezone.utc)
    challenge = LogicChallenge(
        title=title,
        description=description,
        challenge_type=challenge_type,
        age_group=age_group,
        question=question,
        correct_answer=correct_answer,
        solution_explanation=solution_explanation,
        hints=hints or [],
        visual_data=visual_data or {},
        difficulty_rating=difficulty_rating,
        estimated_time_minutes=estimated_time_minutes,
        tags=tags,
        creator_id=creator_id,
        is_active=True,
        created_at=now,  # Définir explicitement la date de création
    )
    
    db.add(challenge)
    db.commit()
    db.refresh(challenge)
    
    logger.info(f"Challenge créé: {challenge.id} - {challenge.title}")
    return challenge


def get_challenge(db: Session, challenge_id: int) -> Optional[LogicChallenge]:
    """
    Récupérer un challenge par ID.
    
    Args:
        db: Session SQLAlchemy
        challenge_id: ID du challenge
    
    Returns:
        LogicChallenge ou None si non trouvé
    """
    return db.query(LogicChallenge).filter(
        LogicChallenge.id == challenge_id,
        LogicChallenge.is_active == True
    ).first()


def list_challenges(
    db: Session,
    challenge_type: Optional[str] = None,
    age_group: Optional[str] = None,
    difficulty_min: Optional[float] = None,
    difficulty_max: Optional[float] = None,
    tags: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
) -> List[LogicChallenge]:
    """
    Lister les challenges avec filtres.
    
    Args:
        db: Session SQLAlchemy
        challenge_type: Filtrer par type (optionnel)
        age_group: Filtrer par groupe d'âge (optionnel)
        difficulty_min: Difficulté minimale (optionnel)
        difficulty_max: Difficulté maximale (optionnel)
        tags: Filtrer par tags (optionnel)
        limit: Nombre maximum de résultats (défaut: 10)
        offset: Offset pour pagination (défaut: 0)
    
    Returns:
        Liste de LogicChallenge
    """
    query = db.query(LogicChallenge).filter(LogicChallenge.is_active == True)
    
    # Filtres
    if challenge_type:
        query = query.filter(LogicChallenge.challenge_type == challenge_type)
    
    if age_group:
        query = query.filter(LogicChallenge.age_group == age_group)
    
    if difficulty_min is not None:
        query = query.filter(LogicChallenge.difficulty_rating >= difficulty_min)
    
    if difficulty_max is not None:
        query = query.filter(LogicChallenge.difficulty_rating <= difficulty_max)
    
    if tags:
        # Recherche partielle dans les tags
        query = query.filter(LogicChallenge.tags.contains(tags))
    
    # Trier par date de création (plus récent d'abord)
    # Si created_at est NULL, utiliser l'ID comme critère secondaire (plus l'ID est élevé, plus récent)
    from sqlalchemy import case
    query = query.order_by(
        LogicChallenge.created_at.desc().nullslast(),
        LogicChallenge.id.desc()  # Critère secondaire : ID décroissant
    )
    
    return query.offset(offset).limit(limit).all()


def count_challenges(
    db: Session,
    challenge_type: Optional[str] = None,
    age_group: Optional[str] = None,
) -> int:
    """
    Compter les challenges avec filtres.
    
    Args:
        db: Session SQLAlchemy
        challenge_type: Filtrer par type (optionnel)
        age_group: Filtrer par groupe d'âge (optionnel)
    
    Returns:
        Nombre de challenges correspondant aux filtres
    """
    query = db.query(LogicChallenge).filter(LogicChallenge.is_active == True)
    
    if challenge_type:
        query = query.filter(LogicChallenge.challenge_type == challenge_type)
    
    if age_group:
        query = query.filter(LogicChallenge.age_group == age_group)
    
    return query.count()


def update_challenge(
    db: Session,
    challenge_id: int,
    **kwargs
) -> Optional[LogicChallenge]:
    """
    Mettre à jour un challenge.
    
    Args:
        db: Session SQLAlchemy
        challenge_id: ID du challenge
        **kwargs: Champs à mettre à jour
    
    Returns:
        LogicChallenge mis à jour ou None si non trouvé
    """
    challenge = get_challenge(db, challenge_id)
    
    if not challenge:
        return None
    
    # Mettre à jour les champs fournis
    for key, value in kwargs.items():
        if hasattr(challenge, key):
            setattr(challenge, key, value)
    
    challenge.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(challenge)
    
    logger.info(f"Challenge mis à jour: {challenge.id}")
    return challenge


def delete_challenge(db: Session, challenge_id: int) -> bool:
    """
    Supprimer (soft delete) un challenge.
    
    Args:
        db: Session SQLAlchemy
        challenge_id: ID du challenge
    
    Returns:
        True si supprimé, False sinon
    """
    challenge = get_challenge(db, challenge_id)
    
    if not challenge:
        return False
    
    challenge.is_active = False
    db.commit()
    
    logger.info(f"Challenge supprimé (soft): {challenge.id}")
    return True


def get_user_completed_challenges(
    db: Session,
    user_id: int
) -> List[int]:
    """
    Récupérer les IDs des challenges complétés par un utilisateur.
    
    Args:
        db: Session SQLAlchemy
        user_id: ID de l'utilisateur
    
    Returns:
        Liste des IDs de challenges complétés
    """
    attempts = db.query(LogicChallengeAttempt).filter(
        LogicChallengeAttempt.user_id == user_id,
        LogicChallengeAttempt.is_correct == True
    ).all()
    
    return [attempt.challenge_id for attempt in attempts]


def record_attempt(
    db: Session,
    user_id: int,
    challenge_id: int,
    user_answer: str,
    is_correct: bool,
    time_spent_seconds: Optional[int] = None,
) -> LogicChallengeAttempt:
    """
    Enregistrer une tentative de résolution.
    
    Args:
        db: Session SQLAlchemy
        user_id: ID de l'utilisateur
        challenge_id: ID du challenge
        user_answer: Réponse fournie
        is_correct: Réponse correcte ou non
        time_spent_seconds: Temps passé (optionnel)
    
    Returns:
        LogicChallengeAttempt créé
    """
    attempt = LogicChallengeAttempt(
        user_id=user_id,
        challenge_id=challenge_id,
        user_answer=user_answer,
        is_correct=is_correct,
        time_spent_seconds=time_spent_seconds,
    )
    
    db.add(attempt)
    
    # Mettre à jour le taux de réussite du challenge
    if is_correct:
        challenge = get_challenge(db, challenge_id)
        if challenge:
            total_attempts = db.query(LogicChallengeAttempt).filter(
                LogicChallengeAttempt.challenge_id == challenge_id
            ).count()
            
            correct_attempts = db.query(LogicChallengeAttempt).filter(
                LogicChallengeAttempt.challenge_id == challenge_id,
                LogicChallengeAttempt.is_correct == True
            ).count()
            
            challenge.success_rate = (correct_attempts / total_attempts) * 100 if total_attempts > 0 else 0.0
    
    db.commit()
    db.refresh(attempt)
    
    logger.info(f"Tentative enregistrée: Challenge {challenge_id}, User {user_id}, Correct: {is_correct}")
    return attempt


def get_challenge_stats(db: Session, challenge_id: int) -> Dict[str, Any]:
    """
    Récupérer les statistiques d'un challenge.
    
    Args:
        db: Session SQLAlchemy
        challenge_id: ID du challenge
    
    Returns:
        Dictionnaire avec les statistiques
    """
    challenge = get_challenge(db, challenge_id)
    
    if not challenge:
        return {}
    
    total_attempts = db.query(LogicChallengeAttempt).filter(
        LogicChallengeAttempt.challenge_id == challenge_id
    ).count()
    
    correct_attempts = db.query(LogicChallengeAttempt).filter(
        LogicChallengeAttempt.challenge_id == challenge_id,
        LogicChallengeAttempt.is_correct == True
    ).count()
    
    unique_users = db.query(LogicChallengeAttempt.user_id).filter(
        LogicChallengeAttempt.challenge_id == challenge_id
    ).distinct().count()
    
    return {
        "challenge_id": challenge_id,
        "title": challenge.title,
        "total_attempts": total_attempts,
        "correct_attempts": correct_attempts,
        "success_rate": (correct_attempts / total_attempts * 100) if total_attempts > 0 else 0.0,
        "unique_users": unique_users,
        "difficulty_rating": challenge.difficulty_rating,
    }

