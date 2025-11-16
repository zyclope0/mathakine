# 🎨 Guide de Standardisation UI/UX - Mathakine

**Date** : Janvier 2025  
**Objectif** : Standardiser l'utilisation des améliorations UI/UX sur toutes les pages  
**Compatibilité** : Tous les thèmes (Spatial, Minimalist, Ocean, Neutral)

---

## 📋 **SYSTÈME DE CLASSES CSS RÉUTILISABLES**

### **1. Cards avec Profondeur Spatiale**

#### **Classe : `.card-spatial-depth`**

**Utilisation** :
```tsx
<Card className="card-spatial-depth">
  {/* Contenu de la card */}
</Card>
```

**Effets appliqués** :
- ✅ Gradient de fond adaptatif selon le thème
- ✅ Glow effect au hover avec couleur primary du thème
- ✅ Élévation au hover (`translateY(-4px)`)
- ✅ Border animé au hover
- ✅ Sweep effect (brillance qui traverse la card)

**Adaptations par thème** :
- **Spatial** : Glow violet prononcé
- **Minimalist** : Ombre nette, border épais au hover
- **Ocean** : Glow bleu subtil
- **Neutre** : Glow gris discret

**Exemple** :
```tsx
// frontend/components/exercises/ExerciseCard.tsx
<Card className="card-spatial-depth">
  {/* ... */}
</Card>
```

---

### **2. Badges avec Effet Sweep**

#### **Classe : `.badge-sweep`**

**Utilisation** :
```tsx
<Badge className="badge-sweep">
  {label}
</Badge>
```

**Effets appliqués** :
- ✅ Animation sweep au hover (brillance qui traverse)
- ✅ Utilise `currentColor` pour s'adapter automatiquement

**Exemple** :
```tsx
<Badge className="badge-sweep bg-green-500/20 text-green-400">
  Initié
</Badge>
```

---

### **3. Boutons CTA Optimisés**

#### **Classe : `.btn-cta-primary`**

**Utilisation** :
```tsx
<Button className="btn-cta-primary">
  Action principale
</Button>
```

**Effets appliqués** :
- ✅ Glow effect adaptatif selon le thème
- ✅ Border animé au hover avec gradient
- ✅ Élévation au hover (`translateY(-2px) scale(1.02)`)
- ✅ Feedback visuel immédiat

**Exemple** :
```tsx
<Button className="btn-cta-primary flex-1">
  Résoudre
</Button>
```

---

### **4. Sections avec Fond Distinct**

#### **Classe : `.section-filter`**

**Utilisation** :
```tsx
<PageSection className="section-filter">
  {/* Section filtres */}
</PageSection>
```

**Effets appliqués** :
- ✅ Fond semi-transparent avec backdrop-filter
- ✅ Border-top accentué avec couleur primary
- ✅ Distinction visuelle claire

**Classe : `.section-generator`**

**Utilisation** :
```tsx
<PageSection className="section-generator">
  {/* Section générateurs */}
</PageSection>
```

**Effets appliqués** :
- ✅ Fond légèrement accentué
- ✅ Border subtile avec couleur primary
- ✅ Hiérarchie visuelle claire

---

### **5. Animations d'Entrée en Cascade**

#### **Classes : `.animate-fade-in-up`, `.animate-fade-in-up-delay-1`, etc.**

**Utilisation** :
```tsx
{/* Section principale */}
<PageSection className="animate-fade-in-up">
  {/* Contenu */}
</PageSection>

{/* Section avec délai */}
<PageSection className="animate-fade-in-up-delay-1">
  {/* Contenu */}
</PageSection>

{/* Cards avec délais différents */}
{items.map((item, index) => {
  const delayClass = index === 0 ? 'animate-fade-in-up-delay-1' 
    : index === 1 ? 'animate-fade-in-up-delay-2' 
    : 'animate-fade-in-up-delay-3';
  return (
    <div key={item.id} className={delayClass}>
      <Card>{/* ... */}</Card>
    </div>
  );
})}
```

**Délais disponibles** :
- `.animate-fade-in-up` : Pas de délai
- `.animate-fade-in-up-delay-1` : 0.1s
- `.animate-fade-in-up-delay-2` : 0.2s
- `.animate-fade-in-up-delay-3` : 0.3s

---

### **6. Badge IA avec Animation Pulse**

#### **Classe : `.badge-ai-pulse`**

**Utilisation** :
```tsx
<Badge className="badge-ai-pulse bg-primary/10 text-primary-on-dark">
  IA
</Badge>
```

**Effets appliqués** :
- ✅ Animation pulse subtile (2s)
- ✅ Glow effect qui pulse
- ✅ Attire l'attention sur les contenus générés par IA

---

## 🎯 **PATTERN STANDARD POUR UNE PAGE**

### **Structure Recommandée**

```tsx
export default function MyPage() {
  return (
    <PageLayout>
      {/* En-tête */}
      <PageHeader title="..." description="..." />

      {/* Section Filtres */}
      <PageSection className="section-filter space-y-3 animate-fade-in-up">
        {/* Contenu filtres */}
      </PageSection>

      {/* Section Actions/Générateurs */}
      <PageSection className="section-generator space-y-3 animate-fade-in-up-delay-1">
        {/* Contenu actions */}
      </PageSection>

      {/* Liste de Cards */}
      <PageSection className="space-y-3 animate-fade-in-up-delay-2">
        <PageGrid columns={{ mobile: 1, tablet: 2, desktop: 3 }}>
          {items.map((item, index) => {
            const delayClass = index < 3 
              ? `animate-fade-in-up-delay-${index + 1}` 
              : 'animate-fade-in-up-delay-3';
            return (
              <div key={item.id} className={delayClass}>
                <Card className="card-spatial-depth">
                  {/* Contenu card */}
                  <Badge className="badge-sweep">Label</Badge>
                  <Button className="btn-cta-primary">Action</Button>
                </Card>
              </div>
            );
          })}
        </PageGrid>
      </PageSection>
    </PageLayout>
  );
}
```

---

## 🔧 **ADAPTATIONS PAR THÈME**

### **Comment ça fonctionne**

Toutes les classes utilisent des **variables CSS** (`var(--primary)`, `var(--card)`, etc.) qui sont définies différemment selon le thème actif (`[data-theme="spatial"]`, etc.).

**Exemple** :
```css
.card-spatial-depth {
  box-shadow: 0 0 20px color-mix(in srgb, var(--primary) 10%, transparent);
}
```

- **Thème Spatial** : `var(--primary)` = `#7c3aed` → Glow violet
- **Thème Ocean** : `var(--primary)` = `#0369a1` → Glow bleu
- **Thème Minimalist** : `var(--primary)` = `#000000` → Ombre nette
- **Thème Neutral** : `var(--primary)` = `#6b7280` → Glow gris

**Pas besoin de modifier le code** : Les effets s'adaptent automatiquement !

---

## ♿ **ACCESSIBILITÉ**

### **Respect Automatique**

Toutes les animations sont **automatiquement désactivées** si :
- ✅ `prefers-reduced-motion: reduce` est détecté
- ✅ Mode Focus TSA/TDAH est activé
- ✅ Reduced Motion est activé dans les préférences

**Aucune action requise** : Le CSS gère tout automatiquement via les media queries.

---

## 📝 **CHECKLIST POUR NOUVELLE PAGE**

### **Avant de créer une nouvelle page**

- [ ] Utiliser `.card-spatial-depth` pour toutes les cards
- [ ] Utiliser `.badge-sweep` pour les badges interactifs
- [ ] Utiliser `.btn-cta-primary` pour les boutons d'action principaux
- [ ] Utiliser `.section-filter` pour la section filtres
- [ ] Utiliser `.section-generator` pour les sections d'actions
- [ ] Ajouter animations d'entrée en cascade (`.animate-fade-in-up-delay-*`)
- [ ] Tester avec tous les thèmes (spatial, minimalist, ocean, neutral)
- [ ] Vérifier accessibilité (reduced motion, focus mode)

---

## 🎨 **EXEMPLES CONCRETS**

### **Page Challenges**

```tsx
<PageSection className="section-filter animate-fade-in-up">
  {/* Filtres défis */}
</PageSection>

<PageSection className="section-generator animate-fade-in-up-delay-1">
  {/* Générateur de défis */}
</PageSection>

<PageGrid>
  {challenges.map((challenge, index) => (
    <div key={challenge.id} className={`animate-fade-in-up-delay-${Math.min(index + 1, 3)}`}>
      <Card className="card-spatial-depth">
        <Badge className="badge-sweep">Difficulté</Badge>
        <Button className="btn-cta-primary">Commencer</Button>
      </Card>
    </div>
  ))}
</PageGrid>
```

### **Page Badges**

```tsx
<PageGrid>
  {badges.map((badge, index) => (
    <div key={badge.id} className={`animate-fade-in-up-delay-${Math.min(index + 1, 3)}`}>
      <Card className="card-spatial-depth">
        {badge.unlocked && (
          <Badge className="badge-ai-pulse">Nouveau</Badge>
        )}
      </Card>
    </div>
  ))}
</PageGrid>
```

---

## ✅ **AVANTAGES DE CE SYSTÈME**

1. **Réutilisable** : Une seule classe CSS pour tous les thèmes
2. **Maintenable** : Modifications centralisées dans `globals.css`
3. **Cohérent** : Même apparence sur toutes les pages
4. **Accessible** : Respect automatique des préférences
5. **Performant** : CSS natif, pas de JavaScript supplémentaire
6. **Évolutif** : Facile d'ajouter de nouveaux effets

---

## 🚀 **PROCHAINES ÉTAPES**

Pour appliquer ce système sur une nouvelle page :

1. **Copier le pattern standard** ci-dessus
2. **Remplacer les classes** par les classes standardisées
3. **Tester avec tous les thèmes**
4. **Vérifier l'accessibilité**

**Temps estimé** : 5-10 minutes par page

---

**Document créé le** : Janvier 2025  
**Dernière mise à jour** : Janvier 2025

