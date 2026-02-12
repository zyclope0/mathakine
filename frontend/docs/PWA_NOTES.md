# 📝 Notes PWA - Warnings et Erreurs Normales

**Date** : 9 Novembre 2025

---

## ✅ **Warnings Corrigés**

### **1. themeColor et viewport dans metadata**

**Warning** :

```
⚠ Unsupported metadata themeColor is configured in metadata export.
⚠ Unsupported metadata viewport is configured in metadata export.
```

**Cause** : Next.js 16 recommande de déplacer `themeColor` et `viewport` vers `generateViewport()`.

**Solution** : ✅ **Corrigé** dans `app/layout.tsx` :

- `themeColor` et `viewport` déplacés vers `generateViewport()`
- Les warnings ne devraient plus apparaître

---

## ⚠️ **Erreurs Normales en Développement**

### **1. GET /sw.js 404**

**Erreur** : `GET /sw.js 404`

**Cause** : Normal en développement car PWA est désactivée :

```typescript
disable: process.env.NODE_ENV === "development";
```

**Explication** :

- Le Service Worker n'est généré qu'en production
- En développement, cette erreur est attendue et peut être ignorée
- Le Service Worker sera disponible après `npm run build`

**Action** : ✅ **Aucune action requise** - C'est normal

---

### **2. GET /icons/icon-\*.png 404**

**Erreur** : `GET /icons/icon-144x144.png 404`

**Cause** : Les icônes PWA n'ont pas encore été créées.

**Explication** :

- Les icônes doivent être créées par un designer
- Pour l'instant, des placeholders peuvent être utilisés
- Le manifest référence ces icônes, donc le navigateur les demande

**Action** :

- Créer les icônes dans `public/icons/` (voir `public/icons/README.md`)
- Ou utiliser des placeholders temporaires

**Note** : Ces erreurs n'empêchent pas l'application de fonctionner, mais la PWA ne sera pas installable sans icônes valides.

---

## 🎯 **Résumé**

| Type    | Message                             | Status          | Action       |
| ------- | ----------------------------------- | --------------- | ------------ |
| Warning | `themeColor/viewport` dans metadata | ✅ Corrigé      | Aucune       |
| 404     | `/sw.js`                            | ✅ Normal (dev) | Aucune       |
| 404     | `/icons/icon-*.png`                 | ⚠️ À créer      | Créer icônes |

---

## 📋 **Checklist**

- [x] Warnings `themeColor/viewport` corrigés
- [x] Erreur `/sw.js` expliquée (normal en dev)
- [ ] Icônes PWA à créer (optionnel pour l'instant)

---

**Dernière mise à jour** : 9 Novembre 2025
