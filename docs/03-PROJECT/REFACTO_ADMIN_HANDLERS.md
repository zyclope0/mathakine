# Refactoring admin_handlers — Migration AdminService

> Date : 27/02/2026  
> Référence : INVENTAIRE_HANDLERS_DB_DIRECTE.md § 5  
> **Statut :** ✅ Complété

---

## Vue d'ensemble

Toute la logique DB des handlers admin a été déplacée vers `AdminService` dans `app/services/admin_service.py`. Les handlers ne font plus de requêtes directes.

| Zone | Méthodes AdminService |
|------|------------------------|
| Config | `get_config_for_api`, `update_config` |
| Overview | `get_overview_for_api` |
| Audit log | `get_audit_log_for_api` |
| Modération | `get_moderation_for_api` |
| Reports | `get_reports_for_api` |
| Users CRUD | `list_users_for_admin`, `patch_user_for_admin`, `send_reset_password_for_admin`, `resend_verification_for_admin` |
| Badges CRUD | `list_badges_for_admin`, `create_badge_for_admin`, `get_badge_for_admin`, `put_badge_for_admin`, `delete_badge_for_admin` |
| Exercises CRUD | `list_exercises_for_admin`, `create_exercise_for_admin`, `get_exercise_for_admin`, `put_exercise_for_admin`, `duplicate_exercise_for_admin`, `patch_exercise_for_admin` |
| Challenges CRUD | `list_challenges_for_admin`, `create_challenge_for_admin`, `get_challenge_for_admin`, `put_challenge_for_admin`, `duplicate_challenge_for_admin`, `patch_challenge_for_admin` |
| Export CSV | `export_csv_data_for_admin` |

---

## Lignes directrices

- Handlers minces : parsing params, appel AdminService, construction JSONResponse/StreamingResponse
- Aucun `db.query`, `db.add`, `db.commit` dans les handlers
- Helpers (`_achievement_to_detail`, `_exercise_to_detail`, `_challenge_to_detail`, `_validate_*`) déplacés dans AdminService
