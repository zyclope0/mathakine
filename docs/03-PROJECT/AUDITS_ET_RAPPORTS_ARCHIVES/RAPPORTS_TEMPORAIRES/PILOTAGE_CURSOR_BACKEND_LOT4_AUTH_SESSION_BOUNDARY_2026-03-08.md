# Lot 4 - Auth session boundary

## Mission
- Assainir les flows `login`, `refresh`, `validate-token`, `current-user` et `logout` pour sortir la logique metier et DB de `server/handlers/auth_handlers.py`.
- Cible finale: les handlers auth de session deviennent des traducteurs HTTP avec cookies/presenter HTTP, tandis que l'orchestration vit dans un service dedie.

## Analyse actuelle
- `server/handlers/auth_handlers.py` melange:
  - parsing JSON
  - fallback refresh
  - acces DB
  - branches metier `login/refresh`
  - construction du payload utilisateur
- `app/services/auth_service.py` existe deja, il est bien teste, et doit etre reutilise au lieu d'etre contourne.
- Les helpers cookie sont une responsabilite HTTP valide et peuvent rester cote handler.

## Ce qui est mal place
- `_recover_refresh_token_fallback` dans le handler.
- Orchestration metier des endpoints `api_login`, `api_refresh_token`, `api_validate_token`, `api_get_current_user`, `api_logout`.
- Construction du payload utilisateur authentifie dans le handler au lieu d'un service ou mapper dedie.

## Ce qui est duplique
- Parsing et validation manuelle des payloads auth.
- Recuperation utilisateur/session et branches d'erreur metier dans le handler.
- Mapping des statuts d'authentification dans plusieurs endpoints proches.

## Decoupage cible
- Nouveau service: `app/services/auth_session_service.py`
  - responsabilite: login, refresh, validate-token, current-user, logout
- Repository eventuel: `app/repositories/user_session_repository.py`
  - a creer seulement si le nouveau service a encore du SQLAlchemy direct qui merite isolation
- Schemas a centraliser dans `app/schemas/user.py`
  - reutiliser `UserLogin`, `RefreshTokenRequest`, `TokenPayload`
  - ajouter `ValidateTokenRequest`
- `auth_handlers.py`
  - garde uniquement les cookies HTTP et les responses HTTP

## Fichiers a lire avant toute modification
- `server/handlers/auth_handlers.py`
- `app/services/auth_service.py`
- `app/schemas/user.py`
- `tests/api/test_auth_flow.py`
- `tests/integration/test_auth_cookies_only.py`
- `tests/integration/test_auth_no_fallback.py`
- `tests/unit/test_auth_service.py`

## Fichiers autorises
- `server/handlers/auth_handlers.py`
- `app/services/auth_service.py` (adaptation minimale si indispensable)
- `app/services/auth_session_service.py` (creation)
- `app/repositories/user_session_repository.py` (creation conditionnelle si necessaire)
- `app/schemas/user.py`
- `tests/api/test_auth_flow.py`
- `tests/integration/test_auth_cookies_only.py`
- `tests/integration/test_auth_no_fallback.py`
- `tests/unit/test_auth_service.py`

## Fichiers explicitement hors scope
- `verify_email`
- `resend_verification_email`
- `api_forgot_password`
- `api_reset_password`
- tout fichier `user_handlers.py`, `admin`, `challenge`, `badge`, `middleware`

## Actions precises a effectuer
1. Ajouter `ValidateTokenRequest` dans `app/schemas/user.py`.
2. Creer `app/services/auth_session_service.py` pour:
   - authentifier un user et preparer les donnees de login
   - valider un token d'access
   - rafraichir un access token avec fallback propre
   - retourner le payload utilisateur courant
   - gerer la logique de logout
3. Sortir `_recover_refresh_token_fallback` du handler vers le nouveau service.
4. Sortir la construction du payload utilisateur du handler vers un mapper/service dedie.
5. Refactorer `api_login`, `api_refresh_token`, `api_validate_token`, `api_get_current_user`, `api_logout` pour qu'ils deviennent purement HTTP.
6. Garder `_set_auth_cookie`, `_set_csrf_cookie`, `_build_login_response`, `_build_refresh_response` cote handler.
7. Conserver strictement:
   - noms de cookies
   - codes HTTP
   - cles JSON existantes
8. Introduire un repository de session uniquement si le service ne peut pas rester propre sans SQLAlchemy direct.

## Checks a lancer
- `pytest -q tests/api/test_auth_flow.py tests/integration/test_auth_cookies_only.py tests/integration/test_auth_no_fallback.py tests/unit/test_auth_service.py --maxfail=20`
- `black app/ server/ tests/ --check`

## Stop conditions
- Si le refactor change un nom de cookie, un status code ou une cle JSON existante.
- Si le lot derive vers `verify/resend/forgot/reset`.
- Si le nouveau service force un redesign du middleware auth.
- Si un bug produit auth est revele hors scope session: stop et rapport factuel.

## Definition of Done
- Les handlers auth de session ne portent plus la logique de fallback ou de validation metier.
- Les cookies restent geres cote HTTP uniquement.
- Les tests `cookies-only` et `no-fallback` restent verts.
- Aucune regression sur `login`, `refresh`, `validate-token`, `current-user`, `logout`.

## Format de compte-rendu final
1. Fichiers modifies
2. Ce qui a ete sorti des handlers auth
3. Nouveau decoupage service/repository/schema
4. Preuve que les cookies et payloads n'ont pas change
5. Checks executes et resultat
6. Risques residuels
7. Recommandation go / no-go pour le lot 5
