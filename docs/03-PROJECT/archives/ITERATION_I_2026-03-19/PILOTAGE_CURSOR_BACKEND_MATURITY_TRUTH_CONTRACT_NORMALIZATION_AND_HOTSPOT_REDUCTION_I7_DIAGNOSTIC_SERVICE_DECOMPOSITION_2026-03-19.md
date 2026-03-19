# Lot I7 - Diagnostic Service Decomposition

> Iteration `I`
> Status: **done** (2026-03-19)

## Mission

Reduce density in `diagnostic_service.py` by extracting one real responsibility cluster.

## Cluster choisi

**Stockage serveur « pending »** (référence opaque, Redis ou mémoire TTL) : tout le bloc qui gérait `_pending_state_memory`, client Redis lazy, cleanup TTL, `store_pending_state` / `load_pending_state` / `delete_pending_state` / `get_pending_state`.

Ce cluster est **orthogonal** à l’IRT (niveaux, rotation, scoring) et aux tokens JWT — frontière nette **infrastructure / persistance courte** vs **logique métier diagnostic**.

## Densité initiale constatée

- `diagnostic_service.py` : **~591 lignes** avant extraction
- Après extraction : **`diagnostic_service.py` ~487 lignes** ; **`diagnostic_pending_storage.py` ~126 lignes**

## Responsabilités séparées après décomposition

| Module | Rôle |
|--------|------|
| `diagnostic_pending_storage.py` | TTL, Redis vs mémoire, opaque refs, load/store/delete, résolution `pending_ref` |
| `diagnostic_service.py` | Session IRT, tokens signés, `check_answer` / `apply_answer_and_advance` (orchestration), génération question, persistance `DiagnosticResult`, scores, `get_latest_score` |

Les symboles `store_pending_state`, `load_pending_state`, `delete_pending_state`, `get_pending_state` restent **importés et exposés** depuis `diagnostic_service` pour compatibilité (`diagnostic_handlers` utilise `diagnostic_svc.*`).

## Structure retenue

```
app/services/diagnostic/diagnostic_pending_storage.py
    ^ importée par
app/services/diagnostic/diagnostic_service.py
```

## Ce qui a été prouvé

- Batterie I7 (runs 1 et 2) : **34 passed** (commande ci-dessous)
- Full gate : **962 passed, 3 skipped** (dont **6** tests `test_diagnostic_service` nouveaux)
- `black`, `isort`, `mypy`, `flake8` (E9,F63,F7,F82 sur package diagnostic) : **OK**

## Ce qui n’a pas été prouvé / hors scope

- IRT (`_apply_answer`, `_next_type`, …), génération de questions, `_compute_final_scores` / `save_result` : **non extraits** dans ce lot
- Handlers : **inchangés** (réexport via `diagnostic_service`)

## Review Reserve Tracking

- **`diagnostic_service.py` reste dense** (~487 lignes) : candidats futurs — **moteur IRT + rotation**, ou **bloc persistance résultat + refresh recommandations**
- Correction **minimale** dans `tests/unit/test_exercise_service.py` : patch `update_user_streak` sur **`exercise_attempt_service`** (import direct) — alignement mock **I6** ; nécessaire pour un full gate vert avec import streak en tête de module

## Mandatory validation (résultats)

### Run 1 — batterie I7 cible

`pytest -q tests/api/test_diagnostic_endpoints.py tests/unit/test_diagnostic_service.py tests/unit/test_error_handler.py --maxfail=20 --no-cov`

→ **34 passed**

### Run 2

Même commande → **34 passed**

### Full gate

`pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py --no-cov`

→ **962 passed, 3 skipped**

### Outils

- `black app/ server/ tests/ --check` → **OK**
- `isort app/ server/ tests/ --check-only --diff` → **OK**
- `mypy app/ server/ --ignore-missing-imports` → **OK** (195 fichiers)
- `flake8 app/services/diagnostic/ --select=E9,F63,F7,F82` → **OK**

## Fichiers modifiés (runtime + tests + doc)

- `app/services/diagnostic/diagnostic_pending_storage.py` — **nouveau**
- `app/services/diagnostic/diagnostic_service.py`
- `tests/unit/test_diagnostic_service.py` — **nouveau**
- `tests/unit/test_exercise_service.py` — patch mock streak (causal gate, voir réserve)
- Ce document

## GO / NO-GO

**GO** — baisse de densité réelle sur le cluster pending ; responsabilité dédiée ; tests locaux + API diagnostic + gate verts.
