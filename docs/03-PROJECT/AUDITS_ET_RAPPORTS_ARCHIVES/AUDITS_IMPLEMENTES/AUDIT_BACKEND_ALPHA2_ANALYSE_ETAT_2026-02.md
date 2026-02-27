# Analyse de l'audit Backend Alpha 2 — État au 28/02/2026

> Ce document croise **AUDIT_BACKEND_ALPHA2_INDUSTRIALISATION.md** avec l'état réel du code pour distinguer : ✅ déjà fait, ⚠️ partiel, ❌ encore à faire.

---

## Synthèse rapide

| Point audit | État réel | Commentaire |
|-------------|-----------|-------------|
| 1. Fuite logique métier dans handlers | ⚠️ Partiellement obsolète | `get_user_stats` et `get_exercise` déléguent aux services. Voir détail ci‑dessous. |
| 2. Couplage services↔modèles / contournement DB | ✅ Fait | Tous les handlers passent par des services. `db.commit()` redondant retiré de `recommendation_handlers` (27/02). |
| 3. Adapter ignore session injectée | ✅ Corrigé (27/02) | `create_generated_exercise` utilise désormais la session injectée via `ExerciseService.create_exercise`. |
| 4. Gestion d'erreurs non uniforme | ✅ Fait (28/02) | Tous les handlers utilisent `api_error_response`. |
| 5. Migrations chronologie / downgrade | ⚠️ Partiel | Chaîne Alembic cohérente (20260205→20260222→20260206…). Downgrade `20260222_legacy_tables` = no-op (volontaire). |
| 6. CI/CD | ✅ Fait | `tests.yml` actif. CI utilise `create_tables()` sans seed. Tests isolés via fixtures. |
| 7. Alignement packaging | ✅ Corrigé (27/02) | `PROJECT_VERSION` aligné à 2.1.0 ; `pathlib` retiré de `requirements.txt`. |

---

## Détail par point

### 1. Fuite de logique métier dans les handlers — ⚠️ Obsolète pour get_exercise et get_user_stats

**Audit :** `get_user_stats` et `get_exercise` feraient les calculs directement dans la route.

**Réalité :**
- `get_exercise` : délègue à `ExerciseService.get_exercise_for_api(db, exercise_id)`.
- `get_user_stats` : délègue à `EnhancedServerAdapter.get_user_stats_for_dashboard(db, user_id, time_range)` → `UserService.get_user_stats`.

La logique métier est dans les services, pas dans les handlers. Cet item peut être considéré comme **résolu** pour ces deux routes.

---

### 2. Couplage fort services↔modèles / contournement DB — ✅ Handlers OK

**Audit :** Handlers interrogent directement la DB au lieu de passer par des services.

**Réalité :** Voir [INVENTAIRE_HANDLERS_DB_DIRECTE.md](../RAPPORTS_TEMPORAIRES/INVENTAIRE_HANDLERS_DB_DIRECTE.md). Tous les handlers (admin, user, exercise, auth, feedback, analytics, challenge, recommendation) utilisent des services.  
Le `db.commit()` redondant a été retiré (27/02). Les services restent couplés aux modèles SQLAlchemy (`db.query`, etc.). L’audit suggère un niveau supplémentaire (repositories / unit-of-work) non mis en place.

---

### 3. Adapter ignore session injectée — ✅ Corrigé

**Audit :** `EnhancedServerAdapter.create_generated_exercise` ignore le paramètre `db` et ouvre une nouvelle session.

**Réalité :** Corrigé le 27/02. La méthode délègue maintenant à `ExerciseService.create_exercise(db, exercise_data)` en utilisant la session injectée.

---

### 4. Gestion d'erreurs non uniforme — ⚠️ Partiel

**Audit :** Handlers renvoient des formats ad hoc (`{"error": ...}`) au lieu d’un schéma d’erreur standardisé.

**Réalité (28/02) :** Schéma unifié `api_error_json` / `api_error_response` avec `{code, message, error, path?, trace_id?, field_errors?}`. Les `error_handlers.py` (404, 500) les utilisent. Handlers métier à migrer progressivement.

---

### 5. Migrations — ⚠️ Partiel

**Audit :** Chronologie incohérente ; downgrade no-op.

**Réalité :**
- Chaîne cohérente : `20260205` → `20260222_legacy_tables` → `20260206_exercises_idx` → …
- Le downgrade de `20260222_legacy_tables` est volontairement un no-op pour éviter les DROP en production. Documenté dans le fichier de migration.
- Si souhaité : documenter une politique de downgrade (supporté vs non supporté) dans un doc dédié.

---

### 6. CI/CD — ✅ Fait (audit basé sur ancien état)

**Audit :** `ci.yml` désactivé ; dépendance à ObiWan.

**Réalité :**
- Le workflow actif est `tests.yml`, pas `ci.yml` (commentaire : « ci.yml supprimé 25/02/2026 »).
- `tests.yml` se déclenche sur `push` et `pull_request` vers main/master/develop.
- ObiWan est créé par `create_tables_with_test_data()` pour l’environnement de test. Les tests ne dépendent pas d’un user préexistant en prod.

---

### 7. Alignement packaging — ✅ Corrigé

**Réalité (après correction 27/02) :**
- `pyproject.toml` : `version = "2.1.0"`
- `app/core/config.py` : `PROJECT_VERSION = "2.1.0"` (aligné)
- `requirements.txt` : `pathlib` retiré.
- `requirements.txt` mélange runtime et dev (pytest, etc.) — séparation possible avec `requirements-dev.txt`.

---

## Plan d'action — état vs recommandations

| Étape audit | État | Action |
|-------------|------|--------|
| 1. Stabiliser contrats API d'erreurs | ⚠️ | Schéma unifié introduit ; 404/500 migrés. Handlers métier à migrer progressivement. |
| 2. Refactor handlers minces | ✅ | Tous les handlers passent par des services (voir INVENTAIRE). |
| 3. Isoler accès DB (repository/UoW) | ✅ | `create_generated_exercise` corrigé. Optionnel : repositories / unit-of-work. |
| 4. Durcir reproductibilité déploiement | ⚠️ | Smoke test dans CI. Pre/post-deploy (alembic current, DB ping, version API) et rollback à documenter. |
| 5. Assainir CI et migrations | ✅ (CI) / ⚠️ (migrations) | CI actif. Migrations : documenter la politique de downgrade. |

---

## Conclusion

L’audit reflète un état plus ancien sur plusieurs points (handlers, CI). Les corrections restantes prioritaires sont :

1. ~~Corriger `create_generated_exercise`~~ ✅ Fait.
2. ~~Alignement version + pathlib~~ ✅ Fait.
3. ~~Schéma d’erreur API (base)~~ ✅ Fait. Handlers métier à migrer au fil de l'eau.
4. ~~db.commit redondant recommendation_handlers~~ ✅ Fait.
5. Restent : documenter politique downgrade migrations ; pre-deploy/smoke si souhaité.
