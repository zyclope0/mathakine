# Accessibilité Frontend — Mathakine

> Dernière mise à jour : 03/03/2026  
> Standards : WCAG 2.1 AAA — Cible : enfants 5-20 ans, TSA/TDAH

---

## 5 Modes d'accessibilité

Tous accessibles via `AccessibilityToolbar` (bouton flottant bas-droit) et persistés dans `localStorage` (Zustand `accessibilityStore`).

### 1. Contraste élevé — `Alt+C`

- Contraste minimum 7:1 (vs 4.5:1 standard)
- Bordures renforcées, couleurs plus distinctes
- CSS : classe `.high-contrast` sur `<html>` — définie dans `globals.css` (tokens shadcn/ui complets)
- `@media (prefers-contrast: high)` — défini dans `globals.css` avec les mêmes tokens (background, foreground, border, primary…)
- **Note** : `accessibility.css` ne redéfinit plus ces variables pour éviter les conflits (nettoyage P4.3 — 03/03/2026)

### 2. Texte agrandi — `Alt+T`

- Taille de texte +20%, espacement augmenté
- CSS : classe `.large-text` sur `<html>`

### 3. Réduction animations — `Alt+M`

- Animations désactivées ou réduites
- Respecte aussi `prefers-reduced-motion` (CSS media query)
- CSS : classe `.reduced-motion` sur `<html>`
- Hook : `useAccessibleAnimation()` désactive automatiquement

### 4. Mode dyslexie — `Alt+D`

- Police OpenDyslexic si disponible
- Espacement lettres augmenté
- CSS : classe `.dyslexia-mode` sur `<html>`

### 5. Mode Focus TSA/TDAH — `Alt+F`

**Objectif** : Réduction maximale des distractions visuelles.

- Masque : footer, sidebar, FeedbackFab, recommandations, éléments décoratifs (Starfield, Particles, Planet)
- Désactive toutes les animations
- Focus visible très renforcé (4px outline + 8px shadow)
- **Conserve le thème choisi** — ne modifie pas les couleurs
- CSS : classe `.focus-mode` sur `<html>`

**État actuel (22/02/2026)** :
- ✅ Application store + classes CSS fonctionnelle
- ✅ Raccourci Alt+F actif
- ✅ Animations spatiales désactivées (Starfield, Particles, Planet retournent `null`)
- ✅ FeedbackFab masqué (classe `feedback-fab`)
- ✅ Source de vérité unique : `globals.css` (le bloc dupliqué dans `accessibility.css` a été supprimé)

**Points d'attention** :
- `line-height: 1.9` sur tous les `div` — peut impacter certains layouts
- `padding: 2rem` sur toutes les cards — peut gonfler les cartes compactes
- Option de masquer thème/langue dans le header possible mais non implémentée

---

## Bonnes pratiques

### ARIA Labels

```tsx
// ✅ Toujours labelliser les boutons icône
<button aria-label="Fermer la modale">
  <X className="h-4 w-4" aria-hidden="true" />
</button>
```

### Navigation clavier

```tsx
// Radiogroup avec flèches
<div role="radiogroup" aria-label="Choix de réponses">
  {choices.map((choice, i) => (
    <button
      role="radio"
      aria-checked={selectedIndex === i}
      tabIndex={selectedIndex === i ? 0 : -1}
      onKeyDown={(e) => {
        if (e.key === 'ArrowDown') selectNext();
        if (e.key === 'ArrowUp') selectPrevious();
      }}
    >
      {choice}
    </button>
  ))}
</div>
```

### Focus visible

```css
/* Standard */
*:focus-visible {
  outline: 2px solid var(--ring);
  outline-offset: 2px;
}

/* Mode Focus TSA/TDAH */
.focus-mode *:focus-visible {
  outline: 4px solid var(--focus-ring);
  outline-offset: 4px;
  box-shadow: 0 0 0 8px rgba(139, 92, 246, 0.2);
}
```

### Animations accessibles

```tsx
import { useAccessibleAnimation } from '@/lib/hooks/useAccessibleAnimation';

function MyComponent() {
  const { createVariants, shouldReduceMotion } = useAccessibleAnimation();

  const variants = createVariants({
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
  });

  return (
    <motion.div
      variants={variants}
      animate={shouldReduceMotion ? {} : 'animate'}
    >
      Contenu
    </motion.div>
  );
}
```

**Règles animations** : max 250ms, easing doux, pas de boucles infinies.

**Composants qui utilisent `useAccessibleAnimation`** :
- `GraphRenderer.tsx` — animations d'entrée Framer Motion (nœuds SVG + arêtes), désactivées si `shouldReduceMotion`
- `DeductionRenderer.tsx` — transitions CSS hover (via `transition-colors`), désactivées si `shouldReduceMotion`
- `ProgressChart.tsx` + `DailyExercisesChart.tsx` — `isAnimationActive` Recharts, désactivé si `shouldReduceMotion`
- `ProgressChart.tsx` + `DailyExercisesChart.tsx` — `isAnimationActive` Recharts

**Recharts** : utiliser `isAnimationActive={!shouldReduceMotion}` sur `<Line>`, `<Bar>`, `<Area>`.

**CSS transitions** : préférer une variable conditionnelle plutôt qu'une classe Tailwind fixe :
```tsx
const hoverTransition = shouldReduceMotion ? "" : "transition-colors";
// Puis dans le JSX :
className={`... ${hoverTransition}`}
```

### Formulaires

```tsx
// Labels associés
<Label htmlFor="username">Nom d'utilisateur</Label>
<Input id="username" aria-required="true" />

// Messages d'erreur
<Input aria-invalid={hasError} aria-describedby={hasError ? "err" : undefined} />
{hasError && <p id="err" role="alert" className="text-destructive">Erreur</p>}
```

### Modales (Dialog)

- Focus automatique sur `DialogTitle` à l'ouverture
- `Escape` ferme la modale (géré par Radix UI)
- Focus retourne au déclencheur à la fermeture

---

## Standards de contraste

| Élément | WCAG AA | Objectif AAA |
|---|---|---|
| Texte normal | 4.5:1 | 7:1 |
| Texte large (18pt+) | 3:1 | 4.5:1 |
| Composants UI | 3:1 | 4.5:1 |

---

## Tests d'accessibilité

### Audit automatique (dev only)

```tsx
import { WCAGAudit } from '@/components/accessibility/WCAGAudit';
// Intégré dans app/layout.tsx uniquement en développement
```

Utilise `@axe-core/react` — résultats dans la console.

### Tests unitaires (Vitest)

```tsx
import { axe, toHaveNoViolations } from 'jest-axe';
expect.extend(toHaveNoViolations);

test('no a11y violations', async () => {
  const { container } = render(<MyComponent />);
  expect(await axe(container)).toHaveNoViolations();
});
```

### Tests E2E (Playwright)

```tsx
test('keyboard accessible', async ({ page }) => {
  await page.goto('/challenges');
  await page.keyboard.press('Tab');
  // Vérifier focus visible
});
```

### Checklist manuelle par composant

- [ ] ARIA labels présents sur boutons icône (y compris `aria-label` i18n — pas de strings hardcodées)
- [ ] Navigation clavier fonctionnelle
- [ ] Focus visible en tout point
- [ ] Contraste suffisant (WebAIM Contrast Checker)
- [ ] Animations respectent `shouldReduceMotion` (hook) **et** `prefers-reduced-motion` (CSS)
- [ ] Images ont texte alternatif descriptif (`alt` non vide — utiliser nom/code si icône)
- [ ] Formulaires ont labels associés — utiliser `<Input>` shadcn/ui, pas `<input>` raw
- [ ] Messages d'erreur avec `role="alert"`

### Checklist par page

- [ ] `<title>` unique
- [ ] Structure sémantique (`<header>`, `<main>`, `<footer>`)
- [ ] Attribut `lang` sur `<html>`
- [ ] Navigation principale accessible au clavier
- [ ] Zoom 200% fonctionnel

---

## Ressources

- [WCAG 2.1 Quick Reference](https://www.w3.org/WAI/WCAG21/quickref/)
- [ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [axe DevTools](https://www.deque.com/axe/devtools/)
- Lecteurs d'écran : NVDA (Windows, gratuit), VoiceOver (macOS/iOS), TalkBack (Android)
