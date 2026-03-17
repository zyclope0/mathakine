# Lot F6 - Replicability and Operability Closure

> Iteration `F`
> Status: done (2026-03-17)

## Mission

Close the iteration `F` by turning the backend into a more repeatably operable and understandable system for another team.

## Priority Targets

- environment truth
- repeatable validation rules
- onboarding / runbook quality
- documentation of operational invariants

## Success Criteria

- clearer setup and run truth
- repeatable validation and deploy expectations
- stronger project-operability documentation

---

## Closure (2026-03-17)

### What F Proved

| Lot | Scope | Proven Outcome |
|-----|-------|----------------|
| F1 | auth_service contracts | CreateUserResult, RefreshTokenResult, UpdatePasswordResult — explicit typed results on create_user, refresh_access_token, update_user_password, create_registered_user_with_verification |
| F2 | badge_requirement_engine | Cluster volume extrait vers `badge_requirement_volume.py` — ~110 lignes, checkers et progress getters par responsabilité métier |
| F3 | admin_content_service | Flux create_badge décomposé : `admin_badge_create_flow.py` — prepare, validate, persist, mapping séparés |
| F4 | seam admin badge create | BadgeCreatePrepared TypedDict, ValidationResult — typage renforcé sur le flux F3 |
| F5 | runtime/data boundary | `app.core.db_boundary` — contrat explicite, run_db_bound, sync_db_session, test prouvant la chaîne active |

**Structural gains** : contrats auth plus explicites, badge engine moins dense, mutation admin badge séparée, typage défendable sur un sous-scope, boundary runtime/data formalisée.

### What F Still Does Not Claim

- **Global strict mypy** : le projet reste en mode non-strict ; typage renforcé uniquement sur seams traités (F4).
- **Repository pattern** : pas de couche repository globale ; accès DB reste via sync_db_session + services.
- **Tous les contrats auth** : `authenticate_user_with_session` et autres chemins restent en tuples ; F1 a traité un sous-ensemble.
- **Tous les clusters admin** : create_exercise, put_challenge, etc. restent non décomposés ; F3 a traité create_badge uniquement.
- **enhanced_server_adapter** : reste legacy ; seul create_generated_exercise est utilisé.
- **Vérification formelle** : aucune preuve de propriétés (invariants, terminaison) ; le backend n'est pas "académique" au sens de la vérification formelle.

### Replicability / Operability Invariants

**Environment** :
- PostgreSQL local sur `localhost:5432` pour les tests
- `TEST_DATABASE_URL` distinct de `DATABASE_URL`
- `REDIS_URL` obligatoire en production (fail-closed si absent)
- `scripts/check_local_db.py` et `scripts/test_backend_local.py` pour préparation locale

**Validation** :
- Full suite : `pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py --no-cov`
- False gate exclu : `tests/api/test_admin_auth_stability.py` (lance pytest depuis pytest)
- Coverage CI : `63 %` sur app/ + server/
- Format : `black app/ server/ tests/ --check`, `isort app/ server/ tests/ --check-only --diff`
- Typage : `mypy app/ server/ --ignore-missing-imports`
- Critique : `flake8 app/ server/ --select=E9,F63,F7,F82`

**Documentation** :
- `docs/INDEX.md` : point d'entrée
- `README_TECH.md` : runtime truth, baseline, monitoring
- `docs/00-REFERENCE/ARCHITECTURE.md` : modèle d'exécution, boundary
- `docs/01-GUIDES/TESTING.md` : gates, batteries, false positives
- `docs/01-GUIDES/DEPLOYMENT_ENV.md` : variables deploy, checklist
- `app.core.db_boundary` : contrat boundary runtime/data

### Validated Backend Baseline

**Post-F (2026-03-17)** :
- full suite : `936 passed, 2 skipped` (excl. test_admin_auth_stability)
- black : green
- isort : green
- mypy : green (annotation-unchecked notes non bloquantes)
- flake8 : green
- coverage gate CI : `63 %`

**Commandes de validation reproductibles** :
```bash
pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py --no-cov
black app/ server/ tests/ --check
isort app/ server/ tests/ --check-only --diff
mypy app/ server/ --ignore-missing-imports
flake8 app/ server/ --select=E9,F63,F7,F82
```

### Niveau Reel Atteint Par Le Backend Apres F

**Défendable** :
- **Industrialisable** : contrats internes plus explicites, hotspots décomposés, boundary formalisée ; changement localisé et coût de changement réduit sur les seams traités.
- **Replicable** : baseline et commandes documentées ; invariants de validation et deploy explicites ; une autre équipe peut reprendre avec les docs.
- **Adaptable** : décomposition par responsabilité métier ; extension de nouveaux seams sans réouvrir les hotspots traités.
- **Gérable** : runbook, gates, false gate documenté ; moins de dette architecturale cachée.

**Non défendable** :
- **Académique** : au sens strict (vérification formelle, preuves de propriétés), le backend n'est pas académique. Le terme "academic" dans le nom de l'itération désigne une ambition de rigueur interne et de discipline explicite, pas une certification formelle.

### Hors Scope F6

- Pas de refactor code
- Pas de modification des contrats HTTP
- Pas de chantier infra externe
- Pas de redesign CI large
