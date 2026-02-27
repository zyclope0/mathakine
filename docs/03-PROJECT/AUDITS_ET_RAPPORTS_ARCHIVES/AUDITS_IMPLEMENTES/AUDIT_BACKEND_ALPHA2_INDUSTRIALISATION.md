# Audit technique back-end (Alpha 2 → industrialisation)

> **Référence** : Voir [AUDIT_BACKEND_ALPHA2_ANALYSE_ETAT_2026-02.md](./AUDIT_BACKEND_ALPHA2_ANALYSE_ETAT_2026-02.md) pour l'état réel (corrections post-audit).

## Périmètre audité
- `app/`
- `server/`
- `migrations/`
- `requirements.txt`, `pyproject.toml`, `runtime.txt`, `render.yaml`
- `.github/workflows/` (tests.yml actif, ci.yml si présent)

## Tableau de score (0-10)
| Axe | Score | Constat factuel |
|---|---:|---|
| Modularité | 5/10 | Une couche `app/services` existe ; couche repository non explicite ; adapter session corrigé (28/02). |
| Sécurité de configuration | 6/10 | Contrôles prod réels ; config migrée BaseSettings (22/02) ; version alignée. |
| Reproductibilité | 6/10 | Render build déterministe ; CI tests.yml actif sur push/PR. |
| Observabilité | 6/10 | Sentry + Prometheus + `/metrics` ; schéma d'erreur unifié introduit (28/02). |

---

## 1) Modularité & dépendances

### 1.1 Couplage services ↔ modèles DB
- Couplage ORM fort : services manipulent `db.query(...)` directement.
- Pas de couche repository explicite.

### 1.2 Fuite de logique métier dans les handlers
- `get_user_stats` et `get_exercise` délèguent aux services (`ExerciseService`, `UserService` via adapter). La logique agrégée reste dans les services ou adapters.
- Voir [AUDIT_BACKEND_ALPHA2_ANALYSE_ETAT](./AUDIT_BACKEND_ALPHA2_ANALYSE_ETAT_2026-02.md) pour le détail.

### 1.3 Point transaction/session — ✅ Corrigé (27/02)
- ~~`EnhancedServerAdapter.create_generated_exercise` ouvrait sa propre session.~~
- **Corrigé** : délègue à `ExerciseService.create_exercise(db, ...)` avec la session injectée.

---

## 2) Reproductibilité & configuration

### 2.1 `app/core/config.py`
- Contrôles prod : `.env` ignoré en production, `SECRET_KEY` obligatoire, mot de passe admin faible interdit.
- **Alignement version (27/02)** : `PROJECT_VERSION = "2.1.0"` (aligné avec pyproject.toml).
- **Mise à jour 22/02** : Config migrée vers `BaseSettings` (pydantic-settings). Serveur démarre, login OK.

### 2.2 `render.yaml`
- Build déterministe : `pip install -r requirements.txt && alembic upgrade head`.
- Healthcheck : `/health`.
- Pas d'étape pre-deploy/smoke explicite déclarée.

### 2.3 `pyproject.toml` / `requirements.txt` / `runtime.txt`
- Python : `requires-python >=3.12` + `runtime.txt python-3.12.0` — cohérent.
- Version produit alignée (27/02).
- **pathlib retiré (27/02)** : redondant en Python 3.12+.
- `requirements.txt` mélange runtime et dev (pas de `requirements-dev.txt`).

---

## 3) Industrialisation & robustesse

### 3.1 Gestion des erreurs — ✅ Unifié (22/02/2026)
- **Corrigé** : schéma unifié `api_error_json` / `api_error_response` avec `code`, `message`, `error`.
- Tous les handlers (auth, user, admin, challenge, chat, exercise, etc.) utilisent `api_error_response`.

### 3.2 Migrations
- `upgrade()`/`downgrade()` définis ; certains downgrade sont no-op (legacy tables).
- Incohérence chronologique de nommage (20260206 dépend de 20260222).

### 3.3 Performance & scaling
- Pool SQLAlchemy configuré ; uvloop présent ; `enhanced_server.py` en startCommand (pas de gunicorn multi-workers dans render.yaml).

---

## 4) CI/CD
- **tests.yml** actif sur push/PR (main, master, develop) — gate tests + lint.
- `ci.yml` si présent : manuel ; `tests.yml` est la source de vérité.

---

## Points faibles — synthèse (état 28/02)

| # | Point | État |
|---|-------|------|
| 1 | Logique/agrégations dans handlers | ⚠️ Réduit (handlers délèguent) |
| 2 | Transaction/session adapter | ✅ Corrigé |
| 3 | Contrat d'erreur API | ⚠️ Base unifiée ; handlers à migrer |
| 4 | Migrations downgrade / graphe | ⚠️ À documenter |
| 5 | Config versioning | ✅ Aligné |
| 6 | CI/CD | ✅ tests.yml actif |

---

## Plan d'action prioritaire

1. **Erreurs API** — Base posée. Migrer handlers au fil de l'eau si souhaité.
2. **Handlers minces** — Tous passent par services. Amélioration possible (agrégations).
3. **Transaction DB** — Adapter corrigé.
4. **Migrations** — Documenter politique downgrade.
5. **CI/CD** — OK ; tests.yml gate principal.
