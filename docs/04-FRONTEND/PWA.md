# Progressive Web App (PWA) — Mathakine

> Dernière mise à jour : 22/02/2026  
> Package : `@ducanh2912/next-pwa` (compatible Next.js 16 App Router)

---

## Configuration

### `next.config.ts`

```typescript
import withPWA from "@ducanh2912/next-pwa";

const pwaConfig = withPWA({
  dest: "public",
  cacheOnFrontEndNav: true,
  aggressiveFrontEndNavCaching: true,
  reloadOnOnline: true,
  swcMinify: true,
  disable: process.env.NODE_ENV === "development", // Désactivé en dev
  workboxOptions: { /* stratégies de cache */ },
});
```

**Important** : Le fichier contient aussi `turbopack: {}` pour éviter le conflit Turbopack/webpack (Next.js 16 + next-pwa).

---

## Manifest (`public/manifest.json`)

| Propriété | Valeur |
|---|---|
| Nom complet | Mathakine - Apprentissage Mathématique Adaptatif |
| Nom court | Mathakine |
| Display | `standalone` (application native) |
| Thème couleur | `#8b5cf6` (violet spatial) |
| Fond | `#0a0a0f` (noir spatial) |
| Orientation | `portrait-primary` |

**Shortcuts** : Exercices (`/exercises`), Défis (`/challenges`), Dashboard (`/dashboard`)

**Icônes requises** (dans `public/icons/`) : 72, 96, 128, 144, 152, 192, 384, 512 px.  
Les icônes 192 et 512 doivent être maskable (safe zone 80%).  
⚠️ Les icônes de petite taille sont actuellement des placeholders — à créer par un designer.

---

## Service Worker

Généré automatiquement dans `public/sw.js` lors du build production (`npm run build`).  
**Désactivé en développement** — l'erreur `GET /sw.js 404` en dev est normale et attendue.

### Stratégies de cache

| Ressource | Stratégie | Durée | Max entries |
|---|---|---|---|
| Fonts Google | CacheFirst | 1 an | 10 |
| Images (PNG, JPG, WebP, AVIF…) | CacheFirst | 30 jours | 100 |
| API (`/api/*`) | NetworkFirst | 5 min | 50 |

**NetworkFirst pour l'API** : données dynamiques, besoin de fraîcheur, fallback cache si offline.

---

## Composant d'installation (`components/pwa/InstallPrompt.tsx`)

- Affiche une invite d'installation après 30 secondes d'utilisation
- Gère `beforeinstallprompt` (capture) et `appinstalled` (confirmation)
- Se masque si l'app est déjà installée
- Intégré dans `app/layout.tsx`

---

## Mode Offline

**Page** : `app/offline/page.tsx` — affichée automatiquement sans connexion.

| Fonctionnalité | Disponible offline |
|---|---|
| Navigation pages visitées | ✅ (cache) |
| Affichage exercices/défis en cache | ✅ |
| Génération d'exercices IA | ❌ (API requise) |
| Soumission de réponses | ❌ (API requise) |

Rechargement automatique quand la connexion revient (`reloadOnOnline: true`).

---

## Tester la PWA

La PWA est **uniquement active en production**. Pour tester :

```bash
npm run build
npm start
# Ouvrir http://localhost:3000
```

**Vérifications** :
1. `http://localhost:3000/manifest.json` — JSON valide
2. DevTools > Application > Service Workers — `sw.js` enregistré
3. DevTools > Application > Manifest — "Add to homescreen" disponible
4. DevTools > Network > Offline — pages cachées fonctionnelles

**Lighthouse** : DevTools > Lighthouse > Progressive Web App → audit complet.

---

## Dépannage

### `GET /sw.js 404`
Normal en développement (PWA désactivée). Aucune action requise.

### `GET /icons/icon-*.png 404`
Les icônes PWA ne sont pas encore créées. L'app fonctionne mais ne peut pas être installée. Action : créer les icônes dans `public/icons/`.

### Conflit Turbopack/webpack
```
ERROR: This build is using Turbopack, with a `webpack` config and no `turbopack` config.
```
Résolu dans `next.config.ts` avec `turbopack: {}`. Si l'erreur réapparaît, vérifier que cette clé est présente.

### PWA non mise à jour après déploiement
Le Service Worker met en cache les assets. Stratégies :
- Forcer le refresh : `navigator.serviceWorker.getRegistrations().then(r => r.forEach(sw => sw.unregister()))`
- En prod : incrémenter la version dans `next.config.ts`

---

## Ressources

- [next-pwa GitHub](https://github.com/Ducanh2912/next-pwa)
- [Web App Manifest MDN](https://developer.mozilla.org/en-US/docs/Web/Manifest)
- [Workbox Documentation](https://developers.google.com/web/tools/workbox)
- [Service Worker API MDN](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)
