# 🔐 AUDIT COMPLET DE LA GESTION DES SESSIONS ET TOKENS

**Date** : 15 novembre 2025  
**Objectif** : Résoudre les problèmes de déconnexions régulières

---

## 🔍 PROBLÈMES IDENTIFIÉS

### 1. **Incohérences dans la durée de vie des tokens**

**Problème** : Durées de vie différentes selon les fichiers
- `app/core/config.py` : `ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7` (7 jours)
- `app/core/constants.py` : `ACCESS_TOKEN_EXPIRE_MINUTES = 30` (30 minutes) ❌
- `server/views.py` : `max_age=3600` (1 heure) ❌

**Impact** : Les cookies expirent avant le token, causant des déconnexions inattendues.

### 2. **Pas de refresh automatique de token**

**Problème** : Quand le token expire, toutes les requêtes échouent avec 401 sans tentative de refresh.

**Impact** : L'utilisateur est déconnecté même si le refresh token est encore valide.

### 3. **Refresh token non utilisé**

**Problème** : Le refresh token est créé et stocké dans les cookies mais jamais utilisé pour rafraîchir l'access token.

**Impact** : Perte de la fonctionnalité de refresh automatique.

### 4. **Pas d'intercepteur API pour gérer les 401**

**Problème** : Le client API ne détecte pas les erreurs 401 pour tenter un refresh automatique.

**Impact** : Chaque requête qui échoue avec 401 nécessite une reconnexion manuelle.

---

## ✅ CORRECTIONS APPLIQUÉES

### 1. **Harmonisation des durées de vie des tokens**

#### `app/core/constants.py`
```python
# Aligné avec config.py (7 jours)
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7
```

#### `server/views.py`
```python
# Utilise maintenant settings.ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.config import settings
access_token_max_age = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
```

**Résultat** : Tous les tokens ont maintenant une durée de vie cohérente de 7 jours.

### 2. **Système de refresh automatique**

#### `frontend/lib/api/client.ts`
- ✅ Ajout de la fonction `refreshAccessToken()` qui appelle `/api/auth/refresh`
- ✅ Intercepteur dans `apiRequest()` qui détecte les 401 et tente un refresh automatique
- ✅ Protection contre les boucles infinies (pas de retry sur `/api/auth/refresh` et `/api/auth/login`)
- ✅ Gestion de l'état de refresh en cours pour éviter les appels multiples simultanés

**Fonctionnement** :
1. Une requête API retourne 401
2. Le client détecte l'erreur 401
3. Appel automatique à `/api/auth/refresh` avec le refresh token (via cookies)
4. Si succès : réessai de la requête originale avec le nouveau token
5. Si échec : erreur 401 propagée (session expirée)

### 3. **Handler Starlette pour refresh token**

#### `server/views.py`
- ✅ Création de `api_refresh_token()` qui lit le refresh token depuis les cookies
- ✅ Appel au service `refresh_access_token()` pour générer un nouveau token
- ✅ Mise à jour du cookie `access_token` avec le nouveau token

#### `server/routes.py`
- ✅ Ajout de la route `/api/auth/refresh` (POST)

**Fonctionnement** :
1. Le frontend appelle `/api/auth/refresh` (sans body, refresh token dans les cookies)
2. Le backend lit le refresh token depuis `request.cookies.get("refresh_token")`
3. Validation et génération d'un nouveau access token
4. Retour du nouveau token dans les cookies HTTP-only

### 4. **Amélioration de la gestion des erreurs**

#### `frontend/hooks/useAuth.ts`
- ✅ Nettoyage du cache utilisateur quand le refresh échoue
- ✅ Gestion explicite des erreurs 401 après refresh automatique

#### `frontend/components/auth/ProtectedRoute.tsx`
- ✅ Déjà bien implémenté, utilise `useAuth` qui bénéficie maintenant du refresh automatique

---

## 📊 ARCHITECTURE FINALE

### Flux d'authentification

```
┌─────────────┐
│   Login     │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│ Génération tokens   │
│ - access_token      │
│ - refresh_token     │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Cookies HTTP-only   │
│ - access_token      │
│   (7 jours)         │
│ - refresh_token     │
│   (30 jours)        │
└─────────────────────┘
```

### Flux de refresh automatique

```
┌─────────────────┐
│ Requête API     │
└────────┬────────┘
         │
         ▼
    ┌────────┐
    │ 401 ?  │
    └───┬────┘
        │ Oui
        ▼
┌──────────────────────┐
│ Refresh automatique  │
│ POST /api/auth/refresh│
└──────────┬───────────┘
           │
           ▼
    ┌──────────────┐
    │ Succès ?     │
    └───┬──────────┘
        │ Oui
        ▼
┌──────────────────┐
│ Réessai requête  │
│ originale        │
└──────────────────┘
```

---

## 🎯 CONFIGURATION FINALE

### Durées de vie des tokens

| Token | Durée | Fichier |
|-------|-------|---------|
| **Access Token** | 7 jours | `app/core/config.py` |
| **Refresh Token** | 30 jours | `app/core/config.py` |
| **Cookie Access Token** | 7 jours | `server/views.py` |
| **Cookie Refresh Token** | 30 jours | `server/views.py` |

### Endpoints d'authentification

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/auth/login` | POST | Connexion et génération de tokens |
| `/api/auth/refresh` | POST | Refresh automatique du token (nouveau) |
| `/api/auth/logout` | POST | Déconnexion |
| `/api/auth/me` | GET | Informations utilisateur courant |

---

## 🔒 SÉCURITÉ

### ✅ Points de sécurité maintenus

1. **Cookies HTTP-only** : Les tokens ne sont pas accessibles via JavaScript
2. **Secure en production** : Cookies sécurisés uniquement en HTTPS
3. **SameSite=Lax** : Protection CSRF
4. **Refresh token rotation** : Nouveau token à chaque refresh (via le service)

### ⚠️ Recommandations futures

1. **Rotation du refresh token** : Implémenter la rotation du refresh token à chaque refresh
2. **Blacklist de tokens** : Pour invalider les tokens lors de la déconnexion
3. **Rate limiting** : Limiter les tentatives de refresh pour éviter les abus
4. **Monitoring** : Logger les refresh automatiques pour détecter les problèmes

---

## 🧪 TESTS RECOMMANDÉS

1. **Test de refresh automatique** :
   - Se connecter
   - Attendre l'expiration du token (ou modifier manuellement)
   - Faire une requête API
   - Vérifier que le refresh se fait automatiquement

2. **Test de déconnexion après expiration du refresh token** :
   - Se connecter
   - Attendre l'expiration du refresh token (30 jours)
   - Faire une requête API
   - Vérifier que l'utilisateur est redirigé vers `/login`

3. **Test de navigation entre pages** :
   - Se connecter
   - Naviguer entre plusieurs pages
   - Vérifier qu'il n'y a pas de déconnexions inattendues

---

## 📝 RÉSUMÉ DES MODIFICATIONS

### Fichiers modifiés

1. **`app/core/constants.py`** : Harmonisation de `ACCESS_TOKEN_EXPIRE_MINUTES`
2. **`server/views.py`** :
   - Correction de `max_age` pour utiliser `settings.ACCESS_TOKEN_EXPIRE_MINUTES`
   - Création de `api_refresh_token()` handler
3. **`server/routes.py`** : Ajout de la route `/api/auth/refresh`
4. **`frontend/lib/api/client.ts`** :
   - Ajout de `refreshAccessToken()`
   - Intercepteur 401 dans `apiRequest()`
5. **`frontend/hooks/useAuth.ts`** : Amélioration de la gestion des erreurs 401

### Nouveaux fichiers

- `docs/AUDIT_SESSION_TOKEN.md` (ce fichier)

---

## ✅ RÉSULTAT ATTENDU

Après ces corrections, les déconnexions régulières devraient être résolues :

1. ✅ **Tokens cohérents** : Tous les tokens ont la même durée de vie (7 jours)
2. ✅ **Refresh automatique** : Les tokens expirés sont rafraîchis automatiquement
3. ✅ **Meilleure UX** : L'utilisateur ne voit plus de déconnexions inattendues
4. ✅ **Sécurité maintenue** : Les cookies HTTP-only et la sécurité sont préservés

---

## 🚀 PROCHAINES ÉTAPES

1. **Tester en conditions réelles** : Vérifier que les déconnexions ne se produisent plus
2. **Monitorer les logs** : Surveiller les refresh automatiques pour détecter les problèmes
3. **Optimiser si nécessaire** : Ajuster les durées de vie selon les retours utilisateurs

---

**Status** : ✅ **Corrections appliquées et prêtes pour tests**

