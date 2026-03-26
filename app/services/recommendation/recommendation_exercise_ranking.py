"""
R3 — Sélection d'exercices pour recommandations : classement déterministe + anti-répétition.

Stratégie (tuple de tri croissant = meilleur en premier) :
  1. Pénalité : exercices déjà recommandés récemment (fenêtre bornée) → triés après.
  2. Âge : correspondance ``age_group`` exercice / profil utilisateur → préférés.
  3. ``view_count`` croissant : légère préférence aux contenus moins « vus ».
  4. ``-id`` (entier) : tie-break stable — parmi équivalents, **plus grand id** (= plus récent)
     dans la fenêtre ``ORDER BY id DESC LIMIT N`` ; évite de toujours figer les plus vieux ids
     du lot récent.

Aucun ``func.random()`` ici : l'ordre est entièrement reproductible pour un même contexte.
L'anti-répétition utilise uniquement les colonnes existantes de ``Recommendation`` (pas de migration).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Iterable, List, Optional, Set

from sqlalchemy.orm import Session

from app.core.constants import AgeGroups
from app.models.exercise import Exercise
from app.models.recommendation import Recommendation

# Fenêtre anti-répétition (recommandations exercice avec exercise_id renseigné)
RECENT_RECOMMENDATION_LOOKBACK_DAYS = 14

# Limite de candidats chargés avant tri Python (borne le coût)
MAX_CANDIDATES_TO_RANK = 150


def collect_recent_recommended_exercise_ids(db: Session, user_id: int) -> Set[int]:
    """
    Exercices déjà présents dans une reco exercice récente pour cet utilisateur.

    À appeler **avant** la suppression des recommandations incomplètes, pour inclure
    aussi la vague courante dans la pénalité.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(
        days=RECENT_RECOMMENDATION_LOOKBACK_DAYS
    )
    rows = (
        db.query(Recommendation.exercise_id)
        .filter(
            Recommendation.user_id == user_id,
            Recommendation.exercise_id.isnot(None),
            Recommendation.recommendation_type == "exercise",
            Recommendation.created_at >= cutoff,
        )
        .all()
    )
    return {eid for (eid,) in rows if eid is not None}


def exercise_fits_user_age_bucket(exercise: Exercise, user_age_group: str) -> bool:
    """True si l'exercice est dans le ou les groupes d'âge attendus pour l'utilisateur."""
    if user_age_group == AgeGroups.ALL_AGES:
        return True
    allowed = set(AgeGroups.AGE_ALIASES.get(user_age_group, [user_age_group]))
    allowed = {str(x).lower() for x in allowed}
    allowed.update({"tous-ages", "tous ages", "all_ages"})
    ag = str(exercise.age_group or "").lower().strip()
    return ag in allowed


def exercise_rank_sort_key(
    exercise: Exercise,
    user_age_group: str,
    penalized_exercise_ids: Set[int],
    user_target_tier: Optional[int] = None,
) -> tuple:
    """
    Clé de tri croissante : les meilleurs candidats ont la plus petite clé.

    Ordre :
      - non pénalisé (0) avant pénalisé (1)
      - correspondance âge (0) avant hors bucket (1)
      - distance tier F42 (0 = meilleur) si ``user_target_tier`` et ``difficulty_tier`` connus
      - view_count croissant
      - ``-id`` : tie-break final stable (id le plus élevé = meilleur parmi équivalents)
    """
    penalized_tier = 1 if exercise.id in penalized_exercise_ids else 0
    age_tier = 0 if exercise_fits_user_age_bucket(exercise, user_age_group) else 1
    if (
        user_target_tier is not None
        and getattr(exercise, "difficulty_tier", None) is not None
    ):
        tier_dist = abs(int(exercise.difficulty_tier) - int(user_target_tier))
    else:
        tier_dist = 0
    view = exercise.view_count or 0
    eid = exercise.id if exercise.id is not None else 0
    return (penalized_tier, age_tier, tier_dist, view, -eid)


def select_top_ranked_exercises(
    candidates: Iterable[Exercise],
    user_age_group: str,
    penalized_exercise_ids: Set[int],
    limit: int,
    user_target_tier: Optional[int] = None,
) -> List[Exercise]:
    """Trie les candidats selon ``exercise_rank_sort_key`` et retourne les ``limit`` premiers."""
    if limit <= 0:
        return []
    items = list(candidates)
    if not items:
        return []
    items.sort(
        key=lambda e: exercise_rank_sort_key(
            e, user_age_group, penalized_exercise_ids, user_target_tier
        )
    )
    return items[:limit]
