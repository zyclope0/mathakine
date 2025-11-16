"""
Service pour les exercices avec support des traductions (PostgreSQL pur).

Utilise psycopg2 directement avec des requêtes SQL brutes.
"""
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, Dict, Any, List
from loguru import logger

from server.database import get_db_connection
from app.db.queries_translations import ExerciseQueriesWithTranslations
from app.utils.translation import parse_accept_language
from app.utils.date_utils import format_dates_for_json
from app.utils.json_utils import parse_choices_json


def get_exercise(exercise_id: int, locale: str = "fr") -> Optional[Dict[str, Any]]:
    """
    Récupère un exercice par ID avec traductions.
    
    Args:
        exercise_id: ID de l'exercice
        locale: Locale demandée (fr, en, etc.)
    
    Returns:
        Dictionnaire avec les données de l'exercice traduites ou None
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        query, base_params = ExerciseQueriesWithTranslations.get_by_id(locale)
        # La requête a 7 %s: 4 pour traductions texte + 2 pour choices CASE + 1 pour WHERE id
        # base_params a 7 éléments: 6 locales + 1 None pour l'ID
        # Remplacer le dernier None par l'exercise_id
        params = base_params[:-1] + (exercise_id,)
        
        cursor.execute(query, params)
        row = cursor.fetchone()
        
        if not row:
            return None
        
        exercise = dict(row)
        
        # Parser les JSON arrays si nécessaire
        exercise['choices'] = parse_choices_json(exercise.get('choices'))
        
        # Formater les dates en ISO format strings pour sérialisation JSON
        exercise = format_dates_for_json(exercise)
        
        return exercise
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'exercice {exercise_id}: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


def count_exercises(
    locale: str = "fr",
    exercise_type: Optional[str] = None,
    difficulty: Optional[str] = None,
    search: Optional[str] = None
) -> int:
    """
    Compte le nombre total d'exercices avec les filtres donnés.
    
    Args:
        locale: Locale demandée
        exercise_type: Type d'exercice à filtrer
        difficulty: Difficulté à filtrer
        search: Terme de recherche
    
    Returns:
        Nombre total d'exercices correspondant aux filtres
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        query, params = ExerciseQueriesWithTranslations.count_exercises(
            locale=locale,
            exercise_type=exercise_type,
            difficulty=difficulty,
            search=search
        )
        
        cursor.execute(query, params)
        result = cursor.fetchone()
        
        return result['total'] if result else 0
    
    except Exception as e:
        logger.error(f"Erreur lors du comptage des exercices: {e}")
        return 0
    finally:
        cursor.close()
        conn.close()


def list_exercises(
    locale: str = "fr",
    exercise_type: Optional[str] = None,
    difficulty: Optional[str] = None,
    search: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Liste les exercices avec traductions et filtres optionnels.
    
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
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        query, params = ExerciseQueriesWithTranslations.list_exercises(
            locale=locale,
            exercise_type=exercise_type,
            difficulty=difficulty,
            search=search,
            limit=limit,
            offset=offset
        )
        
        logger.info(f"Exécution requête SQL avec limit={limit}, offset={offset}, search={search}")
        logger.debug(f"Query SQL: {query[:200]}...")
        logger.debug(f"Params: {params}")
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        logger.info(f"Récupération de {len(rows)} exercices depuis la BDD (locale: {locale}, type: {exercise_type}, difficulty: {difficulty}, search: {search}, limit demandé: {limit}, offset: {offset})")
        
        exercises = []
        for row in rows:
            exercise = dict(row)
            
            # Parser les JSON arrays si nécessaire
            exercise['choices'] = parse_choices_json(exercise.get('choices'))
            
            # Formater les dates en ISO format strings pour sérialisation JSON
            exercise = format_dates_for_json(exercise)
            
            # Log pour déboguer les valeurs NULL
            if not exercise.get('title') or not exercise.get('question'):
                logger.warning(f"Exercice {exercise.get('id')} a des valeurs NULL: title={exercise.get('title')}, question={exercise.get('question')}")
            
            exercises.append(exercise)
        
        logger.info(f"Retour de {len(exercises)} exercices après traitement")
        return exercises
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des exercices: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


def create_exercise_with_translations(
    exercise_data: Dict[str, Any],
    locale: str = "fr"
) -> Optional[Dict[str, Any]]:
    """
    Crée un exercice avec traductions.
    
    Args:
        exercise_data: Dictionnaire avec les données de l'exercice
        locale: Locale principale pour la création
    
    Returns:
        Dictionnaire avec l'exercice créé
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Construire les colonnes de traduction depuis exercise_data
        title_translations = exercise_data.get('title_translations', {})
        if not title_translations and 'title' in exercise_data:
            title_translations = {locale: exercise_data['title']}
        
        question_translations = exercise_data.get('question_translations', {})
        if not question_translations and 'question' in exercise_data:
            question_translations = {locale: exercise_data['question']}
        
        explanation_translations = exercise_data.get('explanation_translations', {})
        if not explanation_translations and 'explanation' in exercise_data:
            explanation_translations = {locale: exercise_data.get('explanation', '')}
        
        hint_translations = exercise_data.get('hint_translations', {})
        if not hint_translations and 'hint' in exercise_data:
            hint_translations = {locale: exercise_data.get('hint', '')}
        
        choices_translations = exercise_data.get('choices_translations', {})
        if not choices_translations and 'choices' in exercise_data:
            choices_translations = {locale: exercise_data.get('choices', [])}
        
        query = """
        INSERT INTO exercises 
        (title, question, explanation, hint, choices,
         title_translations, question_translations, explanation_translations, 
         hint_translations, choices_translations,
         exercise_type, difficulty, correct_answer, tags, 
         creator_id, age_group, context_theme, complexity,
         answer_type, text_metadata,
         image_url, audio_url, ai_generated, is_active, is_archived, view_count,
         created_at, updated_at) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        RETURNING id, created_at
        """
        
        params = (
            exercise_data.get('title', ''),
            exercise_data.get('question', ''),
            exercise_data.get('explanation'),
            exercise_data.get('hint'),
            json.dumps(exercise_data.get('choices', [])) if exercise_data.get('choices') else None,
            json.dumps(title_translations),
            json.dumps(question_translations),
            json.dumps(explanation_translations),
            json.dumps(hint_translations),
            json.dumps(choices_translations),
            exercise_data.get('exercise_type'),
            exercise_data.get('difficulty'),
            exercise_data.get('correct_answer'),
            exercise_data.get('tags'),
            exercise_data.get('creator_id'),  # Peut être NULL
            exercise_data.get('age_group'),  # Peut être NULL
            exercise_data.get('context_theme'),  # Peut être NULL
            exercise_data.get('complexity'),  # Peut être NULL
            exercise_data.get('answer_type'),  # Peut être NULL
            json.dumps(exercise_data.get('text_metadata')) if exercise_data.get('text_metadata') else None,  # Peut être NULL
            exercise_data.get('image_url'),
            exercise_data.get('audio_url'),
            exercise_data.get('ai_generated', False),
            exercise_data.get('is_active', True),
            exercise_data.get('is_archived', False),  # Valeur par défaut : False
            exercise_data.get('view_count', 0),  # Valeur par défaut : 0
        )
        
        cursor.execute(query, params)
        result = cursor.fetchone()
        conn.commit()
        
        # Récupérer l'exercice créé avec traductions
        if result:
            exercise_id = result['id']
            created_at_from_insert = result.get('created_at')
            logger.info(f"Exercice créé avec ID={exercise_id}, created_at depuis INSERT: {created_at_from_insert}, récupération avec locale={locale}")
            created_exercise = get_exercise(exercise_id, locale=locale)
            if created_exercise:
                logger.info(f"Exercice {exercise_id} récupéré: title={created_exercise.get('title')}, created_at={created_exercise.get('created_at')}, question={created_exercise.get('question')}")
            else:
                logger.error(f"Impossible de récupérer l'exercice {exercise_id} après création")
            return created_exercise
        
        logger.error("Aucun exercice créé (result est None)")
        return None
    
    except Exception as e:
        logger.error(f"Erreur lors de la création de l'exercice: {e}")
        conn.rollback()
        return None
    finally:
        cursor.close()
        conn.close()
