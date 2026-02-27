# Audit technique factuel — Backend Mathakine (Alpha 2)

**Date :** 27/02/2026  
**Type :** Audit technique  
**Statut :** Actif — plan d'action à appliquer  
**Périmètre :** `app/`, `server/`, `migrations/`, fichiers de configuration (`requirements.txt`, `pyproject.toml`, `runtime.txt`, `render.yaml`, `.github/workflows/tests.yml`).

> Audit complémentaire à [AUDIT_BACKEND_ALPHA2_INDUSTRIALISATION](../AUDITS_ET_RAPPORTS_ARCHIVES/AUDITS_IMPLEMENTES/AUDIT_BACKEND_ALPHA2_INDUSTRIALISATION.md) (archivé, corrections v2.1.0 appliquées).  
> **Challenge factuel :** [CHALLENGE_AUDIT_TECHNIQUE_BACKEND_2026-02-28.md](./CHALLENGE_AUDIT_TECHNIQUE_BACKEND_2026-02-28.md) — vérification point par point vs code réel.

---

## 1) Tableau de score (0-10)

| Axe | Score | Constats factuels principaux |
|-----|------:|------------------------------|
| Modularité | 5/10 | Les services centralisent une partie de la logique métier mais restent fortement couplés aux modèles ORM. Des handlers contiennent encore de la logique métier + SQL direct + mapping manuel de DTO. |
| Sécurité de configuration | 6/10 | Blocages utiles en production (`SECRET_KEY`, mot de passe admin faible), mais `Settings` n'utilise pas `pydantic-settings` et conserve des valeurs par défaut sensibles en local (DB postgres/postgres). |
| Reproductibilité | 5/10 | Build Render exécute migrations, CI exécute tests/lint/smoke test. Mais seed de données de test non minimaliste en CI (incluant utilisateur ObiWan et datasets), et historique Alembic partiellement non réversible/no-op. |
| Observabilité | 7/10 | Sentry + Prometheus intégrés, middleware métriques présent, healthcheck CI et Render. Structuration d'erreurs encore hétérogène selon handlers (schéma unifié non appliqué partout). |

---

## 2) Modularité & dépendances (factuel)

### 2.1 Couplage services ↔ modèles DB

- Les services importent directement de nombreux modèles SQLAlchemy (ex. `RecommendationService`, `UserService`), avec des requêtes ORM dans la même couche.
- Le couplage est explicite et élevé : les services sont orientés "data-access + métier" plutôt que découplés via ports/repositories.

### 2.2 Fuite de logique métier dans les handlers

- `submit_answer` contient de la logique métier applicative (règles de correction selon type, assemblage attempt, attribution badges, streak, formatage réponse) au lieu d'être uniquement orchestration HTTP.
- Plusieurs handlers retournent des structures d'erreur ad hoc (`{"error": ...}` / `{"detail": ...}`), en parallèle du helper d'erreur unifié.
- Certains handlers manipulent directement des modèles et la transaction SQLAlchemy (`db.add`, `db.commit`) au lieu de passer strictement par des services.
- Présence de SQL brut dans handler de badges (`db.execute(text(...))`).

### 2.3 `requirements.txt` (compatibilité/conflits visibles)

- Incohérence de commentaire : `starlette==0.52.1` est annoté "compatible FastAPI 0.121.0" alors que `fastapi` est pinné `0.133.1`.
- `pydantic-settings` est déclaré mais la configuration actuelle n'utilise pas `BaseSettings`.
- `gunicorn` est installé mais le démarrage Render est `python enhanced_server.py` (donc `uvicorn.run` en code), pas de commande Gunicorn effective dans `render.yaml`.
- `uvloop` est présent dans les dépendances, mais aucun usage explicite/configuration uvloop n'est visible dans le bootstrap serveur.

---

## 3) Reproductibilité & configuration

### 3.1 `app/core/config.py`

**Points robustes :**

- Refus de démarrage en production si `SECRET_KEY` absent.
- Validation post-init en prod qui empêche un `DEFAULT_ADMIN_PASSWORD` vide/faible.

**Limites factuelles :**

- Classe `Settings` maison (attributs de classe) sans validation/typage runtime de `pydantic-settings`.
- Valeurs par défaut locales pour DB et credentials (`postgres/postgres`) encore en dur.
- Logique de détection production répartie sur plusieurs variables (`NODE_ENV`, `ENVIRONMENT`, `MATH_TRAINER_PROFILE`) augmentant la surface d'écart de config.

### 3.2 `render.yaml` (déterminisme build/migration)

- Build backend : `pip install -r requirements.txt && alembic upgrade head` puis `python enhanced_server.py`.
- Healthcheck défini (`/health`).
- Pas d'étape explicite de pre-deploy avec vérification bloquante (ex. migration dry-run, smoke DB séparé, checks de connectivité dépendances externes).
- Le lancement n'utilise pas une commande process manager type Gunicorn/Uvicorn workers explicite dans le manifest.

### 3.3 Cohérence `pyproject.toml` / `requirements.txt` / `runtime.txt`

- Cohérent sur Python 3.12 (`requires-python >=3.12`, `runtime.txt = python-3.12.0`, CI Python 3.12).
- `requirements.txt` inclut des dépendances qui ne sont pas toutes reflétées dans `[project.dependencies]` (absence de verrouillage central via pyproject), donc double source de vérité pour packaging vs déploiement.

---

## 4) Industrialisation & robustesse backend

### 4.1 Gestion des erreurs (`server/error_handlers.py`)

- Handler global 404/500 renvoie JSON unifié via `api_error_response`.
- Cependant, les handlers applicatifs utilisent aussi `ErrorHandler.create_*` (schéma différent : `error_type`, `details`) et parfois des réponses JSON brutes (`error`/`detail`), créant une hétérogénéité de contrat API.
- Les erreurs ne sont donc pas totalement typées/normalisées de bout en bout pour consommation frontend industrielle.

### 4.2 Migrations (`migrations/versions/`)

- Les fichiers définissent `upgrade()`/`downgrade()`, mais plusieurs `downgrade` sont no-op (`pass`) ou non supportés (`NotImplementedError` sur snapshot initial).
- Une migration datée `2026-02-06` dépend d'une révision `20260222_legacy_tables`, ce qui casse la logique chronologique nominale des noms de fichiers (même si techniquement Alembic suit `down_revision`).
- Certaines migrations sont explicitement idempotentes et orientées sécurité de données (choix assumé), au prix d'une réversibilité limitée.

### 4.3 Performance & scaling (pool SQLAlchemy + uvloop)

- Pool SQLAlchemy configuré (`pool_pre_ping`, `pool_size`, `max_overflow`, `pool_recycle`, `pool_timeout`) via paramètres configurables.
- Les handlers sont majoritairement `async` mais utilisent une session SQLAlchemy synchrone dans un context manager async ; pas de passage explicite à SQLAlchemy async engine/session.
- Aucune activation explicite de `uvloop` observée dans le code serveur.

---

## 5) Audit CI/CD (`.github/workflows/tests.yml`)

### 5.1 Non-régression : couverture factuelle

- Pipeline inclut backend tests + couverture + JUnit + smoke `/health`.
- Pipeline inclut lint backend (flake8/black/isort) et pipeline frontend (tsc/eslint/prettier/tests/build).
- `flake8` est restreint aux erreurs critiques (`--select=E9,F63,F7,F82`), donc ne couvre pas la totalité des dettes style/qualité Python.

### 5.2 Points de friction industrialisation

- Initialisation CI appelle `create_tables_with_test_data()` qui peuple des données de test non minimales (dont utilisateur "ObiWan" permanent et jeux de données associés), ce qui augmente le couplage des tests à un dataset préseedé.
- Création DB et init via scripts inline Python dans le YAML (maintenance plus difficile qu'une commande outillée unique/versionnée).
- `ci.yml` n'existe plus (remplacé par `tests.yml`), ce qui peut créer une ambiguïté documentaire si des docs/process mentionnent encore `ci.yml`.

---

## 6) Points faibles factuels bloquants (fichiers ciblés)

1. **Contrat d'erreur API hétérogène** (global handler unifié vs réponses ad hoc dans handlers).
2. **Logique métier encore dans les handlers** (`submit_answer` en particulier).
3. **Accès DB direct et SQL brut dans handlers** (modèles/commit/SQL text dans couche HTTP).
4. **Migrations non pleinement réversibles** (`pass`, `NotImplementedError` sur downgrade).
5. **Chaîne Alembic à chronologie de nommage incohérente** (fichier 20260206 dépend d'une révision 20260222).
6. **Runtime async + DB sync** sans adoption explicite du stack SQLAlchemy async.
7. **CI couplée à seed de données lourdes/permanentes** (ObiWan + fixtures applicatives).
8. **Double source de vérité partielle dépendances/packaging** (`requirements.txt` vs pyproject minimal).
9. **`gunicorn` et `uvloop` présents mais non explicitement activés dans le démarrage Render/code**.

---

## 7) Plan d'action technique prioritaire (5 étapes)

1. **Uniformiser le contrat d'erreur API**  
   Imposer une seule fabrique d'erreur (`code`, `message`, `trace_id`, `field_errors`) pour tous les handlers et retirer les payloads ad hoc.

2. **Extraire la logique métier des handlers**  
   Commencer par `submit_answer` : déplacer règles de correction, attribution badges/streak, assemblage du résultat dans un service d'application transactionnel unique.

3. **Durcir la couche persistance**  
   Introduire une couche repository/use-case claire et supprimer SQL brut/`db.commit()` dans les handlers. Standardiser le transaction boundary côté service.

4. **Assainir migrations et stratégie rollback**  
   Documenter migrations irréversibles, ajouter runbook rollback explicite, et corriger les incohérences de naming chronologique pour réduire le risque opérationnel.

5. **Rendre CI/CD plus déterministe et minimale**  
   Remplacer le seed global par fixtures ciblées par test, factoriser scripts DB init en commandes versionnées, ajouter checks de migration (ex. `alembic current`, test upgrade from scratch) et renforcer la qualité lint (au-delà des seules erreurs critiques).
