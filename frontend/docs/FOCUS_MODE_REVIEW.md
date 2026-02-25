# Revue Mode Focus TSA/TDAH

**Date** : 2025-02-22  
**Objectif** : Audit du mode focus (Alt+F) pour TSA/TDAH

---

## Ce qui fonctionne

| Aspect                                                   | Statut             |
| -------------------------------------------------------- | ------------------ |
| Application via store + classes sur `<html>`             | OK                 |
| Raccourci Alt+F                                          | OK                 |
| Respect du thème utilisateur (pas de surcharge couleurs) | OK                 |
| Animations désactivées (Starfield, Particles, Planet)    | OK via store + CSS |
| Footer masqué via `[role="contentinfo"]`                 | OK                 |
| Contraste menu accessibilité                             | OK (fix récent)    |
| Focus visible renforcé                                   | OK                 |
| useAccessibleAnimation respecte focusMode                | OK                 |

---

## Points d'attention / corrections

### 1. Règle vide Header

`.focus-mode header nav > div:last-child` — commentaire indique masquer thème/langue, mais aucune déclaration → n'a aucun effet.

### 2. FeedbackFab non masqué

Le bouton flottant de feedback reste visible et peut distraire en mode focus.

### 3. Duplication CSS

`accessibility.css` et `globals.css` définissent `.focus-mode`. La source de vérité est `globals.css` (plus complète). La duplication dans `accessibility.css` peut induire en erreur.

### 4. Sélecteurs potentiellement obsolètes

- `.navigation-secondary`, `.sidebar`, `.badges-preview`, `.recommendations` — classes qui pourraient ne pas exister dans la structure actuelle

### 5. Règles très larges

- `line-height: 1.9` sur tous les `div` — peut impacter des layouts
- `padding: 2rem` sur toutes les cards — peut gonfler des cartes compactes
- `min-width: 52px` sur tous les boutons — OK pour touch targets, mais `padding: 0.875rem 1.75rem` peut étirer des boutons icône

---

## Corrections appliquées (2025-02-22)

- **FeedbackFab** : classe `feedback-fab` ajoutée, masquée en mode focus
- **Règle vide** : supprimée (header conservé intact en focus)
- **accessibility.css** : bloc focus-mode retiré (source unique dans globals.css)

## Recommandations futures

- Affiner `line-height` sur `div` si des layouts sont impactés
- Option de masquer thème/langue dans le header (nécessiterait une classe dédiée)
