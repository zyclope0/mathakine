"""
Script pour ajouter des traductions anglaises de test aux badges.
"""
import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

import psycopg2
import json
from server.database import get_database_url
from loguru import logger


def add_english_translations_to_badges(badge_ids: list[int]):
    """
    Ajoute des traductions anglaises de test à des badges spécifiques.
    """
    database_url = get_database_url()
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    try:
        logger.info("Ajout de traductions anglaises de test aux badges...")
        updated_count = 0
        
        for badge_id in badge_ids:
            # Récupérer les traductions actuelles
            cursor.execute("""
                SELECT name_translations, description_translations, star_wars_title_translations 
                FROM achievements 
                WHERE id = %s
            """, (badge_id,))
            row = cursor.fetchone()
            
            if row:
                name_trans = row[0] if row[0] else {}
                description_trans = row[1] if row[1] else {}
                star_wars_title_trans = row[2] if row[2] else {}
                
                # Assurez-vous que les valeurs sont des dictionnaires
                if isinstance(name_trans, str):
                    name_trans = json.loads(name_trans)
                if isinstance(description_trans, str):
                    description_trans = json.loads(description_trans)
                if isinstance(star_wars_title_trans, str):
                    star_wars_title_trans = json.loads(star_wars_title_trans)

                # Ajouter les traductions anglaises de test
                updates = []
                params = []
                
                if 'fr' in name_trans and name_trans['fr']:
                    name_trans['en'] = f"[EN] {name_trans['fr']}"
                    updates.append("name_translations = %s")
                    params.append(json.dumps(name_trans))
                
                if 'fr' in description_trans and description_trans['fr']:
                    description_trans['en'] = f"[EN] {description_trans['fr']}"
                    updates.append("description_translations = %s")
                    params.append(json.dumps(description_trans))
                
                if 'fr' in star_wars_title_trans and star_wars_title_trans['fr']:
                    star_wars_title_trans['en'] = f"[EN] {star_wars_title_trans['fr']}"
                    updates.append("star_wars_title_translations = %s")
                    params.append(json.dumps(star_wars_title_trans))
                
                if updates:
                    query = f"UPDATE achievements SET {', '.join(updates)} WHERE id = %s"
                    params.append(badge_id)
                    cursor.execute(query, tuple(params))
                    logger.info(f"✅ Badge {badge_id} mis à jour avec traductions anglaises")
                    updated_count += 1
                else:
                    logger.warning(f"⚠️ Badge {badge_id} : aucune traduction française trouvée")
            else:
                logger.warning(f"⚠️ Badge {badge_id} non trouvé, impossible d'ajouter des traductions.")
        
        conn.commit()
        logger.success(f"✅ {updated_count} badges mis à jour avec traductions anglaises de test")
    
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Erreur lors de l'ajout des traductions anglaises: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()


def main():
    # Récupérer les IDs des premiers badges disponibles
    database_url = get_database_url()
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    try:
        # Récupérer les 2 premiers badges actifs
        cursor.execute("""
            SELECT id FROM achievements 
            WHERE is_active = true 
            ORDER BY id ASC 
            LIMIT 2
        """)
        badge_ids = [row[0] for row in cursor.fetchall()]
        
        if not badge_ids:
            logger.warning("⚠️ Aucun badge trouvé dans la base de données")
            return
        
        logger.info(f"📋 Badges sélectionnés pour traduction: {badge_ids}")
        add_english_translations_to_badges(badge_ids)
    
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()

