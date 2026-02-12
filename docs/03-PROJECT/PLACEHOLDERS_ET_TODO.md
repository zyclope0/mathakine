# Placeholders et TODOs restants - Mathakine

> Etat au 06/02/2026 apres unification Starlette  
> Derniere mise a jour : 12/02/2026 (auth emails, verification obligatoire)

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

### 2. ❌ `update_user_me` - Mise à jour profil utilisateur
**Fichier** : `server/handlers/user_handlers.py:776`  
**Route** : `PUT /api/users/me`  
**Impact** : **Moyenne** - Les utilisateurs attendent de pouvoir modifier leur profil  
**Description** : Endpoint placeholder

**Solution recommandée** :
```python
@require_auth  # Utiliser le decorateur centralise (server/auth.py)
async def update_user_me(request: Request):
    current_user = request.state.user  # Injecte par @require_auth
    data = await request.json()
    
    # Valider les champs (username, email, full_name, etc.)
    # Vérifier unicité email/username si modifiés
    # Mettre à jour via UserService ou directement en DB
    # Retourner l'utilisateur mis à jour
```

> **Note (09/02/2026)** : Depuis le refactoring auth, tous les handlers authentifies doivent utiliser `@require_auth` (ou `@optional_auth` / `@require_auth_sse`) au lieu de `get_current_user()` directement.

**Champs modifiables suggérés** :
- `username` (vérifier unicité)
- `email` (vérifier unicité + envoyer email de confirmation)
- `full_name`
- `preferred_language` (pour i18n)

---

### 3. ❌ `update_user_password_me` - Changement mot de passe
**Fichier** : `server/handlers/user_handlers.py:801`  
**Route** : `PUT /api/users/me/password`  
**Impact** : **Moyenne** - Sécurité utilisateur  
**Description** : Endpoint placeholder

**Solution recommandée** :
```python
@require_auth  # Utiliser le decorateur centralise (server/auth.py)
async def update_user_password_me(request: Request):
    current_user = request.state.user  # Injecte par @require_auth
    data = await request.json()
    
    # 1. Vérifier l'ancien mot de passe (current_password)
    # 2. Valider le nouveau mot de passe (longueur, complexité)
    # 3. Hasher et sauvegarder le nouveau mot de passe
    # 4. Optionnel : invalider toutes les sessions actives sauf la courante
    # 5. Envoyer email de notification de changement
```

**Validation** :
- Ancien mot de passe correct
- Nouveau mot de passe ≥ 8 caractères
- Nouveau ≠ ancien

---

### 4. ❌ `get_users_leaderboard` - Classement des utilisateurs
**Fichier** : `server/handlers/user_handlers.py:497`  
**Route** : `GET /api/users/leaderboard`  
**Impact** : **Moyenne** - Gamification  
**Description** : Endpoint placeholder

**Solution recommandée** :
```python
async def get_users_leaderboard(request: Request):
    # Paramètres : limit (défaut 50), timeRange (7j/30j/all), orderBy (xp/accuracy/streak)
    # Query : SELECT user.username, user.xp, stats FROM users ORDER BY xp DESC LIMIT X
    # Calculer le rang de chaque utilisateur
    # Retourner : [{rank: 1, username: "Alice", xp: 5000, accuracy: 0.92}, ...]
```

**Note** : Ajouter cache (Redis ou simple dict avec TTL 5min) pour éviter les queries lourdes à chaque requête.

---

### 5. ❌ `get_user_badges_progress` - Progression badges
**Fichier** : `server/handlers/badge_handlers.py:181`  
**Route** : `GET /api/challenges/badges/progress`  
**Impact** : **Moyenne** - Gamification  
**Description** : Endpoint placeholder

**Solution recommandée** :
```python
async def get_user_badges_progress(request: Request):
    user_id = current_user['id']
    
    # Récupérer les badges débloqués
    unlocked_badges = db.query(Achievement).filter(Achievement.user_id == user_id).all()
    
    # Calculer progression vers les badges non débloqués
    # Ex : Badge "100 exercices" → user a 75 exercices → 75%
    all_badges = db.query(BadgeDefinition).all()  # Si table existe
    
    # Retourner : {unlocked: [...], in_progress: [{badge_id, name, progress: 0.75}, ...]}
```

---

## 🟡 Priorité BASSE (Fonctionnalités avancées)

### 6. ❌ `get_all_users` - Liste tous les utilisateurs
**Fichier** : `server/handlers/user_handlers.py:474`  
**Route** : `GET /api/users/`  
**Impact** : **Basse** - Admin uniquement  
**Description** : Endpoint placeholder (admin)

**Solution recommandée** :
- Vérifier que l'utilisateur est admin (`is_admin` field)
- Pagination obligatoire (limit/skip)
- Filtres : search (username/email), is_active, created_after/before

---

### 7. ❌ `get_user_progress_by_exercise_type` - Progression par type
**Fichier** : `server/handlers/user_handlers.py:637`  
**Route** : `GET /api/users/me/progress/{exercise_type}`  
**Impact** : **Basse** - Détail granulaire (déjà disponible dans `/api/users/stats`)  
**Description** : Endpoint placeholder

**Solution recommandée** :
- Peut être supprimé car `/api/users/me/progress` contient déjà `by_category`
- Ou implémenter pour avoir encore plus de détails (historique par type)

---

### 8. ❌ `handle_recommendation_complete` - Marquer recommandation complétée
**Fichier** : `server/handlers/recommendation_handlers.py:128`  
**Route** : `POST /api/recommendations/complete`  
**Impact** : **Basse** - Suivi des recommandations  
**Description** : Endpoint placeholder

**Solution recommandée** :
```python
async def handle_recommendation_complete(request: Request):
    user_id = current_user['id']
    data = await request.json()
    recommendation_id = data.get('recommendation_id')
    
    # Mettre à jour la recommandation : completed_at = now()
    db.query(Recommendation).filter(
        Recommendation.id == recommendation_id,
        Recommendation.user_id == user_id
    ).update({Recommendation.completed_at: datetime.now()})
    db.commit()
```

---

### 9. ❌ `delete_exercise` - Supprimer exercice
**Fichier** : `server/handlers/exercise_handlers.py:940`  
**Route** : `DELETE /api/exercises/{exercise_id}`  
**Impact** : **Basse** - Fonctionnalité admin/créateur  
**Description** : Endpoint placeholder

**Solution recommandée** :
- Vérifier que l'utilisateur est soit admin, soit créateur de l'exercice
- Soft delete (is_deleted=true) plutôt que DELETE physique
- Optionnel : archiver les tentatives associées

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

### 11. ❌ `start_challenge` - Démarrer un défi
**Fichier** : `server/handlers/challenge_handlers.py:522`  
**Route** : `POST /api/challenges/start/{challenge_id}`  
**Impact** : **Très basse** - Tracking optionnel  
**Description** : Endpoint placeholder (tracking de démarrage)

**Solution recommandée** :
- Créer une table `challenge_sessions` avec `started_at`, `user_id`, `challenge_id`
- Permet de tracker le temps total passé sur un défi (différence entre started_at et attempt.created_at)
- **OU** : Supprimer cet endpoint (pas vraiment nécessaire)

---

### 12. ❌ `get_challenge_progress` - Progression d'un défi
**Fichier** : `server/handlers/challenge_handlers.py:549`  
**Route** : `GET /api/challenges/progress/{challenge_id}`  
**Impact** : **Très basse** - Tracking optionnel  
**Description** : Endpoint placeholder

**Solution recommandée** :
- Retourner les tentatives de l'utilisateur pour ce défi spécifique
- Nombre de tentatives, meilleur temps, indices utilisés
- **OU** : Ces infos sont déjà dans `/api/users/me/challenges/progress`

---

### 13. ❌ `get_challenge_rewards` - Récompenses d'un défi
**Fichier** : `server/handlers/challenge_handlers.py:576`  
**Route** : `GET /api/challenges/rewards/{challenge_id}`  
**Impact** : **Très basse** - Système de récompenses non implémenté  
**Description** : Endpoint placeholder

**Solution recommandée** :
- Dépend de la création d'un système de récompenses (XP, badges, items virtuels)
- **Suggestion** : Reporter à plus tard ou supprimer

---

## 🔧 TODOs techniques (non-bloquants)

### 14. 🔵 TODO: Détecter la session actuelle
**Fichier** : `server/handlers/user_handlers.py:904`  
**Ligne** : `"is_current": False  # TODO: Détecter la session actuelle via le token`  
**Impact** : **Basse** - UX (afficher "Session actuelle" dans la liste)

**Solution recommandée** :
```python
# Dans get_user_sessions
current_token = request.cookies.get('access_token') or request.headers.get('Authorization', '').replace('Bearer ', '')

for session in sessions:
    # Comparer session.jti avec le JTI du token actuel
    is_current = (session.jti == decode_jwt(current_token).get('jti'))
    session_dict['is_current'] = is_current
```

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

1. **P1 - Critique** : `api_forgot_password` (sécurité + UX attendue)
2. **P2 - Important** : `update_user_me`, `update_user_password_me` (gestion compte)
3. **P3 - Gamification** : `get_users_leaderboard`, `get_user_badges_progress`
4. **P4 - Admin** : `get_all_users`, `delete_user`
5. **P5 - Optionnel** : Autres endpoints (peuvent être supprimés)

### Endpoints à **supprimer** (plutôt qu'implémenter)

- `start_challenge` → Non nécessaire
- `get_challenge_progress` → Redondant avec `/api/users/me/challenges/progress`
- `get_challenge_rewards` → Système de récompenses non défini
- `get_user_progress_by_exercise_type` → Redondant avec `/api/users/me/progress`

### Nettoyage recommandé

Supprimer les handlers placeholders et leurs routes associées dans `server/routes.py` pour éviter la confusion.

---

## 🚀 Pour aller plus loin

- Créer des issues GitHub/Jira pour chaque endpoint à implémenter
- Définir les specs fonctionnelles (Figma, PRD) pour les fonctionnalités UX
- Tester chaque endpoint implémenté avec des scripts Python (voir `test_progress_api.py` comme modèle)
