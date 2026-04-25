"""
Service de gÃ©nÃ©ration de challenges par IA.
Extrait la logique de gÃ©nÃ©ration streaming depuis challenge_handlers.
"""

import json
import traceback
from datetime import datetime
from typing import TYPE_CHECKING, Any, AsyncGenerator, Dict, Literal, Optional

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
from app.services.challenges.challenge_validation_error_codes import (
    classify_challenge_validation_errors,
)
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
_CHESS_VALIDATION_REPAIR_MAX_TOKENS = 2500
_CHESS_VALIDATION_REPAIR_ERROR_MARKERS = (
    "roi noir déjà en échec",
    "roi blanc déjà en échec",
)
_OPENAI_INVALID_JSON_MARKERS = (
    "Model JSON is invalid",
    "check the stop reason",
)

# Statuts d'orchestration une fois validation / réparation résolus (Phase 1A).
ChallengePipelineGenerationStatus = Literal[
    "accepted", "repaired", "repaired_by_ai", "rejected"
]
CHALLENGE_GENERATION_STATUS_ACCEPTED: ChallengePipelineGenerationStatus = "accepted"
CHALLENGE_GENERATION_STATUS_REPAIRED: ChallengePipelineGenerationStatus = "repaired"
CHALLENGE_GENERATION_STATUS_REPAIRED_BY_AI: ChallengePipelineGenerationStatus = (
    "repaired_by_ai"
)
CHALLENGE_GENERATION_STATUS_REJECTED: ChallengePipelineGenerationStatus = "rejected"


def _resolve_challenge_pipeline_generation_status(
    *,
    validation_passed: bool,
    auto_corrected: bool,
    chess_repair_succeeded: bool,
) -> ChallengePipelineGenerationStatus:
    """A appeler lorsque le pipeline a tranché (validation OK ou rejet final)."""
    if not validation_passed:
        return CHALLENGE_GENERATION_STATUS_REJECTED
    if chess_repair_succeeded:
        return CHALLENGE_GENERATION_STATUS_REPAIRED_BY_AI
    if auto_corrected:
        return CHALLENGE_GENERATION_STATUS_REPAIRED
    return CHALLENGE_GENERATION_STATUS_ACCEPTED


def _extract_complete_challenge_json(full_response: str) -> Dict[str, Any]:
    """Parse uniquement une réponse JSON complète, sans auto-réparer un flux tronqué."""
    if any(marker in full_response for marker in _OPENAI_INVALID_JSON_MARKERS):
        raise json.JSONDecodeError(
            "Réponse OpenAI JSON explicitement invalide ou tronquée",
            full_response,
            0,
        )
    start = full_response.find("{")
    end = full_response.rfind("}")
    if start == -1 or end <= start:
        raise json.JSONDecodeError("Objet JSON incomplet", full_response, max(start, 0))
    return extract_json_from_text(full_response)


def _should_attempt_chess_validation_repair(
    challenge_type: str, validation_errors: list[str]
) -> bool:
    """Autorise une réparation IA bornée pour les positions d'échecs illégales."""
    if (challenge_type or "").strip().lower() != "chess":
        return False
    return any(
        marker in error
        for error in validation_errors
        for marker in _CHESS_VALIDATION_REPAIR_ERROR_MARKERS
    )


def _build_chess_validation_repair_prompt(
    challenge_data: Dict[str, Any],
    validation_errors: list[str],
    *,
    locale: str = "fr",
) -> str:
    """Construit un prompt compact de réparation pour un JSON chess invalide."""
    language_instruction = (
        "Rédige les champs visibles en français."
        if (locale or "fr").lower().startswith("fr")
        else "Keep visible fields in the interface language."
    )
    payload = json.dumps(challenge_data, ensure_ascii=False, indent=2)
    errors = "\n".join(f"- {err}" for err in validation_errors)
    return (
        "Corrige ce défi d'échecs JSON sans ajouter de texte hors JSON.\n"
        f"{language_instruction}\n"
        "Erreurs de validation à corriger :\n"
        f"{errors}\n\n"
        "Contraintes non négociables :\n"
        "- Conserve challenge_type=CHESS/chess et un visual_data.board 8x8.\n"
        "- Utilise seulement K,Q,R,B,N,P / k,q,r,b,n,p dans board.\n"
        "- Position tactique courte : 4 à 8 pièces, exactement un roi blanc et un roi noir.\n"
        "- Si turn=white, le roi noir ne doit pas déjà être attaqué avant le coup blanc.\n"
        "- Si turn=black, le roi blanc ne doit pas déjà être attaqué avant le coup noir.\n"
        "- Recalcule correct_answer et solution_explanation pour être cohérents avec le board corrigé.\n"
        "- Pour mat_en_1 : correct_answer = un seul coup mat.\n"
        "- Pour mat_en_2 : correct_answer = ligne complète coup actif, réponse forcée, coup mat.\n"
        "- Ne mets jamais de choices pour chess.\n\n"
        "JSON à corriger :\n"
        f"{payload}"
    )


async def _repair_chess_validation_failure_with_openai(
    *,
    client: AsyncOpenAI,
    challenge_type: str,
    age_group: str,
    locale: str,
    ai_params: Dict[str, Any],
    challenge_data: Dict[str, Any],
    validation_errors: list[str],
    personalization: Optional["ChallengeStreamPersonalizationMeta"],
) -> tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """Tente une réparation non-stream, uniquement après échec structurel CHESS."""
    fallback_model = resolve_challenge_ai_fallback_model(challenge_type)
    repair_prompt = _build_chess_validation_repair_prompt(
        challenge_data,
        validation_errors,
        locale=locale,
    )
    response = await client.chat.completions.create(
        model=fallback_model,
        messages=[
            {
                "role": "system",
                "content": (
                    "Tu es un validateur/correcteur JSON pour des défis d'échecs. "
                    "Retourne uniquement un objet JSON valide."
                ),
            },
            {"role": "user", "content": repair_prompt},
        ],
        response_format={"type": "json_object"},
        max_tokens=min(
            int(ai_params.get("max_tokens", _CHESS_VALIDATION_REPAIR_MAX_TOKENS)),
            _CHESS_VALIDATION_REPAIR_MAX_TOKENS,
        ),
        temperature=0.2,
    )

    content = ""
    if response.choices and response.choices[0].message.content:
        content = response.choices[0].message.content
    if not content.strip():
        return None, None

    repaired_raw = _extract_complete_challenge_json(content)
    repaired_raw["challenge_type"] = challenge_type
    repaired = normalize_generated_challenge(
        repaired_raw,
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
    repaired = auto_correct_challenge(repaired)

    usage = getattr(response, "usage", None)
    usage_event: Optional[Dict[str, Any]] = None
    if usage is not None:
        usage_event = {
            "model": fallback_model,
            "prompt_tokens": int(getattr(usage, "prompt_tokens", 0) or 0),
            "completion_tokens": int(getattr(usage, "completion_tokens", 0) or 0),
        }
    return repaired, usage_event


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
            "Groupe d'âge '{}' non trouvé dans le mapping, utilisation de '9-11' par défaut",
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
            difficulty_tier=normalized_challenge.get("difficulty_tier"),
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
    chess_repair_succeeded = False
    chess_repair: str = "none"
    usage_events_tracked = False

    try:

        def _record_generation_failure(
            *,
            error_type: str,
            validation_ok: bool = False,
            auto_corrected_flag: bool = False,
            generation_status: Optional[ChallengePipelineGenerationStatus] = None,
            error_codes: Optional[list[str]] = None,
        ) -> None:
            duration = (datetime.now() - start_time).total_seconds()
            generation_metrics.record_generation(
                challenge_type=challenge_type,
                success=False,
                validation_passed=validation_ok,
                auto_corrected=auto_corrected_flag,
                duration_seconds=duration,
                error_type=error_type,
                generation_status=generation_status,
                error_codes=error_codes,
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
        max_retries = AIConfig.get_max_retries(challenge_type)

        @retry(
            stop=stop_after_attempt(max_retries),
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
            use_o_series = AIConfig.is_o_series_reasoning_model(ai_params["model"])
            api_kwargs = build_challenge_ai_stream_kwargs(
                model=ai_params["model"],
                system_content=system_prompt,
                user_content=user_prompt,
                ai_params=ai_params,
            )
            logger.info(
                "Appel API: model={}, o1={}, o_series={}, reasoning={}",
                ai_params["model"],
                use_o1,
                use_o_series,
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
                "Erreur API OpenAI aprÃ¨s {} tentatives: {}",
                max_retries,
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
                "Erreur inattendue lors de la gÃ©nÃ©ration: {}", unexpected_error
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
        reasoning_tokens_observed: Optional[int] = None
        finish_reason_observed: Optional[str] = None
        prompt_length = len(system_prompt) + len(user_prompt)
        prompt_tokens_estimate = prompt_length // 4
        usage_events: list[Dict[str, Any]] = []

        def _queue_usage(
            *,
            model: str,
            prompt_tokens: int,
            completion_tokens: int,
        ) -> None:
            usage_event = {
                "model": model,
                "prompt_tokens": max(0, int(prompt_tokens)),
                "completion_tokens": max(0, int(completion_tokens)),
            }
            if usage_events_tracked:
                usage_stats = token_tracker.track_usage(
                    challenge_type=challenge_type,
                    prompt_tokens=usage_event["prompt_tokens"],
                    completion_tokens=usage_event["completion_tokens"],
                    model=usage_event["model"],
                )
                logger.debug("Token usage tracked: {}", usage_stats)
                return
            usage_events.append(usage_event)

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
                logger.debug("Token usage tracked: {}", usage_stats)
            usage_events_tracked = True

        try:
            async for chunk in stream:
                if chunk.choices:
                    choice = chunk.choices[0]
                    if choice.finish_reason:
                        finish_reason_observed = choice.finish_reason
                    if choice.delta.content:
                        content = choice.delta.content
                        full_response += content
                        completion_tokens_estimate = len(full_response) // 4
                if hasattr(chunk, "usage") and chunk.usage:
                    prompt_tokens_estimate = (
                        chunk.usage.prompt_tokens or prompt_tokens_estimate
                    )
                    completion_tokens_estimate = (
                        chunk.usage.completion_tokens or completion_tokens_estimate
                    )
                    completion_details = getattr(
                        chunk.usage, "completion_tokens_details", None
                    )
                    reasoning_tokens = getattr(
                        completion_details, "reasoning_tokens", None
                    )
                    if reasoning_tokens is not None:
                        reasoning_tokens_observed = int(reasoning_tokens)
        except (RateLimitError, APIError, APITimeoutError) as stream_api_error:
            if is_countable_openai_failure(stream_api_error):
                openai_workload_circuit_breaker.record_countable_failure()
            else:
                openai_workload_circuit_breaker.probe_finished_without_countable_outcome()
            logger.error(
                "Erreur API OpenAI pendant le stream dÃ©fis: {}", stream_api_error
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
            logger.error("Erreur inattendue pendant le stream dÃ©fis: {}", stream_other)
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

        # Fallback si réponse vide OU tronquée par limite de tokens (o-series).
        # ``finish_reason == "length"`` signifie que o-series a dépensé tout son
        # budget (sortie + reasoning caché) sans fermer le JSON. Une re-tentative
        # non stream sur un modèle chat classique a un budget entièrement visible,
        # donc une très forte probabilité d'aboutir à un JSON complet.
        is_o_series_model = AIConfig.is_o_series_reasoning_model(ai_params["model"])
        fallback_trigger_reason: Optional[str] = None
        if is_o_series_model:
            if not full_response.strip():
                fallback_trigger_reason = "empty_response"
            elif finish_reason_observed == "length":
                fallback_trigger_reason = "length_truncation"
        if fallback_trigger_reason is not None:
            logger.warning(
                "Fallback o-series déclenché (raison={}), modèle={}, type={}, "
                "completion_tokens={}, reasoning_tokens={}, max_completion_tokens={}",
                fallback_trigger_reason,
                ai_params["model"],
                challenge_type,
                completion_tokens_estimate,
                reasoning_tokens_observed,
                ai_params["max_tokens"],
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
                fallback_msg = None
                if fallback_resp.choices and fallback_resp.choices[0].message:
                    fallback_msg = fallback_resp.choices[0].message.content
                has_fallback_body = bool(str(fallback_msg or "").strip())
                if has_fallback_body:
                    full_response = str(fallback_msg).strip()
                    if fallback_completion_tokens_estimate == 0:
                        fallback_completion_tokens_estimate = len(full_response) // 4
                    logger.info(
                        "Fallback {}: {} caractÃ¨res reÃ§us",
                        fallback_model,
                        len(full_response),
                    )
                    _queue_usage(
                        model=fallback_model,
                        prompt_tokens=fallback_prompt_tokens_estimate,
                        completion_tokens=fallback_completion_tokens_estimate,
                    )
                else:
                    if fallback_usage is not None:
                        fb_pt = int(getattr(fallback_usage, "prompt_tokens", 0) or 0)
                        fb_ct = int(
                            getattr(fallback_usage, "completion_tokens", 0) or 0
                        )
                        if fb_pt > 0 or fb_ct > 0:
                            _queue_usage(
                                model=fallback_model,
                                prompt_tokens=fb_pt,
                                completion_tokens=fb_ct,
                            )
                    _flush_usage_events()
                    openai_workload_circuit_breaker.probe_finished_without_countable_outcome()
                    _record_generation_failure(
                        error_type="fallback_empty_response",
                    )
                    yield sse_error_message(CHALLENGE_AI_GENERIC_ERROR_MESSAGE)
                    return
            except Exception as fb_err:
                if is_countable_openai_failure(fb_err):
                    openai_workload_circuit_breaker.record_countable_failure()
                    logger.error("Fallback Ã©chouÃ©: {}", fb_err)
                    _flush_usage_events()
                    yield sse_error_message(
                        get_safe_error_message(
                            fb_err,
                            default=CHALLENGE_AI_TRANSIENT_ERROR_MESSAGE,
                        )
                    )
                    return
                openai_workload_circuit_breaker.probe_finished_without_countable_outcome()
                logger.error("Fallback Ã©chouÃ©: {}", fb_err)
                _flush_usage_events()
                yield sse_error_message(
                    get_safe_error_message(
                        fb_err,
                        default=CHALLENGE_AI_GENERIC_ERROR_MESSAGE,
                    )
                )
                return

        openai_workload_circuit_breaker.record_success()

        logger.info(
            "RÃ©ponse reÃ§ue: {} caractÃ¨res, ~{} tokens estimÃ©s",
            len(full_response),
            len(full_response) // 4,
        )
        logger.info(
            "Challenge OpenAI usage: model={}, type={}, reasoning={}, "
            "finish_reason={}, prompt_tokens={}, completion_tokens={}, "
            "reasoning_tokens={}, max_completion_tokens={}",
            ai_params["model"],
            challenge_type,
            ai_params.get("reasoning_effort", "N/A"),
            finish_reason_observed or "unknown",
            prompt_tokens_estimate,
            completion_tokens_estimate,
            reasoning_tokens_observed,
            ai_params["max_tokens"],
        )
        if finish_reason_observed == "length":
            logger.warning(
                "Challenge generation stopped by token limit: model={}, type={}, "
                "reasoning={}, completion_tokens={}, reasoning_tokens={}, "
                "max_completion_tokens={}",
                ai_params["model"],
                challenge_type,
                ai_params.get("reasoning_effort", "N/A"),
                completion_tokens_estimate,
                reasoning_tokens_observed,
                ai_params["max_tokens"],
            )
        _flush_usage_events()

        try:
            challenge_data = _extract_complete_challenge_json(full_response)
        except json.JSONDecodeError as json_error:
            logger.error("Erreur de parsing JSON: {}", json_error)
            logger.debug("RÃ©ponse reÃ§ue: {}", full_response[:500])
            _record_generation_failure(
                error_type=(
                    "json_truncated"
                    if finish_reason_observed == "length"
                    else "json_decode_error"
                )
            )
            yield sse_error_message("Erreur lors du parsing de la réponse JSON")
            return

        if not challenge_data.get("title") or not challenge_data.get("description"):
            logger.error("DonnÃ©es de challenge incomplÃ¨tes: {}", challenge_data)
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
            logger.error("Challenge normalisé invalide: {}", normalized_challenge)
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
            logger.info(
                "Challenge toujours invalide après auto-correction générique; "
                "erreurs: {}",
                validation_errors,
            )
            validation_passed = False
            remaining_errors = list(validation_errors)
            if _should_attempt_chess_validation_repair(
                challenge_type, remaining_errors
            ):
                logger.info("Tentative de réparation IA ciblée CHESS...")
                chess_repair = "chess_ai_attempted"
                repaired_challenge: Optional[Dict[str, Any]] = None
                repair_error: Optional[Exception] = None
                try:
                    repaired_challenge, repair_usage = (
                        await _repair_chess_validation_failure_with_openai(
                            client=client,
                            challenge_type=challenge_type,
                            age_group=age_group,
                            locale=locale,
                            ai_params=ai_params,
                            challenge_data=challenge_data,
                            validation_errors=remaining_errors,
                            personalization=personalization,
                        )
                    )
                    if repair_usage is not None:
                        _queue_usage(**repair_usage)
                except Exception as caught_repair:
                    repair_error = caught_repair
                    logger.warning("Réparation IA CHESS échouée: {}", caught_repair)

                if repair_error is not None:
                    chess_repair = "chess_ai_failed"
                elif repaired_challenge is None:
                    chess_repair = "chess_ai_attempted"
                else:
                    is_valid_after_repair, repair_errors = validate_challenge_logic(
                        repaired_challenge
                    )
                    if is_valid_after_repair:
                        logger.info("Réparation IA CHESS réussie")
                        challenge_data = repaired_challenge
                        auto_corrected = True
                        chess_repair_succeeded = True
                        validation_passed = True
                        chess_repair = "chess_ai_succeeded"
                    else:
                        remaining_errors = repair_errors
                        chess_repair = "chess_ai_failed"

            if not validation_passed:
                logger.error(
                    "Correction automatique impossible. Erreurs restantes: {}",
                    remaining_errors,
                )
                error_codes = classify_challenge_validation_errors(
                    remaining_errors, challenge_type
                )
                logger.info(
                    "Challenge pipeline resolved: status={}, type={}, "
                    "validation_passed={}, auto_corrected={}, error_codes={}, "
                    "repair={}",
                    CHALLENGE_GENERATION_STATUS_REJECTED,
                    challenge_type,
                    validation_passed,
                    auto_corrected,
                    error_codes,
                    chess_repair,
                )
                _record_generation_failure(
                    error_type="validation_failed_after_autocorrect",
                    validation_ok=validation_passed,
                    auto_corrected_flag=auto_corrected,
                    generation_status=CHALLENGE_GENERATION_STATUS_REJECTED,
                    error_codes=error_codes,
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

        pipeline_generation_status = _resolve_challenge_pipeline_generation_status(
            validation_passed=validation_passed,
            auto_corrected=auto_corrected,
            chess_repair_succeeded=chess_repair_succeeded,
        )
        if chess_repair_succeeded:
            repair_for_log: str = "chess_ai_succeeded"
        else:
            repair_for_log = "none"
        logger.info(
            "Challenge pipeline resolved: status={}, type={}, "
            "validation_passed={}, auto_corrected={}, error_codes={}, "
            "repair={}",
            pipeline_generation_status,
            challenge_type,
            validation_passed,
            auto_corrected,
            [],
            repair_for_log,
        )

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
                    generation_status=pipeline_generation_status,
                )

                yield f"data: {json.dumps({'type': 'challenge', 'challenge': challenge_dict})}\n\n"
            else:
                logger.error("Challenge crÃ©Ã© mais invalide")
                _record_generation_failure(
                    error_type="challenge_persistence_missing_id",
                    validation_ok=validation_passed,
                    auto_corrected_flag=auto_corrected,
                    generation_status=pipeline_generation_status,
                )
                yield f"data: {json.dumps({'type': 'challenge', 'challenge': normalized_challenge, 'warning': 'Non sauvegardé en base'})}\n\n"
        except Exception as db_error:
            logger.error("Erreur lors de la sauvegarde du challenge: {}", db_error)
            logger.debug(traceback.format_exc())
            _record_generation_failure(
                error_type="challenge_persistence_error",
                validation_ok=validation_passed,
                auto_corrected_flag=auto_corrected,
                generation_status=pipeline_generation_status,
            )
            if normalized_challenge.get("title"):
                yield f"data: {json.dumps({'type': 'challenge', 'challenge': normalized_challenge, 'warning': 'Non sauvegardé en base'})}\n\n"
            else:
                yield sse_error_message(
                    "Erreur lors de la sauvegarde et challenge invalide"
                )

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    except Exception as gen_error:
        logger.error("Erreur lors de la gÃ©nÃ©ration: {}", gen_error)
        logger.debug(traceback.format_exc())
        duration = (datetime.now() - start_time).total_seconds()
        generation_metrics.record_generation(
            challenge_type=challenge_type,
            success=False,
            validation_passed=False,
            duration_seconds=duration,
            error_type=type(gen_error).__name__,
            generation_status=None,
        )
        yield sse_error_message(
            get_safe_error_message(
                gen_error,
                default=CHALLENGE_AI_GENERIC_ERROR_MESSAGE,
            )
        )
        yield f"data: {json.dumps({'type': 'done'})}\n\n"
