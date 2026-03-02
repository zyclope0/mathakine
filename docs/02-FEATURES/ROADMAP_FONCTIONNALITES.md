# Roadmap Fonctionnalités - Analyse Globale

> **Date** : 06/02/2026 — **Dernière MAJ** : 26/02/2026  
> **Objectif** : Identifier les pages et fonctionnalités à ajouter pour maximiser l'engagement et la rétention  
> **Cible** : Enfants 5-20 ans + Parents

---

## Table des matières

1. [État actuel du projet](#1-état-actuel-du-projet)
2. [Analyse des manques critiques](#2-analyse-des-manques-critiques)
3. [Fonctionnalités prioritaires](#3-fonctionnalités-prioritaires)
4. [Fonctionnalités secondaires](#4-fonctionnalités-secondaires)
5. [Fonctionnalités innovantes](#5-fonctionnalités-innovantes)
6. [Matrice de priorisation](#6-matrice-de-priorisation)
7. [Roadmap suggérée](#7-roadmap-suggérée)

---

## ℹ️ Admin — Implémenté (16/02/2026)

L'espace admin est opérationnel (rôle `archiviste`). Voir [ADMIN_ESPACE_PROPOSITION.md](ADMIN_ESPACE_PROPOSITION.md) et [ADMIN_FEATURE_SECURITE.md](ADMIN_FEATURE_SECURITE.md).

## ℹ️ Monitoring IA Admin — Implémenté (22/02/2026)

Page `/admin/ai-monitoring` opérationnelle :
- KPIs tokens OpenAI (total, coût estimé, moyenne par génération)
- Qualité des générations (taux de succès, échecs validation, auto-corrections, durée)
- Breakdown par type de défi et par modèle IA (o3, o3-mini, gpt-4o-mini…)
- Sélecteur de période (1j / 7j / 30j)
- Endpoints : `GET /api/admin/ai-stats` et `GET /api/admin/generation-metrics`

**Limitation actuelle** : données **in-memory** — perdues à chaque redémarrage serveur.
**Évolution prévue** : persistance DB (voir section 4.6 ci-dessous et `AUDIT_CODE_CLEANUP_2026-03-01.md § 8`).

---

## 1. État actuel du projet

### Pages existantes

| Page | Route | État | Évaluation |
|------|-------|------|------------|
| Accueil | `/` | ✅ Fonctionnel | Bon |
| Dashboard | `/dashboard` | ✅ Fonctionnel | Réorganisé (4 onglets, widget classement) |
| Classement | `/leaderboard` | ✅ Fonctionnel | Nouveau 15/02/2026 |
| Exercices | `/exercises` | ✅ Fonctionnel | Bon |
| Défis logiques | `/challenges` | ✅ Fonctionnel | Bon |
| Badges | `/badges` | ✅ Fonctionnel | À améliorer (voir BADGES_AMELIORATIONS.md) |
| Profil | `/profile` | ✅ Fonctionnel | Modification profil + mot de passe OK |
| Paramètres | `/settings` | ✅ Fonctionnel | Basique |
| Auth | `/login`, `/register` | ✅ Fonctionnel | OK |

### Endpoints implémentés (mise à jour 16/02/2026)

- ✅ `POST /api/auth/forgot-password` - Réinitialisation mot de passe
- ✅ `PUT /api/users/me` - Modification profil
- ✅ `PUT /api/users/me/password` - Changement mot de passe
- ✅ `GET /api/users/leaderboard` - Classement par total_points
- ✅ `GET /api/users/me/sessions` - Sessions actives (is_current, révocation)
- ✅ `GET /api/challenges/badges/progress` - Progression vers badges verrouillés
- ✅ `POST /api/recommendations/complete` - Marquer recommandation comme faite
- ✅ Mode maintenance + registration_enabled (admin config)

---

## 2. Analyse des manques critiques

### 2.1 Comparaison avec les leaders du marché

| Fonctionnalité | Duolingo | Khan Academy | DreamBox | **Mathakine** |
|----------------|----------|--------------|----------|---------------|
| Dashboard enfant | ✅ | ✅ | ✅ | ✅ |
| **Dashboard parent** | ✅ | ✅ | ✅ | ❌ |
| Streak/Série | ✅ | ❌ | ❌ | ✅ |
| **Leaderboard** | ✅ | ❌ | ❌ | ✅ |
| **Défis quotidiens** | ✅ | ✅ | ✅ | ❌ |
| **Révisions espacées** | ✅ | ✅ | ✅ | ❌ |
| **Test diagnostic** | ✅ | ✅ | ✅ | ❌ |
| Parcours adaptatif | ✅ | ✅ | ✅ | Partiel |
| **Objectifs personnalisés** | ✅ | ✅ | ✅ | ❌ |
| Rapports détaillés | ✅ | ✅ | ✅ | Basique |
| Mode hors-ligne | ✅ | ✅ | ❌ | Partiel (PWA) |
| Notifications push | ✅ | ✅ | ✅ | ❌ |

### 2.2 Manques identifiés par catégorie

**Engagement quotidien** (Impact rétention : TRÈS ÉLEVÉ)
- ❌ Défis quotidiens
- ❌ Système de streak
- ❌ Objectifs quotidiens/hebdomadaires

**Implication parentale** (Impact confiance : TRÈS ÉLEVÉ)
- ❌ Dashboard parent
- ❌ Rapports par email
- ❌ Contrôle parental (temps, contenu)

**Personnalisation** (Impact apprentissage : ÉLEVÉ)
- ❌ Test de diagnostic initial
- ❌ Parcours adaptatif intelligent
- ❌ Recommandations personnalisées

**Rétention long terme** (Impact fidélisation : ÉLEVÉ)
- ❌ Révisions espacées
- ❌ Notifications de rappel
- ❌ Récapitulatifs hebdomadaires

---

## 3. Fonctionnalités prioritaires

### 3.1 🔥 Dashboard Parent (P0)

**Pourquoi c'est critique** :
- 73% des parents veulent suivre la progression de leur enfant (source: Common Sense Media)
- DreamBox, Khan Academy, Mathletics ont tous un dashboard parent
- Différenciateur clé pour les décisions d'adoption

**Fonctionnalités du dashboard parent** :

| Fonctionnalité | Description | Priorité |
|----------------|-------------|----------|
| Vue d'ensemble | Temps passé, exercices complétés, progression | P0 |
| Progression par compétence | Graphique radar par type de math | P0 |
| Alertes | Notification si inactivité > 3 jours | P1 |
| Rapport hebdomadaire | Email automatique le dimanche | P1 |
| Objectifs | Définir des objectifs pour l'enfant | P2 |
| Contrôle temps | Limiter le temps d'utilisation quotidien | P2 |

**Architecture suggérée** :
```
/parent
  /dashboard      → Vue d'ensemble enfants
  /child/[id]     → Détail progression enfant
  /settings       → Alertes, contrôles parentaux
  /reports        → Historique des rapports
```

**Modèle de données** :
```
Table: parent_child_links
- parent_user_id (FK users)
- child_user_id (FK users)
- created_at
- permissions (JSON: {view_progress, set_goals, set_limits})
```

---

### 3.2 📅 Défis quotidiens (P0)

**Recherche** :
- Les défis quotidiens augmentent la rétention de **40%** (source: Gamification research)
- Attention : mal conçus, ils peuvent créer du FOMO et de l'obligation négative

**Conception recommandée** :

| Élément | Recommandation |
|---------|----------------|
| Nombre | 3 défis/jour (pas plus) |
| Difficulté | Adaptée au niveau de l'utilisateur |
| Récompense | Points bonus + progression vers badge |
| Expiration | Fin de journée (pas de pression multi-jours) |
| Optionnel | Jamais obligatoire, pas de punition si manqué |

**Types de défis** :
1. "Résous 5 exercices" (quantité)
2. "Obtiens 80% de réussite" (qualité)
3. "Essaie un nouveau type d'exercice" (exploration)
4. "Bats ton meilleur temps" (amélioration personnelle)

**UI suggérée** :
```
┌─────────────────────────────────────────┐
│ 🎯 Défis du jour           2/3 complétés│
├─────────────────────────────────────────┤
│ ✅ Résoudre 5 additions      +50 pts    │
│ ⏳ 80% de réussite (60%)     +75 pts    │
│ ⬜ Essayer une division      +100 pts   │
├─────────────────────────────────────────┤
│ Bonus tous défis : 🏆 +200 pts          │
└─────────────────────────────────────────┘
```

---

### 3.3 🔄 Système de révisions espacées (P0)

**Recherche** :
- Effet moyen d = 0.54 pour l'apprentissage espacé vs massé
- Particulièrement efficace pour les maths (g = 0.43)
- Améliore la rétention long terme de **200%+**

**Implémentation suggérée** :

**Algorithme SM-2 simplifié** :
```
Intervalles de révision :
- 1ère révision : 1 jour après
- 2ème révision : 3 jours
- 3ème révision : 7 jours
- 4ème révision : 14 jours
- 5ème révision : 30 jours
- Ensuite : intervalles doublés

Ajustement selon performance :
- Correct sans hésitation : intervalle x 2.5
- Correct avec hésitation : intervalle x 1.5
- Incorrect : retour à 1 jour
```

**Modèle de données** :
```
Table: spaced_repetition_items
- user_id (FK users)
- exercise_id (FK exercises)
- ease_factor (float, default 2.5)
- interval_days (int)
- next_review_date (date)
- repetition_count (int)
- last_quality (0-5)
```

**UI suggérée** :
```
┌─────────────────────────────────────────┐
│ 📚 Révisions du jour                    │
├─────────────────────────────────────────┤
│ 🔴 3 exercices à revoir (en retard)     │
│ 🟡 5 exercices prévus aujourd'hui       │
│ 🟢 12 exercices maîtrisés               │
├─────────────────────────────────────────┤
│ [Commencer les révisions]               │
└─────────────────────────────────────────┘
```

---

### 3.4 🏆 Leaderboard / Classement (P1)

**Recherche** :
- +40% de leçons/semaine chez Duolingo avec les ligues
- Les classements **relatifs** (vs 10 personnes proches) sont plus efficaces que globaux
- Risque : démotivation des moins performants

**Conception recommandée** :

| Type | Description | Cible |
|------|-------------|-------|
| **Ligue hebdomadaire** | Groupes de 30 personnes, reset chaque lundi | Tous |
| **Classement amis** | Entre amis ajoutés | Social |
| **Top école/classe** | Si intégration scolaire | Écoles |
| **Record personnel** | Comparaison avec soi-même | Non-compétitifs |

**Paramètre utilisateur** :
```
☐ Participer aux classements (opt-in, pas opt-out)
```

**Système de ligues** :
```
Ligue Bronze → Argent → Or → Diamant → Maître
- Top 10 : Promotion
- Bottom 5 : Relégation
- Reset chaque lundi
```

---

### 3.5 🧪 Test de diagnostic initial (P1)

**Pourquoi c'est important** :
- Permet de personnaliser le parcours dès le départ
- Évite la frustration (exercices trop faciles ou difficiles)
- Donne une baseline pour mesurer la progression

**Conception** :

| Phase | Contenu | Durée |
|-------|---------|-------|
| Niveau | 5 questions adaptatives | 3 min |
| Points faibles | 10 questions par domaine | 5-10 min |
| Style | Préférences d'apprentissage (optionnel) | 2 min |

**Algorithme adaptatif** :
- Commencer au niveau moyen
- Si correct : question plus difficile
- Si incorrect : question plus facile
- Arrêter après 2 erreurs consécutives par niveau

**Résultat** :
```
┌─────────────────────────────────────────┐
│ 🎓 Ton profil d'apprentissage           │
├─────────────────────────────────────────┤
│ Niveau global : Padawan (intermédiaire) │
│                                         │
│ Points forts :                          │
│ ████████████ Addition (95%)             │
│ ██████████░░ Multiplication (80%)       │
│                                         │
│ À travailler :                          │
│ ██████░░░░░░ Division (55%)             │
│ ████░░░░░░░░ Fractions (35%)            │
│                                         │
│ [Commencer mon parcours personnalisé]   │
└─────────────────────────────────────────┘
```

---

## 4. Fonctionnalités secondaires

### 4.1 📧 Notifications et rappels (P2)

| Type | Canal | Fréquence |
|------|-------|-----------|
| Rappel inactivité | Push + Email | Après 2 jours |
| Streak en danger | Push | 20h si pas d'activité |
| Badge proche | Push | Quand à 90% |
| Rapport hebdo (parent) | Email | Dimanche 18h |
| Nouveau contenu | Push | Max 1x/semaine |

**Paramètres utilisateur** :
```
Notifications :
☑ Rappels d'entraînement
☑ Alertes de streak
☑ Nouveaux badges
☐ Nouveaux défis disponibles
☐ Classement hebdomadaire
```

---

### 4.2 🎯 Objectifs personnalisés (P2)

**Types d'objectifs** :
- Quotidien : "5 exercices/jour"
- Hebdomadaire : "30 exercices/semaine"
- Mensuel : "Maîtriser les fractions"
- Long terme : "Atteindre le niveau Maître"

**UI** :
```
┌─────────────────────────────────────────┐
│ 🎯 Mes objectifs                        │
├─────────────────────────────────────────┤
│ Aujourd'hui : 3/5 exercices ██████░░░░  │
│ Cette semaine : 18/30      ██████████░░ │
│ Objectif fractions : 60%   ████████░░░░ │
└─────────────────────────────────────────┘
```

---

### 4.3 📊 Rapports détaillés (P2)

**Page /reports ou /progress**

| Section | Contenu |
|---------|---------|
| Vue d'ensemble | Graphique progression globale |
| Par compétence | Radar chart + évolution temporelle |
| Comparaison | Vs soi-même il y a 1 mois |
| Temps | Heures passées, meilleurs jours |
| Erreurs fréquentes | Patterns d'erreurs à corriger |

---

### 4.4 🏠 Préférence page d'accueil après connexion (P2)

**Objectif** : Permettre à l'utilisateur de choisir où il est redirigé après login.

| Valeur | Redirection |
|--------|-------------|
| `exercises` (défaut) | `/exercises` |
| `dashboard` | `/dashboard` |

**Implémentation** :
- Champ `login_redirect_preference` (ou équivalent) en base (modèle `User` ou `accessibility_settings`)
- Option dans la page Profil / Paramètres : « Page d'accueil après connexion » [Exercices | Tableau de bord]
- Réponse `GET /api/users/me` et `PUT /api/users/me` incluent ce champ
- `useAuth.ts` : après onboarding OK, utiliser `data.user.login_redirect_preference` pour la cible

**Effort estimé** : Faible (1 colonne, 1 champ formulaire, 1 branche dans useAuth).

---

### 4.6 🤖 Monitoring IA — Persistance historique (P2)

**Contexte** : `token_tracker` et `generation_metrics` sont en mémoire. Un redémarrage Render efface tout. La page `/admin/ai-monitoring` est souvent à zéro en prod.

**Objectif** : Persister chaque génération en DB pour des stats fiables sur 7/30/90 jours.

**Valeur** :
- Suivre les coûts OpenAI réels sur la durée (budgétisation)
- Détecter les dérives de qualité IA (hausse des échecs de validation)
- Identifier les types de défis les plus coûteux / lents

**Effort estimé** : ~1 jour — complexité moyenne, faible risque.

**Ce qu'il faut faire** :

| # | Action |
|---|--------|
| 1 | 2 nouveaux modèles SQLAlchemy : `AiTokenUsage`, `AiGenerationMetric` |
| 2 | 1 migration Alembic (pattern identique à `edtech_events`) |
| 3 | `token_tracker.track_usage()` → INSERT en DB |
| 4 | `generation_metrics.record_generation()` → INSERT en DB |
| 5 | `get_stats()` / `get_summary()` → requêtes SQL avec filtre `created_at` |
| 6 | Passer la session DB depuis `challenge_ai_service.py` (point délicat) |
| 7 | Mise à jour tests admin |

**Pattern de référence** : `edtech_events` (table JSONB + migration + handler admin).
**Doc technique** : `docs/03-PROJECT/AUDIT_CODE_CLEANUP_2026-03-01.md § 8`.

---

### 4.5 🏫 Mode classe/école (P3)

**Pour les enseignants** :
- Créer une classe
- Inviter des élèves
- Assigner des exercices
- Voir la progression collective
- Exporter des rapports

**Architecture** :
```
/teacher
  /dashboard      → Vue classes
  /class/[id]     → Détail classe
  /assignments    → Devoirs assignés
  /reports        → Rapports exportables
```

---

## 5. Fonctionnalités innovantes

### 5.1 🤖 Tuteur IA contextuel (P3)

**Concept** : Un chatbot qui aide quand l'enfant est bloqué

| Trigger | Action |
|---------|--------|
| 3 erreurs consécutives | Proposer de l'aide |
| Temps > 2x moyenne | Suggérer un indice |
| Demande explicite | Expliquer pas à pas |

**Différenciateur** vs chatbot actuel :
- Contextuel (sait quel exercice est en cours)
- Pédagogique (ne donne pas la réponse, guide)
- Adapté à l'âge

---

### 5.2 🎮 Mode aventure/histoire (P3)

**Concept** : Progression narrative où les maths servent l'histoire

**Exemple** :
> "Le vaisseau spatial a besoin de 150 unités de carburant. Tu as 3 réservoirs de 45 unités chacun. Combien manque-t-il ?"

**Avantages** :
- Contextualise les maths
- Engagement narratif
- Récompenses débloquent la suite de l'histoire

---

### 5.3 🎨 Personnalisation avatar/profil (P3)

**Éléments à débloquer avec les points** :
- Avatars
- Thèmes de couleur
- Titres ("Maître des fractions")
- Cadres de profil

**Impact** : Donne de la valeur aux points gagnés

---

## 6. Matrice de priorisation

| Fonctionnalité | Impact rétention | Effort dev | Priorité |
|----------------|------------------|------------|----------|
| Dashboard parent | ⭐⭐⭐⭐⭐ | Moyen | **P0** |
| Défis quotidiens | ⭐⭐⭐⭐⭐ | Faible | **P0** |
| Révisions espacées | ⭐⭐⭐⭐⭐ | Moyen | **P0** |
| Leaderboard | ⭐⭐⭐⭐ | Faible | **P1** |
| Test diagnostic | ⭐⭐⭐⭐ | Moyen | **P1** |
| Système streak | ⭐⭐⭐⭐⭐ | Faible | **P1** |
| Notifications | ⭐⭐⭐ | Moyen | **P2** |
| Objectifs perso | ⭐⭐⭐ | Faible | **P2** |
| Préférence page d'accueil (profil) | ⭐⭐ | Faible | **P2** |
| Rapports détaillés | ⭐⭐⭐ | Moyen | **P2** |
| Monitoring IA — persistance DB | ⭐⭐ | Faible | **P2** |
| Mode classe | ⭐⭐⭐ | Élevé | **P3** |
| Tuteur IA | ⭐⭐⭐⭐ | Élevé | **P3** |
| Mode aventure | ⭐⭐⭐ | Très élevé | **P4** |
| Personnalisation avatar | ⭐⭐ | Faible | **P4** |

---

## 7. Roadmap suggérée

### Phase 1 - Fondations engagement (2-3 sprints)

| Tâche | Complexité |
|-------|------------|
| Système de streak | Faible |
| Défis quotidiens (3/jour) | Moyenne |
| Améliorations badges (voir doc dédié) | Moyenne |
| Endpoint leaderboard | Faible |
| Page leaderboard | Faible |

### Phase 2 - Personnalisation (2-3 sprints)

| Tâche | Complexité |
|-------|------------|
| Test de diagnostic | Moyenne |
| Système de révisions espacées | Moyenne |
| Recommandations personnalisées | Moyenne |
| Objectifs utilisateur | Faible |
| Préférence page d'accueil après connexion (profil) | Faible |

### Phase 2b - Infrastructure IA (1 sprint)

| Tâche | Complexité |
|-------|------------|
| Monitoring IA — persistance DB (`AiTokenUsage`, `AiGenerationMetric`) | Moyenne |

### Phase 3 - Parents (2-3 sprints)

| Tâche | Complexité |
|-------|------------|
| Modèle parent-enfant | Moyenne |
| Dashboard parent | Moyenne |
| Rapports email | Moyenne |
| Contrôles parentaux | Moyenne |

### Phase 4 - Expansion (3+ sprints)

| Tâche | Complexité |
|-------|------------|
| Notifications push | Moyenne |
| Mode classe/enseignant | Élevée |
| Tuteur IA contextuel | Élevée |
| Mode aventure | Très élevée |

---

## Références

1. [Education Insights 2025-2026: Engagement Fuels Learning](https://www.discoveryeducation.com/education-insights/)
2. [DreamBox Parent Dashboard](https://www.dreambox.com/family/parent-dashboard)
3. [Khan Academy Parent Dashboard](https://support.khanacademy.org/hc/en-us/articles/360039664491)
4. [Meta-analysis: Spaced Repetition for Mathematics](https://link.springer.com/article/10.1007/s10648-025-10035-1)
5. [Daily Quests: Benefits and Pitfalls](https://dl.acm.org/doi/abs/10.1145/3549489)
6. [Gamification Mobile App Retention](https://www.arvisus.com/how-to-build-a-high-retention-mobile-app-ux-psychology-habits-gamification/)

---

## Documents liés

- [BADGES_AMELIORATIONS.md](BADGES_AMELIORATIONS.md) - Détail améliorations page badges
- [ANALYTICS_PROGRESSION.md](ANALYTICS_PROGRESSION.md) - Graphiques de progression
- [PLACEHOLDERS_ET_TODO.md](../03-PROJECT/PLACEHOLDERS_ET_TODO.md) - Endpoints à implémenter
