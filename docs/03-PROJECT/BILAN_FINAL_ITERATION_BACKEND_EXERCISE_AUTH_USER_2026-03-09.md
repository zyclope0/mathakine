# Bilan final - Iteration backend exercise auth user - 2026-03-09

## Verdict
- Iteration backend cloturee
- Version interne finale : `1.0.0`
- Version produit recommandee : `3.1.0-alpha.7`

## Pourquoi rester en alpha
- Le backend sur le perimetre `exercise/auth/user` est maintenant defendable et stable.
- En revanche, le produit dans son ensemble continue d'evoluer vite :
  - backlog fonctionnel encore actif
  - reliquats UX non bloquants
  - prochaine iteration backend encore a ouvrir sur d'autres domaines
- Conclusion : sortir `alpha` maintenant n'apporterait pas de clarte supplementaire.

## Ce qui a ete ferme

### Exercise
- generation et persistance sorties des handlers
- soumission de reponse decoupee en controller/service/repository
- query, interleaved et SSE prep sorties des handlers

### Auth
- boundaries session et recovery separees
- zero drift retabli sur `resend-verification`
- reset password :
  - anciens access tokens rejetes
  - anciens refresh tokens rejetes
  - autres sessions revoquees
- changement de mot de passe depuis le profil :
  - `password_changed_at` aligne
  - anciennes sessions revoquees

### User
- `user_handlers.py` aminci
- facade `user_application_service.py`
- export RGPD recable sur le bon handler HTTP et couvert par test API

## Micro-lots marquants
- `1.2` : suppression de la dependance `app -> server` dans la generation
- `2.2` : durcissement transactionnel de `progress`
- `3.2` : correction du test obsolete qui bloquait la promotion du lot 3
- `5.2-fix` : correction des regressions critiques du mecanisme de revocation
- `6.1` : correction du bug latent `/api/users/me/export`

## Gates a la cloture
- `pytest -q --maxfail=20` -> `785 passed, 2 skipped`
- `black app/ server/ tests/ --check` -> vert

## Changement visible cote produit
- meilleure fiabilite sur les exercices
- meilleure stabilite de login / refresh / reset password
- anciennes sessions invalidees apres reset password
- export des donnees personnelles fonctionnel

## Reliquats non bloquants
- `F36` : flash auth au refresh cote frontend
- prochaine iteration backend a ouvrir sur `challenge`, `admin`, `badge`

## Recommandation pour la suite
- Commit / push possibles si les fichiers non suivis de cette iteration sont bien ajoutes.
- Prochaine iteration backend recommandee : `challenge`, `admin`, `badge`.

