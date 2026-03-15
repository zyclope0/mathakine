# Lot C3 - Coverage Margin

> Date: 14/03/2026
> Iteration: C - Production Hardening
> Priorite: P2 CI hardening
> Statut: **terminé** — voir `PILOTAGE_CURSOR_PRODUCTION_HARDENING_C3_COVERAGE_MARGIN_REPORT_2026-03-14.md`

## 1. Mission

Augmenter la marge de securite du gate coverage CI sans mentir sur l'etat reel
de la suite.

## 2. Contexte actuel prouve

- gate CI backend actuel: `62`
- couverture observee locale: juste au-dessus de `62`
- marge faible, risque de rouge aleatoire ou de regression silencieuse

## 3. Faux positifs a eviter

- monter le seuil sans preuve
- corriger du runtime pour faire monter artificiellement la couverture
- traiter 20 modules a la fois

## 4. Risque production exact

Le risque n'est pas une panne prod directe.
Le risque est une faible force de la CI sur les regressions metier.

## 5. Decision d'architecture imposee

Approche:

- travailler d'abord par modules les moins couverts et les plus rentables
- relever le gate par paliers (`62 -> 65`, puis plus tard)
- si `65` n'est pas soutenable, documenter le vrai seuil

## 6. Ce qui est mal place

- gate coverage trop proche du score reel

## 7. Ce qui est duplique ou fragile

- modules critiques encore faiblement couverts
- risque qu'un petit bruit fasse tomber la CI

## 8. Decoupage cible

- tests seulement, sauf bug reel decouvert
- priorite aux modules <30 % a forte valeur

## 9. Fichiers a lire avant toute modification

- `.github/workflows/tests.yml`
- `pytest.ini`
- `coverage.xml`
- modules les moins couverts pertinents

## 10. Scope autorise

- tests
- CI coverage config
- doc testing si le seuil change

## 11. Scope interdit

- refactor runtime opportuniste
- modification de logique metier pour "faire monter le score"

## 12. Checks exacts

1. `git status --short`
2. `git diff --name-only`
3. commande coverage equivalente CI run 1
4. meme commande run 2
5. `black app/ server/ tests/ --check`

## 13. Exigences de validation

- prouver le seuil retenu
- prouver qu'il passe reellement deux fois
- lister les modules cibles du lot

## 14. Stop conditions

- si le seuil vise n'est pas soutenable sans chantier trop large
- dans ce cas: STOP, documenter le vrai seuil atteignable

## 15. Format de compte-rendu final

1. Fichiers modifies
2. Runtime touche ou non
3. Seuil coverage avant/apres
4. Modules cibles
5. Commande de preuve
6. Resultat run 1
7. Resultat run 2
8. Resultat black
9. Ce qui a ete prouve
10. Ce qui n'a pas ete prouve
11. Risques residuels
12. GO / NO-GO

