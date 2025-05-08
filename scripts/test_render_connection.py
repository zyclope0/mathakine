"""
Script pour tester la connexion à la base de données PostgreSQL sur Render
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv
from loguru import logger

# Configuration du logger
logger.remove()
logger.add(sys.stderr, level="DEBUG")

# Charger les variables d'environnement
load_dotenv()

def test_render_connection():
    """Teste la connexion à la base de données PostgreSQL sur Render"""
    # Récupérer l'URL de connexion à la base de données
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        logger.error("La variable d'environnement DATABASE_URL n'est pas définie")
        return False
    
    logger.info(f"Test de connexion à PostgreSQL: {database_url.split('@')[1]}")
    
    try:
        # Connexion à PostgreSQL
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Vérifier la connexion
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        logger.success(f"Connexion à PostgreSQL réussie. Version: {version[0]}")
        
        # Vérifier les tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        logger.info(f"Tables présentes dans la base de données ({len(tables)}):")
        
        for i, table in enumerate(tables, 1):
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            logger.info(f"  {i}. {table[0]} - {count} enregistrements")
        
        conn.close()
        return True
    
    except Exception as e:
        logger.error(f"Erreur de connexion à PostgreSQL: {e}")
        return False


if __name__ == "__main__":
    result = test_render_connection()
    sys.exit(0 if result else 1) 