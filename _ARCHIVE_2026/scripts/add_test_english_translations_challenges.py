"""
Script pour ajouter des traductions anglaises de test aux défis logiques.
"""
import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

import psycopg2
import json
from server.database import get_database_url
from loguru import logger


def add_english_translations_to_challenges(challenge_ids: list[int]):
    """
    Ajoute des traductions anglaises de test à des défis spécifiques.
    """
    database_url = get_database_url()
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    try:
        logger.info("Ajout de traductions anglaises de test aux défis logiques...")
        updated_count = 0
        
        for challenge_id in challenge_ids:
            # Récupérer les traductions actuelles
            cursor.execute("""
                SELECT title_translations, description_translations, question_translations, 
                       solution_explanation_translations, hints_translations 
                FROM logic_challenges 
                WHERE id = %s
            """, (challenge_id,))
            row = cursor.fetchone()
            
            if row:
                title_trans = row[0] if row[0] else {}
                description_trans = row[1] if row[1] else {}
                question_trans = row[2] if row[2] else {}
                solution_explanation_trans = row[3] if row[3] else {}
                hints_trans = row[4] if row[4] else {}
                
                # Assurez-vous que les valeurs sont des dictionnaires
                if isinstance(title_trans, str):
                    title_trans = json.loads(title_trans)
                if isinstance(description_trans, str):
                    description_trans = json.loads(description_trans)
                if isinstance(question_trans, str):
                    question_trans = json.loads(question_trans)
                if isinstance(solution_explanation_trans, str):
                    solution_explanation_trans = json.loads(solution_explanation_trans)
                if isinstance(hints_trans, str):
                    hints_trans = json.loads(hints_trans)

                # Ajouter les traductions anglaises de test
                updates = []
                params = []
                
                if 'fr' in title_trans and title_trans['fr']:
                    title_trans['en'] = f"[EN] {title_trans['fr']}"
                    updates.append("title_translations = %s")
                    params.append(json.dumps(title_trans))
                
                if 'fr' in description_trans and description_trans['fr']:
                    description_trans['en'] = f"[EN] {description_trans['fr']}"
                    updates.append("description_translations = %s")
                    params.append(json.dumps(description_trans))
                
                if 'fr' in question_trans and question_trans['fr']:
                    question_trans['en'] = f"[EN] {question_trans['fr']}"
                    updates.append("question_translations = %s")
                    params.append(json.dumps(question_trans))
                
                if 'fr' in solution_explanation_trans and solution_explanation_trans['fr']:
                    solution_explanation_trans['en'] = f"[EN] {solution_explanation_trans['fr']}"
                    updates.append("solution_explanation_translations = %s")
                    params.append(json.dumps(solution_explanation_trans))
                
                # Pour hints, c'est un array JSONB
                if hints_trans and isinstance(hints_trans, dict) and 'fr' in hints_trans:
                    hints_fr = hints_trans['fr']
                    if isinstance(hints_fr, list):
                        hints_en = [f"[EN] {hint}" for hint in hints_fr]
                        hints_trans['en'] = hints_en
                        updates.append("hints_translations = %s")
                        params.append(json.dumps(hints_trans))
                
                if updates:
                    query = f"UPDATE logic_challenges SET {', '.join(updates)} WHERE id = %s"
                    params.append(challenge_id)
                    cursor.execute(query, tuple(params))
                    logger.info(f"✅ Défi {challenge_id} mis à jour avec traductions anglaises")
                    updated_count += 1
                else:
                    logger.warning(f"⚠️ Défi {challenge_id} : aucune traduction française trouvée")
            else:
                logger.warning(f"⚠️ Défi {challenge_id} non trouvé, impossible d'ajouter des traductions.")
        
        conn.commit()
        logger.success(f"✅ {updated_count} défis mis à jour avec traductions anglaises de test")
    
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Erreur lors de l'ajout des traductions anglaises: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()


def main():
    # Récupérer les IDs des premiers défis disponibles
    database_url = get_database_url()
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    try:
        # Récupérer les 2 premiers défis actifs
        cursor.execute("""
            SELECT id FROM logic_challenges 
            WHERE is_archived = false 
            ORDER BY id ASC 
            LIMIT 2
        """)
        challenge_ids = [row[0] for row in cursor.fetchall()]
        
        if not challenge_ids:
            logger.warning("⚠️ Aucun défi trouvé dans la base de données")
            return
        
        logger.info(f"📋 Défis sélectionnés pour traduction: {challenge_ids}")
        add_english_translations_to_challenges(challenge_ids)
    
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()

