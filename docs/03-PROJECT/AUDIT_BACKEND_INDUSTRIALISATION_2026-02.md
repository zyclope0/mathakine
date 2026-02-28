# Audit Backend — Industrialisation & Plan d'intervention

**Date :** 28/02/2026  
**Type :** Audit technique (Architecte Logiciel Staff/Principal)  
**Périmètre :** Backend Mathakine (app/, server/)  
**Référence :** [CONVENTION_DOCUMENTATION.md](../CONVENTION_DOCUMENTATION.md)

---

## Sommaire

1. [Bilan de l'existant](#1-bilan-de-lexistant)
2. [Priorités](#2-priorités)
3. [Plan d'intervention par itération](#3-plan-dintervention-par-itération)
4. [Matrice Dev / Test / Prod](#4-matrice-dev--test--prod)
5. [Récapitulatif](#5-récapitulatif)
6. [Historique des modifications](#6-historique-des-modifications)

---

## 1. Bilan de l'existant

### 1.1 Dettes techniques identifiées

| Pilier | Problème | Gravité | Fichiers concernés |
|--------|----------|---------|-------------------|
| **Architecture** | Services statiques (non injectables) | Moyenne | `exercise_service`, `admin_service`, `challenge_service` |
| **Architecture** | Duplication mapping row→dict (3×) | Moyenne | `exercise_service.py` |
| **Architecture** | Incohérence exceptions métier | Faible | `exceptions.py` (ChallengeNotFoundError vs ExerciseNotFoundError) |
| **Architecture** | `queries.py` non utilisé (legacy) | Faible | `app/db/queries.py` |
| **Clean Code** | Imports hors top (E402) | Faible | `exercise_service`, `exercise_handlers` |
| **Clean Code** | ~~**Bug API** `create_validation_error`~~ | ~~Critique~~ ✅ Résolu It1 | `error_handler.py` — API étendue |
| **Clean Code** | Validators dupliqués (exercise_type, difficulty) | Moyenne | `app/schemas/exercise.py` |
| **Clean Code** | ~~`get_safe_error_message(default: str = None)`~~ | ~~Faible~~ ✅ Résolu It1 | `error_handler.py` |
| **Performance** | `ORDER BY RANDOM()` O(n) | Moyenne | `queries.py` (legacy) |
| **Performance** | Absence eager loading explicite | Moyenne | Services (badges, challenges) |
| **Robustesse** | `except Exception` trop large | Moyenne | `adapter`, `transaction`, `exercise_service` |
| **Industrialisation** | Services non mockables | Moyenne | Tous les services |

### 1.2 Anti-patterns

- **God handlers** : mélange parsing HTTP, auth, logique métier dans les handlers.
- **Return None silencieux** : `DatabaseAdapter`, `ExerciseService` retournent `None` au lieu de lever des exceptions métier.
- **Try/except générique** : masquage d'erreurs, rollback implicite mais log incomplet.

### 1.3 Points positifs

- `db_session()` context manager async (100 % des handlers).
- `parse_json_body_any` centralisé.
- `execute_query` sécurisé (params dict obligatoire).
- Exceptions métier partielles (ExerciseNotFoundError, ChallengeNotFoundError).
- DTO Pydantic (SubmitAnswerRequest, SubmitAnswerResponse).
- BadgeService : correction N+1 via stats_cache.

---

## 2. Priorités

### Matrice priorité / effort

| Priorité | Action | Effort | Impact |
|----------|--------|--------|--------|
| **P1** | Corriger bug `create_validation_error` | 1h | Critique (runtime) |
| **P1** | Surcharge API ErrorHandler | 2h | Critique |
| **P2** | Aligner exceptions métier | 1h | Robustesse |
| **P2** | Réorganiser imports (E402) | 2h | Lisibilité |
| **P2** | Corriger typage `get_safe_error_message` | 15 min | Qualité |
| **P3** | Factoriser validators Pydantic | 2h | DRY |
| **P3** | Repository / mapper exercices | 4h | Architecture |
| **P4** | Services injectables (protocols) | 8h | Testabilité |
| **P4** | Optimisation requêtes aléatoires | 2h | Performance |
| **P4** | Audit N+1, eager loading | 4h | Performance |

---

## 3. Plan d'intervention par itération

### Itération 1 — Correctifs critiques (1–2 jours)

**Objectif :** Éliminer les bugs runtime et incohérences API.

**Statut :** ✅ Complétée (28/02/2026)

| # | Tâche | Fichier(s) | Statut |
|---|-------|------------|--------|
| 1.1 | Étendre `ErrorHandler.create_validation_error` pour accepter `(errors, user_message)` | `app/utils/error_handler.py` | ✅ Fait — deux modes (field, message) et (errors, user_message) |
| 1.2 | Corriger les appels dans `challenge_handlers.py` | `server/handlers/challenge_handlers.py` | ✅ N/A — appels déjà corrects, API étendue les supporte |
| 1.3 | Corriger `get_safe_error_message(default: Optional[str] = None)` | `app/utils/error_handler.py` | ✅ Fait |
| 1.4 | Aligner `ChallengeNotFoundError` (optionnel : hériter d'une base commune) | `app/exceptions.py` | ⏸ Reporté (Itération 2 ou ultérieure) |

**Tests requis :**
- `pytest tests/unit/test_error_handler.py -v`
- `pytest tests/api/test_challenge_endpoints.py -v`
- `make test-backend-local`

**Validation prod :**
- Déploiement staging, test manuel GET /api/challenges avec paramètres invalides.
- Vérifier que la réponse 400 contient `field_errors` et `message`.

**Livrables It1 :**
- `ErrorHandler.create_validation_error` : surcharge `(errors, user_message)` implémentée
- Tests unitaires : `TestCreateValidationError` (4 tests) ajoutés
- `get_safe_error_message` : signature corrigée `default: Optional[str] = None`

---

### Itération 2 — Clean Code & robustesse (2–3 jours)

**Objectif :** Réduire la dette technique, améliorer la lisibilité.

| # | Tâche | Fichier(s) | Critères de validation |
|---|-------|------------|------------------------|
| 2.1 | Déplacer tous les imports en tête de module | `exercise_service.py`, `exercise_handlers.py`, etc. | `flake8 app server` sans E402 |
| 2.2 | Factoriser `validate_exercise_type`, `validate_difficulty` | `app/schemas/exercise.py` | Réutilisés dans ExerciseBase et ExerciseUpdate |
| 2.3 | Restreindre les `except Exception` aux cas strictement nécessaires | `DatabaseAdapter`, `ExerciseService` | Exceptions métier levées, pas de return None silencieux pour erreurs DB |
| 2.4 | Documenter ou archiver `queries.py` (ExerciseQueries non utilisé) | `app/db/queries.py`, `docs/` | Note dans code ou doc indiquant le statut legacy |

**Tests requis :**
- `pytest tests/ -x -q --tb=short`
- `python -m flake8 app server --count`
- `python -m black . --check && python -m isort . --check`

**Validation prod :**
- Smoke test endpoints principaux (exercices, challenges, admin).
- Pas de régression sur les tests E2E existants.

---

### Itération 3 — Architecture & DRY (3–4 jours)

**Objectif :** Extraire les responsabilités, réduire la duplication.

| # | Tâche | Fichier(s) | Critères de validation |
|---|-------|------------|------------------------|
| 3.1 | Créer `ExerciseRepository` ou mapper `_row_to_api_dict` | `app/repositories/` ou `app/services/exercise_service.py` | Une seule implémentation du mapping row→dict |
| 3.2 | Refactorer `get_exercise`, `get_exercise_for_api`, `get_exercise_for_submit_validation` | `exercise_service.py` | Délégation au mapper, pas de duplication |
| 3.3 | Introduire `ExerciseServiceProtocol` (typing.Protocol) | `app/services/` | Type hint pour injection future |
| 3.4 | (Optionnel) Factory ou DI minimale pour services | `server/app.py` ou `app/core/` | Services instanciés, pas de static |

**Tests requis :**
- Tests unitaires `test_exercise_service` mis à jour.
- Tests d'intégration `test_exercise_endpoints`.
- `pytest tests/ -v --tb=short`

**Validation prod :**
- Comparer les réponses API avant/après (format JSON identique).
- Vérifier les performances (temps de réponse GET /api/exercises).

---

### Itération 4 — Performance (2–3 jours)

**Objectif :** Optimiser les requêtes et réduire les N+1.

| # | Tâche | Fichier(s) | Critères de validation |
|---|-------|------------|------------------------|
| 4.1 | Remplacer `ORDER BY RANDOM()` par `random_offset` | Services utilisant requêtes aléatoires | Requête exécutée en &lt; 50 ms (benchmark) |
| 4.2 | Audit N+1 sur listes (exercices, challenges, badges) | `exercise_service`, `challenge_service`, `badge_service` | Pas de boucle avec query interne |
| 4.3 | Ajouter `joinedload` / `selectinload` où pertinent | Modèles avec relations | Réduction du nombre de requêtes (SQL log) |

**Tests requis :**
- Benchmark manuel ou script (temps réponse GET /api/exercises?limit=50).
- `pytest tests/` (non-régression).

**Validation prod :**
- Monitoring Sentry / logs : pas d'augmentation erreurs.
- Métriques temps réponse : stables ou en baisse.

---

### Itération 5 — Industrialisation (optionnel, 3–5 jours)

**Objectif :** Rendre le code test-ready, faciliter l'évolution.

| # | Tâche | Fichier(s) | Critères de validation |
|---|-------|------------|------------------------|
| 5.1 | Passer les services en instances injectables | Tous les services | Handler reçoit service en param ou via factory |
| 5.2 | Activer mypy strict sur modules critiques | `app/services/`, `server/handlers/` | `mypy app server` sans erreur |
| 5.3 | Documenter les contrats OpenAPI (schémas) | `docs/` ou annotations | Référence à jour pour les endpoints principaux |

**Tests requis :**
- Couverture maintenue ou augmentée.
- `mypy app server --strict` (si applicable).

**Validation prod :**
- Déploiement progressif (feature flag si besoin).
- Rollback plan documenté.

---

## 4. Matrice Dev / Test / Prod

### 4.1 Workflow par environnement

| Phase | Dev | Test (CI / staging) | Prod |
|-------|-----|---------------------|------|
| **Itération 1** | Correctifs locaux, tests unitaires | `pytest` + tests API, déploiement staging | Déploiement après validation staging |
| **Itération 2** | Refactor, flake8/black/isort | CI lint + tests, staging smoke | Déploiement après 24h sans incident staging |
| **Itération 3** | Refactor architecture | Tests non-régression, comparaison réponses API | Déploiement avec rollback plan |
| **Itération 4** | Optimisations, benchmarks | Métriques performance, pas de régression | Déploiement avec monitoring renforcé |
| **Itération 5** | Injection, mypy | Tests étendus, mypy CI | Déploiement progressif (canary si dispo) |

### 4.2 Critères de passage Dev → Test

| Critère | Commandes |
|---------|-----------|
| Tests unitaires | `pytest tests/unit/ -v` |
| Tests API | `pytest tests/api/ -v` |
| Lint | `flake8 app server && black --check . && isort --check .` |
| (Optionnel) Mypy | `mypy app server --ignore-missing-imports` |

### 4.3 Critères de passage Test → Prod

| Critère | Vérification |
|---------|---------------|
| CI verte | Tous les jobs passent |
| Staging OK | Smoke test manuel ou automatisé |
| Pas de régression | Comparaison réponses API (itérations 3–4) |
| Monitoring | Sentry / logs sans pic d'erreurs |

### 4.4 Rollback par itération

| Itération | Rollback |
|-----------|----------|
| 1 | Revert commit, redéploiement version précédente |
| 2 | Idem, impact limité (lint/docs) |
| 3 | Revert commit ; impact moyen (architecture) |
| 4 | Revert commit ; surveiller perfs avant/après |
| 5 | Revert commit ou désactivation feature flag |

---

## 5. Récapitulatif

| Itération | Durée | Livrables | Risque |
|-----------|-------|------------|--------|
| 1 | 1–2 jours | Bug fix, API cohérente | Faible |
| 2 | 2–3 jours | Clean code, imports, validators | Faible |
| 3 | 3–4 jours | Repository, mapper, DRY | Moyen |
| 4 | 2–3 jours | Optimisations requêtes | Moyen |
| 5 | 3–5 jours | Injection, mypy | Moyen |

**Recommandation :** Exécuter les itérations 1 et 2 en priorité. Les itérations 3–5 peuvent être planifiées selon la roadmap et la charge équipe.

---

## 6. Historique des modifications

| Date | Itération | Détail |
|------|-----------|--------|
| 28/02/2026 | 1 | Création du document, plan d'intervention |
| 28/02/2026 | 1 | ✅ create_validation_error : surcharge (errors, user_message) |
| 28/02/2026 | 1 | ✅ get_safe_error_message : typage Optional[str] |
| 28/02/2026 | 1 | Tests unitaires TestCreateValidationError (4 tests) |

---

## Références

- [REFACTOR_STATUS_2026-02.md](./REFACTOR_STATUS_2026-02.md) — État du refactoring en cours
- [PLAN_REFACTO_ARCHITECTURE_2026-02.md](./PLAN_REFACTO_ARCHITECTURE_2026-02.md) — Plan architecture
- [docs/01-GUIDES/TESTING.md](../01-GUIDES/TESTING.md) — Guide tests
- [docs/01-GUIDES/DEPLOYMENT_ENV.md](../01-GUIDES/DEPLOYMENT_ENV.md) — Environnements déploiement
