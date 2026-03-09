# Pilotage Cursor - Lot 1 bis - Verite API et Documentation Critique

> Date : 08/03/2026
> Type : documentation critique
> Risque accepte : faible

---

## 1. Mission

Finaliser l'alignement de la documentation critique avec la surface HTTP active
et les protections d'auth reelles, sans toucher au code produit.

---

## 2. Objectif de sortie

En fin de lot :

- `API_QUICK_REFERENCE` couvre les endpoints actifs critiques manquants
- les statuts public/protege documentes refletent le middleware et les
  decorateurs reels
- `README_TECH.md` et `AUTH_FLOW.md` ne contiennent plus de contre-verite
  majeure sur la surface API ou l'auth
- l'artefact repo residuel `.gitignore.tmp` est traite ou explicitement laisse

---

## 3. Fichiers a lire avant toute modification

- `README_TECH.md`
- `docs/INDEX.md`
- `docs/02-FEATURES/API_QUICK_REFERENCE.md`
- `docs/02-FEATURES/AUTH_FLOW.md`
- `docs/03-PROJECT/README.md`
- `server/middleware.py`
- `server/routes/auth.py`
- `server/routes/badges.py`
- `server/routes/misc.py`
- `server/routes/admin.py`
- `server/handlers/challenge_handlers.py`
- `app/services/analytics_service.py`
- `frontend/hooks/useAdminEdTechAnalytics.ts`
- `frontend/app/admin/analytics/page.tsx`
- `.gitignore`

---

## 4. Scope autorise

- mise a jour de la documentation critique des routes actives
- correction des mentions auth/public/protege contradictoires avec le code
- correction de comptes approximatifs si une contre-verite est documentee
- nettoyage de `.gitignore.tmp` uniquement si c'est bien un artefact temporaire

---

## 5. Scope interdit

- pas de changement de logique backend ou frontend
- pas de changement de handler, middleware, decorateur ou route
- pas de fix UI/admin analytics dans ce lot
- pas de refactor doc global hors documents critiques cibles

---

## 6. Constats de depart a verifier

Points observes pendant l'audit :

- `docs/02-FEATURES/API_QUICK_REFERENCE.md` ne couvre pas encore plusieurs
  endpoints actifs :
  - `POST /api/auth/validate-token`
  - `POST /api/analytics/event`
  - `POST /api/feedback`
  - `GET /api/badges/rarity`
  - `PATCH /api/badges/pin`
  - `GET /api/admin/analytics/edtech`
  - `GET /api/admin/ai-stats`
  - `GET /api/admin/generation-metrics`
- `POST /api/chat` et `POST /api/chat/stream` sont documentes comme auth
  requis alors que la whitelist middleware les laisse publics
- `GET /api/challenges/{id}` est documente comme public alors que le handler
  est protege
- `README_TECH.md` parle encore d'environ `~85 routes` alors que la surface
  active est plus proche de `~95`
- `.gitignore.tmp` reste present a la racine du repo
- le backend analytics expose `interleaved`, mais l'admin frontend n'affiche
  encore que `exercise|challenge`

Ces constats doivent etre verifies dans le code avant patch.

---

## 7. Plan d'execution

1. Etablir la verite route par route depuis `server/routes/*.py` et
   `server/middleware.py`.
2. Aligner `API_QUICK_REFERENCE.md` sur les endpoints vraiment actifs et leur
   protection reelle.
3. Corriger dans `AUTH_FLOW.md` et `README_TECH.md` uniquement ce qui est
   contredit par le code.
4. Si `interleaved` est bien present cote backend analytics, le documenter
   sans corriger l'UI admin dans ce lot.
5. Traiter `.gitignore.tmp` seulement si son statut d'artefact temporaire est
   factuellement etabli.

---

## 8. Verification attendue

- `git status --short`
- `git diff --name-only`

Si un fichier frontend ou backend executable est modifie par exception, arreter
et signaler un debordement de scope.

---

## 9. Stop conditions

Cursor doit s'arreter si :

- la verite code implique un arbitrage produit et pas une simple correction doc
- deux sources code actives se contredisent et demandent une decision humaine
- `.gitignore.tmp` semble etre un fichier utilisateur volontaire
- la correction documentaire force en realite un changement d'interface admin
  ou de comportement auth

Dans ce cas, ne pas patcher large. Produire seulement :

- le constat factuel
- le risque
- le plus petit sous-lot suivant recommande

---

## 10. Definition of done

- docs critiques alignees sur la surface API active
- statuts auth/public/protege justes sur les endpoints touches
- aucune modification de code produit
- diff court, lisible, justifiable

---

## 11. Compte-rendu demande

Cursor doit retourner :

1. les documents modifies
2. les endpoints ajoutes ou corriges
3. les corrections de statut auth/public/protege
4. le sort de `.gitignore.tmp`
5. les risques residuels encore ouverts
