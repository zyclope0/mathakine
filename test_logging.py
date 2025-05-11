#!/usr/bin/env python
"""
Script pour tester le système de logging de Mathakine
"""
import os
import sys
from datetime import datetime

# Ajouter le répertoire courant au chemin Python pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importer le système de logging
from app.core.logging_config import get_logger

# Créer un logger pour ce script
logger = get_logger("test_logging")

def main():
    """Fonction principale qui génère des logs de test"""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Générer des logs de différents niveaux
    logger.debug(f"[{timestamp}] Ceci est un message de DEBUG de test")
    logger.info(f"[{timestamp}] Ceci est un message d'INFO de test")
    logger.warning(f"[{timestamp}] Ceci est un message de WARNING de test")
    logger.error(f"[{timestamp}] Ceci est un message d'ERROR de test")
    logger.critical(f"[{timestamp}] Ceci est un message de CRITICAL de test")
    
    # Tester avec des données contextuelles
    logger.bind(user_id=123, test_id="ABC-123").info(
        f"[{timestamp}] Test de log avec contexte"
    )
    
    # Tester les exceptions
    try:
        # Générer une exception volontairement
        result = 1 / 0
    except Exception as e:
        logger.exception(f"[{timestamp}] Test d'exception: {str(e)}")
    
    print("Test de logging terminé. Vérifiez les fichiers dans le dossier 'logs/'.")

if __name__ == "__main__":
    main() 