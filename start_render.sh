#!/bin/bash

# Script de démarrage pour Render
# Ce script initialise la base de données et démarre le serveur

# S'assurer que nous sommes dans le bon répertoire
cd /opt/render/project/src

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Initialize the database
echo "Initialisation de la base de données..."
python -c "
import os
import sqlite3
from enhanced_server import init_db
print('Début de l\'initialisation de la base de données...')
print('Répertoire courant:', os.getcwd())
init_db()
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

# Start the server
echo "Démarrage du serveur..."
uvicorn enhanced_server:app --host 0.0.0.0 --port $PORT 