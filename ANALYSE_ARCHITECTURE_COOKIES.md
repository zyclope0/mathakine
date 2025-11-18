# Analyse Architecture: Problème de cookies entre domaines

## 🎯 Problème identifié

**Symptôme**: Génération IA impossible avec erreur "Non authentifié - Cookie manquant"  
**Cause racine**: **Cookies créés pour un domaine ne sont PAS accessibles depuis un autre domaine, même avec `samesite="none"`**

---

## 🏗️ Architecture Mathakine

### Séparation des services

```
┌─────────────────────────────────────────────────────────┐
│ Frontend Next.js                                         │
│ Domain: https://mathakine-frontend.onrender.com         │
│ - Pages React                                            │
│ - Client-side routing                                    │
│ - API routes Next.js (proxy)                             │
└─────────────────────────────────────────────────────────┘
                      ▲
                      │
                      │ HTTP requests
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│ Backend FastAPI                                          │
│ Domain: https://mathakine-alpha.onrender.com            │
│ - API REST                                               │
│ - Authentification (JWT cookies)                         │
│ - Génération IA (OpenAI)                                 │
│ - Base de données                                        │
└─────────────────────────────────────────────────────────┘
```

---

## 🍪 Comment fonctionnent les cookies cross-domain

### Configuration des cookies (Backend FastAPI)

```python
# server/views.py
response.set_cookie(
    key="access_token",
    value=tokens["access_token"],
    httponly=True,        # JavaScript ne peut pas lire
    secure=True,          # HTTPS uniquement
    samesite="none",      # Autorise cross-domain
    max_age=1800          # 30 minutes
)
```

**Domaine du cookie**: `mathakine-alpha.onrender.com` (créé par le backend)

### Règle fondamentale des cookies

> **Un cookie créé pour le domaine A ne peut être lu QUE par le domaine A, même avec `samesite="none"`**

Exemple :
- Cookie créé par `mathakine-alpha.onrender.com` ✅
- Lisible par `mathakine-alpha.onrender.com` ✅
- Lisible par `mathakine-frontend.onrender.com` ❌ **NON !**

---

## 🔍 Analyse du flux d'authentification

### Flux 1: Login (✅ Fonctionne)

```
1. Frontend (mathakine-frontend.onrender.com)
   User clique "Se connecter"
   
2. Frontend → Backend (mathakine-alpha.onrender.com)
   POST /api/auth/login
   credentials: 'include'
   
3. Backend valide et crée les cookies
   Set-Cookie: access_token=... (domain: mathakine-alpha.onrender.com)
   Set-Cookie: refresh_token=...
   
4. Navigateur stocke les cookies
   Cookies associés à: mathakine-alpha.onrender.com ✅
```

### Flux 2: Appel API standard (✅ Fonctionne)

```
1. Frontend veut afficher le profil
   
2. Frontend → Backend directement
   GET https://mathakine-alpha.onrender.com/api/users/me
   credentials: 'include'
   
3. Navigateur envoie automatiquement les cookies
   Cookie: access_token=...; refresh_token=...
   (car destination = mathakine-alpha.onrender.com) ✅
   
4. Backend lit les cookies et répond
   User data ✅
```

### Flux 3: Génération IA via proxy (❌ NE FONCTIONNE PAS)

```
1. Frontend veut générer un défi IA
   
2. Frontend → API route Next.js (même domaine)
   GET https://mathakine-frontend.onrender.com/api/challenges/generate-ai-stream
   
3. API route Next.js essaie de lire les cookies
   request.cookies.get('access_token')
   ❌ Retourne NULL !
   
   Pourquoi ? Les cookies sont pour mathakine-alpha.onrender.com,
   PAS pour mathakine-frontend.onrender.com
   
4. API route retourne erreur
   "Non authentifié - Cookie manquant" ❌
```

### Flux 4: Génération IA directe (✅ SOLUTION)

```
1. Frontend veut générer un défi IA
   
2. Frontend → Backend directement (sans proxy)
   GET https://mathakine-alpha.onrender.com/api/challenges/generate-ai-stream
   credentials: 'include'
   
3. Navigateur envoie automatiquement les cookies
   Cookie: access_token=...; refresh_token=...
   (car destination = mathakine-alpha.onrender.com) ✅
   
4. Backend lit les cookies et génère le défi
   Challenge généré ✅
```

---

## 🔧 Solutions possibles

### Option 1: ✅ Appel direct backend (SOLUTION CHOISIE)

**Principe**: Supprimer l'API route proxy, appeler directement le backend

**Avantages**:
- ✅ Simple et direct
- ✅ Cohérent avec les autres endpoints
- ✅ Cookies accessibles (même domaine)
- ✅ Pas de couche intermédiaire

**Inconvénients**:
- ⚠️ CORS doit être configuré sur le backend (déjà fait)
- ⚠️ Backend exposé directement au frontend

**Implémentation**:
```typescript
// frontend/components/challenges/AIGenerator.tsx
const backendUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://mathakine-alpha.onrender.com';
const url = `${backendUrl}/api/challenges/generate-ai-stream?${params}`;

const response = await fetch(url, {
  credentials: 'include', // Envoie les cookies au backend
});
```

### Option 2: Passer par le proxy mais transmettre les cookies explicitement

**Principe**: API route Next.js récupère les cookies et les transmet en header

**Problème**: Les cookies HTTP-only ne sont PAS accessibles par l'API route Next.js si créés pour un autre domaine !

**Verdict**: ❌ Impossible avec l'architecture actuelle

### Option 3: Unifier les domaines

**Principe**: Utiliser un seul domaine avec sous-domaines

```
Frontend: https://app.mathakine.com
Backend:  https://api.mathakine.com
```

**Avantages**:
- ✅ Cookies partagés entre sous-domaines (avec `domain=.mathakine.com`)
- ✅ Architecture plus professionnelle

**Inconvénients**:
- ❌ Nécessite un nom de domaine personnalisé
- ❌ Configuration DNS et certificats SSL
- ❌ Refonte de l'infrastructure Render

**Verdict**: ✅ Meilleure solution long terme, mais nécessite infrastructure

### Option 4: Tokens en localStorage

**Principe**: Stocker les tokens JWT en localStorage au lieu de cookies HTTP-only

**Avantages**:
- ✅ Accessible depuis JavaScript
- ✅ Pas de problème de domaine

**Inconvénients**:
- ❌ **Vulnérable aux attaques XSS** (faille de sécurité majeure)
- ❌ Moins sécurisé que les cookies HTTP-only
- ❌ Non recommandé pour l'authentification

**Verdict**: ❌ À éviter pour des raisons de sécurité

---

## ✅ Solution implémentée

### Changement de code

**Fichier**: `frontend/components/challenges/AIGenerator.tsx`

#### Avant ❌ (via proxy)
```typescript
const url = `/api/challenges/generate-ai-stream?${params}`;
// → mathakine-frontend.onrender.com/api/challenges/generate-ai-stream
// → Cookies inaccessibles
```

#### Après ✅ (direct backend)
```typescript
const backendUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://mathakine-alpha.onrender.com';
const url = `${backendUrl}/api/challenges/generate-ai-stream?${params}`;
// → mathakine-alpha.onrender.com/api/challenges/generate-ai-stream
// → Cookies envoyés automatiquement ✅
```

### Cohérence avec le reste de l'application

**Tous les autres endpoints** appellent déjà directement le backend :

```typescript
// frontend/lib/api/client.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://mathakine-alpha.onrender.com';

api.get('/api/users/me')          // → Backend direct ✅
api.post('/api/auth/login')       // → Backend direct ✅
api.post('/api/exercises/attempt') // → Backend direct ✅
```

**La génération IA** était la SEULE fonctionnalité qui passait par une API route proxy → Incohérence architecturale

---

## 🧪 Tests de validation

### Test 1: Vérifier l'URL appelée

**Console navigateur** (F12 → Network):
```
Request URL: https://mathakine-alpha.onrender.com/api/challenges/generate-ai-stream?challenge_type=sequence&age_group=10-12
Request Method: GET
Status: 200 OK
```

✅ **L'URL doit pointer vers le backend, PAS vers /api/**

### Test 2: Vérifier les cookies envoyés

**Console navigateur** (F12 → Network → Sélectionner la requête → Headers):
```
Request Headers:
Cookie: access_token=eyJ...; refresh_token=eyJ...
```

✅ **Les cookies doivent être présents dans la requête**

### Test 3: Vérifier la génération

**Interface**:
1. Se connecter ✅
2. Aller sur `/challenges` ✅
3. Configurer défi (Séquence, 10-12 ans) ✅
4. Cliquer "Générer" ✅
5. Observer messages progressifs ✅
6. Défi généré s'affiche ✅
7. Toast "Défi généré avec succès !" ✅

---

## 📊 Comparaison des architectures

### Architecture actuelle (séparée)

```
Frontend (mathakine-frontend.onrender.com)
    ↓ credentials: 'include'
Backend (mathakine-alpha.onrender.com)
    ↓ Set-Cookie (domain: backend)
Cookies accessibles uniquement pour backend ✅
```

**Avantages**:
- ✅ Séparation claire frontend/backend
- ✅ Scalabilité indépendante
- ✅ Technologies différentes (Next.js / FastAPI)

**Inconvénients**:
- ⚠️ CORS requis
- ⚠️ Cookies limités au domaine backend
- ⚠️ Pas de proxy possible

### Architecture unifiée (recommandée long terme)

```
Frontend (app.mathakine.com)
Backend (api.mathakine.com)
Cookies: domain=.mathakine.com
    → Accessibles par app et api ✅
```

**Avantages**:
- ✅ Cookies partagés
- ✅ Architecture professionnelle
- ✅ Proxy possible
- ✅ Meilleure sécurité

**Inconvénients**:
- ❌ Nécessite domaine personnalisé
- ❌ Configuration infrastructure

---

## 🎯 Commits

**Commit**: `db35afc` - "fix: appel direct backend au lieu proxy Next.js - cookies inaccessibles entre domaines"

---

## 📖 Leçons apprises

### 1. Cookies et domaines

**Règle**: Un cookie créé pour `domaine-a.com` n'est **JAMAIS** accessible depuis `domaine-b.com`, même avec :
- `samesite="none"` ✅
- `secure=True` ✅
- HTTPS ✅
- CORS configuré ✅

**Solution**: Appeler directement le domaine qui possède les cookies

### 2. API routes Next.js et authentification

**Quand utiliser les API routes** :
- ✅ Même domaine que le frontend
- ✅ Pour cacher des secrets (API keys)
- ✅ Pour agréger des données

**Quand NE PAS utiliser** :
- ❌ Comme proxy pour authentification cross-domain
- ❌ Quand le backend gère déjà CORS

### 3. Architecture recommandée

**Court terme** (domaines séparés) :
- Frontend → Backend directement
- Cookies HTTP-only pour sécurité
- CORS configuré sur backend

**Long terme** (production) :
- Domaine principal + sous-domaines
- Cookies partagés entre sous-domaines
- CDN + load balancing

---

## ✅ Résultat

La génération de défis logiques avec l'IA fonctionne maintenant **correctement** en appelant directement le backend, exactement comme tous les autres endpoints de l'application.

**Architecture finale**:
```
Frontend → Backend (direct, credentials: 'include')
✅ Cohérent
✅ Simple
✅ Sécurisé
✅ Fonctionnel
```

**Status**: ✅ **Correction validée et déployée**

