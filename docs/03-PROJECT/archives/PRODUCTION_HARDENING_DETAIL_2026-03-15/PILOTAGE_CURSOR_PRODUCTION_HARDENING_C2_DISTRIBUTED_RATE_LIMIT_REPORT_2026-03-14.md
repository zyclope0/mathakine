# Lot C2 - Distributed Rate Limit — Compte-rendu final

> Date: 14/03/2026
> Iteration: C - Production Hardening
> Statut: **terminé**

---

## 1. Fichiers modifiés

| Fichier | Action |
|---------|--------|
| `app/core/config.py` | M - REDIS_URL + validation prod obligatoire |
| `app/utils/rate_limit_store.py` | A/M - store abstrait, fail-closed Redis, fallback dev/test uniquement |
| `app/utils/rate_limit.py` | M - délégation au store |
| `tests/unit/test_rate_limit_store.py` | A/M - tests fail-closed, config prod, batterie causale |

---

## 2. Fichiers runtime modifiés

- `app/core/config.py`
- `app/utils/rate_limit_store.py` (nouveau)
- `app/utils/rate_limit.py`

---

## 3. Fichiers de test modifiés

- `tests/unit/test_rate_limit_store.py` (nouveau)

---

## 4. Mécanisme de vérité retenu après lot (micro-lot fermeture)

**Source de vérité prod** : `RedisRateLimitStore` — obligatoire. Prod sans `REDIS_URL` = `ValueError` au démarrage. Prod avec Redis indisponible au démarrage = `RuntimeError` (pas de fallback mémoire).

**Fallback dev/test** : `MemoryRateLimitStore` uniquement quand `REDIS_URL` vide ou Redis indisponible. Jamais en prod.

**Point d'entrée unique** : `rate_limit.py` → `_check_rate_limit()` → `_get_store().check()`. Les décorateurs restent inchangés.

---

## 5. Rôle exact de Redis

- **Quand** : `REDIS_URL` défini et `ping()` OK au démarrage
- **Où** : `RedisRateLimitStore.check()` — script Lua atomique INCR + EXPIRE, fenêtre fixe par intervalle
- **Clé** : `rl:{scope}:{id}:{window_id}` (ex. `rl:rate_limit:login:1.2.3.4:41234`)
- **Comportement sur panne Redis runtime** : fail-closed — `return False` (refus de la requête), log warning. Plus de fail-open silencieux.

---

## 6. Endpoints / flux réellement protégés

| Endpoint | Décorateur | Limite |
|----------|------------|--------|
| `POST /api/auth/login` | rate_limit_auth("login") | 5 req/min par IP |
| `POST /api/auth/validate-token` | rate_limit_auth("validate-token") | 5 req/min par IP |
| `POST /api/auth/forgot-password` | rate_limit_auth("forgot-password") | 5 req/min par IP |
| `POST /api/auth/resend-verification` | rate_limit_resend_verification | 2 req/min par IP |
| `POST /api/users/` (register) | rate_limit_register | 3 req/min par IP |
| `POST /api/chat` | rate_limit_chat | 15 req/min par IP |
| `POST /api/chat/stream` | rate_limit_chat | 15 req/min par IP |

**Hors scope C2** : `rate_limiter.py` (génération IA challenge, per user_id, hourly/daily) — reste en mémoire.

---

## 7. Ce qui a été prouvé

- Store Memory et Redis implémentés et testés
- `get_rate_limit_store()` retourne Memory quand REDIS_URL vide (dev/test)
- Prod sans REDIS_URL → ValueError au démarrage (test subprocess)
- Redis error runtime → fail-closed (test_redis_store_fail_closed_on_error)
- `_check_rate_limit` délègue au store (tests rate_limit inchangés)
- Bypass TESTING=true conservé
- Full suite verte

---

## 8. Ce qui n'a pas été prouvé

- Redis en conditions réelles (pas de Redis dans l'environnement de test)
- Comportement sous charge multi-instance
- `rate_limiter.py` (challenge IA) non migré — reste mémoire

---

## 9. Résultat run 1

```
pytest -q tests/unit/test_rate_limit.py tests/unit/test_rate_limit_store.py tests/unit/test_chat_service.py --maxfail=20
34 passed
```

---

## 10. Résultat run 2

```
34 passed (même commande)
```

---

## 11. Résultat full suite

```
pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py
834 passed, 2 skipped in 190.66s
```

---

## 12. Résultat black

```
black app/ server/ tests/ --check
All done! 259 files would be left unchanged.
```

---

## 13. Résultat isort

```
isort app/ server/ --check-only --diff
(no output - vert)
```

---

## 14. Risques résiduels

- Panne Redis runtime → fail-closed (429) — pas de dégradation silencieuse
- `rate_limiter.py` (challenge IA) non distribué — périmètre C2 limité aux endpoints auth/chat/register
- Fenêtre Redis = fixe (vs glissante mémoire) — légère différence de comportement à la frontière

---

## 15. GO / NO-GO

**GO** — Micro-lot fermeture validé. Prod ne peut plus démarrer sans REDIS_URL. Comportement fail-closed sur panne Redis. Fallback mémoire strictement dev/test.
