#!/bin/bash

# Script de démarrage pour Render
# Ce script initialise la base de données et démarre le serveur

# S'assurer que nous sommes dans le bon répertoire
cd /opt/render/project/src

# Activer l'environnement virtuel s'il existe
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Installer les dépendances spécifiques à Python 3.13
pip install sqlalchemy>=2.0.27 fastapi>=0.100.0 pydantic>=2.0.0 pydantic-settings

# Configurer les variables d'environnement
export MATH_TRAINER_DEBUG=false
export MATH_TRAINER_PROFILE=prod

# Initialiser la base de données
echo "Initialisation de la base de données..."
python -c "
from app.db.init_db import create_tables
print('Début de l\'initialisation de la base de données...')
create_tables()
print('Base de données initialisée avec succès!')
"

# Vérifier que la table existe avec PostgreSQL
echo "Vérification de la table exercises sur PostgreSQL..."
python -c "
import os
import psycopg2
from urllib.parse import urlparse
import sys
from loguru import logger

logger.info('Vérification de la connexion PostgreSQL sur Render')

# Récupérer l'URL de la base de données depuis les variables d'environnement
database_url = os.environ.get('DATABASE_URL')

if not database_url:
    print('ERREUR: DATABASE_URL n\'est pas définie!')
    sys.exit(1)

try:
    # Parser l'URL de connexion
    print('Tentative de connexion à PostgreSQL:', database_url.split('@')[1])
    
    # Connexion à PostgreSQL
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    # Vérifier si la table exercises existe
    cursor.execute(\"\"\"
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'exercises'
        );
    \"\"\")
    
    if cursor.fetchone()[0]:
        print('La table exercises existe dans PostgreSQL!')
    else:
        print('ERREUR: La table exercises n\'existe pas dans PostgreSQL!')
    
    conn.close()
except Exception as e:
    print(f'ERREUR lors de la connexion à PostgreSQL: {e}')
    sys.exit(1)
"

# Démarrer le serveur avec l'interface graphique
echo "Démarrage du serveur avec l'interface graphique..."
python enhanced_server.py 