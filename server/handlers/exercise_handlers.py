"""
Handlers pour la génération d'exercices (API)
"""
import traceback
import json
from starlette.responses import JSONResponse, RedirectResponse, StreamingResponse
from starlette.requests import Request
from app.services.enhanced_server_adapter import EnhancedServerAdapter
from server.exercise_generator import generate_ai_exercise, generate_simple_exercise, ensure_explanation
from app.core.messages import SystemMessages
from app.models.exercise import ExerciseType
from app.core.config import settings
from app.utils.error_handler import ErrorHandler
from loguru import logger

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
        from fastapi import HTTPException
        
        # Décoder le token pour obtenir le nom d'utilisateur
        try:
            payload = decode_token(access_token)
        except HTTPException:
            # Token invalide ou expiré, retourner None silencieusement
            return None
        except Exception as decode_error:
            # Autre erreur de décodage
            logger.debug(f"Erreur lors du décodage du token: {decode_error}")
            return None
        
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
            
    except Exception as auth_error:
        error_msg = str(auth_error)
        error_type = type(auth_error).__name__
        # Ne pas logger les erreurs de token invalide comme des erreurs critiques
        if "Signature verification failed" in error_msg or "Token" in error_type:
            logger.debug(f"Token invalide ou expiré: {error_msg}")
        else:
            logger.error(f"Erreur lors de la récupération de l'utilisateur: {error_type}: {error_msg}")
            logger.debug(traceback.format_exc())
        
    return None

# Fonction pour obtenir une session de base de données
def get_session():
    """Récupère une session de base de données via l'adaptateur"""
    return EnhancedServerAdapter.get_db_session()

async def generate_exercise(request):
    """Génère un nouvel exercice"""
    params = request.query_params
    exercise_type_raw = params.get('type') or params.get('exercise_type')
    difficulty_raw = params.get('difficulty')
    use_ai = params.get('ai', False)
    
    # Normaliser et valider les paramètres de manière centralisée
    from server.exercise_generator import normalize_and_validate_exercise_params
    
    exercise_type, difficulty = normalize_and_validate_exercise_params(exercise_type_raw, difficulty_raw)
    
    ai_generated = False
    if use_ai and str(use_ai).lower() in ['true', '1', 'yes', 'y']:
        exercise_dict = generate_ai_exercise(exercise_type, difficulty)
        ai_generated = True
    else:
        exercise_dict = generate_simple_exercise(exercise_type, difficulty)
    exercise_dict = ensure_explanation(exercise_dict)
    logger.debug(f"Explication générée: {exercise_dict['explanation']}")
    try:
        # Extraire la locale depuis le header Accept-Language
        from app.utils.translation import parse_accept_language
        accept_language = request.headers.get("Accept-Language")
        locale = parse_accept_language(accept_language) or "fr"
        
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
            "message": f"Impossible de générer l'exercice: {str(e)}"
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
            from app.models.exercise import Exercise
            import json as json_module
            
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
            
            from sqlalchemy import cast, String
            
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
                "question": exercise_row.question,
                "correct_answer": exercise_row.correct_answer,
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

        logger.debug(f"Traitement de la réponse: exercise_id={exercise_id}, selected_answer={selected_answer}")

        # Extraire la locale depuis le header Accept-Language
        from app.utils.translation import parse_accept_language
        accept_language = request.headers.get("Accept-Language")
        locale = parse_accept_language(accept_language) or "fr"
        
        # Utiliser le service ORM ExerciseService
        db_exercise = EnhancedServerAdapter.get_db_session()
        try:
            from app.models.exercise import Exercise, ExerciseType, DifficultyLevel
            from sqlalchemy import cast, String
            
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
        finally:
            EnhancedServerAdapter.close_db_session(db_attempt)
            
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
            try:
                # Obtenir une session SQLAlchemy uniquement pour BadgeService (si nécessaire)
                db = EnhancedServerAdapter.get_db_session()
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
                    logger.info(f"🎖️ {len(new_badges)} nouveaux badges attribués à l'utilisateur {user_id}")
                    for badge in new_badges:
                        logger.debug(f"   - {badge['name']} ({badge['star_wars_title']})")
                
                EnhancedServerAdapter.close_db_session(db)
                
            except Exception as badge_error:
                logger.warning(f"⚠️ Erreur lors de la vérification des badges: {badge_error}")
                logger.debug(traceback.format_exc())
                # Ne pas faire échouer la soumission si les badges échouent
                pass

            # Retourner le résultat avec l'ID de tentative et les nouveaux badges
            response_data = {
                "is_correct": is_correct,
                "correct_answer": correct_answer,
                "explanation": exercise.get('explanation', ""),
                "attempt_id": attempt.get('id') if attempt else None
            }
            
            # Ajouter les nouveaux badges à la réponse
            if new_badges:
                response_data["new_badges"] = new_badges
                response_data["badges_earned"] = len(new_badges)
            
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
        # Récupérer les paramètres de requête
        limit_param = request.query_params.get('limit')
        limit = int(limit_param) if limit_param else 20
        skip = int(request.query_params.get('skip', 0))
        exercise_type_raw = request.query_params.get('exercise_type', None)
        difficulty_raw = request.query_params.get('difficulty', None)
        search = request.query_params.get('search') or request.query_params.get('q')  # Support 'search' et 'q'
        
        # Normaliser les paramètres de filtrage AVANT de les utiliser dans la requête
        from server.exercise_generator import normalize_and_validate_exercise_params
        exercise_type, difficulty = normalize_and_validate_exercise_params(exercise_type_raw, difficulty_raw)
        
        # Si aucun paramètre n'était fourni, remettre à None pour ne pas filtrer
        if not exercise_type_raw:
            exercise_type = None
        if not difficulty_raw:
            difficulty = None
        
        # Calculer la page à partir de skip et limit
        page = (skip // limit) + 1 if limit > 0 else 1
        
        # Extraire la locale depuis le header Accept-Language
        from app.utils.translation import parse_accept_language
        accept_language = request.headers.get("Accept-Language")
        locale = parse_accept_language(accept_language) or "fr"
        
        logger.debug(f"API - Paramètres reçus: limit={limit}, skip={skip}, page={page}, exercise_type_raw={exercise_type_raw}→{exercise_type}, difficulty_raw={difficulty_raw}→{difficulty}, search={search}, locale={locale}")
        
        # Utiliser le service ORM ExerciseService (100% ORM comme recommandé par l'audit)
        db = EnhancedServerAdapter.get_db_session()
        try:
            from app.models.exercise import Exercise, ExerciseType, DifficultyLevel
            from sqlalchemy import or_, text, cast, String
            
            # Construire la requête ORM
            query = db.query(Exercise).filter(Exercise.is_archived == False)
            
            # Filtrer par type si spécifié (utiliser l'enum normalisé)
            if exercise_type:
                # Convertir la string normalisée en enum ExerciseType
                try:
                    exercise_type_enum = ExerciseType(exercise_type)
                    query = query.filter(Exercise.exercise_type == exercise_type_enum)
                except ValueError:
                    logger.warning(f"Type d'exercice invalide après normalisation: {exercise_type}")
            
            # Filtrer par difficulté si spécifiée (utiliser l'enum normalisé)
            if difficulty:
                # Convertir la string normalisée en enum DifficultyLevel
                try:
                    difficulty_enum = DifficultyLevel(difficulty)
                    query = query.filter(Exercise.difficulty == difficulty_enum)
                except ValueError:
                    logger.warning(f"Difficulté invalide après normalisation: {difficulty}")
            
            # Recherche textuelle si spécifié
            if search:
                search_pattern = f"%{search}%"
                query = query.filter(
                    or_(
                        Exercise.title.ilike(search_pattern),
                        Exercise.question.ilike(search_pattern)
                    )
                )
            
            # Compter le total
            total = query.count()
            
            # Récupérer les exercices avec pagination
            # IMPORTANT: Charger les enums en tant que strings pour éviter les erreurs de conversion
            # SQLAlchemy essaie de convertir automatiquement et échoue si la DB contient des minuscules
            # Solution: Utiliser cast() pour forcer le chargement en string dès le début
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
                cast(Exercise.difficulty, String).label('difficulty_str')
            ).filter(Exercise.is_archived == False)
            
            # Appliquer les mêmes filtres que la requête principale
            if exercise_type:
                try:
                    exercise_type_enum = ExerciseType(exercise_type)
                    exercises_objs_raw = exercises_objs_raw.filter(Exercise.exercise_type == exercise_type_enum)
                except ValueError:
                    pass  # Déjà loggé plus haut
            if difficulty:
                try:
                    difficulty_enum = DifficultyLevel(difficulty)
                    exercises_objs_raw = exercises_objs_raw.filter(Exercise.difficulty == difficulty_enum)
                except ValueError:
                    pass  # Déjà loggé plus haut
            if search:
                search_pattern = f"%{search}%"
                exercises_objs_raw = exercises_objs_raw.filter(
                    or_(
                        Exercise.title.ilike(search_pattern),
                        Exercise.question.ilike(search_pattern)
                    )
                )
            
            exercises_objs_raw = exercises_objs_raw.order_by(Exercise.created_at.desc()).limit(limit).offset(skip).all()
            
            # Reconstruire les objets Exercise avec les valeurs normalisées
            exercises_objs = []
            for row in exercises_objs_raw:
                # Créer un objet Exercise minimal avec les valeurs normalisées
                ex = Exercise()
                ex.id = row.id
                ex.title = row.title
                ex.question = row.question
                ex.correct_answer = row.correct_answer
                ex.choices = row.choices
                ex.explanation = row.explanation
                ex.hint = row.hint
                ex.tags = row.tags
                ex.ai_generated = row.ai_generated
                ex.is_active = row.is_active
                ex.view_count = row.view_count
                ex.created_at = row.created_at
                # Stocker les valeurs enum normalisées comme attributs temporaires
                ex._exercise_type_str = row.exercise_type_str.upper() if row.exercise_type_str else "ADDITION"
                ex._difficulty_str = row.difficulty_str.upper() if row.difficulty_str else "PADAWAN"
                exercises_objs.append(ex)
            
            # Convertir en dicts avec parsing JSON sécurisé
            import json as json_module
            
            def safe_parse_json(value, default=None):
                """Parse JSON en gérant les cas None, string vide, ou JSON invalide"""
                if not value:  # None ou string vide
                    return default if default is not None else []
                if isinstance(value, str):
                    try:
                        return json_module.loads(value)
                    except (json_module.JSONDecodeError, ValueError):
                        return default if default is not None else []
                return value  # Déjà un objet Python
            
            def safe_get_enum_value(enum_obj, default="UNKNOWN"):
                """Récupère la valeur d'un enum en gérant les erreurs de conversion"""
                try:
                    if enum_obj is None:
                        return default
                    # Si l'objet a une valeur string temporaire (chargée via requête alternative)
                    if hasattr(enum_obj, '_exercise_type_str'):
                        return enum_obj._exercise_type_str
                    if hasattr(enum_obj, '_difficulty_str'):
                        return enum_obj._difficulty_str
                    # Si c'est déjà un enum Python, retourner sa valeur
                    if hasattr(enum_obj, 'value'):
                        return enum_obj.value
                    # Si c'est une string, la retourner telle quelle (déjà normalisée)
                    if isinstance(enum_obj, str):
                        return enum_obj.upper()  # S'assurer que c'est en majuscule
                    # Sinon, convertir en string et mettre en majuscule
                    return str(enum_obj).upper()
                except (AttributeError, ValueError, LookupError) as e:
                    logger.warning(f"Erreur lors de la récupération de la valeur enum: {e}, valeur brute: {enum_obj}")
                    # En cas d'erreur, essayer de récupérer la valeur brute et la normaliser
                    if isinstance(enum_obj, str):
                        return enum_obj.upper()
                    return default
            
            exercises = [
                {
                    "id": ex.id,
                    "title": ex.title,
                    "exercise_type": safe_get_enum_value(getattr(ex, '_exercise_type_str', None) or getattr(ex, 'exercise_type', None), "ADDITION"),
                    "difficulty": safe_get_enum_value(getattr(ex, '_difficulty_str', None) or getattr(ex, 'difficulty', None), "PADAWAN"),
                    "question": ex.question,
                    "correct_answer": ex.correct_answer,
                    "choices": safe_parse_json(ex.choices, []),
                    "explanation": ex.explanation,
                    "hint": ex.hint,
                    "tags": safe_parse_json(ex.tags, []),
                    "ai_generated": getattr(ex, 'ai_generated', False),
                    "is_active": ex.is_active,
                    "view_count": ex.view_count
                } for ex in exercises_objs
            ]
        finally:
            EnhancedServerAdapter.close_db_session(db)

        # Log pour déboguer
        logger.debug(f"API - Retour de {len(exercises)} exercices sur {total} total (limit demandé: {limit}, page: {page})")
        if len(exercises) > 0:
            logger.debug(f"API - Premier exercice: id={exercises[0].get('id')}, title={exercises[0].get('title')}")
        
        # Retourner le format paginé standardisé
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
    """Génère un nouvel exercice via API JSON (POST)"""
    try:
        # Récupérer les données JSON de la requête
        data = await request.json()
        exercise_type_raw = data.get('exercise_type')
        difficulty_raw = data.get('difficulty')
        use_ai = data.get('ai', False)
        
        # Normaliser et valider les paramètres de manière centralisée
        from server.exercise_generator import normalize_and_validate_exercise_params
        
        exercise_type, difficulty = normalize_and_validate_exercise_params(exercise_type_raw, difficulty_raw)
        
        logger.debug(f"Génération API: type={exercise_type_raw}→{exercise_type}, difficulté={difficulty_raw}→{difficulty}, IA={use_ai}")
        
        # Valider les paramètres
        if not exercise_type_raw or not difficulty_raw:
            return JSONResponse({
                "error": "Les paramètres 'exercise_type' et 'difficulty' sont requis"
            }, status_code=400)
        
        # Générer l'exercice avec les paramètres normalisés
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
                # Extraire la locale depuis le header Accept-Language
                from app.utils.translation import parse_accept_language
                accept_language = request.headers.get("Accept-Language")
                locale = parse_accept_language(accept_language) or "fr"
                
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
        # Récupérer les paramètres de la requête
        exercise_type_raw = request.query_params.get('exercise_type', 'addition')
        difficulty_raw = request.query_params.get('difficulty', 'initie')
        prompt = request.query_params.get('prompt', '')
        
        # Normaliser et valider les paramètres de manière centralisée
        from server.exercise_generator import normalize_and_validate_exercise_params
        
        exercise_type, difficulty = normalize_and_validate_exercise_params(exercise_type_raw, difficulty_raw)
        
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
                
                # Construire le prompt système avec instructions strictes sur le type
                system_prompt = f"""Tu es un assistant pédagogique spécialisé dans la création d'exercices mathématiques pour enfants de 5 à 15 ans.

RÈGLE ABSOLUE : Tu DOIS créer un exercice de type "{exercise_type}" uniquement. Ne crée JAMAIS un exercice d'un autre type.

Types d'exercices possibles :
- "addition" : Exercices d'addition uniquement
- "soustraction" : Exercices de soustraction uniquement
- "multiplication" : Exercices de multiplication uniquement
- "division" : Exercices de division uniquement
- "fractions" : Exercices sur les fractions uniquement
- "geometrie" : Exercices de géométrie (périmètres, aires, volumes) uniquement
- "texte" : Problèmes textuels/logiques uniquement
- "mixte" : Exercices combinant plusieurs opérations
- "divers" : Exercices variés (probabilités, séquences, etc.)

Crée des exercices adaptés au niveau "{difficulty}" avec un contexte spatial/galactique (sans références Star Wars identifiables pour éviter les droits d'auteur).

RÈGLE IMPORTANTE POUR L'INDICE :
L'indice (hint) doit être une PISTE pédagogique qui guide l'élève vers la solution, MAIS NE DOIT JAMAIS donner la réponse directement.
- ✅ BON : "Pense à décomposer le nombre en dizaines et unités"
- ✅ BON : "Quelle opération permet de trouver le total ?"
- ✅ BON : "Regarde bien les nombres dans la question"
- ❌ MAUVAIS : "La réponse est 15"
- ❌ MAUVAIS : "Il faut faire 10 + 5"
- ❌ MAUVAIS : "Additionne 10 et 5 pour obtenir 15"

L'indice doit encourager la réflexion sans révéler la solution.

Retourne uniquement l'exercice au format JSON valide avec ces champs:
{{
  "title": "Titre de l'exercice",
  "question": "Question mathématique avec contexte spatial",
  "correct_answer": "Réponse correcte (nombre)",
  "choices": ["choix1", "choix2", "choix3", "choix4"],
  "explanation": "Explication pédagogique de la solution",
  "hint": "Piste pédagogique qui guide sans donner la réponse"
}}
Assure-toi que les choix incluent la bonne réponse et des erreurs typiques."""
                
                # Construire le prompt utilisateur avec le type normalisé
                user_prompt = f"Crée un exercice de type {exercise_type} niveau {difficulty}. IMPORTANT : L'exercice DOIT être de type {exercise_type}, pas un autre type."
                if prompt:
                    user_prompt += f" {prompt}"
                
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
                        "difficulty": difficulty,  # Déjà normalisé
                        "title": exercise_data.get("title", f"Exercice {exercise_type} {difficulty}"),
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
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        
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
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        
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
            error=e,
            status_code=500,
            user_message="Erreur lors de la récupération des exercices complétés."
        ) 