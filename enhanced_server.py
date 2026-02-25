"""
Point d'entrée principal du backend Mathakine (Math Trainer).

Lance l'application Starlette unifiée (server/app.py) avec toutes les routes API,
le middleware d'auth, SSE streaming IA, etc. FastAPI a été archivé (06/02/2026).

Usage:
    python enhanced_server.py
"""

import os
import sys
from loguru import logger
from dotenv import load_dotenv

# Charger les variables d'environnement (ignorer .env en prod - sécurité)
if os.environ.get("ENVIRONMENT") != "production":
    load_dotenv(override=False)

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
