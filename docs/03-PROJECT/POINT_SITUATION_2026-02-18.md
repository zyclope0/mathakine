# Point de situation — Projet Mathakine

> **Date** : 18 février 2026  
> **Type** : Bilan trimestriel / situation actuelle  
> **Référence** : [SITUATION_FEATURES](../02-FEATURES/SITUATION_FEATURES.md), [EVALUATION_PROJET_2026-02-07](EVALUATION_PROJET_2026-02-07.md)

---

## 1. Vue d'ensemble

**Mathakine** est une plateforme éducative mathématique gamifiée pour enfants (5–20 ans) et parents. Cible : apprentissage adaptatif, rétention, engagement quotidien.

| Indicateur | Valeur |
|------------|--------|
| **Statut** | Production, MVP+ fonctionnel |
| **Version** | 2.1.0 |
| **Stack** | Next.js 16 + Starlette + PostgreSQL + OpenAI |
| **Score qualité** (07/02) | 5.0/10 — MVP+ fonctionnel, pas industrialisé |

---

## 2. Fonctionnalités livrées (récent)

### 2.1 Badges — Finalisation complète (18/02)

| Lot | Description | Statut |
|-----|-------------|--------|
| **A** Refonte UX | Ma collection, en cours, à débloquer. Filtres, tri, rareté, épingler (max 3) | ✅ |
| **B** Admin CRUD | Endpoints + page admin, formulaire création/édition, reformulation B4 | ✅ |
| **C** Moteur générique | `badge_requirement_engine.py`, 10+ types, défis logiques, mixte | ✅ |
| **Paufinage** | Fix N+1 `/api/challenges/badges/progress`, filtre « Proches » onglet À débloquer | ✅ |

- **~32 badges** (progression, maîtrise, régularité, performance, découverte, spéciaux)  
- **4 badges secrets**, principes psychologiques (goal-gradient, endowment, scarcity, social proof, loss aversion)

### 2.2 Gamification

| Élément | État |
|---------|------|
| Streak (série d'entraînement) | ✅ current_streak, best_streak, last_activity_date |
| Leaderboard | ✅ Top 50 global |
| Recommandations + marquer fait | ✅ |
| Notification « Tu approches » | ✅ (badge proche >50 %) |

### 2.3 Auth, utilisateur, plateforme

| Élément | État |
|---------|------|
| Inscription, vérification email, login, refresh token | ✅ |
| Forgot / Reset password | ✅ |
| Sessions actives (liste, révocation) | ✅ |
| Mode maintenance | ✅ Overlay + routes exemptées |
| Inscriptions (on/off) | ✅ `registration_enabled` |
| Paramètres admin (config) | ✅ GET/PUT `/api/admin/config` |

### 2.4 Admin

| Fonctionnalité | État |
|----------------|------|
| Overview, Users, Content | ✅ |
| Exercices, Défis, Badges (CRUD) | ✅ |
| Modération IA, audit log | ✅ |
| Config (maintenance, inscriptions) | ✅ |
| Export CSV | ✅ |

---

## 3. Pages et parcours utilisateur

| Page | Route | État |
|------|-------|------|
| Accueil | `/` | ✅ |
| Dashboard | `/dashboard` | ✅ 4 onglets, widgets progression |
| Classement | `/leaderboard` | ✅ |
| Exercices | `/exercises` | ✅ |
| Défis logiques | `/challenges` | ✅ |
| Badges | `/badges` | ✅ Refonte complète |
| Profil | `/profile` | ✅ |
| Paramètres | `/settings` | ✅ |
| Admin | `/admin/*` | ✅ |

---

## 4. Points forts

- **UX / accessibilité** : 7/10 — thèmes, animations adaptatives, WCAG 2.1 AA
- **Gamification** : badges, streak, leaderboard, recommandations opérationnels
- **Architecture** : séparation handlers / services / models, ~80 routes API
- **i18n** : Français / Anglais (next-intl)
- **Moteur badges** : générique, extensible, défis logiques supportés

---

## 5. Points d’attention

| Domaine | Score (07/02) | Constat |
|---------|---------------|---------|
| **Tests** | 3.5/10 | Risque critique — couverture <20 % backend, <5 % frontend |
| **Performance** | 4.5/10 | Monitoring inexistant (Sentry partiel) |
| **Documentation technique** | 4/10 | README_TECH à jour, manque docs inline |
| **Handlers longs** | ✅ Partiel | `generate_ai_challenge_stream` extrait dans `challenge_ai_service.py` (handler ~60 lignes) |

---

## 6. Priorités suggérées (P1)

| Tâche | Effort | Impact |
|-------|--------|--------|
| Défis quotidiens (3/jour) | Moyen | Rétention |
| Fixture défis tests | Faible | CI fiable |
| Leaderboard ligues | Moyen | Engagement |
| Renforcer couverture tests | Élevé | Qualité, régression |

---

## 7. Prochaines étapes possibles (P2–P3)

- Test de diagnostic initial, parcours adaptatif
- Révisions espacées (SM-2)
- Objectifs personnalisés (quotidien, hebdo)
- Notifications push / email
- Dashboard parent

---

## 8. Références rapides

| Besoin | Document |
|--------|----------|
| Installation | [GETTING_STARTED](../00-REFERENCE/GETTING_STARTED.md) |
| API (endpoints) | [API_QUICK_REFERENCE](../02-FEATURES/API_QUICK_REFERENCE.md) |
| Fonctionnalités détaillées | [SITUATION_FEATURES](../02-FEATURES/SITUATION_FEATURES.md) |
| Roadmap produit | [ROADMAP_FONCTIONNALITES](../02-FEATURES/ROADMAP_FONCTIONNALITES.md) |
| Évaluation qualité | [EVALUATION_PROJET_2026-02-07](EVALUATION_PROJET_2026-02-07.md) |
| Badges (plan, moteur) | [PLAN_REFONTE_BADGES](../02-FEATURES/PLAN_REFONTE_BADGES.md) |

---

*Document généré le 18/02/2026 — Mise à jour manuelle recommandée après chaque livrable majeur.*
