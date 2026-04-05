# DÃ©bat â€” Neuro-inclusion & EdTech Readiness

> GÃ©nÃ©rÃ© le 2026-03-30 via `/octo:debate` (4 providers)
> Motion : Adopter le plan de refonte Neuro-inclusion tel que proposÃ©

---

## Contexte

Le plan soumis au dÃ©bat proposait 3 actions strictes pour Ã©radiquer le design "Default B2B SaaS / Vercel-Core" :

1. Modifier `:root` dans `globals.css` (fond slate-50, card 96.1%)
2. Aplatir les cartes (retirer border + shadow, passer Ã  rounded-3xl)
3. CrÃ©er un layout tubulaire sur le dashboard (max-w-2xl colonne unique)

---

## Positions des 4 providers

### ðŸ”´ Codex â€” ImplÃ©mentation Technique

**3 erreurs techniques bloquantes identifiÃ©es :**

- Action 1 : Modifier `:root` brise la cascade multi-thÃ¨me. Le thÃ¨me Spatial a dÃ©jÃ  `--background: #0a0a0f` dans `[data-theme="spatial"]`. Modifier `:root` en slate-50 propage un fond clair sur tous les thÃ¨mes qui n'overrident pas.
- Action 2 : `card.tsx` a dÃ©jÃ  `border-0`. La shadow est `shadow-[var(--shadow-card)]` (token CSS), pas une classe Tailwind hardcodÃ©e. La "retirer" globalement casse 126 composants.
- Action 3 : Dashboard Tabs + 16 widgets â†’ layout max-w-2xl = scroll infini et perte de densitÃ© utile pour les adultes.

### ðŸŸ¡ Gemini â€” AccessibilitÃ© & Standards EdTech

**Les guardrails sont scientifiquement incomplets :**

- "ZÃ©ro Blanc Pur" n'est pas une norme WCAG â€” c'est une prÃ©fÃ©rence de confort. La variabilitÃ© inter-individuelle TSA/TDAH est extrÃªme.
- "ZÃ©ro dÃ©limitation visuelle" peut crÃ©er une "soupe visuelle" anxiogÃ¨ne pour les profils TSA qui s'appuient sur les zones fonctionnelles pour s'orienter.
- La Conception Universelle pour l'Apprentissage (UDL) recommande plusieurs reprÃ©sentations, pas une reprÃ©sentation unique imposÃ©e.

### ðŸŸ¢ Sonnet â€” Recherche UX & Design

**Bonne direction, mauvais niveau d'abstraction :**

- Le plan agit sur le design system global alors qu'il devrait crÃ©er une couche de prÃ©sentation dÃ©diÃ©e au flux apprenant.
- Il existe dÃ©jÃ  un mode TSA/TDAH dans `globals.css` â€” le plan l'ignore.
- Solution : `LearnerCard` + `LearnerLayout` spÃ©cifiques aux pages exercice/dÃ©fi. CoÃ»t : 2h. Risque : zÃ©ro rÃ©gression sur l'existant.

### ðŸ”µ Claude/Opus â€” SynthÃ¨se & Arbitrage

**La tension rÃ©elle : global vs ciblÃ©.**

- Le diagnostic est correct (manque de couche design apprenant).
- La solution globale est incorrecte (effets de bord sur 126 composants).
- Solution correcte : composants dÃ©diÃ©s au rÃ´le apprenant, tokens `--bg-learner` par thÃ¨me, intÃ©gration ciblÃ©e dans ExerciseSolver et ChallengeSolver.

---

## Verdict

### Sur les 3 actions proposÃ©es

| Action                                             | Verdict                     | Motif                                                                    |
| -------------------------------------------------- | --------------------------- | ------------------------------------------------------------------------ |
| Action 1 : Modifier `:root` globals.css            | âŒ REJETÃ‰                  | Brise la cascade multi-thÃ¨me (7 thÃ¨mes)                                |
| Action 2 : Retirer shadow de card.tsx global       | âš ï¸ PARTIELLEMENT ADOPTÃ‰ | `border-0` dÃ©jÃ  en place ; shadow â†’ opt-in via prop `flat?` sur Card |
| Action 3 : Layout tubulaire sur dashboard existant | âŒ REJETÃ‰                  | Dashboard = outil adulte/parent ; crÃ©er une page apprenant sÃ©parÃ©e    |

### Sur les objectifs de la mission

| Objectif                                        | Verdict       | Action correcte                                            |
| ----------------------------------------------- | ------------- | ---------------------------------------------------------- |
| Anti "IA-look" / design trop gÃ©nÃ©rique        | âœ… LÃ‰GITIME | `LearnerCard` avec shadow nulle et radius organique        |
| ZÃ©ro fond blanc Ã©blouissant                   | âœ… LÃ‰GITIME | Token `--bg-learner` lÃ©gÃ¨rement teintÃ© par thÃ¨me       |
| ZÃ©ro layout surchargÃ© pendant l'apprentissage | âœ… LÃ‰GITIME | `LearnerLayout` max-w-2xl sur pages exercice/dÃ©fi         |
| Mode focus apprenant                            | âœ… LÃ‰GITIME | Extension du mode TSA/TDAH existant ou `FocusModeProvider` |

---

## Plan d'action â€” Neuro-inclusion EdTech (version correcte)

### NI-1 â€” Composants apprenant dÃ©diÃ©s

**PrioritÃ©** : P1 | **Effort** : S-M (1 jour)

- CrÃ©er `frontend/components/learner/LearnerCard.tsx`
  - Shadow nulle, radius 2xl, fond `--bg-learner`, padding gÃ©nÃ©reux
  - RÃ©utilise `Card` avec overrides ciblÃ©s
- CrÃ©er `frontend/components/learner/LearnerLayout.tsx`
  - `max-w-2xl` centrÃ©, `gap-12`, padding gÃ©nÃ©reux
  - ZÃ©ro sidebar, flux de lecture unique

### NI-2 â€” Token `--bg-learner` par thÃ¨me

**PrioritÃ©** : P1 | **Effort** : S (3h)

Ajouter dans `globals.css` pour chacun des 8 themes :

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
[data-theme="aurora"] {
  --bg-learner: #fdf4fb;
}
[data-theme="dino"] {
  --bg-learner: #fefce4;
}
[data-theme="unicorn"] {
  --bg-learner: #fef5fb;
}
```

### NI-3 â€” IntÃ©gration dans ExerciseSolver + ChallengeSolver

**PrioritÃ©** : P1 | **Effort** : S (2h)

- Remplacer `<PageLayout>` par `<LearnerLayout>` dans les pages exercice et dÃ©fi
- Remplacer les `<Card>` wrappant les questions par `<LearnerCard>`
- ZÃ©ro modification des composants globaux

### NI-4 â€” Page d'accueil apprenant tubulaire

**PrioritÃ©** : P2 | **Effort** : M (sprint dÃ©diÃ©)

CrÃ©er une page `/home-learner` ou vue enfant dÃ©diÃ©e avec :

- Actions rapides (Exercices, DÃ©fis, Badges)
- Streak + Niveau
- Layout `LearnerLayout`, fond `--bg-learner`, zÃ©ro colonne multiple

### NI-5 â€” Opt-in `flat` sur `<Card>`

**PrioritÃ©** : P2 | **Effort** : XS (1h)

```tsx
// Ajouter prop flat?: boolean Ã  Card
// flat=true â†’ shadow: none
// Opt-in progressif lÃ  oÃ¹ pertinent, dÃ©faut global inchangÃ©
```

---

## Ce qui N'est PAS Ã  faire

- Modifier `:root` dans `globals.css` â†’ brise les 7 thÃ¨mes
- Passer `rounded-3xl` en dÃ©faut global sur `card.tsx` â†’ affecte toutes les modales admin
- Refactoriser le dashboard principal en colonne unique â†’ dÃ©grade l'expÃ©rience adulte/parent
- Interdire toute dÃ©limitation visuelle â†’ peut crÃ©er une dÃ©sorientation pour certains profils TSA

---

## RÃ©capitulatif des lots

| Lot                       | PrioritÃ© | Effort | Impact                                   |
| ------------------------- | --------- | ------ | ---------------------------------------- |
| NI-1 Composants apprenant | P1        | S-M    | Couche design flux apprenant             |
| NI-2 Token --bg-learner   | P1        | S      | Fond teintÃ© par thÃ¨me                  |
| NI-3 IntÃ©gration Solver  | P1        | S      | Neuro-inclusion lÃ  oÃ¹ l'enfant apprend |
| NI-4 Page apprenant       | P2        | M      | Accueil tubulaire dÃ©diÃ©                |
| NI-5 Opt-in flat Card     | P2        | XS     | FlexibilitÃ© design system               |

**Recommandation solo founder** : NI-1 + NI-2 + NI-3 en un seul sprint (1,5 jour).
RÃ©sultat : les pages exercice et dÃ©fi deviennent neuro-inclusives sans rien casser.

---

## Critique design â€” Audit `/critique` (2026-03-30)

> Session de critique complÃ¨te conduite aprÃ¨s la session FFI-L7â†’L9.
> PÃ©rimÃ¨tre : page d'accueil (`app/page.tsx`), dashboard (`app/dashboard/page.tsx`), solver exercice (`ExerciseSolver.tsx`).
> Score Nielsen : **25/40 â€” Acceptable**, amÃ©liorations significatives nÃ©cessaires.

### Diagnostic AI Slop â€” Verdict

L'interface prÃ©sente **6 tells AI slop actifs** :

| Tell                                                                               | Localisation                                        | GravitÃ© |
| ---------------------------------------------------------------------------------- | --------------------------------------------------- | -------- |
| Dark mode violet + fond `#0a0a0f` = palette AI 2024-2025                           | ThÃ¨me spatial (dÃ©faut)                            | Ã‰levÃ©e |
| Glassmorphism systÃ©matique `bg-card/40 backdrop-blur-md`                          | 15+ composants                                      | Ã‰levÃ©e |
| Hero metric layout (grand nombre + icÃ´ne + label Ã—5)                             | `AcademyStatsWidget`                                | Ã‰levÃ©e |
| IcÃ´ne `rounded-full bg-primary/10` au-dessus de chaque titre                      | Page accueil (4 cartes), gÃ©nÃ©rateur IA, dashboard | Ã‰levÃ©e |
| Identical card grid (icon + title + desc Ã—4)                                      | Section features `app/page.tsx`                     | Moyenne  |
| Sweep effect `::after`/`::before` global sur tous les boutons et toutes les cartes | `globals.css` L.192-278                             | Moyenne  |

Le **thÃ¨me spatial est reconnaissable Ã  100m** comme output Cursor/v0/Bolt. Les 7 autres themes (ocean, forest, dune, aurora, dino, unicorn, minimal) attenuent le probleme â€” mais le theme par defaut reste le premier contact.

Circonstance attÃ©nuante : les 7 thÃ¨mes existent, `prefers-reduced-motion` est gÃ©rÃ© Ã  deux niveaux (CSS + hook React), et le flow de correction post-soumission est de la pÃ©dagogie bien traduite en design.

### Heuristiques Nielsen

| #         | Heuristique                        | Score     | ProblÃ¨me principal                                                                           |
| --------- | ---------------------------------- | --------- | --------------------------------------------------------------------------------------------- |
| 1         | VisibilitÃ© du statut systÃ¨me     | 3         | Le bouton Valider ne montre pas de chargement entre clic et rÃ©ponse serveur sur mobile lent  |
| 2         | Correspondance monde rÃ©el         | 3         | "Mode IA âœ¨", "session entrelacÃ©e" dans les params URL = jargon adulte sur interface enfant |
| 3         | ContrÃ´le utilisateur              | 3         | Back links prÃ©sents partout ; pas d'undo sur soumission (normal)                             |
| 4         | CohÃ©rence et standards            | 2         | Solver exercice vs solver dÃ©fi : conventions HTML diffÃ©rentes ; glassmorphism non-uniforme  |
| 5         | PrÃ©vention des erreurs            | 3         | Validation avant submit, bouton Valider grisÃ© sans rÃ©ponse â€” bien                         |
| 6         | Reconnaissance plutÃ´t que rappel  | 3         | Choix QCM visibles ; label "Mode IA" sans texte explicatif sur mobile                         |
| 7         | FlexibilitÃ© et efficacitÃ©        | 2         | Navigation clavier QCM âœ“ ; zÃ©ro raccourci documentÃ© ; gÃ©nÃ©rateur IA mobile dense        |
| 8         | Design esthÃ©tique et minimaliste  | 2         | Dashboard Overview : 5 widgets simultanÃ©s ; sweep effect global = bruit pur                  |
| 9         | Aide Ã  la rÃ©cupÃ©ration d'erreur | 3         | Toast errors clairs ; `reviewExerciseError` a deux boutons de sortie â€” bien conÃ§u          |
| 10        | Aide et documentation              | 1         | Tooltip `HelpCircle` sur "Mode IA" = seule aide contextuelle visible                          |
| **Total** |                                    | **25/40** | **Acceptable â€” amÃ©liorations significatives nÃ©cessaires**                                 |

### Checklist charge cognitive â€” ExerciseSolver

| Item                   | RÃ©sultat | Note                                                                             |
| ---------------------- | --------- | -------------------------------------------------------------------------------- |
| Focus unique           | âœ…       | L'Ã©noncÃ© est la star de la page                                                |
| Chunking               | âœ…       | Header â†’ Choices â†’ Valider â†’ Feedback                                      |
| Grouping               | âœ…       | Zones visuellement sÃ©parÃ©es                                                    |
| HiÃ©rarchie visuelle   | âš ï¸     | Bouton Valider grisÃ© se fond dans le background avant sÃ©lection                |
| Une chose Ã  la fois   | âœ…       | SÃ©quence claire                                                                 |
| Choix minimaux         | âœ…       | 4 choix max QCM                                                                  |
| MÃ©moire de travail    | âœ…       | Pas de mÃ©moire cross-Ã©cran requise                                             |
| Disclosure progressive | âš ï¸     | Animation backdrop-blur + sweep du board concurrence le feedback post-soumission |

**Score** : 2 Ã©checs â†’ charge cognitive **modÃ©rÃ©e**. Adressable avec NI-1/NI-3.

### Issues prioritaires identifiÃ©es

**[P1] Sweep effect global â€” bruit visuel universel**

- `button::after` + `[data-slot="card"]::before` dans `globals.css` (L.192-278) s'appliquent sur _chaque_ bouton et _chaque_ carte sans exception.
- Sur les cartes QCM, l'animation de brillance concurrence directement le feedback de sÃ©lection â€” le stimuli dÃ©coratif parasite le stimuli pÃ©dagogique.
- **Correction** : Supprimer le sweep global. CrÃ©er classe `.hover-sweep` opt-in pour les surfaces marketing uniquement. Le solver ne doit pas animer ses cartes.

**[P1] Absence de couche design apprenant â€” confirme NI-1/NI-3**

- `SolverFocusBoard` utilise `bg-card/90 backdrop-blur-xl` + bordure violette animÃ©e = mÃªme grammaire visuelle que le dashboard admin pendant la rÃ©solution d'exercice.
- Pour les profils TSA/TDAH : deux stimuli visuels simultanÃ©s (fond flou + bordure colorÃ©e animÃ©e) pendant la rÃ©flexion = charge extraneous.
- **Correction** : NI-1 + NI-2 + NI-3 du plan existant. `LearnerCard` flat + `--bg-learner` + `LearnerLayout` dans les solvers.

**[P2] Section features page d'accueil â€” template AI Ã  100%**

- `grid grid-cols-2 lg:grid-cols-4` de 4 `Card` identiques avec `rounded-full bg-primary/10` au-dessus de chaque titre.
- Premier contact pour un parent qui Ã©value la plateforme = perte de confiance immÃ©diate si la page ressemble Ã  10 000 autres SaaS.
- **Correction** : Casser la grille uniforme. Varier les poids visuels. Une feature mÃ©rite d'Ãªtre grande (apprentissage adaptatif), une peut Ãªtre textuelle, une peut avoir une illustration. Voir NI-6 ci-dessous.

**[P2] AcademyStatsWidget â€” hero metric layout interdit**

- Grille 5 colonnes `grand nombre + icÃ´ne + label`. Ces stats n'ont pas de sens pour l'enfant connectÃ©.
- **Correction** : Message narratif de confiance pour les visiteurs non-connectÃ©s. Supprimer pour les apprenants authentifiÃ©s. Voir NI-7 ci-dessous.

### Personas â€” Red Flags

**Jordan (enfant de 8 ans, premier contact)**

- Bouton "Valider ma rÃ©ponse" grisÃ© avec `opacity-60` â†’ un enfant pense que le bouton est cassÃ©. Pas de label explicatif du type "Choisis une rÃ©ponse d'abord".
- L'indice (Lightbulb) est en bas du solver, souvent sous le fold sur mobile â€” l'enfant ne le trouvera pas.
- Label "Mode IA âœ¨" dans le gÃ©nÃ©rateur : jargon adulte. Un enfant de 8 ans lit "I" "A" sans comprendre.
- Badge "RÃ©vision" en mode spaced-review : aucune explication de ce que Ã§a signifie.

**Sam (profil TSA/TDAH, sensible aux stimuli)**

- Sweep effect `::before` sur les cartes QCM dÃ©clenche un mouvement au survol _pendant la rÃ©flexion_. `prefers-reduced-motion` le supprime mais seulement si l'utilisateur l'a activÃ© au niveau OS.
- `bg-card/90 backdrop-blur-xl` du SolverFocusBoard + bordure violette animÃ©e = deux stimuli simultanÃ©s pendant la rÃ©solution. Exactement ce que le dÃ©bat NI a identifiÃ©.
- Changement `border-color` au survol des cartes QCM pendant que l'enfant lit le choix â€” collision lecture / feedback visuel.

**Parent/Enseignant (dashboard, outil adulte)**

- Dashboard Overview : 5 widgets simultanÃ©ment visibles sans priorisation claire. Pas de lecture Ã©vidente de "par oÃ¹ commencer".
- `DashboardLastUpdate` affiche "il y a 3h" sans contexte de quoi a Ã©tÃ© mis Ã  jour.
- `ExportButton` dans l'en-tÃªte Ã  droite â€” invisible sur mobile sans scroll.

---

## Plan d'action consolidÃ© (post-critique)

> DÃ©cisions issues des rÃ©ponses Ã  la session critique :
>
> - Q1 rÃ©ponse C : NI-1/NI-2/NI-3 (couche apprenant) ET quick wins visuels en parallÃ¨le, dans des commits sÃ©parÃ©s
> - Q2 rÃ©ponse B : Dashboard hors scope â€” prÃ©server tel quel jusqu'Ã  la future page parent/enseignant
> - Q3 rÃ©ponse A : Page d'accueil Ã  traiter (vitrine externe prioritaire)

Les lots NI-1 Ã  NI-5 du plan original restent inchangÃ©s. Les lots suivants s'y ajoutent :

### NI-6 â€” Refonte section features page d'accueil

**PrioritÃ©** : P2 | **Effort** : S (3-4h)

- Casser la grille `grid-cols-2 lg:grid-cols-4` uniforme dans `app/page.tsx`
- Traitement asymÃ©trique : 1 feature grande (apprentissage adaptatif), 2-3 features secondaires Ã  poids rÃ©duit
- Supprimer les `rounded-full bg-primary/10` icon-containers au-dessus de chaque titre
- Supprimer `AcademyStatsWidget` pour les utilisateurs authentifiÃ©s ; conserver uniquement pour les visiteurs non-connectÃ©s avec un message narratif (pas de grille de chiffres bruts)
- Contrainte : zÃ©ro changement aux composants globaux `Card`, `Button`

### NI-7 â€” Suppression du sweep effect global

**PrioritÃ©** : P1 | **Effort** : XS (1h)

- Dans `globals.css` : retirer les blocs `button:not(:disabled)::after` et `[data-slot="card"]::before` (sweep effect)
- CrÃ©er classe utilitaire `.hover-sweep` opt-in avec le mÃªme CSS
- Appliquer `.hover-sweep` uniquement sur les surfaces marketing oÃ¹ l'effet a du sens (cards de la page d'accueil si conservÃ©es)
- Contrainte : ne pas toucher `button:not(:disabled):hover { transform: translateY(-2px) }` dans un premier temps â€” problÃ¨me sÃ©parÃ©, effort sÃ©parÃ©

### NI-8 â€” Microcopy bouton Valider (affordance)

**PrioritÃ©** : P2 | **Effort** : XS (30min)

- Ajouter un label `aria-describedby` ou tooltip visible sous le bouton grisÃ© dans `ExerciseSolverChoices.tsx` : "SÃ©lectionne une rÃ©ponse pour continuer"
- Cible : Jordan (8 ans) qui interprÃ¨te le grisÃ© comme un bug

---

## Critique UX terrain â€” 2026-04-04

> Audit conduit aprÃ¨s la session FFI (NI-1 Ã  NI-8 complÃ©tÃ©s).
> PÃ©rimÃ¨tre Ã©largi : homepage, dashboard, badges, classement, solvers, ExerciseModal.
> Score Nielsen : **23/40 â€” Acceptable avec lacunes significatives.**
> Mode d'Ã©valuation : posture neutre, faits vÃ©rifiÃ©s dans le code avant toute conclusion.

### Corrections apportÃ©es au rapport brut avant documentation

Quatre points du rapport ont Ã©tÃ© contestÃ©s et vÃ©rifiÃ©s dans le code :

| Point                                             | Verdict                 | Preuve code                                                                                                                                                                                      |
| ------------------------------------------------- | ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "ExerciseModal se ferme aprÃ¨s 3s"                | âŒ Inexact              | `setTimeout(3000)` appelle `onExerciseCompleted?.()` ; dans `exercises/page.tsx` ce callback invalide des queries sans fermer la modal                                                           |
| "`jedi_rank` dans le DOM"                         | âš ï¸ SurestimÃ©        | `jedi_rank` est une prop TypeScript `@deprecated` dans `LevelIndicator.tsx` â€” dette interne non visible Ã  l'utilisateur                                                                       |
| "Activer `success-pulse`/`error-shake` est mieux" | âš ï¸ Opinion, pas fait | Les keyframes existent et sont inactifs â€” c'est prouvÃ©. Mais les activer sur surface apprenant peut introduire du bruit post-rÃ©flexion (Mayer, 2009 â€” extraneous load). DÃ©cision ouverte. |
| "Pas de feedback immÃ©diat Valider = P1"          | âš ï¸ Sur-sÃ©vÃ©risÃ©   | Le bouton passe en `disabled` + `Loader2` via `isSubmitting` ; la latence dÃ©pend du cycle React/rÃ©seau. ReclassÃ© P2.                                                                          |

### Heuristiques Nielsen â€” Score terrain

| #         | Heuristique                        | Score     | Finding principal                                                                                                                                                                                                                  |
| --------- | ---------------------------------- | --------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1         | VisibilitÃ© du statut systÃ¨me     | **3**     | Spinner + texte sur loading âœ“. Sur mobile lent : dÃ©lai perceptible entre clic Valider et dÃ©clenchement du `Loader2` (`isSubmitting` non immÃ©diat au clic).                                                                    |
| 2         | Correspondance monde rÃ©el         | **2**     | "session entrelacÃ©e", "spaced-review", "Mode IA âœ¨" â€” jargon adulte sur interface enfant. Badge "RÃ©vision" sans explication.                                                                                                  |
| 3         | ContrÃ´le utilisateur              | **3**     | Back links prÃ©sents. `handleClose` bloquÃ© pendant `isSubmitting`. `ExerciseModal` : le timeout 3s dÃ©clenche `onExerciseCompleted` (invalidation queries), la modal ne se ferme pas automatiquement â€” comportement acceptable. |
| 4         | CohÃ©rence et standards            | **2**     | `error-shake` et `success-pulse` dÃ©finis en CSS mais jamais appliquÃ©s. Deux boutons "Retour aux dÃ©fis" dans ChallengeSolver (haut + bas). `border-2` sur feedback erreur exercice vs `border` sur feedback succÃ¨s.             |
| 5         | PrÃ©vention des erreurs            | **3**     | Bouton Valider grisÃ© + microcopy NI-8 âœ“. `tabIndex` QCM âœ“. Enter vide en open-answer passe silencieusement â€” Ã  corriger.                                                                                                   |
| 6         | Reconnaissance plutÃ´t que rappel  | **2**     | Bouton "Voir un indice" sous le fold mobile dans ~80% des cas (4 boutons QCM `py-6` â‰ˆ 300px + Valider + microcopy avant l'indice). Navigation : 7 items sans prioritÃ© claire pour un enfant.                                    |
| 7         | FlexibilitÃ© et efficacitÃ©        | **2**     | Navigation clavier QCM âœ“. ZÃ©ro raccourci documentÃ©. Dashboard : 16 widgets potentiels, pas de priorisation de lecture. ExportButton invisible mobile.                                                                          |
| 8         | Design esthÃ©tique et minimaliste  | **2**     | Dashboard : 5 widgets simultanÃ©s sans hiÃ©rarchie de lecture. ChallengeSolver : deux blocs "Retour aux dÃ©fis" redondants. `AcademyStatsWidget` : `backdrop-blur-md` dans skeleton ET rendu final (hors NI).                      |
| 9         | Aide Ã  la rÃ©cupÃ©ration d'erreur | **3**     | Toast errors clairs âœ“. `GrowthMindsetHint` sur mauvaise rÃ©ponse âœ“. `role="alert" aria-live="assertive"` sur les error states âœ“.                                                                                             |
| 10        | Aide et documentation              | **1**     | Aucune aide contextuelle pendant la rÃ©solution pour un enfant. Pas d'explication "dÃ©fi logique" vs "exercice". Pas d'onboarding. Tooltip HelpCircle sur "Mode IA" = seule aide visible.                                          |
| **Total** |                                    | **23/40** | **Acceptable â€” dette UX significative pour l'audience enfant**                                                                                                                                                                   |

### Anti-patterns â€” Ã‰tat au 2026-04-04

| Tell AI Slop                                 | Ã‰tat                         | DÃ©tail                                                                                                                        |
| -------------------------------------------- | ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| Violet `#7c3aed` + fond `#0a0a0f`            | âš ï¸ AttÃ©nuÃ©               | ThÃ¨me spatial = palette AI 2024. SauvÃ© par 6 autres thÃ¨mes, mais premier contact encore reconnaissable.                     |
| Glassmorphism systÃ©matique                  | âœ… CorrigÃ© dans learner     | `AcademyStatsWidget` conserve `backdrop-blur-md` dans skeleton ET rendu normal â€” hors scope NI mais visible en homepage.     |
| Hero metric layout                           | âœ… SupprimÃ© pour connectÃ©s | Widget conditionnÃ© `!isAuthLoading && !isAuthenticated`. Le widget lui-mÃªme reste hero-metric pour les non-connectÃ©s.       |
| `rounded-full bg-primary/10` icon-containers | âœ… SupprimÃ© homepage        | Subsiste dans `AcademyStatsWidget` (icÃ´nes stats), `StreakWidget`, `LeaderboardWidget`.                                       |
| Identical card grid Ã—4                      | âœ… CassÃ© homepage           | Features asymÃ©trique. Listes exercices/dÃ©fis conservent la grille uniforme.                                                  |
| Sweep effect global                          | âœ… NeutralisÃ© learner       | `translateY(-2px)` reste actif hors `[data-learner-context]`. Dashboard, badges, classement : tous les boutons lÃ¨vent encore. |
| `error-shake` + `success-pulse`              | âŒ DÃ©finis, jamais utilisÃ©s | CSS mort. DÃ©cision d'activation = choix design ouvert (voir NI-9).                                                            |

### Personas â€” Red Flags terrain

**Jordan (enfant 8-10 ans)**

- Homepage : "Apprendre sÃ©rieusement, sans perdre le plaisir" â€” trop long, prÃ©suppose que l'apprentissage est douloureux pour l'audience cible.
- Liste exercices : 4 dropdowns visibles immÃ©diatement (type, difficultÃ©, Ã¢ge, tri). Surcharge de choix (Schwartz, 2004).
- Feedback succÃ¨s : `CheckCircle2` vert + `GrowthMindsetHint`. Correct mais purement chromatique â€” aucun signal positif fort pour un enfant qui vient de rÃ©ussir.
- Indice : sous le fold mobile. L'enfant bloquÃ© abandonne sans savoir qu'une aide existe.
- Dashboard tabs : "Vue d'ensemble, Recommandations, Progression, Mon Profil" â€” vocabulaire adulte sans sens pour un enfant de 8 ans.
- âš ï¸ **Risque d'abandon Ã©levÃ© au 3e exercice.**

**Sam (profil TSA/TDAH)**

- ThÃ¨me Spatial par dÃ©faut : palette Ã©motionnellement neutre/froide. Fond quasi-noir + violet â€” certains profils TSA associent cette palette Ã  de l'anxiÃ©tÃ© (Ludlow, 2012).
- Zone de rÃ©solution avec `data-learner-context` : correctement neutre. âœ…
- Header de navigation toujours visible pendant la rÃ©solution : 7 liens + icÃ´nes = fond de distracteurs constants.
- `badge-card-earned-compact:hover` : transition `max-height 0.3s ease` dans `@media (hover: hover)` **sans** protection `prefers-reduced-motion` â€” bug accessibilitÃ© prouvÃ© dans le code.
- `ChallengeSolver` : les visualisations interactives (`ChallengeVisualRenderer`) peuvent dÃ©clencher des rendus complexes. Aucune option de simplification visuelle.
- âš ï¸ **Le flux apprenant est protÃ©gÃ©. Le reste de l'interface ne l'est pas.**

**Parent/Enseignant**

- StatsCards dashboard : toutes au mÃªme poids visuel, hiÃ©rarchie "qu'est-ce qui compte le plus" inexistante.
- `DashboardLastUpdate` : "il y a 3h" sans contexte de quoi a Ã©tÃ© mis Ã  jour.
- `ExportButton` invisible mobile.
- Aucune vue "mes Ã©lÃ¨ves / mon enfant" â€” chemin inexistant.
- âš ï¸ **Dashboard = outil adulte non finalisÃ©, pas encore outil parent/enseignant.**

---

## Plan d'action â€” NI-9 Ã  NI-13

> Lots issus de l'audit terrain 2026-04-04. ComplÃ¨tent NI-1 Ã  NI-8.

### NI-9 â€” Feedback post-rÃ©ponse : dÃ©cision animations `success-pulse` / `error-shake`

**PrioritÃ©** : P2 | **Effort** : XS | **Statut** : Ã€ faire

Les keyframes `success-pulse` et `error-shake` sont dÃ©finis dans `globals.css` mais jamais appliquÃ©s.

DÃ©cision de design documentÃ©e :

- Activer sur surface apprenant = risque d'extraneous load post-rÃ©flexion (Mayer, 2009). Ã€ Ã©valuer.
- Activer uniquement si `!shouldReduceMotion` et avec durÃ©e courte (â‰¤ 400ms) pour limiter la distraction.
- Alternative : signal non-cinÃ©tique (couleur + icÃ´ne + son optionnel).

**Scope** : `ExerciseSolverFeedback`, feedback ChallengeSolver.
**DÃ©cision Ã  prendre** : activer `success-pulse` (scale 1â†’1.03â†’1, 300ms) + `error-shake` (translateX Â±4px, 300ms) sous garde `shouldReduceMotion`.

### NI-10 â€” Indice sous le fold mobile : remonter avant les choix

**PrioritÃ©** : P2 | **Effort** : S | **Statut** : Ã€ faire

Le bouton "Voir un indice" est rendu aprÃ¨s les choix QCM et le bouton Valider. Sur mobile 375px :

- 4 boutons QCM `py-6` â‰ˆ 300px
- Bouton Valider + microcopy â‰ˆ 80px
- Total avant l'indice : ~380px â†’ invisible sans scroll

RÃ©fÃ©rence : W3C COGA 2.2 "Provide help for complex information". Un enfant bloquÃ© ne scroll pas pour chercher de l'aide.

**Fix** : DÃ©placer le bouton indice _avant_ les choix (typographie discrÃ¨te, `text-xs text-muted-foreground`, ne concurrence pas les rÃ©ponses) ou sticky en bas de la zone de rÃ©solution.

**Scope** : `ExerciseSolverFeedback` layout, `ExerciseSolver` composition.

### NI-11 â€” Badge hover-reveal : protection `prefers-reduced-motion` manquante

**PrioritÃ©** : P2 | **Effort** : XS | **Statut** : âœ… FAIT 2026-03-30

Dans `globals.css`, le bloc :

```css
@media (hover: hover) {
  .badge-card-earned-compact .badge-card-expandable {
    transition:
      max-height 0.3s ease,
      opacity 0.25s ease;
  }
}
```

est hors de tout `@media (prefers-reduced-motion: reduce)`. La transition `max-height` se dÃ©clenche mÃªme si l'utilisateur a activÃ© `prefers-reduced-motion` au niveau OS.

RÃ©fÃ©rence WCAG 2.1 SC 2.3.3 (Animation from Interactions â€” AAA). Pour un profil TSA/TDAH avec `prefers-reduced-motion`, ce mouvement non protÃ©gÃ© est un bug d'accessibilitÃ© rÃ©el.

**Fix** : Encapsuler la transition `max-height` dans `@media (prefers-reduced-motion: no-preference)`.

**Scope** : `globals.css`, bloc `.badge-card-earned-compact`.

### NI-12 â€” `AcademyStatsWidget` : supprimer `backdrop-blur-md`

**PrioritÃ©** : P3 | **Effort** : XS | **Statut** : Ã€ faire

`AcademyStatsWidget.tsx` utilise `backdrop-blur-md` dans :

- Le skeleton loader (`Card className="... backdrop-blur-md"`)
- Le rendu final (`Card className="... backdrop-blur-md"`)

Ce glassmorphism subsiste aprÃ¨s NI-6 (le composant est conditionnÃ© mais non modifiÃ©). Hors `data-learner-context` mais visible en homepage pour les visiteurs non-connectÃ©s.

**Fix** : Retirer `backdrop-blur-md` des deux `Card`. Remplacer par `bg-card/60` ou fond solide.

**Scope** : `AcademyStatsWidget.tsx`.

### NI-13 â€” Dashboard : vue simplifiÃ©e conditionnelle au rÃ´le

**PrioritÃ©** : P1 | **Effort** : M | **Statut** : Ã€ planifier

Le dashboard prÃ©sente la mÃªme interface au rÃ´le `student` (enfant de 8 ans) et au rÃ´le parent/admin. L'enfant connectÃ© voit : 5 onglets, 16 widgets, graphiques d'axes temporels, bouton export.

C'est la surface la plus visitÃ©e aprÃ¨s la rÃ©solution â€” et la plus mal adaptÃ©e Ã  l'audience principale.

**Fix court terme** : Conditionner l'affichage dans `dashboard/page.tsx` au rÃ´le utilisateur :

- RÃ´le `student` : streak, niveau, bouton "Commencer un exercice", sans onglets Progression / Mon Profil / graphiques.
- RÃ´le parent/admin : vue actuelle inchangÃ©e.

**Fix long terme** : NI-4 (page apprenant sÃ©parÃ©e).

**Scope** : `app/dashboard/page.tsx`, hooks `useAuth` pour rÃ´le.

---

## Mise Ã  jour vÃ©ritÃ© code â€” 2026-04-03

Ce document conserve le dÃ©bat et le plan d'origine. Le bloc ci-dessous reflÃ¨te la rÃ©alitÃ©
du code relu au 2026-04-03 dans le worktree local.

**LÃ©gende**

- âœ… ImplÃ©mentÃ© localement et relu dans le code
- â³ Ã€ faire ou non confirmÃ© dans le code actuel
- ðŸ’¤ Backlog assumÃ©

**ConfirmÃ© dans le code**

- `NI-1` : `LearnerCard` et `LearnerLayout` existent et sont bien rÃ©servÃ©s au flux apprenant.
- `NI-2` : le token `--bg-learner` est bien portÃ© par thÃ¨me et consommÃ© par la couche apprenant.
- `NI-3` : l'intÃ©gration exercise/challenge est en place ; le dÃ©fi a retrouvÃ© une largeur cohÃ©rente (`5xl`) et le `tabIndex` clavier du QCM est alignÃ© sur le solver exercice.
- `NI-6` : la section features de la home a Ã©tÃ© refondue ; `AcademyStatsWidget` n'apparaÃ®t plus pour les utilisateurs authentifiÃ©s et est gardÃ© derriÃ¨re `!isAuthLoading && !isAuthenticated`.
- `NI-7` : le sweep global est passÃ© en opt-in `.hover-sweep`, puis le lift/glow global des boutons et cards a Ã©tÃ© neutralisÃ© dans `[data-learner-context]`.
- `NI-8` : la microcopy d'affordance sous le bouton Valider est prÃ©sente dans `ExerciseSolver`, `ExerciseModal` et `ChallengeSolver` via `aria-describedby` + texte visible.

**Toujours ouverts**

- `NI-5` : l'opt-in `flat` sur `<Card>` n'est pas encore livrÃ©.
- `NI-4` : la page apprenant dÃ©diÃ©e reste un backlog produit, pas un quick win.

---

## Mise Ã  jour vÃ©ritÃ© code â€” 2026-04-04 (sprint NI-4 Ã  NI-13 + correctifs Octopus)

> Audit conduit et corrections appliquÃ©es dans le worktree local puis committÃ©es en lots atomiques.
> VÃ©rification Octopus Challenge intÃ©grÃ©e â€” 4 points factuels corrigÃ©s.

### Ce qui a Ã©tÃ© livrÃ© dans ce sprint

**NI-4 â€” Page `/home-learner` apprenant** (`app/home-learner/page.tsx`)

- `LearnerLayout maxWidth="2xl"`, structure 100 % linÃ©aire, zÃ©ro onglets
- Page-map chips d'ancrage (COGA 4.1.1 â€” prÃ©visibilitÃ© structurelle) : `#section-reviews`, `#section-challenges`, `#section-progress`
- `scroll-behavior: smooth` sur `html, body` dans `globals.css` ; `scroll-mt-20` sur chaque section cible
- `SpacedRepetitionSummaryWidget` + `StudentChallengesBoard` intÃ©grÃ©s
- Section "RÃ©visions" toujours rendue (ancre jamais morte) : `isLoading` â†’ skeleton, `hasError` â†’ message localisÃ©, fallback `EMPTY_SPACED_REPETITION`
- Redirection post-login `apprenant -> /home-learner` dans `useAuth.ts`
- Nav Header : "Mon espace" pour `apprenant`, `Classement` visible dans la navigation principale, `Tableau de bord` relegue au menu profil

**NI-5 â€” Opt-in `flat` sur `<Card>`** (`components/ui/card.tsx`)

- Prop `flat?: boolean` ; `flat=true â†’ shadow-none` ; dÃ©faut global inchangÃ©
- 10 visualizations challenge migrÃ©es (`VisualRenderer`, `PuzzleRenderer`, `GraphRenderer`, `DefaultRenderer`, `SequenceRenderer`, `PatternRenderer`)

**NI-9 â€” Animations `success-pulse` / `error-shake`** (`globals.css` + solvers)

- DÃ©cision prise : **activÃ©es** (post-rÃ©flexion, durÃ©e â‰¤ 600ms, iteration: 1)
- `.feedback-success-animate` / `.feedback-error-animate` dans `globals.css`
- `prefers-reduced-motion: reduce â†’ animation: none !important`
- `role="status"` + `aria-live="polite"` + `aria-atomic="true"` sur les deux blocs feedback

**NI-11 â€” Badge hover-reveal `prefers-reduced-motion`** (`globals.css`)

- `max-height` transition dans `@media (prefers-reduced-motion: no-preference)` uniquement
- OpacitÃ© reste animÃ©e (pas de mouvement physique â€” conforme WCAG 2.1 SC 2.3.3)

**NI-12 â€” `AcademyStatsWidget` glassmorphism** (`AcademyStatsWidget.tsx`)

- `backdrop-blur-md` retirÃ© des deux `Card` (skeleton + rendu)
- `rounded-full bg-primary/10` icon-containers supprimÃ©s â†’ icÃ´nes directes
- `hover:scale-105` parasite supprimÃ©

**NI-13 â€” Boundary dashboard enfant/adulte** (`proxy.ts` + `ProtectedRoute` + routes frontend)

- `proxy.ts` applique maintenant le premier niveau de boundary sur `/home-learner`, `/dashboard` et `/admin`
- `ProtectedRoute` garde `allowedRoles` avec roles canoniques comme fallback client
- `/dashboard` reste la surface analytique dense, mais n'est plus interdit a `apprenant`
- `/home-learner` reste la home principale et protegee pour `apprenant`
- `apprenant` arrive sur `/home-learner` apres login, puis peut ouvrir `/dashboard` via une entree discrete du menu profil
- `isStudentView` et widgets apprenant retirÃ©s du dashboard (StudentChallengesBoard deplace dans `/home-learner`)
- Dashboard adulte par defaut ; boundary partage et type au niveau route serveur + frontend, sans redirect ad hoc locale a la page

### Correctifs Octopus Challenge (audit croisÃ© 2026-04-04)

| Bug Octopus                           | Verdict                     | Correction                                                                                                                                           |
| ------------------------------------- | --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| B1 â€” A1 `prefers-reduced-motion`    | âš ï¸ Partiellement rÃ©solu | `transform: none` et `transition: none` existent dÃ©jÃ  dans le bloc reduce ; un rÃ©siduel `box-shadow` hors learner context reste mineur mais rÃ©el |
| B2 â€” Ancre `#section-reviews` morte | âœ… CorrigÃ©                | Section toujours rendue avec `isLoading`/`hasError`                                                                                                  |
| B3 â€” TODO role apprenant absent     | âœ… CorrigÃ©                | boundary centralise sur roles canoniques dans `ProtectedRoute`, `useAuth.ts` et `Header.tsx`                                                         |
| Double bouton "Retour aux dÃ©fis"     | âœ… CorrigÃ©                | Bouton du bas supprimÃ© â€” lien discret haut + actions contextuelles suffisent                                                                      |

### Dettes rÃ©siduelles connues (non bloquantes)

| ID  | Surface                     | ProblÃ¨me                                                                                                                                                                                 | SÃ©vÃ©ritÃ© |
| --- | --------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| U1  | Partout                     | Jargon enfant rÃ©siduel Ã  la marge ("session entrelacÃ©e" en interne â€” UI dÃ©jÃ  neutralisÃ©e)                                                                                         | P3          |
| U2  | Solvers                     | Aucun onboarding contextuel pour un enfant pendant la rÃ©solution                                                                                                                         | P2          |
| U4  | Liste exercices             | 4 dropdowns visibles d'emblÃ©e (surcharge choix Schwartz 2004)                                                                                                                            | P2          |
| S2  | ThÃ¨me spatial              | Palette `#7c3aed` + `#0a0a0f` = fingerprint AI 2024 â€” dÃ©cision produit requise                                                                                                         | P3          |
| R1  | `dashboard/page.tsx`        | `SpacedRepetitionSummaryWidget` prÃ©sent dans dashboard adulte ET `/home-learner` â€” lÃ©gitime mais non documentÃ©                                                                       | P3          |
| R2  | Boundary surface protegee   | Boundary NI-13 durci par `proxy.ts` + `ProtectedRoute`. Reserve residuelle : `access_scope` / onboarding restent enrichis via backend sur les routes protegees, pas dans le JWT lui-meme. | P3          |
| O1  | `ExerciseSolverChoices.tsx` | `<input>` raw hors design system (dette antÃ©rieure, hors scope NI)                                                                                                                       | P3          |

---

## RÃ©capitulatif consolidÃ© â€” tous les lots

| Lot                                                            | PrioritÃ© | Effort | Scope                                            | Statut                                          |
| -------------------------------------------------------------- | --------- | ------ | ------------------------------------------------ | ----------------------------------------------- |
| NI-1 Composants apprenant (`LearnerCard`, `LearnerLayout`)     | P1        | S-M    | Solvers                                          | âœ… FAIT 2026-03-30                             |
| NI-2 Token `--bg-learner` par thÃ¨me                           | P1        | S      | `globals.css`                                    | âœ… FAIT 2026-03-30                             |
| NI-3 IntÃ©gration Solver (exercice + dÃ©fi)                    | P1        | S      | Solvers                                          | âœ… FAIT 2026-03-30                             |
| NI-4 Page apprenant tubulaire `/home-learner`                  | P2        | M      | Nouvelle page                                    | âœ… FAIT 2026-04-04                             |
| NI-5 Opt-in `flat` sur `<Card>`                                | P2        | XS     | Design system                                    | âœ… FAIT 2026-04-04                             |
| NI-6 Refonte section features accueil                          | P2        | S      | `app/page.tsx`                                   | âœ… FAIT 2026-03-30                             |
| NI-7 Suppression sweep effect global                           | P1        | XS     | `globals.css`                                    | âœ… FAIT 2026-03-30                             |
| NI-8 Microcopy bouton Valider grisÃ©                           | P2        | XS     | Solvers / modal exercice                         | âœ… FAIT 2026-03-30                             |
| NI-9 Animations `success-pulse` / `error-shake`                | P2        | XS     | `globals.css` + solvers                          | âœ… FAIT 2026-04-04                             |
| NI-10 Indice sous le fold mobile                               | P2        | S      | `ExerciseSolverChoices`                          | âœ… FAIT 2026-03-30                             |
| NI-11 Badge hover-reveal : protection `prefers-reduced-motion` | P2        | XS     | `globals.css`                                    | âœ… FAIT 2026-03-30                             |
| NI-12 `AcademyStatsWidget` : supprimer `backdrop-blur-md`      | P3        | XS     | `AcademyStatsWidget.tsx`                         | âœ… FAIT 2026-04-04                             |
| NI-13 Boundary dashboard enfant / adulte                       | P1        | M      | `proxy.ts` + `ProtectedRoute` + routes protegees | âœ… FAIT 2026-04-05 (boundary serveur + client) |

**Tous les lots NI-1 Ã  NI-13 sont livrÃ©s et committÃ©s.**
**Reserve documentee** : `NI-13` est maintenant porte par un proxy + un guard frontend partage. Le dashboard n'est plus interdit a l'apprenant ; il reste simplement de-priorise dans la navigation.

Dettes rÃ©siduelles : voir tableau ci-dessus. Aucune n'est bloquante pour la mise en production du flux apprenant.
