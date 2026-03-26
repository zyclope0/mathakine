# Plan d'exécution — Leaderboard v2 Mathakine

**Date :** 2026-03-25
**Source :** Rapport Discovery leaderboard (session 2026-03-25)
**Préparation :** Claude Code / Octopus
**Exécution :** Cursor Composer
**Validation :** /octo:review après chaque lot

---

## 1. Objectif

Corriger les deux bugs bloquants du leaderboard (UX + filtre cassé),
enrichir l'API avec les données disponibles en DB (avatar, streak, badges),
puis améliorer l'UX/UI pour aligner le leaderboard avec le reste de l'application.

Chaque lot = un scope = un commit = un compte-rendu.

---

## 2. Règles non négociables

1. **Lire avant d'écrire** — auditer les fichiers réels avant toute modification
2. **Un lot = un commit**
3. **Diff strictement borné** — aucun changement hors scope
4. **Pas de refactor large caché**
5. **SQLAlchemy** : `.is_(True)` / `.is_(False)` pour les booléens
6. **Config** : pas de `os.getenv()` direct
7. **Zéro régression** sur les routes auth, le widget LeaderboardWidget du dashboard, et la privacy (`show_in_leaderboards`)
8. **Compatibilité backward** : enrichir la réponse API sans supprimer les champs existants

---

## 3. Vue d'ensemble des lots

| Lot  | Thème                            | Fichiers clés                                         | Risque  |
|------|----------------------------------|-------------------------------------------------------|---------|
| `L1` | Bugs + enrichissement API        | user_service.py, user_handlers.py, leaderboard/page.tsx, useLeaderboard.ts, types | Moyen   |
| `L2` | UX/UI — animations + empty state | leaderboard/page.tsx, LeaderboardWidget.tsx, i18n     | Faible  |

**Hors périmètre (dette connue, traitée séparément) :**
- Filtre temporel (7j/30j/all) — requête SQL complexe sur `point_events`, lot séparé si besoin
- Colonne `age_group` sur `users` — nécessite une migration et un formulaire de profil
- Chat API non-auth (P1 CLAUDE.md)
- Policies IA défis/exercices dupliquées

---

## 4. Gate standard avant review

### Backend
```
D:\Mathakine\.venv\Scripts\python.exe -m pytest tests/api/test_user_endpoints.py -q --tb=short
D:\Mathakine\.venv\Scripts\python.exe -m pytest tests/ -q --tb=short --maxfail=10 --no-cov
D:\Mathakine\.venv\Scripts\python.exe -m black <fichiers touchés> --check
D:\Mathakine\.venv\Scripts\python.exe -m isort <fichiers touchés> --check-only
```

### Frontend
```
cd D:\Mathakine\frontend && npm run lint
cd D:\Mathakine\frontend && npx tsc --noEmit
cd D:\Mathakine\frontend && npx vitest run <tests cibles>
cd D:\Mathakine\frontend && npx prettier --check <fichiers touchés>
```

---

## 5. Format de compte-rendu obligatoire

1. Diagnostic initial (ce qui était cassé)
2. Fichiers modifiés
3. Ce qui a été corrigé / ajouté
4. Ce qui a été laissé volontairement intact
5. Tests ajoutés / modifiés
6. Commandes de vérification exécutées
7. Résultat des checks
8. GO / NO-GO

---

## 6. Lot L1 — Bugs critiques + enrichissement API

### Objectif
- Corriger le bug UX : `Select` piégé dans le `Card` (disparaît si résultats vides)
- Corriger le filtre `age_group` backend : filtre sur `preferred_difficulty` (mauvaise colonne)
- Enrichir la réponse API : `avatar_url`, `current_streak`, `badges_count`
- Aligner les types TypeScript avec la nouvelle réponse

### Diagnostic des bugs

#### Bug UX — Select inaccessible si résultats vides
```tsx
// leaderboard/page.tsx (situation actuelle)
leaderboard.length === 0
  ? <EmptyState/>          // ← Utilisateur bloqué, ne peut pas changer le filtre
  : <Card>
      <CardHeader>
        <Select/>          // ← Disparaît avec le Card
      </CardHeader>
    </Card>
```

**Fix attendu :** Hisser le `Select` (et le `CardTitle`) hors de la condition, dans une zone
toujours visible au-dessus du bloc conditionnel.

#### Bug Backend — Filtre age_group sur mauvaise colonne
```python
# user_service.py (situation actuelle — INCORRECT)
if age_group:
    q = q.filter(User.preferred_difficulty == age_group)
    # preferred_difficulty stocke "easy"|"medium"|"hard", PAS le groupe d'âge
```

**Décision :** Il n'existe pas de colonne `age_group` sur `users` (pas de migration requise
pour L1). Le filtre est fondamentalement cassé.

**Fix attendu :** Supprimer le filtre `age_group` du backend ET le `Select` de filtre du
frontend dans L1. La fonctionnalité de filtre par groupe d'âge nécessiterait une migration
et un formulaire profil — hors périmètre, à documenter dans ROADMAP.

### Enrichissement API

**Champs à ajouter à `get_leaderboard_for_api` :**

| Champ             | Source                          | Type       | Nullable |
|-------------------|---------------------------------|------------|----------|
| `avatar_url`      | `user.avatar_url`               | string     | oui      |
| `current_streak`  | `user.current_streak`           | int        | non (défaut 0) |
| `badges_count`    | `len(user.user_achievements)`   | int        | non (défaut 0) |

**Note performance :** `user.user_achievements` est une relation lazy — utiliser
`joinedload(User.user_achievements)` dans la requête ou `len(user.user_achievements)`
après eager load pour éviter N+1. Préférer `db.query(func.count(...))` corrélé si
le count suffit.

### Scope autorisé

**Backend :**
- `D:\Mathakine\app\services\users\user_service.py` (get_leaderboard_for_api)
- `D:\Mathakine\server\handlers\user_handlers.py` (suppression param age_group)
- `D:\Mathakine\app\services\users\user_application_service.py` (suppression param age_group)

**Frontend :**
- `D:\Mathakine\frontend\hooks\useLeaderboard.ts` (suppression ageGroup, nouveaux champs)
- `D:\Mathakine\frontend\app\leaderboard\page.tsx` (fix Select + suppression filtre)
- `D:\Mathakine\frontend\components\dashboard\LeaderboardWidget.tsx` (nouveaux champs si affichés)
- `D:\Mathakine\frontend\types\api.ts` (si LeaderboardEntry pas dans useLeaderboard.ts)
- `D:\Mathakine\frontend\messages\fr.json` + `en.json` (si nouvelles clés nécessaires)
- tests nécessaires

### Scope interdit

- Table `users` — pas de migration en L1
- `recommendation_service.py`
- `badge_stats_cache.py`
- Autres pages que leaderboard

### Tests minimaux attendus

- `GET /api/users/leaderboard` → retourne `avatar_url`, `current_streak`, `badges_count`
- Page leaderboard : `Select` visible même si `leaderboard.length === 0`
- Page leaderboard : changer l'état du composant quand la liste est vide ne cache pas la UI
- `GET /api/users/leaderboard?age_group=xxx` → ignoré (paramètre supprimé) ou 400

### Commit cible
`fix(leaderboard): fix trapped select UX, remove broken age filter, enrich API response`

### Prompt Cursor
```txt
Tu exécutes le micro-lot L1 "Leaderboard v2 — bugs + enrichissement" en mode quality-first.

Contexte (rapport Discovery 2026-03-25) :
- Bug UX : le Select de filtre est dans le Card qui disparaît quand leaderboard.length === 0
  → l'utilisateur est bloqué, ne peut plus changer de filtre sans re-naviguer
- Bug backend : filtre age_group filtre sur `User.preferred_difficulty` (difficulté préférée
  easy/medium/hard) au lieu d'un vrai groupe d'âge. Il n'existe pas de colonne age_group sur
  users. Le filtre est fondamentalement cassé.
- Enrichissement : avatar_url, current_streak, badges_count sont disponibles en DB mais absents
  de la réponse API

Règle absolue :
- LIRE avant d'ÉCRIRE — auditer les fichiers réels avant toute modification
- Diff strictement borné
- Zéro régression sur privacy (show_in_leaderboards), widget LeaderboardWidget dashboard,
  et auth

Décisions de design imposées :
1. Supprimer le filtre age_group du backend ET du frontend dans ce lot
   (pas de colonne age_group sur users → migration hors périmètre)
   → Documenter dans ROADMAP_FONCTIONNALITES.md sous "Leaderboard — filtre par groupe d'âge"
2. Le Select "Tous les âges" disparaît avec le filtre
3. Le Card reste TOUJOURS visible même si leaderboard.length === 0
   → Restructurer la page pour que le Card/titre soient hors de la condition
   → La zone conditionnelle = seulement le contenu (liste ou empty state)

Périmètre autorisé Backend :
- D:\Mathakine\app\services\users\user_service.py
- D:\Mathakine\server\handlers\user_handlers.py
- D:\Mathakine\app\services\users\user_application_service.py
- tests/api/ ou tests/unit/ selon besoin

Périmètre autorisé Frontend :
- D:\Mathakine\frontend\hooks\useLeaderboard.ts
- D:\Mathakine\frontend\app\leaderboard\page.tsx
- D:\Mathakine\frontend\components\dashboard\LeaderboardWidget.tsx (si pertinent)
- D:\Mathakine\frontend\messages\fr.json + en.json
- tests frontend si nécessaire

Périmètre interdit :
- Migrations DB
- badge_stats_cache.py
- recommendation_service.py
- Autres pages

Travail attendu :
1. user_service.py — get_leaderboard_for_api
   - Lire le fichier entier
   - Supprimer le filtre `if age_group: q = q.filter(User.preferred_difficulty == age_group)`
   - Supprimer le paramètre age_group de la signature
   - Ajouter avatar_url, current_streak, badges_count à la réponse
   - Pour badges_count : utiliser len(user.user_achievements) — vérifier si la relation
     est déjà chargée (joinedload ou lazy). Si lazy, ajouter joinedload dans la requête.

2. user_application_service.py + user_handlers.py
   - Supprimer le paramètre age_group de get_leaderboard()
   - Supprimer le parsing de age_group dans le handler

3. useLeaderboard.ts
   - Supprimer le paramètre ageGroup
   - Ajouter les nouveaux champs dans LeaderboardEntry :
     avatar_url?: string
     current_streak: number
     badges_count: number

4. leaderboard/page.tsx
   - Lire le fichier entier
   - Supprimer le useState ageFilter et le Select de filtre d'âge
   - Restructurer la page pour que le Card (titre + header) soit TOUJOURS visible
   - Seul le contenu interne est conditionnel :
     - isLoading → skeleton ou LoadingState dans le CardContent
     - error → EmptyState dans le CardContent
     - leaderboard.length === 0 → EmptyState dans le CardContent
     - sinon → liste dans le CardContent
   - Afficher avatar_url (UserAvatar déjà importé), current_streak, badges_count
     dans chaque LeaderboardRow

5. Ajouter nouveaux champs dans les types si nécessaire

6. Tests causaux minimaux

Checks obligatoires :
1. git status --short && git diff --name-only
2. D:\Mathakine\.venv\Scripts\python.exe -m pytest tests/api/test_user_endpoints.py -q --tb=short
3. D:\Mathakine\.venv\Scripts\python.exe -m pytest tests/ -q --tb=short --maxfail=10 --no-cov
4. D:\Mathakine\.venv\Scripts\python.exe -m black app/services/users/user_service.py server/handlers/user_handlers.py app/services/users/user_application_service.py --check
5. D:\Mathakine\.venv\Scripts\python.exe -m isort app/services/users/user_service.py server/handlers/user_handlers.py app/services/users/user_application_service.py --check-only
6. cd D:\Mathakine\frontend && npm run lint
7. cd D:\Mathakine\frontend && npx tsc --noEmit
8. cd D:\Mathakine\frontend && npx prettier --check hooks/useLeaderboard.ts app/leaderboard/page.tsx

Format de compte-rendu final obligatoire :
1. Diagnostic initial
2. Fichiers modifiés
3. Ce qui a été corrigé / ajouté
4. Ce qui a été laissé volontairement intact
5. Tests ajoutés / modifiés
6. Commandes de vérification exécutées
7. Résultat des checks
8. GO / NO-GO
```

---

## 7. Lot L2 — UX/UI leaderboard

### Objectif
Aligner le leaderboard visuellement avec le reste de l'application :
- Empty state avec action "Voir tous les défis" ou lien utile
- Animations Framer Motion cohérentes (entrée des lignes, hover)
- Mise en valeur du top 3 (podium visuel)
- Affichage streak et badges dans la row (L1 fournit les données)
- Couleurs par rang Jedi (cohérent avec le profil)
- Responsive mobile (vérifier la row sur petits écrans)

### Scope autorisé

**Frontend uniquement :**
- `D:\Mathakine\frontend\app\leaderboard\page.tsx`
- `D:\Mathakine\frontend\components\dashboard\LeaderboardWidget.tsx`
- `D:\Mathakine\frontend\messages\fr.json` + `en.json`
- tests frontend si nécessaires

### Scope interdit
- Backend Python
- useLeaderboard.ts (L1 a livré les données, L2 consomme uniquement)
- Auth

### Intentions de correction

#### Empty state avec action
```tsx
// Actuellement : message statique
// Cible : EmptyState + lien "Commencer les défis" → /challenges
<EmptyState
  title={t("empty.title")}
  description={t("empty.description")}
  action={<Button asChild><Link href="/challenges">{t("empty.cta")}</Link></Button>}
/>
```

#### Animations Framer Motion
- Entrée de la liste : `staggerChildren` sur `ul`, `fadeInUp` sur chaque `li`
- Hover sur chaque row : légère élévation (calquer sur `StatsCard`)
- Top 3 : animation `scale` légèrement plus grande à l'entrée

#### Podium top 3
- Rang 1 : fond `amber/gold` subtil + border
- Rang 2 : fond `slate/silver` subtil
- Rang 3 : fond `amber-700/bronze` subtil
- Au-delà : fond neutre habituel
- Calquer sur le style des badges EdTech existants

#### Couleurs rang Jedi
```tsx
const jediRankColor = {
  "youngling":    "text-slate-400",
  "padawan":      "text-blue-400",
  "knight":       "text-green-400",
  "master":       "text-purple-400",
  "grand_master": "text-amber-400",
}
```

#### Streak et badges dans la row
- Streak > 0 → icône 🔥 + nombre (discret, `text-xs text-muted-foreground`)
- badges_count > 0 → icône 🏆 + nombre (discret)
- Ne pas afficher si 0 (pas de bruit visuel)

#### LeaderboardWidget (dashboard)
- Même couleurs rang Jedi
- Avatar si disponible

### Tests minimaux attendus
- EmptyState affiché avec lien `/challenges` quand liste vide
- Classes podium appliquées aux 3 premiers rangs
- Composant rendu sans crash avec streaks et badges à 0

### Commit cible
`feat(leaderboard): visual refresh — podium, jedi colors, framer animations, empty state CTA`

### Prompt Cursor
```txt
Tu exécutes le micro-lot L2 "Leaderboard v2 — UX/UI" en mode quality-first.
Ce lot est FRONTEND UNIQUEMENT. L1 a livré les données (avatar_url, current_streak,
badges_count) — ici on les affiche et on améliore l'apparence.

Contexte :
- L1 est terminé et commité : le Select de filtre a été supprimé, le Card est permanent,
  les données avatar/streak/badges sont disponibles dans les props/hooks
- Ce lot améliore l'apparence sans aucune modification backend

Règle absolue :
- LIRE avant d'ÉCRIRE
- Calquer le style sur les composants existants (StatsCard, ChallengesProgressWidget)
- Zéro modification backend

Périmètre autorisé :
- D:\Mathakine\frontend\app\leaderboard\page.tsx
- D:\Mathakine\frontend\components\dashboard\LeaderboardWidget.tsx
- D:\Mathakine\frontend\messages\fr.json + en.json
- tests si nécessaire

Périmètre interdit :
- Backend Python
- useLeaderboard.ts (L1 est figé)
- auth

Travail attendu :
1. leaderboard/page.tsx — Empty state avec action
   - Remplacer <EmptyState> statique par une version avec action
   - Action : Button → Link vers "/challenges" ou "/exercises"
   - Clé i18n : "empty.cta"

2. leaderboard/page.tsx — Animations Framer Motion
   - Envelopper la liste <ul> avec staggerChildren
   - Chaque <li> LeaderboardRow : fadeInUp (opacity 0→1, y 10→0)
   - Respecter useAccessibleAnimation() (shouldReduceMotion) — déjà utilisé dans l'app

3. leaderboard/page.tsx — Podium top 3
   - Rang 1 : fond amber/or subtil (bg-amber-500/10 border-amber-500/20)
   - Rang 2 : fond slate/silver (bg-slate-500/10 border-slate-500/20)
   - Rang 3 : fond amber-700/bronze (bg-amber-700/10 border-amber-700/20)
   - Rang 4+ : fond neutre bg-muted/30

4. leaderboard/page.tsx — Couleurs rang Jedi dans LeaderboardRow
   - youngling → text-slate-400
   - padawan → text-blue-400
   - knight → text-green-400
   - master → text-purple-400
   - grand_master → text-amber-400
   - Appliquer sur le texte du rang Jedi dans la row

5. leaderboard/page.tsx — Streak et badges dans la row
   - Si current_streak > 0 : afficher "🔥 N" en text-xs text-muted-foreground
   - Si badges_count > 0 : afficher icône Trophy + N en text-xs text-muted-foreground
   - Ne rien afficher si 0

6. LeaderboardWidget.tsx (dashboard)
   - Appliquer les mêmes couleurs rang Jedi
   - Afficher avatar si avatar_url disponible (UserAvatar déjà utilisé sur la page principale)

7. i18n fr.json + en.json
   - Ajouter clé "empty.cta" si absente
   - Vérifier toutes les nouvelles clés en fr ET en

Checks obligatoires :
1. git status --short && git diff --name-only
2. cd D:\Mathakine\frontend && npm run lint
3. cd D:\Mathakine\frontend && npx tsc --noEmit
4. cd D:\Mathakine\frontend && npx vitest run __tests__/unit/components/ (non-régression)
5. cd D:\Mathakine\frontend && npx prettier --check app/leaderboard/page.tsx components/dashboard/LeaderboardWidget.tsx

Format de compte-rendu final obligatoire :
1. Diagnostic initial
2. Fichiers modifiés
3. Ce qui a été corrigé / ajouté
4. Ce qui a été laissé volontairement intact
5. Tests ajoutés / modifiés
6. Commandes de vérification exécutées
7. Résultat des checks
8. GO / NO-GO
```

---

## 8. Hors périmètre — Points non traités (à planifier séparément)

Ces points ont été identifiés mais sont volontairement hors des lots L1/L2 :

| Feature | Raison du report | Effort estimé |
|---------|-----------------|---------------|
| Filtre par groupe d'âge réel | `age_group` n'existe pas sur `users` (c'est un champ du contenu, pas du profil). Nécessite colonne `age_group` sur `users` + migration + formulaire profil + dérivation de `grade_level` | M |
| Filtre temporel (7j/30j) | Requête sur `point_events` par fenêtre de temps, nouveau index, surface SQL large | M |
| Leaderboard par type de défi | Nécessite agrégation `challenge_progress` par user | M |
| Leaderboard par type d'exercice | Nécessite agrégation `progress` par user | M |
| Pagination infinie | Architecture actuelle `limit=50` — ajouter cursor pagination | S |
| Anonymisation avancée | Option "afficher pseudonyme" dans profil | S |

→ Tracer dans `docs/02-FEATURES/ROADMAP_FONCTIONNALITES.md` sous "Leaderboard v3"

---

## 8b. Lot L3 — Leaderboard à fort impact ✅ L3-A et L3-B livrés (2026-03-25)

Deux features identifiées post-L2 comme prioritaires pour la valeur EdTech :

### L3-A : Injection "Vous" hors top 50 (F40 ROADMAP) ✅ LIVRÉ — commit f04853a

**Problème** : un utilisateur classé #127 ne se voit jamais dans la liste (limit=50).
Le flag `is_current_user` existe mais est inutile si l'utilisateur n'est pas dans le top 50.

**Solution** :
- Backend : nouveau endpoint `GET /api/users/me/rank` → `{ rank: int, total_points: int }`
  (query `SELECT COUNT(*) + 1 FROM users WHERE total_points > :my_points AND is_active`)
- Frontend : si `is_current_user` absent du top 50, afficher le rang courant en bas de liste
  avec un séparateur visuel `───── votre position ─────`

**Effort** : S (1 endpoint, ~15 lignes backend, ~20 lignes frontend)
**Impact** : ⭐⭐⭐ — essentiel pour la motivation des utilisateurs hors top 50
**Prérequis** : aucun — F42 n'est PAS un prérequis (débat confirmé 3/3). Livrable après L2.

### L3-B : Filtre temporel (semaine / mois / tout) (F41 ROADMAP) ✅ LIVRÉ — commit f5e793f

**Problème** : `total_points` est cumulatif — un utilisateur actif depuis 1 semaine
ne peut jamais dépasser un utilisateur actif depuis 1 an.

**Solution** :
- Backend : query sur `point_events` par fenêtre de temps (`period=week|month|all`)
  `SELECT SUM(points) FROM point_events WHERE user_id = :id AND created_at >= :cutoff`
- L'index `ix_point_events_user_created (user_id, created_at)` existe déjà (migration 20260321)
- Frontend : `Select` période (Semaine / Mois / Tout temps) → requery

**Effort** : M (query agrégée + état frontend)
**Impact** : ⭐⭐⭐ — génère les retours réguliers ("champion de la semaine")
**Prérequis réels** : aucun blocage technique — `apply_points` EST déjà branché sur les exercices
standard (`exercise_attempt_service.py` ligne 127), index déjà en place.
⚠️ Condition de déploiement : vérifier que `point_events` est suffisamment peuplé en production
avant de rendre le filtre "semaine" visible (classement vide = mauvaise UX au lancement).
Le P1 mentionné dans CLAUDE.md est **obsolète** sur ce point — à corriger.

### L3-C : Architecture difficulté/âge (F42 ROADMAP)

**Problème** : `age_group` sur le contenu et `preferred_difficulty` sur l'utilisateur
sont deux axes orthogonaux traités comme un seul. Aucune colonne `age_group` sur `users`.

**Phase 1** — effort S :
- Migration : colonne `age_group VARCHAR(10) NULLABLE` sur `users`
- Backfill conditionnel (pas universel) :
  ```sql
  UPDATE users SET age_group = CASE
    WHEN grade_system = 'suisse' THEN NULL  -- système différent, traitement différé
    WHEN grade_level BETWEEN 1 AND 3 THEN '6-8'
    WHEN grade_level BETWEEN 4 AND 6 THEN '9-11'
    WHEN grade_level BETWEEN 7 AND 9 THEN '12-14'
    WHEN grade_level >= 10 THEN '15+'       -- sans borne haute
    ELSE NULL
  END WHERE age_group IS NULL;
  ```
  → UPDATE batché (ex: par tranches de 500) pour éviter lock table en prod multi-worker
- Formulaire profil : permettre de renseigner/corriger (notamment utilisateurs avec grade_level NULL)
- Envisager : collecter l'**année de naissance** à l'onboarding (plus fiable que grade_level)
- Audit schémas Pydantic `UserResponse`/`UserPublic` : ajouter `age_group: Optional[str]`

**Phase 2** — effort M (dépend de Phase 1) :
- Champ `difficulty_tier INTEGER` (1-12) sur `Exercise` et `LogicChallenge`
- Pattern double-lecture dans `build_recommendation_user_context` **imposé** :
  ```python
  age_group = user.age_group or _grade_to_age_group(user.grade_level)  # fallback
  ```
  Zéro régression pour les utilisateurs avec `age_group = NULL` après backfill partiel.

**Libellés espace (neutres, sans référence de franchise)** :
- Groupes : Explorateurs 6-8 / Navigateurs 9-11 / Pilotes 12-14 / Étoiles 15+ ¹
- Niveaux : Découverte / Apprentissage / Consolidation (remplace easy/medium/hard côté UX)
- ⚠️ **RGPD/mineurs** : ces libellés révèlent indirectement l'âge de l'enfant.
  Réservés au **dashboard parent/enseignant** (couche payante), jamais au classement public.
  Dans le classement public : conserver les rangs de progression existants uniquement.

¹ "Commandants" écarté — connotation militaire signalée par Gemini. "Étoiles" retenu.

**Prérequis** : F42 n'est PAS prérequis de F40. F42 Phase 1 est prérequis de F40-v2
(rang filtré par groupe d'âge), pas de F40 (rang global).

### Séquence L3 (corrigée après débat 25/03/2026)

```
L2    → livré ✅ commit 4a74e52
L3-A  → livré ✅ commit f04853a   (F40, GET /api/users/me/rank + pied de page)
L3-B  → livré ✅ commit f5e793f   (F41, period=week|month|all sur leaderboard + me/rank)
F42 Phase 1 → livré ✅ commit 5b22a06 + 35efd13 (age_group users, backfill, profil, API)
F42 Phase 2 → livré ✅ migration `20260327_content_difficulty_tier` + reco + persistance contenus
```

**Notes techniques F42 Phase 1 (review 2026-03-26) :**

- **P2 — age_group dans le JWT** : valeur brute `"9-11"` incluse dans le payload du token
  d'accès (décodable base64 côté client). Même exposition que `grade_level` déjà présent →
  pas une régression, mais décision consciente. À documenter si un audit RGPD est demandé.
  *Décision : acceptable pour le confort UX (évite un appel API supplémentaire). À revisiter
  si la politique de données évolue.*

- **P3 — Migration non batchée** : le `UPDATE users SET ... WHERE age_group IS NULL` est un
  seul statement sans LIMIT/OFFSET. Acceptable pour la base actuelle (<10k users). Pour toute
  future migration de masse sur `users`, utiliser des tranches de 500 comme prévu dans le plan
  initial (cf. §L3-C Phase 1 ci-dessus).

**Corrections post-débat :**
- F42 N'EST PAS prérequis de F40 — la dépendance déclarée était fausse
- F41 n'est pas techniquement bloqué : `apply_points` est branché, index existe
  → CLAUDE.md P1 "apply_points non appelé pour exercices standard" est **obsolète**
- Libellés espace réservés au dashboard parent (RGPD mineurs) — pas dans le classement public
- "Étoiles" remplace "Commandants" pour le groupe 15+

---

## 9. Séquence de pilotage

```
L1 ✅ → /octo:review ✅ → commit
L2    → /octo:review    → commit
L3-A  → /octo:review    → commit  (après L2)
L3-B  → /octo:review    → commit  (après gamification P1 fixée)
```

Règle : L2 commence seulement après GO sur L1.

---

## 10. Critère de succès

- Bug UX Select : impossible à reproduire après L1 ✅
- Filtre age_group supprimé : API et frontend cohérents ✅
- avatar_url, current_streak, badges_count visibles dans le leaderboard après L1 ✅
- Podium top 3 visuellement distinct après L2
- Rang Jedi coloré de façon cohérente avec le reste de l'app
- Aucune régression sur le widget LeaderboardWidget du dashboard
- Tests causaux verts sur chaque lot
- (L3-A) Utilisateur #127 voit sa position en bas de liste
- (L3-B) Filtre "champion de la semaine" fonctionnel
