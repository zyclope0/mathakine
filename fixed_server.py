"""
Serveur Mathakine simplifié et fonctionnel qui contourne les erreurs de syntaxe
"""

import os
import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse, HTMLResponse, RedirectResponse
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
import traceback
import json
import random
import sqlite3

# Configuration
PORT = int(os.environ.get("PORT", 8081))
DEBUG = os.environ.get("MATH_TRAINER_DEBUG", "true").lower() == "true"

# Utilitaires de base de données
def get_db_connection():
    """Crée une connexion à la base de données SQLite"""
    conn = sqlite3.connect("math_trainer.db")
    conn.row_factory = sqlite3.Row
    return conn

# Routes principales
async def homepage(request):
    """Page d'accueil"""
    return HTMLResponse("""
    <html>
        <head>
            <title>Mathakine - Version Temporaire</title>
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
                .nav {
                    margin-bottom: 20px;
                }
                .nav a {
                    margin-right: 10px;
                    text-decoration: none;
                    color: #0066cc;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Mathakine - Version Temporaire</h1>
                <p class="success">Le serveur fonctionne correctement!</p>
                
                <div class="nav">
                    <a href="/">Accueil</a>
                    <a href="/exercises">Exercices</a>
                    <a href="/dashboard">Tableau de bord</a>
                    <a href="/api/exercises">API Exercices</a>
                </div>
                
                <div class="card">
                    <h2>Version temporaire</h2>
                    <p>Cette version est une solution temporaire pendant que nous résolvons les problèmes dans le serveur principal.</p>
                    <p>Les fonctionnalités principales sont disponibles mais peuvent être limitées.</p>
                </div>
            </div>
        </body>
    </html>
    """)

async def exercises_page(request):
    """Page des exercices"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM exercises LIMIT 10")
        exercises = [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        exercises = []
        print(f"Erreur lors de la récupération des exercices: {e}")
    
    conn.close()
    
    exercise_html = ""
    for ex in exercises:
        exercise_html += f"""
        <div class="exercise-card">
            <h3>{ex.get('title', 'Exercice')}</h3>
            <p>{ex.get('question', 'Question non disponible')}</p>
            <p><strong>Type:</strong> {ex.get('exercise_type', 'Non spécifié')}</p>
            <p><strong>Difficulté:</strong> {ex.get('difficulty', 'Non spécifiée')}</p>
            <a href="/exercise/{ex.get('id', 0)}">Voir l'exercice</a>
        </div>
        """
    
    if not exercise_html:
        exercise_html = "<p>Aucun exercice disponible pour le moment.</p>"
    
    return HTMLResponse(f"""
    <html>
        <head>
            <title>Mathakine - Exercices</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                h1, h2, h3 {{
                    color: #333;
                }}
                .container {{
                    background-color: white;
                    padding: 20px;
                    border-radius: 5px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .exercise-card {{
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    padding: 15px;
                    margin-bottom: 15px;
                }}
                .nav {{
                    margin-bottom: 20px;
                }}
                .nav a {{
                    margin-right: 10px;
                    text-decoration: none;
                    color: #0066cc;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Exercices Mathakine</h1>
                
                <div class="nav">
                    <a href="/">Accueil</a>
                    <a href="/exercises">Exercices</a>
                    <a href="/dashboard">Tableau de bord</a>
                </div>
                
                <h2>Liste des exercices disponibles</h2>
                {exercise_html}
            </div>
        </body>
    </html>
    """)

async def dashboard_page(request):
    """Page de tableau de bord"""
    return HTMLResponse("""
    <html>
        <head>
            <title>Mathakine - Tableau de bord</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }
                h1, h2 {
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
                .stat {
                    display: inline-block;
                    margin: 10px;
                    text-align: center;
                    width: 150px;
                }
                .stat-number {
                    font-size: 24px;
                    font-weight: bold;
                    color: #0066cc;
                }
                .nav {
                    margin-bottom: 20px;
                }
                .nav a {
                    margin-right: 10px;
                    text-decoration: none;
                    color: #0066cc;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Tableau de bord Mathakine</h1>
                
                <div class="nav">
                    <a href="/">Accueil</a>
                    <a href="/exercises">Exercices</a>
                    <a href="/dashboard">Tableau de bord</a>
                </div>
                
                <div class="card">
                    <h2>Vos statistiques</h2>
                    <div class="stat">
                        <div class="stat-number">42</div>
                        <div>Exercices complétés</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">36</div>
                        <div>Réponses correctes</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">85%</div>
                        <div>Taux de réussite</div>
                    </div>
                </div>
                
                <div class="card">
                    <h2>Activité récente</h2>
                    <p>Réussi: 2 + 2 = ?</p>
                    <p>Réussi: 8 - 3 = ?</p>
                    <p>Échoué: 7 x 8 = ?</p>
                </div>
            </div>
        </body>
    </html>
    """)

async def exercise_detail(request):
    """Page de détail d'un exercice"""
    exercise_id = request.path_params["exercise_id"]
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM exercises WHERE id = ?", (exercise_id,))
        exercise = cursor.fetchone()
        conn.close()
        
        if not exercise:
            return HTMLResponse("<h1>Exercice non trouvé</h1>", status_code=404)
        
        exercise = dict(exercise)
        choices = exercise.get('choices', '[]')
        try:
            choices = json.loads(choices) if isinstance(choices, str) else choices
        except:
            choices = []
            
        choices_html = ""
        for choice in choices:
            choices_html += f'<button class="choice-btn" data-value="{choice}">{choice}</button>'
        
        return HTMLResponse(f"""
        <html>
            <head>
                <title>Mathakine - Exercice</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        max-width: 800px;
                        margin: 0 auto;
                        padding: 20px;
                        background-color: #f5f5f5;
                    }}
                    h1, h2 {{
                        color: #333;
                    }}
                    .container {{
                        background-color: white;
                        padding: 20px;
                        border-radius: 5px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }}
                    .card {{
                        border: 1px solid #ddd;
                        border-radius: 4px;
                        padding: 15px;
                        margin-bottom: 15px;
                    }}
                    .nav {{
                        margin-bottom: 20px;
                    }}
                    .nav a {{
                        margin-right: 10px;
                        text-decoration: none;
                        color: #0066cc;
                    }}
                    .choice-btn {{
                        padding: 10px 15px;
                        margin: 5px;
                        background-color: #f1f1f1;
                        border: 1px solid #ddd;
                        border-radius: 4px;
                        cursor: pointer;
                    }}
                    .choice-btn:hover {{
                        background-color: #e9e9e9;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>{exercise.get('title', 'Exercice')}</h1>
                    
                    <div class="nav">
                        <a href="/">Accueil</a>
                        <a href="/exercises">Exercices</a>
                        <a href="/dashboard">Tableau de bord</a>
                    </div>
                    
                    <div class="card">
                        <h2>Question</h2>
                        <p>{exercise.get('question', 'Question non disponible')}</p>
                    </div>
                    
                    <div class="card">
                        <h2>Réponses possibles</h2>
                        {choices_html}
                    </div>
                </div>
            </body>
        </html>
        """)
    except Exception as e:
        print(f"Erreur lors de l'affichage de l'exercice: {e}")
        traceback.print_exc()
        return HTMLResponse("<h1>Erreur lors du chargement de l'exercice</h1>", status_code=500)

# Routes API
async def api_health(request):
    """Vérification de l'état de l'API"""
    return JSONResponse({
        "status": "ok",
        "message": "L'API Mathakine fonctionne correctement",
        "version": "0.1.0"
    })

async def api_exercises(request):
    """Retourne la liste des exercices"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Récupérer les paramètres de requête
        limit = int(request.query_params.get('limit', 10))
        skip = int(request.query_params.get('skip', 0))
        
        cursor.execute("SELECT * FROM exercises LIMIT ? OFFSET ?", (limit, skip))
        exercises = [dict(row) for row in cursor.fetchall()]
        
        # Calculer le total
        cursor.execute("SELECT COUNT(*) FROM exercises")
        total = cursor.fetchone()[0]
        
        conn.close()
        
        # Traiter les choix JSON
        for ex in exercises:
            if 'choices' in ex and ex['choices']:
                try:
                    ex['choices'] = json.loads(ex['choices']) if isinstance(ex['choices'], str) else ex['choices']
                except:
                    ex['choices'] = []
            else:
                ex['choices'] = []
        
        return JSONResponse({
            "items": exercises,
            "total": total,
            "skip": skip,
            "limit": limit
        })
    except Exception as e:
        print(f"Erreur lors de la récupération des exercices: {e}")
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)

async def api_submit_answer(request):
    """Traite la soumission d'une réponse"""
    try:
        data = await request.json()
        exercise_id = data.get('exercise_id')
        selected_answer = data.get('selected_answer')
        
        # Récupérer l'exercice pour vérifier la réponse
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM exercises WHERE id = ?", (exercise_id,))
        exercise = cursor.fetchone()
        
        if not exercise:
            conn.close()
            return JSONResponse({"error": "Exercice non trouvé"}, status_code=404)
        
        exercise = dict(exercise)
        is_correct = selected_answer == exercise['correct_answer']
        
        # Simuler l'enregistrement du résultat
        conn.close()
        
        return JSONResponse({
            "is_correct": is_correct,
            "correct_answer": exercise['correct_answer'],
            "explanation": exercise.get('explanation', "")
        })
    except Exception as e:
        print(f"Erreur lors du traitement de la réponse: {e}")
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)

async def api_stats(request):
    """Retourne les statistiques de l'utilisateur"""
    # Simuler des statistiques
    response_data = {
        'total_exercises': 42,
        'correct_answers': 36,
        'success_rate': 85,
        'experience_points': 420,
        'performance_by_type': {
            'addition': {'completed': 20, 'correct': 18, 'success_rate': 90},
            'soustraction': {'completed': 15, 'correct': 12, 'success_rate': 80},
            'multiplication': {'completed': 7, 'correct': 6, 'success_rate': 85},
            'division': {'completed': 0, 'correct': 0, 'success_rate': 0}
        },
        'recent_activity': [
            {'type': 'exercise_completed', 'is_correct': True, 'description': 'Réussite : 2 + 2 = ?', 'time': '01/06/2023 14:35'},
            {'type': 'exercise_completed', 'is_correct': True, 'description': 'Réussite : 8 - 3 = ?', 'time': '01/06/2023 14:33'},
            {'type': 'exercise_completed', 'is_correct': False, 'description': 'Échec : 7 x 8 = ?', 'time': '01/06/2023 14:30'}
        ],
    }
    
    return JSONResponse(response_data)

# Routes
routes = [
    Route("/", homepage),
    Route("/exercises", exercises_page),
    Route("/dashboard", dashboard_page),
    Route("/exercise/{exercise_id:int}", exercise_detail),
    
    # Routes API
    Route("/api/health", api_health),
    Route("/api/exercises", api_exercises),
    Route("/api/submit", api_submit_answer, methods=["POST"]),
    Route("/api/stats", api_stats),
    
    # Fichiers statiques
    Mount("/static", StaticFiles(directory="static"), name="static")
]

# Application Starlette
app = Starlette(debug=DEBUG, routes=routes)

# Point d'entrée principal
if __name__ == "__main__":
    print("========================================")
    print(f"ATTENTION: Démarrage de FIXED_SERVER.PY - Version simplifiée sur le port {PORT}")
    print("Ce n'est PAS le serveur enhanced_server.py")
    print("========================================")
    uvicorn.run(app, host="0.0.0.0", port=PORT, reload=DEBUG) 