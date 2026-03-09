# Pilotage Cursor - Stabilisation Post-Features

> Date : 08/03/2026
> Usage : document maitre pour piloter `Composer 1.5` puis `Cursor`
> Statut : preparation de lots d'execution

---

## 1. Objectif

Ce dossier sert a piloter une passe de stabilisation apres un burst de
features, sans tomber dans un "gros refactor backend" a risque.

Principe :

- on traite les risques par lots fermes
- on ne melange pas plusieurs natures de changements dans le meme lot
- on n'autorise pas de refactor transverse tant que les lots precedents ne sont
  pas clos

---

## 2. Roles

### Composer 1.5

Usage recommande :

- cartographier le lot
- confirmer les fichiers reellement touches
- proposer un plan d'execution court
- signaler les risques de debordement de scope

Composer ne doit pas partir en refactor ou patch diffus.

### Cursor

Usage recommande :

- executer un seul lot a la fois
- rester strictement dans le perimetre defini
- produire les preuves de non-regression
- s'arreter si le scope reel depasse le lot

---

## 3. Ordre strict d'execution

1. [LOT 1 - Verite terrain et hygiene](./PILOTAGE_CURSOR_LOT1_VERITE_TERRAIN_2026-03-08.md)
2. [LOT 2 - Durcissement prod immediat](./PILOTAGE_CURSOR_LOT2_DURCISSEMENT_PROD_2026-03-08.md)
3. [LOT 1 bis - Verite API et documentation critique](./PILOTAGE_CURSOR_LOT1BIS_VERITE_API_DOC_2026-03-08.md)
4. [LOT 3 - Bouclier de non-regression](./PILOTAGE_CURSOR_LOT3_BOUCLIER_NON_REGRESSION_2026-03-08.md)
5. [LOT 4 - Extraction architecture ciblee](./PILOTAGE_CURSOR_LOT4_EXTRACTION_ARCHI_CIBLEE_2026-03-08.md)

Ne pas executer le lot suivant si le precedent n'est pas ferme.

---

## 4. Regles non negociables

- un lot = un objectif = une preuve = une sortie
- pas de "nettoyage opportuniste" hors scope
- pas de modification fonctionnelle cachee dans un lot d'hygiene
- pas de refactor structurel sans tests caracterisation avant
- pas de deux lots backend sensibles en parallele
- si un lot touche plus de 8 fichiers sans justification forte, il doit etre
  recoupe

---

## 5. Gate entre les lots

Avant de passer au lot suivant, on exige :

- diff lisible et coherent avec le lot
- checks du lot executes
- risque residuel note explicitement
- docs critiques mises a jour si contrat change

Gate minimum finale :

- `black app/ server/ tests/ --check`
- `pytest -q --maxfail=20`
- dans `frontend/` :
  - `npx tsc --noEmit`
  - `npm run lint`
  - `npm run i18n:validate`
  - `npx vitest run`

---

## 6. Strategie de risque

La bonne methode ici n'est pas :

- "on refactorise tout ce qui est moche"

La bonne methode est :

- on verrouille d'abord la verite terrain
- on ferme ensuite les risques prod immediats
- on traite ensuite le reliquat documentaire critique sans toucher au produit
- on ajoute les preuves de non-regression
- on n'ouvre qu'un seul hotspot architectural a la fois

---

## 7. Format de compte-rendu demande a Cursor

Pour chaque lot, Cursor doit retourner :

1. ce qui a ete change
2. ce qui a ete volontairement laisse hors scope
3. les checks executes
4. les risques residuels
5. la recommandation "go / no-go" pour le lot suivant

---

## 8. Decision de pilotage

Tant que le projet est en mode "post-features", il faut preferer :

- des lots courts
- des contrats explicites
- des preuves de non-regression

et eviter :

- les passes globales de "realignement backend"
- les grands refactors non bornes
- les changements simultanes code + doc + architecture + tests sans
  separation nette
