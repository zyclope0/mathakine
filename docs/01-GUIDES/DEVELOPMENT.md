# 💻 DEVELOPMENT GUIDE - MATHAKINE

**Version** : 3.0.0  
**Date** : 09 fevrier 2026 (mise a jour)  
**Audience** : Developpeurs

---

## 📋 TABLE DES MATIÈRES

1. [Environnement de développement](#environnement)
2. [Workflow développement](#workflow)
3. [Conventions de code](#conventions)
4. [Structure du code](#structure)
5. [Debugging](#debugging)
6. [Best practices](#best-practices)
7. [Ressources](#ressources)

---

## 🛠️ ENVIRONNEMENT {#environnement}

### Prérequis
- **Node.js** 18+ (recommandé : 20 LTS)
- **Python** 3.12+
- **PostgreSQL** 15+ (ou SQLite pour dev)
- **Git** 2.40+
- **VS Code** (recommandé) avec extensions

### Extensions VS Code recommandées
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "bradlc.vscode-tailwindcss",
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-typescript-next",
    "mikestead.dotenv",
    "redhat.vscode-yaml"
  ]
}
```

### Configuration initiale

#### 1. Backend Python
```bash
# Créer environnement virtuel
python -m venv venv

# Activer (Windows)
venv\Scripts\activate

# Activer (Mac/Linux)
source venv/bin/activate

# Installer dépendances
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Outils dev

# Configuration
cp sample.env .env
# Éditer .env avec vos valeurs
```

#### 2. Frontend Next.js
```bash
cd frontend

# Installer dépendances
npm install

# Configuration
cp .env.example .env.local
# Éditer .env.local
```

#### 3. Database
```bash
# Option 1 : SQLite (dev)
python -m app.db.init_db

# Option 2 : PostgreSQL (local)
createdb mathakine
alembic upgrade head
python -m app.db.init_db --seed
```

---

## 🔄 WORKFLOW DÉVELOPPEMENT {#workflow}

### Démarrage quotidien

```bash
# Terminal 1 : Backend
cd D:\Mathakine
venv\Scripts\activate
python enhanced_server.py

# Terminal 2 : Frontend
cd D:\Mathakine\frontend
npm run dev

# Terminal 3 : Tests (optionnel)
cd D:\Mathakine
pytest tests/ -v --watch
```

### Créer une nouvelle feature

#### 1. Créer une branche
```bash
git checkout -b feature/nom-feature
```

#### 2. Développer backend

**Créer un modèle** (`app/models/`)
```python
# app/models/my_model.py
from sqlalchemy import Column, Integer, String
from app.db.base import Base

class MyModel(Base):
    __tablename__ = "my_models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(1000))
```

**Créer un schéma** (`app/schemas/`)
```python
# app/schemas/my_model.py
from pydantic import BaseModel

class MyModelBase(BaseModel):
    name: str
    description: str | None = None

class MyModelCreate(MyModelBase):
    pass

class MyModel(MyModelBase):
    id: int
    
    class Config:
        from_attributes = True
```

**Créer un service** (`app/services/`)
```python
# app/services/my_model_service.py
from sqlalchemy.orm import Session
from app.models.my_model import MyModel
from app.schemas.my_model import MyModelCreate

def create_my_model(db: Session, data: MyModelCreate) -> MyModel:
    """Créer un nouveau MyModel"""
    db_obj = MyModel(**data.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_my_model(db: Session, id: int) -> MyModel | None:
    """Récupérer un MyModel par ID"""
    return db.query(MyModel).filter(MyModel.id == id).first()
```

**Creer un handler** (`server/handlers/`)

> **Depuis le 09/02/2026** : Utiliser les decorateurs d'authentification de `server/auth.py` au lieu de verifier manuellement le token.

```python
# server/handlers/my_model_handlers.py
from starlette.responses import JSONResponse
from server.auth import require_auth, optional_auth
from app.services import my_model_service
from app.schemas.my_model import MyModelCreate

@require_auth  # Authentification obligatoire - injecte request.state.user
async def create_my_model_handler(request):
    """POST /api/my-models"""
    try:
        current_user = request.state.user  # Injecte par @require_auth
        data = await request.json()
        db = request.state.db
        
        # Validation
        model_data = MyModelCreate(**data)
        
        # Creation
        result = my_model_service.create_my_model(db, model_data)
        
        return JSONResponse({
            "id": result.id,
            "name": result.name,
            "description": result.description
        }, status_code=201)
        
    except Exception as creation_error:
        from app.utils.error_handler import api_error_response
        return api_error_response(500, str(creation_error))

@optional_auth  # Auth optionnelle - request.state.user = None si non connecte
async def list_my_models_handler(request):
    """GET /api/my-models"""
    current_user = request.state.user  # Peut etre None
    # ...
```

**Decorateurs disponibles** (`server/auth.py`) :
| Decorateur | Usage | Comportement si non authentifie |
|------------|-------|-------------------------------|
| `@require_auth` | Endpoints proteges | Retourne 401 JSON |
| `@optional_auth` | Endpoints mixtes | `request.state.user = None` |
| `@require_auth_sse` | Streams SSE proteges | Retourne erreur SSE |

**Ajouter route** (`server/routes/` — module concerné, ex. `exercises.py`)
```python
from server.handlers.my_model_handlers import create_my_model_handler

routes = [
    # ... routes existantes
    Route("/api/my-models", create_my_model_handler, methods=["POST"]),
]
```

#### 3. Développer frontend

**Créer un type** (`frontend/types/`)
```typescript
// frontend/types/my-model.ts
export interface MyModel {
  id: number;
  name: string;
  description?: string;
}

export interface CreateMyModelData {
  name: string;
  description?: string;
}
```

**Créer un hook** (`frontend/hooks/`)
```typescript
// frontend/hooks/useMyModels.ts
import { useQuery, useMutation } from '@tanstack/react-query';
import { api } from '@/lib/api/client';
import type { MyModel, CreateMyModelData } from '@/types/my-model';

export function useMyModels() {
  return useQuery({
    queryKey: ['my-models'],
    queryFn: async () => {
      const response = await api.get<MyModel[]>('/my-models');
      return response;
    },
  });
}

export function useCreateMyModel() {
  return useMutation({
    mutationFn: async (data: CreateMyModelData) => {
      return await api.post<MyModel>('/my-models', data);
    },
  });
}
```

**Créer un composant** (`frontend/components/`)
```typescript
// frontend/components/my-models/MyModelList.tsx
'use client';

import { useMyModels } from '@/hooks/useMyModels';

export function MyModelList() {
  const { data: models, isLoading, error } = useMyModels();
  
  if (isLoading) return <div>Chargement...</div>;
  if (error) return <div>Erreur: {error.message}</div>;
  
  return (
    <div className="grid gap-4">
      {models?.map((model) => (
        <div key={model.id} className="p-4 border rounded">
          <h3 className="font-bold">{model.name}</h3>
          <p className="text-gray-600">{model.description}</p>
        </div>
      ))}
    </div>
  );
}
```

**Créer une page** (`frontend/app/`)
```typescript
// frontend/app/my-models/page.tsx
import { MyModelList } from '@/components/my-models/MyModelList';

export default function MyModelsPage() {
  return (
    <div className="container py-8">
      <h1 className="text-3xl font-bold mb-8">My Models</h1>
      <MyModelList />
    </div>
  );
}
```

#### 4. Créer migration

```bash
# Générer migration
alembic revision --autogenerate -m "Add my_models table"

# Vérifier la migration
cat alembic/versions/xxxx_add_my_models_table.py

# Appliquer
alembic upgrade head
```

#### 5. Écrire tests

**Test backend** (`tests/api/`)
```python
# tests/api/test_my_models.py
import pytest

def test_create_my_model(client, db):
    """Test création MyModel"""
    response = client.post("/api/my-models", json={
        "name": "Test Model",
        "description": "Test description"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Model"
    assert "id" in data
```

**Test frontend** (`frontend/__tests__/`)
```typescript
// frontend/__tests__/components/MyModelList.test.tsx
import { render, screen } from '@testing-library/react';
import { MyModelList } from '@/components/my-models/MyModelList';

test('renders my models', () => {
  render(<MyModelList />);
  expect(screen.getByText(/chargement/i)).toBeInTheDocument();
});
```

#### 6. Commit et push

```bash
# Vérifier changements
git status
git diff

# Ajouter fichiers
git add app/models/my_model.py
git add app/schemas/my_model.py
git add app/services/my_model_service.py
git add server/handlers/my_model_handlers.py
git add tests/api/test_my_models.py
git add frontend/types/my-model.ts
git add frontend/hooks/useMyModels.ts
git add frontend/components/my-models/

# Commit
git commit -m "feat: Add MyModel feature

- Add MyModel model, schema, service
- Add API endpoints for MyModel
- Add frontend components and hooks
- Add tests
"

# Push
git push origin feature/nom-feature
```

#### 7. Créer Pull Request

```bash
# Sur GitHub
# 1. Ouvrir PR depuis branche
# 2. Remplir template PR
# 3. Attendre CI/CD
# 4. Code review
# 5. Merge
```

---

## 📐 CONVENTIONS DE CODE {#conventions}

### Backend (Python)

#### Naming
```python
# ✅ CORRECT
def get_user_by_id(db: Session, user_id: int) -> User | None:
    """Récupérer un utilisateur par ID"""
    return db.query(User).filter(User.id == user_id).first()

except Exception as user_retrieval_error:
    logger.error(f"Error: {user_retrieval_error}")

# ❌ INCORRECT
def getUserById(db, id):
    return db.query(User).filter(User.id == id).first()

except Exception as e:
    logger.error(f"Error: {e}")
```

#### Docstrings
```python
def calculate_user_score(user_id: int, challenge_type: str) -> float:
    """
    Calculer le score d'un utilisateur pour un type de défi.
    
    Args:
        user_id: ID de l'utilisateur
        challenge_type: Type de défi (SEQUENCE, PATTERN, etc.)
    
    Returns:
        Score calculé (0.0 à 100.0)
    
    Raises:
        ValueError: Si user_id invalide
        DatabaseError: Si erreur DB
    """
    # Implementation
    pass
```

#### Type hints
```python
from typing import Optional, List, Dict

def get_challenges(
    db: Session,
    challenge_type: Optional[str] = None,
    age_group: Optional[str] = None,
    limit: int = 10
) -> List[Challenge]:
    """Lister les challenges avec filtres"""
    query = db.query(Challenge)
    
    if challenge_type:
        query = query.filter(Challenge.challenge_type == challenge_type)
    
    if age_group:
        query = query.filter(Challenge.age_group == age_group)
    
    return query.limit(limit).all()
```

### Frontend (TypeScript)

#### Naming
```typescript
// ✅ CORRECT
const fetchUserData = async (userId: number): Promise<User> => {
  const response = await api.get<User>(`/users/${userId}`);
  return response;
};

// Composants : PascalCase
export function UserProfile({ userId }: UserProfileProps) {
  // ...
}

// Hooks : useCamelCase
export function useUserData(userId: number) {
  // ...
}

// ❌ INCORRECT
const FetchUserData = async (user_id: number) => {
  // ...
};
```

#### Types
```typescript
// Interfaces pour objets
interface User {
  id: number;
  username: string;
  email: string;
}

// Types pour unions
type UserRole = 'student' | 'teacher' | 'admin';

// Enums pour constantes
enum ChallengeType {
  SEQUENCE = 'SEQUENCE',
  PATTERN = 'PATTERN',
  PUZZLE = 'PUZZLE',
}
```

#### Données dynamiques (Record&lt;string, unknown&gt;)

Les renderers de visualisation reçoivent `visualData: Record<string, unknown>`. Pour éviter les erreurs TypeScript au build :

```typescript
// ✅ Chaînes pour JSX
const description: string = String(visualData.description ?? "");

// ✅ Tableaux
const items = Array.isArray(visualData.items) ? visualData.items : [];

// ✅ Condition + JSX (éviter unknown comme ReactNode)
{Boolean(visualData.flag) && <div>{String(visualData.flag)}</div>}

// ✅ Accès propriétés d'objets
const obj = value as Record<string, unknown>;
if (obj?.key) { /* ... */ }
```

#### Composants React
```typescript
// ✅ CORRECT - Composant fonctionnel avec TypeScript
interface UserCardProps {
  user: User;
  onEdit?: (user: User) => void;
}

export function UserCard({ user, onEdit }: UserCardProps) {
  const handleEdit = () => {
    onEdit?.(user);
  };
  
  return (
    <div className="p-4 border rounded">
      <h3 className="font-bold">{user.username}</h3>
      <p className="text-gray-600">{user.email}</p>
      {onEdit && (
        <button onClick={handleEdit} className="mt-2">
          Éditer
        </button>
      )}
    </div>
  );
}
```

---

## 📁 STRUCTURE DU CODE {#structure}

Voir [Architecture](../00-REFERENCE/ARCHITECTURE.md) pour structure complète.

### Organisation backend
```
app/services/my_feature_service.py   # Logique métier
app/models/my_feature.py             # Modèles DB
app/schemas/my_feature.py            # Schémas Pydantic
server/handlers/my_feature_handlers.py # Handlers HTTP
tests/api/test_my_feature.py         # Tests API
tests/unit/test_my_feature_service.py # Tests unitaires
```

### Organisation frontend
```
frontend/types/my-feature.ts                # Types TypeScript
frontend/hooks/useMyFeature.ts              # Custom hooks
frontend/components/my-feature/             # Composants
  ├── MyFeatureList.tsx
  ├── MyFeatureCard.tsx
  └── MyFeatureForm.tsx
frontend/app/my-feature/                    # Pages
  ├── page.tsx                              # Liste
  └── [id]/page.tsx                         # Détails
frontend/__tests__/my-feature/              # Tests
```

---

## 🐛 DEBUGGING {#debugging}

### Backend

#### Logging
```python
from loguru import logger

# Niveaux de log
logger.debug("Debug info")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error occurred")
logger.critical("Critical error")

# Avec contexte
logger.info(f"User {user_id} created challenge {challenge_id}")

# Avec exception
try:
    # code
except Exception as error:
    logger.exception(f"Failed to process: {error}")
```

#### Debugger Python (pdb)
```python
# Insérer breakpoint
import pdb; pdb.set_trace()

# Ou avec Python 3.7+
breakpoint()

# Commandes pdb
# n : next line
# s : step into
# c : continue
# p variable : print variable
# l : list code around
# q : quit
```

#### VS Code Debug
```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Enhanced Server",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/enhanced_server.py",
      "console": "integratedTerminal",
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      }
    }
  ]
}
```

### Frontend

#### Console.log
```typescript
// Development only
if (process.env.NODE_ENV === 'development') {
  console.log('User data:', userData);
  console.table(challenges);
}
```

#### React DevTools
- Installer extension Chrome/Firefox
- Inspecter composants
- Voir props, state, hooks

#### Next.js DevTools
```typescript
// next.config.js
module.exports = {
  reactStrictMode: true,
  logging: {
    fetches: {
      fullUrl: true,
    },
  },
};
```

---

## ✅ BEST PRACTICES {#best-practices}

### Backend

1. **Toujours utiliser type hints**
```python
def get_user(db: Session, user_id: int) -> User | None:
    pass
```

2. **Gérer les exceptions proprement**
```python
try:
    # code
except SpecificError as specific_error:
    logger.error(f"Specific error: {specific_error}")
    raise
except Exception as general_error:
    logger.exception(f"Unexpected error: {general_error}")
    raise HTTPException(status_code=500)
```

3. **Utiliser les services pour logique métier**
```python
# ✅ CORRECT
result = challenge_service.create_challenge(db, challenge_data)

# ❌ INCORRECT
challenge = Challenge(**data)
db.add(challenge)
db.commit()
```

4. **Constants centralisées**
```python
from app.core.constants import CHALLENGE_TYPES_DB, normalize_challenge_type

# ✅ CORRECT
normalized_type = normalize_challenge_type(user_input)

# ❌ INCORRECT
challenge_types = {"SEQUENCE": "...", "PATTERN": "..."}
```

### Frontend

1. **Utiliser TanStack Query pour API**
```typescript
// ✅ CORRECT
const { data, isLoading } = useQuery({
  queryKey: ['challenges'],
  queryFn: () => api.get('/challenges'),
});

// ❌ INCORRECT
const [data, setData] = useState([]);
useEffect(() => {
  fetch('/api/challenges').then(r => r.json()).then(setData);
}, []);
```

2. **Composants réutilisables**
```typescript
// components/ui/Button.tsx - Réutilisable
export function Button({ variant, children, ...props }: ButtonProps) {
  return <button className={cn(baseStyles, variants[variant])} {...props}>
    {children}
  </button>;
}
```

3. **Types stricts**
```typescript
// ✅ CORRECT
interface Challenge {
  id: number;
  title: string;
}

// ❌ INCORRECT
const challenge: any = { ... };
```

---

## 📚 RESSOURCES {#ressources}

### Documentation
- [Architecture](../00-REFERENCE/ARCHITECTURE.md)
- [API Reference](../00-REFERENCE/API.md)
- [Testing Guide](TESTING.md)
- [Troubleshooting](TROUBLESHOOTING.md)

### Outils
- **Python** : https://docs.python.org/3/
- **Starlette** : https://www.starlette.io/
- **SQLAlchemy** : https://docs.sqlalchemy.org/
- **Next.js** : https://nextjs.org/docs
- **React** : https://react.dev/
- **TanStack Query** : https://tanstack.com/query/latest

### Communauté
- GitHub Issues
- GitHub Discussions
- Code Review

---

**Bon développement !** 💻🚀

