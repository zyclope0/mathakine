# Analytics Service EdTech — Mathakine

> Scope : `app/services/analytics/analytics_service.py`
> Updated : 2026-03-27

---

## Objectif

Enregistrer et agréger les événements comportementaux EdTech liés à l'engagement utilisateur.
Ce service est **intentionnellement minimaliste** : seuls deux événements sont instrumentés (Quick Start analytics).

---

## Architecture

```
app/services/analytics/
└── analytics_service.py   AnalyticsService (méthodes statiques)

app/models/edtech_event.py  EdTechEvent (table edtech_events)
```

**Point d'entrée API** : `POST /api/analytics/event` → handler dans `server/handlers/analytics_handlers.py`

---

## Événements valides

```python
VALID_EVENTS = frozenset({"quick_start_click", "first_attempt"})
```

Tout autre nom d'événement est rejeté sans écriture DB (retour `False`).

| Événement | Déclencheur | Payload attendu |
|-----------|-------------|-----------------|
| `quick_start_click` | Clic sur une action Quick Start (page accueil) | `{ "guided": bool, "type": "exercise"|"challenge"|"interleaved" }` |
| `first_attempt` | Première tentative après Quick Start | `{ "timeToFirstAttemptMs": number, "type": "exercise"|"challenge"|"interleaved" }` |

---

## API publique

### `record_edtech_event` (DB sync)

```python
AnalyticsService.record_edtech_event(
    db: Session,
    *,
    event: str,
    payload: Optional[Dict[str, Any]] = None,
    user_id: Optional[int] = None,
) -> bool
```

Retourne `True` si enregistré, `False` si `event` invalide.

### `record_edtech_event_sync` (wrapper async-friendly)

```python
record_edtech_event_sync(
    event="quick_start_click",
    payload={"guided": True, "type": "exercise"},
    user_id=42,
)
```

Utilisé depuis les handlers async via `run_db_bound()`.

### `get_edtech_analytics_for_admin`

```python
AnalyticsService.get_edtech_analytics_for_admin(
    db: Session,
    *,
    since: datetime,
    event_filter: str = "",
    limit: int = 200,   # max 500
) -> Dict[str, Any]
```

Retourne :

```json
{
  "since": "2026-03-01T00:00:00",
  "aggregates": {
    "quick_start_click": { "count": 142, "avg_time_to_first_attempt_ms": null },
    "first_attempt": {
      "count": 89,
      "avg_time_to_first_attempt_ms": 4320,
      "by_type": { "exercise": 60, "challenge": 25, "interleaved": 4 }
    }
  },
  "ctr_summary": {
    "total_clicks": 142,
    "guided_clicks": 98,
    "guided_rate_pct": 69.0,
    "by_type": { "exercise": 80, "challenge": 50, "interleaved": 12 }
  },
  "unique_users": 37,
  "events": [...]
}
```

---

## Modèle DB

Table `edtech_events` (`app/models/edtech_event.py`) :

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | Integer PK | Auto-incrément |
| `user_id` | Integer FK nullable | `users.id` — null si non connecté |
| `event` | String | Nom de l'événement (`quick_start_click`, `first_attempt`) |
| `payload` | JSONB | Données libres (validées à l'écriture) |
| `created_at` | DateTime TZ | Horodatage serveur |

---

## Limitations connues

- Pas de dédoublonnage : un clic rapide déclenche N événements `quick_start_click`.
- Les valeurs `timeToFirstAttemptMs` négatives sont filtrées silencieusement (décalage horaire, données de test).
- Pas de TTL ou purge automatique — `scripts/truncate_edtech_events.py` pour maintenance manuelle.
- Surface admin uniquement : aucun endpoint public de consultation des agrégats.

---

## Scripts de maintenance

| Script | Usage |
|--------|-------|
| `scripts/truncate_edtech_events.py` | Purge les événements au-delà d'un horizon |
| `scripts/cleanup_edtech_aberrant_data.py` | Supprime les données aberrantes (valeurs négatives, payloads malformés) |

Voir `docs/01-GUIDES/SCRIPTS_UTILITIES.md` pour les commandes exactes.
