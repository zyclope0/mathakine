# 🌐 Guide i18n - Système de Traduction Mathakine

**Date de création** : Janvier 2025  
**Version** : 1.0  
**Framework** : next-intl (Next.js App Router)

---

## 📋 **TABLE DES MATIÈRES**

1. [Architecture](#architecture)
2. [Structure des Fichiers](#structure-des-fichiers)
3. [Utilisation dans les Composants](#utilisation-dans-les-composants)
4. [Ajout de Nouvelles Traductions](#ajout-de-nouvelles-traductions)
5. [Bonnes Pratiques](#bonnes-pratiques)
6. [Workflow de Traduction](#workflow-de-traduction)
7. [Dépannage](#dépannage)

---

## 🏗️ **ARCHITECTURE**

### **Stack Technique**

- **Bibliothèque** : `next-intl` v4.4.0
- **Store** : Zustand avec persistance localStorage
- **Fichiers de messages** : JSON (`messages/fr.json`, `messages/en.json`)
- **Provider** : `NextIntlProvider` (client-side)

### **Flux de Données**

```
┌─────────────────┐
│ LocaleStore     │ (Zustand avec persist)
│ (fr/en)         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ NextIntlProvider│ Charge messages selon locale
│                 │ - FR: import synchrone
│                 │ - EN: import asynchrone
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Composants      │ useTranslations('namespace.key')
│ Pages           │
└─────────────────┘
```

### **Composants Clés**

1. **`NextIntlProvider`** (`components/providers/NextIntlProvider.tsx`)
   - Charge les messages selon la locale
   - Messages FR chargés de manière synchrone (évite erreurs)
   - Messages EN chargés de manière asynchrone

2. **`LocaleStore`** (`lib/stores/localeStore.ts`)
   - Store Zustand avec persistance localStorage
   - Valeur par défaut : `'fr'`
   - Clé localStorage : `locale-preferences`

3. **`LanguageSelector`** (`components/locale/LanguageSelector.tsx`)
   - Composant UI pour changer la langue
   - Intégré dans le Header

4. **`LocaleInitializer`** (`components/locale/LocaleInitializer.tsx`)
   - Détecte la langue du navigateur au premier chargement
   - Initialise la locale si non définie

---

## 📁 **STRUCTURE DES FICHIERS**

### **Organisation**

```
frontend/
├── messages/
│   ├── fr.json          # Traductions françaises (281 lignes)
│   └── en.json          # Traductions anglaises (281 lignes)
│
├── components/
│   ├── providers/
│   │   └── NextIntlProvider.tsx    # Provider i18n
│   └── locale/
│       ├── LanguageSelector.tsx     # Sélecteur langue
│       └── LocaleInitializer.tsx    # Initialisation locale
│
└── lib/
    └── stores/
        └── localeStore.ts           # Store Zustand locale
```

### **Structure des Fichiers de Messages**

Les fichiers JSON suivent une structure hiérarchique par **namespace** :

```json
{
  "common": {
    "appName": "Mathakine",
    "loading": "Chargement...",
    "error": "Erreur"
  },
  "auth": {
    "login": {
      "title": "Connexion",
      "username": "Nom d'utilisateur"
    },
    "logout": "Déconnexion"
  },
  "navigation": {
    "home": "Accueil",
    "dashboard": "Tableau de bord"
  },
  "toasts": {
    "auth": {
      "loginSuccess": "Connexion réussie !",
      "loginError": "Erreur de connexion"
    }
  }
}
```

### **Namespaces Actuels**

| Namespace | Description | Utilisation |
|-----------|-------------|-------------|
| `common` | Textes communs (boutons, labels génériques) | Partout |
| `auth` | Authentification (login, register, logout) | Pages auth |
| `navigation` | Liens de navigation | Header |
| `exercises` | Exercices mathématiques | Pages exercices |
| `challenges` | Défis logiques | Pages défis |
| `dashboard` | Tableau de bord | Page dashboard |
| `badges` | Badges et gamification | Page badges |
| `accessibility` | Accessibilité | AccessibilityToolbar |
| `theme` | Thèmes | ThemeSelector |
| `errors` | Messages d'erreur | Partout |
| `toasts` | Notifications toast | Hooks et composants |

---

## 💻 **UTILISATION DANS LES COMPOSANTS**

### **Hook `useTranslations`**

```typescript
import { useTranslations } from 'next-intl';

// Dans un composant
const t = useTranslations('namespace');
const text = t('key'); // "Valeur traduite"
```

### **Exemples d'Utilisation**

#### **1. Traduction Simple**

```typescript
'use client';

import { useTranslations } from 'next-intl';

export function MyComponent() {
  const t = useTranslations('common');
  
  return (
    <div>
      <h1>{t('appName')}</h1>
      <p>{t('loading')}</p>
    </div>
  );
}
```

#### **2. Traduction avec Namespace Imbriqué**

```typescript
'use client';

import { useTranslations } from 'next-intl';

export function LoginPage() {
  const t = useTranslations('auth.login');
  
  return (
    <form>
      <label>{t('username')}</label>
      <input type="text" />
      <button>{t('submit')}</button>
    </form>
  );
}
```

#### **3. Traduction avec Plusieurs Namespaces**

```typescript
'use client';

import { useTranslations } from 'next-intl';

export function Header() {
  const t = useTranslations('navigation');
  const tAuth = useTranslations('auth');
  
  return (
    <nav>
      <a href="/">{t('home')}</a>
      <a href="/dashboard">{t('dashboard')}</a>
      <button>{tAuth('logout')}</button>
    </nav>
  );
}
```

#### **4. Traduction dans les Hooks**

```typescript
'use client';

import { useTranslations } from 'next-intl';
import { toast } from 'sonner';

export function useAuth() {
  const t = useTranslations('toasts.auth');
  
  const loginMutation = useMutation({
    onSuccess: () => {
      toast.success(t('loginSuccess'));
    },
    onError: () => {
      toast.error(t('loginError'));
    },
  });
  
  return { login: loginMutation.mutate };
}
```

### **Patterns d'Utilisation**

#### **✅ BON : Utiliser les traductions**

```typescript
const t = useTranslations('exercises');
<h1>{t('title')}</h1>
```

#### **❌ MAUVAIS : Texte hardcodé**

```typescript
<h1>Exercices Mathématiques</h1> // ❌ Hardcodé en français
```

---

## ➕ **AJOUT DE NOUVELLES TRADUCTIONS**

### **Étape 1 : Ajouter les Clés dans `messages/fr.json`**

```json
{
  "maPage": {
    "title": "Titre de ma page",
    "description": "Description de ma page",
    "button": {
      "submit": "Valider",
      "cancel": "Annuler"
    }
  }
}
```

### **Étape 2 : Ajouter les Traductions dans `messages/en.json`**

```json
{
  "maPage": {
    "title": "My Page Title",
    "description": "My page description",
    "button": {
      "submit": "Submit",
      "cancel": "Cancel"
    }
  }
}
```

### **Étape 3 : Utiliser dans le Composant**

```typescript
'use client';

import { useTranslations } from 'next-intl';

export function MaPage() {
  const t = useTranslations('maPage');
  
  return (
    <div>
      <h1>{t('title')}</h1>
      <p>{t('description')}</p>
      <button>{t('button.submit')}</button>
    </div>
  );
}
```

### **Règles de Nommage**

1. **Namespaces** : camelCase, nom descriptif (`exercises`, `dashboard`)
2. **Clés** : camelCase, nom descriptif (`title`, `submitButton`)
3. **Clés imbriquées** : Utiliser des objets JSON (`button.submit`)

### **Exemple Complet : Ajouter une Nouvelle Page**

#### **1. Ajouter dans `messages/fr.json`**

```json
{
  "settings": {
    "title": "Paramètres",
    "description": "Gérez vos préférences",
    "sections": {
      "account": "Compte",
      "notifications": "Notifications",
      "privacy": "Confidentialité"
    },
    "save": "Enregistrer",
    "cancel": "Annuler"
  }
}
```

#### **2. Ajouter dans `messages/en.json`**

```json
{
  "settings": {
    "title": "Settings",
    "description": "Manage your preferences",
    "sections": {
      "account": "Account",
      "notifications": "Notifications",
      "privacy": "Privacy"
    },
    "save": "Save",
    "cancel": "Cancel"
  }
}
```

#### **3. Créer la Page**

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
      
      <section>
        <h2>{t('sections.notifications')}</h2>
      </section>
      
      <button>{t('save')}</button>
      <button>{t('cancel')}</button>
    </div>
  );
}
```

---

## ✅ **BONNES PRATIQUES**

### **1. Organisation des Namespaces**

- ✅ **Un namespace par domaine fonctionnel** (`exercises`, `challenges`, `badges`)
- ✅ **Namespace `common` pour textes réutilisables** (boutons, labels génériques)
- ✅ **Namespace `toasts` pour notifications** (regroupé par domaine)

### **2. Structure Hiérarchique**

```json
// ✅ BON : Structure claire et logique
{
  "exercises": {
    "title": "...",
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

```json
// ❌ MAUVAIS : Structure plate et confuse
{
  "exercisesTitle": "...",
  "exercisesGeneratorTitle": "...",
  "exercisesSolverQuestion": "..."
}
```

### **3. Réutilisation**

- ✅ **Utiliser `common` pour textes répétés** (`submit`, `cancel`, `loading`)
- ✅ **Éviter la duplication** (ne pas répéter "Valider" partout)

### **4. Clés Descriptives**

```json
// ✅ BON : Clés descriptives
{
  "exercises": {
    "generateButton": "Générer un exercice",
    "aiGenerateButton": "Générer avec l'IA"
  }
}
```

```json
// ❌ MAUVAIS : Clés génériques
{
  "exercises": {
    "button1": "Générer un exercice",
    "button2": "Générer avec l'IA"
  }
}
```

### **5. Traductions Complètes**

- ✅ **Traduire TOUT le texte visible** (titres, descriptions, boutons, labels)
- ✅ **Traduire les messages d'erreur** (`errors` namespace)
- ✅ **Traduire les toasts** (`toasts` namespace)

### **6. Gestion des Variables**

```typescript
// ✅ BON : Utiliser les paramètres de traduction
const t = useTranslations('common');
const message = t('welcome', { name: user.username });
// "Bienvenue {name} !" → "Bienvenue John !"

// Dans messages/fr.json :
{
  "common": {
    "welcome": "Bienvenue {name} !"
  }
}
```

### **7. Fallback et Valeurs par Défaut**

```typescript
// ✅ BON : Fallback explicite
const t = useTranslations('common');
const text = t('optionalKey') || 'Valeur par défaut';

// ✅ BON : Vérification de clé
if (t.raw('key')) {
  // Clé existe
}
```

---

## 🔄 **WORKFLOW DE TRADUCTION**

### **Processus Recommandé**

```
1. Identifier le texte à traduire
   ↓
2. Déterminer le namespace approprié
   ↓
3. Ajouter la clé dans messages/fr.json
   ↓
4. Ajouter la traduction dans messages/en.json
   ↓
5. Utiliser useTranslations dans le composant
   ↓
6. Tester avec les deux langues
   ↓
7. Vérifier la cohérence (même structure FR/EN)
```

### **Checklist Avant Commit**

- [ ] Clés ajoutées dans `messages/fr.json`
- [ ] Traductions ajoutées dans `messages/en.json`
- [ ] Structure identique entre FR et EN
- [ ] Clés utilisées dans les composants
- [ ] Pas de texte hardcodé restant
- [ ] Testé avec changement de langue

### **Script de Vérification (À Créer)**

```bash
# Vérifier que toutes les clés FR existent en EN
# Vérifier que toutes les clés EN existent en FR
# Vérifier la structure identique
```

---

## 🔧 **DÉPANNAGE**

### **Erreur : `MISSING_MESSAGE`**

**Symptôme** :
```
MISSING_MESSAGE: Could not resolve `namespace.key` in messages for locale `fr`.
```

**Causes possibles** :
1. Clé manquante dans le fichier JSON
2. Namespace incorrect
3. Messages non chargés (problème de provider)

**Solutions** :
1. Vérifier que la clé existe dans `messages/fr.json`
2. Vérifier le namespace utilisé (`useTranslations('namespace')`)
3. Vérifier que `NextIntlProvider` est bien dans le layout
4. Vérifier que les messages sont chargés (console.log)

### **Erreur : Messages Non Chargés**

**Symptôme** : Toutes les traductions retournent la clé au lieu de la valeur

**Solutions** :
1. Vérifier que `NextIntlProvider` enveloppe les composants
2. Vérifier que les fichiers JSON sont valides (syntaxe)
3. Vérifier que l'import des messages fonctionne

### **Problème : Changement de Langue Ne Fonctionne Pas**

**Solutions** :
1. Vérifier que `LocaleStore` est bien utilisé
2. Vérifier que `setLocale` est appelé correctement
3. Vérifier que les messages EN sont bien chargés
4. Vérifier la console pour erreurs de chargement

### **Debug**

```typescript
// Afficher toutes les traductions disponibles
const t = useTranslations();
console.log(t.raw()); // Affiche toutes les clés

// Vérifier si une clé existe
if (t.raw('namespace.key')) {
  console.log('Clé existe');
}

// Afficher la locale actuelle
import { useLocaleStore } from '@/lib/stores/localeStore';
const { locale } = useLocaleStore();
console.log('Locale actuelle:', locale);
```

---

## 📊 **ÉTAT ACTUEL**

### **Statistiques**

- **Fichiers de messages** : 2 (fr.json, en.json)
- **Lignes de traduction** : ~281 par langue
- **Namespaces** : 11
- **Pages traduites** : ~30% (Header, toasts)
- **Pages à traduire** : ~70% (login, exercises, dashboard, etc.)

### **Namespaces Disponibles**

| Namespace | Clés | Statut |
|-----------|------|--------|
| `common` | 24 | ✅ Complet |
| `auth` | 20 | ✅ Complet |
| `navigation` | 7 | ✅ Complet |
| `exercises` | 47 | ✅ Complet |
| `challenges` | 33 | ✅ Complet |
| `dashboard` | 30 | ✅ Complet |
| `badges` | 22 | ✅ Complet |
| `accessibility` | 5 | ✅ Complet |
| `theme` | 4 | ✅ Complet |
| `errors` | 11 | ✅ Complet |
| `toasts` | 43 | ✅ Complet |

### **Pages à Traduire**

- [ ] `app/login/page.tsx`
- [ ] `app/register/page.tsx`
- [ ] `app/forgot-password/page.tsx`
- [ ] `app/exercises/page.tsx`
- [ ] `app/exercise/[id]/page.tsx`
- [ ] `app/challenges/page.tsx`
- [ ] `app/challenge/[id]/page.tsx`
- [ ] `app/dashboard/page.tsx`
- [ ] `app/badges/page.tsx`
- [ ] `app/page.tsx` (homepage)

---

## 🚀 **PROCHAINES ÉTAPES**

### **Phase 1 : Industrialisation** ✅
- [x] Documentation complète
- [ ] Script de vérification des traductions
- [ ] Template pour nouvelles pages

### **Phase 2 : Migration des Pages**
- [ ] Traduire pages d'authentification
- [ ] Traduire pages exercices
- [ ] Traduire pages défis
- [ ] Traduire dashboard
- [ ] Traduire badges

### **Phase 3 : Optimisation**
- [ ] Lazy loading des messages par page
- [ ] Cache des traductions
- [ ] Validation automatique des clés

---

## 📚 **RESSOURCES**

- **Documentation next-intl** : https://next-intl-docs.vercel.app/
- **Fichiers de messages** : `frontend/messages/`
- **Provider** : `frontend/components/providers/NextIntlProvider.tsx`
- **Store** : `frontend/lib/stores/localeStore.ts`

---

## ✅ **CONCLUSION**

Ce guide documente le système i18n actuel de Mathakine. Suivez ces pratiques pour maintenir la cohérence et faciliter l'ajout de nouvelles traductions.

**Pour toute question ou amélioration, référez-vous à ce document.**

---

**Dernière mise à jour** : Janvier 2025

