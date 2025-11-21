# Guide de Test - Visualisations Interactives des Challenges

## 📋 Vue d'ensemble

Ce guide explique comment tester les nouvelles visualisations interactives pour les challenges. Des challenges de test ont été créés avec `visual_data` pour chaque type de visualisation.

## 🎯 Challenges de Test Disponibles

5 challenges de test ont été créés dans la base de données :

| ID | Titre | Type | Visualisation |
|----|-------|------|---------------|
| 2356 | Test Sequence - Suite de nombres | SEQUENCE | Séquence animée avec mise en évidence |
| 2357 | Test Pattern - Grille 3x3 | PATTERN | Grille interactive cliquable |
| 2358 | Test Visuel - Formes geometriques | VISUAL | Formes avec contrôles (rotation, zoom, flip) |
| 2359 | Test Puzzle - Reorganiser les etapes | PUZZLE | Drag & drop pour réorganiser |
| 2360 | Test Graphe - Reseau de connexions | GRAPH | Visualisation SVG de graphe |

## 🧪 Étapes de Test

### 1. Accéder à la page Challenges

1. Démarrez le serveur frontend (si pas déjà fait) :
   ```bash
   cd frontend
   npm run dev
   ```

2. Ouvrez votre navigateur et allez sur : `http://localhost:3000/challenges`

3. Connectez-vous si nécessaire

### 2. Tester chaque Type de Visualisation

#### ✅ Test SEQUENCE (ID: 2356)

**Attendu :**
- Affichage d'une séquence de nombres : `2 → 4 → 7 → 11`
- Animation d'entrée pour chaque élément
- Mise en évidence au clic sur un élément
- Flèches entre les éléments

**Actions à tester :**
- Cliquer sur chaque nombre pour le mettre en évidence
- Vérifier l'animation au survol
- Vérifier que le pattern suggéré s'affiche en bas

#### ✅ Test PATTERN (ID: 2357)

**Attendu :**
- Grille 3x3 avec des X et O
- Cellules cliquables pour sélection
- Animation au survol

**Actions à tester :**
- Cliquer sur plusieurs cellules pour les sélectionner
- Vérifier que les cellules sélectionnées changent de couleur
- Vérifier le compteur de cellules sélectionnées

#### ✅ Test VISUAL (ID: 2358)

**Attendu :**
- Formes géométriques affichées
- Contrôles en haut : Rotation, Zoom avant/arrière, Retournement
- ASCII art si disponible

**Actions à tester :**
- Cliquer sur le bouton de rotation → vérifier la rotation
- Utiliser les boutons de zoom → vérifier le zoom
- Cliquer sur retournement → vérifier le flip horizontal
- Vérifier que les animations sont fluides

#### ✅ Test PUZZLE (ID: 2359)

**Attendu :**
- Liste de 4 éléments : "Servir", "Préparer", "Cuire", "Mélanger"
- Possibilité de glisser-déposer pour réorganiser
- Indicateur de position (#1, #2, etc.)

**Actions à tester :**
- Glisser un élément vers le haut/bas
- Vérifier que l'élément suit le curseur pendant le drag
- Relâcher et vérifier que l'ordre est mis à jour
- Tester avec le clavier (si supporté)

#### ✅ Test GRAPH (ID: 2360)

**Attendu :**
- Visualisation SVG d'un graphe avec 4 nœuds (A, B, C, D)
- Arêtes entre les nœuds
- Layout circulaire automatique

**Actions à tester :**
- Vérifier que tous les nœuds sont visibles
- Vérifier que les arêtes sont correctement dessinées
- Vérifier le compteur de nœuds et arêtes en bas

### 3. Tester le Fallback (DefaultRenderer)

Pour tester le renderer par défaut, vous pouvez :

1. Créer un challenge avec un type non supporté (ex: `RIDDLE`, `DEDUCTION`)
2. Ajouter des `visual_data` au format JSON
3. Vérifier que les données s'affichent de manière structurée
4. Tester le toggle "Vue structurée" / "Vue JSON"

### 4. Tester la Compatibilité Multi-Thèmes

Pour chaque visualisation, tester avec les 4 thèmes disponibles :

1. **Spatial** : Fond étoilé, couleurs spatiales
2. **Minimalist** : Design épuré
3. **Ocean** : Thème océanique
4. **Neutral** : Thème neutre

**Vérifications :**
- Les couleurs s'adaptent au thème
- Les bordures et backgrounds sont cohérents
- Les animations fonctionnent dans tous les thèmes

### 5. Tester l'Accessibilité

**Vérifications :**
- Support clavier pour tous les contrôles interactifs
- Labels ARIA présents
- Contraste des couleurs suffisant
- Animations respectent `prefers-reduced-motion`

## 🐛 Problèmes Potentiels et Solutions

### Problème : Les visualisations ne s'affichent pas

**Solution :**
1. Vérifier que `visual_data` n'est pas `null` dans la base de données
2. Vérifier la console du navigateur pour les erreurs
3. Vérifier que le `challenge_type` correspond bien au type attendu

### Problème : Le drag & drop ne fonctionne pas

**Solution :**
1. Vérifier que `@dnd-kit` est bien installé
2. Vérifier la console pour les erreurs JavaScript
3. Tester avec un autre navigateur

### Problème : Les animations sont saccadées

**Solution :**
1. Vérifier les performances avec les DevTools
2. Réduire le nombre d'éléments animés simultanément
3. Vérifier que `prefers-reduced-motion` est respecté

## 📝 Scripts Utiles

### Créer de nouveaux challenges de test

```bash
python scripts/test_challenge_visualizations.py
```

### Mettre à jour les types de challenges

```bash
python scripts/update_challenge_types.py
```

### Vérifier les challenges avec visual_data

```sql
SELECT id, title, challenge_type, visual_data IS NOT NULL as has_visual_data
FROM logic_challenges
WHERE visual_data IS NOT NULL
ORDER BY created_at DESC;
```

## ✅ Checklist de Validation

- [ ] Toutes les visualisations s'affichent correctement
- [ ] Les interactions fonctionnent (clic, drag, hover)
- [ ] Les animations sont fluides
- [ ] Compatible avec tous les thèmes
- [ ] Accessible au clavier
- [ ] Responsive (mobile, tablette, desktop)
- [ ] Pas d'erreurs dans la console
- [ ] Performance acceptable (< 100ms pour les interactions)

## 🎨 Personnalisation

Pour créer vos propres visualisations, consultez :
- `frontend/components/challenges/visualizations/ChallengeVisualRenderer.tsx` : Routeur principal
- `frontend/components/challenges/visualizations/*Renderer.tsx` : Composants spécifiques

## 📚 Documentation Technique

- [Architecture des Visualisations](../docs/architecture/visualizations.md) (à créer)
- [Types de Challenges](../docs/features/challenges.md)
- [Guide de Contribution](../CONTRIBUTING.md)

