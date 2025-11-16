"""
Adaptateur pour intégrer les traductions dans EnhancedServerAdapter.

Fournit des méthodes compatibles avec l'API existante mais avec support des traductions.
"""
from typing import Optional, Dict, Any, List
from loguru import logger

from app.services.exercise_service_translations import (
    get_exercise as get_exercise_with_translation,
    list_exercises as list_exercises_with_translation
)
from app.utils.translation import parse_accept_language
from app.utils.date_utils import format_dates_for_json


def get_exercise_by_id_with_locale(
    exercise_id: int,
    locale: str = "fr"
) -> Optional[Dict[str, Any]]:
    """
    Récupère un exercice par ID avec traductions.
    Compatible avec l'API de EnhancedServerAdapter.
    
    Args:
        exercise_id: ID de l'exercice
        locale: Locale demandée (fr, en, etc.)
    
    Returns:
        Dictionnaire avec les données de l'exercice traduites ou None
    """
    try:
        exercise = get_exercise_with_translation(exercise_id, locale=locale)
        
        if not exercise:
            return None
        
        # Formater les dates si nécessaire
        exercise = format_dates_for_json(exercise)
        
        return exercise
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'exercice {exercise_id}: {e}")
        return None


def list_exercises_with_locale(
    locale: str = "fr",
    exercise_type: Optional[str] = None,
    difficulty: Optional[str] = None,
    search: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Liste les exercices avec traductions et filtres optionnels.
    Compatible avec l'API de EnhancedServerAdapter.
    
    Args:
        locale: Locale demandée
        exercise_type: Type d'exercice à filtrer
        difficulty: Difficulté à filtrer
        search: Terme de recherche (recherche dans title et question)
        limit: Nombre maximum de résultats
        offset: Décalage pour pagination
    
    Returns:
        Liste de dictionnaires avec les données des exercices traduites
    """
    try:
        exercises = list_exercises_with_translation(
            locale=locale,
            exercise_type=exercise_type,
            difficulty=difficulty,
            search=search,
            limit=limit,
            offset=offset
        )
        
        # Formater les dates pour chaque exercice
        exercises = [format_dates_for_json(exercise) for exercise in exercises]
        
        return exercises
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des exercices: {e}")
        return []


def count_exercises_with_locale(
    locale: str = "fr",
    exercise_type: Optional[str] = None,
    difficulty: Optional[str] = None,
    search: Optional[str] = None
) -> int:
    """
    Compte le nombre total d'exercices avec les filtres donnés.
    Compatible avec l'API de EnhancedServerAdapter.
    
    Args:
        locale: Locale demandée
        exercise_type: Type d'exercice à filtrer
        difficulty: Difficulté à filtrer
        search: Terme de recherche
    
    Returns:
        Nombre total d'exercices correspondant aux filtres
    """
    try:
        from app.services.exercise_service_translations import count_exercises
        return count_exercises(
            locale=locale,
            exercise_type=exercise_type,
            difficulty=difficulty,
            search=search
        )
    except Exception as e:
        logger.error(f"Erreur lors du comptage des exercices: {e}")
        return 0

