# Workflow utilisateur & Éducation — Vue d'ensemble et refactoring

> **Objectif** : Contexte global du parcours utilisateur et de la partie éducation, pour guider les refactorings tout en gardant la cohérence.
> **Date** : Février 2026

---

## 1. Vue d'ensemble du parcours actuel

### 1.1 Flux utilisateur (schéma)

```
Accueil (/) 
    │
    ├── Non connecté → Register → Auto-login → Onboarding (si nouveau) → Dashboard
    │                     └── Verify email (optionnel, bandeau si non fait)
    │
    └── Connecté 
            │
            ├── /dashboard (4 onglets : Vue d'ensemble, Recommandations, Progression, Détails)
            │       ├── Recommandations → lien vers /exercises/[id] ou /challenge/[id]
            │       └── Stats, Streak, Classement, Graphiques
            │
            ├── /exercises (liste paginée, filtres, ordre random, masquer réussis)
            │       └── Clic carte → ExerciseSolver ou modal
            │
            ├── /challenges (idem structure)
            │       └── Clic carte → ChallengeModal → ChallengeSolver
            │
            ├── /badges (En cours / À débloquer)
            ├── /leaderboard (classement, filtre âge)
            ├── /profile
            └── /settings
```

### 1.2 Composants clés

| Domaine | Hooks / Services | Pages |
|---------|------------------|-------|
| Auth | `useAuth` | login, register, verify-email, forgot-password, reset-password |
| Stats | `useUserStats`, `useProgressStats`, `useChallengesProgress` | dashboard |
| Recommandations | `useRecommendations` (generate, complete) | dashboard (onglet) |
| Exercices | `useExercises`, `useCompletedExercises` | exercises |
| Défis | `useChallenges`, `useCompletedChallenges` | challenges |
| Badges | `useBadgesProgress` | badges |
| Contenu | `usePaginatedContent` (DRY) | exercises, challenges |

---

## 2. Points d'amélioration identifiés

### 2.1 Workflow utilisateur

| Amélioration | Complexité | Impact | Priorité |
|--------------|------------|--------|----------|
| **Onboarding premier login** (inclut Quick Win #1 « First Exercise \< 90s ») | Moyenne | Élevé | P0 |
| **Parcours guidé** (Dashboard → Exercice/Défi en 1 clic) | Faible | Moyen | P1 |
| **Recommandations cliquables** | — | — | ✅ Déjà fait (lien exercice/défi) |
| **Breadcrumb / contexte** ("Tu es ici") | Faible | Moyen | P2 |
| **Retour après résolution** (retour intelligent au dashboard ou liste) | Moyenne | Moyen | P1 |
| **Dashboard parent** (vue distincte) | Élevée | Élevé | P2 (roadmap) |

### 2.2 Partie éducation

**Manque de personnalisation initiale à l'inscription**

Le formulaire d'inscription collecte seulement l'identité de compte (username, email, password, full_name) sans calibration pédagogique (classe, niveau, difficulté cible, rythme). Sans diagnostic ou préférences éducatives dès l'entrée, l'adaptation démarre tard et affaiblit la promesse « adaptive learning » au moment critique des premières 5 minutes. Impact : premières sessions moins pertinentes, engagement précoce plus fragile. (Complémentaire au test diagnostic initial et à l’adaptation difficulté ci-dessous.)

| Amélioration | Complexité | Impact | Priorité |
|--------------|------------|--------|----------|
| **Calibration pédagogique à l'inscription** (classe, niveau, difficulté, rythme) | Moyenne | Élevé | P1 |
| **Révisions espacées** (spaced repetition) | Élevée | Élevé | P2 |
| **Test diagnostic initial** | Élevée | Élevé | P2 |
| **Défis quotidiens** (objectif du jour) | Moyenne | Élevé | P1 |
| **Objectifs personnalisés** (ex: "3 exercices/jour") | Moyenne | Moyen | P2 |
| **Feedback pédagogique enrichi** (explication des erreurs) | Moyenne | Moyen | P1 |
| **Adaptation difficulté** (basée sur succès/échecs) | Élevée | Élevé | P2 |

### 2.3 Audit activation (EdTech 2026)

**Constat — Vérification email = goulot d'activation**

Après inscription, l'utilisateur est redirigé vers le login avec `verify=true`, et le login échoue en 403 tant que l'email n'est pas validé. Le renvoi d'email existe, mais survient après un échec (ou action explicite), pas comme flux principal guidé.

**Risque UX** : Sur les produits éducatifs grand public, chaque étape asynchrone avant le 1er exercice augmente fortement l'abandon (surtout mobile + parents/enfants). Impact : baisse du taux « inscription → premier exercice ».

| Solution | Priorité | KPI cible |
|---------|----------|-----------|
| **Quick Win #1 — "First Exercise in \< 90s"** : court-circuiter la friction email pour la première session (session limitée tant que non vérifié, ou parcours invité pédagogique), puis nudges de vérification ensuite. | **P0** | +20 à +35 % sur « signup → 1er exercice » |
| **Quick Win #2 — Onboarding pédagogique en 3 écrans max** : mini-diagnostic initial (niveau perçu, classe/âge, objectif, préférence difficulté) avant d'ouvrir le dashboard. Le reste sur le profil. | **P0** | +15 % rétention J1, baisse du drop après session 1 |

En EdTech 2026, la métrique clé d'activation est l'accès à la valeur pédagogique immédiate.

#### Quick Win #2 — Détail

- **Action** : Ajouter mini-diagnostic initial (niveau perçu, classe/âge, objectif, préférence de difficulté) avant d'ouvrir le dashboard. Le reste sur le profil.
- **Pourquoi** : Améliore instantanément la pertinence des premières recommandations et réduit la sensation « générique ».
- **KPI cible** : +15 % rétention J1, baisse du drop après session 1.

#### Évaluation de complexité et 3 axes possibles

| Axe | Approche | Complexité | Effort | Risques / contraintes |
|-----|----------|------------|--------|------------------------|
| **Axe 1 — Auto-login limité** | Après inscription, connexion automatique avec session « non vérifiée ». Accès exercices/défis immédiat. Bandeau « Vérifiez votre email » pour débloquer dashboard complet, export, badges. | Moyenne | 3–5 j | Gestion des restrictions par route ; risque de comptes spam (rate limit existant). |
| **Axe 2 — Parcours invité (sans compte)** | Bouton « Essayer sans compte » : 1–3 exercices en mode démo (sans sauvegarde) ou avec session anonyme. CTA « Créez un compte pour sauvegarder ». | Élevée | 1–2 sem | `submit_answer` exige `user_id` ; refonte partielle du flux, migration des données invité → compte. |
| **Axe 3 — Token post-inscription** | Après register, retour d’un token à usage unique (ex. 15 min). Redirection directe vers `/exercises?token=xxx`. Échange token → session limitée. | Moyenne | 3–5 j | Nouveau flux token, endpoint dédié ou modification de la réponse register. |

**Détail par axe :**

- **Axe 1** : Lever le 403 au login pour les utilisateurs non vérifiés ; ajouter un claim `email_verified` dans le JWT ; adapter les handlers (ex. `require_auth`) pour restreindre certains accès ; bandeau frontend ; redirection post-register vers `/exercises` au lieu de `/verify-email`.
- **Axe 2** : Mode invité = `user_id` nullable ou session anonyme ; `ExerciseResult` optionnel ou stockage temporaire ; fusion des données à la création de compte.
- **Axe 3** : Endpoint `POST /api/auth/activate-session` (token → cookies) ou extension de la réponse register ; frontend lit le token et appelle l’API ; même logique de session limitée qu’axe 1.

**Recommandation** : Axe 1 ou 3 — impact rapide, surface de changement maîtrisée. L’axe 2 est plus lourd et mieux adapté à une évolution produit distincte (mode démo public).

### 2.4 Refactorings techniques (sans changer UX)

| Amélioration | Complexité | Impact |
|--------------|------------|--------|
| **DRY exercices/challenges** (ContentCardBase, usePaginatedContent) | Partiel déjà fait | Bonne base |
| **Centraliser la logique "completed"** (useCompletedItems) | Faible | Déjà en place |
| **Unifier les filtres** (exercises/challenges) en composant réutilisable | Faible | Lisibilité |
| **handleRefresh dashboard** (invalidation complète) | Faible | Corrigé |

---

## 3. Plan d'action — S'approcher des axes

### 3.1 État actuel

| Axe / Quick Win | Statut | Note |
|-----------------|--------|------|
| **Quick Win #1** (First Exercise < 90s) | ✅ Fait | Auto-login, période de grâce 45 min, bandeau, restrictions |
| **Quick Win #2** (Onboarding pédagogique 3 écrans) | ✅ Fait | Page `/onboarding`, champs BDD, redirections, système suisse/unifié |
| **Calibration à l'inscription** | ✅ Fait | Intégrée dans l'onboarding (classe, âge, objectif, rythme, grade_system) |
| **Profil/paramètres pour non vérifiés** | ✅ Fait | Accès sans `requireFullAccess` pour modifier email, renvoyer lien |
| **Parcours guidé** (Dashboard → 1 clic) | ✅ Fait | Bloc QuickStartActions en tête overview |
| **Recommandations personnalisées** | ✅ Fait | Utilise onboarding/profil : age_group, grade_level, learning_goal |
| **Axe 2** (Parcours invité) | 🔲 Optionnel | Élevée, roadmap distincte |

### 3.2 Prochaines étapes recommandées

1. ~~**Quick Win #2 — Onboarding pédagogique**~~ ✅ Fait (alpha.3)
   - Route `/onboarding` avec sélecteur système scolaire (suisse 1H-11H / unifié 1-12), classe, groupe d'âge, objectif, rythme
   - Champs BDD : `onboarding_completed_at`, `learning_goal`, `practice_rhythm`, `grade_system`
   - Redirection post-login vers `/onboarding` si `onboarding_completed_at` null, sinon dashboard/exercises
   - Dashboard protégé : redirection vers onboarding si non complété

2. ~~**Parcours guidé**~~ ✅ Fait
   - Bloc "Que veux-tu faire ?" en tête de l'onglet Vue d'ensemble
   - 2 CTA : Un exercice / Un défi — liens guidés vers reco si dispo, fallback /exercises et /challenges
   - Priorisation : priority desc ; data-attrs pour instrumentation (CTR, temps vers 1er attempt)

3. ~~**Redirection post-login/register**~~ ✅ Fait
   - Après login : si `onboarding_completed_at` null → `/onboarding` puis `/dashboard` ; sinon → `/exercises` ou cible post-inscription
   - Profil et paramètres accessibles aux non vérifiés (pour renvoyer lien de vérification)

### 3.3 Données existantes / ajoutées

Le modèle `User` expose : `grade_level`, `grade_system` (suisse/unifié), `preferred_difficulty`, `learning_style`, `learning_goal`, `practice_rhythm`, `onboarding_completed_at`.

---

## 4. Complexité estimée par type

- **Faible** : 1–2 jours, peu de risque de régression
- **Moyenne** : 3–5 jours, tests + documentation
- **Élevée** : 1–2 semaines, changement de modèle ou nouveau flux

---

## 5. Principes pour les implémentations

1. **Garder le contexte** : Toute modification dans exercises, challenges, dashboard ou recommendations doit considérer le flux complet (accueil → contenu → retour).
2. **Éviter les silos** : Les hooks (useRecommendations, useExercises, etc.) partagent des queryKey React Query ; penser à l'invalidation croisée.
3. **Respecter les personas** : Lucas 8 ans (TDAH), Emma 14 ans (dyscalculie), Marine parent — cf. GUIDE_UTILISATEUR_MVP.md.
4. **Accessibilité** : Mode Focus, reduced motion, contraste — déjà en place via useAccessibleAnimation.
5. **i18n** : Toujours passer par les clés `messages/fr.json` et `en.json`.

---

## 6. Références

- [GUIDE_UTILISATEUR_MVP.md](../01-GUIDES/GUIDE_UTILISATEUR_MVP.md) — Cible, personas, parcours
- [SITUATION_FEATURES.md](SITUATION_FEATURES.md) — État des fonctionnalités
- [ROADMAP_FONCTIONNALITES.md](ROADMAP_FONCTIONNALITES.md) — Priorités produit
- [AUDIT_DASHBOARD_2026-02.md](../03-PROJECT/AUDIT_DASHBOARD_2026-02.md) — Corrections restantes dashboard
- [06-WIDGETS/](../06-WIDGETS/) — Design system widgets
