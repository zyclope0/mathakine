"""
Script de migration de SQLite vers PostgreSQL sur Render pour Mathakine
"""

import os
import sys
import sqlite3
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from loguru import logger
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Configuration du logger
logger.remove()
logger.add(sys.stderr, level="DEBUG")

# Variables de connexion Render hardcodées (pour éviter les problèmes de lecture des variables d'environnement)
RENDER_DB_NAME = "mathakine_test"
RENDER_DB_USER = "zyclope"
RENDER_DB_PASSWORD = "Zp4PX83vdxl5pDyxRJVaheIHArAhyN5l"
RENDER_DB_HOST = "dpg-d0e53tp5pdvs73aol3h0-a.frankfurt-postgres.render.com"
RENDER_DB_PORT = "5432"

def get_sqlite_connection():
    """Établit la connexion à la base de données SQLite"""
    try:
        logger.debug("Tentative de connexion à SQLite")
        conn = sqlite3.connect('math_trainer.db')
        conn.row_factory = sqlite3.Row
        logger.debug("Connexion à SQLite établie avec succès")
        return conn
    except Exception as e:
        logger.error(f"Erreur de connexion à SQLite: {e}")
        sys.exit(1)

def get_postgres_connection():
    """Établit la connexion à PostgreSQL sur Render"""
    try:
        # Connexion directe à la base de données Render
        params = {
            'dbname': RENDER_DB_NAME,
            'user': RENDER_DB_USER,
            'password': RENDER_DB_PASSWORD,
            'host': RENDER_DB_HOST,
            'port': RENDER_DB_PORT
        }
        
        # Afficher les informations de connexion pour le débogage
        logger.debug(f"Paramètres de connexion PostgreSQL Render: dbname={params['dbname']}, user={params['user']}, host={params['host']}, port={params['port']}")
        
        # Essai de connexion
        logger.debug("Tentative de connexion à PostgreSQL sur Render...")
        conn = psycopg2.connect(**params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        logger.debug(f"Connexion à PostgreSQL sur Render établie avec succès")
        
        return conn
    except Exception as e:
        logger.error(f"Erreur de connexion à PostgreSQL sur Render: {e}")
        import traceback
        logger.error(traceback.format_exc())
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
        
        # Si le nom de la colonne suggère un booléen, utiliser BOOLEAN
        col_type = col['type'].upper()
        if (name.startswith('is_') or name.startswith('has_') or name == 'active' or name == 'enabled') and col_type == 'INTEGER':
            logger.debug(f"Conversion de la colonne {name} de INTEGER à BOOLEAN")
            type_ = 'BOOLEAN'
        else:
            type_ = type_mapping.get(col_type, 'TEXT')
        
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
    
    # Récupérer les noms des colonnes et les types
    columns = [description[0] for description in sqlite_cursor.description]
    
    # Récupérer le schéma pour détecter les colonnes booléennes
    schema = get_table_schema(sqlite_conn, table_name)
    boolean_columns = {}
    for col in schema:
        if col['type'].upper() == 'BOOLEAN':
            boolean_columns[col['name']] = True
    
    # Préparer la requête d'insertion
    placeholders = ', '.join(['%s'] * len(columns))
    insert_sql = f'INSERT INTO "{table_name}" ({", ".join([f"\"{col}\"" for col in columns])}) VALUES ({placeholders})'
    
    try:
        # Insérer les données
        for row_dict in rows:
            # Convertir les entiers en booléens pour les colonnes booléennes
            row_list = list(row_dict)
            for i, col_name in enumerate(columns):
                if col_name in boolean_columns and row_list[i] is not None:
                    row_list[i] = bool(row_list[i])
            
            pg_cursor.execute(insert_sql, row_list)
        
        pg_conn.commit()
        logger.info(f"{len(rows)} lignes migrées vers la table {table_name}")
    except Exception as e:
        logger.error(f"Erreur lors de la migration des données de {table_name}: {e}")
        pg_conn.rollback()
        raise

def main():
    """Fonction principale de migration"""
    logger.info("Début de la migration de SQLite vers PostgreSQL sur Render")
    
    # Connexion à SQLite
    sqlite_conn = get_sqlite_connection()
    
    # Connexion à PostgreSQL sur Render
    pg_conn = get_postgres_connection()
    
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
        
        logger.success("Migration vers Render terminée avec succès!")
        
    except Exception as e:
        logger.error(f"Erreur lors de la migration: {e}")
        sys.exit(1)
    finally:
        sqlite_conn.close()
        pg_conn.close()

if __name__ == "__main__":
    main() 