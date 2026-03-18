# Pilotage Cursor — Architecture Clean (all_models / all_schemas + Vertical Slicing)

> Créé : 18/03/2026  
> Status : **Cible A CLOSED — Cible B CLOSED**  
> Principe : Baby Steps, aucune modification de logique métier, validation QA obligatoire par itération

## Contexte

L'application est fonctionnellement stable. L'architecture technique doit évoluer pour résoudre deux problèmes majeurs :
1. **Imports globaux toxiques** : `all_models.py` et `all_schemas.py` (couplage fort, lenteur au chargement)
2. **Services à plat** : `app/services/` contient plus de 60 fichiers sans Bounded Contexts (absence de découpage vertical)

Référence : [POINTS_RESTANTS_2026-03-15.md](./POINTS_RESTANTS_2026-03-15.md) § Next Technical Candidates.

## Baseline de départ (post-G, post–H1–H3)

- gate standard backend : `pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py --no-cov` → `951 passed, 2 skipped`
- black, isort, mypy, flake8 : green
- measured local coverage : `67.30 %`
- coverage gate CI : `63 %`

## Règles absolues (qualité & non-régression)

| Règle | Description |
|-------|-------------|
| **Aucune modification de logique métier** | Uniquement déplacement de fichiers et mise à jour des imports. Comportement identique à 100 %. |
| **Baby Steps** | Interdiction de faire toutes les modifications d'un coup. Découpage en itérations ultra-courtes. |
| **Quality Gate** | À la fin de chaque itération : compile + pytest. Ne jamais passer à la suivante sans accord explicite « Go Itération Suivante ». |
| **Protocole Cursor Max Effort** | [CURSOR_MAX_EFFORT_BACKEND_PROTOCOL_2026-03-11.md](./CURSOR_MAX_EFFORT_BACKEND_PROTOCOL_2026-03-11.md) — run 1, run 2, full suite si blast radius étendu. |

## Méthodologie (alignée itérations E, F, G)

Comme pour les itérations précédentes :

1. **Un seul sous-scope par lot** — pas de mélange de périmètres
2. **Batterie cible** → run 1 → run 2 → full suite si blast radius > sous-scope
3. **black, isort, mypy, flake8** verts avant verdict GO
4. **Pas de changement de contrat HTTP public**
5. **Pas de refactor global** — uniquement déplacements et imports
6. **Validation explicite** : fichiers runtime modifiés, endpoints touchés, ce qui a été prouvé

## Known False Gate

Ne pas utiliser comme gate de validation standard :
- `tests/api/test_admin_auth_stability.py`

## Cible A — Désamorçage (all_models / all_schemas)

### État actuel

- `all_models.py` : supprimé (A3)
- `all_schemas.py` : supprimé (A5)
- **99 % du codebase** utilise des imports directs (`from app.models.user import User`, `from app.schemas.user import UserCreate`)

---

### Itération A1 — Remplacer all_models dans app/db/init_db.py

| Élément | Détail |
|--------|--------|
| **Mission** | Remplacer `import app.models.all_models` par imports directs des modules de modèles requis pour `Base.metadata.create_all` (fallback Alembic) |
| **Fichiers modifiés** | `app/db/init_db.py` |
| **Batterie cible** | `pytest -q -k "test_init or test_create or test_initialize" --maxfail=5 --no-cov` |
| **Checks obligatoires** | git status, run 1, run 2, black, isort |
| **Verdict** | GO uniquement si green reproductible |

**A1 Réalisation (2026-03-18)**  
- `import app.models.all_models` remplacé par 15 imports de modules (achievement, admin_audit_log, attempt, daily_challenge, diagnostic_result, edtech_event, exercise, feedback_report, logic_challenge, notification, progress, recommendation, setting, user, user_session)  
- Run 1, run 2 : 48 passed  
- black, isort : green  
- **GO**

#### Travail à prévoir (post-A1, avant A2)

Le désamorçage de `all_models` implique que l’énumération des modèles est désormais explicite en plusieurs endroits. **Lors de l’ajout d’un nouveau modèle** (nouveau fichier dans `app/models/`), la checklist suivante s’applique :

| Fichier | Action |
|---------|--------|
| `app/models/<nouveau_modele>.py` | Créer le fichier modèle |
| `migrations/env.py` | Ajouter l’import du module (pour Alembic autogenerate) |
| `app/db/init_db.py` | Ajouter `import app.models.<nouveau_modele>  # noqa: F401` |
| `app/models/__init__.py` | Après A2 : ajouter au `__all__` et imports si réexport souhaité |

Référence : [docs/01-GUIDES/CONTRIBUTING.md](../01-GUIDES/CONTRIBUTING.md) § Ajouter un nouveau modèle.

---

### Itération A2 — Remplacer all_models dans app/models/__init__.py

| Élément | Détail |
|--------|--------|
| **Mission** | Remplacer `from app.models.all_models import *` par imports directs depuis chaque module + `__all__` explicite |
| **Fichiers modifiés** | `app/models/__init__.py` |
| **Batterie cible** | `pytest -q --maxfail=10 --no-cov` (tests unitaires ciblés) |
| **Checks obligatoires** | run 1, run 2, black, isort |
| **Note** | Vérifier qu’aucun import `from app.models import X` n’existe (déjà confirmé : 0 occurrence) |

**A2 Réalisation (2026-03-18)**  
- `from app.models.all_models import *` remplacé par 15 imports explicites + `__all__`  
- Batterie init/create : 48 passed ; test_models, test_db_init_service, test_database_init : 30 passed  
- black, isort : green  
- Échecs StaleDataError/session : **bisect (18/03) confirme aucune causalité avec A1/A2** — les mêmes tests sont flaky avec le code original (5 runs : 4/5 échecs) et avec A1+A2 (3/5 échecs). Cause : isolation session préexistante (db_session sans nested transaction). **Fix appliqué** : `tests/conftest.py` db_session avec `join_transaction_mode="create_savepoint"` (pattern SQLAlchemy 2.0) — 5/5 runs verts après fix.  
- **GO**

---

### Itération A3 — Supprimer all_models.py

| Élément | Détail |
|--------|--------|
| **Mission** | Supprimer `app/models/all_models.py` |
| **Fichiers supprimés** | `app/models/all_models.py` |
| **Batterie cible** | Full suite |
| **Checks obligatoires** | run 1, run 2, black, isort, mypy |

**A3 Réalisation (2026-03-18)**  
- `app/models/all_models.py` supprimé ; `app/models/__init__.py` utilise imports directs + `legacy_tables`.  
- Fix conftest : `db_session` simplifiée (session classique, plus de savepoint) ; ordre de suppression FK corrigé dans `test_data_cleanup.py`.  
- Run 1, run 2 : 951 passed, 2 skipped.  
- black, isort, mypy : green.  
- **GO**

---

### Itération A4 — Remplacer all_schemas dans app/schemas/__init__.py

| Élément | Détail |
|--------|--------|
| **Mission** | Remplacer `from app.schemas.all_schemas import *` par imports directs depuis chaque module + `__all__` explicite |
| **Fichiers modifiés** | `app/schemas/__init__.py` |
| **Batterie cible** | `pytest -q --maxfail=10 --no-cov` |
| **Checks obligatoires** | run 1, run 2, black, isort |

**A4 Réalisation (2026-03-18)**  
- `from app.schemas.all_schemas import *` remplacé par imports directs depuis attempt, common, exercise, logic_challenge, progress, user, user_session + `__all__` explicite.  
- Fichier unique modifié : `app/schemas/__init__.py` (all_schemas.py inchangé, suppression prévue en A5).  
- Run 1, run 2 : 951 passed, 2 skipped.  
- black, isort : green.  
- **GO**

---

### Itération A5 — Supprimer all_schemas.py

| Élément | Détail |
|--------|--------|
| **Mission** | Supprimer `app/schemas/all_schemas.py` |
| **Fichiers supprimés** | `app/schemas/all_schemas.py` |
| **Batterie cible** | Full suite |
| **Checks obligatoires** | run 1, run 2, black, isort, mypy |

**A5 Réalisation (2026-03-18)**  
- `app/schemas/all_schemas.py` supprimé (orphelin depuis A4).  
- Run 1, run 2 : 951 passed, 2 skipped.  
- black, isort, mypy : green (correction isort préexistante sur `app/models/__init__.py`).  
- **GO**

---

### Itération A6 — Mise à jour documentation

| Élément | Détail |
|--------|--------|
| **Mission** | Mettre à jour `docs/CONVENTION_DOCUMENTATION.md` et toute référence à `all_models` / `all_schemas` |
| **Validation** | `grep -r "all_models\|all_schemas" docs/ app/ server/ tests/` → 0 occurrence restante (hors ce pilotage) |

**A6 Réalisation (2026-03-18)**  
- `CONVENTION_DOCUMENTATION.md` : table source de vérité modèles/schémas mise à jour ; ligne Schémas Pydantic ajoutée.  
- `CONTRIBUTING.md` : checklist modèles (A1–A5) ; nouvelle checklist schémas (A4–A5).  
- `03-PROJECT/README.md`, `POINTS_RESTANTS`, `INDEX.md` : statut Cible A closed.  
- `CONTEXTE_PROJET_REEL.md` : structure models/ corrigée.  
- `README_TECH.md` : section Architecture Clean (Cible A) ajoutée.  
- `docs/00-REFERENCE/ARCHITECTURE.md` : app/models et app/schemas (modules explicites) ; baseline 951 passed.  
- Validation : grep hors pilotage → 0 occurrence dans docs guides/ref.  
- **GO**

---

## Cible B — Vertical Slicing (app/services/) — **CLOSED** (2026-03-18)

### État final — Cartographie réalisée

| Sous-dossier | Fichiers | Nb |
|--------------|----------|-----|
| **auth/** | auth_service, auth_session_service, auth_recovery_service | 3 |
| **users/** | user_service, user_application_service | 2 |
| **badges/** | badge_service, badge_application_service, badge_award_service, badge_award_persistence, badge_progress_service, badge_user_view_service, badge_rarity_service, badge_format_helpers, badge_gamification_updates, badge_requirement_engine, badge_requirement_volume, badge_requirement_fallbacks, badge_requirement_validation, badge_stats_cache | 14 |
| **exercises/** | exercise_service, exercise_query_service, exercise_attempt_service, exercise_generation_service, exercise_stream_service, exercise_ai_service, exercise_stats_service, interleaved_practice_service, adaptive_difficulty_service | 9 |
| **challenges/** | challenge_service, challenge_query_service, challenge_attempt_service, challenge_stream_service, challenge_ai_service, challenge_answer_service, challenge_validator, challenge_pattern_sequence_validation, challenge_validation_analysis, logic_challenge_service, maze_validator | 11 |
| **progress/** | progress_timeline_service, streak_service, daily_challenge_service | 3 |
| **admin/** | admin_service, admin_application_service, admin_read_service, admin_content_service, admin_user_service, admin_config_service, admin_stats_service, admin_overview_service, admin_reporting_service, admin_moderation_service, admin_audit_service, admin_helpers, admin_badge_create_flow, admin_exercise_create_flow | 14 |
| **analytics/** | analytics_service | 1 |
| **communication/** | email_service, chat_service | 2 |
| **core/** | db_init_service, enhanced_server_adapter | 2 |
| **diagnostic/** | diagnostic_service | 1 |
| **feedback/** | feedback_service | 1 |
| **recommendation/** | recommendation_service | 1 |

**Résultat validation finale** : `pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py --no-cov` → `951 passed, 2 skipped`. Aucun fichier de logique métier à la racine de `app/services/`.

---

### Itération B1 — Créer app/services/auth/ (3 fichiers)

| Élément | Détail |
|--------|--------|
| **Mission** | Créer `app/services/auth/`, y déplacer auth_service, auth_session_service, auth_recovery_service. Créer `__init__.py` avec réexports. Mettre à jour tous les imports (handlers, tests, autres services). |
| **Fichiers déplacés** | auth_service.py, auth_session_service.py, auth_recovery_service.py |
| **Imports à mettre à jour** | server/handlers/auth_handlers.py, server/auth.py, autres services appelants |
| **Batterie cible** | `pytest -q tests/unit/test_auth_service.py tests/api/test_auth_flow.py -k "not test_admin_auth_stability" --no-cov` |
| **Checks obligatoires** | run 1, run 2, full suite (blast radius = handlers), black, isort, mypy |

---

### Itération B2 — Créer app/services/users/ (2 fichiers)

| Élément | Détail |
|--------|--------|
| **Mission** | Créer `app/services/users/`, y déplacer user_service, user_application_service |
| **Batterie cible** | `pytest -q tests/unit/test_user_service.py tests/api/test_user_endpoints.py --no-cov` |

---

### Itération B3 — Créer app/services/badges/ (14 fichiers)

| Élément | Détail |
|--------|--------|
| **Mission** | Créer `app/services/badges/`, y déplacer les 14 fichiers badge. Gérer les dépendances internes (engine → volume, application → service). |
| **Batterie cible** | `pytest -q tests/unit/test_badge* tests/api/test_badge* --no-cov` |

---

### Itération B4 — Créer app/services/exercises/ (9 fichiers)

| Élément | Détail |
|--------|--------|
| **Mission** | Créer `app/services/exercises/`, y déplacer les 9 fichiers exercise |
| **Batterie cible** | `pytest -q tests/unit/test_exercise* tests/api/test_exercise_endpoints* --no-cov` |

---

### Itération B5 — Créer app/services/challenges/ (11 fichiers)

| Élément | Détail |
|--------|--------|
| **Mission** | Créer `app/services/challenges/`, y déplacer les 11 fichiers challenge / logic_challenge |
| **Batterie cible** | `pytest -q tests/unit/test_challenge* tests/unit/test_logic_challenge* tests/api/test_challenge* --no-cov` |

---

### Itération B6 — Créer app/services/admin/ (14 fichiers)

| Élément | Détail |
|--------|--------|
| **Mission** | Créer `app/services/admin/`, y déplacer les 14 fichiers admin |
| **Batterie cible** | `pytest -q tests/unit/test_admin* tests/api/test_admin* --no-cov` |

---

### Itération B7 — Créer app/services/analytics/ et app/services/core/

| Élément | Détail |
|--------|--------|
| **Mission** | Créer `app/services/analytics/` (1 fichier), `app/services/core/` (10 fichiers partagés) |
| **Batterie cible** | Full suite (analytics, diagnostic, daily_challenge, etc.) |

---

### Itération B8 — Nettoyer app/services/__init__.py

| Élément | Détail |
|--------|--------|
| **Mission** | Adapter `app/services/__init__.py` pour réexporter depuis les nouveaux sous-packages |
| **Batterie cible** | Full suite, vérifier les imports dans tout le projet |

---

## Ordre d'exécution global

1. **Cible A** : A1 → A2 → A3 → A4 → A5 → A6 (désamorçage complet)
2. **Cible B** : B1 → B2 → B3 → B4 → B5 → B6 → B7 → B8 (vertical slicing)

## Format compte-rendu (par itération)

À la fin de chaque itération, documenter :

1. Fichiers modifiés (runtime)
2. Fichiers de test modifiés
3. Sous-scope réalisé
4. Ce qui a été prouvé
5. Résultat run 1, run 2, full suite si applicable
6. Résultat black, isort, mypy, flake8
7. **GO / NO-GO**

## Hors scope

- Modifications de logique métier
- Changement de contrat HTTP public
- Refactor global
- Introduction de nouveaux patterns (repository, CQRS, etc.) — uniquement réorganisation de fichiers

## Références

- [POINTS_RESTANTS_2026-03-15.md](./POINTS_RESTANTS_2026-03-15.md)
- [CURSOR_MAX_EFFORT_BACKEND_PROTOCOL_2026-03-11.md](./CURSOR_MAX_EFFORT_BACKEND_PROTOCOL_2026-03-11.md)
- [docs/CONVENTION_DOCUMENTATION.md](../CONVENTION_DOCUMENTATION.md)
- Archive G : [archives/LOTS_G_RESIDUAL_CONTRACTS_AND_CLEANUP_2026-03-18/README.md](./archives/LOTS_G_RESIDUAL_CONTRACTS_AND_CLEANUP_2026-03-18/README.md)
