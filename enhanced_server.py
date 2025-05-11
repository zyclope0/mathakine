"""
Serveur amélioré avec plus de fonctionnalités mais sans FastAPI pour compatibilité Python 3.13
"""

import uvicorn
import psycopg2
import json
import os
import sys
import random
import traceback
import requests
from pathlib import Path
from datetime import datetime
from starlette.applications import Starlette
from starlette.responses import JSONResponse, HTMLResponse, RedirectResponse
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.templating import Jinja2Templates

# Import des constantes et messages centralisés
from app.core.constants import ExerciseTypes, DifficultyLevels, DISPLAY_NAMES, DIFFICULTY_LIMITS, Messages, Tags
from app.core.messages import SystemMessages, ExerciseMessages, InterfaceTexts
from app.db.queries import ExerciseQueries, ResultQueries, UserStatsQueries

# Chemins et configurations
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = str(BASE_DIR / 'static')
TEMPLATES_DIR = str(BASE_DIR / 'templates')
DATABASE_URL = os.environ.get("DATABASE_URL", "")

# Autres configurations
PORT = int(os.environ.get("PORT", 8000))
DEBUG = os.environ.get("MATH_TRAINER_DEBUG", "true").lower() == "true"
LOG_LEVEL = os.environ.get("MATH_TRAINER_LOG_LEVEL", "DEBUG")

# Vérifier la configuration de la base de données
print(f"Mode Base de données: PostgreSQL")
if not DATABASE_URL:
    print("⚠️ ERREUR: Variable DATABASE_URL non définie")
    sys.exit(1)

# Middleware CORS pour permettre les requêtes cross-origin
middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
]

# Fonction pour obtenir une connexion à la base de données PostgreSQL


def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        return conn
    except Exception as e:
        print(f"Erreur de connexion à PostgreSQL: {e}")
        raise e

# Templates pour le rendu HTML
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Ajouter le filtre tojson
templates.env.filters["tojson"] = lambda obj: json.dumps(obj)

# Génération de templates manquants


def generate_template_files():
    """Génère les fichiers de template manquants s'ils n'existent pas"""
    if not os.path.exists(TEMPLATES_DIR):
        os.makedirs(TEMPLATES_DIR)

    # Créer une page d'erreur
    error_template = os.path.join(TEMPLATES_DIR, "error.html")
    if not os.path.exists(error_template):
        with open(error_template, "w") as f:
            f.write("""
            {% extends "base.html" %}

{% block title %}Erreur - Mathakine{% endblock %}

            {% block content %}
    <div class="error-container">
        <div class="error-icon">
            <i class="fas fa-exclamation-triangle fa-4x"></i>
            </div>
        <h2 class="error-title">{{ error }}</h2>
        <p class="error-message">{{ message }}</p>
        <div class="error-actions">
            <a href="/" class="btn primary-btn">
                <i class="fas fa-home"></i> Retour à l'accueil
            </a>
            </div>
            </div>
            {% endblock %}

{% block styles %}
<style>
    .error-container {
        background-color: var(--sw-card-bg);
        border-radius: 12px;
        padding: 40px;
        margin: 30px auto;
        max-width: 600px;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
        border: 1px solid var(--sw-card-border);
    }

    .error-icon {
        color: var(--sw-red);
        margin-bottom: 20px;
    }

    .error-title {
        color: var(--sw-gold);
        margin-bottom: 15px;
    }

    .error-message {
        color: var(--sw-text);
        margin-bottom: 30px;
        line-height: 1.6;
    }

    .error-actions {
        margin-top: 20px;
    }
</style>
    {% endblock %}
    """)
        print(f"Template d'erreur créé: {error_template}")

# Handlers pour les routes
async def homepage(request):
    return templates.TemplateResponse("home.html", {"request": request})

async def exercises_page(request):
    # Vérifier si nous venons d'une génération d'exercices
    just_generated = request.query_params.get('generated', 'false') == 'true'
    print(f"Page d'exercices chargée, just_generated={just_generated}")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Requête pour les exercices non archivés
        cursor.execute("SELECT * FROM exercises WHERE is_archived IS NOT TRUE ORDER BY id DESC LIMIT 10")

        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

        exercises = []
        for row in rows:
            exercise = dict(zip(columns, row))

            # Sécuriser le traitement JSON
            if exercise.get('choices'):
                try:
                    # Vérifier si choices est déjà un objet Python (liste)
                    if isinstance(exercise['choices'], list):
                        pass
                    else:
                        exercise['choices'] = json.loads(exercise['choices'])
                except (ValueError, TypeError) as e:
                    print(f"Erreur lors du parsing JSON des choix pour l'exercice {exercise.get('id')}: {e}")
                    exercise['choices'] = []
            else:
                exercise['choices'] = []

            exercises.append(exercise)

    except Exception as e:
        print(f"Erreur lors de la récupération des exercices: {e}")
        traceback.print_exc()
        exercises = []
    finally:
        conn.close()

    return templates.TemplateResponse("exercises.html", {
        "request": request,
        "exercises": exercises,
        "just_generated": just_generated
    })

async def get_exercise(request):
    exercise_id = request.path_params.get('exercise_id')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM exercises WHERE id = %s", (exercise_id,))

    columns = [desc[0] for desc in cursor.description]
    row = cursor.fetchone()

    if not row:
        conn.close()
        return JSONResponse({"error": "Exercice non trouvé"}, status_code=404)

    exercise = dict(zip(columns, row))

    # Sécurisation de l'accès aux données JSON
    if exercise.get('choices'):
        try:
            # Vérifier si choices est déjà un objet Python (liste)
            if isinstance(exercise['choices'], list):
                pass  # Déjà au bon format
            else:
                exercise['choices'] = json.loads(exercise['choices'])
        except (ValueError, TypeError) as e:
            print(f"Erreur lors du parsing JSON des choix pour l'exercice {exercise.get('id')}: {e}")
            exercise['choices'] = []
    else:
        exercise['choices'] = []

    conn.close()

    return JSONResponse(exercise)

async def dashboard(request):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Récupérer les statistiques globales
        cursor.execute('''
        SELECT
            SUM(total_attempts) as total_completed,
            SUM(correct_attempts) as correct_answers
        FROM user_stats
        ''')

        columns = [desc[0] for desc in cursor.description]
        row = cursor.fetchone()
        overall_stats = dict(zip(columns, row)) if row else {"total_completed": 0
            , "correct_answers": 0}

    # Calculer le taux de réussite
        total_completed = overall_stats.get('total_completed', 0) or 0
        correct_answers = overall_stats.get('correct_answers', 0) or 0
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
                WHERE exercise_type = %s
            ''', (exercise_type,))

            columns = [desc[0] for desc in cursor.description]
            row = cursor.fetchone()
            type_stats = dict(zip(columns, row)) if row else {"total": 0, "correct": 0}

            total = type_stats.get('total', 0) or 0
            correct = type_stats.get('correct', 0) or 0

            stats[f'{exercise_type}_total'] = total
            stats[f'{exercise_type}_correct'] = correct
            stats[f'{exercise_type}_progress'] = int((correct / total * 100) if total > 0 else 0)

    # Récupérer les exercices récents
        try:
            # PostgreSQL utilise created_at au lieu de date_submitted
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

            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            recent_exercises = [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            print(f"Erreur lors de la récupération des exercices récents: {e}")
            recent_exercises = []

        conn.close()

        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "stats": stats,
            "recent_exercises": recent_exercises
        })
    except Exception as e:
        print(f"Erreur lors du chargement du tableau de bord: {e}")
        traceback.print_exc()
        if 'conn' in locals() and conn:
            conn.close()

        # Afficher un message d'erreur
        return templates.TemplateResponse("home.html", {
            "request": request,
            "error_message": f"Erreur lors du chargement du tableau de bord: {str(e)}"
        }, status_code=500)

async def exercise_detail_page(request):
    exercise_id = request.path_params['exercise_id']

    conn = get_db_connection()
    cursor = conn.cursor()

    # Récupérer l'exercice
    cursor.execute("SELECT * FROM exercises WHERE id = %s", (exercise_id,))

    columns = [desc[0] for desc in cursor.description]
    row = cursor.fetchone()

    if not row:
        conn.close()
        return templates.TemplateResponse("home.html", {
            "request": request,
            "error_message": "L'exercice demandé n'existe pas."
        })

    # Convertir en dictionnaire
    exercise_dict = dict(zip(columns, row))

    # Traiter correctement les choix JSON
    if exercise_dict.get('choices'):
        try:
            # Vérifier si choices est déjà un objet Python (liste)
            if isinstance(exercise_dict['choices'], list):
                pass  # Déjà au bon format
            else:
                exercise_dict['choices'] = json.loads(exercise_dict['choices'])

            # Vérification supplémentaire pour s'assurer que c'est une liste
            if not isinstance(exercise_dict['choices'], list):
                exercise_dict['choices'] = []
        except (ValueError, TypeError) as e:
            print(f"Erreur JSON pour l'exercice {exercise_id}: {e}")
            exercise_dict['choices'] = []
    else:
        exercise_dict['choices'] = []

    conn.close()

    return templates.TemplateResponse("exercise.html", {
        "request": request,
        "exercise": exercise_dict
    })

# Fonction pour normaliser le type d'exercice
def normalize_exercise_type(exercise_type):
    """Normalise le type d'exercice"""
    if not exercise_type:
        return ExerciseTypes.ADDITION

    exercise_type = exercise_type.lower()

    # Parcourir tous les types d'exercices et leurs alias
    for type_key, aliases in ExerciseTypes.TYPE_ALIASES.items():
        if exercise_type in aliases:
            return type_key
            
    # Si aucune correspondance trouvée, retourner le type tel quel
    return exercise_type

# Fonction pour normaliser la difficulté
def normalize_difficulty(difficulty):
    """Normalise le niveau de difficulté"""
    if not difficulty:
        return DifficultyLevels.PADAWAN

    difficulty = difficulty.lower()

    # Parcourir tous les niveaux de difficulté et leurs alias
    for level_key, aliases in DifficultyLevels.LEVEL_ALIASES.items():
        if difficulty in aliases:
            return level_key
            
    # Si aucune correspondance trouvée, retourner la difficulté telle quelle
    return difficulty

# Initialiser la base de données


def init_database():
    """Initialise la base de données si nécessaire"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Créer la table des exercices si elle n'existe pas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS exercises (
        id SERIAL PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        creator_id INTEGER,
        exercise_type VARCHAR(50) NOT NULL,
        difficulty VARCHAR(50) NOT NULL,
        tags VARCHAR(255),
        question TEXT NOT NULL,
        correct_answer VARCHAR(255) NOT NULL,
        choices JSON,
        explanation TEXT,
        hint TEXT,
        image_url VARCHAR(255),
        audio_url VARCHAR(255),
        is_active BOOLEAN DEFAULT TRUE,
        is_archived BOOLEAN DEFAULT FALSE,
        ai_generated BOOLEAN DEFAULT FALSE,
        view_count INTEGER DEFAULT 0,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Ajouter la colonne ai_generated si elle n'existe pas
    try:
        cursor.execute("""
        ALTER TABLE exercises ADD COLUMN IF NOT EXISTS ai_generated BOOLEAN DEFAULT FALSE
        """)
        conn.commit()
    except Exception as e:
        print(f"Note: {str(e)}")
        conn.rollback()

    # Mettre à jour les exercices existants qui contiennent "TEST-ZAXXON"
    try:
        cursor.execute("""
        UPDATE exercises
        SET ai_generated = TRUE
        WHERE title LIKE '%TEST-ZAXXON%' OR question LIKE '%TEST-ZAXXON%'
        """)
        conn.commit()
    except Exception as e:
        print(f"Note: {str(e)}")
        conn.rollback()

    # Créer la table des résultats si elle n'existe pas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS results (
        id SERIAL PRIMARY KEY,
        exercise_id INTEGER NOT NULL,
        user_id INTEGER,
        session_id VARCHAR(255),
        is_correct BOOLEAN NOT NULL,
        time_taken REAL NOT NULL,
        answer_given VARCHAR(255),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (exercise_id) REFERENCES exercises (id)
    )
    """)

    # Créer la table user_stats
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_stats (
        id SERIAL PRIMARY KEY,
        exercise_type VARCHAR(50) NOT NULL,
        difficulty VARCHAR(50) NOT NULL,
        total_attempts INTEGER DEFAULT 0,
        correct_attempts INTEGER DEFAULT 0,
        last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.close()

    print("Base de données initialisée avec succès")

# Fonctions pour la génération et résolution d'exercices
async def generate_exercise(request):
    """Génère un nouvel exercice"""
    try:
        # Obtenir les paramètres (type et difficulté)
        # Cas spécial : le paramètre peut être 'exercise_type' ou 'type'
        exercise_type = request.query_params.get('exercise_type')
        if exercise_type is None:
            exercise_type = request.query_params.get('type')
        if exercise_type is None:
            exercise_type = 'addition'

        difficulty = request.query_params.get('difficulty', 'padawan')

        # Vérifier si on demande une génération par IA
        use_ai = request.query_params.get('ai', '').lower() == 'true'

        # Normaliser les paramètres
        exercise_type = normalize_exercise_type(exercise_type)
        difficulty = normalize_difficulty(difficulty)

        if use_ai:
            print(f"Génération d'un exercice IA de type: {exercise_type}, difficulté: {difficulty}")
            # Générer un exercice avec TEST-ZAXXON dans le titre pour simuler la génération par IA
            exercise_dict = generate_ai_exercise(exercise_type, difficulty)
        else:
            print(f"Génération d'un exercice de type: {exercise_type}, difficulté: {difficulty}")
            # Générer l'exercice normalement
            exercise_dict = generate_simple_exercise(exercise_type, difficulty)

        # Enregistrer l'exercice dans la base de données
        conn = get_db_connection()
        cursor = conn.cursor()

        # Préparer les choix au format JSON
        choices_json = json.dumps(exercise_dict['choices'])

        # Vérifier si ai_generated est dans le dictionnaire, sinon le définir à False
        ai_generated = exercise_dict.get('ai_generated', use_ai)

        # Insérer dans la base de données
        cursor.execute("""
            INSERT INTO exercises
            (title, exercise_type, difficulty, question, correct_answer, choices
                , tags, is_archived, ai_generated)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            exercise_dict['title'],
            exercise_dict['exercise_type'],
            exercise_dict['difficulty'],
            exercise_dict['question'],
            exercise_dict['correct_answer'],
            choices_json,
            exercise_dict.get('tags', 'generated'),
            False,  # is_archived
            ai_generated  # ai_generated
        ))

        result = cursor.fetchone()
        exercise_id = result[0]
        conn.close()

        # Rediriger vers la page des exercices
        return RedirectResponse(url="/exercises?generated=true", status_code=303)

    except Exception as e:
        print(f"Erreur lors de la génération d'exercice: {e}")
        traceback.print_exc()
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": "Erreur de génération",
            "message": f"Impossible de générer l'exercice: {str(e)}"
        }, status_code=500)



def generate_ai_exercise(exercise_type, difficulty):
    """Génère un exercice avec contexte Star Wars pour simuler une génération par IA"""
    import random
    
    normalized_type = normalize_exercise_type(exercise_type)
    normalized_difficulty = normalize_difficulty(difficulty)
    
    # Récupérer les limites pour ce type d'exercice et cette difficulté
    difficulty_config = DIFFICULTY_LIMITS.get(normalized_difficulty, DIFFICULTY_LIMITS[DifficultyLevels.PADAWAN])
    type_limits = difficulty_config.get(normalized_type, difficulty_config.get("default", {"min": 1, "max": 10}))
    
    # Contextes Star Wars pour les exercices
    contexts = [
        "Sur la planète Tatooine, un marchand Jawa vend {num1} pièces détachées de droïdes. Un fermier d'humidité en achète {num2}.",
        "Le Faucon Millenium a parcouru {num1} parsecs. Après une mission pour la Résistance, il parcourt encore {num2} parsecs.",
        "Luke Skywalker s'entraîne avec {num1} cubes de levitation. Yoda lui en donne {num2} de plus.",
        "Dans la base rebelle, il y a {num1} X-wings. Après la bataille, il ne reste que {num2} vaisseaux.",
        "Rey a trouvé {num1} cristaux kyber. Elle en utilise {num2} pour son nouveau sabre laser.",
        "Han Solo a fait {num1} voyages pour livrer des marchandises. Il doit encore faire {num2} voyages cette semaine.",
        "Sur la planète Endor, {num1} Ewoks préparent un piège. {num2} autres Ewoks les rejoignent."
    ]
    
    # Sélectionner un contexte au hasard
    context = random.choice(contexts)
    
    # Générer les nombres en fonction du type et de la difficulté
    if normalized_type == ExerciseTypes.ADDITION:
        min_val, max_val = type_limits.get("min", 1), type_limits.get("max", 10)
        num1, num2 = random.randint(min_val, max_val), random.randint(min_val, max_val)
        result = num1 + num2
        
        # Construire la question avec contexte Star Wars
        question_text = context.format(num1=num1, num2=num2)
        question = f"{question_text} Combien y a-t-il de {random.choice(['éléments', 'unités', 'objets'])} au total?"
        
        correct_answer = str(result)
        
    elif normalized_type == ExerciseTypes.SUBTRACTION:
        limits = type_limits
        num1 = random.randint(limits.get("min1", 5), limits.get("max1", 20))
        num2 = random.randint(limits.get("min2", 1), limits.get("max2", 5))
        
        # Assurer que num1 > num2 pour éviter les résultats négatifs
        if num1 < num2:
            num1, num2 = num2, num1
            
        result = num1 - num2
        
        # Contextes pour soustraction
        sub_contexts = [
            "Le destroyer impérial a {num1} TIE Fighters. {num2} sont détruits lors d'une bataille.",
            "Darth Vader commande {num1} stormtroopers, mais {num2} sont capturés par les rebelles.",
            "Il y avait {num1} droïdes dans le centre de réparation. {num2} ont été récupérés par leurs propriétaires."
        ]
        
        context = random.choice(sub_contexts)
        question_text = context.format(num1=num1, num2=num2)
        question = f"{question_text} Combien reste-t-il de {random.choice(['unités', 'vaisseaux', 'soldats', 'droïdes'])}?"
        
        correct_answer = str(result)
        
    elif normalized_type == ExerciseTypes.MULTIPLICATION:
        min_val, max_val = type_limits.get("min", 1), type_limits.get("max", 10)
        num1, num2 = random.randint(min_val, max_val), random.randint(min_val, max_val)
        result = num1 * num2
        
        # Contextes pour multiplication
        mult_contexts = [
            "Chaque escadron rebelle compte {num1} pilotes. S'il y a {num2} escadrons, ",
            "Un chasseur de primes gagne {num1} crédits par mission. S'il effectue {num2} missions, ",
            "Chaque pod de course peut atteindre {num1} fois la vitesse du son. Si Anakin pousse son pod à {num2} fois cette limite, "
        ]
        
        context = random.choice(mult_contexts)
        question_text = context.format(num1=num1, num2=num2)
        question = f"{question_text}quel est le total de {random.choice(['pilotes', 'crédits', 'vitesse'])}?"
        
        correct_answer = str(result)
        
    elif normalized_type == ExerciseTypes.DIVISION:
        limits = type_limits
        min_result = limits.get("min_result", 1)
        max_result = limits.get("max_result", 5)
        min_divisor = limits.get("min_divisor", 2)
        max_divisor = limits.get("max_divisor", 5)
        
        # Générer d'abord le diviseur et le résultat pour assurer une division exacte
        num2 = random.randint(min_divisor, max_divisor)  # diviseur
        result = random.randint(min_result, max_result)  # quotient
        num1 = num2 * result  # dividende
        
        # Contextes pour division
        div_contexts = [
            "Les {num1} stormtroopers doivent être répartis en {num2} groupes égaux pour rechercher les droïdes.",
            "Le Faucon Millenium a {num1} parsecs à parcourir à une vitesse de {num2} parsecs par heure.",
            "Les rebelles ont {num1} blasters à distribuer équitablement à {num2} soldats."
        ]
        
        context = random.choice(div_contexts)
        question_text = context.format(num1=num1, num2=num2)
        question = f"{question_text} Combien de {random.choice(['stormtroopers par groupe', 'heures de voyage', 'blasters par soldat'])}?"
        
        correct_answer = str(result)
    
    else:
        # Par défaut, faire une addition si le type n'est pas reconnu
        min_val, max_val = 1, 10
        num1, num2 = random.randint(min_val, max_val), random.randint(min_val, max_val)
        result = num1 + num2
        
        question_text = context.format(num1=num1, num2=num2)
        question = f"{question_text} Combien y a-t-il de {random.choice(['éléments', 'unités', 'objets'])} au total?"
        
        correct_answer = str(result)
    
    # Générer les choix
    if result <= 10:
        wrong_answers = [result + 1, result - 1, result + 2]
    else:
        percent_variations = [0.1, -0.1, 0.2] 
        wrong_answers = [result + int(result * var) for var in percent_variations]
    
    # S'assurer que les réponses incorrectes sont positives et uniques
    wrong_answers = [max(1, ans) for ans in wrong_answers]
    
    # Ajouter la bonne réponse et mélanger
    choices = wrong_answers + [result]
    choices = list(set(choices))  # Suppression des doublons
    
    # Si on a perdu des choix à cause des doublons, en ajouter de nouveaux
    while len(choices) < 4:
        new_wrong = result + random.randint(3, 5) * random.choice([-1, 1])
        if new_wrong > 0 and new_wrong not in choices:
            choices.append(new_wrong)
    
    # Convertir les choix en strings        
    choices = [str(c) for c in choices]
    random.shuffle(choices)
    
    # Créer le titre de l'exercice IA
    title = f"{Messages.AI_EXERCISE_PREFIX}: {DISPLAY_NAMES.get(normalized_difficulty, 'Inconnu')} - {DISPLAY_NAMES.get(normalized_type, 'Inconnu')}"
    
    return {
        "title": title,
        "exercise_type": normalized_type,
        "difficulty": normalized_difficulty,
        "question": question,
        "correct_answer": correct_answer,
        "choices": choices,
        "tags": Tags.AI + "," + Tags.GENERATIVE + "," + Tags.STARWARS,
        "ai_generated": True
    }



def generate_simple_exercise(exercise_type, difficulty):
    """Génère un exercice simple de manière algorithmique"""
    import random

    normalized_type = normalize_exercise_type(exercise_type)
    normalized_difficulty = normalize_difficulty(difficulty)
    
    # Récupérer les limites pour ce type et cette difficulté
    difficulty_config = DIFFICULTY_LIMITS.get(normalized_difficulty, DIFFICULTY_LIMITS[DifficultyLevels.PADAWAN])
    
    # Limites par défaut si le type n'est pas trouvé
    type_limits = difficulty_config.get(normalized_type, difficulty_config.get("default", {"min": 1, "max": 10}))
    
    if normalized_type == ExerciseTypes.ADDITION:
        # Génération d'une addition
        min_val, max_val = type_limits.get("min", 1), type_limits.get("max", 10)
        num1, num2 = random.randint(min_val, max_val), random.randint(min_val, max_val)
        
        result = num1 + num2
        question = ExerciseMessages.QUESTION_ADDITION.format(num1=num1, num2=num2)
        correct_answer = str(result)
        choices = [str(result), str(result-1), str(result+1), str(result+2)]
        random.shuffle(choices)

        return {
            "title": ExerciseMessages.TITLE_ADDITION,
            "exercise_type": normalized_type,
            "difficulty": normalized_difficulty,
            "question": question,
            "correct_answer": correct_answer,
            "choices": choices,
            "tags": Tags.ALGORITHMIC + "," + Tags.SIMPLE
        }

    elif normalized_type == ExerciseTypes.SUBTRACTION:
        # Génération d'une soustraction
        limits = type_limits
        num1 = random.randint(limits.get("min1", 5), limits.get("max1", 20))
        num2 = random.randint(limits.get("min2", 1), limits.get("max2", 5))

        # Assurer que num1 > num2 pour éviter les résultats négatifs
        if num1 < num2:
            num1, num2 = num2, num1

        result = num1 - num2
        question = ExerciseMessages.QUESTION_SUBTRACTION.format(num1=num1, num2=num2)
        correct_answer = str(result)
        choices = [str(result), str(result-1), str(result+1), str(result+2)]
        random.shuffle(choices)

        return {
            "title": ExerciseMessages.TITLE_SUBTRACTION,
            "exercise_type": normalized_type,
            "difficulty": normalized_difficulty,
            "question": question,
            "correct_answer": correct_answer,
            "choices": choices,
            "tags": Tags.ALGORITHMIC + "," + Tags.SIMPLE
        }

    elif normalized_type == ExerciseTypes.MULTIPLICATION:
        # Génération d'une multiplication
        min_val, max_val = type_limits.get("min", 1), type_limits.get("max", 10)
        num1, num2 = random.randint(min_val, max_val), random.randint(min_val, max_val)

        result = num1 * num2
        question = ExerciseMessages.QUESTION_MULTIPLICATION.format(num1=num1, num2=num2)
        correct_answer = str(result)
        choices = [str(result), str(result-num1), str(result+num1), str(result+num2)]
        random.shuffle(choices)

        return {
            "title": ExerciseMessages.TITLE_MULTIPLICATION,
            "exercise_type": normalized_type,
            "difficulty": normalized_difficulty,
            "question": question,
            "correct_answer": correct_answer,
            "choices": choices,
            "tags": Tags.ALGORITHMIC + "," + Tags.SIMPLE
        }

    elif normalized_type == ExerciseTypes.DIVISION:
        # Génération d'une division
        limits = type_limits
        min_result = limits.get("min_result", 1)
        max_result = limits.get("max_result", 5)
        min_divisor = limits.get("min_divisor", 2)
        max_divisor = limits.get("max_divisor", 5)
        
        # Générer d'abord le diviseur et le résultat pour assurer une division exacte
        num2 = random.randint(min_divisor, max_divisor)  # diviseur
        result = random.randint(min_result, max_result)  # quotient
        num1 = num2 * result  # dividende

        question = ExerciseMessages.QUESTION_DIVISION.format(num1=num1, num2=num2)
        correct_answer = str(result)
        choices = [str(result), str(result-1), str(result+1), str(result+num2//2)]
        random.shuffle(choices)

        return {
            "title": ExerciseMessages.TITLE_DIVISION,
            "exercise_type": normalized_type,
            "difficulty": normalized_difficulty,
            "question": question,
            "correct_answer": correct_answer,
            "choices": choices,
            "tags": Tags.ALGORITHMIC + "," + Tags.SIMPLE
        }

    else:
        # Par défaut, faire une addition si le type n'est pas reconnu
        min_val, max_val = 1, 10
        num1, num2 = random.randint(min_val, max_val), random.randint(min_val, max_val)
        
        result = num1 + num2
        question = ExerciseMessages.QUESTION_ADDITION.format(num1=num1, num2=num2)
        correct_answer = str(result)
        choices = [str(result), str(result-1), str(result+1), str(result+2)]
        random.shuffle(choices)

        return {
            "title": ExerciseMessages.TITLE_DEFAULT,
            "exercise_type": ExerciseTypes.ADDITION,
            "difficulty": normalized_difficulty,
            "question": question,
            "correct_answer": correct_answer,
            "choices": choices,
            "tags": Tags.ALGORITHMIC + "," + Tags.SIMPLE
        }

async def submit_answer(request):
    """Traite la soumission d'une réponse à un exercice"""
    try:
        # Récupérer les données de la requête
        data = await request.json()
        exercise_id = data.get('exercise_id')
        selected_answer = data.get('selected_answer')
        time_spent = data.get('time_spent', 0)

        # Récupérer l'exercice pour vérifier la réponse
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM exercises WHERE id = %s", (exercise_id,))
        columns = [desc[0] for desc in cursor.description]
        row = cursor.fetchone()

        if not row:
            conn.close()
            return JSONResponse({"error": "Exercice non trouvé"}, status_code=404)

        exercise = dict(zip(columns, row))
        is_correct = selected_answer == exercise['correct_answer']

        # Utiliser uniquement les colonnes que nous savons exister
        try:
            # Version simplifiée avec seulement exercise_id et is_correct
            cursor.execute("""
                INSERT INTO results (exercise_id, is_correct)
                VALUES (%s, %s)
            """, (exercise_id, is_correct))
        except Exception as e:
            print(f"Erreur lors de l'insertion dans results: {e}")
            # En dernier recours, ne pas enregistrer le résultat mais continuer pour mettre à jour les stats
            pass

        # Mettre à jour les statistiques user_stats
        exercise_type = normalize_exercise_type(exercise['exercise_type'])
        difficulty = normalize_difficulty(exercise['difficulty'])

        # Vérifier si une entrée existe pour ce type/difficulté
        cursor.execute("""
            SELECT id, total_attempts, correct_attempts
            FROM user_stats
            WHERE exercise_type = %s AND difficulty = %s
        """, (exercise_type, difficulty))

        row = cursor.fetchone()

        if row:
            # Mettre à jour l'entrée existante
            stats_id, total_attempts, correct_attempts = row
            cursor.execute("""
                UPDATE user_stats
                SET total_attempts = %s, correct_attempts = %s, last_updated = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (total_attempts + 1, correct_attempts + (1 if is_correct else 0), stats_id))
        else:
            # Créer une nouvelle entrée
            cursor.execute("""
                INSERT INTO user_stats (exercise_type, difficulty, total_attempts, correct_attempts)
                VALUES (%s, %s, %s, %s)
            """, (exercise_type, difficulty, 1, 1 if is_correct else 0))

        conn.commit()
        conn.close()

        # Retourner le résultat
        return JSONResponse({
            "is_correct": is_correct,
            "correct_answer": exercise['correct_answer'],
            "explanation": exercise.get('explanation', "")
        })

    except Exception as e:
        print(f"Erreur lors du traitement de la réponse: {e}")
        traceback.print_exc()
        return JSONResponse({"error": f"Erreur: {str(e)}"}, status_code=500)

async def get_exercises_list(request):
    """Retourne la liste des exercices récents"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Récupérer les exercices non archivés
        cursor.execute("SELECT * FROM exercises WHERE is_archived IS NOT TRUE ORDER BY id DESC LIMIT 10")

        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

        exercises = []
        for row in rows:
            exercise = dict(zip(columns, row))

            # Traiter correctement les choix JSON
            if exercise.get('choices'):
                try:
                    # Vérifier si choices est déjà un objet Python (liste)
                    if isinstance(exercise['choices'], list):
                        pass  # Déjà au bon format
                    else:
                        exercise['choices'] = json.loads(exercise['choices'])
                except (ValueError, TypeError) as e:
                    print(f"Erreur JSON pour l'exercice {exercise.get('id')}: {e}")
                    exercise['choices'] = []
            else:
                exercise['choices'] = []

            exercises.append(exercise)

        conn.close()

        return JSONResponse({
            "items": exercises,
            "total": len(exercises),
            "skip": 0,
            "limit": 10
        })

    except Exception as e:
        print(f"Erreur lors de la récupération des exercices: {e}")
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)

async def delete_exercise(request):
    """Supprime un exercice par son ID"""
    try:
        exercise_id = request.path_params.get('exercise_id')

        conn = get_db_connection()
        cursor = conn.cursor()

        # Vérifier si l'exercice existe
        cursor.execute("SELECT id FROM exercises WHERE id = %s", (exercise_id,))
        if cursor.fetchone() is None:
            conn.close()
            return JSONResponse({"error": "Exercice non trouvé"}, status_code=404)

        # Supprimer les résultats associés à cet exercice (si la table a une contrainte de clé étrangère)
        try:
            cursor.execute("DELETE FROM results WHERE exercise_id = %s", (exercise_id,))
        except Exception as e:
            # Ignorer les erreurs ici, car la table results pourrait ne pas avoir de contrainte
            print(f"Note: Impossible de supprimer les résultats associés: {e}")

        # Supprimer l'exercice
        cursor.execute("DELETE FROM exercises WHERE id = %s", (exercise_id,))
        conn.commit()
        conn.close()

        return JSONResponse({"success": True, "message": "Exercice supprimé avec succès"}
            , status_code=200)

    except Exception as e:
        print(f"Erreur lors de la suppression de l'exercice: {e}")
        traceback.print_exc()
        return JSONResponse({"error": f"Erreur: {str(e)}"}, status_code=500)

async def get_user_stats(request):
    """
    Endpoint pour obtenir les statistiques utilisateur pour le tableau de bord.
    Route: /api/users/stats
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Récupérer les statistiques globales
        cursor.execute("""
        SELECT
            SUM(total_attempts) as total_exercises,
            SUM(correct_attempts) as correct_answers
        FROM user_stats
        """)
        
        columns = [desc[0] for desc in cursor.description]
        row = cursor.fetchone()
        overall_stats = dict(zip(columns, row)) if row else {"total_exercises": 0, "correct_answers": 0}

        # Calculer le taux de réussite
        total_exercises = overall_stats.get('total_exercises', 0) or 0
        correct_answers = overall_stats.get('correct_answers', 0) or 0
        success_rate = int((correct_answers / total_exercises * 100) if total_exercises > 0 else 0)

        # Statistiques par type d'exercice
        performance_by_type = {}
        for exercise_type in ['addition', 'subtraction', 'multiplication', 'division']:
            cursor.execute("""
            SELECT
                SUM(total_attempts) as total,
                SUM(correct_attempts) as correct
            FROM user_stats
            WHERE exercise_type = %s
            """, (exercise_type,))
            
            columns = [desc[0] for desc in cursor.description]
            row = cursor.fetchone()
            type_stats = dict(zip(columns, row)) if row else {"total": 0, "correct": 0}

            total = type_stats.get('total', 0) or 0
            correct = type_stats.get('correct', 0) or 0
            success_rate_type = int((correct / total * 100) if total > 0 else 0)

            # Convertir les types en français pour le frontend
            type_fr = {'addition': 'addition', 'subtraction': 'soustraction',
                    'multiplication': 'multiplication', 'division': 'division'}

            performance_by_type[type_fr.get(exercise_type, exercise_type)] = {
                'completed': total,
                'correct': correct,
                'success_rate': success_rate_type
            }

        # Récupérer les exercices récents pour l'activité
        cursor.execute("""
        SELECT
            e.question,
            r.is_correct,
            r.created_at as completed_at
        FROM results r
        JOIN exercises e ON r.exercise_id = e.id
        ORDER BY r.created_at DESC
        LIMIT 10
        """)
        
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        recent_results = [dict(zip(columns, row)) for row in rows]

        # Formater les activités récentes
        recent_activity = []
        for result in recent_results:
            try:
                # Adapter le format de date pour PostgreSQL
                timestamp = result.get('completed_at')
                if isinstance(timestamp, str):
                    from datetime import datetime
                    timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00')) if 'Z' in timestamp else datetime.fromisoformat(timestamp)
                formatted_time = timestamp.strftime("%d/%m/%Y %H:%M") if hasattr(timestamp, 'strftime') else str(timestamp)
            except Exception as e:
                print(f"Erreur dans le formatage de la date: {e}")
                formatted_time = str(result.get('completed_at', ''))

            activity = {
                'type': 'exercise_completed',
                'is_correct': bool(result.get('is_correct')),
                'description': f"{'Réussite' if result.get('is_correct') else 'Échec'} : {result.get('question', '')}",
                'time': formatted_time
            }
            recent_activity.append(activity)

        # Simuler les données de niveau pour le moment
        level_data = {
            'current': 1,
            'title': 'Débutant Stellaire',
            'current_xp': 25,
            'next_level_xp': 100
        }

        # Récupérer la progression réelle par jour pour les 7 derniers jours
        from datetime import datetime, timedelta
        
        today = datetime.now().date()
        day_labels = []
        exercise_counts = []
        
        # Générer les étiquettes des 7 derniers jours
        for i in range(6, -1, -1):
            past_date = today - timedelta(days=i)
            if i == 0:
                day_labels.append('Aujourd\'hui')
            else:
                day_labels.append(f'J-{i}')
                
        # Pour chaque jour, récupérer le nombre d'exercices résolus
        try:
            # Utiliser la fonction date_trunc pour obtenir la date sans l'heure en PostgreSQL
            cursor.execute("""
            SELECT 
                DATE(created_at) as exercise_date,
                COUNT(*) as exercise_count
            FROM results
            WHERE created_at >= %s
            GROUP BY DATE(created_at)
            ORDER BY exercise_date ASC
            """, (today - timedelta(days=6),))
            
            date_counts = {}
            rows = cursor.fetchall()
            for row in rows:
                date_obj = row[0]
                if isinstance(date_obj, str):
                    date_obj = datetime.strptime(date_obj, '%Y-%m-%d').date()
                date_counts[date_obj] = row[1]
            
            # Remplir le tableau avec les comptages réels ou zéro si aucun exercice
            for i in range(6, -1, -1):
                past_date = today - timedelta(days=i)
                exercise_counts.append(date_counts.get(past_date, 0))
                
        except Exception as e:
            print(f"Erreur lors de la récupération des données de progression journalière: {e}")
            traceback.print_exc()
            # En cas d'erreur, revenir aux données simulées mais plus réalistes
            exercise_counts = [0, 0, 0, 0, 0, 0, 0]
            # Ajouter le total exercices à aujourd'hui pour que ce soit cohérent
            if total_exercises > 0:
                exercise_counts[-1] = total_exercises

        progress_over_time = {
            'labels': day_labels,
            'datasets': [{
                'label': 'Exercices résolus',
                'data': exercise_counts
            }]
        }

        conn.close()

        response_data = {
            'total_exercises': total_exercises,
            'correct_answers': correct_answers,
            'success_rate': success_rate,
            'experience_points': total_exercises * 10,  # Points d'XP simulés
            'performance_by_type': performance_by_type,
            'recent_activity': recent_activity,
            'level': level_data,
            'progress_over_time': progress_over_time
        }
        
        print("Données du tableau de bord générées:", response_data)
        return JSONResponse(response_data)
    
    except Exception as e:
        print(f"Erreur lors de la récupération des statistiques utilisateur: {e}")
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)

# Configuration des routes
routes = [
    # Pages HTML
    Route("/", homepage),
    Route("/exercises", exercises_page),
    Route("/dashboard", dashboard),
    Route("/exercise/{exercise_id:int}", exercise_detail_page),
    Route("/api/users/stats", get_user_stats),

    # API
    Route("/api/exercises/", get_exercises_list, methods=["GET"]),
    Route("/api/exercises/{exercise_id:int}", get_exercise, methods=["GET"]),
    Route("/api/exercises/{exercise_id:int}", delete_exercise, methods=["DELETE"]),
    Route("/api/exercises/generate", generate_exercise, methods=["GET"]),
    Route("/api/exercises/{exercise_id:int}/submit", submit_answer, methods=["POST"]),

    # Fichiers statiques
    Mount("/static", StaticFiles(directory=STATIC_DIR), name="static"),
]

# Fonction d'initialisation
async def startup():
    generate_template_files()
    init_database()

# Création de l'application Starlette
app = Starlette(
    debug=DEBUG,
    routes=routes,
    middleware=middleware,
    on_startup=[startup]
)



def main():
    """Point d'entrée principal de l'application"""
    print(f"Lancement du serveur sur le port {PORT}")
    uvicorn.run(
        "enhanced_server:app",
        host="0.0.0.0",
        port=PORT,
        reload=DEBUG,
        log_level=LOG_LEVEL.lower()
    )

if __name__ == "__main__":
    main()
