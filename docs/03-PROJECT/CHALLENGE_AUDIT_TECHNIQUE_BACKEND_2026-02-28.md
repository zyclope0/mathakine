# Challenge factuel — Audit technique Backend Alpha 2 (27/02/2026)

**Date :** 28/02/2026  
**Référence :** [AUDIT_TECHNIQUE_BACKEND_ALPHA2_2026-02-27.md](./AUDIT_TECHNIQUE_BACKEND_ALPHA2_2026-02-27.md)  
**Méthode :** Confrontation point par point avec le code source réel (`app/`, `server/`, `migrations/`).

---

## Synthèse rapide

| Point audit | Vérification code | Commentaire |
|-------------|-------------------|-------------|
| **2.2 Fuite logique métier dans submit_answer** | ✅ **Confirmé** | Logique `is_correct` (texte vs numérique), assemblage réponse, badges, streak dans le handler |
| **2.2 Erreurs ad hoc vs unifié** | ✅ **Confirmé** | `JSONResponse({"error": ...})`, `ErrorHandler.create_*` (schema différent de `api_error_response`) |
| **2.2 db.add / db.commit dans handlers** | ✅ **Confirmé** | auth_handlers (185, 300-301, 668), user_handlers (171), admin_handlers_utils (76) |
| **2.2 SQL brut dans handlers** | ✅ **Confirmé** | badge_handlers.py L115-136 : `db.execute(text(""SELECT...""))` |
| **2.3 requirements.txt** | ✅ **Confirmé** | starlette "0.121.0" vs fastapi 0.133.1 ; pydantic-settings non utilisé ; gunicorn/uvloop présents non activés |
| **3.1 config.py** | ✅ **Confirmé** | Settings maison, postgres/postgres en dur, multi-variables prod |
| **3.2 render.yaml** | ✅ **Confirmé** | `python enhanced_server.py`, pas Gunicorn, pas pre-deploy bloquante |
| **4.1 Hétérogénéité erreurs** | ✅ **Confirmé** | api_error_response (code, message) vs ErrorHandler (error, error_type, details) vs JSONResponse brut |
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

### 2.2 Erreurs ad hoc vs schéma unifié

**Fichiers concernés :**

| Handler | Format utilisé | Fichier |
|---------|---------------|---------|
| exercise_handlers | `JSONResponse({"error": ...})` L165, L263 | exercise_handlers.py |
| exercise_handlers | `ErrorHandler.create_not_found_error` L121, 126 | exercise_handlers.py |
| exercise_handlers | `ErrorHandler.create_error_response` L134, 199, 377, 465, 555, 890 | exercise_handlers.py |
| error_handlers (global) | `api_error_response` (code, message, trace_id) | error_handlers.py |

**Schéma ErrorHandler :** `error`, `error_type`, `details` (optionnel) — différent de `api_error_json` (code, message, path, trace_id, field_errors).

### 2.2 db.add / db.commit dans handlers

| Fichier | Ligne | Contexte |
|---------|-------|----------|
| auth_handlers.py | 185 | `db.commit()` — resend verification token |
| auth_handlers.py | 300-301 | `db.add(db_session_row)` + `db.commit()` — création UserSession au login |
| auth_handlers.py | 668 | `db.commit()` — autre flow |
| user_handlers.py | 171 | `db.commit()` — register, mise à jour verification token |
| admin_handlers_utils.py | 76 | `db.add(log)` — audit log (pas de commit explicite, transaction parente) |

### 2.2 SQL brut dans badge_handlers

**Fichier :** `server/handlers/badge_handlers.py` L115-136

```python
stats = db.execute(
    text("""
    SELECT COUNT(*) as total_attempts, ...
    FROM attempts WHERE user_id = :user_id
    """),
    {"user_id": user_id},
).fetchone()

badge_stats = db.execute(
    text("""SELECT a.category, COUNT(*) ... FROM achievements a JOIN user_achievements ua ..."""),
    {"user_id": user_id},
).fetchall()
```

**Confirmé :** Requêtes SQL brutes dans le handler, non encapsulées dans un service/repository.

---

## 2) Configuration & reproductibilité — vérification

### 2.3 requirements.txt

| Point | Code réel |
|-------|-----------|
| starlette "compatible FastAPI 0.121.0" | requirements.txt L3 : `starlette==0.52.1  # Version compatible FastAPI 0.121.0` — fastapi L2 : `0.133.1` |
| pydantic-settings non utilisé | config.py : `class Settings` avec attributs de classe, pas `BaseSettings` |
| gunicorn | requirements.txt L52, render.yaml L14 : `python enhanced_server.py` — pas Gunicorn |
| uvloop | requirements.txt L53 (conditionnel Windows), server/app.py L81 : `uvicorn.run(...)` sans paramètre `loop` |

### 3.1 app/core/config.py

- `Settings` : classe maison, attributs `os.getenv(...)`, pas de pydantic-settings
- Valeurs par défaut : `postgres/postgres` dans DATABASE_URL, TEST_DATABASE_URL, POSTGRES_*
- Détection prod : `NODE_ENV`, `ENVIRONMENT`, `MATH_TRAINER_PROFILE` (L163-166)

### 4.1 Hétérogénéité schéma erreurs

**api_error_json / api_error_response (app/utils/error_handler.py) :**
- Champs : `code`, `message`, `error` (alias), `path`, `trace_id`, `field_errors`

**ErrorHandler.create_error_response :**
- Champs : `error`, `error_type`, `error_message`, `details` (en dev)

**ErrorHandler.create_not_found_error :**
- Champs : `error`, `resource_type`, `resource_id`

**ErrorHandler.create_validation_error :**
- Champs : `error`, `field`, `message`

**Conclusion :** Plusieurs schémas coexistent. Le frontend doit gérer `message`, `detail`, `error` selon les endpoints (client.ts).

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
