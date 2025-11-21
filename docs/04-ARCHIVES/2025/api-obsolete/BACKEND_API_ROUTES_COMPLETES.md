# 📋 BACKEND STARLETTE - ROUTES API COMPLÈTES

**Date** : 20 novembre 2025  
**Backend** : Starlette (port 8000)  
**Statut** : ✅ **API JSON PURE - 37 ROUTES**

---

## 🎯 ROUTES PAR CATÉGORIE

### 🔐 AUTHENTIFICATION (6 routes)

#### POST `/api/auth/login`
**Description** : Connexion avec username/password  
**Body** :
```json
{
  "username": "string",
  "password": "string"
}
```
**Response 200** :
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "role": "user",
    "is_email_verified": true
  }
}
```
**Cookie** : `access_token` (httponly, samesite=lax)

---

#### POST `/api/auth/refresh`
**Description** : Rafraîchir le token d'accès  
**Body** :
```json
{
  "refresh_token": "string"
}
```
**Response 200** :
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

---

#### POST `/api/auth/logout`
**Description** : Déconnexion (invalide le token côté client)  
**Headers** : `Cookie: access_token=...`  
**Response 200** :
```json
{
  "detail": "Déconnecté avec succès"
}
```

---

#### POST `/api/auth/forgot-password`
**Description** : Demander réinitialisation mot de passe  
**Body** :
```json
{
  "email": "user@example.com"
}
```
**Response 200** :
```json
{
  "message": "Si cette adresse email est associée à un compte...",
  "success": true
}
```

---

#### GET `/api/auth/verify-email?token=...`
**Description** : Vérifier l'email avec un token  
**Query Params** : `token=abc123`  
**Response 200** :
```json
{
  "message": "Email vérifié avec succès",
  "success": true,
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "is_email_verified": true
  }
}
```

---

#### POST `/api/auth/resend-verification`
**Description** : Renvoyer l'email de vérification  
**Body** :
```json
{
  "email": "user@example.com"
}
```
**Response 200** :
```json
{
  "message": "Email de vérification envoyé"
}
```

---

### 👤 USERS (3 routes)

#### POST `/api/users/`
**Description** : Créer un nouveau compte utilisateur  
**Body** :
```json
{
  "username": "string",
  "email": "user@example.com",
  "password": "string",
  "full_name": "John Doe" // optionnel
}
```
**Response 201** :
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "created_at": "2025-11-20T...",
  "is_email_verified": false
}
```

---

#### GET `/api/users/me`
**Description** : Récupérer les infos de l'utilisateur connecté  
**Headers** : `Cookie: access_token=...`  
**Response 200** :
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "is_authenticated": true,
  "role": "user"
}
```

---

#### GET `/api/users/stats`
**Description** : Récupérer les statistiques de l'utilisateur  
**Headers** : `Cookie: access_token=...`  
**Response 200** :
```json
{
  "total_exercises": 42,
  "completed_exercises": 38,
  "success_rate": 90.5,
  "total_challenges": 15,
  "completed_challenges": 12
}
```

---

### 📚 EXERCISES (8 routes)

#### GET `/api/exercises?limit=10&offset=0`
**Description** : Liste des exercices  
**Response 200** :
```json
[
  {
    "id": 1,
    "title": "Addition simple",
    "difficulty": "easy",
    "type": "calculation"
  }
]
```

---

#### GET `/api/exercises/{exercise_id}`
**Description** : Détails d'un exercice  
**Response 200** :
```json
{
  "id": 1,
  "title": "Addition simple",
  "description": "Calculer 5 + 3",
  "difficulty": "easy",
  "type": "calculation",
  "question": "5 + 3 = ?",
  "correct_answer": "8"
}
```

---

#### DELETE `/api/exercises/{exercise_id}`
**Description** : Supprimer (archiver) un exercice  
**Response 200** :
```json
{
  "message": "Exercice archivé avec succès",
  "id": 1
}
```

---

#### GET `/api/exercises/generate?difficulty=easy&type=calculation`
**Description** : Générer un exercice aléatoire  
**Response 200** : Même structure que GET `/api/exercises/{id}`

---

#### POST `/api/exercises/generate`
**Description** : Générer un exercice avec paramètres avancés  
**Body** :
```json
{
  "difficulty": "medium",
  "type": "logic",
  "age_group": "age_9_11"
}
```

---

#### GET `/api/exercises/generate-ai-stream?type=calculation&difficulty=easy`
**Description** : Générer un exercice avec IA (streaming)  
**Headers** : `Accept: text/event-stream`  
**Response** : Server-Sent Events (SSE)

---

#### GET `/api/exercises/completed-ids`
**Description** : IDs des exercices complétés par l'utilisateur  
**Response 200** :
```json
{
  "completed_ids": [1, 2, 5, 8, 12]
}
```

---

#### POST `/api/submit-answer`
**Description** : Soumettre une réponse à un exercice  
**Body** :
```json
{
  "exercise_id": 1,
  "answer": "8"
}
```
**Response 200** :
```json
{
  "correct": true,
  "message": "Bonne réponse !",
  "points_earned": 10
}
```

---

### 🏆 BADGES (4 routes)

#### GET `/api/badges/user`
**Description** : Badges de l'utilisateur connecté  

#### GET `/api/badges/available`
**Description** : Badges disponibles  

#### POST `/api/badges/check`
**Description** : Vérifier si de nouveaux badges sont débloqués  

#### GET `/api/badges/stats`
**Description** : Statistiques badges de l'utilisateur  

---

### 💡 RECOMMENDATIONS (3 routes)

#### GET `/api/recommendations`
**Description** : Obtenir des recommandations d'exercices  

#### POST `/api/recommendations/generate`
**Description** : Générer de nouvelles recommandations  

#### POST `/api/recommendations/complete`
**Description** : Marquer une recommandation comme complétée  

---

### 💬 CHAT (2 routes)

#### POST `/api/chat`
**Description** : Envoyer un message au chatbot  

#### POST `/api/chat/stream`
**Description** : Chat en streaming (SSE)  

---

### 🎯 CHALLENGES (10 routes)

#### GET `/api/challenges?limit=10&challenge_type=calculation&age_group=age_6_8`
**Description** : Liste des challenges avec filtres  
**Query Params** :
- `limit` : Nombre de résultats
- `offset` : Pagination
- `challenge_type` : `calculation`, `logic`, `spatial`, `pattern`, `memory`
- `age_group` : `age_6_8`, `age_9_11`, `age_12_15`
- `difficulty` : `easy`, `medium`, `hard`, `expert`

**Response 200** :
```json
[
  {
    "id": 1,
    "title": "Défi Addition",
    "challenge_type": "calculation",
    "difficulty": "easy",
    "age_group": "age_6_8",
    "points": 10
  }
]
```

---

#### GET `/api/challenges/{challenge_id}`
**Description** : Détails d'un challenge  

---

#### POST `/api/challenges/{challenge_id}/attempt`
**Description** : Soumettre une tentative de challenge  

---

#### GET `/api/challenges/{challenge_id}/hint`
**Description** : Obtenir un indice pour un challenge  

---

#### GET `/api/challenges/completed-ids`
**Description** : IDs des challenges complétés  

---

#### POST `/api/challenges/start/{challenge_id}`
**Description** : Démarrer un challenge  

---

#### GET `/api/challenges/progress/{challenge_id}`
**Description** : Progression sur un challenge  

---

#### GET `/api/challenges/rewards/{challenge_id}`
**Description** : Récompenses d'un challenge  

---

#### GET `/api/challenges/generate-ai-stream?challenge_type=calculation&difficulty=easy`
**Description** : Générer un challenge avec IA (streaming) ⚠️ CRITIQUE  
**Headers** : `Accept: text/event-stream`  
**Response** : Server-Sent Events (SSE)

**Paramètres** :
- `challenge_type` : `calculation`, `logic`, `spatial`, `pattern`, `memory`
- `difficulty` : `easy`, `medium`, `hard`, `expert`
- `age_group` : `age_6_8`, `age_9_11`, `age_12_15`

---

#### GET `/api/challenges/badges/progress`
**Description** : Progression badges liés aux challenges  

---

### 🏅 LEADERBOARD (1 route)

#### GET `/api/users/leaderboard`
**Description** : Classement des utilisateurs  

---

## 📊 RÉSUMÉ

```
Total : 37 routes API JSON

Authentification    : 6 routes
Users              : 3 routes
Exercises          : 8 routes
Badges             : 4 routes
Recommendations    : 3 routes
Chat               : 2 routes
Challenges         : 10 routes
Leaderboard        : 1 route
```

---

## 🔗 BASE URL

### Développement local
```
http://localhost:8000
```

### Production (Render)
```
https://mathakine-alpha.onrender.com
```

---

## 🔑 AUTHENTIFICATION

### Méthode 1 : Cookie (recommandé)
Le cookie `access_token` est automatiquement défini lors du login et envoyé avec chaque requête.

### Méthode 2 : Header Authorization
```
Authorization: Bearer eyJ...
```

---

## ⚠️ ROUTES NON IMPLÉMENTÉES (optionnelles)

Ces routes n'existent pas encore mais peuvent être ajoutées si nécessaire :

```
PUT    /api/users/me                 ← Modifier profil
DELETE /api/users/me                 ← Supprimer compte
PUT    /api/users/me/password        ← Changer mot de passe
GET    /api/users/me/export          ← Exporter données RGPD
```

---

**Document créé le** : 20 novembre 2025  
**Backend** : Starlette (server/)  
**Frontend** : Next.js (frontend/)  
**Architecture** : API JSON pure

