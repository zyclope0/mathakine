# Delta restant post iteration backend challenge/admin/badge

Date: 2026-03-11
Statut: trace historique locale, non bloquante

## Delta technique
### Faux gate connu
- `tests/api/test_admin_auth_stability.py`
  - Lance `pytest` depuis `pytest` avec couverture.
  - Ne doit pas etre utilise comme gate de validation standard.
  - A isoler ou reecrire si on veut une preuve de stabilite transverse fiable.

### Hotspots restant volumineux
- `app/services/challenge_validator.py`
- `app/services/admin_content_service.py`
- `app/services/auth_service.py`
- `app/services/user_service.py`
- `app/services/exercise_service.py`
- `app/services/challenge_service.py`
- `app/services/badge_requirement_engine.py`

Note:
- `badge_service.py` et `admin_stats_service.py` ont depuis ete decomposes dans
  `Contracts / Hardening`
- `challenge_validator.py` a ete clarifie par dispatch et extractions bornees,
  mais reste un gros module

### Dette de preuve secondaire
- Certaines validations d'erreur fines restent principalement prouvees par la full suite ou des tests indirects, pas par une matrice exhaustive endpoint par endpoint.
- Ce point est acceptable pour la cloture locale, mais pas pour une promesse de couverture exhaustive du produit.

## Delta documentation
- Garder `README_TECH.md`, `docs/00-REFERENCE/ARCHITECTURE.md` et `docs/02-FEATURES/API_QUICK_REFERENCE.md` alignes lors de la prochaine vague de changements backend.
- Conserver la distinction entre:
  - changelog produit public
  - versioning interne d'iteration backend

## Note d'actualisation

L'iteration `challenge/admin/badge`, puis `Runtime Truth` et `Contracts / Hardening`,
ont depuis ete cloturees et poussees. Ce document reste utile pour garder la
trace du faux gate connu et de la dette de preuve secondaire, mais ne doit plus
etre lu comme une feuille de route active.
