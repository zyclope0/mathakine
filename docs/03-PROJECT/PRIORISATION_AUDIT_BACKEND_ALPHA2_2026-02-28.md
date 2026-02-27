# Priorisation des corrections — Audit Backend Alpha 2

**Date :** 28/02/2026  
**Référence :** [AUDIT_TECHNIQUE_BACKEND_ALPHA2_2026-02-27.md](./AUDIT_TECHNIQUE_BACKEND_ALPHA2_2026-02-27.md)  
**Critères :** Risque × Facilité × Gain (1–3, 3 = élevé)

---

## Tableau de priorisation

| # | Point audit | Risque | Facilité | Gain | Score | Priorité |
|---|-------------|--------|----------|------|-------|----------|
| 1 | Contrat erreur API hétérogène | 3 | 2 | 3 | 18 | **P1** |
| 2 | Logique métier dans submit_answer | 2 | 2 | 3 | 12 | **P2** |
| 3 | SQL brut dans badge_handlers | 2 | 3 | 3 | 18 | **P1** |
| 4 | db.add/db.commit dans handlers (auth/user) | 2 | 1 | 2 | 4 | **P3 ✅** |
| 5 | requirements.txt (commentaire, pydantic-settings) | 1 | 3 | 1 | 3 | **P1** (partiel) |
| 6 | Migrations non réversibles | 1 | 1 | 1 | 1 | P4 |
| 7 | Chaîne Alembic nommage | 1 | 1 | 1 | 1 | P4 |
| 8 | CI ObiWan / seed lourd | 2 | 1 | 2 | 4 | P3 |
| 9 | gunicorn / uvloop non activés | 1 | 2 | 1 | 2 | P4 |

---

## Plan d'exécution

### P1 — ✅ Implémenté (28/02/2026)

1. **Erreurs API unifiées** : Tous les handlers utilisent `api_error_response(status_code, message)` — contrat unifié `{code, message, error}`. Handlers migrés : auth, user, admin, challenge, chat, exercise, feedback, recommendation, analytics, middleware, server/auth, request_utils, rate_limit.
2. **SQL brut badge_handlers** : `BadgeService.get_user_gamification_stats(user_id)` — plus de SQL dans le handler.
3. **requirements.txt** : Commentaire starlette corrigé (FastAPI 0.133.1).

### Session 22/02/2026 — Refactors et stabilisation

| Réfacteur | Détail |
|-----------|--------|
| **Unification erreurs API** | Remplacement de tous les `JSONResponse({"error":...})` et `{"detail":...}` par `api_error_response` dans auth_handlers (~25 occ.), user_handlers, admin_handlers, challenge_handlers, chat_handlers, exercise_handlers, feedback_handlers, recommendation_handlers, analytics_handlers |
| **Qualité code** | Black (admin, auth, challenge, user), isort (request_utils, admin_handlers, user_handlers), flake8 F821 (UserSession import auth_service) |
| **CI tests** | test_get_exercises : correction assert `[] or None` → vérifier `"items" in data` (liste vide en CI sans seed) |

### P2 — ✅ Implémenté (28/02/2026)

4. **submit_answer** : Logique extraite vers `ExerciseService.submit_answer_result` (validation, record_attempt, badges, streak). Handler = orchestration HTTP uniquement.

### P3 — ✅ Implémenté (28/02/2026)

5. **auth/user db.commit** : AuthService.resend_verification_token, create_session, initiate_password_reset, set_verification_token_for_new_user. Handlers n'ont plus de db.add/db.commit.
6. **CI fixtures** : ✅ 22/02/2026 — CI initialise le schéma uniquement (create_tables), sans seed ObiWan. Tests isolés via fixtures. BDD prod non impactée (base test dédiée CI/Docker).

### P4 — Non prioritaire

7. Migrations réversibles, nommage Alembic, uvloop : documentation ou choix assumé.

---

### Option A — ✅ Implémenté (22/02/2026)

7. **Config pydantic-settings** : `app/core/config.py` migré vers `BaseSettings` (pydantic-settings). Typage des champs, validation via `Field`, chargement depuis `.env` + variables d'environnement. Valeurs sensibles (postgres/postgres) restent en défaut pour dev local uniquement.

**Validation** : Serveur démarre (`python enhanced_server.py`), connexion et login fonctionnent. Tests backend passent.
