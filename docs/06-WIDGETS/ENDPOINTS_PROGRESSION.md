# Endpoints de Progression - Disponibles pour Dashboard

Ce document liste les endpoints de progression **déjà implémentés** en Starlette qui peuvent être utilisés dans le dashboard frontend.

## 📊 Endpoints actuellement actifs

### 1. GET /api/users/stats
**Utilisé par :** `frontend/hooks/useUserStats.ts`

**Paramètres :**
- `timeRange`: "7" | "30" | "90" | "all"

**Réponse :**
```json
{
  "total_attempts": 50,
  "correct_attempts": 40,
  "success_rate": 80,
  "experience_points": 500,
  "level": {
    "current": 5,
    "progress_to_next": 60
  },
  "performance_by_type": {
    "addition": {
      "completed": 10,
      "correct": 9,
      "success_rate": 90.0
    }
  },
  "recent_activity": [...]
}
```

---

## 🎯 Endpoints disponibles mais non utilisés (prêts pour intégration)

### 2. GET /api/users/me/progress
**Disponible :** ✅ Starlette handler (`server/handlers/user_handlers.py`)

**Route :** `/api/users/me/progress`

**Authentification :** Required (Cookie ou Bearer token)

**Réponse :**
```json
{
  "total_attempts": 50,
  "correct_attempts": 40,
  "accuracy": 0.8,
  "average_time": 23.5,
  "exercises_completed": 25,
  "highest_streak": 12,
  "current_streak": 5,
  "by_category": {
    "addition": {
      "completed": 10,
      "accuracy": 0.9
    },
    "multiplication": {
      "completed": 8,
      "accuracy": 0.75
    }
  }
}
```

**Utilisation suggérée :**
- Widget "Streak" dans le dashboard
- Graphique "Progression par catégorie"
- Badge "Meilleur streak"

---

### 3. GET /api/users/me/challenges/progress
**Disponible :** ✅ Starlette handler (`server/handlers/user_handlers.py`)

**Route :** `/api/users/me/challenges/progress`

**Authentification :** Required (Cookie ou Bearer token)

**Réponse :**
```json
{
  "completed_challenges": 5,
  "total_challenges": 20,
  "success_rate": 0.83,
  "average_time": 45.5,
  "challenges": [
    {
      "id": 1,
      "title": "Défi de déduction logique",
      "is_completed": true,
      "attempts": 2,
      "best_time": 35.2
    }
  ]
}
```

**Utilisation suggérée :**
- Section "Défis complétés" dans le dashboard
- Graphique temps moyen par défi
- Badges de défi (complétés X/Y)

---

## 🔧 Intégration dans le dashboard

### Étape 1 : Créer un hook React Query

```typescript
// frontend/hooks/useProgressStats.ts
export function useProgressStats() {
  return useQuery({
    queryKey: ['user', 'progress'],
    queryFn: async () => {
      return await api.get<ProgressStats>('/api/users/me/progress');
    }
  });
}

export function useChallengesProgress() {
  return useQuery({
    queryKey: ['user', 'challenges', 'progress'],
    queryFn: async () => {
      return await api.get<ChallengesProgress>('/api/users/me/challenges/progress');
    }
  });
}
```

### Étape 2 : Utiliser dans le dashboard

```typescript
// frontend/app/dashboard/page.tsx
const { data: progress } = useProgressStats();
const { data: challengesProgress } = useChallengesProgress();

// Afficher le streak actuel
<StreakWidget current={progress?.current_streak} best={progress?.highest_streak} />

// Afficher les défis complétés
<ChallengesWidget completed={challengesProgress?.completed_challenges} total={challengesProgress?.total_challenges} />
```

---

## 📝 Notes techniques

- **Architecture actuelle :** Starlette pur (port 10000)
- **FastAPI archivé :** `_ARCHIVE_2026/app/main.py` + `_ARCHIVE_2026/app/api/api.py`
- **Handlers actifs :** `server/handlers/user_handlers.py`
- **Routes :** `server/routes.py` (86 routes totales)

**Authentification supportée :**
- ✅ Cookie `access_token` (HttpOnly)
- ✅ Header `Authorization: Bearer <token>` (ajouté pour tests/API clients)

---

## 🧪 Test

Script de test disponible : `test_progress_api.py`

```bash
python test_progress_api.py
```
