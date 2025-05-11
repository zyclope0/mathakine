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
from app.core.messages import SystemMessages, ExerciseMessages, InterfaceTexts, StarWarsNarratives
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
    
    # Récupérer les paramètres de filtrage
    exercise_type = request.query_params.get('exercise_type', None)
    difficulty = request.query_params.get('difficulty', None)
    
    print(f"Paramètres reçus - exercise_type: {exercise_type}, difficulty: {difficulty}")
    
    # Normaliser les paramètres si présents
    if exercise_type:
        exercise_type = normalize_exercise_type(exercise_type)
        print(f"Type d'exercice normalisé: {exercise_type}")
    if difficulty:
        difficulty = normalize_difficulty(difficulty)
        print(f"Difficulté normalisée: {difficulty}")

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # DEBUG: Vérifier si les exercices existent dans la DB
        cursor.execute("SELECT COUNT(*) FROM exercises")
        count = cursor.fetchone()[0]
        print(f"Nombre total d'exercices dans la base de données: {count}")
        
        # Utiliser une requête SQL personnalisée sans filtrer sur is_archived
        if exercise_type and difficulty:
            print(f"Exécution requête personnalisée par type et difficulté: ({exercise_type}, {difficulty})")
            cursor.execute("""
            SELECT * FROM exercises 
            WHERE exercise_type = %s AND difficulty = %s
            ORDER BY id
            """, (exercise_type, difficulty))
        elif exercise_type:
            print(f"Exécution requête personnalisée par type: ({exercise_type},)")
            cursor.execute("""
            SELECT * FROM exercises 
            WHERE exercise_type = %s
            ORDER BY id
            """, (exercise_type,))
        elif difficulty:
            print(f"Exécution requête personnalisée par difficulté: ({difficulty},)")
            cursor.execute("""
            SELECT * FROM exercises 
            WHERE difficulty = %s
            ORDER BY id
            """, (difficulty,))
        else:
            print("Exécution requête personnalisée pour tous les exercices")
            cursor.execute("""
            SELECT * FROM exercises 
            ORDER BY id
            """)

        columns = [desc[0] for desc in cursor.description]
        print(f"Colonnes retournées: {columns}")
        rows = cursor.fetchall()
        print(f"Nombre de lignes récupérées: {len(rows)}")
    
        exercises = []
        for row in rows:
            exercise = dict(zip(columns, row))
            
            # Afficher le premier exercice pour le débogage
            if len(exercises) == 0:
                print(f"Premier exercice récupéré: {exercise}")

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
    
        print(f"Nombre d'exercices récupérés: {len(exercises)}")
        if len(exercises) > 0:
            print(f"Premier exercice: ID={exercises[0].get('id')}, Titre={exercises[0].get('title')}")
            print(f"Dernier exercice: ID={exercises[-1].get('id')}, Titre={exercises[-1].get('title')}")

    except Exception as e:
        print(f"Erreur lors de la récupération des exercices: {e}")
        traceback.print_exc()
        exercises = []

    finally:
        conn.close()
    
    # Message pour indiquer si on vient de générer un exercice
    message = None
    message_type = None
    if just_generated:
        message = "Exercice généré avec succès. Vous pouvez maintenant le résoudre ou en générer un autre."
        message_type = "success"

    # Créer des dictionnaires pour l'affichage des types et niveaux
    exercise_types = {key: DISPLAY_NAMES[key] for key in ExerciseTypes.ALL_TYPES}
    difficulty_levels = {key: DISPLAY_NAMES[key] for key in DifficultyLevels.ALL_LEVELS}
    
    # Mappings pour l'affichage des exercices dans la liste
    exercise_type_display = DISPLAY_NAMES
    difficulty_display = DISPLAY_NAMES
    
    # Préfixe IA pour les templates
    ai_prefix = Messages.AI_EXERCISE_PREFIX

    print(f"Préparation du rendu template avec {len(exercises)} exercices")
    print(f"Chemin du template: {TEMPLATES_DIR}/exercises.html")
    
    # Vérifier que les mappings sont bien générés
    print(f"Types d'exercices disponibles: {exercise_types}")
    print(f"Niveaux de difficulté disponibles: {difficulty_levels}")
    
    try:
        response = templates.TemplateResponse("exercises.html", {
            "request": request,
            "exercises": exercises,
            "message": message,
            "message_type": message_type,
            "exercise_types": exercise_types,
            "difficulty_levels": difficulty_levels,
            "exercise_type_display": exercise_type_display,
            "difficulty_display": difficulty_display,
            "ai_prefix": ai_prefix
        })
        print("Template rendu avec succès")
        return response
    except Exception as e:
        print(f"Erreur lors du rendu du template: {e}")
        traceback.print_exc()
        return HTMLResponse("<h1>Erreur lors du chargement des exercices</h1><p>Veuillez réessayer ultérieurement.</p>")

async def get_exercise(request):
    exercise_id = request.path_params.get('exercise_id')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(ExerciseQueries.GET_BY_ID, (exercise_id,))

    columns = [desc[0] for desc in cursor.description]
    row = cursor.fetchone()

    if not row:
        conn.close()
        return JSONResponse({"error": SystemMessages.ERROR_EXERCISE_NOT_FOUND}, status_code=404)

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
    """Rendu de la page de détail d'un exercice"""
    exercise_id = request.path_params["exercise_id"]
    print(f"Accès à la page de détail de l'exercice {exercise_id}")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Récupérer l'exercice
        print(f"Exécution de la requête pour récupérer l'exercice {exercise_id}")
        print(f"Requête SQL: {ExerciseQueries.GET_BY_ID}")
        
        cursor.execute(ExerciseQueries.GET_BY_ID, (exercise_id,))
        columns = [desc[0] for desc in cursor.description]
        print(f"Colonnes retournées: {columns}")
        row = cursor.fetchone()
        print(f"Résultat de la requête: {row}")
        
        if not row:
            print(f"ERREUR: L'exercice {exercise_id} n'a pas été trouvé dans la base de données")
            return templates.TemplateResponse("error.html", {
                "request": request,
                "error": "Exercice non trouvé",
                "message": f"L'exercice avec l'ID {exercise_id} n'existe pas ou a été supprimé."
            }, status_code=404)
        
        # Convertir en dictionnaire
        exercise = dict(zip(columns, row))
        print(f"Exercice récupéré: {exercise}")
        
        # Sécuriser le traitement JSON
        if exercise.get('choices'):
            try:
                if isinstance(exercise['choices'], list):
                    print("Les choix sont déjà au format liste")
                else:
                    print(f"Conversion des choix du format {type(exercise['choices'])} au format liste")
                    exercise['choices'] = json.loads(exercise['choices'])
                    print(f"Choix après conversion: {exercise['choices']}")
            except (ValueError, TypeError) as e:
                print(f"Erreur lors du parsing JSON des choix pour l'exercice {exercise_id}: {e}")
                exercise['choices'] = []
        else:
            print("Aucun choix trouvé pour cet exercice, initialisation avec une liste vide")
            exercise['choices'] = []
            
    except Exception as e:
        print(f"Exception lors de la récupération de l'exercice {exercise_id}: {str(e)}")
        traceback.print_exc()
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": "Erreur de base de données",
            "message": f"Une erreur est survenue lors de la récupération de l'exercice: {str(e)}"
        }, status_code=500)
    
    finally:
        conn.close()

    # Mappings pour l'affichage des types et niveaux
    exercise_type_display = DISPLAY_NAMES
    difficulty_display = DISPLAY_NAMES
    
    print(f"Rendu du template exercise_detail.html avec l'exercice {exercise_id}")
    
    try:
        return templates.TemplateResponse("exercise_detail.html", {
            "request": request,
            "exercise": exercise,
            "exercise_type_display": exercise_type_display,
            "difficulty_display": difficulty_display
        })
    except Exception as template_error:
        print(f"ERREUR lors du rendu du template: {str(template_error)}")
        traceback.print_exc()
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": "Erreur de template",
            "message": f"Une erreur est survenue lors du rendu du template: {str(template_error)}"
        }, status_code=500)

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
    cursor.execute(ExerciseQueries.CREATE_TABLE)

    # Ajouter la colonne ai_generated si elle n'existe pas
    try:
        cursor.execute("""
        ALTER TABLE exercises ADD COLUMN IF NOT EXISTS ai_generated BOOLEAN DEFAULT FALSE
        """)
        conn.commit()
    except Exception as e:
        print(f"Note: {str(e)}")
        conn.rollback()

    # Mettre à jour les exercices existants qui contiennent le préfixe d'IA
    try:
        cursor.execute(f"""
        UPDATE exercises
        SET ai_generated = TRUE
        WHERE title LIKE '%{Messages.AI_EXERCISE_PREFIX}%' OR question LIKE '%{Messages.AI_EXERCISE_PREFIX}%'
        """)
        conn.commit()
    except Exception as e:
        print(f"Note: {str(e)}")
        conn.rollback()

    # Créer la table des résultats si elle n'existe pas
    cursor.execute(ResultQueries.CREATE_TABLE)

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
    # Récupérer les paramètres (type d'exercice, difficulté)
    params = request.query_params
    exercise_type = params.get('type')
    difficulty = params.get('difficulty')
    use_ai = params.get('ai', False)
    
    # Normaliser les types et difficultés
    normalized_type = normalize_exercise_type(exercise_type) if exercise_type else None
    normalized_difficulty = normalize_difficulty(difficulty) if difficulty else None
    
    # Si le type n'est pas spécifié, en prendre un au hasard
    if not normalized_type:
        normalized_type = random.choice(ExerciseTypes.ALL_TYPES)
    
    # Si la difficulté n'est pas spécifiée, en prendre une au hasard
    if not normalized_difficulty:
        normalized_difficulty = random.choice(DifficultyLevels.ALL_LEVELS)
    
    # Si on demande de l'IA, utiliser la fonction de génération IA
    ai_generated = False
    if use_ai and str(use_ai).lower() in ['true', '1', 'yes', 'y']:
        exercise_dict = generate_ai_exercise(normalized_type, normalized_difficulty)
        ai_generated = True
    else:
        # Génération algorithmique simple
        exercise_dict = generate_simple_exercise(normalized_type, normalized_difficulty)
    
    # Préparer les choix pour la base de données (JSON)
    choices_json = json.dumps(exercise_dict.get('choices', []))
    
    # S'assurer que l'explication est définie et n'est pas None
    if 'explanation' not in exercise_dict or exercise_dict['explanation'] is None or exercise_dict['explanation'] == "None" or exercise_dict['explanation'] == "":
        if exercise_dict['exercise_type'] == ExerciseTypes.ADDITION:
            exercise_dict['explanation'] = f"Pour additionner {exercise_dict.get('num1', '?')} et {exercise_dict.get('num2', '?')}, il faut calculer leur somme: {exercise_dict['correct_answer']}"
        elif exercise_dict['exercise_type'] == ExerciseTypes.SUBTRACTION:
            exercise_dict['explanation'] = f"Pour soustraire {exercise_dict.get('num2', '?')} de {exercise_dict.get('num1', '?')}, il faut calculer leur différence: {exercise_dict['correct_answer']}"
        elif exercise_dict['exercise_type'] == ExerciseTypes.MULTIPLICATION:
            exercise_dict['explanation'] = f"Pour multiplier {exercise_dict.get('num1', '?')} par {exercise_dict.get('num2', '?')}, il faut calculer leur produit: {exercise_dict['correct_answer']}"
        elif exercise_dict['exercise_type'] == ExerciseTypes.DIVISION:
            exercise_dict['explanation'] = f"Pour diviser {exercise_dict.get('num1', '?')} par {exercise_dict.get('num2', '?')}, il faut calculer leur quotient: {exercise_dict['correct_answer']}"
        else:
            exercise_dict['explanation'] = f"La réponse correcte est {exercise_dict['correct_answer']}"
    
    print(f"Explication générée: {exercise_dict['explanation']}")
    
    try:
        # Se connecter à la base de données
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # DEBUGGAGE: Vérifier si l'explication est bien définie
        print(f"Insertion d'un exercice avec explication: {exercise_dict.get('explanation', 'NON DÉFINIE')}")
        
        # Insérer dans la base de données en utilisant la requête centralisée
        print("Insertion d'un nouvel exercice...")
        cursor.execute("""
        INSERT INTO exercises 
        (title, creator_id, exercise_type, difficulty, tags, question, correct_answer, 
        choices, explanation, hint, image_url, audio_url, ai_generated, is_archived) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, false)
        RETURNING id
        """, (
            exercise_dict['title'],              # title
            None,                                # creator_id (pour l'instant, None)
            exercise_dict['exercise_type'],      # exercise_type
            exercise_dict['difficulty'],         # difficulty
            exercise_dict.get('tags', 'generated'), # tags
            exercise_dict['question'],           # question
            exercise_dict['correct_answer'],     # correct_answer
            choices_json,                        # choices
            exercise_dict['explanation'],        # explanation (maintenant garanti non-null)
            exercise_dict.get('hint', None),     # hint
            exercise_dict.get('image_url', None), # image_url
            exercise_dict.get('audio_url', None), # audio_url
            ai_generated                         # ai_generated
        ))
        
        result = cursor.fetchone()
        exercise_id = result[0]
        conn.commit()
        conn.close()
        
        print(f"Nouvel exercice créé avec ID={exercise_id}, explication: {exercise_dict['explanation']}")

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
    
    # Structure de base commune pour tous les types d'exercices générés par IA
    exercise_data = {
        "exercise_type": normalized_type,
        "difficulty": normalized_difficulty,
        "ai_generated": True,
        "tags": Tags.AI + "," + Tags.GENERATIVE + "," + Tags.STARWARS
    }
    
    # Préfixe et suffixe pour enrichir l'explication
    explanation_prefix = random.choice(StarWarsNarratives.EXPLANATION_PREFIXES)
    explanation_suffix = random.choice(StarWarsNarratives.EXPLANATION_SUFFIXES)
    
    if normalized_type == ExerciseTypes.ADDITION:
        min_val, max_val = type_limits.get("min", 1), type_limits.get("max", 10)
        num1, num2 = random.randint(min_val, max_val), random.randint(min_val, max_val)
        result = num1 + num2
        
        # Modèles de question d'addition avec thématique Star Wars
        addition_templates = [
            # Format: (question, explication)
            (
                f"Sur la planète {random.choice(StarWarsNarratives.LOCATIONS)}, {random.choice(StarWarsNarratives.CHARACTERS)} a trouvé {num1} {random.choice(StarWarsNarratives.OBJECTS)}. Plus tard, il en trouve encore {num2}. Combien de {random.choice(StarWarsNarratives.OBJECTS)} a-t-il maintenant?",
                f"Au début, il y avait {num1} objets, puis {num2} autres ont été ajoutés. Pour résoudre ce problème d'addition, il faut calculer {num1} + {num2}, ce qui donne {result} objets au total."
            ),
            (
                f"{random.choice(StarWarsNarratives.CHARACTERS)} a capturé {num1} {random.choice(StarWarsNarratives.OBJECTS)} lors d'une mission sur {random.choice(StarWarsNarratives.LOCATIONS)}. {random.choice(StarWarsNarratives.CHARACTERS)} lui en donne {num2} de plus. Combien en a-t-il au total?",
                f"Ce problème d'addition consiste à ajouter les {num1} objets initiaux aux {num2} nouveaux objets. Le calcul est donc {num1} + {num2} = {result}."
            ),
            (
                f"Une escouade de {num1} stormtroopers patrouille sur {random.choice(StarWarsNarratives.LOCATIONS)}. Ils sont rejoints par {num2} autres stormtroopers. Combien sont-ils maintenant?",
                f"Pour résoudre ce problème, nous devons additionner le nombre initial de stormtroopers ({num1}) au nombre de renforts ({num2}). Cela nous donne {num1} + {num2} = {result} stormtroopers au total."
            )
        ]
        
        question_template, explanation_template = random.choice(addition_templates)
        
        exercise_data.update({
            "title": f"[{Messages.AI_EXERCISE_PREFIX}] Aventure spatiale - Addition niveau {difficulty}",
            "question": question_template,
            "correct_answer": str(result),
            "num1": num1,
            "num2": num2,
            "explanation": f"[{Messages.AI_EXERCISE_PREFIX}] {explanation_prefix} {explanation_template} {explanation_suffix}"
        })
        
    elif normalized_type == ExerciseTypes.SUBTRACTION:
        limits = type_limits
        num1 = random.randint(limits.get("min1", 5), limits.get("max1", 20))
        num2 = random.randint(limits.get("min2", 1), limits.get("max2", 5))
        
        # Assurer que num1 > num2 pour éviter les résultats négatifs
        if num1 < num2:
            num1, num2 = num2, num1
            
        result = num1 - num2
        
        # Modèles de question de soustraction avec thématique Star Wars
        subtraction_templates = [
            # Format: (question, explication)
            (
                f"Le Destroyer Impérial avait {num1} chasseurs TIE. Après une bataille contre les rebelles, {num2} ont été détruits. Combien de chasseurs TIE reste-t-il?",
                f"Initialement, l'Empire disposait de {num1} chasseurs. Suite à la bataille, {num2} ont été perdus. Pour calculer ceux qui restent, on effectue la soustraction {num1} - {num2} = {result} chasseurs TIE."
            ),
            (
                f"{random.choice(StarWarsNarratives.CHARACTERS)} possédait {num1} {random.choice(StarWarsNarratives.OBJECTS)}. Malheureusement, {num2} ont été volés par des pillards Jawas sur {random.choice(StarWarsNarratives.LOCATIONS)}. Combien lui reste-t-il de {random.choice(StarWarsNarratives.OBJECTS)}?",
                f"Dans ce problème de soustraction, nous commençons avec {num1} objets puis nous en perdons {num2}. L'opération mathématique est {num1} - {num2} = {result}."
            ),
            (
                f"Une flotte de {num1} vaisseaux rebelles affronte l'Empire. Après la bataille, {num2} vaisseaux sont détruits. Combien de vaisseaux rebelles ont survécu?",
                f"Pour résoudre ce problème, nous devons soustraire le nombre de vaisseaux détruits ({num2}) du nombre initial ({num1}). Le calcul est {num1} - {num2} = {result} vaisseaux survivants."
            )
        ]
        
        question_template, explanation_template = random.choice(subtraction_templates)
        
        exercise_data.update({
            "title": f"[{Messages.AI_EXERCISE_PREFIX}] Conflit galactique - Soustraction niveau {difficulty}",
            "question": question_template,
            "correct_answer": str(result),
            "num1": num1,
            "num2": num2,
            "explanation": f"[{Messages.AI_EXERCISE_PREFIX}] {explanation_prefix} {explanation_template} {explanation_suffix}"
        })
        
    elif normalized_type == ExerciseTypes.MULTIPLICATION:
        # Utiliser des limites adaptées pour la multiplication
        if normalized_difficulty == DifficultyLevels.INITIE:
            num1 = random.randint(2, 5)
            num2 = random.randint(2, 5)
        else:
            num1 = random.randint(type_limits.get("min", 2), type_limits.get("max", 10))
            num2 = random.randint(type_limits.get("min", 2), type_limits.get("max", 10))
        
        result = num1 * num2
        
        # Modèles de question de multiplication avec thématique Star Wars
        multiplication_templates = [
            # Format: (question, explication)
            (
                f"Chaque Jedi du Temple possède {num2} cristaux kyber pour construire ses sabres laser. S'il y a {num1} Jedi, combien de cristaux kyber sont nécessaires au total?",
                f"Ce problème demande de calculer le nombre total de cristaux pour tous les Jedi. Chaque Jedi ayant {num2} cristaux, et comme il y a {num1} Jedi, nous devons faire la multiplication {num1} × {num2} = {result} cristaux au total."
            ),
            (
                f"Sur {random.choice(StarWarsNarratives.LOCATIONS)}, chaque escadron compte {num2} X-wings. Si la Résistance dispose de {num1} escadrons, combien de X-wings cela représente-t-il?",
                f"Pour trouver le nombre total de vaisseaux, nous multiplions le nombre d'escadrons ({num1}) par le nombre de X-wings dans chaque escadron ({num2}). Donc {num1} × {num2} = {result} X-wings au total."
            ),
            (
                f"Un stormtrooper transporte {num2} blasters. Combien de blasters sont transportés par {num1} stormtroopers?",
                f"Dans ce problème de multiplication, nous calculons combien d'objets sont portés au total. Avec {num2} blasters par stormtrooper et {num1} stormtroopers, la multiplication est {num1} × {num2} = {result} blasters au total."
            )
        ]
        
        question_template, explanation_template = random.choice(multiplication_templates)
        
        exercise_data.update({
            "title": f"[{Messages.AI_EXERCISE_PREFIX}] Forces galactiques - Multiplication niveau {difficulty}",
            "question": question_template,
            "correct_answer": str(result),
            "num1": num1,
            "num2": num2,
            "explanation": f"[{Messages.AI_EXERCISE_PREFIX}] {explanation_prefix} {explanation_template} {explanation_suffix}"
        })
        
    elif normalized_type == ExerciseTypes.DIVISION:
        # Générer une division avec reste nul
        divisor_range = type_limits.get("divisor_range", (2, 10))
        result_range = type_limits.get("result_range", (1, 10))
        
        # Pour assurer une division sans reste, on génère d'abord le diviseur et le quotient
        num2 = random.randint(divisor_range[0], divisor_range[1])  # diviseur
        result = random.randint(result_range[0], result_range[1])  # quotient
        num1 = num2 * result  # dividende
        
        # Modèles de question de division avec thématique Star Wars
        division_templates = [
            # Format: (question, explication)
            (
                f"{num1} jeunes Padawans doivent être répartis en groupes de {num2} pour s'entraîner avec différents Maîtres Jedi. Combien de groupes seront formés?",
                f"Pour résoudre ce problème, nous devons diviser le nombre total de Padawans ({num1}) par la taille de chaque groupe ({num2}). Le calcul est {num1} ÷ {num2} = {result} groupes."
            ),
            (
                f"La Résistance a récupéré {num1} caisses de provisions qui doivent être réparties équitablement entre {num2} bases sur différentes planètes. Combien de caisses chaque base recevra-t-elle?",
                f"Il s'agit d'une division où nous partageons {num1} caisses entre {num2} bases. En effectuant {num1} ÷ {num2}, nous obtenons {result} caisses par base."
            ),
            (
                f"{num1} stormtroopers sont divisés en escouades de {num2}. Combien d'escouades complètes peuvent être formées?",
                f"Pour déterminer le nombre d'escouades, nous divisons le nombre total de stormtroopers ({num1}) par le nombre de stormtroopers par escouade ({num2}). Le calcul est donc {num1} ÷ {num2} = {result} escouades."
            )
        ]
        
        question_template, explanation_template = random.choice(division_templates)
        
        exercise_data.update({
            "title": f"[{Messages.AI_EXERCISE_PREFIX}] Tactique impériale - Division niveau {difficulty}",
            "question": question_template,
            "correct_answer": str(result),
            "num1": num1,
            "num2": num2,
            "explanation": f"[{Messages.AI_EXERCISE_PREFIX}] {explanation_prefix} {explanation_template} {explanation_suffix}"
        })
    
    else:
        # Par défaut, création d'un exercice d'addition
        min_val, max_val = type_limits.get("min", 1), type_limits.get("max", 10)
        num1, num2 = random.randint(min_val, max_val), random.randint(min_val, max_val)
        result = num1 + num2
        
        character = random.choice(StarWarsNarratives.CHARACTERS)
        object_type = random.choice(StarWarsNarratives.OBJECTS)
        location = random.choice(StarWarsNarratives.LOCATIONS)
        
        question = f"{character} a trouvé {num1} {object_type} sur {location}. Plus tard, il en trouve encore {num2}. Combien de {object_type} a-t-il maintenant?"
        explanation = f"Au début, {character} avait {num1} {object_type}, puis a trouvé {num2} autres. Pour résoudre ce problème d'addition, il faut calculer {num1} + {num2} = {result} {object_type} au total."
        
        exercise_data.update({
            "title": f"[{Messages.AI_EXERCISE_PREFIX}] Aventure sur {location} - Addition niveau {difficulty}",
            "question": question,
            "correct_answer": str(result),
            "num1": num1,
            "num2": num2,
            "explanation": f"[{Messages.AI_EXERCISE_PREFIX}] {explanation_prefix} {explanation} {explanation_suffix}"
        })
    
    # Générer des choix pertinents en fonction du résultat
    result_int = int(result)
    choices = [str(result_int)]
    
    # Ajouter des erreurs typiques en fonction du type d'exercice
    if normalized_type == ExerciseTypes.ADDITION:
        choices.extend([str(result_int + 1), str(result_int - 1), str(num1 * num2)])
    elif normalized_type == ExerciseTypes.SUBTRACTION:
        choices.extend([str(result_int + 1), str(result_int - 1), str(num2 - num1 if num2 > num1 else 1)])
    elif normalized_type == ExerciseTypes.MULTIPLICATION:
        choices.extend([str(result_int + num1), str(result_int - num2), str(num1 + num2)])
    elif normalized_type == ExerciseTypes.DIVISION:
        choices.extend([str(result_int + 1), str(result_int - 1), str(num1 // (num2+1) if num2 < num1 else 1)])
    
    # Assurer au moins 4 choix uniques
    while len(set(choices)) < 4:
        new_choice = str(result_int + random.randint(-10, 10))
        if new_choice != str(result_int) and int(new_choice) > 0:
            choices.append(new_choice)
    
    # Limiter à 4 choix et mélanger
    choices = list(set(choices))[:4]
    if str(result_int) not in choices:
        choices[0] = str(result_int)
    random.shuffle(choices)
    
    exercise_data["choices"] = choices
    
    return exercise_data



def generate_simple_exercise(exercise_type, difficulty):
    """Génère un exercice simple de manière algorithmique"""
    import random

    normalized_type = normalize_exercise_type(exercise_type)
    normalized_difficulty = normalize_difficulty(difficulty)
    
    # Récupérer les limites pour ce type et cette difficulté
    difficulty_config = DIFFICULTY_LIMITS.get(normalized_difficulty, DIFFICULTY_LIMITS[DifficultyLevels.PADAWAN])
    
    # Limites par défaut si le type n'est pas trouvé
    type_limits = difficulty_config.get(normalized_type, difficulty_config.get("default", {"min": 1, "max": 10}))
    
    # Structure de base commune pour tous les types d'exercices
    exercise_data = {
        "exercise_type": normalized_type,
        "difficulty": normalized_difficulty
    }
    
    if normalized_type == ExerciseTypes.ADDITION:
        # Génération d'une addition
        min_val, max_val = type_limits.get("min", 1), type_limits.get("max", 10)
        num1, num2 = random.randint(min_val, max_val), random.randint(min_val, max_val)
        
        result = num1 + num2
        question = ExerciseMessages.QUESTION_ADDITION.format(num1=num1, num2=num2)
        correct_answer = str(result)
        choices = [str(result), str(result-1), str(result+1), str(result+2)]
        random.shuffle(choices)

        exercise_data.update({
            "title": ExerciseMessages.TITLE_ADDITION,
            "question": question,
            "correct_answer": correct_answer,
            "choices": choices,
            "tags": Tags.ALGORITHMIC + "," + Tags.SIMPLE,
            "num1": num1,
            "num2": num2,
            "explanation": f"Pour additionner {num1} et {num2}, il faut calculer leur somme, donc {num1} + {num2} = {result}."
        })
        return exercise_data

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

        exercise_data.update({
            "title": ExerciseMessages.TITLE_SUBTRACTION,
            "question": question,
            "correct_answer": correct_answer,
            "choices": choices,
            "tags": Tags.ALGORITHMIC + "," + Tags.SIMPLE,
            "num1": num1,
            "num2": num2,
            "explanation": f"Pour soustraire {num2} de {num1}, il faut calculer leur différence, donc {num1} - {num2} = {result}."
        })
        return exercise_data

    elif normalized_type == ExerciseTypes.MULTIPLICATION:
        # Génération d'une multiplication
        min_val, max_val = type_limits.get("min", 1), type_limits.get("max", 10)
        num1, num2 = random.randint(min_val, max_val), random.randint(min_val, max_val)

        result = num1 * num2
        question = ExerciseMessages.QUESTION_MULTIPLICATION.format(num1=num1, num2=num2)
        correct_answer = str(result)
        choices = [str(result), str(result-num1), str(result+num1), str(result+num2)]
        random.shuffle(choices)

        exercise_data.update({
            "title": ExerciseMessages.TITLE_MULTIPLICATION,
            "question": question,
            "correct_answer": correct_answer,
            "choices": choices,
            "tags": Tags.ALGORITHMIC + "," + Tags.SIMPLE,
            "num1": num1,
            "num2": num2,
            "explanation": f"Pour multiplier {num1} par {num2}, il faut calculer leur produit, donc {num1} × {num2} = {result}."
        })
        return exercise_data

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

        exercise_data.update({
            "title": ExerciseMessages.TITLE_DIVISION,
            "question": question,
            "correct_answer": correct_answer,
            "choices": choices,
            "tags": Tags.ALGORITHMIC + "," + Tags.SIMPLE,
            "num1": num1,
            "num2": num2,
            "explanation": f"Pour diviser {num1} par {num2}, il faut calculer leur quotient, donc {num1} ÷ {num2} = {result}."
        })
        return exercise_data

    else:
        # Par défaut, faire une addition si le type n'est pas reconnu
        min_val, max_val = 1, 10
        num1, num2 = random.randint(min_val, max_val), random.randint(min_val, max_val)
        
        result = num1 + num2
        question = ExerciseMessages.QUESTION_ADDITION.format(num1=num1, num2=num2)
        correct_answer = str(result)
        choices = [str(result), str(result-1), str(result+1), str(result+2)]
        random.shuffle(choices)

        exercise_data.update({
            "title": ExerciseMessages.TITLE_DEFAULT,
            "question": question,
            "correct_answer": correct_answer,
            "choices": choices,
            "tags": Tags.ALGORITHMIC + "," + Tags.SIMPLE,
            "num1": num1,
            "num2": num2,
            "explanation": f"Pour additionner {num1} et {num2}, il faut calculer leur somme, donc {num1} + {num2} = {result}."
        })
        return exercise_data

async def submit_answer(request):
    """Traite la soumission d'une réponse à un exercice"""
    try:
        # Récupérer les données de la requête
        data = await request.json()
        exercise_id = data.get('exercise_id')
        selected_answer = data.get('selected_answer')
        time_spent = data.get('time_spent', 0)
        user_id = data.get('user_id', 1)  # Utiliser l'ID 1 par défaut pour un utilisateur non authentifié

        print(f"Traitement de la réponse: exercise_id={exercise_id}, selected_answer={selected_answer}")

        # Récupérer l'exercice pour vérifier la réponse
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(ExerciseQueries.GET_BY_ID, (exercise_id,))
        columns = [desc[0] for desc in cursor.description]
        row = cursor.fetchone()

        if not row:
            conn.close()
            return JSONResponse({"error": SystemMessages.ERROR_EXERCISE_NOT_FOUND}, status_code=404)

        exercise = dict(zip(columns, row))
        is_correct = selected_answer == exercise['correct_answer']
        
        print(f"Réponse correcte? {is_correct}")

        # Enregistrer le résultat dans la table results
        try:
            print("Tentative d'insertion dans la table results...")
            cursor.execute(ResultQueries.INSERT, (
                exercise_id,     # exercise_id
                is_correct,      # is_correct
                1,               # attempt_count (par défaut 1 pour la première tentative)
                time_spent       # time_spent
            ))
            print("Insertion réussie dans la table results")
            
            # Commit immédiatement après l'insertion réussie
            conn.commit()
            print("Transaction validée (commit) pour l'insertion de résultat")
        except Exception as e:
            print(f"ERREUR lors de l'insertion dans results: {e}")
            conn.rollback()
            print("Transaction annulée (rollback) suite à l'erreur")
            # Renvoyer une réponse avec l'erreur mais continuer pour l'affichage côté client
            return JSONResponse({
                "is_correct": is_correct,
                "correct_answer": exercise['correct_answer'],
                "explanation": exercise.get('explanation', ""),
                "error": f"Erreur lors de l'enregistrement du résultat: {str(e)}"
            }, status_code=500)

        # Mettre à jour les statistiques user_stats
        exercise_type = normalize_exercise_type(exercise['exercise_type'])
        difficulty = normalize_difficulty(exercise['difficulty'])

        try:
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
                print(f"Statistiques mises à jour pour type={exercise_type}, difficulté={difficulty}")
            else:
                # Créer une nouvelle entrée
                cursor.execute("""
                    INSERT INTO user_stats (exercise_type, difficulty, total_attempts, correct_attempts)
                    VALUES (%s, %s, %s, %s)
                """, (exercise_type, difficulty, 1, 1 if is_correct else 0))
                print(f"Nouvelles statistiques créées pour type={exercise_type}, difficulté={difficulty}")
            
            # Commit pour les statistiques
            conn.commit()
            print("Transaction validée (commit) pour les statistiques")
        except Exception as stats_error:
            print(f"ERREUR lors de la mise à jour des statistiques: {stats_error}")
            conn.rollback()
            # On continue malgré l'erreur car les résultats sont déjà enregistrés

        conn.close()
        print("Connexion fermée, traitement terminé avec succès")

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
        
        # Récupérer les paramètres de requête
        limit = int(request.query_params.get('limit', 10))
        skip = int(request.query_params.get('skip', 0))
        exercise_type = request.query_params.get('exercise_type', None)
        difficulty = request.query_params.get('difficulty', None)
        
        print(f"API - Paramètres reçus: exercise_type={exercise_type}, difficulty={difficulty}")
        
        # Normaliser les paramètres si présents
        if exercise_type:
            exercise_type = normalize_exercise_type(exercise_type)
            print(f"API - Type d'exercice normalisé: {exercise_type}")
        if difficulty:
            difficulty = normalize_difficulty(difficulty)
            print(f"API - Difficulté normalisée: {difficulty}")
        
        # Choisir la requête appropriée selon les paramètres
        if exercise_type and difficulty:
            cursor.execute(ExerciseQueries.GET_BY_TYPE_AND_DIFFICULTY, (exercise_type, difficulty))
        elif exercise_type:
            cursor.execute(ExerciseQueries.GET_BY_TYPE, (exercise_type,))
        elif difficulty:
            cursor.execute(ExerciseQueries.GET_BY_DIFFICULTY, (difficulty,))
        else:
            cursor.execute(ExerciseQueries.GET_ALL)

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

        # Appliquer pagination manuellement
        total = len(exercises)
        paginated_exercises = exercises[skip:skip+limit] if skip < total else []

        return JSONResponse({
            "items": paginated_exercises,
            "total": total,
            "skip": skip,
            "limit": limit
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
        cursor.execute(ExerciseQueries.GET_BY_ID, (exercise_id,))
        if cursor.fetchone() is None:
            conn.close()
            return JSONResponse({"error": SystemMessages.ERROR_EXERCISE_NOT_FOUND}, status_code=404)

        # Supprimer les résultats associés à cet exercice (si la table a une contrainte de clé étrangère)
        try:
            cursor.execute("DELETE FROM results WHERE exercise_id = %s", (exercise_id,))
        except Exception as e:
            # Ignorer les erreurs ici, car la table results pourrait ne pas avoir de contrainte
            print(f"Note: Impossible de supprimer les résultats associés: {e}")

        # Supprimer l'exercice
        cursor.execute(ExerciseQueries.DELETE, (exercise_id,))
        conn.commit()
        conn.close()

        return JSONResponse({"success": True, "message": SystemMessages.SUCCESS_DELETED}, status_code=200)

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
        # ID utilisateur fictif pour l'instant (sera remplacé par l'authentification plus tard)
        user_id = 1
        
        print("Début de la récupération des statistiques utilisateur")
        conn = get_db_connection()
        cursor = conn.cursor()

        # Récupérer les statistiques globales
        print("Exécution de la requête pour récupérer les statistiques globales")
        cursor.execute("""
        SELECT
            SUM(total_attempts) as total_exercises,
            SUM(correct_attempts) as correct_answers
        FROM user_stats
        """)
        
        columns = [desc[0] for desc in cursor.description]
        row = cursor.fetchone()
        print(f"Statistiques globales brutes: {row}")
        overall_stats = dict(zip(columns, row)) if row else {"total_exercises": 0, "correct_answers": 0}
        print(f"Statistiques globales formatées: {overall_stats}")

        # Calculer le taux de réussite
        total_exercises = overall_stats.get('total_exercises', 0) or 0
        correct_answers = overall_stats.get('correct_answers', 0) or 0
        success_rate = int((correct_answers / total_exercises * 100) if total_exercises > 0 else 0)
        print(f"Taux de réussite calculé: {success_rate}%")

        # Statistiques par type d'exercice
        performance_by_type = {}
        exercise_type_data = []  # Pour stocker les données pour le graphique de progression
        
        print("Récupération des statistiques par type d'exercice")
        for exercise_type in ExerciseTypes.ALL_TYPES[:4]:  # Pour l'instant, juste les 4 types de base
            print(f"Récupération des statistiques pour le type {exercise_type}")
            cursor.execute("""
            SELECT
                SUM(total_attempts) as total,
                SUM(correct_attempts) as correct
            FROM user_stats
            WHERE exercise_type = %s
            """, (exercise_type,))
            
            columns = [desc[0] for desc in cursor.description]
            row = cursor.fetchone()
            print(f"Statistiques brutes pour {exercise_type}: {row}")
            type_stats = dict(zip(columns, row)) if row else {"total": 0, "correct": 0}

            total = type_stats.get('total', 0) or 0
            correct = type_stats.get('correct', 0) or 0
            success_rate_type = int((correct / total * 100) if total > 0 else 0)
            print(f"Taux de réussite pour {exercise_type}: {success_rate_type}%")

            # Convertir les types en français pour le frontend
            type_fr = {
                ExerciseTypes.ADDITION: 'Addition', 
                ExerciseTypes.SUBTRACTION: 'Soustraction',
                ExerciseTypes.MULTIPLICATION: 'Multiplication', 
                ExerciseTypes.DIVISION: 'Division'
            }
            
            # Stocker les données pour le graphique (utiliser les statistiques réelles)
            exercise_type_data.append(total)

            performance_by_type[type_fr.get(exercise_type, exercise_type).lower()] = {
                'completed': total,
                'correct': correct,
                'success_rate': success_rate_type
            }
        
        print(f"Performance par type complète: {performance_by_type}")

        # Récupérer les exercices récents pour l'activité
        print("Récupération des exercices récents")
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
        print(f"Nombre d'exercices récents trouvés: {len(rows)}")
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
        
        print(f"Nombre d'activités récentes formatées: {len(recent_activity)}")
        
        # Récupérer les statistiques d'exercices par jour sur les 30 derniers jours
        print("Récupération des exercices par jour sur les 30 derniers jours")
        try:
            cursor.execute(UserStatsQueries.GET_EXERCISES_BY_DAY)
            
            daily_data = cursor.fetchall()
            print(f"Nombre de jours avec des exercices: {len(daily_data)}")
            
            # Créer un dict avec tous les jours des 30 derniers jours
            from datetime import datetime, timedelta
            current_date = datetime.now().date()
            
            # Initialiser avec zéro pour chaque jour
            daily_exercises = {}
            for i in range(30, -1, -1):
                day = current_date - timedelta(days=i)
                day_str = day.strftime("%d/%m")
                daily_exercises[day_str] = 0
            
            # Remplir avec les données réelles
            for row in daily_data:
                try:
                    # Si la date est au format YYYY-MM-DD (comme retourné par DATE())
                    date_str = row[0]  # Format YYYY-MM-DD
                    # Convertir en objet date pour le formater en DD/MM
                    if isinstance(date_str, str):
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                    else:
                        date_obj = date_str  # Déjà un objet date
                    day_str = date_obj.strftime("%d/%m")
                    
                    daily_exercises[day_str] = row[1]  # Nombre d'exercices ce jour-là
                    print(f"Jour {day_str}: {row[1]} exercices")
                except Exception as e:
                    print(f"Erreur lors du traitement de la date {row[0]}: {e}")
                    continue
            
            # Créer les données pour le graphique par jour
            daily_labels = list(daily_exercises.keys())
            daily_counts = list(daily_exercises.values())
            
            print(f"Données du graphique quotidien générées: {len(daily_labels)} jours")
        except Exception as e:
            print(f"Erreur lors de la récupération des exercices quotidiens: {e}")
            traceback.print_exc()
            
            # En cas d'erreur, utiliser des données vides plutôt que des données aléatoires
            print("Utilisation de données vides pour le graphique quotidien")
            
            from datetime import datetime, timedelta
            current_date = datetime.now().date()
            
            daily_exercises = {}
            for i in range(30, -1, -1):
                day = current_date - timedelta(days=i)
                day_str = day.strftime("%d/%m")
                daily_exercises[day_str] = 0
            
            daily_labels = list(daily_exercises.keys())
            daily_counts = list(daily_exercises.values())
            
        # Graphique des exercices quotidiens
        exercises_by_day = {
            'labels': daily_labels,
            'datasets': [{
                'label': 'Exercices par jour',
                'data': daily_counts,
                'borderColor': 'rgba(255, 206, 86, 1)',
                'backgroundColor': 'rgba(255, 206, 86, 0.2)',
            }]
        }

        # Simuler les données de niveau pour le moment
        level_data = {
            'current': 1,
            'title': 'Débutant Stellaire',
            'current_xp': 25,
            'next_level_xp': 100
        }

        # Utiliser les données par type d'exercice pour le graphique de progression
        print("Construction du graphique basé sur les données réelles")
        
        # Vérifier si nous avons des données réelles
        if sum(exercise_type_data) > 0:
            type_labels = ['Addition', 'Soustraction', 'Multiplication', 'Division']
            print(f"Données pour le graphique par type d'exercice: {exercise_type_data}")
            
            progress_over_time = {
                'labels': type_labels,
                'datasets': [{
                    'label': 'Exercices résolus',
                    'data': exercise_type_data
                }]
            }
        else:
            # Si aucune donnée réelle, générer des données de test
            print("Aucune donnée réelle pour le graphique, génération de données de test")
            progress_over_time = {
                'labels': ['Addition', 'Soustraction', 'Multiplication', 'Division'],
                'datasets': [{
                    'label': 'Exercices résolus',
                    'data': [10, 5, 8, 3]
                }]
            }
        
        print(f"Structure finale du graphique: {progress_over_time}")

        conn.close()

        response_data = {
            'total_exercises': total_exercises,
            'correct_answers': correct_answers,
            'success_rate': success_rate,
            'experience_points': total_exercises * 10,  # Points d'XP simulés
            'performance_by_type': performance_by_type,
            'recent_activity': recent_activity,
            'level': level_data,
            'progress_over_time': progress_over_time,
            'exercises_by_day': exercises_by_day
        }
        
        print("Données du tableau de bord générées complètes:", response_data)
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
    Route("/exercises/{exercise_id:int}", exercise_detail_page),
    Route("/api/users/stats", get_user_stats),

    # API
    Route("/api/exercises", get_exercises_list),
    Route("/api/exercises/{exercise_id:int}", get_exercise),
    Route("/api/exercises/{exercise_id:int}", delete_exercise, methods=["DELETE"]),
    Route("/api/exercises/generate", generate_exercise),
    Route("/api/exercises/{exercise_id:int}/submit", submit_answer, methods=["POST"]),
    Route("/api/submit-answer", submit_answer, methods=["POST"]),  # Route alternative pour la soumission des exercices

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
