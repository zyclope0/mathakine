# Placeholders et TODOs restants - Mathakine

> État au 06/02/2026 après unification Starlette  
> Dernière mise à jour : 16/02/2026 (Quick wins 1-4 implémentés)

## ✅ Quick wins 16/02/2026

| # | Tâche | Fichiers | Description |
|---|-------|----------|-------------|
| 1 | **maintenance_mode & registration_enabled** | `app/utils/settings_reader.py`, `server/middleware.py`, `server/handlers/user_handlers.py` | Maintenance : middleware 503 sauf /health, /metrics, /api/admin/*, /api/auth/login, refresh, validate-token. Inscriptions : 403 sur POST /api/users/ si `registration_enabled=false` |
| 2 | **handle_recommendation_complete** | `server/handlers/recommendation_handlers.py` | POST /api/recommendations/complete — met à jour `is_completed`, `completed_at` sur la recommandation |
| 3 | **get_user_badges_progress** | `server/handlers/badge_handlers.py`, `app/services/badge_service.py` | GET /api/challenges/badges/progress — retourne `{unlocked, in_progress}` avec progress 0-1 pour badges non débloqués |
| 4 | **is_current session** | `server/handlers/user_handlers.py` | GET /api/users/me/sessions — `is_current: true` sur la session la plus récente (proxy : requête depuis celle-ci) |

---

## ✅ Quick wins maintenance / code quality (22/02/2026)

Tâches à faible risque : optimiser, nettoyer, sécuriser, faciliter modularité.

| # | Tâche | Statut | Description |
|---|-------|--------|-------------|
| 1 | **rate_limit.py nettoyage** | ✅ Fait | Import `JSONResponse` en top-level, constantes `MSG_RATE_LIMIT_RETRY` et `MSG_CHAT_RATE_LIMIT` |
| 2 | **rate_limiter.py import** | ✅ Fait | Suppression import `Tuple` inutilisé |
| 3 | **Messages erreur API** | ✅ Fait | `Messages.JSON_BODY_INVALID`, `JSON_BODY_NOT_OBJECT` dans `request_utils.py` |
| 4 | **Helper `_rate_limit_response** | ✅ Fait | Ajouté dans `rate_limit.py` |
| 5 | **Tests rate_limit** | ✅ Fait | `tests/unit/test_rate_limit.py` |
| 6 | **Nettoyage placeholders** | ✅ Fait | Suppression routes + handlers : `start_challenge`, `get_challenge_progress`, `get_challenge_rewards`, `get_user_progress_by_exercise_type` |

---

## 📋 Récapitulatif

Ce document liste tous les endpoints/handlers **placeholders** (non implémentés) dans le projet.

**NOTE IMPORTANTE** : Les placeholders dans `app/api/endpoints/challenges.py` (FastAPI) ne sont plus pertinents car ce fichier est archivé et les handlers Starlette correspondants sont **déjà implémentés** :
- ✅ `GET /api/challenges` → Implémenté dans `server/handlers/challenge_handlers.py::get_challenges_list`
- ✅ `GET /api/challenges/{id}` → Implémenté dans `server/handlers/challenge_handlers.py::get_challenge`
- ✅ `POST /api/challenges/{id}/attempt` → Implémenté dans `server/handlers/challenge_handlers.py::submit_challenge_answer`
- ✅ `GET /api/challenges/{id}/hint` → Implémenté dans `server/handlers/challenge_handlers.py::get_challenge_hint`

---

## 🔴 Priorité HAUTE (Impact sécurité/UX)

### 1. ✅ `api_forgot_password` / `api_reset_password` - Réinitialisation mot de passe (implémenté 12/02/2026)
**Fichier** : `server/handlers/auth_handlers.py`  
**Routes** : `POST /api/auth/forgot-password`, `POST /api/auth/reset-password`  
**Implémentation** : Token stocké sur modèle User (`password_reset_token`, `password_reset_expires_at`), email via SendGrid/SMTP, templates thème Jedi (`app/utils/email_templates.py`).

---

## 🟠 Priorité MOYENNE (Fonctionnalités attendues)

### 2. ✅ `update_user_me` - Mise à jour profil utilisateur (implémenté)
**Fichier** : `server/handlers/user_handlers.py`  
**Route** : `PUT /api/users/me`  
**Implémentation** : Validation (email, full_name, grade_level, learning_style, preferred_theme, accessibility_settings), unicité email, réponse utilisateur mis à jour.

**Champs modifiables** : email (unicité), full_name, grade_level, learning_style, preferred_difficulty, preferred_theme, accessibility_settings (language_preference, timezone, notification_preferences, privacy_settings)

---

### 3. ✅ `update_user_password_me` - Changement mot de passe (implémenté)
**Fichier** : `server/handlers/user_handlers.py`  
**Route** : `PUT /api/users/me/password`  
**Implémentation** : Protégé CSRF, validation current_password/new_password (min 8 car.), hash et sauvegarde.

**Validation** :
- Ancien mot de passe correct
- Nouveau mot de passe ≥ 8 caractères
- Nouveau ≠ ancien

---

### 4. ✅ `get_users_leaderboard` - Classement des utilisateurs (implémenté)
**Fichier** : `server/handlers/user_handlers.py`  
**Route** : `GET /api/users/leaderboard`  
**Implémentation** : Top utilisateurs par total_points, respecte show_in_leaderboards (privacy). Paramètres: limit (défaut 50).

---

### 5. ✅ `get_user_badges_progress` - Progression badges (implémenté 16/02/2026)
**Route** : `GET /api/challenges/badges/progress`  
**Implémentation** : BadgeService.get_badges_progress(user_id) — `{unlocked: [{id, code, name}], in_progress: [{id, code, name, progress, current, target}]}`. Progression calculée pour badges avec `attempts_count` ou `min_attempts`+`success_rate`.

---

## 🟡 Priorité BASSE (Fonctionnalités avancées)

### 6. ✅ `admin_users` - Liste utilisateurs (implémenté via admin)
**Route** : `GET /api/admin/users` (et non `GET /api/users/`)  
**Implémentation** : Liste paginée avec recherche, filtre rôle, filtre is_active. Page `/admin/users`.

---

### 7. ~~`get_user_progress_by_exercise_type`~~ — ✅ Supprimé (22/02/2026)
**Route** : ~~`GET /api/users/me/progress/{exercise_type}`~~  
Redondant avec `/api/users/me/progress`. Route et handler supprimés.

---

### 8. ✅ `handle_recommendation_complete` - Marquer recommandation complétée (implémenté 16/02/2026)
**Route** : `POST /api/recommendations/complete`  
**Body** : `{ "recommendation_id": int }`  
**Implémentation** : Met à jour `is_completed`, `completed_at` sur la recommandation (vérifie user_id).

---

### 9. ✅ Archivage exercices (via admin, pas DELETE)
**Route** : `PATCH /api/admin/exercises/{id}` avec `{is_archived: true}`  
**Implémentation** : L'admin peut archiver (soft delete) via `/admin/content`. Pas de DELETE physique.

---

### 10. ❌ `delete_user` - Supprimer utilisateur
**Fichier** : `server/handlers/user_handlers.py:826`  
**Route** : `DELETE /api/users/{user_id}`  
**Impact** : **Basse** - Admin uniquement, RGPD  
**Description** : Endpoint placeholder

**Solution recommandée** :
- Vérifier que l'utilisateur est admin
- Soft delete (is_active=false) ou hard delete
- RGPD : anonymiser les données (username → "user_deleted_12345")
- Supprimer toutes les sessions actives

---

### 11. ~~`start_challenge`~~ — ✅ Supprimé (22/02/2026)
**Route** : ~~`POST /api/challenges/start/{challenge_id}`~~  
Non nécessaire. Route et handler supprimés.

---

### 12. ~~`get_challenge_progress`~~ — ✅ Supprimé (22/02/2026)
**Route** : ~~`GET /api/challenges/progress/{challenge_id}`~~  
Redondant avec `/api/users/me/challenges/progress`. Route et handler supprimés.

---

### 13. ~~`get_challenge_rewards`~~ — ✅ Supprimé (22/02/2026)
**Route** : ~~`GET /api/challenges/rewards/{challenge_id}`~~  
Système de récompenses non défini. Route et handler supprimés.

---

## 🔧 TODOs techniques (non-bloquants)

### 14. ✅ Détecter la session actuelle (implémenté 16/02/2026)
**Fichier** : `server/handlers/user_handlers.py`  
**Implémentation** : `is_current: true` sur la session avec le `last_activity` le plus récent (proxy : la requête provient probablement de cette session). Une implémentation future avec `jti` dans le JWT serait plus précise.

---

## 📝 Recommandations finales

### Pattern d'authentification (mise a jour 09/02/2026)

Tous les nouveaux handlers authentifies doivent utiliser les decorateurs definis dans `server/auth.py` :

```python
from server.auth import require_auth, optional_auth, require_auth_sse

@require_auth          # 401 si non authentifie, injecte request.state.user
@optional_auth         # request.state.user = None si non authentifie
@require_auth_sse      # Erreur SSE si non authentifie (pour les streams)
```

### Priorités d'implémentation suggérées (ordre)

1. **P1 - Critique** : ✅ `api_forgot_password` (implémenté)
2. **P2 - Important** : ✅ `update_user_me`, ✅ `update_user_password_me` (implémentés)
3. **P3 - Gamification** : `get_users_leaderboard`, `get_user_badges_progress`
4. **P4 - Admin** : `get_all_users`, `delete_user`
5. **P5 - Optionnel** : Autres endpoints (peuvent être supprimés)

### Endpoints à **supprimer** (plutôt qu'implémenter) — ✅ Fait (22/02/2026)

- ~~`start_challenge`~~ — Supprimé
- ~~`get_challenge_progress`~~ — Supprimé
- ~~`get_challenge_rewards`~~ — Supprimé
- ~~`get_user_progress_by_exercise_type`~~ — Supprimé

### Nettoyage recommandé — ✅ Fait (22/02/2026)

Les handlers placeholders `start_challenge`, `get_challenge_progress`, `get_challenge_rewards`, `get_user_progress_by_exercise_type` ont été supprimés de `server/routes/` et des handlers associés.

---

## 🔧 Dette technique résiduelle — Audit Architecture 2026-03 (22/02/2026)

> Audit complet Phases 0→4 terminé. Les items ci-dessous sont les points non finalisés, classés par priorité. Référence : [AUDIT_ARCHITECTURE_BACKEND_2026-03.md](../archives/HISTORIQUE_PRE_REFACTOR_2026-03-13/AUDIT_ARCHITECTURE_BACKEND_2026-03.md)

### Priorité BASSE — Découpage `constants.py` partiel (A10)

| Item | Détail | Effort |
|------|--------|--------|
| `constants.py` 12 concerns → modules | Seul le domaine challenge a été extrait (`constants_challenge.py`). Il reste à extraire `exercise_constants.py`, `user_constants.py`, `normalization.py` | ~2h |

**Contexte :** Fonctionnel tel quel — `constants.py` est un hub de re-export stable. L'extraction complète améliorerait la lisibilité mais n'est pas bloquante.

---

### Priorité BASSE — Tests d'intégration sur les handlers delete/archive

| Item | Détail | Effort |
|------|--------|--------|
| Pas de test API pour `DELETE /api/users/me` avec erreur DB simulée | Le handler catch `UserNotFoundError` → 404, mais le path `DatabaseOperationError` → 500 n'est pas couvert par un test d'intégration | ~1h |

---

### Pour mémoire — Items délibérément non traités

| Item | Raison |
|------|--------|
| `auth_service.py` → classe `AuthService` (A7) | Remplacer pattern fonctions module-level. Risque élevé (33 tests + handlers), bénéfice faible à court terme. À faire lors d'une refonte auth. |
| `get_user_stats_for_dashboard` résiduel (A9) | 4 sous-méthodes extraites. Une 5e extraction (streak) possible mais rendement décroissant. |
| mypy strict mode | Le projet passe mypy standard. Mode strict (`--strict`) génère ~40 erreurs sur les duck-typing SQLAlchemy. À activer progressivement. |

---

## 🚀 Pour aller plus loin

### Avatars utilisateurs — banque + upload (UI ready — 03/03/2026)

**Contexte :** Le classement (`/leaderboard`) et le widget dashboard affichent actuellement un avatar généré dynamiquement (initiale du pseudo + dégradé de couleur déterministe). C'est un fallback fonctionnel et élégant, mais l'utilisateur devrait pouvoir choisir ou uploader son propre avatar.

**Fonctionnalités à implémenter (backend + frontend) :**

#### 1. Banque d'avatars prédéfinis
- Proposer une sélection d'avatars thématiques (ex : icônes spatiales, personnages Mathakine) côté frontend
- Stocker le choix comme `avatar_preset: string` sur le modèle `User`
- Endpoint : `PUT /api/users/me` — étendre avec le champ `avatar_preset`

#### 2. Upload d'image personnalisée
- Formulaire d'upload dans la page Profil (`/profile` ou `/settings`)
- Formats acceptés : `image/jpeg`, `image/png`, `image/webp` — taille max recommandée : 2 Mo
- Redimensionnement serveur : générer au minimum 3 tailles — `40×40` (widget, classement compact), `80×80` (carte profil), `160×160` (page profil)
- Stockage : fichier local `public/avatars/{user_id}.webp` ou bucket S3/objet cloud selon l'infrastructure
- Endpoint à créer : `POST /api/users/me/avatar` (multipart/form-data) → retourne `{ avatar_url: string }`
- Endpoint à créer : `DELETE /api/users/me/avatar` → supprime et repasse au fallback initiale

#### 3. Modèle User (backend)
| Champ | Type | Description |
|---|---|---|
| `avatar_url` | `string \| null` | URL absolue ou chemin relatif vers l'image uploadée |
| `avatar_preset` | `string \| null` | Identifiant d'un avatar prédéfini de la banque |

Priorité : `avatar_url` > `avatar_preset` > fallback initiale+dégradé.

#### 4. Composant frontend `UserAvatar` (à créer)
Centraliser la logique dans un composant réutilisable :
```tsx
// frontend/components/ui/UserAvatar.tsx
<UserAvatar username={entry.username} avatarUrl={entry.avatar_url} size="sm" | "md" | "lg" />
```
- `size="sm"` → `h-7 w-7` (widget leaderboard)
- `size="md"` → `h-10 w-10` (page leaderboard, journal d'activité)
- `size="lg"` → `h-16 w-16` (page profil)
- Fallback automatique si `avatarUrl` est `null` : initiale + dégradé (déjà implémenté)

#### 5. Intégration classement (déjà prête)
- `LeaderboardEntry` dans `hooks/useLeaderboard.ts` → ajouter `avatar_url?: string | null`
- `LeaderboardPage` et `LeaderboardWidget` → remplacer `PlayerAvatar` / `MiniAvatar` par `<UserAvatar>`
- Aucune modification structurelle de layout nécessaire — les composants sont déjà dimensionnés

**Fichiers frontend à modifier lors de l'implémentation :**
- `frontend/hooks/useLeaderboard.ts` — ajouter `avatar_url` à `LeaderboardEntry`
- `frontend/app/leaderboard/page.tsx` — remplacer `PlayerAvatar` par `<UserAvatar>`
- `frontend/components/dashboard/LeaderboardWidget.tsx` — remplacer `MiniAvatar` par `<UserAvatar>`
- `frontend/components/ui/UserAvatar.tsx` — **à créer** (composant centralisé)
- `frontend/app/profile/page.tsx` (ou settings) — ajouter section upload/sélection avatar

**Fichiers backend à modifier :**
- `app/models/user.py` — ajouter `avatar_url`, `avatar_preset`
- `server/handlers/user_handlers.py` — `PUT /api/users/me` + nouveau `POST /api/users/me/avatar`
- Migration Alembic — nouvelle migration pour les colonnes avatar

**Priorité : 🟠 Moyenne** — Amélioration UX identitaire, non bloquant fonctionnellement.

---

### Journal d'activité — enrichissement des données backend (UI ready — 03/03/2026)

**Contexte :** La page Tableau de bord → onglet Détails affiche un journal d'activité (`RecentActivity`).  
L'interface est **prête à accueillir des données enrichies** ; c'est le backend (`GET /api/users/me/stats` → champ `recent_activity`) qui doit remonter des informations plus précises.

**État actuel du backend :** Chaque entrée retourne `type: "exercise_completed"` + `description: "Exercice complété"` (libellé générique), sans catégorie, sans score, sans XP.

**Améliorations backend souhaitées :**

| Champ actuel | Amélioration souhaitée | Exemple de valeur |
|---|---|---|
| `description: "Exercice complété"` | Nom de la catégorie ou titre de l'exercice | `"Exercice : Fractions"` |
| `type: "exercise_completed"` | Type étendu : `"exercise"`, `"challenge"`, `"badge"` | `"challenge"` → icône Trophée |
| *(absent)* | Score ou gain XP | `"score": 100` ou `"xp_gained": 15` |
| `is_correct: bool` | Conserver — déjà utilisé pour la couleur de la bordure | — |

**Ce que l'UI affichera automatiquement sans modification :**

- Icône variée selon `type` (`CheckCircle2` exercice, `Trophy` défi, `Medal` badge) — il suffira d'étendre `getItemStyle()` dans `RecentActivity.tsx`
- Score en badge (`+15 XP`, `100%`) — ajouter un `<Badge>` conditionnel si `activity.xp_gained` ou `activity.score` est présent
- Titre de l'exercice en gras à la place de "Exercice complété"

**Fichiers frontend prêts (aucune modification structurelle nécessaire) :**
- `frontend/components/dashboard/RecentActivity.tsx` — interface `ActivityItem` à étendre avec `xp_gained?: number`, `score?: number`

**Fichier backend à mettre à jour :**
- `app/services/user_stats_service.py` — méthode qui construit `recent_activity` : enrichir avec le vrai nom de l'exercice/défi/badge, le type précis, et le XP gagné.

**Priorité : 🟡 Basse** — Purement cosmétique, aucun impact fonctionnel. À inclure lors d'une prochaine itération backend sur les stats utilisateur.

---

### Normalisation des niveaux de difficulté (souhait produit — 27/02/2026)

Sortir de la logique Star Wars (INITIE, PADAWAN, CHEVALIER, MAITRE, GRAND_MAITRE) pour des libellés plus universels. Voir **[docs/02-FEATURES/NIVEAUX_DIFFICULTE_NORMALISATION.md](../02-FEATURES/NIVEAUX_DIFFICULTE_NORMALISATION.md)**.

---

- Créer des issues GitHub/Jira pour chaque endpoint à implémenter
- Définir les specs fonctionnelles (Figma, PRD) pour les fonctionnalités UX
- Tester chaque endpoint implémenté avec des scripts Python (voir `test_progress_api.py` comme modèle)
