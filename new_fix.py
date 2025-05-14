"""
Deuxième tentative pour corriger enhanced_server.py
"""

import os
import sys

def main():
    print("Application des correctifs à enhanced_server.py...")
    
    # Vérifier si le fichier existe
    if not os.path.exists("enhanced_server.py"):
        print("Erreur: Le fichier enhanced_server.py est manquant!")
        return 1
    
    # Créer une sauvegarde
    with open("enhanced_server.py", "r", encoding="utf-8") as f:
        original_content = f.read()
    
    # Écrire le fichier corrigé directement
    with open("enhanced_server_fixed.py", "w", encoding="utf-8") as f:
        # Écrire le début du fichier jusqu'à la fonction submit_answer
        start_marker = 'async def submit_answer(request):'
        start_pos = original_content.find(start_marker)
        if start_pos == -1:
            print("Erreur: Impossible de trouver la fonction submit_answer!")
            return 1
        
        f.write(original_content[:start_pos])
        
        # Écrire la fonction submit_answer corrigée
        f.write("""async def submit_answer(request):
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
""")
        
        # Trouver la fonction get_exercises_list
        start_marker_exercises = 'async def get_exercises_list(request):'
        start_pos_exercises = original_content.find(start_marker_exercises)
        if start_pos_exercises == -1:
            print("Erreur: Impossible de trouver la fonction get_exercises_list!")
            return 1
        
        # Trouver la fin de la fonction submit_answer et le début de la fonction get_exercises_list
        end_pos = original_content.find('async def', start_pos + 1)
        if end_pos == -1 or end_pos > start_pos_exercises:
            end_pos = start_pos_exercises
        
        # Écrire le code entre submit_answer et get_exercises_list
        f.write(original_content[end_pos:start_pos_exercises])
        
        # Écrire la fonction get_exercises_list corrigée
        f.write("""async def get_exercises_list(request):
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
""")
        
        # Trouver la fonction get_user_stats
        start_marker_stats = 'async def get_user_stats(request):'
        start_pos_stats = original_content.find(start_marker_stats)
        if start_pos_stats == -1:
            print("Erreur: Impossible de trouver la fonction get_user_stats!")
            return 1
        
        # Trouver la fin de la fonction get_exercises_list et le début de la fonction get_user_stats
        end_pos = original_content.find('async def', start_pos_exercises + 1)
        if end_pos == -1 or end_pos > start_pos_stats:
            end_pos = start_pos_stats
        
        # Écrire le code entre get_exercises_list et get_user_stats
        f.write(original_content[end_pos:start_pos_stats])
        
        # Écrire la fonction get_user_stats corrigée
        f.write("""async def get_user_stats(request):
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
        cursor.execute('''
        SELECT 
            SUM(total_attempts) as total_exercises,
            SUM(correct_attempts) as correct_answers
        FROM user_stats
        ''')
        
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
            cursor.execute('''
            SELECT 
                SUM(total_attempts) as total,
                SUM(correct_attempts) as correct
            FROM user_stats
                WHERE exercise_type = %s
            ''', (exercise_type,))
            
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
""")
        
        # Trouver la fin de la fonction get_user_stats et écrire le reste du fichier
        end_pos = original_content.find('async def', start_pos_stats + 1)
        if end_pos == -1:
            # Si c'est la dernière fonction, écrire jusqu'à la fin du fichier
            f.write(original_content[original_content.find('\n', start_pos_stats + len(start_marker_stats)):])
        else:
            # Sinon, trouver la fin de get_user_stats
            next_def_pos = original_content.find('async def', start_pos_stats + len(start_marker_stats))
            if next_def_pos != -1:
                # Écrire le reste du fichier
                f.write(original_content[next_def_pos:])
            else:
                # S'il n'y a pas d'autre fonction, écrire jusqu'à la fin
                f.write(original_content[original_content.find('\n', start_pos_stats + len(start_marker_stats)):])
    
    print("Fichier enhanced_server_fixed.py créé avec succès!")
    print("Pour tester la correction: python mathakine_cli.py run --server-file=enhanced_server_fixed.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 