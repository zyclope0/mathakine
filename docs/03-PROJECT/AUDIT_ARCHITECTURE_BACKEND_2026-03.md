# Audit Architecture Backend — Industrialisation & Clean Code

**Date :** 03/03/2026
**Type :** Audit architecture (SOLID, Clean Code, performances, sécurité, industrialisation)
**Périmètre :** `app/` (81 fichiers .py) + `server/` (33 fichiers .py)
**Méthode :** Inspection systématique, analyse des dépendances croisées, audit des patterns
**Statut :** En cours — document vivant, mis à jour au fil des corrections

**Complémentaire à :** [AUDIT_CODE_CLEANUP_2026-03-01.md](./AUDIT_CODE_CLEANUP_2026-03-01.md) (bugs, dead code, incohérences — corrigé)

---

## Sommaire

1. [Résumé exécutif](#1-résumé-exécutif)
2. [Constats détaillés par pilier](#2-constats-détaillés)
3. [Plan d'implémentation priorisé](#3-plan-dimplémentation-priorisé)
4. [Détail des phases](#4-détail-des-phases)
5. [Matrice risque / bénéfice / difficulté](#5-matrice)
6. [Dépendances entre phases](#6-dépendances)
7. [Historique des corrections](#7-historique)

---

## 1. Résumé exécutif

| Pilier | Critical | High | Medium | Low | Total |
|--------|----------|------|--------|-----|-------|
| 🏗️ Architecture & SOLID | 3 | 4 | 5 | 0 | **12** |
| ✨ Clean Code & Lisibilité | 0 | 2 | 4 | 4 | **10** |
| 🚀 Performances | 0 | 1 | 2 | 1 | **4** |
| 🛡️ Robustesse & Sécurité | 1 | 3 | 1 | 0 | **5** |
| 🏭 Industrialisation | 0 | 0 | 3 | 2 | **5** |
| **Total** | **4** | **10** | **15** | **7** | **36** |

**Fichiers les plus impactés (par nombre de constats) :**

| Fichier | Lignes | Constats | Problème dominant |
|---------|--------|----------|-------------------|
| `server/exercise_generator.py` | 1693 | 6 | God file, 2 fonctions de 800+ lignes |
| `app/services/admin_service.py` | 1585 | 7 | God class, 9 domaines, 0 DTO |
| `server/handlers/challenge_handlers.py` | 965 | 4 | God handler 598 lignes |
| `server/handlers/chat_handlers.py` | 668 | 3 | 120 lignes dupliquées |
| `app/services/user_service.py` | 1116 | 5 | Fonction 199 lignes, SQL dupliqué |
| `server/middleware.py` | 339 | 5 | 3 registres de routes divergents |
| `app/services/auth_service.py` | 560 | 4 | Pattern incohérent, except dead |

---

## 2. Constats détaillés {#2-constats-détaillés}

### 🛡️ Sécurité (correction immédiate)

#### S1. CSRF bypass via env var `TESTING`

| | |
|---|---|
| **Fichier** | `server/middleware.py:206` + `app/utils/csrf.py:30` |
| **Sévérité** | CRITICAL |
| **Statut** | ✅ Corrigé (03/03/2026) |

```python
if os.getenv("TESTING", "false").lower() == "true":
    return await call_next(request)
```

**Problème :** Un kill-switch global désactive le CSRF pour toute l'app. Si un attaquant peut influencer les env vars (container mal configuré, SSRF), la protection CSRF est annulée.

**Correction appliquée :** Bypass TESTING supprimé dans `middleware.py` ET `csrf.py`. Les tests utilisent `unittest.mock.patch` session-scoped dans `conftest.py` — aucune surface d'attaque en production. Test de régression `test_testing_env_does_not_bypass_csrf` ajouté.

---

#### S2. Injection SQL dans `safe_delete` fallback

| | |
|---|---|
| **Fichier** | `app/db/transaction.py:152` |
| **Sévérité** | HIGH |
| **Statut** | ✅ Corrigé (03/03/2026) |

```python
stmt = f"DELETE FROM {obj.__tablename__} WHERE id = :id"
```

**Problème :** `__tablename__` interpolé directement. Risque faible (valeur contrôlée par le code) mais pattern dangereux qui pourrait être copié.

**Correction appliquée :** Garde ajoutée : `if not table_name.replace("_", "").isalnum(): return False` — rejette tout nom de table suspect avant l'interpolation SQL.

---

#### S3. Credentials DB par défaut en production

| | |
|---|---|
| **Fichier** | `app/core/config.py:57-58` |
| **Sévérité** | HIGH |
| **Statut** | ✅ Corrigé (03/03/2026) |

```python
POSTGRES_USER: str = Field(default="postgres")
POSTGRES_PASSWORD: str = Field(default="postgres")
```

**Problème :** Si `POSTGRES_PASSWORD` n'est pas défini en env, l'app se connecte avec `postgres:postgres`. La validation production (`_validate_production_settings`) vérifie `SECRET_KEY` et `DEFAULT_ADMIN_PASSWORD` mais pas `POSTGRES_PASSWORD`.

**Correction appliquée :** `POSTGRES_PASSWORD` ajouté à `_validate_production_settings` — rejette `""`, `"postgres"`, `"password"` en `ENVIRONMENT=production`.

---

#### S4. DATABASE_URL loggée avec credentials

| | |
|---|---|
| **Fichier** | `app/core/config.py:170-173` |
| **Sévérité** | HIGH |
| **Statut** | ✅ Corrigé (03/03/2026) |

```python
if settings.TESTING:
    logger.info(f"Mode test détecté, utilisation de l'URL: {settings.SQLALCHEMY_DATABASE_URL}")
```

**Correction appliquée :** `urlparse` utilisé pour extraire uniquement `host:port/db` — les credentials ne sont plus loggées.

---

#### S5. Except handlers inatteignables dans `refresh_access_token`

| | |
|---|---|
| **Fichier** | `app/services/auth_service.py:272-281` |
| **Sévérité** | HIGH — Robustesse |
| **Statut** | ✅ Corrigé (03/03/2026) |

**Problème :** `jwt.InvalidSignatureError` (sous-classe de `JWTError`) est attrapée après `JWTError` → inatteignable. Idem pour `jwt.ExpiredSignatureError`. Les utilisateurs reçoivent des messages d'erreur génériques au lieu de messages spécifiques.

**Correction appliquée :** `ExpiredSignatureError` placé en premier (message spécifique "Token de rafraîchissement expiré"). `InvalidSignatureError` supprimé (n'existe pas dans `python-jose` — les erreurs de signature sont wrappées en `JWTError`). Tests mis à jour pour vérifier les nouveaux messages spécifiques.

---

### 🏗️ Architecture & SOLID

#### A1. God file `exercise_generator.py`

| | |
|---|---|
| **Fichier** | `server/exercise_generator.py` (1693 lignes) |
| **Sévérité** | CRITICAL |
| **Statut** | ✅ Refactorisé (Phase 3.4, 03/03/2026) |

**Problème :** 2 fonctions quasi-identiques de 857 et 757 lignes chacune (`generate_ai_exercise`, `generate_simple_exercise`). 40+ branches `if/elif`. Cyclomatic complexity > 50. 80% de duplication entre les 2 fonctions — seule la couche narrative Star Wars diffère.

**Correction appliquée :** Extraction de 4 helpers partagés dans `exercise_generator_helpers.py` (`init_exercise_context`, `build_base_exercise_data`, `default_addition_fallback`, `apply_test_title`). Bloc d'initialisation et fallback dédupliqués. 25 tests de caractérisation + suite complète (651 tests, 0 échecs).

**Gain :** Réduction de la duplication, point d'entrée unique pour la normalisation et le fallback. Prépare une éventuelle future extraction Strategy pattern par type.

---

#### A2. God class `AdminService`

| | |
|---|---|
| **Fichier** | `app/services/admin_service.py` (1585 lignes) |
| **Sévérité** | CRITICAL |
| **Statut** | ✅ Découpé (Phase 3.3, 03/03/2026) |

**Problème :** 9 domaines métier dans 1 classe : Config, Dashboard, Audit, Modération, Rapports, Users, Badges, Exercices, Challenges, Export CSV.

**Correction appliquée :** Découpé en `AdminConfigService`, `AdminStatsService`, `AdminUserService`, `AdminContentService` + `admin_helpers.py` (helpers partagés). `AdminService` conservé comme façade re-exportant toutes les méthodes (Strangler Fig). 626 tests, 0 échecs.

---

#### A3. God handler `submit_challenge_answer`

| | |
|---|---|
| **Fichier** | `server/handlers/challenge_handlers.py:184-781` (598 lignes) |
| **Sévérité** | CRITICAL |
| **Statut** | ✅ Extrait (Phase 3.1, 03/03/2026) |

**Problème :** 7 fonctions helper définies inline, 7 algorithmes de comparaison par type de défi, vérification badges, streak, notification — tout dans 1 handler HTTP.

**Correction appliquée :** Créé `app/services/challenge_answer_service.py` avec les 7 algorithmes de comparaison + 4 helpers + dispatcher `check_answer()`. Handler réduit à parse request → `check_answer()` → format response. 47 tests de caractérisation + 626 tests complets, 0 échecs.

---

#### A4. Duplication massive `chat_api` / `chat_api_stream`

| | |
|---|---|
| **Fichier** | `server/handlers/chat_handlers.py` |
| **Sévérité** | HIGH |
| **Statut** | ✅ Factorisé (Phase 3.2, 03/03/2026) |

**Problème :** ~120 lignes copiées-collées entre les 2 handlers : listes de keywords, détection images, génération DALL-E, prompt building, config OpenAI.

**Correction appliquée :** Créé `app/services/chat_service.py` avec `detect_image_request`, `generate_image`, `build_chat_config`, `cleanup_markdown_images` + helpers (`_detect_complexity`, `_estimate_age`, `_build_system_prompt`). 19 tests de caractérisation + suite complète passante.

---

#### A5. User lookups dupliqués

| | |
|---|---|
| **Fichiers** | `app/services/auth_service.py` + `app/services/user_service.py` |
| **Sévérité** | HIGH |
| **Statut** | ⬜ À fusionner |

**Problème :** `get_user_by_username`, `get_user_by_email`, `get_user_by_id` existent dans les 2 fichiers avec des implémentations quasi-identiques.

**Correction recommandée :** Source unique dans `user_service.py`, `auth_service.py` les réutilise.

---

#### A6. 3 registres de routes divergents dans middleware

| | |
|---|---|
| **Fichier** | `server/middleware.py` |
| **Sévérité** | HIGH |
| **Statut** | ✅ Corrigé (03/03/2026) |

**Problème :** Auth whitelist, CSRF exempt, Maintenance exempt — 3 sets indépendants qui dérivent. Routes comme `/api/auth/login` apparaissent dans les 3.

**Correction appliquée :** `_ROUTE_REGISTRY` unique avec tuple `(path, methods, csrf_exempt)`. Les sets `_AUTH_PUBLIC_EXACT` et `_CSRF_EXEMPT_NORMALIZED` sont dérivés automatiquement à l'initialisation du module. Maintenance exempt reste séparé (préoccupation différente).

---

#### A7. `auth_service.py` pattern incohérent

| | |
|---|---|
| **Fichier** | `app/services/auth_service.py` |
| **Sévérité** | MEDIUM |
| **Statut** | ⬜ À aligner |

**Problème :** Fonctions module-level alors que tous les autres services sont des classes. `HTTPException` (FastAPI) levée dans la couche service — couple au framework.

**Correction recommandée :** Convertir en classe `AuthService`. Remplacer `HTTPException` par un result type ou une exception métier.

---

#### A8. `list_challenges` / `count_challenges` — 90% dupliqué

| | |
|---|---|
| **Fichier** | `app/services/challenge_service.py` |
| **Sévérité** | MEDIUM |
| **Statut** | ⬜ À factoriser |

**Correction recommandée :** Extraire `_apply_challenge_filters(query, ...)` réutilisé par les 2 fonctions + par `admin_service`.

---

#### A9. `get_user_stats_for_dashboard` — 199 lignes, 7 responsabilités

| | |
|---|---|
| **Fichier** | `app/services/user_service.py:420-619` |
| **Sévérité** | MEDIUM |
| **Statut** | ⬜ À décomposer |

**Correction recommandée :** Découper en 7 méthodes privées. La méthode principale orchestre les appels.

---

#### A10. `constants.py` — 12 concerns dans 1 fichier

| | |
|---|---|
| **Fichier** | `app/core/constants.py` (563 lignes) |
| **Sévérité** | MEDIUM |
| **Statut** | ⬜ À découper |

**Correction recommandée :** Découper en `exercise_constants.py`, `challenge_constants.py`, `user_constants.py`, `normalization.py`.

---

### ✨ Clean Code & Lisibilité

#### CC1. 4 patterns de parsing body dans les handlers

| | |
|---|---|
| **Fichiers** | Tous les handlers |
| **Sévérité** | HIGH |
| **Statut** | ✅ Corrigé (03/03/2026) |

**Patterns trouvés :**
1. `parse_json_body(request, required=[], optional=[])` — validant
2. `parse_json_body_any(request)` — sans validation
3. `await request.json()` — brut
4. `await request.body()` + `json.loads` — manuel

**Même fichier, patterns différents :** `chat_handlers.py` utilise `parse_json_body` dans `chat_api` mais `request.json()` dans `chat_api_stream`. `auth_handlers.py` utilise les 3 premiers.

**Correction appliquée :** Tous les handlers utilisent `parse_json_body` ou `parse_json_body_any`. Les 5 `await request.json()` bruts remplacés. Imports inline montés en top-level.

---

#### CC2. 4 patterns de réponse erreur

| | |
|---|---|
| **Fichiers** | Tous les handlers |
| **Sévérité** | HIGH |
| **Statut** | ✅ Corrigé (03/03/2026) |

**Patterns trouvés :**
1. `api_error_response(status, msg)` — canonique
2. `ErrorHandler.create_error_response(error, status_code, user_message)`
3. `ErrorHandler.create_validation_error(errors, user_message)`
4. `JSONResponse({"error": ...})` ad-hoc

**Correction appliquée :** 2 `JSONResponse({error:...})` dans `chat_handlers.py` remplacés par `api_error_response()`. Pattern désormais unifié.

---

#### CC3. 17 `traceback.print_exc()` vs `logger.debug(traceback.format_exc())`

| | |
|---|---|
| **Fichiers** | `user_handlers` (10), `challenge_handlers` (2), `exercise_handlers` (1), `chat_handlers` (2) |
| **Sévérité** | MEDIUM |
| **Statut** | ✅ Corrigé (03/03/2026) |

**Correction appliquée :** 26 occurrences de `traceback.print_exc()` dans 7 fichiers handlers remplacées par `logger.error(..., exc_info=True)`. Imports `traceback` nettoyés quand devenus inutiles.

---

#### CC4. Type hints absents sur handlers

| | |
|---|---|
| **Fichiers** | `exercise_handlers` (6/8 sans type), `chat_handlers` (2/2) |
| **Sévérité** | MEDIUM |
| **Statut** | ✅ Corrigé (03/03/2026) |

**Correction appliquée :** Return type `-> JSONResponse` (ou `-> Response` pour streaming) ajouté sur ~80 handlers. `request` typé `Request` partout.

---

#### CC5. Cookie config dupliquée 4 fois

| | |
|---|---|
| **Fichiers** | `auth_handlers` (x3), `user_handlers` (x1) |
| **Sévérité** | MEDIUM |
| **Statut** | ✅ Corrigé (03/03/2026) |

**Correction appliquée :** `get_cookie_config()` extraite dans `app/core/security.py`. 4 duplications remplacées dans `auth_handlers.py` et `user_handlers.py`.

---

#### CC6. Validation mot de passe dupliquée

| | |
|---|---|
| **Fichiers** | `auth_handlers`, `user_handlers` |
| **Sévérité** | MEDIUM |
| **Statut** | ✅ Corrigé (03/03/2026) |

**Correction appliquée :** `validate_password_strength()` extraite dans `app/core/security.py`. 3 duplications dans handlers + 1 dans schema Pydantic refactorisées.

---

#### CC7–CC10. Low priority

| # | Constat | Fichiers |
|---|---------|----------|
| CC7 | f-strings dans `logger.info/error()` | Middleware, handlers |
| CC8 | `VALID_THEMES`, `FRONTEND_URL` hardcodés dans handlers | `user_handlers`, `auth_handlers` |
| CC9 | `import traceback` inside except blocks | `exercise_service`, `chat_handlers` |
| CC10 | `PROJECT_VERSION` hardcodé `"2.1.0"` duplique `package.json` | `config.py` |

---

### 🚀 Performances

#### P1. CORS origins — 2 sources de vérité

| | |
|---|---|
| **Fichier** | `server/middleware.py:270-301` vs `app/core/config.py:109-119` |
| **Sévérité** | HIGH |
| **Statut** | ✅ Corrigé (03/03/2026) |

**Problème :** `get_middleware()` construit sa propre liste d'origines CORS en ignorant `settings.BACKEND_CORS_ORIGINS`.

**Correction appliquée :** `middleware.py` utilise désormais `settings.BACKEND_CORS_ORIGINS`. Logique www-variant et render.com fallback centralisée dans `config.py`.

---

#### P2. `normalize_age_group` — O(n*m) alias scan

| | |
|---|---|
| **Fichier** | `app/core/constants.py:179-214` |
| **Sévérité** | MEDIUM |
| **Statut** | ✅ Corrigé (03/03/2026) |

**Correction appliquée :** Dict plat `_AGE_GROUP_LOOKUP` pré-calculé au chargement du module. Lookup O(1) au lieu de O(n*m).

---

#### P3. CSRF exempt set reconstruit à chaque requête mutante

| | |
|---|---|
| **Fichier** | `server/middleware.py:200-202` |
| **Sévérité** | MEDIUM |
| **Statut** | ✅ Corrigé (03/03/2026) |

**Correction appliquée :** `_CSRF_EXEMPT_NORMALIZED` est un `frozenset` pré-calculé, dérivé automatiquement de `_ROUTE_REGISTRY`.

---

#### P4. `SELECT *` et `ORDER BY RANDOM()` dans `queries.py`

| | |
|---|---|
| **Fichier** | `app/db/queries.py` |
| **Sévérité** | LOW (dead code) |
| **Statut** | ⬜ Supprimer le fichier |

---

### 🏭 Industrialisation

#### I1. `Dict[str, Any]` partout — aucun DTO

| | |
|---|---|
| **Fichiers** | Tous les services |
| **Sévérité** | MEDIUM |
| **Statut** | ⬜ À typer |

**Problème :** Services retournent des `Dict[str, Any]` ou des tuples opaques `(Optional[Dict], Optional[str], int)`. Aucun contrat typé — mypy ne détecte rien.

**Correction recommandée :** Introduire des `TypedDict` ou `dataclass` pour les retours de services (`UserStatsResult`, `AdminListResponse`, etc.).

---

#### I2. `int()` non protégé sur path params admin

| | |
|---|---|
| **Fichier** | `server/handlers/admin_handlers.py` — 14 occurrences |
| **Sévérité** | MEDIUM |
| **Statut** | ⬜ À protéger |

**Correction recommandée :** Helper `safe_int_path_param(request, name) -> int` avec retour 400 si invalide.

---

#### I3. `AdminService` importé 28 fois inline

| | |
|---|---|
| **Fichier** | `server/handlers/admin_handlers.py` |
| **Sévérité** | MEDIUM |
| **Statut** | ✅ Corrigé (03/03/2026) |

**Correction appliquée :** Import unique top-level dans `admin_handlers.py`. 28 imports inline supprimés.

---

#### I4. Dead code résiduel

| | |
|---|---|
| **Fichiers** | `queries.py` (402 lignes), `LoggingLevels`/`ExerciseStatus` dans constants |
| **Sévérité** | LOW |
| **Statut** | ⬜ À supprimer |

---

#### I5. `safe_delete`/`safe_archive` retournent des booléens

| | |
|---|---|
| **Fichier** | `app/db/transaction.py` |
| **Sévérité** | LOW |
| **Statut** | ⬜ À repenser |

---

## 3. Plan d'implémentation priorisé {#3-plan-dimplémentation-priorisé}

### Critères de priorisation

Chaque action est évaluée sur 4 axes (score 1-5) :

| Axe | 1 | 5 |
|-----|---|---|
| **Risque** (si on ne fait rien) | Cosmétique | Faille production |
| **Bénéfice** | Confort développeur | Prévient des bugs critiques |
| **Difficulté** | 5 = très difficile | 1 = trivial |
| **Impact chaîné** | Isolé | Débloque d'autres phases |

### Vue d'ensemble

```
Phase 0 ──► Phase 1 ──► Phase 2 ──────────► Phase 3 ──► Phase 4
Sécurité    Standards    Services légers      God files    Industrialisation
(1 jour)    (2-3 jours)  (2-3 jours)         (5-7 jours)  (2-3 jours)
                │                                  ▲
                └────── débloque ─────────────────┘
```

---

## 4. Détail des phases {#4-détail-des-phases}

### Phase 0 — Sécurité (1 jour)

**Justification :** Aucune autre phase ne réduit le risque production. Ces corrections sont isolées (pas de cascade), rapides, et sans régression possible.

| # | Action | Constat | Difficulté | Test |
|---|--------|---------|------------|------|
| 0.1 | Supprimer le bypass CSRF `TESTING` env var — mock le middleware en test | S1 | Facile | Tests CSRF existants (23) à vérifier sans env var |
| 0.2 | Protéger `safe_delete` : `assert __tablename__.isalnum()` | S2 | Trivial | Test régression : delete d'un objet standard |
| 0.3 | Ajouter `POSTGRES_PASSWORD` à `_validate_production_settings` | S3 | Trivial | Test unitaire |
| 0.4 | Masquer credentials dans le log `DATABASE_URL` | S4 | Facile | Test unitaire |
| 0.5 | Réordonner except blocks dans `refresh_access_token` | S5 | Facile | Tests auth existants |
| 0.6 | Protéger les 14 `int()` path params dans `admin_handlers` | I2 | Facile | 14 tests de régression |

---

### Phase 1 — Standardisation des patterns ✅ TERMINÉE (03/03/2026)

**Justification :** Avant de refactoriser les gros fichiers, il faut que les patterns soient cohérents. Sinon, chaque extraction de service reproduira les incohérences.

**Prérequis :** Phase 0 (sécurité middleware OK avant de toucher aux handlers).
**Résultat :** 394/394 tests passed, Black OK. 10/10 items implémentés.

| # | Action | Constat | Statut |
|---|--------|---------|--------|
| 1.1 | Unifier parsing body → `parse_json_body` partout | CC1 | ✅ |
| 1.2 | Unifier réponses erreur → `api_error_response` partout | CC2 | ✅ |
| 1.3 | Remplacer 26 `traceback.print_exc()` par `logger.error(..., exc_info=True)` | CC3 | ✅ |
| 1.4 | Extraire `get_cookie_config()` | CC5 | ✅ |
| 1.5 | Extraire `validate_password_strength()` partagé | CC6 | ✅ |
| 1.6 | Ajouter type hints (`-> JSONResponse`/`-> Response`) sur ~80 handlers | CC4 | ✅ |
| 1.7 | Unifier les registres de routes middleware (`_ROUTE_REGISTRY`) | A6 | ✅ |
| 1.8 | Unifier CORS origins → `settings.BACKEND_CORS_ORIGINS` unique | P1 | ✅ |
| 1.9 | Pré-calculer CSRF exempt frozenset + `normalize_age_group` dict O(1) | P2, P3 | ✅ |
| 1.10 | Monter `AdminService` en import top-level (28 inline → 1) | I3 | ✅ |

---

### Phase 2 — Refactoring services légers ✅ TERMINÉE (03/03/2026)

**Justification :** Corrections de structure dans les services sans toucher aux 3 God objects. Chaque action est autonome, faible risque de régression.

**Prérequis :** Phase 1 (patterns standardisés pour que les services extraits soient cohérents).

| # | Action | Constat | Statut |
|---|--------|---------|--------|
| 2.1 | Fusionner user lookups → source unique dans `user_service.py` | A5 | ✅ Corrigé (03/03/2026) |
| 2.2 | Aligner `auth_service.py` → pattern tuple (plus de HTTPException) | A7 | ✅ Corrigé (03/03/2026) |
| 2.3 | Extraire `_apply_challenge_filters()` dans `challenge_service.py` | A8 | ✅ Corrigé (03/03/2026) |
| 2.4 | Décomposer `get_user_stats_for_dashboard` en 4 sous-méthodes | A9 | ✅ Corrigé (03/03/2026) |
| 2.5 | Supprimer `queries.py` (dead code confirmé) | I4 | ✅ Corrigé (03/03/2026) |
| 2.6 | Supprimer `LoggingLevels`, `ExerciseStatus` de constants | I4 | ✅ Corrigé (03/03/2026) |
| 2.7 | Déplacer `VALID_THEMES`, `FRONTEND_URL` vers `constants.py`/`config.py` | CC8 | ✅ Corrigé (03/03/2026) |
| 2.8 | Remplacer `HTTPException` par exception métier dans `auth_service` | A7 | ✅ Corrigé (03/03/2026) |
| 2.9 | Introduire les premiers `TypedDict` sur les retours les plus utilisés | I1 | ✅ Corrigé (03/03/2026) |

**Corrections appliquées Phase 2 :**

- **2.1** : Les 3 fonctions standalone `get_user_by_*` dans `auth_service.py` délèguent désormais à `UserService`. Les `db.query(User).filter(...)` inline dans `admin_service.py` (3), `badge_service.py` (4) et `user_service.py` (2) remplacés par `UserService.get_user()`.
- **2.2 + 2.8** : `auth_service.py` ne dépend plus de `fastapi.HTTPException`. `create_user`, `refresh_access_token`, `update_user_password` retournent des tuples `(result, error, status)`, comme `AdminService`. Les handlers et les 33 tests unitaires mis à jour.
- **2.3** : Extraction de `_apply_challenge_filters()` dans `challenge_service.py`. Le bloc de ~40 lignes dupliqué entre `list_challenges` et `count_challenges` est maintenant factorisé. Import `adapt_enum_for_db` monté au top-level.
- **2.4** : `get_user_stats_for_dashboard` (~200 lignes) décomposé en orchestrateur + 4 sous-méthodes : `_compute_performance_by_type`, `_fetch_recent_activity`, `_compute_progress_over_time`, `_count_completed_challenges`.
- **2.5** : Suppression de `app/db/queries.py` (403 lignes de dead code legacy) et `tests/unit/test_queries.py` (13 tests obsolètes).
- **2.6** : Suppression de `LoggingLevels` (redondant avec `logging` stdlib) et `ExerciseStatus` (redondant avec `True`/`False`) dans `constants.py`.
- **2.7** : `VALID_THEMES` et `VALID_LEARNING_STYLES` centralisés dans `constants.py` (frozenset). `FRONTEND_URL` ajouté comme champ Pydantic dans `config.py`. 8 `os.getenv("FRONTEND_URL", ...)` dupliqués remplacés par `settings.FRONTEND_URL`.
- **2.9** : Nouveau module `app/core/types.py` avec `TokenResponse`, `TokenRefreshResponse`, `PaginatedResponse`, `DashboardStats`, `PerformanceByType`, `ChartData`, `ChartDataset`. Appliqués sur `auth_service.py` et `user_service.py`.

---

### Phase 3 — Refactoring des God objects ✅ TERMINÉE (03/03/2026)

**Justification :** Les 3 plus gros chantiers du codebase. Chacun est un risque de régression élevé mais le bénéfice structurel est majeur. À faire dans cet ordre :

**Prérequis :** Phases 1+2 (patterns cohérents, helpers extraits, DTOs disponibles).

| # | Action | Constat | Difficulté | Test |
|---|--------|---------|------------|------|
| 3.1 | **Extraire `ChallengeAnswerService`** — 7 algorithmes de comparaison dans un service testable | A3 | Élevé | Nouveau fichier test dédié + tests handlers existants |
| 3.2 | **Extraire `ChatService`** — factoriser les 120 lignes dupliquées | A4 | Moyen | Tests chat existants |
| 3.3 | **Découper `AdminService`** en 4-5 services spécialisés | A2 | Élevé | 25+ tests admin existants |
| 3.4 | **Refactoriser `exercise_generator.py`** — Strategy pattern, fusion AI/simple | A1 | Très élevé | Tests génération + tests E2E |

**Ordre logique Phase 3 :**
- **3.1 avant 3.3** : le pattern d'extraction de `submit_challenge_answer` sert de modèle pour le découpage `AdminService`
- **3.2** : rapide, autonome, peut se faire en parallèle de 3.1
- **3.3** : utilise les DTOs de Phase 2.9 et le pattern d'extraction de 3.1
- **3.4 en dernier** : le plus risqué, touche la génération de contenu. Nécessite une validation E2E complète

---

### Phase 4 — Industrialisation ✅ PARTIELLEMENT TERMINÉE (03/03/2026)

**Justification :** Dernière couche de polish — finit les TypedDict, découpe les constantes, nettoie les derniers anti-patterns. Faible risque, bénéfice de maintenabilité long terme.

**Prérequis :** Phase 3 (les services découpés ont besoin de DTOs finalisés).

| # | Action | Constat | Difficulté | Statut | Détail |
|---|--------|---------|------------|--------|--------|
| 4.1 | Compléter les `TypedDict`/`dataclass` sur tous les retours services | I1 | Moyen | ✅ Corrigé | `UserProgressDict`, `ChallengesProgressDict`, `ChallengeStatsDict`, `AuditLogPageDict`, `ModerationDict`, `AdminReportDict`, `AdminUserListDict`, `AdminUserItemDict` dans `app/core/types.py`. Appliqués à `admin_stats_service`, `challenge_service`, `user_service`, `admin_user_service`. |
| 4.2 | Découper `constants.py` en modules par domaine | A10 | Facile | ✅ Corrigé | `app/core/constants_challenge.py` extrait (challenge types, aliases, `normalize_challenge_type`, `AGE_GROUPS_DB`). `constants.py` re-exporte via hub pour compat. Extensible (exercise, user…). |
| 4.3 | Adopter `format_paginated_response` dans les handlers | H9 câblage | Facile | ✅ Corrigé | Appliqué dans `exercise_service.py` (service) et `challenge_handlers.py`. `user_handlers.py` — aucune pagination inline trouvée. |
| 4.4 | Adopter `enum_mapping.py` dans les handlers | H9 câblage | Facile | ✅ Corrigé | `challenge_handlers.py` → `age_group_exercise_from_api`. `challenge_list_params.py` → `challenge_type_from_api` + `age_group_challenge_from_api`. `exercise_list_params.py` déjà propre (via `normalize_and_validate_exercise_params`). |
| 4.5 | Repenser `safe_delete`/`safe_archive` → exceptions | I5 | Moyen | ⏳ Différé | Touche 10+ fichiers dont 5 fichiers de tests avec assertions `result is False`. Rapport risque/bénéfice défavorable à ce stade. À traiter dans une prochaine itération dédiée. |

---

## 5. Matrice risque / bénéfice / difficulté {#5-matrice}

| Phase | Risque (si rien) | Bénéfice | Difficulté | Impact chaîné | Durée | ROI |
|-------|-----------------|----------|------------|---------------|-------|-----|
| **Phase 0** Sécurité | ⬛⬛⬛⬛⬛ 5/5 | ⬛⬛⬛⬛⬛ 5/5 | ⬛ 1/5 | Faible | 1 jour | **Immédiat** |
| **Phase 1** Standards | ⬛⬛⬛ 3/5 | ⬛⬛⬛⬛ 4/5 | ⬛⬛ 2/5 | **Élevé** (débloque P2+P3) | 2-3 jours | **Très élevé** |
| **Phase 2** Services légers ✅ | ⬛⬛ 2/5 | ⬛⬛⬛ 3/5 | ⬛⬛ 2/5 | Moyen (débloque P3) | 2-3 jours | Élevé |
| **Phase 3** God objects ✅ | ⬛⬛⬛ 3/5 | ⬛⬛⬛⬛⬛ 5/5 | ⬛⬛⬛⬛ 4/5 | Faible | 5-7 jours | Élevé (long terme) |
| **Phase 4** Industrialisation ✅ | ⬛ 1/5 | ⬛⬛⬛ 3/5 | ⬛⬛ 2/5 | Faible | 2-3 jours | Moyen |

**Recommandation :** Phases 0 et 1 ont le meilleur ROI — faible effort, haut impact, débloquent la suite. Phase 3 est le gros investissement à planifier sur un sprint dédié.

---

## 6. Dépendances entre phases {#6-dépendances}

```
Phase 0 (Sécurité)
  │
  ▼
Phase 1 (Standards) ◄── impérative avant toute extraction de service
  │
  ├──► Phase 2 (Services légers) ◄── peut démarrer dès Phase 1 terminée
  │      │
  │      ▼
  └──► Phase 3 (God objects) ◄── utilise les helpers et DTOs de Phase 2
         │
         ▼
       Phase 4 (Industrialisation) ◄── finalise le typage après les découpages
```

**Actions parallélisables :**
- Phase 2.1–2.6 (services légers) sont indépendantes entre elles
- Phase 3.1 (ChallengeAnswerService) et 3.2 (ChatService) sont indépendantes
- Phase 4.1–4.5 sont indépendantes entre elles

**Dépendances dures :**
- Phase 1.7 (registres routes) avant Phase 0.1 si on veut tester le CSRF proprement
- Phase 2.9 (TypedDict) avant Phase 3.3 (AdminService) pour typer les retours
- Phase 3.1 (extraction pattern) avant Phase 3.3 (réutilisation du pattern)
- Phase 3.4 (exercise_generator) en dernier : risque maximal, nécessite E2E

---

## 7. Historique des corrections {#7-historique}

| Date | Phase | Item | Détail |
|------|-------|------|--------|
| 03/03/2026 | — | — | Création du document (audit initial) |
| 03/03/2026 | 0 | S1 | Suppression bypass CSRF `TESTING` env var dans `middleware.py` + `csrf.py`. Mock session-scoped dans `conftest.py`. Test de régression ajouté. |
| 03/03/2026 | 0 | S2 | Garde `isalnum()` ajoutée sur `__tablename__` dans `safe_delete` fallback SQL. |
| 03/03/2026 | 0 | S3 | `POSTGRES_PASSWORD` ajouté à la validation production (`_validate_production_settings`). |
| 03/03/2026 | 0 | S4 | Log `DATABASE_URL` masqué via `urlparse` (host/port/db uniquement). |
| 03/03/2026 | 0 | S5 | `ExpiredSignatureError` en premier except. `InvalidSignatureError` supprimé (inexistant dans python-jose). Tests mis à jour. |
| 03/03/2026 | 0 | I2 | Déjà corrigé — `int()` wrappers remplacés par accès direct `path_params["key"]` (Starlette `:int` converter). |
| 03/03/2026 | 1 | CC3 | 26 `traceback.print_exc()` → `logger.error(..., exc_info=True)` dans 7 fichiers handlers. Imports nettoyés. |
| 03/03/2026 | 1 | P2, P3 | `normalize_age_group` O(1) via dict pré-calculé. `_CSRF_EXEMPT_NORMALIZED` frozenset pré-calculé. |
| 03/03/2026 | 1 | I3 | `AdminService` : 28 imports inline → 1 import top-level dans `admin_handlers.py`. |
| 03/03/2026 | 1 | P1 | CORS origins unifié : `middleware.py` utilise `settings.BACKEND_CORS_ORIGINS` (source unique dans `config.py`). |
| 03/03/2026 | 1 | CC5 | `get_cookie_config()` extraite dans `app/core/security.py`. 4 duplications éliminées. |
| 03/03/2026 | 1 | CC6 | `validate_password_strength()` extraite dans `app/core/security.py`. 3 duplications handlers + 1 schema. |
| 03/03/2026 | 1 | CC1 | Parsing body unifié : `parse_json_body`/`parse_json_body_any` partout. 5 `request.json()` bruts remplacés, 4 imports inline montés top-level. |
| 03/03/2026 | 1 | CC2 | 2 `JSONResponse(error)` → `api_error_response()` dans `chat_handlers.py`. |
| 03/03/2026 | 1 | CC4 | Return types `-> JSONResponse`/`-> Response` ajoutés sur ~80 handlers. `request: Request` typé partout. |
| 03/03/2026 | 1 | A6 | `_ROUTE_REGISTRY` unique : auth-whitelist et CSRF-exempt dérivés automatiquement. |
| 03/03/2026 | 2 | 2.5 | Suppression `app/db/queries.py` (403 lignes dead code) et `tests/unit/test_queries.py` (13 tests obsolètes). |
| 03/03/2026 | 2 | 2.6 | Suppression `LoggingLevels` et `ExerciseStatus` (dead code dans `constants.py`). |
| 03/03/2026 | 2 | 2.7 | `VALID_THEMES`/`VALID_LEARNING_STYLES` → `constants.py` (frozenset). `FRONTEND_URL` → champ Pydantic `config.py`. 8 `os.getenv` dupliqués éliminés. |
| 03/03/2026 | 2 | 2.1 | User lookups : 3 fonctions `auth_service.py` délèguent à `UserService`. 9 `db.query(User).filter(...)` inline → `UserService.get_user()`. |
| 03/03/2026 | 2 | 2.3 | `_apply_challenge_filters()` extraite dans `challenge_service.py`. 2×40 lignes dupliquées → 1 fonction partagée. |
| 03/03/2026 | 2 | 2.2+2.8 | `auth_service.py` : `fastapi.HTTPException` éliminé. `create_user`, `refresh_access_token`, `update_user_password` → tuples. 33 tests adaptés. |
| 03/03/2026 | 2 | 2.4 | `get_user_stats_for_dashboard` (~200 lignes) → orchestrateur + 4 sous-méthodes privées. |
| 03/03/2026 | 2 | 2.9 | Nouveau `app/core/types.py` : 7 TypedDict (`TokenResponse`, `DashboardStats`, `ChartData`…). Appliqués sur `auth_service.py` et `user_service.py`. |

---

## Références

- [AUDIT_CODE_CLEANUP_2026-03-01.md](./AUDIT_CODE_CLEANUP_2026-03-01.md) — Audit bugs, dead code, incohérences (corrigé)
- [AUDIT_BACKEND_INDUSTRIALISATION_2026-02.md](./AUDIT_BACKEND_INDUSTRIALISATION_2026-02.md) — Audit backend précédent (itérations 1–5)
- [REFACTOR_STATUS_2026-02.md](./REFACTOR_STATUS_2026-02.md) — État du refactoring
- [docs/01-GUIDES/TESTING.md](../01-GUIDES/TESTING.md) — Guide tests
