"""
Script pour ajouter des traductions anglaises de test à quelques exercices.
"""
import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

import psycopg2
import json
from server.database import get_database_url
from loguru import logger

def add_english_translations():
    """Ajoute des traductions anglaises de test à quelques exercices"""
    conn = psycopg2.connect(get_database_url())
    conn.autocommit = True
    cursor = conn.cursor()
    
    try:
        # Récupérer quelques exercices
        cursor.execute("""
            SELECT id, title, question, explanation, hint, choices 
            FROM exercises 
            WHERE is_archived = false 
            LIMIT 5
        """)
        exercises = cursor.fetchall()
        
        updated = 0
        
        for exercise_id, title, question, explanation, hint, choices in exercises:
            # Créer des traductions anglaises de test
            title_en = f"[EN] {title}" if title else None
            question_en = f"[EN] {question}" if question else None
            explanation_en = f"[EN] {explanation}" if explanation else None
            hint_en = f"[EN] {hint}" if hint else None
            
            # Pour choices, créer une traduction anglaise simple
            choices_en = None
            if choices:
                try:
                    if isinstance(choices, str):
                        choices_list = json.loads(choices)
                    else:
                        choices_list = choices
                    
                    if isinstance(choices_list, list):
                        choices_en = [f"[EN] {choice}" for choice in choices_list]
                except:
                    pass
            
            # Mettre à jour les traductions
            updates = []
            params = []
            
            if title_en:
                cursor.execute("""
                    SELECT title_translations FROM exercises WHERE id = %s
                """, (exercise_id,))
                row = cursor.fetchone()
                current_translations = row[0] if row else {}
                
                if isinstance(current_translations, str):
                    current_translations = json.loads(current_translations)
                
                current_translations['en'] = title_en
                updates.append("title_translations = %s")
                params.append(json.dumps(current_translations))
            
            if question_en:
                cursor.execute("""
                    SELECT question_translations FROM exercises WHERE id = %s
                """, (exercise_id,))
                row = cursor.fetchone()
                current_translations = row[0] if row else {}
                
                if isinstance(current_translations, str):
                    current_translations = json.loads(current_translations)
                
                current_translations['en'] = question_en
                updates.append("question_translations = %s")
                params.append(json.dumps(current_translations))
            
            if explanation_en:
                cursor.execute("""
                    SELECT explanation_translations FROM exercises WHERE id = %s
                """, (exercise_id,))
                row = cursor.fetchone()
                current_translations = row[0] if row else {}
                
                if isinstance(current_translations, str):
                    current_translations = json.loads(current_translations)
                
                current_translations['en'] = explanation_en
                updates.append("explanation_translations = %s")
                params.append(json.dumps(current_translations))
            
            if hint_en:
                cursor.execute("""
                    SELECT hint_translations FROM exercises WHERE id = %s
                """, (exercise_id,))
                row = cursor.fetchone()
                current_translations = row[0] if row else {}
                
                if isinstance(current_translations, str):
                    current_translations = json.loads(current_translations)
                
                current_translations['en'] = hint_en
                updates.append("hint_translations = %s")
                params.append(json.dumps(current_translations))
            
            if choices_en:
                cursor.execute("""
                    SELECT choices_translations FROM exercises WHERE id = %s
                """, (exercise_id,))
                row = cursor.fetchone()
                current_translations = row[0] if row else {}
                
                if isinstance(current_translations, str):
                    current_translations = json.loads(current_translations)
                
                current_translations['en'] = choices_en
                updates.append("choices_translations = %s")
                params.append(json.dumps(current_translations))
            
            # Exécuter la mise à jour
            if updates:
                query = f"UPDATE exercises SET {', '.join(updates)} WHERE id = %s"
                params.append(exercise_id)
                cursor.execute(query, tuple(params))
                updated += 1
                logger.info(f"✅ Exercice {exercise_id} mis à jour avec traductions anglaises")
        
        logger.success(f"✅ {updated} exercices mis à jour avec traductions anglaises de test")
        return True
    
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    logger.info("🚀 Ajout de traductions anglaises de test...")
    success = add_english_translations()
    sys.exit(0 if success else 1)

