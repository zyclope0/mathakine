# Lot I6 - Handler Error Pipeline and Response Normalization

> Iteration `I`
> Status: **done** (2026-03-19)

## Mission

Reduce duplicated try/except/log/traceback glue in the main HTTP handler modules while preserving thin HTTP behavior.

## Why This Lot Exists

Several handler modules are large mainly because they repeat:
- request parsing glue
- `run_db_bound(...)`
- exception mapping
- log + traceback capture

This is mostly HTTP-layer noise, not business logic, but it still raises maintenance cost.

## Primary Scope (lot réalisé)

- **`server/handlers/challenge_handlers.py`** — cluster unique I6
- **`app/utils/error_handler.py`** — micro-extension **strictement causale** : paramètre `handler_log_context` sur `ErrorHandler.create_error_response`

## In Scope (réalisé)

- Normaliser le pipeline **log + réponse JSON 500** pour les `except Exception` du module challenge
- Réduire le boilerplate sans déplacer le métier hors des services
- Comportement observable HTTP inchangé (même schéma d’erreur, mêmes codes)

## Out of Scope

- Refonte globale des handlers (`auth_handlers`, `exercise_handlers`, `user_handlers` hors régression)
- Middleware, sécurité, frontend
- Helper « universel » opaque : le mécanisme est **nommé et documenté** sur `ErrorHandler`

## Success Criteria (preuve)

- Moins de lignes répétées `logger.error` + `logger.debug(traceback)` + `ErrorHandler.create_error_response` / `api_error_response`+`get_safe_error_message`
- Handlers toujours transport-oriented
- Pas de changement de payload public

---

## Compte-rendu I6 (2026-03-19)

### 1. Fichiers modifiés

| Fichier | Rôle |
|---------|------|
| `app/utils/error_handler.py` | `handler_log_context` sur `ErrorHandler.create_error_response` |
| `server/handlers/challenge_handlers.py` | Normalisation des branches `except Exception` internes |
| `tests/unit/test_error_handler.py` | Test de non-régression D1 + tag Sentry `handler_context` |
| `docs/03-PROJECT/PILOTAGE_..._I6_....md` | Ce document |

### 2. Fichiers runtime modifiés

- `app/utils/error_handler.py`
- `server/handlers/challenge_handlers.py`

### 3. Fichiers de test modifiés

- `tests/unit/test_error_handler.py`

### 4. Cluster choisi

**Handlers défis logiques** — `server/handlers/challenge_handlers.py` uniquement (liste, détail, soumission tentative, indice, IDs complétés).

### 5. Duplication initiale constatée

Sur chaque `except Exception` « catch-all » :

1. `logger.error(f"... {exc}")` ou équivalent
2. `logger.debug(traceback.format_exc())` **ou** `logger.error(..., exc_info=True)`
3. Puis soit `ErrorHandler.create_error_response(...)`, soit `api_error_response(500, get_safe_error_message(...))`

**Problème** : `ErrorHandler.create_error_response` journalisait **déjà** l’exception + traceback + Sentry — les handlers **doublaient** logs et rendaient le flux difficile à lire. Les branches `submit` / `hint` mélangeaient `get_safe_error_message` (Sentry) avec des logs séparés = patterns hétérogènes pour le même besoin « 500 interne ».

### 6. Pipeline normalisé retenu

- Un paramètre optionnel **`handler_log_context: str`** sur `ErrorHandler.create_error_response` :
  - **Un seul** log : `logger.error("%s | %s: %s", context, type, message, exc_info=True)`
  - Pas de `logger.debug(traceback)` redondant dans le handler
  - `capture_exception_for_sentry` inchangé + tag `handler_context` (tronqué) pour traçabilité
- Les handlers challenge passent le **libellé métier HTTP** (récupération liste, soumission, etc.) comme contexte lisible.

### 7. Structure retenue

```
challenge_handlers (except Exception)
    -> ErrorHandler.create_error_response(..., handler_log_context="...")
```

Pas de nouveau module « magique » séparé : l’API reste **ErrorHandler**, avec un seam explicite documenté.

### 8. Ce qui a été prouvé

- **`challenge_handlers.py`** : **24 suppressions / 17 ajouts** (diff git) — gain surtout **sémantique** : fin des **logs + traceback dupliqués** avant `create_error_response`, et **unification** des branches `submit` / `hint` (plus de `api_error_response`+`get_safe_error_message` parallèle à un autre chemin Sentry)
- Fichier **~301 lignes** (post-lot) ; le critère « vrai gain » est la **disparition du pattern répétitif** plus que le compte brut de lignes
- Batterie cible **2× verte** (voir §10–11)
- Full gate **vert** (voir §12)
- Test unitaire : chemin `handler_log_context` respecte D1 (pas de fuite du message d’exception dans le JSON)

### 9. Ce qui n’a pas été prouvé / hors scope I6

- **`generate_ai_challenge_stream`** : erreurs SSE via `sse_error_response` — pattern différent, non unifié dans ce lot
- **`auth_handlers` / `exercise_handlers` / `user_handlers`** : même anti-pattern possible ; **non traité** ici (blast radius volontairement limité)

### Review Reserve Tracking

- Duplication **similaire** (traceback + `ErrorHandler.create_error_response`) subsiste dans **`exercise_handlers.py`** et ailleurs — candidats pour un **lot ultérieur** **même pattern** (`handler_log_context` déjà disponible).
- **`auth_handlers`** : volume élevé de `traceback.format_exc()` — à traiter avec la **même** discipline si on étend, sans helper opaque.

### 10. Résultat run 1

Commande :

`pytest -q tests/api/test_auth_flow.py tests/api/test_user_endpoints.py tests/api/test_challenge_endpoints.py tests/api/test_challenges_flow.py tests/unit/test_error_handler.py --maxfail=20 --no-cov`

→ **`82 passed, 1 skipped`**

### 11. Résultat run 2

Même commande → **`82 passed, 1 skipped`**

### 12. Résultat full gate

`pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py --no-cov`

→ **`956 passed, 3 skipped`** (+1 test unitaire `test_error_handler` vs baseline 955)

### 13. black

- **`black app/ server/ tests/ --check`** : **OK** — **287 fichiers** inchangés (fermeture **micro-lot I6b** : gate formatage strict, voir ci-dessous)
- Fichiers I6 : **OK** (`error_handler.py`, `challenge_handlers.py`, `test_error_handler.py`)

### Micro-lot I6b — fermeture stricte du gate `black` (2026-03-19)

- **Objectif** : lever la réserve « `black --check` rouge sur 3 fichiers tests » sans toucher au runtime.
- **Constat** : sur arbre **aligné sur `HEAD`**, les fichiers `tests/unit/test_answer_validation.py`, `test_answer_validation_formats.py`, `test_exercise_service.py` sont **déjà conformes** à Black ; `black <fichiers>` ne produit **aucun** diff.
- **Attention** : un `black` sur un worktree **local** mélangeant retours à la ligne / edits non commités peut afficher un diff incluant d’autres changements — pour un diff **uniquement** formatage, isoler avec `git checkout --` sur ces fichiers puis `black` uniquement.
- **Vérifications I6b** : batterie I6 cible **2×** `82 passed, 1 skipped` ; `black app/ server/ tests/ --check` **vert** ; `isort app/ server/ tests/ --check-only` **vert**.

### 14. isort

**OK** (`app/ server/ tests/ --check-only`)

### 15. mypy

**OK** — `Success: no issues found in 194 source files` (`app/ server/`)

### 16. flake8 (E9, F63, F7, F82)

**OK** sur les fichiers runtime touchés

### 17. Risques résiduels

- Extension future de `handler_log_context` : garder des **chaînes courtes** (troncature 200 chars côté Sentry tag)
- Handlers non migrés : incohérence **temporaire** log/response jusqu’à prochain lot

### 18. GO / NO-GO

**GO** — vraie baisse de duplication et de double journalisation sur le cluster **challenge_handlers** ; pipeline explicite ; contrats HTTP inchangés ; preuves tests vertes.
