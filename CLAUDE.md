# CLAUDE.md — Mathakine

Contexte projet chargé automatiquement à chaque session Claude Code.

---

## Projet

**Mathakine** — plateforme EdTech SaaS d'apprentissage des mathématiques pour enfants (thème Star Wars/Jedi).

- **Modèle** : Freemium B2C + B2B (familles, écoles, collèges)
- **Gratuit** : expérience enfant complète (exercices, défis, gamification)
- **Payant** : tableau de bord parent/enseignant, suivi élèves, gestion multi-enfants/classes
- **Solo founder** — adapter toutes les recommandations à la contrainte d'une seule personne

---

## Stack technique

| Couche | Techno |
|--------|--------|
| Backend | Python / Starlette (PAS FastAPI) + SQLAlchemy + PostgreSQL |
| Frontend | Next.js 15 + TypeScript + Tailwind, i18n fr/en |
| IA | OpenAI GPT via SSE POST (`exercise_ai_service`, `challenge_ai_service`) |
| Auth | JWT (access 15min + refresh 7j), cookies HTTP-only |
| Rate limiting | Redis (prod) / mémoire (dev/test) |
| Déploiement | Render (multi-worker Gunicorn) |
| Version | 2.1.0 |

---

## Architecture clés

- `app/services/` — logique métier (séparation stricte)
- `server/handlers/` + `server/routes/` — couche HTTP
- `app/core/ai_generation_policy.py` — policy modèles IA exercices
- `app/core/ai_config.py` + `challenge_ai_model_policy.py` — policy modèles IA défis (deux systèmes coexistants — dette connue)
- `challenge_contract_policy.py` — contrat IA9 (`response_mode` : QCM / texte / interaction)
- SSE migré GET → POST (body JSON) pour les deux flux IA
- Gamification : ledger `point_events` + badges + streaks + `jedi_rank`

---

## État de santé (2026-03-25)

- Code review : **78/100** — `docs/03-PROJECT/CODE_REVIEW_2026-03-22.md`
- Audit technique : **7.0/10** — `docs/03-PROJECT/AUDIT_TECHNIQUE_2026-03-22.md`
- Tests : 1249 passent, 2 skipped, couverture backend 67%
- Tooling : black + isort + mypy + flake8 — tous verts
- Gate CI : `pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py --no-cov`

---

## Risques prioritaires connus

| Priorité | Fichier | Problème |
|----------|---------|----------|
| ~~P0~~ | ~~`app/utils/token_tracker.py`~~ | ~~Fuite mémoire read-path (`get_stats` + `defaultdict` → buckets vides)~~ — **RÉSOLU** (dict explicite + `.get` en lecture ; TTL/cap inchangés) |
| ~~P0~~ | ~~`app/services/gamification/gamification_service.py:86`~~ | ~~Race condition — `with_for_update()` absent~~ — **RÉSOLU** (guard PostgreSQL/SQLite + `with_for_update()` implémenté) |
| P1 | `frontend/app/api/chat/route.ts` | Routes chat sans authentification (coût OpenAI non contrôlé) |
| P1 | `.env.example` | `REDIS_URL` absente → crash démarrage prod |
| P1 | `app/services/challenges/challenge_service.py:353` | Double filtrage `is_active`/`is_archived` incohérent |
| ~~P1~~ | ~~`app/services/exercises/exercise_attempt_service.py`~~ | ~~`apply_points` non appelé pour exercices standard~~ — **RÉSOLU** (`exercise_attempt_service.py:127`) |

---

## Workflow outils IA

| Situation | Outil |
|-----------|-------|
| Planifier une feature, séquencer les tâches | **Codex** |
| Vérifier une approche avant de coder | **Claude Code** |
| Implémenter, éditer des fichiers | **Cursor Composer** |
| Valider après implémentation | **Claude Code** `/octo:review` |
| Débugger un problème difficile | **Claude Code** `/octo:debug` |
| Audit avant mise en prod | **Claude Code** `/octo:security` |

**Règle impérative** : `git commit` avant de changer d'outil. Un seul outil écrit le code à la fois.

---

## Priorités produit actuelles

1. **Corriger les P0** — fuite mémoire TokenTracker + race condition gamification
2. **Architecture âge/difficulté (F42)** — colonne `age_group` sur `users`, backfill conditionnel
3. **Onboarding enfant fluide** — inscription → premier exercice en < 2 minutes
4. **Tableau de bord parent minimal** — la première brique payante

---

## Conventions du projet

- Langue du code : anglais (variables, fonctions, commentaires techniques)
- Langue de la doc projet : français
- Pas de `os.getenv()` direct — utiliser `settings.X` (Pydantic-validated)
- Filtres SQLAlchemy : `.is_(True)` / `.is_(False)` (pas `== True`)
- Logging : `logger.error("msg: %s", var)` (pas f-string)
- Tout nouveau backlog → `docs/02-FEATURES/ROADMAP_FONCTIONNALITES.md`

---

## Référence rapide docs

| Document | Rôle |
|----------|------|
| `docs/03-PROJECT/README.md` | Index gouvernance projet |
| `docs/02-FEATURES/ROADMAP_FONCTIONNALITES.md` | Backlog produit source de vérité |
| `docs/02-FEATURES/API_QUICK_REFERENCE.md` | Référence API runtime |
| `docs/02-FEATURES/CHALLENGE_CONTRACT_IA9.md` | Contrat défis response_mode |
| `docs/03-PROJECT/CODE_REVIEW_2026-03-22.md` | Dernière revue de code |
| `docs/03-PROJECT/AUDIT_TECHNIQUE_2026-03-22.md` | Dernier audit technique |
