#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module de validation des variables d'environnement.
Ce script permet de valider que les variables d'environnement respectent
les contraintes définies et qu'elles sont du bon type.
"""

import os
import re
import logging
from typing import Dict, Any, List, Tuple, Callable, Optional, Union

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("env_validator")

# Types de validation disponibles
VALIDATION_TYPES = {
    "boolean": "Une valeur booléenne (true/false)",
    "port": "Un numéro de port valide (1024-65535)",
    "log_level": "Un niveau de log valide (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    "profile": "Un profil valide (dev, test, prod)",
    "string": "Une chaîne de caractères non vide",
    "api_key": "Une clé API valide (format spécifique)"
}

def validate_boolean(value: str) -> Tuple[bool, Optional[str]]:
    """
    Valide qu'une valeur est un booléen (true/false).
    
    Args:
        value (str): La valeur à valider
        
    Returns:
        Tuple[bool, Optional[str]]: (validité, message d'erreur)
    """
    if value.lower() not in ["true", "false"]:
        return False, f"Doit être 'true' ou 'false', reçu: '{value}'"
    return True, None

def validate_port(value: str) -> Tuple[bool, Optional[str]]:
    """
    Valide qu'une valeur est un port valide (entier entre 1024 et 65535).
    
    Args:
        value (str): La valeur à valider
        
    Returns:
        Tuple[bool, Optional[str]]: (validité, message d'erreur)
    """
    try:
        port = int(value)
        if port < 1024 or port > 65535:
            return False, f"Le port doit être entre 1024 et 65535, reçu: {port}"
        return True, None
    except ValueError:
        return False, f"Le port doit être un nombre entier, reçu: '{value}'"

def validate_log_level(value: str) -> Tuple[bool, Optional[str]]:
    """
    Valide qu'une valeur est un niveau de log valide.
    
    Args:
        value (str): La valeur à valider
        
    Returns:
        Tuple[bool, Optional[str]]: (validité, message d'erreur)
    """
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if value.upper() not in valid_levels:
        return False, f"Niveau de log doit être un de {', '.join(valid_levels)}, reçu: '{value}'"
    return True, None

def validate_profile(value: str) -> Tuple[bool, Optional[str]]:
    """
    Valide qu'une valeur est un profil valide.
    
    Args:
        value (str): La valeur à valider
        
    Returns:
        Tuple[bool, Optional[str]]: (validité, message d'erreur)
    """
    valid_profiles = ["dev", "test", "prod"]
    if value.lower() not in valid_profiles:
        return False, f"Profil doit être un de {', '.join(valid_profiles)}, reçu: '{value}'"
    return True, None

def validate_string(value: str) -> Tuple[bool, Optional[str]]:
    """
    Valide qu'une valeur est une chaîne non vide.
    
    Args:
        value (str): La valeur à valider
        
    Returns:
        Tuple[bool, Optional[str]]: (validité, message d'erreur)
    """
    if not value or value.strip() == "":
        return False, "La valeur ne peut pas être vide"
    return True, None

def validate_api_key(value: str) -> Tuple[bool, Optional[str]]:
    """
    Valide qu'une valeur ressemble à une clé API.
    Pour OpenAI, les clés commencent par 'sk-' suivi de caractères alphanumériques.
    
    Args:
        value (str): La valeur à valider
        
    Returns:
        Tuple[bool, Optional[str]]: (validité, message d'erreur)
    """
    # Pour OpenAI, vérifie que la clé commence par sk- et a une longueur raisonnable
    if value.startswith("sk-") and len(value) > 20:
        return True, None
    else:
        return False, "Format de clé API invalide (doit commencer par 'sk-' pour OpenAI)"

# Définition des validateurs pour chaque variable
VALIDATORS = {
    "MATH_TRAINER_DEBUG": validate_boolean,
    "MATH_TRAINER_TEST_MODE": validate_boolean,
    "MATH_TRAINER_PORT": validate_port,
    "MATH_TRAINER_LOG_LEVEL": validate_log_level,
    "MATH_TRAINER_PROFILE": validate_profile,
    "OPENAI_API_KEY": validate_api_key
}

def validate_variable(name: str, value: str) -> Tuple[bool, Optional[str]]:
    """
    Valide une variable d'environnement selon son nom et sa valeur.
    
    Args:
        name (str): Nom de la variable
        value (str): Valeur de la variable
        
    Returns:
        Tuple[bool, Optional[str]]: (validité, message d'erreur)
    """
    # Si la variable n'a pas de validateur défini, on considère qu'elle est valide
    if name not in VALIDATORS:
        return True, None
    
    # Obtenir le validateur approprié et valider la valeur
    validator = VALIDATORS[name]
    return validator(value)

def validate_env_dict(env_vars: Dict[str, str]) -> Dict[str, Tuple[bool, Optional[str]]]:
    """
    Valide un dictionnaire de variables d'environnement.
    
    Args:
        env_vars (Dict[str, str]): Dictionnaire de variables d'environnement
        
    Returns:
        Dict[str, Tuple[bool, Optional[str]]]: Résultats de validation pour chaque variable
    """
    results = {}
    for name, value in env_vars.items():
        results[name] = validate_variable(name, value)
    return results

def validate_env_file(file_path: str) -> Dict[str, Tuple[bool, Optional[str]]]:
    """
    Valide toutes les variables d'environnement dans un fichier .env
    
    Args:
        file_path (str): Chemin vers le fichier .env
        
    Returns:
        Dict[str, Tuple[bool, Optional[str]]]: Résultats de validation pour chaque variable
    """
    env_vars = {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split('=', 1)
                if len(parts) == 2:
                    name, value = parts
                    env_vars[name] = value
    except Exception as e:
        logger.error(f"Erreur lors de la lecture du fichier {file_path}: {e}")
        return {}
    
    return validate_env_dict(env_vars)

def print_validation_results(results: Dict[str, Tuple[bool, Optional[str]]]) -> bool:
    """
    Affiche les résultats de validation de façon lisible et colorée.
    
    Args:
        results (Dict[str, Tuple[bool, Optional[str]]]): Résultats de validation
        
    Returns:
        bool: True si toutes les validations sont réussies, False sinon
    """
    all_valid = True
    print("\nRésultats de validation des variables d'environnement:")
    print("====================================================")
    
    # Trier les résultats pour un affichage plus cohérent
    sorted_results = sorted(results.items())
    
    for name, (is_valid, message) in sorted_results:
        if is_valid:
            print(f"[OK] {name}: Valide")
        else:
            all_valid = False
            print(f"[ERREUR] {name}: {message}")
    
    print("\nRésumé:")
    if all_valid:
        print("[SUCCÈS] Toutes les variables sont valides.")
    else:
        print("[ÉCHEC] Certaines variables sont invalides.")
    
    return all_valid

def main():
    """Fonction principale pour exécuter la validation en ligne de commande"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Valide les variables d'environnement")
    parser.add_argument('--env-file', '-e', type=str, help="Chemin vers le fichier .env à valider")
    parser.add_argument('--verbose', '-v', action='store_true', help="Afficher plus de détails")
    
    args = parser.parse_args()
    
    # Si le mode verbeux est activé, configurer le logging en conséquence
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Si un fichier .env est spécifié, le valider
    if args.env_file:
        results = validate_env_file(args.env_file)
        all_valid = print_validation_results(results)
        return 0 if all_valid else 1
    
    # Sinon, valider les variables d'environnement actuelles
    env_vars = {k: v for k, v in os.environ.items() if k in VALIDATORS}
    if not env_vars:
        logger.warning("Aucune variable d'environnement à valider trouvée dans l'environnement actuel.")
        return 0
    
    results = validate_env_dict(env_vars)
    all_valid = print_validation_results(results)
    return 0 if all_valid else 1

if __name__ == "__main__":
    import sys
    sys.exit(main()) 