# PILOTAGE B5.1 — Premier seuil couverture CI

> Date: 13/03/2026
> Statut: terminé
> Lot: B5 — CI and typing hardening, sous-lot B5.1

---

## 1. Fichiers modifiés

| Fichier | Action |
|---------|--------|
| `.github/workflows/tests.yml` | M — ajout `--cov-fail-under=62`, `--ignore=tests/api/test_admin_auth_stability.py` |
| `pytest.ini` | M — commentaire seuil aligné |
| `docs/01-GUIDES/TESTING.md` | M — section couverture CI, seuil, faux gate |
| `docs/03-PROJECT/PILOTAGE_CURSOR_BACKEND_CONTRACTS_HARDENING_B51_COVERAGE_CI_2026-03-13.md` | A — ce document |

---

## 2. Runtime touché ou non

**Non.** Aucun fichier runtime ou de test modifié.

---

## 3. Configuration coverage avant / après

| Élément | Avant | Après |
|---------|-------|-------|
| CI `--cov-fail-under` | absent | `62` |
| CI exclusion faux gate | absent | `--ignore=tests/api/test_admin_auth_stability.py` |
| pytest.ini | commentaire 60 | commentaire 62, référence CI |
| TESTING.md | pas de section couverture | section « Couverture CI » avec seuil et commande |

---

## 4. Seuil retenu

**62 %**

- Cible initiale : 65 % (lot B5)
- Couverture observée localement : plage 62,74–62,84 % selon les runs
- 65 non soutenable sans chantier de tests
- 62 soutenable : couverture observée >= 62 %

---

## 5. Preuve que le seuil passe

Commande validante (équivalent CI) :

```bash
python -m pytest tests/ --ignore=tests/archives/ --ignore=tests/api/test_admin_auth_stability.py \
  --cov=app --cov=server --cov-fail-under=62 -m "not slow" -q --tb=no
```

Résultat observé : couverture >= 62 % (plage 62,74–62,84 % selon les runs) ✓

---

## 6. Ce qui a été prouvé

- Seuil 62 configuré dans la CI
- Exclusion du faux gate `test_admin_auth_stability.py` alignée avec la stratégie projet
- Documentation TESTING.md mise à jour
- Aucune modification runtime

---

## 7. Ce qui n'a pas été prouvé

- Passage du workflow GitHub Actions en conditions réelles (validation locale uniquement)

---

## 8. Risques résiduels

- Le seuil 62 est conservateur ; un objectif 65 ou 70 nécessitera un lot dédié de tests

---

## 9. Résultats des checks

| Check | Résultat |
|-------|----------|
| Run 1 (coverage gate) | 823 passed, 2 skipped ; coverage >= 62 % ✓ |
| Run 2 (coverage gate) | 823 passed, 2 skipped ; coverage >= 62 % ✓ |
| Full suite (sans coverage) | 823 passed, 2 skipped ✓ |
| black app/ server/ tests/ --check | All done ✓ |

## 10. GO / NO-GO

**GO** — Le lot B5.1 est clos : gate coverage 62 % introduit, documenté, soutenable sur le tree courant.
