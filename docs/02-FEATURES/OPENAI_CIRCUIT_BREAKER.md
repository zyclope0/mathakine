# Circuit Breaker OpenAI — Mathakine

> Scope : `app/utils/circuit_breaker.py`
> Updated : 2026-03-27

---

## Objectif

Éviter d'enchaîner les timeouts et appels inutiles vers OpenAI quand le service amont est dégradé.
Le circuit breaker est **process-local** : un seul breaker partagé par worker Gunicorn, non synchronisé entre workers.

---

## États

```
         5 échecs / 120 s
CLOSED ─────────────────────→ OPEN
  ↑                               │
  │ succès sonde             60 s cooldown
  │                               │
  └────────── HALF_OPEN ←─────────┘
               (1 sonde)
```

| État | Comportement |
|------|-------------|
| `CLOSED` | Appels autorisés normalement |
| `OPEN` | Appels refusés — message utilisateur renvoyé sans appel OpenAI |
| `HALF_OPEN` | Un seul appel test autorisé ; succès → `CLOSED`, échec → `OPEN` |

---

## Seuils par défaut

| Paramètre | Valeur | Constante |
|-----------|--------|-----------|
| Seuil d'ouverture | 5 échecs | `OPENAI_CIRCUIT_FAILURE_THRESHOLD` |
| Fenêtre de comptage | 120 s | `OPENAI_CIRCUIT_FAILURE_WINDOW_SECONDS` |
| Cooldown avant sonde | 60 s | `OPENAI_CIRCUIT_COOLDOWN_SECONDS` |

---

## Exceptions comptées (ouvrent le circuit)

```python
openai.APITimeoutError       # timeout réseau
openai.RateLimitError        # HTTP 429
openai.APIConnectionError    # erreur réseau bas niveau
openai.InternalServerError   # HTTP 500+
openai.APIStatusError        # HTTP 5xx ou 408
```

**Non comptées** : erreurs client HTTP 4xx (hors 429), erreurs métier internes, erreurs de validation schema.

---

## Utilisation dans les services

Le breaker est instancié en singleton global :

```python
# app/utils/circuit_breaker.py
openai_workload_circuit_breaker = OpenAiWorkloadCircuitBreaker()
```

Dans les services IA (`exercise_ai_service.py`, `challenge_ai_service.py`) :

```python
from app.utils.circuit_breaker import (
    openai_workload_circuit_breaker,
    is_countable_openai_failure,
)

if not openai_workload_circuit_breaker.check_allow():
    # Renvoyer OPENAI_CIRCUIT_OPEN_USER_MESSAGE via SSE
    yield error_event(OPENAI_CIRCUIT_OPEN_USER_MESSAGE)
    return

try:
    # appel OpenAI ...
    openai_workload_circuit_breaker.record_success()
except Exception as exc:
    if is_countable_openai_failure(exc):
        openai_workload_circuit_breaker.record_countable_failure()
    else:
        openai_workload_circuit_breaker.probe_finished_without_countable_outcome()
    raise
```

---

## Message utilisateur (circuit OPEN)

```
"Le service de génération IA est temporairement indisponible. Veuillez réessayer dans quelques instants."
```

Ce message est visible côté client dans le toast SSE `error`.

---

## Limites documentées

- **Process-local** : chaque worker Gunicorn maintient son propre état. En déploiement multi-worker, un worker peut être en `OPEN` pendant qu'un autre est en `CLOSED`. Render équilibre le trafic entre les workers.
- **Non persisté** : redémarrage du worker → `CLOSED` immédiat.
- **Granularité unique** : un seul breaker pour exercices et défis — une panne OpenAI sur les défis ouvre aussi le circuit pour les exercices.
- **Pas de bulkhead** : les flux SSE actifs au moment de l'ouverture ne sont pas interrompus.

---

## Troubleshooting

### Circuit resté OPEN trop longtemps

Le cooldown est de 60 s. Si le service OpenAI est revenu mais le circuit ne se ferme pas :
- vérifier qu'une sonde (`HALF_OPEN`) a bien réussi ;
- redémarrer le worker en dernier recours (`CLOSED` initial).

### `probe_finished_without_countable_outcome`

Appelé quand une erreur non-OpenAI (ex. erreur validation schema) survient pendant la sonde.
Libère la sonde sans réouvrir le circuit — permet une nouvelle sonde au prochain appel.
