"""
Handlers API pour le diagnostic adaptatif initial - F03.

Endpoints :
  GET  /api/diagnostic/status   - etat du diagnostic (complete ou non)
  POST /api/diagnostic/start    - cree une session vierge
  POST /api/diagnostic/question - genere la prochaine question depuis l'etat de session
  POST /api/diagnostic/answer   - soumet une reponse, retourne etat mis a jour + feedback
  POST /api/diagnostic/complete - finalise la session, persiste DiagnosticResult

Design stateless : l'etat de session (dict JSON) transite dans le corps de la requete.
Le backend ne conserve rien entre les appels jusqu'a /complete - seule la table
diagnostic_results est ecrite a la fin.
"""

import json
import time
from typing import Any, Dict, Optional, Union

from starlette.requests import Request
from starlette.responses import JSONResponse

import app.services.diagnostic.diagnostic_service as diagnostic_svc
from app.core.logging_config import get_logger
from app.core.runtime import run_db_bound
from app.utils.request_utils import read_body_with_limit
from server.auth import require_auth

logger = get_logger(__name__)


# --------------------------------------------------------------------------- #
# Helpers internes                                                              #
# --------------------------------------------------------------------------- #


async def _parse_json(
    request: Request,
) -> Union[Dict[str, Any], None, JSONResponse]:
    """Parse le corps JSON avec garde MAX_CONTENT_LENGTH (D2b). Retourne dict, None, ou 413."""
    body_bytes, err = await read_body_with_limit(request)
    if err is not None:
        return err
    if not body_bytes:
        return {}
    try:
        return json.loads(body_bytes.decode("utf-8"))
    except (json.JSONDecodeError, ValueError) as exc:
        logger.warning("Corps JSON invalide: %s", exc)
        return None


def _session_error(msg: str, status_code: int = 400) -> JSONResponse:
    return JSONResponse({"error": msg}, status_code=status_code)


# --------------------------------------------------------------------------- #
# GET /api/diagnostic/status                                                   #
# --------------------------------------------------------------------------- #


@require_auth
async def get_diagnostic_status(request: Request) -> JSONResponse:
    """
    Retourne l'etat du diagnostic pour l'utilisateur connecte.

    Reponse :
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
    latest = await run_db_bound(diagnostic_svc.get_latest_score_sync, user["id"])
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
    Cree et retourne une session de diagnostic vierge avec state_token signe.

    Corps (optionnel) :
    { "triggered_from": "onboarding" | "settings" }

    Reponse :
    {
        "session": { ...etat initial... },
        "state_token": str,   // token signe - source de verite pour les appels suivants
        "started_at_ts": float
    }
    """
    body = await _parse_json(request)
    if isinstance(body, JSONResponse):
        return body
    if body is None:
        return _session_error("Corps JSON invalide")

    triggered_from = body.get("triggered_from", "onboarding")
    if triggered_from not in ("onboarding", "settings"):
        triggered_from = "onboarding"

    session = diagnostic_svc.create_session(triggered_from)
    state = {"session": session, "pending_ref": None}
    state_token = diagnostic_svc.sign_state_token(state)
    return JSONResponse(
        {
            "session": session,
            "state_token": state_token,
            "started_at_ts": time.time(),
        }
    )


# --------------------------------------------------------------------------- #
# POST /api/diagnostic/question                                                #
# --------------------------------------------------------------------------- #


@require_auth
async def get_next_question(request: Request) -> JSONResponse:
    """
    Genere la prochaine question depuis le state_token verifie.

    Corps :
    { "state_token": str }   // token emis par /start ou /answer

    Reponse si question disponible (HTTP 200) :
    {
        "done": false,
        "question": { ... },
        "state_token": str   // a renvoyer pour /answer
    }

    Reponse si session terminee (HTTP 200) :
    { "done": true, "state_token": str }   // a renvoyer pour /complete
    """
    body = await _parse_json(request)
    if isinstance(body, JSONResponse):
        return body
    if body is None:
        return _session_error("Corps JSON invalide")

    state_token = body.get("state_token")
    if not state_token or not isinstance(state_token, str):
        return _session_error("Champ 'state_token' manquant ou invalide", 400)

    state = diagnostic_svc.verify_state_token(state_token)
    if state is None:
        return _session_error("State token invalide ou expire", 401)

    session = state.get("session")
    if not session or not isinstance(session, dict):
        return _session_error("Etat de session invalide", 400)

    if diagnostic_svc.is_session_complete(session):
        next_state = {"session": session, "pending_ref": None}
        return JSONResponse(
            {
                "done": True,
                "state_token": diagnostic_svc.sign_state_token(next_state),
            }
        )

    question = diagnostic_svc.generate_question(session)
    if question is None:
        next_state = {"session": session, "pending_ref": None}
        return JSONResponse(
            {
                "done": True,
                "state_token": diagnostic_svc.sign_state_token(next_state),
            }
        )

    # correct_answer reste uniquement dans le state_token signe, jamais expose au client
    correct_answer = question.pop("correct_answer", "")
    pending_ref = diagnostic_svc.store_pending_state(
        {
            "exercise_type": question["exercise_type"],
            "correct_answer": correct_answer,
        }
    )
    next_state = {
        "session": session,
        "pending_ref": pending_ref,
    }
    return JSONResponse(
        {
            "done": False,
            "question": question,
            "state_token": diagnostic_svc.sign_state_token(next_state),
        }
    )


# --------------------------------------------------------------------------- #
# POST /api/diagnostic/answer                                                  #
# --------------------------------------------------------------------------- #


@require_auth
async def submit_diagnostic_answer(request: Request) -> JSONResponse:
    """
    Soumet la reponse de l'utilisateur. La correction est faite cote backend
    (correct_answer lu depuis le state_token verifie, jamais du client).

    Corps :
    {
        "state_token": str,   // token emis par /question
        "user_answer": str
    }

    Reponse :
    {
        "is_correct": bool,
        "session": { ...etat mis a jour... },
        "state_token": str,
        "session_complete": bool
    }
    """
    body = await _parse_json(request)
    if isinstance(body, JSONResponse):
        return body
    if body is None:
        return _session_error("Corps JSON invalide")

    state_token = body.get("state_token")
    user_answer = body.get("user_answer", "")

    if not state_token or not isinstance(state_token, str):
        return _session_error("Champ 'state_token' manquant ou invalide", 400)

    state = diagnostic_svc.verify_state_token(state_token)
    if state is None:
        return _session_error("State token invalide ou expire", 401)

    try:
        is_correct = diagnostic_svc.check_answer(state, user_answer)
    except ValueError:
        return _session_error("Aucune question en attente pour cette session", 400)

    pending = diagnostic_svc.get_pending_state(state)
    if not pending:
        return _session_error("Question en attente introuvable ou expiree", 400)
    exercise_type = pending["exercise_type"]
    correct_answer = pending.get("correct_answer", "")

    diagnostic_svc.apply_answer_and_advance(state, exercise_type, is_correct)

    session = state["session"]
    next_state = {"session": session, "pending_ref": None}
    next_token = diagnostic_svc.sign_state_token(next_state)

    # correct_answer expose uniquement apres soumission, pour feedback pedagogique
    return JSONResponse(
        {
            "is_correct": is_correct,
            "correct_answer": correct_answer,
            "session": session,
            "state_token": next_token,
            "session_complete": diagnostic_svc.is_session_complete(session),
        }
    )


# --------------------------------------------------------------------------- #
# POST /api/diagnostic/complete                                                #
# --------------------------------------------------------------------------- #


@require_auth
async def complete_diagnostic(request: Request) -> JSONResponse:
    """
    Finalise et persiste le diagnostic. La session est lue depuis le state_token
    verifie (jamais depuis le client).

    Corps :
    {
        "state_token": str,
        "duration_seconds": int    // optionnel
    }

    Reponse succes (HTTP 201) :
    {
        "success": true,
        "result": { ... }
    }
    """
    user = request.state.user
    body = await _parse_json(request)
    if isinstance(body, JSONResponse):
        return body
    if body is None:
        return _session_error("Corps JSON invalide")

    state_token = body.get("state_token")
    if not state_token or not isinstance(state_token, str):
        return _session_error("Champ 'state_token' manquant ou invalide", 400)

    state = diagnostic_svc.verify_state_token(state_token)
    if state is None:
        return _session_error("State token invalide ou expire", 401)

    session = state.get("session")
    if not session or not isinstance(session, dict):
        return _session_error("Etat de session invalide", 400)

    duration_seconds: Optional[int] = body.get("duration_seconds")
    if duration_seconds is not None:
        try:
            duration_seconds = int(duration_seconds)
        except (ValueError, TypeError):
            duration_seconds = None

    success, result_data = await run_db_bound(
        diagnostic_svc.save_result_sync,
        user["id"],
        session,
        duration_seconds,
    )

    if not success or result_data is None:
        return JSONResponse(
            {"success": False, "error": "Erreur lors de la sauvegarde du diagnostic"},
            status_code=500,
        )

    return JSONResponse(
        {"success": True, "result": result_data},
        status_code=201,
    )
