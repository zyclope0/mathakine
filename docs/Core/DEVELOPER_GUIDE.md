# Guide du développeur Mathakine

Ce guide complet fournit toutes les informations nécessaires pour les développeurs souhaitant travailler sur le projet Mathakine, une application éducative mathématique pour enfants avec thème Star Wars.

## Sommaire
1. [Démarrage rapide](#1-démarrage-rapide)
2. [Architecture du projet](#2-architecture-du-projet)
3. [Système d'authentification](#3-système-dauthentification)
4. [Référence API](#4-référence-api)
5. [Guide d'extension du projet](#5-guide-dextension-du-projet)
6. [Bonnes pratiques et normes de codage](#6-bonnes-pratiques-et-normes-de-codage)
7. [Déploiement](#7-déploiement)
8. [Résolution des problèmes courants](#8-résolution-des-problèmes-courants)

## 1. Démarrage rapide

### Prérequis

- Python 3.13 ou supérieur
- PostgreSQL 15+ (pour la production) ou SQLite (pour le développement)
- Gestionnaire de packages pip

### Installation

1. **Cloner le dépôt**
   ```bash
   git clone https://github.com/zyclope0/mathakine.git
   cd mathakine
   ```

2. **Créer un environnement virtuel**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurer les variables d'environnement**
   - Copier le fichier `.env.example` vers `.env`
   - Modifier les valeurs selon votre environnement
   ```bash
   cp .env.example .env
   ```

5. **Initialiser la base de données**
   ```bash
   python mathakine_cli.py init
   ```

6. **Lancer l'application**
   ```bash
   # Avec interface utilisateur
   python mathakine_cli.py run

   # Version API uniquement
   python mathakine_cli.py run --api-only
   ```

7. **Accéder à l'application**
   - Interface web: http://localhost:8000
   - Documentation API: http://localhost:8000/docs

### Configuration pour le développement

1. **Activer le mode développement**
   ```bash
   # Dans .env
   ENVIRONMENT=development
   DEBUG=True
   ```

2. **Configurer la base de données de développement**
   ```bash
   # Dans .env
   DATABASE_URL=sqlite:///./mathakine_dev.db
   ```

3. **Configurer les outils de développement**
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Lancer les tests**
   ```bash
   python mathakine_cli.py test
   ```

## 2. Architecture du projet

### Structure principale
```
mathakine/
├── app/                    # Application FastAPI (API REST pure)
│   ├── api/                # Endpoints API
│   ├── core/               # Configuration et utilitaires
│   ├── db/                 # Accès bases de données
│   ├── models/             # Modèles SQLAlchemy
│   ├── schemas/            # Schémas Pydantic
│   └── services/           # Logique métier
├── docs/                   # Documentation complète
├── logs/                   # Journaux applicatifs
├── migrations/             # Scripts de migration
├── scripts/                # Scripts utilitaires
├── static/                 # Fichiers statiques (CSS, JS)
├── templates/              # Templates HTML (Jinja2)
├── tests/                  # Tests (unitaires, API, intégration)
├── enhanced_server.py      # Serveur principal (UI + API)
├── mathakine_cli.py        # Interface en ligne de commande
└── app/main.py             # Point d'entrée API FastAPI
```

### Flux d'authentification et d'utilisation

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Client         │────►│  Authentification ───►│  API Sécurisée  │
│  (Navigateur)   │     │  (JWT Token)    │     │  (Endpoints)    │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## 3. Système d'authentification

### Vue d'ensemble

Le système d'authentification de Mathakine (surnommé "Les Cristaux d'Identité") est basé sur les tokens JWT (JSON Web Tokens), offrant :

- Inscription et création de compte
- Connexion et génération de tokens
- Gestion de sessions sans état via JWT
- Système de rôles utilisateurs hiérarchiques
- Middleware de sécurité pour protéger les routes

### Rôles utilisateurs

Mathakine utilise quatre rôles utilisateurs principaux, conformes à la thématique Star Wars :

1. **PADAWAN** : Utilisateur standard, accès de base à l'application
2. **MAÎTRE** : Enseignant ou créateur de contenu, peut créer des exercices
3. **GARDIEN** : Modérateur, avec des privilèges de gestion des utilisateurs et du contenu
4. **ARCHIVISTE** : Administrateur, accès complet à toutes les fonctionnalités

Ces rôles sont implémentés dans `app/models/user.py` en tant qu'énumération `UserRole`.

### Architecture technique

Le système d'authentification est réparti sur plusieurs fichiers :

- `app/core/security.py` : Utilitaires de sécurité (hachage de mots de passe, création de tokens)
- `app/services/auth_service.py` : Services d'authentification (vérification, création d'utilisateurs)
- `app/api/deps.py` : Dépendances FastAPI pour la vérification des tokens et des rôles
- `app/api/endpoints/auth.py` : Endpoints d'API pour l'authentification
- `app/api/endpoints/users.py` : Endpoints de gestion des utilisateurs
- `app/schemas/user.py` : Schémas Pydantic pour la validation des données utilisateur

### Configuration

Les paramètres de sécurité sont définis dans plusieurs endroits :

1. Dans `app/core/config.py` :
   ```python
   # JWT Security
   SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
   ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24 * 7))  # 7 jours
   ```

2. Dans `app/core/constants.py` :
   ```python
   class SecurityConfig:
       TOKEN_EXPIRY_MINUTES = 60 * 24 * 7  # 7 jours
       ALGORITHM = "HS256"
       ACCESS_TOKEN_EXPIRE_MINUTES = 30
   ```

Il est recommandé de définir une clé secrète forte via la variable d'environnement `SECRET_KEY` en production.

### Fonctionnement du système JWT

#### 1. Création d'un utilisateur

```
POST /api/users/
{
    "username": "luke_skywalker",
    "email": "luke@jedi-temple.sw",
    "password": "StrongPassword123",
    "full_name": "Luke Skywalker",
    "role": "padawan"  # Optionnel, "padawan" par défaut
}
```

Le mot de passe est haché via bcrypt avant d'être stocké en base de données.

#### 2. Authentification et obtention d'un token

```
POST /api/auth/login
{
    "username": "luke_skywalker",
    "password": "StrongPassword123"
}
```

Réponse :
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
}
```

#### 3. Utilisation du token pour les requêtes authentifiées

Pour toutes les routes protégées, incluez l'en-tête d'autorisation :

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### 4. Récupération de l'utilisateur actuel

```
GET /api/auth/me
```

Retourne les informations de l'utilisateur connecté.

### Protection des routes et vérification des rôles

Pour protéger une route, utilisez les dépendances définies dans `app/api/deps.py` :

```python
# Route accessible à tout utilisateur connecté
@router.get("/protected")
def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello, {current_user.username}!"}

# Route accessible uniquement aux Maîtres
@router.post("/exercises")
def create_exercise(
    exercise_data: ExerciseCreate,
    current_user: User = Depends(get_current_maitre_user)
):
    # Créer un exercice...
    pass

# Route accessible uniquement aux Gardiens et Archivistes
@router.get("/users")
def list_users(
    current_user: User = Depends(get_current_gardien_or_archiviste)
):
    # Lister les utilisateurs...
    pass

# Route accessible uniquement aux Archivistes
@router.delete("/system/reset")
def reset_system(
    current_user: User = Depends(get_current_archiviste)
):
    # Réinitialiser le système...
    pass
```

### Structure des tokens JWT

Les tokens JWT contiennent les informations suivantes :

- **sub** : Nom d'utilisateur (sujet du token)
- **exp** : Date d'expiration du token
- **role** : Rôle de l'utilisateur

Ces informations sont encodées et signées avec la clé secrète, garantissant leur intégrité.

## 4. Référence API

### Documentation interactive

La documentation API interactive est disponible aux URLs suivantes :

- **Swagger UI** : `/api/docs` - Interface interactive avec possibilité de tester les endpoints
- **ReDoc** : `/api/redoc` - Documentation plus lisible et mieux organisée
- **OpenAPI JSON** : `/api/openapi.json` - Spécification OpenAPI au format JSON

### Authentification API

#### Obtention d'un token

```
POST /api/auth/login
```

**Corps de la requête** :
```json
{
  "username": "string",
  "password": "string"
}
```

**Réponse** (200 OK) :
```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

### Endpoints Utilisateurs

#### Liste des utilisateurs

```
GET /api/users/
```
- **Accès** : Gardien, Archiviste
- **Paramètres de requête** :
  - `skip` (int, défaut: 0) : Nombre d'éléments à sauter
  - `limit` (int, défaut: 100) : Nombre maximum d'éléments à retourner

#### Création d'un utilisateur

```
POST /api/users/
```
- **Accès** : Public (inscription)
- **Corps de la requête** : Détails de l'utilisateur à créer

#### Informations sur l'utilisateur courant

```
GET /api/users/me
```
- **Accès** : Utilisateur authentifié
- **Réponse** : Détails de l'utilisateur connecté

### Endpoints Exercices

#### Liste des exercices

```
GET /api/exercises/
```
- **Accès** : Public
- **Paramètres de requête** :
  - `skip` (int, défaut: 0) : Nombre d'éléments à sauter
  - `limit` (int, défaut: 100) : Nombre maximum d'éléments à retourner
  - `exercise_type` (string, optionnel) : Type d'exercice
  - `difficulty` (string, optionnel) : Niveau de difficulté

#### Création d'un exercice

```
POST /api/exercises/
```
- **Accès** : Gardien, Archiviste
- **Corps de la requête** : Détails de l'exercice

#### Soumettre une réponse

```
POST /api/exercises/{exercise_id}/submit
```
- **Accès** : Utilisateur authentifié
- **Paramètres de chemin** :
  - `exercise_id` (int) : ID de l'exercice
- **Corps de la requête** :
```json
{
  "answer": "string"
}
```

#### Générer un exercice

```
GET /api/exercises/generate
```
- **Paramètres de requête** :
  - `exercise_type` (string, optionnel) : Type d'exercice
  - `difficulty` (string, optionnel) : Niveau de difficulté
  - `use_ai` (bool, défaut: false) : Utiliser l'IA pour la génération

### Endpoints Défis Logiques

#### Liste des défis logiques

```
GET /api/challenges/
```
- **Paramètres de requête** :
  - `skip` (int, défaut: 0) : Nombre d'éléments à sauter
  - `limit` (int, défaut: 100) : Nombre maximum d'éléments à retourner
  - `challenge_type` (string, optionnel) : Type de défi
  - `age_group` (string, optionnel) : Groupe d'âge cible
  - `active_only` (bool, défaut: true) : Ne retourner que les défis actifs

#### Tenter de résoudre un défi

```
POST /api/challenges/{challenge_id}/attempt
```
- **Accès** : Utilisateur authentifié
- **Paramètres de chemin** :
  - `challenge_id` (int) : ID du défi logique
- **Corps de la requête** :
```json
{
  "answer": "string"
}
```

#### Obtenir un indice

```
GET /api/challenges/{challenge_id}/hint
```
- **Accès** : Utilisateur authentifié
- **Paramètres de chemin** :
  - `challenge_id` (int) : ID du défi logique
- **Paramètres de requête** :
  - `level` (int, défaut: 1) : Niveau d'indice (1-3)

### Pagination et filtrage

La plupart des endpoints de liste supportent :

- **Pagination** via les paramètres `skip` et `limit`
- **Filtrage** via des paramètres spécifiques (ex: `exercise_type`, `difficulty`)
- **Tri** via le paramètre `sort_by` (sur certains endpoints)

Pour la liste complète des endpoints API, consultez la documentation interactive (`/api/docs`).

## 5. Guide d'extension du projet

### Ajouter un nouveau type d'exercice

1. **Mettre à jour les constantes**

   Ouvrez `app/core/constants.py` et ajoutez le nouveau type d'exercice:

   ```python
   class ExerciseTypes:
       ADDITION = "addition"
       SUBTRACTION = "subtraction"
       MULTIPLICATION = "multiplication"
       DIVISION = "division"
       NEW_TYPE = "nouveau_type"  # Ajoutez votre nouveau type ici
   ```

2. **Ajouter la logique de génération**

   Créez ou modifiez la fonction de génération dans `enhanced_server.py`:

   ```python
   def generate_new_type_exercise(difficulty):
       """Génère un exercice de type nouveau_type"""
       # Obtenir les limites numériques en fonction du niveau de difficulté
       min_val, max_val = DIFFICULTY_LIMITS.get(difficulty, (1, 10))
       
       # Générer les opérandes en fonction des limites
       operand1 = random.randint(min_val, max_val)
       operand2 = random.randint(min_val, max_val)
       
       # Calculer la réponse correcte
       correct_answer = perform_operation(operand1, operand2)
       
       # Générer les fausses réponses
       choices = generate_choices(correct_answer, min_val, max_val)
       
       # Créer la question
       question = f"{operand1} opération {operand2} = ?"
       
       return {
           "exercise_type": ExerciseTypes.NEW_TYPE,
           "difficulty": difficulty,
           "question": question,
           "correct_answer": str(correct_answer),
           "choices": json.dumps(choices),
           "explanation": f"Explication de l'opération {operand1} opération {operand2} = {correct_answer}"
       }
   ```

3. **Mettre à jour le routeur de génération**

   Dans `enhanced_server.py`, modifiez la fonction `generate_exercise`:

   ```python
   async def generate_exercise(request):
       # Récupération des paramètres...
       
       # Sélection du générateur en fonction du type d'exercice
       if exercise_type == ExerciseTypes.ADDITION:
           exercise_data = generate_addition_exercise(difficulty)
       elif exercise_type == ExerciseTypes.SUBTRACTION:
           exercise_data = generate_subtraction_exercise(difficulty)
       # ...autres types existants
       elif exercise_type == ExerciseTypes.NEW_TYPE:
           exercise_data = generate_new_type_exercise(difficulty)
       else:
           return JSONResponse({"error": f"Type d'exercice non pris en charge: {exercise_type}"}, status_code=400)
       
       # Suite du code...
   ```

4. **Mettre à jour l'interface utilisateur**

   Ajoutez une option pour le nouveau type d'exercice dans `templates/exercises.html`.

5. **Mettre à jour les messages**

   Ajoutez les textes correspondants dans `app/core/messages.py`.

6. **Tester votre nouveau type d'exercice**

   Créez un test dans `tests/unit/test_exercise_generators.py`.

### Ajouter un nouvel endpoint API

1. **Créer le nouveau endpoint dans app/api/endpoints/**

   Par exemple, pour un endpoint de statistiques avancées, créez `app/api/endpoints/analytics.py`:

   ```python
   from fastapi import APIRouter, Depends, HTTPException
   from sqlalchemy.orm import Session
   from ...db.session import get_db
   from ...schemas.analytics import AnalyticsResponse
   from ...services.analytics_service import get_advanced_analytics
   
   router = APIRouter(
       prefix="/analytics",
       tags=["analytics"],
       responses={404: {"description": "Non trouvé"}}
   )
   
   @router.get("/advanced", response_model=AnalyticsResponse)
   def read_advanced_analytics(db: Session = Depends(get_db)):
       """
       Récupère des statistiques avancées sur les performances des utilisateurs
       """
       try:
           return get_advanced_analytics(db)
       except Exception as e:
           raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")
   ```

2. **Créer le schéma correspondant**

   Créez `app/schemas/analytics.py` pour définir le format de données.

3. **Implémenter le service**

   Créez `app/services/analytics_service.py` pour la logique métier.

4. **Enregistrer le router**

   Dans `app/api/api.py`, ajoutez:

   ```python
   from fastapi import APIRouter
   from .endpoints import exercises, users, challenges, auth, analytics  # Ajoutez analytics ici
   
   api_router = APIRouter()
   api_router.include_router(exercises.router)
   api_router.include_router(users.router)
   api_router.include_router(challenges.router)
   api_router.include_router(auth.router)
   api_router.include_router(analytics.router)  # Ajoutez cette ligne
   ```

5. **Tester le nouvel endpoint**

   Créez un test dans `tests/api/test_analytics.py`.

### Ajouter une nouvelle table dans la base de données

1. **Créer le modèle**

   Créez `app/models/feedback.py` avec la définition de la table.

2. **Mettre à jour les modèles associés**

   Ajoutez les relations nécessaires dans les modèles existants.

3. **Créer le schéma Pydantic**

   Créez `app/schemas/feedback.py` pour la validation des données.

4. **Mettre à jour la fonction d'initialisation de la base de données**

   Dans `app/db/init_db.py`, assurez-vous que les nouvelles tables sont créées.

5. **Créer les requêtes SQL centralisées**

   Dans `app/db/queries.py`, ajoutez les requêtes nécessaires.

6. **Créer les endpoints API**

   Créez `app/api/endpoints/feedback.py` avec les opérations CRUD appropriées.

7. **Mettre à jour le script de migration (si nécessaire)**

   Si vous utilisez des scripts de migration, créez-en un nouveau dans `migrations/`.

## 6. Bonnes pratiques et normes de codage

### Style de code

- Suivez la PEP 8 pour le style de code Python
- Utilisez les outils de formatage automatique (Black, isort)
- Limitez la longueur des lignes à 88 caractères (standard Black)

### Documentation

- Documentez toutes les fonctions avec des docstrings
- Utilisez le format de documentation Google pour les docstrings
- Mettez à jour la documentation de l'API lors de l'ajout de nouveaux endpoints

### Tests

- Créez des tests pour toutes les nouvelles fonctionnalités
- Visez une couverture de test d'au moins 80%
- Utilisez pytest pour exécuter les tests

### Gestion des erreurs

- Utilisez des blocs try/except appropriés
- Journalisez les erreurs avec suffisamment de contexte
- Retournez des codes HTTP et des messages d'erreur appropriés

### Sécurité

1. **En développement** :
   - Utilisez des mots de passe forts, même pour les comptes de test
   - Ne commitez jamais de clés secrètes dans le dépôt

2. **En production** :
   - Définissez une clé secrète forte via la variable d'environnement `SECRET_KEY`
   - Utilisez HTTPS pour toutes les communications
   - Définissez une durée de vie appropriée pour les tokens (7 jours par défaut)
   - Surveillez les journaux d'authentification pour détecter les activités suspectes

3. **Pour les développeurs** :
   - N'exposez jamais les mots de passe hachés dans les réponses API
   - Utilisez les dépendances FastAPI pour vérifier les autorisations
   - Testez les cas limites (token expiré, mauvais rôle, etc.)

## 7. Déploiement

### Déploiement sur Render

1. **Créer un nouveau service Web**:
   - Lier au dépôt GitHub
   - Type: Web Service
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app.main:app -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$PORT`

2. **Configurer les variables d'environnement**:
   - DATABASE_URL: URL PostgreSQL fournie par Render
   - ENVIRONMENT: production
   - SECRET_KEY: Une clé secrète forte

### Déploiement avec Docker

1. **Construire l'image**:
   ```bash
   docker build -t mathakine:latest .
   ```

2. **Exécuter le conteneur**:
   ```bash
   docker run -d -p 8000:8000 \
     -e DATABASE_URL=postgres://user:password@db:5432/mathakine \
     -e SECRET_KEY=votre_cle_secrete \
     -e ENVIRONMENT=production \
     --name mathakine-app \
     mathakine:latest
   ```

## 8. Résolution des problèmes courants

Pour une liste complète des problèmes courants et leurs solutions, consultez le document [CORRECTIONS_ET_MAINTENANCE.md](../CORRECTIONS_ET_MAINTENANCE.md).

---

*Ce document consolidé remplace les anciens documents GUIDE_DEVELOPPEUR.md, AUTH_GUIDE.md et API_REFERENCE.md.*
*Dernière mise à jour : 14 Mai 2025* 