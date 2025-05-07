#!/bin/bash

# Création du répertoire de données si nécessaire
mkdir -p /data

# Vérification si la base de données existe dans le volume persistant
if [ ! -f "/data/math_trainer.db" ]; then
  echo "Initialisation de la base de données dans le volume persistant..."
  # Forcer la création de la BD dans /data
  export MATH_TRAINER_DB_PATH="/data/math_trainer.db"
  python scripts/create_database.py
else
  echo "Base de données existante trouvée dans le volume persistant."
fi

# Créer un lien symbolique pour que l'application utilise la BD du volume
ln -sf /data/math_trainer.db ./math_trainer.db

echo "Configuration de la base de données persistante terminée!" 