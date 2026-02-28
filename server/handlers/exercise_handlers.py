"""
Handlers pour la génération d'exercices (API)
"""

import json
import traceback

from app.core.logging_config import get_logger

logger = get_logger(__name__)
from pydantic import ValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse, StreamingResponse

from app.core.ai_config import AIConfig
from app.core.config import settings
from app.exceptions import ExerciseNotFoundError, ExerciseSubmitError
from app.models.exercise import ExerciseType
from app.schemas.exercise import SubmitAnswerRequest

# Import du service de badges
from app.services.enhanced_server_adapter import EnhancedServerAdapter
from app.services.exercise_service import ExerciseService
from app.services.exercise_stats_service import ExerciseStatsService
from app.utils.db_utils import db_session
from app.utils.error_handler import (
    ErrorHandler,
    api_error_response,
    get_safe_error_message,
)
from server.auth import optional_auth, require_auth, require_auth_sse
from server.exercise_generator import (
    ensure_explanation,
    generate_ai_exercise,
    generate_simple_exercise,
)


async def generate_exercise(request):
    """Génère un nouvel exercice en utilisant le groupe d'âge."""
    params = request.query_params
    exercise_type_raw = params.get("type") or params.get("exercise_type")
    age_group_raw = params.get("age_group")  # Changed from difficulty
    use_ai = params.get("ai", False)

    # Normaliser et valider les paramètres
    from server.exercise_generator import normalize_and_validate_exercise_params

    exercise_type, age_group, derived_difficulty = (
        normalize_and_validate_exercise_params(exercise_type_raw, age_group_raw)
    )

    ai_generated = False
    if use_ai and str(use_ai).lower() in ["true", "1", "yes", "y"]:
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

        async with db_session() as db:
            # Sauvegarder l'exercice avec age_group et la difficulté dérivée
            created_exercise = EnhancedServerAdapter.create_generated_exercise(
                db=db,
                exercise_type=exercise_dict["exercise_type"],
                age_group=exercise_dict["age_group"],  # Save age_group
                difficulty=exercise_dict["difficulty"],  # Save derived difficulty
                title=exercise_dict["title"],
                question=exercise_dict["question"],
                correct_answer=exercise_dict["correct_answer"],
                choices=exercise_dict["choices"],
                explanation=exercise_dict["explanation"],
                hint=exercise_dict.get("hint"),
                tags=exercise_dict.get("tags", "generated"),
                ai_generated=ai_generated,
                locale=locale,
            )
            if created_exercise:
                exercise_id = created_exercise["id"]
                logger.info(f"Nouvel exercice créé avec ID={exercise_id}")
                logger.debug(f"Explication: {exercise_dict['explanation']}")
            else:
                logger.error("Erreur: L'exercice n'a pas été créé")
                templates = request.app.state.templates
                return templates.TemplateResponse(
                    "error.html",
                    {
                        "request": request,
                        "error": "Erreur de génération",
                        "message": "Impossible de créer l'exercice dans la base de données.",
                    },
                    status_code=500,
                )
        return RedirectResponse(url="/exercises?generated=true", status_code=303)
    except Exception as exercise_generation_error:
        logger.error(
            f"Erreur lors de la génération d'exercice: {exercise_generation_error}"
        )
        logger.debug(traceback.format_exc())
        templates = request.app.state.templates
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": "Erreur de génération",
                "message": f"Impossible de générer l'exercice: {str(exercise_generation_error)}",
            },
            status_code=500,
        )


async def get_exercise(request):
    """Récupère un exercice par son ID (format API, sans correct_answer)."""
    exercise_id = request.path_params.get("exercise_id")
    try:
        async with db_session() as db:
            exercise = ExerciseService.get_exercise_for_api(db, int(exercise_id))
        if not exercise:
            return ErrorHandler.create_not_found_error(
                resource_type="Exercice", resource_id=exercise_id
            )
        return JSONResponse(exercise)
    except (ValueError, TypeError):
        return ErrorHandler.create_not_found_error(
            resource_type="Exercice", resource_id=exercise_id
        )
    except Exception as exercise_retrieval_error:
        logger.error(
            f"Erreur récupération exercice: "
            f"{type(exercise_retrieval_error).__name__}: {exercise_retrieval_error}"
        )
        logger.debug(traceback.format_exc())
        return ErrorHandler.create_error_response(
            exercise_retrieval_error,
            status_code=500,
            user_message="Erreur lors de la récupération de l'exercice",
        )


@require_auth
async def submit_answer(request):
    """Orchestration HTTP : parse, valide, délègue à ExerciseService.submit_answer_result."""
    try:
        current_user = request.state.user
        try:
            raw_data = await request.json()
        except (json.JSONDecodeError, TypeError):
            return api_error_response(400, "Corps JSON invalide.")

        try:
            payload = SubmitAnswerRequest.model_validate(raw_data)
        except ValidationError as e:
            return JSONResponse(
                {"detail": e.errors()},
                status_code=422,
            )

        exercise_id = int(request.path_params.get("exercise_id"))
        user_id = current_user.get("id", 1)

        logger.debug(
            f"Traitement de la réponse: exercise_id={exercise_id}, "
            f"answer={payload.answer}"
        )

        async with db_session() as db:
            try:
                response_data = ExerciseService.submit_answer_result(
                    db, exercise_id, user_id, payload.answer, payload.time_spent
                )
                return JSONResponse(response_data.model_dump())
            except (ExerciseNotFoundError, ExerciseSubmitError) as e:
                return api_error_response(e.status_code, e.message)
            except Exception as db_error:
                logger.error(
                    f"❌ ERREUR lors de l'enregistrement: "
                    f"{type(db_error).__name__}: {db_error}"
                )
                logger.debug(traceback.format_exc())
                return api_error_response(
                    500, "Erreur lors de l'enregistrement de la tentative"
                )

    except (ExerciseNotFoundError, ExerciseSubmitError) as e:
        return api_error_response(e.status_code, e.message)
    except Exception as response_processing_error:
        logger.error(
            f"❌ ERREUR lors du traitement de la réponse: "
            f"{type(response_processing_error).__name__}: "
            f"{response_processing_error}"
        )
        logger.debug(traceback.format_exc())
        return ErrorHandler.create_error_response(
            response_processing_error,
            status_code=500,
            user_message="Erreur lors du traitement de la réponse",
        )


@optional_auth
async def get_exercises_list(request):
    """Retourne la liste des exercices avec pagination. Ordre aléatoire par défaut pour varier l'entraînement."""
    from server.handlers.exercise_list_params import (
        parse_exercise_list_params,
    )

    try:
        current_user = getattr(request.state, "user", None)
        q = parse_exercise_list_params(request)
        user_id = current_user.get("id") if current_user else None

        logger.debug(
            f"API exercises: limit={q.limit}, skip={q.skip}, "
            f"exercise_type={q.exercise_type}, age_group={q.age_group}"
        )

        async with db_session() as db:
            response_data = ExerciseService.get_exercises_list_for_api(
                db,
                limit=q.limit,
                skip=q.skip,
                exercise_type=q.exercise_type,
                age_group=q.age_group,
                search=q.search,
                order=q.order,
                hide_completed=q.hide_completed,
                user_id=user_id,
            )
            return JSONResponse(response_data.model_dump())

    except Exception as exercises_list_error:
        logger.error(
            f"Erreur lors de la récupération des exercices: {exercises_list_error}"
        )
        logger.debug(traceback.format_exc())
        return ErrorHandler.create_error_response(
            exercises_list_error,
            status_code=500,
            user_message="Erreur lors de la récupération des exercices",
        )


async def generate_exercise_api(request):
    """Génère un nouvel exercice via API JSON (POST) en utilisant le groupe d'âge."""
    try:
        # Récupérer les données JSON de la requête
        data = await request.json()
        exercise_type_raw = data.get("exercise_type")
        age_group_raw = data.get("age_group")  # Changed from difficulty
        use_ai = data.get("ai", False)

        # Normaliser et valider les paramètres
        from server.exercise_generator import normalize_and_validate_exercise_params

        exercise_type, age_group, derived_difficulty = (
            normalize_and_validate_exercise_params(exercise_type_raw, age_group_raw)
        )

        logger.debug(
            f"Génération API: type={exercise_type_raw}→{exercise_type}, groupe d'âge={age_group_raw}→{age_group}, IA={use_ai}"
        )

        # Valider les paramètres
        if not exercise_type_raw or not age_group_raw:
            return api_error_response(
                400, "Les paramètres 'exercise_type' et 'age_group' sont requis"
            )

        # Générer l'exercice
        ai_generated = False
        if use_ai and str(use_ai).lower() in ["true", "1", "yes", "y"]:
            exercise_dict = generate_ai_exercise(exercise_type, age_group)
            ai_generated = True
        else:
            exercise_dict = generate_simple_exercise(exercise_type, age_group)

        exercise_dict = ensure_explanation(exercise_dict)

        # Optionnellement sauvegarder en base de données
        save_to_db = data.get("save", True)
        if save_to_db:
            try:
                # Extraire la locale
                from app.utils.translation import parse_accept_language

                accept_language = request.headers.get("Accept-Language")
                locale = parse_accept_language(accept_language) or "fr"

                async with db_session() as db:
                    # Sauvegarder l'exercice avec age_group et la difficulté dérivée
                    created_exercise = EnhancedServerAdapter.create_generated_exercise(
                        db=db,
                        exercise_type=exercise_dict["exercise_type"],
                        age_group=exercise_dict["age_group"],  # Save age_group
                        difficulty=exercise_dict[
                            "difficulty"
                        ],  # Save derived difficulty
                        title=exercise_dict["title"],
                        question=exercise_dict["question"],
                        correct_answer=exercise_dict["correct_answer"],
                        choices=exercise_dict["choices"],
                        explanation=exercise_dict["explanation"],
                        hint=exercise_dict.get("hint"),
                        tags=exercise_dict.get("tags", "generated"),
                        ai_generated=ai_generated,
                        locale=locale,
                    )
                    if created_exercise:
                        exercise_dict["id"] = created_exercise["id"]
                        logger.info(
                            f"Exercice sauvegardé avec ID={created_exercise['id']}"
                        )
            except Exception as save_error:
                logger.warning(f"Erreur lors de la sauvegarde: {save_error}")
                # Continuer même si la sauvegarde échoue

        # Retourner l'exercice généré
        return JSONResponse(exercise_dict)

    except Exception as api_generation_error:
        logger.error(
            f"Erreur lors de la génération d'exercice API: {api_generation_error}"
        )
        logger.debug(traceback.format_exc())
        return ErrorHandler.create_error_response(
            api_generation_error,
            status_code=500,
            user_message="Erreur lors de la génération de l'exercice",
        )


@require_auth_sse
async def generate_ai_exercise_stream(request):
    """
    Génère un exercice avec OpenAI en streaming SSE.
    Délègue la logique au service exercise_ai_service.
    """
    try:
        from app.services.exercise_ai_service import (
            generate_exercise_stream as svc_generate_stream,
        )
        from app.utils.prompt_sanitizer import (
            sanitize_user_prompt,
            validate_prompt_safety,
        )
        from app.utils.sse_utils import SSE_HEADERS, sse_error_response
        from app.utils.translation import parse_accept_language
        from server.exercise_generator import normalize_and_validate_exercise_params

        current_user = request.state.user
        exercise_type_raw = request.query_params.get("exercise_type", "addition")
        age_group_raw = request.query_params.get(
            "age_group"
        ) or request.query_params.get("difficulty", "6-8")
        prompt_raw = request.query_params.get("prompt", "")

        is_safe, safety_reason = validate_prompt_safety(prompt_raw)
        if not is_safe:
            logger.warning(f"Prompt utilisateur rejeté pour sécurité: {safety_reason}")
            return sse_error_response(f"Prompt invalide: {safety_reason}")
        prompt = sanitize_user_prompt(prompt_raw)

        exercise_type, age_group, derived_difficulty = (
            normalize_and_validate_exercise_params(exercise_type_raw, age_group_raw)
        )

        if not settings.OPENAI_API_KEY:
            return sse_error_response("OpenAI API key non configurée")

        accept_language = request.headers.get("Accept-Language")
        locale = parse_accept_language(accept_language) or "fr"
        user_id = current_user.get("id") if current_user else None

        async def generate():
            async for event in svc_generate_stream(
                exercise_type=exercise_type,
                age_group=age_group,
                derived_difficulty=derived_difficulty,
                prompt=prompt,
                locale=locale,
                user_id=user_id,
            ):
                yield event

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
                **dict(SSE_HEADERS),
            },
        )

    except Exception as stream_error:
        logger.error(f"Erreur dans generate_ai_exercise_stream: {stream_error}")
        logger.debug(traceback.format_exc())
        from app.utils.sse_utils import sse_error_response

        return sse_error_response(str(stream_error))


@optional_auth
async def get_completed_exercises_ids(request: Request):
    """
    Récupère la liste des IDs d'exercices complétés par l'utilisateur actuel.
    Route: GET /api/exercises/completed-ids
    """
    try:
        current_user = request.state.user
        if not current_user:
            return JSONResponse({"completed_ids": []}, status_code=200)

        user_id = current_user.get("id")
        if not user_id:
            return JSONResponse({"completed_ids": []}, status_code=200)

        async with db_session() as db:
            completed_ids = ExerciseService.get_user_completed_exercise_ids(db, user_id)

        logger.debug(
            f"Récupération de {len(completed_ids)} exercices complétés pour l'utilisateur {user_id}"
        )
        return JSONResponse({"completed_ids": completed_ids})

    except Exception as completed_retrieval_error:
        logger.error(
            f"Erreur lors de la récupération des exercices complétés: {completed_retrieval_error}"
        )
        logger.debug(traceback.format_exc())
        return ErrorHandler.create_error_response(
            error=completed_retrieval_error,
            status_code=500,
            user_message="Erreur lors de la récupération des exercices complétés.",
        )


async def get_exercises_stats(request: Request):
    """
    Statistiques globales des Épreuves de l'Académie (exercices).

    Route: GET /api/exercises/stats

    Retourne les statistiques sur l'ensemble des exercices disponibles :
    - Nombre total d'épreuves dans l'Académie
    - Répartition par discipline (type d'exercice)
    - Répartition par rang (difficulté)
    - Répartition par groupe d'apprentis (groupe d'âge)
    - Statistiques de complétion globales

    Thème Académie des Sages :
    - Types → Disciplines mathématiques
    - Difficultés → Rangs de l'Académie (Initié → Grand Maître)
    - Groupes d'âge → Niveaux d'apprentissage
    """
    logger.info("=== DEBUT get_exercises_stats ===")
    try:
        async with db_session() as db:
            response_data = ExerciseStatsService.get_exercises_stats_for_api(db)
            total_exercises = response_data["academy_statistics"]["total_exercises"]
            logger.info(
                f"Statistiques des épreuves récupérées: {total_exercises} épreuves actives"
            )
            return JSONResponse(response_data)

    except Exception as e:
        logger.error(
            f"Erreur lors de la récupération des statistiques d'exercices: {e}"
        )
        traceback.print_exc()
        return api_error_response(
            500, "Une perturbation empêche l'accès aux archives. Réessayez plus tard."
        )
