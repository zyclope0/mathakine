"""
Handlers pour les defis logiques (API Starlette)

LOT 1 : handlers de lecture anemiques - parse, appel query service, mapping HTTP.
"""

import traceback

from pydantic import ValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse

from app.core.logging_config import get_logger
from app.exceptions import ChallengeNotFoundError
from app.schemas.logic_challenge import ChallengeAttemptRequest, ChallengeListResponse
from app.services.challenge_attempt_service import submit_challenge_attempt
from app.services.challenge_query_service import (
    get_challenge_detail_for_api,
    get_challenge_hint_for_api,
)
from app.services.challenge_query_service import (
    get_completed_challenges_ids as query_completed_challenges_ids,
)
from app.services.challenge_query_service import (
    list_challenges_for_api,
)
from app.services.challenge_stream_service import prepare_stream_context
from app.utils.error_handler import (
    ErrorHandler,
    api_error_response,
    get_safe_error_message,
)
from app.utils.request_utils import parse_json_body_any
from app.utils.translation import parse_accept_language
from server.auth import (
    optional_auth,
    require_auth,
    require_auth_sse,
    require_full_access,
)

logger = get_logger(__name__)


def _first_validation_error_message(ve: ValidationError) -> str:
    """Extrait le premier message d'erreur d'une ValidationError Pydantic."""
    errs = ve.errors()
    if errs:
        msg = errs[0].get("msg", "Payload invalide")
        return str(msg) if isinstance(msg, str) else "Payload invalide"
    return "Payload invalide"


@require_auth
@require_full_access
async def get_challenges_list(request: Request) -> JSONResponse:
    """
    Liste des defis logiques avec filtres optionnels.
    Route: GET /api/challenges
    """
    from server.handlers.challenge_list_params import parse_challenge_list_params

    try:
        current_user = request.state.user
        p = parse_challenge_list_params(request)

        accept_language = request.headers.get("Accept-Language", "fr")
        locale = parse_accept_language(accept_language)
        logger.debug(
            f"API - Parametres: limit={p.limit}, skip={p.skip}, order={p.order}, "
            f"hide_completed={p.hide_completed}"
        )

        user_id = current_user.get("id")

        response_data = await list_challenges_for_api(
            challenge_type=p.challenge_type,
            age_group_db=p.age_group_db,
            search=p.search,
            skip=p.skip,
            limit=p.limit,
            active_only=p.active_only,
            order=p.order,
            hide_completed=p.hide_completed,
            user_id=user_id,
        )
        total = response_data.get("total", 0)
        items_count = len(response_data.get("items", []))
        logger.info(
            f"Recuperation reussie de {items_count} defis sur {total} total (locale: {locale})"
        )
        return JSONResponse(ChallengeListResponse(**response_data).model_dump())
    except ValueError as filter_validation_error:
        logger.error(f"Erreur de validation des parametres: {filter_validation_error}")
        return ErrorHandler.create_validation_error(
            errors=[str(filter_validation_error)],
            user_message="Les parametres de filtrage sont invalides.",
        )
    except Exception as challenges_retrieval_error:
        logger.error(
            f"Erreur lors de la recuperation des defis: {challenges_retrieval_error}"
        )
        logger.debug(traceback.format_exc())
        return ErrorHandler.create_error_response(
            error=challenges_retrieval_error,
            status_code=500,
            user_message="Erreur lors de la recuperation des defis.",
        )


@require_auth
@require_full_access
async def get_challenge(request: Request) -> JSONResponse:
    """
    Recupere un defi logique par son ID.
    Route: GET /api/challenges/{challenge_id}
    """
    try:
        challenge_id = int(request.path_params.get("challenge_id"))

        accept_language = request.headers.get("Accept-Language", "fr")
        locale = parse_accept_language(accept_language)

        challenge_dict = await get_challenge_detail_for_api(challenge_id)

        logger.info(
            f"Recuperation reussie du defi logique {challenge_id} (locale: {locale})"
        )
        return JSONResponse(challenge_dict)
    except ChallengeNotFoundError:
        return api_error_response(404, "Defi logique non trouve")
    except ValueError as id_validation_error:
        logger.error(f"Erreur de validation: {id_validation_error}")
        return ErrorHandler.create_validation_error(
            errors=["ID de defi invalide"],
            user_message="L'identifiant du defi est invalide.",
        )
    except Exception as challenge_retrieval_error:
        logger.error(
            f"Erreur lors de la recuperation du defi: {challenge_retrieval_error}"
        )
        logger.debug(traceback.format_exc())
        return ErrorHandler.create_error_response(
            error=challenge_retrieval_error,
            status_code=500,
            user_message="Erreur lors de la recuperation du defi.",
        )


@require_auth
@require_full_access
async def submit_challenge_answer(request: Request) -> JSONResponse:
    """
    Soumet une reponse a un defi logique.
    Route: POST /api/challenges/{challenge_id}/attempt
    """
    try:
        current_user = request.state.user

        user_id = current_user.get("id")
        if not user_id:
            return api_error_response(401, "Utilisateur invalide")

        challenge_id = int(request.path_params.get("challenge_id"))
        data_or_err = await parse_json_body_any(request)
        if isinstance(data_or_err, JSONResponse):
            return data_or_err
        data = data_or_err

        try:
            attempt_req = ChallengeAttemptRequest.model_validate(data)
        except ValidationError as ve:
            return api_error_response(400, _first_validation_error_message(ve))

        response_data = await submit_challenge_attempt(
            challenge_id, user_id, attempt_req
        )
        return JSONResponse(response_data)
    except ChallengeNotFoundError:
        return api_error_response(404, "Defi logique non trouve")
    except ValueError:
        return api_error_response(400, "ID de defi invalide")
    except Exception as submission_error:
        logger.error(f"Erreur lors de la soumission de la reponse: {submission_error}")
        logger.debug(traceback.format_exc())
        return api_error_response(500, get_safe_error_message(submission_error))


@require_auth
@require_full_access
async def get_challenge_hint(request: Request) -> JSONResponse:
    """
    Recupere un indice pour un defi logique.
    Route: GET /api/challenges/{challenge_id}/hint
    """
    try:
        challenge_id = int(request.path_params.get("challenge_id"))
        level = int(request.query_params.get("level", 1))

        hint_data = await get_challenge_hint_for_api(challenge_id, level)
        return JSONResponse(hint_data)
    except ChallengeNotFoundError:
        return api_error_response(404, "Defi logique non trouve")
    except ValueError as ve:
        err_msg = str(ve).strip()
        if "Indice de niveau" in err_msg and "non disponible" in err_msg:
            return api_error_response(400, err_msg)
        return api_error_response(400, "ID de defi ou niveau invalide")
    except Exception as hint_retrieval_error:
        logger.error(
            f"Erreur lors de la recuperation de l'indice: {hint_retrieval_error}",
            exc_info=True,
        )
        return api_error_response(500, get_safe_error_message(hint_retrieval_error))


@optional_auth
async def get_completed_challenges_ids(request: Request) -> JSONResponse:
    """
    Recupere la liste des IDs de challenges completes par l'utilisateur actuel.
    Route: GET /api/challenges/completed-ids
    """
    try:
        current_user = request.state.user
        if not current_user:
            return JSONResponse({"completed_ids": []}, status_code=200)

        user_id = current_user.get("id")
        if not user_id:
            return JSONResponse({"completed_ids": []}, status_code=200)

        completed_ids = await query_completed_challenges_ids(user_id)

        logger.debug(
            f"Recuperation de {len(completed_ids)} challenges completes pour l'utilisateur {user_id}"
        )
        return JSONResponse({"completed_ids": completed_ids})

    except Exception as completed_challenges_error:
        logger.error(
            f"Erreur lors de la recuperation des challenges completes: {completed_challenges_error}"
        )
        logger.debug(traceback.format_exc())
        return ErrorHandler.create_error_response(
            error=completed_challenges_error,
            status_code=500,
            user_message="Erreur lors de la recuperation des challenges completes.",
        )


@require_auth_sse
@require_full_access
async def generate_ai_challenge_stream(request: Request) -> Response:
    """
    Genere un challenge avec OpenAI en streaming SSE.
    Handler fin : lecture request, preparation via challenge_stream_service, StreamingResponse.
    """
    from app.services.challenge_ai_service import (
        generate_challenge_stream as svc_generate_stream,
    )
    from app.utils.sse_utils import SSE_HEADERS, sse_error_response

    try:
        current_user = request.state.user
        query, error_msg = prepare_stream_context(
            challenge_type_raw=request.query_params.get("challenge_type", "sequence"),
            age_group_raw=request.query_params.get("age_group", "10-12"),
            prompt_raw=request.query_params.get("prompt", ""),
            user_id=current_user.get("id") if current_user else None,
            accept_language=request.headers.get("Accept-Language", "fr"),
        )

        if error_msg:
            return sse_error_response(error_msg)

        async def generate():
            async for event in svc_generate_stream(
                challenge_type=query.challenge_type,
                age_group=query.age_group,
                prompt=query.prompt,
                user_id=query.user_id,
                locale=query.locale,
            ):
                yield event

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers=dict(SSE_HEADERS),
        )

    except Exception as ai_stream_error:
        logger.error(
            f"Erreur dans generate_ai_challenge_stream: {ai_stream_error}",
            exc_info=True,
        )
        return sse_error_response("Erreur lors de la generation")
