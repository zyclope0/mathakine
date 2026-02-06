#!/usr/bin/env python3
"""
Script pour initialiser la base de données de test Render avec le schéma.
Utilise l'URL fournie pour se connecter et créer toutes les tables.
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire racine au path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.db.init_db import create_tables_with_test_data
from app.core.logging_config import get_logger

logger = get_logger(__name__)

# URL de la base de test Render
TEST_DATABASE_URL = "postgresql://mathakine_test_jk25_user:kZL3B6D8frkEgDRWd1xdLZz9mZemjkKo@dpg-d4lj1n9r0fns73fc6ncg-a/mathakine_test_jk25"

def main():
    """Initialise la base de test Render avec le schéma"""
    print("=" * 60)
    print("🔧 Initialisation de la base de test Render")
    print("=" * 60)
    print()
    
    # Définir temporairement DATABASE_URL pour l'initialisation
    original_db_url = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL
    
    try:
        # Réinitialiser l'engine pour utiliser la nouvelle URL
        from app.db.base import engine
        engine.dispose()  # Fermer les connexions existantes
        
        print(f"📡 Connexion à la base de test...")
        print(f"   Database: mathakine_test_jk25")
        print()
        
        # Créer les tables et les données de test
        print("📋 Création des tables...")
        create_tables_with_test_data()
        
        print()
        print("=" * 60)
        print("✅ Base de test initialisée avec succès !")
        print("=" * 60)
        print()
        print("📝 Configuration à ajouter dans Render (service mathakine-alpha):")
        print()
        print(f"   TEST_DATABASE_URL={TEST_DATABASE_URL}")
        print()
        print("⚠️  IMPORTANT: Ne modifiez PAS DATABASE_URL (doit rester la production)")
        print()
        
        return 0
        
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return 1
        
    finally:
        # Restaurer l'URL originale
        if original_db_url:
            os.environ["DATABASE_URL"] = original_db_url
        else:
            os.environ.pop("DATABASE_URL", None)

if __name__ == "__main__":
    sys.exit(main())

