# Analytics EdTech — Parcours guidé et conversion

> **Statut** : Implémenté  
> **Date** : 25/02/2026  
> **Cible** : Admins (rôle archiviste)

## Objectif

Mesurer l'efficacité du bloc Quick Start (parcours guidé) :
- **CTR Quick Start** : clics exercice vs défi, guidé vs libre
- **Temps vers 1er attempt** : délai entre vue du dashboard et première soumission
- **Conversion** : exercice vs défi, parcours guidé ou non

---

## 1. Instrumentation frontend

### 1.1 Événements collectés

| Événement | Déclencheur | Payload |
|-----------|-------------|---------|
| `quick_start_click` | Clic sur un CTA Quick Start (exercice ou défi) | type, guided, targetId |
| `first_attempt` | Première soumission (exercice ou défi) après visite dashboard | type, targetId, timeToFirstAttemptMs |

### 1.2 Module `lib/analytics/edtech.ts`

- `trackDashboardView()` — enregistre le timestamp (sessionStorage) quand le bloc Quick Start est affiché
- `trackQuickStartClick(payload)` — appelé au clic sur un lien exercice/défi
- `trackFirstAttempt(type, targetId)` — appelé lors de la soumission d'une tentative (useSubmitAnswer, useChallenges)

### 1.3 Envoi des données

- **Fire-and-forget** : POST `/api/analytics/event` sans bloquer l'UX
- **CustomEvent** `mathakine-edtech` pour intégrations externes (GA, Plausible, etc.)

---

## 2. Persistance et API

### 2.1 Table `edtech_events`

| Colonne | Type | Description |
|---------|------|-------------|
| id | INTEGER | Clé primaire |
| user_id | INTEGER | Utilisateur (FK users, SET NULL) |
| event | VARCHAR(50) | quick_start_click, first_attempt |
| payload | JSONB | type, guided, targetId, timeToFirstAttemptMs |
| created_at | TIMESTAMPTZ | Horodatage |

**Migration** : `20260225_add_edtech_events.py`

### 2.2 Endpoints

| Méthode | Route | Description | Auth |
|---------|-------|-------------|------|
| POST | `/api/analytics/event` | Enregistrer un événement | require_auth |
| GET | `/api/admin/analytics/edtech` | Consulter agrégats + liste | require_admin |

**Paramètres GET** : `period=7d|30d`, `event=quick_start_click|first_attempt`, `limit=200` (max 500)

### 2.3 Réponse API admin

```json
{
  "period": "7d",
  "since": "2026-02-18T00:00:00Z",
  "aggregates": {
    "quick_start_click": { "count": 42, "avg_time_to_first_attempt_ms": null },
    "first_attempt": { "count": 28, "avg_time_to_first_attempt_ms": 45000 }
  },
  "ctr_summary": {
    "total_clicks": 42,
    "guided_clicks": 31,
    "guided_rate_pct": 73.8
  },
  "events": [...]
}
```

---

## 3. Page Admin

**Route** : `/admin/analytics`

**Accès** : rôle `archiviste` uniquement.

**Contenu** :
- Filtres : période (7d / 30d), type d'événement
- KPIs : clics Quick Start, % guidés, 1ers attempts, temps moyen
- Table des derniers événements (date, type, user_id, détails)

---

## 4. Logs

Les événements sont aussi loggés avec le préfixe `[EDTECH]` pour grep :

```bash
grep "\[EDTECH\]" /var/log/mathakine.log
```

Format JSON par ligne.

---

## 5. Références

- **Frontend** : `frontend/lib/analytics/edtech.ts`, `QuickStartActions.tsx`, `useSubmitAnswer.ts`, `useChallenges.ts`
- **Backend** : `server/handlers/analytics_handlers.py`
- **Modèle** : `app/models/edtech_event.py`
