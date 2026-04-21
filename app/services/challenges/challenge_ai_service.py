"""
Service de gÃ©nÃ©ration de challenges par IA.
Extrait la logique de gÃ©nÃ©ration streaming depuis challenge_handlers.
"""

import json
import traceback
from datetime import datetime
from typing import TYPE_CHECKING, Any, AsyncGenerator, Dict, Optional

from openai import APIError, APITimeoutError, AsyncOpenAI, RateLimitError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.ai_config import AIConfig
from app.core.config import settings
from app.core.db_boundary import sync_db_session
from app.core.logging_config import get_logger
from app.core.runtime import run_db_bound
from app.services.challenges import challenge_service
from app.services.challenges.challenge_ai_model_policy import (
    build_challenge_ai_stream_kwargs,
    resolve_challenge_ai_fallback_model,
)
from app.services.challenges.challenge_contract_policy import (
    apply_visual_contract_normalization,
    compute_response_mode,
    filter_choices_for_persistence,
    sanitize_choices_for_delivery,
)
from app.services.challenges.challenge_difficulty_policy import (
    calibrate_challenge_difficulty,
)
from app.services.challenges.challenge_prompt_composition import (
    AGE_GROUP_PARAMS,
    build_challenge_system_prompt,
    build_challenge_user_prompt,
)
from app.services.challenges.challenge_service import normalize_age_group_for_frontend
from app.services.challenges.challenge_validator import (
    auto_correct_challenge,
    validate_challenge_logic,
)
from app.utils.circuit_breaker import (
    OPENAI_CIRCUIT_OPEN_USER_MESSAGE,
    is_countable_openai_failure,
    openai_workload_circuit_breaker,
)
from app.utils.error_handler import get_safe_error_message
from app.utils.generation_metrics import generation_metrics
from app.utils.json_utils import extract_json_from_text
from app.utils.sse_utils import sse_error_message, sse_status_message
from app.utils.token_tracker import token_tracker

if TYPE_CHECKING:
    from app.schemas.logic_challenge import ChallengeStreamPersonalizationMeta

logger = get_logger(__name__)
CHALLENGE_AI_GENERIC_ERROR_MESSAGE = (
    "Erreur inattendue lors de la g\u00e9n\u00e9ration du d\u00e9fi. R\u00e9essayez."
)
CHALLENGE_AI_TRANSIENT_ERROR_MESSAGE = (
    "Erreur temporaire lors de la g\u00e9n\u00e9ration du d\u00e9fi. R\u00e9essayez."
)


def normalize_generated_challenge(
    challenge_data: Dict[str, Any],
    challenge_type: str,
    age_group: str,
    *,
    f42_rating_hint: Optional[float] = None,
    difficulty_tier: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Normalise les données générées avec ajustements de difficulté (policy IA5).
    difficulty_tier: F42 tier 1-12 from the personalization context — included
    in the output so that fallback SSE paths (DB error) carry the tier too.
    """
    if age_group not in AGE_GROUP_PARAMS:
        logger.warning(
            "Groupe d'age '%s' non trouve dans le mapping, utilisation de '9-11' par defaut",
            age_group,
        )

    final_age_group = age_group
    ai_difficulty = challenge_data.get("difficulty_rating")
    if isinstance(ai_difficulty, (int, float)):
        ai_d: Optional[float] = float(ai_difficulty)
    else:
        ai_d = None

    title = str(challenge_data.get("title", "") or "")
    vd_raw = challenge_data.get("visual_data", {})
    if isinstance(vd_raw, str):
        try:
            vd_raw = json.loads(vd_raw)
        except (json.JSONDecodeError, TypeError):
            vd_raw = {}
    vd = apply_visual_contract_normalization(
        challenge_type, vd_raw if isinstance(vd_raw, dict) else {}
    )

    final_difficulty, calibration_meta = calibrate_challenge_difficulty(
        challenge_type=challenge_type,
        age_group=final_age_group,
        visual_data=vd,
        title=title,
        ai_difficulty=ai_d,
        f42_rating_hint=f42_rating_hint,
    )

    raw_choices = challenge_data.get("choices")
    policy_choices = filter_choices_for_persistence(
        challenge_type, final_difficulty, raw_choices
    )
    choices_out = sanitize_choices_for_delivery(
        challenge_type,
        final_difficulty,
        policy_choices,
        str(challenge_data.get("correct_answer", "")),
    )
    if policy_choices and not choices_out:
        logger.info(
            "[ChallengeAI] choices_stripped_after_quality_check challenge_type={} difficulty_rating={}",
            challenge_type,
            final_difficulty,
        )
    response_mode = compute_response_mode(
        challenge_type, vd, final_difficulty, choices_out
    )

    return {
        "challenge_type": challenge_type,
        "age_group": final_age_group,
        "title": challenge_data.get("title", f"Défi {challenge_type}"),
        "description": challenge_data.get("description", ""),
        "question": challenge_data.get("question", ""),
        "correct_answer": str(challenge_data.get("correct_answer", "")),
        "solution_explanation": challenge_data.get("solution_explanation", ""),
        "hints": challenge_data.get("hints", []),
        "visual_data": vd,
        "difficulty_rating": final_difficulty,
        "difficulty_tier": difficulty_tier,
        "estimated_time_minutes": 10,
        "tags": "ai,generated,mathélogique",
        "choices": choices_out,
        "response_mode": response_mode,
        "difficulty_calibration": calibration_meta,
    }


def _build_ai_generation_parameters(
    *,
    challenge_type: str,
    age_group: str,
    model: str,
    difficulty_calibration: Any,
    response_mode: Optional[str] = None,
    f42_personalization: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """ParamÃ¨tres de gÃ©nÃ©ration persistÃ©s (JSON) â€” Ã©vite les clÃ©s ad hoc dans le handler."""
    gp: Dict[str, Any] = {
        "source": "ai",
        "challenge_type": challenge_type,
        "age_group": age_group,
        "model": model,
    }
    if difficulty_calibration is not None:
        gp["difficulty_calibration"] = difficulty_calibration
    if response_mode:
        gp["response_mode"] = response_mode
    if f42_personalization:
        gp["f42_personalization"] = f42_personalization
    return gp


def _persist_challenge_sync(
    normalized_challenge: Dict[str, Any],
    user_id: Optional[int],
    challenge_type: str,
    model: str = "unknown",
    f42_personalization: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    """
    Persiste un challenge gÃ©nÃ©rÃ© en base via sync_db_session.
    Retourne challenge_dict si succÃ¨s, None sinon.
    """
    with sync_db_session() as db:
        created_challenge = challenge_service.create_challenge(
            db=db,
            title=normalized_challenge["title"],
            description=normalized_challenge["description"],
            challenge_type=normalized_challenge["challenge_type"],
            age_group=normalized_challenge["age_group"],
            question=normalized_challenge.get("question"),
            correct_answer=normalized_challenge["correct_answer"],
            solution_explanation=normalized_challenge["solution_explanation"],
            hints=normalized_challenge.get("hints", []),
            visual_data=normalized_challenge.get("visual_data", {}),
            difficulty_rating=normalized_challenge.get("difficulty_rating", 3.0),
            estimated_time_minutes=normalized_challenge.get(
                "estimated_time_minutes", 10
            ),
            tags=normalized_challenge.get("tags", "ai,generated"),
            creator_id=user_id,
            choices=normalized_challenge.get("choices"),
            generation_parameters=_build_ai_generation_parameters(
                challenge_type=challenge_type,
                age_group=normalized_challenge["age_group"],
                model=model,
                difficulty_calibration=normalized_challenge.get(
                    "difficulty_calibration"
                ),
                response_mode=normalized_challenge.get("response_mode"),
                f42_personalization=f42_personalization,
            ),
        )
        if (
            created_challenge
            and hasattr(created_challenge, "title")
            and created_challenge.title
        ):
            return {
                "id": created_challenge.id,
                "title": created_challenge.title,
                "description": created_challenge.description,
                "challenge_type": (
                    str(created_challenge.challenge_type)
                    if hasattr(created_challenge.challenge_type, "value")
                    else created_challenge.challenge_type
                ),
                "age_group": normalize_age_group_for_frontend(
                    created_challenge.age_group
                ),
                "question": created_challenge.question,
                "correct_answer": created_challenge.correct_answer,
                "solution_explanation": created_challenge.solution_explanation,
                "hints": created_challenge.hints or [],
                "visual_data": created_challenge.visual_data or {},
                "difficulty_rating": created_challenge.difficulty_rating,
                "difficulty_tier": created_challenge.difficulty_tier,
                "estimated_time_minutes": created_challenge.estimated_time_minutes,
                "tags": created_challenge.tags,
                "is_active": created_challenge.is_active,
                "created_at": (
                    created_challenge.created_at.isoformat()
                    if created_challenge.created_at
                    else None
                ),
                "choices": created_challenge.choices or [],
                "response_mode": normalized_challenge.get("response_mode"),
            }
        return None


async def generate_challenge_stream(
    challenge_type: str,
    age_group: str,
    prompt: str,
    user_id: Optional[int],
    locale: str = "fr",
    *,
    personalization: Optional["ChallengeStreamPersonalizationMeta"] = None,
) -> AsyncGenerator[str, None]:
    """
    GÃ©nÃ©rateur async qui produit des Ã©vÃ©nements SSE (f"data: {json.dumps(...)}\n\n").
    """
    start_time = datetime.now()
    validation_passed = True
    auto_corrected = False
    usage_events_tracked = False

    try:

        def _record_generation_failure(
            *,
            error_type: str,
            validation_ok: bool = False,
            auto_corrected_flag: bool = False,
        ) -> None:
            duration = (datetime.now() - start_time).total_seconds()
            generation_metrics.record_generation(
                challenge_type=challenge_type,
                success=False,
                validation_passed=validation_ok,
                auto_corrected=auto_corrected_flag,
                duration_seconds=duration,
                error_type=error_type,
            )

        try:
            from openai import AsyncOpenAI
        except ImportError:
            yield sse_error_message("Bibliothèque OpenAI non installée")
            return

        if not settings.OPENAI_API_KEY:
            yield sse_error_message("OpenAI API key non configurée")
            return

        ai_params = AIConfig.get_openai_params(challenge_type)
        client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=ai_params["timeout"],
        )

        system_prompt = build_challenge_system_prompt(challenge_type, age_group)
        if personalization is not None:
            from app.services.challenges.challenge_generation_context import (
                build_personalization_prompt_section_from_meta,
            )

            system_prompt += "\n\n" + build_personalization_prompt_section_from_meta(
                personalization
            )
        user_prompt = build_challenge_user_prompt(
            challenge_type,
            age_group,
            prompt,
            locale=locale,
        )

        if AIConfig.is_o1_model(ai_params["model"]):
            system_prompt += "\n\nCRITIQUE : Retourne UNIQUEMENT un objet JSON valide, sans texte ou markdown avant/aprÃ¨s. Aucune explication hors du JSON."

        if not openai_workload_circuit_breaker.check_allow():
            _record_generation_failure(error_type="openai_circuit_open")
            yield sse_error_message(OPENAI_CIRCUIT_OPEN_USER_MESSAGE)
            return

        yield sse_status_message("Génération en cours...")

        @retry(
            stop=stop_after_attempt(AIConfig.MAX_RETRIES),
            wait=wait_exponential(
                multiplier=AIConfig.RETRY_BACKOFF_MULTIPLIER,
                min=AIConfig.RETRY_MIN_WAIT,
                max=AIConfig.RETRY_MAX_WAIT,
            ),
            retry=retry_if_exception_type((RateLimitError, APIError, APITimeoutError)),
            reraise=True,
        )
        async def create_stream_with_retry():
            use_o1 = AIConfig.is_o1_model(ai_params["model"])
            use_o3 = AIConfig.is_o3_model(ai_params["model"])
            api_kwargs = build_challenge_ai_stream_kwargs(
                model=ai_params["model"],
                system_content=system_prompt,
                user_content=user_prompt,
                ai_params=ai_params,
            )
            logger.info(
                "Appel API: model=%s, o1=%s, o3=%s, reasoning=%s",
                ai_params["model"],
                use_o1,
                use_o3,
                ai_params.get("reasoning_effort", "N/A"),
            )
            return await client.chat.completions.create(**api_kwargs)

        try:
            stream = await create_stream_with_retry()
        except (RateLimitError, APIError, APITimeoutError) as api_error:
            if is_countable_openai_failure(api_error):
                openai_workload_circuit_breaker.record_countable_failure()
            else:
                openai_workload_circuit_breaker.probe_finished_without_countable_outcome()
            logger.error(
                "Erreur API OpenAI aprÃ¨s %s tentatives: %s",
                AIConfig.MAX_RETRIES,
                api_error,
            )
            yield sse_error_message(
                get_safe_error_message(
                    api_error,
                    default=CHALLENGE_AI_TRANSIENT_ERROR_MESSAGE,
                )
            )
            return
        except Exception as unexpected_error:
            if is_countable_openai_failure(unexpected_error):
                openai_workload_circuit_breaker.record_countable_failure()
            else:
                openai_workload_circuit_breaker.probe_finished_without_countable_outcome()
            logger.error(
                "Erreur inattendue lors de la gÃ©nÃ©ration: %s", unexpected_error
            )
            yield sse_error_message(
                get_safe_error_message(
                    unexpected_error,
                    default=CHALLENGE_AI_GENERIC_ERROR_MESSAGE,
                )
            )
            return

        full_response = ""
        prompt_tokens_estimate = 0
        completion_tokens_estimate = 0
        prompt_length = len(system_prompt) + len(user_prompt)
        prompt_tokens_estimate = prompt_length // 4
        usage_events: list[Dict[str, Any]] = []

        def _queue_usage(
            *,
            model: str,
            prompt_tokens: int,
            completion_tokens: int,
        ) -> None:
            usage_events.append(
                {
                    "model": model,
                    "prompt_tokens": max(0, int(prompt_tokens)),
                    "completion_tokens": max(0, int(completion_tokens)),
                }
            )

        def _flush_usage_events() -> None:
            nonlocal usage_events_tracked
            if usage_events_tracked:
                return
            for usage_event in usage_events:
                usage_stats = token_tracker.track_usage(
                    challenge_type=challenge_type,
                    prompt_tokens=usage_event["prompt_tokens"],
                    completion_tokens=usage_event["completion_tokens"],
                    model=usage_event["model"],
                )
                logger.debug("Token usage tracked: %s", usage_stats)
            usage_events_tracked = True

        try:
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    completion_tokens_estimate = len(full_response) // 4
                if hasattr(chunk, "usage") and chunk.usage:
                    prompt_tokens_estimate = (
                        chunk.usage.prompt_tokens or prompt_tokens_estimate
                    )
                    completion_tokens_estimate = (
                        chunk.usage.completion_tokens or completion_tokens_estimate
                    )
        except (RateLimitError, APIError, APITimeoutError) as stream_api_error:
            if is_countable_openai_failure(stream_api_error):
                openai_workload_circuit_breaker.record_countable_failure()
            else:
                openai_workload_circuit_breaker.probe_finished_without_countable_outcome()
            logger.error(
                "Erreur API OpenAI pendant le stream dÃ©fis: %s", stream_api_error
            )
            yield sse_error_message(
                get_safe_error_message(
                    stream_api_error,
                    default=CHALLENGE_AI_TRANSIENT_ERROR_MESSAGE,
                )
            )
            return
        except Exception as stream_other:
            if is_countable_openai_failure(stream_other):
                openai_workload_circuit_breaker.record_countable_failure()
            else:
                openai_workload_circuit_breaker.probe_finished_without_countable_outcome()
            logger.error("Erreur inattendue pendant le stream dÃ©fis: %s", stream_other)
            yield sse_error_message(
                get_safe_error_message(
                    stream_other,
                    default=CHALLENGE_AI_GENERIC_ERROR_MESSAGE,
                )
            )
            return

        _queue_usage(
            model=ai_params["model"],
            prompt_tokens=prompt_tokens_estimate,
            completion_tokens=completion_tokens_estimate,
        )

        # Fallback si rÃ©ponse vide (o3)
        if not full_response.strip() and AIConfig.is_o3_model(ai_params["model"]):
            logger.warning(
                "RÃ©ponse vide de o3, fallback vers modÃ¨le sans raisonnement..."
            )
            fallback_model = resolve_challenge_ai_fallback_model(challenge_type)
            try:
                fallback_client = AsyncOpenAI(
                    api_key=settings.OPENAI_API_KEY,
                    timeout=ai_params.get("timeout", 120),
                )
                fallback_resp = await fallback_client.chat.completions.create(
                    model=fallback_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    response_format={"type": "json_object"},
                    max_tokens=ai_params["max_tokens"],
                    temperature=0.4,
                )
                fallback_prompt_tokens_estimate = prompt_length // 4
                fallback_completion_tokens_estimate = 0
                fallback_usage = getattr(fallback_resp, "usage", None)
                if fallback_usage is not None:
                    if getattr(fallback_usage, "prompt_tokens", None) is not None:
                        fallback_prompt_tokens_estimate = int(
                            fallback_usage.prompt_tokens
                        )
                    if getattr(fallback_usage, "completion_tokens", None) is not None:
                        fallback_completion_tokens_estimate = int(
                            fallback_usage.completion_tokens
                        )
                if fallback_resp.choices and fallback_resp.choices[0].message.content:
                    full_response = fallback_resp.choices[0].message.content
                    if fallback_completion_tokens_estimate == 0:
                        fallback_completion_tokens_estimate = len(full_response) // 4
                    logger.info(
                        "Fallback %s: %s caractÃ¨res reÃ§us",
                        fallback_model,
                        len(full_response),
                    )
                _queue_usage(
                    model=fallback_model,
                    prompt_tokens=fallback_prompt_tokens_estimate,
                    completion_tokens=fallback_completion_tokens_estimate,
                )
            except Exception as fb_err:
                if is_countable_openai_failure(fb_err):
                    openai_workload_circuit_breaker.record_countable_failure()
                    logger.error("Fallback Ã©chouÃ©: %s", fb_err)
                    yield sse_error_message(
                        get_safe_error_message(
                            fb_err,
                            default=CHALLENGE_AI_TRANSIENT_ERROR_MESSAGE,
                        )
                    )
                    return
                openai_workload_circuit_breaker.probe_finished_without_countable_outcome()
                logger.error("Fallback Ã©chouÃ©: %s", fb_err)

        openai_workload_circuit_breaker.record_success()

        logger.info(
            "RÃ©ponse reÃ§ue: %s caractÃ¨res, ~%s tokens estimÃ©s",
            len(full_response),
            len(full_response) // 4,
        )
        _flush_usage_events()

        try:
            challenge_data = extract_json_from_text(full_response)
        except json.JSONDecodeError as json_error:
            logger.error("Erreur de parsing JSON: %s", json_error)
            logger.debug("RÃ©ponse reÃ§ue: %s", full_response[:500])
            _record_generation_failure(error_type="json_decode_error")
            yield sse_error_message("Erreur lors du parsing de la réponse JSON")
            return

        if not challenge_data.get("title") or not challenge_data.get("description"):
            logger.error("DonnÃ©es de challenge incomplÃ¨tes: %s", challenge_data)
            _record_generation_failure(error_type="incomplete_generated_challenge")
            yield sse_error_message(
                "Les données générées sont incomplètes (titre ou description manquant)"
            )
            return

        challenge_data["challenge_type"] = challenge_type
        normalized_challenge = normalize_generated_challenge(
            challenge_data,
            challenge_type,
            age_group,
            f42_rating_hint=(
                personalization.target_difficulty_rating_hint
                if personalization is not None
                else None
            ),
            difficulty_tier=(
                personalization.resolved_target_tier
                if personalization is not None
                else None
            ),
        )

        if not normalized_challenge.get("title") or not normalized_challenge.get(
            "description"
        ):
            logger.error("Challenge normalisé invalide: %s", normalized_challenge)
            _record_generation_failure(error_type="normalized_challenge_invalid")
            yield sse_error_message("Erreur lors de la normalisation des données")
            return

        prevalidated_challenge = auto_correct_challenge(normalized_challenge)
        if prevalidated_challenge != normalized_challenge:
            auto_corrected = True
        challenge_data = prevalidated_challenge
        is_valid, validation_errors = validate_challenge_logic(challenge_data)

        if not is_valid:
            logger.warning(
                "Challenge généré avec erreurs de validation: {}", validation_errors
            )
            logger.info("Tentative de correction automatique...")
            corrected_challenge = auto_correct_challenge(challenge_data)
            is_valid_after_correction, remaining_errors = validate_challenge_logic(
                corrected_challenge
            )
            if is_valid_after_correction:
                logger.info("Correction automatique réussie")
                challenge_data = corrected_challenge
                auto_corrected = True
                validation_passed = True
            else:
                logger.error(
                    "Correction automatique impossible. Erreurs restantes: {}",
                    remaining_errors,
                )
                validation_passed = False
                _record_generation_failure(
                    error_type="validation_failed_after_autocorrect"
                )
                errors_str = ", ".join(remaining_errors[:5])
                yield sse_error_message(
                    "Le défi généré ne passe pas la validation finale "
                    f"(correction automatique impossible). Détail : {errors_str}"
                )
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
                return
        else:
            logger.debug("Challenge validÃ© avec succÃ¨s")
            validation_passed = True

        normalized_challenge = challenge_data

        try:
            pers_dump = (
                personalization.model_dump(exclude_none=True)
                if personalization is not None
                else None
            )
            challenge_dict = await run_db_bound(
                _persist_challenge_sync,
                normalized_challenge,
                user_id,
                challenge_type,
                ai_params.get("model", "unknown"),
                pers_dump,
            )
            if challenge_dict:
                duration = (datetime.now() - start_time).total_seconds()
                generation_metrics.record_generation(
                    challenge_type=challenge_type,
                    success=True,
                    validation_passed=validation_passed,
                    auto_corrected=auto_corrected,
                    duration_seconds=duration,
                )

                yield f"data: {json.dumps({'type': 'challenge', 'challenge': challenge_dict})}\n\n"
            else:
                logger.error("Challenge crÃ©Ã© mais invalide")
                _record_generation_failure(
                    error_type="challenge_persistence_missing_id",
                    validation_ok=validation_passed,
                    auto_corrected_flag=auto_corrected,
                )
                yield f"data: {json.dumps({'type': 'challenge', 'challenge': normalized_challenge, 'warning': 'Non sauvegardé en base'})}\n\n"
        except Exception as db_error:
            logger.error("Erreur lors de la sauvegarde du challenge: %s", db_error)
            logger.debug(traceback.format_exc())
            _record_generation_failure(
                error_type="challenge_persistence_error",
                validation_ok=validation_passed,
                auto_corrected_flag=auto_corrected,
            )
            if normalized_challenge.get("title"):
                yield f"data: {json.dumps({'type': 'challenge', 'challenge': normalized_challenge, 'warning': 'Non sauvegardé en base'})}\n\n"
            else:
                yield sse_error_message(
                    "Erreur lors de la sauvegarde et challenge invalide"
                )

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    except Exception as gen_error:
        logger.error("Erreur lors de la gÃ©nÃ©ration: %s", gen_error)
        logger.debug(traceback.format_exc())
        duration = (datetime.now() - start_time).total_seconds()
        generation_metrics.record_generation(
            challenge_type=challenge_type,
            success=False,
            validation_passed=False,
            duration_seconds=duration,
            error_type=type(gen_error).__name__,
        )
        yield sse_error_message(
            get_safe_error_message(
                gen_error,
                default=CHALLENGE_AI_GENERIC_ERROR_MESSAGE,
            )
        )
