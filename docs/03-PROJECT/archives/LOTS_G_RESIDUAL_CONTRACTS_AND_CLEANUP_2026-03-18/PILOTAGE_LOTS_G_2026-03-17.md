# Pilotage Cursor - Lots G (Residual Contracts and Cleanup)

> Créé: 17/03/2026 — **Clôturé: 18/03/2026** (archive)
> Principe: même discipline que F — sous-scope unique, preuve, blast radius limité

## Contexte

Itération F fermée. Ces lots prolongent la discipline F sans réouvrir F.
Référence: [POINTS_RESTANTS_2026-03-15.md](../../POINTS_RESTANTS_2026-03-15.md) § Next Technical Candidates.

## Baseline de départ

- full suite: `936 passed, 2 skipped` (excl. test_admin_auth_stability)
- black, isort, mypy, flake8: green
- measured local coverage: `67.30 %`
- coverage gate CI: `63 %`

## Règles invariantes (comme F)

- Un seul sous-scope par lot
- Batterie cible → run 2 → full suite si blast radius > sous-scope
- black, isort, mypy, flake8 verts
- Pas de changement de contrat HTTP public
- Pas de refactor global
- Protocole: [CURSOR_MAX_EFFORT_BACKEND_PROTOCOL_2026-03-11.md](../../CURSOR_MAX_EFFORT_BACKEND_PROTOCOL_2026-03-11.md)

---

## Lot G1 — Contrat `authenticate_user_with_session`

### Status: done (2026-03-17)

### Mission

Remplacer le retour `Tuple[Optional[User], Optional[TokenResponse]]` par un type explicite, sur le modèle F1.

### Fichiers concernés

| Fichier | Rôle |
|---------|------|
| `app/schemas/auth_result.py` | Ajouter `AuthenticateWithSessionResult` |
| `app/services/auth_service.py` | Modifier signature et retour de `authenticate_user_with_session` |
| `app/services/auth_session_service.py` | Adapter l'appel (déballer le result) |

### G1 Réalisation (2026-03-17)

- `AuthenticateWithSessionResult` ajouté dans `app/schemas/auth_result.py`
- `authenticate_user_with_session` retourne désormais `AuthenticateWithSessionResult`
- `perform_login` utilise `result.is_success`, `result.user`, `result.token_data`
- Test `test_authenticate_user_with_session_single_commit` adapté
- Run 1, run 2: 56 passed
- black, isort, mypy, flake8: green

---

## Lot G2 — Extraction cluster `success_rate` du badge engine

### Status: done (2026-03-06, fix code mort 2026-03-18)

### Mission

Extraire `_check_success_rate` (et progress si existant) vers `badge_requirement_volume.py`, sur le modèle F2.

### G2 Réalisation (2026-03-06)

- `_resolve_success_rate_stats`, `check_success_rate`, `progress_success_rate` dans `badge_requirement_volume.py`
- Engine : import depuis volume
- Tests : `test_success_rate_*`, `test_progress_success_rate_*` dans `test_badge_requirement_volume.py`
- Run 1, run 2 : 40 passed

### G2 Fix clôture (2026-03-18)

- Suppression du code mort `_progress_success_rate` resté dans `badge_requirement_engine.py`

---

## Lot G3 — Flux `create_exercise` admin

### Status: done (2026-03-18)

### G3 Réalisation (2026-03-18)

- `ExerciseCreatePrepared` ajouté dans `app/core/types.py`
- `admin_exercise_create_flow.py` : `prepare_exercise_create_data`, `validate_exercise_create_pre_persist`, `persist_exercise_create`
- `admin_content_service.create_exercise_for_admin` réduit à orchestration
- Tests : `test_admin_exercise_create_flow.py` (prepare, validate, persist)
- Run : 35 passed ; black, isort, flake8 : green

---

## Lot G4 — Normalisation imports `db_boundary`

### Status: done (2026-03-18)

### G4 Réalisation (2026-03-18)

- 19 fichiers runtime : import `sync_db_session` depuis `app.core.db_boundary` (au lieu de `app.utils.db_utils`)
- Services : auth_session, auth_recovery, user_application, badge_application, admin_application, admin_read, exercise_query, exercise_generation, exercise_attempt, exercise_ai, challenge_query, challenge_attempt, challenge_ai, daily_challenge, analytics, feedback, recommendation, diagnostic
- Utils : settings_reader ; Tests : test_helpers, test_auth_flow
- Run 1, run 2 : 950 passed, 2 skipped ; black, isort : green

---

## Ordre d'exécution (effectif)

| Ordre | Lot | Statut |
|-------|-----|--------|
| 1 | G1 | done |
| 2 | G4 | done |
| 3 | G2 | done |
| 4 | G3 | done |
