"""
Adaptateur pour intégrer les traductions dans les handlers de défis.

Fournit des méthodes compatibles avec l'API existante mais avec support des traductions.
"""
from typing import Optional, Dict, Any, List
from loguru import logger

from app.services.challenge_service_translations import (
    get_challenge as get_challenge_with_translation,
    list_challenges as list_challenges_with_translation,
    count_challenges as count_challenges_with_translation
)


def get_challenge_by_id_with_locale(
    challenge_id: int,
    locale: str = "fr"
) -> Optional[Dict[str, Any]]:
    """
    Récupère un défi logique par ID avec traductions.
    Compatible avec l'API de EnhancedServerAdapter.
    
    Args:
        challenge_id: ID du défi
        locale: Locale demandée (fr, en, etc.)
    
    Returns:
        Dictionnaire avec les données du défi traduites ou None
    """
    try:
        challenge = get_challenge_with_translation(challenge_id, locale=locale)
        
        if not challenge:
            return None
        
        # Formater les dates si nécessaire
        if challenge.get('created_at'):
            if hasattr(challenge['created_at'], 'isoformat'):
                challenge['created_at'] = challenge['created_at'].isoformat()
        
        if challenge.get('updated_at'):
            if hasattr(challenge['updated_at'], 'isoformat'):
                challenge['updated_at'] = challenge['updated_at'].isoformat()
        
        return challenge
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du défi {challenge_id}: {e}")
        return None


def list_challenges_with_locale(
    locale: str = "fr",
    challenge_type: Optional[str] = None,
    age_group: Optional[str] = None,
    search: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Liste les défis logiques avec traductions et filtres optionnels.
    Compatible avec l'API de EnhancedServerAdapter.
    
    Args:
        locale: Locale demandée
        challenge_type: Type de défi à filtrer
        age_group: Groupe d'âge à filtrer
        search: Terme de recherche
        limit: Nombre maximum de résultats
        offset: Décalage pour pagination
    
    Returns:
        Liste de dictionnaires avec les données des défis traduites
    """
    try:
        challenges = list_challenges_with_translation(
            locale=locale,
            challenge_type=challenge_type,
            age_group=age_group,
            search=search,
            limit=limit,
            offset=offset
        )
        
        # Les dates sont déjà formatées par list_challenges_with_translation
        return challenges
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des défis: {e}")
        return []


def count_challenges_with_locale(
    locale: str = "fr",
    challenge_type: Optional[str] = None,
    age_group: Optional[str] = None,
    search: Optional[str] = None
) -> int:
    """
    Compte le nombre total de défis avec les filtres donnés.
    Compatible avec l'API de EnhancedServerAdapter.
    
    Args:
        locale: Locale demandée
        challenge_type: Type de défi à filtrer
        age_group: Groupe d'âge à filtrer
        search: Terme de recherche
    
    Returns:
        Nombre total de défis correspondant aux filtres
    """
    try:
        return count_challenges_with_translation(
            locale=locale,
            challenge_type=challenge_type,
            age_group=age_group,
            search=search
        )
    except Exception as e:
        logger.error(f"Erreur lors du comptage des défis: {e}")
        return 0

