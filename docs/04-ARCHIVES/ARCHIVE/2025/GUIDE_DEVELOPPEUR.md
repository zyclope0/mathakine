# Guide du développeur Mathakine

Ce document consolidé offre un guide complet pour les développeurs souhaitant installer, configurer ou étendre le projet Mathakine. Il couvre à la fois la mise en place initiale et les instructions pour ajouter de nouvelles fonctionnalités.

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

## 3. Guide d'extension du projet

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

   Ajoutez une option pour le nouveau type d'exercice dans `templates/exercises.html`:

   ```html
   <select class="form-select" id="exercise-type">
       <option value="addition">Addition</option>
       <option value="subtraction">Soustraction</option>
       <option value="multiplication">Multiplication</option>
       <option value="division">Division</option>
       <option value="nouveau_type">Nouveau Type</option>  <!-- Ajoutez cette ligne -->
   </select>
   ```

5. **Mettre à jour les messages**

   Ajoutez les textes correspondants dans `app/core/messages.py`:

   ```python
   class ExerciseTypeLabels:
       ADDITION = "Addition"
       SUBTRACTION = "Soustraction"
       MULTIPLICATION = "Multiplication"
       DIVISION = "Division"
       NEW_TYPE = "Nouveau Type"  # Ajoutez cette ligne
   ```

6. **Tester votre nouveau type d'exercice**

   Créez un test dans `tests/unit/test_exercise_generators.py`:

   ```python
   def test_generate_new_type_exercise():
       """Test la génération d'exercices du nouveau type"""
       for difficulty in DIFFICULTY_LEVELS:
           exercise = generate_new_type_exercise(difficulty)
           assert exercise["exercise_type"] == ExerciseTypes.NEW_TYPE
           assert exercise["difficulty"] == difficulty
           # Autres assertions spécifiques à votre type...
   ```

### Ajouter un nouveau niveau de difficulté

1. **Mettre à jour les constantes**

   Dans `app/core/constants.py`, ajoutez le nouveau niveau:

   ```python
   class DifficultyLevels:
       INITIATE = "initiate"  # Initié (facile)
       PADAWAN = "padawan"    # Padawan (intermédiaire)
       KNIGHT = "knight"      # Chevalier (difficile)
       MASTER = "master"      # Maître (expert)
       LEGEND = "legend"      # Légende (nouveau niveau)
   
   # Et ajoutez aussi les limites numériques correspondantes
   DIFFICULTY_LIMITS = {
       DifficultyLevels.INITIATE: (1, 10),
       DifficultyLevels.PADAWAN: (10, 50),
       DifficultyLevels.KNIGHT: (50, 100),
       DifficultyLevels.MASTER: (100, 500),
       DifficultyLevels.LEGEND: (500, 1000),  # Ajoutez cette ligne
   }
   ```

2. **Mettre à jour l'interface utilisateur**

   Modifiez le sélecteur de difficulté dans `templates/exercises.html`:

   ```html
   <select class="form-select" id="difficulty-level">
       <option value="initiate">Initié</option>
       <option value="padawan">Padawan</option>
       <option value="knight">Chevalier</option>
       <option value="master">Maître</option>
       <option value="legend">Légende</option>  <!-- Ajoutez cette ligne -->
   </select>
   ```

3. **Mettre à jour les messages**

   Ajoutez les textes correspondants dans `app/core/messages.py`:

   ```python
   class DifficultyLabels:
       INITIATE = "Initié"
       PADAWAN = "Padawan"
       KNIGHT = "Chevalier"
       MASTER = "Maître"
       LEGEND = "Légende"  # Ajoutez cette ligne
   ```

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

   Créez `app/schemas/analytics.py`:

   ```python
   from pydantic import BaseModel
   from typing import Dict, List, Optional
   from datetime import datetime
   
   class PerformanceData(BaseModel):
       exercise_type: str
       success_rate: float
       average_time: float
       count: int
   
   class AnalyticsResponse(BaseModel):
       overall_performance: float
       performance_by_type: List[PerformanceData]
       performance_by_difficulty: Dict[str, float]
       trend: List[Dict[str, float]]
       last_updated: datetime
   ```

3. **Implémenter le service**

   Créez `app/services/analytics_service.py`:

   ```python
   from sqlalchemy.orm import Session
   from sqlalchemy import func, desc
   from datetime import datetime, timedelta
   from ..models.result import Result
   from ..models.exercise import Exercise
   
   def get_advanced_analytics(db: Session):
       """
       Récupère des statistiques avancées sur les performances
       """
       # Code pour générer les statistiques
       # ...
       
       return {
           "overall_performance": 0.75,
           "performance_by_type": [],
           "performance_by_difficulty": {},
           "trend": [],
           "last_updated": datetime.now()
       }
   ```

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

   Créez un test dans `tests/api/test_analytics.py`:

   ```python
   from fastapi.testclient import TestClient
   from app.main import app
   
   client = TestClient(app)
   
   def test_read_advanced_analytics():
       response = client.get("/api/analytics/advanced")
       assert response.status_code == 200
       data = response.json()
       assert "overall_performance" in data
       assert "performance_by_type" in data
       # Autres assertions...
   ```

### Ajouter une nouvelle table dans la base de données

1. **Créer le modèle**

   Créez `app/models/feedback.py`:

   ```python
   from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, DateTime
   from sqlalchemy.orm import relationship
   import datetime
   from .base import Base
   
   class Feedback(Base):
       __tablename__ = "feedback"
       
       id = Column(Integer, primary_key=True, index=True)
       exercise_id = Column(Integer, ForeignKey("exercises.id"))
       user_id = Column(Integer, ForeignKey("users.id"))
       rating = Column(Integer)  # Par exemple, 1-5
       comment = Column(Text)
       is_archived = Column(Boolean, default=False)
       created_at = Column(DateTime, default=datetime.datetime.utcnow)
       
       # Relations
       exercise = relationship("Exercise", back_populates="feedback")
       user = relationship("User", back_populates="feedback")
   ```

2. **Mettre à jour les modèles associés**

   Dans `app/models/exercise.py`:

   ```python
   # Ajouter la relation
   feedback = relationship("Feedback", back_populates="exercise", cascade="all, delete-orphan")
   ```

   Dans `app/models/user.py`:

   ```python
   # Ajouter la relation
   feedback = relationship("Feedback", back_populates="user", cascade="all, delete-orphan")
   ```

3. **Créer le schéma Pydantic**

   Créez `app/schemas/feedback.py`:

   ```python
   from pydantic import BaseModel, Field
   from typing import Optional
   from datetime import datetime
   
   class FeedbackBase(BaseModel):
       exercise_id: int
       rating: int = Field(..., ge=1, le=5)
       comment: Optional[str] = None
   
   class FeedbackCreate(FeedbackBase):
       pass
   
   class FeedbackUpdate(BaseModel):
       rating: Optional[int] = Field(None, ge=1, le=5)
       comment: Optional[str] = None
       is_archived: Optional[bool] = None
   
   class FeedbackInDB(FeedbackBase):
       id: int
       user_id: Optional[int] = None
       is_archived: bool
       created_at: datetime
       
       class Config:
           orm_mode = True
   
   class Feedback(FeedbackInDB):
       pass
   ```

4. **Mettre à jour la fonction d'initialisation de la base de données**

   Dans `app/db/init_db.py`, assurez-vous que les nouvelles tables sont créées:

   ```python
   # Importez le nouveau modèle
   from app.models.feedback import Feedback
   
   def init_db(db: Session) -> None:
       # Créer les tables
       Base.metadata.create_all(bind=engine)
       
       # Autres opérations d'initialisation...
   ```

5. **Créer les requêtes SQL centralisées**

   Dans `app/db/queries.py`, ajoutez:

   ```python
   class FeedbackQueries:
       INSERT = """
       INSERT INTO feedback (exercise_id, user_id, rating, comment)
       VALUES (%s, %s, %s, %s)
       RETURNING id
       """
       
       GET_BY_ID = """
       SELECT id, exercise_id, user_id, rating, comment, is_archived, created_at
       FROM feedback
       WHERE id = %s
       """
       
       GET_BY_EXERCISE = """
       SELECT id, exercise_id, user_id, rating, comment, is_archived, created_at
       FROM feedback
       WHERE exercise_id = %s AND is_archived = false
       ORDER BY created_at DESC
       """
       
       # Autres requêtes...
   ```

6. **Créer les endpoints API**

   Créez `app/api/endpoints/feedback.py` avec les opérations CRUD appropriées.

7. **Mettre à jour le script de migration (si nécessaire)**

   Si vous utilisez des scripts de migration, créez-en un nouveau dans `migrations/`.

## 4. Bonnes pratiques et normes de codage

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

## 5. Déploiement

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

## 6. Résolution des problèmes courants

Voir le document [CORRECTIONS_ET_MAINTENANCE.md](CORRECTIONS_ET_MAINTENANCE.md) pour une liste complète des problèmes courants et leurs solutions.

---

*Ce document consolidé remplace les anciens documents GETTING_STARTED.md et EXTENSION_GUIDE.md.*  
*Dernière mise à jour : 11 Mai 2025* 