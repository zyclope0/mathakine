"""
Service de diagnostic adaptatif initial — F03.

Implémente un algorithme IRT (Item Response Theory) simplifié pour évaluer
le niveau d'un utilisateur en 4 opérations arithmétiques :
ADDITION, SOUSTRACTION, MULTIPLICATION, DIVISION.

Algorithme :
  - Départ au niveau médian (PADAWAN, ordinal 1)
  - Réponse correcte → niveau +1 (plafonné à GRAND_MAITRE)
  - Réponse incorrecte → niveau -1 (plancher à INITIE)
  - Arrêt d'un type : 2 erreurs consécutives au MÊME niveau → niveau établi
  - Session complète : tous les types terminés OU 10 questions atteintes

Les questions sont générées à la volée par exercise_generator.generate_ai_exercise()
(générateur interne, pas de requête OpenAI, pas de stockage dans exercises).

État de session (DiagnosticSessionState) : dict sérialisable en JSON, stocké côté
frontend entre chaque question (stateless backend entre les appels).

Architecture :
  - DiagnosticService  : logique métier pure (aucune dépendance DB directe sauf save)
  - generate_question() : délègue au générateur interne, applique LaTeX
  - next_type()         : stratégie de rotation des types (round-robin équilibré)
  - save_result()       : écrit DiagnosticResult, déclenche recommandations
  - get_latest_score()  : point d'entrée unique pour recommendation_service
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.constants import AgeGroups, DifficultyLevels, ExerciseTypes
from app.core.logging_config import get_logger
from app.models.diagnostic_result import DiagnosticResult

logger = get_logger(__name__)

# --------------------------------------------------------------------------- #
# Constantes de l'algorithme — seul endroit à modifier pour tuner l'algo      #
# --------------------------------------------------------------------------- #

# Types évalués (logique exclue de V1 : pas de générateur interne de qualité)
DIAGNOSTIC_TYPES: List[str] = [
    ExerciseTypes.ADDITION,
    ExerciseTypes.SUBTRACTION,
    ExerciseTypes.MULTIPLICATION,
    ExerciseTypes.DIVISION,
]

# Niveau de départ (ordinal 1 = PADAWAN)
STARTING_LEVEL_ORDINAL: int = 1

# Nombre max de questions sur toute la session
MAX_QUESTIONS: int = 10

# Nombre d'erreurs consécutives au même niveau pour figer un type
CONSECUTIVE_ERRORS_TO_STOP: int = 2

# Mapping ordinal ↔ difficulté (source de vérité unique)
_ORDINAL_TO_DIFFICULTY: Dict[int, str] = {
    0: DifficultyLevels.INITIE,
    1: DifficultyLevels.PADAWAN,
    2: DifficultyLevels.CHEVALIER,
    3: DifficultyLevels.MAITRE,
    4: DifficultyLevels.GRAND_MAITRE,
}
_DIFFICULTY_TO_ORDINAL: Dict[str, int] = {v: k for k, v in _ORDINAL_TO_DIFFICULTY.items()}

# Mapping difficulté → age_group pour le générateur interne
_DIFFICULTY_TO_AGE_GROUP: Dict[str, str] = {
    DifficultyLevels.INITIE: AgeGroups.GROUP_6_8,
    DifficultyLevels.PADAWAN: AgeGroups.GROUP_9_11,
    DifficultyLevels.CHEVALIER: AgeGroups.GROUP_12_14,
    DifficultyLevels.MAITRE: AgeGroups.GROUP_15_17,
    DifficultyLevels.GRAND_MAITRE: AgeGroups.ADULT,
}


# --------------------------------------------------------------------------- #
# Structures de données de session                                             #
# --------------------------------------------------------------------------- #

def _initial_type_state(level_ordinal: int = STARTING_LEVEL_ORDINAL) -> Dict[str, Any]:
    """État initial pour un type d'exercice dans la session."""
    return {
        "level_ordinal": level_ordinal,          # niveau courant (0-4)
        "correct": 0,                             # bonnes réponses pour ce type
        "total": 0,                               # questions posées pour ce type
        "consecutive_errors": 0,                  # erreurs consécutives au niveau courant
        "done": False,                            # type finalisé (2 erreurs ou session max)
        "last_error_level": None,                 # niveau où les 2 erreurs ont été commises
    }


def create_session(triggered_from: str = "onboarding") -> Dict[str, Any]:
    """
    Crée un état de session vierge.

    triggered_from : "onboarding" | "settings"
    """
    return {
        "triggered_from": triggered_from,
        "questions_asked": 0,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "types": {t: _initial_type_state() for t in DIAGNOSTIC_TYPES},
        # Index de rotation pour alterner les types équitablement
        "type_rotation_index": 0,
    }


# --------------------------------------------------------------------------- #
# Logique IRT                                                                  #
# --------------------------------------------------------------------------- #

def _next_type(session: Dict[str, Any]) -> Optional[str]:
    """
    Retourne le prochain type à évaluer (round-robin sur les types non terminés).
    Retourne None si tous les types sont terminés ou MAX_QUESTIONS atteint.
    """
    if session["questions_asked"] >= MAX_QUESTIONS:
        return None

    active = [t for t in DIAGNOSTIC_TYPES if not session["types"][t]["done"]]
    if not active:
        return None

    # Round-robin : reprendre là où on s'était arrêté
    idx = session["type_rotation_index"] % len(active)
    return active[idx]


def _advance_rotation(session: Dict[str, Any]) -> None:
    """Avance l'index de rotation après avoir posé une question."""
    active = [t for t in DIAGNOSTIC_TYPES if not session["types"][t]["done"]]
    if active:
        session["type_rotation_index"] = (session["type_rotation_index"] + 1) % len(active)


def _apply_answer(session: Dict[str, Any], exercise_type: str, is_correct: bool) -> None:
    """
    Met à jour l'état IRT pour un type après une réponse.

    Règles :
    - Correct  → level +1, reset consecutive_errors
    - Incorrect → consecutive_errors +1
                  si consecutive_errors >= seuil → done = True (niveau figé)
                  sinon → level -1 (plancher 0)
    """
    ts = session["types"][exercise_type]
    ts["total"] += 1
    session["questions_asked"] += 1

    if is_correct:
        ts["correct"] += 1
        ts["consecutive_errors"] = 0
        # Monter d'un niveau si possible
        ts["level_ordinal"] = min(ts["level_ordinal"] + 1, max(_ORDINAL_TO_DIFFICULTY.keys()))
    else:
        ts["consecutive_errors"] += 1
        current_level = ts["level_ordinal"]

        if ts["consecutive_errors"] >= CONSECUTIVE_ERRORS_TO_STOP:
            # Niveau établi : on fige à ce niveau
            ts["done"] = True
            ts["last_error_level"] = current_level
            logger.debug(
                f"Diagnostic: type={exercise_type} figé au niveau ordinal {current_level}"
            )
        else:
            # Descendre d'un niveau (plancher 0)
            ts["level_ordinal"] = max(ts["level_ordinal"] - 1, 0)

    _advance_rotation(session)


def is_session_complete(session: Dict[str, Any]) -> bool:
    """Retourne True si la session est terminée (tous types done ou max questions)."""
    if session["questions_asked"] >= MAX_QUESTIONS:
        return True
    return all(session["types"][t]["done"] for t in DIAGNOSTIC_TYPES)


# --------------------------------------------------------------------------- #
# Génération de questions                                                      #
# --------------------------------------------------------------------------- #

def generate_question(session: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Génère la prochaine question du diagnostic.

    Délègue à generate_ai_exercise() du générateur interne — aucune requête IA,
    aucun stockage en DB.

    Retourne un dict avec les champs nécessaires au frontend, ou None si la
    session est terminée.
    """
    # Import ici pour éviter les imports circulaires au niveau module
    from server.exercise_generator import generate_ai_exercise

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
            f"Diagnostic: erreur génération exercice type={exercise_type} "
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
        # Méta pour le frontend
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
    Calcule les scores finaux depuis l'état de session.

    Format de sortie (stocké dans DiagnosticResult.scores) :
    {
        "addition":       {"level": 2, "difficulty": "CHEVALIER", "correct": 4, "total": 5},
        "soustraction":   {"level": 1, ...},
        ...
    }
    """
    scores = {}
    for ex_type in DIAGNOSTIC_TYPES:
        ts = session["types"][ex_type]
        # Si le type n'a pas été évalué (0 questions), on ne le stocke pas
        if ts["total"] == 0:
            continue
        # Le niveau final = le niveau courant (déjà ajusté par l'algo IRT)
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
    Persiste le résultat de la session en base.

    Retourne (success, DiagnosticResult | None).
    Déclenche la régénération des recommandations après sauvegarde.
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
            f"DiagnosticResult sauvegardé: user={user_id} "
            f"questions={result.questions_asked} scores={scores}"
        )

        # Déclenche la régénération des recommandations pour profiter du diagnostic
        _refresh_recommendations(db, user_id)

        return True, result

    except SQLAlchemyError as exc:
        logger.error(f"Erreur sauvegarde DiagnosticResult user={user_id}: {exc}")
        db.rollback()
        return False, None


def _refresh_recommendations(db: Session, user_id: int) -> None:
    """
    Régénère les recommandations utilisateur après un diagnostic.
    Isolé dans une fonction pour ne pas bloquer save_result en cas d'erreur.
    """
    try:
        from app.services.recommendation_service import RecommendationService
        RecommendationService.generate_recommendations(db, user_id)
    except Exception as exc:
        logger.warning(
            f"Impossible de régénérer les recommandations après diagnostic "
            f"user={user_id}: {exc}"
        )


# --------------------------------------------------------------------------- #
# Point d'entrée public pour les autres services                               #
# --------------------------------------------------------------------------- #

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
    Retourne None si aucun diagnostic n'a été effectué.
    """
    result = (
        db.query(DiagnosticResult)
        .filter(DiagnosticResult.user_id == user_id)
        .order_by(DiagnosticResult.completed_at.desc())
        .first()
    )
    if not result:
        return None
    return {
        "id": result.id,
        "completed_at": result.completed_at.isoformat(),
        "triggered_from": result.triggered_from,
        "questions_asked": result.questions_asked,
        "duration_seconds": result.duration_seconds,
        "scores": result.scores or {},
    }


def has_completed_diagnostic(db: Session, user_id: int) -> bool:
    """Vérifie rapidement si l'utilisateur a au moins un diagnostic complété."""
    return (
        db.query(DiagnosticResult.id)
        .filter(DiagnosticResult.user_id == user_id)
        .first()
    ) is not None


def difficulty_to_ordinal(difficulty: str) -> int:
    """Convertit une chaîne difficulté → ordinal (utilitaire exposé aux tests)."""
    return _DIFFICULTY_TO_ORDINAL.get(difficulty.upper(), STARTING_LEVEL_ORDINAL)


def ordinal_to_difficulty(ordinal: int) -> str:
    """Convertit un ordinal → chaîne difficulté (utilitaire exposé aux tests)."""
    return _ORDINAL_TO_DIFFICULTY.get(ordinal, DifficultyLevels.PADAWAN)
