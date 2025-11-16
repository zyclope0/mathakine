"""
Service pour les défis logiques avec support des traductions (PostgreSQL pur).

Utilise psycopg2 directement avec des requêtes SQL brutes.
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, Dict, Any, List
from loguru import logger
import json
import traceback

from server.database import get_db_connection
from app.db.queries_translations import ChallengeQueriesWithTranslations
from app.utils.date_utils import format_dates_for_json
from app.utils.json_utils import parse_choices_json


def normalize_age_group_for_insert(age_group: str) -> str:
    """
    Normalise un groupe d'âge vers les valeurs PostgreSQL valides.
    
    Valeurs PostgreSQL acceptées : GROUP_10_12, GROUP_13_15, ALL_AGES
    
    Args:
        age_group: Valeur brute du groupe d'âge
    
    Returns:
        Valeur normalisée pour PostgreSQL
    """
    if not age_group:
        return 'GROUP_10_12'  # Valeur par défaut
    
    age_group_lower = age_group.lower().strip()
    
    # Mapping des valeurs vers les valeurs PostgreSQL valides
    age_group_mapping = {
        # Valeurs textuelles
        'enfant': 'GROUP_10_12',
        'adolescent': 'GROUP_13_15',
        'adulte': 'ALL_AGES',
        # Valeurs avec tirets
        '9-12': 'GROUP_10_12',
        '10-12': 'GROUP_10_12',
        '12-13': 'GROUP_13_15',
        '13-15': 'GROUP_13_15',
        '13+': 'GROUP_13_15',
        # Valeurs avec underscores
        'group_10_12': 'GROUP_10_12',
        'group_13_15': 'GROUP_13_15',
        'all_ages': 'ALL_AGES',
        'all': 'ALL_AGES',
        # Valeurs en majuscules (déjà normalisées)
        'GROUP_10_12': 'GROUP_10_12',
        'GROUP_13_15': 'GROUP_13_15',
        'ALL_AGES': 'ALL_AGES',
        # Valeurs avec préfixe AGE_
        'age_9_12': 'GROUP_10_12',
        'age_12_13': 'GROUP_13_15',
        'age_13_plus': 'GROUP_13_15',
    }
    
    # Chercher dans le mapping
    normalized = age_group_mapping.get(age_group_lower)
    if normalized:
        return normalized
    
    # Si la valeur commence par GROUP_, la mettre en majuscules
    if age_group.upper().startswith('GROUP_'):
        return age_group.upper()
    
    # Valeur par défaut si non trouvée
    logger.warning(f"Groupe d'âge non reconnu '{age_group}', utilisation de GROUP_10_12 par défaut")
    return 'GROUP_10_12'


def get_challenge(challenge_id: int, locale: str = "fr") -> Optional[Dict[str, Any]]:
    """
    Récupère un défi logique par ID avec traductions.
    
    Args:
        challenge_id: ID du défi
        locale: Locale demandée (fr, en, etc.)
    
    Returns:
        Dictionnaire avec les données du défi traduites ou None
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        query, base_params = ChallengeQueriesWithTranslations.get_by_id(locale)
        # Remplacer le dernier None par le challenge_id
        params = base_params[:-1] + (challenge_id,)
        
        cursor.execute(query, params)
        row = cursor.fetchone()
        
        if not row:
            return None
        
        challenge = dict(row)
        
        # Parser les JSON arrays si nécessaire
        if challenge.get('hints'):
            if isinstance(challenge['hints'], str):
                challenge['hints'] = json.loads(challenge['hints'])
            elif isinstance(challenge['hints'], dict):
                challenge['hints'] = list(challenge['hints'].values()) if challenge['hints'] else None
        
        if challenge.get('choices'):
            if isinstance(challenge['choices'], str):
                challenge['choices'] = json.loads(challenge['choices'])
            elif isinstance(challenge['choices'], dict):
                challenge['choices'] = list(challenge['choices'].values()) if challenge['choices'] else None
        
        if challenge.get('visual_data'):
            if isinstance(challenge['visual_data'], str):
                challenge['visual_data'] = json.loads(challenge['visual_data'])
        
        # Formater les dates en ISO format strings pour sérialisation JSON
        challenge = format_dates_for_json(challenge)
        
        return challenge
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du défi {challenge_id}: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


def list_challenges(
    locale: str = "fr",
    challenge_type: Optional[str] = None,
    age_group: Optional[str] = None,
    search: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Liste les défis logiques avec traductions et filtres optionnels.
    
    Args:
        locale: Locale demandée
        challenge_type: Type de défi à filtrer
        age_group: Groupe d'âge à filtrer
        search: Terme de recherche (recherche dans title et description)
        limit: Nombre maximum de résultats
        offset: Décalage pour pagination
    
    Returns:
        Liste de dictionnaires avec les données des défis traduites
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        query, params = ChallengeQueriesWithTranslations.list_challenges(
            locale=locale,
            challenge_type=challenge_type,
            age_group=age_group,
            search=search,
            limit=limit,
            offset=offset
        )
        
        logger.info(f"Exécution requête SQL avec limit={limit}, offset={offset}, search={search}")
        logger.debug(f"Query SQL: {query[:200]}...")
        logger.debug(f"Params: {params}")
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        logger.info(f"Récupération de {len(rows)} défis depuis la BDD (locale: {locale}, type: {challenge_type}, age_group: {age_group}, search: {search}, limit demandé: {limit}, offset: {offset})")
        
        challenges = []
        for row in rows:
            challenge = dict(row)
            
            # Parser les JSON arrays si nécessaire
            challenge['choices'] = parse_choices_json(challenge.get('choices'))
            
            if challenge.get('hints'):
                if isinstance(challenge['hints'], str):
                    challenge['hints'] = json.loads(challenge['hints'])
                elif isinstance(challenge['hints'], dict):
                    challenge['hints'] = list(challenge['hints'].values()) if challenge['hints'] else None
            
            if challenge.get('visual_data'):
                if isinstance(challenge['visual_data'], str):
                    challenge['visual_data'] = json.loads(challenge['visual_data'])
            
            # Formater les dates en ISO format strings pour sérialisation JSON
            challenge = format_dates_for_json(challenge)
            
            challenges.append(challenge)
        
        logger.info(f"Retour de {len(challenges)} défis après traitement")
        return challenges
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des défis: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


def count_challenges(
    locale: str = "fr",
    challenge_type: Optional[str] = None,
    age_group: Optional[str] = None,
    search: Optional[str] = None
) -> int:
    """
    Compte le nombre total de défis avec les filtres donnés.
    
    Args:
        locale: Locale demandée
        challenge_type: Type de défi à filtrer
        age_group: Groupe d'âge à filtrer
        search: Terme de recherche
    
    Returns:
        Nombre total de défis correspondant aux filtres
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        query, params = ChallengeQueriesWithTranslations.count_challenges(
            locale=locale,
            challenge_type=challenge_type,
            age_group=age_group,
            search=search
        )
        
        cursor.execute(query, params)
        result = cursor.fetchone()
        
        return result['total'] if result else 0
    
    except Exception as e:
        logger.error(f"Erreur lors du comptage des défis: {e}")
        return 0
    finally:
        cursor.close()
        conn.close()


def create_challenge_with_translations(
    db,  # Session DB (non utilisée mais conservée pour compatibilité)
    title: str,
    description: str,
    challenge_type: str,
    age_group: str,
    question: Optional[str] = None,
    correct_answer: str = "",
    solution_explanation: Optional[str] = None,
    hints: Optional[List[str]] = None,
    visual_data: Optional[Dict[str, Any]] = None,
    difficulty_rating: float = 3.0,
    estimated_time_minutes: int = 10,
    tags: Optional[str] = None,
    creator_id: Optional[int] = None,
    locale: str = "fr"
) -> Optional[Dict[str, Any]]:
    """
    Crée un challenge avec traductions.
    
    Args:
        db: Session DB (non utilisée, conservée pour compatibilité)
        title: Titre du challenge
        description: Description du challenge
        challenge_type: Type de challenge (SEQUENCE, PATTERN, etc.)
        age_group: Groupe d'âge (GROUP_10_12, etc.)
        question: Question optionnelle
        correct_answer: Réponse correcte
        solution_explanation: Explication de la solution
        hints: Liste d'indices
        visual_data: Données visuelles (JSON)
        difficulty_rating: Note de difficulté (1-5)
        estimated_time_minutes: Temps estimé en minutes
        tags: Tags séparés par virgules
        creator_id: ID du créateur
        locale: Locale principale pour la création
    
    Returns:
        Dictionnaire avec le challenge créé
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Construire les colonnes de traduction
        title_translations = {locale: title}
        description_translations = {locale: description}
        question_translations = {locale: question} if question else {locale: None}
        solution_explanation_translations = {locale: solution_explanation} if solution_explanation else {locale: None}
        hints_translations = {locale: hints} if hints else {locale: []}
        
        # Préparer les données JSON
        hints_json = json.dumps(hints) if hints else None
        visual_data_json = json.dumps(visual_data) if visual_data else None
        
        query = """
        INSERT INTO logic_challenges 
        (title, description, question, solution_explanation, correct_answer,
         title_translations, description_translations, question_translations, 
         solution_explanation_translations, hints_translations,
         challenge_type, age_group, hints, visual_data,
         difficulty_rating, estimated_time_minutes, tags,
         creator_id, is_active, is_archived, view_count,
         created_at, updated_at) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        RETURNING id, created_at
        """
        
        # Normaliser le groupe d'âge pour PostgreSQL
        # Les valeurs valides sont : GROUP_10_12, GROUP_13_15, ALL_AGES
        normalized_age_group = normalize_age_group_for_insert(age_group)
        
        params = (
            title,
            description,
            question,
            solution_explanation,
            correct_answer,
            json.dumps(title_translations),
            json.dumps(description_translations),
            json.dumps(question_translations),
            json.dumps(solution_explanation_translations),
            json.dumps(hints_translations),
            challenge_type.upper(),  # S'assurer que c'est en majuscules
            normalized_age_group,
            hints_json,
            visual_data_json,
            difficulty_rating,
            estimated_time_minutes,
            tags or "ai,generated,mathélogique",
            creator_id,
            True,  # is_active
            False,  # is_archived
            0,  # view_count
        )
        
        cursor.execute(query, params)
        conn.commit()
        
        result = cursor.fetchone()
        challenge_id = result['id'] if result else None
        
        if not challenge_id:
            logger.error("Erreur: Le challenge n'a pas été créé")
            return None
        
        logger.info(f"Challenge créé avec ID={challenge_id}")
        
        # Récupérer le challenge créé avec traductions
        created_challenge = get_challenge(challenge_id, locale=locale)
        
        return created_challenge
    
    except Exception as e:
        logger.error(f"Erreur lors de la création du challenge: {e}")
        logger.debug(traceback.format_exc())
        conn.rollback()
        return None
    finally:
        cursor.close()
        conn.close()

