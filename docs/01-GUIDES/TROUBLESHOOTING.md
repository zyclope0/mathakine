# 🔧 TROUBLESHOOTING GUIDE - MATHAKINE

**Version** : 2.0.0  
**Date** : 20 novembre 2025  
**Audience** : Tous

---

## 🆘 PROBLÈMES COURANTS

### Backend

#### ❌ Backend ne démarre pas

**Erreur** :
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution** :
```bash
# Réinstaller dépendances
pip install --upgrade -r requirements.txt

# Vérifier environnement virtuel activé
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

---

**Erreur** :
```
sqlalchemy.exc.OperationalError: unable to open database file
```

**Solution** :
```bash
# Créer la base de données
python -m app.db.init_db

# Vérifier DATABASE_URL dans .env
DATABASE_URL=sqlite:///./mathakine.db
```

---

**Erreur** :
```
ValueError: SECRET_KEY not set
```

**Solution** :
```bash
# Générer SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Ajouter dans .env
SECRET_KEY=<generated-key>
```

---

**Erreur** :
```
Address already in use (port 8000)
```

**Solution** :
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:8000 | xargs kill -9

# OU utiliser un autre port
PORT=8001 python enhanced_server.py
```

---

#### ❌ Erreurs database

**Erreur** :
```
alembic.util.exc.CommandError: Can't locate revision identified by 'xxxxx'
```

**Solution** :
```bash
# Reset migrations (DEV ONLY!)
rm alembic/versions/*.py
rm mathakine.db

# Créer nouvelle migration
alembic revision --autogenerate -m "Initial"
alembic upgrade head
python -m app.db.init_db
```

---

**Erreur** :
```
psycopg2.OperationalError: FATAL: password authentication failed
```

**Solution** :
```bash
# Vérifier DATABASE_URL
echo $DATABASE_URL

# Format correct
DATABASE_URL=postgresql://user:password@localhost:5432/mathakine

# Vérifier PostgreSQL actif
# Windows: Services → PostgreSQL
# Mac/Linux: sudo systemctl status postgresql
```

---

### Frontend

#### ❌ Frontend ne démarre pas

**Erreur** :
```
Error: Cannot find module 'next'
```

**Solution** :
```bash
cd frontend

# Nettoyer et réinstaller
rm -rf node_modules package-lock.json
npm install

# OU
npm ci  # Plus rapide, utilise package-lock.json
```

---

**Erreur** :
```
Error: ECONNREFUSED 127.0.0.1:8000
```

**Solution** :
```bash
# Vérifier backend est lancé
# Terminal 1: python enhanced_server.py

# Vérifier NEXT_PUBLIC_API_BASE_URL dans .env.local
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

---

**Erreur** :
```
Port 3000 is already in use
```

**Solution** :
```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:3000 | xargs kill -9

# OU utiliser autre port
npm run dev -- -p 3001
```

---

#### ❌ Erreurs build

**Erreur** :
```
Type error: Property 'xxx' does not exist on type 'yyy'
```

**Solution** :
```typescript
// Vérifier types dans frontend/types/
// Ajouter propriété manquante

interface Challenge {
  id: number;
  title: string;
  xxx: string;  // Ajouter propriété
}
```

---

**Erreur** :
```
Error: Hydration failed
```

**Solution** :
```typescript
// Utiliser useEffect pour code client-only
'use client';

import { useEffect, useState } from 'react';

export function MyComponent() {
  const [mounted, setMounted] = useState(false);
  
  useEffect(() => {
    setMounted(true);
  }, []);
  
  if (!mounted) return null;
  
  return <div>...</div>;
}
```

---

### API / CORS

#### ❌ CORS errors

**Erreur** :
```
Access to fetch at 'http://localhost:8000/api/...' has been blocked by CORS policy
```

**Solution Backend** :
```python
# enhanced_server.py
from starlette.middleware.cors import CORSMiddleware

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],  # Frontend URL
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
]
```

**Solution Frontend** :
```typescript
// lib/api/client.ts
const response = await fetch(url, {
  credentials: 'include',  // Important!
  headers: {
    'Content-Type': 'application/json',
  },
});
```

---

#### ❌ OPTIONS 400 Bad Request (preflight CORS)

**Erreur** (logs backend) :
```
OPTIONS /api/users/me HTTP/1.1 400 Bad Request
OPTIONS /api/exercises/completed-ids HTTP/1.1 400 Bad Request
```

**Cause** : L'origine du frontend (Origin header) n'est pas dans la liste CORS du backend, ou FRONTEND_URL est mal configurée.

**Solutions** :

1. **Vérifier FRONTEND_URL sur le backend** (Render, .env prod) :
   ```
   FRONTEND_URL=https://mathakine.fun
   ```
   ou `https://www.mathakine.fun` selon le domaine utilisé.

2. **Origine exacte** : L'Origin envoyée par le navigateur doit correspondre exactement (schéma + domaine + port). Le backend ajoute désormais les variantes www/non-www automatiquement.

3. **Vérifier les env frontend** : `NEXT_PUBLIC_API_BASE_URL` doit pointer vers l'URL du backend (ex. `https://mathakine-backend.onrender.com`).

---

#### ❌ 401 Unauthorized

**Erreur** :
```
HTTP 401: Unauthorized
```

**Solutions** :

1. **Token expiré**
```typescript
// Implémenter refresh token
if (response.status === 401) {
  await refreshToken();
  // Réessayer requête
}
```

2. **Cookie pas envoyé**
```typescript
// Vérifier credentials: 'include'
await fetch(url, {
  credentials: 'include',  // ✅
});
```

3. **Token invalide**
```bash
# Backend logs
logger.error(f"Token validation failed: {error}")

# Regénérer token
# Se déconnecter/reconnecter
```

---

#### ❌ 404 Not Found

**Erreur** :
```
HTTP 404: Not Found
```

**Solutions** :

1. **Route n'existe pas**
```python
# Vérifier server/routes.py
Route("/api/challenges", challenges_handler, methods=["GET"]),
```

2. **URL incorrecte**
```typescript
// ✅ CORRECT
await api.get('/challenges');

// ❌ INCORRECT
await api.get('/challenge');  // Singular
```

---

### Tests

#### ❌ Tests échouent

**Erreur** :
```
pytest: command not found
```

**Solution** :
```bash
# Installer pytest
pip install pytest pytest-cov

# Vérifier environnement virtuel activé
which pytest  # Doit pointer vers venv/
```

---

**Erreur** :
```
FAILED tests/api/test_auth.py::test_login - AssertionError
```

**Solution** :
```bash
# Voir détails
pytest tests/api/test_auth.py::test_login -v

# Debug
pytest tests/api/test_auth.py::test_login -v -s  # Voir prints

# Debugger
import pdb; pdb.set_trace()
```

---

**Erreur** :
```
fixture 'db' not found
```

**Solution** :
```python
# Vérifier tests/conftest.py existe
# Et contient fixture db

@pytest.fixture
def db(engine):
    TestingSessionLocal = sessionmaker(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
```

---

### Performance

#### ❌ Backend lent

**Diagnostics** :
```python
# Activer logging SQL
# app/core/config.py
SQLALCHEMY_ECHO = True  # Voir toutes les requêtes

# Profiler
import cProfile
cProfile.run('my_function()')
```

**Solutions** :
1. **Ajouter indexes**
```python
# alembic migration
op.create_index('idx_challenge_type', 'logic_challenges', ['challenge_type'])
```

2. **Utiliser eager loading**
```python
# ❌ N+1 queries
challenges = db.query(Challenge).all()
for c in challenges:
    print(c.user.username)  # Query par challenge

# ✅ 1 query
from sqlalchemy.orm import joinedload
challenges = db.query(Challenge).options(joinedload(Challenge.user)).all()
```

3. **Cache**
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_challenge_types():
    return db.query(ChallengeType).all()
```

---

#### ❌ Frontend lent

**Diagnostics** :
```typescript
// React DevTools Profiler
// Chrome DevTools → Performance

// Log render times
console.time('render');
// ... component render
console.timeEnd('render');
```

**Solutions** :
1. **Memoization**
```typescript
import { useMemo, useCallback } from 'react';

const expensiveValue = useMemo(() => {
  return computeExpensiveValue(data);
}, [data]);

const handleClick = useCallback(() => {
  // ...
}, [dep1, dep2]);
```

2. **Code splitting**
```typescript
// Lazy load composants
import dynamic from 'next/dynamic';

const HeavyComponent = dynamic(() => import('./HeavyComponent'), {
  loading: () => <p>Loading...</p>,
});
```

3. **Optimiser images**
```typescript
import Image from 'next/image';

<Image
  src="/image.jpg"
  width={800}
  height={600}
  loading="lazy"
  alt="..."
/>
```

---

## 🔍 DEBUGGING

### Backend

```python
# Logging
from loguru import logger

logger.debug("Debug message")
logger.info(f"User {user_id} logged in")
logger.error(f"Error: {error}")
logger.exception("Exception occurred")  # Avec stacktrace

# Breakpoint
import pdb; pdb.set_trace()

# OU Python 3.7+
breakpoint()
```

### Frontend

```typescript
// Console
console.log('Data:', data);
console.table(users);
console.group('API Calls');
console.log('Call 1');
console.log('Call 2');
console.groupEnd();

// React DevTools
// Inspecter composants, props, state, hooks

// Network tab
// Vérifier requêtes API, status, headers, payload
```

---

## 📊 LOGS

### Localisation logs

**Backend** :
```bash
# Development
# Console où enhanced_server.py tourne

# Production (Render)
# Dashboard → Service → Logs
```

**Frontend** :
```bash
# Development
# Console où npm run dev tourne

# Browser
# F12 → Console

# Production
# Sentry, LogRocket, etc.
```

### Niveaux de log

```python
# Backend
DEBUG    # Infos détaillées debug
INFO     # Infos générales
WARNING  # Avertissements
ERROR    # Erreurs récupérables
CRITICAL # Erreurs critiques

# Configuration
# .env
LOG_LEVEL=INFO  # Production
LOG_LEVEL=DEBUG  # Development
```

---

## 🆘 BESOIN D'AIDE ?

### Ressources

1. **Documentation**
   - [Getting Started](../00-REFERENCE/GETTING_STARTED.md)
   - [Architecture](../00-REFERENCE/ARCHITECTURE.md)
   - [API Reference](../00-REFERENCE/API.md)
   - [Development Guide](DEVELOPMENT.md)
   - [FAQ](FAQ.md)

2. **GitHub**
   - [Issues](https://github.com/yourusername/mathakine/issues)
   - [Discussions](https://github.com/yourusername/mathakine/discussions)

3. **Communauté**
   - Stack Overflow (tag: mathakine)
   - Discord/Slack communauté

---

## 📋 CHECKLIST DEBUG

Avant de demander de l'aide, vérifier :

- [ ] Code à jour (`git pull`)
- [ ] Dépendances à jour (`pip install -r requirements.txt`, `npm install`)
- [ ] Variables d'environnement configurées (`.env`, `.env.local`)
- [ ] Base de données créée et migrée
- [ ] Logs consultés (erreurs, warnings)
- [ ] Backend et frontend démarrés
- [ ] Ports corrects (8000, 3000)
- [ ] CORS configuré
- [ ] Tests passent

---

## 🎨 THÈME ET ACCESSIBILITÉ

### ❌ Dark mode ne fonctionne pas

**Symptôme** : Le bouton dark mode est cliqué mais l'interface ne change pas

**Cause** : Sélecteurs CSS incorrects dans `globals.css`

**Solution** :
```css
/* ❌ INCORRECT - sélecteur descendant */
.dark [data-theme='spatial'] { ... }

/* ✅ CORRECT - même élément */
.dark[data-theme='spatial'] { ... }
```

**Explication** : Les classes `dark` et `data-theme` sont sur le même élément (`<html>`), pas en relation parent-enfant.

---

### ❌ Bouton accessibilité invisible

**Symptôme** : Le bouton accessibilité (roue crantée) n'apparaît pas ou est mal positionné

**Causes possibles** :

1. **`willChange: 'opacity, transform'`** dans un composant parent (crée un nouveau stacking context et casse `position: fixed`)
2. **z-index insuffisant** (doit être très élevé, ex: 99999)
3. **Conflits avec d'autres Portals** (ex: DropdownMenu de shadcn/ui)

**Solution** :
```tsx
// Utiliser un Portal dédié avec styles inline
useEffect(() => {
  let container = document.getElementById('accessibility-portal');
  if (!container) {
    container = document.createElement('div');
    container.id = 'accessibility-portal';
    container.style.cssText = `
      position: fixed;
      bottom: 24px;
      left: 24px;
      z-index: 99999;
    `;
    document.body.appendChild(container);
  }
}, []);

return createPortal(<MyButton />, container);
```

---

### ❌ Génération IA "Non authentifié - Cookie manquant" en production

**Symptôme** : Génération IA fonctionne en dev mais pas en prod. Message : "Non authentifié - Cookie manquant" ou log `[Exercise AI Stream Proxy] Missing auth cookie`.

**Cause** : En production, frontend et backend sont sur des domaines différents (ex. `mathakine-frontend.onrender.com` vs `mathakine-backend.onrender.com`). Le cookie `access_token` posé par le backend ne s’envoie pas aux routes API Next.js (`/api/exercises/generate-ai-stream`) car elles sont sur le domaine frontend.

**Solution** : Le système de sync-cookie copie le token sur le domaine frontend après login :

1. **`/api/auth/sync-cookie`** : POST avec `{ access_token }` pose le cookie sur le domaine frontend
2. **`login`** : attend la sync avant de rediriger (`await syncAccessTokenToFrontend`)
3. **`ensureFrontendAuthCookie()`** : appelé avant génération IA (refresh + sync si besoin)
4. **`AuthSyncProvider`** : au chargement, si `refresh_token` présent, fait un refresh + sync

**Diagnostic** :

- Ouvrir `https://[ton-frontend]/api/auth/check-cookie` dans le navigateur après connexion
  - `has_access_token_cookie: true` → cookie OK
  - `false` → se déconnecter puis se reconnecter
- Logs Render : chercher `[Exercise AI Stream Proxy] Cookies reçus:` pour voir ce qui arrive au proxy

**Autres vérifications** :

- Utiliser `request.cookies.getAll()` au lieu de `request.headers.get('cookie')` côté proxy
- Vérifier `NEXT_PUBLIC_API_BASE_URL` défini sur Render (frontend)
- Version openai : `openai>=1.40.0`

---

**Bon debugging !** 🔧✅

