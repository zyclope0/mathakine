# Iteration C - Production Hardening

> Date: 14/03/2026
> Statut: actif
> Strategie: quality-first, max-effort
> Protocole: `CURSOR_MAX_EFFORT_BACKEND_PROTOCOL_2026-03-11.md`

## Objectif

Cette iteration ne vise plus prioritairement la structure interne du backend.
Elle vise a fermer les risques production reels encore ouverts apres les
iterations `Runtime Truth` et `Contracts / Hardening`.

Priorites:

1. retablir l'integrite du flux diagnostic
2. rendre la protection anti-abus robuste en multi-instance
3. augmenter la marge de securite CI autour de la couverture
4. trancher le legacy API non monte
5. solder les residus DRY / hygiene a faible blast radius

## Contexte actuel prouve

Baseline locale de reference au 14/03/2026:

- full suite hors faux gate: `823 passed, 2 skipped`
- `black app/ server/ tests/ --check` -> vert
- `isort app/ server/ --check-only --diff` -> vert
- gate coverage CI backend: `--cov-fail-under=62`

Etat du projet:

- iteration `Runtime Truth`: cloturee
- iteration `Contracts / Hardening`: cloturee
- quick wins post-refactor: clotures

## Faux positifs a eviter

- confondre faille d'integrite metier et simple dette d'architecture
- traiter le flash auth frontend sans reproduction reelle
- annoncer un durcissement "production" sur la seule base de tests verts
- melanger anti-abus distribue et refactor runtime general
- ouvrir un lot Redis, CI et auth dans la meme passe

## Lots de l'iteration C

### C1 - Diagnostic integrity
- `PILOTAGE_CURSOR_PRODUCTION_HARDENING_C1_DIAGNOSTIC_INTEGRITY_2026-03-14.md`

### C2 - Distributed rate limit
- `PILOTAGE_CURSOR_PRODUCTION_HARDENING_C2_DISTRIBUTED_RATE_LIMIT_2026-03-14.md`

### C3 - Coverage margin
- `PILOTAGE_CURSOR_PRODUCTION_HARDENING_C3_COVERAGE_MARGIN_2026-03-14.md`

### C4 - Legacy API truth
- `PILOTAGE_CURSOR_PRODUCTION_HARDENING_C4_LEGACY_API_TRUTH_2026-03-14.md`

### C5 - Hygiene and DRY finish
- `PILOTAGE_CURSOR_PRODUCTION_HARDENING_C5_HYGIENE_DRY_2026-03-14.md`

## Ordre d'execution impose

1. `C1`
2. `C2`
3. `C3`
4. `C4`
5. `C5`

Regle:
- ne pas ouvrir `C2` tant que `C1` n'est pas qualifie
- ne pas utiliser `C3` pour masquer un risque `C1` ou `C2`
- ne pas ouvrir `C4`/`C5` pour eviter un sujet prod plus important

## Gate d'iteration

Pour considerer l'iteration C terminee:

- le flux diagnostic ne depend plus d'un `correct_answer` librement falsifiable
- la protection anti-abus ne repose plus uniquement sur de la memoire mono-instance
- le gate coverage CI a gagne une marge soutenable au-dela de `62`
- le statut de `app/api/endpoints/*` est tranche honnetement
- les residus DRY immediats documentes sont soldes ou explicitement deferes

## Definition de "production hardening"

Cette iteration ne cherche pas:

- a refaire toute l'architecture
- a activer `mypy` strict global partout
- a supprimer tout le legacy historique du depot
- a "faire plus propre"

Elle cherche:

- a fermer les risques qui restent genants dans une posture production stricte
- a documenter exactement ce qui reste hors scope

## Compte-rendu attendu pour chaque lot

Chaque lot doit dire:

- quel risque production exact est traite
- quelle decision d'architecture a ete appliquee
- quels endpoints / flux reels sont touches
- quelle preuve a ete apportee
- ce qui reste hors scope

