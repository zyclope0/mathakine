# 🔄 Workflow de Traduction - Guide Pratique

**Date de création** : Janvier 2025  
**Objectif** : Industrialiser le processus de traduction

---

## 📋 **WORKFLOW STANDARD**

### **Étape 1 : Identifier le Texte à Traduire**

```typescript
// ❌ AVANT : Texte hardcodé
<h1>Exercices Mathématiques</h1>
<p>Choisissez un exercice ou générez-en un nouveau</p>
```

### **Étape 2 : Déterminer le Namespace**

- **Nouvelle page** → Créer un nouveau namespace (`settings`, `profile`)
- **Page existante** → Utiliser le namespace existant (`exercises`, `dashboard`)
- **Texte commun** → Utiliser `common`

### **Étape 3 : Ajouter les Clés dans `messages/fr.json`**

```json
{
  "exercises": {
    "title": "Exercices Mathématiques",
    "description": "Choisissez un exercice ou générez-en un nouveau"
  }
}
```

### **Étape 4 : Ajouter les Traductions dans `messages/en.json`**

```json
{
  "exercises": {
    "title": "Math Exercises",
    "description": "Choose an exercise or generate a new one"
  }
}
```

### **Étape 5 : Utiliser dans le Composant**

```typescript
'use client';

import { useTranslations } from 'next-intl';

export default function ExercisesPage() {
  const t = useTranslations('exercises');
  
  return (
    <div>
      <h1>{t('title')}</h1>
      <p>{t('description')}</p>
    </div>
  );
}
```

### **Étape 6 : Tester**

1. Changer la langue dans le sélecteur
2. Vérifier que les traductions s'affichent correctement
3. Vérifier qu'il n'y a pas d'erreurs dans la console

---

## 🎯 **CAS D'USAGE COURANTS**

### **Cas 1 : Traduire une Page Existante**

#### **Exemple : Page Login**

**1. Identifier les textes hardcodés**

```typescript
// app/login/page.tsx
<CardTitle>Connexion</CardTitle>
<CardDescription>Accédez à votre compte Mathakine</CardDescription>
<Label>Nom d'utilisateur</Label>
<Label>Mot de passe</Label>
```

**2. Vérifier si les clés existent déjà**

```bash
# Chercher dans messages/fr.json
grep -i "connexion\|nom.*utilisateur\|mot.*passe" messages/fr.json
```

**3. Utiliser les clés existantes ou en créer de nouvelles**

```typescript
// Les clés existent déjà dans auth.login
const t = useTranslations('auth.login');

<CardTitle>{t('title')}</CardTitle>
<CardDescription>Accédez à votre compte Mathakine</CardDescription>
<Label>{t('username')}</Label>
<Label>{t('password')}</Label>
```

**4. Ajouter les clés manquantes si nécessaire**

```json
// messages/fr.json
{
  "auth": {
    "login": {
      "title": "Connexion",
      "description": "Accédez à votre compte Mathakine",
      "username": "Nom d'utilisateur",
      "password": "Mot de passe"
    }
  }
}
```

### **Cas 2 : Créer une Nouvelle Page**

#### **Exemple : Page Settings**

**1. Créer le namespace dans les fichiers de messages**

```json
// messages/fr.json
{
  "settings": {
    "title": "Paramètres",
    "description": "Gérez vos préférences",
    "sections": {
      "account": "Compte",
      "notifications": "Notifications"
    },
    "save": "Enregistrer",
    "cancel": "Annuler"
  }
}
```

```json
// messages/en.json
{
  "settings": {
    "title": "Settings",
    "description": "Manage your preferences",
    "sections": {
      "account": "Account",
      "notifications": "Notifications"
    },
    "save": "Save",
    "cancel": "Cancel"
  }
}
```

**2. Créer la page avec traductions**

```typescript
// app/settings/page.tsx
'use client';

import { useTranslations } from 'next-intl';

export default function SettingsPage() {
  const t = useTranslations('settings');
  
  return (
    <div>
      <h1>{t('title')}</h1>
      <p>{t('description')}</p>
      
      <section>
        <h2>{t('sections.account')}</h2>
      </section>
      
      <button>{t('save')}</button>
      <button>{t('cancel')}</button>
    </div>
  );
}
```

### **Cas 3 : Traduire un Composant Réutilisable**

#### **Exemple : Composant Button**

**1. Utiliser `common` pour les textes génériques**

```json
// messages/fr.json
{
  "common": {
    "submit": "Valider",
    "cancel": "Annuler",
    "save": "Enregistrer"
  }
}
```

**2. Utiliser dans le composant**

```typescript
// components/ui/Button.tsx
'use client';

import { useTranslations } from 'next-intl';

export function Button({ variant = 'default', children, ...props }) {
  const t = useTranslations('common');
  
  // Si children est une clé de traduction
  const text = typeof children === 'string' && children.startsWith('common.')
    ? t(children.replace('common.', ''))
    : children;
  
  return <button {...props}>{text}</button>;
}
```

### **Cas 4 : Traduire les Toasts**

**1. Ajouter dans `toasts` namespace**

```json
// messages/fr.json
{
  "toasts": {
    "exercises": {
      "generateSuccess": "Exercice généré !",
      "generateError": "Erreur de génération"
    }
  }
}
```

**2. Utiliser dans le hook**

```typescript
// hooks/useExercises.ts
'use client';

import { useTranslations } from 'next-intl';
import { toast } from 'sonner';

export function useExercises() {
  const t = useTranslations('toasts.exercises');
  
  const generateMutation = useMutation({
    onSuccess: () => {
      toast.success(t('generateSuccess'));
    },
    onError: () => {
      toast.error(t('generateError'));
    },
  });
  
  return { generate: generateMutation.mutate };
}
```

---

## 🔍 **VÉRIFICATIONS**

### **Checklist Avant Commit**

- [ ] **Clés ajoutées dans `messages/fr.json`**
- [ ] **Traductions ajoutées dans `messages/en.json`**
- [ ] **Structure identique entre FR et EN**
- [ ] **Clés utilisées dans les composants**
- [ ] **Pas de texte hardcodé restant**
- [ ] **Testé avec changement de langue**
- [ ] **Pas d'erreurs dans la console**

### **Vérification Automatique (À Implémenter)**

```bash
# Script à créer : scripts/check-translations.js
# Vérifie que :
# 1. Toutes les clés FR existent en EN
# 2. Toutes les clés EN existent en FR
# 3. Structure identique
# 4. Pas de clés orphelines
```

---

## 📝 **TEMPLATE POUR NOUVELLE PAGE**

### **Template Minimal**

```typescript
// app/ma-page/page.tsx
'use client';

import { useTranslations } from 'next-intl';

export default function MaPage() {
  const t = useTranslations('maPage');
  
  return (
    <div>
      <h1>{t('title')}</h1>
      <p>{t('description')}</p>
    </div>
  );
}
```

### **Template Complet**

```typescript
// app/ma-page/page.tsx
'use client';

import { useTranslations } from 'next-intl';
import { Button } from '@/components/ui/button';

export default function MaPage() {
  const t = useTranslations('maPage');
  const tCommon = useTranslations('common');
  
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-4">{t('title')}</h1>
      <p className="text-muted-foreground mb-6">{t('description')}</p>
      
      <div className="space-y-4">
        <section>
          <h2 className="text-xl font-semibold mb-2">{t('sections.main')}</h2>
          <p>{t('sections.mainDescription')}</p>
        </section>
      </div>
      
      <div className="mt-6 flex gap-2">
        <Button>{tCommon('save')}</Button>
        <Button variant="outline">{tCommon('cancel')}</Button>
      </div>
    </div>
  );
}
```

---

## 🎨 **BONNES PRATIQUES**

### **1. Nommage des Clés**

```json
// ✅ BON : Clés descriptives et cohérentes
{
  "exercises": {
    "title": "...",
    "generateButton": "...",
    "aiGenerateButton": "..."
  }
}
```

```json
// ❌ MAUVAIS : Clés génériques ou incohérentes
{
  "exercises": {
    "title": "...",
    "btn1": "...",
    "btn2": "..."
  }
}
```

### **2. Réutilisation**

```typescript
// ✅ BON : Utiliser common pour textes répétés
const tCommon = useTranslations('common');
<Button>{tCommon('submit')}</Button>
<Button>{tCommon('cancel')}</Button>
```

```typescript
// ❌ MAUVAIS : Répéter les traductions
const t = useTranslations('maPage');
<Button>{t('submit')}</Button> // Si submit existe déjà dans common
```

### **3. Structure Hiérarchique**

```json
// ✅ BON : Structure logique et imbriquée
{
  "exercises": {
    "generator": {
      "title": "...",
      "selectType": "..."
    },
    "solver": {
      "question": "...",
      "submit": "..."
    }
  }
}
```

### **4. Traductions Complètes**

- ✅ Traduire **TOUT** le texte visible
- ✅ Traduire les **messages d'erreur**
- ✅ Traduire les **toasts**
- ✅ Traduire les **placeholders**

---

## 🚀 **PROCHAINES AMÉLIORATIONS**

### **Scripts à Créer**

1. **`scripts/check-translations.js`**
   - Vérifie la cohérence FR/EN
   - Détecte les clés manquantes
   - Détecte les clés orphelines

2. **`scripts/extract-translations.js`**
   - Extrait les textes hardcodés
   - Génère les clés de traduction
   - Crée les entrées dans les fichiers JSON

3. **`scripts/validate-translations.js`**
   - Valide la syntaxe JSON
   - Vérifie les clés utilisées
   - Génère un rapport

---

## 📚 **RESSOURCES**

- **Guide principal** : `docs/development/I18N_GUIDE.md`
- **Fichiers de messages** : `frontend/messages/`
- **Documentation next-intl** : https://next-intl-docs.vercel.app/

---

**Dernière mise à jour** : Janvier 2025

