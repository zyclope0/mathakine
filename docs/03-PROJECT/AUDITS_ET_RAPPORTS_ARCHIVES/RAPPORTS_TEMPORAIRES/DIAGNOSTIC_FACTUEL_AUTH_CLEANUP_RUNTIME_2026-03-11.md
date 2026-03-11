# Diagnostic factuel auth / cleanup / runtime

Date : 11/03/2026  
Statut : actif  
Portee : preuves de code et hypotheses strictement bornees

## Objet

Ce document fixe ce qui est prouve dans le code sur le bloc de stabilisation `admin/auth`, et separe explicitement :

1. les problemes factuellement visibles dans le code
2. les hypotheses encore a prouver
3. les faux positifs a eviter

Le but n'est pas de deduire une cause depuis un test rouge.  
Le but est d'identifier ce qui est objectivement risquant ou incoherent dans le code courant.

## Constats prouves dans le code

### 1. Les tests d'integration auth n'utilisent pas tous le namespace reserve `fixture_auth_*`

Faits :

- Dans [tests/conftest.py](D:/Mathakine/tests/conftest.py), `_create_authenticated_client()` cree maintenant des users:
  - `fixture_auth_{role}_{unique_id}`
  - voir lignes 289 a 292
- Dans le meme fichier, cette fixture a maintenant un teardown explicite par `id`
  - voir lignes 342 a 357
- Dans [tests/utils/test_data_cleanup.py](D:/Mathakine/tests/utils/test_data_cleanup.py), `fixture_auth_%` a bien ete retire des patterns de cleanup globaux
  - voir ligne 65

Mais :

- Dans [tests/integration/test_auth_cookies_only.py](D:/Mathakine/tests/integration/test_auth_cookies_only.py), les users sont encore crees avec :
  - `test_cookies_{unique_id}`
  - voir ligne 15
- Dans [tests/integration/test_auth_no_fallback.py](D:/Mathakine/tests/integration/test_auth_no_fallback.py), les users sont encore crees avec :
  - `test_no_fallback_{unique_id}`
  - voir ligne 39
- Dans [tests/utils/test_data_cleanup.py](D:/Mathakine/tests/utils/test_data_cleanup.py), le cleanup global capture toujours :
  - `test_%`
  - `auth_test_%`
  - voir lignes 43 et 64

Conclusion factuelle :

- la correction `fixture_auth_*` est reelle
- mais elle est partielle
- toute surface de test qui cree encore des users `test_%` ou `auth_test_%` reste compatible avec une suppression par cleanup global

### 2. `authenticate_user_with_session()` cree une session sans revalider l'existence du user juste avant l'insert

Faits :

- Dans [app/services/auth_service.py](D:/Mathakine/app/services/auth_service.py), `authenticate_user_with_session()` est defini ligne 540
- Il fait :
  - `authenticate_user(...)`
  - `create_user_token(user)`
  - `create_session(db, user.id, ...)`
  - `db.commit()`
  - voir lignes 540 a 561
- `create_session()` est defini ligne 427
- Cette fonction insere directement un `UserSession` avec `user_id=user_id`
  - voir lignes 427 a 451

Conclusion factuelle :

- il n'existe pas de re-fetch explicite du `User` juste avant l'insertion `UserSession`
- si `user.id` n'est plus visible ou valide dans cette session au moment du `create_session()`, la FK `user_sessions.user_id -> users.id` peut casser

Ce constat ne prouve pas encore pourquoi le user disparait.  
Il prouve une fragilite runtime concrete du flow login/session.

### 3. `reset_password_with_token()` supprime les sessions via la relation ORM, puis refresh le user

Faits :

- Dans [app/services/auth_service.py](D:/Mathakine/app/services/auth_service.py), `reset_password_with_token()` est defini ligne 483
- Il:
  - recharge l'utilisateur par `password_reset_token`
  - met a jour mot de passe / token / `password_changed_at`
  - supprime toutes les sessions via:
    - `for s in list(user.user_sessions): db.delete(s)`
    - voir ligne 511
  - flush/commit
  - `db.refresh(user)`

Conclusion factuelle :

- le code courant n'utilise plus le bulk delete de sessions qui avait deja cause des effets de bord
- le chemin actuel est plus sain qu'avant
- si un `StaleDataError` reapparait, il faut maintenant chercher soit :
  - un user stale / supprime
  - soit un probleme de session/visibilite DB
  - pas un bulk delete de `UserSession`

### 4. Le fallback `safe_delete()` peut bypasser la suppression ORM normale

Faits :

- Dans [app/db/transaction.py](D:/Mathakine/app/db/transaction.py), `safe_delete()` est defini ligne 94
- En cas d'echec du commit apres `db_session.delete(obj)`, il existe un fallback SQL brut :
  - `DELETE FROM {table_name} WHERE id = :id`
  - voir ligne 160

Conclusion factuelle :

- si ce chemin est pris pour un `User`, on ne s'appuie plus sur les cascades ORM Python mais uniquement sur les contraintes/cascades DB reelles
- c'est une vraie zone de risque pour des FKs comme :
  - `user_achievements_user_id_fkey`
  - `user_sessions_user_id_fkey`

Ce document ne prouve pas que ce fallback est declenche actuellement.  
Il prouve que ce chemin de code existe et qu'il est objectivement risquant pour `User`.

### 5. `server/auth.py` retourne bien `None` si le user n'est plus trouvable en base

Faits :

- Dans [server/auth.py](D:/Mathakine/server/auth.py), `get_current_user()` est defini ligne 21
- Le token est decode, puis le user est relu en base via `get_user_by_username`
  - voir ligne 75
- si le user n'existe plus, la fonction retourne `None`
  - voir lignes 78 et 83

Conclusion factuelle :

- un `401` sur route protegee peut tres bien etre cause par un token encore present mais un user absent en base
- ce comportement est coherent avec les symptomes observes pendant les iterations precedentes

## Constats de fragilite tests, egalement prouves dans le code

### 6. Tous les tests challenge ne sont pas completement deterministes

Faits :

- Dans [tests/api/test_challenge_endpoints.py](D:/Mathakine/tests/api/test_challenge_endpoints.py), plusieurs tests utilisent encore une selection via la liste `/api/challenges` :
  - ligne 28 : `challenge_id = challenges[0]["id"]`
  - ligne 91 : meme pattern
  - ligne 174 : meme pattern
- Les deux tests precedemment rouges ont ete corriges pour utiliser `challenge_with_hints_id` :
  - `test_challenge_attempt_correct` lignes 49 a 59
  - `test_challenge_with_centralized_fixtures` lignes 292 a 305

Conclusion factuelle :

- la correction recente des 2 tests est bonne
- mais le fichier conserve d'autres points potentiellement sensibles a l'ordre / au contenu de la liste
- cela reste une dette de stabilite de test, pas une preuve d'un bug runtime challenge

## Faux positifs a eviter

### A. Accuser le read path admin

Je ne vois pas de bug de wiring evident dans :

- [app/services/admin_read_service.py](D:/Mathakine/app/services/admin_read_service.py)
- [server/handlers/analytics_handlers.py](D:/Mathakine/server/handlers/analytics_handlers.py)
- [server/handlers/feedback_handlers.py](D:/Mathakine/server/handlers/feedback_handlers.py)

Ces fichiers ne sont pas la meilleure cible pour les symptomes auth/session.

### B. Dire que la correction `fixture_auth_*` a tout regle

Faux.

Elle a corrige :

- `_create_authenticated_client()`

Elle n'a pas corrige :

- `test_auth_cookies_only.py`
- `test_auth_no_fallback.py`

tant que ces tests utilisent encore `test_%`.

## Hypotheses fortes mais pas encore prouvees

### H1. Les users de certains tests d'integration auth sont encore supprimables par cleanup global

Tres probable, car :

- ils utilisent encore `test_%`
- le cleanup capture `test_%`

Mais il faut encore prouver dans un run instrumente :

- a quel moment exact le user disparait
- avant ou apres login
- avant ou apres creation de session

### H2. Il existe un second probleme auth runtime distinct du cleanup

Tres probable si, apres sortie complete des tests auth du namespace `test_%`, il reste encore :

- des `500` login
- ou des FK `user_sessions.user_id`

Dans ce cas, la cible suivante est :

- [app/services/auth_service.py](D:/Mathakine/app/services/auth_service.py)
  - `authenticate_user_with_session()`
  - `create_session()`
  - eventuellement `reset_password_with_token()`

## Correctifs minimaux recommandes

### Priorite 1

Sortir **toutes** les fixtures auth d'integration du namespace `test_%` :

- `test_auth_cookies_only.py`
- `test_auth_no_fallback.py`

Vers un namespace reserve, par exemple :

- `fixture_auth_cookie_*`
- `fixture_auth_nofallback_*`

Et verifier qu'aucun pattern de cleanup ne les capture.

### Priorite 2

Apres cela seulement, revalider :

1. `tests/integration/test_auth_cookies_only.py`
2. `tests/integration/test_auth_no_fallback.py`
3. `tests/api/test_auth_flow.py`

Si ces tests restent rouges, ouvrir alors un diagnostic runtime sur `auth_service.py`.

### Priorite 3

Auditer si `UserService.delete_user()` peut passer par `TransactionManager.safe_delete()` sur `User`.  
Si oui, traiter ce chemin comme une dette serieuse, car le fallback SQL brut est objectivement risquant.

## Ce que ce document permet d'affirmer

On peut affirmer avec certitude :

1. qu'une partie des tests auth a ete correctement sortie du cleanup global
2. qu'une autre partie des tests auth utilise encore un namespace capture par le cleanup
3. que `authenticate_user_with_session()` est fragile au moment de `create_session()`
4. que `safe_delete()` contient un fallback SQL brut objectivement risquant pour `User`

On ne peut pas encore affirmer avec certitude :

1. que tous les `500` login viennent uniquement du cleanup
2. que `safe_delete()` est effectivement declenche sur le chemin utilisateur actuel
3. que tout symptome challenge recent vient du runtime et non de tests encore fragiles

## Decision de travail recommandee

Ne plus traiter ce sujet par symptomes.

Ordre recommande :

1. finir la sortie des tests auth du namespace `test_%`
2. rerun auth cible
3. seulement si auth reste rouge, diagnostiquer `auth_service.py`
4. traiter separement la dette de stabilite des tests challenge restants

