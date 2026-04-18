"""
Service d'adaptation dynamique de difficulté — F05.

Détermine le groupe d'âge (et donc la difficulté) adaptatif pour un utilisateur
selon une cascade de priorités :

  1. Diagnostic IRT (F03) — évaluation initiale par type d'exercice, valide 30 jours
  2. Progression temps réel — taux de réussite + streak sur les 7 derniers jours
  3. Profil utilisateur — users.age_group (F42), puis preferred_difficulty ou grade_level
  4. Fallback — GROUP_9_11 (PADAWAN)

Après résolution du niveau de base, un ajustement « boost/descente » est appliqué :
  - completion_rate > 85 % ET streak >= 3  → monter d'un niveau
  - completion_rate < 50 % ET streak = 0   → descendre d'un niveau
  - sinon                                  → niveau de base maintenu

Types couverts par l'IRT (F03) :
  - ADDITION, SOUSTRACTION, MULTIPLICATION, DIVISION → score IRT direct
  - MIXTE → minimum des scores IRT des 4 types de base (protection surcharge)
  - FRACTIONS → moyenne IRT de MULTIPLICATION + DIVISION (proximité algébrique)
  - GEOMETRIE, TEXTE, DIVERS → pas de score IRT par type ; **prior ordinal seedé**
    (profil utilisateur, traçé ``source=seeded_prior`` — pas une calibration IRT réelle)
    puis cascade habituelle si le seed ne s’applique pas

La fonction publique resolve_irt_level() expose le niveau IRT résolu par type,
utilisée par le frontend pour décider du mode de réponse (QCM vs saisie libre)
sans dépendre du flag is_open_answer du générateur.

Fondements scientifiques :
  - Hattie (2009) — Formative assessment : d=0.90 ; calibrer la difficulté sur le
    niveau réel est la condition préalable à l'apprentissage efficace.
  - Sweller (1988) — Cognitive Load Theory : l'alignement difficulté/compétence
    prévient la surcharge cognitive (trop facile = ennui, trop difficile = anxiété).
  - Deci & Ryan (2000) — SDT : l'autonomie et le sentiment de compétence sont
    préservés quand la difficulté est dans la zone proximale de développement.
  - Vygotsky (1978) — ZPD : retirer l'aide QCM uniquement quand la maîtrise est
    prouvée par type (GRAND_MAITRE IRT), pas globalement.
"""

import threading
import time
from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Tuple

from sqlalchemy.orm import Session

from app.core.constants import AgeGroups, DifficultyLevels, ExerciseTypes
from app.core.difficulty_tier import pedagogical_band_index_from_difficulty
from app.core.logging_config import get_logger
from app.core.mastery_tier_bridge import mastery_level_int_to_pedagogical_band
from app.core.user_age_group import normalized_age_group_from_user_profile
from app.models.progress import Progress


@dataclass
class AdaptiveGenerationContext:
    """Rich context resolved for local exercise generation (F42 second axis).

    Carries the age_group resolved by the adaptive cascade AND a pedagogical_band
    derived from mastery data (when available).  Two learners in the same age
    group but with different mastery can therefore receive different bands and
    hence different numeric calibration bounds.

    Attributes:
        age_group:          Canonical age_group (e.g. "GROUP_9_11").
        pedagogical_band:   "discovery" | "learning" | "consolidation".
                            Cold-start default is ``COLD_START_PEDAGOGICAL_BAND``
                            (F42-P2a: currently ``learning``).
        mastery_source:     Human-readable description of what drove the band
                            (for debug / traceability).
    """

    age_group: str
    pedagogical_band: str
    mastery_source: str = "fallback"


logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# F42-P2a — cold-start pedagogical band (product decision, do not change casually)
# ---------------------------------------------------------------------------
# When there is no recent Progress (>= min attempts) and no valid IRT band mapping,
# the second axis defaults to this band for all age groups. Unknown age still uses
# GROUP_9_11 via _resolve_stable_age_group; band stays "learning" (not "discovery").
COLD_START_PEDAGOGICAL_BAND: str = "learning"

# F42-P2b — in-process cache for resolve_adaptive_context (no Redis)
_ADAPTIVE_CONTEXT_CACHE_TTL_SEC: float = 300.0
_adaptive_context_cache: Dict[
    Tuple[int, str], Tuple[float, AdaptiveGenerationContext]
] = {}
_adaptive_context_cache_lock = threading.Lock()


def clear_resolve_adaptive_context_cache() -> None:
    """Clear the adaptive context cache (tests / rare admin use). TTL handles normal expiry."""
    with _adaptive_context_cache_lock:
        _adaptive_context_cache.clear()


def invalidate_resolve_adaptive_context_cache(
    user_id: Optional[int], exercise_type: Optional[str]
) -> None:
    """Invalidate one cached adaptive-context entry after a Progress write."""
    if user_id is None or not exercise_type:
        return
    cache_key = (int(user_id), str(exercise_type).strip().lower())
    with _adaptive_context_cache_lock:
        _adaptive_context_cache.pop(cache_key, None)


# ---------------------------------------------------------------------------
# Mappings internes
# ---------------------------------------------------------------------------

_ORDINAL_TO_DIFFICULTY = {
    0: DifficultyLevels.INITIE,
    1: DifficultyLevels.PADAWAN,
    2: DifficultyLevels.CHEVALIER,
    3: DifficultyLevels.MAITRE,
    4: DifficultyLevels.GRAND_MAITRE,
}

_DIFFICULTY_TO_ORDINAL = {v: k for k, v in _ORDINAL_TO_DIFFICULTY.items()}

_ORDINAL_TO_AGE_GROUP = {
    0: AgeGroups.GROUP_6_8,
    1: AgeGroups.GROUP_9_11,
    2: AgeGroups.GROUP_12_14,
    3: AgeGroups.GROUP_15_17,
    4: AgeGroups.ADULT,
}

# Mapping preferred_difficulty string → ordinal.
# Couvre à la fois les DifficultyLevels ("GRAND_MAITRE") ET les age_group
# stockés dans le champ preferred_difficulty depuis l'onboarding ("adulte", "9-11"…).
_PREF_DIFFICULTY_TO_ORDINAL: Dict[str, int] = {
    # DifficultyLevels (valeurs normalisées backend)
    DifficultyLevels.INITIE: 0,
    DifficultyLevels.PADAWAN: 1,
    DifficultyLevels.CHEVALIER: 2,
    DifficultyLevels.MAITRE: 3,
    DifficultyLevels.GRAND_MAITRE: 4,
    # AgeGroups (valeurs stockées par l'onboarding frontend)
    AgeGroups.GROUP_6_8: 0,  # "6-8"   → INITIE
    AgeGroups.GROUP_9_11: 1,  # "9-11"  → PADAWAN
    AgeGroups.GROUP_12_14: 2,  # "12-14" → CHEVALIER
    AgeGroups.GROUP_15_17: 3,  # "15-17" → MAITRE
    AgeGroups.ADULT: 4,  # "adulte" → GRAND_MAITRE
}

# ---------------------------------------------------------------------------
# Types IRT — direct vs proxy
# ---------------------------------------------------------------------------

# Types évalués directement par le diagnostic IRT (F03) — clés en minuscules
IRT_DIRECT_TYPES = frozenset(
    {
        ExerciseTypes.ADDITION.lower(),
        ExerciseTypes.SUBTRACTION.lower(),
        ExerciseTypes.SOUSTRACTION.lower(),  # alias
        ExerciseTypes.MULTIPLICATION.lower(),
        ExerciseTypes.DIVISION.lower(),
    }
)

# Types non couverts par IRT mais qui ont un proxy calculé.
# Clés en minuscules (type_key normalisé dans _irt_ordinal_for_type).
# "min"  → minimum des scores IRT des 4 types de base
# list   → moyenne des scores IRT des types listés
IRT_PROXY_TYPES: Dict[str, object] = {
    ExerciseTypes.MIXTE.lower(): "min",  # mixte = niveau le plus faible
    ExerciseTypes.FRACTIONS.lower(): [
        ExerciseTypes.DIVISION.lower()
    ],  # fractions → niveau division (plus conservateur)
}
# GEOMETRIE, TEXTE, DIVERS → pas de proxy IRT ; voir IRT_SEEDED_TYPES + _seeded_ordinal_for_type

# Types sans score IRT par exercice : prior ordinal **seedé** depuis le profil (GAP 2 cold start).
# Ce n’est pas un modèle IRT continu (pas de paramètres a/b/c) — uniquement un ordinal cohérent
# avec la grille INITIE…GRAND_MAITRE pour éviter un ``resolve_irt_level`` systématiquement vide.
IRT_SEEDED_TYPES = frozenset(
    {
        ExerciseTypes.GEOMETRIE.lower(),
        ExerciseTypes.TEXTE.lower(),
        ExerciseTypes.DIVERS.lower(),
    }
)

# TEXTE / DIVERS : politique conservatrice — ne pas seed au-delà de MAITRE (ordinal 3) sans mesure IRT.
_SEEDED_TEXTE_DIVERS_MAX_ORDINAL = 3

# Mapping grade_level (1–12) → ordinal
_GRADE_TO_ORDINAL = {
    1: 0,
    2: 0,
    3: 0,
    4: 1,
    5: 1,
    6: 1,
    7: 2,
    8: 2,
    9: 2,
    10: 3,
    11: 3,
    12: 4,
}

# Seuils d'ajustement temps réel (Sweller 1988 / Csikszentmihalyi flow zone)
_BOOST_RATE_THRESHOLD = 85.0  # % → monter d'un niveau
_BOOST_STREAK_THRESHOLD = 3  # tentatives réussies consécutives minimum
_DESCENT_RATE_THRESHOLD = 50.0  # % → descendre d'un niveau
# streak = 0 signifie que la dernière tentative était incorrecte

# Validité du diagnostic IRT (en jours)
_IRT_MAX_AGE_DAYS = 30

# Seuil minimum de tentatives pour que la progression temps réel soit significative
_MIN_ATTEMPTS_FOR_REALTIME = 5

# Fenêtre temporelle pour la progression temps réel (en jours)
_REALTIME_WINDOW_DAYS = 7


# ---------------------------------------------------------------------------
# Fonctions internes
# ---------------------------------------------------------------------------


def _ordinal_to_age_group(ordinal: int) -> str:
    """Convertit un ordinal (0–4) en age_group canonique."""
    clamped = max(0, min(4, ordinal))
    return _ORDINAL_TO_AGE_GROUP[clamped]


def _mastery_to_ordinal(mastery_level: int) -> int:
    """
    Convertit le mastery_level de Progress (1–5) en ordinal difficulté (0–4).

    mastery_level 1 (< 50 %)  → INITIE (0)
    mastery_level 2 (50–70 %) → PADAWAN (1)
    mastery_level 3 (70–85 %) → CHEVALIER (2)
    mastery_level 4 (85–95 %) → MAITRE (3)
    mastery_level 5 (>= 95 %) → GRAND_MAITRE (4)
    """
    return max(0, min(4, mastery_level - 1))


def _adjust_for_realtime_progress(
    db: Session,
    user_id: int,
    exercise_type: str,
    base_ordinal: int,
) -> int:
    """
    Ajuste l'ordinal de base selon la progression récente de l'utilisateur.

    - Cherche la ligne Progress pour (user_id, exercise_type) sur les 7 derniers jours.
    - Si completion_rate > 85 % ET streak >= 3 → ordinal + 1 (boost)
    - Si completion_rate < 50 % ET streak = 0 → ordinal - 1 (descente)
    - Sinon → ordinal inchangé

    Renvoie l'ordinal ajusté (toujours entre 0 et 4).
    """
    try:
        window_start = datetime.now(timezone.utc) - timedelta(
            days=_REALTIME_WINDOW_DAYS
        )
        progress = (
            db.query(Progress)
            .filter(
                Progress.user_id == user_id,
                Progress.exercise_type == exercise_type.lower(),
                Progress.last_active_date >= window_start,
            )
            .first()
        )

        if progress is None or progress.total_attempts < _MIN_ATTEMPTS_FOR_REALTIME:
            return base_ordinal

        rate = progress.completion_rate or 0.0
        streak = progress.streak or 0

        if rate > _BOOST_RATE_THRESHOLD and streak >= _BOOST_STREAK_THRESHOLD:
            adjusted = min(4, base_ordinal + 1)
            logger.debug(
                "[AdaptiveDifficulty] user=%s type=%s "
                "boost %s→%s (rate=%.1f%% streak=%s)",
                user_id,
                exercise_type,
                base_ordinal,
                adjusted,
                rate,
                streak,
            )
            return adjusted

        if rate < _DESCENT_RATE_THRESHOLD and streak == 0:
            adjusted = max(0, base_ordinal - 1)
            logger.debug(
                "[AdaptiveDifficulty] user=%s type=%s "
                "descente %s→%s (rate=%.1f%% streak=%s)",
                user_id,
                exercise_type,
                base_ordinal,
                adjusted,
                rate,
                streak,
            )
            return adjusted

    except Exception as e:
        logger.warning(
            "[AdaptiveDifficulty] Erreur lecture progression user=%s: %s", user_id, e
        )

    return base_ordinal


# ---------------------------------------------------------------------------
# IRT score lookup — fonctions internes
# ---------------------------------------------------------------------------


def _get_irt_scores_if_valid(db: Session, user_id: int) -> Optional[Dict]:
    """
    Retourne le dict scores du dernier diagnostic IRT si < 30 jours, sinon None.
    Format : {"addition": {"level": 2, "difficulty": "CHEVALIER", ...}, ...}
    """
    try:
        from app.services.diagnostic.diagnostic_service import get_latest_score

        latest = get_latest_score(db, user_id)
        if not latest:
            return None
        completed_at = latest.get("completed_at")
        if not completed_at:
            return None
        if isinstance(completed_at, str):
            completed_at = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))
        if not completed_at.tzinfo:
            completed_at = completed_at.replace(tzinfo=timezone.utc)
        if (datetime.now(timezone.utc) - completed_at).days > _IRT_MAX_AGE_DAYS:
            return None
        return latest.get("scores") or {}
    except Exception as e:
        logger.warning(
            "[AdaptiveDifficulty] Erreur lecture IRT user=%s: %s", user_id, e
        )
        return None


def _irt_ordinal_for_type(scores: Dict, type_key: str) -> Optional[int]:
    """
    Résout l'ordinal IRT pour un type donné (direct ou via proxy).
    Retourne None si le type n'est pas couvert et n'a pas de proxy.
    """
    # 1. Score direct
    direct = scores.get(type_key)
    if direct:
        ordinal = _DIFFICULTY_TO_ORDINAL.get(direct.get("difficulty", ""))
        if ordinal is not None:
            return ordinal

    # 2. Proxy
    proxy = IRT_PROXY_TYPES.get(type_key)
    if proxy == "min":
        # Minimum des 4 types de base évalués
        base_keys = [
            ExerciseTypes.ADDITION.lower(),
            ExerciseTypes.SUBTRACTION.lower(),
            ExerciseTypes.MULTIPLICATION.lower(),
            ExerciseTypes.DIVISION.lower(),
        ]
        ordinals = [
            _DIFFICULTY_TO_ORDINAL[scores[k]["difficulty"]]
            for k in base_keys
            if k in scores and scores[k].get("difficulty") in _DIFFICULTY_TO_ORDINAL
        ]
        return min(ordinals) if ordinals else None
    elif isinstance(proxy, list):
        # Moyenne (arrondie vers le bas) des types listés
        ordinals = [
            _DIFFICULTY_TO_ORDINAL[scores[k.lower()]["difficulty"]]
            for k in proxy
            if k.lower() in scores
            and scores[k.lower()].get("difficulty") in _DIFFICULTY_TO_ORDINAL
        ]
        if ordinals:
            return int(sum(ordinals) / len(ordinals))

    return None


def _seeded_ordinal_for_type(db: Session, user_id: int, type_key: str) -> Optional[int]:
    """
    Prior ordinal **seedé** pour GEOMETRIE / TEXTE / DIVERS (cold start GAP 2).

    N'est **pas** une mesure issue d'un diagnostic IRT calibré (pas de paramètres a/b/c).
    Ordre de résolution (fail-open → None) :
      1. ``preferred_difficulty`` (même table de mapping que le reste du service)
      2. ``grade_level`` (1–12 → ordinal via ``_GRADE_TO_ORDINAL``)
      3. ``age_group`` persisté (via ``normalized_age_group_from_user_profile``)

    Pour TEXTE et DIVERS, l'ordinal est plafonné à MAITRE (ordinal 3) — pas de GRAND_MAITRE
    depuis le seul seed profil (politique conservatrice documentée produit).
    """
    if type_key not in IRT_SEEDED_TYPES:
        return None

    try:
        from app.models.user import User

        user = db.query(User).filter(User.id == user_id).first()
    except Exception as e:  # noqa: BLE001
        logger.warning(
            "[AdaptiveDifficulty] seeded_prior user lookup failed user_id=%s: %s",
            user_id,
            e,
        )
        return None

    if user is None:
        return None

    uid = getattr(user, "id", None)
    if not isinstance(uid, int):
        # Évite de traiter un MagicMock ou un stub de test comme un User réel.
        return None

    upstream: Optional[str] = None
    ordinal: Optional[int] = None

    try:
        preferred = getattr(user, "preferred_difficulty", None)
        if preferred:
            key = str(preferred).strip()
            if key in _PREF_DIFFICULTY_TO_ORDINAL:
                ordinal = _PREF_DIFFICULTY_TO_ORDINAL[key]
                upstream = "preferred_difficulty"

        if ordinal is None:
            grade = getattr(user, "grade_level", None)
            if grade is not None and isinstance(grade, int):
                gord = _GRADE_TO_ORDINAL.get(grade)
                if gord is not None:
                    ordinal = gord
                    upstream = "grade_level"

        if ordinal is None:
            ag = normalized_age_group_from_user_profile(user)
            if ag and ag in _PREF_DIFFICULTY_TO_ORDINAL:
                ordinal = _PREF_DIFFICULTY_TO_ORDINAL[ag]
                upstream = "age_group"

        if ordinal is None:
            return None

        if type_key in (
            ExerciseTypes.TEXTE.lower(),
            ExerciseTypes.DIVERS.lower(),
        ):
            ordinal = min(ordinal, _SEEDED_TEXTE_DIVERS_MAX_ORDINAL)

        ordinal = max(0, min(4, ordinal))

        logger.info(
            "[AdaptiveDifficulty] resolve_irt_level user_id={} exercise_type={} "
            "source=seeded_prior ordinal={} upstream={} "
            "(ordinal seed from profile — not a calibrated IRT score)",
            user_id,
            type_key,
            ordinal,
            upstream,
        )
        return ordinal
    except Exception as e:  # noqa: BLE001
        logger.warning(
            "[AdaptiveDifficulty] seeded_prior failed user_id=%s type=%s: %s",
            user_id,
            type_key,
            e,
        )
        return None


# ---------------------------------------------------------------------------
# Point d'entrée public — niveau IRT par type
# ---------------------------------------------------------------------------


def resolve_irt_level(db: Session, user_id: int, exercise_type: str) -> Optional[str]:
    """
    Retourne la difficulté IRT résolue (ex: "GRAND_MAITRE") pour un utilisateur
    et un type d'exercice, ou None si aucun score IRT disponible/applicable.

    Utilisé par :
      - resolve_adaptive_difficulty() (étape 1 de la cascade)
      - L'endpoint GET /api/exercises/irt-level (consommé par le frontend
        pour décider du mode de réponse QCM vs saisie libre)

    Types directs  : ADDITION, SOUSTRACTION, MULTIPLICATION, DIVISION
    Types proxys   : MIXTE (min des 4), FRACTIONS (proxy division)
    Types sans IRT par exercice : GEOMETRIE, TEXTE, DIVERS → prior **seedé** (profil,
    ``source=seeded_prior`` dans les logs) si aucun ordinal IRT/proxy ; sinon None.
    """
    type_key = exercise_type.lower()
    ordinal: Optional[int] = None

    scores = _get_irt_scores_if_valid(db, user_id)
    if scores is not None:
        ordinal = _irt_ordinal_for_type(scores, type_key)
        if ordinal is not None:
            return _ORDINAL_TO_DIFFICULTY.get(ordinal)

    if type_key in IRT_SEEDED_TYPES:
        seeded = _seeded_ordinal_for_type(db, user_id, type_key)
        if seeded is not None:
            return _ORDINAL_TO_DIFFICULTY.get(seeded)

    return None


# ---------------------------------------------------------------------------
# Point d'entrée public — résolution complète de difficulté adaptative
# ---------------------------------------------------------------------------


def resolve_adaptive_difficulty(
    db: Session,
    user,
    exercise_type: str,
) -> str:
    """
    Retourne l'age_group adaptatif pour l'utilisateur et le type d'exercice demandé.

    Cascade de priorités :
      1. Diagnostic IRT (get_latest_score) — si < 30 jours et type évalué
      2. Progression temps réel (Progress) — si >= 5 tentatives sur 7 jours
      3. Profil utilisateur (preferred_difficulty / grade_level)
      4. Fallback GROUP_9_11 (PADAWAN)

    Args:
        db:            Session SQLAlchemy active.
        user:          Objet User SQLAlchemy (doit avoir .id, .preferred_difficulty, .grade_level).
        exercise_type: Type normalisé (ex: "ADDITION").

    Returns:
        age_group canonique (ex: "GROUP_9_11").
    """
    user_id = getattr(user, "id", None)
    if user_id is None:
        return AgeGroups.GROUP_9_11

    type_key = exercise_type.lower()

    # ------------------------------------------------------------------
    # 1. Diagnostic IRT (direct + proxy MIXTE/FRACTIONS)
    # ------------------------------------------------------------------
    try:
        scores = _get_irt_scores_if_valid(db, user_id)
        if scores is not None:
            ordinal = _irt_ordinal_for_type(scores, type_key)
            if ordinal is not None:
                difficulty = _ORDINAL_TO_DIFFICULTY.get(ordinal, "")
                ordinal = _adjust_for_realtime_progress(db, user_id, type_key, ordinal)
                age_group = _ordinal_to_age_group(ordinal)
                logger.debug(
                    "[AdaptiveDifficulty] user=%s type=%s → IRT %s (ordinal=%s) → %s",
                    user_id,
                    exercise_type,
                    difficulty,
                    ordinal,
                    age_group,
                )
                return age_group
    except Exception as e:
        logger.warning(
            "[AdaptiveDifficulty] Erreur lecture diagnostic IRT user=%s: %s", user_id, e
        )

    # ------------------------------------------------------------------
    # 2. Progression temps réel
    # ------------------------------------------------------------------
    try:
        window_start = datetime.now(timezone.utc) - timedelta(
            days=_REALTIME_WINDOW_DAYS
        )
        progress = (
            db.query(Progress)
            .filter(
                Progress.user_id == user_id,
                Progress.exercise_type == type_key,
                Progress.last_active_date >= window_start,
            )
            .first()
        )
        if progress and progress.total_attempts >= _MIN_ATTEMPTS_FOR_REALTIME:
            ordinal = _mastery_to_ordinal(progress.mastery_level or 1)
            ordinal = _adjust_for_realtime_progress(db, user_id, type_key, ordinal)
            age_group = _ordinal_to_age_group(ordinal)
            logger.debug(
                "[AdaptiveDifficulty] user=%s type=%s → Progress mastery=%s (ordinal=%s) → %s",
                user_id,
                exercise_type,
                progress.mastery_level,
                ordinal,
                age_group,
            )
            return age_group
    except Exception as e:
        logger.warning(
            "[AdaptiveDifficulty] Erreur lecture progression user=%s: %s", user_id, e
        )

    # ------------------------------------------------------------------
    # 3. Profil utilisateur
    # ------------------------------------------------------------------
    try:
        persisted_ag = normalized_age_group_from_user_profile(user)
        if persisted_ag:
            logger.debug(
                "[AdaptiveDifficulty] user=%s type=%s → users.age_group → %s",
                user_id,
                exercise_type,
                persisted_ag,
            )
            return persisted_ag

        preferred = getattr(user, "preferred_difficulty", None)
        if preferred:
            ordinal = _PREF_DIFFICULTY_TO_ORDINAL.get(preferred)
            if ordinal is not None:
                age_group = _ordinal_to_age_group(ordinal)
                logger.debug(
                    "[AdaptiveDifficulty] user=%s type=%s → preferred_difficulty=%s → %s",
                    user_id,
                    exercise_type,
                    preferred,
                    age_group,
                )
                return age_group

        grade = getattr(user, "grade_level", None)
        if grade and isinstance(grade, int):
            ordinal = _GRADE_TO_ORDINAL.get(grade, 1)
            age_group = _ordinal_to_age_group(ordinal)
            logger.debug(
                "[AdaptiveDifficulty] user=%s type=%s → grade_level=%s → %s",
                user_id,
                exercise_type,
                grade,
                age_group,
            )
            return age_group
    except Exception as e:
        logger.warning(
            "[AdaptiveDifficulty] Erreur lecture profil user=%s: %s", user_id, e
        )

    # ------------------------------------------------------------------
    # 4. Fallback
    # ------------------------------------------------------------------
    logger.debug(
        "[AdaptiveDifficulty] user=%s type=%s → fallback PADAWAN",
        user_id,
        exercise_type,
    )
    return AgeGroups.GROUP_9_11


# ---------------------------------------------------------------------------
# Second axis: pedagogical band from mastery — C2 single source (bridge)
# ---------------------------------------------------------------------------

_PEDAGOGICAL_BAND_LABELS = ("discovery", "learning", "consolidation")


def _band_from_mastery_level(mastery_level: Optional[int]) -> str:
    """Map Progress.mastery_level (1–5) → pedagogical_band string."""
    return mastery_level_int_to_pedagogical_band(mastery_level)


def _resolve_band_from_progress(
    db: Session, user_id: int, exercise_type: str
) -> Optional[str]:
    """
    Attempt to resolve a pedagogical band from the user's Progress record.

    Returns "discovery" | "learning" | "consolidation", or None if no
    sufficiently rich Progress record is found.
    """
    try:
        window_start = datetime.now(timezone.utc) - timedelta(
            days=_REALTIME_WINDOW_DAYS
        )
        progress = (
            db.query(Progress)
            .filter(
                Progress.user_id == user_id,
                Progress.exercise_type == exercise_type.lower(),
                Progress.last_active_date >= window_start,
            )
            .first()
        )
        if progress and progress.total_attempts >= _MIN_ATTEMPTS_FOR_REALTIME:
            band = _band_from_mastery_level(progress.mastery_level)
            logger.debug(
                "[AdaptiveDifficulty] user=%s type=%s mastery=%s → band=%s",
                user_id,
                exercise_type,
                progress.mastery_level,
                band,
            )
            return band
    except Exception as e:  # noqa: BLE001
        logger.warning(
            "[AdaptiveDifficulty] Erreur lecture bande mastery user=%s: %s",
            user_id,
            e,
        )
    return None


def _resolve_band_from_irt(
    db: Session,
    user_id: int,
    exercise_type: str,
) -> Optional[str]:
    """
    Resolve a pedagogical band from the latest valid IRT diagnostic.

    This preserves the previous adaptive signal when no recent ``Progress`` row
    is available, while keeping the age axis stable in the F42 path.
    """
    irt_level = resolve_irt_level(db, user_id, exercise_type)
    if irt_level is None:
        return None
    band_idx = pedagogical_band_index_from_difficulty(irt_level)
    if band_idx is None:
        return None
    return _PEDAGOGICAL_BAND_LABELS[band_idx]


# ---------------------------------------------------------------------------
# Public entry point — rich context (age_group + pedagogical_band)
# ---------------------------------------------------------------------------


def _resolve_adaptive_context_impl(
    db: Session,
    user,
    exercise_type: str,
) -> AdaptiveGenerationContext:
    """
    Uncached resolution — see :func:`resolve_adaptive_context` for the contract.
    """
    user_id = getattr(user, "id", None)

    # ------------------------------------------------------------------
    # Step 1: stable base age_group (NOT remapped by mastery)
    # ------------------------------------------------------------------
    # We deliberately do NOT call resolve_adaptive_difficulty() here because
    # that function already uses mastery/IRT to remap the age_group, which
    # would conflate the two axes and prevent "same age, different band".
    age_group = _resolve_stable_age_group(user)

    # ------------------------------------------------------------------
    # Step 2: pedagogical_band from mastery data (second axis)
    # ------------------------------------------------------------------
    if user_id is not None:
        band = _resolve_band_from_progress(db, user_id, exercise_type)
        if band is not None:
            return AdaptiveGenerationContext(
                age_group=age_group,
                pedagogical_band=band,
                mastery_source="progress_mastery",
            )

        band = _resolve_band_from_irt(db, user_id, exercise_type)
        if band is not None:
            return AdaptiveGenerationContext(
                age_group=age_group,
                pedagogical_band=band,
                mastery_source="irt_diagnostic",
            )

    # ------------------------------------------------------------------
    # Step 3: cold-start band (F42-P2a) — see ``COLD_START_PEDAGOGICAL_BAND``.
    # Applies when there is no qualifying Progress row and no IRT band.
    # ------------------------------------------------------------------
    return AdaptiveGenerationContext(
        age_group=age_group,
        pedagogical_band=COLD_START_PEDAGOGICAL_BAND,
        mastery_source="fallback",
    )


def resolve_adaptive_context(
    db: Session,
    user,
    exercise_type: str,
) -> AdaptiveGenerationContext:
    """
    Resolve a full :class:`AdaptiveGenerationContext` for F42 generation.

    This is the **second-axis entry point**.  It separates two independent signals:

    1. **Base age_group** — resolved from the user's *stable profile*
       (``users.age_group`` → ``preferred_difficulty`` → ``grade_level`` → fallback).
       This age does NOT change with mastery: two learners with the same profile
       age always share the same base age_group in this path.

    2. **Pedagogical band** — resolved from ``Progress.mastery_level`` for the
       requested exercise type.  Two learners with the same profile age but
       different mastery levels receive *different* bands, and therefore different
       F42 tiers and different calibration bounds.

    This separation is the key invariant of the F42 second axis:
      ``same age_group, different mastery → different band → different tier``.

    Cascade for the base age_group (stable, mastery-independent):
      1. ``users.age_group`` if set
      2. ``preferred_difficulty`` if set
      3. ``grade_level`` if set
      4. Fallback GROUP_9_11

    Cascade for the pedagogical band:
      1. ``Progress.mastery_level`` if >= 5 recent attempts
      2. Latest valid IRT diagnostic (mapped to discovery / learning / consolidation)
      3. Fallback ``COLD_START_PEDAGOGICAL_BAND`` (F42-P2a)

    Results are cached in-process for ``_ADAPTIVE_CONTEXT_CACHE_TTL_SEC`` seconds
    per (``user_id``, ``exercise_type``) — F42-P2b.

    This function does NOT modify the public HTTP contract.
    """
    user_id = getattr(user, "id", None)
    type_key = exercise_type.strip().lower()

    if user_id is None:
        ctx = replace(_resolve_adaptive_context_impl(db, user, exercise_type))
        logger.info(
            "f43_adaptive_context: user_id=null exercise_type=%%s mastery_source=%%s pedagogical_band=%%s",
            type_key,
            ctx.mastery_source,
            ctx.pedagogical_band,
        )
        return ctx

    cache_key = (int(user_id), type_key)
    now = time.monotonic()
    with _adaptive_context_cache_lock:
        entry = _adaptive_context_cache.get(cache_key)
        if entry is not None:
            expires_at, ctx = entry
            if now < expires_at:
                return replace(ctx)
        ctx = _resolve_adaptive_context_impl(db, user, exercise_type)
        # F43-A1 — log once per cache fill (≈ at most once per TTL per user/type).
        logger.info(
            "f43_adaptive_context: user_id=%%s exercise_type=%%s mastery_source=%%s pedagogical_band=%%s",
            int(user_id),
            type_key,
            ctx.mastery_source,
            ctx.pedagogical_band,
        )
        _adaptive_context_cache[cache_key] = (
            now + _ADAPTIVE_CONTEXT_CACHE_TTL_SEC,
            ctx,
        )
        return replace(ctx)


def _resolve_stable_age_group(user) -> str:
    """
    Resolve the stable base age_group from the user profile WITHOUT using
    mastery/IRT data.  This is the age axis for F42 generation — it must not
    be remapped by mastery so that the two axes remain independent.

    Cascade (mirrors steps 3 & 4 of resolve_adaptive_difficulty):
      1. users.age_group (F42 persisted)
      2. preferred_difficulty / preferred age_group
      3. grade_level
      4. Fallback GROUP_9_11
    """
    try:
        persisted_ag = normalized_age_group_from_user_profile(user)
        if persisted_ag:
            return persisted_ag

        preferred = getattr(user, "preferred_difficulty", None)
        if preferred:
            ordinal = _PREF_DIFFICULTY_TO_ORDINAL.get(preferred)
            if ordinal is not None:
                return _ordinal_to_age_group(ordinal)

        grade = getattr(user, "grade_level", None)
        if grade and isinstance(grade, int):
            ordinal = _GRADE_TO_ORDINAL.get(grade, 1)
            return _ordinal_to_age_group(ordinal)
    except Exception as e:  # noqa: BLE001
        logger.warning("[AdaptiveDifficulty] Erreur lecture profil stable user: %s", e)

    return AgeGroups.GROUP_9_11
