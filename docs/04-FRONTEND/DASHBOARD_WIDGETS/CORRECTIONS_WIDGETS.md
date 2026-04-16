# Corrections des widgets de progression

> Corrections appliquées le 06/02/2026

## 🐛 Problèmes identifiés

### 1. Traductions incorrectes dans CategoryAccuracyChart
**Symptôme :** Affichage de `exercises.types.TEXTE` et `exercises.types.MULTIPLICATION` au lieu des noms traduits.

**Cause :** Les catégories arrivent en majuscules depuis la base de données (`TEXTE`, `MULTIPLICATION`), mais les clés de traduction dans `messages/fr.json` sont en minuscules (`texte`, `multiplication`).

**Solution :**
```typescript
// Avant
{tExercises(`types.${category}`, { defaultValue: category })}

// Après
const categoryKey = category.toLowerCase().replace('exercises.types.', '');
{tExercises(`types.${categoryKey}`, { defaultValue: categoryKey })}
```

**Fichier modifié :** `frontend/components/dashboard/CategoryAccuracyChart.tsx`

**Note 24/03/2026 :**
- le widget recalcule maintenant correctement ses libelles quand la locale change apres le premier rendu
- une non-regression unitaire couvre ce cas : `frontend/components/dashboard/CategoryAccuracyChart.test.tsx`

---

### 2. Hauteurs non uniformes des widgets
**Symptôme :** Les 3 nouveaux widgets (Série, Défis, Précision) n'avaient pas la même hauteur, créant un rendu visuel incohérent.

**Cause :** Les composants Card n'utilisaient pas de layout flex pour s'adapter à la hauteur du conteneur parent.

**Solution :**

#### 2.1 Grid parent avec items-stretch
```tsx
// frontend/app/dashboard/page.tsx
<div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 items-stretch">
```

#### 2.2 Cards avec Flexbox
```tsx
// Structure appliquée aux 3 widgets
<Card className="bg-card border-primary/20 h-full flex flex-col">
  <CardHeader className="pb-3 flex-shrink-0">
    {/* Header fixe */}
  </CardHeader>
  
  <CardContent className="flex-grow">
    {/* Contenu flexible */}
  </CardContent>
</Card>
```

**Classes Tailwind ajoutées :**
- `h-full` : Prend toute la hauteur disponible
- `flex flex-col` : Layout flex vertical
- `flex-shrink-0` : Header ne rétrécit pas
- `flex-grow` : Contenu s'étire pour remplir l'espace

**Fichiers modifiés :**
- `frontend/components/dashboard/StreakWidget.tsx`
- `frontend/components/dashboard/ChallengesProgressWidget.tsx`
- `frontend/components/dashboard/CategoryAccuracyChart.tsx`
- `frontend/app/dashboard/page.tsx`

---

## ✅ Résultat

### Traductions
✅ Les catégories s'affichent maintenant correctement :
- `TEXTE` → "Problèmes textuels"
- `MULTIPLICATION` → "Multiplication"
- Toutes les catégories sont traduites (minuscules/majuscules gérées)

### Hauteurs uniformes
✅ Les 3 widgets ont maintenant la même hauteur :
- Série en cours (StreakWidget)
- Progression des défis (ChallengesProgressWidget)
- Précision par catégorie (CategoryAccuracyChart)

✅ Layout responsive cohérent :
- Mobile (< 768px) : 1 colonne
- Tablet (768-1024px) : 2 colonnes
- Desktop (>= 1024px) : 3 colonnes

✅ Skeletons de chargement aussi uniformisés

---

## 🧪 Tests

### Build frontend
```bash
npm run build
✅ Build réussi en 40.4s
✅ TypeScript : OK
✅ 19/19 pages générées
✅ Aucune erreur
```

### Validation visuelle
Les captures d'écran montrent maintenant :
- ✅ Noms de catégories traduits correctement
- ✅ Hauteurs identiques pour les 3 widgets
- ✅ Alignement parfait dans la grille
- ✅ Compatible dark mode et light mode

---

## 📝 Code avant/après

### CategoryAccuracyChart - Traductions

**Avant :**
```tsx
<Badge variant="outline">
  {tExercises(`types.${category}`, { defaultValue: category })}
</Badge>
// category = "TEXTE" → clé cherchée: "types.TEXTE" → ❌ non trouvée
```

**Après :**
```tsx
const categoryKey = category.toLowerCase().replace('exercises.types.', '');

<Badge variant="outline">
  {tExercises(`types.${categoryKey}`, { defaultValue: categoryKey })}
</Badge>
// category = "TEXTE" → categoryKey = "texte" → clé: "types.texte" → ✅ trouvée
```

---

### Widgets - Hauteurs uniformes

**Avant :**
```tsx
<Card className="bg-card border-primary/20">
  <CardHeader className="pb-3">
    {/* Header */}
  </CardHeader>
  <CardContent>
    {/* Contenu */}
  </CardContent>
</Card>
// ❌ Hauteur variable selon le contenu
```

**Après :**
```tsx
<Card className="bg-card border-primary/20 h-full flex flex-col">
  <CardHeader className="pb-3 flex-shrink-0">
    {/* Header */}
  </CardHeader>
  <CardContent className="flex-grow">
    {/* Contenu */}
  </CardContent>
</Card>
// ✅ Hauteur uniforme, contenu s'ajuste
```

---

## 🎨 Impact visuel

### Avant les corrections
- Texte : `exercises.types.TEXTE` (non traduit)
- Widgets : Hauteurs inégales, alignement cassé
- UX : Incohérent, peu professionnel

### Après les corrections
- Texte : `Problèmes textuels` (traduit)
- Widgets : Hauteurs identiques, alignement parfait
- UX : Cohérent, professionnel, harmonieux

---

## 📚 Références

**Fichiers modifiés :**
1. `frontend/components/dashboard/CategoryAccuracyChart.tsx`
2. `frontend/components/dashboard/StreakWidget.tsx`
3. `frontend/components/dashboard/ChallengesProgressWidget.tsx`
4. `frontend/app/dashboard/page.tsx`

**Documentation associée :**
- `INTEGRATION_PROGRESSION_WIDGETS.md`
- `DESIGN_SYSTEM_WIDGETS.md`

---

**Date :** 06/02/2026  
**Validé par :** Build réussi + Tests visuels
