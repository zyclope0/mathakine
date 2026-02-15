# Proposition : Espace Admin Mathakine

> **Date** : 15/02/2026  
> **Objectif** : Définir un espace admin pour gérer les points clés, basé sur l'analyse des leaders du secteur et les best practices

---

## 1. Benchmark — Plateformes de référence

### 1.1 Comparatif fonctionnalités admin

| Fonctionnalité | Khan Academy | Prodigy | Mathletics | Duolingo for Schools | **Recommandation** |
|----------------|:------------:|:-------:|:----------:|:--------------------:|:------------------:|
| **Tableau de bord global** (KPIs plateforme) | ✅ | ✅ | ✅ | ✅ | **P0** |
| **Gestion utilisateurs** (liste, recherche, désactivation) | ✅ | ✅ | ✅ | ✅ | **P0** |
| **Statistiques d'usage** (inscriptions, activité, DAU/MAU) | ✅ | ✅ | ✅ | ✅ | **P0** |
| **Gestion contenu** (exercices, défis, modération) | ✅ | ✅ | ✅ | ✅ | **P0** |
| **Export données** (CSV, rapports) | ✅ | ✅ | ✅ | ✅ | **P0** |
| **Modération contenu IA** (signalement, validation) | ✅ | ✅ | - | ✅ | **P1** |
| **Promotion rôle** (user → modérateur, etc.) | ✅ | ✅ | ✅ | ✅ | **P0** |
| **Audit trail** (log des actions admin) | ✅ | - | ✅ | ✅ | **P1** |
| **Configuration plateforme** (paramètres globaux) | - | ✅ | ✅ | ✅ | **P2** |
| **Rapports par période** (hebdo, mensuel) | ✅ | ✅ | ✅ | ✅ | **P1** |

### 1.2 Synthèse des best practices

**Khan Academy**
- Teacher Dashboard : gestion classes, roster élèves, analytics apprentissage
- Administrateurs : rapports CSV, suivi usage institutionnel
- Modération : monitoring des interactions, suppression accès si abus

**Prodigy**
- Données temps réel dès que les élèves jouent
- Leaderboard classe, défis inter-classes
- Rapports : Assessment, Placement, Progress, Comprehension, Usage

**Mathletics**
- Teacher Console : gestion élèves, cours, devoirs, évaluations
- Admin : rapports admin, gestion roster école, rollover année

**Duolingo for Schools**
- Suivi progression classe
- Attribution devoirs
- Rapports engagement

**Points communs identifiés**
1. **RBAC obligatoire** — aucun endpoint admin sans vérification rôle
2. **Vue agrégée d'abord** — KPIs globaux avant le détail
3. **Export CSV** — pour rapports, conformité, analyse externe
4. **Actions réversibles** — désactivation plutôt que suppression définitive
5. **Logging** — traçabilité des actions sensibles (audit trail)

---

## 2. Proposition pour Mathakine

### 2.1 Périmètre par priorité

#### Phase 1 — MVP Admin (P0)

| Module | Description | Endpoints | Page frontend |
|--------|-------------|-----------|---------------|
| **Overview** | KPIs plateforme | `GET /api/admin/overview` | `/admin` |
| **Utilisateurs** | Liste, recherche, désactiver | `GET/PATCH /api/admin/users` | `/admin/users` |
| **Contenu** | Stats exercices/défis, archivage | `GET/PATCH /api/admin/exercises`, `/admin/challenges` | `/admin/content` |
| **Export** | CSV utilisateurs, exercices, tentatives | `GET /api/admin/export?type=users\|exercises\|attempts` | Intégré dans chaque module |

#### Phase 2 — Enrichissement (P1)

| Module | Description | Endpoints |
|--------|-------------|-----------|
| **Rapports** | Rapports par période (inscriptions, activité, taux succès) | `GET /api/admin/reports?period=7d\|30d` |
| **Modération IA** | Liste exercices/défis générés IA, signalement, validation | `GET /api/admin/moderation` |
| **Audit trail** | Log des actions admin (qui a fait quoi, quand) | `GET /api/admin/audit-log` |

#### Phase 3 — Avancé (P2)

| Module | Description |
|--------|-------------|
| **Configuration** | Paramètres globaux (limites, features flags) |
| **Badges** | Création/modification des définitions de badges |
| **Promotion rôle** | Interface pour promouvoir padawan → maitre, etc. |

---

## 3. Architecture proposée

### 3.1 Rôles (aligné avec `UserRole`)

| Rôle | Valeur DB | Accès admin |
|------|-----------|-------------|
| Padawan | `padawan` | Aucun |
| Maître | `maitre` | Aucun (réservé futur : créateur exercices) |
| Gardien | `gardien` | Modération, contenu (lecture + archivage) |
| **Archiviste** | `archiviste` | **Accès complet** (admin) |

**Note** : Le décorateur `require_role` utilisera `"archiviste"` pour l'accès admin complet. Alias possible : `require_admin` → vérifie `archiviste` ou `gardien` selon l'action.

### 3.2 Structure des routes

```
/admin                        → Redirection /admin/overview
/admin/overview               → KPIs (users, exercises, challenges, attempts)
/admin/users                  → Liste users, recherche, filtre rôle, désactivation
/admin/content                → Onglets Exercices | Défis (stats, archivage)
/admin/export                 → Sélecteur type + période → téléchargement CSV
/admin/audit-log              → (Phase 2) Log des actions
```

### 3.3 Endpoints API proposés (Phase 1)

```
GET  /api/admin/overview
     → { total_users, active_users_30d, total_exercises, total_challenges,
         attempts_today, attempts_7d, new_users_7d, avg_success_rate }

GET  /api/admin/users?search=&role=&is_active=&skip=&limit=
     → Liste paginée avec filtres (require archiviste)

PATCH /api/admin/users/{id}
     → { is_active: bool } — désactivation compte (require archiviste)

GET  /api/admin/exercises?archived=&type=&skip=&limit=
     → Liste exercices avec stats (nb tentatives, taux succès)

PATCH /api/admin/exercises/{id}
     → { is_archived: bool }

GET  /api/admin/challenges?archived=&type=&skip=&limit=
     → Liste défis avec stats

PATCH /api/admin/challenges/{id}
     → { is_archived: bool }

GET  /api/admin/export?type=users|exercises|attempts|overview&period=7d|30d
     → Streaming CSV ou JSON (require archiviste)
```

---

## 4. Sécurité (référence ADMIN_FEATURE_SECURITE.md)

1. **Décorateur `require_role("archiviste")`** — à implémenter dans `server/auth.py`
2. **Appliqué sur chaque handler** — jamais `@require_auth` seul pour `/api/admin/*`
3. **Rate limiting** — renforcé sur les routes admin (ex: 30 req/min)
4. **Audit trail** — log de chaque action (user_id, action, resource, timestamp)
5. **Pas de suppression définitive** — `is_active=false`, `is_archived=true`

---

## 5. UI/UX recommandations

| Élément | Recommandation |
|---------|----------------|
| **Accès** | Lien `/admin` visible uniquement si `role === "archiviste"` |
| **Layout** | Sidebar avec modules (Overview, Users, Content, Export) |
| **Tables** | Pagination, tri, filtres (comme exercices existant) |
| **Confirmations** | Modal pour désactivation user, archivage contenu |
| **Feedback** | Toast succès/erreur sur chaque action |
| **Responsive** | Admin souvent sur desktop — priorité large screen |

---

## 6. Plan d'implémentation suggéré

| Étape | Description | Estimation |
|-------|-------------|------------|
| 1 | Implémenter `require_role` dans auth.py | 1h |
| 2 | `GET /api/admin/overview` + page Overview | 2–3h |
| 3 | `GET/PATCH /api/admin/users` + page Users | 3–4h |
| 4 | `GET/PATCH /api/admin/exercises` et challenges + page Content | 3–4h |
| 5 | `GET /api/admin/export` + boutons Export | 2h |
| 6 | Tests unitaires + E2E basique | 2h |

**Total Phase 1** : ~15–18h

---

## 7. Références

- [ADMIN_FEATURE_SECURITE.md](ADMIN_FEATURE_SECURITE.md) — Exigences RBAC
- [ROADMAP_FONCTIONNALITES.md](ROADMAP_FONCTIONNALITES.md) — Contexte roadmap
- Modèle : `app/models/user.py` → `UserRole` (PADAWAN, MAITRE, GARDIEN, ARCHIVISTE)
- Auth : `server/auth.py`
