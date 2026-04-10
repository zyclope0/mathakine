# F02 - DailyChallengesWidget

> Date : 2026-03-06  
> Reference feature : [F02_DEFIS_QUOTIDIENS.md](../../02-FEATURES/F02_DEFIS_QUOTIDIENS.md)

---

## Vue d'ensemble

Widget dashboard qui affiche les 3 defis quotidiens de l'utilisateur :

- volume
- type specifique
- logique

Emplacement :

- onglet Vue d'ensemble du dashboard

---

## Source de verite runtime

- composant : `frontend/components/dashboard/DailyChallengesWidget.tsx`
- hook : `frontend/hooks/useDailyChallenges.ts`
- endpoint : `GET /api/daily-challenges`
- types : `frontend/types/api.ts`

---

## Contraintes UX

- 3 cartes maximum
- progression `X/3`
- CTA vers l'entrainement si des defis restent en attente
- fonds neutres et accent de couleur seulement sur les icones

---

## i18n

Les libelles lives sous :

- `dashboard.dailyChallenges`

dans :

- `frontend/messages/fr.json`
- `frontend/messages/en.json`

---

## Notes techniques

- le hook utilise `queryKey: ["daily-challenges"]`
- l'invalidation se fait lors du refresh dashboard via React Query
