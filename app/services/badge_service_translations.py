"""
Service pour les badges avec support des traductions (PostgreSQL pur).

Utilise psycopg2 directement avec des requêtes SQL brutes.
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, Dict, Any, List
from datetime import datetime
from loguru import logger

from server.database import get_db_connection
from app.db.queries_translations import AchievementQueriesWithTranslations


def get_achievement(achievement_id: int, locale: str = "fr") -> Optional[Dict[str, Any]]:
    """
    Récupère un badge par ID avec traductions.
    
    Args:
        achievement_id: ID du badge
        locale: Locale demandée (fr, en, etc.)
    
    Returns:
        Dictionnaire avec les données du badge traduites ou None
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        query, base_params = AchievementQueriesWithTranslations.get_by_id(locale)
        # Ajouter l'achievement_id à la fin des paramètres
        params = base_params + (achievement_id,)
        
        cursor.execute(query, params)
        row = cursor.fetchone()
        
        if not row:
            return None
        
        achievement = dict(row)
        
        # Convertir les dates datetime en strings ISO
        if achievement.get('created_at'):
            if isinstance(achievement['created_at'], datetime):
                achievement['created_at'] = achievement['created_at'].isoformat()
            elif hasattr(achievement['created_at'], 'isoformat'):
                achievement['created_at'] = achievement['created_at'].isoformat()
        
        # Parser requirements si nécessaire
        if achievement.get('requirements'):
            if isinstance(achievement['requirements'], str):
                import json
                try:
                    achievement['requirements'] = json.loads(achievement['requirements'])
                except:
                    pass
        
        return achievement
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du badge {achievement_id}: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


def list_achievements(locale: str = "fr") -> List[Dict[str, Any]]:
    """
    Liste tous les badges avec traductions.
    
    Args:
        locale: Locale demandée
    
    Returns:
        Liste de dictionnaires avec les données des badges traduites
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        query, params = AchievementQueriesWithTranslations.list_all(locale)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        achievements = []
        for row in rows:
            achievement = dict(row)
            
            # Convertir les dates datetime en strings ISO
            if achievement.get('created_at'):
                if isinstance(achievement['created_at'], datetime):
                    achievement['created_at'] = achievement['created_at'].isoformat()
                elif hasattr(achievement['created_at'], 'isoformat'):
                    achievement['created_at'] = achievement['created_at'].isoformat()
            
            # Parser requirements si nécessaire
            if achievement.get('requirements'):
                if isinstance(achievement['requirements'], str):
                    import json
                    try:
                        achievement['requirements'] = json.loads(achievement['requirements'])
                    except:
                        pass
            
            achievements.append(achievement)
        
        return achievements
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des badges: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

