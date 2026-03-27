"""
Service de diagnostic adaptatif initial - F03.

Implemente un algorithme IRT (Item Response Theory) simplifie pour evaluer
le niveau d'un utilisateur en 4 operations arithmetiques :
ADDITION, SOUSTRACTION, MULTIPLICATION, DIVISION.

Algorithme :
  - Depart au niveau median (PADAWAN, ordinal 1)
  - Reponse correcte -> niveau +1 (plafonne a GRAND_MAITRE)
  - Reponse incorrecte -> niveau -1 (plancher a INITIE)
  - Arret d'un type : 2 erreurs consecutives au MEME niveau -> niveau etabli
  - Session complete : tous les types termines OU 10 questions atteintes

Les questions sont generees a la volee par exercise_generator.generate_ai_exercise()
(generateur interne, pas de requete OpenAI, pas de stockage dans exercises).

Etat de session (DiagnosticSessionState) : dict serialisable en JSON, stocke cote
frontend entre chaque question (stateless backend entre les appels).

Architecture :
  - diagnostic_pending_storage : stockage TTL pending (Redis ou memoire), hors IRT
  - DiagnosticService (ce module) : session IRT, tokens, questions, persistance
  - generate_question() : delegue au generateur interne, applique LaTeX
  - save_result()       : ecrit DiagnosticResult, declenche recommandations
  - get_latest_score()  : point d'entree unique pour recommendation_service
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.constants import AgeGroups, DifficultyLevels, ExerciseTypes
from app.core.db_boundary import sync_db_session
from app.core.logging_config import get_logger
from app.core.mastery_tier_bridge import (
    DEFAULT_AGE_GROUP_FALLBACK,
    canonical_age_group_with_fallback,
    enrich_diagnostic_scores_f42,
)
from app.core.security import sign_diagnostic_state, verify_diagnostic_state
from app.models.diagnostic_result import DiagnosticResult
from app.models.user import User
from app.services.diagnostic.diagnostic_pending_storage import (
    delete_pending_state,
    get_pending_state,
    load_pending_state,
    store_pending_state,
)

logger = get_logger(__name__)

# --------------------------------------------------------------------------- #
# Constantes de l'algorithme - seul endroit a modifier pour tuner l'algo      #
# --------------------------------------------------------------------------- #

# Types evalues (logique exclue de V1 : pas de generateur interne de qualite)
DIAGNOSTIC_TYPES: List[str] = [
    ExerciseTypes.ADDITION,
    ExerciseTypes.SUBTRACTION,
    ExerciseTypes.MULTIPLICATION,
    ExerciseTypes.DIVISION,
]

# Niveau de depart (ordinal 1 = PADAWAN)
STARTING_LEVEL_ORDINAL: int = 1

# Nombre max de questions sur toute la session
MAX_QUESTIONS: int = 10

# Nombre d'erreurs consecutives au meme niveau pour figer un type
CONSECUTIVE_ERRORS_TO_STOP: int = 2

# Mapping ordinal <-> difficulte (source de verite unique)
_ORDINAL_TO_DIFFICULTY: Dict[int, str] = {
    0: DifficultyLevels.INITIE,
    1: DifficultyLevels.PADAWAN,
    2: DifficultyLevels.CHEVALIER,
    3: DifficultyLevels.MAITRE,
    4: DifficultyLevels.GRAND_MAITRE,
}
_DIFFICULTY_TO_ORDINAL: Dict[str, int] = {
    v: k for k, v in _ORDINAL_TO_DIFFICULTY.items()
}

# Mapping difficulte -> age_group pour le generateur interne
_DIFFICULTY_TO_AGE_GROUP: Dict[str, str] = {
    DifficultyLevels.INITIE: AgeGroups.GROUP_6_8,
    DifficultyLevels.PADAWAN: AgeGroups.GROUP_9_11,
    DifficultyLevels.CHEVALIER: AgeGroups.GROUP_12_14,
    DifficultyLevels.MAITRE: AgeGroups.GROUP_15_17,
    DifficultyLevels.GRAND_MAITRE: AgeGroups.ADULT,
}


# --------------------------------------------------------------------------- #
# Structures de donnees de session                                             #
# --------------------------------------------------------------------------- #


def _initial_type_state(level_ordinal: int = STARTING_LEVEL_ORDINAL) -> Dict[str, Any]:
    """Etat initial pour un type d'exercice dans la session."""
    return {
        "level_ordinal": level_ordinal,  # niveau courant (0-4)
        "correct": 0,  # bonnes reponses pour ce type
        "total": 0,  # questions posees pour ce type
        "consecutive_errors": 0,  # erreurs consecutives au niveau courant
        "done": False,  # type finalise (2 erreurs ou session max)
        "last_error_level": None,  # niveau ou les 2 erreurs ont ete commises
    }


def create_session(triggered_from: str = "onboarding") -> Dict[str, Any]:
    """
    Cree un etat de session vierge.

    triggered_from : "onboarding" | "settings"
    """
    return {
        "triggered_from": triggered_from,
        "questions_asked": 0,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "types": {t: _initial_type_state() for t in DIAGNOSTIC_TYPES},
        # Index de rotation pour alterner les types equitablement
        "type_rotation_index": 0,
    }


# --------------------------------------------------------------------------- #
# State token (C1 - integrity backend)                                         #
# --------------------------------------------------------------------------- #
#
# Structure du state signe : {"session": {...}, "pending_ref": str | None}
# Stockage pending serveur (Redis / memoire) : diagnostic_pending_storage.


def sign_state_token(state: Dict[str, Any]) -> str:
    """Signe l'etat diagnostic. Retourne un token JWT."""
    return sign_diagnostic_state(state)


def verify_state_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verifie le token et retourne l'etat.
    Retourne None si token invalide, expire ou falsifie.
    """
    return verify_diagnostic_state(token)


def check_answer(state: Dict[str, Any], user_answer: str) -> bool:
    """
    Compare la reponse utilisateur a la bonne reponse contenue dans le state verifie.
    Source de verite : backend uniquement (pas de correct_answer client).

    Raises:
        ValueError: si state n'a pas de pending (question en attente).
    """
    pending = get_pending_state(state)
    if not pending:
        raise ValueError("Aucune question en attente pour cette session")
    correct = pending.get("correct_answer", "")
    return str(user_answer).strip().lower() == str(correct).strip().lower()


def apply_answer_and_advance(
    state: Dict[str, Any], exercise_type: str, is_correct: bool
) -> None:
    """
    Applique la reponse au state et efface le pending.
    Mutate state en place.
    """
    _apply_answer(state["session"], exercise_type, is_correct)
    pending_ref = state.get("pending_ref")
    if pending_ref and isinstance(pending_ref, str):
        delete_pending_state(pending_ref)
    state["pending_ref"] = None


# --------------------------------------------------------------------------- #
# Logique IRT                                                                  #
# --------------------------------------------------------------------------- #


def _next_type(session: Dict[str, Any]) -> Optional[str]:
    """
    Retourne le prochain type a evaluer (round-robin sur les types non termines).
    Retourne None si tous les types sont termines ou MAX_QUESTIONS atteint.
    """
    if session["questions_asked"] >= MAX_QUESTIONS:
        return None

    active = [t for t in DIAGNOSTIC_TYPES if not session["types"][t]["done"]]
    if not active:
        return None

    # Round-robin : reprendre la ou on s'etait arrete
    idx = session["type_rotation_index"] % len(active)
    return active[idx]


def _advance_rotation(session: Dict[str, Any]) -> None:
    """Avance l'index de rotation apres avoir pose une question."""
    active = [t for t in DIAGNOSTIC_TYPES if not session["types"][t]["done"]]
    if active:
        session["type_rotation_index"] = (session["type_rotation_index"] + 1) % len(
            active
        )


def _apply_answer(
    session: Dict[str, Any], exercise_type: str, is_correct: bool
) -> None:
    """
    Met a jour l'etat IRT pour un type apres une reponse.

    Regles :
    - Correct  -> level +1, reset consecutive_errors
    - Incorrect -> consecutive_errors +1
                  si consecutive_errors >= seuil -> done = True (niveau fige)
                  sinon → level -1 (plancher 0)
    """
    ts = session["types"][exercise_type]
    ts["total"] += 1
    session["questions_asked"] += 1

    if is_correct:
        ts["correct"] += 1
        ts["consecutive_errors"] = 0
        # Monter d'un niveau si possible
        ts["level_ordinal"] = min(
            ts["level_ordinal"] + 1, max(_ORDINAL_TO_DIFFICULTY.keys())
        )
    else:
        ts["consecutive_errors"] += 1
        current_level = ts["level_ordinal"]

        if ts["consecutive_errors"] >= CONSECUTIVE_ERRORS_TO_STOP:
            # Niveau etabli : on fige a ce niveau
            ts["done"] = True
            ts["last_error_level"] = current_level
            logger.debug(
                f"Diagnostic: type={exercise_type} fige au niveau ordinal {current_level}"
            )
        else:
            # Descendre d'un niveau (plancher 0)
            ts["level_ordinal"] = max(ts["level_ordinal"] - 1, 0)

    _advance_rotation(session)


def is_session_complete(session: Dict[str, Any]) -> bool:
    """Retourne True si la session est terminee (tous types done ou max questions)."""
    if session["questions_asked"] >= MAX_QUESTIONS:
        return True
    return all(session["types"][t]["done"] for t in DIAGNOSTIC_TYPES)


# --------------------------------------------------------------------------- #
# Generation de questions                                                      #
# --------------------------------------------------------------------------- #


def generate_question(session: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Genere la prochaine question du diagnostic.

    Delegue a generate_ai_exercise() du generateur interne - aucune requete IA,
    aucun stockage en DB.

    Retourne un dict avec les champs necessaires au frontend, ou None si la
    session est terminee.
    """
    # Import ici pour eviter les imports circulaires au niveau module
    from app.generators.exercise_generator import generate_ai_exercise

    exercise_type = _next_type(session)
    if exercise_type is None:
        return None

    level_ordinal = session["types"][exercise_type]["level_ordinal"]
    difficulty = _ORDINAL_TO_DIFFICULTY[level_ordinal]
    age_group = _DIFFICULTY_TO_AGE_GROUP[difficulty]

    try:
        raw = generate_ai_exercise(exercise_type, age_group)
    except Exception as exc:
        logger.error(
            f"Diagnostic: erreur generation exercice type={exercise_type} "
            f"difficulty={difficulty}: {exc}"
        )
        return None

    return {
        "exercise_type": exercise_type,
        "difficulty": difficulty,
        "level_ordinal": level_ordinal,
        "question": raw.get("question", ""),
        "choices": raw.get("choices", []),
        "correct_answer": raw.get("correct_answer", ""),
        "explanation": raw.get("explanation", ""),
        "hint": raw.get("hint", ""),
        # Meta pour le frontend
        "question_number": session["questions_asked"] + 1,
        "max_questions": MAX_QUESTIONS,
        "types_remaining": len(
            [t for t in DIAGNOSTIC_TYPES if not session["types"][t]["done"]]
        ),
    }


# --------------------------------------------------------------------------- #
# Persistence                                                                  #
# --------------------------------------------------------------------------- #


def _compute_final_scores(session: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calcule les scores finaux depuis l'etat de session.

    Format de sortie (stocke dans DiagnosticResult.scores) :
    {
        "addition":       {"level": 2, "difficulty": "CHEVALIER", "correct": 4, "total": 5},
        "soustraction":   {"level": 1, ...},
        ...
    }
    """
    scores = {}
    for ex_type in DIAGNOSTIC_TYPES:
        ts = session["types"][ex_type]
        # Si le type n'a pas ete evalue (0 questions), on ne le stocke pas
        if ts["total"] == 0:
            continue
        # Le niveau final = le niveau courant (deja ajuste par l'algo IRT)
        final_level = ts["level_ordinal"]
        scores[ex_type.lower()] = {
            "level": final_level,
            "difficulty": _ORDINAL_TO_DIFFICULTY[final_level],
            "correct": ts["correct"],
            "total": ts["total"],
        }
    return scores


def save_result(
    db: Session,
    user_id: int,
    session: Dict[str, Any],
    duration_seconds: Optional[int] = None,
) -> Tuple[bool, Optional[DiagnosticResult]]:
    """
    Persiste le resultat de la session en base.

    Retourne (success, DiagnosticResult | None).
    Declenche la regeneration des recommandations apres sauvegarde.
    """
    try:
        scores = _compute_final_scores(session)
        result = DiagnosticResult(
            user_id=user_id,
            triggered_from=session.get("triggered_from", "onboarding"),
            scores=scores,
            questions_asked=session["questions_asked"],
            duration_seconds=duration_seconds,
        )
        db.add(result)
        db.commit()
        db.refresh(result)
        logger.info(
            f"DiagnosticResult sauvegarde: user={user_id} "
            f"questions={result.questions_asked} scores={scores}"
        )

        # Declenche la regeneration des recommandations pour profiter du diagnostic
        _refresh_recommendations(db, user_id)

        return True, result

    except SQLAlchemyError as exc:
        logger.error(f"Erreur sauvegarde DiagnosticResult user={user_id}: {exc}")
        db.rollback()
        return False, None


def save_result_sync(
    user_id: int,
    session: Dict[str, Any],
    duration_seconds: Optional[int] = None,
) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Use case sync: persiste le resultat de diagnostic.
    Retourne (success, result_data_dict) avec result_data_dict serialise dans le contexte DB.
    Execute via run_db_bound() depuis les handlers async.
    """
    with sync_db_session() as db:
        success, result = save_result(
            db, user_id=user_id, session=session, duration_seconds=duration_seconds
        )
        if not success or result is None:
            return False, None
        return True, {
            "id": result.id,
            "completed_at": result.completed_at.isoformat(),
            "triggered_from": result.triggered_from,
            "questions_asked": result.questions_asked,
            "duration_seconds": result.duration_seconds,
            "scores": result.scores or {},
        }


def _refresh_recommendations(db: Session, user_id: int) -> None:
    """
    Regenere les recommandations utilisateur apres un diagnostic.
    Isole dans une fonction pour ne pas bloquer save_result en cas d'erreur.
    """
    try:
        from app.services.recommendation.recommendation_service import (
            RecommendationService,
        )

        RecommendationService.generate_recommendations(db, user_id)
    except Exception as exc:
        logger.warning(
            f"Impossible de regenerer les recommandations apres diagnostic "
            f"user={user_id}: {exc}"
        )


# --------------------------------------------------------------------------- #
# Point d'entree public pour les autres services                               #
# --------------------------------------------------------------------------- #


def get_latest_score_sync(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Use case sync: recupere le dernier score de diagnostic.
    Execute via run_db_bound() depuis les handlers async.
    """
    with sync_db_session() as db:
        return get_latest_score(db, user_id)


def get_latest_score(db: Session, user_id: int) -> Optional[Dict[str, Any]]:
    """
    Retourne le dernier score de diagnostic pour un utilisateur.

    Format de retour :
    {
        "completed_at": "2026-03-04T...",
        "triggered_from": "onboarding",
        "scores": {
            "addition": {"level": 2, "difficulty": "CHEVALIER", "correct": 4, "total": 5},
            ...
        }
    }
    Retourne None si aucun diagnostic n'a ete effectue.
    """
    result = (
        db.query(DiagnosticResult)
        .filter(DiagnosticResult.user_id == user_id)
        .order_by(DiagnosticResult.completed_at.desc())
        .first()
    )
    if not result:
        return None
    scores = result.scores or {}
    payload: Dict[str, Any] = {
        "id": result.id,
        "completed_at": result.completed_at.isoformat(),
        "triggered_from": result.triggered_from,
        "questions_asked": result.questions_asked,
        "duration_seconds": result.duration_seconds,
        "scores": scores,
    }
    user = db.query(User).filter(User.id == user_id).first()
    canon = (
        canonical_age_group_with_fallback(user)
        if user is not None
        else DEFAULT_AGE_GROUP_FALLBACK
    )
    payload["scores_f42"] = enrich_diagnostic_scores_f42(
        scores, canonical_age_group=canon
    )
    payload["canonical_age_group_f42"] = canon
    return payload


def has_completed_diagnostic(db: Session, user_id: int) -> bool:
    """Verifie rapidement si l'utilisateur a au moins un diagnostic complete."""
    return (
        db.query(DiagnosticResult.id)
        .filter(DiagnosticResult.user_id == user_id)
        .first()
    ) is not None


def difficulty_to_ordinal(difficulty: str) -> int:
    """Convertit une chaine difficulte -> ordinal (utilitaire expose aux tests)."""
    return _DIFFICULTY_TO_ORDINAL.get(difficulty.upper(), STARTING_LEVEL_ORDINAL)


def ordinal_to_difficulty(ordinal: int) -> str:
    """Convertit un ordinal -> chaine difficulte (utilitaire expose aux tests)."""
    return _ORDINAL_TO_DIFFICULTY.get(ordinal, DifficultyLevels.PADAWAN)
