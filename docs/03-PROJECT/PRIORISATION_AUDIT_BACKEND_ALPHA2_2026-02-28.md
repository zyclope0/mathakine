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
| 4 | db.add/db.commit dans handlers (auth/user) | 2 | 1 | 2 | 4 | P3 |
| 5 | requirements.txt (commentaire, pydantic-settings) | 1 | 3 | 1 | 3 | **P1** (partiel) |
| 6 | Migrations non réversibles | 1 | 1 | 1 | 1 | P4 |
| 7 | Chaîne Alembic nommage | 1 | 1 | 1 | 1 | P4 |
| 8 | CI ObiWan / seed lourd | 2 | 1 | 2 | 4 | P3 |
| 9 | gunicorn / uvloop non activés | 1 | 2 | 1 | 2 | P4 |

---

## Plan d'exécution

### P1 — ✅ Implémenté (28/02/2026)

1. **Erreurs API unifiées** : ErrorHandler utilise maintenant `api_error_json` (code, message, error). `api_error_response` utilisé dans submit_answer et badge_handlers pour les erreurs ad hoc.
2. **SQL brut badge_handlers** : `BadgeService.get_user_gamification_stats(user_id)` — plus de SQL dans le handler.
3. **requirements.txt** : Commentaire starlette corrigé (FastAPI 0.133.1).

### P2 — Prochaine itération

4. **submit_answer** : Extraire logique `is_correct` et assemblage réponse vers `ExerciseService.submit_answer_result(db, exercise, selected_answer, time_spent, user_id)`.

### P3 — Backlog

5. **auth/user db.commit** : Migrer `resend_verification_email`, `login` (UserSession), `register` vers AuthService/UserService.
6. **CI fixtures** : Remplacer seed global par fixtures ciblées par test (plus gros chantier).

### P4 — Non prioritaire

7. Migrations réversibles, nommage Alembic, uvloop : documentation ou choix assumé.
