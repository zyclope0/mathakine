# Challenge factuel — Audit technique Backend Alpha 2 (27/02/2026)

**Date :** 28/02/2026  
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
| **2.3 requirements.txt** | ⚠️ Partiel | starlette corrigé ; pydantic-settings / gunicorn / uvloop à traiter |
| **3.1 config.py** | ✅ Corrigé | Migré vers pydantic-settings BaseSettings (22/02) |
| **3.2 render.yaml** | ✅ Confirmé | `python enhanced_server.py`, pas Gunicorn |
| **4.1 Hétérogénéité erreurs** | ✅ Corrigé | Contrat unifié `api_error_response` partout (22/02) |
| **4.2 Migrations chronologie** | ✅ **Confirmé** | 20260206_exercises_idx dépend de 20260222_legacy_tables |
| **4.3 uvloop** | ✅ **Confirmé** | Aucun `loop=uvloop` ou import explicite dans enhanced_server / server/app.py |
| **5.2 CI ObiWan** | ✅ **Confirmé** | create_tables_with_test_data() en CI ; db_init_service crée ObiWan |
| **ci.yml** | ⚠️ **Partiel** | ci.yml n'existe plus (tests.yml actif) — docs à vérifier |

---

## 1) Modularité & dépendances — vérification

### 2.2 Fuite logique métier dans submit_answer

**Fichier :** `server/handlers/exercise_handlers.py` L142-350

| Élément audit | Code réel |
|---------------|-----------|
| Règles de correction selon type | L205-216 : `text_based_types`, comparaison insensible à la casse pour TEXTE/MIXTE, stricte pour les autres — **dans le handler** |
| Assemblage attempt | L224-254 : construction manuelle du dict `attempt` à partir de `attempt_obj` |
| Attribution badges | L276-296 : `BadgeService.check_and_award_badges` appelé dans le handler, assemblage `attempt_for_badges` manuel |
| Streak | L314-318 : `update_user_streak(db, user_id)` appelé dans le handler |
| Formatage réponse | L325-347 : construction `response_data` avec `correct_answer`, `explanation`, `new_badges`, `progress_notification` |

**Délégation partielle :** `ExerciseService.get_exercise_for_submit_validation` et `ExerciseService.record_attempt` sont utilisés. La logique de correction et l’orchestration (badges, streak, réponse) restent dans le handler.

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
| starlette "compatible FastAPI 0.121.0" | requirements.txt L3 : `starlette==0.52.1  # Version compatible FastAPI 0.121.0` — fastapi L2 : `0.133.1` |
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

### 5.2 CI — create_tables_with_test_data / ObiWan

**tests.yml L98-103 :**
```yaml
run: |
  python -c "
  from app.db.init_db import create_tables_with_test_data
  create_tables_with_test_data()
  "
```

**app/services/db_init_service.py L98, 141 :** Création utilisateur "ObiWan" et log "incluant ObiWan permanent".

**Conclusion :** Le seed CI n’est pas minimal ; ObiWan et les fixtures sont créés avant les tests.

---

## 4) Points partiellement nuancés

### Auth handlers et AuthService

L’audit mentionne des handlers qui manipulent directement la DB. En réalité :
- `verify_email` et `api_reset_password` délèguent à `AuthService.verify_email_token` et `reset_password_with_token`
- Mais `db.commit()` reste dans le handler pour `resend_verification_email` (token) et `login` (UserSession)

Donc : délégation partielle, certaines opérations DB restent dans les handlers.

### admin_handlers vs AdminService

D’après INVENTAIRE_HANDLERS_DB_DIRECTE (archivé), les handlers admin passent par AdminService. Le seul `db.add` restant est dans `admin_handlers_utils._log_admin_action` pour l’audit log — utilitaire appelé par les handlers, pas un CRUD métier.

---

## 5) Conclusion

L’audit du 27/02 reflète correctement l’état du code. Les 9 points faibles bloquants sont vérifiés. Les nuances concernent :
- La délégation partielle auth/admin (AuthService, AdminService) déjà en place
- La structure des erreurs : schéma unifié existe mais n’est pas utilisé partout

Le plan d’action en 5 étapes reste pertinent et priorisable tel quel.
