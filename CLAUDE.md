# CLAUDE.md - Mathakine

Contexte projet charge automatiquement a chaque session Claude Code.

---

## Projet

**Mathakine** - plateforme EdTech SaaS d'apprentissage des mathematiques pour enfants.

**Position produit au 2026-03-26 :**
- transition active d'un ancien theme Star Wars/Jedi vers un theme spatial plus neutre ;
- le codebase est encore **hybride** ;
- ne pas introduire de nouvelles references Star Wars/Jedi dans les nouveaux flux, libelles, prompts ou tags sans raison explicite de compatibilite.

- **Modele** : Freemium B2C + B2B (familles, ecoles, colleges)
- **Gratuit** : experience enfant complete (exercices, defis, gamification)
- **Payant** : tableau de bord parent/enseignant, suivi eleves, gestion multi-enfants/classes
- **Solo founder** - adapter toutes les recommandations a la contrainte d'une seule personne

---

## Stack technique

| Couche | Techno |
|--------|--------|
| Backend | Python / Starlette (PAS FastAPI) + SQLAlchemy + PostgreSQL |
| Frontend | Next.js 15 + TypeScript + Tailwind, i18n fr/en |
| IA | OpenAI GPT via SSE POST (`exercise_ai_service`, `challenge_ai_service`) |
| Auth | JWT (access 15min + refresh 7j), cookies HTTP-only |
| Rate limiting | Redis (prod) / memoire (dev/test) |
| Deploiement | Render (multi-worker Gunicorn) |
| Version | 2.1.0 |

---

## Architecture cles

- `app/services/` - logique metier (separation stricte)
- `server/handlers/` + `server/routes/` - couche HTTP
- `app/core/ai_generation_policy.py` - policy modeles IA exercices
- `app/core/ai_config.py` + `challenge_ai_model_policy.py` - policy modeles IA defis (deux systemes coexistent - dette connue)
- `challenge_contract_policy.py` - contrat IA9 (`response_mode` : QCM / texte / interaction)
- SSE migre GET -> POST (body JSON) pour les deux flux IA
- Gamification : ledger `point_events` + badges + streaks + champ legacy `jedi_rank` (neutralisation d'affichage en cours ; ne pas renommer sans plan de contrat)

---

## Etat de sante (2026-03-25)

- Code review : **78/100** - `docs/03-PROJECT/CODE_REVIEW_2026-03-22.md`
- Audit technique : **7.0/10** - `docs/03-PROJECT/AUDIT_TECHNIQUE_2026-03-22.md`
- Tests : 1249 passent, 2 skipped, couverture backend 67%
- Tooling : black + isort + mypy + flake8 - tous verts
- Gate CI : `pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py --no-cov`

---

## Risques prioritaires connus

| Priorite | Fichier | Probleme |
|----------|---------|----------|
| ~~P0~~ | ~~`app/utils/token_tracker.py`~~ | ~~Fuite memoire read-path (`get_stats` + `defaultdict` -> buckets vides)~~ - **RESOLU** |
| ~~P0~~ | ~~`app/services/gamification/gamification_service.py:86`~~ | ~~Race condition - `with_for_update()` absent~~ - **RESOLU** |
| P1 | `frontend/app/api/chat/route.ts` | Routes chat sans authentification (cout OpenAI non controle) |
| P1 | `.env.example` | `REDIS_URL` absente -> crash demarrage prod |
| ~~P1~~ | ~~`app/services/challenges/challenge_service.py:353`~~ | ~~Double filtrage `is_active`/`is_archived` incoherent~~ - **RESOLU** |
| ~~P1~~ | ~~`app/services/exercises/exercise_attempt_service.py`~~ | ~~`apply_points` non appele pour exercices standard~~ - **RESOLU** |

---

## Workflow outils IA

| Situation | Outil |
|-----------|-------|
| Planifier une feature, sequencer les taches | **Codex** |
| Verifier une approche avant de coder | **Claude Code** |
| Implementer, editer des fichiers | **Cursor Composer** |
| Valider apres implementation | **Claude Code** `/octo:review` |
| Debugger un probleme difficile | **Claude Code** `/octo:debug` |
| Audit avant mise en prod | **Claude Code** `/octo:security` |

**Regle imperative** : `git commit` avant de changer d'outil. Un seul outil ecrit le code a la fois.

---

## Priorites produit actuelles

1. **F42 completion end-to-end** - generation, progression/evaluation, defis, surfaces publiques
2. **Neutralisation thematique progressive** - ne plus etendre Star Wars/Jedi, converger vers spatial neutre
3. **Securisation route chat** - authentification / controle du cout OpenAI
4. **Fiabilisation deploiement** - `.env.example` / `REDIS_URL`
5. **Tableau de bord parent minimal** - premiere brique payante

---

## Conventions du projet

- Langue du code : anglais (variables, fonctions, commentaires techniques)
- Langue de la doc projet : francais
- Pas de `os.getenv()` direct - utiliser `settings.X` (Pydantic-validated)
- Filtres SQLAlchemy : `.is_(True)` / `.is_(False)` (pas `== True`)
- Logging : `logger.error("msg: %s", var)` (pas f-string)
- Pas de nouvelle copie Star Wars/Jedi dans les nouveaux textes UI, prompts, tags ou commentaires metier ; preferer spatial neutre sauf compat legacy explicitement documentee
- Tout nouveau backlog -> `docs/02-FEATURES/ROADMAP_FONCTIONNALITES.md`

---

## Reference rapide docs

| Document | Role |
|----------|------|
| `docs/03-PROJECT/README.md` | Index gouvernance projet |
| `docs/02-FEATURES/ROADMAP_FONCTIONNALITES.md` | Backlog produit source de verite |
| `docs/02-FEATURES/API_QUICK_REFERENCE.md` | Reference API runtime |
| `docs/02-FEATURES/CHALLENGE_CONTRACT_IA9.md` | Contrat defis response_mode |
| `docs/03-PROJECT/CODE_REVIEW_2026-03-22.md` | Derniere revue de code |
| `docs/03-PROJECT/AUDIT_TECHNIQUE_2026-03-22.md` | Dernier audit technique |
