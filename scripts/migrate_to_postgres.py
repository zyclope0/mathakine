"""
Script de migration de SQLite vers PostgreSQL pour Mathakine
"""

import os
import sys
import sqlite3
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from loguru import logger

def get_sqlite_connection():
    """Établit la connexion à la base de données SQLite"""
    try:
        conn = sqlite3.connect('math_trainer.db')
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logger.error(f"Erreur de connexion à SQLite: {e}")
        sys.exit(1)

def get_postgres_connection(db_name=None):
    """Établit la connexion à PostgreSQL"""
    try:
        # Connexion initiale à la base postgres pour créer la base de données
        conn = psycopg2.connect(
            dbname='postgres',
            user=os.getenv('POSTGRES_USER', 'postgres'),
            password=os.getenv('POSTGRES_PASSWORD', 'postgres'),
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            port=os.getenv('POSTGRES_PORT', '5432')
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        if db_name:
            # Créer la base de données si elle n'existe pas
            with conn.cursor() as cur:
                cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
                if not cur.fetchone():
                    cur.execute(f'CREATE DATABASE {db_name}')
            
            # Se connecter à la nouvelle base de données
            conn.close()
            conn = psycopg2.connect(
                dbname=db_name,
                user=os.getenv('POSTGRES_USER', 'postgres'),
                password=os.getenv('POSTGRES_PASSWORD', 'postgres'),
                host=os.getenv('POSTGRES_HOST', 'localhost'),
                port=os.getenv('POSTGRES_PORT', '5432')
            )
        
        return conn
    except Exception as e:
        logger.error(f"Erreur de connexion à PostgreSQL: {e}")
        sys.exit(1)

def get_table_schema(conn, table_name):
    """Récupère le schéma d'une table SQLite"""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    return cursor.fetchall()

def create_postgres_table(pg_conn, table_name, schema):
    """Crée une table PostgreSQL basée sur le schéma SQLite"""
    cursor = pg_conn.cursor()
    
    # Convertir les types SQLite en types PostgreSQL
    type_mapping = {
        'INTEGER': 'INTEGER',
        'REAL': 'DOUBLE PRECISION',
        'TEXT': 'TEXT',
        'BLOB': 'BYTEA',
        'BOOLEAN': 'BOOLEAN',
        'DATETIME': 'TIMESTAMP'
    }
    
    columns = []
    for col in schema:
        name = col['name']
        type_ = type_mapping.get(col['type'].upper(), 'TEXT')
        nullable = 'NOT NULL' if col['notnull'] else ''
        pk = 'PRIMARY KEY' if col['pk'] else ''
        columns.append(f'"{name}" {type_} {nullable} {pk}'.strip())
    
    create_table_sql = f'CREATE TABLE IF NOT EXISTS "{table_name}" (\n    ' + ',\n    '.join(columns) + '\n)'
    
    try:
        cursor.execute(create_table_sql)
        pg_conn.commit()
        logger.info(f"Table {table_name} créée dans PostgreSQL")
    except Exception as e:
        logger.error(f"Erreur lors de la création de la table {table_name}: {e}")
        pg_conn.rollback()
        raise

def migrate_data(sqlite_conn, pg_conn, table_name):
    """Migre les données d'une table SQLite vers PostgreSQL"""
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    # Récupérer les données
    sqlite_cursor.execute(f'SELECT * FROM {table_name}')
    rows = sqlite_cursor.fetchall()
    
    if not rows:
        logger.info(f"Table {table_name} vide, pas de données à migrer")
        return
    
    # Récupérer les noms des colonnes
    columns = [description[0] for description in sqlite_cursor.description]
    
    # Préparer la requête d'insertion
    placeholders = ', '.join(['%s'] * len(columns))
    insert_sql = f'INSERT INTO "{table_name}" ({", ".join([f"\"{col}\"" for col in columns])}) VALUES ({placeholders})'
    
    try:
        # Insérer les données
        for row in rows:
            pg_cursor.execute(insert_sql, row)
        
        pg_conn.commit()
        logger.info(f"{len(rows)} lignes migrées vers la table {table_name}")
    except Exception as e:
        logger.error(f"Erreur lors de la migration des données de {table_name}: {e}")
        pg_conn.rollback()
        raise

def main():
    """Fonction principale de migration"""
    logger.info("Début de la migration de SQLite vers PostgreSQL")
    
    # Connexion à SQLite
    sqlite_conn = get_sqlite_connection()
    
    # Connexion à PostgreSQL
    db_name = os.getenv('POSTGRES_DB', 'mathakine')
    pg_conn = get_postgres_connection(db_name)
    
    try:
        # Liste des tables à migrer
        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        # Migrer chaque table
        for table in tables:
            logger.info(f"Migration de la table {table}")
            
            # Créer la table dans PostgreSQL
            schema = get_table_schema(sqlite_conn, table)
            create_postgres_table(pg_conn, table, schema)
            
            # Migrer les données
            migrate_data(sqlite_conn, pg_conn, table)
        
        logger.success("Migration terminée avec succès!")
        
    except Exception as e:
        logger.error(f"Erreur lors de la migration: {e}")
        sys.exit(1)
    finally:
        sqlite_conn.close()
        pg_conn.close()

if __name__ == "__main__":
    main() 