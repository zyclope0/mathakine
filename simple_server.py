"""
Serveur minimal simplifié pour tester le démarrage de Mathakine
"""

import uvicorn
import os
from starlette.applications import Starlette
from starlette.responses import JSONResponse, HTMLResponse
from starlette.routing import Route

PORT = int(os.environ.get("PORT", 8000))
DEBUG = os.environ.get("MATH_TRAINER_DEBUG", "true").lower() == "true"

# Route principale
async def homepage(request):
    return HTMLResponse("""
    <html>
        <head>
            <title>Mathakine - Version Simplifiée</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }
                h1 {
                    color: #333;
                }
                .container {
                    background-color: white;
                    padding: 20px;
                    border-radius: 5px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .card {
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    padding: 15px;
                    margin-bottom: 15px;
                }
                .success {
                    color: green;
                    font-weight: bold;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Mathakine - Version Simplifiée</h1>
                <p class="success">Le serveur fonctionne correctement!</p>
                
                <div class="card">
                    <h2>Version temporaire</h2>
                    <p>Cette version est une version temporaire simplifiée pour tester le démarrage du serveur.</p>
                    <p>Pour utiliser la version complète, veuillez corriger les erreurs dans enhanced_server.py.</p>
                </div>
                
                <div class="card">
                    <h2>API Test</h2>
                    <p>Pour tester l'API, accédez à <a href="/api/health">/api/health</a></p>
                </div>
            </div>
        </body>
    </html>
    """)

# Route d'API pour vérifier l'état
async def health_check(request):
    return JSONResponse({
        "status": "ok",
        "server": "simple_server.py",
        "version": "0.1.0"
    })

# Configuration des routes
routes = [
    Route("/", homepage),
    Route("/api/health", health_check),
]

# Création de l'application Starlette
app = Starlette(
    debug=DEBUG,
    routes=routes
)

# Fonction principale
def main():
    """Point d'entrée principal de l'application"""
    print(f"Lancement du serveur simplifié sur le port {PORT}")
    uvicorn.run(
        "simple_server:app",
        host="0.0.0.0",
        port=PORT,
        reload=DEBUG
    )

if __name__ == "__main__":
    main() 