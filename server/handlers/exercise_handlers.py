"""
Handlers pour la génération d'exercices (API)
"""
import traceback
import json
from starlette.responses import JSONResponse, RedirectResponse
from app.services.enhanced_server_adapter import EnhancedServerAdapter
from server.exercise_generator import generate_ai_exercise, generate_simple_exercise, ensure_explanation
from app.core.messages import SystemMessages
from app.models.exercise import ExerciseType

# Import du service de badges
from app.services.badge_service import BadgeService

# Fonction pour obtenir l'utilisateur courant
async def get_current_user(request):
    """Récupère l'utilisateur actuellement authentifié"""
    try:
        access_token = request.cookies.get("access_token")
        if not access_token:
            return None
            
        # Utiliser le service d'authentification pour décoder le token
        from app.core.security import decode_token
        from app.services.auth_service import get_user_by_username
        
        # Décoder le token pour obtenir le nom d'utilisateur
        payload = decode_token(access_token)
        username = payload.get("sub")
        
        if not username:
            return None
            
        # Récupérer l'utilisateur depuis la base de données
        db = EnhancedServerAdapter.get_db_session()
        try:
            user = get_user_by_username(db, username)
            if user:
                return {
                    "is_authenticated": True,
                    "id": user.id,
                    "username": user.username,
                    "role": user.role
                }
        finally:
            EnhancedServerAdapter.close_db_session(db)
            
    except Exception as e:
        print(f"Erreur lors de la récupération de l'utilisateur: {str(e)}")
        
    return None

# Fonction pour obtenir une session de base de données
def get_session():
    """Récupère une session de base de données via l'adaptateur"""
    return EnhancedServerAdapter.get_db_session()

async def generate_exercise(request):
    """Génère un nouvel exercice"""
    params = request.query_params
    exercise_type = params.get('type')
    difficulty = params.get('difficulty')
    use_ai = params.get('ai', False)
    ai_generated = False
    if use_ai and str(use_ai).lower() in ['true', '1', 'yes', 'y']:
        exercise_dict = generate_ai_exercise(exercise_type, difficulty)
        ai_generated = True
    else:
        exercise_dict = generate_simple_exercise(exercise_type, difficulty)
    exercise_dict = ensure_explanation(exercise_dict)
    print(f"Explication générée: {exercise_dict['explanation']}")
    try:
        db = EnhancedServerAdapter.get_db_session()
        try:
            created_exercise = EnhancedServerAdapter.create_generated_exercise(
                db=db,
                exercise_type=exercise_dict['exercise_type'],
                difficulty=exercise_dict['difficulty'],
                title=exercise_dict['title'],
                question=exercise_dict['question'],
                correct_answer=exercise_dict['correct_answer'],
                choices=exercise_dict['choices'],
                explanation=exercise_dict['explanation'],
                hint=exercise_dict.get('hint'),
                tags=exercise_dict.get('tags', 'generated'),
                ai_generated=ai_generated
            )
            if created_exercise:
                exercise_id = created_exercise['id']
                print(f"Nouvel exercice créé avec ID={exercise_id}, explication: {exercise_dict['explanation']}")
            else:
                print("Erreur: L'exercice n'a pas été créé")
                templates = request.app.state.templates
                return templates.TemplateResponse("error.html", {
                    "request": request,
                    "error": "Erreur de génération",
                    "message": "Impossible de créer l'exercice dans la base de données."
                }, status_code=500)
        finally:
            EnhancedServerAdapter.close_db_session(db)
        return RedirectResponse(url="/exercises?generated=true", status_code=303)
    except Exception as e:
        print(f"Erreur lors de la génération d'exercice: {e}")
        traceback.print_exc()
        templates = request.app.state.templates
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": "Erreur de génération",
            "message": f"Impossible de générer l'exercice: {str(e)}"
        }, status_code=500)

async def get_exercise(request):
    """Récupère un exercice par son ID"""
    exercise_id = request.path_params.get('exercise_id')

    try:
        # Utiliser l'adaptateur pour récupérer l'exercice
        db = EnhancedServerAdapter.get_db_session()
        
        try:
            exercise = EnhancedServerAdapter.get_exercise_by_id(db, exercise_id)
            
            if not exercise:
                return JSONResponse({"error": SystemMessages.ERROR_EXERCISE_NOT_FOUND}, status_code=404)
            
            # Convertir les objets datetime en chaînes pour la sérialisation JSON
            if 'created_at' in exercise and exercise['created_at']:
                exercise['created_at'] = exercise['created_at'].isoformat()
            if 'updated_at' in exercise and exercise['updated_at']:
                exercise['updated_at'] = exercise['updated_at'].isoformat()
                
            return JSONResponse(exercise)
        
        finally:
            EnhancedServerAdapter.close_db_session(db)
    
    except Exception as e:
        print(f"Erreur lors de la récupération de l'exercice: {e}")
        traceback.print_exc()
        return JSONResponse({"error": f"Erreur: {str(e)}"}, status_code=500)

async def submit_answer(request):
    """Traite la soumission d'une réponse à un exercice"""
    try:
        # Vérifier l'authentification de l'utilisateur
        current_user = await get_current_user(request)
        if not current_user:
            return JSONResponse(
                {"error": "Vous devez être authentifié pour soumettre une réponse."},
                status_code=401
            )
        
        # Récupérer les données de la requête
        data = await request.json()
        exercise_id = data.get('exercise_id')
        selected_answer = data.get('answer') or data.get('selected_answer')  # Support both formats
        time_spent = data.get('time_spent', 0)
        user_id = current_user.get('id', 1)  # Utiliser l'ID de l'utilisateur authentifié

        # Valider les paramètres requis
        if exercise_id is None:
            return JSONResponse(
                {"error": "L'ID de l'exercice est requis."},
                status_code=400
            )
        
        if selected_answer is None:
            return JSONResponse(
                {"error": "La réponse est requise."},
                status_code=400
            )

        print(f"Traitement de la réponse: exercise_id={exercise_id}, selected_answer={selected_answer}")

        # Utiliser l'adaptateur pour obtenir une session SQLAlchemy
        db = EnhancedServerAdapter.get_db_session()
        
        try:
            # Récupérer l'exercice pour vérifier la réponse
            exercise = EnhancedServerAdapter.get_exercise_by_id(db, exercise_id)
            if not exercise:
                return JSONResponse({"error": SystemMessages.ERROR_EXERCISE_NOT_FOUND}, status_code=404)

            # Déterminer si la réponse est correcte
            is_correct = False
            
            # Types d'exercices qui devraient avoir une comparaison insensible à la casse
            text_based_types = [ExerciseType.TEXTE.value, ExerciseType.MIXTE.value]
            
            # Pour les types de questions textuelles, la comparaison est insensible à la casse
            if exercise.get('exercise_type') in text_based_types:
                is_correct = selected_answer.lower().strip() == exercise['correct_answer'].lower().strip()
            else:
                # Pour les questions numériques et autres, comparaison stricte
                is_correct = selected_answer == exercise['correct_answer']
                
            print(f"Réponse correcte? {is_correct}")

            # Enregistrer la tentative avec notre adaptateur
            attempt_data = {
                "user_id": user_id,
                "exercise_id": exercise_id,
                "user_answer": selected_answer,
                "is_correct": is_correct,
                "time_spent": time_spent
            }
            
            attempt = EnhancedServerAdapter.record_attempt(db, attempt_data)
            
            if not attempt:
                print("ERREUR: La tentative n'a pas été enregistrée correctement")
                return JSONResponse({
                    "is_correct": is_correct,
                    "correct_answer": exercise['correct_answer'],
                    "explanation": exercise.get('explanation', ""),
                    "error": "Erreur lors de l'enregistrement de la tentative"
                }, status_code=500)
                
            print("Tentative enregistrée avec succès")

            # 🎖️ NOUVEAU: Vérifier et attribuer les badges
            new_badges = []
            try:
                badge_service = BadgeService(db)
                
                # Préparer les données de la tentative pour l'évaluation des badges
                attempt_for_badges = {
                    "exercise_type": exercise.get('exercise_type'),
                    "is_correct": is_correct,
                    "time_spent": time_spent,
                    "exercise_id": exercise_id
                }
                
                # Vérifier et attribuer les nouveaux badges
                new_badges = badge_service.check_and_award_badges(user_id, attempt_for_badges)
                
                if new_badges:
                    print(f"🎖️ {len(new_badges)} nouveaux badges attribués à l'utilisateur {user_id}")
                    for badge in new_badges:
                        print(f"   - {badge['name']} ({badge['star_wars_title']})")
                
            except Exception as badge_error:
                print(f"⚠️ Erreur lors de la vérification des badges: {badge_error}")
                # Ne pas faire échouer la soumission si les badges échouent
                pass

            # Retourner le résultat avec l'ID de tentative et les nouveaux badges
            response_data = {
                "is_correct": is_correct,
                "correct_answer": exercise['correct_answer'],
                "explanation": exercise.get('explanation', ""),
                "attempt_id": attempt.get('id', 0)
            }
            
            # Ajouter les nouveaux badges à la réponse
            if new_badges:
                response_data["new_badges"] = new_badges
                response_data["badges_earned"] = len(new_badges)
            
            return JSONResponse(response_data)
            
        finally:
            # Fermer la session dans tous les cas
            EnhancedServerAdapter.close_db_session(db)

    except Exception as e:
        print(f"Erreur lors du traitement de la réponse: {e}")
        traceback.print_exc()
        return JSONResponse({"error": f"Erreur: {str(e)}"}, status_code=500)

async def get_exercises_list(request):
    """Retourne la liste des exercices récents"""
    try:
        # Récupérer les paramètres de requête
        limit = int(request.query_params.get('limit', 10))
        skip = int(request.query_params.get('skip', 0))
        exercise_type = request.query_params.get('exercise_type', None)
        difficulty = request.query_params.get('difficulty', None)
        
        print(f"API - Paramètres reçus: exercise_type={exercise_type}, difficulty={difficulty}")
        
        # Utiliser l'adaptateur pour obtenir une session SQLAlchemy
        db = EnhancedServerAdapter.get_db_session()
        
        try:
            # Utiliser l'adaptateur pour lister les exercices
            exercises = EnhancedServerAdapter.list_exercises(
                db,
                exercise_type=exercise_type,
                difficulty=difficulty,
                limit=None  # Nous gérons la pagination manuellement pour être cohérent avec l'existant
            )
            
            # Appliquer pagination manuellement
            total = len(exercises)
            paginated_exercises = exercises[skip:skip+limit] if skip < total else []

            return JSONResponse({
                "items": paginated_exercises,
                "total": total,
                "skip": skip,
                "limit": limit
            })
            
        finally:
            # Fermer la session dans tous les cas
            EnhancedServerAdapter.close_db_session(db)

    except Exception as e:
        print(f"Erreur lors de la récupération des exercices: {e}")
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)

async def generate_exercise_api(request):
    """Génère un nouvel exercice via API JSON (POST)"""
    try:
        # Récupérer les données JSON de la requête
        data = await request.json()
        exercise_type = data.get('exercise_type')
        difficulty = data.get('difficulty')
        use_ai = data.get('ai', False)
        
        print(f"Génération API: type={exercise_type}, difficulté={difficulty}, IA={use_ai}")
        
        # Valider les paramètres
        if not exercise_type or not difficulty:
            return JSONResponse({
                "error": "Les paramètres 'exercise_type' et 'difficulty' sont requis"
            }, status_code=400)
        
        # Générer l'exercice
        ai_generated = False
        if use_ai and str(use_ai).lower() in ['true', '1', 'yes', 'y']:
            exercise_dict = generate_ai_exercise(exercise_type, difficulty)
            ai_generated = True
        else:
            exercise_dict = generate_simple_exercise(exercise_type, difficulty)
        
        exercise_dict = ensure_explanation(exercise_dict)
        
        # Optionnellement sauvegarder en base de données
        save_to_db = data.get('save', True)
        if save_to_db:
            try:
                db = EnhancedServerAdapter.get_db_session()
                try:
                    created_exercise = EnhancedServerAdapter.create_generated_exercise(
                        db=db,
                        exercise_type=exercise_dict['exercise_type'],
                        difficulty=exercise_dict['difficulty'],
                        title=exercise_dict['title'],
                        question=exercise_dict['question'],
                        correct_answer=exercise_dict['correct_answer'],
                        choices=exercise_dict['choices'],
                        explanation=exercise_dict['explanation'],
                        hint=exercise_dict.get('hint'),
                        tags=exercise_dict.get('tags', 'generated'),
                        ai_generated=ai_generated
                    )
                    if created_exercise:
                        exercise_dict['id'] = created_exercise['id']
                        print(f"Exercice sauvegardé avec ID={created_exercise['id']}")
                finally:
                    EnhancedServerAdapter.close_db_session(db)
            except Exception as e:
                print(f"Erreur lors de la sauvegarde: {e}")
                # Continuer même si la sauvegarde échoue
        
        # Retourner l'exercice généré
        return JSONResponse(exercise_dict)
        
    except Exception as e:
        print(f"Erreur lors de la génération d'exercice API: {e}")
        traceback.print_exc()
        return JSONResponse({
            "error": f"Erreur lors de la génération: {str(e)}"
        }, status_code=500) 