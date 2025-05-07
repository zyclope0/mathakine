#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module pour charger les profils d'environnement depuis le fichier JSON central.
Ce script fournit des fonctions pour charger, manipuler et exporter les profils
d'environnement.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Optional, Any

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("load_profiles")

def get_profiles_path():
    """Obtient le chemin vers le fichier profiles.json"""
    script_dir = Path(__file__).resolve().parent
    return script_dir / "profiles.json"

def load_profiles():
    """Charge les profils depuis le fichier JSON"""
    profiles_path = get_profiles_path()
    
    if not profiles_path.exists():
        raise FileNotFoundError(f"Fichier de profils non trouvé: {profiles_path}")
    
    try:
        with open(profiles_path, 'r', encoding='utf-8') as f:
            profiles = json.load(f)
        return profiles
    except json.JSONDecodeError as e:
        raise ValueError(f"Erreur de format JSON dans {profiles_path}: {e}")
    except Exception as e:
        raise Exception(f"Erreur lors du chargement des profils: {e}")

def get_profile(profile_name):
    """
    Récupère un profil spécifique par son nom
    
    Args:
        profile_name (str): Nom du profil (dev, test, prod)
        
    Returns:
        dict: Variables d'environnement du profil
    """
    profiles = load_profiles()
    
    if profile_name not in profiles:
        raise ValueError(f"Profil inconnu: {profile_name}")
    
    # Vérifier la validité du profil si le module de validation est disponible
    try:
        from validate_env import validate_env_dict, print_validation_results
        
        # Valider le profil
        results = validate_env_dict(profiles[profile_name])
        
        # Vérifier s'il y a des erreurs et les afficher
        has_errors = False
        for _, (is_valid, _) in results.items():
            if not is_valid:
                has_errors = True
                break
        
        if has_errors:
            logger.warning(f"Problèmes détectés dans le profil '{profile_name}':")
            print_validation_results(results)
            logger.warning("Les valeurs invalides peuvent causer des problèmes.")
    except ImportError:
        logger.debug("Module de validation non disponible. Validation ignorée.")
    
    return profiles[profile_name]

def get_available_profiles():
    """
    Récupère la liste des profils disponibles
    
    Returns:
        list: Noms des profils disponibles
    """
    profiles = load_profiles()
    return list(profiles.keys())

def export_env_file(profile_name, env_file_path, extra_vars=None):
    """
    Exporte un profil vers un fichier .env
    
    Args:
        profile_name (str): Nom du profil à exporter
        env_file_path (str): Chemin du fichier .env à créer
        extra_vars (dict, optional): Variables supplémentaires à ajouter
    """
    profile = get_profile(profile_name)
    
    # Ajouter les variables supplémentaires si fournies
    if extra_vars and isinstance(extra_vars, dict):
        profile.update(extra_vars)
    
    # Vérifier la validité des variables avant exportation
    try:
        from validate_env import validate_env_dict
        
        # Valider les variables
        results = validate_env_dict(profile)
        has_errors = False
        
        # Identifier les erreurs
        errors = {}
        for key, (is_valid, message) in results.items():
            if not is_valid:
                has_errors = True
                errors[key] = message
        
        # Avertir si des erreurs sont trouvées
        if has_errors:
            logger.warning("Des variables invalides ont été détectées avant l'exportation:")
            for key, message in errors.items():
                logger.warning(f"  - {key}: {message}")
            logger.warning("Le fichier .env sera créé, mais pourrait causer des problèmes.")
    except ImportError:
        logger.debug("Module de validation non disponible. Validation ignorée.")
    
    # Créer le contenu du fichier .env
    content = [
        "# Fichier d'environnement Math Trainer",
        f"# Profil: {profile_name}",
        f"# Généré le: {import_datetime().now().strftime('%Y-%m-%d %H:%M:%S')}",
        ""
    ]
    
    # Ajouter chaque variable d'environnement
    for key, value in profile.items():
        content.append(f"{key}={value}")
    
    # Écrire dans le fichier
    try:
        with open(env_file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))
        logger.info(f"Fichier .env créé avec succès: {env_file_path}")
    except Exception as e:
        logger.error(f"Erreur lors de l'écriture du fichier {env_file_path}: {e}")
        raise
    
    return env_file_path

def import_datetime():
    """Import datetime module (séparé pour éviter l'import en haut du fichier)"""
    import datetime
    return datetime

if __name__ == "__main__":
    # Test du module
    try:
        profiles = load_profiles()
        print(f"Profils disponibles: {', '.join(profiles.keys())}")
        
        for profile_name in profiles:
            print(f"\nProfil: {profile_name}")
            for key, value in profiles[profile_name].items():
                print(f"  {key} = {value}")
    except Exception as e:
        print(f"Erreur: {e}") 