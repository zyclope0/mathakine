"""
Handlers API pour le diagnostic adaptatif initial — F03.

Endpoints :
  GET  /api/diagnostic/status   — état du diagnostic (complété ou non)
  POST /api/diagnostic/start    — crée une session vierge
  POST /api/diagnostic/question — génère la prochaine question depuis l'état de session
  POST /api/diagnostic/answer   — soumet une réponse, retourne état mis à jour + feedback
  POST /api/diagnostic/complete — finalise la session, persiste DiagnosticResult

Design stateless : l'état de session (dict JSON) transite dans le corps de la requête.
Le backend ne conserve rien entre les appels jusqu'à /complete — seule la table
diagnostic_results est écrite à la fin.
"""

import json
import time
from typing import Any, Dict, Optional

from starlette.requests import Request
from starlette.responses import JSONResponse

import app.services.diagnostic_service as diagnostic_svc
from app.core.logging_config import get_logger
from app.utils.db_utils import db_session
from server.auth import require_auth

logger = get_logger(__name__)


# --------------------------------------------------------------------------- #
# Helpers internes                                                              #
# --------------------------------------------------------------------------- #


async def _parse_json(request: Request) -> Optional[Dict[str, Any]]:
    """Parse le corps JSON de la requête avec gestion d'erreur."""
    try:
        body = await request.body()
        if not body:
            return {}
        return json.loads(body)
    except (json.JSONDecodeError, ValueError) as exc:
        logger.warning(f"Corps JSON invalide: {exc}")
        return None


def _session_error(msg: str, status_code: int = 400) -> JSONResponse:
    return JSONResponse({"error": msg}, status_code=status_code)


# --------------------------------------------------------------------------- #
# GET /api/diagnostic/status                                                   #
# --------------------------------------------------------------------------- #


@require_auth
async def get_diagnostic_status(request: Request) -> JSONResponse:
    """
    Retourne l'état du diagnostic pour l'utilisateur connecté.

    Réponse :
    {
        "has_completed": bool,
        "latest": {   // null si jamais fait
            "id": int,
            "completed_at": "ISO",
            "triggered_from": "onboarding"|"settings",
            "questions_asked": int,
            "duration_seconds": int|null,
            "scores": { "addition": {"level": 2, "difficulty": "CHEVALIER", ...}, ... }
        }
    }
    """
    user = request.state.user
    async with db_session() as db:
        latest = diagnostic_svc.get_latest_score(db, user["id"])
    return JSONResponse(
        {
            "has_completed": latest is not None,
            "latest": latest,
        }
    )


# --------------------------------------------------------------------------- #
# POST /api/diagnostic/start                                                   #
# --------------------------------------------------------------------------- #


@require_auth
async def start_diagnostic(request: Request) -> JSONResponse:
    """
    Crée et retourne une session de diagnostic vierge.

    Corps (optionnel) :
    { "triggered_from": "onboarding" | "settings" }

    Réponse :
    {
        "session": { ...état initial... },
        "started_at_ts": float   // timestamp pour mesurer la durée côté frontend
    }
    """
    body = await _parse_json(request)
    if body is None:
        return _session_error("Corps JSON invalide")

    triggered_from = body.get("triggered_from", "onboarding")
    if triggered_from not in ("onboarding", "settings"):
        triggered_from = "onboarding"

    session = diagnostic_svc.create_session(triggered_from)
    return JSONResponse(
        {
            "session": session,
            "started_at_ts": time.time(),
        }
    )


# --------------------------------------------------------------------------- #
# POST /api/diagnostic/question                                                #
# --------------------------------------------------------------------------- #


@require_auth
async def get_next_question(request: Request) -> JSONResponse:
    """
    Génère la prochaine question du diagnostic depuis l'état de session courant.

    Corps :
    { "session": { ...état de session... } }

    Réponse si question disponible (HTTP 200) :
    {
        "done": false,
        "question": {
            "exercise_type": str,
            "difficulty": str,
            "level_ordinal": int,
            "question": str,          // texte LaTeX/Markdown
            "choices": [str, str, str, str],
            "correct_answer": str,
            "explanation": str,
            "hint": str,
            "question_number": int,
            "max_questions": int,
            "types_remaining": int
        }
    }

    Réponse si session terminée (HTTP 200) :
    { "done": true }
    """
    body = await _parse_json(request)
    if body is None:
        return _session_error("Corps JSON invalide")

    session = body.get("session")
    if not session or not isinstance(session, dict):
        return _session_error("Champ 'session' manquant ou invalide")

    if diagnostic_svc.is_session_complete(session):
        return JSONResponse({"done": True})

    question = diagnostic_svc.generate_question(session)
    if question is None:
        return JSONResponse({"done": True})

    return JSONResponse({"done": False, "question": question})


# --------------------------------------------------------------------------- #
# POST /api/diagnostic/answer                                                  #
# --------------------------------------------------------------------------- #


@require_auth
async def submit_diagnostic_answer(request: Request) -> JSONResponse:
    """
    Soumet la réponse de l'utilisateur pour une question et met à jour la session.

    Corps :
    {
        "session": { ...état de session... },
        "exercise_type": str,      // type de la question répondue
        "user_answer": str,        // réponse choisie par l'utilisateur
        "correct_answer": str      // bonne réponse (passée depuis le frontend)
    }

    Réponse :
    {
        "is_correct": bool,
        "session": { ...état mis à jour... },
        "session_complete": bool
    }

    Note : correct_answer est fourni par le frontend (non stocké en DB).
    Le backend ne revalide pas — l'évaluation finale est en /complete.
    """
    body = await _parse_json(request)
    if body is None:
        return _session_error("Corps JSON invalide")

    session = body.get("session")
    exercise_type = body.get("exercise_type")
    user_answer = body.get("user_answer", "")
    correct_answer = body.get("correct_answer", "")

    if not session or not isinstance(session, dict):
        return _session_error("Champ 'session' manquant ou invalide")
    if not exercise_type:
        return _session_error("Champ 'exercise_type' manquant")

    # Normaliser la comparaison (strip, casse insensible)
    is_correct = str(user_answer).strip().lower() == str(correct_answer).strip().lower()

    # Mettre à jour l'état IRT
    diagnostic_svc._apply_answer(session, exercise_type, is_correct)

    return JSONResponse(
        {
            "is_correct": is_correct,
            "session": session,
            "session_complete": diagnostic_svc.is_session_complete(session),
        }
    )


# --------------------------------------------------------------------------- #
# POST /api/diagnostic/complete                                                #
# --------------------------------------------------------------------------- #


@require_auth
async def complete_diagnostic(request: Request) -> JSONResponse:
    """
    Finalise la session de diagnostic et persiste le DiagnosticResult en base.

    Corps :
    {
        "session": { ...état de session final... },
        "duration_seconds": int    // durée totale mesurée côté frontend (optionnel)
    }

    Réponse succès (HTTP 201) :
    {
        "success": true,
        "result": {
            "id": int,
            "completed_at": "ISO",
            "triggered_from": str,
            "questions_asked": int,
            "duration_seconds": int|null,
            "scores": { ... }
        }
    }

    Réponse échec (HTTP 500) :
    { "success": false, "error": str }
    """
    user = request.state.user
    body = await _parse_json(request)
    if body is None:
        return _session_error("Corps JSON invalide")

    session = body.get("session")
    if not session or not isinstance(session, dict):
        return _session_error("Champ 'session' manquant ou invalide")

    duration_seconds: Optional[int] = body.get("duration_seconds")
    if duration_seconds is not None:
        try:
            duration_seconds = int(duration_seconds)
        except (ValueError, TypeError):
            duration_seconds = None

    result_data: Optional[Dict[str, Any]] = None
    async with db_session() as db:
        success, result = diagnostic_svc.save_result(
            db=db,
            user_id=user["id"],
            session=session,
            duration_seconds=duration_seconds,
        )
        # Extraire les données DANS le contexte de session pour éviter DetachedInstanceError
        if success and result is not None:
            result_data = {
                "id": result.id,
                "completed_at": result.completed_at.isoformat(),
                "triggered_from": result.triggered_from,
                "questions_asked": result.questions_asked,
                "duration_seconds": result.duration_seconds,
                "scores": result.scores or {},
            }

    if not success or result_data is None:
        return JSONResponse(
            {"success": False, "error": "Erreur lors de la sauvegarde du diagnostic"},
            status_code=500,
        )

    return JSONResponse(
        {"success": True, "result": result_data},
        status_code=201,
    )
