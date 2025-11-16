"""
Script pour migrer les données existantes vers le système de traductions.
Utilise psycopg2 directement avec PostgreSQL.

Usage:
    python scripts/migrations/migrate_to_translations.py
"""
import sys
import os
import json
from pathlib import Path

# Ajouter le répertoire racine au path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

import psycopg2
from psycopg2.extras import RealDictCursor
from server.database import get_db_connection
from loguru import logger


def migrate_exercises():
    """Migre les exercices vers le système de traductions"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Vérifier que les colonnes existent
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'exercises' 
            AND column_name LIKE '%_translations'
        """)
        existing_columns = [row['column_name'] for row in cursor.fetchall()]
        
        if not existing_columns:
            logger.error("Les colonnes de traduction n'existent pas. Exécutez d'abord la migration SQL.")
            return False
        
        # Récupérer tous les exercices
        cursor.execute("""
            SELECT id, title, question, explanation, hint, choices 
            FROM exercises
        """)
        exercises = cursor.fetchall()
        
        migrated = 0
        
        for exercise in exercises:
            exercise_id = exercise['id']
            updates = []
            params = []
            
            # Vérifier et migrer title_translations
            cursor.execute(
                "SELECT title_translations FROM exercises WHERE id = %s",
                (exercise_id,)
            )
            row = cursor.fetchone()
            title_translations = row['title_translations'] if row else None
            
            if not title_translations or title_translations == {} or title_translations.get('fr') is None:
                updates.append("title_translations = %s")
                params.append(json.dumps({"fr": exercise['title']}))
            
            # Migrer question_translations
            cursor.execute(
                "SELECT question_translations FROM exercises WHERE id = %s",
                (exercise_id,)
            )
            row = cursor.fetchone()
            question_translations = row['question_translations'] if row else None
            
            if not question_translations or question_translations == {} or question_translations.get('fr') is None:
                updates.append("question_translations = %s")
                params.append(json.dumps({"fr": exercise['question']}))
            
            # Migrer explanation_translations
            if exercise.get('explanation'):
                cursor.execute(
                    "SELECT explanation_translations FROM exercises WHERE id = %s",
                    (exercise_id,)
                )
                row = cursor.fetchone()
                explanation_translations = row['explanation_translations'] if row else None
                
                if not explanation_translations or explanation_translations == {} or explanation_translations.get('fr') is None:
                    updates.append("explanation_translations = %s")
                    params.append(json.dumps({"fr": exercise['explanation']}))
            
            # Migrer hint_translations
            if exercise.get('hint'):
                cursor.execute(
                    "SELECT hint_translations FROM exercises WHERE id = %s",
                    (exercise_id,)
                )
                row = cursor.fetchone()
                hint_translations = row['hint_translations'] if row else None
                
                if not hint_translations or hint_translations == {} or hint_translations.get('fr') is None:
                    updates.append("hint_translations = %s")
                    params.append(json.dumps({"fr": exercise['hint']}))
            
            # Migrer choices_translations
            if exercise.get('choices'):
                cursor.execute(
                    "SELECT choices_translations FROM exercises WHERE id = %s",
                    (exercise_id,)
                )
                row = cursor.fetchone()
                choices_translations = row['choices_translations'] if row else None
                
                if not choices_translations or choices_translations == {} or choices_translations.get('fr') is None:
                    # Parser choices si c'est une string JSON
                    choices = exercise['choices']
                    if isinstance(choices, str):
                        try:
                            choices = json.loads(choices)
                        except:
                            choices = [choices]
                    
                    updates.append("choices_translations = %s")
                    params.append(json.dumps({"fr": choices}))
            
            # Exécuter la mise à jour si nécessaire
            if updates:
                query = f"UPDATE exercises SET {', '.join(updates)} WHERE id = %s"
                params.append(exercise_id)
                cursor.execute(query, tuple(params))
                migrated += 1
        
        conn.commit()
        logger.success(f"✅ Migré {migrated} exercices sur {len(exercises)}")
        return True
    
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Erreur lors de la migration des exercices: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        cursor.close()
        conn.close()


def migrate_challenges():
    """Migre les défis logiques vers le système de traductions"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Vérifier que les colonnes existent
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'logic_challenges' 
            AND column_name LIKE '%_translations'
        """)
        existing_columns = [row['column_name'] for row in cursor.fetchall()]
        
        if not existing_columns:
            logger.warning("Les colonnes de traduction n'existent pas pour logic_challenges. Ignoré.")
            return False
        
        # Récupérer tous les défis
        cursor.execute("""
            SELECT id, title, description, question, solution_explanation, hints 
            FROM logic_challenges
        """)
        challenges = cursor.fetchall()
        
        migrated = 0
        
        for challenge in challenges:
            challenge_id = challenge['id']
            updates = []
            params = []
            
            # Migrer title_translations
            cursor.execute(
                "SELECT title_translations FROM logic_challenges WHERE id = %s",
                (challenge_id,)
            )
            row = cursor.fetchone()
            title_translations = row['title_translations'] if row else None
            
            if not title_translations or title_translations == {} or title_translations.get('fr') is None:
                updates.append("title_translations = %s")
                params.append(json.dumps({"fr": challenge['title']}))
            
            # Migrer description_translations
            cursor.execute(
                "SELECT description_translations FROM logic_challenges WHERE id = %s",
                (challenge_id,)
            )
            row = cursor.fetchone()
            description_translations = row['description_translations'] if row else None
            
            if not description_translations or description_translations == {} or description_translations.get('fr') is None:
                updates.append("description_translations = %s")
                params.append(json.dumps({"fr": challenge['description']}))
            
            # Migrer question_translations
            if challenge.get('question'):
                cursor.execute(
                    "SELECT question_translations FROM logic_challenges WHERE id = %s",
                    (challenge_id,)
                )
                row = cursor.fetchone()
                question_translations = row['question_translations'] if row else None
                
                if not question_translations or question_translations == {} or question_translations.get('fr') is None:
                    updates.append("question_translations = %s")
                    params.append(json.dumps({"fr": challenge['question']}))
            
            # Migrer solution_explanation_translations
            if challenge.get('solution_explanation'):
                cursor.execute(
                    "SELECT solution_explanation_translations FROM logic_challenges WHERE id = %s",
                    (challenge_id,)
                )
                row = cursor.fetchone()
                solution_translations = row['solution_explanation_translations'] if row else None
                
                if not solution_translations or solution_translations == {} or solution_translations.get('fr') is None:
                    updates.append("solution_explanation_translations = %s")
                    params.append(json.dumps({"fr": challenge['solution_explanation']}))
            
            # Migrer hints_translations
            if challenge.get('hints'):
                cursor.execute(
                    "SELECT hints_translations FROM logic_challenges WHERE id = %s",
                    (challenge_id,)
                )
                row = cursor.fetchone()
                hints_translations = row['hints_translations'] if row else None
                
                if not hints_translations or hints_translations == {} or hints_translations.get('fr') is None:
                    hints = challenge['hints']
                    if isinstance(hints, str):
                        try:
                            hints = json.loads(hints)
                        except:
                            hints = [hints]
                    
                    updates.append("hints_translations = %s")
                    params.append(json.dumps({"fr": hints}))
            
            # Exécuter la mise à jour si nécessaire
            if updates:
                query = f"UPDATE logic_challenges SET {', '.join(updates)} WHERE id = %s"
                params.append(challenge_id)
                cursor.execute(query, tuple(params))
                migrated += 1
        
        conn.commit()
        logger.success(f"✅ Migré {migrated} défis sur {len(challenges)}")
        return True
    
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Erreur lors de la migration des défis: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        cursor.close()
        conn.close()


def migrate_achievements():
    """Migre les badges vers le système de traductions"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Vérifier que les colonnes existent
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'achievements' 
            AND column_name LIKE '%_translations'
        """)
        existing_columns = [row['column_name'] for row in cursor.fetchall()]
        
        if not existing_columns:
            logger.warning("Les colonnes de traduction n'existent pas pour achievements. Ignoré.")
            return False
        
        # Récupérer tous les badges
        cursor.execute("""
            SELECT id, name, description, star_wars_title 
            FROM achievements
        """)
        achievements = cursor.fetchall()
        
        migrated = 0
        
        for achievement in achievements:
            achievement_id = achievement['id']
            updates = []
            params = []
            
            # Migrer name_translations
            cursor.execute(
                "SELECT name_translations FROM achievements WHERE id = %s",
                (achievement_id,)
            )
            row = cursor.fetchone()
            name_translations = row['name_translations'] if row else None
            
            if not name_translations or name_translations == {} or name_translations.get('fr') is None:
                updates.append("name_translations = %s")
                params.append(json.dumps({"fr": achievement['name']}))
            
            # Migrer description_translations
            if achievement.get('description'):
                cursor.execute(
                    "SELECT description_translations FROM achievements WHERE id = %s",
                    (achievement_id,)
                )
                row = cursor.fetchone()
                description_translations = row['description_translations'] if row else None
                
                if not description_translations or description_translations == {} or description_translations.get('fr') is None:
                    updates.append("description_translations = %s")
                    params.append(json.dumps({"fr": achievement['description']}))
            
            # Migrer star_wars_title_translations
            if achievement.get('star_wars_title'):
                cursor.execute(
                    "SELECT star_wars_title_translations FROM achievements WHERE id = %s",
                    (achievement_id,)
                )
                row = cursor.fetchone()
                star_wars_translations = row['star_wars_title_translations'] if row else None
                
                if not star_wars_translations or star_wars_translations == {} or star_wars_translations.get('fr') is None:
                    updates.append("star_wars_title_translations = %s")
                    params.append(json.dumps({"fr": achievement['star_wars_title']}))
            
            # Exécuter la mise à jour si nécessaire
            if updates:
                query = f"UPDATE achievements SET {', '.join(updates)} WHERE id = %s"
                params.append(achievement_id)
                cursor.execute(query, tuple(params))
                migrated += 1
        
        conn.commit()
        logger.success(f"✅ Migré {migrated} badges sur {len(achievements)}")
        return True
    
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Erreur lors de la migration des badges: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        cursor.close()
        conn.close()


def main():
    """Fonction principale pour exécuter toutes les migrations"""
    logger.info("🚀 Démarrage de la migration vers le système de traductions...")
    
    # Exécuter les migrations dans l'ordre
    success_exercises = migrate_exercises()
    success_challenges = migrate_challenges()
    success_achievements = migrate_achievements()
    
    if success_exercises and success_challenges and success_achievements:
        logger.success("✅ Migration complète réussie !")
        return 0
    else:
        logger.error("❌ Certaines migrations ont échoué")
        return 1


if __name__ == "__main__":
    sys.exit(main())

