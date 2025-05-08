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

# Vérifier que la table existe
echo "Vérification de la table exercises..."
python -c "
import os
import sqlite3
print('Répertoire courant:', os.getcwd())
conn = sqlite3.connect('math_trainer.db')
cursor = conn.cursor()
cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\" AND name=\"exercises\"')
if cursor.fetchone():
    print('La table exercises existe!')
else:
    print('ERREUR: La table exercises n\'existe pas!')
conn.close()
"

# Démarrer le serveur
echo "Démarrage du serveur..."
uvicorn app.main:app --host 0.0.0.0 --port $PORT 