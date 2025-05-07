#!/bin/bash

# Installation des dépendances
pip install -r requirements.txt

# Configuration de la base de données persistante
bash setup_persistent_db.sh

# Création d'un fichier .env si nécessaire
if [ ! -f .env ]; then
  echo "Création du fichier .env..."
  cp sample.env .env
  echo "MATH_TRAINER_PROFILE=prod" >> .env
fi

echo "Build terminé avec succès!" 