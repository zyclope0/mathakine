"""
Serveur amélioré avec plus de fonctionnalités mais sans FastAPI pour compatibilité Python 3.13
"""

import uvicorn
import sqlite3
import json
import os
import sys
import random
import traceback  # Ajout pour le debug
import requests  # Pour les appels API
import uuid  # Pour générer des identifiants uniques
from pathlib import Path
from datetime import datetime

# Charger les variables d'environnement depuis le fichier .env s'il existe
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("Variables d'environnement chargées depuis le fichier .env")
except ImportError:
    print("Module dotenv non disponible, utilisation des variables d'environnement système uniquement")

# Créer une application avec Starlette
try:
    from starlette.applications import Starlette
    from starlette.responses import JSONResponse, HTMLResponse, RedirectResponse
    from starlette.routing import Route, Mount
    from starlette.middleware import Middleware
    from starlette.middleware.cors import CORSMiddleware
    from starlette.staticfiles import StaticFiles
    from starlette.templating import Jinja2Templates
    from starlette.requests import Request
except ImportError:
    print("Installation des dépendances nécessaires...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", 
                          "starlette==0.27.0", 
                          "uvicorn==0.20.0",
                          "jinja2==3.1.2",
                          "aiofiles==23.2.1"])
    from starlette.applications import Starlette
    from starlette.responses import JSONResponse, HTMLResponse, RedirectResponse
    from starlette.routing import Route, Mount
    from starlette.middleware import Middleware
    from starlette.middleware.cors import CORSMiddleware
    from starlette.staticfiles import StaticFiles
    from starlette.templating import Jinja2Templates
    from starlette.requests import Request

# Configuration de base
DB_PATH = "math_trainer.db"
PORT = int(os.environ.get("MATH_TRAINER_PORT", 8081))  # Utiliser la variable d'environnement
DEBUG = os.environ.get("MATH_TRAINER_DEBUG", "true").lower() == "true"  # Utiliser la variable d'environnement
LOG_LEVEL = os.environ.get("MATH_TRAINER_LOG_LEVEL", "DEBUG")  # Utiliser la variable d'environnement
TEST_MODE = os.environ.get("MATH_TRAINER_TEST_MODE", "false").lower() == "true"  # Utiliser la variable d'environnement
PROFILE = os.environ.get("MATH_TRAINER_PROFILE", "dev")  # Utiliser la variable d'environnement

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")

print(f"Configuration chargée: Port={PORT}, Debug={DEBUG}, Profile={PROFILE}, Log Level={LOG_LEVEL}")

# Configuration de l'API IA (utilisation d'OpenAI comme exemple)
# Cette clé est un placeholder. Dans un déploiement réel, elle doit être stockée en sécurité
API_KEY = os.environ.get("OPENAI_API_KEY", "")
USE_AI_GENERATION = bool(API_KEY)  # Utiliser la génération IA seulement si une clé API est disponible

# Vérifier si le port est disponible, sinon utiliser 8082
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock.bind(('localhost', PORT))
except socket.error:
    print(f"Port {PORT} déjà utilisé, utilisation du port 8082")
    PORT = 8082
finally:
    sock.close()

# Créer les dossiers pour les templates et fichiers statiques s'ils n'existent pas
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)
    
    # Créer un CSS de base
    css_file = os.path.join(STATIC_DIR, "style.css")
    with open(css_file, "w") as f:
        f.write("""
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
        }
        header {
            background-color: #4CAF50;
            color: white;
            padding: 1rem;
            text-align: center;
            margin-bottom: 2rem;
            border-radius: 5px;
        }
        .container {
            padding: 20px;
        }
        .card {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .exercise {
            background-color: #f9f9f9;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 1rem;
        }
        .btn {
            display: inline-block;
            background: #4CAF50;
            color: #fff;
            border: none;
            padding: 10px 20px;
            cursor: pointer;
            text-decoration: none;
            font-size: 16px;
            border-radius: 5px;
        }
        .btn-secondary {
            background: #6c757d;
        }
        .choice-btn {
            display: block;
            width: 100%;
            text-align: left;
            margin-bottom: 10px;
            padding: 10px;
            background-color: #f0f0f0;
            border: 1px solid #ddd;
            border-radius: 5px;
            cursor: pointer;
        }
        .choice-btn:hover {
            background-color: #e0e0e0;
        }
        .choice-btn.correct {
            background-color: #d4edda;
            border-color: #c3e6cb;
            color: #155724;
        }
        .choice-btn.incorrect {
            background-color: #f8d7da;
            border-color: #f5c6cb;
            color: #721c24;
        }
        .explanation {
            padding: 15px;
            margin-top: 15px;
            background-color: #e8f4f8;
            border-radius: 5px;
            border-left: 5px solid #5bc0de;
        }
        """)
    print(f"Fichier CSS créé dans {STATIC_DIR}")

if not os.path.exists(TEMPLATES_DIR):
    os.makedirs(TEMPLATES_DIR)
    
    # Créer un template HTML de base
    base_template = os.path.join(TEMPLATES_DIR, "base.html")
    with open(base_template, "w") as f:
        f.write("""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{% block title %}Mathakine{% endblock %}</title>
            <link rel="stylesheet" href="/static/style.css">
        </head>
        <body>
            <header>
                <h1>Mathakine</h1>
                <nav>
                    <a href="/" class="btn">Accueil</a>
                    <a href="/exercises" class="btn">Exercices</a>
                    <a href="/api/exercises/generate" class="btn">Nouvel exercice</a>
                </nav>
            </header>
            <div class="container">
                {% block content %}{% endblock %}
            </div>
            <script>
                // JavaScript commun
                document.addEventListener('DOMContentLoaded', function() {
                    console.log('App loaded');
                });
            </script>
            {% block scripts %}{% endblock %}
        </body>
        </html>
        """)
    
    # Template pour la page d'accueil
    home_template = os.path.join(TEMPLATES_DIR, "home.html")
    with open(home_template, "w") as f:
        f.write("""
        {% extends "base.html" %}
        
        {% block title %}Accueil - Mathakine{% endblock %}
        
        {% block content %}
        <div class="card">
            <h2>Bienvenue sur Mathakine</h2>
            <p>Améliorez vos compétences en mathématiques avec notre application d'exercices interactifs.</p>
            <a href="/exercises" class="btn">Voir les exercices</a>
            <a href="/api/exercises/generate" class="btn">Générer un nouvel exercice</a>
        </div>
        <div class="card">
            <h3>Fonctionnalités</h3>
            <ul>
                <li>Exercices de maths générés automatiquement</li>
                <li>Différents types d'opérations : additions, soustractions, multiplications</li>
                <li>Niveau de difficulté adapté</li>
                <li>Suivi de vos résultats</li>
            </ul>
        </div>
        {% endblock %}
        """)
    
    # Template pour la liste des exercices
    exercises_template = os.path.join(TEMPLATES_DIR, "exercises.html")
    with open(exercises_template, "w") as f:
        f.write("""
        {% extends "base.html" %}
        
        {% block title %}Exercices - Mathakine{% endblock %}
        
        {% block content %}
        <h2>Liste des exercices</h2>
        <div class="card">
            <a href="/api/exercises/generate" class="btn">Générer un nouvel exercice</a>
        </div>
        
        {% for exercise in exercises %}
        <div class="card exercise">
            <h3>{{ exercise.question }}</h3>
            <div class="choices">
                {% for choice in exercise.choices %}
                <button class="choice-btn" data-value="{{ choice }}" data-correct="{{ exercise.correct_answer }}">
                    {{ choice }}
                </button>
                {% endfor %}
            </div>
            <div class="explanation" style="display: none;">
                <strong>Explication:</strong> {{ exercise.explanation }}
            </div>
        </div>
        {% endfor %}
        
        {% if not exercises %}
        <div class="card">
            <p>Aucun exercice disponible. Générez-en un nouveau !</p>
        </div>
        {% endif %}
        {% endblock %}
        
        {% block scripts %}
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                const choiceButtons = document.querySelectorAll('.choice-btn');
                
                choiceButtons.forEach(button => {
                    button.addEventListener('click', function() {
                        const selectedValue = this.getAttribute('data-value');
                        const correctAnswer = this.getAttribute('data-correct');
                        const explanation = this.closest('.exercise').querySelector('.explanation');
                        
                        // Reset all buttons in this exercise
                        const siblings = this.closest('.choices').querySelectorAll('.choice-btn');
                        siblings.forEach(btn => {
                            btn.classList.remove('correct', 'incorrect');
                        });
                        
                        // Mark the current button
                        if (selectedValue === correctAnswer) {
                            this.classList.add('correct');
                        } else {
                            this.classList.add('incorrect');
                            // Find and mark the correct answer
                            siblings.forEach(btn => {
                                if (btn.getAttribute('data-value') === correctAnswer) {
                                    btn.classList.add('correct');
                                }
                            });
                        }
                        
                        // Show explanation
                        explanation.style.display = 'block';
                    });
                });
            });
        </script>
        {% endblock %}
        """)
    
    print(f"Templates HTML créés dans {TEMPLATES_DIR}")

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
    
    # Créer la table user_stats si elle n'existe pas (nouvelle)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exercise_type TEXT NOT NULL,
        difficulty TEXT NOT NULL,
        total_attempts INTEGER DEFAULT 0,
        correct_attempts INTEGER DEFAULT 0,
        last_updated TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Vérifier si les statistiques utilisateur sont vides
    cursor.execute("SELECT COUNT(*) FROM user_stats")
    stats_count = cursor.fetchone()[0]
    
    if stats_count == 0:
        for exercise_type in ['addition', 'subtraction', 'multiplication', 'division']:
            for difficulty in ['easy', 'medium', 'hard']:
                cursor.execute('''
                INSERT INTO user_stats (exercise_type, difficulty, total_attempts, correct_attempts)
                VALUES (?, ?, 0, 0)
                ''', (exercise_type, difficulty))
    
    conn.commit()
    conn.close()
    print("Base de données initialisée avec succès")

# Templates pour le rendu HTML
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Handlers pour les routes
async def homepage(request):
    return templates.TemplateResponse("home.html", {"request": request})

async def exercises_page(request):
    # Vérifier si nous venons d'une génération d'exercices
    just_generated = request.query_params.get('generated', 'false') == 'true'
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Récupérer les exercices les plus récents en priorité
    cursor.execute("SELECT * FROM exercises WHERE is_archived = 0 ORDER BY id DESC LIMIT 10")
    rows = cursor.fetchall()
    
    exercises = []
    for row in rows:
        exercise = dict(row)
        if exercise['choices']:
            exercise['choices'] = json.loads(exercise['choices'])
        exercises.append(exercise)
    
    conn.close()
    
    return templates.TemplateResponse("exercises.html", {
        "request": request,
        "exercises": exercises,
        "just_generated": just_generated
    })

async def debug_info(request):
    info = {
        "app_name": "Mathakine (Version améliorée)",
        "debug_mode": DEBUG,
        "profile": PROFILE,
        "log_level": LOG_LEVEL,
        "port": PORT,
        "database_path": DB_PATH,
        "python_version": sys.version,
        "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "templates_dir": TEMPLATES_DIR,
        "static_dir": STATIC_DIR,
        "test_mode": TEST_MODE,
        "ai_generation": USE_AI_GENERATION
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

async def dashboard(request):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Récupérer les statistiques globales
    cursor.execute('''
    SELECT 
        SUM(total_attempts) as total_completed,
        SUM(correct_attempts) as correct_answers
    FROM user_stats
    ''')
    overall_stats = cursor.fetchone()
    
    # Calculer le taux de réussite
    total_completed = overall_stats['total_completed'] or 0
    correct_answers = overall_stats['correct_answers'] or 0
    success_rate = int((correct_answers / total_completed * 100) if total_completed > 0 else 0)
    
    # Récupérer les statistiques par type d'exercice
    stats = {
        'total_completed': total_completed,
        'correct_answers': correct_answers,
        'success_rate': success_rate,
    }
    
    for exercise_type in ['addition', 'subtraction', 'multiplication', 'division']:
        cursor.execute('''
        SELECT 
            SUM(total_attempts) as total,
            SUM(correct_attempts) as correct
        FROM user_stats
        WHERE exercise_type = ?
        ''', (exercise_type,))
        type_stats = cursor.fetchone()
        
        total = type_stats['total'] or 0
        correct = type_stats['correct'] or 0
        
        stats[f'{exercise_type}_total'] = total
        stats[f'{exercise_type}_correct'] = correct
        stats[f'{exercise_type}_progress'] = int((correct / total * 100) if total > 0 else 0)
    
    # Récupérer les exercices récents
    cursor.execute('''
    SELECT 
        e.question,
        r.is_correct,
        r.created_at as completed_at
    FROM results r
    JOIN exercises e ON r.exercise_id = e.id
    ORDER BY r.created_at DESC
    LIMIT 10
    ''')
    recent_exercises = cursor.fetchall()
    
    conn.close()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "stats": stats,
        "recent_exercises": recent_exercises
    })

async def submit_answer(request):
    data = await request.json()
    exercise_id = data.get('exercise_id')
    selected_answer = data.get('selected_answer')
    time_spent = data.get('time_spent', 0)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Récupérer l'exercice
    cursor.execute("SELECT * FROM exercises WHERE id = ?", (exercise_id,))
    exercise = cursor.fetchone()
    
    if not exercise:
        conn.close()
        return JSONResponse({"error": "Exercice non trouvé"}, status_code=404)
    
    is_correct = selected_answer == exercise['correct_answer']
    
    # Enregistrer le résultat
    cursor.execute('''
    INSERT INTO results (exercise_id, is_correct, time_spent)
    VALUES (?, ?, ?)
    ''', (exercise_id, is_correct, time_spent))
    
    # Mettre à jour les statistiques utilisateur
    cursor.execute('''
    UPDATE user_stats
    SET 
        total_attempts = total_attempts + 1,
        correct_attempts = correct_attempts + CASE WHEN ? THEN 1 ELSE 0 END,
        last_updated = CURRENT_TIMESTAMP
    WHERE exercise_type = ? AND difficulty = ?
    ''', (is_correct, exercise['exercise_type'], exercise['difficulty']))
    
    # Marquer l'exercice comme complété
    cursor.execute('''
    UPDATE exercises
    SET is_completed = 1
    WHERE id = ?
    ''', (exercise_id,))
    
    conn.commit()
    conn.close()
    
    return JSONResponse({
        "is_correct": is_correct,
        "correct_answer": exercise['correct_answer'],
        "explanation": exercise['explanation']
    })

# Fonction pour générer un exercice via une API d'IA
async def generate_ai_exercise(exercise_type, difficulty, age=9):
    """
    Génère un exercice mathématique en utilisant une API d'IA.
    """
    if not USE_AI_GENERATION:
        return None
    
    try:
        prompt = f"""
        Crée un exercice de mathématiques de type {exercise_type} avec un niveau de difficulté {difficulty} 
        pour un enfant autiste de {age} ans. Format de réponse en JSON avec les champs suivants:
        {{
            "question": "L'énoncé de l'exercice",
            "choices": [choix1, choix2, choix3, choix4],
            "correct_answer": "Le bon choix",
            "explanation": "Explication adaptée pour un enfant autiste"
        }}
        Pour les exercices de division, assure-toi que ce soit adapté au niveau de l'enfant.
        """
        
        # Appel à l'API OpenAI
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }
        
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 300
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # Extraire le JSON de la réponse
            import re
            json_match = re.search(r'({.*})', content, re.DOTALL)
            if json_match:
                exercise_data = json.loads(json_match.group(1))
                return exercise_data
        
        print(f"Erreur lors de l'appel à l'API IA: {response.status_code} - {response.text}")
        return None
    
    except Exception as e:
        print(f"Exception lors de la génération d'exercice IA: {e}")
        traceback.print_exc()
        return None

# Modification de la fonction de génération d'exercice
async def generate_exercise(request):
    # Récupérer les paramètres de requête
    params = dict(request.query_params)
    exercise_type = params.get('type')
    difficulty = params.get('difficulty', 'easy')
    use_ai = params.get('ai', 'false').lower() == 'true'
    
    # Si l'IA est activée et disponible, utiliser la génération IA
    ai_exercise = None
    if use_ai and USE_AI_GENERATION:
        ai_exercise = await generate_ai_exercise(exercise_type, difficulty)
    
    # Si l'IA n'est pas activée ou a échoué, continuer avec la génération algorithmique standard
    if ai_exercise:
        question = ai_exercise['question']
        choices = ai_exercise['choices']
        correct_answer = str(ai_exercise['correct_answer'])
        explanation = ai_exercise['explanation']
        
        # Si le type n'est pas spécifié, essayer de le déduire de la question
        if not exercise_type:
            if '+' in question:
                exercise_type = 'addition'
            elif '-' in question:
                exercise_type = 'subtraction'
            elif '×' in question or 'x' in question or '*' in question:
                exercise_type = 'multiplication'
            elif '÷' in question or '/' in question:
                exercise_type = 'division'
            else:
                exercise_type = 'unknown'
    else:
        # Génération algorithmique standard (code existant)
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Si l'exercice recommandé est demandé, trouver le type avec le plus faible taux de réussite
        if exercise_type == 'recommended':
            cursor.execute('''
            SELECT 
                exercise_type,
                SUM(correct_attempts) * 100.0 / CASE WHEN SUM(total_attempts) > 0 THEN SUM(total_attempts) ELSE 1 END as success_rate
            FROM user_stats
            GROUP BY exercise_type
            ORDER BY success_rate ASC
            LIMIT 1
            ''')
            result = cursor.fetchone()
            exercise_type = result['exercise_type'] if result else None
        
        # Déterminer le niveau de difficulté adaptatif si non spécifié
        if difficulty == 'adaptive':
            if exercise_type:
                cursor.execute('''
                SELECT 
                    difficulty,
                    SUM(correct_attempts) * 100.0 / CASE WHEN SUM(total_attempts) > 0 THEN SUM(total_attempts) ELSE 1 END as success_rate
                FROM user_stats
                WHERE exercise_type = ?
                GROUP BY difficulty
                ''', (exercise_type,))
                difficulties = cursor.fetchall()
                
                # Logique adaptative: si plus de 80% de réussite, augmenter la difficulté
                for diff in difficulties:
                    if diff['difficulty'] == 'easy' and diff['success_rate'] > 80:
                        difficulty = 'medium'
                    elif diff['difficulty'] == 'medium' and diff['success_rate'] > 80:
                        difficulty = 'hard'
                    else:
                        difficulty = 'easy'
            else:
                difficulty = 'easy'
        
        # Types d'exercices disponibles
        available_types = ["addition", "subtraction", "multiplication", "division"]
        if not exercise_type or exercise_type not in available_types:
            exercise_type = random.choice(available_types)
        
        # Initialiser les variables
        explanation = ""
        
        # Génération de l'exercice en fonction du type et de la difficulté
        if exercise_type == "addition":
            if difficulty == "easy":
                num1 = random.randint(1, 10)
                num2 = random.randint(1, 10)
            elif difficulty == "medium":
                num1 = random.randint(10, 50)
                num2 = random.randint(10, 50)
            else:  # hard
                num1 = random.randint(50, 100)
                num2 = random.randint(50, 100)
            
            result = num1 + num2
            question = f"Combien font {num1} + {num2} ?"
            explanation = f"{num1} + {num2} = {result}"
        
        elif exercise_type == "subtraction":
            if difficulty == "easy":
                num2 = random.randint(1, 10)
                num1 = random.randint(num2, 20)
            elif difficulty == "medium":
                num2 = random.randint(10, 30)
                num1 = random.randint(num2, 50)
            else:  # hard
                num2 = random.randint(20, 50)
                num1 = random.randint(num2, 100)
            
            result = num1 - num2
            question = f"Combien font {num1} - {num2} ?"
            explanation = f"{num1} - {num2} = {result}"
        
        elif exercise_type == "multiplication":
            if difficulty == "easy":
                num1 = random.randint(1, 5)
                num2 = random.randint(1, 5)
            elif difficulty == "medium":
                num1 = random.randint(2, 10)
                num2 = random.randint(2, 10)
            else:  # hard
                num1 = random.randint(5, 15)
                num2 = random.randint(5, 15)
            
            result = num1 * num2
            question = f"Combien font {num1} × {num2} ?"
            explanation = f"{num1} × {num2} = {result}"
        
        elif exercise_type == "division":
            remainder = 0  # Initialiser remainder pour tous les cas
            if difficulty == "easy":
                # Diviseurs faciles: 2, 5, 10
                divisor = random.choice([2, 5, 10])
                quotient = random.randint(1, 10)
                dividend = divisor * quotient
                explanation = f"{dividend} ÷ {divisor} = {quotient}"
            elif difficulty == "medium":
                # Divisions sans reste
                divisor = random.randint(2, 10)
                quotient = random.randint(1, 10)
                dividend = divisor * quotient
                explanation = f"{dividend} ÷ {divisor} = {quotient}"
            else:  # hard
                # Divisions avec reste
                divisor = random.randint(3, 12)
                quotient = random.randint(1, 10)
                remainder = random.randint(0, divisor - 1)
                dividend = divisor * quotient + remainder
                
                explanation = f"{dividend} ÷ {divisor} = {quotient}" + (f" avec un reste de {remainder}" if remainder > 0 else "")
            
            if difficulty == "hard" and remainder != 0:
                question = f"Combien font {dividend} ÷ {divisor} ? (Donne le quotient sans le reste)"
            else:
                question = f"Combien font {dividend} ÷ {divisor} ?"
                
            result = quotient
        
        # Génération des choix
        correct_answer = str(result)
        choices = [result]
        
        # Génération de distracteurs plus pertinents en fonction du type d'exercice
        if exercise_type == "addition":
            # Erreurs courantes en addition
            choices.extend([
                result + 1,  # Erreur de comptage
                result - 1,  # Erreur de comptage
                result + 10,  # Erreur de retenue
            ])
        elif exercise_type == "subtraction":
            # Erreurs courantes en soustraction
            choices.extend([
                result + 1,
                result - 1,
                num2 - num1  # Inversion des nombres
            ])
        elif exercise_type == "multiplication":
            # Erreurs courantes en multiplication
            choices.extend([
                result + num1,  # Ajout au lieu de multiplication
                result - num2,  # Erreur de calcul
                num1 + num2  # Addition au lieu de multiplication
            ])
        else:  # division
            # Erreurs courantes en division
            choices.extend([
                dividend // 10,  # Erreur de virgule
                divisor,  # Confusion entre diviseur et quotient
                dividend - divisor  # Soustraction au lieu de division
            ])
        
        # Enlever les doublons et les valeurs négatives ou nulles
        choices = list(set(choices))
        choices = [c for c in choices if c > 0]
        
        # S'assurer d'avoir exactement 4 choix
        while len(choices) < 4:
            fake = result + random.randint(-5, 5)
            if fake > 0 and fake not in choices:
                choices.append(fake)
        
        # Si plus de 4 choix, garder le correct et 3 autres aléatoires
        if len(choices) > 4:
            other_choices = [c for c in choices if c != result]
            random.shuffle(other_choices)
            choices = [result] + other_choices[:3]
        
        random.shuffle(choices)
        
        conn.close()
    
    # Enregistrement en base de données
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Enregistrement en base de données
    cursor.execute('''
    INSERT INTO exercises (question, correct_answer, choices, explanation, exercise_type, difficulty)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (question, correct_answer, json.dumps(choices), explanation, exercise_type, difficulty))
    
    exercise_id = cursor.lastrowid
    
    # Récupération de l'exercice créé
    cursor.execute("SELECT * FROM exercises WHERE id = ?", (exercise_id,))
    row = cursor.fetchone()
    
    conn.commit()
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
        "created_at": row[9],
        "ai_generated": use_ai and ai_exercise is not None
    }
    
    # Rediriger vers la page d'exercices après génération
    if request.headers.get("accept", "").startswith("text/html"):
        return RedirectResponse(url="/exercises?generated=true", status_code=303)
    
    return JSONResponse(exercise)

async def delete_exercise(request):
    data = await request.json()
    exercise_id = data.get('exercise_id')
    
    if not exercise_id:
        return JSONResponse({"error": "ID de l'exercice manquant"}, status_code=400)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Vérifier si l'exercice existe
    cursor.execute("SELECT id FROM exercises WHERE id = ?", (exercise_id,))
    exercise = cursor.fetchone()
    
    if not exercise:
        conn.close()
        return JSONResponse({"error": "Exercice non trouvé"}, status_code=404)
    
    # Supprimer l'exercice
    cursor.execute("DELETE FROM exercises WHERE id = ?", (exercise_id,))
    
    # Supprimer les résultats associés
    cursor.execute("DELETE FROM results WHERE exercise_id = ?", (exercise_id,))
    
    conn.commit()
    conn.close()
    
    return JSONResponse({"success": True, "message": "Exercice supprimé avec succès"})

# Création de l'application
routes = [
    Route("/", homepage),
    Route("/debug", debug_info),
    Route("/exercises", exercises_page),
    Route("/dashboard", dashboard),
    Route("/api/exercises", get_exercises),
    Route("/api/exercises/generate", generate_exercise),
    Route("/api/submit-answer", submit_answer, methods=["POST"]),
    Route("/api/delete-exercise", delete_exercise, methods=["POST"]),
    Mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
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
    
    try:
        # Démarrer le serveur
        print(f"Démarrage du serveur amélioré sur le port {PORT}...")
        print(f"Profil d'environnement: {PROFILE}")
        print(f"Mode Debug: {DEBUG}")
        print(f"Niveau de log: {LOG_LEVEL}")
        print(f"Mode Test: {TEST_MODE}")
        print(f"Interface utilisateur disponible à l'adresse: http://localhost:{PORT}")
        print(f"API disponible à l'adresse: http://localhost:{PORT}/api/exercises")
        uvicorn.run(app, host="0.0.0.0", port=PORT, log_level=LOG_LEVEL.lower())
    except Exception as e:
        print(f"Erreur lors du démarrage du serveur: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main() 