# Plan d'amélioration et refactoring — Page badges et gestion des achievements

> **Date** : 16/02/2026 — **MAJ** : Enrichi psychologie, Option 1, itérations  
> **Objectif** : Refonte page badges, admin CRUD, refactoring du moteur de badges  
> **Approche** : **Option 1** (UX d'abord), **petites itérations** pour réagir en cas de problème  
> **Sources** : [BADGES_AMELIORATIONS](BADGES_AMELIORATIONS.md), [ADMIN_ESPACE_PROPOSITION](ADMIN_ESPACE_PROPOSITION.md), études gamification 2024-2025, Cialdini, Kahneman & Tversky

---

## Table des matières

1. [État actuel et constats](#1-état-actuel-et-constats)
2. [Périmètre du plan](#2-périmètre-du-plan)
3. [Challenges psychologiques — Principes et études](#3-challenges-psychologiques--principes-et-études)
4. [Lot A — Refonte UX/UI page badges](#4-lot-a--refonte-uxui-page-badges)
5. [Lot B — Admin CRUD badges](#5-lot-b--admin-crud-badges)
6. [Lot C — Refactoring moteur badges](#6-lot-c--refactoring-moteur-badges)
7. [Matrice complexité / risque](#7-matrice-complexité--risque)
8. [Ordre d'exécution et itérations](#8-ordre-dexécution-et-itérations)
9. [Suivi d'avancement — À mettre à jour](#9-suivi-davancement--à-mettre-à-jour)

---

## 1. État actuel et constats

### Page badges (`/badges`)

| Élément | État | Problème potentiel |
|---------|------|--------------------|
| Layout | Stats en haut (4 cartes) + perf + badges en cours + grille | Chargée, hiérarchie peu lisible |
| Grille | `BadgeGrid` + `BadgeCard` | Pas de filtres, tri limité |
| Progression | Barres X/Y (16/02) | Implémenté mais `_get_badge_progress` ne gère que 2 types de requirements |
| Conditions | Absentes sur cartes | L'utilisateur ne sait pas comment débloquer |
| Bouton « Vérifier » | Obligatoire | Pas de déblocage temps réel |

### Modèle `Achievement` et logique

| Élément | État | Problème |
|---------|------|----------|
| Création badges | Probablement migrations / SQL | Pas d'interface admin |
| Suppression | Aucune | Risque FK `user_achievements` |
| Modification | Aucune | Changement = migration ou script |
| `BadgeService._check_badge_requirements` | ~15 `if badge.code == 'xxx'` | Fort couplage, difficile d'ajouter des badges |
| `_get_badge_progress` | 2 types (attempts_count, min_attempts+success_rate) | Beaucoup de badges renvoient 0/0/0 |

### Liste des badges actuels (codes connus)

`first_steps`, `padawan_path`, `knight_trial`, `addition_master`, `speed_demon`, `perfect_day`, `jedi_master`, `grand_master`, `subtraction_master`, `multiplication_master`, `division_master`, `expert`, `perfectionist`, `perfect_week`, (+ explorations `all_types`, `min_per_type`)

---

## 2. Périmètre du plan

| Lot | Description | Dépendances |
|-----|-------------|-------------|
| **A** | Refonte UX/UI page badges | Aucune |
| **B** | Admin CRUD (créer, modifier, supprimer badges) | Modèle existant |
| **C** | Refactoring moteur (requirements génériques, progress) | Lot B (optionnel) |

---

## 3. Challenges psychologiques — Principes et études

Les meilleures études en gamification, rétention et psychologie cognitive orientent le design des badges. Voici les principes appliqués au plan :

### 3.1 Effet de progression (Goal-Gradient) — Clark Hull, 1932

> *« La motivation et l'effort augmentent à mesure que l'on perçoit l'approche d'un objectif. »*

| Donnée | Application badges |
|--------|--------------------|
| Barres de progression : **+40-60%** d'engagement | Afficher X/Y sur chaque badge verrouillé |
| Progrès initial offert (ex: 10%) amplifie l'effet | Nouveaux users : démarrer avec 1-2 badges « en cours » visibles |
| Formulation « Plus que 3 » > « 5/8 » | Texte motivationnel : « Plus que 3 exercices ! » |

**Référence** : Kivetz et al., Goal-Gradient Effect in UX (LogRocket)

### 3.2 Biais de dotation (Endowment Effect) — Thaler, Kahneman & Knetsch

> *« La propriété augmente la valeur perçue au-delà de sa valeur marchande. »*

| Donnée | Application badges |
|--------|--------------------|
| Les objets possédés sont surévalués | Mettre en avant « Ma collection » — badges obtenus en premier ou section dédiée |
| Ownership crée l'attachement | Permettre de « mettre en avant » 1-3 badges sur le profil / header |
| Badges = propriété virtuelle valorisée | Animations distinctes pour les badges obtenus vs verrouillés |

**Référence** : Study on endowment with tangible/intangible goods (2024, Flore)

### 3.3 Biais de rareté (Scarcity) — Cialdini, principes d'influence

> *« Les objets perçus comme limités ou rares sont attribués une valeur supérieure. »*

| Donnée | Application badges |
|--------|--------------------|
| Rareté quantitative > temporelle en gamification | Badges « légendaires », « or » = visuels distincts (brillance, bordure) |
| « Seulement X% l'ont » renforce le désir | Indicateur rareté : « Rare » (e.g. &lt;5% des users), « Commun » |
| Exclusivité motive | Badges secrets, limited edition (événements, saisons) |

**Référence** : NN/G Scarcity Principle, Make it Scarce (Behavioral Design), LogRocket UX

### 3.4 Preuve sociale (Social Proof) — Cialdini

> *« Les gens se fient au comportement des autres pour juger de la valeur d'une action. »*

| Donnée | Application badges |
|--------|--------------------|
| « X% des utilisateurs ont ce badge » | Afficher : « 12% des padawans l'ont débloqué » sur cartes verrouillées |
| Comparaison avec pairs proches | Badges débloqués par « des utilisateurs de ton niveau » |
| Duolingo : ligues = preuve sociale compétitive | Lien vers leaderboard, « Ton classement parmi les padawans » |

**Référence** : Duolingo gamification (StriveCloud, NudgeNow), Long-Term Gamification Survey 2024

### 3.5 Aversion à la perte (Loss Aversion) — Kahneman & Tversky

> *« La peur de perdre motive 2x plus que l'espoir de gagner. »*

| Donnée | Application badges |
|--------|--------------------|
| Streak perdu = perte perçue forte | Système de streak (jours consécutifs) — Duolingo : 3.6x rétention |
| « Tu approches, ne lâche pas ! » | Toast / message si proche (80-90%) : « Plus qu'un effort ! » |
| Progrès en danger = motivation | Notification douce si inactivité (streak en danger) |

**Référence** : Duolingo -21% churn avec Streak Freeze, Prospect Theory

---

## 4. Lot A — Refonte UX/UI page badges

### 4.1 Objectifs

- Simplifier la hiérarchie visuelle
- Réduire la surcharge cognitive (stats, perf, progression, grille)
- Appliquer les principes psychologiques (progression, endowment, rareté, preuve sociale)
- Ajouter filtres et tri
- Afficher les conditions d'obtention sur chaque badge

### 4.2 Tâches proposées (optimisées par la psychologie)

| # | Tâche | Description | Principe |
|---|-------|-------------|----------|
| A1 | **Redesign layout** | En-tête allégé (titre + points + niveau), fusion des 4 cartes stats en une vue condensée | Réduction charge cognitive |
| A2 | **Réorganiser sections** | 1) **Ma collection** (obtenus en premier — endowment), 2) Badges en cours (progression), 3) À débloquer (verrouillés), 4) Stats détaillées (repliable) | Endowment, Goal-Gradient |
| A3 | **Conditions visibles** | Sur chaque `BadgeCard` verrouillé : « Résoudre 50 exercices », « Plus que 12 ! » | Goal-Gradient |
| A4 | **Indicateur rareté** | Badge « Rare » (&lt;5% des users), « Légendaire » (or) — visuel distinct (bordure, brillance) | Scarcity |
| A5 | **Preuve sociale** | « X% des utilisateurs ont ce badge » — endpoint stats par badge (`count user_achievements`) | Social Proof |
| A6 | **Filtres** | Par statut (Tous / Obtenus / Verrouillés / Proches >50%), par catégorie, par difficulté, par rareté | Autonomie |
| A7 | **Tri** | Par progression (proches d'abord — goal-gradient), date d'obtention, points, rareté | Goal-Gradient |
| A8 | **BadgeCard amélioré** | Barre de progression + conditions + rareté + % social proof | Consolidation |
| A9 | **Mise en avant « Ma collection »** | Section « Mes trophées » mise en avant, option « Épingler » 1-3 badges (profil/header) | Endowment |

### 4.3 Nouveaux besoins backend (pour A4, A5)

| Besoin | Endpoint / Donnée | Effort |
|--------|-------------------|--------|
| Rareté par badge | `GET /api/badges/stats` étendu : `{ badge_id: { unlock_count, total_users, rarity_percent } }` | Faible |
| Preuve sociale | Même endpoint : `unlock_percent` par badge | Faible |

### 4.4 Fichiers impactés

- `frontend/app/badges/page.tsx`
- `frontend/components/badges/BadgeCard.tsx`
- `frontend/components/badges/BadgeGrid.tsx`
- `frontend/hooks/useBadges.ts`, `useBadgesProgress.ts`
- `server/handlers/badge_handlers.py` (stats rareté)
- `app/services/badge_service.py` (méthode `get_badges_rarity`)
- `frontend/messages/fr.json`, `en.json` (traductions conditions, rareté)

### 4.5 Complexité : **Moyenne**  
### 4.6 Risque : **Faible**

| Risque | Mitigation |
|--------|------------|
| Régression visuelle | Tests visuels, vérifier accessibilité |
| Perf (filtres côté client) | Pagination ou virtualisation si >50 badges |
| Stats rareté coûteuses | Cache 5-10 min, requête agrégée unique |

---

## 5. Lot B — Admin CRUD badges

### 5.1 Objectifs

- Permettre de créer, modifier, supprimer des badges depuis l'admin
- Aligner avec le CRUD exercices/défis existant
- Gérer l'impact sur `user_achievements` (suppression)
- **Design orienté psychologie** : gamification, rétention et psychologie cognitive guident la conception des badges (création, modification, suppression)

### 5.2 Tâches proposées

| # | Tâche | Description |
|---|-------|-------------|
| B1 | **Endpoints API** | `GET /api/admin/badges`, `POST /api/admin/badges`, `GET /api/admin/badges/{id}`, `PUT /api/admin/badges/{id}`, `DELETE /api/admin/badges/{id}` ou `PATCH is_active` |
| B2 | **Handlers admin** | `admin_handlers.py` ou nouveau `admin_badge_handlers.py` |
| B3 | **Page admin** | `/admin/content` — nouvel onglet « Badges » ou `/admin/badges` dédié |
| B4 | **Reformuler badges existants** | Auditer et reformuler les badges actuels (icône, titre, visuel, objectif) dans le contexte du projet. Création, modification, suppression : alignement sur gamification, rétention, psychologie cognitive — **Goal-gradient**, **endowment**, **scarcity**, **social proof**, **loss aversion** |
| B5 | **Formulaire création/édition** | Champs : code, name, description, category, difficulty, points_reward, is_secret, requirements (JSON éditable ou formulaire structuré). Aide-contexte rappelant les principes psychologiques pour orienter le design |
| B6 | **Suppression** | Soft delete (`is_active=false`) recommandé ; hard delete avec cascade sur `user_achievements` si requis |
| B7 | **Validation** | Code unique, requirements JSON valide, schéma minimum (`attempts_count` ou `min_attempts`+`success_rate`) |

### 5.3 B4 — Principes psychologiques pour la reformulation

Lors de l'audit et reformulation des badges (B4), chaque badge doit être repensé selon le contexte actuel du projet et les principes suivants :

| Principe | Application au design du badge |
|----------|-------------------------------|
| **Goal-gradient** | Objectif progressif (X/Y), barre visible, formulation « Plus que X » — incite à l'effort |
| **Endowment** | Visuel valorisant pour les badges obtenus, option épingler — renforce la propriété perçue |
| **Scarcity** | Badges or/légendaire = visuels distincts ; « Rare » (&lt;5%) — rareté motive |
| **Social proof** | « X% ont débloqué » — comparaison avec les pairs renforce le désir |
| **Loss aversion** | Streaks, « Tu approches, ne lâche pas ! » — peur de perdre motive 2× plus que l'espoir de gagner |

**Livrable B4** : Chaque badge reformulé avec icône, titre, description, objectif alignés sur ces principes et le contexte Mathakine (thème Jedi, gamification éducative).

### 5.4 Schéma `requirements` à supporter (minimum)

```json
{ "attempts_count": 50 }
{ "min_attempts": 50, "success_rate": 80 }
{ "exercise_type": "addition", "consecutive_correct": 20 }
{ "max_time": 5 }
{ "consecutive_days": 7 }
```

### 5.5 Fichiers impactés

- `server/handlers/admin_handlers.py` ou nouveau fichier
- `server/routes.py`
- `app/schemas/` (schema Achievement pour admin)
- `frontend/app/admin/content/` ou `admin/badges/`
- `frontend/hooks/useAdminBadges.ts` (à créer)
- `frontend/lib/api/client.ts`

### 5.6 Complexité : **Moyenne**  
### 5.7 Risque : **Moyen**

| Risque | Mitigation |
|--------|------------|
| Badge supprimé alors que des users l'ont | Soft delete, ou vérifier `user_achievements` avant delete |
| Requirements invalides | Validation Pydantic + tests unitaires |
| Code duplicate | Contrainte UNIQUE en base, erreur 409 côté API |

---

## 6. Lot C — Refactoring moteur badges

### 6.1 Objectifs

- Remplacer les 15+ `if badge.code == 'xxx'` par un moteur générique basé sur `requirements` JSON
- Étendre `_get_badge_progress` pour tous les types de requirements
- Permettre d'ajouter de nouveaux badges sans modifier le code

### 6.2 Architecture proposée

**Types de requirements à supporter** :

| Type | Clés JSON | Calcul progression | Exemple |
|------|-----------|--------------------|---------|
| `attempts_count` | `attempts_count` | count(attempts) / target | Premiers Pas |
| `success_rate` | `min_attempts`, `success_rate` | total/target, rate check | Expert |
| `consecutive` | `exercise_type`, `consecutive_correct` | max streak / target | Maître additions |
| `max_time` | `max_time` | 0 ou 1 (binaire) | Éclair |
| `consecutive_days` | `consecutive_days` | jours consécutifs / target | Semaine parfaite |
| `perfect_day` | — | 0 ou 1 (binaire) | Journée parfaite |
| `all_types` | `min_per_type` ? | types couverts / total | Explorateur |
| `min_per_type` | `min_count` | min(counts) / target | Polyvalent |

### 6.3 Tâches proposées

| # | Tâche | Description |
|---|-------|-------------|
| C1 | **Registry de vérificateurs** | `BadgeRequirementChecker` par type : `check_attempts_count`, `check_success_rate`, `check_consecutive`, etc. |
| C2 | **Refactor `_check_badge_requirements`** | Détecter le type depuis `requirements`, appeler le checker adéquat ; garder fallback par code pour rétrocompatibilité |
| C3 | **Refactor `_get_badge_progress`** | Implémenter `get_progress` pour chaque type (consecutive, days, etc.) |
| C4 | **Migration données** | S'assurer que tous les badges en base ont un `requirements` valide et complet |
| C5 | **Tests** | Tests unitaires pour chaque type de requirement |

### 6.4 Fichiers impactés

- `app/services/badge_service.py` (refactoring majeur)
- Nouveau `app/services/badge_requirement_engine.py` (optionnel, extraction)
- `tests/` (badge_service, handlers)

### 6.5 Complexité : **Élevée**  
### 6.6 Risque : **Moyen à élevé**

| Risque | Mitigation |
|--------|------------|
| Régression : badges non attribués | Tests de non-régression sur chaque badge existant |
| Edge cases (perfect_day, consecutive_days) | Logique métier complexe, bien tester |
| Performances | Requêtes SQL optimisées, cache si besoin |

---

## 7. Matrice complexité / risque

| Lot | Complexité | Risque | Effort estimé |
|-----|-------------|--------|---------------|
| **A** Refonte UX (+ psychologie) | Moyenne | Faible | 4–6 jours |
| **B** Admin CRUD (+ B4 reformulation) | Moyenne | Moyen | 4–6 jours |
| **C** Moteur badges | Élevée | Moyen à élevé | 5–8 jours |

### Dépendances

```
A (UX) ──────► Peut être fait en premier
     │
B (Admin) ───► Indépendant, peut précéder ou suivre A
     │
C (Moteur) ──► Utile après B pour gérer les nouveaux types de requirements créés par admin
               Mais peut être fait avant B si priorité = qualité du code actuel
```

---

## 8. Ordre d'exécution et itérations

### Option choisie : **Option 1 — UX d'abord**

> **Stratégie** : Avancer par **petites itérations** pour pouvoir réagir en cas de problème. On ne fait pas tout d'un coup.

### Séquence globale

1. **Lot A** — Refonte page badges (par itérations A-1 à A-4)
2. **Lot B** — Admin CRUD (par itérations B-1 à B-3)
3. **Lot C** — Refactoring moteur (si nécessaire)

---

### Lot A — Décomposition en itérations

| Ité | Tâches | Livrable | Durée estimée | Point de contrôle |
|-----|--------|----------|---------------|-------------------|
| **A-1** | A1 (layout), A2 (sections) | Page restructurée : en-tête allégé, ordre Ma collection → En cours → À débloquer | 1–2 j | Vérifier que rien n'est cassé, navigation fluide |
| **A-2** | A3 (conditions), A8 (BadgeCard) | Conditions visibles sur BadgeCard verrouillé, barre de progression intégrée | 1 j | Chaque badge verrouillé affiche « Comment débloquer » |
| **A-3** | A6 (filtres), A7 (tri) | Filtres (statut, catégorie, difficulté) et tri (progression, date) | 1 j | Tester combinaisons filtres + tri |
| **A-4** | A4 (rareté), A5 (preuve sociale), A9 (épingler) | Backend stats rareté + « X% ont débloqué » + option épingler | 1–2 j | Endpoint stats, cache si perfs |

**Règle** : Après chaque itération → commit, test, validation. Si problème : ajuster avant de passer à la suivante.

---

### Lot B — Décomposition en itérations (après A)

| Ité | Tâches | Livrable | Durée estimée | Point de contrôle |
|-----|--------|----------|---------------|-------------------|
| **B-1** | B1, B2 (API) | Endpoints `GET/POST/PUT/DELETE /api/admin/badges` + handlers | 1 j | Tests API (curl/Postman) |
| **B-2** | B3, B5 (page + formulaire) | Page admin badges, formulaire création/édition avec rappel des principes psychologiques | 1–2 j | CRUD fonctionnel en admin |
| **B-3** | B6, B7 (suppression, validation) | Soft delete, validation requirements | 0.5–1 j | Pas de régression |
| **B-4** | B4 (reformulation) | Audit et reformulation des badges existants : icône, titre, visuel, objectif — alignement goal-gradient, endowment, scarcity, social proof, loss aversion | 1–2 j | Cohérence design + psychologie, contexte projet |

---

### Lot C — Décomposition (si priorité)

| Ité | Tâches | Livrable |
|-----|--------|----------|
| **C-1** | C1, C2 | Registry vérificateurs, refactor `_check_badge_requirements` |
| **C-2** | C3, C4, C5 | `_get_badge_progress` étendu, migration, tests |

---

## 9. Suivi d'avancement — À mettre à jour

> **À remplir au fur et à mesure des itérations.** Modifier ce fichier après chaque livrable.

### Lot A — Refonte UX

| Ité | Statut | Date | Notes / Problèmes rencontrés |
|-----|--------|------|------------------------------|
| **A-1** | ✅ Fait | 16/02 | Layout allégé, sections Ma collection → En cours → À débloquer, stats repliables |
| **A-2** | ✅ Fait | 16/02 | Conditions visibles (criteria_text), barre progression dans BadgeCard verrouillé |
| **A-3** | ✅ Fait | 16/02 | Filtres (statut, catégorie, difficulté) et tri (progression, date, points, catégorie) |
| **A-4** | ✅ Fait | 16/02 | Rareté, preuve sociale (« X% ont débloqué »), indicateur Rare, option épingler (max 3) |

**Légende** : ⬜ À faire | 🔄 En cours | ✅ Fait | ⏸️ En pause

### Lot B — Admin CRUD

| Ité | Statut | Date | Notes / Problèmes rencontrés |
|-----|--------|------|------------------------------|
| **B-1** | ✅ Fait | 16/02 | Endpoints GET/POST/PUT/DELETE /api/admin/badges + handlers, soft delete |
| **B-2** | ✅ Fait | 16/02 | Onglet Badges dans /admin/content, BadgeCreateModal, BadgeEditModal, useAdminBadges, filtres actifs/catégorie |
| **B-3** | ⬜ À faire | — | |
| **B-4** | ⬜ À faire | — | Reformulation badges existants (icône, titre, visuel, objectif) — psychologie cognitive |

### Lot C — Moteur

| Ité | Statut | Date | Notes |
|-----|--------|------|-------|
| **C-1** | ⬜ À faire | — | |
| **C-2** | ⬜ À faire | — | |

### Décisions / Ajustements

| Date | Décision ou ajustement |
|------|------------------------|
| 16/02 | Option 1 choisie. Itérations documentées. |
| 16/02 | A-1 livré : en-tête condensé (barre stats), ordre Ma collection → Badges en cours → À débloquer, stats détaillées repliables. |
| 16/02 | A-2 livré : _format_requirements_to_text dans badge_service, criteria_text dans API, BadgeCard affiche conditions + barre X/Y sur badges verrouillés. |
| 16/02 | A-3 livré : barre filtres (statut, catégorie, difficulté), tri (progression, date, points, catégorie), bouton Réinitialiser. BadgeGrid accepte sortBy. |
| 16/02 | A-4 livré : GET /api/badges/rarity (stats par badge), preuve sociale + badge Rare dans BadgeCard, PATCH /api/badges/pin, colonne pinned_badge_ids, épingler max 3 badges. Migration 20260216_pinned. |
| 16/02 | Lot B enrichi : B4 ajouté — reformulation des badges existants (icône, titre, visuel, objectif) alignée sur goal-gradient, endowment, scarcity, social proof, loss aversion. B5 (formulaire) intègre rappel des principes. |
| 16/02 | B-1 livré : GET/POST/PUT/DELETE /api/admin/badges. Handlers dans admin_handlers.py. Soft delete (is_active=false). Validation requirements (attempts_count, min_attempts+success_rate, ou schémas étendus). |
| 16/02 | B-2 livré : Onglet Badges dans /admin/content, BadgeCreateModal, BadgeEditModal, useAdminBadges, filtres actifs/catégorie. Bloc repliable principes psychologiques dans les modales. GET /api/admin/badges/{id} inclut _user_count. |
| 16/02 | **Audit refactoring** : BadgeCard « Obtenu le » → i18n (earnedOn), BadgeGrid tri difficulté → legendary ajouté. Vérifié : earned_badges.id = achievement_id, rarityMap clés string, progressMap cohérent, admin CRUD cohérent. |

**Workflow** : À chaque fin d'itération → mettre à jour le statut (⬜ → 🔄 → ✅), la date, et les notes si problème. Ajouter les décisions dans le tableau ci-dessus.

### Audit technique (16/02 — nuit)

| Élément | Vérifié | Note |
|--------|---------|------|
| earned_badges.id | ✅ | id = achievement_id (badge), cohérent avec BadgeGrid earnedBadgeMap |
| rarityMap | ✅ | Clés string (badge.id), by_badge depuis GET /api/badges/rarity |
| progressMap | ✅ | Filtrage inProgress target>0, pas de 0/0 affichés (P0 audit) |
| BadgeCard cadenas | ✅ | Uniquement sur badges verrouillés (Lock si !isEarned) |
| BadgeEditModal loading | ✅ | DialogTitle présent pour accessibilité Radix |
| _format_requirements_to_text | ✅ | Couvre attempts_count, min_attempts+success_rate, consecutive, max_time, consecutive_days |
| _validate_requirements | ✅ | attempts_count, min_attempts+success_rate, ou objet non vide (consecutive_days, etc.) |
| Tri difficulté BadgeGrid | ✅ | legendary ajouté dans difficultyOrder |
| i18n BadgeCard date | ✅ | earnedOn + toLocaleDateString(locale) |

---

## Annexes

### A. Fichiers clés actuels

- `app/models/achievement.py` — Modèle Achievement, UserAchievement
- `app/services/badge_service.py` — Logique vérification + progression
- `server/handlers/badge_handlers.py` — Endpoints publics
- `frontend/app/badges/page.tsx` — Page principale
- `frontend/components/badges/BadgeCard.tsx`, `BadgeGrid.tsx`

### B. Références

- [BADGES_AMELIORATIONS](BADGES_AMELIORATIONS.md) — Améliorations UX détaillées
- [BADGES_AUDIT_PAUFINAGE](BADGES_AUDIT_PAUFINAGE.md) — Audit pré-paufinage (ergonomie 2560×1440, rétention, gamification)
- [ADMIN_ESPACE_PROPOSITION](ADMIN_ESPACE_PROPOSITION.md) — Phase 3 : « Badges | Création/modification »
- [SITUATION_FEATURES](SITUATION_FEATURES.md) — Priorités globales

### C. Études psychologie (gamification, rétention, biais)

- **Goal-Gradient** : Clark Hull 1932, Kivetz ; barres progression +40-60% engagement
- **Endowment effect** : Thaler, Kahneman & Knetsch ; ownership augmente valeur perçue
- **Scarcity** : Cialdini ; NN/G Scarcity Principle, Make it Scarce
- **Social proof** : Cialdini ; Duolingo ligues, StriveCloud/NudgeNow
- **Loss aversion** : Kahneman & Tversky ; Duolingo streak -21% churn
- **Long-Term Gamification Survey** (Springer 2024) : ownership, communauté, défis évolutifs
