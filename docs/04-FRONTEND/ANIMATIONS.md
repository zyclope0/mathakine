# Animations Frontend - Mathakine

> Statut : reference active
> Updated : 2026-04-05
> Scope : motion visible, decor spatial, garde-fous a11y

---

## Verite actuelle

Les animations Mathakine sont separees en deux familles :

1. **Motion UI**
   - `Header.tsx`
   - `PageTransition.tsx`
   - `InstallPrompt.tsx`
   - widgets dashboard qui utilisent `useAccessibleAnimation()`

2. **Decor spatial**
   - `Starfield.tsx`
   - `Planet.tsx`
   - `Particles.tsx`
   - `DinoFloating.tsx`
   - `UnicornFloating.tsx`

Le conteneur decoratif commun est `SpatialBackground.tsx`.

---

## Regle EdTech

Pendant la phase de reflexion apprenant, le decor ne doit pas prendre le dessus.

Concretement :

- les surfaces apprenant utilisent `LearnerLayout` / `LearnerCard`
- `data-learner-context` neutralise les lifts et bruits interactifs non essentiels
- le feedback anime ne se declenche qu'apres la reponse
- le decor spatial se coupe en `focusMode` ou `reducedMotion`

---

## Composants decoratifs

| Composant         | Role                      | Notes                                  |
| ----------------- | ------------------------- | -------------------------------------- |
| `Starfield`       | fond etoiles              | adapte ses couleurs au theme           |
| `Planet`          | objet decoratif principal | `dino` et `unicorn` ont un rendu dedie |
| `Particles`       | profondeur douce          | theme-aware                            |
| `DinoFloating`    | accent theme dino         | visible uniquement sur `dino`          |
| `UnicornFloating` | accent theme licorne      | visible uniquement sur `unicorn`       |

Le decor suit maintenant **8 themes**, pas 7.

---

## Motion UI

Les surfaces globales les plus exposees utilisent `LazyMotion` + `domAnimation` :

- `frontend/components/layout/Header.tsx`
- `frontend/components/layout/PageTransition.tsx`
- `frontend/components/pwa/InstallPrompt.tsx`

Objectif :

- garder des transitions lisibles
- reduire le cout motion
- respecter les preferences d'accessibilite

---

## Accessibilite motion

La source de verite est `frontend/lib/hooks/useAccessibleAnimation.ts`.

Le hook combine :

- preference store `reducedMotion`
- preference store `focusMode`
- preference systeme `prefers-reduced-motion`
- garde SSR-safe

Nuance importante :

- sur les charts dashboard, `useAccessibleAnimation({ respectFocusMode: false })`
  permet de respecter `reducedMotion` et la preference systeme sans bloquer
  inutilement l'animation juste parce que `focusMode` est active ailleurs

---

## Feedback anime apprenant

Deux classes sont actives :

- `.feedback-success-animate`
- `.feedback-error-animate`

Usage :

- feedback post-reponse dans les solveurs
- une seule fois
- coupe automatiquement sous `prefers-reduced-motion: reduce`

Ces animations sont considerees acceptables parce qu'elles arrivent **apres**
la reponse, pas pendant la reflexion.

---

## A ne pas faire

- reintroduire un sweep global sur tous les boutons/cartes
- ajouter des animations de reflexion dans les solveurs apprenant
- ignorer `useAccessibleAnimation()` sur les composants motion
- documenter encore 7 themes ou l'ancien theme `peach`

---

## References

- [ACCESSIBILITY.md](ACCESSIBILITY.md)
- [THEMES.md](../02-FEATURES/THEMES.md)
- [UX_SURFACES.md](UX_SURFACES.md)
