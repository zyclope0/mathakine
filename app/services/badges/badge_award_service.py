"""
Vérification et attribution des badges (B3.1/B3.2).

Orchestrateur : moteur générique + fallback par code.
Délègue à badge_requirement_fallbacks, badge_award_persistence, badge_gamification_updates.
"""

import json
from typing import Any, Dict, List

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.models.achievement import Achievement, UserAchievement
from app.services.badges.badge_award_persistence import award_badge
from app.services.badges.badge_gamification_updates import update_user_gamification
from app.services.badges.badge_requirement_engine import check_requirements
from app.services.badges.badge_requirement_fallbacks import (
    check_badge_requirements_by_code,
)
from app.services.badges.badge_stats_cache import build_stats_cache
from app.services.users.user_service import UserService

logger = get_logger(__name__)


class BadgeAwardService:
    """Orchestrateur : vérification et attribution des badges mérités."""

    def __init__(self, db: Session, *, auto_commit: bool = True):
        self.db = db
        self.auto_commit = auto_commit

    def _flush_or_commit(self) -> None:
        if self.auto_commit:
            self.db.commit()
        else:
            self.db.flush()

    def _rollback_if_needed(self) -> None:
        if self.auto_commit:
            self.db.rollback()

    def check_and_award_badges(
        self, user_id: int, attempt_data: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Vérifier et attribuer les badges mérités par un utilisateur."""
        savepoint = self.db.begin_nested() if not self.auto_commit else None
        try:
            user = UserService.get_user(self.db, user_id)
            if not user:
                logger.error("Utilisateur %s non trouvé", user_id)
                return []

            available_badges = (
                self.db.query(Achievement).filter(Achievement.is_active.is_(True)).all()
            )
            earned_badge_ids = set(
                badge_id[0]
                for badge_id in self.db.query(UserAchievement.achievement_id)
                .filter(UserAchievement.user_id == user_id)
                .all()
            )
            stats_cache = build_stats_cache(self.db, user_id)

            new_badges = []
            for badge in available_badges:
                if badge.id not in earned_badge_ids:
                    if self._check_badge_requirements(
                        user_id, badge, attempt_data, stats_cache
                    ):
                        new_badge = award_badge(
                            self.db,
                            user_id,
                            badge,
                            flush_fn=self._flush_or_commit,
                            rollback_fn=self._rollback_if_needed,
                            auto_commit=self.auto_commit,
                        )
                        if new_badge:
                            new_badges.append(new_badge)
                            logger.info(
                                "🎖️ Badge '%s' attribué à l'utilisateur %s",
                                badge.name,
                                user_id,
                            )

            if new_badges:
                update_user_gamification(
                    self.db,
                    user_id,
                    new_badges,
                    flush_fn=self._flush_or_commit,
                    rollback_fn=self._rollback_if_needed,
                    auto_commit=self.auto_commit,
                )

            if savepoint and savepoint.is_active:
                savepoint.commit()
            return new_badges

        except SQLAlchemyError as badge_check_error:
            if savepoint and savepoint.is_active:
                savepoint.rollback()
            else:
                self._rollback_if_needed()
            logger.error(
                "Erreur DB lors de la vérification des badges pour l'utilisateur %s: %s",
                user_id,
                badge_check_error,
            )
            return []
        except (TypeError, ValueError) as badge_check_error:
            if savepoint and savepoint.is_active:
                savepoint.rollback()
            else:
                self._rollback_if_needed()
            logger.error(
                "Erreur de données lors de la vérification des badges pour l'utilisateur %s: %s",
                user_id,
                badge_check_error,
            )
            return []

    def _check_badge_requirements(
        self,
        user_id: int,
        badge: Achievement,
        attempt_data: Dict[str, Any] = None,
        stats_cache: Dict[str, Any] = None,
    ) -> bool:
        """Vérifier si un utilisateur remplit les conditions pour un badge."""
        if not badge.requirements:
            return False
        try:
            requirements = (
                json.loads(badge.requirements)
                if isinstance(badge.requirements, str)
                else badge.requirements
            )
        except (json.JSONDecodeError, TypeError):
            logger.error("Requirements invalides pour le badge %s", badge.code)
            return False
        if not isinstance(requirements, dict):
            return False

        result = check_requirements(
            self.db, user_id, requirements, attempt_data, stats_cache
        )
        if result is not None:
            return result
        return check_badge_requirements_by_code(
            self.db, user_id, badge, requirements, attempt_data
        )
