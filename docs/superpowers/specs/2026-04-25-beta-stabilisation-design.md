# Design — Stabilisation beta v3.6.0

**Date :** 2026-04-25  
**Scope :** Solidification sans feature nouvelle — audit sécurité, audit runtime, métriques Phase 2A, alignement docs  
**Contrainte :** Solo founder, zéro refonte, zéro migration DB

---

## Contexte

Mathakine est en `3.6.0-beta.4`. Les phases 0, 1A et 1B du plan de solidification défis sont réalisées. L'objectif de cette spec est de fermer les gaps restants pour valider la beta et rendre le projet solide avant toute ouverture publique.

**Ce qui n'est PAS dans le scope :**
- Nouvelles features produit
- Migration DB
- Refonte d'architecture
- Nouveaux providers IA
- Bump seuils Vitest sans mesure CI

---

## Ordre d'exécution

1. Audit sécurité → corrections findings bloquants
2. Audit solidité runtime → corrections findings bloquants
3. Fermer Phase 2A métriques + generation_confidence log-only
4. Alignement docs/version

---

## Section 1 — Audit sécurité

### Périmètre

| Domaine | Fichiers cibles |
|---------|----------------|
| Auth/JWT | `server/auth.py`, `app/services/auth/`, `app/core/security.py` |
| Headers sécurité | `server/middleware.py` |
| PII logs | `app/services/auth/auth_service.py` |
| Pipeline SSE défis | `app/services/challenges/challenge_ai_service.py` |
| Circuit breaker | `app/core/` (circuit breaker) |

### Points de vérification

- **Auth/JWT** : fenêtre `recover_refresh_token_from_access_token` = 3600s (assumée, pas 7j) ; cookies `SameSite`/`Secure` conditionnels à `_is_production()` uniquement
- **Headers** : `SECURE_HEADERS` actif uniquement si `_is_production()` — vérifier que le flag est bien positionné en staging/prod Render ; `HSTS` ne sort pas en dev/CI
- **PII logs** : alias HMAC-SHA256 en place — vérifier qu'aucun chemin de log ne laisse passer `username`/`email` en clair (notamment les handlers HTTP level)
- **SSE défis** : un défi `rejected` ne part jamais au frontend — vérifier que le chemin d'erreur SSE ferme proprement le stream sans données partielles
- **Circuit breaker multi-workers** : `HALF_OPEN` en mémoire process — état divergent entre workers Gunicorn est assumé (in-memory) ; vérifier que c'est documenté et qu'aucun code ne suppose un état partagé
- **Rate limiting** : comportement si `REDIS_URL` absent en prod — vérifier qu'il y a un fallback explicite ou une erreur de démarrage claire

### Méthode

`/octo:security` sur les fichiers listés, puis revue manuelle des findings. Seuls les **findings bloquants** (crash potentiel, fuite de données, auth bypass) sont corrigés dans ce sprint. Les findings cosmétiques sont loggués dans la roadmap.

---

## Section 2 — Audit solidité runtime

### Périmètre

| Domaine | Fichiers cibles |
|---------|----------------|
| Contrats API frontend↔backend | Hooks TS critiques + handlers Python correspondants |
| Pipeline SSE défis | `challenge_ai_service.py` |
| Validateur | `challenge_validator.py` (63KB) |
| Deduction solver | `challenge_deduction_solver.py` |
| Gamification ledger | `app/services/gamification/`, `point_events` |

### Points de vérification

- **Contrats API** : champs optionnels côté Python traités comme obligatoires côté TypeScript dans `useChallengeSolverController`, `useAIChallengeGenerator`, `useSubmitAnswer` — ou l'inverse
- **SSE edge cases** : `finish_reason=length` non détecté → JSON tronqué accepté silencieusement ; fallback `gpt-4o-mini` qui échoue également ; stream coupé sans event `done`
- **Validator faux négatifs** : règles contradictoires ou lacunaires sur `deduction`, `chess`, `probability` — les types ayant reçu le plus de correctifs récents
- **Métriques in-memory** : `GenerationMetrics` perdue au redémarrage worker — vérifier que c'est explicitement documenté dans `get_summary()` (disclaimer existe, vérifier qu'il est suffisant)
- **Deduction solver timeout** : absence de timeout documentée dans le plan — vérifier si un puzzle pathologique peut bloquer le worker ; si oui, finding bloquant
- **Gamification double-comptage** : un challenge SSE retenté (après `rejected`) peut-il déclencher deux fois le `point_events` ledger si la seconde génération réussit ?

### Méthode

`/octo:review` ciblé sur les fichiers listés. Même règle : seuls les findings bloquants sont corrigés maintenant.

---

## Section 3 — Phase 2A métriques + generation_confidence

### Fichiers modifiés

- `app/utils/generation_metrics.py` — extension des compteurs et calculs
- `app/services/challenges/challenge_ai_service.py` — instrumentation chess repair + calcul confidence

### Ajouts à `GenerationMetrics`

**Compteurs chess repair explicites** (à instrumenter dans `challenge_ai_service.py`) :
```python
chess_repair_attempted: int  # chaque déclenchement du repair OpenAI chess
chess_repair_succeeded: int  # repair validé (→ repaired_by_ai)
chess_repair_failed: int     # repair tenté mais toujours invalide
```

**Taux dérivés dans `get_summary()`** :
```python
repair_success_rate   # repaired_by_ai / (repaired + repaired_by_ai) par type
fallback_rate         # tentatives fallback / total, avec cause typée
fallback_causes       # {empty_response, length_truncation, fallback_empty_response}
```

**Percentiles latence** (données déjà dans `_generation_history`) :
```python
latency_p50_ms   # P50 par type
latency_p95_ms   # P95 par type
```

### generation_confidence (log-only)

Calculé à la fin de `normalize_generated_challenge()` dans `challenge_ai_service.py` :

| Condition | Delta |
|-----------|-------|
| Validation pass premier essai | +0.1 |
| Repair déclenché | -0.3 |
| Erreur auto-corrigée (par occurrence) | -0.1 |
| Difficulty clampée | -0.2 |

- Score clampé entre 0.0 et 1.0
- **Loggué uniquement** avec le statut pipeline — pas de champ DB, pas de migration
- Pas exposé dans `get_summary()` pour l'instant (log-only = bruit minimal)

### Contraintes

- Aucune migration DB
- Aucun nouvel endpoint
- Les nouveaux champs s'ajoutent au `get_summary()` existant sans casser le contrat actuel

---

## Section 4 — Alignement docs/version

### Fichiers à corriger

| Fichier | Problème | Correction |
|---------|----------|-----------|
| `README_TECH.md` | Affiche `3.6.0-beta.2` | Mettre à jour à `3.6.0-beta.4` + état ACTIF-03 fermé, seuils 46/38/42/48 |
| `CLAUDE.md` | Version `3.6.0-beta.2` | Mettre à jour à `3.6.0-beta.4` |
| `memory/project_mathakine_context.md` | Snapshot encore sur beta.3 | Mettre à jour à beta.4 + état plan solidification |

### Règle

Patches ciblés sur les champs de version et d'état uniquement. Pas de réécriture globale. Pas de nouvelles sections.

---

## Definition of Done

- [ ] Audit sécurité terminé, findings bloquants listés et corrigés ou explicitement assumés
- [ ] Audit runtime terminé, findings bloquants listés et corrigés ou explicitement assumés
- [ ] `GenerationMetrics` expose `repair_success_rate`, `fallback_rate`, `latency_p50/p95`, chess counters
- [ ] `generation_confidence` loggué (pas persisté) sur chaque génération défi
- [ ] `README_TECH.md`, `CLAUDE.md`, `memory/project_mathakine_context.md` sur `3.6.0-beta.4`
- [ ] Aucune feature nouvelle introduite
- [ ] Aucune migration DB
- [ ] Tests existants toujours verts (pas de régression)
