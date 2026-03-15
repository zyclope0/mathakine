# Plan de stabilisation pré-backlog — Backend & Frontend

**Date :** 06/03/2026  
**Type :** Plan d'implémentation guidé  
**Statut :** Actif

---

## 1. Objectif

Ce document décrit **comment assainir la base technique avant d'empiler de nouvelles fonctionnalités**.

Il est volontairement :

- **très guidé**
- **découpé en petites itérations**
- **orienté faible régression**
- **adapté à une exécution par un modèle moins puissant**

Le but n'est pas de "refactorer pour refactorer", mais de **sécuriser la suite du backlog** sur 5 axes :

1. **Transactions backend** plus fiables
2. **Frontière handler -> service** plus nette
3. **Frontend design system / thèmes** plus homogène
4. **Patterns React / lint** plus propres
5. **Contrats de services** plus robustes

---

## 2. Sources de vérité à consulter avant chaque itération

Toujours relire les documents suivants avant de commencer un lot :

1. [`AUDIT_ARCHITECTURE_BACKEND_2026-03.md`](./AUDIT_ARCHITECTURE_BACKEND_2026-03.md)
2. [`AUDIT_FRONTEND_INDUSTRIALISATION_2026-03.md`](./AUDIT_FRONTEND_INDUSTRIALISATION_2026-03.md)
3. [`ANALYSE_DUPLICATION_DRY_2026-02.md`](./ANALYSE_DUPLICATION_DRY_2026-02.md)
4. [`PLAN_CLEAN_CODE_ET_DTO_2026-02.md`](./PLAN_CLEAN_CODE_ET_DTO_2026-02.md)
5. [`REFACTOR_STATUS_2026-02.md`](./REFACTOR_STATUS_2026-02.md)

Ces documents servent à éviter deux erreurs :

- retravailler un sujet déjà corrigé
- casser une convention déjà définie

---

## 3. Règles d'exécution obligatoires

### 3.1 Règles de scope

- **Une seule préoccupation par itération**
- **Pas de feature en parallèle**
- **Pas de refactor backend + frontend dans le même commit**
- **Pas de renommage massif si le lot ne le justifie pas**
- **Pas de "clean up opportuniste" hors périmètre**

### 3.2 Règles anti-régression

- modifier le **minimum de fichiers nécessaire**
- ne pas changer la logique métier en même temps que la structure
- préserver les signatures publiques tant que possible
- introduire des wrappers de compatibilité si une extraction est risquée
- privilégier les changements **revertables**

### 3.3 Règles de validation

Pour chaque lot :

1. `npm run format:check` si le frontend est touché
2. `npm run lint` si le frontend est touché
3. `npm run build` si le frontend est touché
4. `pytest` ciblé sur la zone backend touchée
5. `pytest` global si la zone backend est transversale

### 3.4 Règles de commit

- 1 commit = 1 lot cohérent
- message de commit orienté intention
- ne pas mélanger "style", "refactor", "fix" et "feature" dans le même commit

Exemples :

- `refactor(backend): centralize request transaction ownership`
- `refactor(frontend): replace hardcoded dashboard surfaces with semantic tokens`
- `fix(frontend): remove set-state-in-effect anti-patterns from shared components`

---

## 4. Méthode standard pour un modèle moins puissant

À répéter **à l'identique** pour chaque mini-itération.

### Étape A — Comprendre le périmètre

1. Lire le document courant
2. Lire l'audit concerné
3. Lire uniquement les fichiers ciblés
4. Écrire une todo-list courte

### Étape B — Inspecter avant de modifier

Utiliser systématiquement des recherches ciblées :

#### Backend

```powershell
rg "commit\(" app server
rg "rollback\(" app server
rg "^async def " server/handlers
rg "Dict\[str, Any\]|\(result, error, status\)" app/services
```

#### Frontend

```powershell
rg "border-white/10|bg-white/5|bg-slate|dark:bg-slate|text-white/|shadow-\[" frontend/components
rg "eslint-disable-next-line react-hooks/set-state-in-effect" frontend
rg "Loader2|animate-spin" frontend/components
```

### Étape C — Modifier

- faire un diff **petit**
- conserver les comportements
- préférer l'extraction à la réécriture
- ajouter des commentaires uniquement si nécessaire

### Étape D — Vérifier

Exemples de séquence :

```powershell
cd frontend
npm run format:check
npm run lint
npm run build
```

```powershell
pytest tests/unit/test_auth_service.py
pytest tests/unit/test_user_service.py
pytest
```

### Étape E — Stop ou continuer ?

Continuer uniquement si :

- tests verts
- diff relisible
- pas de changement inattendu
- pas d'élargissement de scope

Sinon :

- corriger immédiatement
- ou arrêter et ouvrir le lot suivant plus tard

---

## 5. Priorisation recommandée avant backlog

### À faire avant de nouvelles implémentations

1. **F1 — Frontend design-system / thématisation résiduelle**

### À faire ensuite si temps disponible

- **F2 — Nettoyage des anti-patterns React restants** — ✅ traité sur le périmètre ciblé du plan
- **B3 — Contrats de services typés**

### À ne faire que si le backlog touche cette zone

- **B4 — Refactor profond de `server/exercise_generator.py`**

---

## 6. Workstream B1 — Transactions backend

### 6.1 Pourquoi ce chantier est prioritaire

Aujourd'hui, plusieurs handlers et services peuvent encore appeler `commit()` à des niveaux différents.

Conséquences :

- risque de persistance partielle
- rollback incomplet en cas d'échec tardif
- side effects externes déclenchés après un état DB déjà validé
- difficulté à raisonner sur l'atomicité d'une requête

### 6.2 État cible

**Règle cible :**

- le **point d'orchestration** d'une requête mutante est l'unique propriétaire du `commit/rollback`
- les services feuilles modifient l'objet session mais **ne commit pas**
- les handlers HTTP ne contiennent pas de logique transactionnelle métier complexe

### 6.3 Fichiers à inspecter en priorité

- `server/handlers/exercise_handlers.py`
- `server/handlers/challenge_handlers.py`
- `server/handlers/daily_challenge_handlers.py`
- `app/services/streak_service.py`
- `app/services/badge_service.py`
- `app/services/auth_service.py`
- `app/services/admin_user_service.py`
- `app/services/admin_content_service.py`

### 6.4 Sous-itérations recommandées

#### B1.1 — Inventaire des `commit()`

**Objectif** : établir la liste réelle des commits.

**Commande** :

```powershell
rg "commit\(" app server
```

**Livrable** :

- tableau `fichier -> fonction -> raison du commit`

**DoD** :

- tous les sites `commit()` et `rollback()` identifiés

#### B1.2 — Choisir le propriétaire de transaction par flux

**Flux prioritaires** :

1. tentative d'exercice
2. tentative de défi
3. auth / refresh
4. profil utilisateur
5. daily challenges

**Décision à prendre par flux** :

- handler propriétaire ?
- service d'orchestration propriétaire ?

**Recommandation** :

- préférer **service d'orchestration**
- interdire les commits dans les helpers appelés par plusieurs flux

#### B1.3 — Refactor d'un seul flux à la fois

**Ordre conseillé** :

1. `daily_challenge`
2. `auth`
3. `profile`
4. `exercise attempt`
5. `challenge attempt`

**Règle** :

- ne pas faire plusieurs flux dans le même commit

### 6.5 Critères d'acceptation

- un seul point de commit par requête mutante dans le lot traité
- aucun helper partagé ne commit
- tests unitaires verts
- tests d'intégration du flux vert

### 6.6 Risque / effort

- **Effort :** moyen
- **Risque :** moyen à élevé

### 6.7 Recommandation d'exécution

À faire **avant backlog**.

### 6.8 État après exécution B1

**Statut :** flux critiques clarifiés et vérifiés.

**Flux traités :**

- `daily_challenge` : `app/services/daily_challenge_service.py` porte le commit unique du flux `GET /api/daily-challenges`
- `auth / register` : `app/services/auth_service.py` centralise l'inscription via `create_registered_user_with_verification()`
- `auth / login` : `app/services/auth_service.py` centralise login + session via `authenticate_user_with_session()`
- `profile / sessions` : `server/handlers/user_handlers.py` délègue les mutations au service sans logique transactionnelle métier complexe côté HTTP
- `exercise attempt` : `app/services/exercise_service.py` reste propriétaire du commit final, avec side effects best effort via savepoints et `auto_commit=False`
- `challenge attempt` : `app/services/logic_challenge_service.py` reste propriétaire du commit final, avec la même convention

**Tests exécutés :**

- `tests/unit/test_daily_challenge_service.py`
- `tests/unit/test_auth_service.py`
- `tests/unit/test_exercise_service.py`
- `tests/unit/test_logic_challenge_service.py`
- `tests/api/test_daily_challenge_endpoints.py`
- `tests/api/test_auth_flow.py`
- `tests/api/test_user_endpoints.py`
- `tests/api/test_exercise_endpoints.py`
- `tests/integration/test_user_exercise_flow.py`
- `tests/api/test_progress_endpoints.py`
- `tests/api/test_challenge_endpoints.py`

**Résultat :** `163` tests ciblés B1 passés.

**Réserve volontaire :**

- des `commit()` restent dans des zones adjacentes non prioritaires pour le backlog immédiat (`admin_*`, `feedback`, `analytics`, `enhanced_server_adapter`, `challenge_service` legacy)
- `badge_service` et `streak_service` conservent des chemins `auto_commit=True` pour usages standalone, mais les flux critiques composés passent désormais par `auto_commit=False`

---

## 7. Workstream B2 — Handler -> service boundary

### 7.1 Objectif

Faire des handlers HTTP de vrais adaptateurs :

- parse request
- validation transport
- appel service
- format response

Et rien de plus.

### 7.2 Symptômes à traiter

- logique métier dans les handlers
- side effects déclenchés côté route
- normalisation et composition de payloads dispersées

### 7.3 Fichiers prioritaires

- `server/handlers/exercise_handlers.py`
- `server/handlers/challenge_handlers.py`
- `server/handlers/user_handlers.py`
- `server/handlers/auth_handlers.py`

### 7.4 Sous-itérations recommandées

#### B2.1 — Auth

Extraire/clarifier :

- composition cookie/token
- règles de refresh
- logique de login

**Cibles** :

- `api_login()`
- `api_refresh_token()`

#### B2.2 — User / Profile

Extraire/clarifier :

- normalisation profil
- update me
- validation métier non transport

**Cibles** :

- `create_user_account()`
- `update_user_me()`

#### B2.3 — Exercise flows

Extraire/clarifier :

- génération
- fallback
- orchestration diagnostic/adaptation

#### B2.4 — Challenge flows

Extraire/clarifier :

- soumission
- badges/streak side effects
- logique partagée réutilisable

### 7.5 DoD

- handlers plus courts
- aucune règle métier complexe inline
- logique testable sans HTTP
- mêmes réponses API qu'avant

### 7.6 Risque / effort

- **Effort :** moyen à moyen-haut
- **Risque :** moyen

### 7.7 Recommandation d'exécution

À faire **avant backlog** si les prochaines features touchent ces flux.

### 7.8 État après exécution B2

**Statut :** handlers critiques allégés sur `auth`, `user/profile`, `exercise`, `challenge`.

**Points réalisés :**

- `server/handlers/auth_handlers.py` : extraction de la composition réponse/cookies et clarification du fallback refresh
- `server/handlers/user_handlers.py` : normalisation profil et sérialisation utilisateur déplacées vers `app/services/user_service.py`
- `server/handlers/exercise_handlers.py` : validation de payload de soumission isolée dans un helper dédié
- `server/handlers/challenge_handlers.py` : normalisation de payload de soumission isolée dans un helper dédié

**Garde-fous :**

- mêmes endpoints et mêmes formats de réponse conservés
- logique de normalisation testable sans requête HTTP complète
- validations ciblées rejouées sur les suites `auth/user` puis `exercise/challenge`

---

## 8. Workstream F1 — Frontend design system et thèmes

### 8.1 Objectif

Finir l'industrialisation visuelle pour éviter que chaque nouvelle feature réintroduise :

- des couleurs hardcodées
- des surfaces ad hoc
- des ombres custom non sémantiques
- des composants qui dérivent du design system

### 8.2 État actuel

Une partie importante a déjà été traitée, et le dashboard principal a maintenant reçu un premier sweep cohérent.

**État constaté :**

- un socle de tokens visuels thème/spatial a été ajouté dans `frontend/app/globals.css`
- un premier sweep visuel est déjà engagé sur `frontend/components/dashboard/ProgressChart.tsx`, `frontend/components/dashboard/DailyExercisesChart.tsx`, `frontend/components/challenges/visualizations/GraphRenderer.tsx` et `frontend/components/challenges/visualizations/ChessRenderer.tsx`
- ces changements vont dans le bon sens (`border-border/50`, couleurs sémantiques `warning` / `success`, strokes SVG branchés sur les tokens)
- `F1.1` et `F1.2` sont maintenant traités sur les cartes dashboard et CTA interactives via des surfaces partagées (`dashboard-card-surface`, `dashboard-card-surface-interactive`, `dashboard-card-icon-chip`)
- le lot F1 reste néanmoins ouvert sur les générateurs et les renderers les plus personnalisés

**Dette encore visible sur les cibles F1 :**

- générateurs : `AIGeneratorBase` et `UnifiedExerciseGenerator` gardent encore des surfaces ad hoc et des `shadow-[...]` locaux
- solveurs / renderers : `ExerciseSolver` et surtout `CodingRenderer` gardent encore plusieurs hardcodes de couleurs (`bg-slate-*`, glow custom, verts hardcodés)
- `BadgeCard` garde encore un token local `bg-slate-300` pour la variante `silver`

### 8.3 Cibles prioritaires

- `frontend/components/dashboard/LeaderboardWidget.tsx`
- `frontend/components/dashboard/StatsCard.tsx`
- `frontend/components/dashboard/QuickStartActions.tsx`
- `frontend/components/dashboard/AverageTimeWidget.tsx`
- `frontend/components/dashboard/RecentActivity.tsx`
- `frontend/components/dashboard/CategoryAccuracyChart.tsx`
- `frontend/components/dashboard/LevelIndicator.tsx`
- `frontend/components/shared/AIGeneratorBase.tsx`
- `frontend/components/exercises/UnifiedExerciseGenerator.tsx`
- `frontend/components/exercises/ExerciseSolver.tsx`
- `frontend/components/challenges/visualizations/CodingRenderer.tsx`
- `frontend/components/badges/BadgeCard.tsx`

### 8.4 Règles de refactor visuel

Toujours appliquer dans cet ordre :

1. **tokens sémantiques existants**
2. **classe utilitaire existante**
3. **nouveau token global** si plusieurs composants partagent le besoin
4. **style custom local** uniquement si aucun token n'est adapté

### 8.5 Anti-patterns à supprimer

- `border-white/10`
- `bg-white/5`
- `bg-slate-*`
- `dark:bg-slate-*`
- `text-white/80`
- `shadow-[...]` dupliqués sans abstraction

### 8.6 Sous-itérations recommandées

#### F1.1 — Dashboard cards

**Cibles** :

- `LeaderboardWidget`
- `AverageTimeWidget`
- `RecentActivity`
- `CategoryAccuracyChart`
- `LevelIndicator`

**Objectif** :

- unifier surfaces, bordures et glow

#### F1.2 — CTA / cards interactives

**Cibles** :

- `QuickStartActions`
- `StatsCard`

**Objectif** :

- faire passer ces composants sur le même langage visuel que le reste du dashboard

#### F1.3 — Générateurs

**Cibles** :

- `AIGeneratorBase`
- `UnifiedExerciseGenerator`

**Objectif** :

- réduire les variations locales de card/surface/shadow

#### F1.4 — Renderers visuels

**Cibles** :

- `CodingRenderer`
- autres renderers encore en `bg-slate-*`

**Objectif** :

- thème cohérent, pas seulement "dark mode compatible"

### 8.7 DoD

- plus de hardcodes couleurs dans le lot traité
- rendu cohérent sur plusieurs thèmes
- `format`, `lint`, `build` verts

### 8.8 Risque / effort

- **Effort :** moyen
- **Risque :** faible à moyen

### 8.9 Recommandation d'exécution

À faire **avant backlog frontend significatif**.

### 8.10 État après revue F1

**Statut :** partiellement traité, non terminé.

**Lecture opérationnelle :**

- le socle thème/tokens progresse
- `F1.1` est traité sur `LeaderboardWidget`, `AverageTimeWidget`, `RecentActivity`, `CategoryAccuracyChart` et `LevelIndicator`
- `F1.2` est traité sur `QuickStartActions` et `StatsCard`
- `F1.3` et `F1.4` restent ouverts
- le chantier F1 n'est donc pas encore clôturé à l'échelle du plan

**Validation ciblée réalisée après `F1.1` / `F1.2` :**

- frontend : `eslint`, `tsc --noEmit`, `next build`
- résultat : vert sur le lot dashboard / CTA

**Priorité pratique recommandée :**

- enchaîner avec `F1.3` sur les générateurs
- garder `F1.4` pour la fin, avec `CodingRenderer` comme plus gros reliquat

---

## 9. Workstream F2 — Nettoyage des anti-patterns React

### 9.1 Objectif

Supprimer les `eslint-disable-next-line react-hooks/set-state-in-effect` restants quand une solution plus propre existe.

### 9.2 Cibles identifiées

- `frontend/components/auth/ProtectedRoute.tsx`
- `frontend/components/accessibility/AccessibilityToolbar.tsx`
- `frontend/components/challenges/visualizations/CodingRenderer.tsx`
- `frontend/components/challenges/visualizations/DeductionRenderer.tsx`
- `frontend/components/challenges/visualizations/ProbabilityRenderer.tsx`
- `frontend/components/challenges/visualizations/RiddleRenderer.tsx`
- `frontend/components/challenges/visualizations/GraphRenderer.tsx`
- `frontend/components/challenges/visualizations/ChessRenderer.tsx`
- `frontend/components/exercises/ExerciseModal.tsx`
- `frontend/components/pwa/InstallPrompt.tsx`
- `frontend/components/layout/AlphaBanner.tsx`
- `frontend/app/reset-password/page.tsx`
- `frontend/components/theme/DarkModeToggle.tsx`

**État constaté :**

- le sous-lot `F2.1` a été traité sur `DarkModeToggle`, `InstallPrompt`, `AlphaBanner` et `reset-password/page.tsx`
- le sous-lot `F2.2` a été traité sur `ProtectedRoute`, `AccessibilityToolbar` et `ExerciseModal`
- le sous-lot `F2.3` a été traité sur `CodingRenderer`, `DeductionRenderer`, `ProbabilityRenderer`, `RiddleRenderer`, `GraphRenderer` et `ChessRenderer`
- `0` fichier ciblé reste concerné
- `0` occurrence de `eslint-disable-next-line react-hooks/set-state-in-effect` reste présente sur ce périmètre

### 9.3 Stratégie de correction

Toujours préférer, dans cet ordre :

1. **initialiseur de state** (`useState(() => ...)`)
2. **valeur dérivée** (`useMemo`, calcul direct)
3. **guard `typeof window/document`**
4. **callback asynchrone / subscription**
5. **microtask ou workaround** seulement en dernier recours

### 9.4 Sous-itérations recommandées

#### F2.1 — Composants low risk

- `DarkModeToggle`
- `InstallPrompt`
- `AlphaBanner`
- `reset-password/page.tsx`

#### F2.2 — Composants shared medium risk

- `ProtectedRoute`
- `AccessibilityToolbar`
- `ExerciseModal`

#### F2.3 — Renderers

- `CodingRenderer`
- `DeductionRenderer`
- `ProbabilityRenderer`
- `RiddleRenderer`
- `GraphRenderer`
- `ChessRenderer`

### 9.5 DoD

- directive eslint supprimée ou justifiée explicitement
- pas de warning lint nouveau
- comportement identique

### 9.6 Risque / effort

- **Effort :** faible à moyen
- **Risque :** faible à moyen

### 9.7 Recommandation d'exécution

Très bon chantier **avant backlog**, car peu coûteux et rentable.

### 9.8 État après revue F2

**Statut :** traité sur le périmètre identifié.

**Lecture opérationnelle :**

- `F2.1` peut être considéré comme fait sur ce périmètre low risk
- `F2.2` peut être considéré comme fait sur ce périmètre shared medium risk
- `F2.3` peut être considéré comme fait sur le périmètre renderers listé dans ce plan
- le chantier `react-hooks/set-state-in-effect` est clos sur les cibles recensées ici
- le prochain chantier restant avant backlog est désormais `F1`

**Validation locale réalisée après clôture F2 :**

- backend : `flake8` (critique), `black --check`, `isort --check`, `mypy`, `pytest tests/ -m "not slow"`, smoke `/health`
- frontend : `tsc --noEmit`, `eslint`, `prettier --check`, `i18n:check`, `i18n:validate`, `vitest --run`, `next build`
- résultat : validation locale complète verte sur le périmètre actuel

---

## 10. Workstream B3 — Contrats de services typés

### 10.1 Objectif

Réduire les retours fragiles :

- `Dict[str, Any]`
- tuples `(result, error, status)`

### 10.2 Cibles prioritaires

- `app/services/auth_service.py`
- `app/services/user_service.py`
- `app/services/admin_user_service.py`
- `app/services/admin_content_service.py`
- `app/services/badge_service.py`
- `app/services/challenge_service.py`
- `app/services/diagnostic_service.py`
- `app/core/types.py`

### 10.3 Règle cible

Préférer :

- `TypedDict` si shape simple
- `dataclass` si état métier structuré
- `Result` explicite si succès/erreur

Exemple cible :

```python
class ServiceResult(TypedDict):
    ok: bool
    status: int
    error: str | None
```

### 10.4 Sous-itérations recommandées

1. `auth_service`
2. `user_service`
3. `admin_*`
4. `badge_service` / `challenge_service`

### 10.5 DoD

- moins de tuples opaques
- moins de `Dict[str, Any]`
- appels côté handlers plus lisibles

### 10.6 Risque / effort

- **Effort :** moyen
- **Risque :** faible à moyen

### 10.7 Recommandation d'exécution

Important, mais **peut attendre** après les workstreams B1/B2/F1/F2.

---

## 11. Workstream B4 — Refactor profond de `server/exercise_generator.py`

### 11.1 Important

Ce chantier est **conditionnel**.

Ne pas le lancer par principe. Le lancer seulement si le backlog à venir touche :

- génération d'exercices
- adaptation dynamique
- fallback IA
- diagnostic initial

### 11.2 Pourquoi il est à part

- gros fichier central
- beaucoup de branches
- zone à forte sensibilité métier
- fort risque de régression

### 11.3 Approche recommandée

#### B4.1 — Caractérisation

- écrire/renforcer les tests de comportement avant extraction

#### B4.2 — Registry / strategy

- extraire la logique par type d'exercice
- introduire un registry explicite

#### B4.3 — Orchestrateur léger

- garder `exercise_generator.py` comme façade transitoire

### 11.4 DoD

- moins de branching central
- génération testable par type
- même comportement public

### 11.5 Risque / effort

- **Effort :** élevé
- **Risque :** élevé

### 11.6 Recommandation d'exécution

**Ne pas faire avant backlog** sauf si le backlog dépend directement de cette zone.

---

## 12. Ordre recommandé d'exécution

**État courant :** `B1`, `B2`, `F2`, `F1.1` et `F1.2` sont traités. Le chemin restant le plus logique avant backlog est maintenant :

1. finir `F1` (`F1.3` puis `F1.4`)
2. validation locale complète (`format`, `lint`, `build`, `pytest`)
3. backlog

### Option A — Plan minimal avant backlog

1. finir `F1` — générateurs puis renderers visuels
2. validation locale complète
3. backlog

### Option B — Plan robuste avant backlog

1. finir `F1`
2. validation locale complète
3. `B3`
4. backlog

### Option C — Plan complet si backlog génération

1. finir `F1`
2. validation locale complète
3. `B3`
4. `B4`
5. backlog

---

## 13. Découpage conseillé en petites PR / petits commits

### Frontend recommandé

1. `fix(frontend): remove low-risk set-state-in-effect usages`
2. `refactor(frontend): unify dashboard surfaces and borders with theme tokens`
3. `refactor(frontend): align generators with design-system surfaces`
4. `refactor(frontend): remove remaining renderer color hardcodes`

### Backend recommandé

1. `refactor(backend): inventory and centralize transaction ownership for auth flows`
2. `refactor(backend): move profile mutation orchestration into services`
3. `refactor(backend): centralize transaction ownership for daily challenges`
4. `refactor(backend): slim exercise handlers and extract orchestration service`
5. `refactor(backend): slim challenge handlers and extract orchestration service`
6. `refactor(backend): replace tuple service contracts with typed results`

---

## 14. Checklist de fin de lot

À copier-coller avant chaque clôture d'itération :

```markdown
- [ ] Scope respecté
- [ ] Pas de feature ajoutée
- [ ] Diff relisible
- [ ] format frontend OK
- [ ] lint frontend OK
- [ ] build frontend OK
- [ ] tests backend ciblés OK
- [ ] tests backend globaux si nécessaire OK
- [ ] aucun changement inattendu dans des fichiers hors scope
- [ ] commit unique et cohérent
```

---

## 15. Checklist avant démarrage backlog

Le backlog peut commencer quand les conditions minimales suivantes sont vraies :

- [x] transactions backend clarifiées sur les flux critiques
- [x] handlers critiques allégés
- [ ] composants frontend structurants cohérents avec le design system
- [x] anti-patterns React les plus visibles nettoyés
- [x] CI locale verte (`format`, `lint`, `build`, `pytest`)

---

## 16. Résumé exécutable

Si un modèle moins puissant doit exécuter ce plan, lui donner **une seule instruction à la fois** :

1. lire ce document
2. choisir **un seul** sous-lot
3. lire uniquement les fichiers indiqués
4. modifier le minimum
5. lancer les validations
6. s'arrêter et reporter

**Ne jamais lui demander de faire "le plan complet" d'un seul coup.**

---

## Références

- [`AUDIT_ARCHITECTURE_BACKEND_2026-03.md`](./AUDIT_ARCHITECTURE_BACKEND_2026-03.md)
- [`AUDIT_FRONTEND_INDUSTRIALISATION_2026-03.md`](./AUDIT_FRONTEND_INDUSTRIALISATION_2026-03.md)
- [`ANALYSE_DUPLICATION_DRY_2026-02.md`](./ANALYSE_DUPLICATION_DRY_2026-02.md)
- [`PLAN_CLEAN_CODE_ET_DTO_2026-02.md`](./PLAN_CLEAN_CODE_ET_DTO_2026-02.md)
- [`REFACTOR_STATUS_2026-02.md`](./REFACTOR_STATUS_2026-02.md)
