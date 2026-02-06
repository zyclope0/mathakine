"""
Script pour exécuter la migration SQL des colonnes de traduction.
Utilise psycopg2 pour exécuter directement le fichier SQL.
"""
import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

import psycopg2
from loguru import logger
from server.database import get_database_url

def run_sql_migration():
    """Exécute la migration SQL depuis le fichier"""
    migration_file = Path(__file__).parent / "add_translation_columns.sql"
    
    if not migration_file.exists():
        logger.error(f"Fichier de migration non trouvé: {migration_file}")
        return False
    
    try:
        # Lire le fichier SQL
        with open(migration_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Se connecter à la base de données
        db_url = get_database_url()
        logger.info(f"Connexion à la base de données: {db_url.split('@')[1] if '@' in db_url else '***'}")
        
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        try:
            # Exécuter le script SQL
            logger.info("Exécution de la migration SQL...")
            cursor.execute(sql_content)
            
            # Vérifier que les colonnes ont été créées
            logger.info("Vérification des colonnes créées...")
            
            # Vérifier exercises
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'exercises' 
                AND column_name LIKE '%_translations'
            """)
            exercise_cols = [row[0] for row in cursor.fetchall()]
            logger.success(f"✅ Colonnes exercises: {', '.join(exercise_cols) if exercise_cols else 'Aucune'}")
            
            # Vérifier logic_challenges
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'logic_challenges' 
                AND column_name LIKE '%_translations'
            """)
            challenge_cols = [row[0] for row in cursor.fetchall()]
            logger.success(f"✅ Colonnes logic_challenges: {', '.join(challenge_cols) if challenge_cols else 'Aucune'}")
            
            # Vérifier achievements
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'achievements' 
                AND column_name LIKE '%_translations'
            """)
            achievement_cols = [row[0] for row in cursor.fetchall()]
            logger.success(f"✅ Colonnes achievements: {', '.join(achievement_cols) if achievement_cols else 'Aucune'}")
            
            # Compter les exercices migrés
            cursor.execute("SELECT COUNT(*) FROM exercises WHERE title_translations IS NOT NULL")
            exercise_count = cursor.fetchone()[0]
            logger.info(f"📊 {exercise_count} exercices avec traductions")
            
            logger.success("✅ Migration SQL terminée avec succès!")
            return True
            
        finally:
            cursor.close()
            conn.close()
    
    except Exception as e:
        logger.error(f"❌ Erreur lors de la migration SQL: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_sql_migration()
    sys.exit(0 if success else 1)

