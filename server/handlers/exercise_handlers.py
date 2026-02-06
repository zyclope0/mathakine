"""
Handlers pour la génération d'exercices (API)
"""
import json
import traceback

from app.core.logging_config import get_logger

logger = get_logger(__name__)
from starlette.requests import Request
from starlette.responses import (JSONResponse, RedirectResponse,
                                 StreamingResponse)

from app.core.config import settings
from app.core.messages import SystemMessages
from app.models.exercise import ExerciseType
# Import du service de badges
from app.services.badge_service import BadgeService
from app.services.enhanced_server_adapter import EnhancedServerAdapter
from app.utils.error_handler import ErrorHandler
from server.auth import get_current_user
from server.exercise_generator import (ensure_explanation,
                                       generate_ai_exercise,
                                       generate_simple_exercise)


# Fonction pour obtenir une session de base de données
def get_session():
    """Récupère une session de base de données via l'adaptateur"""
    return EnhancedServerAdapter.get_db_session()

async def generate_exercise(request):
    """Génère un nouvel exercice en utilisant le groupe d'âge."""
    params = request.query_params
    exercise_type_raw = params.get('type') or params.get('exercise_type')
    age_group_raw = params.get('age_group') # Changed from difficulty
    use_ai = params.get('ai', False)
    
    # Normaliser et valider les paramètres
    from server.exercise_generator import \
        normalize_and_validate_exercise_params
    
    exercise_type, age_group, derived_difficulty = normalize_and_validate_exercise_params(exercise_type_raw, age_group_raw)
    
    ai_generated = False
    if use_ai and str(use_ai).lower() in ['true', '1', 'yes', 'y']:
        exercise_dict = generate_ai_exercise(exercise_type, age_group)
        ai_generated = True
    else:
        exercise_dict = generate_simple_exercise(exercise_type, age_group)
        
    exercise_dict = ensure_explanation(exercise_dict)
    logger.debug(f"Explication générée: {exercise_dict['explanation']}")
    try:
        # Extraire la locale
        from app.utils.translation import parse_accept_language
        accept_language = request.headers.get("Accept-Language")
        locale = parse_accept_language(accept_language) or "fr"
        
        db = EnhancedServerAdapter.get_db_session()
        try:
            # Sauvegarder l'exercice avec age_group et la difficulté dérivée
            created_exercise = EnhancedServerAdapter.create_generated_exercise(
                db=db,
                exercise_type=exercise_dict['exercise_type'],
                age_group=exercise_dict['age_group'], # Save age_group
                difficulty=exercise_dict['difficulty'], # Save derived difficulty
                title=exercise_dict['title'],
                question=exercise_dict['question'],
                correct_answer=exercise_dict['correct_answer'],
                choices=exercise_dict['choices'],
                explanation=exercise_dict['explanation'],
                hint=exercise_dict.get('hint'),
                tags=exercise_dict.get('tags', 'generated'),
                ai_generated=ai_generated,
                locale=locale
            )
            if created_exercise:
                exercise_id = created_exercise['id']
                logger.info(f"Nouvel exercice créé avec ID={exercise_id}")
                logger.debug(f"Explication: {exercise_dict['explanation']}")
            else:
                logger.error("Erreur: L'exercice n'a pas été créé")
                templates = request.app.state.templates
                return templates.TemplateResponse("error.html", {
                    "request": request,
                    "error": "Erreur de génération",
                    "message": "Impossible de créer l'exercice dans la base de données."
                }, status_code=500)
        finally:
            EnhancedServerAdapter.close_db_session(db)
        return RedirectResponse(url="/exercises?generated=true", status_code=303)
    except Exception as exercise_generation_error:
        logger.error(f"Erreur lors de la génération d'exercice: {exercise_generation_error}")
        logger.debug(traceback.format_exc())
        templates = request.app.state.templates
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": "Erreur de génération",
            "message": f"Impossible de générer l'exercice: {str(exercise_generation_error)}"
        }, status_code=500)

async def get_exercise(request):
    """Récupère un exercice par son ID avec support des traductions"""
    exercise_id = request.path_params.get('exercise_id')

    try:
        # Extraire la locale depuis le header Accept-Language
        from app.utils.translation import parse_accept_language
        accept_language = request.headers.get("Accept-Language")
        locale = parse_accept_language(accept_language) or "fr"
        
        # Utiliser le service ORM ExerciseService
        db = EnhancedServerAdapter.get_db_session()
        try:
            import json as json_module

            from app.models.exercise import Exercise
            
            def safe_parse_json(value, default=None):
                """Parse JSON en gérant les cas None, string vide, ou JSON invalide"""
                if not value:
                    return default if default is not None else []
                if isinstance(value, str):
                    try:
                        return json_module.loads(value)
                    except (json_module.JSONDecodeError, ValueError):
                        return default if default is not None else []
                return value
            
            from sqlalchemy import String, cast

            # IMPORTANT: Charger les enums en tant que strings pour éviter les erreurs de conversion
            # SQLAlchemy essaie de convertir automatiquement et échoue si la DB contient des minuscules
            # Solution: Utiliser cast() pour forcer le chargement en string dès le début
            exercise_row = db.query(
                Exercise.id,
                Exercise.title,
                Exercise.question,
                Exercise.correct_answer,
                Exercise.choices,
                Exercise.explanation,
                Exercise.hint,
                Exercise.tags,
                Exercise.ai_generated,
                Exercise.age_group,
                cast(Exercise.exercise_type, String).label('exercise_type_str'),
                cast(Exercise.difficulty, String).label('difficulty_str')
            ).filter(Exercise.id == exercise_id).first()
            
            if not exercise_row:
                return ErrorHandler.create_not_found_error(f"Exercice {exercise_id} non trouvé")
            
            exercise = {
                "id": exercise_row.id,
                "title": exercise_row.title,
                "exercise_type": exercise_row.exercise_type_str.upper() if exercise_row.exercise_type_str else "ADDITION",
                "difficulty": exercise_row.difficulty_str.upper() if exercise_row.difficulty_str else "PADAWAN",
                "age_group": exercise_row.age_group,
                "question": exercise_row.question,
                # correct_answer volontairement omis pour éviter la triche (renvoyé uniquement après soumission)
                "choices": safe_parse_json(exercise_row.choices, []),
                "explanation": exercise_row.explanation,
                "hint": exercise_row.hint,
                "tags": safe_parse_json(exercise_row.tags, []),
                "ai_generated": exercise_row.ai_generated or False
            }
        finally:
            EnhancedServerAdapter.close_db_session(db)
        
        if not exercise:
            return JSONResponse({"error": SystemMessages.ERROR_EXERCISE_NOT_FOUND}, status_code=404)
                
        return JSONResponse(exercise)
    
    except Exception as exercise_retrieval_error:
        logger.error(f"Erreur lors de la récupération de l'exercice: {exercise_retrieval_error}")
        logger.debug(traceback.format_exc())
        return ErrorHandler.create_error_response(exercise_retrieval_error, status_code=500, user_message="Erreur lors de la récupération de l'exercice")

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
        exercise_id = int(request.path_params.get('exercise_id')) # Get from path_params
        selected_answer = data.get('answer') or data.get('selected_answer')  # Support both formats
        time_spent = data.get('time_spent', 0)
        user_id = current_user.get('id', 1)  # Utiliser l'ID de l'utilisateur authentifié

        # Valider les paramètres requis
        # exercise_id est maintenant garanti par le path_params, donc pas besoin de vérifier s'il est None
        
        if selected_answer is None:
            return JSONResponse(
                {"error": "La réponse est requise."},
                status_code=400
            )

        logger.debug(f"Traitement de la réponse: exercise_id={exercise_id}, selected_answer={selected_answer}")

        # Extraire la locale depuis le header Accept-Language
        from app.utils.translation import parse_accept_language
        accept_language = request.headers.get("Accept-Language")
        locale = parse_accept_language(accept_language) or "fr"
        
        # Utiliser le service ORM ExerciseService
        db_exercise = EnhancedServerAdapter.get_db_session()
        try:
            from sqlalchemy import String, cast

            from app.models.exercise import (DifficultyLevel, Exercise,
                                             ExerciseType)

            # IMPORTANT: Charger les enums en tant que strings pour éviter les erreurs de conversion
            exercise_row = db_exercise.query(
                Exercise.id,
                Exercise.question,
                Exercise.correct_answer,
                Exercise.choices,
                Exercise.explanation,
                cast(Exercise.exercise_type, String).label('exercise_type_str'),
                cast(Exercise.difficulty, String).label('difficulty_str')
            ).filter(Exercise.id == exercise_id).first()
            
            if not exercise_row:
                return JSONResponse({"error": SystemMessages.ERROR_EXERCISE_NOT_FOUND}, status_code=404)
            
            # Normaliser les valeurs enum en majuscules
            exercise_type_normalized = exercise_row.exercise_type_str.upper() if exercise_row.exercise_type_str else "ADDITION"
            difficulty_normalized = exercise_row.difficulty_str.upper() if exercise_row.difficulty_str else "PADAWAN"
            
            exercise = {
                "id": exercise_row.id,
                "exercise_type": exercise_type_normalized,
                "difficulty": difficulty_normalized,
                "correct_answer": exercise_row.correct_answer,
                "choices": exercise_row.choices,
                "question": exercise_row.question,
                "explanation": exercise_row.explanation
            }
        finally:
            EnhancedServerAdapter.close_db_session(db_exercise)

        # Déterminer si la réponse est correcte
        is_correct = False
        
        # Vérifier que correct_answer existe
        correct_answer = exercise.get('correct_answer')
        if not correct_answer:
            logger.error(f"ERREUR: L'exercice {exercise_id} n'a pas de correct_answer")
            return ErrorHandler.create_error_response(
                ValueError("L'exercice n'a pas de réponse correcte définie"),
                status_code=500,
                user_message="L'exercice n'a pas de réponse correcte définie."
            )
        
        # Types d'exercices qui devraient avoir une comparaison insensible à la casse
        text_based_types = [ExerciseType.TEXTE.value, ExerciseType.MIXTE.value]
        exercise_type = exercise.get('exercise_type', '')
        
        # Pour les types de questions textuelles, la comparaison est insensible à la casse
        if exercise_type in text_based_types:
            is_correct = str(selected_answer).lower().strip() == str(correct_answer).lower().strip()
        else:
            # Pour les questions numériques et autres, comparaison stricte
            is_correct = str(selected_answer).strip() == str(correct_answer).strip()
            
        logger.debug(f"Réponse correcte? {is_correct} (selected: '{selected_answer}', correct: '{correct_answer}')")

        # Enregistrer la tentative avec PostgreSQL direct
        db_attempt = EnhancedServerAdapter.get_db_session()
        try:
            # Préparer les données de la tentative
            attempt_data = {
                "user_id": user_id,
                "exercise_id": exercise_id,
                "user_answer": selected_answer,
                "is_correct": is_correct,
                "time_spent": time_spent
            }
            
            logger.debug(f"Tentative d'enregistrement avec attempt_data: {attempt_data}")
            # Utiliser le service ORM ExerciseService.record_attempt
            from app.services.exercise_service import ExerciseService
            attempt_obj = ExerciseService.record_attempt(db_attempt, attempt_data)
            logger.debug(f"Résultat de record_attempt: {attempt_obj}")
            
            # Convertir l'objet Attempt en dictionnaire pour la réponse
            if attempt_obj:
                attempt = {
                    "id": attempt_obj.id,
                    "user_id": attempt_obj.user_id,
                    "exercise_id": attempt_obj.exercise_id,
                    "user_answer": attempt_obj.user_answer,
                    "is_correct": attempt_obj.is_correct,
                    "time_spent": attempt_obj.time_spent,
                    "created_at": attempt_obj.created_at.isoformat() if attempt_obj.created_at else None
                }
            else:
                attempt = None
            
            if not attempt:
                logger.error("ERREUR: La tentative n'a pas été enregistrée correctement")
                return JSONResponse({
                    "is_correct": is_correct,
                    "correct_answer": correct_answer,
                    "explanation": exercise.get('explanation', ""),
                    "error": "Erreur lors de l'enregistrement de la tentative"
                }, status_code=500)
                
            logger.info("Tentative enregistrée avec succès")

            # 🎖️ NOUVEAU: Vérifier et attribuer les badges
            new_badges = []
            db_badges = None
            try:
                # Obtenir une session SQLAlchemy uniquement pour BadgeService (si nécessaire)
                db_badges = EnhancedServerAdapter.get_db_session()
                badge_service = BadgeService(db_badges)
                
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
                    logger.info(f"🎖️ {len(new_badges)} nouveaux badges attribués à l'utilisateur {user_id}")
                    for badge in new_badges:
                        logger.debug(f"   - {badge['name']} ({badge['star_wars_title']})")
                
            except Exception as badge_error:
                logger.warning(f"⚠️ Erreur lors de la vérification des badges: {badge_error}")
                logger.debug(traceback.format_exc())
                # Ne pas faire échouer la soumission si les badges échouent
            finally:
                if db_badges:
                    EnhancedServerAdapter.close_db_session(db_badges)

            # Retourner le résultat avec l'ID de tentative et les nouveaux badges
            from app.utils.json_utils import make_json_serializable
            
            response_data = {
                "is_correct": is_correct,
                "correct_answer": correct_answer,
                "explanation": exercise.get('explanation', ""),
                "attempt_id": attempt.get('id') if attempt else None
            }
            
            # Ajouter les nouveaux badges à la réponse (nettoyer pour sérialisation JSON)
            if new_badges:
                response_data["new_badges"] = make_json_serializable(new_badges)
                response_data["badges_earned"] = len(new_badges)
            
            # Nettoyer toutes les données avant sérialisation JSON (gère les MagicMock dans les tests)
            response_data = make_json_serializable(response_data)
            
            return JSONResponse(response_data)
            
        except Exception as db_error:
            # Gérer les erreurs spécifiques à la base de données
            error_msg = str(db_error)
            error_type = type(db_error).__name__
            logger.error(f"❌ ERREUR DB lors de l'enregistrement: {error_type}: {error_msg}")
            logger.debug(traceback.format_exc())
            
            # Retourner quand même le résultat de validation même si l'enregistrement échoue
            return JSONResponse({
                "is_correct": is_correct,
                "correct_answer": correct_answer,
                "explanation": exercise.get('explanation', ""),
                "error": "Erreur lors de l'enregistrement de la tentative",
                "error_type": error_type,
                "error_message": error_msg
            }, status_code=500)
        finally:
            EnhancedServerAdapter.close_db_session(db_attempt)

    except Exception as response_processing_error:
        logger.error(f"❌ ERREUR lors du traitement de la réponse: {type(response_processing_error).__name__}: {str(response_processing_error)}")
        logger.debug(traceback.format_exc())
        
        # Retourner une réponse d'erreur standardisée
        return ErrorHandler.create_error_response(
            response_processing_error,
            status_code=500,
            user_message="Erreur lors du traitement de la réponse"
        )

async def get_exercises_list(request):
    """Retourne la liste des exercices récents avec support des traductions et pagination standardisée"""
    try:
        logger.debug("[STEP 1] Début de get_exercises_list")
        
        # Récupérer les paramètres de requête
        limit_param = request.query_params.get('limit')
        limit = int(limit_param) if limit_param else 20
        skip = int(request.query_params.get('skip', 0))
        exercise_type_raw = request.query_params.get('exercise_type', None)
        age_group_raw = request.query_params.get('age_group', None) # Changed from difficulty
        search = request.query_params.get('search') or request.query_params.get('q')  # Support 'search' et 'q'
        
        logger.debug(f"[STEP 2] Params: limit={limit}, skip={skip}, type={exercise_type_raw}, age_group={age_group_raw}")
        
        # Normaliser les paramètres de filtrage
        from server.exercise_generator import \
            normalize_and_validate_exercise_params
        exercise_type, age_group, _ = normalize_and_validate_exercise_params(exercise_type_raw, age_group_raw)
        
        logger.debug(f"[STEP 3] Après normalisation: type={exercise_type}, age_group={age_group}")
        
        # Si aucun paramètre n'était fourni, remettre à None pour ne pas filtrer
        if not exercise_type_raw:
            exercise_type = None
        if not age_group_raw:
            age_group = None
        
        # Calculer la page à partir de skip et limit
        page = (skip // limit) + 1 if limit > 0 else 1
        
        # Extraire la locale depuis le header Accept-Language
        from app.utils.translation import parse_accept_language
        accept_language = request.headers.get("Accept-Language")
        locale = parse_accept_language(accept_language) or "fr"
        
        logger.debug(f"[STEP 4] API - Paramètres finaux: limit={limit}, skip={skip}, page={page}, exercise_type={exercise_type}, age_group={age_group}, search={search}, locale={locale}")
        
        # Utiliser le service ORM ExerciseService (100% ORM comme recommandé par l'audit)
        db = EnhancedServerAdapter.get_db_session()
        logger.debug("[STEP 5] Session DB obtenue")
        try:
            logger.debug("[STEP 6] Début du bloc try DB")
            from sqlalchemy import String, cast, or_, text

            from app.models.exercise import (DifficultyLevel, Exercise,
                                             ExerciseType)

            logger.debug("[STEP 7] Imports effectués")
            
            # Construire la requête ORM
            query = db.query(Exercise).filter(Exercise.is_archived == False)
            logger.debug("[STEP 8] Query de base créée")
            
            # Filtrer par type si spécifié (utiliser l'enum normalisé)
            if exercise_type:
                query = query.filter(Exercise.exercise_type == exercise_type)
            
            # Filtrer par groupe d'âge si spécifié
            if age_group:
                query = query.filter(Exercise.age_group == age_group)
            
            # Recherche textuelle si spécifié
            if search:
                search_pattern = f"%{search}%"
                query = query.filter(
                    or_(
                        Exercise.title.ilike(search_pattern),
                        Exercise.question.ilike(search_pattern)
                    )
                )
            
            logger.debug("[STEP 9] Filtres appliqués")
            
            # Compter le total
            total = query.count()
            logger.debug(f"[STEP 10] Total compté: {total}")
            
            # Récupérer les exercices avec pagination
            exercises_objs_raw = db.query(
                Exercise.id,
                Exercise.title,
                Exercise.question,
                Exercise.correct_answer,
                Exercise.choices,
                Exercise.explanation,
                Exercise.hint,
                Exercise.tags,
                Exercise.ai_generated,
                Exercise.is_active,
                Exercise.view_count,
                Exercise.created_at,
                cast(Exercise.exercise_type, String).label('exercise_type_str'),
                cast(Exercise.difficulty, String).label('difficulty_str'),
                Exercise.age_group # Récupérer aussi le groupe d'âge
            ).filter(Exercise.is_archived == False)
            
            # Appliquer les mêmes filtres que la requête principale
            if exercise_type:
                exercises_objs_raw = exercises_objs_raw.filter(Exercise.exercise_type == exercise_type)
            if age_group:
                exercises_objs_raw = exercises_objs_raw.filter(Exercise.age_group == age_group)
            if search:
                search_pattern = f"%{search}%"
                exercises_objs_raw = exercises_objs_raw.filter(
                    or_(
                        Exercise.title.ilike(search_pattern),
                        Exercise.question.ilike(search_pattern)
                    )
                )
            
            exercises_objs_raw = exercises_objs_raw.order_by(Exercise.created_at.desc()).limit(limit).offset(skip).all()
            logger.debug(f"[STEP 11] Exercices récupérés: {len(exercises_objs_raw)} éléments")
            
            import json as json_module
            def safe_parse_json(value, default=None):
                if not value: return default if default is not None else []
                if isinstance(value, str):
                    try: return json_module.loads(value)
                    except (json_module.JSONDecodeError, ValueError): return default if default is not None else []
                return value

            logger.debug("[STEP 12] Début de la construction de la liste d'exercices")
            exercises = []
            for idx, row in enumerate(exercises_objs_raw):
                try:
                    logger.debug(f"[STEP 12.{idx}] Processing row id={row.id}, type={type(row.exercise_type_str)}, diff={type(row.difficulty_str)}")
                    exercise_dict = {
                        "id": row.id,
                        "title": row.title,
                        "exercise_type": row.exercise_type_str.upper() if row.exercise_type_str else "ADDITION",
                        "difficulty": row.difficulty_str.upper() if row.difficulty_str else "PADAWAN",
                        "age_group": row.age_group,
                        "question": row.question,
                        "correct_answer": row.correct_answer,
                        "choices": safe_parse_json(row.choices, []),
                        "explanation": row.explanation,
                        "hint": row.hint,
                        "tags": safe_parse_json(row.tags, []),
                        "ai_generated": row.ai_generated,
                        "is_active": row.is_active,
                        "view_count": row.view_count
                    }
                    exercises.append(exercise_dict)
                except Exception as row_error:
                    logger.error(f"[STEP 12.{idx}] ERROR processing row: {row_error}")
                    raise
            logger.debug(f"[STEP 13] Liste d'exercices construite: {len(exercises)} éléments")
        finally:
            EnhancedServerAdapter.close_db_session(db)

        has_more = (skip + len(exercises)) < total
        
        response_data = {
            "items": exercises,
            "total": total,
            "page": page,
            "limit": limit,
            "hasMore": has_more
        }
        
        return JSONResponse(response_data)

    except Exception as exercises_list_error:
        logger.error(f"Erreur lors de la récupération des exercices: {exercises_list_error}")
        logger.debug(traceback.format_exc())
        return ErrorHandler.create_error_response(exercises_list_error, status_code=500, user_message="Erreur lors de la récupération des exercices")

async def generate_exercise_api(request):
    """Génère un nouvel exercice via API JSON (POST) en utilisant le groupe d'âge."""
    try:
        # Récupérer les données JSON de la requête
        data = await request.json()
        exercise_type_raw = data.get('exercise_type')
        age_group_raw = data.get('age_group') # Changed from difficulty
        use_ai = data.get('ai', False)
        
        # Normaliser et valider les paramètres
        from server.exercise_generator import \
            normalize_and_validate_exercise_params
        
        exercise_type, age_group, derived_difficulty = normalize_and_validate_exercise_params(exercise_type_raw, age_group_raw)
        
        logger.debug(f"Génération API: type={exercise_type_raw}→{exercise_type}, groupe d'âge={age_group_raw}→{age_group}, IA={use_ai}")
        
        # Valider les paramètres
        if not exercise_type_raw or not age_group_raw:
            return JSONResponse({
                "error": "Les paramètres 'exercise_type' et 'age_group' sont requis"
            }, status_code=400)
        
        # Générer l'exercice
        ai_generated = False
        if use_ai and str(use_ai).lower() in ['true', '1', 'yes', 'y']:
            exercise_dict = generate_ai_exercise(exercise_type, age_group)
            ai_generated = True
        else:
            exercise_dict = generate_simple_exercise(exercise_type, age_group)
        
        exercise_dict = ensure_explanation(exercise_dict)
        
        # Optionnellement sauvegarder en base de données
        save_to_db = data.get('save', True)
        if save_to_db:
            try:
                # Extraire la locale
                from app.utils.translation import parse_accept_language
                accept_language = request.headers.get("Accept-Language")
                locale = parse_accept_language(accept_language) or "fr"
                
                db = EnhancedServerAdapter.get_db_session()
                try:
                    # Sauvegarder l'exercice avec age_group et la difficulté dérivée
                    created_exercise = EnhancedServerAdapter.create_generated_exercise(
                        db=db,
                        exercise_type=exercise_dict['exercise_type'],
                        age_group=exercise_dict['age_group'], # Save age_group
                        difficulty=exercise_dict['difficulty'], # Save derived difficulty
                        title=exercise_dict['title'],
                        question=exercise_dict['question'],
                        correct_answer=exercise_dict['correct_answer'],
                        choices=exercise_dict['choices'],
                        explanation=exercise_dict['explanation'],
                        hint=exercise_dict.get('hint'),
                        tags=exercise_dict.get('tags', 'generated'),
                        ai_generated=ai_generated,
                        locale=locale
                    )
                    if created_exercise:
                        exercise_dict['id'] = created_exercise['id']
                        logger.info(f"Exercice sauvegardé avec ID={created_exercise['id']}")
                finally:
                    EnhancedServerAdapter.close_db_session(db)
            except Exception as save_error:
                logger.warning(f"Erreur lors de la sauvegarde: {save_error}")
                # Continuer même si la sauvegarde échoue
        
        # Retourner l'exercice généré
        return JSONResponse(exercise_dict)
        
    except Exception as api_generation_error:
        logger.error(f"Erreur lors de la génération d'exercice API: {api_generation_error}")
        logger.debug(traceback.format_exc())
        return ErrorHandler.create_error_response(api_generation_error, status_code=500, user_message="Erreur lors de la génération de l'exercice")

async def generate_ai_exercise_stream(request):
    """
    Génère un exercice avec OpenAI en streaming SSE.
    Permet un affichage progressif de la génération pour une meilleure UX.
    """
    try:
        # Vérifier l'authentification
        current_user = await get_current_user(request)
        if not current_user or not current_user.get("is_authenticated"):
            async def auth_error_generator():
                yield f"data: {json.dumps({'type': 'error', 'message': 'Non authentifié'})}\n\n"
            return StreamingResponse(
                auth_error_generator(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                }
            )

        # Récupérer les paramètres de la requête
        exercise_type_raw = request.query_params.get('exercise_type', 'addition')
        # Support des deux paramètres : age_group (nouveau) et difficulty (legacy)
        age_group_raw = request.query_params.get('age_group') or request.query_params.get('difficulty', '6-8')
        prompt_raw = request.query_params.get('prompt', '')

        # Sanitizer le prompt utilisateur pour éviter l'injection
        from app.utils.prompt_sanitizer import (sanitize_user_prompt,
                                                validate_prompt_safety)
        is_safe, safety_reason = validate_prompt_safety(prompt_raw)
        if not is_safe:
            logger.warning(f"Prompt utilisateur rejeté pour sécurité: {safety_reason}")
            async def safety_error_generator():
                yield f"data: {json.dumps({'type': 'error', 'message': f'Prompt invalide: {safety_reason}'})}\n\n"
            return StreamingResponse(
                safety_error_generator(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                }
            )
        prompt = sanitize_user_prompt(prompt_raw)
        
        # Normaliser et valider les paramètres de manière centralisée
        from server.exercise_generator import \
            normalize_and_validate_exercise_params
        
        exercise_type, age_group, derived_difficulty = normalize_and_validate_exercise_params(exercise_type_raw, age_group_raw)
        
        # Vérifier que la clé OpenAI est configurée
        if not settings.OPENAI_API_KEY:
            async def error_generator():
                yield f"data: {json.dumps({'type': 'error', 'message': 'OpenAI API key non configurée'})}\n\n"
            
            return StreamingResponse(
                error_generator(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                }
            )
        
        async def generate():
            try:
                # Importer OpenAI de manière conditionnelle
                try:
                    from openai import AsyncOpenAI
                except ImportError:
                    yield f"data: {json.dumps({'type': 'error', 'message': 'Bibliothèque OpenAI non installée'})}\n\n"
                    return
                
                client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
                
                # Définir les plages de nombres selon la difficulté
                difficulty_ranges = {
                    "INITIE": {"min": 1, "max": 20, "desc": "nombres simples de 1 à 20"},
                    "PADAWAN": {"min": 1, "max": 100, "desc": "nombres jusqu'à 100"},
                    "CHEVALIER": {"min": 10, "max": 500, "desc": "nombres jusqu'à 500, calculs intermédiaires"},
                    "MAITRE": {"min": 50, "max": 1000, "desc": "nombres jusqu'à 1000, problèmes complexes"},
                    "GRAND_MAITRE": {"min": 100, "max": 10000, "desc": "grands nombres, problèmes avancés"}
                }
                diff_info = difficulty_ranges.get(derived_difficulty, difficulty_ranges["PADAWAN"])
                
                # Déterminer le contexte thématique
                has_custom_theme = prompt and any(word in prompt.lower() for word in ['thème', 'theme', 'contexte', 'histoire', 'univers', 'monde'])
                default_theme = "spatial/galactique (vaisseaux, planètes, étoiles - sans références Star Wars)" if not has_custom_theme else ""
                
                # Construire le prompt système optimisé
                system_prompt = f"""Tu es un créateur d'exercices mathématiques pédagogiques.

## CONTRAINTES OBLIGATOIRES
- Type d'exercice : **{exercise_type}** (STRICTEMENT ce type, aucun autre)
- Niveau : {derived_difficulty} ({diff_info['desc']})
- Groupe d'âge cible : {age_group}
{f"- Contexte par défaut : {default_theme}" if default_theme else ""}

## GUIDE PAR TYPE
- addition/soustraction/multiplication/division : opération unique du type demandé
- fractions : opérations avec fractions (addition, simplification, comparaison)
- geometrie : périmètres, aires, volumes avec formules adaptées au niveau
- texte : problème concret avec mise en situation, nécessitant raisonnement
- mixte : combiner 2-3 opérations différentes dans un même calcul
- divers : suites logiques, pourcentages, conversions, probabilités simples

## RÈGLES QUALITÉ
1. La question doit être claire et sans ambiguïté
2. Les 4 choix doivent inclure : la bonne réponse + 3 erreurs plausibles (erreurs de calcul typiques)
3. L'explication doit détailler le raisonnement étape par étape
4. L'indice doit GUIDER sans donner la réponse (ex: "Quelle opération pour trouver le total ?")

## FORMAT JSON STRICT
{{
  "title": "Titre court et engageant",
  "question": "Énoncé complet du problème",
  "correct_answer": "Réponse numérique uniquement",
  "choices": ["choix1", "choix2", "choix3", "choix4"],
  "explanation": "Explication pédagogique détaillée",
  "hint": "Piste sans révéler la solution"
}}"""
                
                # Construire le prompt utilisateur - PRIORITÉ à la description personnalisée
                if prompt and prompt.strip():
                    # Si l'utilisateur a une description, elle est PRIORITAIRE
                    user_prompt = f"""INSTRUCTIONS PERSONNALISÉES DE L'UTILISATEUR (PRIORITAIRES) :
"{prompt.strip()}"

Crée un exercice de type {exercise_type} (niveau {derived_difficulty}) en respectant ces instructions personnalisées."""
                else:
                    # Pas de description personnalisée, utiliser le contexte par défaut
                    user_prompt = f"Crée un exercice de type {exercise_type} pour le niveau {derived_difficulty} avec un contexte spatial engageant."
                
                # Envoyer un message de démarrage (sans afficher le JSON brut)
                yield f"data: {json.dumps({'type': 'status', 'message': 'Génération en cours...'})}\n\n"
                
                # Créer le stream OpenAI
                stream = await client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    stream=True,
                    temperature=0.7,
                    response_format={"type": "json_object"}  # Forcer JSON
                )
                
                full_response = ""
                # Ne pas envoyer les chunks JSON au client (pas utile pour l'utilisateur)
                # On accumule juste la réponse complète en arrière-plan
                async for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        full_response += content
                        # Ne plus envoyer les chunks JSON au client (masqué pour meilleure UX)
                
                # Parser la réponse JSON complète
                try:
                    exercise_data = json.loads(full_response)
                    
                    # Normaliser les données pour correspondre au format attendu
                    # Utiliser les valeurs normalisées (déjà normalisées plus haut)
                    normalized_exercise = {
                        "exercise_type": exercise_type,  # Déjà normalisé
                        "age_group": age_group,  # Groupe d'âge normalisé
                        "difficulty": derived_difficulty,  # Difficulté dérivée du groupe d'âge
                        "title": exercise_data.get("title", f"Exercice {exercise_type} {age_group}"),
                        "question": exercise_data.get("question", ""),
                        "correct_answer": str(exercise_data.get("correct_answer", "")),
                        "choices": exercise_data.get("choices", []),
                        "explanation": exercise_data.get("explanation", ""),
                        "hint": exercise_data.get("hint", ""),
                        "ai_generated": True,
                        "tags": "ai,generated"
                    }
                    
                    # Optionnellement sauvegarder en base de données
                    try:
                        # Extraire la locale depuis le header Accept-Language
                        from app.utils.translation import parse_accept_language
                        accept_language = request.headers.get("Accept-Language")
                        locale = parse_accept_language(accept_language) or "fr"
                        
                        db = EnhancedServerAdapter.get_db_session()
                        try:
                            created_exercise = EnhancedServerAdapter.create_generated_exercise(
                                db=db,
                                exercise_type=normalized_exercise['exercise_type'],
                                age_group=normalized_exercise['age_group'],
                                difficulty=normalized_exercise['difficulty'],
                                title=normalized_exercise['title'],
                                question=normalized_exercise['question'],
                                correct_answer=normalized_exercise['correct_answer'],
                                choices=normalized_exercise['choices'],
                                explanation=normalized_exercise['explanation'],
                                hint=normalized_exercise.get('hint'),
                                tags=normalized_exercise.get('tags', 'ai,generated'),
                                ai_generated=True,
                                locale=locale
                            )
                            if created_exercise:
                                normalized_exercise['id'] = created_exercise['id']
                        finally:
                            EnhancedServerAdapter.close_db_session(db)
                    except Exception as save_error:
                        logger.warning(f"Erreur lors de la sauvegarde: {save_error}")
                        # Continuer même si la sauvegarde échoue
                    
                    # Envoyer l'exercice complet
                    yield f"data: {json.dumps({'type': 'exercise', 'exercise': normalized_exercise})}\n\n"
                    
                except json.JSONDecodeError as json_error:
                    yield f"data: {json.dumps({'type': 'error', 'message': f'Erreur de parsing JSON: {str(json_error)}'})}\n\n"
                    
            except Exception as ai_generation_error:
                logger.error(f"Erreur lors de la génération IA: {ai_generation_error}")
                logger.debug(traceback.format_exc())
                yield f"data: {json.dumps({'type': 'error', 'message': str(ai_generation_error)})}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # Désactiver le buffering pour nginx
            }
        )
        
    except Exception as stream_error:
        logger.error(f"Erreur dans generate_ai_exercise_stream: {stream_error}")
        logger.debug(traceback.format_exc())
        async def error_generator():
            yield f"data: {json.dumps({'type': 'error', 'message': str(stream_error)})}\n\n"
        
        return StreamingResponse(
            error_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )


async def get_completed_exercises_ids(request: Request):
    """
    Récupère la liste des IDs d'exercices complétés par l'utilisateur actuel.
    Route: GET /api/exercises/completed-ids
    """
    try:
        # Vérifier l'authentification
        current_user = await get_current_user(request)
        if not current_user or not current_user.get("is_authenticated"):
            return JSONResponse({"completed_ids": []}, status_code=200)
        
        user_id = current_user.get("id")
        if not user_id:
            return JSONResponse({"completed_ids": []}, status_code=200)
        
        # Récupérer les IDs d'exercices avec au moins une tentative correcte
        from server.database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            query = """
                SELECT DISTINCT exercise_id 
                FROM attempts 
                WHERE user_id = %s AND is_correct = true
            """
            cursor.execute(query, (user_id,))
            rows = cursor.fetchall()
            completed_ids = [row[0] for row in rows] if rows else []
            
            logger.debug(f"Récupération de {len(completed_ids)} exercices complétés pour l'utilisateur {user_id}")
            return JSONResponse({"completed_ids": completed_ids})
        finally:
            cursor.close()
            conn.close()
            
    except Exception as completed_retrieval_error:
        logger.error(f"Erreur lors de la récupération des exercices complétés: {completed_retrieval_error}")
        logger.debug(traceback.format_exc())
        return ErrorHandler.create_error_response(
            error=completed_retrieval_error,
            status_code=500,
            user_message="Erreur lors de la récupération des exercices complétés."
        )


async def delete_exercise(request: Request):
    """
    Handler pour supprimer un exercice (placeholder).
    Route: DELETE /api/exercises/{exercise_id}
    """
    try:
        current_user = await get_current_user(request)
        if not current_user or not current_user.get("is_authenticated"):
            return JSONResponse({"error": "Non authentifié"}, status_code=401)
        
        exercise_id = int(request.path_params.get('exercise_id'))
        user_id = current_user.get('id')
        logger.info(f"Tentative de suppression de l'exercice {exercise_id} par l'utilisateur {user_id}. Fonctionnalité en développement.")

        return JSONResponse(
            {"message": f"La suppression de l'exercice {exercise_id} est en cours de développement."},
            status_code=200
        )
    except ValueError:
        return JSONResponse({"error": "ID d'exercice invalide"}, status_code=400)
    except Exception as e:
        logger.error(f"Erreur lors de la suppression de l'exercice: {e}")
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)
 