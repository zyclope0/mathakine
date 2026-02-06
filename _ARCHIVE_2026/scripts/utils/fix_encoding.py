#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script pour corriger l'encodage des fichiers env.example et .env.example
et s'assurer que les caractères accentués sont correctement affichés.
"""

import os
import sys
from pathlib import Path

# Obtenir le chemin du script
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent.parent

# Chemins des fichiers
env_example_util = script_dir / "env.example"
env_example_dest = project_root / ".env.example"

# Contenu du fichier avec des caractères accentués
env_content = """# Math Trainer - Fichier d'environnement exemple
# Copiez ce fichier vers .env à la racine du projet et ajustez les valeurs selon votre environnement

# Configuration du serveur
MATH_TRAINER_DEBUG=true                # Active/désactive le mode debug (true/false)
MATH_TRAINER_PORT=8081                 # Port du serveur web
MATH_TRAINER_LOG_LEVEL=INFO            # Niveau de logs (DEBUG, INFO, WARNING, ERROR)
MATH_TRAINER_TEST_MODE=false           # Active/désactive le mode test (true/false)

# Base de données
DATABASE_URL=sqlite:///./math_trainer.db # URL de connexion à la base de données

# Intégration OpenAI (optionnel)
OPENAI_API_KEY=votre_clé_api_ici       # Clé API OpenAI (ne pas committer ce fichier avec une vraie clé)

# Profil d'environnement
MATH_TRAINER_PROFILE=dev               # Profil actif (dev, test, prod)

# Variables spécifiques aux tests
# TEST_DATABASE_URL=sqlite:///./math_trainer_test.db  # Base de données dédiée aux tests

# Variables spécifiques à la production
# ALLOWED_HOSTS=mathtrainer.example.com,localhost  # Hôtes autorisés en production
# SESSION_COOKIE_SECURE=true                       # Cookies sécurisés en production
"""



def main():
    """Fonction principale pour corriger l'encodage des fichiers"""
    print("Correction de l'encodage des fichiers env.example et .env.example...")

    try:
        # Écrire le contenu dans les fichiers avec encodage UTF-8
        with open(env_example_util, 'w', encoding='utf-8') as f:
            f.write(env_content)

        with open(env_example_dest, 'w', encoding='utf-8') as f:
            f.write(env_content)

        print(f"Fichiers mis à jour avec succès en encodage UTF-8:")
        print(f"  - {env_example_util}")
        print(f"  - {env_example_dest}")

        # Vérifier l'encodage
        with open(env_example_dest, 'r', encoding='utf-8') as f:
            content = f.read()
            if "désactive" in content and "données" in content:
                print("✓ Vérification réussie : Les caractères accentués sont correctement encodés.")
            else:
                print("⚠ Attention : Possible problème d'encodage des caractères accentués.")

        return 0
    except Exception as e:
        print(f"Erreur lors de la correction de l'encodage: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
