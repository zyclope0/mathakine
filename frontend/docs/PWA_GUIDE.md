# 📱 Guide PWA - Frontend Mathakine

**Date** : 9 Novembre 2025  
**Status** : ✅ **PWA Configurée**

---

## 📋 **Table des Matières**

- [Configuration](#configuration)
- [Manifest](#manifest)
- [Service Worker](#service-worker)
- [Installation](#installation)
- [Mode Offline](#mode-offline)
- [Cache Strategies](#cache-strategies)
- [Tests](#tests)

---

## ⚙️ **Configuration**

### **Package Installé**

```bash
npm install @ducanh2912/next-pwa
```

**Pourquoi `@ducanh2912/next-pwa` ?**

- Compatible avec Next.js 16 App Router
- Support TypeScript
- Configuration Workbox intégrée
- Maintenance active

### **Configuration Next.js**

Le fichier `next.config.ts` est configuré avec `withPWA` :

```typescript
import withPWA from "@ducanh2912/next-pwa";

const pwaConfig = withPWA({
  dest: "public",
  cacheOnFrontEndNav: true,
  aggressiveFrontEndNavCaching: true,
  reloadOnOnline: true,
  swcMinify: true,
  disable: process.env.NODE_ENV === "development", // Désactivé en dev
  workboxOptions: {
    // Stratégies de cache configurées
  },
});
```

**Options importantes** :

- `disable: process.env.NODE_ENV === "development"` : PWA désactivée en développement
- `cacheOnFrontEndNav` : Cache automatique lors de la navigation
- `reloadOnOnline` : Rechargement automatique quand la connexion revient

---

## 📄 **Manifest**

### **Fichier `public/manifest.json`**

Le manifest définit les métadonnées de l'application PWA :

- **Nom** : Mathakine - Apprentissage Mathématique Adaptatif
- **Nom court** : Mathakine
- **Thème** : #8b5cf6 (violet spatial)
- **Fond** : #0a0a0f (noir spatial)
- **Display** : standalone (application native)
- **Orientation** : portrait-primary

### **Icônes Requises**

Les icônes doivent être placées dans `public/icons/` :

- 72x72, 96x96, 128x128, 144x144, 152x152, 192x192, 384x384, 512x512

**Note** : Les icônes 192x192 et 512x512 doivent être maskable (safe zone de 80%).

### **Shortcuts**

3 raccourcis définis :

- **Exercices** : `/exercises`
- **Défis** : `/challenges`
- **Dashboard** : `/dashboard`

---

## 🔧 **Service Worker**

### **Génération Automatique**

Le Service Worker est généré automatiquement lors du build production dans `public/sw.js`.

### **Stratégies de Cache**

#### **1. Fonts Google (CacheFirst)**

- Cache : 1 an
- Max entries : 10
- URLs : `fonts.googleapis.com`, `fonts.gstatic.com`

#### **2. Images (CacheFirst)**

- Cache : 30 jours
- Max entries : 100
- Formats : PNG, JPG, JPEG, SVG, GIF, WebP, AVIF

#### **3. API (NetworkFirst)**

- Cache : 5 minutes
- Max entries : 50
- Timeout : 10 secondes
- URLs : `/api/*`

**Pourquoi NetworkFirst pour l'API ?**

- Données dynamiques (exercices, statistiques)
- Besoin de données à jour
- Fallback vers cache si offline

---

## 📲 **Installation**

### **Composant InstallPrompt**

Le composant `InstallPrompt` (`components/pwa/InstallPrompt.tsx`) :

- Détecte si l'app peut être installée
- Affiche un prompt après 30 secondes d'utilisation
- Permet l'installation en un clic
- Se masque automatiquement si déjà installé

### **Événements Gérés**

- `beforeinstallprompt` : Capture le prompt d'installation
- `appinstalled` : Détecte l'installation réussie

### **Utilisation**

Le composant est intégré dans `app/layout.tsx` et s'affiche automatiquement.

---

## 📴 **Mode Offline**

### **Page Offline**

Une page dédiée `/offline` (`app/offline/page.tsx`) :

- S'affiche automatiquement si offline
- Bouton de réessai
- Message informatif

### **Fonctionnalités Offline**

**Disponibles** :

- Navigation entre pages visitées (cache)
- Affichage des exercices/défis en cache
- Affichage des statistiques en cache

**Non disponibles** :

- Génération d'exercices (nécessite API)
- Soumission de réponses (nécessite API)
- Synchronisation des données

### **Gestion de la Reconnexion**

- Rechargement automatique quand `online` revient
- Synchronisation des données en attente (futur)

---

## 🗄️ **Cache Strategies**

### **CacheFirst**

- **Utilisé pour** : Assets statiques (fonts, images)
- **Avantage** : Performance maximale
- **Inconvénient** : Peut servir du contenu obsolète

### **NetworkFirst**

- **Utilisé pour** : Données dynamiques (API)
- **Avantage** : Données toujours à jour
- **Inconvénient** : Nécessite connexion

### **StaleWhileRevalidate** (futur)

- **Utilisé pour** : Contenu qui peut être légèrement obsolète
- **Avantage** : Performance + fraîcheur

---

## 🧪 **Tests**

### **Build Production**

```bash
npm run build
npm start
```

### **Vérifications**

1. **Manifest** :
   - Ouvrir `http://localhost:3000/manifest.json`
   - Vérifier que le JSON est valide

2. **Service Worker** :
   - Ouvrir DevTools > Application > Service Workers
   - Vérifier que `sw.js` est enregistré

3. **Installation** :
   - Chrome DevTools > Application > Manifest
   - Vérifier que "Add to homescreen" est disponible
   - Tester l'installation

4. **Offline** :
   - DevTools > Network > Offline
   - Vérifier que les pages en cache fonctionnent
   - Vérifier la page `/offline`

### **Lighthouse PWA Audit**

```bash
# Ouvrir Chrome DevTools > Lighthouse
# Sélectionner "Progressive Web App"
# Lancer l'audit
```

**Critères PWA** :

- ✅ Manifest valide
- ✅ Service Worker enregistré
- ✅ HTTPS (production)
- ✅ Responsive design
- ✅ Thème color défini
- ✅ Icônes définies

---

## 📝 **Notes Importantes**

### **Développement**

La PWA est **désactivée en développement** pour éviter les problèmes de cache :

```typescript
disable: process.env.NODE_ENV === "development";
```

### **Production**

En production, le Service Worker est généré automatiquement lors du build.

### **Icônes**

Les icônes doivent être créées par un designer. Pour l'instant, des placeholders peuvent être utilisés.

### **HTTPS**

La PWA nécessite HTTPS en production. Render.com fournit HTTPS automatiquement.

---

## 🔗 **Ressources**

- [next-pwa Documentation](https://github.com/Ducanh2912/next-pwa)
- [Web App Manifest](https://developer.mozilla.org/en-US/docs/Web/Manifest)
- [Service Worker API](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)
- [Workbox Documentation](https://developers.google.com/web/tools/workbox)

---

## ✅ **Checklist**

- [x] Package `@ducanh2912/next-pwa` installé
- [x] Configuration `next.config.ts` complète
- [x] Manifest `manifest.json` créé
- [x] Métadonnées PWA dans `layout.tsx`
- [x] Composant `InstallPrompt` créé
- [x] Page offline créée
- [x] Stratégies de cache configurées
- [ ] Icônes PWA créées (à faire par designer)
- [ ] Tests en production effectués

---

**Dernière mise à jour** : 9 Novembre 2025
