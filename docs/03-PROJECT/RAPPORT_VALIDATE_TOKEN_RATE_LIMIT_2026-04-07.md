# Rapport — Comportement du rate limit sur `POST /api/auth/validate-token`

**Date du constat initial :** 2026-04-07  
**Mise à jour analytique :** 2026-04-08  
**Périmètre :** production (logs Render), backend Starlette, frontend Next.js (App Router)  
**Destinataires :** validation produit / responsable projet  
**Statut :** constat factuel, analyse causale stricte, corrections déjà intégrées, et plan d'action recommandé

---

## 1. Objet

Documenter ce qui a été observé en production concernant les réponses **HTTP 429** sur l'endpoint **`POST /api/auth/validate-token`**, distinguer ce qui est **prouvé par le code et les logs** de ce qui reste **hypothèse infra**, lister les **corrections déjà faites** autour du flux, puis expliciter **ce qu'il reste à décider / implémenter**.

Ce document ne prétend pas que tout a déjà été corrigé côté produit. Il documente l'état réel au 2026-04-08.

---

## 2. Contexte technique

| Élément                       | Détail                                                                                                                                            |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| Endpoint                      | `POST /api/auth/validate-token` — validation JWT côté backend avant certaines décisions session/cookie côté frontend Next                         |
| Implémentation backend        | `@rate_limit_auth("validate-token")` dans `app/utils/rate_limit.py` + handler `api_validate_token` dans `server/handlers/auth_handlers.py`        |
| Consommateurs frontend connus | `frontend/lib/auth/server/routeSession.ts` (`routeSession`) et `frontend/app/api/auth/sync-cookie/route.ts` (`syncCookie`)                        |
| Attribution diagnostic        | header `X-Mathakine-Validate-Caller` construit par `frontend/lib/auth/server/validateTokenBackendHeaders.ts`                                      |
| Rate limit actuel             | même famille que `login` / `forgot-password` : **5 requêtes / minute / clé**, fenêtre **60 s**, clé basée sur l'IP telle que déduite des en-têtes |

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

### 4.1 Construction de la clé de rate limit

Dans `app/utils/rate_limit.py` :

- `RATE_LIMIT_AUTH_MAX = 5`
- `api_validate_token` est bien décoré par `@rate_limit_auth("validate-token")`
- la clé est `rate_limit:{endpoint}:{ip}`
- `_get_client_ip(request)` prend :
  - `X-Forwarded-For.split(",")[0].strip()` si présent
  - sinon `request.client.host`

Conclusion :

- `validate-token` partage aujourd'hui le même ordre de grandeur de quota que `login`
- la granularité de la clé est **IP-only**

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

Ces points ont déjà été corrigés autour du flux, mais **ils ne résolvent pas encore le problème de quota** :

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

## 9. Ce qui n'est pas encore corrigé

### 9.1 Le point bloquant principal

`validate-token` est toujours limité comme `login` :

- **5/min par clé IP**

Tant que ce point ne change pas, les symptômes de saturation peuvent revenir.

### 9.2 Les appels Next redondants ne sont pas encore réduits

À ce stade :

- `routeSession` et `syncCookie` existent toujours comme consommateurs
- il n'y a pas encore de stratégie explicite de déduplication ou de cache court documentée pour ce flux

### 9.3 La politique proxy/CDN n'est pas explicitement figée

Il n'existe pas encore ici de décision finale documentée sur :

- quel hop / header est fiable
- dans quelles conditions
- avec quel niveau de confiance infra

---

## 10. Décision recommandée

### 10.1 Court terme — stabilisation pragmatique

Faire un lot dédié `validate-token` et :

1. sortir `validate-token` de `RATE_LIMIT_AUTH_MAX`
2. créer un quota dédié, plus élevé
3. garder `login` / `forgot-password` inchangés

Ordre de grandeur recommandé :

- **60 à 120 requêtes / minute** pour `validate-token`

Pourquoi :

- c'est le correctif le plus simple
- il cible le symptôme réel
- il réduit immédiatement les faux positifs de rate limit sans ouvrir un chantier infra complet

### 10.2 Moyen terme — réduction du trafic côté Next

Auditer ensuite :

- fréquence réelle des appels `routeSession`
- éventuelles revalidations inutiles
- possibilité de déduplication / cache court local au cycle de requête

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

- ajouter une constante dédiée :
  - par exemple `RATE_LIMIT_VALIDATE_TOKEN_MAX`
- créer un décorateur ou un chemin dédié pour `validate-token`
- ajouter / adapter les tests backend du rate limit pour ce nouveau quota

### Lot 2 — audit d'appels Next

- mesurer qui appelle `validate-token`, à quelle fréquence, et sous quelles routes
- identifier si `routeSession` peut être moins bavard

### Lot 3 — décision infra

- trancher la confiance des headers proxy/CDN
- ne pas le faire "à moitié" sans décision explicite

---

## 13. Synthèse exécutive

1. Les `429` sur `validate-token` ne ressemblent pas à un bruteforce login classique.
2. Le code prouve que `validate-token` partage aujourd'hui un plafond `5/min` fondé sur une clé IP-only.
3. Le frontend Next serveur a plusieurs consommateurs de cet endpoint.
4. Avec ce calibrage, des rafales légitimes peuvent saturer le compteur.
5. Le correctif le plus pragmatique est de **donner à `validate-token` un quota dédié plus élevé**, sans toucher aux limites de `login`.
6. Une réduction des appels Next et une stratégie proxy plus fine sont pertinentes ensuite, mais ne doivent pas retarder la stabilisation.

---

## 14. Références code

- `app/utils/rate_limit.py`
- `server/handlers/auth_handlers.py`
- `frontend/lib/auth/server/routeSession.ts`
- `frontend/app/api/auth/sync-cookie/route.ts`
- `frontend/lib/auth/server/validateTokenBackendHeaders.ts`
- `README_TECH.md`

---

Document de décision technique.  
Au 2026-04-08, le diagnostic est jugé **suffisamment solide pour planifier un lot de stabilisation dédié**, même si la stratégie proxy de long terme reste à trancher explicitement.
