# Pilotage Cursor - Lot 1 - Verite Terrain

> Date : 08/03/2026
> Type : hygiene et alignement
> Risque accepte : faible

---

## 1. Mission

Realigner la documentation critique et l'hygiene repo sur l'etat reel du code,
sans changer le comportement produit.

---

## 2. Objectif de sortie

En fin de lot :

- les docs critiques refletent la verite des routes et des changements recents
- les artefacts temporaires repo sont nettoyes ou explicitement ignores
- le warning frontend trivial est traite
- aucune logique backend metier n'a change

---

## 3. Fichiers a lire avant toute modification

- `README_TECH.md`
- `docs/INDEX.md`
- `docs/02-FEATURES/API_QUICK_REFERENCE.md`
- `docs/03-PROJECT/README.md`
- `server/routes/admin.py`
- `frontend/app/exercises/interleaved/page.tsx`
- `.gitignore`

---

## 4. Scope autorise

- mise a jour documentation critique
- nettoyage d'artefacts repo evidents
- correction d'un warning lint trivial
- alignement index docs / dates / liens / routes references

---

## 5. Scope interdit

- pas de changement de contrat API
- pas de refactor backend
- pas de changement metier dans les handlers
- pas de modification des tests sauf si indispensable pour un warning outillage

---

## 6. Constats de depart a considerer comme vrais jusqu'a preuve du contraire

- `docs/INDEX.md` est date du `07/03/2026` alors qu'il contient deja une entree
  `08/03/2026`
- `server/routes/admin.py` expose `GET /api/admin/feedback`
- `docs/02-FEATURES/API_QUICK_REFERENCE.md` ne reference pas cet endpoint
- le repo contient des artefacts `.gitignore.*` et `gitignore_export.txt`
- `frontend/app/exercises/interleaved/page.tsx` garde un etat `"error"` devenu
  probablement mort

---

## 7. Plan d'execution

1. Verifier la verite des routes backend reelles avant de toucher la doc.
2. Aligner `API_QUICK_REFERENCE` uniquement sur ce qui existe vraiment.
3. Mettre a jour l'en-tete de `docs/INDEX.md` et les entrees de navigation si
   necessaire.
4. Mettre a jour `docs/03-PROJECT/README.md` si de nouveaux documents de
   pilotage sont ajoutes.
5. Nettoyer les artefacts repo temporaires seulement s'ils sont bien des
   residus non voulus.
6. Traiter le warning lint trivial dans `frontend/app/exercises/interleaved/page.tsx`
   sans changer le flux utilisateur.

---

## 8. Verification attendue

- `git status --short`
- `git diff --name-only`
- dans `frontend/` : `npm run lint`
- si la page interleaved est touchee : `npx tsc --noEmit`

---

## 9. Stop conditions

Cursor doit s'arreter et ne pas continuer si :

- la doc et les routes ne racontent pas la meme histoire et qu'il faut trancher
  un comportement produit
- les fichiers `.gitignore.*` semblent etre un travail utilisateur volontaire
- le warning frontend cache en fait un vrai bug de logique

Dans ce cas, produire seulement :

- le constat
- les options
- le plus petit sous-lot suivant recommande

---

## 10. Definition of done

- docs critiques alignees
- index docs navigable
- plus de warning lint sur ce point
- aucun changement de comportement metier
- diff court et lisible

---

## 11. Compte-rendu demande

Cursor doit lister :

1. les fichiers doc/repo modifies
2. l'endpoint ou la date qui a ete realignee
3. les artefacts repo nettoyes ou conserves
4. les checks executes
5. tout doute reste ouvert

