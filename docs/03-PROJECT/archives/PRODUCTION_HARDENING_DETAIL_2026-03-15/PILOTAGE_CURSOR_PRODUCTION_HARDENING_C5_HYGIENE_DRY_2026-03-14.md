# Lot C5 - Hygiene and DRY Finish

> Date: 14/03/2026
> Iteration: C - Production Hardening
> Priorite: P3 hygiene
> Statut: **terminé** — voir [PILOTAGE_CURSOR_PRODUCTION_HARDENING_C5_HYGIENE_DRY_REPORT_2026-03-15.md](./PILOTAGE_CURSOR_PRODUCTION_HARDENING_C5_HYGIENE_DRY_REPORT_2026-03-15.md)

## 1. Mission

Solder les residus DRY/hygiene les plus simples et les plus defendables.

## 2. Contexte actuel prouve

Exemples de residus cites:

- double bloc d'import `AsyncOpenAI` dans `server/handlers/chat_handlers.py`
- reliquats TODO H9 sur enum/pagination/formatting

## 3. Faux positifs a eviter

- transformer un lot hygiene en refactor de domaine
- melanger de la simplification utile avec du nettoyage cosmetique diffus

## 4. Risque production exact

Risque faible:

- dette de maintenance
- divergence de comportement future

## 5. Decision d'architecture imposee

Le lot doit rester:

- petit
- causal
- sans changement produit visible

## 6. Ce qui est mal place

- duplication immediate
- TODO de wiring simple laisses trop longtemps

## 7. Ce qui est duplique ou fragile

- imports dupliques
- formats de mapping encore heterogenes si H9 confirme

## 8. Fichiers a lire avant toute modification

- `D:\\Mathakine\\server\\handlers\\chat_handlers.py`
- `D:\\Mathakine\\app\\utils\\enum_mapping.py`
- `D:\\Mathakine\\app\\utils\\response_formatters.py`

## 9. Scope autorise

- nettoyages DRY immediats
- TODO H9 si le scope reste petit

## 10. Scope interdit

- gros refactor chat
- refonte globale des handlers
- modifications produit visibles

## 11. Checks exacts

1. `git status --short`
2. `git diff --name-only`
3. batterie ciblee selon fichiers touches
4. relancer la meme batterie
5. full suite si runtime backend reellement touche
6. `black app/ server/ tests/ --check`
7. `isort app/ server/ --check-only --diff`

## 12. Exigences de validation

- lister les duplications effectivement retirees
- prouver qu'aucun scope large n'a ete ouvert

## 13. Stop conditions

- si un "petit nettoyage" force un refactor de domaine
- dans ce cas: STOP, deferer a une iteration dediee

## 14. Format de compte-rendu final

1. Fichiers modifies
2. Fichiers runtime modifies
3. Fichiers de test modifies
4. Residus hygiene / DRY traites
5. Ce qui a ete prouve
6. Ce qui n'a pas ete prouve
7. Resultat run 1
8. Resultat run 2
9. Resultat full suite
10. Resultat black
11. Resultat isort
12. Risques residuels
13. GO / NO-GO

