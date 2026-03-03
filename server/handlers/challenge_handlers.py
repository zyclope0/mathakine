"""
Handlers pour les défis logiques (API Starlette)
"""

import json
import traceback
from datetime import datetime

from app.core.logging_config import get_logger

logger = get_logger(__name__)
from sqlalchemy.exc import SQLAlchemyError
from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse

import app.core.constants as constants
from app.core.config import settings

# Importer les constantes et fonctions centralisées
from app.core.constants import (
    CHALLENGE_TYPES_API,
    CHALLENGE_TYPES_DB,
    calculate_difficulty_for_age_group,
    normalize_age_group,
)
from app.core.messages import SystemMessages
from app.exceptions import ChallengeNotFoundError

# NOTE: challenge_service_translations_adapter archivé - utiliser fonctions de challenge_service.py
from app.services import challenge_service
from app.services.enhanced_server_adapter import EnhancedServerAdapter
from app.services.logic_challenge_service import LogicChallengeService
from app.utils.db_utils import db_session
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


@require_auth
@require_full_access
async def get_challenges_list(request: Request) -> JSONResponse:
    """
    Liste des défis logiques avec filtres optionnels.
    Route: GET /api/challenges
    """
    from app.schemas.logic_challenge import ChallengeListItem, ChallengeListResponse
    from server.handlers.challenge_list_params import parse_challenge_list_params

    try:
        current_user = request.state.user
        p = parse_challenge_list_params(request)

        accept_language = request.headers.get("Accept-Language", "fr")
        locale = parse_accept_language(accept_language)
        logger.debug(
            f"API - Paramètres: limit={p.limit}, skip={p.skip}, order={p.order}, "
            f"hide_completed={p.hide_completed}"
        )

        user_id = current_user.get("id")
        exclude_ids: list[int] = []

        async with db_session() as db:
            if p.hide_completed and user_id:
                exclude_ids = challenge_service.get_user_completed_challenges(
                    db, user_id
                )
            # Count d'abord pour random_offset (O(1) vs ORDER BY RANDOM() O(n))
            total = challenge_service.count_challenges(
                db=db,
                challenge_type=p.challenge_type,
                age_group=p.age_group_db,
                search=p.search,
                exclude_ids=exclude_ids if exclude_ids else None,
                active_only=p.active_only,
            )
            challenges = challenge_service.list_challenges(
                db=db,
                challenge_type=p.challenge_type,
                age_group=p.age_group_db,
                search=p.search,
                limit=p.limit,
                offset=p.skip,
                order=p.order,
                exclude_ids=exclude_ids if exclude_ids else None,
                total=total if p.order == "random" else None,
                active_only=p.active_only,
            )
            challenges_list = [
                ChallengeListItem.model_validate(
                    challenge_service.challenge_to_api_dict(c)
                )
                for c in challenges
            ]

        page = (p.skip // p.limit) + 1 if p.limit > 0 else 1
        has_more = (p.skip + len(challenges_list)) < total
        response_data = ChallengeListResponse(
            items=challenges_list,
            total=total,
            page=page,
            limit=p.limit,
            hasMore=has_more,
        )
        logger.info(
            f"Récupération réussie de {len(challenges_list)} défis sur {total} total (locale: {locale})"
        )
        return JSONResponse(response_data.model_dump())
    except ValueError as filter_validation_error:
        logger.error(f"Erreur de validation des paramètres: {filter_validation_error}")
        return ErrorHandler.create_validation_error(
            errors=[str(filter_validation_error)],
            user_message="Les paramètres de filtrage sont invalides.",
        )
    except Exception as challenges_retrieval_error:
        logger.error(
            f"Erreur lors de la récupération des défis: {challenges_retrieval_error}"
        )
        logger.debug(traceback.format_exc())
        return ErrorHandler.create_error_response(
            error=challenges_retrieval_error,
            status_code=500,
            user_message="Erreur lors de la récupération des défis.",
        )


@require_auth
@require_full_access
async def get_challenge(request: Request) -> JSONResponse:
    """
    Récupère un défi logique par son ID.
    Route: GET /api/challenges/{challenge_id}
    """
    try:
        current_user = request.state.user

        challenge_id = int(request.path_params.get("challenge_id"))

        # Récupérer la locale depuis le header Accept-Language
        accept_language = request.headers.get("Accept-Language", "fr")
        locale = parse_accept_language(accept_language)

        async with db_session() as db:
            from app.services.challenge_service import get_challenge_for_api

            challenge_dict = get_challenge_for_api(db, challenge_id)

        logger.info(
            f"Récupération réussie du défi logique {challenge_id} (locale: {locale})"
        )
        return JSONResponse(challenge_dict)
    except ChallengeNotFoundError:
        return api_error_response(404, "Défi logique non trouvé")
    except ValueError as id_validation_error:
        logger.error(f"Erreur de validation: {id_validation_error}")
        return ErrorHandler.create_validation_error(
            errors=["ID de défi invalide"],
            user_message="L'identifiant du défi est invalide.",
        )
    except Exception as challenge_retrieval_error:
        logger.error(
            f"Erreur lors de la récupération du défi: {challenge_retrieval_error}"
        )
        logger.debug(traceback.format_exc())
        return ErrorHandler.create_error_response(
            error=challenge_retrieval_error,
            status_code=500,
            user_message="Erreur lors de la récupération du défi.",
        )


@require_auth
@require_full_access
async def submit_challenge_answer(request: Request) -> JSONResponse:
    """
    Soumet une réponse à un défi logique.
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

        user_solution = data.get("user_solution") or data.get("answer")
        time_spent = data.get("time_spent")
        hints_used_raw = data.get("hints_used", [])

        # Convertir hints_used de liste à entier (nombre d'indices utilisés)
        # Le modèle attend un Integer, pas une liste
        if isinstance(hints_used_raw, list):
            hints_used_count = len(hints_used_raw)
        elif isinstance(hints_used_raw, int):
            hints_used_count = hints_used_raw
        else:
            hints_used_count = 0

        if not user_solution:
            return api_error_response(400, "Réponse requise")

        async with db_session() as db:
            challenge = LogicChallengeService.get_challenge_or_raise(db, challenge_id)

            from app.services.challenge_answer_service import check_answer

            challenge_type = (
                str(challenge.challenge_type).lower()
                if challenge.challenge_type
                else ""
            )
            is_correct = check_answer(
                challenge_type=challenge_type,
                user_answer=user_solution,
                correct_answer=challenge.correct_answer or "",
                visual_data=getattr(challenge, "visual_data", None),
            )

            attempt_data = {
                "user_id": user_id,
                "challenge_id": challenge_id,
                "user_solution": user_solution,
                "is_correct": is_correct,
                "time_spent": time_spent,
                "hints_used": hints_used_count,
            }
            logger.debug(
                f"Tentative d'enregistrement de challenge avec attempt_data: {attempt_data}"
            )
            attempt = LogicChallengeService.record_attempt(db, attempt_data)
            if not attempt:
                return api_error_response(500, "Impossible d'enregistrer la tentative.")
            logger.debug(f"Tentative challenge créée: {attempt.id}")

            # Lot C / B5 : vérifier les badges (défis logiques, mixte) après une tentative correcte
            new_badges = []
            if is_correct:
                try:
                    from app.services.badge_service import BadgeService

                    badge_service = BadgeService(db)
                    new_badges = badge_service.check_and_award_badges(user_id)
                except (SQLAlchemyError, TypeError, ValueError) as badge_err:
                    logger.warning(
                        "Badge check après défi (best effort): %s",
                        badge_err,
                        exc_info=True,
                    )

            # Mettre à jour la série d'entraînement (streak) — toute tentative compte
            try:
                from app.services.streak_service import update_user_streak
            except ImportError:
                logger.warning(
                    "Streak service indisponible (ImportError)", exc_info=True
                )
            else:
                try:
                    update_user_streak(db, user_id)
                except SQLAlchemyError:
                    logger.debug("Streak update skipped (DB error)", exc_info=True)
                except (TypeError, ValueError):
                    logger.debug(
                        "Streak update skipped (data/type error)", exc_info=True
                    )

            # Notification « Tu approches » si pas de nouveau badge mais un proche
            progress_notif = None
            if not new_badges:
                try:
                    from app.services.badge_service import BadgeService

                    svc = BadgeService(db)
                    progress_notif = svc.get_closest_progress_notification(user_id)
                except (SQLAlchemyError, TypeError, ValueError):
                    logger.debug(
                        "Progress notification skipped (best effort)",
                        exc_info=True,
                    )

            response_data = {
                "is_correct": is_correct,
                "explanation": challenge.solution_explanation if is_correct else None,
                "new_badges": new_badges,
            }
            if progress_notif:
                response_data["progress_notification"] = progress_notif

            if not is_correct:
                # Ne pas révéler la bonne réponse immédiatement, mais la donner dans l'explication après plusieurs tentatives
                hints_list = (
                    challenge.hints if isinstance(challenge.hints, list) else []
                )
                response_data["hints_remaining"] = len(hints_list) - hints_used_count

            return JSONResponse(response_data)
    except ChallengeNotFoundError:
        return api_error_response(404, "Défi logique non trouvé")
    except ValueError:
        return api_error_response(400, "ID de défi invalide")
    except Exception as submission_error:
        logger.error(f"Erreur lors de la soumission de la réponse: {submission_error}")
        import traceback

        logger.debug(traceback.format_exc())
        return api_error_response(500, get_safe_error_message(submission_error))


@require_auth
@require_full_access
async def get_challenge_hint(request: Request) -> JSONResponse:
    """
    Récupère un indice pour un défi logique.
    Route: GET /api/challenges/{challenge_id}/hint
    """
    try:
        challenge_id = int(request.path_params.get("challenge_id"))
        level = int(request.query_params.get("level", 1))

        async with db_session() as db:
            challenge = LogicChallengeService.get_challenge_or_raise(db, challenge_id)

            # Récupérer les indices
            hints = challenge.hints
            if isinstance(hints, str):
                try:
                    hints = json.loads(hints)
                except (json.JSONDecodeError, ValueError):
                    # Si le parsing échoue, traiter comme une liste vide
                    hints = []
            elif hints is None:
                hints = []

            # S'assurer que hints est une liste
            if not isinstance(hints, list):
                hints = []

            if level < 1 or level > len(hints):
                return api_error_response(
                    400, f"Indice de niveau {level} non disponible"
                )

            # Retourner l'indice spécifique au niveau demandé (index 0-based)
            hint_text = hints[level - 1] if level <= len(hints) else None
            return JSONResponse(
                {"hint": hint_text}
            )  # Retourner l'indice spécifique au niveau
    except ChallengeNotFoundError:
        return api_error_response(404, "Défi logique non trouvé")
    except ValueError:
        return api_error_response(400, "ID de défi ou niveau invalide")
    except Exception as hint_retrieval_error:
        logger.error(
            f"Erreur lors de la récupération de l'indice: {hint_retrieval_error}",
            exc_info=True,
        )
        return api_error_response(500, get_safe_error_message(hint_retrieval_error))


@optional_auth
async def get_completed_challenges_ids(request: Request) -> JSONResponse:
    """
    Récupère la liste des IDs de challenges complétés par l'utilisateur actuel.
    Route: GET /api/challenges/completed-ids
    """
    try:
        current_user = request.state.user
        if not current_user:
            return JSONResponse({"completed_ids": []}, status_code=200)

        user_id = current_user.get("id")
        if not user_id:
            return JSONResponse({"completed_ids": []}, status_code=200)

        async with db_session() as db:
            completed_ids = challenge_service.get_user_completed_challenges(db, user_id)

        logger.debug(
            f"Récupération de {len(completed_ids)} challenges complétés pour l'utilisateur {user_id}"
        )
        return JSONResponse({"completed_ids": completed_ids})

    except Exception as completed_challenges_error:
        logger.error(
            f"Erreur lors de la récupération des challenges complétés: {completed_challenges_error}"
        )
        logger.debug(traceback.format_exc())
        return ErrorHandler.create_error_response(
            error=completed_challenges_error,
            status_code=500,
            user_message="Erreur lors de la récupération des challenges complétés.",
        )


@require_auth_sse
@require_full_access
async def generate_ai_challenge_stream(request: Request) -> Response:
    """
    Génère un challenge avec OpenAI en streaming SSE.
    Délègue la logique au service challenge_ai_service.
    """
    try:
        current_user = request.state.user
        challenge_type_raw = request.query_params.get("challenge_type", "sequence")
        age_group_raw = request.query_params.get("age_group", "10-12")
        prompt_raw = request.query_params.get("prompt", "")

        from app.services.challenge_ai_service import (
            generate_challenge_stream as svc_generate_stream,
        )
        from app.utils.prompt_sanitizer import (
            sanitize_user_prompt,
            validate_prompt_safety,
        )
        from app.utils.sse_utils import SSE_HEADERS, sse_error_response

        is_safe, safety_reason = validate_prompt_safety(prompt_raw)
        if not is_safe:
            logger.warning(f"Prompt utilisateur rejeté pour sécurité: {safety_reason}")
            return sse_error_response(f"Prompt invalide: {safety_reason}")

        prompt = sanitize_user_prompt(prompt_raw)

        challenge_type = challenge_type_raw.lower()
        valid_types = [
            "sequence",
            "pattern",
            "visual",
            "puzzle",
            "graph",
            "riddle",
            "deduction",
            "chess",
            "coding",
            "probability",
        ]
        if challenge_type not in valid_types:
            logger.warning(
                f"Type de challenge invalide: {challenge_type_raw}, utilisation de 'sequence' par défaut"
            )
            challenge_type = "sequence"

        normalized_age_group = normalize_age_group(age_group_raw)
        age_group = (
            normalized_age_group
            if normalized_age_group
            else constants.AgeGroups.GROUP_6_8
        )

        user_id = current_user.get("id")
        if user_id:
            from app.utils.rate_limiter import rate_limiter

            allowed, rate_limit_reason = rate_limiter.check_rate_limit(
                user_id=user_id, max_per_hour=10, max_per_day=50
            )
            if not allowed:
                logger.warning(
                    f"Rate limit atteint pour utilisateur {user_id}: {rate_limit_reason}"
                )
                return sse_error_response(
                    f"Limite de génération atteinte: {rate_limit_reason}"
                )

        if not settings.OPENAI_API_KEY:
            return sse_error_response("OpenAI API key non configurée")

        accept_language = request.headers.get("Accept-Language", "fr")
        locale = parse_accept_language(accept_language) or "fr"

        async def generate():
            async for event in svc_generate_stream(
                challenge_type=challenge_type,
                age_group=age_group,
                prompt=prompt,
                user_id=user_id,
                locale=locale,
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
        return sse_error_response("Erreur lors de la génération")
