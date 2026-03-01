"""
Service pour la gestion des challenges logiques (SQLAlchemy ORM).

Ce service remplace challenge_service_translations.py qui utilisait du raw SQL.
Utilise uniquement SQLAlchemy ORM pour la maintenabilité.

Créé : Phase 4 (20 Nov 2025)
"""

import os
import random
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.core.logging_config import get_logger

logger = get_logger(__name__)
from sqlalchemy import and_, case, func, or_
from sqlalchemy.orm import Session

from app.models.logic_challenge import (
    AgeGroup,
    LogicChallenge,
    LogicChallengeAttempt,
    LogicChallengeType,
)

# ============================================================================
# MAPPING DES GROUPES D'ÂGE (après migration ENUM)
# ============================================================================
# PostgreSQL ENUM `agegroup` contient (après migration):
#   - GROUP_6_8    (6-8 ans)
#   - GROUP_10_12  (9-11 ans) - legacy name
#   - GROUP_13_15  (12-14 ans) - legacy name
#   - GROUP_15_17  (15-17 ans)
#   - ADULT        (adultes)
#   - ALL_AGES     (tous âges)
#
# Frontend utilise:
#   - 6-8, 9-11, 12-14, 15-17, adulte, tous-ages
# ============================================================================

# Mapping des groupes d'âge frontend vers les valeurs ENUM PostgreSQL
FRONTEND_TO_DB_AGE_GROUP = {
    # Groupes d'âge frontend → valeurs DB (mapping 1:1 après migration)
    "6-8": AgeGroup.GROUP_6_8,  # 6-8 ans → GROUP_6_8
    "9-11": AgeGroup.GROUP_10_12,  # 9-11 ans → GROUP_10_12
    "12-14": AgeGroup.GROUP_13_15,  # 12-14 ans → GROUP_13_15
    "15-17": AgeGroup.GROUP_15_17,  # 15-17 ans → GROUP_15_17
    "adulte": AgeGroup.ADULT,  # adulte → ADULT
    "tous-ages": AgeGroup.ALL_AGES,  # tous âges → ALL_AGES
    # Anciennes valeurs (rétrocompatibilité)
    "10-12": AgeGroup.GROUP_10_12,
    "13-15": AgeGroup.GROUP_13_15,
    "all": AgeGroup.ALL_AGES,
    # Valeurs legacy qui pourraient arriver (code ancien)
    "enfant": AgeGroup.GROUP_6_8,
    "adolescent": AgeGroup.GROUP_13_15,
    "9-12": AgeGroup.GROUP_10_12,
    "12-13": AgeGroup.GROUP_13_15,
    "13+": AgeGroup.GROUP_15_17,
    # Valeurs DB (cas où on reçoit déjà la valeur DB)
    "group_6_8": AgeGroup.GROUP_6_8,
    "group_10_12": AgeGroup.GROUP_10_12,
    "group_13_15": AgeGroup.GROUP_13_15,
    "group_15_17": AgeGroup.GROUP_15_17,
    "adult": AgeGroup.ADULT,
    "all_ages": AgeGroup.ALL_AGES,
}

# Mapping inverse : ENUM PostgreSQL vers format frontend pour affichage
DB_TO_FRONTEND_AGE_GROUP = {
    AgeGroup.GROUP_6_8: "6-8",  # GROUP_6_8 → 6-8 ans
    AgeGroup.GROUP_10_12: "9-11",  # GROUP_10_12 → 9-11 ans
    AgeGroup.GROUP_13_15: "12-14",  # GROUP_13_15 → 12-14 ans
    AgeGroup.GROUP_15_17: "15-17",  # GROUP_15_17 → 15-17 ans
    AgeGroup.ADULT: "adulte",  # ADULT → adulte
    AgeGroup.ALL_AGES: "tous-ages",  # ALL_AGES → tous âges
}

# Alias pour compatibilité (même contenu)
DB_TO_FRONTEND_AGE_GROUP_EXTENDED = DB_TO_FRONTEND_AGE_GROUP


def normalize_age_group_for_db(age_group: str) -> AgeGroup:
    """
    Convertit un groupe d'âge frontend vers une valeur ENUM PostgreSQL.

    Args:
        age_group: Groupe d'âge (format frontend ou ENUM)

    Returns:
        Valeur AgeGroup compatible avec PostgreSQL
    """
    if not age_group:
        return AgeGroup.ALL_AGES

    # Normaliser la casse
    age_group_lower = age_group.lower().strip()

    # Chercher dans le mapping
    if age_group_lower in FRONTEND_TO_DB_AGE_GROUP:
        return FRONTEND_TO_DB_AGE_GROUP[age_group_lower]

    # Si c'est déjà une valeur AgeGroup, la retourner
    try:
        return AgeGroup(age_group_lower)
    except ValueError:
        pass

    # Fallback vers ALL_AGES
    logger.warning(f"Groupe d'âge non reconnu: {age_group}, utilisation de ALL_AGES")
    return AgeGroup.ALL_AGES


def normalize_age_group_for_frontend(age_group) -> str:
    """
    Convertit une valeur ENUM PostgreSQL vers le format frontend.

    Args:
        age_group: Valeur AgeGroup de la DB (peut être AgeGroup, str, ou None)

    Returns:
        String au format frontend (6-8, 9-11, etc.)
    """
    if not age_group:
        return "tous-ages"

    # Si c'est une string, essayer de la convertir en AgeGroup d'abord
    if isinstance(age_group, str):
        # Vérifier d'abord dans le mapping étendu par valeur string
        age_group_lower = age_group.lower()
        for ag_enum, frontend_val in DB_TO_FRONTEND_AGE_GROUP_EXTENDED.items():
            if ag_enum.value == age_group_lower or ag_enum.name == age_group.upper():
                return frontend_val
        # Fallback
        return "tous-ages"

    # Si c'est un enum, utiliser le mapping étendu
    return DB_TO_FRONTEND_AGE_GROUP_EXTENDED.get(age_group, "tous-ages")


def challenge_to_api_dict(challenge) -> Dict[str, Any]:
    """
    Convertit un objet LogicChallenge en dict pour l'API liste.

    Args:
        challenge: Objet LogicChallenge (ORM)

    Returns:
        Dict avec les champs attendus par le frontend.
    """
    return {
        "id": challenge.id,
        "title": challenge.title,
        "description": challenge.description,
        "challenge_type": challenge.challenge_type,
        "age_group": normalize_age_group_for_frontend(challenge.age_group),
        "difficulty": challenge.difficulty,
        "tags": challenge.tags,
        "difficulty_rating": challenge.difficulty_rating,
        "estimated_time_minutes": challenge.estimated_time_minutes,
        "success_rate": challenge.success_rate,
        "view_count": challenge.view_count,
        "is_archived": challenge.is_archived,
    }


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
    generation_parameters: Optional[Dict] = None,
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

    # Convertir le groupe d'âge frontend vers la valeur ENUM PostgreSQL
    db_age_group = normalize_age_group_for_db(age_group)
    logger.debug(f"Conversion groupe d'âge: {age_group} -> {db_age_group}")

    challenge = LogicChallenge(
        title=title,
        description=description,
        challenge_type=challenge_type,
        age_group=db_age_group,
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
        generation_parameters=generation_parameters,
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
    return (
        db.query(LogicChallenge)
        .filter(LogicChallenge.id == challenge_id, LogicChallenge.is_active == True)
        .first()
    )


def get_challenge_for_api(db: Session, challenge_id: int) -> Optional[Dict[str, Any]]:
    """
    Récupère un challenge formaté pour l'API (GET /api/challenges/{id}).
    Inclut les défis archivés (pas de filtre is_active).
    Lève ChallengeNotFoundError si le défi n'existe pas.
    """
    from app.exceptions import ChallengeNotFoundError
    from app.services.logic_challenge_service import LogicChallengeService
    from app.utils.json_utils import safe_parse_json

    challenge = LogicChallengeService.get_challenge(db, challenge_id)
    if not challenge:
        raise ChallengeNotFoundError()
    return {
        "id": challenge.id,
        "title": challenge.title,
        "description": challenge.description,
        "challenge_type": challenge.challenge_type,
        "age_group": normalize_age_group_for_frontend(challenge.age_group),
        "difficulty": challenge.difficulty,
        "question": challenge.question,
        "correct_answer": challenge.correct_answer,
        "choices": safe_parse_json(challenge.choices, []),
        "solution_explanation": challenge.solution_explanation,
        "visual_data": safe_parse_json(challenge.visual_data, {}),
        "hints": safe_parse_json(challenge.hints, []),
        "tags": challenge.tags,
        "difficulty_rating": challenge.difficulty_rating,
        "estimated_time_minutes": challenge.estimated_time_minutes,
        "success_rate": challenge.success_rate,
        "view_count": challenge.view_count,
        "is_active": challenge.is_active,
        "is_archived": challenge.is_archived,
    }


def list_challenges(
    db: Session,
    challenge_type: Optional[str] = None,
    age_group: Optional[str] = None,
    difficulty_min: Optional[float] = None,
    difficulty_max: Optional[float] = None,
    tags: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
    order: str = "random",
    exclude_ids: Optional[List[int]] = None,
    total: Optional[int] = None,
    active_only: bool = True,
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
    # Normaliser challenge_type pour cohérence enum (API "SEQUENCE" → DB)
    from app.utils.db_helpers import adapt_enum_for_db

    challenge_type_db = (
        adapt_enum_for_db("LogicChallengeType", challenge_type)
        if challenge_type
        else None
    )

    query = db.query(LogicChallenge).filter(LogicChallenge.is_active == True)

    if active_only:
        query = query.filter(LogicChallenge.is_archived == False)

    # Filtres
    if challenge_type_db:
        query = query.filter(LogicChallenge.challenge_type == challenge_type_db)

    if age_group:
        query = query.filter(LogicChallenge.age_group == age_group)

    if difficulty_min is not None:
        query = query.filter(LogicChallenge.difficulty_rating >= difficulty_min)

    if difficulty_max is not None:
        query = query.filter(LogicChallenge.difficulty_rating <= difficulty_max)

    if tags:
        query = query.filter(LogicChallenge.tags.contains(tags))

    # Recherche texte : title, description, tags (comme AdminService)
    if search and search.strip():
        pattern = f"%{search.strip()}%"
        query = query.filter(
            or_(
                LogicChallenge.title.ilike(pattern),
                LogicChallenge.description.ilike(pattern),
                LogicChallenge.tags.ilike(pattern),
            )
        )

    # Exclure les défis déjà réussis si demandé
    if exclude_ids:
        query = query.filter(LogicChallenge.id.notin_(exclude_ids))

    # Ordre : aléatoire par défaut (varier l'entraînement), ou récent
    if order == "recent":
        query = query.order_by(
            LogicChallenge.created_at.desc().nullslast(), LogicChallenge.id.desc()
        )
        return query.offset(offset).limit(limit).all()

    # Optimisation: random_offset O(1) au lieu de ORDER BY RANDOM() O(n).
    # Désactivé en TESTING: double engine fixtures vs handlers → items=[].
    # Réf: DIAGNOSTIC_CHALLENGES_LIST_2026-02.md
    _use_random_offset = (
        total is not None and total > 0 and os.getenv("TESTING", "").lower() != "true"
    )
    if _use_random_offset:
        max_offset_val = max(0, total - limit - offset)
        random_offset_val = (
            random.randint(0, max_offset_val) if max_offset_val > 0 else 0
        )
        return (
            query.order_by(LogicChallenge.id)
            .offset(offset + random_offset_val)
            .limit(limit)
            .all()
        )

    # func.random() O(n) — stable en tests, fallback si total non fourni
    return query.order_by(func.random()).offset(offset).limit(limit).all()


def count_challenges(
    db: Session,
    challenge_type: Optional[str] = None,
    age_group: Optional[str] = None,
    difficulty_min: Optional[float] = None,
    difficulty_max: Optional[float] = None,
    tags: Optional[str] = None,
    search: Optional[str] = None,
    exclude_ids: Optional[List[int]] = None,
    active_only: bool = True,
) -> int:
    """
    Compter les challenges avec filtres.
    Aligné sur list_challenges pour cohérence total/items.

    Args:
        db: Session SQLAlchemy
        challenge_type: Filtrer par type (optionnel)
        age_group: Filtrer par groupe d'âge (optionnel)
        difficulty_min: Difficulté minimale (optionnel)
        difficulty_max: Difficulté maximale (optionnel)
        tags: Filtrer par tags (optionnel)
        exclude_ids: IDs à exclure du comptage (ex: défis déjà réussis)

    Returns:
        Nombre de challenges correspondant aux filtres
    """
    from app.utils.db_helpers import adapt_enum_for_db

    challenge_type_db = (
        adapt_enum_for_db("LogicChallengeType", challenge_type)
        if challenge_type
        else None
    )

    query = db.query(LogicChallenge).filter(LogicChallenge.is_active == True)

    if active_only:
        query = query.filter(LogicChallenge.is_archived == False)

    if challenge_type_db:
        query = query.filter(LogicChallenge.challenge_type == challenge_type_db)

    if age_group:
        query = query.filter(LogicChallenge.age_group == age_group)

    if difficulty_min is not None:
        query = query.filter(LogicChallenge.difficulty_rating >= difficulty_min)

    if difficulty_max is not None:
        query = query.filter(LogicChallenge.difficulty_rating <= difficulty_max)

    if tags:
        query = query.filter(LogicChallenge.tags.contains(tags))

    if search and search.strip():
        pattern = f"%{search.strip()}%"
        query = query.filter(
            or_(
                LogicChallenge.title.ilike(pattern),
                LogicChallenge.description.ilike(pattern),
                LogicChallenge.tags.ilike(pattern),
            )
        )

    if exclude_ids:
        query = query.filter(LogicChallenge.id.notin_(exclude_ids))

    return query.count()


def update_challenge(
    db: Session, challenge_id: int, **kwargs
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

    challenge.updated_at = datetime.now(timezone.utc)
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


def get_user_completed_challenges(db: Session, user_id: int) -> List[int]:
    """
    Récupérer les IDs des challenges complétés par un utilisateur (distincts).

    Args:
        db: Session SQLAlchemy
        user_id: ID de l'utilisateur

    Returns:
        Liste des IDs de challenges complétés (sans doublons)
    """
    rows = (
        db.query(LogicChallengeAttempt.challenge_id)
        .filter(
            LogicChallengeAttempt.user_id == user_id,
            LogicChallengeAttempt.is_correct == True,
        )
        .distinct()
        .all()
    )
    return [r[0] for r in rows if r[0] is not None]


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

    # Mettre à jour le taux de réussite du challenge (sur chaque tentative, pas seulement les correctes)
    challenge = get_challenge(db, challenge_id)
    if challenge:
        # Requête unique avec agrégation pour total et correct
        stats = (
            db.query(
                func.count(LogicChallengeAttempt.id).label("total"),
                func.count(case((LogicChallengeAttempt.is_correct == True, 1))).label(
                    "correct"
                ),
            )
            .filter(LogicChallengeAttempt.challenge_id == challenge_id)
            .first()
        )

        total_attempts = stats.total if stats and stats.total else 0
        correct_attempts = stats.correct if stats and stats.correct else 0
        challenge.success_rate = (
            (correct_attempts / total_attempts) * 100 if total_attempts > 0 else 0.0
        )

    db.commit()
    db.refresh(attempt)

    logger.info(
        f"Tentative enregistrée: Challenge {challenge_id}, User {user_id}, Correct: {is_correct}"
    )
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

    total_attempts = (
        db.query(LogicChallengeAttempt)
        .filter(LogicChallengeAttempt.challenge_id == challenge_id)
        .count()
    )

    correct_attempts = (
        db.query(LogicChallengeAttempt)
        .filter(
            LogicChallengeAttempt.challenge_id == challenge_id,
            LogicChallengeAttempt.is_correct == True,
        )
        .count()
    )

    unique_users = (
        db.query(LogicChallengeAttempt.user_id)
        .filter(LogicChallengeAttempt.challenge_id == challenge_id)
        .distinct()
        .count()
    )

    return {
        "challenge_id": challenge_id,
        "title": challenge.title,
        "total_attempts": total_attempts,
        "correct_attempts": correct_attempts,
        "success_rate": (
            (correct_attempts / total_attempts * 100) if total_attempts > 0 else 0.0
        ),
        "unique_users": unique_users,
        "difficulty_rating": challenge.difficulty_rating,
    }
