"""
Handlers pour le chatbot utilisant OpenAI
Optimisé avec streaming SSE, smart routing, et best practices AI modernes
"""

import json
from datetime import datetime

from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse

from app.core.config import settings
from app.core.logging_config import get_logger

try:
    from openai import AsyncOpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    AsyncOpenAI = None  # type: ignore[assignment,misc]
from app.services.communication.chat_service import (
    assistant_chat_metrics_key,
    build_chat_config,
    build_openai_chat_completion_kwargs,
    cleanup_markdown_images,
    detect_image_request,
    extract_chat_usage_estimate,
    generate_image,
    generation_duration_seconds,
)
from app.utils.error_handler import api_error_response, get_safe_error_message
from app.utils.generation_metrics import generation_metrics
from app.utils.rate_limit import rate_limit_chat
from app.utils.request_utils import parse_json_body, parse_json_body_any
from app.utils.token_tracker import token_tracker

logger = get_logger(__name__)


@rate_limit_chat
async def chat_api(request: Request) -> JSONResponse:
    """
    Endpoint API pour le chatbot

    Utilise OpenAI pour répondre aux questions sur Mathakine
    """
    started_at = datetime.now()
    metrics_key = "assistant_chat"
    try:
        if not OPENAI_AVAILABLE:
            return api_error_response(503, "OpenAI non disponible")

        if not settings.OPENAI_API_KEY:
            return api_error_response(503, "Clé API OpenAI non configurée")

        data_or_err = await parse_json_body(
            request,
            required={"message": "Message requis"},
            optional={"conversation_history": []},
        )
        if isinstance(data_or_err, JSONResponse):
            return data_or_err
        message_raw = data_or_err["message"]
        conversation_history = data_or_err.get("conversation_history", [])[:20]

        from app.utils.prompt_sanitizer import (
            sanitize_user_prompt,
            validate_prompt_safety,
        )

        is_safe, safety_reason = validate_prompt_safety(message_raw)
        if not is_safe:
            return api_error_response(400, f"Message invalide: {safety_reason}")
        message = sanitize_user_prompt(message_raw, max_length=2000)

        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        is_image_req, is_math = detect_image_request(message)
        image_url = None
        if is_image_req and is_math:
            image_url = await generate_image(client, message)

        cfg = build_chat_config(message, conversation_history)
        metrics_key = assistant_chat_metrics_key(str(cfg.get("complexity")))
        completion_kw = build_openai_chat_completion_kwargs(cfg, stream=False)

        response = await client.chat.completions.create(**completion_kw)

        assistant_message = cleanup_markdown_images(response.choices[0].message.content)
        prompt_tokens, completion_tokens = extract_chat_usage_estimate(
            response,
            messages=cfg["messages"],
            completion_text=assistant_message,
        )
        token_tracker.track_usage(
            challenge_type=metrics_key,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            model=cfg["model"],
        )
        generation_metrics.record_generation(
            challenge_type=metrics_key,
            success=True,
            validation_passed=True,
            duration_seconds=generation_duration_seconds(started_at),
        )

        response_data = {
            "response": assistant_message,
            "model_used": cfg["model"],
            "complexity": cfg["complexity"],
        }

        if image_url:
            response_data["image_url"] = image_url
            response_data["type"] = "image"

        return JSONResponse(response_data)

    except Exception as chat_api_error:
        logger.error(f"Erreur dans chat_api: {str(chat_api_error)}", exc_info=True)
        generation_metrics.record_generation(
            challenge_type=metrics_key,
            success=False,
            validation_passed=False,
            duration_seconds=generation_duration_seconds(started_at),
            error_type=type(chat_api_error).__name__,
        )
        return api_error_response(500, get_safe_error_message(chat_api_error))


@rate_limit_chat
async def chat_api_stream(request: Request) -> Response:
    """
    Endpoint API pour le chatbot avec streaming SSE.

    Streaming pour meilleure UX — l'utilisateur voit la réponse
    apparaître progressivement au lieu d'attendre la réponse complète.
    """
    started_at = datetime.now()
    metrics_key = "assistant_chat"
    try:
        if not OPENAI_AVAILABLE:
            return _sse_error("OpenAI non disponible")

        if not settings.OPENAI_API_KEY:
            return _sse_error("Clé API OpenAI non configurée")

        data_or_err = await parse_json_body_any(request)
        if isinstance(data_or_err, JSONResponse):
            return data_or_err
        message_raw = data_or_err.get("message", "")
        conversation_history = data_or_err.get("conversation_history", [])[:20]

        if not message_raw:
            return _sse_error("Message requis")

        from app.utils.prompt_sanitizer import (
            sanitize_user_prompt,
            validate_prompt_safety,
        )

        is_safe, safety_reason = validate_prompt_safety(message_raw)
        if not is_safe:
            return _sse_error(f"Message invalide: {safety_reason}")
        message = sanitize_user_prompt(message_raw, max_length=2000)

        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        is_image_req, is_math = detect_image_request(message)
        image_url = None
        if is_image_req and is_math:
            image_url = await generate_image(client, message)

        cfg = build_chat_config(message, conversation_history)
        metrics_key = assistant_chat_metrics_key(str(cfg.get("complexity")))

        async def generate_stream():
            try:
                full_response = ""
                if image_url:
                    yield f"data: {json.dumps({'type': 'image', 'url': image_url})}\n\n"

                yield f"data: {json.dumps({'type': 'status', 'message': 'Réflexion en cours...'})}\n\n"

                stream_kw = build_openai_chat_completion_kwargs(cfg, stream=True)
                stream = await client.chat.completions.create(**stream_kw)

                async for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        full_response += content
                        yield f"data: {json.dumps({'type': 'chunk', 'content': content})}\n\n"

                prompt_tokens, completion_tokens = extract_chat_usage_estimate(
                    None,
                    messages=cfg["messages"],
                    completion_text=full_response,
                )
                token_tracker.track_usage(
                    challenge_type=metrics_key,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    model=cfg["model"],
                )
                generation_metrics.record_generation(
                    challenge_type=metrics_key,
                    success=True,
                    validation_passed=True,
                    duration_seconds=generation_duration_seconds(started_at),
                )
                yield f"data: {json.dumps({'type': 'done', 'model_used': cfg['model'], 'complexity': cfg['complexity']})}\n\n"

            except Exception as stream_generation_error:
                logger.error(f"Erreur dans generate_stream: {stream_generation_error}")
                generation_metrics.record_generation(
                    challenge_type=metrics_key,
                    success=False,
                    validation_passed=False,
                    duration_seconds=generation_duration_seconds(started_at),
                    error_type=type(stream_generation_error).__name__,
                )
                yield f"data: {json.dumps({'type': 'error', 'message': get_safe_error_message(stream_generation_error)})}\n\n"

        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    except Exception as chat_stream_error:
        logger.error(f"Erreur dans chat_api_stream: {chat_stream_error}", exc_info=True)
        generation_metrics.record_generation(
            challenge_type=metrics_key,
            success=False,
            validation_passed=False,
            duration_seconds=generation_duration_seconds(started_at),
            error_type=type(chat_stream_error).__name__,
        )
        return _sse_error(get_safe_error_message(chat_stream_error))


def _sse_error(message: str) -> StreamingResponse:
    """Retourne une erreur SSE formatée."""

    async def _gen():
        yield f"data: {json.dumps({'type': 'error', 'message': message})}\n\n"

    return StreamingResponse(
        _gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )
