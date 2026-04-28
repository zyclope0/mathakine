# References - Mathakine

> Point d'entree du dossier `00-REFERENCE`
> Updated: 28/04/2026

## Role

Ce dossier contient les references transversales vivantes : architecture, gouvernance runtime et demarrage global.

## Lire d'abord

1. [ARCHITECTURE.md](ARCHITECTURE.md)
2. [DIFFICULTY_AND_RANKS_MANIFEST.md](DIFFICULTY_AND_RANKS_MANIFEST.md)
3. [AI_MODEL_GOVERNANCE.md](AI_MODEL_GOVERNANCE.md)
4. [GETTING_STARTED.md](GETTING_STARTED.md)
5. [DATA_MODEL.md](DATA_MODEL.md) — ERD 22 entités ORM (tables, colonnes clés, relations)
6. [USER_ROLE_NOMENCLATURE.md](USER_ROLE_NOMENCLATURE.md) — rôles canoniques, mapping legacy, boundary apprenant/adulte

## Architecture Decision Records (ADR)

Les ADRs vivent dans [`docs/05-ADR/`](../05-ADR/README.md).

## Regle

- si une reference devient la source de verite multi-workloads ou multi-modules, elle doit vivre ici
- chaque claim technique stable doit pointer vers le code actif
- toute decision architecturale non reversible doit avoir un ADR dans ce dossier
