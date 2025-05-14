import re

# Lire le fichier enhanced_server.py
with open('enhanced_server.py', 'r', encoding='utf-8') as file:
    content = file.read()

# Définir la fonction get_user_stats à ajouter
get_user_stats_function = '''
async def get_user_stats(request):
    """
    Endpoint pour obtenir les statistiques utilisateur pour le tableau de bord.
    Route: /api/users/stats
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Récupérer les statistiques globales
    cursor.execute("""
    SELECT
        SUM(total_attempts) as total_exercises,
        SUM(correct_attempts) as correct_answers
    FROM user_stats
    """)
    overall_stats = cursor.fetchone()

    # Calculer le taux de réussite
    total_exercises = overall_stats['total_exercises'] or 0
    correct_answers = overall_stats['correct_answers'] or 0
    success_rate = int((correct_answers / total_exercises * 100) if total_exercises > 0 else 0)

    # Statistiques par type d'exercice
    performance_by_type = {}
    for exercise_type in ['addition', 'subtraction', 'multiplication', 'division']:
        cursor.execute("""
        SELECT
            SUM(total_attempts) as total,
            SUM(correct_attempts) as correct
        FROM user_stats
        WHERE exercise_type = ?
        """, (exercise_type,))
        type_stats = cursor.fetchone()

        total = type_stats['total'] or 0
        correct = type_stats['correct'] or 0
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
    recent_results = cursor.fetchall()

    # Formater les activités récentes
    recent_activity = []
    for result in recent_results:
        try:
            timestamp = datetime.fromisoformat(result['completed_at'].replace('Z'
                , '+00:00')) if 'Z' in result['completed_at'] else datetime.fromisoformat(result['completed_at'])
            formatted_time = timestamp.strftime("%d/%m/%Y %H:%M")
        except Exception:
            formatted_time = str(result['completed_at'])

        activity = {
            'type': 'exercise_completed',
            'is_correct': bool(result['is_correct']),
            'description': f"{'Réussite' if result['is_correct'] else 'Échec'} : {result['question']}",
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

    # Simuler les données de progression dans le temps
    progress_over_time = {
        'labels': ['J-6', 'J-5', 'J-4', 'J-3', 'J-2', 'J-1', 'Aujourd\\'hui'],
        'datasets': [{
            'label': 'Exercices résolus',
            'data': [0, 2, 5, 3, 8, 4, total_exercises - 22 if total_exercises > 22 else 0]
        }]
    }

    conn.close()

    return JSONResponse({
        'total_exercises': total_exercises,
        'correct_answers': correct_answers,
        'success_rate': success_rate,
        'experience_points': total_exercises * 10,  # Points d'XP simulés
        'performance_by_type': performance_by_type,
        'recent_activity': recent_activity,
        'level': level_data,
        'progress_over_time': progress_over_time
    })
'''

# Ajouter la fonction avant la définition des routes
pattern = r'# Création de l\'application'
if re.search(pattern, content):
    content = re.sub(pattern, get_user_stats_function + '\n\n# Création de l\'application', content)

# Ajouter la route à la liste des routes
pattern = r'Route\("/exercise/{exercise_id:int}", exercise_detail_page\),'
if re.search(pattern, content):
    replacement = pattern + '\n    Route("/api/users/stats", get_user_stats),'
    content = content.replace(pattern, replacement)

# Ecrire le contenu modifié
with open('enhanced_server.py', 'w', encoding='utf-8') as file:
    file.write(content)

print("Fonction get_user_stats et route ajoutées avec succès!")
