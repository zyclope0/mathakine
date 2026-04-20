"""
Handlers pour la génération d'exercices (API)
"""

import json
import traceback

from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from starlette.requests import Request
from starlette.responses import (
    JSONResponse,
    RedirectResponse,
    Response,
    StreamingResponse,
)

from app.core.logging_config import get_logger
from app.core.runtime import run_db_bound
from app.exceptions import (
    ExerciseNotFoundError,
    ExerciseSubmitError,
    InterleavedNotEnoughVariety,
)
from app.schemas.exercise import (
    GenerateExerciseRequest,
    GenerateExerciseStreamPostBody,
    GenerateExerciseStreamQuery,
    InterleavedPlanQuery,
    SubmitAnswerRequest,
)
from app.services.exercises.exercise_attempt_service import submit_answer_sync
from app.services.exercises.exercise_generation_service import (
    AgeGroupRequiredError,
    generate_exercise_sync,
)
from app.services.exercises.exercise_query_service import (
    get_completed_exercise_ids_sync,
    get_exercise_for_api_sync,
    get_exercises_list_for_api_sync,
    get_exercises_stats_for_api_sync,
    get_interleaved_plan_for_api_sync,
)
from app.services.exercises.exercise_stream_service import prepare_stream_context
from app.utils.error_handler import (
    ErrorHandler,
    api_error_response,
    capture_internal_error_response,
)
from app.utils.request_utils import parse_json_body_any, parse_json_body_as_model
from app.utils.translation import parse_accept_language
from server.auth import optional_auth, require_auth, require_auth_sse
from server.exercise_generator import normalize_and_validate_exercise_params

logger = get_logger(__name__)


def _parse_submit_answer_payload(raw_data: dict) -> SubmitAnswerRequest:
    """Valide la payload de soumission d'exercice hors contexte HTTP."""
    return SubmitAnswerRequest.model_validate(raw_data)


async def generate_exercise(request: Request) -> Response:
    """Génère un nouvel exercice en utilisant le groupe d'âge.

    Paramètre ?adaptive=true (défaut) : si l'utilisateur est authentifié et
    qu'aucun age_group n'est fourni explicitement, la difficulté est résolue
    de façon adaptative (IRT → progression → profil → fallback).
    Passer ?adaptive=false ou fournir age_group pour forcer le mode statique.
    """
    params = request.query_params
    exercise_type_raw = params.get("type") or params.get("exercise_type")
    age_group_raw = params.get("age_group")
    use_ai = params.get("ai", False)
    adaptive = params.get("adaptive", "true").lower() not in ("false", "0", "no")
    current_user = getattr(request.state, "user", None)
    user_id = current_user["id"] if current_user else None
    locale = parse_accept_language(request.headers.get("Accept-Language")) or "fr"

    try:
        result = await run_db_bound(
            generate_exercise_sync,
            exercise_type_raw or "addition",
            age_group_raw,
            use_ai,
            adaptive,
            True,  # save
            user_id,
            locale,
            False,  # require_age_group
        )
        if result.id:
            logger.info("Nouvel exercice créé avec ID=%s", result.id)
        return RedirectResponse(url="/exercises?generated=true", status_code=303)
    except Exception as exercise_generation_error:
        logger.error(
            "Erreur lors de la génération d'exercice: %s", exercise_generation_error
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


async def get_exercise(request: Request) -> JSONResponse:
    """Récupère un exercice par son ID (format API, sans correct_answer)."""
    exercise_id = request.path_params.get("exercise_id")
    try:
        exercise = await run_db_bound(get_exercise_for_api_sync, int(exercise_id))
        if exercise is None:
            raise ExerciseSubmitError(
                500, "Erreur lors de la récupération de l'exercice"
            )
        return JSONResponse(exercise)
    except (ExerciseNotFoundError,) as e:
        return api_error_response(e.status_code, e.message)
    except (ValueError, TypeError):
        return ErrorHandler.create_not_found_error(
            resource_type="Exercice", resource_id=exercise_id
        )
    except Exception as exercise_retrieval_error:
        logger.error(
            "Erreur récupération exercice: %s: %s",
            type(exercise_retrieval_error).__name__,
            exercise_retrieval_error,
        )
        logger.debug(traceback.format_exc())
        return ErrorHandler.create_error_response(
            exercise_retrieval_error,
            status_code=500,
            user_message="Erreur lors de la récupération de l'exercice",
        )


@require_auth
async def submit_answer(request: Request) -> JSONResponse:
    """Orchestration HTTP : parse, valide, délègue à exercise_attempt_service.submit_answer."""
    try:
        current_user = request.state.user
        raw_data_or_err = await parse_json_body_any(request)
        if isinstance(raw_data_or_err, JSONResponse):
            # Contrat submit_answer: JSON invalide -> 400 (pas 422)
            if raw_data_or_err.status_code == 422:
                return api_error_response(400, "Corps JSON invalide.")
            return raw_data_or_err
        raw_data = raw_data_or_err

        try:
            payload = _parse_submit_answer_payload(raw_data)
        except ValidationError as e:
            return JSONResponse(
                {"detail": e.errors()},
                status_code=422,
            )

        exercise_id = int(request.path_params.get("exercise_id"))
        user_id = current_user.get("id", 1)

        logger.debug(
            "Traitement de la réponse: exercise_id=%s, answer=%s",
            exercise_id,
            payload.answer,
        )

        response_data = await run_db_bound(
            submit_answer_sync,
            exercise_id,
            user_id,
            payload.answer,
            payload.time_spent,
        )
        return JSONResponse(response_data.model_dump())

    except (ExerciseNotFoundError, ExerciseSubmitError) as e:
        return api_error_response(e.status_code, e.message)
    except (ValueError, TypeError):
        return api_error_response(400, "Identifiant d'exercice invalide")
    except SQLAlchemyError as submit_db_error:
        logger.error(
            "exercise.submit_answer: erreur base de données: %s",
            submit_db_error,
            exc_info=True,
        )
        return capture_internal_error_response(
            submit_db_error,
            "Erreur lors du traitement de la réponse",
            tags={
                "handler": "exercise.submit_answer",
                "error_class": "SQLAlchemyError",
            },
        )
    except Exception as response_processing_error:
        logger.error(
            "❌ ERREUR lors du traitement de la réponse: %s: %s",
            type(response_processing_error).__name__,
            response_processing_error,
        )
        logger.debug(traceback.format_exc())
        return ErrorHandler.create_error_response(
            response_processing_error,
            status_code=500,
            user_message="Erreur lors du traitement de la réponse",
        )


@optional_auth
async def get_exercises_list(request: Request) -> JSONResponse:
    """Retourne la liste des exercices avec pagination. Ordre aléatoire par défaut pour varier l'entraînement."""
    from server.handlers.exercise_list_params import (
        parse_exercise_list_params,
    )

    try:
        current_user = getattr(request.state, "user", None)
        q = parse_exercise_list_params(request)
        user_id = current_user.get("id") if current_user else None

        logger.debug(
            "API exercises: limit=%s, skip=%s, exercise_type=%s, age_group=%s",
            q.limit,
            q.skip,
            q.exercise_type,
            q.age_group,
        )

        response_data = await run_db_bound(get_exercises_list_for_api_sync, q, user_id)
        return JSONResponse(response_data.model_dump())

    except Exception as exercises_list_error:
        logger.error(
            "Erreur lors de la récupération des exercices: %s", exercises_list_error
        )
        logger.debug(traceback.format_exc())
        return ErrorHandler.create_error_response(
            exercises_list_error,
            status_code=500,
            user_message="Erreur lors de la récupération des exercices",
        )


@require_auth
async def get_interleaved_plan_api(request: Request) -> JSONResponse:
    """F32 — Retourne un plan entrelacé de types d'exercices pour l'utilisateur."""
    try:
        length_raw = request.query_params.get("length", "10")
        try:
            length = int(length_raw)
        except ValueError:
            length = 10
        if length < 1:
            length = 10

        current_user = request.state.user
        user_id = current_user["id"]

        query = InterleavedPlanQuery(length=length)
        plan = await run_db_bound(get_interleaved_plan_for_api_sync, user_id, query)
        return JSONResponse(plan)

    except InterleavedNotEnoughVariety as e:
        return JSONResponse(
            {
                "detail": {
                    "code": "not_enough_variety",
                    "message": e.message,
                }
            },
            status_code=409,
        )
    except Exception as plan_err:
        logger.error("Erreur plan entrelacé: %s", plan_err)
        logger.debug(traceback.format_exc())
        return ErrorHandler.create_error_response(
            plan_err,
            status_code=500,
            user_message="Erreur lors du calcul du plan",
        )


@optional_auth
async def generate_exercise_api(request: Request) -> JSONResponse:
    """Génère un nouvel exercice via API JSON (POST) en utilisant le groupe d'âge.

    Paramètre "adaptive": true (défaut) : si l'utilisateur est authentifié et
    qu'aucun age_group n'est fourni, la difficulté est résolue de façon adaptative.
    """
    try:
        data_or_err = await parse_json_body_any(request)
        if isinstance(data_or_err, JSONResponse):
            return data_or_err

        try:
            payload = GenerateExerciseRequest.model_validate(data_or_err)
        except ValidationError as e:
            return JSONResponse({"detail": e.errors()}, status_code=422)

        if not payload.exercise_type or not str(payload.exercise_type).strip():
            return api_error_response(400, "Le paramètre 'exercise_type' est requis")

        current_user = getattr(request.state, "user", None)
        user_id = current_user["id"] if current_user else None
        locale = parse_accept_language(request.headers.get("Accept-Language")) or "fr"

        try:
            result = await run_db_bound(
                generate_exercise_sync,
                payload.exercise_type,
                payload.age_group,
                payload.ai,
                payload.adaptive,
                payload.save,
                user_id,
                locale,
                True,  # require_age_group
            )
        except AgeGroupRequiredError as e:
            return api_error_response(400, str(e))

        return JSONResponse(result.model_dump(mode="json", exclude_none=True))

    except Exception as api_generation_error:
        logger.error(
            "Erreur lors de la génération d'exercice API: %s", api_generation_error
        )
        logger.debug(traceback.format_exc())
        return ErrorHandler.create_error_response(
            api_generation_error,
            status_code=500,
            user_message="Erreur lors de la génération de l'exercice",
        )


@require_auth_sse
async def generate_ai_exercise_stream(request: Request) -> Response:
    """
    Génère un exercice avec OpenAI en streaming SSE.
    Body JSON typé (POST) — le prompt ne transite plus dans l'URL.
    """
    try:
        from app.services.exercises.exercise_ai_service import (
            generate_exercise_stream as svc_generate_stream,
        )
        from app.utils.sse_utils import SSE_HEADERS, sse_error_response

        body_or_err = await parse_json_body_as_model(
            request, GenerateExerciseStreamPostBody
        )
        if isinstance(body_or_err, JSONResponse):
            return body_or_err

        query = GenerateExerciseStreamQuery(
            exercise_type=body_or_err.exercise_type,
            age_group=body_or_err.age_group,
            prompt=body_or_err.prompt,
        )
        current_user = request.state.user
        user_id = current_user.get("id") if current_user else None
        accept_language = request.headers.get("Accept-Language")

        context, error = await run_db_bound(
            prepare_stream_context, query, user_id, accept_language
        )
        if error:
            logger.warning("Préparation stream rejetée: %s", error)
            return sse_error_response(error)

        async def generate():
            async for event in svc_generate_stream(
                exercise_type=context.exercise_type,
                age_group=context.age_group,
                derived_difficulty=context.derived_difficulty,
                pedagogical_band_override=context.pedagogical_band,
                prompt=context.prompt,
                locale=context.locale,
                user_id=context.user_id,
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
        logger.error("Erreur dans generate_ai_exercise_stream: %s", stream_error)
        logger.debug(traceback.format_exc())
        from app.utils.sse_utils import sse_error_response

        return sse_error_response(str(stream_error))


@optional_auth
async def get_completed_exercises_ids(request: Request) -> JSONResponse:
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

        completed_ids = await run_db_bound(get_completed_exercise_ids_sync, user_id)

        logger.debug(
            "Récupération de %s exercices complétés pour l'utilisateur %s",
            len(completed_ids),
            user_id,
        )
        return JSONResponse({"completed_ids": completed_ids})

    except Exception as completed_retrieval_error:
        logger.error(
            "Erreur lors de la récupération des exercices complétés: %s",
            completed_retrieval_error,
        )
        logger.debug(traceback.format_exc())
        return ErrorHandler.create_error_response(
            error=completed_retrieval_error,
            status_code=500,
            user_message="Erreur lors de la récupération des exercices complétés.",
        )


async def get_exercises_stats(request: Request) -> JSONResponse:
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
        response_data = await run_db_bound(get_exercises_stats_for_api_sync)
        total_exercises = response_data["academy_statistics"]["total_exercises"]
        logger.info(
            "Statistiques des épreuves récupérées: %s épreuves actives", total_exercises
        )
        return JSONResponse(response_data)

    except Exception as e:
        logger.error(
            "Erreur lors de la récupération des statistiques d'exercices: %s",
            e,
            exc_info=True,
        )
        return api_error_response(
            500, "Une perturbation empêche l'accès aux archives. Réessayez plus tard."
        )
