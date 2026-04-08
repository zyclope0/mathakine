# Plan de session — Mathakine

## Fermeture du sidecar FFI-L19* (validate-token / rate-limit / proxy trust)

| Lot | Statut | Résumé |
|-----|--------|--------|
| **FFI-L19A** | Fermé | Bucket backend dédié `validate-token` (90/min/IP) ; login/forgot-password stricts (5/min). |
| **FFI-L19B** | Fermé | Next server : `validateTokenRuntime.ts` — coalescence + micro-cache succès 2,5 s. |
| **FFI-L19C** | Fermé | Politique IP explicite : `RATE_LIMIT_TRUST_X_FORWARDED_FOR` + `_get_client_ip` documenté (voir rapport §17, `README_TECH`). |

**La séquence FFI-L19\* est terminée.** Ne pas rouvrir ce fil sans nouveau constat produit ou ticket dédié.

### Hors scope documenté (non traité en L19C)

- Headers CDN type `CF-Connecting-IP` sans setting et preuve infra dédiés.
- Liste `TRUSTED_PROXY_IPS` / CIDR pour n’utiliser XFF que si le hop TCP est un proxy connu.
- Re-key rate-limit par utilisateur (backlog produit distinct).

---

## Recentrage actif : roadmap frontend principale

Après clôture FFI-L19\*, la **priorité d’exécution** revient à la feuille de route **frontend** (standardisation, industrialisation UI, dette UX technique), notamment :

- `docs/02-FEATURES/ROADMAP_FONCTIONNALITES.md`
- `docs/03-PROJECT/README.md` et trackers projet associés
- audits de contexte : `docs/03-PROJECT/AUDIT_FRONTEND_STANDARDISATION_2026-03-29.md`, `AUDIT_FRONTEND_INDUSTRIALISATION_2026-03.md` (lecture / priorisation, pas de nouvelle digression backend rate-limit)

Les changements backend hors périmètre roadmap frontend doivent rester **petits, nommés et reviewables** (pas de mélange avec une « suite » FFI-L19 ad hoc).
