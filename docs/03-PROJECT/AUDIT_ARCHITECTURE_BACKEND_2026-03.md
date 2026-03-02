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
| **Fichier** | `server/middleware.py:206` |
| **Sévérité** | CRITICAL |
| **Statut** | ⬜ À corriger |

```python
if os.getenv("TESTING", "false").lower() == "true":
    return await call_next(request)
```

**Problème :** Un kill-switch global désactive le CSRF pour toute l'app. Si un attaquant peut influencer les env vars (container mal configuré, SSRF), la protection CSRF est annulée.

**Correction recommandée :** Supprimer le bypass env var. Injecter le comportement de test via une fixture pytest qui mock le middleware ou via un header de test dédié (`X-Test-Bypass-CSRF`) accepté uniquement quand `DEBUG=true` + requête locale.

---

#### S2. Injection SQL dans `safe_delete` fallback

| | |
|---|---|
| **Fichier** | `app/db/transaction.py:152` |
| **Sévérité** | HIGH |
| **Statut** | ⬜ À corriger |

```python
stmt = f"DELETE FROM {obj.__tablename__} WHERE id = :id"
```

**Problème :** `__tablename__` interpolé directement. Risque faible (valeur contrôlée par le code) mais pattern dangereux qui pourrait être copié.

**Correction recommandée :** Ajouter `assert obj.__tablename__.isalnum()` avant l'interpolation, ou mieux : supprimer le fallback raw SQL (l'ORM `db.delete()` suffit).

---

#### S3. Credentials DB par défaut en production

| | |
|---|---|
| **Fichier** | `app/core/config.py:57-58` |
| **Sévérité** | HIGH |
| **Statut** | ⬜ À corriger |

```python
POSTGRES_USER: str = Field(default="postgres")
POSTGRES_PASSWORD: str = Field(default="postgres")
```

**Problème :** Si `POSTGRES_PASSWORD` n'est pas défini en env, l'app se connecte avec `postgres:postgres`. La validation production (`_validate_production_settings`) vérifie `SECRET_KEY` et `DEFAULT_ADMIN_PASSWORD` mais pas `POSTGRES_PASSWORD`.

**Correction recommandée :** Ajouter `POSTGRES_PASSWORD` à la validation production.

---

#### S4. DATABASE_URL loggée avec credentials

| | |
|---|---|
| **Fichier** | `app/core/config.py:170-173` |
| **Sévérité** | HIGH |
| **Statut** | ⬜ À corriger |

```python
if settings.TESTING:
    logger.info(f"Mode test détecté, utilisation de l'URL: {settings.SQLALCHEMY_DATABASE_URL}")
```

**Correction recommandée :** Logger uniquement le host/db, pas le password. Utiliser `urlparse` pour masquer les credentials.

---

#### S5. Except handlers inatteignables dans `refresh_access_token`

| | |
|---|---|
| **Fichier** | `app/services/auth_service.py:272-281` |
| **Sévérité** | HIGH — Robustesse |
| **Statut** | ⬜ À corriger |

**Problème :** `jwt.InvalidSignatureError` (sous-classe de `JWTError`) est attrapée après `JWTError` → inatteignable. Idem pour `jwt.ExpiredSignatureError`. Les utilisateurs reçoivent des messages d'erreur génériques au lieu de messages spécifiques.

**Correction recommandée :** Réordonner les except blocks : sous-classes avant la classe parente.

---

### 🏗️ Architecture & SOLID

#### A1. God file `exercise_generator.py`

| | |
|---|---|
| **Fichier** | `server/exercise_generator.py` (1693 lignes) |
| **Sévérité** | CRITICAL |
| **Statut** | ⬜ À refactoriser |

**Problème :** 2 fonctions quasi-identiques de 857 et 757 lignes chacune (`generate_ai_exercise`, `generate_simple_exercise`). 40+ branches `if/elif`. Cyclomatic complexity > 50. 80% de duplication entre les 2 fonctions — seule la couche narrative Star Wars diffère.

**Correction recommandée :** Strategy pattern — 1 classe de base `ExerciseGenerator` + 1 stratégie par type d'exercice (8 fichiers de ~80 lignes). Paramètre `narrative_style` pour fusionner AI et simple.

**Gain :** Ajouter un type d'exercice = créer 1 fichier, pas modifier 2 fonctions de 800 lignes.

---

#### A2. God class `AdminService`

| | |
|---|---|
| **Fichier** | `app/services/admin_service.py` (1585 lignes) |
| **Sévérité** | CRITICAL |
| **Statut** | ⬜ À découper |

**Problème :** 9 domaines métier dans 1 classe : Config, Dashboard, Audit, Modération, Rapports, Users, Badges, Exercices, Challenges, Export CSV.

**Correction recommandée :** Découper en `AdminUserService`, `AdminContentService` (exercises + challenges), `AdminBadgeService`, `AdminExportService`. Conserver un `AdminService` façade si besoin.

---

#### A3. God handler `submit_challenge_answer`

| | |
|---|---|
| **Fichier** | `server/handlers/challenge_handlers.py:184-781` (598 lignes) |
| **Sévérité** | CRITICAL |
| **Statut** | ⬜ À extraire |

**Problème :** 7 fonctions helper définies inline, 7 algorithmes de comparaison par type de défi, vérification badges, streak, notification — tout dans 1 handler HTTP.

**Correction recommandée :** Extraire dans un `ChallengeAnswerService` avec les algorithmes de comparaison. Le handler ne fait plus que : parse request → appel service → format response.

---

#### A4. Duplication massive `chat_api` / `chat_api_stream`

| | |
|---|---|
| **Fichier** | `server/handlers/chat_handlers.py` |
| **Sévérité** | HIGH |
| **Statut** | ⬜ À factoriser |

**Problème :** ~120 lignes copiées-collées entre les 2 handlers : listes de keywords, détection images, génération DALL-E, prompt building, config OpenAI.

**Correction recommandée :** Extraire un `ChatService` avec les méthodes partagées.

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
| **Statut** | ⬜ À unifier |

**Problème :** Auth whitelist, CSRF exempt, Maintenance exempt — 3 sets indépendants qui dérivent. Routes comme `/api/auth/login` apparaissent dans les 3.

**Correction recommandée :** 1 structure unique `RouteConfig` : `{path: {auth_required, csrf_required, maintenance_exempt}}`.

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
| **Statut** | ⬜ À standardiser |

**Patterns trouvés :**
1. `parse_json_body(request, required=[], optional=[])` — validant
2. `parse_json_body_any(request)` — sans validation
3. `await request.json()` — brut
4. `await request.body()` + `json.loads` — manuel

**Même fichier, patterns différents :** `chat_handlers.py` utilise `parse_json_body` dans `chat_api` mais `request.json()` dans `chat_api_stream`. `auth_handlers.py` utilise les 3 premiers.

**Correction recommandée :** Adopter `parse_json_body` partout (avec `required` et `optional`).

---

#### CC2. 4 patterns de réponse erreur

| | |
|---|---|
| **Fichiers** | Tous les handlers |
| **Sévérité** | HIGH |
| **Statut** | ⬜ À standardiser |

**Patterns trouvés :**
1. `api_error_response(status, msg)` — canonique
2. `ErrorHandler.create_error_response(error, status_code, user_message)`
3. `ErrorHandler.create_validation_error(errors, user_message)`
4. `JSONResponse({"error": ...})` ad-hoc

**Correction recommandée :** Adopter `api_error_response` partout, déprécier `ErrorHandler.create_*`.

---

#### CC3. 17 `traceback.print_exc()` vs `logger.debug(traceback.format_exc())`

| | |
|---|---|
| **Fichiers** | `user_handlers` (10), `challenge_handlers` (2), `exercise_handlers` (1), `chat_handlers` (2) |
| **Sévérité** | MEDIUM |
| **Statut** | ⬜ À standardiser |

**Correction recommandée :** Remplacer tous par `logger.error("...", exc_info=True)`.

---

#### CC4. Type hints absents sur handlers

| | |
|---|---|
| **Fichiers** | `exercise_handlers` (6/8 sans type), `chat_handlers` (2/2) |
| **Sévérité** | MEDIUM |
| **Statut** | ⬜ À compléter |

**Correction recommandée :** Ajouter `request: Request` et `-> JSONResponse` sur tous les handlers.

---

#### CC5. Cookie config dupliquée 4 fois

| | |
|---|---|
| **Fichiers** | `auth_handlers` (x3), `user_handlers` (x1) |
| **Sévérité** | MEDIUM |
| **Statut** | ⬜ À factoriser |

**Correction recommandée :** Extraire `get_cookie_config() -> CookieConfig`.

---

#### CC6. Validation mot de passe dupliquée

| | |
|---|---|
| **Fichiers** | `auth_handlers`, `user_handlers` |
| **Sévérité** | MEDIUM |
| **Statut** | ⬜ À factoriser |

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
| **Statut** | ⬜ À unifier |

**Problème :** `get_middleware()` construit sa propre liste d'origines CORS en ignorant `settings.BACKEND_CORS_ORIGINS`.

---

#### P2. `normalize_age_group` — O(n*m) alias scan

| | |
|---|---|
| **Fichier** | `app/core/constants.py:179-214` |
| **Sévérité** | MEDIUM |
| **Statut** | ⬜ À optimiser |

**Correction recommandée :** Pré-calculer un dict plat `{alias: group}` au module-level → lookup O(1).

---

#### P3. CSRF exempt set reconstruit à chaque requête mutante

| | |
|---|---|
| **Fichier** | `server/middleware.py:200-202` |
| **Sévérité** | MEDIUM |
| **Statut** | ⬜ À optimiser |

**Correction recommandée :** Pré-calculer le set normalisé (frozenset) au module-level.

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
| **Statut** | ⬜ À monter top-level |

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

### Phase 1 — Standardisation des patterns (2-3 jours)

**Justification :** Avant de refactoriser les gros fichiers, il faut que les patterns soient cohérents. Sinon, chaque extraction de service reproduira les incohérences.

**Prérequis :** Phase 0 (sécurité middleware OK avant de toucher aux handlers).

| # | Action | Constat | Difficulté | Test |
|---|--------|---------|------------|------|
| 1.1 | Unifier parsing body → `parse_json_body` partout | CC1 | Moyen | Tests API existants |
| 1.2 | Unifier réponses erreur → `api_error_response` partout | CC2 | Moyen | Tests API existants |
| 1.3 | Remplacer 17 `traceback.print_exc()` par `logger.error(..., exc_info=True)` | CC3 | Facile | Pas de test nécessaire (comportement identique) |
| 1.4 | Extraire `get_cookie_config()` | CC5 | Facile | 1 test unitaire |
| 1.5 | Extraire `validate_password()` partagé | CC6 | Facile | 1 test unitaire |
| 1.6 | Ajouter type hints manquants sur handlers | CC4 | Facile | `mypy --strict` |
| 1.7 | Unifier les registres de routes middleware | A6 | Moyen | Tests middleware existants (23) |
| 1.8 | Unifier CORS origins → `settings.BACKEND_CORS_ORIGINS` unique | P1 | Facile | Test manuel |
| 1.9 | Pré-calculer CSRF exempt frozenset + `normalize_age_group` dict | P2, P3 | Facile | Tests existants |
| 1.10 | Monter `AdminService` en import top-level | I3 | Trivial | Aucun |

---

### Phase 2 — Refactoring services légers (2-3 jours)

**Justification :** Corrections de structure dans les services sans toucher aux 3 God objects. Chaque action est autonome, faible risque de régression.

**Prérequis :** Phase 1 (patterns standardisés pour que les services extraits soient cohérents).

| # | Action | Constat | Difficulté | Test |
|---|--------|---------|------------|------|
| 2.1 | Fusionner user lookups → source unique dans `user_service.py` | A5 | Facile | Tests auth + tests user |
| 2.2 | Aligner `auth_service.py` → pattern classe | A7 | Moyen | Tests auth existants |
| 2.3 | Extraire `_apply_challenge_filters()` dans `challenge_service.py` | A8 | Facile | Tests challenges existants |
| 2.4 | Décomposer `get_user_stats_for_dashboard` en 7 méthodes | A9 | Moyen | Tests dashboard existants |
| 2.5 | Supprimer `queries.py` (dead code confirmé) | I4 | Trivial | Supprimer le test associé |
| 2.6 | Supprimer `LoggingLevels`, `ExerciseStatus` de constants | I4 | Trivial | Aucun |
| 2.7 | Déplacer `VALID_THEMES`, `FRONTEND_URL` vers `constants.py`/`config.py` | CC8 | Facile | Tests existants |
| 2.8 | Remplacer `HTTPException` par exception métier dans `auth_service` | A7 | Moyen | Tests auth |
| 2.9 | Introduire les premiers `TypedDict` sur les retours les plus utilisés | I1 | Moyen | `mypy` |

---

### Phase 3 — Refactoring des God objects (5-7 jours)

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

### Phase 4 — Industrialisation (2-3 jours)

**Justification :** Dernière couche de polish — finit les TypedDict, découpe les constantes, nettoie les derniers anti-patterns. Faible risque, bénéfice de maintenabilité long terme.

**Prérequis :** Phase 3 (les services découpés ont besoin de DTOs finalisés).

| # | Action | Constat | Difficulté | Test |
|---|--------|---------|------------|------|
| 4.1 | Compléter les `TypedDict`/`dataclass` sur tous les retours services | I1 | Moyen | `mypy --strict` |
| 4.2 | Découper `constants.py` en modules par domaine | A10 | Facile | Imports vérifiés |
| 4.3 | Adopter `format_paginated_response` dans les handlers | H9 câblage (audit cleanup) | Facile | Tests API existants |
| 4.4 | Adopter `enum_mapping.py` dans les handlers | H9 câblage (audit cleanup) | Facile | Tests API existants |
| 4.5 | Repenser `safe_delete`/`safe_archive` → exceptions | I5 | Moyen | Tests transaction existants |

---

## 5. Matrice risque / bénéfice / difficulté {#5-matrice}

| Phase | Risque (si rien) | Bénéfice | Difficulté | Impact chaîné | Durée | ROI |
|-------|-----------------|----------|------------|---------------|-------|-----|
| **Phase 0** Sécurité | ⬛⬛⬛⬛⬛ 5/5 | ⬛⬛⬛⬛⬛ 5/5 | ⬛ 1/5 | Faible | 1 jour | **Immédiat** |
| **Phase 1** Standards | ⬛⬛⬛ 3/5 | ⬛⬛⬛⬛ 4/5 | ⬛⬛ 2/5 | **Élevé** (débloque P2+P3) | 2-3 jours | **Très élevé** |
| **Phase 2** Services légers | ⬛⬛ 2/5 | ⬛⬛⬛ 3/5 | ⬛⬛ 2/5 | Moyen (débloque P3) | 2-3 jours | Élevé |
| **Phase 3** God objects | ⬛⬛⬛ 3/5 | ⬛⬛⬛⬛⬛ 5/5 | ⬛⬛⬛⬛ 4/5 | Faible | 5-7 jours | Élevé (long terme) |
| **Phase 4** Industrialisation | ⬛ 1/5 | ⬛⬛⬛ 3/5 | ⬛⬛ 2/5 | Faible | 2-3 jours | Moyen |

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

---

## Références

- [AUDIT_CODE_CLEANUP_2026-03-01.md](./AUDIT_CODE_CLEANUP_2026-03-01.md) — Audit bugs, dead code, incohérences (corrigé)
- [AUDIT_BACKEND_INDUSTRIALISATION_2026-02.md](./AUDIT_BACKEND_INDUSTRIALISATION_2026-02.md) — Audit backend précédent (itérations 1–5)
- [REFACTOR_STATUS_2026-02.md](./REFACTOR_STATUS_2026-02.md) — État du refactoring
- [docs/01-GUIDES/TESTING.md](../01-GUIDES/TESTING.md) — Guide tests
