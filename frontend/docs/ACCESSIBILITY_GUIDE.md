# ♿ Guide d'Accessibilité - Frontend Mathakine

**Date** : 9 Novembre 2025  
**Standards** : WCAG 2.1 AAA  
**Cible** : Enfants 5-20 ans avec TSA/TDAH

---

## 📋 **Table des Matières**

- [Standards WCAG 2.1 AAA](#standards-wcag-21-aaa)
- [Modes d'Accessibilité](#modes-daccessibilité)
- [Bonnes Pratiques](#bonnes-pratiques)
- [Tests d'Accessibilité](#tests-daccessibilité)
- [Ressources](#ressources)

---

## 🎯 **Standards WCAG 2.1 AAA**

### **Niveaux de Conformité**

- **Niveau A** : Minimum requis
- **Niveau AA** : Recommandé (notre cible minimale)
- **Niveau AAA** : Optimal (notre objectif)

### **Principes WCAG**

1. **Perceptible** : L'information doit être présentable de manière perceptible
2. **Utilisable** : Les composants doivent être utilisables
3. **Compréhensible** : L'information doit être compréhensible
4. **Robuste** : Le contenu doit être robuste et interprétable

---

## 🛠️ **Modes d'Accessibilité**

### **1. Mode Contraste Élevé**

**Activation** : Bouton dans `AccessibilityToolbar` ou `Alt+C`

**Effets** :
- Contraste minimum 7:1 (au lieu de 4.5:1)
- Bordures renforcées
- Couleurs plus distinctes

**CSS** : Classe `.high-contrast` appliquée à `<html>`

---

### **2. Mode Texte Agrandi**

**Activation** : Bouton dans `AccessibilityToolbar` ou `Alt+T`

**Effets** :
- Taille de texte augmentée de 20%
- Espacement augmenté
- Meilleure lisibilité

**CSS** : Classe `.large-text` appliquée à `<html>`

---

### **3. Réduction Animations**

**Activation** : Bouton dans `AccessibilityToolbar` ou `Alt+M`

**Effets** :
- Animations désactivées ou réduites
- Transitions simplifiées
- Respect `prefers-reduced-motion`

**CSS** : Classe `.reduced-motion` appliquée à `<html>`

**Hook** : `useAccessibleAnimation()` désactive automatiquement les animations

---

### **4. Mode Dyslexie**

**Activation** : Bouton dans `AccessibilityToolbar` ou `Alt+D`

**Effets** :
- Police adaptée (OpenDyslexic si disponible)
- Espacement lettres augmenté
- Meilleure distinction des caractères

**CSS** : Classe `.dyslexia-mode` appliquée à `<html>`

---

### **5. Mode Focus TSA/TDAH**

**Activation** : Bouton dans `AccessibilityToolbar`

**Effets** :
- Masquage distractions (sidebar, footer, recommandations)
- Zone de focus agrandie
- Animations désactivées
- Focus visible renforcé
- Éléments décoratifs masqués (étoiles, particules)

**CSS** : Classe `.focus-mode` appliquée à `<html>`

**Phase 1** : Mode unique avec fonctionnalités essentielles  
**Phase 2** (futur) : Niveaux 2 et 3 avec options avancées

---

## ✅ **Bonnes Pratiques**

### **1. ARIA Labels**

**Toujours fournir des labels** :

```typescript
// ✅ Bon
<button aria-label="Fermer la modale">
  <X className="h-4 w-4" aria-hidden="true" />
</button>

// ❌ Mauvais
<button>
  <X className="h-4 w-4" />
</button>
```

---

### **2. Navigation Clavier**

**Tous les éléments interactifs doivent être accessibles au clavier** :

```typescript
// ✅ Bon
<button
  onKeyDown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      handleClick();
    }
  }}
>
  Cliquer
</button>
```

**Radiogroups** : Utiliser `role="radiogroup"` et navigation flèches :

```typescript
<div role="radiogroup" aria-label="Choix de réponses">
  {choices.map((choice, index) => (
    <button
      role="radio"
      aria-checked={isSelected}
      tabIndex={isSelected ? 0 : -1}
      onKeyDown={(e) => {
        // Navigation flèches
        if (e.key === 'ArrowDown' || e.key === 'ArrowRight') {
          // Sélectionner suivant
        }
      }}
    >
      {choice}
    </button>
  ))}
</div>
```

---

### **3. Contraste des Couleurs**

**Minimum WCAG AA** : 4.5:1 pour texte normal, 3:1 pour texte large  
**Objectif WCAG AAA** : 7:1 pour texte normal, 4.5:1 pour texte large

**Vérification** :
- Utiliser [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- Tester avec outils de développement
- Utiliser `@axe-core/react` pour audit automatique

**Exemple** :
```css
/* ✅ Bon contraste */
.text-primary {
  color: #7c3aed; /* Contraste 4.6:1 avec blanc */
}

/* ✅ Meilleur contraste pour petits textes */
.text-primary-on-dark {
  color: #a78bfa; /* Contraste 5.2:1 avec fond sombre */
}
```

---

### **4. Focus Visible**

**Toujours rendre le focus visible** :

```css
/* Focus visible renforcé */
*:focus-visible {
  outline: 2px solid var(--ring);
  outline-offset: 2px;
}
```

**Mode Focus TSA/TDAH** :
```css
.focus-mode *:focus-visible {
  outline: 4px solid var(--focus-ring);
  outline-offset: 4px;
  box-shadow: 0 0 0 8px rgba(139, 92, 246, 0.2);
}
```

---

### **5. Animations Accessibles**

**Utiliser le hook `useAccessibleAnimation`** :

```typescript
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

**Règles** :
- Durées courtes (150-250ms)
- Easing doux
- Pas de boucles infinies
- Respect `prefers-reduced-motion`

---

### **6. Images et Media**

**Toujours fournir un texte alternatif** :

```typescript
// ✅ Bon
<Image 
  src="/image.jpg" 
  alt="Description de l'image"
  aria-label="Description détaillée si nécessaire"
/>

// ❌ Mauvais
<Image src="/image.jpg" />
```

**Images décoratives** :
```typescript
<img src="/decoration.jpg" alt="" aria-hidden="true" />
```

---

### **7. Formulaires**

**Toujours associer labels aux inputs** :

```typescript
// ✅ Bon
<div>
  <Label htmlFor="username">Nom d'utilisateur</Label>
  <Input id="username" aria-required="true" />
</div>

// ✅ Alternative avec aria-label
<Input 
  aria-label="Nom d'utilisateur"
  aria-required="true"
/>
```

**Messages d'erreur** :
```typescript
<Input 
  aria-invalid={hasError}
  aria-describedby={hasError ? "error-message" : undefined}
/>
{hasError && (
  <p id="error-message" role="alert">
    Message d'erreur
  </p>
)}
```

---

### **8. Modales et Dialogs**

**Toujours gérer le focus** :

```typescript
<Dialog>
  <DialogTrigger>Ouvrir</DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Focus automatique ici</DialogTitle>
    </DialogHeader>
    {/* Contenu */}
  </DialogContent>
</Dialog>
```

**Fermeture** :
- Toujours prévoir `Escape` pour fermer
- Bouton de fermeture visible
- Focus retour au déclencheur après fermeture

---

## 🧪 **Tests d'Accessibilité**

### **1. Audit Automatique**

**Composant WCAGAudit** :

```typescript
import { WCAGAudit } from '@/components/accessibility/WCAGAudit';

// Dans layout.tsx
<WCAGAudit />
```

**Outils** :
- `@axe-core/react` : Audit automatique
- Chrome DevTools : Lighthouse accessibility
- WAVE : Extension navigateur

---

### **2. Tests Manuels**

**Checklist** :
- [ ] Navigation clavier complète
- [ ] Focus visible partout
- [ ] Contraste suffisant (outil de vérification)
- [ ] Lecteur d'écran (NVDA, JAWS, VoiceOver)
- [ ] Zoom 200% fonctionnel
- [ ] Mode contraste élevé fonctionnel

---

### **3. Tests Automatisés**

**Tests Vitest** :

```typescript
import { render, screen } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

test('should have no accessibility violations', async () => {
  const { container } = render(<MyComponent />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

**Tests Playwright** :

```typescript
import { test, expect } from '@playwright/test';

test('should be keyboard accessible', async ({ page }) => {
  await page.goto('/');
  await page.keyboard.press('Tab');
  // Vérifier que le focus est visible
});
```

---

## 🎯 **Standards Spécifiques**

### **Contraste Minimum**

| Élément | WCAG AA | WCAG AAA (Objectif) |
|---------|---------|---------------------|
| Texte normal | 4.5:1 | 7:1 |
| Texte large (18pt+) | 3:1 | 4.5:1 |
| Composants UI | 3:1 | 4.5:1 |

### **Taille de Focus**

- **Minimum** : 2px outline
- **Recommandé** : 4px outline avec offset
- **Mode Focus TSA/TDAH** : 4px outline + 8px shadow

### **Durée Animations**

- **Maximum** : 250ms pour interactions
- **Recommandé** : 150-200ms
- **Réduction** : Désactiver si `reducedMotion` activé

---

## 📚 **Ressources**

### **Documentation**

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)
- [WebAIM Resources](https://webaim.org/resources/)

### **Outils**

- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [WAVE Browser Extension](https://wave.webaim.org/extension/)
- [axe DevTools](https://www.deque.com/axe/devtools/)

### **Lecteurs d'Écran**

- **NVDA** : Windows (gratuit)
- **JAWS** : Windows (payant)
- **VoiceOver** : macOS/iOS (intégré)
- **TalkBack** : Android (intégré)

---

## ✅ **Checklist d'Accessibilité**

### **Pour Chaque Composant**

- [ ] ARIA labels présents
- [ ] Navigation clavier fonctionnelle
- [ ] Focus visible
- [ ] Contraste suffisant
- [ ] Animations respectent `reducedMotion`
- [ ] Images ont `alt` text
- [ ] Formulaires ont labels associés
- [ ] Messages d'erreur accessibles
- [ ] Tests d'accessibilité passés

### **Pour Chaque Page**

- [ ] Titre de page unique (`<title>`)
- [ ] Structure sémantique (`<header>`, `<main>`, `<footer>`)
- [ ] Navigation principale accessible
- [ ] Skip links si nécessaire
- [ ] Langue du document définie (`lang`)

---

## 🚀 **Exemples Concrets**

### **Bouton Accessible**

```typescript
<Button
  onClick={handleClick}
  aria-label="Valider la réponse"
  aria-busy={isLoading}
  disabled={isLoading}
>
  {isLoading ? (
    <>
      <Loader2 className="mr-2 h-4 w-4 animate-spin" aria-hidden="true" />
      Validation...
    </>
  ) : (
    'Valider'
  )}
</Button>
```

### **Input Accessible**

```typescript
<div>
  <Label htmlFor="answer">Réponse</Label>
  <Input
    id="answer"
    type="text"
    value={answer}
    onChange={(e) => setAnswer(e.target.value)}
    aria-required="true"
    aria-invalid={hasError}
    aria-describedby={hasError ? "error-message" : undefined}
    onKeyDown={(e) => {
      if (e.key === 'Enter' && answer.trim()) {
        handleSubmit();
      }
    }}
  />
  {hasError && (
    <p id="error-message" role="alert" className="text-destructive">
      Erreur de validation
    </p>
  )}
</div>
```

### **Radiogroup Accessible**

```typescript
<div 
  role="radiogroup" 
  aria-label="Choix de réponses"
  onKeyDown={(e) => {
    // Navigation flèches
    if (e.key === 'ArrowDown' || e.key === 'ArrowRight') {
      selectNext();
    } else if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') {
      selectPrevious();
    }
  }}
>
  {choices.map((choice, index) => (
    <button
      key={index}
      role="radio"
      aria-checked={selectedIndex === index}
      tabIndex={selectedIndex === index ? 0 : -1}
      onClick={() => selectChoice(index)}
    >
      {choice}
    </button>
  ))}
</div>
```

---

## 📝 **Notes Importantes**

### **Mode Focus TSA/TDAH**

Ce mode est spécifiquement conçu pour les utilisateurs avec TSA/TDAH :
- Réduction maximale des distractions
- Focus sur la tâche principale uniquement
- Animations désactivées
- Focus visible très renforcé

**Phase 1** : Mode unique avec fonctionnalités essentielles  
**Phase 2** (futur) : Niveaux supplémentaires avec options avancées

---

## 🔗 **Ressources Internes**

- [Composant AccessibilityToolbar](../components/accessibility/AccessibilityToolbar.tsx)
- [Hook useAccessibleAnimation](../lib/hooks/useAccessibleAnimation.ts)
- [Styles accessibilité](../../styles/accessibility.css)

---

**Dernière mise à jour** : 9 Novembre 2025

