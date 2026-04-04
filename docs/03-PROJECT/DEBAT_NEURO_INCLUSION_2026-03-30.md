# Débat — Neuro-inclusion & EdTech Readiness

> Généré le 2026-03-30 via `/octo:debate` (4 providers)
> Motion : Adopter le plan de refonte Neuro-inclusion tel que proposé

---

## Contexte

Le plan soumis au débat proposait 3 actions strictes pour éradiquer le design "Default B2B SaaS / Vercel-Core" :

1. Modifier `:root` dans `globals.css` (fond slate-50, card 96.1%)
2. Aplatir les cartes (retirer border + shadow, passer à rounded-3xl)
3. Créer un layout tubulaire sur le dashboard (max-w-2xl colonne unique)

---

## Positions des 4 providers

### 🔴 Codex — Implémentation Technique

**3 erreurs techniques bloquantes identifiées :**

- Action 1 : Modifier `:root` brise la cascade multi-thème. Le thème Spatial a déjà `--background: #0a0a0f` dans `[data-theme="spatial"]`. Modifier `:root` en slate-50 propage un fond clair sur tous les thèmes qui n'overrident pas.
- Action 2 : `card.tsx` a déjà `border-0`. La shadow est `shadow-[var(--shadow-card)]` (token CSS), pas une classe Tailwind hardcodée. La "retirer" globalement casse 126 composants.
- Action 3 : Dashboard Tabs + 16 widgets → layout max-w-2xl = scroll infini et perte de densité utile pour les adultes.

### 🟡 Gemini — Accessibilité & Standards EdTech

**Les guardrails sont scientifiquement incomplets :**

- "Zéro Blanc Pur" n'est pas une norme WCAG — c'est une préférence de confort. La variabilité inter-individuelle TSA/TDAH est extrême.
- "Zéro délimitation visuelle" peut créer une "soupe visuelle" anxiogène pour les profils TSA qui s'appuient sur les zones fonctionnelles pour s'orienter.
- La Conception Universelle pour l'Apprentissage (UDL) recommande plusieurs représentations, pas une représentation unique imposée.

### 🟢 Sonnet — Recherche UX & Design

**Bonne direction, mauvais niveau d'abstraction :**

- Le plan agit sur le design system global alors qu'il devrait créer une couche de présentation dédiée au flux apprenant.
- Il existe déjà un mode TSA/TDAH dans `globals.css` — le plan l'ignore.
- Solution : `LearnerCard` + `LearnerLayout` spécifiques aux pages exercice/défi. Coût : 2h. Risque : zéro régression sur l'existant.

### 🔵 Claude/Opus — Synthèse & Arbitrage

**La tension réelle : global vs ciblé.**

- Le diagnostic est correct (manque de couche design apprenant).
- La solution globale est incorrecte (effets de bord sur 126 composants).
- Solution correcte : composants dédiés au rôle apprenant, tokens `--bg-learner` par thème, intégration ciblée dans ExerciseSolver et ChallengeSolver.

---

## Verdict

### Sur les 3 actions proposées

| Action                                             | Verdict                 | Motif                                                                |
| -------------------------------------------------- | ----------------------- | -------------------------------------------------------------------- |
| Action 1 : Modifier `:root` globals.css            | ❌ REJETÉ               | Brise la cascade multi-thème (7 thèmes)                              |
| Action 2 : Retirer shadow de card.tsx global       | ⚠️ PARTIELLEMENT ADOPTÉ | `border-0` déjà en place ; shadow → opt-in via prop `flat?` sur Card |
| Action 3 : Layout tubulaire sur dashboard existant | ❌ REJETÉ               | Dashboard = outil adulte/parent ; créer une page apprenant séparée   |

### Sur les objectifs de la mission

| Objectif                                      | Verdict     | Action correcte                                            |
| --------------------------------------------- | ----------- | ---------------------------------------------------------- |
| Anti "IA-look" / design trop générique        | ✅ LÉGITIME | `LearnerCard` avec shadow nulle et radius organique        |
| Zéro fond blanc éblouissant                   | ✅ LÉGITIME | Token `--bg-learner` légèrement teinté par thème           |
| Zéro layout surchargé pendant l'apprentissage | ✅ LÉGITIME | `LearnerLayout` max-w-2xl sur pages exercice/défi          |
| Mode focus apprenant                          | ✅ LÉGITIME | Extension du mode TSA/TDAH existant ou `FocusModeProvider` |

---

## Plan d'action — Neuro-inclusion EdTech (version correcte)

### NI-1 — Composants apprenant dédiés

**Priorité** : P1 | **Effort** : S-M (1 jour)

- Créer `frontend/components/learner/LearnerCard.tsx`
  - Shadow nulle, radius 2xl, fond `--bg-learner`, padding généreux
  - Réutilise `Card` avec overrides ciblés
- Créer `frontend/components/learner/LearnerLayout.tsx`
  - `max-w-2xl` centré, `gap-12`, padding généreux
  - Zéro sidebar, flux de lecture unique

### NI-2 — Token `--bg-learner` par thème

**Priorité** : P1 | **Effort** : S (3h)

Ajouter dans `globals.css` pour chacun des 7 thèmes :

```css
[data-theme="spatial"] {
  --bg-learner: #0d0d18;
}
[data-theme="ocean"] {
  --bg-learner: #0e1829;
}
[data-theme="minimal"] {
  --bg-learner: #f5f5f5;
}
[data-theme="dune"] {
  --bg-learner: #fdf4e7;
}
[data-theme="forest"] {
  --bg-learner: #edfbf0;
}
[data-theme="peach"] {
  --bg-learner: #fff4ee;
}
[data-theme="dino"] {
  --bg-learner: #fefce4;
}
```

### NI-3 — Intégration dans ExerciseSolver + ChallengeSolver

**Priorité** : P1 | **Effort** : S (2h)

- Remplacer `<PageLayout>` par `<LearnerLayout>` dans les pages exercice et défi
- Remplacer les `<Card>` wrappant les questions par `<LearnerCard>`
- Zéro modification des composants globaux

### NI-4 — Page d'accueil apprenant tubulaire

**Priorité** : P2 | **Effort** : M (sprint dédié)

Créer une page `/home-learner` ou vue enfant dédiée avec :

- Actions rapides (Exercices, Défis, Badges)
- Streak + Niveau
- Layout `LearnerLayout`, fond `--bg-learner`, zéro colonne multiple

### NI-5 — Opt-in `flat` sur `<Card>`

**Priorité** : P2 | **Effort** : XS (1h)

```tsx
// Ajouter prop flat?: boolean à Card
// flat=true → shadow: none
// Opt-in progressif là où pertinent, défaut global inchangé
```

---

## Ce qui N'est PAS à faire

- Modifier `:root` dans `globals.css` → brise les 7 thèmes
- Passer `rounded-3xl` en défaut global sur `card.tsx` → affecte toutes les modales admin
- Refactoriser le dashboard principal en colonne unique → dégrade l'expérience adulte/parent
- Interdire toute délimitation visuelle → peut créer une désorientation pour certains profils TSA

---

## Récapitulatif des lots

| Lot                       | Priorité | Effort | Impact                                 |
| ------------------------- | -------- | ------ | -------------------------------------- |
| NI-1 Composants apprenant | P1       | S-M    | Couche design flux apprenant           |
| NI-2 Token --bg-learner   | P1       | S      | Fond teinté par thème                  |
| NI-3 Intégration Solver   | P1       | S      | Neuro-inclusion là où l'enfant apprend |
| NI-4 Page apprenant       | P2       | M      | Accueil tubulaire dédié                |
| NI-5 Opt-in flat Card     | P2       | XS     | Flexibilité design system              |

**Recommandation solo founder** : NI-1 + NI-2 + NI-3 en un seul sprint (1,5 jour).
Résultat : les pages exercice et défi deviennent neuro-inclusives sans rien casser.

---

## Critique design — Audit `/critique` (2026-03-30)

> Session de critique complète conduite après la session FFI-L7→L9.
> Périmètre : page d'accueil (`app/page.tsx`), dashboard (`app/dashboard/page.tsx`), solver exercice (`ExerciseSolver.tsx`).
> Score Nielsen : **25/40 — Acceptable**, améliorations significatives nécessaires.

### Diagnostic AI Slop — Verdict

L'interface présente **6 tells AI slop actifs** :

| Tell                                                                               | Localisation                                      | Gravité |
| ---------------------------------------------------------------------------------- | ------------------------------------------------- | ------- |
| Dark mode violet + fond `#0a0a0f` = palette AI 2024-2025                           | Thème spatial (défaut)                            | Élevée  |
| Glassmorphism systématique `bg-card/40 backdrop-blur-md`                           | 15+ composants                                    | Élevée  |
| Hero metric layout (grand nombre + icône + label ×5)                               | `AcademyStatsWidget`                              | Élevée  |
| Icône `rounded-full bg-primary/10` au-dessus de chaque titre                       | Page accueil (4 cartes), générateur IA, dashboard | Élevée  |
| Identical card grid (icon + title + desc ×4)                                       | Section features `app/page.tsx`                   | Moyenne |
| Sweep effect `::after`/`::before` global sur tous les boutons et toutes les cartes | `globals.css` L.192-278                           | Moyenne |

Le **thème spatial est reconnaissable à 100m** comme output Cursor/v0/Bolt. Les 6 autres thèmes (ocean, forest, dune, peach, dino, minimal) atténuent le problème — mais le thème par défaut reste le premier contact.

Circonstance atténuante : les 7 thèmes existent, `prefers-reduced-motion` est géré à deux niveaux (CSS + hook React), et le flow de correction post-soumission est de la pédagogie bien traduite en design.

### Heuristiques Nielsen

| #         | Heuristique                      | Score     | Problème principal                                                                          |
| --------- | -------------------------------- | --------- | ------------------------------------------------------------------------------------------- |
| 1         | Visibilité du statut système     | 3         | Le bouton Valider ne montre pas de chargement entre clic et réponse serveur sur mobile lent |
| 2         | Correspondance monde réel        | 3         | "Mode IA ✨", "session entrelacée" dans les params URL = jargon adulte sur interface enfant |
| 3         | Contrôle utilisateur             | 3         | Back links présents partout ; pas d'undo sur soumission (normal)                            |
| 4         | Cohérence et standards           | 2         | Solver exercice vs solver défi : conventions HTML différentes ; glassmorphism non-uniforme  |
| 5         | Prévention des erreurs           | 3         | Validation avant submit, bouton Valider grisé sans réponse — bien                           |
| 6         | Reconnaissance plutôt que rappel | 3         | Choix QCM visibles ; label "Mode IA" sans texte explicatif sur mobile                       |
| 7         | Flexibilité et efficacité        | 2         | Navigation clavier QCM ✓ ; zéro raccourci documenté ; générateur IA mobile dense            |
| 8         | Design esthétique et minimaliste | 2         | Dashboard Overview : 5 widgets simultanés ; sweep effect global = bruit pur                 |
| 9         | Aide à la récupération d'erreur  | 3         | Toast errors clairs ; `reviewExerciseError` a deux boutons de sortie — bien conçu           |
| 10        | Aide et documentation            | 1         | Tooltip `HelpCircle` sur "Mode IA" = seule aide contextuelle visible                        |
| **Total** |                                  | **25/40** | **Acceptable — améliorations significatives nécessaires**                                   |

### Checklist charge cognitive — ExerciseSolver

| Item                   | Résultat | Note                                                                             |
| ---------------------- | -------- | -------------------------------------------------------------------------------- |
| Focus unique           | ✅       | L'énoncé est la star de la page                                                  |
| Chunking               | ✅       | Header → Choices → Valider → Feedback                                            |
| Grouping               | ✅       | Zones visuellement séparées                                                      |
| Hiérarchie visuelle    | ⚠️       | Bouton Valider grisé se fond dans le background avant sélection                  |
| Une chose à la fois    | ✅       | Séquence claire                                                                  |
| Choix minimaux         | ✅       | 4 choix max QCM                                                                  |
| Mémoire de travail     | ✅       | Pas de mémoire cross-écran requise                                               |
| Disclosure progressive | ⚠️       | Animation backdrop-blur + sweep du board concurrence le feedback post-soumission |

**Score** : 2 échecs → charge cognitive **modérée**. Adressable avec NI-1/NI-3.

### Issues prioritaires identifiées

**[P1] Sweep effect global — bruit visuel universel**

- `button::after` + `[data-slot="card"]::before` dans `globals.css` (L.192-278) s'appliquent sur _chaque_ bouton et _chaque_ carte sans exception.
- Sur les cartes QCM, l'animation de brillance concurrence directement le feedback de sélection — le stimuli décoratif parasite le stimuli pédagogique.
- **Correction** : Supprimer le sweep global. Créer classe `.hover-sweep` opt-in pour les surfaces marketing uniquement. Le solver ne doit pas animer ses cartes.

**[P1] Absence de couche design apprenant — confirme NI-1/NI-3**

- `SolverFocusBoard` utilise `bg-card/90 backdrop-blur-xl` + bordure violette animée = même grammaire visuelle que le dashboard admin pendant la résolution d'exercice.
- Pour les profils TSA/TDAH : deux stimuli visuels simultanés (fond flou + bordure colorée animée) pendant la réflexion = charge extraneous.
- **Correction** : NI-1 + NI-2 + NI-3 du plan existant. `LearnerCard` flat + `--bg-learner` + `LearnerLayout` dans les solvers.

**[P2] Section features page d'accueil — template AI à 100%**

- `grid grid-cols-2 lg:grid-cols-4` de 4 `Card` identiques avec `rounded-full bg-primary/10` au-dessus de chaque titre.
- Premier contact pour un parent qui évalue la plateforme = perte de confiance immédiate si la page ressemble à 10 000 autres SaaS.
- **Correction** : Casser la grille uniforme. Varier les poids visuels. Une feature mérite d'être grande (apprentissage adaptatif), une peut être textuelle, une peut avoir une illustration. Voir NI-6 ci-dessous.

**[P2] AcademyStatsWidget — hero metric layout interdit**

- Grille 5 colonnes `grand nombre + icône + label`. Ces stats n'ont pas de sens pour l'enfant connecté.
- **Correction** : Message narratif de confiance pour les visiteurs non-connectés. Supprimer pour les apprenants authentifiés. Voir NI-7 ci-dessous.

### Personas — Red Flags

**Jordan (enfant de 8 ans, premier contact)**

- Bouton "Valider ma réponse" grisé avec `opacity-60` → un enfant pense que le bouton est cassé. Pas de label explicatif du type "Choisis une réponse d'abord".
- L'indice (Lightbulb) est en bas du solver, souvent sous le fold sur mobile — l'enfant ne le trouvera pas.
- Label "Mode IA ✨" dans le générateur : jargon adulte. Un enfant de 8 ans lit "I" "A" sans comprendre.
- Badge "Révision" en mode spaced-review : aucune explication de ce que ça signifie.

**Sam (profil TSA/TDAH, sensible aux stimuli)**

- Sweep effect `::before` sur les cartes QCM déclenche un mouvement au survol _pendant la réflexion_. `prefers-reduced-motion` le supprime mais seulement si l'utilisateur l'a activé au niveau OS.
- `bg-card/90 backdrop-blur-xl` du SolverFocusBoard + bordure violette animée = deux stimuli simultanés pendant la résolution. Exactement ce que le débat NI a identifié.
- Changement `border-color` au survol des cartes QCM pendant que l'enfant lit le choix — collision lecture / feedback visuel.

**Parent/Enseignant (dashboard, outil adulte)**

- Dashboard Overview : 5 widgets simultanément visibles sans priorisation claire. Pas de lecture évidente de "par où commencer".
- `DashboardLastUpdate` affiche "il y a 3h" sans contexte de quoi a été mis à jour.
- `ExportButton` dans l'en-tête à droite — invisible sur mobile sans scroll.

---

## Plan d'action consolidé (post-critique)

> Décisions issues des réponses à la session critique :
>
> - Q1 réponse C : NI-1/NI-2/NI-3 (couche apprenant) ET quick wins visuels en parallèle, dans des commits séparés
> - Q2 réponse B : Dashboard hors scope — préserver tel quel jusqu'à la future page parent/enseignant
> - Q3 réponse A : Page d'accueil à traiter (vitrine externe prioritaire)

Les lots NI-1 à NI-5 du plan original restent inchangés. Les lots suivants s'y ajoutent :

### NI-6 — Refonte section features page d'accueil

**Priorité** : P2 | **Effort** : S (3-4h)

- Casser la grille `grid-cols-2 lg:grid-cols-4` uniforme dans `app/page.tsx`
- Traitement asymétrique : 1 feature grande (apprentissage adaptatif), 2-3 features secondaires à poids réduit
- Supprimer les `rounded-full bg-primary/10` icon-containers au-dessus de chaque titre
- Supprimer `AcademyStatsWidget` pour les utilisateurs authentifiés ; conserver uniquement pour les visiteurs non-connectés avec un message narratif (pas de grille de chiffres bruts)
- Contrainte : zéro changement aux composants globaux `Card`, `Button`

### NI-7 — Suppression du sweep effect global

**Priorité** : P1 | **Effort** : XS (1h)

- Dans `globals.css` : retirer les blocs `button:not(:disabled)::after` et `[data-slot="card"]::before` (sweep effect)
- Créer classe utilitaire `.hover-sweep` opt-in avec le même CSS
- Appliquer `.hover-sweep` uniquement sur les surfaces marketing où l'effet a du sens (cards de la page d'accueil si conservées)
- Contrainte : ne pas toucher `button:not(:disabled):hover { transform: translateY(-2px) }` dans un premier temps — problème séparé, effort séparé

### NI-8 — Microcopy bouton Valider (affordance)

**Priorité** : P2 | **Effort** : XS (30min)

- Ajouter un label `aria-describedby` ou tooltip visible sous le bouton grisé dans `ExerciseSolverChoices.tsx` : "Sélectionne une réponse pour continuer"
- Cible : Jordan (8 ans) qui interprète le grisé comme un bug

---

## Critique UX terrain — 2026-04-04

> Audit conduit après la session FFI (NI-1 à NI-8 complétés).
> Périmètre élargi : homepage, dashboard, badges, classement, solvers, ExerciseModal.
> Score Nielsen : **23/40 — Acceptable avec lacunes significatives.**
> Mode d'évaluation : posture neutre, faits vérifiés dans le code avant toute conclusion.

### Corrections apportées au rapport brut avant documentation

Quatre points du rapport ont été contestés et vérifiés dans le code :

| Point | Verdict | Preuve code |
|-------|---------|-------------|
| "ExerciseModal se ferme après 3s" | ❌ Inexact | `setTimeout(3000)` appelle `onExerciseCompleted?.()` ; dans `exercises/page.tsx` ce callback invalide des queries sans fermer la modal |
| "`jedi_rank` dans le DOM" | ⚠️ Surestimé | `jedi_rank` est une prop TypeScript `@deprecated` dans `LevelIndicator.tsx` — dette interne non visible à l'utilisateur |
| "Activer `success-pulse`/`error-shake` est mieux" | ⚠️ Opinion, pas fait | Les keyframes existent et sont inactifs — c'est prouvé. Mais les activer sur surface apprenant peut introduire du bruit post-réflexion (Mayer, 2009 — extraneous load). Décision ouverte. |
| "Pas de feedback immédiat Valider = P1" | ⚠️ Sur-sévérisé | Le bouton passe en `disabled` + `Loader2` via `isSubmitting` ; la latence dépend du cycle React/réseau. Reclassé P2. |

### Heuristiques Nielsen — Score terrain

| # | Heuristique | Score | Finding principal |
|---|-------------|-------|-------------------|
| 1 | Visibilité du statut système | **3** | Spinner + texte sur loading ✓. Sur mobile lent : délai perceptible entre clic Valider et déclenchement du `Loader2` (`isSubmitting` non immédiat au clic). |
| 2 | Correspondance monde réel | **2** | "session entrelacée", "spaced-review", "Mode IA ✨" — jargon adulte sur interface enfant. Badge "Révision" sans explication. |
| 3 | Contrôle utilisateur | **3** | Back links présents. `handleClose` bloqué pendant `isSubmitting`. `ExerciseModal` : le timeout 3s déclenche `onExerciseCompleted` (invalidation queries), la modal ne se ferme pas automatiquement — comportement acceptable. |
| 4 | Cohérence et standards | **2** | `error-shake` et `success-pulse` définis en CSS mais jamais appliqués. Deux boutons "Retour aux défis" dans ChallengeSolver (haut + bas). `border-2` sur feedback erreur exercice vs `border` sur feedback succès. |
| 5 | Prévention des erreurs | **3** | Bouton Valider grisé + microcopy NI-8 ✓. `tabIndex` QCM ✓. Enter vide en open-answer passe silencieusement — à corriger. |
| 6 | Reconnaissance plutôt que rappel | **2** | Bouton "Voir un indice" sous le fold mobile dans ~80% des cas (4 boutons QCM `py-6` ≈ 300px + Valider + microcopy avant l'indice). Navigation : 7 items sans priorité claire pour un enfant. |
| 7 | Flexibilité et efficacité | **2** | Navigation clavier QCM ✓. Zéro raccourci documenté. Dashboard : 16 widgets potentiels, pas de priorisation de lecture. ExportButton invisible mobile. |
| 8 | Design esthétique et minimaliste | **2** | Dashboard : 5 widgets simultanés sans hiérarchie de lecture. ChallengeSolver : deux blocs "Retour aux défis" redondants. `AcademyStatsWidget` : `backdrop-blur-md` dans skeleton ET rendu final (hors NI). |
| 9 | Aide à la récupération d'erreur | **3** | Toast errors clairs ✓. `GrowthMindsetHint` sur mauvaise réponse ✓. `role="alert" aria-live="assertive"` sur les error states ✓. |
| 10 | Aide et documentation | **1** | Aucune aide contextuelle pendant la résolution pour un enfant. Pas d'explication "défi logique" vs "exercice". Pas d'onboarding. Tooltip HelpCircle sur "Mode IA" = seule aide visible. |
| **Total** | | **23/40** | **Acceptable — dette UX significative pour l'audience enfant** |

### Anti-patterns — État au 2026-04-04

| Tell AI Slop | État | Détail |
|---|---|---|
| Violet `#7c3aed` + fond `#0a0a0f` | ⚠️ Atténué | Thème spatial = palette AI 2024. Sauvé par 6 autres thèmes, mais premier contact encore reconnaissable. |
| Glassmorphism systématique | ✅ Corrigé dans learner | `AcademyStatsWidget` conserve `backdrop-blur-md` dans skeleton ET rendu normal — hors scope NI mais visible en homepage. |
| Hero metric layout | ✅ Supprimé pour connectés | Widget conditionné `!isAuthLoading && !isAuthenticated`. Le widget lui-même reste hero-metric pour les non-connectés. |
| `rounded-full bg-primary/10` icon-containers | ✅ Supprimé homepage | Subsiste dans `AcademyStatsWidget` (icônes stats), `StreakWidget`, `LeaderboardWidget`. |
| Identical card grid ×4 | ✅ Cassé homepage | Features asymétrique. Listes exercices/défis conservent la grille uniforme. |
| Sweep effect global | ✅ Neutralisé learner | `translateY(-2px)` reste actif hors `[data-learner-context]`. Dashboard, badges, classement : tous les boutons lèvent encore. |
| `error-shake` + `success-pulse` | ❌ Définis, jamais utilisés | CSS mort. Décision d'activation = choix design ouvert (voir NI-9). |

### Personas — Red Flags terrain

**Jordan (enfant 8-10 ans)**

- Homepage : "Apprendre sérieusement, sans perdre le plaisir" — trop long, présuppose que l'apprentissage est douloureux pour l'audience cible.
- Liste exercices : 4 dropdowns visibles immédiatement (type, difficulté, âge, tri). Surcharge de choix (Schwartz, 2004).
- Feedback succès : `CheckCircle2` vert + `GrowthMindsetHint`. Correct mais purement chromatique — aucun signal positif fort pour un enfant qui vient de réussir.
- Indice : sous le fold mobile. L'enfant bloqué abandonne sans savoir qu'une aide existe.
- Dashboard tabs : "Vue d'ensemble, Recommandations, Progression, Mon Profil" — vocabulaire adulte sans sens pour un enfant de 8 ans.
- ⚠️ **Risque d'abandon élevé au 3e exercice.**

**Sam (profil TSA/TDAH)**

- Thème Spatial par défaut : palette émotionnellement neutre/froide. Fond quasi-noir + violet — certains profils TSA associent cette palette à de l'anxiété (Ludlow, 2012).
- Zone de résolution avec `data-learner-context` : correctement neutre. ✅
- Header de navigation toujours visible pendant la résolution : 7 liens + icônes = fond de distracteurs constants.
- `badge-card-earned-compact:hover` : transition `max-height 0.3s ease` dans `@media (hover: hover)` **sans** protection `prefers-reduced-motion` — bug accessibilité prouvé dans le code.
- `ChallengeSolver` : les visualisations interactives (`ChallengeVisualRenderer`) peuvent déclencher des rendus complexes. Aucune option de simplification visuelle.
- ⚠️ **Le flux apprenant est protégé. Le reste de l'interface ne l'est pas.**

**Parent/Enseignant**

- StatsCards dashboard : toutes au même poids visuel, hiérarchie "qu'est-ce qui compte le plus" inexistante.
- `DashboardLastUpdate` : "il y a 3h" sans contexte de quoi a été mis à jour.
- `ExportButton` invisible mobile.
- Aucune vue "mes élèves / mon enfant" — chemin inexistant.
- ⚠️ **Dashboard = outil adulte non finalisé, pas encore outil parent/enseignant.**

---

## Plan d'action — NI-9 à NI-13

> Lots issus de l'audit terrain 2026-04-04. Complètent NI-1 à NI-8.

### NI-9 — Feedback post-réponse : décision animations `success-pulse` / `error-shake`

**Priorité** : P2 | **Effort** : XS | **Statut** : À faire

Les keyframes `success-pulse` et `error-shake` sont définis dans `globals.css` mais jamais appliqués.

Décision de design documentée :
- Activer sur surface apprenant = risque d'extraneous load post-réflexion (Mayer, 2009). À évaluer.
- Activer uniquement si `!shouldReduceMotion` et avec durée courte (≤ 400ms) pour limiter la distraction.
- Alternative : signal non-cinétique (couleur + icône + son optionnel).

**Scope** : `ExerciseSolverFeedback`, feedback ChallengeSolver.
**Décision à prendre** : activer `success-pulse` (scale 1→1.03→1, 300ms) + `error-shake` (translateX ±4px, 300ms) sous garde `shouldReduceMotion`.

### NI-10 — Indice sous le fold mobile : remonter avant les choix

**Priorité** : P2 | **Effort** : S | **Statut** : À faire

Le bouton "Voir un indice" est rendu après les choix QCM et le bouton Valider. Sur mobile 375px :
- 4 boutons QCM `py-6` ≈ 300px
- Bouton Valider + microcopy ≈ 80px
- Total avant l'indice : ~380px → invisible sans scroll

Référence : W3C COGA 2.2 "Provide help for complex information". Un enfant bloqué ne scroll pas pour chercher de l'aide.

**Fix** : Déplacer le bouton indice *avant* les choix (typographie discrète, `text-xs text-muted-foreground`, ne concurrence pas les réponses) ou sticky en bas de la zone de résolution.

**Scope** : `ExerciseSolverFeedback` layout, `ExerciseSolver` composition.

### NI-11 — Badge hover-reveal : protection `prefers-reduced-motion` manquante

**Priorité** : P2 | **Effort** : XS | **Statut** : À faire — bug prouvé

Dans `globals.css`, le bloc :

```css
@media (hover: hover) {
  .badge-card-earned-compact .badge-card-expandable {
    transition: max-height 0.3s ease, opacity 0.25s ease;
  }
}
```

est hors de tout `@media (prefers-reduced-motion: reduce)`. La transition `max-height` se déclenche même si l'utilisateur a activé `prefers-reduced-motion` au niveau OS.

Référence WCAG 2.1 SC 2.3.3 (Animation from Interactions — AAA). Pour un profil TSA/TDAH avec `prefers-reduced-motion`, ce mouvement non protégé est un bug d'accessibilité réel.

**Fix** : Encapsuler la transition `max-height` dans `@media (prefers-reduced-motion: no-preference)`.

**Scope** : `globals.css`, bloc `.badge-card-earned-compact`.

### NI-12 — `AcademyStatsWidget` : supprimer `backdrop-blur-md`

**Priorité** : P3 | **Effort** : XS | **Statut** : À faire

`AcademyStatsWidget.tsx` utilise `backdrop-blur-md` dans :
- Le skeleton loader (`Card className="... backdrop-blur-md"`)
- Le rendu final (`Card className="... backdrop-blur-md"`)

Ce glassmorphism subsiste après NI-6 (le composant est conditionné mais non modifié). Hors `data-learner-context` mais visible en homepage pour les visiteurs non-connectés.

**Fix** : Retirer `backdrop-blur-md` des deux `Card`. Remplacer par `bg-card/60` ou fond solide.

**Scope** : `AcademyStatsWidget.tsx`.

### NI-13 — Dashboard : vue simplifiée conditionnelle au rôle

**Priorité** : P1 | **Effort** : M | **Statut** : À planifier

Le dashboard présente la même interface au rôle `student` (enfant de 8 ans) et au rôle parent/admin. L'enfant connecté voit : 5 onglets, 16 widgets, graphiques d'axes temporels, bouton export.

C'est la surface la plus visitée après la résolution — et la plus mal adaptée à l'audience principale.

**Fix court terme** : Conditionner l'affichage dans `dashboard/page.tsx` au rôle utilisateur :
- Rôle `student` : streak, niveau, bouton "Commencer un exercice", sans onglets Progression / Mon Profil / graphiques.
- Rôle parent/admin : vue actuelle inchangée.

**Fix long terme** : NI-4 (page apprenant séparée).

**Scope** : `app/dashboard/page.tsx`, hooks `useAuth` pour rôle.

---

## Mise à jour vérité code — 2026-04-03

Ce document conserve le débat et le plan d'origine. Le bloc ci-dessous reflète la réalité
du code relu au 2026-04-03 dans le worktree local.

**Légende**

- ✅ Implémenté localement et relu dans le code
- ⏳ À faire ou non confirmé dans le code actuel
- 💤 Backlog assumé

**Confirmé dans le code**

- `NI-1` : `LearnerCard` et `LearnerLayout` existent et sont bien réservés au flux apprenant.
- `NI-2` : le token `--bg-learner` est bien porté par thème et consommé par la couche apprenant.
- `NI-3` : l'intégration exercise/challenge est en place ; le défi a retrouvé une largeur cohérente (`5xl`) et le `tabIndex` clavier du QCM est aligné sur le solver exercice.
- `NI-6` : la section features de la home a été refondue ; `AcademyStatsWidget` n'apparaît plus pour les utilisateurs authentifiés et est gardé derrière `!isAuthLoading && !isAuthenticated`.
- `NI-7` : le sweep global est passé en opt-in `.hover-sweep`, puis le lift/glow global des boutons et cards a été neutralisé dans `[data-learner-context]`.
- `NI-8` : la microcopy d'affordance sous le bouton Valider est présente dans `ExerciseSolver`, `ExerciseModal` et `ChallengeSolver` via `aria-describedby` + texte visible.

**Toujours ouverts**

- `NI-5` : l'opt-in `flat` sur `<Card>` n'est pas encore livré.
- `NI-4` : la page apprenant dédiée reste un backlog produit, pas un quick win.

---

## Récapitulatif consolidé — tous les lots

| Lot | Priorité | Effort | Scope | Statut |
| --- | -------- | ------ | ----- | ------ |
| NI-1 Composants apprenant (`LearnerCard`, `LearnerLayout`) | P1 | S-M | Solvers | ✅ FAIT 2026-03-30 |
| NI-2 Token `--bg-learner` par thème | P1 | S | `globals.css` | ✅ FAIT 2026-03-30 |
| NI-3 Intégration Solver (exercice + défi) | P1 | S | Solvers | ✅ FAIT 2026-03-30 |
| NI-4 Page apprenant tubulaire `/home-learner` | P2 | M | Nouvelle page | 💤 Backlog |
| NI-5 Opt-in `flat` sur `<Card>` | P2 | XS | Design system | ✅ FAIT 2026-04-04 |
| NI-6 Refonte section features accueil | P2 | S | `app/page.tsx` | ✅ FAIT 2026-03-30 |
| NI-7 Suppression sweep effect global | P1 | XS | `globals.css` | ✅ FAIT 2026-03-30 |
| NI-8 Microcopy bouton Valider grisé | P2 | XS | Solvers / modal exercice | ✅ FAIT 2026-03-30 |
| NI-9 Décision animations `success-pulse` / `error-shake` | P2 | XS | `globals.css` + solvers | À faire |
| NI-10 Indice sous le fold mobile | P2 | S | `ExerciseSolverFeedback` | À faire |
| NI-11 Badge hover-reveal : protection `prefers-reduced-motion` | P2 | XS | `globals.css` | À faire |
| NI-12 `AcademyStatsWidget` : supprimer `backdrop-blur-md` | P3 | XS | `AcademyStatsWidget.tsx` | À faire |
| NI-13 Dashboard vue conditionnelle enfant / adulte | P1 | M | `dashboard/page.tsx` | À planifier |

**Recommandation solo founder révisée** :

- Sprint NI-1→NI-8 : terminé — couche apprenant en place, homepage refondue, affordance correcte.
- Sprint NI-9→NI-12 (quick wins, ~2h) : NI-11 en priorité (bug accessibilité réel), NI-12 (glassmorphism résiduel), NI-10 (UX enfant), NI-9 (décision design à prendre).
- Sprint NI-13 (M) : à planifier quand le rôle parent/enseignant est prêt — bloquant pour la monétisation B2B.
- NI-4 : backlog long terme, après NI-13.
