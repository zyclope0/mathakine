# Analytics et Suivi de Progression

> **Statut** : Idées à implémenter  
> **Date** : 06/02/2026  
> **Endpoint existant** : `/api/exercises/stats`

## Objectif

Proposer des visualisations qui démontrent l'efficacité pédagogique du site et la progression des utilisateurs.

---

## 1. Graphiques de Progression Utilisateur

### 1.1 Courbe d'évolution du taux de réussite

| Élément | Description |
|---------|-------------|
| **Données sources** | `Attempt.created_at` + `Attempt.is_correct` |
| **Type de graphique** | Ligne temporelle (jour/semaine/mois) |
| **Valeur ajoutée** | Montre l'amélioration concrète au fil du temps |
| **Endpoint à créer** | `GET /api/users/me/progress/timeline?period=week` |

### 1.2 Temps de résolution moyen

| Élément | Description |
|---------|-------------|
| **Données sources** | `Attempt.time_spent` |
| **Type de graphique** | Ligne descendante |
| **Valeur ajoutée** | Prouve l'automatisation des compétences (plus rapide = maîtrise) |
| **Endpoint à créer** | Inclure dans timeline ci-dessus |

### 1.3 Progression par discipline

| Élément | Description |
|---------|-------------|
| **Données sources** | `Exercise.exercise_type` + taux de réussite |
| **Type de graphique** | Multi-lignes ou radar chart |
| **Valeur ajoutée** | Identifier forces et faiblesses |
| **Endpoint existant** | `/api/exercises/stats` → `by_discipline` |

---

## 2. Graphiques de Montée en Difficulté

### 2.1 Distribution des niveaux réussis

| Élément | Description |
|---------|-------------|
| **Données sources** | `Exercise.difficulty_level` des exercices réussis |
| **Type de graphique** | Barres empilées ou "funnel" |
| **Valeur ajoutée** | Montre le passage Initié → Padawan → Chevalier → Maître |
| **Endpoint existant** | `/api/exercises/stats` → `by_rank` |

### 2.2 Taux de réussite maintenu malgré difficulté croissante

| Élément | Description |
|---------|-------------|
| **Données sources** | Croisement difficulté × réussite × temps |
| **Type de graphique** | Scatter plot ou heatmap |
| **Valeur ajoutée** | Preuve de maîtrise solide (pas juste des exercices faciles) |
| **Endpoint à créer** | `GET /api/users/me/progress/difficulty-curve` |

---

## 3. Graphiques d'Engagement

### 3.1 Heatmap d'activité

| Élément | Description |
|---------|-------------|
| **Données sources** | `Attempt.created_at` (horodatage) |
| **Type de graphique** | Calendrier type contributions GitHub |
| **Valeur ajoutée** | Régularité = clé de l'apprentissage |
| **Endpoint à créer** | `GET /api/users/me/activity/heatmap` |

### 3.2 Streak et badges de régularité

| Élément | Description |
|---------|-------------|
| **Données sources** | Jours consécutifs avec au moins 1 tentative |
| **Type de graphique** | Compteur + historique |
| **Valeur ajoutée** | Gamification motivante |
| **Endpoint existant** | Partiellement dans `/api/users/me/stats` |

---

## 4. Graphiques Globaux (Admin/Dashboard)

### 4.1 Tendance globale du site

| Élément | Description |
|---------|-------------|
| **Données sources** | Agrégation de tous les utilisateurs |
| **Type de graphique** | Taux de réussite moyen par cohorte/mois |
| **Valeur ajoutée** | Valide l'efficacité pédagogique globale du site |
| **Endpoint à créer** | `GET /api/admin/analytics/trends` |

### 4.2 Comparaison exercices AI vs manuels

| Élément | Description |
|---------|-------------|
| **Données sources** | `Exercise.ai_generated` + taux de réussite associé |
| **Type de graphique** | Barres comparatives |
| **Valeur ajoutée** | Mesurer la qualité des exercices générés par IA |
| **Endpoint existant** | Données partiellement dans `/api/exercises/stats` |

---

## 5. Données supplémentaires à collecter (optionnel)

| Donnée | Table/Champ suggéré | Utilité |
|--------|---------------------|---------|
| Score initial (test diagnostic) | `users.initial_assessment_score` | Comparaison avant/après |
| Objectifs utilisateur | `user_goals` (nouvelle table) | Mesurer atteinte des objectifs personnalisés |
| Sessions (début/fin) | `user_sessions` (nouvelle table) | Durée d'attention, engagement par session |

---

## 6. Composants Frontend suggérés

| Composant | Librairie suggérée | Emplacement |
|-----------|-------------------|-------------|
| Ligne temporelle | Recharts ou Chart.js | Dashboard utilisateur |
| Radar chart | Recharts | Dashboard utilisateur |
| Heatmap calendrier | react-calendar-heatmap | Dashboard ou profil |
| Barres empilées | Recharts | Dashboard / Admin |

---

## 7. Priorisation suggérée

### Phase 1 - Quick wins (données déjà disponibles)
1. Radar chart par discipline (données dans `/api/exercises/stats`)
2. Distribution par niveau de difficulté (données dans `/api/exercises/stats`)

### Phase 2 - Endpoints à créer
3. Courbe d'évolution temporelle (nécessite agrégation par date)
4. Heatmap d'activité

### Phase 3 - Nouvelles données
5. Score initial / test diagnostic
6. Comparaison AI vs manuel avec détails

---

## Références

- **Endpoint stats existant** : `server/handlers/exercise_handlers.py::get_exercises_stats`
- **Hook frontend** : `frontend/hooks/useAcademyStats.ts`
- **Widget existant** : `frontend/components/home/AcademyStatsWidget.tsx`
