# Pilotage Cursor - Lot 3 - Bouclier Non-Regression

> Date : 08/03/2026
> Type : tests et caracterisation
> Risque accepte : faible

---

## 1. Mission

Ajouter ou renforcer les tests autour des flux recemment implementes et des
contrats durcis, avant toute extraction architecturale.

---

## 2. Objectif de sortie

En fin de lot :

- les chemins critiques des features recentes sont couverts par des tests
  cibles
- on a une preuve claire des contrats attendus
- aucun patch produit opportuniste n'est glisse dans un lot de tests

---

## 3. Fichiers a lire avant toute modification

- `frontend/lib/analytics/edtech.ts`
- `frontend/app/exercises/interleaved/page.tsx`
- `frontend/components/exercises/ExerciseSolver.tsx`
- `server/handlers/exercise_handlers.py`
- `tests/api/test_exercise_endpoints.py`
- `tests/unit/test_exercise_handlers.py`
- tests frontend analytics / interleaved

---

## 4. Scope autorise

- ajout ou renforcement de tests backend/frontend
- petites corrections de fixture ou de setup de test
- documentation des contrats verifies dans les tests

---

## 5. Scope interdit

- pas de refactor code produit en meme temps
- pas de correction metier silencieuse "au passage"
- pas d'ouverture d'un nouveau lot technique dans ce lot

Si un bug produit est decouvert, il faut l'isoler et proposer un lot de patch
dedie.

---

## 6. Matrice minimale a couvrir

### Backend

- `POST /api/exercises/generate` avec `save=true` :
  - succes avec `id`
  - echec de persistance => erreur explicite
- resolution adaptive :
  - utilisateur auth + `adaptive=true` + pas de `age_group` force
  - fallback propre si resolution impossible

### Frontend

- session `interleaved` :
  - un seul `first_attempt` par session
  - pas de double emission sur exercice suivant
- branche d'erreur :
  - erreur de generation initiale
  - erreur sur "exercice suivant" sans perte de session

---

## 7. Plan d'execution

1. Inventorier les tests existants avant d'en ajouter.
2. Completer d'abord les trous les plus proches du risque produit.
3. Ne modifier le code produit que si un test impossible a ecrire revele un
   vrai probleme de testabilite mineur.
4. Si un vrai bug fonctionnel apparait, arreter le lot et le remonter
   explicitement.

---

## 8. Verification attendue

- `pytest -q tests/api/test_exercise_endpoints.py tests/unit/test_exercise_handlers.py tests/unit/test_adaptive_difficulty_service.py --maxfail=20`
- dans `frontend/` :
  - `npx vitest run`
  - `npx tsc --noEmit`

Si le diff test devient large, terminer aussi par :

- `pytest -q --maxfail=20`

---

## 9. Stop conditions

Cursor doit s'arreter si :

- un test revele un bug produit qui exige un lot de patch dedie
- le lot commence a modifier plusieurs services de prod
- il faut redefinir un contrat fonctionnel non tranche

---

## 10. Definition of done

- tests cibles ajoutes ou durcis
- matrice des chemins critiques couverte
- aucune correction produit non demandee glissee dans ce lot
- checks cibles verts

---

## 11. Compte-rendu demande

Cursor doit lister :

1. les contrats verifies
2. les nouveaux tests ajoutes
3. les zones encore non couvertes
4. les checks executes
5. les bugs potentiels detectes mais non patches
