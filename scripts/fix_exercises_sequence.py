#!/usr/bin/env python
"""
Script pour réparer la séquence d'auto-incrément de la table exercises

Ce script corrige spécifiquement la séquence d'auto-incrément de la table exercises
qui cause l'erreur "null value in column \"id\" of relation \"exercises\" violates not-null constraint"
"""

import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)



def fix_exercises_sequence():
    """
    Réinitialise la séquence d'auto-incrément de la table exercises.
    """
    try:
        if not settings.DATABASE_URL.startswith('postgresql'):
            logger.warning("Cette opération n'est nécessaire que pour PostgreSQL")
            return

        connection_string = settings.DATABASE_URL
        logger.info(f"Connexion à la base de données: {connection_string.split('@')[-1]}")

        conn = psycopg2.connect(connection_string)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Récupérer tous les IDs existants dans la table exercises
        cursor.execute("SELECT COUNT(*) FROM exercises")
        count = cursor.fetchone()[0]
        logger.info(f"Nombre d'exercices trouvés: {count}")

        # Trouver la valeur maximale de l'ID
        cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM exercises")
        max_id = cursor.fetchone()[0]
        logger.info(f"Valeur maximale d'ID trouvée: {max_id - 1}")

        # Trouver le nom exact de la séquence
        cursor.execute("""
            SELECT pg_get_serial_sequence('exercises', 'id')
        """)
        sequence_name = cursor.fetchone()[0]

        if not sequence_name:
            logger.warning("Aucune séquence trouvée pour la colonne id de la table exercises")

            # Créer une nouvelle séquence si elle n'existe pas
            logger.info("Création d'une nouvelle séquence...")
            cursor.execute(f"""
                CREATE SEQUENCE IF NOT EXISTS exercises_id_seq
                START WITH {max_id}
                OWNED BY exercises.id
            """)

            # Associer la séquence à la colonne id
            cursor.execute("""
                ALTER TABLE exercises
                ALTER COLUMN id
                SET DEFAULT nextval('exercises_id_seq')
            """)

            sequence_name = 'exercises_id_seq'
            logger.success(f"Nouvelle séquence créée et associée: {sequence_name}")
        else:
            logger.info(f"Séquence trouvée: {sequence_name}")

        # Réinitialiser la séquence
        cursor.execute(f"ALTER SEQUENCE {sequence_name} RESTART WITH %s", (max_id,))
        logger.success(f"Séquence {sequence_name} réinitialisée à {max_id}")

        # Vérifier que la séquence fonctionne
        cursor.execute(f"SELECT nextval('{sequence_name}')")
        next_val = cursor.fetchone()[0]
        logger.info(f"Prochain ID qui sera utilisé: {next_val}")

        # Réinitialiser la séquence à nouveau (moins 1 car nous venons de consommer une valeur)
        cursor.execute(f"ALTER SEQUENCE {sequence_name} RESTART WITH %s", (max_id,))

        cursor.close()
        conn.close()
        logger.success("Séquence de la table exercises réparée avec succès")

    except Exception as e:
        logger.error(f"Erreur lors de la réparation de la séquence: {str(e)}")
        raise

if __name__ == "__main__":
    logger.info("Démarrage de la réparation de la séquence pour la table exercises")
    fix_exercises_sequence()
    logger.info("Terminé")
