"""
Façade applicative pour les mutations admin users/config (LOT 5)
et admin content (LOT 6).

Centralise l'ouverture DB, l'orchestration admin/auth/user/content et le wiring
des mutations. Les handlers ne font que : parse request, validation minimale,
appel façade, mapping HTTP.
"""

from typing import Any, Dict, List, Optional, Tuple

from app.services.admin_service import AdminService
from app.utils.db_utils import db_session


class AdminApplicationService:
    """Façade pour les mutations admin users/config et content."""

    @staticmethod
    async def update_config(
        settings_in: Dict[str, Any], admin_user_id: Optional[int]
    ) -> None:
        """PUT /api/admin/config — met à jour les paramètres globaux."""
        async with db_session() as db:
            AdminService.update_config(db, settings_in, admin_user_id)

    @staticmethod
    async def patch_user(
        user_id: int,
        admin_user_id: int,
        data: Dict[str, Any],
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
        """
        PATCH /api/admin/users/{user_id} — mise à jour is_active et/ou role.

        Returns:
            (result_dict, error_message, status_code)
        """
        async with db_session() as db:
            return AdminService.validate_and_patch_user(
                db,
                user_id=user_id,
                admin_user_id=admin_user_id,
                data=data,
            )

    @staticmethod
    async def send_reset_password(user_id: int) -> Tuple[bool, Optional[str], int]:
        """
        POST /api/admin/users/{user_id}/send-reset-password.

        Returns:
            (success, error_message, status_code)
        """
        async with db_session() as db:
            return AdminService.send_reset_password_for_admin(db, user_id)

    @staticmethod
    async def resend_verification(
        user_id: int,
    ) -> Tuple[bool, bool, Optional[str], int]:
        """
        POST /api/admin/users/{user_id}/resend-verification.

        Returns:
            (success, already_verified, error_message, status_code)
        """
        async with db_session() as db:
            return AdminService.resend_verification_for_admin(db, user_id)

    @staticmethod
    async def delete_user(
        user_id: int, admin_user_id: int
    ) -> Tuple[bool, Optional[str], int]:
        """
        DELETE /api/admin/users/{user_id} — suppression définitive.

        Returns:
            (success, error_message, status_code)
        """
        async with db_session() as db:
            return AdminService.delete_user_for_admin(
                db, user_id=user_id, admin_user_id=admin_user_id
            )

    # ── Content (LOT 6) ───────────────────────────────────────────────────

    @staticmethod
    async def create_exercise_for_admin(
        data: Dict[str, Any], admin_user_id: Optional[int]
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
        """POST /api/admin/exercises — création d'un exercice."""
        async with db_session() as db:
            return AdminService.create_exercise_for_admin(
                db, data=data, admin_user_id=admin_user_id
            )

    @staticmethod
    async def put_exercise_for_admin(
        exercise_id: str,
        data: Dict[str, Any],
        admin_user_id: Optional[int],
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
        """PUT /api/admin/exercises/{exercise_id} — mise à jour complète."""
        async with db_session() as db:
            return AdminService.put_exercise_for_admin(
                db,
                exercise_id=exercise_id,
                data=data,
                admin_user_id=admin_user_id,
            )

    @staticmethod
    async def duplicate_exercise_for_admin(
        exercise_id: str, admin_user_id: Optional[int]
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
        """POST /api/admin/exercises/{exercise_id}/duplicate — crée une copie."""
        async with db_session() as db:
            return AdminService.duplicate_exercise_for_admin(
                db, exercise_id=exercise_id, admin_user_id=admin_user_id
            )

    @staticmethod
    async def patch_exercise_for_admin(
        exercise_id: str,
        is_archived: bool,
        admin_user_id: Optional[int],
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
        """PATCH /api/admin/exercises/{exercise_id} — toggle is_archived."""
        async with db_session() as db:
            return AdminService.patch_exercise_for_admin(
                db,
                exercise_id=exercise_id,
                is_archived=is_archived,
                admin_user_id=admin_user_id,
            )

    @staticmethod
    async def create_badge_for_admin(
        data: Dict[str, Any], admin_user_id: Optional[int]
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
        """POST /api/admin/badges — création d'un badge."""
        async with db_session() as db:
            return AdminService.create_badge_for_admin(
                db, data=data, admin_user_id=admin_user_id
            )

    @staticmethod
    async def put_badge_for_admin(
        badge_id: str,
        data: Dict[str, Any],
        admin_user_id: Optional[int],
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
        """PUT /api/admin/badges/{badge_id} — mise à jour complète."""
        async with db_session() as db:
            return AdminService.put_badge_for_admin(
                db,
                badge_id=badge_id,
                data=data,
                admin_user_id=admin_user_id,
            )

    @staticmethod
    async def delete_badge_for_admin(
        badge_id: str, admin_user_id: Optional[int]
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
        """DELETE /api/admin/badges/{badge_id} — soft delete."""
        async with db_session() as db:
            return AdminService.delete_badge_for_admin(
                db, badge_id=badge_id, admin_user_id=admin_user_id
            )

    @staticmethod
    async def create_challenge_for_admin(
        data: Dict[str, Any], admin_user_id: Optional[int]
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
        """POST /api/admin/challenges — création d'un défi."""
        async with db_session() as db:
            return AdminService.create_challenge_for_admin(
                db, data=data, admin_user_id=admin_user_id
            )

    @staticmethod
    async def put_challenge_for_admin(
        challenge_id: str,
        data: Dict[str, Any],
        admin_user_id: Optional[int],
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
        """PUT /api/admin/challenges/{challenge_id} — mise à jour complète."""
        async with db_session() as db:
            return AdminService.put_challenge_for_admin(
                db,
                challenge_id=challenge_id,
                data=data,
                admin_user_id=admin_user_id,
            )

    @staticmethod
    async def duplicate_challenge_for_admin(
        challenge_id: str, admin_user_id: Optional[int]
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
        """POST /api/admin/challenges/{challenge_id}/duplicate — crée une copie."""
        async with db_session() as db:
            return AdminService.duplicate_challenge_for_admin(
                db, challenge_id=challenge_id, admin_user_id=admin_user_id
            )

    @staticmethod
    async def patch_challenge_for_admin(
        challenge_id: str,
        is_archived: bool,
        admin_user_id: Optional[int],
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
        """PATCH /api/admin/challenges/{challenge_id} — toggle is_archived."""
        async with db_session() as db:
            return AdminService.patch_challenge_for_admin(
                db,
                challenge_id=challenge_id,
                is_archived=is_archived,
                admin_user_id=admin_user_id,
            )

    @staticmethod
    async def export_csv_data_for_admin(
        export_type: str,
        period: str,
        admin_user_id: Optional[int],
    ) -> Tuple[List[str], List[List[Any]]]:
        """GET /api/admin/export — préparation métier (headers + rows)."""
        async with db_session() as db:
            return AdminService.export_csv_data_for_admin(
                db,
                export_type=export_type,
                period=period,
                admin_user_id=admin_user_id,
            )
