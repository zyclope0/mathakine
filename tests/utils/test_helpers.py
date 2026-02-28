"""
Utilitaires pour aider à l'écriture de tests fiables.

Ce module fournit des fonctions et classes pour:
- Générer des valeurs de test uniques
- Simplifier la création d'instances de modèles
- Convertir des dictionnaires en instances de modèles
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Type, TypeVar, cast

from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.exercise import DifficultyLevel, Exercise, ExerciseType
from app.models.user import User, UserRole
from app.utils.db_helpers import adapt_enum_for_db, get_enum_value

# Type générique pour les modèles
T = TypeVar("T")


def unique_id(prefix: str = "") -> str:
    """
    Génère un identifiant unique pour les tests.

    Args:
        prefix: Préfixe optionnel à ajouter à l'identifiant

    Returns:
        Une chaîne unique de la forme {prefix}_{uuid}
    """
    unique_suffix = uuid.uuid4().hex[:8]
    return f"{prefix}_{unique_suffix}" if prefix else unique_suffix


def unique_username() -> str:
    """
    Génère un nom d'utilisateur unique pour les tests.

    Returns:
        Un nom d'utilisateur unique
    """
    return unique_id("test_user")


def unique_email(domain: str = "example.com") -> str:
    """
    Génère une adresse email unique pour les tests.

    Args:
        domain: Le domaine de l'email

    Returns:
        Une adresse email unique
    """
    local_part = unique_id("test")
    return f"{local_part}@{domain}"


def verify_user_email_for_tests(username: str) -> None:
    """
    Marque un utilisateur comme email vérifié (pour les tests qui nécessitent un login).
    À appeler après création via API, avant tenter un login.
    """
    from app.models.user import User
    from app.services.enhanced_server_adapter import EnhancedServerAdapter

    db = EnhancedServerAdapter.get_db_session()
    try:
        user = db.query(User).filter(User.username == username).first()
        if user:
            user.is_email_verified = True
            db.commit()
    finally:
        EnhancedServerAdapter.close_db_session(db)


def set_user_created_at_for_tests(username: str, minutes_ago: float) -> None:
    """
    Recule la date de création d'un utilisateur (pour tester la période de grâce).

    Args:
        username: Nom d'utilisateur
        minutes_ago: Nombre de minutes dans le passé (ex: 50 pour dépasser 45 min)
    """
    from app.models.user import User
    from app.services.enhanced_server_adapter import EnhancedServerAdapter

    db = EnhancedServerAdapter.get_db_session()
    try:
        user = db.query(User).filter(User.username == username).first()
        if user:
            user.created_at = datetime.now(timezone.utc) - timedelta(
                minutes=minutes_ago
            )
            db.commit()
    finally:
        EnhancedServerAdapter.close_db_session(db)


def dict_to_user(user_data: Dict[str, Any]) -> User:
    """
    Convertit un dictionnaire en instance de User.

    Cette fonction est particulièrement utile pour convertir les données
    générées par la fixture mock_user en instance de User.

    Args:
        user_data: Dictionnaire contenant les données de l'utilisateur

    Returns:
        Instance de User
    """
    user = User(
        username=user_data["username"],
        email=user_data["email"],
        hashed_password=user_data.get(
            "hashed_password", get_password_hash(user_data["password"])
        ),
        full_name=user_data.get("full_name"),
        role=user_data.get("role", UserRole.PADAWAN.value),
        is_active=user_data.get("is_active", True),
        grade_level=user_data.get("grade_level"),
        learning_style=user_data.get("learning_style"),
        preferred_difficulty=user_data.get("preferred_difficulty"),
        preferred_theme=user_data.get("preferred_theme", "light"),
        accessibility_settings=user_data.get("accessibility_settings"),
    )
    return user


def dict_to_exercise(exercise_data: Dict[str, Any]) -> Exercise:
    """
    Convertit un dictionnaire en instance d'Exercise.

    Args:
        exercise_data: Dictionnaire contenant les données de l'exercice

    Returns:
        Instance d'Exercise
    """
    exercise = Exercise(
        title=exercise_data["title"],
        question=exercise_data["question"],
        correct_answer=exercise_data["correct_answer"],
        exercise_type=exercise_data.get("exercise_type", ExerciseType.ADDITION.value),
        difficulty=exercise_data.get("difficulty", DifficultyLevel.INITIE.value),
        age_group=exercise_data.get("age_group", "6-8"),
        creator_id=exercise_data.get("creator_id"),
        choices=exercise_data.get("choices"),
        explanation=exercise_data.get("explanation"),
        hint=exercise_data.get("hint"),
        image_url=exercise_data.get("image_url"),
        is_active=exercise_data.get("is_active", True),
        is_archived=exercise_data.get("is_archived", False),
        ai_generated=exercise_data.get("ai_generated", False),
    )
    return exercise


def adapted_dict_to_user(user_data: Dict[str, Any], db_session: Session) -> User:
    """
    Convertit un dictionnaire en instance de User avec adaptation des valeurs d'enum pour PostgreSQL.

    Cette fonction est particulièrement utile pour les tests avec PostgreSQL
    qui nécessitent des valeurs d'enum correctement adaptées.

    Args:
        user_data: Dictionnaire contenant les données de l'utilisateur
        db_session: Session de base de données pour adapter les valeurs d'enum

    Returns:
        Instance de User avec des valeurs d'enum adaptées pour PostgreSQL
    """
    # Adapter le rôle pour PostgreSQL
    role_value = user_data.get("role", "padawan")
    adapted_role = adapt_enum_for_db("UserRole", role_value, db_session)

    user = User(
        username=user_data["username"],
        email=user_data["email"],
        hashed_password=user_data.get(
            "hashed_password", get_password_hash(user_data["password"])
        ),
        full_name=user_data.get("full_name"),
        role=adapted_role,
        is_active=user_data.get("is_active", True),
        grade_level=user_data.get("grade_level"),
        learning_style=user_data.get("learning_style"),
        preferred_difficulty=user_data.get("preferred_difficulty"),
        preferred_theme=user_data.get("preferred_theme", "light"),
        accessibility_settings=user_data.get("accessibility_settings"),
    )
    return user


def adapted_dict_to_exercise(
    exercise_data: Dict[str, Any], db_session: Session
) -> Exercise:
    """
    Convertit un dictionnaire en instance d'Exercise avec adaptation des valeurs d'enum pour PostgreSQL.

    Args:
        exercise_data: Dictionnaire contenant les données de l'exercice
        db_session: Session de base de données pour adapter les valeurs d'enum

    Returns:
        Instance d'Exercise avec des valeurs d'enum adaptées pour PostgreSQL
    """
    # Adapter les valeurs d'enum pour PostgreSQL
    exercise_type_value = exercise_data.get("exercise_type", "addition")
    difficulty_value = exercise_data.get("difficulty", "initie")

    adapted_exercise_type = adapt_enum_for_db(
        "ExerciseType", exercise_type_value, db_session
    )
    adapted_difficulty = adapt_enum_for_db(
        "DifficultyLevel", difficulty_value, db_session
    )

    exercise = Exercise(
        title=exercise_data["title"],
        question=exercise_data["question"],
        correct_answer=exercise_data["correct_answer"],
        exercise_type=adapted_exercise_type,
        difficulty=adapted_difficulty,
        age_group=exercise_data.get("age_group", "6-8"),
        creator_id=exercise_data.get("creator_id"),
        choices=exercise_data.get("choices"),
        explanation=exercise_data.get("explanation"),
        hint=exercise_data.get("hint"),
        image_url=exercise_data.get("image_url"),
        is_active=exercise_data.get("is_active", True),
        is_archived=exercise_data.get("is_archived", False),
        ai_generated=exercise_data.get("ai_generated", False),
    )
    return exercise
