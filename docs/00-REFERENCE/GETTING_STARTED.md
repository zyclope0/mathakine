# 🚀 GETTING STARTED - MATHAKINE

**Version** : 2.0.0  
**Date** : 20 novembre 2025  
**Temps estimé** : 15-30 minutes

---

## 📋 PRÉREQUIS

### Logiciels requis
- **Node.js** 18+ (pour frontend)
- **Python** 3.12+ (pour backend)
- **PostgreSQL** 15+ (production) ou SQLite (dev)
- **Git**

### Connaissances recommandées
- Bases de Python et FastAPI/Starlette
- Bases de React et Next.js
- Bases de SQL
- Terminal/ligne de commande

---

## ⚡ INSTALLATION RAPIDE (5 MIN)

### 1. Cloner le repository
```bash
git clone https://github.com/yourusername/mathakine.git
cd mathakine
```

### 2. Backend (Starlette API)
```bash
# Créer environnement virtuel
python -m venv venv

# Activer (Windows)
venv\Scripts\activate
# OU (Mac/Linux)
source venv/bin/activate

# Installer dépendances
pip install -r requirements.txt

# Copier variables d'environnement
cp sample.env .env

# Créer base de données (SQLite dev)
python -m app.db.init_db

# Lancer serveur
python enhanced_server.py
```

✅ **Backend accessible** : http://localhost:8000

### 3. Frontend (Next.js)
```bash
cd frontend

# Installer dépendances
npm install

# Copier variables d'environnement
cp .env.example .env.local

# Lancer dev server
npm run dev
```

✅ **Frontend accessible** : http://localhost:3000

---

## 🔧 CONFIGURATION

### Variables d'environnement Backend (.env)
```bash
# Base de données (SQLite dev)
DATABASE_URL=sqlite:///./mathakine.db

# OU PostgreSQL (production)
# DATABASE_URL=postgresql://user:password@localhost:5432/mathakine

# Secret key (générer avec: python -c "import secrets; print(secrets.token_urlsafe(32))")
SECRET_KEY=your-secret-key-here

# CORS (frontend autorisé)
ALLOWED_ORIGINS=http://localhost:3000

# Logging
LOG_LEVEL=DEBUG

# OpenAI (optionnel, pour génération IA)
OPENAI_API_KEY=sk-...
```

### Variables d'environnement Frontend (.env.local)
```bash
# Backend API
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_API_URL=http://localhost:8000/api

# Feature flags
NEXT_PUBLIC_ENABLE_AI_GENERATION=true
```

---

## 📝 PREMIERS PAS

### 1. Créer un compte
```bash
# Via API
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"test123","role":"student"}'

# OU via interface
# Ouvrir http://localhost:3000/register
```

### 2. Se connecter
```bash
# Via API
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}'

# OU via interface
# Ouvrir http://localhost:3000/login
```

### 3. Tester les fonctionnalités
- **Exercises** : http://localhost:3000/exercises
- **Challenges** : http://localhost:3000/challenges
- **Dashboard** : http://localhost:3000/dashboard
- **Badges** : http://localhost:3000/badges

---

## 🧪 TESTS

### Backend
```bash
# Tous les tests
pytest tests/ -v

# Tests critiques uniquement
pytest tests/ -v -m critical

# Avec coverage
pytest tests/ -v --cov=app --cov=server --cov-report=html

# Voir coverage
open htmlcov/index.html
```

### Frontend
```bash
cd frontend

# Tests unitaires
npm run test

# Tests E2E
npm run test:e2e

# Build production
npm run build
```

---

## 🐛 TROUBLESHOOTING

### Backend ne démarre pas

**Problème** : `ImportError: No module named 'fastapi'`
```bash
# Solution : Réinstaller dépendances
pip install --upgrade -r requirements.txt
```

**Problème** : `sqlalchemy.exc.OperationalError: unable to open database file`
```bash
# Solution : Créer la base de données
python -m app.db.init_db
```

**Problème** : `ValueError: SECRET_KEY not set`
```bash
# Solution : Configurer .env
cp sample.env .env
# Éditer .env et générer une SECRET_KEY
```

### Frontend ne démarre pas

**Problème** : `Error: Cannot find module 'next'`
```bash
# Solution : Réinstaller node_modules
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Problème** : `Error: ECONNREFUSED 127.0.0.1:8000`
```bash
# Solution : Vérifier que le backend est lancé
# Dans un autre terminal :
python enhanced_server.py
```

### Port déjà utilisé

**Backend (8000)**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:8000 | xargs kill -9
```

**Frontend (3000)**
```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:3000 | xargs kill -9
```

---

## 📊 STRUCTURE DU PROJET

```
mathakine/
├── frontend/              # Next.js frontend
│   ├── app/              # App Router pages
│   ├── components/       # React components
│   ├── hooks/            # Custom hooks
│   ├── lib/              # Utilities
│   └── types/            # TypeScript types
│
├── app/                   # FastAPI app
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   ├── api/endpoints/    # API endpoints
│   └── core/             # Configuration
│
├── server/                # Starlette app (API JSON)
│   ├── handlers/         # Request handlers
│   ├── routes.py         # ~80 routes API
│   └── auth.py           # Auth centralisé
│
├── tests/                 # Tests
│   ├── api/              # Tests API
│   ├── unit/             # Tests unitaires
│   └── integration/      # Tests intégration
│
├── docs/                  # Documentation ⭐
│   ├── 00-REFERENCE/     # Documents de référence
│   ├── 01-GUIDES/        # Guides pratiques
│   ├── 02-FEATURES/      # Fonctionnalités
│   ├── 03-PROJECT/       # Gestion projet
│   └── 04-ARCHIVES/      # Archives
│
└── .github/workflows/     # CI/CD GitHub Actions
```

---

## 🎯 PROCHAINES ÉTAPES

### Pour les développeurs
1. **Lire l'architecture** : [`ARCHITECTURE.md`](ARCHITECTURE.md)
2. **Consulter l'API** : [`API.md`](API.md)
3. **Guide développement** : [`../01-GUIDES/DEVELOPMENT.md`](../01-GUIDES/DEVELOPMENT.md)
4. **Contribuer** : [`../01-GUIDES/CONTRIBUTING.md`](../01-GUIDES/CONTRIBUTING.md)

### Pour les contributeurs
1. **Roadmap** : [`../03-PROJECT/ROADMAP.md`](../03-PROJECT/ROADMAP.md)
2. **Changelog** : [`../03-PROJECT/CHANGELOG.md`](../03-PROJECT/CHANGELOG.md)
3. **Tests** : [`../01-GUIDES/TESTING.md`](../01-GUIDES/TESTING.md)

### Pour le déploiement
1. **Render** : [`../01-GUIDES/DEPLOYMENT.md`](../01-GUIDES/DEPLOYMENT.md)
2. **Docker** : [`../01-GUIDES/DOCKER.md`](../01-GUIDES/DOCKER.md)

---

## 💡 AIDE

### Documentation
- **Index complet** : [`../INDEX.md`](../INDEX.md)
- **Glossaire** : [`GLOSSARY.md`](GLOSSARY.md)
- **FAQ** : [`../01-GUIDES/FAQ.md`](../01-GUIDES/FAQ.md)

### Support
- **Issues GitHub** : https://github.com/yourusername/mathakine/issues
- **Discussions** : https://github.com/yourusername/mathakine/discussions

---

## ✅ CHECKLIST

Avant de commencer à développer, vérifier :

- [ ] Node.js 18+ installé
- [ ] Python 3.11+ installé
- [ ] PostgreSQL installé (ou SQLite pour dev)
- [ ] Backend démarré (http://localhost:8000)
- [ ] Frontend démarré (http://localhost:3000)
- [ ] Compte créé et connexion fonctionnelle
- [ ] Tests passent (`pytest tests/`)
- [ ] Documentation lue (ARCHITECTURE.md, API.md)

---

**Prêt à coder !** 🚀

**Besoin d'aide ?** Consultez [`../01-GUIDES/TROUBLESHOOTING.md`](../01-GUIDES/TROUBLESHOOTING.md)

