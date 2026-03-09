# Pilotage Cursor - Lot 2 - Durcissement Prod Immediat

> Date : 08/03/2026
> Type : reduction de risque prod
> Risque accepte : faible a moyen

---

## 1. Mission

Fermer les risques de production immediats identifies par l'audit, sans ouvrir
de refactor structurel.

---

## 2. Objectif de sortie

En fin de lot :

- aucun log auth/session non indispensable n'est expose
- les traces debug front evidentes ne restent pas en prod
- le comportement fonctionnel d'auth et de navigation reste identique

---

## 3. Fichiers a lire avant toute modification

- `docs/03-PROJECT/POLITIQUE_REDACTION_LOGS_PII.md`
- `server/handlers/auth_handlers.py`
- `server/auth.py`
- `frontend/components/auth/ProtectedRoute.tsx`
- tests auth associes

---

## 4. Scope autorise

- reduction ou suppression de logs trop bavards
- redaction de metadonnees sensibles
- suppression de `console.log` de production
- ajustements mineurs de tests si les logs ou branches de rendu sont affectes

---

## 5. Scope interdit

- pas de changement du flux auth
- pas de changement de schema cookie/token
- pas de rework du refresh flow
- pas de refactor transverse du middleware ou de toute la couche auth

---

## 6. Constats de depart

Points deja observes :

- `server/handlers/auth_handlers.py` logge les cookies presents et des
  metadonnees du refresh
- `frontend/components/auth/ProtectedRoute.tsx` contient plusieurs
  `console.log` qui ressemblent a des traces de debug de prod

Ces constats doivent etre verifies dans le code avant modification.

---

## 7. Plan d'execution

1. Cartographier les logs auth/session existants.
2. Classer chaque log en trois categories :
   - utile et conserve
   - utile mais a redacteur
   - inutile et a supprimer
3. Supprimer en priorite les logs qui revelent :
   - liste de cookies
   - provenance body/cookie du refresh
   - longueur ou metadata du token
4. Nettoyer les `console.log` de `ProtectedRoute` si leur seule valeur est le
   debug.
5. Ne pas toucher a la logique de controle d'acces sauf si un bug direct est
   mis au jour par le nettoyage.

---

## 8. Verification attendue

- `pytest -q tests/api/test_auth_flow.py tests/integration/test_auth_cookies_only.py tests/integration/test_auth_no_fallback.py --maxfail=20`
- dans `frontend/` :
  - `npx tsc --noEmit`
  - `npm run lint`

---

## 9. Stop conditions

Cursor doit s'arreter si :

- la suppression des logs revele une dependance implicite en debug
- le nettoyage de `ProtectedRoute` force a redefinir le comportement produit
- un changement de logique auth serait necessaire pour finir le lot

Dans ce cas, ne pas patcher large. Produire un sous-lot dedie.

---

## 10. Definition of done

- aucun log auth inutilement sensible n'est conserve
- aucun `console.log` de debug de prod ne reste sur la route protegee
- tests auth cibles verts
- frontend typecheck + lint verts sur les fichiers touches

---

## 11. Compte-rendu demande

Cursor doit retourner :

1. les logs supprimes ou redacts
2. la preuve que le flux auth n'a pas change
3. les checks executes
4. les risques residuels encore presents

