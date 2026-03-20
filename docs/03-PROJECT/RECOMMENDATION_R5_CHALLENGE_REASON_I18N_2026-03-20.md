# R5 — Recommandations défis + raisons i18n (2026-03-20)

## Objectif

- Branche **défis logiques** : scoring explicite (historique tentatives 90j, taux de réussite, diversité 30j, `difficulty_rating`, objectif `samuser`), sans tirage `ORDER BY random()` dominant.
- **Raisons** : `reason_code` + `reason_params` persistés ; `reason` = fallback court (EN) pour compat API / clients anciens.
- **Frontend** : affichage prioritaire via `next-intl` si `reason_code` présent.

## Stratégie challenge (profils)

Ordre de classification :

1. **struggling** — ≥3 tentatives sur 90j et taux de réussite &lt; 0,45 → `reco.challenge.gentle_progress` ; score favorise `difficulty_rating` bas et types « onboarding » (sequence / puzzle / pattern).
2. **novice** — 0 défi complété et &lt;5 tentatives 90j → `reco.challenge.onboarding` ; bonus types onboarding.
3. **mature** — ≥3 défis complétés **ou** (≥10 tentatives 90j et taux ≥ 0,5) → `reco.challenge.variety` ; bonus type absent des 30j, malus type dominant récent.
4. **developing** — défaut → `reco.challenge.skill_stretch`.

Filtres pool : `is_archived == false`, `is_active == true`, âge (comme avant), exclusion des défis déjà **réussis**.

## Limite `difficulty_rating`

Valeur souvent absente ou peu fiable : défaut **3.0** sur l’échelle 1–5. Le score l’utilise comme signal **secondaire** (pas un classement « scientifique »).

## API

- Champs optionnels : `reason_code`, `reason_params` (objet JSON).
- `reason` toujours renseigné pour les nouvelles recos défi (fallback).
- Recos exercice : **R6** (2026-03-21) — `reason_code` / `reason_params` sur les branches couvertes (improvement, progression, maintenance, discovery, fallback) + **next-intl** côté dashboard ; avant R6, texte FR / `reason` seul. Voir [R6](./RECOMMENDATION_R6_EXERCISE_DISCOVERY_AND_REASONS_2026-03-21.md) et clôture [R7](./RECOMMENDATION_R7_CLOSURE_ITERATION_R_2026-03-21.md).
- **R5b** — `GET` liste : même filtre que la génération pour le contenu défi affiché : exclut défi absent, archivé ou **`is_active == false`** (reco déjà en base si le défi est désactivé ensuite).
- **R5c** — Hygiène ORM : `delete(..., synchronize_session=False)` sur le bulk delete des recos incomplètes avant régénération (évite `ObjectDeletedError` si plusieurs `generate` dans la même session de test) ; `set_committed_value(user, "recommendations", [])` pour réaligner la collection en mémoire après le bulk (évite état incohérent / FK intermittentes ; `expire` sur la relation a été écarté).
- **R5d** — Stabilité tests (infra) : le nettoyage auto utilisait encore `get_test_engine()` (2ᵉ pool) en secours alors que `db_session` et l’app utilisent `app.db.base.engine` — source documentée d’incohérences FK / visibilité. Correction : secours sur `_get_session_engine()` ; cleanup en **deux commits** (enfants puis `users`) pour qu’un échec tardif sur `DELETE users` n’annule pas les suppressions déjà faites ; catch-all `user_id` + tables F02/F03 (`daily_challenges`, `diagnostic_results`, …) ; journalisation des comptes restants avant rollback ; `pytest.fail` si le cleanup échoue (plus de continuation silencieuse).

## Migration

- Alembic `20260320_rec_reason_i18n` : colonnes `reason_code`, `reason_params` sur `recommendations`.
- **Tests** : fixture session `conftest` exécute un `ALTER` idempotent si les colonnes manquent (base locale sans migration).

## Fichiers touchés (référence)

- `app/services/recommendation/recommendation_service.py`
- `app/models/recommendation.py`
- `migrations/versions/20260320_add_recommendation_reason_i18n.py`
- `app/schemas/recommendation.py`
- `frontend/hooks/useRecommendations.ts`, `Recommendations.tsx`, `messages/fr.json`, `messages/en.json`
- Tests : `tests/unit/test_recommendation_service.py`, `tests/api/test_recommendation_endpoints.py`, `frontend/__tests__/unit/hooks/useRecommendationsReason.test.ts`
