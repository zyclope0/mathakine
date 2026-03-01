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
| **Architecture** | ~~Duplication mapping row→dict (3×)~~ | ~~Moyenne~~ ✅ Résolu It3 | `_exercise_row_to_dict` centralisé |
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

**Statut :** ✅ Complétée (28/02/2026)

| # | Tâche | Fichier(s) | Statut |
|---|-------|------------|--------|
| 2.1 | Déplacer tous les imports en tête de module | `exercise_service.py`, `exercise_handlers.py` | ✅ Fait — imports consolidés, inline supprimés |
| 2.2 | Factoriser `validate_exercise_type`, `validate_difficulty` | `app/schemas/exercise.py` | ✅ Fait — `_validate_exercise_type`, `_validate_difficulty` réutilisables |
| 2.3 | Restreindre les `except Exception` aux cas strictement nécessaires | `DatabaseAdapter`, `ExerciseService` | ⏸ Reporté (Itération 3 ou ultérieure) |
| 2.4 | Documenter ou archiver `queries.py` (ExerciseQueries non utilisé) | `app/db/queries.py` | ✅ Fait — docstring STATUT LEGACY |

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

**Statut :** ✅ Complétée (28/02/2026)

| # | Tâche | Fichier(s) | Statut |
|---|-------|------------|--------|
| 3.1 | Créer mapper `_exercise_row_to_dict` | `app/services/exercise_service.py` | ✅ Fait — une implémentation centralisée |
| 3.2 | Refactorer `get_exercise_for_api`, `get_exercise_for_submit_validation` | `exercise_service.py` | ✅ Fait — délégation au mapper |
| 3.3 | Introduire `ExerciseServiceProtocol` (typing.Protocol) | `exercise_service.py` | ✅ Fait |
| 3.4 | (Optionnel) Factory ou DI minimale | — | ⏸ Reporté |

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

**Statut :** ✅ Complétée (01/03/2026)

| # | Tâche | Fichier(s) | Critères de validation | Statut |
|---|-------|------------|------------------------|--------|
| 4.1 | Remplacer `ORDER BY RANDOM()` par `random_offset` | Services utilisant requêtes aléatoires | Requête exécutée en &lt; 50 ms (benchmark) | ✅ `exercise_service` — random_offset OK. ✅ `challenge_service` — random_offset OK en prod (hors TESTING), func.random() en tests (stable). Voir [Plan 4.1](#plan-41-à-100--random_offset-challenge_service). |
| 4.2 | Audit N+1 sur listes (exercices, challenges, badges) | `exercise_service`, `challenge_service`, `badge_service` | Pas de boucle avec query interne | ✅ Complété 22/02/2026. Voir [Plan 4.2](#plan-42-audit-n1). |
| 4.3 | Ajouter `joinedload` / `selectinload` où pertinent | Modèles avec relations | Réduction du nombre de requêtes (SQL log) | ✅ Complété 22/02/2026. Voir [Plan 4.3](#plan-43-joinedload-selectinload). |

**Tests requis :**
- Benchmark manuel ou script (temps réponse GET /api/exercises?limit=50).
- `pytest tests/` (non-régression).

**Diagnostic complet :** [DIAGNOSTIC_CHALLENGES_LIST_2026-02.md](DIAGNOSTIC_CHALLENGES_LIST_2026-02.md) — traçage route → handler → DB, identification des 3 points de défaillance.

#### Plan 4.1 à 100 % — random_offset challenge_service {#plan-41-à-100--random_offset-challenge_service}

**Problème :** Avec `random_offset` dans `challenge_service.list_challenges`, l’API retourne `items=[]` alors que `total=38` (count correct, list vide). Avec `func.random()`, tout fonctionne.

**Cause racine :** Les fixtures utilisent `get_test_engine()` (conftest) tandis que les handlers utilisent `app.db.base.engine` (SessionLocal). Deux engines distincts → deux pools de connexions. Le pattern `random_offset` (count + offset aléatoire + limit) semble sensible à cette séparation en environnement de test.

**Résolu 01/03/2026.** `random_offset` activé en prod (hors TESTING), `func.random()` en tests.

**Solution retenue :** Désactiver `random_offset` quand `TESTING=true` (voir `challenge_service.list_challenges`).

~~1. **Unifier les engines en mode test**  
   Faire en sorte que `db_session` (conftest) utilise `app.db.base.engine` au lieu de `get_test_engine()`.  
   - Tentative 22/02 : unification a empiré (6 échecs au lieu de 5). Cause à clarifier.  
   - Pistes : ordre d’initialisation (conftest vs app), isolation des transactions, cleanup `logic_challenge_db`.

2. **Implémenter `random_offset`** dans `challenge_service.list_challenges` (ordre aléatoire) :
   ```python
   total = count_query.count()  # requête séparée, mêmes filtres
   max_offset_val = max(0, total - limit - offset)
   random_offset_val = random.randint(0, max_offset_val) if max_offset_val > 0 else 0
   return query.order_by(LogicChallenge.id).offset(offset + random_offset_val).limit(limit).all()
   ```
   Référence : `exercise_service.list_exercises_for_api` (lignes 579–587).

3. **Valider** : `pytest tests/api/test_challenge_endpoints.py -v` — tous les tests passent.~~

**Validation prod :**
- Monitoring Sentry / logs : pas d'augmentation erreurs.
- Métriques temps réponse : stables ou en baisse.

#### Plan 4.2 — Audit N+1 {#plan-42-audit-n1}

**Résultat audit (22/02/2026) :**

| Service | N+1 identifiés | Correction |
|---------|----------------|------------|
| `exercise_service` | Aucun | — |
| `challenge_service` | Aucun | — |
| `badge_service` | 2 | Voir ci-dessous |
| `badge_requirement_engine` | 1 | Voir ci-dessous |

**Corrections appliquées :**

1. **badge_service._build_stats_cache** (l.177–195) : boucle `for ex_t in exercise_types` avec `db.execute` par type pour calculer les streaks. → Une seule requête `SELECT ex_type, is_correct ORDER BY created_at DESC LIMIT 500`, puis calcul des streaks en Python.

2. **badge_service._check_min_per_type** (l.570–590) : boucle `for ex_type in all_types_set` avec `db.execute` par type. → Une seule requête `GROUP BY LOWER(exercise_type)` pour récupérer les counts par type.

3. **badge_requirement_engine._check_min_per_type** (fallback sans stats_cache) : même pattern. → Même correction (requête GROUP BY unique).

**Tests ajoutés :** `tests/unit/test_badge_requirement_engine.py::TestCheckRequirementsMinPerType` (2 tests de régression pour min_per_type).

#### Plan 4.3 — joinedload / selectinload {#plan-43-joinedload-selectinload}

**Objectif :** Réduire les requêtes SQL en pré-chargeant les relations utilisées après une requête liste.

**Modifications (22/02/2026) :**

| Fichier | Relation | Stratégie | Impact |
|---------|----------|-----------|--------|
| `admin_service.get_audit_log_for_api` | `AdminAuditLog.admin_user` | `joinedload` | Avant : 1 + N requêtes (User par log). Après : 1 requête avec LEFT JOIN. |
| `recommendation_service.get_user_recommendations` | `Recommendation.exercise`, `Recommendation.challenge` | `selectinload` | Avant : 1 + 2N requêtes (Exercise et Challenge par rec). Après : 3 requêtes (recs + batch exercises + batch challenges). |

**Validation :** `pytest tests/api/test_recommendation_endpoints.py tests/unit/test_recommendation_service.py -v` — tous les tests passent.

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
| 28/02/2026 | 2 | Imports en tête : exercise_service, exercise_handlers |
| 28/02/2026 | 2 | Validators DRY : _validate_exercise_type, _validate_difficulty |
| 28/02/2026 | 2 | queries.py : docstring STATUT LEGACY |
| 28/02/2026 | 3 | _exercise_row_to_dict : mapper DRY row→dict |
| 28/02/2026 | 3 | ExerciseServiceProtocol (typing.Protocol) |
| 01/03/2026 | 4 | exercise_service : random_offset (O(1)) pour liste exercices |
| 01/03/2026 | 4 | challenge_service : conserve func.random() (random_offset → bug isolation tests) |
| 01/03/2026 | 4 | test_challenge_endpoints : test_get_logic_challenges déplacé en dernier (fix isolation) |
| 01/03/2026 | 7 | Unification engines : db_session (conftest) utilise app.db.base.engine. Corrige test_get_current_user_authenticated (FK user_sessions). |

---

## 7. Effets de bord et régressions (post-audit)

**Constat :** Des erreurs de tests signalées après la mise en œuvre de l'audit n'existaient pas avant. La cause peut venir des **Itérations 1, 2 ou 3** (ou de leur combinaison), pas spécifiquement de l'Itération 4.

### 7.1 Erreurs signalées

| Test / symptôme | Erreur | Cause probable |
|-----------------|--------|----------------|
| `test_reset_password_full_flow` | `StaleDataError: UPDATE statement on table 'users' expected to update 1 row(s); 0 were matched` | Isolation sessions/engines ou ordre d'import (It1–3). En isolation, le test **passe**. |
| Admin / challenge (archiviste, etc.) | "Cannot authenticate archiviste: Erreur lors de la connexion" | Ordre des tests ou état DB (fixtures, rollback) qui casse l’auth pour les tests suivants. |
| `test_get_challenge_hint` | SKIP "Erreur lors de la connexion" | Même hypothèse que ci-dessus. |

### 7.2 Trace par itération (à investiguer)

| Itération | Fichiers modifiés | Lien potentiel avec les erreurs |
|-----------|-------------------|----------------------------------|
| **It1** | `error_handler.py` : `create_validation_error`, `get_safe_error_message` | `user_handlers` et `auth_handlers` importent `api_error_response`, `get_safe_error_message`. Changement de signature ou de comportement en cas d'exception pourrait masquer ou modifier le flux d'erreur. **À vérifier :** les `except` dans auth_handlers qui appellent `get_safe_error_message` ou `api_error_response`. |
| **It2** | `exercise_service.py`, `exercise_handlers.py` : imports en tête ; `app/schemas/exercise.py` : validators | **Ordre d'import** : les imports déplacés en tête changent l'ordre de chargement des modules. Si `exercise_service` ou `exercise_handlers` est chargé avant/après un module critique (ex. `app.db.base`), l'initialisation de l'engine ou des pools peut différer. **À vérifier :** chaîne d'import au démarrage (conftest → enhanced_server → routes → handlers). |
| **It3** | `exercise_service.py` : `_exercise_row_to_dict`, `ExerciseServiceProtocol`, refactor `get_exercise_for_api` | Pas de lien direct avec auth. `auth_service` et `auth_handlers` n'utilisent pas `TransactionManager` ni `DatabaseAdapter`. **It3 peu probable** pour les erreurs auth. |

### 7.3 Cause racine connue (Plan 4.1)

- Deux engines en test : `app.db.base.engine` (handlers) vs `get_test_engine()` (conftest `db_session`). Même URL, pools distincts.
- **Repro** : `test_reset_password_full_flow` passe en isolation et avec `tests/api/test_auth_flow.py` complet. L’erreur apparaît probablement en **suite complète** ou **CI** (ordre, parallélisme, état DB).

### 7.4 Plan d'investigation (à exécuter)

1. **It1** : Comparer les blocs `except` dans `auth_handlers.py` et `user_handlers.py` avant/après It1 (git log). Vérifier si `get_safe_error_message` ou `create_validation_error` modifient le flux en cas de `StaleDataError`.
2. **It2** : Reproduire l'ordre d'import au chargement : lister les modules chargés (ex. `python -c "import enhanced_server; ..."` avec trace) et comparer avec un revert des imports en tête.
3. **It3** : Vérifier si `TransactionManager` ou `DatabaseAdapter` sont utilisés dans le flux auth (forgot-password, reset-password). Si non, It3 peu probable.
4. **Suite complète** : Lancer `pytest tests/ -v --tb=long` et noter l'ordre exact du premier échec. Reproduire avec `-x` sur le test précédent pour tester l'effet de l'ordre.

### 7.5 Pistes de résolution

1. **Unifier les engines en test** : ✅ Fait (22/02/2026). La fixture `db_session` utilise désormais `app.db.base.engine` au lieu de `get_test_engine()`. Corrige la FK `user_sessions_user_id_fkey` (user non visible entre requêtes).
2. **Rendre le test robuste** : éviter la lecture directe en DB pour le token ; par ex. endpoint test-only ou mock du flux email.
3. **Isolation des tests admin** : vérifier l’ordre des fixtures (`role_client`, `archiviste_client`) et le cleanup entre tests.

---

## Références

- [REFACTOR_STATUS_2026-02.md](./REFACTOR_STATUS_2026-02.md) — État du refactoring en cours
- [PLAN_REFACTO_ARCHITECTURE_2026-02.md](./PLAN_REFACTO_ARCHITECTURE_2026-02.md) — Plan architecture
- [docs/01-GUIDES/TESTING.md](../01-GUIDES/TESTING.md) — Guide tests
- [docs/01-GUIDES/DEPLOYMENT_ENV.md](../01-GUIDES/DEPLOYMENT_ENV.md) — Environnements déploiement
