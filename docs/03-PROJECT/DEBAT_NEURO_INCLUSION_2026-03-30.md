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

| Lot                                                        | Priorité | Effort | Scope                    | Statut                              |
| ---------------------------------------------------------- | -------- | ------ | ------------------------ | ----------------------------------- |
| NI-1 Composants apprenant (`LearnerCard`, `LearnerLayout`) | P1       | S-M    | Solvers                  | ✅ Implémenté localement 2026-04-03 |
| NI-2 Token `--bg-learner` par thème                        | P1       | S      | `globals.css`            | ✅ Implémenté localement 2026-04-03 |
| NI-3 Intégration Solver (exercice + défi)                  | P1       | S      | Solvers                  | ✅ Implémenté localement 2026-04-03 |
| NI-4 Page apprenant tubulaire `/home-learner`              | P2       | M      | Nouvelle page            | 💤 Backlog                          |
| NI-5 Opt-in `flat` sur `<Card>`                            | P2       | XS     | Design system            | À faire                             |
| NI-6 Refonte section features accueil                      | P2       | S      | `app/page.tsx`           | ✅ Implémenté localement 2026-04-03 |
| NI-7 Suppression sweep effect global                       | P1       | XS     | `globals.css`            | ✅ Implémenté localement 2026-04-03 |
| NI-8 Microcopy bouton Valider grisé                        | P2       | XS     | Solvers / modal exercice | ✅ Implémenté localement 2026-04-03 |

**Recommandation solo founder révisée** :

- Sprint 1 (1,5 jour) : `NI-7 + NI-1 + NI-2 + NI-3` — implémenté localement ; à intégrer proprement si l'objectif est d'en faire une série Git défendable.
- Sprint 2 (demi-journée) : `NI-6` et `NI-8` sont faits localement ; `NI-5` reste le quick win ouvert.
- Sprint 3 (sprint dédié) : `NI-4` — page apprenant séparée, quand le dashboard parent/enseignant est prêt.
