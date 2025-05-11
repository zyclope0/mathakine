#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script pour créer directement le fichier .env.example
avec les caractères accentués correctement encodés.
"""

import os
import sys
from pathlib import Path

# Obtenir le chemin du projet
project_root = Path(__file__).resolve().parent.parent.parent

# Chemin du fichier destination
env_example_dest = project_root / ".env.example"



def main():
    """Fonction principale pour créer le fichier .env.example"""
    print(f"Création du fichier {env_example_dest}...")

    try:
        with open(env_example_dest, 'w', encoding='utf-8') as f:
            f.write("""# Math Trainer - Fichier d'environnement exemple
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
""")

        print(f"Fichier {env_example_dest} créé avec succès (encodage UTF-8)")

        # Vérifier l'encodage
        with open(env_example_dest, 'r', encoding='utf-8') as f:
            content = f.read()
            if "désactive" in content and "données" in content:
                print("✓ Vérification réussie : Les caractères accentués sont correctement encodés.")
            else:
                print("⚠ Attention : Possible problème d'encodage des caractères accentués.")

        return 0
    except Exception as e:
        print(f"Erreur lors de la création du fichier: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
