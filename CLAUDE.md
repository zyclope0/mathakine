# CLAUDE.md - Mathakine

Contexte projet charge automatiquement a chaque session Claude Code.

---

## Projet

**Mathakine** - plateforme EdTech SaaS d'apprentissage des mathematiques pour enfants.

**Position produit au 2026-04-16 :**

- train visible courant : **`3.6.0-beta.2`**
- le theme spatial neutre est la direction active ; ne pas reintroduire de nouvelle copie Star Wars/Jedi hors compat legacy explicitement documentee
- le frontend a ferme **ACTIF-03** (co-localisation des tests) ; le dernier finding frontend actif reste **ACTIF-04** (couverture / seuils Vitest)
- la feuille de route produit active reste `docs/02-FEATURES/ROADMAP_FONCTIONNALITES.md`
- `.claude/session-plan.md` est une note locale de pilotage founder, pas une preuve runtime autonome

- **Modele** : Freemium B2C + B2B (familles, ecoles, colleges)
- **Gratuit** : experience enfant complete (exercices, defis, gamification)
- **Payant** : tableau de bord parent/enseignant, suivi eleves, gestion multi-enfants/classes
- **Solo founder** - adapter toutes les recommandations a la contrainte d'une seule personne

---

## Stack technique

| Couche        | Techno                                                                  |
| ------------- | ----------------------------------------------------------------------- |
| Backend       | Python / Starlette (pas FastAPI) + SQLAlchemy + PostgreSQL              |
| Frontend      | Next.js 16.2.3 + TypeScript + Tailwind + next-intl fr/en                |
| IA            | OpenAI via SSE POST (`exercise_ai_service`, `challenge_ai_service`)     |
| Auth          | JWT (access 15 min + refresh 7 j), cookies HTTP-only                    |
| Rate limiting | Redis (prod) / memoire (dev/test)                                       |
| Deploiement   | Render (Gunicorn + `uvicorn.workers.UvicornWorker`)                     |
| Version       | `3.6.0-beta.2`                                                          |

---

## Architecture cles

- `app/services/` - logique metier ; controllers/handlers minces
- `server/handlers/` + `server/routes/` - couche HTTP
- `enhanced_server.py` - exporte l'entree ASGI concrete `app = get_app()`
- `app/core/ai_generation_policy.py` - policy modeles IA exercices
- `app/core/ai_config.py` + `challenge_ai_model_policy.py` - policy modeles IA defis (dualite documentee)
- `challenge_contract_policy.py` - contrat IA9 (`response_mode` : QCM / texte / interaction)
- frontend : logique runtime isolee dans hooks/controllers ; vues minces ; tests Vitest co-localises
- gamification : ledger `point_events` + badges + streaks + champ legacy `jedi_rank` conserve comme compatibilite backend

---

## Etat de sante

- backend prod : entree Gunicorn/Starlette stabilisee avec `enhanced_server:app`
- frontend quality:
  - **ACTIF-03** ferme
  - **ACTIF-04** encore ouvert
  - seuils Vitest courants : **46 / 38 / 42 / 48**
- dependances backend :
  - `requirements.txt` = runtime/prod
  - `requirements-dev.txt` = dev/test/docs
- docs actives :
  - gouvernance projet : `docs/03-PROJECT/README.md`
  - reference technique vivante : `README_TECH.md`
  - changelog release : `CHANGELOG.md`

---

## Risques prioritaires connus

| Priorite | Sujet | Probleme |
| -------- | ----- | -------- |
| P1 | `ACTIF-04` frontend | couverture Vitest encore en dessous de l'horizon cible ; toute hausse de seuil doit etre appuyee par une nouvelle mesure CI |
| P2 | Dette architecture backend IA | dualite `ai_config.py` / `challenge_ai_model_policy.py` encore documentee comme dette |
| P2 | Dette docs founder/locales | `.claude/session-plan.md` peut diverger du runtime si on le traite comme source de verite au lieu d'une note de pilotage |

---

## Workflow outils IA

| Situation | Outil |
| --------- | ----- |
| Planifier une feature, sequencer les taches | Codex |
| Verifier une approche avant de coder | Claude Code |
| Implementer, editer des fichiers | Cursor Composer |
| Valider apres implementation | Claude Code `/octo:review` |
| Debugger un probleme difficile | Claude Code `/octo:debug` |
| Audit avant mise en prod | Claude Code `/octo:security` |

**Regle imperative** : `git commit` avant de changer d'outil. Un seul outil ecrit le code a la fois.

---

## Priorites produit actuelles

1. **ACTIF-04 / qualite frontend** - remonter la couverture par ecriture de tests utiles puis re-mesure CI
2. **Parent dashboard / relation parent-enfant** - voir `docs/02-FEATURES/PARENT_DASHBOARD_AND_CHILD_LINKS.md`
3. **Beta fermee** - feedback outille, securite/headers, documentation utilisateur, cadrage OAuth Google (pilotage local dans `.claude/session-plan.md`)
4. **Neutralisation thematique progressive** - ne plus etendre Star Wars/Jedi, converger vers spatial neutre
5. **Fiabilisation documentation / ops** - garder guides, changelog et runbooks alignes sur le code actif

---

## Conventions du projet

- Langue du code : anglais (variables, fonctions, commentaires techniques)
- Langue de la doc projet : francais
- Pas de `os.getenv()` direct - utiliser `settings.X` (Pydantic-validated)
- Filtres SQLAlchemy : `.is_(True)` / `.is_(False)` (pas `== True`)
- Logging : `logger.error("msg %s", var)` (pas f-string)
- Pas de nouvelle copie Star Wars/Jedi dans les nouveaux textes UI, prompts, tags ou commentaires metier ; preferer spatial neutre sauf compat legacy explicitement documentee
- Tout nouveau backlog produit -> `docs/02-FEATURES/ROADMAP_FONCTIONNALITES.md`
- Toute note historique fermee doit quitter le flux actif et aller en archive canonique

---

## Reference rapide docs

| Document | Role |
| -------- | ---- |
| `docs/03-PROJECT/README.md` | index gouvernance projet |
| `docs/02-FEATURES/ROADMAP_FONCTIONNALITES.md` | backlog produit source de verite |
| `docs/02-FEATURES/API_QUICK_REFERENCE.md` | reference API runtime |
| `docs/03-PROJECT/AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md` | audit qualite frontend actif |
| `docs/03-PROJECT/AUDIT_FRONTEND_STANDARDISATION_2026-03-29.md` | reference architecture frontend active |
| `README_TECH.md` | reference technique vivante |
| `CHANGELOG.md` | source de verite version / release |
