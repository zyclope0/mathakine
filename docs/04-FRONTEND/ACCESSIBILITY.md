# Accessibilite Frontend - Mathakine

> Statut : reference active
> Updated : 2026-04-05
> Standards : WCAG AA minimum, ambition AAA sur les surfaces critiques

---

## Verite actuelle

Mathakine conserve **5 modes d'accessibilite** dans `accessibilityStore` :

1. contraste eleve
2. texte agrandi
3. reduction des animations
4. mode dyslexie
5. focus mode TSA/TDAH

Leur etat est persiste via Zustand et applique au document HTML.

---

## Source de verite code

- Store : `frontend/lib/stores/accessibilityStore.ts`
- Styles globaux : `frontend/app/globals.css`
- Toolbar : `frontend/components/accessibility/AccessibilityToolbar.tsx`
- Hook motion : `frontend/lib/hooks/useAccessibleAnimation.ts`
- Preference systeme : `frontend/lib/hooks/useSystemReducedMotion.ts`

---

## Mouvement et reduction motion

`useAccessibleAnimation()` est la reference active.

Le hook :

- lit `reducedMotion`
- lit `focusMode`
- lit `prefers-reduced-motion`
- reste SSR-safe

Politique actuelle :

- par defaut, `focusMode` compte dans `shouldReduceMotion`
- exception volontaire sur les charts dashboard :
  `useAccessibleAnimation({ respectFocusMode: false })`

Cela permet :

- d'eviter le bruit visuel pendant les parcours apprenant
- sans casser inutilement les animations de visualisation du dashboard adulte

---

## Focus mode et surface apprenant

Le focus mode vise la reduction maximale des distracteurs.

Etat actuel :

- decor spatial masque
- animations coupees
- focus visible renforce
- la couche apprenant ajoute `data-learner-context` pour neutraliser lifts et hover noise

Cette neutralisation complete :

- les solveurs
- `home-learner`
- les composants `LearnerCard` / `LearnerLayout`

---

## Theme switching

Le changement de theme et le passage clair/sombre utilisent
`html.theme-switching` pour couper temporairement les transitions globales.

But :

- eviter l'effet saccade / couches de couleur successives
- garder un changement de theme plus propre sur desktop et mobile

---

## Feedback et etats

Sur les surfaces apprenant :

- les hints de validation sont visibles sous le bouton grise
- les feedbacks succes/erreur ont des classes dediees
- ces animations sont coupees si `prefers-reduced-motion` l'exige

Sur les charts :

- `isAnimationActive={!shouldReduceMotion}` reste la regle
- les charts dashboard respectent le systeme et le store motion

---

## Checklist composant

- labels et roles ARIA presents
- focus visible testable au clavier
- cible tactile >= 44x44
- aucun mouvement non essentiel pendant la reflexion
- `useAccessibleAnimation()` ou garde CSS equivalente sur tout composant anime
- fallback de chargement ou erreur au lieu d'un crash

---

## Limites connues

- le dashboard adulte reste plus dense que la surface apprenant
- certaines transitions hors `data-learner-context` restent volontaires pour les surfaces non apprenant
- le role `parent` n'existe pas encore comme surface distincte

---

## References

- [ANIMATIONS.md](ANIMATIONS.md)
- [THEMES.md](../02-FEATURES/THEMES.md)
- [UX_SURFACES.md](UX_SURFACES.md)
