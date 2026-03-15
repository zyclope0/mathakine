# Lot C4 - Legacy API Truth

> Date: 14/03/2026
> Iteration: C - Production Hardening
> Priorite: P2 simplification runtime
> Statut: **terminé** — voir [PILOTAGE_CURSOR_PRODUCTION_HARDENING_C4_LEGACY_API_TRUTH_REPORT_2026-03-15.md](./PILOTAGE_CURSOR_PRODUCTION_HARDENING_C4_LEGACY_API_TRUTH_REPORT_2026-03-15.md)

## 1. Mission

Trancher honnetement le statut de `app/api/endpoints/*`.

## 2. Contexte actuel prouve

- le runtime actif est route via `server/app.py` et `server/routes/*`
- `app/api/endpoints/*` existe physiquement
- ce perimetre n'est pas la source de verite runtime actuelle

## 3. Faux positifs a eviter

- croire qu'un dossier present est necessairement actif
- rebrancher un legacy non teste pour "eviter de supprimer"

## 4. Risque production exact

Impact:

- surcharge cognitive
- faux perimetre runtime
- divergence documentaire possible

## 5. Decision d'architecture imposee

Le lot doit trancher:

- soit archiver / supprimer clairement le legacy non monte
- soit le reintegrer officiellement avec wiring et tests

Recommandation par defaut:
- retirer/archiver

## 6. Ce qui est mal place

- code endpoint legacy visible dans le depot sans role runtime clair

## 7. Ce qui est duplique ou fragile

- deux facons de raconter l'API du projet

## 8. Fichiers a lire avant toute modification

- `D:\\Mathakine\\server\\app.py`
- `D:\\Mathakine\\server\\routes\\`
- `D:\\Mathakine\\app\\api\\endpoints\\`
- `D:\\Mathakine\\README_TECH.md`
- `D:\\Mathakine\\docs\\02-FEATURES\\API_QUICK_REFERENCE.md`

## 9. Scope autorise

- `app/api/endpoints/*`
- doc technique associee
- imports morts strictement lies a ce perimetre

## 10. Scope interdit

- refactor des routes runtime reelles
- retour implicite a FastAPI sans lot dedie

## 11. Checks exacts

1. `git status --short`
2. `git diff --name-only`
3. preuve de wiring runtime
4. tests/doc checks necessaires selon option retenue

## 12. Exigences de validation

- prouver noir sur blanc le statut runtime reel
- prouver la decision "archiver/supprimer" ou "reintegrer"
- pas de GO si le perimetre reste ambigu

## 13. Stop conditions

- si le perimetre est en fait encore utilise par un flux non documente
- dans ce cas: STOP, documenter avant toute suppression

## 14. Format de compte-rendu final

1. Fichiers modifies
2. Runtime touche ou non
3. Statut reel de `app/api/endpoints/*`
4. Decision retenue
5. Preuve de wiring
6. Resultats de validation
7. Risques residuels
8. GO / NO-GO

