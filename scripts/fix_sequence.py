#!/usr/bin/env python
"""
Script pour réparer les séquences d'auto-incrément PostgreSQL

Ce script corrige les séquences d'auto-incrément des tables PostgreSQL
qui peuvent être désynchronisées, causant des erreurs d'insertion.
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)



def reset_sequences():
    """
    Réinitialise toutes les séquences d'auto-incrément pour correspondre
    à la valeur maximale actuelle des IDs dans chaque table.
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

        # Récupérer toutes les tables avec une colonne id en primary key
        cursor.execute("""
            SELECT
                t.table_name
            FROM
                information_schema.tables t
            JOIN
                information_schema.columns c ON t.table_name = c.table_name
            WHERE
                t.table_schema = 'public' AND
                c.column_name = 'id'
        """)

        tables = cursor.fetchall()

        for table in tables:
            table_name = table[0]
            seq_name = f"{table_name}_id_seq"

            # Vérifier si la séquence existe
            cursor.execute("""
                SELECT EXISTS(
                    SELECT 1 FROM pg_sequences WHERE schemaname = 'public' AND sequencename = %s
                )
            """, (seq_name,))

            seq_exists = cursor.fetchone()[0]

            if seq_exists:
                logger.info(f"Réinitialisation de la séquence pour la table {table_name}")

                # Trouver la valeur maximale de l'ID dans la table
                cursor.execute(f"SELECT COALESCE(MAX(id), 0) + 1 FROM {table_name}")
                max_id = cursor.fetchone()[0]

                # Réinitialiser la séquence
                cursor.execute(f"ALTER SEQUENCE {seq_name} RESTART WITH {max_id}")
                logger.success(f"Séquence {seq_name} réinitialisée à {max_id}")
            else:
                logger.warning(f"Pas de séquence trouvée pour la table {table_name}")

        cursor.close()
        conn.close()
        logger.success("Toutes les séquences ont été réinitialisées avec succès")

    except Exception as e:
        logger.error(f"Erreur lors de la réinitialisation des séquences: {str(e)}")
        raise

if __name__ == "__main__":
    logger.info("Démarrage de la réparation des séquences")
    reset_sequences()
    logger.info("Terminé")
