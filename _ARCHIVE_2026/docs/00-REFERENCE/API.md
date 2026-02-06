# 🔌 API BACKEND MATHAKINE

**Version** : 2.0.0  
**Base URL** : `http://localhost:8000` (dev) | `https://mathakine-backend.onrender.com` (prod)  
**Date** : 20 novembre 2025

---

## 📊 VUE D'ENSEMBLE

- **37 routes API JSON** pures
- **Aucune route HTML** (supprimées en Phase 2)
- **Format** : REST + SSE pour streaming
- **Auth** : JWT via cookies HTTP-only
- **CORS** : Configuré pour frontend Next.js

---

## 🔐 AUTHENTIFICATION

### POST /api/auth/login
Connexion utilisateur

**Request**
```json
{
  "username": "john.doe",
  "password": "securepassword123"
}
```

**Response 200**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "john.doe",
    "email": "john@example.com",
    "role": "student"
  }
}
```

**Errors**
- `401`: Credentials invalides
- `500`: Erreur serveur

---

### POST /api/auth/refresh
Rafraîchir le token d'accès

**Request**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response 200**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### GET /api/users/me
Obtenir l'utilisateur actuellement connecté

**Headers**
```
Cookie: access_token=<JWT>
```

**Response 200**
```json
{
  "id": 1,
  "username": "john.doe",
  "email": "john@example.com",
  "role": "student",
  "is_active": true,
  "created_at": "2025-01-15T10:30:00Z"
}
```

**Errors**
- `401`: Non authentifié
- `500`: Erreur serveur

---

### POST /api/auth/register
Inscription nouvel utilisateur

**Request**
```json
{
  "username": "jane.smith",
  "email": "jane@example.com",
  "password": "securepassword123",
  "role": "student"
}
```

**Response 201**
```json
{
  "id": 2,
  "username": "jane.smith",
  "email": "jane@example.com",
  "role": "student",
  "is_active": true
}
```

**Errors**
- `400`: Données invalides
- `409`: Username/email déjà existant
- `500`: Erreur serveur

---

## 🎯 CHALLENGES

### GET /api/challenges
Lister tous les challenges avec filtres

**Query Parameters**
- `challenge_type` (optional): SEQUENCE, PATTERN, PUZZLE, CALCULATION, CHESS
- `age_group` (optional): GROUP_6_8, GROUP_10_12, GROUP_13_15
- `difficulty_min` (optional): float
- `difficulty_max` (optional): float

**Example**
```
GET /api/challenges?challenge_type=SEQUENCE&age_group=GROUP_10_12
```

**Response 200**
```json
[
  {
    "id": 1,
    "title": "Suite de Fibonacci",
    "description": "Trouvez le prochain nombre dans la séquence",
    "challenge_type": "SEQUENCE",
    "age_group": "GROUP_10_12",
    "difficulty_rating": 2.5,
    "correct_answer": "13",
    "solution_explanation": "La suite de Fibonacci...",
    "hints": {
      "level_1": "Regardez la relation entre les nombres",
      "level_2": "Chaque nombre est la somme des deux précédents"
    }
  },
  ...
]
```

---

### GET /api/challenges/{id}
Obtenir un challenge par ID

**Response 200**
```json
{
  "id": 1,
  "title": "Suite de Fibonacci",
  "description": "Trouvez le prochain nombre dans la séquence: 0, 1, 1, 2, 3, 5, 8, ?",
  "challenge_type": "SEQUENCE",
  "age_group": "GROUP_10_12",
  "difficulty_rating": 2.5,
  "correct_answer": "13",
  "solution_explanation": "La suite de Fibonacci se construit en additionnant les deux nombres précédents.",
  "hints": {
    "level_1": "Regardez la relation entre les nombres",
    "level_2": "Chaque nombre est la somme des deux précédents",
    "level_3": "0+1=1, 1+1=2, 1+2=3, 2+3=5, 3+5=8, 5+8=?"
  },
  "estimated_time_minutes": 5,
  "created_at": "2025-01-10T08:00:00Z"
}
```

**Errors**
- `404`: Challenge non trouvé
- `500`: Erreur serveur

---

### POST /api/challenges/{id}/attempt
Soumettre une tentative de résolution

**Request**
```json
{
  "user_answer": "13"
}
```

**Response 200**
```json
{
  "is_correct": true,
  "feedback": "Bravo ! Votre réponse est correcte.",
  "points_earned": 50,
  "solution_explanation": "La suite de Fibonacci...",
  "new_badges": ["FIRST_CHALLENGE", "SEQUENCE_MASTER"]
}
```

**Errors**
- `400`: Données invalides
- `401`: Non authentifié
- `404`: Challenge non trouvé
- `500`: Erreur serveur

---

### GET /api/challenges/{id}/hint
Obtenir un indice pour un challenge

**Query Parameters**
- `level` (optional): 1, 2, 3 (niveau d'indice)

**Example**
```
GET /api/challenges/1/hint?level=2
```

**Response 200**
```json
{
  "hint": "Chaque nombre est la somme des deux précédents",
  "level": 2,
  "remaining_hints": 1
}
```

**Errors**
- `404`: Challenge ou niveau non trouvé
- `500`: Erreur serveur

---

### GET /api/challenges/generate-ai-stream
Générer un challenge avec IA (streaming SSE)

**Query Parameters**
- `challenge_type` (required): SEQUENCE, PATTERN, PUZZLE, CALCULATION, CHESS
- `difficulty` (required): easy, medium, hard
- `age_group` (optional): GROUP_6_8, GROUP_10_12, GROUP_13_15

**Example**
```
GET /api/challenges/generate-ai-stream?challenge_type=SEQUENCE&difficulty=medium&age_group=GROUP_10_12
```

**Response (Server-Sent Events)**
```
event: data
data: {"type": "title", "content": "Suite arithmétique"}

event: data
data: {"type": "description", "content": "Trouvez le prochain nombre..."}

event: data
data: {"type": "complete", "challenge": {...}}

event: done
data: {"status": "success"}
```

**Errors**
- `400`: Paramètres invalides
- `401`: Non authentifié
- `500`: Erreur génération IA

---

## 📝 EXERCISES

### GET /api/exercises
Lister tous les exercices avec filtres

**Query Parameters**
- `exercise_type` (optional): ADDITION, SUBTRACTION, MULTIPLICATION, DIVISION
- `difficulty` (optional): EASY, MEDIUM, HARD
- `is_active` (optional): true, false

**Example**
```
GET /api/exercises?exercise_type=ADDITION&difficulty=EASY
```

**Response 200**
```json
[
  {
    "id": 1,
    "title": "Addition simple",
    "exercise_type": "ADDITION",
    "difficulty": "EASY",
    "question": "Combien font 5 + 3 ?",
    "correct_answer": "8",
    "choices": ["6", "7", "8", "9"],
    "explanation": "5 + 3 = 8",
    "hint": "Comptez sur vos doigts",
    "is_active": true
  },
  ...
]
```

---

### POST /api/exercises
Créer un nouvel exercice

**Request**
```json
{
  "title": "Multiplication difficile",
  "exercise_type": "MULTIPLICATION",
  "difficulty": "HARD",
  "question": "Combien font 13 × 17 ?",
  "correct_answer": "221",
  "choices": ["221", "231", "211", "241"],
  "explanation": "13 × 17 = 221",
  "hint": "Utilisez la méthode de la distributivité"
}
```

**Response 201**
```json
{
  "id": 42,
  "title": "Multiplication difficile",
  ...
  "created_at": "2025-01-20T14:30:00Z"
}
```

**Errors**
- `400`: Données invalides
- `401`: Non authentifié
- `403`: Permissions insuffisantes
- `500`: Erreur serveur

---

### GET /api/exercises/{id}
Obtenir un exercice par ID

**Response 200**
```json
{
  "id": 1,
  "title": "Addition simple",
  "exercise_type": "ADDITION",
  "difficulty": "EASY",
  "question": "Combien font 5 + 3 ?",
  "correct_answer": "8",
  "choices": ["6", "7", "8", "9"],
  "explanation": "5 + 3 = 8. L'addition est l'opération qui combine deux nombres.",
  "hint": "Comptez sur vos doigts : 5 doigts + 3 doigts = ?",
  "view_count": 127,
  "success_rate": 0.85,
  "created_at": "2025-01-10T10:00:00Z"
}
```

---

### POST /api/exercises/{id}/attempt
Soumettre une tentative de résolution

**Request**
```json
{
  "user_answer": "8",
  "time_spent_seconds": 15
}
```

**Response 200**
```json
{
  "is_correct": true,
  "feedback": "Excellent ! Réponse correcte.",
  "points_earned": 10,
  "explanation": "5 + 3 = 8",
  "new_badges": []
}
```

---

### GET /api/exercises/generate-ai-stream
Générer un exercice avec IA (streaming SSE)

**Query Parameters**
- `exercise_type` (required): ADDITION, SUBTRACTION, MULTIPLICATION, DIVISION
- `difficulty` (required): EASY, MEDIUM, HARD

**Example**
```
GET /api/exercises/generate-ai-stream?exercise_type=MULTIPLICATION&difficulty=MEDIUM
```

**Response (Server-Sent Events)**
```
event: data
data: {"type": "question", "content": "Combien font 12 × 8 ?"}

event: data
data: {"type": "answer", "content": "96"}

event: data
data: {"type": "complete", "exercise": {...}}
```

---

## 🏆 BADGES & GAMIFICATION

### GET /api/badges/user
Obtenir les badges de l'utilisateur connecté

**Response 200**
```json
{
  "earned_badges": [
    {
      "code": "FIRST_EXERCISE",
      "name": "Premier Exercice",
      "description": "Complété votre premier exercice",
      "icon_url": "/badges/first-exercise.svg",
      "points": 10,
      "earned_at": "2025-01-15T10:30:00Z"
    },
    ...
  ],
  "user_stats": {
    "total_badges": 5,
    "total_points": 250,
    "level": 3,
    "rank": "Padawan"
  }
}
```

---

### GET /api/badges/available
Obtenir tous les badges disponibles

**Response 200**
```json
[
  {
    "code": "FIRST_EXERCISE",
    "name": "Premier Exercice",
    "description": "Complété votre premier exercice",
    "icon_url": "/badges/first-exercise.svg",
    "points": 10,
    "criteria": {
      "type": "exercise_completion",
      "count": 1
    }
  },
  {
    "code": "CHALLENGE_MASTER",
    "name": "Maître des Défis",
    "description": "Réussi 50 défis",
    "icon_url": "/badges/challenge-master.svg",
    "points": 500,
    "criteria": {
      "type": "challenge_completion",
      "count": 50
    }
  },
  ...
]
```

---

### POST /api/badges/check
Vérifier et attribuer les nouveaux badges

**Response 200**
```json
{
  "new_badges": [
    {
      "code": "SEQUENCE_MASTER",
      "name": "Maître des Séquences",
      "points": 100
    }
  ],
  "message": "1 nouveaux badges obtenus"
}
```

---

### GET /api/gamification/stats
Obtenir les statistiques de gamification

**Response 200**
```json
{
  "user_id": 1,
  "total_points": 750,
  "level": 5,
  "rank": "Chevalier Jedi",
  "progress_to_next_level": 0.65,
  "stats": {
    "exercises_completed": 45,
    "challenges_completed": 23,
    "badges_earned": 8,
    "average_success_rate": 0.87,
    "total_time_spent_minutes": 320
  },
  "recent_achievements": [
    {
      "type": "badge",
      "name": "SEQUENCE_MASTER",
      "earned_at": "2025-01-20T14:00:00Z"
    },
    ...
  ]
}
```

---

## 👤 USER & STATS

### GET /api/users/stats
Statistiques de l'utilisateur connecté

**Response 200**
```json
{
  "exercises_completed": 45,
  "challenges_completed": 23,
  "total_attempts": 78,
  "success_rate": 0.87,
  "favorite_exercise_type": "MULTIPLICATION",
  "favorite_challenge_type": "SEQUENCE",
  "total_points": 750,
  "current_streak_days": 7,
  "longest_streak_days": 14
}
```

---

### GET /api/users/progress
Progression de l'utilisateur

**Response 200**
```json
{
  "weekly_progress": [
    {"date": "2025-01-13", "exercises": 5, "challenges": 2, "points": 75},
    {"date": "2025-01-14", "exercises": 7, "challenges": 3, "points": 110},
    ...
  ],
  "current_goals": [
    {
      "type": "daily_exercises",
      "target": 5,
      "current": 3,
      "progress": 0.6
    },
    ...
  ]
}
```

---

### PUT /api/users/me
Mettre à jour le profil utilisateur

**Request**
```json
{
  "email": "newemail@example.com",
  "preferences": {
    "theme": "dark",
    "language": "fr"
  }
}
```

**Response 200**
```json
{
  "id": 1,
  "username": "john.doe",
  "email": "newemail@example.com",
  "preferences": {
    "theme": "dark",
    "language": "fr"
  }
}
```

---

## ⚠️ CODES D'ERREUR

| Code | Signification | Description |
|------|---------------|-------------|
| `200` | OK | Succès |
| `201` | Created | Ressource créée |
| `400` | Bad Request | Données invalides |
| `401` | Unauthorized | Non authentifié |
| `403` | Forbidden | Permissions insuffisantes |
| `404` | Not Found | Ressource non trouvée |
| `409` | Conflict | Conflit (ex: username existant) |
| `500` | Internal Server Error | Erreur serveur |

---

## 🔄 SERVER-SENT EVENTS (SSE)

### Format des événements

```
event: data
data: {"type": "...", "content": "..."}

event: error
data: {"message": "..."}

event: done
data: {"status": "success"}
```

### Gestion côté client

```typescript
const eventSource = new EventSource('/api/challenges/generate-ai-stream?...');

eventSource.addEventListener('data', (event) => {
  const data = JSON.parse(event.data);
  // Traiter les données
});

eventSource.addEventListener('done', () => {
  eventSource.close();
});

eventSource.onerror = (error) => {
  console.error('SSE Error:', error);
  eventSource.close();
};
```

---

## 📚 RÉFÉRENCES

- **Architecture** : [`ARCHITECTURE.md`](ARCHITECTURE.md)
- **Getting Started** : [`../01-GUIDES/GETTING_STARTED.md`](../01-GUIDES/GETTING_STARTED.md)
- **Tests API** : [`../01-GUIDES/TESTING.md`](../01-GUIDES/TESTING.md)

---

**Total : 37 routes API JSON pures**  
**Dernière mise à jour** : 20 novembre 2025

