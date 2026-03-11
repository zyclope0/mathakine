# Delta restant post iteration backend challenge/admin/badge

Date: 2026-03-11
Statut: non bloquant pour la cloture locale

## Delta technique
### Faux gate connu
- `tests/api/test_admin_auth_stability.py`
  - Lance `pytest` depuis `pytest` avec couverture.
  - Ne doit pas etre utilise comme gate de validation standard.
  - A isoler ou reecrire si on veut une preuve de stabilite transverse fiable.

### Hotspots restant volumineux
- `app/services/challenge_validator.py`
- `app/services/badge_service.py`
- `app/services/admin_content_service.py`
- `app/services/admin_stats_service.py`

### Dette de preuve secondaire
- Certaines validations d'erreur fines restent principalement prouvees par la full suite ou des tests indirects, pas par une matrice exhaustive endpoint par endpoint.
- Ce point est acceptable pour la cloture locale, mais pas pour une promesse de couverture exhaustive du produit.

## Delta documentation
- Garder `README_TECH.md`, `docs/00-REFERENCE/ARCHITECTURE.md` et `docs/02-FEATURES/API_QUICK_REFERENCE.md` alignes lors de la prochaine vague de changements backend.
- Conserver la distinction entre:
  - changelog produit public
  - versioning interne d'iteration backend

## Recommandation suite
1. Commit/push de l'iteration challenge/admin/badge en `3.1.0-alpha.8`.
2. Ne pas reutiliser `tests/api/test_admin_auth_stability.py` comme gate CI sans reecriture.
3. Ouvrir la prochaine iteration uniquement sur un perimetre borne et independant.
