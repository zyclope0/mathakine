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

## 6.1 État d'avancement (implémenté)

| Itération | Contenu | Statut |
|-----------|---------|--------|
| **1** | `require_role`, `require_admin`, RBAC dans `server/auth.py` | ✅ |
| **2** | Route `GET /api/admin/health` | ✅ |
| **3** | `GET /api/admin/overview` + KPIs (users, exercises, challenges, attempts) | ✅ |
| **4** | Page `/admin`, layout sidebar, lien Admin dans menu utilisateur | ✅ |
| **5** | `GET /api/admin/users`, `PATCH /api/admin/users/{id}`, page `/admin/users` | ✅ |
| **6** | `GET/PATCH /api/admin/exercises`, `GET/PATCH /api/admin/challenges`, page `/admin/content` | ✅ |
| **7** | Export CSV — `GET /api/admin/export`, bloc téléchargement sur `/admin` | ✅ |
| **8** | Rapports par période — `GET /api/admin/reports?period=7d|30d`, bloc Rapports sur `/admin` | ✅ |
| **9** | Utilisateurs avancés — modification rôle, envoi emails forcés (reset MDP, vérification), etc. | ✅ |
| **10** | Édition contenu — clic exercice/défi → édition ergonomique in-place ou modal | ✅ |
| **11** | Création contenu — formulaire ergonomique pour créer exercice ou défi | ✅ |
| **12** | Modération IA — liste exercices/défis générés IA | ✅ |
| **13** | Audit trail — log des actions admin (qui a fait quoi, quand) | ✅ |

### Détail itération 5 — Page Utilisateurs

- **Tableau** : pseudo, email, nom, rôle, statut (actif/inactif), date inscription
- **Filtres** : recherche (pseudo, email, nom), rôle (Padawan, Maître, Gardien, Archiviste), statut (Tous, Actifs, Inactifs)
- **Pagination** : 20 par page, navigation précédent/suivant
- **Actions** : Désactiver / Activer (un admin ne peut pas se désactiver lui-même)
- **Carte Utilisateurs** sur `/admin` cliquable → redirige vers `/admin/users`

### Détail itération 6 — Page Contenu

- **Onglets** : Exercices | Défis logiques
- **Tableau exercices** : titre, type, difficulté, âge, tentatives, taux succès, statut (actif/archivé), action Archiver/Réactiver
- **Tableau défis** : titre, type, âge, tentatives, taux succès, statut, action Archiver/Réactiver
- **Filtres** : type, statut (Tous, Actifs, Archivés)
- **Pagination** : 20 par page
- **Cartes Exercices et Défis** sur `/admin` cliquables → `/admin/content`

### Détail itération 7 — Export CSV

- **Endpoint** : `GET /api/admin/export?type=&period=`
- **Types** : users, exercises, attempts, overview
- **Périodes** : all, 30d, 7d
- **Limite** : 10 000 lignes par export
- **UI** : Bloc Export CSV sur la page `/admin` (sélecteurs + bouton Télécharger)

### Détail itération 8 — Rapports par période

- **Endpoint** : `GET /api/admin/reports?period=7d|30d`
- **Données** : inscriptions (nouveaux users), utilisateurs actifs, tentatives (exercices + défis), taux de succès
- **UI** : Bloc Rapports par période sur `/admin` (sélecteur 7j/30j, cartes Inscriptions, Actifs, Tentatives, Taux succès)

### Détail itération 9 — Utilisateurs avancés

- **Modification du rôle** : `PATCH /api/admin/users/{id}` étendu avec `{ role: "padawan"|"maitre"|"gardien"|"archiviste" }` — l’admin peut promouvoir ou rétrograder un utilisateur (sauf se rétrograder lui-même)
- **Forcer envoi email changement de mot de passe** : bouton « Envoyer lien reset MDP » déclenchant `POST /api/auth/forgot-password` pour l’email du user (ou nouvel endpoint admin dédié)
- **Forcer envoi email vérification inscription** : bouton « Renvoyer email vérification » via endpoint existant ou admin
- **Autres** : réinitialiser mot de passe (admin définit un mot de passe temporaire + email), afficher date dernière connexion, débloquer compte si lockout futur
- **UI** : sur chaque ligne user, menu actions (⋮) avec : Modifier rôle, Envoyer reset MDP, Renvoyer vérification, etc.

### Détail itération 10 — Édition contenu

- **Clic sur exercice ou défi** : ouverture d’une vue/modal d’édition ergonomique
- **Champs éditables** : titre, type, difficulté, groupe d’âge, énoncé (question/consigne), réponses, corrigé, etc.
- **Endpoint** : `PUT /api/admin/exercises/{id}`, `PUT /api/admin/challenges/{id}` (ou extension de PATCH)
- **UI** : tableau avec ligne cliquable → panneau latéral ou modal plein écran ; preview en direct ; sauvegarde avec feedback
- **Ergonomie** : champs groupés, validation inline, annulation possible, pas de perte de données

### Détail itération 11 — Création contenu

- **Formulaire création exercice** : champs alignés sur le modèle (titre, type, difficulté, âge, énoncé, réponse attendue, etc.) — formulaire structuré et user-friendly
- **Formulaire création défi** : idem pour défis logiques (type, âge, consigne, grille/solution, etc.)
- **Endpoints** : `POST /api/admin/exercises`, `POST /api/admin/challenges`
- **UI** : bouton « Créer un exercice » / « Créer un défi » sur `/admin/content` ; formulaire en modal ou page dédiée `/admin/content/exercises/new`, `/admin/content/challenges/new`
- **Validation** : vérification des champs obligatoires, feedback immédiat, aide contextuelle

---

## 7. Références

- [ADMIN_FEATURE_SECURITE.md](ADMIN_FEATURE_SECURITE.md) — Exigences RBAC
- [ROADMAP_FONCTIONNALITES.md](ROADMAP_FONCTIONNALITES.md) — Contexte roadmap
- Modèle : `app/models/user.py` → `UserRole` (PADAWAN, MAITRE, GARDIEN, ARCHIVISTE)
- Auth : `server/auth.py`
