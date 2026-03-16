# Endpoints et integrations frontend/admin encore a completer

> Etat de reference au 14/03/2026
> Document actif de gaps restants, pas inventaire historique exhaustif

## Resume

La majorite des endpoints backend visibles cote utilisateur et admin sont deja
relies. Ce document ne recense plus de gap endpoint prioritaire prouve a ce
stade.

Le quick win `admin + /api/exercises/stats` a ete implemente le 14/03/2026 :

- hook existant reutilise : `frontend/hooks/useAcademyStats.ts`
- section admin ajoutee sur `frontend/app/admin/page.tsx`
- composant dedie : `frontend/components/admin/AdminAcademyStatsSection.tsx`

Les endpoints deja relies en production n'ont pas vocation a rester listes ici.

## 1. Endpoints deja relies a ne plus traiter comme gaps

Les points suivants ne doivent plus etre classes comme "non integres" :

- `/api/exercises/stats`
- `/api/users/leaderboard`
- `/api/users/me`
- `/api/users/me/password`
- `/api/users/me/sessions`
- `/api/challenges/badges/progress`
- `/api/recommendations/complete`
- endpoints diagnostic deja relies au frontend
- endpoints admin principaux deja relies (`overview`, `audit-log`, `moderation`, `reports`, `config`, `content`, `users`, `feedback`, `analytics`)

## 2. Gaps encore plausibles mais non reouverts ici

Ce document n'ouvre pas de nouveau chantier sans preuve de besoin produit.
Les sujets suivants restent possibles mais non prioritaires sans signal terrain :

- preuves de branches d'erreur fines sur certains endpoints admin/feedback/analytics
- polish UX auth au refresh (`F36`) si le flash est encore reproductible

## 3. Regle de maintenance du document

Quand un endpoint est relie en production ou qu'un gap est ferme, il doit etre :

1. retire de ce document
2. deplace dans le changelog ou dans le recap de l'iteration concernee si besoin

Ce fichier doit rester court, verifie et exploitable.
