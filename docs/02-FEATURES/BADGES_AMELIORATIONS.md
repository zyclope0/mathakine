# Améliorations Page Badges - Analyse et Priorisation

> **Date** : 06/02/2026 — **MAJ 17/02** : UX onglets + cartes compactes dépliables  
> **Statut** : Analyse complète — P0 progression ✅, UX Lot A ✅ (onglets, cartes dépliables)  
> **Cible** : Enfants 5-20 ans (dont TSA/TDAH)

---

## Table des matières

1. [Analyse du système actuel](#1-analyse-du-système-actuel)
2. [Fondements psychologiques](#2-fondements-psychologiques)
3. [Benchmarks : Duolingo & Khan Academy](#3-benchmarks--duolingo--khan-academy)
4. [Améliorations priorisées](#4-améliorations-priorisées)
5. [Spécifications détaillées](#5-spécifications-détaillées)
6. [Considérations accessibilité TSA/TDAH](#6-considérations-accessibilité-tsatdah)
7. [Plan d'implémentation](#7-plan-dimplémentation)

---

## 1. Analyse du système actuel

### Ce qui existe

| Composant | État | Évaluation |
|-----------|------|------------|
| Liste des badges | ✅ Fonctionnel | Affichage correct |
| États obtenu/verrouillé | ✅ Fonctionnel | Visuels distincts |
| Points de récompense | ✅ Fonctionnel | Affichés sur chaque badge |
| Catégories (progression, mastery, special) | ✅ Fonctionnel | Icônes distinctes |
| Difficultés (bronze, silver, gold) | ✅ Fonctionnel | Médailles visuelles |
| Stats utilisateur | ✅ Fonctionnel | Points, niveau, rang |
| Bouton "Vérifier badges" | ✅ Fonctionnel | Déclenchement manuel |
| Date d'obtention | ✅ Fonctionnel | Affichée pour badges obtenus |
| **Onglets En cours / À débloquer** | ✅ 17/02 | Ma collection en haut ; onglets uniquement pour ces deux sections |
| **Cartes obtenus compactes** | ✅ 17/02 | Titre + 1-2 infos (difficulté, pts, date) ; déplie au survol (desktop) ou toujours étendu (mobile) |

### Ce qui manque (critique)

| Élément manquant | Impact rétention | Priorité | État |
|------------------|------------------|----------|------|
| **Progression vers badges verrouillés** | Très élevé | P0 | ✅ Implémenté 16/02 (GET /api/challenges/badges/progress, barres X/Y) |
| **Conditions d'obtention visibles** | Élevé | P0 | À faire |
| **Déblocage automatique temps réel** | Élevé | P1 |
| **Notifications de progression** | Moyen | P1 |
| **Système de streak** | Très élevé | P1 |
| **Filtres et tri** | Moyen | P2 |
| **Célébrations visuelles** | Moyen | P2 |

---

## 2. Fondements psychologiques

### 2.1 Théorie de l'autodétermination (Deci & Ryan)

La motivation intrinsèque repose sur trois besoins fondamentaux :

| Besoin | Application badges | Implémentation suggérée |
|--------|-------------------|------------------------|
| **Compétence** | Sentiment de progression | Barres de progression, niveaux de maîtrise |
| **Autonomie** | Choix et contrôle | Filtres, objectifs personnalisés |
| **Appartenance** | Connexion sociale | Classements relatifs, partage |

**Recommandation** : Les badges doivent renforcer le sentiment de compétence, pas créer de pression externe.

### 2.2 Effet Goal-Gradient (Clark Hull, 1932)

> "La motivation et l'effort augmentent à mesure que l'on perçoit l'approche d'un objectif."

**Implications concrètes** :
- Les barres de progression augmentent l'engagement de **40-60%**
- La visualisation du progrès transforme l'arrêt en "abandon" plutôt qu'en choix neutre
- L'effet est amplifié quand le progrès initial est offert (ex: commencer à 10% plutôt que 0%)

**Application** : Afficher "Plus que 3 exercices pour débloquer X" plutôt que "5/8 exercices"

### 2.3 Aversion à la perte (Kahneman & Tversky)

> "Les humains sont 2x plus motivés par la peur de perdre que par l'espoir de gagner."

**Application Duolingo** : Le système de streak exploite cette psychologie
- Perdre un streak de 30 jours est perçu comme une "perte"
- Le "Streak Freeze" réduit le churn de **21%**

**Application Mathakine** : Implémenter un système de série d'entraînement

### 2.4 Récompenses variables (B.F. Skinner)

Les récompenses imprévisibles créent un engagement plus fort que les récompenses fixes.

**Application** :
- Badges "surprise" pour comportements non attendus
- Bonus aléatoires de points
- Défis quotidiens variés

### 2.5 Considérations développementales (enfants 5-20 ans)

| Tranche d'âge | Caractéristiques | Adaptation badges |
|---------------|------------------|-------------------|
| 5-8 ans | Gratification immédiate, visuel | Animations, sons, récompenses fréquentes |
| 9-12 ans | Collection, compétition | Badges à collectionner, mini-classements |
| 13-16 ans | Identité, social | Personnalisation, partage |
| 17-20 ans | Maîtrise, efficacité | Stats détaillées, optimisation |

---

## 3. Benchmarks : Duolingo & Khan Academy

### 3.1 Duolingo - Le maître de la rétention

**Métriques de succès** :
- 20+ millions d'utilisateurs actifs mensuels
- 80% des utilisateurs quittent les apps d'apprentissage en 1 semaine, Duolingo les retient
- Engagement augmenté de **60%** grâce à la gamification

**Éléments clés** :

| Élément | Mécanisme | Résultat |
|---------|-----------|----------|
| **Streak** | Jours consécutifs d'activité | 3.6x plus de rétention à 7 jours |
| **Streak Freeze** | Récupération d'un streak perdu | -21% de churn |
| **Widget iOS** | Affichage du streak sur l'écran d'accueil | +60% d'engagement |
| **Ligues XP** | Classements hebdomadaires | +40% de leçons/semaine |
| **Double XP Weekend** | Événements limités | +50% d'activité |
| **Skills dorées fissurées** | Visualisation de l'oubli | Encourage la révision |

### 3.2 Khan Academy - L'approche éducative

**Système de maîtrise à 4 niveaux** :
1. **Attempted** (0 points) - Essayé
2. **Familiar** (50 points) - Familier
3. **Proficient** (80 points) - Compétent
4. **Mastered** (100 points) - Maîtrisé

**Points forts** :
- Progression visible par compétence
- Challenges de maîtrise personnalisés (6 questions, 3 compétences)
- Possibilité de régresser (encourage la révision)
- Pourcentage de maîtrise par cours/unité

---

## 4. Améliorations priorisées

### P0 - Critique (Impact immédiat sur rétention)

#### 4.1 Barres de progression vers badges verrouillés ✅ Implémenté (16/02)

**Problème actuel** : Les badges verrouillés n'indiquent pas la progression
**Solution** : Afficher une barre de progression + texte "X/Y pour débloquer"

> **Implémenté** : `GET /api/challenges/badges/progress`, hook `useBadgesProgress`, section « Badges en cours » sur `/badges`

```
┌─────────────────────────────────────────┐
│ 🔒 Mathématicien en herbe               │
│ "Résoudre 50 exercices"                 │
│                                         │
│ ████████░░░░░░░░░░░░ 38/50 (76%)       │
│ Plus que 12 exercices !                 │
└─────────────────────────────────────────┘
```

**Impact attendu** : +30-40% d'engagement (basé sur études goal-gradient)

#### 4.2 Conditions d'obtention visibles

**Problème actuel** : L'utilisateur ne sait pas comment obtenir un badge
**Solution** : Afficher les critères sur chaque badge verrouillé

**Critères à afficher** :
- Nombre d'exercices/défis requis
- Taux de réussite minimum
- Type d'exercices spécifiques
- Streak requis

### P1 - Important (Amélioration significative)

#### 4.3 Système de streak (série d'entraînement)

**Inspiration** : Duolingo (3.6x rétention)

**Implémentation** :
- Compteur de jours consécutifs avec activité
- Icône flamme 🔥 dans le header
- Notification si streak en danger
- "Streak Freeze" (1 gratuit/semaine, achetables avec points)
- Badges liés aux streaks (7j, 30j, 100j, 365j)

**Données nécessaires** :
- Nouvelle table `user_streaks` ou champ dans `users`
- Tracking de la dernière activité quotidienne

#### 4.4 Déblocage automatique en temps réel

**Problème actuel** : L'utilisateur doit cliquer "Vérifier mes badges"
**Solution** : Vérification automatique après chaque exercice/défi

**Implémentation** :
- Appel API léger après chaque `POST /api/exercises/{id}/attempt`
- WebSocket ou polling pour notifications
- Animation de célébration au déblocage

#### 4.5 Notifications de progression

**Types de notifications** :
- "Tu approches du badge X ! (80%)"
- "Plus qu'un exercice pour débloquer Y !"
- "Félicitations ! Badge Z débloqué !"

**Canaux** :
- Toast in-app (priorité)
- Push notification (optionnel, configurable)

### P2 - Nice-to-have (Amélioration ergonomique)

#### 4.6 Filtres et tri

**Filtres suggérés** :
- Par statut : Tous / Obtenus / Verrouillés / Proches (>50%)
- Par catégorie : Progression / Maîtrise / Spécial
- Par difficulté : Bronze / Argent / Or

**Tri** :
- Par progression (proches d'abord)
- Par date d'obtention
- Par points de récompense

#### 4.7 Célébrations visuelles améliorées

**Au déblocage** :
- Animation confettis
- Son de célébration (désactivable)
- Modal de félicitations avec partage social

**Effet "wow"** pour badges rares :
- Animation dorée pour badges gold
- Effet de brillance amplifié

#### 4.8 Badges secrets

**Principe** : Badges cachés qui apparaissent seulement quand débloqués

**Exemples** :
- "Noctambule" : Exercice résolu après minuit
- "Perfectionniste" : 10 exercices d'affilée sans erreur
- "Explorateur" : Essayé tous les types d'exercices

**Impact** : Encourage l'exploration, effet de surprise

---

## 5. Spécifications détaillées

### 5.1 Structure de données pour progression

```typescript
interface BadgeProgress {
  badge_id: number;
  badge_code: string;
  current_value: number;      // Ex: 38
  target_value: number;       // Ex: 50
  progress_percent: number;   // Ex: 76
  criteria_description: string; // Ex: "Résoudre 50 exercices"
  is_earned: boolean;
  earned_at?: string;
}
```

### 5.2 Endpoint implémenté (16/02)

> **Implémenté** : `GET /api/challenges/badges/progress` (et non `/api/badges/progress`)

```
GET /api/challenges/badges/progress
Response: {
  badges_progress: BadgeProgress[],
  next_achievable: BadgeProgress[], // Badges les plus proches (<5 actions)
  streak: {
    current: number,
    best: number,
    streak_freeze_available: number
  }
}
```

### 5.3 Composant BadgeCard amélioré

```tsx
// Ajouts au BadgeCard existant
interface BadgeCardProps {
  badge: Badge;
  progress?: BadgeProgress; // NOUVEAU
  isEarned: boolean;
}

// Dans le rendu
{!isEarned && progress && (
  <div className="mt-3">
    <div className="text-xs text-muted-foreground mb-1">
      {progress.criteria_description}
    </div>
    <div className="w-full bg-muted rounded-full h-2">
      <div 
        className="bg-primary h-2 rounded-full transition-all"
        style={{ width: `${progress.progress_percent}%` }}
      />
    </div>
    <div className="text-xs mt-1 text-primary">
      {progress.current_value}/{progress.target_value} 
      ({progress.progress_percent}%)
    </div>
  </div>
)}
```

---

## 6. Considérations accessibilité TSA/TDAH

### 6.1 Principes pour TSA (Trouble du Spectre Autistique)

| Besoin | Implémentation |
|--------|----------------|
| Prévisibilité | Critères de badges explicites, pas de surprises négatives |
| Clarté visuelle | Contrastes forts, icônes cohérentes |
| Réduction surcharge | Option pour désactiver animations/sons |
| Routine | Encourager les streaks de manière positive (pas de culpabilisation) |

### 6.2 Principes pour TDAH

| Besoin | Implémentation |
|--------|----------------|
| Gratification immédiate | Micro-récompenses fréquentes, feedback instantané |
| Objectifs courts | Badges atteignables rapidement (pas que des badges "100 exercices") |
| Stimulation visuelle | Animations, couleurs vives (mais désactivables) |
| Rappels doux | Notifications non-intrusives, pas de pression |

### 6.3 Paramètres utilisateur suggérés

```
Préférences de gamification :
☑ Activer les animations de célébration
☑ Activer les sons
☐ Masquer les badges non obtenus
☑ Notifications de progression
☐ Mode compétition (classements)
```

---

## 7. Plan d'implémentation

### Phase 1 - Fondations (Sprint 1)

| Tâche | Complexité | Fichiers impactés |
|-------|------------|-------------------|
| Endpoint `/api/challenges/badges/progress` | Moyenne | `badge_handlers.py`, `badge_service.py` |
| Hook `useBadgeProgress` | Faible | Nouveau fichier |
| Barre de progression sur BadgeCard | Faible | `BadgeCard.tsx` |
| Critères d'obtention visibles | Faible | `BadgeCard.tsx`, traductions |

### Phase 2 - Streak System (Sprint 2)

| Tâche | Complexité | Fichiers impactés |
|-------|------------|-------------------|
| Table/champ streak en DB | Moyenne | Migration Alembic |
| Service de calcul streak | Moyenne | `badge_service.py` ou nouveau |
| Composant StreakDisplay | Faible | Nouveau composant |
| Intégration header | Faible | `Header.tsx` |
| Badges streak (7j, 30j, 100j) | Faible | Seed DB |

### Phase 3 - Temps réel (Sprint 3)

| Tâche | Complexité | Fichiers impactés |
|-------|------------|-------------------|
| Vérification auto après exercice | Faible | `exercise_handlers.py` |
| Toast de progression | Faible | Composant toast |
| Animation déblocage | Moyenne | `BadgeCard.tsx`, nouveau composant |

### Phase 4 - Polish (Sprint 4)

| Tâche | Complexité | Fichiers impactés |
|-------|------------|-------------------|
| Filtres et tri | Faible | `BadgesPage.tsx` |
| Badges secrets | Faible | Seed DB, `BadgeCard.tsx` |
| Paramètres utilisateur | Moyenne | Settings, context |
| Célébrations améliorées | Moyenne | Animations, sons |

---

## Métriques de succès

| Métrique | Baseline actuel | Objectif |
|----------|-----------------|----------|
| Temps sur page badges | À mesurer | +50% |
| Taux de retour J+7 | À mesurer | +30% |
| Badges débloqués/utilisateur | À mesurer | +40% |
| Exercices/jour (utilisateurs avec streak) | À mesurer | +25% |

---

## Références

1. [Gamification with Purpose: What Learners Prefer](https://arxiv.org/html/2512.08551v1)
2. [The Psychology of Gamification](https://badgeos.org/the-psychology-of-gamification-and-learning/)
3. [Duolingo's Gamification Secrets](https://www.orizon.co/blog/duolingos-gamification-secrets)
4. [Khan Academy Gamification Case Study](https://trophy.so/blog/khan-academy-gamification-case-study)
5. [Goal-Gradient Effect in UX](https://blog.logrocket.com/ux-design/goal-gradient-effect)
6. [Educational Gamification 2025 Research](https://link.springer.com/article/10.1007/s40692-025-00366-x)

---

## Fichiers liés

- `frontend/app/badges/page.tsx` - Page principale
- `frontend/components/badges/BadgeCard.tsx` - Composant carte
- `frontend/hooks/useBadges.ts` - Hook données
- `frontend/hooks/useBadgesProgress.ts` - Hook progression (nouveau 16/02)
- `server/handlers/badge_handlers.py` - Endpoints API
- `app/services/badge_service.py` - Service métier
- `app/services/badge_requirement_engine.py` - Moteur générique (Lot C-1, 17/02)

---

**Avancements 17/02** : B4 reformulation 17 badges, C-1 moteur générique (badges défis/mixte), terrain B5. **UX** : onglets En cours / À débloquer ; cartes obtenus compactes (dépliable au survol). [B4_REFORMULATION_BADGES](../03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/AUDITS_IMPLEMENTES/B4_REFORMULATION_BADGES.md), [PLAN_REFONTE_BADGES](../03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/AUDITS_IMPLEMENTES/PLAN_REFONTE_BADGES.md).

**Voir aussi** : [ROADMAP_FONCTIONNALITES.md](ROADMAP_FONCTIONNALITES.md). **[PLAN_REFONTE_BADGES.md](../03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/AUDITS_IMPLEMENTES/PLAN_REFONTE_BADGES.md)** — Plan refonte + Admin CRUD + moteur (backlog & priorités)..
