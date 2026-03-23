# F02 — DailyChallengesWidget

> **Date :** 06/03/2026  
> **Référence feature :** [F02_DEFIS_QUOTIDIENS.md](../02-FEATURES/F02_DEFIS_QUOTIDIENS.md)

---

## 1. Vue d'ensemble

Widget affichant les 3 défis quotidiens de l'utilisateur : volume (exercices quelconques), type spécifique (ex: Soustraction), défis logiques.

**Emplacement :** Onglet Vue d'ensemble du dashboard, grille col-span-8 à côté de StreakWidget (col-span-4).

---

## 2. Composant

**Fichier :** `frontend/components/dashboard/DailyChallengesWidget.tsx`

**Hook :** `useDailyChallenges()` → `GET /api/daily-challenges`

**Types :** `DailyChallenge` dans `frontend/types/api.ts`

---

## 3. Structure UI

- **En-tête :** Icône calendrier, titre "Défis du jour", sous-titre "3 objectifs pour garder le rythme", compteur X/3 Terminé
- **Liste :** 3 cartes (ChallengeItem) par défi
  - Icône : Calculator (volume), Target (specific), Swords (logic), CheckCircle2 (complété)
  - Conteneur icône : `bg-primary/10 text-primary` (pending) ou `bg-success/20 text-success` (complété)
  - Fond carte : `bg-muted/30` (pending) ou `bg-success/5` (complété)
  - Badge XP : `inline-flex rounded-full px-2.5 py-0.5 text-xs font-semibold bg-primary/10 text-primary border border-primary/20`
- **CTA :** "S'entraîner maintenant" → `/exercises` (si défis en attente)

---

## 4. Design system (Anti-Cheap)

| Élément | Règle |
|---------|-------|
| Fonds des cartes pending | `bg-muted/30 hover:bg-muted/50 border-border/50` — neutre, pas de couleur lourde |
| Accent couleur | Uniquement sur le conteneur d'icône à gauche |
| Pluralisation | ICU format sans "(s)" : `{count, plural, one {# exercice} other {# exercices}}` |
| Badges XP | Badge arrondi avec bordure, pas de texte nu |

---

## 5. Traductions

**Clés :** `dashboard.dailyChallenges` (fr.json, en.json)

- `volume`, `specific`, `logic`, `fallback` — format ICU plural
- `completed`, `pending`, `bonus`, `cta`, `expiresAt`

---

## 6. Layout responsive

- **Desktop (md+) :** Grille 12 colonnes — Défis col-span-8, série col-span-4
- **Mobile :** Empilés verticalement (grid-cols-1)
- **Hauteur uniforme :** `flex-1 min-h-0` sur les deux widgets pour aligner les hauteurs

---

## 7. Invalidation cache

Le hook `useDailyChallenges` utilise `queryKey: ["daily-challenges"]`. Invalidation à faire lors du refresh dashboard : `queryClient.invalidateQueries({ queryKey: ["daily-challenges"] })`.
