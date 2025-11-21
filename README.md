# 🎓 Mathakine - Plateforme Éducative Mathématique

**Version** : 2.0.0  
**Date** : 20 novembre 2025  
**Statut** : 🟢 Production Ready

---

## 📚 Documentation

**🎯 Point d'entrée** : [**docs/INDEX.md**](docs/INDEX.md) ⭐

### Documents essentiels
- **[Getting Started](docs/00-REFERENCE/GETTING_STARTED.md)** - Installation 15 min
- **[Architecture](docs/00-REFERENCE/ARCHITECTURE.md)** - Vue d'ensemble technique
- **[API Reference](docs/00-REFERENCE/API.md)** - 37 routes documentées

### Par besoin
- **Développer** : [Development Guide](docs/01-GUIDES/DEVELOPMENT.md)
- **Déployer** : [Deployment Guide](docs/01-GUIDES/DEPLOYMENT.md)
- **Tester** : [Testing Guide](docs/01-GUIDES/TESTING.md)
- **Problème** : [Troubleshooting](docs/01-GUIDES/TROUBLESHOOTING.md)

---

## 🚀 À propos

**Mathakine** est une plateforme éducative mathématique conçue pour les enfants autistes, offrant une expérience d'apprentissage personnalisée et engageante.

### Mission
Rendre les mathématiques accessibles et amusantes pour tous les enfants, en particulier ceux avec des besoins spéciaux.

---

## ⚡ Installation Rapide

```bash
# 1. Cloner
git clone https://github.com/yourusername/mathakine.git
cd mathakine

# 2. Backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp sample.env .env
python enhanced_server.py

# 3. Frontend
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

✅ **Frontend** : http://localhost:3000  
✅ **Backend** : http://localhost:8000

**Guide complet** : [Getting Started](docs/00-REFERENCE/GETTING_STARTED.md)

---

## 🏗️ Architecture

```
Frontend Next.js (localhost:3000)
    ↓ REST API + SSE
Backend Starlette API (localhost:8000)
    ↓ SQLAlchemy ORM
PostgreSQL Database
```

- **Frontend** : Next.js 16, React 19, TypeScript, Tailwind CSS, shadcn/ui
- **Backend** : Starlette (API JSON pure, 37 routes), Python 3.11
- **Database** : PostgreSQL 15 (prod) / SQLite (dev)

**Détails** : [Architecture](docs/00-REFERENCE/ARCHITECTURE.md)

---

## 📊 État du Projet

### Qualité Code (Nov 2025)
- **Dette technique** : 🟢 FAIBLE (-80%)
- **Tests** : 42 fichiers, 60%+ coverage
- **CI/CD** : ✅ GitHub Actions
- **Code** : 95%+ lisibilité

### Phases Complétées (19-20 Nov 2025)
✅ **Phase 1** : Nettoyage code mort (-130 lignes)  
✅ **Phase 2** : Backend 100% API (-389 lignes)  
✅ **Phase 3** : Constants centralisées (DRY)  
✅ **Phase 4** : Services ORM unifiés  
✅ **Phase 5** : Tests automatisés (CI/CD)  
✅ **Phase 6** : Nommage & Lisibilité (+95%)

**Bilan** : [BILAN_COMPLET.md](docs/03-PROJECT/BILAN_COMPLET.md)

---

## 🛠️ Technologies

**Frontend**
- Next.js 16 (App Router)
- React 19 + TypeScript 5
- Tailwind CSS 4 + shadcn/ui
- TanStack Query + Zustand
- next-intl (i18n FR/EN)

**Backend**
- Python 3.11
- Starlette + FastAPI
- SQLAlchemy 2.0 (ORM)
- PostgreSQL 15
- Alembic (migrations)

**DevOps**
- GitHub Actions (CI/CD)
- Render (hosting)
- Docker
- Pytest + Codecov

---

## 📁 Structure

```
mathakine/
├── frontend/              # Next.js app
│   ├── app/              # App Router pages
│   ├── components/       # React components
│   └── lib/              # Utilities
├── app/                   # FastAPI
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic (ORM)
│   └── api/endpoints/    # API endpoints
├── server/                # Starlette (API JSON)
│   ├── handlers/         # Request handlers
│   ├── routes.py         # 37 routes API
│   └── auth.py           # Auth centralisé
├── tests/                 # Tests (42 fichiers)
├── docs/                  # Documentation ⭐
│   ├── 00-REFERENCE/     # Docs de référence
│   ├── 01-GUIDES/        # Guides pratiques
│   ├── 02-FEATURES/      # Fonctionnalités
│   ├── 03-PROJECT/       # Gestion projet
│   └── INDEX.md          # Index complet
└── .github/workflows/     # CI/CD
```

---

## 🧪 Tests

```bash
# Backend
pytest tests/ -v                    # Tous les tests
pytest tests/ -v -m critical        # Tests critiques
pytest tests/ --cov --cov-report=html  # Avec coverage

# Frontend
cd frontend
npm run test        # Tests unitaires
npm run test:e2e    # Tests E2E
npm run build       # Build production
```

---

## 🚢 Déploiement

### Production (Render)
- **Frontend** : https://mathakine-frontend.onrender.com/
- **Backend** : https://mathakine-backend.onrender.com/

### Guide complet
[Deployment Guide](docs/01-GUIDES/DEPLOYMENT.md)

---

## 🤝 Contribution

Contributions bienvenues ! 🎉

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit (`git commit -m 'Add AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

**Guide** : [Contributing](docs/01-GUIDES/CONTRIBUTING.md)

---

## 📖 Ressources

### Documentation
- **[Index Documentation](docs/INDEX.md)** ⭐ - Point d'entrée complet
- **[Architecture](docs/00-REFERENCE/ARCHITECTURE.md)** - Architecture technique
- **[API Reference](docs/00-REFERENCE/API.md)** - 37 routes API
- **[Glossaire](docs/00-REFERENCE/GLOSSARY.md)** - Terminologie

### Guides
- **[Getting Started](docs/00-REFERENCE/GETTING_STARTED.md)** - Installation
- **[Development](docs/01-GUIDES/DEVELOPMENT.md)** - Développement
- **[Testing](docs/01-GUIDES/TESTING.md)** - Tests
- **[FAQ](docs/01-GUIDES/FAQ.md)** - Questions fréquentes

### Projet
- **[Roadmap](docs/03-PROJECT/ROADMAP.md)** - Feuille de route
- **[Changelog](docs/03-PROJECT/CHANGELOG.md)** - Historique versions
- **[Bilan Phases](docs/03-PROJECT/BILAN_COMPLET.md)** - Refactoring 2025

---

## 💡 Support

- **Documentation** : [docs/INDEX.md](docs/INDEX.md)
- **Issues** : [GitHub Issues](https://github.com/yourusername/mathakine/issues)
- **Discussions** : [GitHub Discussions](https://github.com/yourusername/mathakine/discussions)

---

## 📜 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 🎯 Quick Links

| Besoin | Lien |
|--------|------|
| 🚀 Démarrer | [Getting Started](docs/00-REFERENCE/GETTING_STARTED.md) |
| 🏗️ Architecture | [Architecture](docs/00-REFERENCE/ARCHITECTURE.md) |
| 🔌 API | [API Reference](docs/00-REFERENCE/API.md) |
| 💻 Dev | [Development Guide](docs/01-GUIDES/DEVELOPMENT.md) |
| 🧪 Tests | [Testing Guide](docs/01-GUIDES/TESTING.md) |
| 🚢 Deploy | [Deployment Guide](docs/01-GUIDES/DEPLOYMENT.md) |
| ❓ Aide | [FAQ](docs/01-GUIDES/FAQ.md) / [Troubleshooting](docs/01-GUIDES/TROUBLESHOOTING.md) |
| 📚 Documentation complète | [INDEX.md](docs/INDEX.md) ⭐ |

---

**Made with ❤️ for children with special needs**

**Version 2.0.0** - Production Ready (Nov 2025)
