# Lot 5 - Auth recovery and verification

## Mission
- Assainir les flows `verify-email`, `resend-verification`, `forgot-password` et `reset-password` pour sortir les regles metier et l'orchestration email/token de `server/handlers/auth_handlers.py`.
- Cible finale: les handlers gardent les decorators et le mapping HTTP, tandis que la logique recovery/verification vit dans un service applicatif dedie.

## Analyse actuelle
- `verify_email`, `resend_verification_email`, `api_forgot_password`, `api_reset_password` portent encore:
  - branches metier
  - cooldown resend
  - envoi email
  - messages de securite
  - gestion d'erreurs metier
- Certains schemas existent deja (`ForgotPasswordRequest`), d'autres manquent.
- `auth_service.py` et `EmailService` existent et doivent rester les briques metier de base.

## Ce qui est mal place
- Cooldown resend dans le handler.
- Validation/reset workflow dans le handler.
- Orchestration email et token trop haute dans la pile.
- Trop de decisions metier et de logs sensibles au niveau HTTP.

## Ce qui est duplique
- Reponses de securite "ne pas reveler l'existence du compte".
- Branches `invalid`, `expired`, `already_verified`.
- Parsing d'entrees proches sur plusieurs routes recovery.

## Decoupage cible
- Nouveau service: `app/services/auth_recovery_service.py`
  - responsabilite: verify, resend, forgot, reset
- Schemas a ajouter dans `app/schemas/user.py`
  - `ResendVerificationRequest`
  - `ResetPasswordRequest`
- Le handler garde:
  - rate limiting
  - parsing HTTP
  - mapping exceptions -> reponses HTTP

## Fichiers a lire avant toute modification
- `server/handlers/auth_handlers.py`
- `app/services/auth_service.py`
- `app/services/email_service.py`
- `app/schemas/user.py`
- `tests/api/test_auth_flow.py`
- `tests/unit/test_auth_service.py`

## Fichiers autorises
- `server/handlers/auth_handlers.py`
- `app/services/auth_service.py` (adaptation minimale si necessaire)
- `app/services/email_service.py` (adaptation minimale si necessaire)
- `app/services/auth_recovery_service.py` (creation)
- `app/schemas/user.py`
- `tests/api/test_auth_flow.py`
- `tests/unit/test_auth_service.py`

## Fichiers explicitement hors scope
- `api_login`
- `api_refresh_token`
- `api_validate_token`
- `api_get_current_user`
- `api_logout`
- tout fichier `user_handlers.py`, `admin`, `challenge`, `badge`, `middleware`

## Actions precises a effectuer
1. Ajouter `ResendVerificationRequest` et `ResetPasswordRequest` dans `app/schemas/user.py`.
2. Creer `app/services/auth_recovery_service.py` pour:
   - verifier un token d'email
   - renvoyer un email de verification avec cooldown
   - declencher un forgot-password
   - executer un reset-password
3. Faire lever des exceptions metier explicites pour:
   - `invalid`
   - `expired`
   - `already_verified`
   - `cooldown`
   - `email_send_failed`
4. Reutiliser `auth_service.py` et `EmailService` sans dupliquer les regles.
5. Refactorer les handlers recovery pour qu'ils ne gardent que:
   - decorators de rate limiting
   - parsing/validation HTTP
   - appel service
   - mapping erreurs -> `api_error_response` ou `JSONResponse`
6. Reduire les logs contenant email/username si le lot touche ces branches.
7. Conserver les messages de securite existants et les codes HTTP exposes aux tests.

## Checks a lancer
- `pytest -q tests/api/test_auth_flow.py tests/unit/test_auth_service.py --maxfail=20`
- `black app/ server/ tests/ --check`

## Stop conditions
- Si le lot commence a toucher la session auth du lot 4.
- Si un changement oblige a modifier le middleware.
- Si un changement force a exposer plus d'information au client qu'aujourd'hui.
- Si un bug produit d'email/token est revele hors scope recovery: stop et rapport factuel.

## Definition of Done
- Les flows verify/resend/forgot/reset ne contiennent plus de regles metier dans le handler.
- Les schemas d'entree sont explicites et valides.
- Les messages de securite existants restent compatibles.
- Les tests auth cibles restent verts.

## Format de compte-rendu final
1. Fichiers modifies
2. Ce qui a ete sorti des handlers recovery
3. Nouveau decoupage service/schema
4. Preuve que les messages et statuts exposes restent compatibles
5. Checks executes et resultat
6. Risques residuels
7. Recommandation go / no-go pour le lot 6
