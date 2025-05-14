"""
Serveur minimal sans FastAPI pour contourner les problèmes de compatibilité avec Python 3.13
"""

import uvicorn
import sqlite3
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Charger les variables d'environnement depuis le fichier .env s'il existe
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("Variables d'environnement chargées depuis le fichier .env")
except ImportError:
    print("Module dotenv non disponible, utilisation des variables d'environnement système uniquement")

# Créer une application simple avec Starlette
try:
    from starlette.applications import Starlette
    from starlette.responses import JSONResponse, HTMLResponse
    from starlette.routing import Route
    from starlette.middleware import Middleware
    from starlette.middleware.cors import CORSMiddleware
except ImportError:
    print("Installation des dépendances nécessaires...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "starlette==0.27.0", "uvicorn==0.20.0"])
    from starlette.applications import Starlette
    from starlette.responses import JSONResponse, HTMLResponse
    from starlette.routing import Route
    from starlette.middleware import Middleware
    from starlette.middleware.cors import CORSMiddleware

# Configuration de base
DB_PATH = "math_trainer.db"
PORT = int(os.environ.get("MATH_TRAINER_PORT", 8000))  # Utiliser la variable d'environnement
DEBUG = os.environ.get("MATH_TRAINER_DEBUG", "true").lower() == "true"  # Utiliser la variable d'environnement
LOG_LEVEL = os.environ.get("MATH_TRAINER_LOG_LEVEL", "DEBUG")  # Utiliser la variable d'environnement
TEST_MODE = os.environ.get("MATH_TRAINER_TEST_MODE", "false").lower() == "true"  # Utiliser la variable d'environnement
PROFILE = os.environ.get("MATH_TRAINER_PROFILE", "dev")  # Utiliser la variable d'environnement

print(f"Configuration chargée: Port={PORT}, Debug={DEBUG}, Profile={PROFILE}, Log Level={LOG_LEVEL}")

# Vérifier si le port 8000 est disponible, sinon utiliser 8080
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock.bind(('localhost', PORT))
except socket.error:
    print(f"Port {PORT} déjà utilisé, utilisation du port 8080")
    PORT = 8080
finally:
    sock.close()

# Initialiser la base de données
def init_db():
    # Créer le fichier .env s'il n'existe pas
    if not Path('.env').exists():
        with open('.env', 'w') as f:
            f.write(f"MATH_TRAINER_DEBUG={DEBUG}\n")
            f.write(f"MATH_TRAINER_PORT={PORT}\n")
            f.write(f"MATH_TRAINER_LOG_LEVEL={LOG_LEVEL}\n")
            f.write(f"MATH_TRAINER_TEST_MODE={TEST_MODE}\n")
            f.write(f"MATH_TRAINER_PROFILE={PROFILE}\n")
            f.write(f"DATABASE_URL=sqlite:///./{DB_PATH}\n")
        print("Fichier .env créé")

    # Vérifier si la base de données existe, sinon la créer
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Créer la table exercises si elle n'existe pas
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS exercises (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        correct_answer TEXT NOT NULL,
        choices TEXT,
        explanation TEXT,
        exercise_type TEXT NOT NULL,
        difficulty TEXT DEFAULT 'easy',
        is_archived BOOLEAN DEFAULT 0,
        is_completed BOOLEAN DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Créer la table results si elle n'existe pas
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exercise_id INTEGER,
        is_correct BOOLEAN DEFAULT 0,
        attempt_count INTEGER DEFAULT 1,
        time_spent REAL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (exercise_id) REFERENCES exercises (id)
    )
    ''')
    
    # Vérifier s'il y a des données de test
    cursor.execute("SELECT COUNT(*) FROM exercises")
    count = cursor.fetchone()[0]
    
    # Ajouter des données de test si la table est vide
    if count == 0:
        cursor.execute('''
        INSERT INTO exercises (question, correct_answer, choices, explanation, exercise_type, difficulty)
        VALUES 
        ('Combien font 2 + 2 ?', '4', '[1, 2, 3, 4]', '2 + 2 = 4', 'addition', 'easy'),
        ('Combien font 5 - 3 ?', '2', '[1, 2, 3, 4]', '5 - 3 = 2', 'subtraction', 'easy'),
        ('Combien font 3 × 4 ?', '12', '[10, 11, 12, 13]', '3 × 4 = 12', 'multiplication', 'medium')
        ''')
    
    conn.commit()
    conn.close()
    print("Base de données initialisée avec succès")

# Handlers pour les routes
async def homepage(request):
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mathakine API</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            h1 { color: #333; }
            .card { border: 1px solid #ddd; border-radius: 5px; padding: 15px; margin-bottom: 15px; }
            .endpoints { list-style-type: none; padding: 0; }
            .endpoints li { margin-bottom: 10px; }
            a { color: #0066cc; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>Mathakine API</h1>
        <div class="card">
            <p>Bienvenue sur l'API Mathakine - Version minimale compatible avec Python 3.13</p>
            <p>Cette version est une solution de contournement des problèmes de compatibilité entre FastAPI et Python 3.13.</p>
        </div>
        <div class="card">
            <h2>Endpoints disponibles :</h2>
            <ul class="endpoints">
                <li><a href="/api/exercises">/api/exercises</a> - Liste des exercices</li>
                <li><a href="/api/exercises/generate">/api/exercises/generate</a> - Générer un nouvel exercice</li>
                <li><a href="/debug">/debug</a> - Informations de débogage</li>
            </ul>
        </div>
    </body>
    </html>
    """)

async def debug_info(request):
    info = {
        "app_name": "Mathakine (Version minimale)",
        "debug_mode": DEBUG,
        "profile": PROFILE,
        "log_level": LOG_LEVEL,
        "port": PORT,
        "database_path": DB_PATH,
        "python_version": sys.version,
        "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "test_mode": TEST_MODE,
        "environment": dict(os.environ)
    }
    return JSONResponse(info)

async def get_exercises(request):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM exercises WHERE is_archived = 0 LIMIT 10")
    rows = cursor.fetchall()
    
    exercises = []
    for row in rows:
        exercise = dict(row)
        if exercise['choices']:
            exercise['choices'] = json.loads(exercise['choices'])
        exercises.append(exercise)
    
    conn.close()
    
    return JSONResponse({
        "items": exercises,
        "total": len(exercises),
        "skip": 0,
        "limit": 10
    })

async def generate_exercise(request):
    import random
    
    # Types d'exercices disponibles
    exercise_types = ["addition", "subtraction", "multiplication"]
    exercise_type = random.choice(exercise_types)
    
    # Génération de l'exercice
    if exercise_type == "addition":
        num1 = random.randint(1, 20)
        num2 = random.randint(1, 20)
        result = num1 + num2
        question = f"Combien font {num1} + {num2} ?"
        explanation = f"{num1} + {num2} = {result}"
    elif exercise_type == "subtraction":
        num1 = random.randint(10, 30)
        num2 = random.randint(1, num1)
        result = num1 - num2
        question = f"Combien font {num1} - {num2} ?"
        explanation = f"{num1} - {num2} = {result}"
    else:  # multiplication
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        result = num1 * num2
        question = f"Combien font {num1} × {num2} ?"
        explanation = f"{num1} × {num2} = {result}"
    
    # Génération des choix
    correct_answer = str(result)
    choices = [result]
    while len(choices) < 4:
        fake = result + random.randint(-5, 5)
        if fake != result and fake not in choices and fake > 0:
            choices.append(fake)
    random.shuffle(choices)
    
    # Enregistrement en base de données
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO exercises (question, correct_answer, choices, explanation, exercise_type, difficulty)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (question, correct_answer, json.dumps(choices), explanation, exercise_type, 'easy'))
    
    exercise_id = cursor.lastrowid
    
    conn.commit()
    
    # Récupération de l'exercice créé
    cursor.execute("SELECT * FROM exercises WHERE id = ?", (exercise_id,))
    row = cursor.fetchone()
    
    conn.close()
    
    # Formatage du résultat
    exercise = {
        "id": row[0],
        "question": row[1],
        "correct_answer": row[2],
        "choices": json.loads(row[3]) if row[3] else None,
        "explanation": row[4],
        "exercise_type": row[5],
        "difficulty": row[6],
        "is_archived": bool(row[7]),
        "is_completed": bool(row[8]),
        "created_at": row[9]
    }
    
    return JSONResponse(exercise)

async def status(request):
    """Endpoint simple pour vérifier que le serveur fonctionne"""
    return JSONResponse({"status": "OK", "profile": PROFILE, "port": PORT})

# Création de l'application
routes = [
    Route("/", homepage),
    Route("/debug", debug_info),
    Route("/status", status),
    Route("/api/exercises", get_exercises),
    Route("/api/exercises/generate", generate_exercise)
]

middleware = [
    Middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
]

app = Starlette(debug=DEBUG, routes=routes, middleware=middleware)

# Fonction principale
def main():
    # S'assurer que nous sommes dans le bon répertoire
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir:
        os.chdir(script_dir)
    
    # Initialiser la base de données
    init_db()
    
    # Démarrer le serveur
    print(f"Démarrage du serveur sur le port {PORT}...")
    print(f"Profil d'environnement: {PROFILE}")
    print(f"Mode Debug: {DEBUG}")
    print(f"Niveau de log: {LOG_LEVEL}")
    print(f"Mode Test: {TEST_MODE}")
    print(f"L'API sera accessible à l'adresse: http://localhost:{PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level=LOG_LEVEL.lower())

if __name__ == "__main__":
    main()