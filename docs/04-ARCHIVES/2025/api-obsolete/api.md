# 📚 Référence API Mathakine

**Documentation complète des endpoints API** - Version 1.5.0  
*Dernière mise à jour : 6 juin 2025*

---

## 🎯 Vue d'Ensemble

L'API Mathakine expose **40+ endpoints REST** organisés en 5 domaines principaux. L'architecture dual-backend (FastAPI + Starlette) offre une API pure pour intégrations externes et une interface web intégrée.

### Informations Générales
- **Base URL** : `http://localhost:8000/api`
- **Format** : JSON exclusivement
- **Authentification** : JWT Bearer tokens
- **Versioning** : Headers `Accept-Version: v1`
- **Rate Limiting** : 100 req/min par IP

---

## 📚 Documentation Interactive

### Interfaces Automatiques
- **🔧 Swagger UI** : `/api/docs` - Interface interactive pour tester les endpoints
- **📖 ReDoc** : `/api/redoc` - Documentation lisible et organisée  
- **📄 OpenAPI Spec** : `/api/openapi.json` - Spécification technique complète

---

## 🔑 Authentification

### Obtention d'un Token JWT

#### `POST /api/auth/login`
Authentifie un utilisateur et retourne un token d'accès.

**Corps de la requête** :
```json
{
  "username": "ObiWan",
  "password": "motdepasse123"
}
```

**Réponse (200 OK)** :
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": 1,
    "username": "ObiWan",
    "role": "user",
    "jedi_rank": "Padawan"
  }
}
```

**Codes d'erreur** :
- `400` : Données invalides
- `401` : Identifiants incorrects
- `429` : Trop de tentatives

### Utilisation du Token
Pour tous les endpoints sécurisés, inclure le header :
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Déconnexion

#### `POST /api/auth/logout`
Invalide le token actuel.

**Réponse (200 OK)** :
```json
{
  "message": "Déconnexion réussie"
}
```

---

## 👤 Endpoints Utilisateurs

### Liste des Utilisateurs

#### `GET /api/users/`
Récupère la liste des utilisateurs (accès restreint).

**Permissions** : Gardien, Archiviste  
**Paramètres de requête** :
- `skip` (int, défaut: 0) : Pagination - éléments à ignorer
- `limit` (int, défaut: 100) : Nombre maximum d'éléments
- `role` (string, optionnel) : Filtrer par rôle (user, gardien, archiviste)

**Exemple de requête** :
```http
GET /api/users/?skip=0&limit=10&role=user
Authorization: Bearer <token>
```

**Réponse (200 OK)** :
```json
{
  "users": [
    {
      "id": 1,
      "username": "ObiWan", 
      "email": "obiwan@jedi.temple",
      "full_name": "Obi-Wan Kenobi",
      "role": "user",
      "jedi_rank": "Maître",
      "total_points": 1250,
      "current_level": 5,
      "created_at": "2025-01-15T10:30:00Z",
      "is_active": true
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 10
}
```

### Créer un Utilisateur

#### `POST /api/users/`
Inscription d'un nouvel utilisateur.

**Accès** : Public  
**Corps de la requête** :
```json
{
  "username": "AnakinSky",
  "email": "anakin@tatooine.net", 
  "password": "MotDePasseSecurise123!",
  "full_name": "Anakin Skywalker",
  "grade_level": "CM1",
  "preferred_difficulty": "padawan"
}
```

**Réponse (201 Created)** :
```json
{
  "id": 42,
  "username": "AnakinSky",
  "email": "anakin@tatooine.net",
  "full_name": "Anakin Skywalker", 
  "role": "user",
  "jedi_rank": "Initié",
  "created_at": "2025-06-06T14:30:00Z"
}
```

### Profil Utilisateur Actuel

#### `GET /api/users/me`
Récupère les informations de l'utilisateur connecté.

**Permissions** : Utilisateur authentifié  
**Réponse (200 OK)** :
```json
{
  "id": 1,
  "username": "ObiWan",
  "email": "obiwan@jedi.temple", 
  "full_name": "Obi-Wan Kenobi",
  "role": "user",
  "jedi_rank": "Maître",
  "grade_level": "6ème",
  "learning_style": "visuel",
  "preferred_difficulty": "chevalier",
  "total_points": 1250,
  "current_level": 5,
  "experience_points": 3400,
  "accessibility_settings": {
    "high_contrast": false,
    "large_text": false,
    "reduced_motion": true,
    "dyslexia_font": false
  },
  "statistics": {
    "exercises_completed": 156,
    "success_rate": 87.5,
    "average_time": 45.2,
    "streak": 7
  }
}
```

### Détails d'un Utilisateur

#### `GET /api/users/{user_id}`
Récupère les détails d'un utilisateur spécifique.

**Permissions** : Gardien, Archiviste ou l'utilisateur lui-même  
**Paramètres** :
- `user_id` (int) : ID de l'utilisateur

**Exemple** :
```http
GET /api/users/42
Authorization: Bearer <token>
```

### Mise à Jour Profil

#### `PUT /api/users/me`
Met à jour le profil de l'utilisateur connecté.

**Corps de la requête** :
```json
{
  "full_name": "Obi-Wan Kenobi (Maître)",
  "preferred_difficulty": "maitre",
  "accessibility_settings": {
    "high_contrast": true,
    "large_text": false,
    "reduced_motion": true,
    "dyslexia_font": false
  }
}
```

### Suppression d'Utilisateur

#### `DELETE /api/users/{user_id}`
Supprime un utilisateur et toutes ses données (cascade).

**Permissions** : Archiviste uniquement  
**Réponse (204 No Content)** : Suppression réussie

---

## 📝 Endpoints Exercices

### Liste des Exercices

#### `GET /api/exercises/`
Récupère la liste des exercices disponibles.

**Accès** : Public  
**Paramètres de requête** :
- `exercise_type` (string) : Type (`addition`, `fractions`, `geometrie`, `divers`)
- `difficulty` (string) : Niveau (`initie`, `padawan`, `chevalier`, `maitre`)

**Réponse (200 OK)** :
```json
{
  "exercises": [
    {
      "id": 12,
      "title": "Fractions : Addition Niveau Padawan",
      "exercise_type": "fractions",
      "difficulty": "padawan",
      "question": "Calcule 5/6 + 3/4",
      "choices": ["19/12", "8/10", "15/24", "2/5"],
      "correct_answer": "19/12",
      "estimated_time_minutes": 3,
      "difficulty_rating": 2.5,
      "success_rate": 78.5,
      "created_at": "2025-06-01T09:15:00Z"
    }
  ]
}
```

### Générer un Exercice

#### `POST /api/exercises/generate`
Génère un nouvel exercice selon les paramètres.

**Corps de la requête** :
```json
{
  "exercise_type": "fractions",
  "difficulty": "chevalier", 
  "save": true
}
```

**Réponse (201 Created)** :
```json
{
  "id": 156,
  "title": "Fractions : Multiplication Niveau Chevalier",
  "exercise_type": "fractions",
  "difficulty": "chevalier",
  "question": "Calcule 7/9 × 4/5",
  "choices": ["28/45", "11/14", "35/40", "28/40"],
  "correct_answer": "28/45",
  "solution_explanation": "7/9 × 4/5 = (7×4)/(9×5) = 28/45"
}
```

### Soumettre une Réponse

#### `POST /api/exercises/{exercise_id}/submit`
Soumet une réponse à un exercice.

**Permissions** : Utilisateur authentifié  
**Corps de la requête** :
```json
{
  "answer": "28/45",
  "time_spent": 142
}
```

**Réponse (200 OK)** :
```json
{
  "is_correct": true,
  "score": 100,
  "feedback": "Excellente réponse ! Tu maîtrises la multiplication des fractions.",
  "points_earned": 15,
  "user_stats": {
    "total_points": 1265,
    "success_rate": 87.8
  }
}
```

---

## 🧩 Endpoints Défis Logiques

### Liste des Défis

#### `GET /api/challenges/`
Récupère la liste des défis logiques disponibles.

**Réponse (200 OK)** :
```json
{
  "challenges": [
    {
      "id": 2292,
      "title": "🚀 Code de Navigation Spatiale",
      "description": "Trouve le prochain code de la séquence de navigation",
      "challenge_type": "SEQUENCE",
      "age_group": "12-13",
      "question": "Quelle est la prochaine valeur : 2 → 4 → 8 → 16 → ?",
      "correct_answer": "32",
      "difficulty_rating": 2.5,
      "estimated_time_minutes": 8
    }
  ]
}
```

### Tenter un Défi

#### `POST /api/challenges/{challenge_id}/attempt`
Soumet une tentative de résolution d'un défi.

**Corps de la requête** :
```json
{
  "answer": "32",
  "time_spent": 425
}
```

**Réponse (200 OK)** :
```json
{
  "is_correct": true,
  "score": 85,
  "feedback": "Parfait ! Tu as identifié le bon pattern.",
  "points_earned": 25
}
```

---

## 📊 Endpoints Tableau de Bord

### Statistiques Utilisateur

#### `GET /api/dashboard/stats`
Récupère les statistiques complètes de l'utilisateur connecté.

**Réponse (200 OK)** :
```json
{
  "global_stats": {
    "total_points": 1265,
    "exercises_completed": 157,
    "success_rate": 87.8,
    "current_streak": 8,
    "jedi_rank": "Chevalier"
  },
  "exercise_stats": {
    "by_type": {
      "addition": {"completed": 45, "success_rate": 91.1},
      "fractions": {"completed": 23, "success_rate": 78.3},
      "geometrie": {"completed": 18, "success_rate": 83.3}
    }
  }
}
```

### Graphique de Progression

#### `GET /api/dashboard/progress`
Récupère les données pour le graphique de progression.

**Paramètres de requête** :
- `period` (string) : Période (`7d`, `30d`, `90d`, `1y`)
- `metric` (string) : Métrique (`attempts`, `success_rate`, `points`)

**Réponse (200 OK)** :
```json
{
  "period": "30d",
  "metric": "attempts",
  "data": [
    {
      "date": "2025-05-07",
      "value": 3,
      "success_rate": 100.0
    },
    {
      "date": "2025-05-08", 
      "value": 5,
      "success_rate": 80.0
    }
  ],
  "summary": {
    "total_attempts": 89,
    "total_successes": 78,
    "average_daily": 2.97,
    "trend": "increasing"
  }
}
```

### Recommandations

#### `GET /api/dashboard/recommendations`
Récupère les recommandations personnalisées.

**Réponse (200 OK)** :
```json
{
  "next_exercises": [
    {
      "exercise_type": "fractions",
      "difficulty": "chevalier",
      "reason": "Continue sur les fractions pour renforcer tes acquis",
      "confidence": 0.85
    }
  ],
  "skill_focus": [
    {
      "skill": "Division de fractions",
      "current_level": 0.68,
      "target_level": 0.80,
      "recommended_exercises": 5
    }
  ],
  "challenges": [
    {
      "challenge_id": 2295,
      "title": "🔺 Géométrie des Astéroïdes",
      "reason": "Parfait pour ton niveau en géométrie",
      "estimated_success": 0.78
    }
  ]
}
```

---

## 🛡️ Gestion des Erreurs

### Codes de Statut HTTP

| Code | Signification | Usage |
|------|---------------|--------|
| 200 | OK | Requête réussie |
| 201 | Created | Ressource créée |
| 204 | No Content | Suppression réussie |
| 400 | Bad Request | Données invalides |
| 401 | Unauthorized | Token manquant/invalide |
| 403 | Forbidden | Permissions insuffisantes |
| 404 | Not Found | Ressource introuvable |
| 409 | Conflict | Conflit (ex: email existant) |
| 422 | Unprocessable Entity | Validation échouée |
| 429 | Too Many Requests | Rate limit dépassé |
| 500 | Internal Server Error | Erreur serveur |

### Format des Erreurs

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Les données fournies sont invalides",
    "details": {
      "field": "email",
      "reason": "Format d'email invalide"
    }
  }
}
```

### Codes d'Erreur Spécifiques

#### Authentification
- `INVALID_CREDENTIALS` : Identifiants incorrects
- `TOKEN_EXPIRED` : Token JWT expiré
- `TOKEN_INVALID` : Token malformé
- `ACCOUNT_INACTIVE` : Compte désactivé

#### Validation
- `MISSING_FIELD` : Champ requis manquant
- `INVALID_FORMAT` : Format de données incorrect
- `VALUE_TOO_LONG` : Valeur trop longue
- `VALUE_TOO_SHORT` : Valeur trop courte

#### Business Logic
- `EXERCISE_NOT_FOUND` : Exercice introuvable
- `INSUFFICIENT_PERMISSIONS` : Permissions insuffisantes
- `DUPLICATE_ENTRY` : Entrée dupliquée (email/username)
- `CHALLENGE_ALREADY_COMPLETED` : Défi déjà résolu

---

## 🔧 Paramètres et Configuration

### Headers Requis

#### Authentification
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
Accept: application/json
```

#### Versionning (Optionnel)
```http
Accept-Version: v1
```

#### Tracking (Optionnel)
```http
X-Request-ID: unique-request-identifier
X-User-Agent: Mathakine-Client/1.0
```

### Paramètres de Pagination

Tous les endpoints de liste supportent :
- `skip` (int) : Nombre d'éléments à ignorer (défaut: 0)
- `limit` (int) : Nombre maximum d'éléments (défaut: 100, max: 1000)

### Filtres Avancés

#### Exercices
- `search` (string) : Recherche textuelle
- `tags` (array) : Filtrer par tags
- `created_after` (datetime) : Créés après cette date
- `difficulty_min` (float) : Difficulté minimale (1.0-5.0)

#### Utilisateurs  
- `role` (string) : Filtrer par rôle
- `active_only` (bool) : Utilisateurs actifs uniquement
- `jedi_rank` (string) : Filtrer par rang Jedi

---

## 📚 Exemples d'Intégration

### Client JavaScript

```javascript
class MathakineAPI {
  constructor(baseURL = 'http://localhost:8000/api') {
    this.baseURL = baseURL;
    this.token = null;
  }

  async login(username, password) {
    const response = await fetch(`${this.baseURL}/auth/login`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({username, password})
    });
    const data = await response.json();
    this.token = data.access_token;
    return data;
  }

  async generateExercise(type, difficulty) {
    return fetch(`${this.baseURL}/exercises/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.token}`
      },
      body: JSON.stringify({exercise_type: type, difficulty})
    }).then(r => r.json());
  }
}
```

### Client Python

```python
import requests
from typing import Optional, Dict, Any

class MathakineAPIClient:
    def __init__(self, base_url: str = "http://localhost:8000/api", token: Optional[str] = None):
        self.base_url = base_url
        self.token = token
        self.session = requests.Session()
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[Any, Any]:
        headers = kwargs.pop('headers', {})
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        headers['Content-Type'] = 'application/json'
        
        response = self.session.request(
            method=method,
            url=f"{self.base_url}{endpoint}",
            headers=headers,
            **kwargs
        )
        response.raise_for_status()
        return response.json()
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        data = self._request('POST', '/auth/login', json={
            'username': username,
            'password': password
        })
        self.token = data['access_token']
        return data
    
    def get_exercises(self, exercise_type: Optional[str] = None, 
                     difficulty: Optional[str] = None, 
                     limit: int = 100) -> Dict[str, Any]:
        params = {'limit': limit}
        if exercise_type:
            params['exercise_type'] = exercise_type
        if difficulty:
            params['difficulty'] = difficulty
            
        return self._request('GET', '/exercises/', params=params)
    
    def submit_exercise(self, exercise_id: int, answer: str, time_spent: int) -> Dict[str, Any]:
        return self._request('POST', f'/exercises/{exercise_id}/submit', json={
            'answer': answer,
            'time_spent': time_spent
        })

# Usage
client = MathakineAPIClient()
client.login('ObiWan', 'motdepasse123')
exercises = client.get_exercises(exercise_type='fractions', difficulty='padawan')
result = client.submit_exercise(156, '28/45', 142)
```

---

## 🚀 Rate Limiting et Performance

### Limites par Défaut
- **Utilisateurs non-authentifiés** : 30 req/min
- **Utilisateurs authentifiés** : 100 req/min  
- **Utilisateurs premium** : 300 req/min
- **API clients** : 1000 req/min

### Headers de Rate Limiting
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1717689600
Retry-After: 60
```

### Optimisations Recommandées
- **Mise en cache** : Cache les réponses GET pendant 5-15 minutes
- **Pagination** : Utilisez `limit` raisonnable (≤ 50 pour UI)
- **Filtres** : Appliquez des filtres pour réduire les données
- **Compression** : Activez gzip pour les gros payloads

---

## 📖 Changelog API

### Version 1.5.0 (Juin 2025)
- ✨ **Nouveaux endpoints** : 3 nouveaux types d'exercices (fractions, géométrie, divers)
- ✨ **Défis logiques** : 5 nouveaux défis spatiaux Star Wars
- 🔧 **Authentification améliorée** : Cookies HTTP-only pour session web
- 📊 **Statistiques temps réel** : Nouvelles métriques dashboard
- 🛡️ **Sécurité renforcée** : Protection CSRF et validation améliorée

### Version 1.4.0 (Mai 2025)  
- ✨ **Système de badges** : Endpoints pour accomplissements
- 📈 **Analytics avancées** : Métriques de progression détaillées
- 🎯 **Recommandations** : IA pour suggestions personnalisées

---

**API conçue pour l'intégration et la performance** 🚀📚

*Documentation générée automatiquement - Version 1.5.0* 