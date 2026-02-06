# Endpoints et leur intégration Frontend

> État au 06/02/2026

## Vue d'ensemble

Ce document liste les endpoints API et leur statut d'intégration dans l'interface utilisateur.

---

## 1. `/api/exercises/stats` - Statistiques globales de l'Académie

### Statut
- **Backend** : ✅ Implémenté et testé
- **Frontend** : ✅ Intégré (widget page d'accueil)
- **Admin** : 🔄 Prévu (page admin dédiée)

### Description
Retourne les statistiques globales de tous les exercices de l'Académie (pas les stats d'un utilisateur spécifique).

### Différence avec `/api/users/stats`
| `/api/exercises/stats` | `/api/users/stats` |
|------------------------|-------------------|
| Stats **globales** de l'Académie | Stats **personnelles** d'un utilisateur |
| Tous les exercices | Exercices de l'utilisateur connecté |
| Public (pas d'auth requise) | Auth requise |

### Données retournées
```json
{
  "archive_status": "Chroniques accessibles",
  "academy_statistics": {
    "total_challenges": 30,
    "archived_challenges": 0,
    "ai_generated": 11,
    "ai_generated_percentage": 36.7
  },
  "by_discipline": {
    "ADDITION": {"discipline_name": "Art de l'Addition", "count": 6, "percentage": 20.0}
  },
  "by_rank": {
    "INITIE": {"rank_name": "Initié", "description": "Premier pas vers la sagesse", "count": 8}
  },
  "by_apprentice_group": {
    "6-8": {"group_name": "Novices", "count": 8}
  },
  "global_performance": {
    "total_attempts": 6,
    "successful_attempts": 4,
    "mastery_rate": 66.7,
    "message": "Les apprentis progressent..."
  },
  "legendary_challenges": [...],
  "sage_wisdom": "Citation inspirante..."
}
```

### Intégrations réalisées

#### Widget Page d'accueil (06/02/2026)
- **Fichiers** :
  - `frontend/hooks/useAcademyStats.ts` - Hook React Query
  - `frontend/components/home/AcademyStatsWidget.tsx` - Composant widget
  - `frontend/app/page.tsx` - Intégration (lazy loaded)

- **Affichage** :
  - Nombre d'épreuves disponibles
  - Taux de maîtrise global
  - Épreuves générées par IA
  - Nombre total de tentatives
  - Citation de sagesse aléatoire

#### Page Admin (À faire)
Pour une future page admin (`/admin/stats`), l'endpoint peut fournir :
- Répartition détaillée par discipline (`by_discipline`)
- Répartition par rang/difficulté (`by_rank`)
- Répartition par groupe d'âge (`by_apprentice_group`)
- Top 5 des épreuves les plus tentées (`legendary_challenges`)

```tsx
// Exemple d'utilisation pour page admin
import { useAcademyStats } from '@/hooks/useAcademyStats';

export default function AdminStatsPage() {
  const { stats, isLoading } = useAcademyStats();
  
  // Graphiques détaillés avec stats.by_discipline, stats.by_rank, etc.
}
```

---

## Résumé

| Endpoint | Backend | Frontend Public | Admin |
|----------|---------|-----------------|-------|
| `/api/exercises/stats` | ✅ | ✅ Widget accueil | 🔄 Prévu |
| `/api/users/stats` | ✅ | ✅ Dashboard | - |

---

**Auteur** : Assistant IA  
**Date** : 06/02/2026  
**Dernière mise à jour** : 06/02/2026 - Intégration widget page d'accueil
