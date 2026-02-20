# 🎓 Mathakine - Plateforme Éducative Mathématique

**Plateforme d'apprentissage mathématique adaptative avec IA générative**

[![Version](https://img.shields.io/badge/version-2.1.0-blue.svg)](https://github.com/zyclope0/mathakine)
[![Statut](https://img.shields.io/badge/statut-production-brightgreen.svg)](https://github.com/zyclope0/mathakine)
[![Licence](https://img.shields.io/badge/licence-MIT-green.svg)](LICENSE)

---

## 📖 À propos

**Mathakine** est une plateforme éducative mathématique interactive conçue pour offrir une expérience d'apprentissage personnalisée et engageante, particulièrement adaptée aux enfants avec besoins spéciaux.

### ✨ Fonctionnalités principales

- 🎯 **Exercices mathématiques adaptatifs** (addition, soustraction, multiplication, division)
- 🧩 **Défis logiques IA** (patterns, séquences, énigmes, graphes, visuels)
- 🏆 **Système de badges** et récompenses
- 📊 **Suivi de progression** (séries, précision, statistiques)
- 🤖 **Génération IA** (OpenAI GPT-5.x)
- 🌐 **Multilingue** (Français / Anglais)
- 🎨 **Multi-thème** (clair/sombre/système)
- ♿ **Accessible** (WCAG 2.1 AA, animations adaptatives)

---

## 📚 Documentation

**🎯 Point d'entrée principal** : [**docs/INDEX.md**](docs/INDEX.md) ⭐

### Documents essentiels

| Document | Description | Priorité |
|----------|-------------|----------|
| **[README_TECH.md](README_TECH.md)** | Documentation technique complète (48 endpoints, architecture, stack) | 🔴 Élevée |
| **[docs/INDEX.md](docs/INDEX.md)** | Index navigation documentation | 🔴 Élevée |
| **[docs/00-REFERENCE/GETTING_STARTED.md](docs/00-REFERENCE/GETTING_STARTED.md)** | Installation pas-à-pas | 🔴 Élevée |
| **[docs/01-GUIDES/DEVELOPMENT.md](docs/01-GUIDES/DEVELOPMENT.md)** | Workflow développement | 🟡 Moyenne |
| **[docs/01-GUIDES/TESTING.md](docs/01-GUIDES/TESTING.md)** | Guide tests | 🟡 Moyenne |
| **[docs/01-GUIDES/TROUBLESHOOTING.md](docs/01-GUIDES/TROUBLESHOOTING.md)** | Dépannage | 🟢 Basse |

---

## ⚡ Installation Rapide (15 min)

### Prérequis

- **Python** 3.12+ ([télécharger](https://www.python.org/downloads/))
- **Node.js** 18.17+ ([télécharger](https://nodejs.org/))
- **PostgreSQL** 15+ ([télécharger](https://www.postgresql.org/download/)) OU SQLite (dev)
- **Git** ([télécharger](https://git-scm.com/downloads))

### Installation

```bash
# 1. Cloner le projet
git clone https://github.com/zyclope0/mathakine.git
cd mathakine

# 2. Configuration backend
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt

# 3. Variables d'environnement
cp .env.example .env
# Éditer .env avec vos clés API (DATABASE_URL, SECRET_KEY, OPENAI_API_KEY)

# 4. Base de données
alembic upgrade head

# 5. Lancer backend (port 10000)
python enhanced_server.py

# 6. Configuration frontend (nouveau terminal)
cd frontend
npm install
cp .env.example .env.local
# Éditer .env.local (NEXT_PUBLIC_API_BASE_URL=http://localhost:10000)

# 7. Lancer frontend (port 3000)
npm run dev
```

**✅ Application disponible** : http://localhost:3000  
**✅ API backend** : http://localhost:10000

**Guide détaillé** : [GETTING_STARTED.md](docs/00-REFERENCE/GETTING_STARTED.md)

---

## 🏗️ Architecture

### Vue d'ensemble

```
┌─────────────────────────────────────────┐
│  Frontend Next.js (localhost:3000)      │
│  • React 19 + TypeScript                │
│  • Tailwind CSS + shadcn/ui             │
│  • React Query (cache)                  │
│  • next-intl (i18n FR/EN)               │
└──────────────┬──────────────────────────┘
               │ REST API + SSE
               ↓
┌─────────────────────────────────────────┐
│  Backend Starlette (localhost:10000)    │
│  • 48 routes API                        │
│  • Handlers + middleware                │
│  • SSE streaming (IA)                   │
│  • Auth JWT (cookies + Bearer)          │
└──────────────┬──────────────────────────┘
               │
    ┌──────────┴──────────┐
    ↓                     ↓
┌──────────┐        ┌────────────┐
│ Services │        │  OpenAI    │
│ (logique)│        │  GPT-5.x   │
└────┬─────┘        └────────────┘
     │ SQLAlchemy ORM
     ↓
┌──────────────┐
│  PostgreSQL  │
│  (prod/dev)  │
└──────────────┘
```

### Stack technique

**Frontend**
- **Framework** : Next.js 16.1.6 (App Router)
- **UI** : React 19.2.0, TypeScript 5.x
- **Styling** : Tailwind CSS 4.x, shadcn/ui
- **State** : TanStack Query 5.90.7, Zustand 5.0.8
- **i18n** : next-intl 4.4.0
- **Animations** : Framer Motion 12.23.24

**Backend**
- **Framework** : Starlette 0.49.3 (API pure, FastAPI archivé 06/02/2026)
- **Python** : 3.12+
- **ORM** : SQLAlchemy 2.0.44
- **BDD** : PostgreSQL 15+ (prod), SQLite (dev)
- **Migrations** : Alembic 1.13.1
- **Auth** : JWT (python-jose) + Bcrypt
- **IA** : OpenAI 1.12.0 (GPT-5.1, GPT-5-mini, GPT-5.2)
- **Logs** : Loguru

**DevOps**
- **Tests** : Pytest (backend), Vitest (frontend), Playwright (E2E)
- **CI/CD** : GitHub Actions
- **Hosting** : Render (prod)
- **Conteneurisation** : Docker

**Documentation technique complète** : [README_TECH.md](README_TECH.md)

---

## 📁 Structure du Projet

```
mathakine/
├── frontend/                 # Next.js App Router
│   ├── app/                 # Pages (dashboard, exercises, challenges, profile)
│   ├── components/          # Composants React (ui/, dashboard/, auth/, etc.)
│   ├── hooks/               # 16 hooks React Query
│   ├── lib/                 # Utilitaires (api/, stores/)
│   ├── messages/            # i18n (fr.json, en.json)
│   └── public/              # Assets statiques
│
├── server/                   # Backend Starlette (couche HTTP)
│   ├── handlers/            # 7 handlers (auth, user, exercise, challenge, etc.)
│   ├── routes.py            # 48 routes API
│   ├── auth.py              # Authentification centralisée
│   ├── middleware.py        # CORS, logging, rate limiting
│   └── app.py               # App Starlette
│
├── app/                      # Backend logique métier (indépendant HTTP)
│   ├── models/              # SQLAlchemy ORM (7 tables)
│   ├── schemas/             # Pydantic validation
│   ├── services/            # Business logic (CRUD + logique métier)
│   ├── core/                # Config (settings, ai_config, logging)
│   └── utils/               # Utilitaires (rate_limiter, prompt_sanitizer, etc.)
│
├── tests/                    # Tests (pytest, vitest, playwright)
├── docs/                     # Documentation (voir docs/INDEX.md)
├── alembic/                  # Migrations DB
├── _ARCHIVE_2026/           # Code archivé (FastAPI, docs obsolètes)
├── enhanced_server.py       # Point d'entrée backend
└── requirements.txt         # Dépendances Python
```

---

## 🧪 Tests

### Backend (Python - Pytest)

```bash
# Tous les tests
pytest tests/ -v

# Tests critiques seulement
pytest tests/ -v -m critical

# Avec coverage
pytest tests/ --cov --cov-report=html

# Tests spécifiques
pytest tests/test_auth.py -v
pytest tests/test_exercise_service.py -v
```

### Frontend (TypeScript - Vitest + Playwright)

```bash
cd frontend

# Tests unitaires
npm run test                 # Mode watch
npm run test:coverage        # Avec coverage

# Tests E2E
npm run test:e2e             # Headless
npm run test:e2e:ui          # Mode UI

# Build production (validation TypeScript)
npm run build
```

**Guide complet** : [docs/01-GUIDES/TESTING.md](docs/01-GUIDES/TESTING.md)

---

## 📊 État du Projet

### Qualité code (Février 2026)

- ✅ **Architecture unifiée** : Starlette pur (FastAPI archivé)
- ✅ **Documentation rationalisée** : -92% docs obsolètes
- ✅ **Tests** : 42 fichiers, 60%+ coverage
- ✅ **Dette technique** : Faible (imports lazy à optimiser)
- ✅ **Lisibilité** : 95%+ (nommage clair, code commenté)
- ✅ **Sécurité** : RGPD, OWASP, rate limiting, JWT

### Dernières mises à jour (12/02/2026)

- ✅ **Énigmes** : Rendu pots/plaque (formatage correct), masquage ascii_art redondant
- ✅ **Échecs** : Highlights sur pièces uniquement, tour/objectif, format réponse, prompt IA positions tactiques
- ✅ **Auth production** : Sync cookie cross-domain (login, refresh, avant génération IA), routes diagnostic
- ✅ **Unification backend** : Starlette pur (FastAPI archivé)
- ✅ **Widgets dashboard** : Série, Défis, Précision par catégorie
- ✅ **Documentation** : Rationalisée (~15 docs actifs)

**Historique complet** : [docs/INDEX.md](docs/INDEX.md) (section « Dernières mises à jour »)

---

## 🚀 Déploiement

### Environnements

- **Local** : http://localhost:3000 (frontend) + http://localhost:10000 (backend)
- **Production** : https://mathakine-frontend.onrender.com (frontend) + backend sur Render

### Variables d'environnement

**Backend (`.env`)**
```env
DATABASE_URL=postgresql://user:password@localhost/mathakine
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=sk-proj-xxx
PORT=10000
```

**Frontend (`frontend/.env.local`)**
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:10000
NEXT_PUBLIC_SITE_URL=http://localhost:3000
```

**Guide détaillé** : [docs/01-GUIDES/DEVELOPMENT.md](docs/01-GUIDES/DEVELOPMENT.md)

---

## 🤝 Contribution

Les contributions sont les bienvenues ! Veuillez suivre ces étapes :

1. **Lire** : [docs/01-GUIDES/CONTRIBUTING.md](docs/01-GUIDES/CONTRIBUTING.md)
2. **Fork** le projet
3. **Créer** une branche (`git checkout -b feature/amazing-feature`)
4. **Commit** vos changements (`git commit -m 'Add amazing feature'`)
5. **Push** vers la branche (`git push origin feature/amazing-feature`)
6. **Ouvrir** une Pull Request

**Conventions** :
- Code Python : PEP 8 + type hints
- Code TypeScript : ESLint + Prettier
- Messages de commit : Convention Conventional Commits
- Tests : Obligatoires pour nouvelles fonctionnalités

---

## 📜 Licence

Ce projet est sous licence **MIT** - voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 📧 Contact

**Projet** : [https://github.com/zyclope0/mathakine](https://github.com/zyclope0/mathakine)  
**Issues** : [https://github.com/zyclope0/mathakine/issues](https://github.com/zyclope0/mathakine/issues)

---

## 🙏 Remerciements

- [Next.js](https://nextjs.org/) - Framework React
- [Starlette](https://www.starlette.io/) - Framework ASGI Python
- [OpenAI](https://openai.com/) - Génération IA (GPT-5.x)
- [shadcn/ui](https://ui.shadcn.com/) - Composants UI
- [Tailwind CSS](https://tailwindcss.com/) - CSS utility-first

---

**Prêt à commencer ?** 🚀 Suivez le [guide d'installation](docs/00-REFERENCE/GETTING_STARTED.md) !

**Version** : 2.1.0 | **Dernière mise à jour** : 12/02/2026
