#!/usr/bin/env python
"""
Script pour optimiser la base de données PostgreSQL après migration.
Ce script effectue:
1. Création d'index sur les colonnes fréquemment utilisées
2. Vacuum et analyse des tables
3. Vérification et rapport sur l'état de la base de données
"""

import os
import sys
import time
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv
from loguru import logger

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Configuration du logger
logger.remove()
logger.add(sys.stderr, level="INFO")
logger.add("logs/postgres_optimization_{time}.log", level="DEBUG", rotation="10 MB")



def get_postgres_connection():
    """Établit la connexion à PostgreSQL"""
    try:
        pg_user = os.getenv('POSTGRES_USER')
        pg_password = os.getenv('POSTGRES_PASSWORD')
        pg_host = os.getenv('POSTGRES_HOST')
        pg_port = os.getenv('POSTGRES_PORT')
        pg_db = os.getenv('POSTGRES_DB')

        params = {
            'dbname': pg_db,
            'user': pg_user,
            'password': pg_password,
            'host': pg_host,
            'port': pg_port
        }

        logger.debug("Tentative de connexion à PostgreSQL...")
        conn = psycopg2.connect(**params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        logger.debug(f"Connexion à PostgreSQL établie avec succès (base de données {pg_db})")

        return conn
    except Exception as e:
        logger.error(f"Erreur de connexion à PostgreSQL: {e}")
        sys.exit(1)



def get_table_names(conn):
    """Récupère la liste des tables dans la base de données"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT tablename FROM pg_tables
        WHERE schemaname = 'public'
    """)
    return [table[0] for table in cursor.fetchall()]



def get_table_stats(conn, table_name):
    """Récupère les statistiques d'une table"""
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT count(*) FROM "{table_name}"
    """)
    count = cursor.fetchone()[0]

    cursor.execute(f"""
        SELECT pg_size_pretty(pg_total_relation_size('{table_name}'))
    """)
    size = cursor.fetchone()[0]

    return {
        'count': count,
        'size': size
    }



def create_indexes(conn):
    """Crée des index sur les colonnes fréquemment utilisées"""
    indexes = [
        # Tables et colonnes à indexer
        ('exercises', 'exercise_type'),
        ('exercises', 'difficulty'),
        ('exercises', 'created_at'),
        ('results', 'exercise_id'),
        ('results', 'is_correct'),
        ('results', 'created_at'),
        ('user_stats', 'exercise_type'),
        ('user_stats', 'difficulty')
    ]

    cursor = conn.cursor()

    created_indexes = 0
    for table, column in indexes:
        index_name = f"idx_{table}_{column}"
        try:
            # Vérifier si l'index existe déjà
            cursor.execute(f"""
                SELECT 1 FROM pg_indexes
                WHERE indexname = '{index_name}'
            """)
            if cursor.fetchone():
                logger.info(f"L'index {index_name} existe déjà")
                continue

            # Créer l'index
            start_time = time.time()
            cursor.execute(f'CREATE INDEX {index_name} ON "{table}" ("{column}")')
            elapsed = time.time() - start_time

            logger.success(f"Index {index_name} créé en {elapsed:.2f} secondes")
            created_indexes += 1
        except Exception as e:
            logger.error(f"Erreur lors de la création de l'index {index_name}: {e}")

    return created_indexes



def vacuum_analyze(conn):
    """Exécute VACUUM ANALYZE sur toutes les tables"""
    tables = get_table_names(conn)
    cursor = conn.cursor()

    for table in tables:
        try:
            logger.info(f"Exécution de VACUUM ANALYZE sur {table}...")
            start_time = time.time()
            cursor.execute(f'VACUUM ANALYZE "{table}"')
            elapsed = time.time() - start_time

            logger.success(f"VACUUM ANALYZE sur {table} terminé en {elapsed:.2f} secondes")
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution de VACUUM ANALYZE sur {table}: {e}")



def check_database_health(conn):
    """Vérifie l'état de santé de la base de données"""
    logger.info("Vérification de l'état de santé de la base de données...")

    # Vérifier les tables et leur taille
    tables = get_table_names(conn)
    logger.info(f"Nombre de tables: {len(tables)}")

    table_stats = {}
    for table in tables:
        stats = get_table_stats(conn, table)
        table_stats[table] = stats
        logger.info(f"Table {table}: {stats['count']} lignes, taille: {stats['size']}")

    # Vérifier les index
    cursor = conn.cursor()
    cursor.execute("""
        SELECT indexname, tablename
        FROM pg_indexes
        WHERE schemaname = 'public'
    """)
    indexes = cursor.fetchall()
    logger.info(f"Nombre d'index: {len(indexes)}")
    for idx in indexes:
        logger.info(f"Index {idx[0]} sur la table {idx[1]}")

    # Vérifier les connexions actives
    cursor.execute("""
        SELECT count(*) FROM pg_stat_activity
    """)
    active_connections = cursor.fetchone()[0]
    logger.info(f"Connexions actives: {active_connections}")

    return {
        'tables': len(tables),
        'indexes': len(indexes),
        'active_connections': active_connections,
        'table_stats': table_stats
    }



def main():
    """Fonction principale"""
    logger.info("Début de l'optimisation de la base de données PostgreSQL")

    # Connexion à PostgreSQL
    try:
        pg_conn = get_postgres_connection()
    except Exception as e:
        logger.error(f"Impossible de se connecter à PostgreSQL: {e}")
        sys.exit(1)

    # Vérifier l'état initial
    logger.info("État initial de la base de données:")
    initial_state = check_database_health(pg_conn)

    # Créer les index
    logger.info("Création des index...")
    created_indexes = create_indexes(pg_conn)
    logger.info(f"{created_indexes} nouveaux index créés")

    # Exécuter VACUUM ANALYZE
    logger.info("Exécution de VACUUM ANALYZE sur toutes les tables...")
    vacuum_analyze(pg_conn)

    # Vérifier l'état final
    logger.info("État final de la base de données après optimisation:")
    final_state = check_database_health(pg_conn)

    # Fermer la connexion
    pg_conn.close()

    logger.success("Optimisation de la base de données PostgreSQL terminée avec succès")
    logger.info(f"Nombre de tables: {final_state['tables']}")
    logger.info(f"Nombre d'index: {final_state['indexes']}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
