# Rapport De Revue Documentaire - 2026-04-16

> Scope: active documentation truth review
> Reviewer posture: repository-first, code-first, zero-trust toward stale documentation

## Resume executif

Les **89 documents actifs preexistants** du depot ont ete relus et challenges contre la verite terrain du code, des tests, de la configuration, de la CI, du deploy, et de l'etat Git.

Resultat :

- les contradictions actives les plus critiques ont ete corrigees
- les notes d'implementation closes encore au root actif ont ete archivees
- l'ancien bucket `docs/06-WIDGETS/` a quitte le flux actif
- `CHANGELOG.md` a ete realigne sur la realite 2026-04-16
- les docs actives restantes sont coherentes avec le repo sur les points runtime, versions, seuils de couverture, emplacements de tests et gouvernance documentaire

## Findings

### P1

- Aucun finding `P1` ouvert apres corrections.

### P2

- `CHANGELOG.md` et plusieurs guides actifs deploiement/runtime etaient en retard sur la verite terrain :
  - split `requirements.txt` / `requirements-dev.txt`
  - backend Render `Mathakine-alpha`
  - entree ASGI canonique `enhanced_server:app`
  - seuils Vitest `46 / 38 / 42 / 48`
  - fermeture `ACTIF-03` et reduction de `frontend/__tests__/unit/`
- Ces ecarts ont ete corriges.

### P3

- Plusieurs chemins de tests etaient encore documentes a l'ancien emplacement `frontend/__tests__/unit/...` alors que les suites ont ete co-localisees.
- `frontend/README.md` annoncait encore `55 hooks` au lieu de `58`.
- `docs/04-FRONTEND/HOOKS_CATALOGUE.md` contenait une duplication residuelle de deux hooks.
- `docs/03-PROJECT/archives/IMPLEMENTATION_NOTES_CLOSED_2026-04/README.md` n'inventoriait pas encore `IMPLEMENTATION_F35_REDACTION_LOGS_DB.md`.
- Ces ecarts ont ete corriges.

## Inventaire des documents actifs controles

### Par zone

- `root + assistant docs`: `6`
- `docs/00-REFERENCE`: `7`
- `docs/01-GUIDES`: `20`
- `docs/02-FEATURES`: `20`
- `docs/03-PROJECT` actifs: `11`
- `docs/04-FRONTEND`: `16`
- `docs/05-ADR`: `6`
- `docs/assets`: `1`
- `docs/` root docs: `2`

### Regles d'inclusion

- inclus:
  - `README.md`
  - `README_TECH.md`
  - `CHANGELOG.md`
  - `CLAUDE.md`
  - `.claude/session-plan.md`
  - `.github/copilot-instructions.md`
  - tous les `docs/**/*.md` hors buckets explicitement archives
- exclus du flux actif:
  - tout chemin sous `docs/**/archives/**`
  - la collection legacy `docs/03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/**`
  - binaires documentaires (`.docx`) et artefacts generes

## Corrections appliquees

### Runtime, setup et deploy

- guides backend/setup realignes sur `requirements-dev.txt` pour le dev/test
- guides deploy/runbook/maintenance realignes sur le backend Render `Mathakine-alpha`
- references runtime realignees sur `gunicorn enhanced_server:app`

Documents touches :

- `README.md`
- `docs/00-REFERENCE/GETTING_STARTED.md`
- `docs/01-GUIDES/CONTRIBUTING.md`
- `docs/01-GUIDES/DEVELOPMENT.md`
- `docs/01-GUIDES/DEPLOYMENT_ENV.md`
- `docs/01-GUIDES/MAINTENANCE.md`
- `docs/01-GUIDES/QU_EST_CE_QUE_VENV.md`
- `docs/01-GUIDES/TESTING.md`
- `docs/01-GUIDES/TROUBLESHOOTING.md`
- `docs/03-PROJECT/CICD_DEPLOY.md`

### Frontend architecture, i18n et tests

- `frontend/README.md` realigne sur:
  - `Next.js 16.2.3`
  - `next-intl 4.9.1`
  - `58 hooks`
  - note juste sur `.claude/session-plan.md`
- `frontend/__tests__/README.md` realigne sur la nouvelle structure `unit/` minimale
- docs frontend realignees sur:
  - tests de routes API co-localises
  - fermeture `ACTIF-03`
  - seuils Vitest `46 / 38 / 42 / 48`
  - architecture actuelle des hooks/composants
- docs i18n nettoyees des dettes deja traitees

Documents touches :

- `frontend/README.md`
- `frontend/__tests__/README.md`
- `docs/01-GUIDES/I18N_CONTRIBUTION.md`
- `docs/02-FEATURES/I18N.md`
- `docs/04-FRONTEND/API_ROUTES.md`
- `docs/04-FRONTEND/ARCHITECTURE.md`
- `docs/04-FRONTEND/HOOKS_CATALOGUE.md`
- `docs/04-FRONTEND/COMPONENTS_CATALOGUE.md`
- `docs/04-FRONTEND/README.md`
- `docs/04-FRONTEND/DASHBOARD_WIDGETS/CORRECTIONS_WIDGETS.md`
- `docs/04-FRONTEND/DASHBOARD_WIDGETS/README.md`

### Gouvernance projet, audits et changelog

- `README_TECH.md` realigne sur la verite active:
  - `ACTIF-03` clos
  - `ACTIF-04-COVERAGE-03` pris en compte
  - chemins archives pour les notes closes
- `docs/03-PROJECT/README.md` clarifie le role de `.claude/session-plan.md`
- `docs/INDEX.md` realigne les liens actifs/archives
- audits frontend actifs realignes sur la verite terrain
- `docs/02-FEATURES/ROADMAP_FONCTIONNALITES.md` realigne les liens vers les notes d'implementation archivees
- `CHANGELOG.md` remis en coherence exhaustive sur les changements non livres de `3.6.0-alpha.1`

Documents touches :

- `README_TECH.md`
- `CHANGELOG.md`
- `docs/INDEX.md`
- `docs/02-FEATURES/ROADMAP_FONCTIONNALITES.md`
- `docs/03-PROJECT/README.md`
- `docs/03-PROJECT/AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md`
- `docs/03-PROJECT/AUDIT_FRONTEND_STANDARDISATION_2026-03-29.md`
- `docs/03-PROJECT/ANALYSE_DEPENDANCES_ET_OPPORTUNITES_2026-04-13.md`
- `CLAUDE.md`

### Convention documentaire

- `docs/CONVENTION_DOCUMENTATION.md` realigne sur la taxonomie active
- `docs/06-WIDGETS/` n'est plus presente comme bucket actif

## Documents archives avec justification

### Notes d'implementation closes sorties du flux actif

Deplaces vers `docs/03-PROJECT/archives/IMPLEMENTATION_NOTES_CLOSED_2026-04/` :

- `IMPLEMENTATION_F07_TIMELINE.md`
- `IMPLEMENTATION_F32_SESSION_ENTRELACEE.md`
- `RAPPORT_VALIDATE_TOKEN_RATE_LIMIT_2026-04-07.md`

Justification :

- utiles pour la tracabilite
- closes
- ne doivent plus etre prises pour source de verite active

### Redirects widgets legacy sortis du flux actif

Deplaces vers `docs/04-FRONTEND/archives/LEGACY_WIDGET_REDIRECTS_2026-04/` :

- `CORRECTIONS_WIDGETS.md`
- `DESIGN_SYSTEM_WIDGETS.md`
- `ENDPOINTS_PROGRESSION.md`
- `F02_DAILY_CHALLENGES_WIDGET.md`
- `INTEGRATION_PROGRESSION_WIDGETS.md`
- `README.md`

Justification :

- anciens redirects de compatibilite
- doublonnaient la doc canonique de `docs/04-FRONTEND/DASHBOARD_WIDGETS/`

## Points encore ambigus ou a arbitrer

- `.claude/session-plan.md` a ete relu et challenge, mais n'a pas ete edite dans cette revue car le fichier porte deja des modifications locales de travail. Son statut a ete clarifie dans les docs actives : note de pilotage founder locale, pas verite runtime autonome.
- `.github/copilot-instructions.md` a ete relu et garde actif comme document d'assistance/projet. Aucun ecart bloquant avec la verite terrain n'a justifie une correction dans cette passe.
- `AGENTS.md` n'existe pas comme fichier dans le repo. Les instructions AGENTS ont ete fournies via le contexte de travail, pas par un document versionne.

## Verdict global sur la fiabilite de la documentation

Verdict: **documentation active defendable et coherente avec la verite terrain**, apres correction et archivage.

Ce qui etait faux :

- versions et seuils frontend partiellement obsoletes
- chemins de tests apres co-localisation
- separation prod/dev Python mal refletee
- notes closes encore laissees dans le flux actif
- `CHANGELOG.md` partiellement stale

Ce qui a ete corrige :

- changelog
- guides setup/deploy/maintenance/testing
- docs frontend architecture/API/hooks/components
- README/index actifs
- liens et chemins d'archives

Ce qui a ete archive :

- 3 notes d'implementation closes
- 6 redirects widgets legacy

Ce qui reste a trancher manuellement :

- aucun arbitrage technique bloquant
- seulement la politique future de maintien ou non de certaines notes secondaires de pilotage (`CURSOR_MAX_EFFORT_BACKEND_PROTOCOL_2026-03-11.md`, `DEBAT_NEURO_INCLUSION_2026-03-30.md`) comme docs actives ou comme archives de contexte

