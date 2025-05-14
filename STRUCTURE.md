# Structure du Projet Mathakine

## Vue d'ensemble

```
mathakine/
├── app/              # Application principale
├── docs/            # Documentation
├── tests/           # Tests
├── scripts/         # Scripts utilitaires
└── services/        # Services métier
```

## Composants Principaux

### 📱 Application (`app/`)

```
app/
├── api/            # Endpoints API REST
├── core/           # Logique métier centrale
├── models/         # Modèles de données
├── services/       # Services applicatifs
├── templates/      # Templates HTML
└── utils/          # Utilitaires
```

### 📚 Documentation (`docs/`)

```
docs/
├── Core/           # Documentation principale
│   ├── QUICKSTART.md
│   ├── CONTRIBUTING.md
│   └── ARCHITECTURE_DIAGRAMS.md
├── Tech/           # Documentation technique
├── Features/       # Documentation fonctionnelle
└── assets/         # Ressources visuelles
```

### 🧪 Tests (`tests/`)

```
tests/
├── unit/          # Tests unitaires
├── integration/   # Tests d'intégration
├── e2e/           # Tests end-to-end
└── fixtures/      # Données de test
```

### 🛠 Scripts (`scripts/`)

```
scripts/
├── deployment/    # Scripts de déploiement
├── database/      # Scripts de base de données
└── utils/         # Scripts utilitaires
```

### 🔧 Services (`services/`)

```
services/
├── auth/          # Service d'authentification
├── exercises/     # Service des exercices
├── progress/      # Service de progression
└── analytics/     # Service d'analytique
```

## Fichiers Clés

- `mathakine_cli.py` : Point d'entrée CLI
- `enhanced_server.py` : Serveur principal
- `alembic.ini` : Configuration des migrations
- `requirements.txt` : Dépendances Python
- `.env` : Configuration environnement

## Technologies

### Backend
- FastAPI (API REST)
- SQLAlchemy (ORM)
- Alembic (Migrations)
- Redis (Cache)

### Frontend
- Jinja2 (Templates)
- TailwindCSS (Styles)
- Alpine.js (Interactivité)

### Tests
- pytest
- pytest-cov
- pytest-asyncio

### Outils
- Docker
- PostgreSQL
- Redis
- Prometheus

## Conventions

### Nommage
- Modules : `snake_case`
- Classes : `PascalCase`
- Fonctions : `snake_case`
- Constants : `UPPER_CASE`

### Structure des Commits
- feat: Nouvelles fonctionnalités
- fix: Corrections de bugs
- docs: Documentation
- style: Formatage
- refactor: Refactoring
- test: Tests
- chore: Maintenance

### Documentation
- Docstrings : Google style
- Markdown : Documentation
- Mermaid : Diagrammes

---

*Dernière mise à jour : 15 juin 2025* 