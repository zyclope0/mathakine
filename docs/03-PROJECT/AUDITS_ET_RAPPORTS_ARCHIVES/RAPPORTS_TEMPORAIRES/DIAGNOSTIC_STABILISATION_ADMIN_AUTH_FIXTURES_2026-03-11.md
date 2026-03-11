# Diagnostic de stabilisation admin auth fixtures - 2026-03-11

## Statut
- Document de cadrage de rupture.
- Ce document suspend la logique de micro-lots `LOT 4.x` orientee symptomes.
- Il fixe la lecture actuelle, les faux positifs a eviter, et la strategie correcte pour reprendre le chantier.

## Contexte
- Iteration backend active: `challenge/admin/badge`.
- Etat des lots:
  - `LOT 1 challenge query`: acceptable.
  - `LOT 2 challenge attempt`: acceptable.
  - `LOT 3 challenge AI stream`: acceptable.
  - `LOT 4 admin read`: non cloturable a ce stade.
- Probleme constate: les reruns admin/auth ne sont pas stables, alors que le code du read path admin parait coherent.

## Conclusion executrice
- Le read path admin n'est probablement pas la cause racine principale.
- Le blocage actuel releve d'abord de la stabilisation des fixtures auth/admin, du cleanup de test, puis possiblement d'un second probleme runtime auth distinct.
- Tant que ce diagnostic n'est pas traite, il ne faut plus ouvrir `LOT 5`.

## Ce qui a ete prouve factuellement

### 1. Le code runtime du read path admin est coherent
Les fichiers modifies au `LOT 4` ne montrent pas de bug de wiring evident:
- `app/services/admin_read_service.py`
- `server/handlers/analytics_handlers.py`
- `server/handlers/feedback_handlers.py`

Les routes runtime touchees par ce refactor restent:
- `GET /api/admin/analytics/edtech`
- `GET /api/admin/feedback`

Le probleme ne doit donc plus etre formule comme "admin read a casse l'admin" sans preuve supplementaire.

### 2. Le fix `LOT 4.5` a recree la collision qu'il etait cense corriger
Dans `tests/conftest.py`, `_create_authenticated_client()` a ete change pour creer:
- `fixture_auth_padawan_<id>`
- `fixture_auth_archiviste_<id>`
- plus generalement `fixture_auth_{role}_{id}`

Mais dans `tests/utils/test_data_cleanup.py`, `TEST_PATTERNS["usernames"]` contient aussi:
- `fixture_auth_%`

Donc:
- les fixture users auth/admin ont change de namespace
- mais ce namespace reste capture par le cleanup global

Le correctif est donc logiquement invalide:
- la collision n'a pas ete supprimee
- elle a seulement ete deplacee

### 3. Les fixture users disparaissent encore avant certaines requetes HTTP
Les assertions de diagnostic ajoutees dans:
- `tests/api/test_admin_analytics.py`

ont deja prouve, sur des runs rouges, que:
- le `padawan` de fixture est absent en base juste avant `POST /api/analytics/event`
- parfois l'`archiviste` aussi

Cela explique directement une partie des `401`:
- `server/auth.py` decode le token
- relit l'utilisateur en base
- renvoie `None` si l'utilisateur n'existe plus

Donc:
- token encore present
- utilisateur absent en base
- resultat = `401`

### 4. Il existe aussi un second signal auth/runtime distinct
La suite:
- `tests/api/test_auth_flow.py`

reste capable d'echouer sur:
- `test_reset_password_full_flow`
- `test_reset_password_revokes_old_tokens`
- `test_refresh_token`

Symptomes observables:
- `500` au login apres creation/reset utilisateur
- violation FK `user_sessions_user_id_fkey`
- `user_id` absent de `users` au moment de l'insertion dans `user_sessions`

Le blocage n'est donc pas entierement reductible au read path admin.

## Faux positifs a eviter

### Faux positif 1: accuser le read path admin
Il ne faut plus demander a Cursor de retoucher en priorite:
- `app/services/admin_read_service.py`
- `server/handlers/analytics_handlers.py`
- `server/handlers/feedback_handlers.py`

Sans preuve forte, ce serait travailler sur le mauvais symptome.

### Faux positif 2: croire que le pre-yield cleanup explique tout
Le fait d'avoir ajoute un cleanup pre-yield dans `tests/conftest.py` n'est pas une explication causale suffisante.

Sur certains tests admin, l'ordre de setup montre:
- cleanup pre-yield
- puis creation des clients authentifies du test courant

Donc le simple ajout d'un pre-yield cleanup ne demontre pas pourquoi les users de fixture disparaissent ensuite.

### Faux positif 3: croire que `admin_audit_logs` est toute la racine
La nullification preventive de `admin_audit_logs.admin_user_id` dans le cleanup est raisonnable.
Mais:
- elle n'explique pas la disparition des fixture users avant requete
- elle ne suffit pas a expliquer les erreurs `user_sessions_user_id_fkey`

`admin_audit_logs` est un symptome ou un facteur aggravant possible, pas une preuve de racine unique.

## Lecture correcte du probleme

### Probleme A - collision fixtures/cleanup
Les fixtures auth/admin vivent encore dans un namespace capture par le cleanup global.

Effets plausibles:
- `401` sur admin/auth
- utilisateurs de fixture absents en base avant requete
- instability d'un rerun a l'autre

### Probleme B - possible bug runtime auth distinct
Si, apres suppression de la collision fixtures/cleanup, l'auth cible reste rouge, alors il faudra investiguer un second sujet dans:
- `app/services/auth_service.py`
  - `authenticate_user_with_session(...)`
  - `create_session(...)`
  - `reset_password_with_token(...)`

Il ne faut pas melanger ces deux problemes dans le meme patch sans preuve.

## Strategie de rupture recommandee

### Phase 1 - sortir completement les fixtures auth/admin du cleanup global
Objectif:
- rendre impossible la suppression des fixture users auth/admin par les patterns generiques

Decision:
- garder `fixture_auth_*` et `fixture_auth_flow_*` comme namespace reserve
- retirer `fixture_auth_%` des patterns generiques de `tests/utils/test_data_cleanup.py`

Raison:
- un namespace reserve n'a aucun sens s'il reste dans le cleanup global

### Phase 2 - donner un teardown explicite aux fixtures auth/admin
Objectif:
- ne plus compter sur `TEST_PATTERNS` pour supprimer les users de fixtures actives

Decision:
- `_create_authenticated_client()` doit supprimer explicitement son user par `id` en fin de fixture
- les fixtures auth flow qui creent des users specifiques doivent faire de meme

Raison:
- le cycle de vie d'une fixture active ne doit pas dependre d'un balayage global par pattern

### Phase 3 - garder le cleanup global comme balai de securite
Objectif:
- nettoyer les residus
- pas gerer le cycle de vie principal des fixtures auth/admin

Decision:
- `TestDataManager.cleanup_test_data()` reste utile pour les donnees jetables generiques
- mais il ne doit plus etre l'outil principal de destruction des fixtures auth/admin vivantes

### Phase 4 - revalider
Relancer dans cet ordre:
1. batterie admin/feedback run 1
2. batterie admin/feedback run 2
3. suite auth ciblee
4. full suite
5. `black app/ server/ tests/ --check`

### Phase 5 - seulement si auth reste rouge
Ouvrir alors un diagnostic runtime dedie sur:
- `app/services/auth_service.py`

Avec verification factuelle de:
- l'existence du user juste avant `create_session(...)`
- l'existence du user juste apres `reset_password_with_token(...)`
- le comportement de la session SQLAlchemy au moment du `flush/commit`

## Ce que Cursor doit faire et ne pas faire

### A faire
- corriger la collision fixtures/cleanup
- mettre en place un teardown explicite des fixture users auth/admin
- revalider avec deux reruns de la batterie admin/feedback
- relancer la suite auth ciblee
- relancer la full suite
- distinguer clairement ce qui est corrige par la phase fixtures et ce qui relèverait d'un second bug auth

### A ne pas faire
- ne pas retoucher `admin_read_service.py`
- ne pas retoucher `analytics_handlers.py`
- ne pas retoucher `feedback_handlers.py`
- ne pas ouvrir `LOT 5`
- ne pas affaiblir les assertions de test
- ne pas vendre un `GO` si le vert n'est pas reproductible

## Fichiers cibles prioritaires

### Phase fixtures/cleanup
- `tests/conftest.py`
- `tests/utils/test_data_cleanup.py`
- `tests/api/test_admin_ai_stats.py`
- `tests/api/test_admin_analytics.py`
- `tests/api/test_admin_users_delete.py`
- `tests/api/test_auth_flow.py`

### Phase auth runtime seulement si necessaire
- `server/auth.py`
- `app/services/auth_service.py`

## Preuves minimales exigees de Cursor
- preuve que le namespace `fixture_auth_*` ne matche plus aucun pattern de cleanup global
- preuve que les fixture users existent encore en DB juste avant les requetes admin/auth critiques
- run 1 admin/feedback vert
- run 2 admin/feedback vert
- auth ciblee verte
- full suite verte
- `black` vert

## Format de sortie exige a Cursor
1. fichiers modifies
2. fichiers runtime modifies
3. fichiers tests modifies
4. endpoints reellement touches
5. ce qui a ete prouve factuellement
6. ce qui reste hypothese
7. cause exacte ou meilleure explication defendable des `401`
8. dire explicitement si la collision fixtures/cleanup etait ou non la bonne cible
9. correctif applique et pourquoi il est borne
10. resultat run 1 checks cibles
11. resultat run 2 checks cibles
12. resultat auth cible
13. resultat full suite
14. risques residuels
15. recommendation go / no-go

## Critere de sortie de ce chantier
- `LOT 4` n'est validable que si:
  - le read path admin reste code-correct
  - les fixtures auth/admin sortent completement du cleanup global
  - les reruns admin/feedback sont reproductibles
  - la suite auth ciblee est verte
  - la full suite est verte

Tant que ces 5 conditions ne sont pas reunies, `LOT 4` reste `NO-GO`.

