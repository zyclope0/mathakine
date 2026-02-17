# Point de situation — Fonctionnalités Mathakine

> **Date** : 16/02/2026  
> **Objectif** : État des lieux des fonctionnalités, ce qui est documenté, ce qui manque, et priorisation des implémentations

---

## Table des matières

1. [Inventaire docs 02-FEATURES](#1-inventaire-docs-02-features)
2. [Fonctionnalités récentes (16/02) — Nouvelles](#2-fonctionnalités-récentes-1602--nouvelles)
3. [État par domaine](#3-état-par-domaine)
4. [Priorité des implémentations](#4-priorité-des-implémentations)
5. [Références croisées](#5-références-croisées)

---

## 1. Inventaire docs 02-FEATURES

| Document | Contenu | Dernière MAJ | Couverture |
|----------|---------|--------------|------------|
| [API_QUICK_REFERENCE.md](API_QUICK_REFERENCE.md) | Cheat sheet endpoints API (Auth, Users, Admin, etc.) | 16/02 | ✅ Complète |
| [AUTH_FLOW.md](AUTH_FLOW.md) | Flux inscription → verify → login → reset password | 15/02 | ✅ Complète |
| [ADMIN_ESPACE_PROPOSITION.md](ADMIN_ESPACE_PROPOSITION.md) | Benchmark, périmètre admin, itérations | 15/02 | ✅ Complète |
| [ADMIN_FEATURE_SECURITE.md](ADMIN_FEATURE_SECURITE.md) | RBAC, require_admin, rôles | 15/02 | ✅ Complète |
| [THEMES.md](THEMES.md) | 7 thèmes visuels, themeStore | 15/02 | ✅ Complète |
| [I18N.md](I18N.md) | next-intl, messages, bonnes pratiques | Jan 2025 | ✅ Complète |
| [ROADMAP_FONCTIONNALITES.md](ROADMAP_FONCTIONNALITES.md) | Roadmap produit, P0-P4, phases | 15/02 | ✅ Complète |
| [BADGES_AMELIORATIONS.md](BADGES_AMELIORATIONS.md) | Améliorations page badges, psychologie | 06/02 | 🔄 MAJ 16/02 (progression implémentée) |
| [PLAN_REFONTE_BADGES.md](PLAN_REFONTE_BADGES.md) | Plan refonte badges + Admin CRUD + moteur | 16/02 | Nouveau |
| [ANALYTICS_PROGRESSION.md](ANALYTICS_PROGRESSION.md) | Graphiques progression (à implémenter) | 06/02 | Spécifications |

---

## 2. Fonctionnalités récentes (16/02) — Nouvelles

Les éléments suivants ont été implémentés et sont désormais documentés ici :

### 2.1 Mode maintenance et paramètres plateforme

| Élément | Implémentation | Doc dédiée |
|--------|----------------|------------|
| **maintenance_mode** | `app/utils/settings_reader.py`, `MaintenanceMiddleware` | — |
| **MaintenanceOverlay** | Overlay blocant sauf `/login`, `/admin` + lien « Accès admin » | — |
| **registration_enabled** | 403 sur `POST /api/users/` si `false` | — |
| **Paramètres admin** | `GET/PUT /api/admin/config` → table `settings` | [ADMIN_ESPACE_PROPOSITION](ADMIN_ESPACE_PROPOSITION.md) |

**Routes exemptées maintenance :** `/health`, `/metrics`, `/api/admin/*`, `/api/auth/login`, `/api/auth/refresh`, `/api/auth/validate-token`, `/api/auth/csrf`

### 2.2 Sessions actives

| Élément | Implémentation | Page |
|--------|----------------|------|
| **UserSession à chaque login** | `server/handlers/auth_handlers.py` | — |
| **GET /api/users/me/sessions** | `is_current: true` sur session la plus récente | `/settings` |
| **Révocation session** | `DELETE /api/users/me/sessions/{id}` | `/settings` |

### 2.3 Badges — Progression (P0 de BADGES_AMELIORATIONS)

| Élément | Implémentation | Page |
|--------|----------------|------|
| **GET /api/challenges/badges/progress** | `{unlocked, in_progress}` avec barres de progression | `/badges` |
| **Section « Badges en cours »** | Hook `useBadgesProgress`, barres X/Y | `/badges` |

### 2.4 Recommandations — Marquer comme fait

| Élément | Implémentation | Page |
|--------|----------------|------|
| **POST /api/recommendations/complete** | Met à jour `is_completed`, `completed_at` | Dashboard (onglet Recommandations) |
| **Bouton ✓ Marquer comme fait** | Chaque carte recommandation | Dashboard |

---

## 3. État par domaine

### Auth & Utilisateur
| Fonctionnalité | Backend | Frontend | Doc |
|----------------|---------|----------|-----|
| Inscription | ✅ | ✅ | AUTH_FLOW |
| Vérification email | ✅ | ✅ | AUTH_FLOW |
| Login / Logout | ✅ | ✅ | AUTH_FLOW |
| Refresh token | ✅ | ✅ | AUTH_FLOW |
| Forgot / Reset password | ✅ | ✅ | AUTH_FLOW |
| Sessions actives | ✅ | ✅ | SITUATION (ici) |
| Profil (PUT /me) | ✅ | ✅ | ENDPOINTS_NON_INTEGRES |
| Changement mot de passe | ✅ | ✅ | ENDPOINTS_NON_INTEGRES |

### Gamification
| Fonctionnalité | Backend | Frontend | Doc |
|----------------|---------|----------|-----|
| Leaderboard | ✅ | ✅ | ROADMAP, ENDPOINTS |
| Badges (liste, check) | ✅ | ✅ | BADGES_AMELIORATIONS |
| **Badges — progression** | ✅ | ✅ | SITUATION (ici), BADGES_AMELIORATIONS |
| Recommandations | ✅ | ✅ | — |
| **Recommandations — marquer fait** | ✅ | ✅ | SITUATION (ici) |
| Streak | ✅ | ✅ | — |

### Admin
| Fonctionnalité | Backend | Frontend | Doc |
|----------------|---------|----------|-----|
| Overview, Users, Content | ✅ | ✅ | ADMIN_ESPACE_PROPOSITION |
| Modération IA, Audit log | ✅ | ✅ | ADMIN_ESPACE_PROPOSITION |
| Config (maintenance, inscriptions) | ✅ | ✅ | ADMIN_ESPACE_PROPOSITION |
| Export CSV | ✅ | ✅ | API_QUICK_REFERENCE |

### Plateforme
| Fonctionnalité | Backend | Frontend | Doc |
|----------------|---------|----------|-----|
| Mode maintenance | ✅ | ✅ (overlay) | SITUATION (ici) |
| Inscriptions (on/off) | ✅ | — | SITUATION (ici) |

---

## 4. Priorité des implémentations

### P0 — Critique / Quick wins (fait 16/02)
- [x] maintenance_mode + registration_enabled
- [x] handle_recommendation_complete
- [x] get_user_badges_progress
- [x] is_current (sessions)
- [x] UserSession à chaque login

### P1 — Haute priorité (roadmap engagement)

| Tâche | Effort | Source | Notes |
|-------|--------|--------|-------|
| **Système de streak** | Faible | ROADMAP 3.4 | Existe partiellement — à renforcer |
| **Défis quotidiens** (3/jour) | Moyen | ROADMAP 3.2 | Nouveau modèle + UI |
| **Fixture défis tests** | Faible | Tests | 8 tests skippés « No challenges » |
| **Leaderboard ligues** | Moyen | ROADMAP 3.4 | Actuellement top 50 global |

### P2 — Moyenne priorité

| Tâche | Effort | Source | Notes |
|-------|--------|--------|-------|
| **Test de diagnostic** | Moyen | ROADMAP 3.5 | Niveau initial, parcours adaptatif |
| **Révisions espacées** | Moyen | ROADMAP 3.3 | Algorithme SM-2, table dédiée |
| **Conditions badges visibles** | Faible | BADGES_AMELIORATIONS | « Plus que X exercices pour Y » |
| **Objectifs personnalisés** | Faible | ROADMAP 4.2 | Quotidien, hebdo, mensuel |
| **Notifications** | Moyen | ROADMAP 4.1 | Push, email rappel |

### P3 — Basse priorité

| Tâche | Effort | Source | Notes |
|-------|--------|--------|-------|
| **Dashboard parent** | Moyen | ROADMAP 3.1 | parent_child_links, vue enfant |
| **delete_user (admin)** | Faible | PLACEHOLDERS | RGPD, soft/hard delete |
| **Mode classe/enseignant** | Élevé | ROADMAP 4.4 | — |
| **Tuteur IA contextuel** | Élevé | ROADMAP 5.1 | — |

### À supprimer / Ne pas implémenter
- `start_challenge` — Non nécessaire
- `get_challenge_progress` — Redondant
- `get_challenge_rewards` — Système non défini
- `get_user_progress_by_exercise_type` — Redondant avec /me/progress

---

## 5. Références croisées

| Besoin | Document |
|--------|----------|
| Liste endpoints API | [API_QUICK_REFERENCE](API_QUICK_REFERENCE.md) |
| Placeholders / TODOs techniques | [PLACEHOLDERS_ET_TODO](../03-PROJECT/PLACEHOLDERS_ET_TODO.md) |
| Intégration frontend | [ENDPOINTS_NON_INTEGRES](../03-PROJECT/ENDPOINTS_NON_INTEGRES.md) |
| Roadmap produit | [ROADMAP_FONCTIONNALITES](ROADMAP_FONCTIONNALITES.md) |
| Admin (benchmark, périmètre) | [ADMIN_ESPACE_PROPOSITION](ADMIN_ESPACE_PROPOSITION.md) |
| Admin (sécurité RBAC) | [ADMIN_FEATURE_SECURITE](ADMIN_FEATURE_SECURITE.md) |
| Flux auth complet | [AUTH_FLOW](AUTH_FLOW.md) |
| Badges (améliorations) | [BADGES_AMELIORATIONS](BADGES_AMELIORATIONS.md) |
| Graphiques progression | [ANALYTICS_PROGRESSION](ANALYTICS_PROGRESSION.md) |
| Thèmes visuels | [THEMES](THEMES.md) |
| i18n | [I18N](I18N.md) |
