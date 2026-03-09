# Versioning logique du refactor backend exercise/auth/user

## Portee
- Ce document trace le versioning interne de l'iteration backend centree sur `exercise`, `auth` et `user`.
- Il ne remplace pas la version produit publiee dans [`CHANGELOG.md`](../../CHANGELOG.md).
- L'iteration est maintenant cloturee. Les iterations backend suivantes devront ouvrir un nouveau document de versioning.

## Regles utilisees pendant l'iteration
- Format en cours d'iteration : `0.<lot>.<patch>`
- Version mineure : increment uniquement quand un lot est clos fonctionnellement et techniquement.
- Version patch : micro-lot de fermeture ou de durcissement dans un meme lot.
- Release candidate : format `0.<lot>.0-rc.N`, utilisee quand le code a atterri mais que le lot n'etait pas encore promouvable.
- Gate de promotion :
  - checks cibles au vert
  - aucun P1 ouvert sur le scope modifie
  - au moins un signal smoke end-user conforme quand le runtime etait touche
  - pour les jalons critiques :
    - `pytest -q --maxfail=20`
    - `black app/ server/ tests/ --check`

## Mapping final

| Version interne | Statut | Signification |
|-----------------|--------|---------------|
| `0.1.0` | Clos | Lot 1 : generation et persistance sorties des handlers |
| `0.1.1` | Clos | Lot 1.1 : repository autonome, resultat type, preuve adaptive restauree |
| `0.1.2` | Clos | Lot 1.2 : dependance `app -> server` retiree de la generation |
| `0.2.0` | Clos | Lot 2 : orchestration submit deplacee vers service/repository |
| `0.2.1` | Clos | Lot 2.1 : couverture metier de validation restauree |
| `0.2.2` | Clos | Lot 2.2 : savepoint/rollback sur `progress` |
| `0.3.0-rc.1` | Candidat | Lot 3 implemente, en attente de cloture des checks et tests |
| `0.3.0` | Clos | Lot 3 : boundary lecture/query/SSE `exercise` fermee |
| `0.4.0` | Clos | Lot 4 : boundary session auth fermee |
| `0.5.0` | Clos | Lot 5 : boundary recovery auth fermee |
| `0.5.1` | Clos | Lot 5.1 : zero drift retabli sur `resend-verification` |
| `0.5.2` | Clos | Lot 5.2 : revocation post-reset password validee apres correctif |
| `0.6.0` | Clos | Lot 6 : boundary `user` refactoree |
| `0.6.1` | Clos | Lot 6.1 : route export recablee, test API ajoute, reliquat handler ferme |
| `1.0.0` | Clos | Iteration complete `exercise/auth/user` avec gates finales vertes |

## Revue finale par domaine

### Exercise
- Lots 1 a 3 clos.
- Gains durables :
  - generation sortie du handler
  - soumission de reponse decoupee en controller/service/repository
  - query, interleaved et SSE prep sorties des handlers
- Point de vigilance : garder `server/exercise_generator*.py` comme couche de compatibilite, pas comme point d'evolution futur.

### Auth
- Lots 4 et 5 clos, puis micro-lots 5.1 et 5.2 fermes.
- Gains durables :
  - boundary session auth amincie
  - boundary recovery/verification amincie
  - anciens tokens rejetes apres reset password
  - autres sessions revoquees apres reset password
- Point de vigilance : si changement de mot de passe depuis le profil doit invalider aussi les anciens tokens, ce sera un lot de securite dedie.

### User
- Lot 6 clos avec fermeture 6.1.
- Gains durables :
  - `user_handlers.py` aminci
  - facade `user_application_service.py`
  - export RGPD recable et couvert par test API

## Gates de cloture
- `pytest -q --maxfail=20` : vert (`785 passed, 2 skipped`)
- `black app/ server/ tests/ --check` : vert
- Signaux end-user conformes sur :
  - login + refresh session
  - soumission exercice
  - reset password avec revocation effective au prochain controle protege

## Conclusion
- Version interne finale de cette iteration : `1.0.0`
- Cette version interne ne doit pas etre exposee telle quelle au produit.
- Cote release publique, la recommandation est de rester en `alpha` et de publier la stabilisation backend sous `3.1.0-alpha.7`.
