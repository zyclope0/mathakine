# Rapport — Comportement du rate limit sur `POST /api/auth/validate-token`

**Date du constat initial :** 2026-04-07  
**Mise à jour analytique :** 2026-04-08  
**Correctif calibrage (FFI-L19A) :** 2026-04-08 — quota dédié `validate-token`, voir §15  
**Réduction appels Next (FFI-L19B) :** 2026-04-08 — runtime partagé + coalescence + TTL succès 2,5 s, voir §16  
**Périmètre :** production (logs Render), backend Starlette, frontend Next.js (App Router)  
**Destinataires :** validation produit / responsable projet  
**Statut :** constat historique conservé ; calibrage backend (L19A) + dédup Next server (L19B) livrés ; suite : **FFI-L19C** confiance proxy / clé plus fine

---

## 1. Objet

Documenter ce qui a été observé en production concernant les réponses **HTTP 429** sur l'endpoint **`POST /api/auth/validate-token`**, distinguer ce qui est **prouvé par le code et les logs** de ce qui reste **hypothèse infra**, lister les **corrections déjà faites** autour du flux, puis expliciter **ce qu'il reste à décider / implémenter**.

Ce document ne prétend pas que tout a déjà été corrigé côté produit. Il documente l'état réel au 2026-04-08.

---

## 2. Contexte technique

| Élément                       | Détail                                                                                                                                            |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| Endpoint                      | `POST /api/auth/validate-token` — validation JWT côté backend avant certaines décisions session/cookie côté frontend Next                         |
| Implémentation backend        | `@rate_limit_validate_token` sur `api_validate_token` + `RATE_LIMIT_VALIDATE_TOKEN_MAX` dans `app/utils/rate_limit.py` ; login / forgot-password restent sur `@rate_limit_auth` + `RATE_LIMIT_AUTH_SENSITIVE_MAX` |
| Consommateurs frontend connus | `frontend/lib/auth/server/routeSession.ts` (`routeSession`) et `frontend/app/api/auth/sync-cookie/route.ts` (`syncCookie`)                        |
| Attribution diagnostic        | header `X-Mathakine-Validate-Caller` construit par `frontend/lib/auth/server/validateTokenBackendHeaders.ts`                                      |
| Rate limit (état courant)     | **`validate-token` : 90 req / min / IP** (bucket `validate_token`, clé `rate_limit:validate-token:{ip}`). **Login / forgot-password : 5 / min / IP** (bucket `auth_sensitive`, clé `rate_limit:{endpoint}:{ip}`). Fenêtre **60 s**. |

---

## 3. Symptômes observés en production

- rafales de **429 Too Many Requests** sur `validate-token` en navigation normale
- pics de warnings concentrés sur une fenêtre très courte, compatibles avec des **requêtes parallèles server-side**
- `User-Agent: node` dans les logs diagnostic, cohérent avec des fetchs **Next.js serveur**
- présence de `validate_caller=routeSession` majoritairement, parfois `syncCookie`

Lecture principale :

- le bruit observé ressemble davantage à un **effet de l'architecture runtime** qu'à un abus utilisateur classique
- le problème ne ressemble pas au profil d'un bruteforce login

---

## 4. Ce qui est prouvé par le code actuel

### 4.1 Construction de la clé de rate limit (historique — avant FFI-L19A)

Dans `app/utils/rate_limit.py`, **avant** le lot FFI-L19A :

- un seul plafond « auth » à **5** (`RATE_LIMIT_AUTH_MAX`) couvrait aussi `validate-token`
- `api_validate_token` était décoré par `@rate_limit_auth("validate-token")`
- la clé était `rate_limit:{endpoint}:{ip}`
- `_get_client_ip(request)` prend :
  - `X-Forwarded-For.split(",")[0].strip()` si présent
  - sinon `request.client.host`

Conclusion (historique) :

- `validate-token` **partageait** le même ordre de grandeur de quota que `login`
- la granularité de la clé restait **IP-only**

### 4.1 bis État courant après FFI-L19A (2026-04-06)

- **Login / forgot-password** : `RATE_LIMIT_AUTH_SENSITIVE_MAX = 5`, décorateur `rate_limit_auth`, clé `rate_limit:{endpoint}:{ip}`, log **429** avec `bucket=auth_sensitive`.
- **`validate-token`** : `RATE_LIMIT_VALIDATE_TOKEN_MAX = 90`, décorateur `rate_limit_validate_token`, clé **`rate_limit:validate-token:{ip}`** (indépendante du compteur login), log **429** avec `bucket=validate_token`.
- **Justification du 90/min** : dans la fourchette **60–120** recommandée en §10.1 ; suffisant pour des rafales Next serveur légitimes par IP sans aligner le plafond sur celui du login (**5**).
- **Non traité dans ce lot** : confiance proxy / clé plus fine que l’IP (cf. §6, §10.3).

### 4.2 Multiplicité des appels frontend

Dans le frontend :

- `frontend/lib/auth/server/routeSession.ts`
  - appelle `/api/auth/validate-token`
  - envoie `X-Mathakine-Validate-Caller: routeSession`
  - utilise `cache: "no-store"`
- `frontend/app/api/auth/sync-cookie/route.ts`
  - appelle aussi `/api/auth/validate-token`
  - envoie `X-Mathakine-Validate-Caller: syncCookie`

Conclusion :

- plusieurs chemins Next serveur peuvent frapper le même endpoint
- des rafales concurrentes sont plausibles sans comportement anormal côté utilisateur

### 4.3 Nature du header d'attribution

`X-Mathakine-Validate-Caller` :

- sert au diagnostic
- n'est pas une preuve de confiance
- peut être spoofé par un client arbitraire

Conclusion :

- utile pour lire les logs
- insuffisant pour construire une politique de sécurité à lui seul

---

## 5. Ce qui est fortement corroboré par les logs

Les extraits fournis montrent de façon cohérente :

1. `ua='node'`
2. `validate_caller=routeSession` en majorité, `syncCookie` aussi présent
3. une IP de clé souvent identique (`74.220.51.250`)
4. un `X-Forwarded-For` dont le premier hop reste stable sur les événements étudiés

Lecture forte :

- le backend agrège une part importante du trafic `validate-token` dans **un même seau IP**
- avec un plafond de **5/min**, il est normal de voir des 429 dès que le trafic Next serveur devient un peu parallèle

---

## 6. Ce qui reste hypothèse infra

Le code ne prouve pas à lui seul :

- que `74.220.51.250` est exactement l'IP Render partagée
- ni que le premier hop de `X-Forwarded-For` correspond toujours à une infrastructure mutualisée plutôt qu'à l'utilisateur final

En revanche, même sans cette preuve absolue, le système reste déjà fragile :

- clé IP-only
- quota `5/min`
- appels server-side multiples
- navigation App Router concurrente

Donc l'hypothèse infra renforce le diagnostic, mais elle n'est pas nécessaire pour conclure que le calibrage actuel est mauvais pour `validate-token`.

---

## 7. Analyse causale stricte

### 7.1 Ce qui se passe probablement

1. Un utilisateur navigue normalement.
2. Next serveur résout plusieurs branches / routes / états de session.
3. `routeSession` appelle `validate-token`.
4. `syncCookie` peut aussi appeler `validate-token`.
5. Le backend compte ces appels sous une même clé IP.
6. Le plafond `5 / 60 s` saute rapidement.
7. Des `429` apparaissent alors que le token peut être parfaitement valide.

### 7.2 Conclusion de calibrage

Le problème principal n'est pas un bug de parsing JWT, ni un problème de log, ni une simple anomalie de monitoring.

Le problème principal est :

- **même famille de rate limit que `login`**
- **clé trop grossière pour le pattern runtime réel**

Autrement dit :

- l'intention de sécurité initiale était défendable
- le calibrage est désormais inadapté à la réalité du trafic `validate-token`

---

## 8. Corrections déjà intégrées au code

Ces points ont été intégrés autour du flux. Les diagnostics ci-dessous restent utiles. Le **calibrage quota** `validate-token` est traité séparément en **FFI-L19A** (§15).

### 8.1 Diagnostics backend améliorés

Déjà intégré :

- logs enrichis sur `validate-token` avec :
  - IP effective utilisée pour la clé
  - `User-Agent`
  - `Referer`
  - début de `X-Forwarded-For`
  - `validate_caller`

### 8.2 Formatage logs Loguru corrigé

Déjà intégré :

- passage aux placeholders `{}` côté Loguru pour que les logs de prod soient lisibles

### 8.3 Alignement test/runtime sur `settings.TESTING`

Déjà intégré :

- `rate_limit.py` utilise `settings.TESTING`
- les tests sont réalignés sur cette vérité runtime

### 8.4 Durcissement `sync-cookie`

Déjà intégré :

- `frontend/app/api/auth/sync-cookie/route.ts` valide maintenant la forme minimale du JWT avant l'appel backend :
  - 3 segments
  - segments non vides
  - longueur bornée

Important :

- ce durcissement protège le flux contre des tokens manifestement absurdes
- il **ne traite pas** le problème de rafales 429 sur des tokens bien formés et légitimes

---

## 9. Ce qui reste ouvert après FFI-L19A

### 9.1 Quota `validate-token` vs login

**Résolu (FFI-L19A)** : `validate-token` dispose d’un bucket et d’un plafond **distincts** du login — §15.

### 9.2 Les appels Next redondants

**Réduit (FFI-L19B, 2026-04-06)** : module partagé `frontend/lib/auth/server/validateTokenRuntime.ts` — coalescence des requêtes **en cours** pour la même paire `(baseUrl, token)` (un seul `fetch` concurrent), et micro-cache **succès uniquement** **`VALIDATE_TOKEN_SUCCESS_TTL_MS` = 2500 ms** (pas de cache des 401 ni des erreurs transitoires). Consommateurs : `routeSession`, `sync-cookie`.

### 9.3 La politique proxy/CDN n'est pas explicitement figée

Il n'existe pas encore ici de décision finale documentée sur :

- quel hop / header est fiable
- dans quelles conditions
- avec quel niveau de confiance infra

---

## 10. Décision recommandée

### 10.1 Court terme — stabilisation pragmatique

**Réalisé (FFI-L19A, 2026-04-06)** :

1. `validate-token` sorti du bucket auth sensible partagé avec login
2. quota dédié **`RATE_LIMIT_VALIDATE_TOKEN_MAX = 90`** / min / IP
3. `login` / `forgot-password` inchangés (**5/min**)

La fourchette **60–120** / min recommandée initialement est respectée (choix **90**).

### 10.2 Moyen terme — réduction du trafic côté Next

**Partiellement fait (FFI-L19B)** : déduplication intra-runtime documentée (voir §9.2). Suite possible : audit des **fréquences** d’appel `routeSession` / parcours RSC, sans élargir le TTL côté client.

### 10.3 Long terme — clé plus fidèle à l'utilisateur réel

N'ouvrir ce chantier qu'avec décision infra explicite :

- `CF-Connecting-IP`
- ou autre hop / header de confiance
- avec politique anti-spoofing documentée

---

## 11. Options écartées pour l'instant

### 11.1 Ne rien faire

Non recommandé :

- le bruit log et les 429 correspondent à un problème réel de calibrage

### 11.2 Traiter ça comme un bruteforce login

Non recommandé :

- les signaux observés (`node`, `routeSession`, `syncCookie`) pointent vers un trafic applicatif serveur normal

### 11.3 Baser la sécurité uniquement sur le frontend

Non pertinent :

- le sujet est côté backend / infrastructure de limitation

---

## 12. Plan d'action proposé après le lot en cours

### Lot 1 — stabilisation backend ciblée

**Fait (FFI-L19A)** : constantes `RATE_LIMIT_VALIDATE_TOKEN_MAX` / `RATE_LIMIT_AUTH_SENSITIVE_MAX`, décorateur `rate_limit_validate_token`, tests `tests/unit/test_rate_limit.py`.

### Lot 2 — audit d'appels Next

- **FFI-L19B** : point d’entrée unique + coalescence + TTL succès 2,5 s (voir `validateTokenRuntime.ts`)
- suite : mesurer fréquences par route RSC / réductions produit si pertinent

### Lot 3 — décision infra

- trancher la confiance des headers proxy/CDN
- ne pas le faire "à moitié" sans décision explicite

---

## 13. Synthèse exécutive

1. Les `429` sur `validate-token` ne ressemblent pas à un bruteforce login classique.
2. **Avant FFI-L19A**, `validate-token` partageait un plafond `5/min` avec login sur une clé IP-only.
3. Le frontend Next serveur a plusieurs consommateurs de cet endpoint.
4. Ce calibrage provoquait des rafales légitimes saturant le compteur.
5. **Après FFI-L19A** : quota dédié **90/min** pour `validate-token`, login/forgot-password **inchangés (5/min)** ; logs **429** distinguent `bucket=auth_sensitive` vs `bucket=validate_token`.
6. Pistes suivantes : réduction des appels Next et stratégie proxy plus fine (hors périmètre du lot quota).

---

## 14. Références code

- `app/utils/rate_limit.py`
- `server/handlers/auth_handlers.py`
- `frontend/lib/auth/server/routeSession.ts`
- `frontend/app/api/auth/sync-cookie/route.ts`
- `frontend/lib/auth/server/validateTokenBackendHeaders.ts`
- `frontend/lib/auth/server/validateTokenRuntime.ts`
- `README_TECH.md`

---

## 15. Livrable FFI-L19A (calibrage)

| Élément | Détail |
| ------- | ------ |
| Constante login / forgot-password | `RATE_LIMIT_AUTH_SENSITIVE_MAX = 5` |
| Constante validate-token | `RATE_LIMIT_VALIDATE_TOKEN_MAX = 90` |
| Décorateur validate-token | `rate_limit_validate_token` → clé `rate_limit:validate-token:{ip}` |
| Décorateur auth sensible | `rate_limit_auth` → clé `rate_limit:{endpoint}:{ip}` |
| Observabilité | WARNING **429** : `bucket=…`, `endpoint=…` (auth), IP, diagnostics existants |
| Tests | `tests/unit/test_rate_limit.py` : buckets distincts, 6× validate OK + 6e login bloqué, logs |

Hors scope explicite : confiance `X-Forwarded-For` / CDN, re-key par utilisateur.

---

## 16. Livrable FFI-L19B (Next server — moins d’appels redondants)

| Élément | Détail |
| ------- | ------ |
| Module | `frontend/lib/auth/server/validateTokenRuntime.ts` — `validateAccessTokenWithBackend(baseUrl, token, caller)` |
| Coalescence | Une seule requête HTTP en vol pour la même clé mémoire `baseUrl + "\\0" + token` (synchrone) |
| Micro-cache | **Succès 200 uniquement** ; TTL **`VALIDATE_TOKEN_SUCCESS_TTL_MS` = 2500 ms** ; pas de stockage persistant |
| Non cache | 401, autres HTTP, erreurs réseau → jamais réutilisés comme « valide » |
| Tests | `__tests__/unit/lib/auth/server/validateTokenRuntime.test.ts` + resets dans `routeSession` / `sync-cookie` tests |

Prépare **FFI-L19C** (proxy trust / clé plus fine) sans le mélanger.

---

Document de décision technique.  
Le diagnostic initial (2026-04-08) a conduit au lot **FFI-L19A** (quota dédié, 2026-04-06), puis **FFI-L19B** (dédup Next server, 2026-04-06). La stratégie proxy / clé plus fine reste le lot **FFI-L19C**.

