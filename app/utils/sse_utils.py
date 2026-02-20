"""
Utilitaires SSE (Server-Sent Events) — DRY pour génération IA en streaming.
"""
import json
from typing import AsyncGenerator

from starlette.responses import StreamingResponse


SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
}


async def sse_error_generator(message: str) -> AsyncGenerator[str, None]:
    """Générateur async SSE pour envoyer une erreur."""
    yield f"data: {json.dumps({'type': 'error', 'message': message})}\n\n"


def sse_error_response(message: str, extra_headers: dict | None = None) -> StreamingResponse:
    """Retourne une StreamingResponse SSE avec un message d'erreur."""
    headers = dict(SSE_HEADERS)
    if extra_headers:
        headers.update(extra_headers)
    return StreamingResponse(
        sse_error_generator(message),
        media_type="text/event-stream",
        headers=headers,
    )


def sse_status_message(message: str) -> str:
    """Formate un événement SSE de statut (string à yield)."""
    return f"data: {json.dumps({'type': 'status', 'message': message})}\n\n"


def sse_error_message(message: str) -> str:
    """Formate un événement SSE d'erreur (string à yield)."""
    return f"data: {json.dumps({'type': 'error', 'message': message})}\n\n"
