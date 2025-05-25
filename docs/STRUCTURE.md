# Structure du Projet Mathakine

## Organisation des Répertoires

```
mathakine/
├── app/                    # Application FastAPI principale
│   ├── api/               # Endpoints API REST
│   ├── core/             # Configuration et utilitaires
│   ├── models/           # Modèles SQLAlchemy
│   ├── schemas/          # Schémas Pydantic
│   └── services/         # Services métier
├── server/               # Serveur Starlette avec interface web
│   ├── handlers/         # Handlers API modulaires
│   │   ├── exercise_handlers.py  # Gestion des exercices
│   │   └── user_handlers.py      # Gestion utilisateurs/stats
│   ├── views/            # Vues pour les pages HTML
│   ├── api_routes.py     # Configuration des routes API
│   └── routes.py         # Configuration des routes principales
├── static/               # Fichiers statiques (CSS, JS)
├── templates/            # Templates HTML Jinja2
├── tests/               # Tests par niveau
└── docs/                # Documentation
```

## Composants Principaux

### 1. Application FastAPI (app/)
[... existant ...]

### 2. Serveur Starlette (server/)

#### 2.1 Handlers API (`server/handlers/`)
Module dédié à la logique de traitement des requêtes API, organisé par domaine fonctionnel :

**Exercise Handlers** (`exercise_handlers.py`):
- `generate_exercise`: Génération d'exercices (standard/IA)
- `get_exercise`: Récupération par ID
- `submit_answer`: Validation des réponses
- `get_exercises_list`: Liste paginée des exercices

**User Handlers** (`user_handlers.py`):
- `get_user_stats`: Statistiques et tableaux de bord utilisateur
  - Statistiques globales
  - Performance par type d'exercice
  - Données de progression

#### 2.2 Routes (`routes.py` et `api_routes.py`)
- Configuration centralisée des routes
- Association routes/handlers
- Gestion des méthodes HTTP
- Montage des fichiers statiques

[... reste du document existant ...]

## Patterns de Développement

### Modularisation des Handlers
- Séparation par domaine fonctionnel
- Un module = une responsabilité
- Réutilisation facilitée
- Tests unitaires simplifiés

### Gestion des Sessions
- Utilisation systématique de `EnhancedServerAdapter`
- Pattern try/finally pour la fermeture des sessions
- Gestion centralisée des erreurs

[... reste du document existant ...] 