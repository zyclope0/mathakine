"""
Façade applicative pour les mutations admin users/config (LOT 5)
et admin content (LOT 6).

Centralise l'ouverture DB, l'orchestration admin/auth/user/content et le wiring
des mutations. Les handlers ne font que : parse request, validation minimale,
appel façade via run_db_bound, mapping HTTP.

LOT A6 : sync + sync_db_session, exécuté via run_db_bound() depuis les handlers.
LOT B2 : contrats explicites (AdminError, result models) à la place des tuples.
"""

from typing import Any, Dict, List, Optional

from app.core.db_boundary import sync_db_session
from app.schemas.admin import (
    AdminActionSuccess,
    AdminError,
    AdminExportDataResult,
    AdminResendVerificationResult,
    AdminUserMutationResult,
)
from app.services.admin.admin_service import AdminService


class AdminApplicationService:
    """Façade pour les mutations admin users/config et content."""

    @staticmethod
    def update_config(
        settings_in: Dict[str, Any], admin_user_id: Optional[int]
    ) -> None:
        """PUT /api/admin/config — met à jour les paramètres globaux."""
        with sync_db_session() as db:
            AdminService.update_config(db, settings_in, admin_user_id)

    @staticmethod
    def patch_user(
        user_id: int,
        admin_user_id: int,
        data: Dict[str, Any],
    ) -> AdminUserMutationResult:
        """
        PATCH /api/admin/users/{user_id} — mise à jour is_active et/ou role.
        Lève AdminError en cas d'erreur.
        """
        with sync_db_session() as db:
            result, err, code = AdminService.validate_and_patch_user(
                db,
                user_id=user_id,
                admin_user_id=admin_user_id,
                data=data,
            )
            if err:
                raise AdminError(err, code)
            return AdminUserMutationResult.model_validate(result)

    @staticmethod
    def send_reset_password(user_id: int) -> AdminActionSuccess:
        """
        POST /api/admin/users/{user_id}/send-reset-password.
        Lève AdminError en cas d'erreur.
        """
        with sync_db_session() as db:
            result = AdminService.send_reset_password_for_admin(db, user_id)
            if not result.success:
                raise AdminError(result.error or "Erreur inconnue", result.status_code)
            return AdminActionSuccess(message="Email de réinitialisation envoyé.")

    @staticmethod
    def resend_verification(user_id: int) -> AdminResendVerificationResult:
        """
        POST /api/admin/users/{user_id}/resend-verification.
        Lève AdminError en cas d'erreur.
        """
        with sync_db_session() as db:
            result = AdminService.resend_verification_for_admin(db, user_id)
            if not result.success:
                raise AdminError(result.error or "Erreur inconnue", result.status_code)
            message = (
                "L'email est déjà vérifié."
                if result.already_verified
                else "Email de vérification envoyé."
            )
            return AdminResendVerificationResult(
                already_verified=result.already_verified, message=message
            )

    @staticmethod
    def delete_user(user_id: int, admin_user_id: int) -> AdminActionSuccess:
        """
        DELETE /api/admin/users/{user_id} — suppression définitive.
        Lève AdminError en cas d'erreur.
        """
        with sync_db_session() as db:
            result = AdminService.delete_user_for_admin(
                db, user_id=user_id, admin_user_id=admin_user_id
            )
            if not result.success:
                raise AdminError(
                    result.error or "Erreur lors de la suppression.",
                    result.status_code,
                )
            return AdminActionSuccess(message="Utilisateur supprimé.")

    # ── Content (LOT 6) ───────────────────────────────────────────────────

    @staticmethod
    def create_exercise_for_admin(
        data: Dict[str, Any], admin_user_id: Optional[int]
    ) -> Dict[str, Any]:
        """POST /api/admin/exercises — création d'un exercice. Lève AdminError si erreur."""
        with sync_db_session() as db:
            result, err, code = AdminService.create_exercise_for_admin(
                db, data=data, admin_user_id=admin_user_id
            )
            if err:
                raise AdminError(err, code)
            return result

    @staticmethod
    def put_exercise_for_admin(
        exercise_id: int,
        data: Dict[str, Any],
        admin_user_id: Optional[int],
    ) -> Dict[str, Any]:
        """PUT /api/admin/exercises/{exercise_id} — mise à jour complète. Lève AdminError si erreur."""
        with sync_db_session() as db:
            result, err, code = AdminService.put_exercise_for_admin(
                db,
                exercise_id=exercise_id,
                data=data,
                admin_user_id=admin_user_id,
            )
            if err:
                raise AdminError(err, code)
            return result

    @staticmethod
    def duplicate_exercise_for_admin(
        exercise_id: int, admin_user_id: Optional[int]
    ) -> Dict[str, Any]:
        """POST /api/admin/exercises/{exercise_id}/duplicate — crée une copie. Lève AdminError si erreur."""
        with sync_db_session() as db:
            result, err, code = AdminService.duplicate_exercise_for_admin(
                db, exercise_id=exercise_id, admin_user_id=admin_user_id
            )
            if err:
                raise AdminError(err, code)
            return result

    @staticmethod
    def patch_exercise_for_admin(
        exercise_id: int,
        is_archived: bool,
        admin_user_id: Optional[int],
    ) -> Dict[str, Any]:
        """PATCH /api/admin/exercises/{exercise_id} — toggle is_archived. Lève AdminError si erreur."""
        with sync_db_session() as db:
            result, err, code = AdminService.patch_exercise_for_admin(
                db,
                exercise_id=exercise_id,
                is_archived=is_archived,
                admin_user_id=admin_user_id,
            )
            if err:
                raise AdminError(err, code)
            return result

    @staticmethod
    def create_badge_for_admin(
        data: Dict[str, Any], admin_user_id: Optional[int]
    ) -> Dict[str, Any]:
        """POST /api/admin/badges — création d'un badge. Lève AdminError si erreur."""
        with sync_db_session() as db:
            r = AdminService.create_badge_for_admin(
                db, data=data, admin_user_id=admin_user_id
            )
            if not r.is_success:
                raise AdminError(
                    r.error_message or "Erreur création badge", r.status_code
                )
            return r.data

    @staticmethod
    def put_badge_for_admin(
        badge_id: int,
        data: Dict[str, Any],
        admin_user_id: Optional[int],
    ) -> Dict[str, Any]:
        """PUT /api/admin/badges/{badge_id} — mise à jour complète. Lève AdminError si erreur."""
        with sync_db_session() as db:
            r = AdminService.put_badge_for_admin(
                db,
                badge_id=badge_id,
                data=data,
                admin_user_id=admin_user_id,
            )
            if not r.is_success:
                raise AdminError(
                    r.error_message or "Erreur mise à jour badge", r.status_code
                )
            return r.data

    @staticmethod
    def delete_badge_for_admin(
        badge_id: int, admin_user_id: Optional[int]
    ) -> Dict[str, Any]:
        """DELETE /api/admin/badges/{badge_id} — soft delete. Lève AdminError si erreur."""
        with sync_db_session() as db:
            r = AdminService.delete_badge_for_admin(
                db, badge_id=badge_id, admin_user_id=admin_user_id
            )
            if not r.is_success:
                raise AdminError(
                    r.error_message or "Erreur suppression badge", r.status_code
                )
            return r.data

    @staticmethod
    def create_challenge_for_admin(
        data: Dict[str, Any], admin_user_id: Optional[int]
    ) -> Dict[str, Any]:
        """POST /api/admin/challenges — création d'un défi. Lève AdminError si erreur."""
        with sync_db_session() as db:
            result, err, code = AdminService.create_challenge_for_admin(
                db, data=data, admin_user_id=admin_user_id
            )
            if err:
                raise AdminError(err, code)
            return result

    @staticmethod
    def put_challenge_for_admin(
        challenge_id: int,
        data: Dict[str, Any],
        admin_user_id: Optional[int],
    ) -> Dict[str, Any]:
        """PUT /api/admin/challenges/{challenge_id} — mise à jour complète. Lève AdminError si erreur."""
        with sync_db_session() as db:
            result, err, code = AdminService.put_challenge_for_admin(
                db,
                challenge_id=challenge_id,
                data=data,
                admin_user_id=admin_user_id,
            )
            if err:
                raise AdminError(err, code)
            return result

    @staticmethod
    def duplicate_challenge_for_admin(
        challenge_id: int, admin_user_id: Optional[int]
    ) -> Dict[str, Any]:
        """POST /api/admin/challenges/{challenge_id}/duplicate — crée une copie. Lève AdminError si erreur."""
        with sync_db_session() as db:
            result, err, code = AdminService.duplicate_challenge_for_admin(
                db, challenge_id=challenge_id, admin_user_id=admin_user_id
            )
            if err:
                raise AdminError(err, code)
            return result

    @staticmethod
    def patch_challenge_for_admin(
        challenge_id: int,
        is_archived: bool,
        admin_user_id: Optional[int],
    ) -> Dict[str, Any]:
        """PATCH /api/admin/challenges/{challenge_id} — toggle is_archived. Lève AdminError si erreur."""
        with sync_db_session() as db:
            result, err, code = AdminService.patch_challenge_for_admin(
                db,
                challenge_id=challenge_id,
                is_archived=is_archived,
                admin_user_id=admin_user_id,
            )
            if err:
                raise AdminError(err, code)
            return result

    @staticmethod
    def export_csv_data_for_admin(
        export_type: str,
        period: str,
        admin_user_id: Optional[int],
    ) -> AdminExportDataResult:
        """GET /api/admin/export — préparation métier (headers + rows)."""
        with sync_db_session() as db:
            headers, rows = AdminService.export_csv_data_for_admin(
                db,
                export_type=export_type,
                period=period,
                admin_user_id=admin_user_id,
            )
            return AdminExportDataResult(headers=headers, rows=rows)
