# Audit Dashboard — Incohérences et duplications

**Date :** Février 2026  
**Type :** Audit actif  
**Statut :** Recos partielles

---

## Problèmes identifiés

### 1. Imports inutilisés (page.tsx)
- `LevelIndicatorSkeleton` — importé mais jamais utilisé
- `RecommendationsSkeleton` — importé mais jamais utilisé

**Impact :** Dead code, bundle légèrement gonflé.

---

### 2. Duplication dans fr.json
- La clé `"tabs"` apparaît **deux fois** dans `dashboard` (lignes 614 et 669)
- En JSON, la seconde écrase la première — redondance sans effet fonctionnel
- À supprimer : le bloc dupliqué (lignes 669-676)

---

### 3. Labels mobiles non traduits (sm:hidden)
```tsx
<span className="sm:hidden">Vue</span>
<span className="sm:hidden">Recommandés</span>
<span className="sm:hidden">Stats</span>
<span className="sm:hidden">Détails</span>
```
- Hardcodés en français
- Même pattern que profile (Profil, Prefs, Stats) — incohérence assumée
- **Recommandation :** Ajouter `tabs.overviewShort`, etc. pour i18n complète

---

### 4. handleRefresh — rafraîchissement partiel
- `handleRefresh` appelle uniquement `refetch()` de `useUserStats`
- Les hooks `useProgressStats` et `useChallengesProgress` ne sont **pas** invalidés
- L'utilisateur s'attend à un rafraîchissement complet
- **Recommandation :** Invalider `["user","progress"]` et `["user","challenges","progress"]`

---

### 5. Skeleton loading vs structure réelle
- Le skeleton affiche : StatsCard×3, Chart×2, PerformanceByType
- L'onglet Vue d'ensemble affiche : StatsCard×3, StreakWidget, ChallengesProgressWidget, CategoryAccuracyChart, RecentActivity
- Le skeleton ne reflète pas la nouvelle structure à onglets
- **Impact :** Léger décalage visuel au chargement — acceptable pour l'instant

---

### 6. État vide `!stats`
- Condition `{!stats && <EmptyState />}` en bas du render
- Avec les early returns (`isLoading`, `error`), `stats` est normalement défini quand on arrive là
- **Statut :** Garde-fou correct — pas de changement

---

## Résumé des corrections à appliquer

| # | Correction | Priorité |
|---|------------|----------|
| 1 | Supprimer imports LevelIndicatorSkeleton, RecommendationsSkeleton | Haute |
| 2 | Supprimer bloc `tabs` dupliqué dans fr.json | Haute |
| 3 | Ajouter tabs.overviewShort etc. + utiliser t() pour mobile | Moyenne |
| 4 | handleRefresh : invalider progress + challenges | Moyenne |
