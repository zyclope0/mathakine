# Assets de documentation

> Updated: 23/03/2026

Ce dossier contient les artefacts non-Markdown utilises par la documentation.

## Structure actuelle

- `prototypes/` : prototypes et maquettes HTML non canoniques

### Regles prototypes

- un prototype ici n'est jamais la source de verite produit
- la priorisation reste dans `docs/02-FEATURES/ROADMAP_FONCTIONNALITES.md`
- si un prototype devient une vraie feature, la reference active doit migrer vers `02-FEATURES/` ou `04-FRONTEND/`

## Regles

- ne mettre ici que des artefacts documentaires legers: prototypes, schemas exportes, images de doc
- ne pas y stocker un workspace applicatif complet ou un projet Node avec `node_modules`
- les workspaces de generation de presentations doivent vivre hors `docs/` (ex: `presentations/`)
- si `images/`, `diagrams/` ou `icons/` sont crees plus tard, ils doivent correspondre a un usage reel et non a une structure theorique
