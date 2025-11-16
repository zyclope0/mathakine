# 🔧 Dépannage PWA - Frontend Mathakine

**Date** : 9 Novembre 2025

---

## ⚠️ **Erreurs Courantes**

### **1. Erreur Turbopack/Webpack**

**Erreur** :
```
ERROR: This build is using Turbopack, with a `webpack` config and no `turbopack` config.
```

**Cause** : Next.js 16 utilise Turbopack par défaut, mais `next-pwa` ajoute une configuration webpack.

**Solution** : Ajouter `turbopack: {}` dans `next.config.ts` :

```typescript
const nextConfig: NextConfig = {
  turbopack: {}, // Résout le conflit Turbopack/webpack
  // ... reste de la config
};
```

**Status** : ✅ **Résolu** dans `next.config.ts`

---

### **2. Warning Middleware Déprécié**

**Warning** :
```
⚠ The "middleware" file convention is deprecated. Please use "proxy" instead.
```

**Cause** : Next.js recommande d'utiliser "proxy" pour certaines fonctionnalités de routage.

**Solution** : 
- Le middleware fonctionne toujours et est toujours supporté
- Le warning peut être ignoré pour l'instant
- Le middleware est utilisé pour la protection des routes, pas pour le proxy
- Si nécessaire, migrer vers `next.config.ts` avec configuration `rewrites` (futur)

**Status** : ⚠️ **Warning acceptable** - Pas d'action requise pour l'instant

---

### **3. Service Worker Non Généré**

**Problème** : Le Service Worker n'est pas généré lors du build.

**Solutions** :

1. **Vérifier que PWA n'est pas désactivée** :
   ```typescript
   disable: process.env.NODE_ENV === "development" // OK en dev
   ```

2. **Build en production** :
   ```bash
   npm run build
   ```

3. **Vérifier les fichiers générés** :
   - `public/sw.js` doit exister après le build
   - `public/workbox-*.js` doit exister

4. **Vérifier les permissions** :
   - Le dossier `public/` doit être accessible en écriture

---

### **4. Manifest Non Trouvé**

**Problème** : `manifest.json` retourne 404.

**Solutions** :

1. **Vérifier le chemin** :
   - Le fichier doit être dans `public/manifest.json`
   - Accessible via `http://localhost:3000/manifest.json`

2. **Vérifier les métadonnées** :
   ```typescript
   // Dans app/layout.tsx
   manifest: "/manifest.json",
   ```

3. **Vérifier le build** :
   - Le fichier `manifest.json` doit être copié dans `.next/static/`

---

### **5. Installation PWA Non Disponible**

**Problème** : Le bouton "Installer" n'apparaît pas.

**Solutions** :

1. **Vérifier HTTPS** :
   - PWA nécessite HTTPS en production
   - En développement, utiliser `localhost` (HTTPS simulé)

2. **Vérifier le manifest** :
   - Le manifest doit être valide
   - Les icônes doivent exister

3. **Vérifier les critères PWA** :
   - Service Worker enregistré
   - Manifest valide
   - HTTPS (production)
   - Responsive design

4. **Tester avec Lighthouse** :
   - Chrome DevTools > Lighthouse > PWA
   - Vérifier les critères manquants

---

### **6. Mode Offline Ne Fonctionne Pas**

**Problème** : L'application ne fonctionne pas hors ligne.

**Solutions** :

1. **Vérifier le Service Worker** :
   - DevTools > Application > Service Workers
   - Vérifier que `sw.js` est actif

2. **Vérifier le cache** :
   - DevTools > Application > Cache Storage
   - Vérifier que les caches sont créés

3. **Vérifier les stratégies** :
   - Les pages doivent être visitées au moins une fois
   - Les assets doivent être en cache

4. **Tester la navigation** :
   - Visiter plusieurs pages en ligne
   - Passer en mode offline
   - Vérifier que les pages visitées fonctionnent

---

## 🧪 **Tests de Vérification**

### **Checklist PWA**

- [ ] Build production réussi (`npm run build`)
- [ ] Service Worker généré (`public/sw.js` existe)
- [ ] Manifest accessible (`/manifest.json` retourne 200)
- [ ] Icônes définies (même si placeholders)
- [ ] Installation disponible (Chrome DevTools)
- [ ] Mode offline fonctionne (pages visitées)
- [ ] Cache fonctionne (assets en cache)

### **Commandes de Test**

```bash
# Build production
cd frontend
npm run build

# Démarrer production
npm start

# Tester en localhost:3000
# Ouvrir Chrome DevTools > Application > Service Workers
# Vérifier que sw.js est enregistré
```

---

## 📚 **Ressources**

- [next-pwa Troubleshooting](https://github.com/Ducanh2912/next-pwa#troubleshooting)
- [Next.js Turbopack Config](https://nextjs.org/docs/app/api-reference/next-config-js/turbopack)
- [PWA Checklist](https://web.dev/pwa-checklist/)

---

**Dernière mise à jour** : 9 Novembre 2025

