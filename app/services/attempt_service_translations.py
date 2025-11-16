"""
Service pour les tentatives avec support PostgreSQL pur.

Utilise psycopg2 directement avec des requêtes SQL brutes.
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, Dict, Any
from loguru import logger

from server.database import get_db_connection
from app.utils.date_utils import format_date_for_json


def create_attempt_with_postgres(attempt_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Crée une tentative d'exercice avec PostgreSQL direct.
    
    Args:
        attempt_data: Dictionnaire contenant les données de la tentative
            - user_id: int (requis)
            - exercise_id: int (requis)
            - user_answer: str (requis)
            - is_correct: bool (requis)
            - time_spent: float (optionnel)
            - attempt_number: int (optionnel, défaut: 1)
            - hints_used: int (optionnel, défaut: 0)
            - device_info: str (optionnel)
    
    Returns:
        Dictionnaire avec les données de la tentative créée ou None
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Vérifier que l'exercice existe
        exercise_id = attempt_data.get("exercise_id")
        cursor.execute("SELECT id FROM exercises WHERE id = %s", (exercise_id,))
        exercise_exists = cursor.fetchone()
        
        if not exercise_exists:
            logger.error(f"Tentative d'enregistrement d'une tentative pour un exercice inexistant (ID {exercise_id})")
            return None
        
        # Préparer les valeurs avec des valeurs par défaut
        user_id = attempt_data.get("user_id")
        user_answer = attempt_data.get("user_answer") or attempt_data.get("answer") or ""
        is_correct = attempt_data.get("is_correct", False)
        time_spent = attempt_data.get("time_spent")
        hints_used = attempt_data.get("hints_used", 0)
        device_info = attempt_data.get("device_info")
        
        # Calculer le numéro de tentative si non fourni
        attempt_number = attempt_data.get("attempt_number")
        if not attempt_number:
            cursor.execute(
                "SELECT COALESCE(MAX(attempt_number), 0) + 1 as next_number FROM attempts WHERE user_id = %s AND exercise_id = %s",
                (user_id, exercise_id)
            )
            result = cursor.fetchone()
            if result:
                attempt_number = result['next_number']
            else:
                attempt_number = 1
        
        # Insérer la tentative
        insert_query = """
            INSERT INTO attempts (
                user_id, exercise_id, user_answer, is_correct, 
                time_spent, attempt_number, hints_used, device_info, created_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP
            ) RETURNING id, user_id, exercise_id, user_answer, is_correct, 
                       time_spent, attempt_number, hints_used, device_info, created_at
        """
        
        cursor.execute(
            insert_query,
            (
                user_id,
                exercise_id,
                user_answer,
                is_correct,
                time_spent,
                attempt_number,
                hints_used,
                device_info
            )
        )
        
        row = cursor.fetchone()
        conn.commit()
        
        if not row:
            logger.error("La tentative n'a pas été créée")
            return None
        
        attempt = dict(row)
        
        # Formater les dates en ISO format strings pour sérialisation JSON
        attempt['created_at'] = format_date_for_json(attempt.get('created_at'))
        
        logger.info(f"Tentative créée avec ID: {attempt['id']}")
        return attempt
    
    except Exception as e:
        conn.rollback()
        error_type = type(e).__name__
        error_msg = str(e)
        logger.error(f"❌ ERREUR lors de la création de la tentative: {error_type}: {error_msg}")
        import traceback
        logger.error(f"Traceback complet:\n{traceback.format_exc()}")
        return None
    finally:
        cursor.close()
        conn.close()


def create_challenge_attempt_with_postgres(attempt_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Crée une tentative de challenge avec PostgreSQL direct.
    
    Args:
        attempt_data: Dictionnaire contenant les données de la tentative
            - user_id: int (requis)
            - challenge_id: int (requis)
            - user_solution: str (requis)
            - is_correct: bool (requis)
            - time_spent: float (optionnel)
            - hints_used: list ou int (optionnel, défaut: 0 ou [])
    
    Returns:
        Dictionnaire avec les données de la tentative créée ou None
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Vérifier que le challenge existe
        challenge_id = attempt_data.get("challenge_id")
        if not challenge_id:
            logger.error("challenge_id manquant dans attempt_data")
            return None
        
        check_query = "SELECT id FROM logic_challenges WHERE id = %s"
        cursor.execute(check_query, (challenge_id,))
        if not cursor.fetchone():
            logger.error(f"Challenge avec ID {challenge_id} introuvable")
            return None
        
        # Récupérer les données
        user_id = attempt_data.get("user_id")
        user_solution = attempt_data.get("user_solution") or attempt_data.get("answer", "")
        is_correct = attempt_data.get("is_correct", False)
        time_spent = attempt_data.get("time_spent")
        hints_used = attempt_data.get("hints_used", [])
        
        # Convertir hints_used en format compatible avec le schéma réel
        # Le schéma a : hint_level1_used, hint_level2_used, hint_level3_used (BOOLEAN)
        # et hints_used (INTEGER) pour le nombre total d'indices utilisés
        hint_level1_used = False
        hint_level2_used = False
        hint_level3_used = False
        hints_used_count = 0
        
        if isinstance(hints_used, list):
            # Si c'est une liste, déterminer quels niveaux ont été utilisés
            hints_used_count = len(hints_used)
            if hints_used_count >= 1:
                hint_level1_used = True
            if hints_used_count >= 2:
                hint_level2_used = True
            if hints_used_count >= 3:
                hint_level3_used = True
        elif isinstance(hints_used, int):
            # Si c'est un entier, c'est le nombre d'indices utilisés
            hints_used_count = hints_used
            if hints_used_count >= 1:
                hint_level1_used = True
            if hints_used_count >= 2:
                hint_level2_used = True
            if hints_used_count >= 3:
                hint_level3_used = True
        
        if not user_id:
            logger.error("user_id manquant dans attempt_data")
            return None
        
        if not user_solution:
            logger.error("user_solution manquant dans attempt_data")
            return None
        
        # Insérer la tentative dans logic_challenge_attempts
        # Le schéma réel a : user_solution, hint_level1_used, hint_level2_used, hint_level3_used, hints_used (INTEGER)
        insert_query = """
            INSERT INTO logic_challenge_attempts (
                user_id, challenge_id, user_solution, is_correct, 
                time_spent, hint_level1_used, hint_level2_used, hint_level3_used, hints_used, created_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP
            ) RETURNING id, user_id, challenge_id, user_solution, is_correct, 
                       time_spent, hint_level1_used, hint_level2_used, hint_level3_used, hints_used, created_at
        """
        
        cursor.execute(
            insert_query,
            (
                user_id,
                challenge_id,
                user_solution,
                is_correct,
                time_spent,
                hint_level1_used,
                hint_level2_used,
                hint_level3_used,
                hints_used_count,
            )
        )
        
        row = cursor.fetchone()
        conn.commit()
        
        if not row:
            logger.error("La tentative de challenge n'a pas été créée")
            return None
        
        attempt = dict(row)
        
        # Formater les dates en ISO format strings pour sérialisation JSON
        attempt['created_at'] = format_date_for_json(attempt.get('created_at'))
        
        # Reconstruire hints_used comme liste pour compatibilité avec le frontend
        hints_list = []
        if attempt.get('hint_level1_used'):
            hints_list.append(0)
        if attempt.get('hint_level2_used'):
            hints_list.append(1)
        if attempt.get('hint_level3_used'):
            hints_list.append(2)
        attempt['hints_used'] = hints_list
        
        logger.info(f"✅ Tentative de challenge créée avec ID: {attempt['id']}, challenge_id: {challenge_id}, user_id: {user_id}, is_correct: {is_correct}")
        logger.debug(f"Détails de la tentative: {attempt}")
        return attempt
    
    except Exception as e:
        conn.rollback()
        error_type = type(e).__name__
        error_msg = str(e)
        logger.error(f"❌ ERREUR lors de la création de la tentative de challenge: {error_type}: {error_msg}")
        import traceback
        logger.error(f"Traceback complet:\n{traceback.format_exc()}")
        return None
    finally:
        cursor.close()
        conn.close()

