# Lot C4 - Legacy API Truth — Compte-rendu final

> Date: 15/03/2026
> Iteration: C - Production Hardening
> Statut: **terminé**
> Micro-lot clôture : revalidation vérité terrain 15/03/2026

---

## Revalidation vérité terrain (micro-lot clôture)

| Vérification | Résultat |
|--------------|----------|
| `app/api/endpoints/*` absent du runtime actif | OK — dossier n'existe pas |
| Imports actifs `app.api.endpoints` / `app.api.deps` | Aucun — grep sur app/, server/, tests/ : 0 résultat |
| Archive `_ARCHIVE_2026/app/api/` présente | OK — deps.py, endpoints/* (auth, badges, challenges, exercises, recommendations, users) |
| Wiring runtime | OK — server/app.py → get_routes() uniquement, pas d'import app.api |
| Full suite | 868 passed, 2 skipped |
| black | OK — 261 fichiers inchangés |
| isort | OK — aucune sortie |

---

## 1. Fichiers modifiés

| Fichier | Action |
|---------|--------|
| `app/api/__init__.py` | M — stub explicatif (legacy archivé) |
| `app/api/endpoints/*` | S — supprimé (archivé) |
| `app/api/deps.py` | S — supprimé (archivé) |
| `_ARCHIVE_2026/app/api/endpoints/*` | A — copie des endpoints |
| `_ARCHIVE_2026/app/api/deps.py` | A — copie |
| `_ARCHIVE_2026/FASTAPI_ARCHIVE_NOTE.md` | M — documentation archivage endpoints |
| `README_TECH.md` | M — legacy archive |
| `README.md` | M — legacy archive |
| `docs/00-REFERENCE/ARCHITECTURE.md` | M — legacy archive |
| `docs/00-REFERENCE/GETTING_STARTED.md` | M — legacy archive |
| `docs/02-FEATURES/API_QUICK_REFERENCE.md` | M — legacy archive |
| `docs/INDEX.md` | M — legacy archive |
| `docs/06-WIDGETS/ENDPOINTS_PROGRESSION.md` | M — legacy archive |

---

## 2. Fichiers runtime modifiés

**Aucun.** Le runtime `server/routes/*`, `server/handlers/*`, `server/app.py` n'a pas été touché.

---

## 3. Fichiers legacy retirés / archivés / laissés

| Fichier | Action |
|---------|--------|
| `app/api/endpoints/auth.py` | Archivé → `_ARCHIVE_2026/app/api/endpoints/` |
| `app/api/endpoints/badges.py` | Archivé → `_ARCHIVE_2026/app/api/endpoints/` |
| `app/api/endpoints/challenges.py` | Archivé → `_ARCHIVE_2026/app/api/endpoints/` |
| `app/api/endpoints/exercises.py` | Archivé → `_ARCHIVE_2026/app/api/endpoints/` |
| `app/api/endpoints/recommendations.py` | Archivé → `_ARCHIVE_2026/app/api/endpoints/` |
| `app/api/endpoints/users.py` | Archivé → `_ARCHIVE_2026/app/api/endpoints/` |
| `app/api/endpoints/__init__.py` | Archivé → `_ARCHIVE_2026/app/api/endpoints/` |
| `app/api/deps.py` | Archivé → `_ARCHIVE_2026/app/api/` |
| `app/api/__init__.py` | Conservé — stub minimal |

---

## 4. Statut final de `app/api/endpoints/*`

**Archivé.** Le périmètre n'existe plus dans `app/api/`. Il est conservé dans `_ARCHIVE_2026/app/api/endpoints/` pour référence historique. Aucune réactivation implicite.

---

## 5. Source de vérité runtime officielle après lot

- **Routes** : `server/routes/` + `server/handlers/`
- **Point d'entrée** : `enhanced_server.py` → `server.app.create_app()` → `get_routes()`
- **Référence API** : `docs/02-FEATURES/API_QUICK_REFERENCE.md`

---

## 6. Références actives restantes ou absence de références

**Aucune référence active.** `grep` sur `app.api` et `api.endpoints` dans le code Python : 0 résultat. Le périmètre n'était jamais importé.

---

## 7. Ce qui a été prouvé

- Wiring runtime : `server/app.py` utilise uniquement `server.routes.get_routes()` — aucun import de `app.api`
- Absence d'imports actifs : aucun fichier dans `app/`, `server/`, `tests/` n'importe `app.api.endpoints` ou `app.api.deps`
- Archivage : endpoints et deps copiés dans `_ARCHIVE_2026/`, originaux supprimés
- Full suite verte : 868 passed, 2 skipped (revalidation micro-lot clôture)
- Documentation : README_TECH, ARCHITECTURE, API_QUICK_REFERENCE, INDEX, GETTING_STARTED, ENDPOINTS_PROGRESSION alignés

---

## 8. Ce qui n'a pas été prouvé

- Réactivation du legacy (hors scope)

---

## 9. Résultat full suite (revalidation micro-lot clôture)

```
pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py --no-cov
```

**Résultat observé** : 868 passed, 2 skipped.

---

## 10. Résultat black

```
black app/ server/ tests/ --check
```

**Résultat** : OK — 261 fichiers inchangés.

---

## 11. Résultat isort

```
isort app/ server/ --check-only --diff
```

**Résultat** : OK — aucune sortie.

---

## 12. Risques résiduels

- Aucun pour le périmètre C4

---

## 13. Corrections factuelles (micro-lot clôture)

- Remplacement « 632 passed, 9 failed » par « 868 passed, 2 skipped » (résultat réel rerunné)
- Suppression des mentions d'échecs préexistants (full suite verte)
- Ajout tableau revalidation vérité terrain
- Mise à jour « Ce qui a été prouvé » : full suite verte incluse

---

## 14. GO / NO-GO

**GO** — Clôture C4. Le statut de `app/api/endpoints/*` est tranché : archivé, non monté, non importé. La source de vérité runtime est documentée. Full suite verte (868 passed, 2 skipped). black et isort verts. Aucune réactivation implicite. Report aligné sur la vérité terrain rerunnée.
