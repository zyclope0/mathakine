# F36 - Flash auth au refresh - Verification 2026-03-14

## Statut

Non reproduit. Aucun changement frontend applique.

## Scope verifie

- `frontend/hooks/useAuth.ts`
- `frontend/components/auth/ProtectedRoute.tsx`
- `frontend/app/api/auth/check-cookie/route.ts`
- `frontend/app/api/auth/sync-cookie/route.ts`
- `frontend/__tests__/unit/components/ProtectedRoute.test.tsx`

## Constats factuels

### 1. Bootstrap auth deja protege dans `useAuth`

`useAuth.ts` :

- recupere `["auth", "me"]` via React Query
- convertit explicitement un `401` en `null` sans lever une erreur parasite
- fixe directement `["auth", "me"]` au login avec `queryClient.setQueryData(["auth", "me"], data.user)`

Ce point evite deja le cas classique "redirect vers /login avant que le cache auth soit hydrate".

### 2. `ProtectedRoute` attend deja la fin du bootstrap

`ProtectedRoute.tsx` :

- n'autorise la redirection que quand `hasCheckedAuth` vaut `true`
- conserve un ecran de chargement tant que `isLoading && user === null`
- laisse immediatement passer le contenu si un `user` est deja en cache, meme pendant `isLoading`
- ne redirige vers `/login` qu'apres un timeout de securite de 1500 ms si l'etat reste indetermine

### 3. Une preuve unitaire existe deja

`ProtectedRoute.test.tsx` couvre deja :

- affichage immediat du contenu si `user` est deja en cache
- redirection vers `/login` seulement apres expiration du timeout de securite

Le scenario "cache utilisateur deja hydrate -> pas de redirect parasite" est donc deja verifie.

## Conclusion

Le symptome F36 n'est pas reproduit proprement sur l'etat actuel du code.

La lecture du code et le test unitaire existant montrent que :

- le bootstrap auth a deja ete stabilise
- la redirection prematuree est deja explicitement evitee

## Decision

- pas de modification frontend
- pas de changement backend
- garder F36 comme point d'observation UX seulement si un symptome reel reapparait

## Recommandation

Si un flash visuel reapparait plus tard, reouvrir un mini-lot uniquement avec :

1. reproduction video ou sequence exacte
2. verification de l'ordre `isLoading / user / isAuthenticated`
3. correction minimale dans `useAuth` ou `ProtectedRoute`
