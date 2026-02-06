# 🚢 DEPLOYMENT GUIDE - MATHAKINE

**Version** : 2.0.0  
**Date** : 20 novembre 2025  
**Audience** : DevOps, Développeurs

---

## 📋 TABLE DES MATIÈRES

1. [Vue d'ensemble](#vue-ensemble)
2. [Déploiement sur Render](#render)
3. [Configuration production](#configuration)
4. [Database migrations](#migrations)
5. [Monitoring](#monitoring)
6. [Troubleshooting](#troubleshooting)

---

## 🎯 VUE D'ENSEMBLE {#vue-ensemble}

### Architecture production

```
┌──────────────────────────────────────────┐
│   Frontend (Render Static Site)          │
│   https://mathakine-frontend.onrender.com│
└────────────────┬─────────────────────────┘
                 │ HTTPS/REST
                 ↓
┌──────────────────────────────────────────┐
│   Backend (Render Web Service)           │
│   https://mathakine-backend.onrender.com │
└────────────────┬─────────────────────────┘
                 │ PostgreSQL
                 ↓
┌──────────────────────────────────────────┐
│   Database (Render PostgreSQL)           │
│   postgresql://...                       │
└──────────────────────────────────────────┘
```

### Services déployés

| Service | Type | URL Production |
|---------|------|----------------|
| **Frontend** | Static Site | https://mathakine-frontend.onrender.com |
| **Backend** | Web Service | https://mathakine-backend.onrender.com |
| **Database** | PostgreSQL | Interne Render |

---

## 🌐 DÉPLOIEMENT SUR RENDER {#render}

### 1. Prérequis

- ✅ Compte Render.com
- ✅ Repository GitHub connecté
- ✅ Code en production ready
- ✅ Variables d'environnement préparées

### 2. Déployer le Backend

#### 2.1 Créer Web Service

1. **Dashboard Render** → New + → Web Service
2. **Connect Repository** : `mathakine`
3. **Configuration** :
   ```
   Name: mathakine-backend
   Region: Frankfurt (EU Central)
   Branch: main
   Root Directory: (leave empty)
   Runtime: Python 3.11
   Build Command: pip install -r requirements.txt
   Start Command: python enhanced_server.py
   ```

#### 2.2 Variables d'environnement

```bash
# Database (auto-généré par Render)
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Security
SECRET_KEY=<générer avec: python -c "import secrets; print(secrets.token_urlsafe(32))">
ALLOWED_ORIGINS=https://mathakine-frontend.onrender.com,http://localhost:3000

# Application
ENVIRONMENT=production
LOG_LEVEL=INFO
DEBUG=False

# OpenAI (optionnel)
OPENAI_API_KEY=sk-...

# Email (optionnel)
SENDGRID_API_KEY=SG....
EMAIL_FROM=noreply@mathakine.com
```

#### 2.3 Santé check

```python
# Render vérifie automatiquement
# GET / doit retourner 200

# enhanced_server.py
@app.route("/")
async def health_check(request):
    return JSONResponse({"status": "healthy"})
```

#### 2.4 Deploy

- Click **Create Web Service**
- Attendre build (~5 min)
- Vérifier logs
- Tester URL : `https://mathakine-backend.onrender.com/`

### 3. Déployer la Database

#### 3.1 Créer PostgreSQL

1. **Dashboard Render** → New + → PostgreSQL
2. **Configuration** :
   ```
   Name: mathakine-db
   Database: mathakine
   User: mathakine_user
   Region: Frankfurt (EU Central)
   PostgreSQL Version: 15
   ```

#### 3.2 Connecter au backend

1. Copier **Internal Database URL**
2. Backend → Environment → Add `DATABASE_URL`
3. Redéployer backend

#### 3.3 Migrations

```bash
# En local, pointer vers DB production
export DATABASE_URL="postgresql://..."

# Appliquer migrations
alembic upgrade head

# Seed data (optionnel)
python -m app.db.init_db --seed
```

### 4. Déployer le Frontend

#### 4.1 Créer Static Site

1. **Dashboard Render** → New + → Static Site
2. **Connect Repository** : `mathakine`
3. **Configuration** :
   ```
   Name: mathakine-frontend
   Branch: main
   Root Directory: frontend
   Build Command: npm install && npm run build
   Publish Directory: frontend/out
   ```

#### 4.2 Variables d'environnement

```bash
# Backend API
NEXT_PUBLIC_API_BASE_URL=https://mathakine-backend.onrender.com
NEXT_PUBLIC_API_URL=https://mathakine-backend.onrender.com/api

# Features
NEXT_PUBLIC_ENABLE_AI_GENERATION=true

# Analytics (optionnel)
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX
```

#### 4.3 next.config.js pour Static Export

```javascript
// frontend/next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',  // Static export
  images: {
    unoptimized: true,  // Pour static export
  },
  trailingSlash: true,
};

module.exports = nextConfig;
```

#### 4.4 Deploy

- Click **Create Static Site**
- Attendre build (~3 min)
- Vérifier logs
- Tester URL : `https://mathakine-frontend.onrender.com/`

---

## ⚙️ CONFIGURATION PRODUCTION {#configuration}

### Backend (enhanced_server.py)

```python
import os
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

def create_app():
    # CORS configuration
    allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
    
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=allowed_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    ]
    
    app = Starlette(
        debug=os.getenv("DEBUG", "False").lower() == "true",
        middleware=middleware,
        routes=routes,
    )
    
    return app

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        "enhanced_server:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True,
    )
```

### Frontend (API Client)

```typescript
// frontend/lib/api/client.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export const api = {
  async get<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      credentials: 'include',  // Important pour cookies
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    return response.json();
  },
  
  async post<T>(endpoint: string, data: any): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    return response.json();
  },
};
```

### Environment Variables

#### Backend (.env)
```bash
# ===== PRODUCTION =====
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://user:password@host:5432/mathakine

# Security
SECRET_KEY=<generate-secure-key>
ALLOWED_ORIGINS=https://mathakine-frontend.onrender.com

# CORS
ALLOW_CREDENTIALS=true

# Session
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=none

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60

# OpenAI (optionnel)
OPENAI_API_KEY=sk-...

# Email (optionnel)
SENDGRID_API_KEY=SG...
EMAIL_FROM=noreply@mathakine.com
```

#### Frontend (.env.local)
```bash
# ===== PRODUCTION =====
NEXT_PUBLIC_API_BASE_URL=https://mathakine-backend.onrender.com
NEXT_PUBLIC_API_URL=https://mathakine-backend.onrender.com/api

# Features
NEXT_PUBLIC_ENABLE_AI_GENERATION=true
NEXT_PUBLIC_ENABLE_ANALYTICS=true

# Analytics (optionnel)
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX
NEXT_PUBLIC_HOTJAR_ID=XXXXXXX
```

---

## 🗄️ DATABASE MIGRATIONS {#migrations}

### Workflow migrations

```bash
# 1. Créer migration (local)
alembic revision --autogenerate -m "Add new table"

# 2. Vérifier fichier généré
cat alembic/versions/xxxx_add_new_table.py

# 3. Tester en local
alembic upgrade head

# 4. Commit et push
git add alembic/versions/
git commit -m "db: Add new table migration"
git push origin main

# 5. Appliquer en production
# Se connecter à la DB production
export DATABASE_URL="postgresql://..."
alembic upgrade head
```

### Rollback migration

```bash
# Retour une version en arrière
alembic downgrade -1

# Retour à version spécifique
alembic downgrade <revision_id>

# Voir historique
alembic history
```

### Backup avant migration

```bash
# Backup Render PostgreSQL
# Dashboard → Database → Backups → Create Backup

# OU via CLI
pg_dump -h host -U user -d mathakine > backup_$(date +%Y%m%d).sql

# Restore si besoin
psql -h host -U user -d mathakine < backup_20251120.sql
```

---

## 📊 MONITORING {#monitoring}

### Render Dashboard

**Métriques disponibles :**
- CPU usage
- Memory usage
- Response time
- Error rate
- Requests per second

**Logs :**
```bash
# Voir logs en temps réel
# Dashboard → Service → Logs

# Filtrer logs
# Search: "error", "warning", "critical"
```

### Health Checks

#### Backend
```python
# enhanced_server.py
from starlette.responses import JSONResponse
from sqlalchemy import text

@app.route("/health")
async def health_check(request):
    """Health check endpoint"""
    try:
        # Check database
        db = request.state.db
        db.execute(text("SELECT 1"))
        
        return JSONResponse({
            "status": "healthy",
            "database": "connected",
            "version": "2.0.0"
        })
    except Exception as health_check_error:
        return JSONResponse({
            "status": "unhealthy",
            "error": str(health_check_error)
        }, status_code=503)
```

#### Frontend
```typescript
// frontend/app/api/health/route.ts
export async function GET() {
  try {
    // Check backend API
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_BASE_URL}/health`
    );
    
    if (!response.ok) {
      return Response.json(
        { status: 'unhealthy', backend: 'unreachable' },
        { status: 503 }
      );
    }
    
    return Response.json({ status: 'healthy' });
  } catch (error) {
    return Response.json(
      { status: 'unhealthy', error: error.message },
      { status: 503 }
    );
  }
}
```

### Alertes

**Render Notifications :**
1. Dashboard → Account Settings → Notifications
2. Configurer email/Slack
3. Activer alertes :
   - Deploy failed
   - Service down
   - High CPU/memory usage

### Performance Monitoring

**Outils recommandés :**
- **Sentry** : Error tracking
- **LogRocket** : Session replay
- **Google Analytics** : User analytics
- **Hotjar** : Heatmaps

---

## 🐛 TROUBLESHOOTING {#troubleshooting}

### Backend ne démarre pas

**Problème** : Build failed
```
Error: No module named 'fastapi'
```

**Solution** :
```bash
# Vérifier requirements.txt à la racine
# Render build depuis racine projet

# requirements.txt doit inclure toutes dépendances
fastapi
starlette
sqlalchemy
alembic
psycopg2-binary
...
```

**Problème** : Database connection failed
```
Error: could not connect to server
```

**Solution** :
```bash
# Vérifier DATABASE_URL dans Environment
# Format: postgresql://user:password@host:5432/dbname

# Vérifier que DB est dans même région
# Backend et DB doivent être dans Frankfurt
```

### Frontend ne charge pas

**Problème** : API calls fail (CORS)
```
Access to fetch blocked by CORS policy
```

**Solution** :
```python
# Backend: enhanced_server.py
ALLOWED_ORIGINS = [
    "https://mathakine-frontend.onrender.com",
    "http://localhost:3000"  # Pour dev
]

# Vérifier cookies
allow_credentials=True
```

**Problème** : 404 sur routes
```
404 Not Found
```

**Solution** :
```javascript
// next.config.js
module.exports = {
  trailingSlash: true,  // Important pour static export
  output: 'export',
};
```

### Database issues

**Problème** : Slow queries
```bash
# Activer query logging
# PostgreSQL Settings → Log Settings → log_statement = all

# Analyser slow queries
SELECT * FROM pg_stat_statements 
ORDER BY total_time DESC 
LIMIT 10;
```

**Solution** :
```python
# Ajouter indexes
# alembic/versions/xxx_add_indexes.py
def upgrade():
    op.create_index('idx_challenges_type', 'logic_challenges', ['challenge_type'])
    op.create_index('idx_challenges_age', 'logic_challenges', ['age_group'])
```

---

## 📚 RESSOURCES

- [Render Documentation](https://render.com/docs)
- [PostgreSQL on Render](https://render.com/docs/databases)
- [Static Sites on Render](https://render.com/docs/static-sites)
- [Architecture](../00-REFERENCE/ARCHITECTURE.md)
- [Troubleshooting](TROUBLESHOOTING.md)

---

**Bon déploiement !** 🚀🌐

