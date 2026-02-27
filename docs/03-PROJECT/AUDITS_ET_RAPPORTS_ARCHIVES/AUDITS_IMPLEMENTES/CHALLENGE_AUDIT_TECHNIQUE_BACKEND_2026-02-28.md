# Challenge factuel — Audit technique Backend Alpha 2 (27/02/2026)

**Date :** 28/02/2026  
**Statut :** ✅ Audit clôturé — voir [CLOTURE_AUDIT_BACKEND_ALPHA2_2026-02-22.md](./CLOTURE_AUDIT_BACKEND_ALPHA2_2026-02-22.md)  
**Référence :** [AUDIT_TECHNIQUE_BACKEND_ALPHA2_2026-02-27.md](./AUDIT_TECHNIQUE_BACKEND_ALPHA2_2026-02-27.md)  
**Méthode :** Confrontation point par point avec le code source réel (`app/`, `server/`, `migrations/`).

---

## Synthèse rapide

| Point audit | État | Commentaire |
|-------------|------|-------------|
| **2.2 Fuite logique métier dans submit_answer** | ✅ Corrigé | Logique extraite vers `ExerciseService.submit_answer_result` (28/02) |
| **2.2 Erreurs ad hoc vs unifié** | ✅ Corrigé | Tous les handlers utilisent `api_error_response` (22/02) |
| **2.2 db.add / db.commit dans handlers** | ✅ Corrigé | Services AuthService, UserService ; plus de commit dans handlers (28/02) |
| **2.2 SQL brut dans handlers** | ✅ Corrigé | `BadgeService.get_user_gamification_stats` (28/02) |
| **2.3 requirements.txt** | ⚠️ Partiel | starlette + pydantic-settings corrigés ; gunicorn / uvloop non activés (P4) |
| **3.1 config.py** | ✅ Corrigé | Migré vers pydantic-settings BaseSettings (22/02) |
| **3.2 render.yaml** | ✅ Confirmé | `python enhanced_server.py`, pas Gunicorn |
| **4.1 Hétérogénéité erreurs** | ✅ Corrigé | Contrat unifié `api_error_response` partout (22/02) |
| **4.2 Migrations chronologie** | ✅ **Confirmé** | 20260206_exercises_idx dépend de 20260222_legacy_tables |
| **4.3 uvloop** | ✅ **Confirmé** | Aucun `loop=uvloop` ou import explicite dans enhanced_server / server/app.py |
| **5.2 CI ObiWan** | ✅ **Corrigé** | CI utilise `create_tables()` sans seed (22/02). Tests via fixtures. |
| **ci.yml** | ✅ **Confirmé** | tests.yml est la source de vérité unique ; ci.yml supprimé. |

---

## 1) Modularité & dépendances — vérification

### 2.2 Fuite logique métier dans submit_answer — ✅ Corrigé (28/02/2026)

**Fichier :** `server/handlers/exercise_handlers.py` L144-165

| Élément audit | Code réel |
|---------------|-----------|
| Le handler délègue à | `ExerciseService.submit_answer_result(db, exercise_id, user_id, selected_answer, time_spent)` — toute la logique dans le service |

**Délégation partielle :** `ExerciseService.get_exercise_for_submit_validation` et `ExerciseService.record_attempt` sont utilisés. La logique de correction et l’orchestration (badges, streak, réponse) est dans le service (28/02).

### 2.2 Erreurs ad hoc vs schéma unifié — ✅ Corrigé (22/02/2026)

Tous les handlers utilisent désormais `api_error_response(status_code, message)` — contrat unifié `{code, message, error}`. Fichiers : auth, user, admin, challenge, chat, exercise, feedback, recommendation, analytics, middleware, utils.

### 2.2 db.add / db.commit dans handlers — ✅ Corrigé (28/02/2026)

Logique déplacée vers services : `AuthService.resend_verification_token`, `create_session`, `initiate_password_reset`, `set_verification_token_for_new_user` ; `UserService` pour register. Handlers = orchestration HTTP uniquement.

### 2.2 SQL brut dans badge_handlers — ✅ Corrigé (28/02/2026)

Remplacé par `BadgeService.get_user_gamification_stats(user_id)`. Handler délègue au service.

---

## 2) Configuration & reproductibilité — vérification

### 2.3 requirements.txt

| Point | Code réel |
|-------|-----------|
| starlette | ✅ Corrigé — `starlette==0.52.1  # Compatible FastAPI 0.133.1` |
| pydantic-settings | ✅ Utilisé — config.py hérite de BaseSettings (22/02) |
| gunicorn | requirements.txt L52, render.yaml L14 : `python enhanced_server.py` — pas Gunicorn |
| uvloop | requirements.txt L53 (conditionnel Windows), server/app.py L81 : `uvicorn.run(...)` sans paramètre `loop` |

### 3.1 app/core/config.py — ✅ Corrigé (22/02/2026)

- `Settings` : hérite de `BaseSettings` (pydantic-settings), typage et validation via `Field`
- Chargement : `.env` en dev, variables d'environnement (prod)
- Valeurs par défaut postgres/postgres conservées pour dev local

### 4.1 Hétérogénéité schéma erreurs — ✅ Corrigé (22/02/2026)

Contrat unifié `api_error_response` : `{code, message, error}`. Tous les handlers l'utilisent. Le frontend lit `message` ou `error` (client.ts ligne 162).

---

## 3) Migrations & CI — vérification

### 4.2 Chronologie Alembic

**Fichier :** `migrations/versions/20260206_1530_add_exercises_indexes.py` L21  
```python
down_revision: Union[str, None] = '20260222_legacy_tables'
```

Une migration datée 2026-02-06 dépend d’une révision 2026-02-22. L’audit est correct sur l’incohérence de nommage (même si la chaîne Alembic est valide via `down_revision`).

### 5.2 CI — create_tables / ObiWan — ✅ Corrigé (22/02/2026)

**tests.yml L98-103 :**
```yaml
run: |
  python -c "
  from app.services.db_init_service import create_tables
  create_tables()
  "
```


**Conclusion :** CI initialise le schéma uniquement. Tests isolés via fixtures. Plus de seed ObiWan.

---

## 4) Points résiduels (P3 corrigé 28/02)

- **Auth** : `db.commit` déplacé vers AuthService/UserService. Handlers = orchestration HTTP.
- **Admin** : passent par AdminService. Seul `db.add` restant : `_log_admin_action` (audit log).

---

## 5) Conclusion

L'audit du 27/02 reflète l'état du code. Les 9 points bloquants sont corrigés (28/02). Tous les handlers utilisent `api_error_response`. Logique métier déléguée aux services. **Audit clôturé.**
