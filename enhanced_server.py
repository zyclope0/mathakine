"""
Serveur web amélioré pour Mathakine (Math Trainer)

Ce module est l'interface web principale de Mathakine, fournissant à la fois:
- Une interface utilisateur web complète via des templates Jinja2
- Des endpoints API JSON pour les interactions programmatiques

Relation avec app/main.py:
- enhanced_server.py: Interface principale avec UI web + API minimaliste (à utiliser par défaut)
- app/main.py: API REST pure destinée aux tests, au débogage ou aux clients externes

Les deux modules partagent les mêmes modèles de données et services, mais ont des objectifs différents:
- enhanced_server.py est optimisé pour l'expérience utilisateur et l'interface web
- app/main.py est optimisé pour les interactions programmatiques via API REST

Pour démarrer ce serveur, utilisez la commande:
    python mathakine_cli.py run
    
Pour démarrer uniquement l'API REST:
    python mathakine_cli.py run --api-only
"""

import os
import sys
from loguru import logger
from dotenv import load_dotenv

# Charger les variables d'environnement AVANT de les lire
load_dotenv(override=True)

# Import from our server module
from server import create_app, run_server

# Configuration from environment variables
PORT = int(os.environ.get("PORT", 8000))
DEBUG = os.environ.get("MATH_TRAINER_DEBUG", "true").lower() == "true"
HOST = os.environ.get("MATH_TRAINER_HOST", "0.0.0.0")

# Create the Starlette application using our modular architecture
app = create_app(debug=DEBUG)

def main():
    """Point d'entrée principal pour le serveur"""
    print("========================================")
    print(f"ENHANCED_SERVER.PY - Serveur complet démarré sur le port {PORT}")
    print("Serveur avec interface graphique complète")
    print("========================================")
    run_server(host=HOST, port=PORT, debug=DEBUG)

if __name__ == "__main__":
    main() 
