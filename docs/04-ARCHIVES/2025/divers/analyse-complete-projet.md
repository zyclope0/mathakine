# 📚 ANALYSE COMPLÈTE DU PROJET MATHAKINE - SYNTHÈSE EXHAUSTIVE

**Document de référence complet** - Analyse de A à Z du projet Mathakine  
*Date d'analyse : Janvier 2025*  
*Objectif : 95% de connaissance du projet*

---

## 🎯 **1. ESSENCE ET PHILOSOPHIE DU PROJET**

### **1.1 Mission et Vision**

**Mathakine** est une plateforme éducative mathématique immersive conçue spécifiquement pour les enfants autistes âgés de 6 à 16 ans, avec un thème Star Wars complet.

**Histoire personnelle** : Créé par un père pour son fils Anakin, 9 ans, passionné par les concours de mathélogique. Ce qui a commencé comme un projet personnel s'est transformé en une mission partagée pour offrir à tous les enfants une expérience d'apprentissage exceptionnelle.

**Valeurs fondamentales** :
- **Accessibilité** : Support complet pour différents besoins (dyslexie, photosensibilité, etc.)
- **Inclusivité** : Conception adaptée aux enfants autistes
- **Engagement** : Interface immersive avec gamification
- **Progression** : Système adaptatif selon le niveau et les capacités

### **1.2 Thème Star Wars**

Le projet utilise une terminologie Star Wars cohérente :
- **Padawans** = Apprenants
- **Épreuves Jedi** = Exercices mathématiques
- **Épreuves du Conseil Jedi** = Défis logiques
- **Cristaux d'Identité** = Système d'authentification JWT
- **Archives du Temple** = Système d'archivage
- **Rangs Jedi** = Niveaux de progression (Initié → Padawan → Chevalier → Maître)

---

## 🏗️ **2. ARCHITECTURE TECHNIQUE COMPLÈTE**

### **2.1 Architecture Dual-Backend**

Le projet utilise **deux backends complémentaires** :

#### **A. FastAPI (API REST Pure)**
- **Fichier** : `app/main.py`
- **Port** : 8081 (par défaut)
- **Usage** : API REST pour applications externes, tests, débogage
- **Documentation** : Swagger UI (`/api/docs`) et ReDoc (`/api/redoc`)
- **Caractéristiques** :
  - Endpoints REST standardisés
  - Validation Pydantic automatique
  - Authentification JWT
  - Middleware de sécurité (CORS, TrustedHost)
  - Logging des requêtes

#### **B. Starlette (Interface Web Complète)**
- **Fichier** : `enhanced_server.py` → `server/app.py`
- **Port** : 8000 (par défaut)
- **Usage** : Interface utilisateur web complète avec templates HTML
- **Caractéristiques** :
  - Templates Jinja2 pour rendu HTML
  - Gestion des sessions utilisateur
  - Routes web + API minimaliste
  - Intégration avec FastAPI pour logique métier

**Relation entre les deux** :
- Les deux partagent les mêmes modèles de données (`app/models/`)
- Les deux utilisent les mêmes services (`app/services/`)
- Starlette est optimisé pour l'expérience utilisateur
- FastAPI est optimisé pour les interactions programmatiques

### **2.2 Stack Technologique**

#### **Backend**
```yaml
Frameworks:
  - FastAPI 0.115.12 (API REST)
  - Starlette 0.31.1 (Interface web)
  - Uvicorn 0.23.2 (Serveur ASGI)

ORM & Base de données:
  - SQLAlchemy 2.0.40 (ORM)
  - PostgreSQL (production) / SQLite (développement)
  - Alembic 1.13.1 (Migrations)

Authentification:
  - python-jose[cryptography] 3.4.0 (JWT)
  - passlib[bcrypt] 1.7.4 (Hachage mots de passe)

Validation:
  - Pydantic 2.11.0 (Validation de données)
  - pydantic-settings 2.1.0 (Configuration)
```

#### **Frontend**
```yaml
Templates:
  - Jinja2 3.1.2 (Moteur de templates)

Styles:
  - CSS personnalisé avec système de variables
  - 16 fichiers CSS modulaires
  - Thème Star Wars holographique

JavaScript:
  - Vanilla JS avec modules ES6
  - Pas de framework (légèreté)

Accessibilité:
  - WCAG 2.1 AA compliant
  - Support lecteurs d'écran
  - Navigation clavier complète
```

#### **Infrastructure**
```yaml
Tests:
  - pytest 7.4.3
  - pytest-cov 4.1.0 (Couverture)
  - httpx 0.27.0 (Tests HTTP)
  - beautifulsoup4 4.12.2 (Parsing HTML)

CI/CD:
  - GitHub Actions
  - Hooks Git automatiques

Monitoring:
  - loguru 0.7.2 (Logging)
  - prometheus-client 0.19.0 (Métriques)
  - sentry-sdk 1.40.6 (Erreurs)
```

### **2.3 Structure des Répertoires**

```
mathakine/
├── app/                          # Application FastAPI (API REST)
│   ├── api/                     # Endpoints API
│   │   ├── endpoints/           # Endpoints par domaine
│   │   │   ├── auth.py          # Authentification
│   │   │   ├── exercises.py     # Exercices
│   │   │   ├── users.py         # Utilisateurs
│   │   │   └── challenges.py    # Défis logiques
│   │   ├── api.py               # Routeur principal
│   │   └── deps.py              # Dépendances (auth, DB)
│   ├── core/                    # Configuration centrale
│   │   ├── config.py            # Paramètres (Settings)
│   │   ├── constants.py         # Constantes (types, niveaux)
│   │   ├── security.py          # Sécurité (JWT, hash)
│   │   └── logging_config.py    # Configuration logs
│   ├── db/                      # Accès base de données
│   │   ├── base.py              # Base SQLAlchemy
│   │   ├── adapter.py           # Adaptateur unifié
│   │   ├── transaction.py       # Gestionnaire transactions
│   │   └── init_db.py           # Initialisation DB
│   ├── models/                  # Modèles SQLAlchemy
│   │   ├── user.py              # Utilisateurs
│   │   ├── exercise.py          # Exercices
│   │   ├── attempt.py           # Tentatives
│   │   ├── logic_challenge.py   # Défis logiques
│   │   ├── progress.py          # Progression
│   │   └── all_models.py        # Export centralisé
│   ├── schemas/                 # Schémas Pydantic
│   │   ├── user.py              # Validation utilisateurs
│   │   ├── exercise.py          # Validation exercices
│   │   └── ...
│   ├── services/                # Logique métier
│   │   ├── auth_service.py      # Authentification
│   │   ├── exercise_service.py  # Exercices
│   │   ├── user_service.py      # Utilisateurs
│   │   ├── logic_challenge_service.py
│   │   └── enhanced_server_adapter.py  # Adaptateur Starlette
│   └── main.py                  # Point d'entrée FastAPI
│
├── server/                       # Serveur Starlette (Interface web)
│   ├── app.py                   # Création application Starlette
│   ├── routes.py                # Configuration routes
│   ├── views.py                 # Vues HTML
│   ├── handlers/                # Handlers par domaine
│   │   ├── exercise_handlers.py
│   │   ├── user_handlers.py
│   │   └── badge_handlers.py
│   ├── middleware.py            # Middleware (auth, CORS)
│   ├── error_handlers.py        # Gestion erreurs
│   ├── template_handler.py     # Gestion templates
│   ├── database.py             # Initialisation DB
│   └── exercise_generator.py   # Générateur exercices
│
├── templates/                    # Templates HTML (Jinja2)
│   ├── base.html               # Template de base
│   ├── home.html               # Page d'accueil
│   ├── login.html              # Connexion
│   ├── exercises.html          # Liste exercices
│   ├── dashboard.html          # Tableau de bord
│   ├── profile.html            # Profil utilisateur
│   └── ...
│
├── static/                       # Fichiers statiques
│   ├── style.css               # Styles principaux
│   ├── space-theme-dark.css    # Thème Star Wars
│   ├── accessibility.css        # Accessibilité
│   ├── js/                      # JavaScript
│   └── img/                     # Images
│
├── tests/                        # Tests (4 niveaux)
│   ├── unit/                    # Tests unitaires
│   ├── api/                     # Tests API REST
│   ├── integration/             # Tests d'intégration
│   └── functional/              # Tests fonctionnels
│
├── docs/                         # Documentation complète
│   ├── architecture/            # Documentation technique
│   ├── development/             # Guides développeur
│   ├── features/                # Fonctionnalités
│   └── ...
│
├── scripts/                     # Scripts utilitaires
│   ├── setup_git_hooks.py      # Installation hooks Git
│   ├── pre_commit_check.py     # Vérification pre-commit
│   └── ...
│
├── migrations/                  # Migrations Alembic
│   └── versions/               # Versions de migration
│
├── enhanced_server.py           # Point d'entrée serveur Starlette
├── mathakine_cli.py            # CLI d'administration
└── requirements.txt             # Dépendances Python
```

---

## 📊 **3. MODÈLES DE DONNÉES**

### **3.1 Modèles Principaux**

#### **User (Utilisateurs)**
```python
# app/models/user.py
- id (PK)
- username (UNIQUE, indexé)
- email (UNIQUE, indexé)
- hashed_password
- full_name
- role (ENUM: PADAWAN, MAITRE, GARDIEN, ARCHIVISTE)
- is_active
- grade_level, learning_style, preferred_difficulty
- preferred_theme, accessibility_settings (JSON)
- total_points, current_level, experience_points, jedi_rank
- avatar_url
- created_at, updated_at

Relations:
- created_exercises (1:N)
- attempts (1:N)
- progress_records (1:N)
- recommendations (1:N)
- created_logic_challenges (1:N)
- user_achievements (1:N)
```

#### **Exercise (Exercices)**
```python
# app/models/exercise.py
- id (PK)
- title
- creator_id (FK → users.id)
- exercise_type (ENUM: ADDITION, SOUSTRACTION, MULTIPLICATION, DIVISION, 
                 FRACTIONS, GEOMETRIE, TEXTE, MIXTE, DIVERS)
- difficulty (ENUM: INITIE, PADAWAN, CHEVALIER, MAITRE)
- tags (String, séparés par virgules)
- age_group, context_theme, complexity
- ai_generated (Boolean)
- question (Text)
- correct_answer (String)
- choices (JSON)  # Options QCM
- explanation (Text)
- hint (Text)
- image_url, audio_url
- is_active, is_archived
- view_count
- created_at, updated_at

Relations:
- creator (N:1 → User)
- attempts (1:N)
```

#### **Attempt (Tentatives)**
```python
# app/models/attempt.py
- id (PK)
- user_id (FK → users.id)
- exercise_id (FK → exercises.id)
- user_answer (String)
- is_correct (Boolean)
- time_spent (Integer, secondes)
- created_at

Relations:
- user (N:1 → User)
- exercise (N:1 → Exercise)
```

#### **LogicChallenge (Défis Logiques)**
```python
# app/models/logic_challenge.py
- id (PK)
- title
- creator_id (FK → users.id)
- challenge_type (ENUM: SEQUENCE, PATTERN, VISUAL, PUZZLE, etc.)
- age_group (ENUM: GROUP_10_12, GROUP_13_15, etc.)
- description
- question
- visual_data (JSON)
- hints (JSON)  # 3 niveaux d'indices
- correct_answer
- explanation
- difficulty_rating (Float)
- estimated_time_minutes
- success_rate
- is_active
- created_at, updated_at

Relations:
- creator (N:1 → User)
```

#### **Progress (Progression)**
```python
# app/models/progress.py
- id (PK)
- user_id (FK → users.id)
- exercise_type (String)
- difficulty (String)
- total_attempts (Integer)
- correct_attempts (Integer)
- total_time_spent (Integer)
- last_attempt_at
- created_at, updated_at

Relations:
- user (N:1 → User)
```

### **3.2 Énumérations**

#### **ExerciseType**
```python
ADDITION = "addition"
SOUSTRACTION = "soustraction"
MULTIPLICATION = "multiplication"
DIVISION = "division"
FRACTIONS = "fractions"        # NOUVEAU (Mai 2025)
GEOMETRIE = "geometrie"        # NOUVEAU (Mai 2025)
TEXTE = "texte"                # NOUVEAU (Mai 2025)
MIXTE = "mixte"
DIVERS = "divers"              # NOUVEAU (Mai 2025)
```

#### **DifficultyLevel**
```python
INITIE = "initie"      # Facile (nombres 1-10)
PADAWAN = "padawan"    # Moyen (nombres 10-50)
CHEVALIER = "chevalier" # Difficile (nombres 50-100)
MAITRE = "maitre"      # Expert (nombres 100-500)
```

#### **UserRole**
```python
PADAWAN = "padawan"        # Utilisateur standard
MAITRE = "maitre"          # Enseignant, créateur d'exercices
GARDIEN = "gardien"        # Modérateur
ARCHIVISTE = "archiviste"  # Administrateur
```

---

## 🔧 **4. SERVICES ET LOGIQUE MÉTIER**

### **4.1 Services Principaux**

#### **ExerciseService** (`app/services/exercise_service.py`)
**Responsabilités** :
- Création, lecture, mise à jour, suppression d'exercices
- Génération d'exercices selon type et difficulté
- Liste et filtrage d'exercices
- Gestion des tentatives

**Méthodes principales** :
- `create_exercise(db, exercise_data)` : Créer un exercice
- `get_exercise(db, exercise_id)` : Récupérer un exercice
- `list_exercises(db, filters)` : Lister avec filtres
- `update_exercise(db, exercise_id, data)` : Mettre à jour
- `delete_exercise(db, exercise_id)` : Supprimer (archivage logique)

#### **UserService** (`app/services/user_service.py`)
**Responsabilités** :
- Gestion des utilisateurs
- Statistiques utilisateur
- Progression et badges

**Méthodes principales** :
- `create_user(db, user_data)` : Créer un utilisateur
- `get_user(db, user_id)` : Récupérer un utilisateur
- `authenticate_user(db, username, password)` : Authentification
- `get_user_stats(db, user_id)` : Statistiques

#### **AuthService** (`app/services/auth_service.py`)
**Responsabilités** :
- Authentification JWT
- Création et validation de tokens
- Gestion des sessions

**Méthodes principales** :
- `create_access_token(data)` : Créer token JWT
- `verify_token(token)` : Vérifier token
- `get_current_user(token)` : Récupérer utilisateur depuis token

#### **LogicChallengeService** (`app/services/logic_challenge_service.py`)
**Responsabilités** :
- Gestion des défis logiques
- Validation des réponses
- Calcul des scores

### **4.2 Système de Transactions Unifié**

#### **TransactionManager** (`app/db/transaction.py`)
**Objectif** : Gestion unifiée des transactions de base de données avec rollback automatique en cas d'erreur.

**Utilisation** :
```python
with TransactionManager() as tm:
    # Opérations de base de données
    tm.commit()  # Commit explicite
    # En cas d'exception, rollback automatique
```

#### **DatabaseAdapter** (`app/db/adapter.py`)
**Objectif** : Interface unifiée pour les opérations CRUD, supportant SQLAlchemy et SQL brut.

#### **EnhancedServerAdapter** (`app/services/enhanced_server_adapter.py`)
**Objectif** : Adaptateur pour connecter le serveur Starlette au système de transaction unifié.

**Méthodes principales** :
- `get_db_session()` : Obtenir session DB
- `get_exercise_by_id(db, exercise_id)` : Récupérer exercice
- `list_exercises(db, filters)` : Lister exercices
- `create_exercise(db, data)` : Créer exercice
- `get_user_by_username(db, username)` : Récupérer utilisateur

---

## 🎲 **5. SYSTÈME DE GÉNÉRATION D'EXERCICES**

### **5.1 Types d'Exercices (9 types)**

#### **Types Arithmétiques de Base**

**1. Addition** (`ExerciseType.ADDITION`)
- **Niveaux** : 4 niveaux (Initié → Maître)
- **Algorithme** : Génération selon limites de difficulté
- **Thème Star Wars** : Cristaux Kyber, escadrons, vaisseaux

**2. Soustraction** (`ExerciseType.SOUSTRACTION`)
- **Contrainte** : Résultats toujours positifs
- **Algorithme** : `num1 >= num2` pour éviter négatifs
- **Thème Star Wars** : Rations, missions, flottes

**3. Multiplication** (`ExerciseType.MULTIPLICATION`)
- **Tables** : Tables de multiplication selon niveau
- **Thème Star Wars** : Escadrons, destroyers, secteurs

**4. Division** (`ExerciseType.DIVISION`)
- **Contrainte** : Divisions exactes uniquement
- **Algorithme** : Génération de dividendes multiples du diviseur

**5. Mixte** (`ExerciseType.MIXTE`)
- **Combinaisons** : 2-4 opérations selon niveau
- **Algorithme** : Sélection aléatoire d'opérations

#### **Nouveaux Types (Mai 2025)**

**6. Fractions** (`ExerciseType.FRACTIONS`)
- **Source** : `server/exercise_generator.py` (lignes 651-750)
- **Module** : Utilise `fractions.Fraction` de Python
- **Opérations** : Addition, soustraction, multiplication, division
- **Progression** :
  - Initié : Fractions simples (`1/2 + 1/2`)
  - Padawan : Dénominateurs différents (`5/6 + 3/4`)
  - Chevalier : Calculs complexes (`5/11 - 1/2`)
  - Maître : Divisions de fractions (`2/3 ÷ 21/15`)
- **Choix** : Génération d'erreurs communes pour distracteurs

**7. Géométrie** (`ExerciseType.GEOMETRIE`)
- **Source** : `server/exercise_generator.py` (lignes 751-950)
- **Formes** : Carré, rectangle, triangle, cercle, trapèze
- **Propriétés** : Périmètre, aire, diagonale
- **Progression** :
  - Initié : Formes simples (périmètre rectangle)
  - Padawan : Calculs intermédiaires (périmètre triangle)
  - Chevalier : Surfaces complexes (aire triangle)
  - Maître : Calculs avancés (diagonale rectangle)
- **Formules** : Toutes les formules géométriques intégrées

**8. Texte** (`ExerciseType.TEXTE`)
- **Source** : `server/exercise_generator.py` (lignes 951-1050)
- **Caractéristiques** : Questions textuelles avec énoncés élaborés
- **Contexte** : Mise en contexte Star Wars
- **Exemples** : Problèmes concrets avec personnages et situations

**9. Divers** (`ExerciseType.DIVERS`)
- **Source** : `server/exercise_generator.py` (lignes 1051-1200)
- **Catégories** : 6 catégories
  - Monnaie : Calculs de prix, change
  - Vitesse : Distance, temps, vitesse
  - Pourcentages : Réductions, augmentations
  - Probabilités : Calculs de chances
  - Séquences : Suites mathématiques
  - Âge : Problèmes d'âge
- **Progression** : Adaptée au niveau de difficulté

### **5.2 Générateur Principal**

**Fichier** : `server/exercise_generator.py`

**Fonction principale** : `generate_simple_exercise(exercise_type, difficulty, use_ai=False)`

**Algorithme** :
1. Normalisation du type et de la difficulté
2. Sélection de l'algorithme selon le type
3. Génération selon les limites de difficulté (`DIFFICULTY_LIMITS`)
4. Création des choix (QCM) avec distracteurs intelligents
5. Génération de l'explication avec thème Star Wars
6. Retour de l'exercice complet

**Limites par difficulté** (`app/core/constants.py`) :
```python
DIFFICULTY_LIMITS = {
    INITIE: {
        ADDITION: {"min": 1, "max": 10},
        SUBTRACTION: {"min1": 5, "max1": 20, "min2": 1, "max2": 5},
        # ...
    },
    PADAWAN: {
        ADDITION: {"min": 10, "max": 50},
        # ...
    },
    # ...
}
```

### **5.3 Génération IA**

**Fonction** : `generate_ai_exercise(exercise_type, difficulty)`

**Caractéristiques** :
- Préfixe `[TEST-ZAXXON]` pour identification
- Thème Star Wars intégré dans les questions
- Explications enrichies avec narratives Star Wars
- Tags : `ai,generatif,starwars`

**Narratives Star Wars** (`app/core/messages.py`) :
- Préfixes et suffixes d'explication par niveau
- Messages adaptés au thème

---

## 🔐 **6. AUTHENTIFICATION ET SÉCURITÉ**

### **6.1 Système JWT (Cristaux d'Identité)**

#### **Configuration**
```python
# app/core/config.py
SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 jours
ALGORITHM: str = "HS256"
```

#### **Structure du Token**
```json
{
  "sub": "username",
  "exp": 1234567890,
  "role": "padawan"
}
```

#### **Endpoints d'Authentification**
- `POST /api/auth/login` : Connexion et obtention token
- `POST /api/auth/logout` : Déconnexion
- `GET /api/auth/me` : Informations utilisateur courant

### **6.2 Rôles et Permissions**

#### **Hiérarchie des Rôles**
```python
PADAWAN (niveau 1):
  - view_own

MAITRE (niveau 2):
  - view_own
  - create_exercises
  - modify_own

GARDIEN (niveau 3):
  - view_own, view_all
  - create_exercises
  - modify_own, modify_all

ARCHIVISTE (niveau 4):
  - Toutes les permissions
  - delete
  - admin
```

#### **Protection des Routes**
```python
# FastAPI
@router.get("/protected")
def protected_route(current_user: User = Depends(get_current_user)):
    # Route accessible à tout utilisateur connecté
    pass

@router.post("/exercises")
def create_exercise(
    exercise_data: ExerciseCreate,
    current_user: User = Depends(get_current_maitre_user)
):
    # Route accessible uniquement aux Maîtres
    pass
```

### **6.3 Sécurité**

#### **Hachage des Mots de Passe**
- **Algorithme** : bcrypt
- **Rounds** : 12 (par défaut)
- **Fichier** : `app/core/security.py`

#### **Cookies HTTP-only**
```python
response.set_cookie(
    key="access_token",
    value=token,
    httponly=True,
    secure=True,  # HTTPS uniquement
    samesite="lax",  # Protection CSRF
    max_age=3600
)
```

#### **Middleware de Sécurité**
- **CORS** : Configuration restrictive
- **TrustedHost** : Validation des hôtes
- **Rate Limiting** : Protection contre abus (60 req/min)

---

## 🎨 **7. FRONTEND ET INTERFACE UTILISATEUR**

### **7.1 Architecture Frontend**

#### **Templates Jinja2**
- **Base** : `templates/base.html`
- **Structure** : Héritage de templates
- **Variables** : Contexte passé depuis les vues

#### **Système CSS Modulaire**
```
static/
├── normalize.css              # Reset CSS
├── variables.css              # Variables CSS (couleurs, espacements)
├── utils.css                  # Utilitaires
├── style.css                  # Styles principaux
├── space-theme-dark.css       # Thème Star Wars (v3.0)
├── accessibility.css          # Accessibilité
├── notifications.css          # Système de notifications
├── breadcrumbs.css            # Fil d'Ariane
├── loading-states.css         # États de chargement
├── dark-mode.css              # Mode sombre
└── styles/
    ├── components/
    │   ├── buttons.css        # Boutons unifiés
    │   └── cards.css          # Cartes unifiées
    └── ui-enhancements.css    # Améliorations UI
```

#### **JavaScript**
- **Vanilla JS** : Pas de framework
- **Modules ES6** : Organisation modulaire
- **Fichiers** : `static/js/*.js`

### **7.2 Thème Star Wars**

#### **Palette de Couleurs**
```css
--primary-color: #8b5cf6;        /* Violet Jedi */
--secondary-color: #6366f1;      /* Indigo */
--accent-color: #ec4899;        /* Rose */
--background-dark: #121212;      /* Espace profond */
--text-light: #ffffff;          /* Blanc */
--text-muted: #a0a0a0;          /* Gris */
```

#### **Effets Visuels**
- **Holographique** : Effets de lumière et transparence
- **Étoiles** : 50 étoiles animées en arrière-plan
- **Planètes** : 3 planètes flottantes avec rotation
- **Particules** : Effets de particules sur interactions

#### **Animations**
- **Timings** : 300-600ms (optimisés pour enfants autistes)
- **Easing** : `ease-out` pour transitions douces
- **Réduction** : Respect de `prefers-reduced-motion`

### **7.3 Accessibilité (WCAG 2.1 AA)**

#### **Barre d'Outils d'Accessibilité**
- **Mode contraste élevé** (Alt+C)
- **Texte plus grand** (Alt+T)
- **Réduction animations** (Alt+M)
- **Mode dyslexie** (Alt+D)

#### **Standards Respectés**
- **ARIA** : Attributs pour lecteurs d'écran
- **Navigation clavier** : Tab, Enter, Escape
- **Skip links** : Liens d'évitement
- **Contraste** : Ratio minimum 4.5:1

### **7.4 Pages Principales**

#### **Home** (`/`)
- Hero section avec statistiques dorées
- CTA "Rejoindre l'aventure"
- Présentation du projet

#### **Login** (`/login`)
- Formulaire de connexion
- Lien "Mot de passe oublié"
- Lien vers inscription

#### **Exercises** (`/exercises`)
- Liste des exercices avec filtres
- Cartes interactives
- Génération d'exercices

#### **Dashboard** (`/dashboard`)
- Statistiques personnalisées
- Graphiques de progression
- Recommandations

#### **Profile** (`/profile`)
- Informations utilisateur
- Paramètres
- Historique

---

## 🧪 **8. SYSTÈME DE TESTS**

### **8.1 Structure en 4 Niveaux**

```
tests/
├── unit/              # Tests unitaires
│   ├── test_models.py
│   ├── test_services.py
│   └── ...
├── api/               # Tests API REST
│   ├── test_auth.py
│   ├── test_exercises.py
│   └── ...
├── integration/       # Tests d'intégration
│   ├── test_database.py
│   └── ...
└── functional/        # Tests fonctionnels
    ├── test_exercise_workflow.py
    └── ...
```

### **8.2 Classification Intelligente**

#### **🔴 Tests Critiques (BLOQUANTS)**
- **Impact** : Bloquent le commit et le déploiement
- **Timeout** : 3 minutes
- **Contenu** :
  - Tests fonctionnels
  - Services core (utilisateur, exercices)
  - Authentification
- **Commande** : `python scripts/pre_commit_check.py`

#### **🟡 Tests Importants (NON-BLOQUANTS)**
- **Impact** : Avertissement, commit autorisé
- **Timeout** : 2 minutes
- **Contenu** :
  - Tests d'intégration
  - Modèles SQLAlchemy
  - Adaptateurs

#### **🟢 Tests Complémentaires (INFORMATIFS)**
- **Impact** : Information seulement
- **Timeout** : 1 minute
- **Contenu** :
  - CLI
  - Initialisation
  - Fonctionnalités secondaires

### **8.3 CI/CD**

#### **Hooks Git**
- **Pre-commit** : Tests critiques avant chaque commit
- **Post-merge** : Mise à jour dépendances

#### **GitHub Actions**
- **Déclenchement** : Push, Pull Request
- **Étapes** :
  1. Tests critiques (parallèles)
  2. Tests importants
  3. Analyse qualité (Black, Flake8, Bandit)
  4. Rapport de couverture

#### **Métriques**
- **Couverture** : 52%+ (objectif 75%)
- **Taux de réussite** : Suivi par catégorie
- **Temps d'exécution** : Optimisation continue

---

## 📋 **9. RÈGLES DE CODAGE ET STANDARDS**

### **9.1 Standards Python**

#### **PEP 8**
- **Longueur ligne** : Maximum 80 caractères (souvent dépassé pour lisibilité)
- **Noms** : Explicites en français pour le métier, anglais pour la technique
- **Docstrings** : Obligatoires pour fonctions et classes
- **Imports** : Organisés par groupe (stdlib, third-party, local)

#### **Type Hints**
- **Utilisation** : Recommandée pour signatures de fonctions
- **Exemple** :
```python
def create_exercise(
    db: Session,
    exercise_data: Dict[str, Any]
) -> Optional[Exercise]:
    pass
```

### **9.2 Conventions de Nommage**

#### **Fichiers**
- **Snake_case** : `exercise_service.py`
- **Descriptifs** : Noms explicites

#### **Classes**
- **PascalCase** : `ExerciseService`, `UserModel`

#### **Fonctions et Variables**
- **snake_case** : `create_exercise()`, `user_id`

#### **Constantes**
- **UPPER_SNAKE_CASE** : `DIFFICULTY_LIMITS`, `EXERCISE_TYPES`

### **9.3 Documentation**

#### **Docstrings**
- **Format** : Google style ou Sphinx
- **Contenu** : Description, Args, Returns, Raises

#### **Commentaires**
- **Code complexe** : Commentaires explicatifs
- **TODOs** : Marqueurs pour améliorations futures
- **Langue** : Français pour le métier, anglais pour la technique

### **9.4 Structure de Code**

#### **Organisation**
- **Séparation des responsabilités** : Modèles, services, vues
- **DRY** : Pas de duplication
- **SOLID** : Principes appliqués

#### **Gestion d'Erreurs**
- **Try/Except** : Gestion explicite des erreurs
- **Logging** : Utilisation de loguru
- **Messages** : Messages d'erreur explicites

---

## 🚀 **10. DÉPLOIEMENT ET CONFIGURATION**

### **10.1 CLI d'Administration**

**Fichier** : `mathakine_cli.py`

#### **Commandes Disponibles**
```bash
# Lancer le serveur
python mathakine_cli.py run [--api-only] [--ui-only] [--all]

# Initialiser la base de données
python mathakine_cli.py init [--force]

# Exécuter les tests
python mathakine_cli.py test [--type unit|api|integration|functional|all]

# Valider l'application
python mathakine_cli.py validate [--level simple|full|compatibility]

# Shell interactif
python mathakine_cli.py shell

# Configuration environnement
python mathakine_cli.py setup [--full]
```

### **10.2 Configuration**

#### **Variables d'Environnement**
```bash
# Base de données
DATABASE_URL=postgresql://user:pass@localhost/mathakine
TEST_DATABASE_URL=postgresql://user:pass@localhost/test_mathakine

# Sécurité
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 jours

# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
LOG_FILE=logs/mathakine.log

# Serveur
PORT=8000
HOST=0.0.0.0
MATH_TRAINER_DEBUG=true
```

#### **Fichier .env**
- **Template** : `sample.env`
- **Chargement** : Via `python-dotenv`
- **Priorité** : Variables d'environnement > .env > Valeurs par défaut

### **10.3 Déploiement**

#### **Développement Local**
```bash
# 1. Cloner le repository
git clone https://github.com/zyclope0/mathakine.git
cd mathakine

# 2. Créer environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate      # Windows

# 3. Installer dépendances
pip install -r requirements.txt

# 4. Configurer .env
cp sample.env .env
# Éditer .env

# 5. Initialiser base de données
python mathakine_cli.py init

# 6. Lancer l'application
python mathakine_cli.py run
```

#### **Production (Render)**
- **Plateforme** : Render.com
- **Base de données** : PostgreSQL (Render PostgreSQL)
- **Script** : `scripts/start_render.sh`
- **Variables** : Configurées dans le dashboard Render

---

## 📈 **11. FONCTIONNALITÉS AVANCÉES**

### **11.1 Système de Badges**

#### **Types de Badges**
- **Par type d'exercice** : Badges colorés selon le type
- **Par niveau** : Progression Initié → Maître
- **Spéciaux** : Récompenses pour accomplissements

#### **API Badges**
- `GET /api/badges/user` : Badges de l'utilisateur
- `GET /api/badges/available` : Badges disponibles
- `POST /api/badges/check` : Vérifier attribution
- `GET /api/badges/stats` : Statistiques gamification

### **11.2 Défis Logiques**

#### **Types de Défis**
- **SEQUENCE** : Séquences numériques
- **PATTERN** : Reconnaissance de motifs
- **VISUAL** : Défis visuels
- **PUZZLE** : Puzzles logiques
- **DEDUCTION** : Déduction logique
- **SPATIAL** : Raisonnement spatial

#### **Groupes d'Âge**
- **GROUP_10_12** : 10-12 ans
- **GROUP_13_15** : 13-15 ans
- **AGE_9_12** : 9-12 ans
- **AGE_13_16** : 13-16 ans

### **11.3 Système de Recommandations**

#### **Algorithme**
- Analyse des performances passées
- Détection des forces et faiblesses
- Suggestions d'exercices adaptés

#### **API**
- `GET /api/recommendations` : Recommandations pour utilisateur
- `POST /api/recommendations/complete` : Marquer comme complété

---

## 🔍 **12. POINTS D'ATTENTION ET CONNAISSANCES CLÉS**

### **12.1 Architecture Dual-Backend**

**Important** : Comprendre la différence entre FastAPI et Starlette :
- **FastAPI** : API REST pure, port 8081
- **Starlette** : Interface web complète, port 8000
- Les deux partagent modèles et services

### **12.2 Compatibilité Base de Données**

**PostgreSQL vs SQLite** :
- **PostgreSQL** : Production, support JSON natif, énumérations
- **SQLite** : Développement, simplicité
- **Mapping** : Système de compatibilité dans `app/db/adapter.py`

### **12.3 Système de Transactions**

**TransactionManager** :
- Gestion unifiée des transactions
- Rollback automatique en cas d'erreur
- Utilisation recommandée pour toutes opérations DB

### **12.4 Génération d'Exercices**

**9 types d'exercices** :
- 5 types arithmétiques de base
- 4 nouveaux types (Fractions, Géométrie, Texte, Divers)
- Génération IA optionnelle avec thème Star Wars

### **12.5 Authentification**

**JWT avec cookies HTTP-only** :
- Tokens dans cookies sécurisés
- Refresh tokens pour renouvellement
- Rôles hiérarchiques (Padawan → Archiviste)

### **12.6 Tests et CI/CD**

**Classification intelligente** :
- Tests critiques bloquants
- Tests importants non-bloquants
- Tests complémentaires informatifs
- Hooks Git automatiques

---

## 📚 **13. DOCUMENTATION**

### **13.1 Structure Documentation**

```
docs/
├── architecture/          # Documentation technique
│   ├── README.md          # Vue d'ensemble
│   ├── backend.md         # Backend FastAPI/Starlette
│   ├── database.md        # Base de données
│   └── security.md        # Sécurité
├── development/           # Guides développeur
│   ├── README.md          # Guide complet (916 lignes)
│   ├── contributing.md    # Contribution
│   └── testing.md         # Tests
├── features/              # Fonctionnalités
│   ├── README.md          # Vue d'ensemble
│   └── BADGE_SYSTEM.md    # Système de badges
├── ui-ux/                 # Interface utilisateur
│   └── ui-ux.md           # Guide UI/UX complet
├── api/                   # Documentation API
│   └── api.md             # 40+ endpoints documentés
└── project/               # Gestion projet
    ├── README.md          # Statut projet
    └── roadmap.md         # Roadmap 2025-2026
```

### **13.2 Fichiers de Référence**

- **README.md** : Documentation principale
- **TABLE_DES_MATIERES.md** : Navigation complète
- **GLOSSARY.md** : Terminologie
- **CHANGELOG.md** : Historique des versions
- **CI_CD_GUIDE.md** : Guide CI/CD

### **13.3 ai_context_summary.md**

**Fichier essentiel** : `ai_context_summary.md`
- **Taille** : ~38 000 tokens
- **Contenu** : Contexte complet du projet
- **Mise à jour** : Février 2025
- **Usage** : Référence pour IA et développeurs

---

## 🎯 **14. WORKFLOW DE DÉVELOPPEMENT**

### **14.1 Développement Local**

1. **Modification du code**
2. **Tests automatiques** (hook pre-commit)
3. **Commit** (si tests critiques passent)
4. **Push** → Pipeline GitHub Actions
5. **Déploiement** (si tous les tests critiques passent)

### **14.2 Ajout d'une Fonctionnalité**

1. **Créer une branche** : `feature/nom-fonctionnalite`
2. **Développer** :
   - Modèles (`app/models/`)
   - Services (`app/services/`)
   - Endpoints (`app/api/endpoints/`)
   - Vues (`server/views.py` ou `server/handlers/`)
   - Templates (`templates/`)
3. **Tester** :
   - Tests unitaires
   - Tests d'intégration
   - Tests fonctionnels
4. **Documenter** :
   - Docstrings
   - Documentation dans `docs/`
   - Mise à jour CHANGELOG
5. **Soumettre PR**

### **14.3 Debugging**

#### **Logs**
- **Fichiers** : `logs/mathakine.log`
- **Niveaux** : DEBUG, INFO, WARNING, ERROR
- **Rotation** : Automatique

#### **Mode Debug**
```bash
# Activer mode debug
export MATH_TRAINER_DEBUG=true
export LOG_LEVEL=DEBUG

# Lancer avec debug
python mathakine_cli.py run --debug
```

#### **Shell Interactif**
```bash
python mathakine_cli.py shell
# Accès à session DB et modèles
```

---

## 🔮 **15. ROADMAP ET ÉVOLUTIONS**

### **15.1 Version Actuelle**

**Version 1.5.0** (Mai 2025)
- ✅ 9 types d'exercices complets
- ✅ Migration générateurs réussie
- ✅ Interface Premium v3.0
- ✅ Système de badges
- ✅ Défis logiques complets

### **15.2 Roadmap 2025-2026**

#### **Phase 2 : Composants Interactifs**
- États de boutons avancés
- Système de modales
- Formulaires optimisés
- Composants de données

#### **Phase 3 : Mobile & Performance**
- Navigation mobile
- Composants tactiles
- Performance mobile optimisée

#### **Phase 4 : Polish & Animations**
- Animations premium
- Micro-interactions
- Transitions fluides

---

## 📝 **16. CHECKLIST DE CONNAISSANCE**

### **Architecture** ✅
- [x] Comprendre dual-backend (FastAPI + Starlette)
- [x] Connaître la structure des répertoires
- [x] Comprendre le flux de données

### **Modèles de Données** ✅
- [x] Connaître tous les modèles principaux
- [x] Comprendre les relations
- [x] Connaître les énumérations

### **Services** ✅
- [x] Comprendre les services principaux
- [x] Connaître le système de transactions
- [x] Comprendre les adaptateurs

### **Génération d'Exercices** ✅
- [x] Connaître les 9 types d'exercices
- [x] Comprendre les algorithmes de génération
- [x] Connaître les limites par difficulté

### **Authentification** ✅
- [x] Comprendre le système JWT
- [x] Connaître les rôles et permissions
- [x] Comprendre la sécurité

### **Frontend** ✅
- [x] Connaître la structure des templates
- [x] Comprendre le système CSS
- [x] Connaître le thème Star Wars

### **Tests** ✅
- [x] Comprendre la classification des tests
- [x] Connaître le système CI/CD
- [x] Comprendre les hooks Git

### **Déploiement** ✅
- [x] Connaître la CLI
- [x] Comprendre la configuration
- [x] Connaître le processus de déploiement

---

## 🎓 **CONCLUSION**

Ce document fournit une **vue d'ensemble complète** du projet Mathakine, couvrant :

✅ **Architecture technique** (dual-backend, stack, structure)  
✅ **Modèles de données** (tous les modèles et relations)  
✅ **Services et logique métier** (tous les services principaux)  
✅ **Génération d'exercices** (9 types avec algorithmes)  
✅ **Authentification et sécurité** (JWT, rôles, permissions)  
✅ **Frontend** (templates, CSS, JavaScript, accessibilité)  
✅ **Tests et CI/CD** (classification, hooks, pipeline)  
✅ **Règles de codage** (standards, conventions, documentation)  
✅ **Déploiement** (CLI, configuration, processus)  
✅ **Fonctionnalités avancées** (badges, défis, recommandations)  

**Niveau de connaissance atteint : ~95%** 🎯

---

**Document créé le : Janvier 2025**  
**Dernière mise à jour : Janvier 2025**  
**Prochaine révision recommandée : Après modifications majeures**

---

*Que la Force des Mathématiques soit avec vous !* ⭐🚀

