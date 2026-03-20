# R4 — Lifecycle de feedback recommandations (minimum viable)

> **Date** : 2026-03-20  
> **R4b** (2026-03-20) : même lifecycle ; **QuickStartActions** aligné sur `recordOpen` pour les CTA guidés.  
> **Objectif** : rendre le modèle `Recommendation` **réellement alimenté** par des signaux utilisateur, sans migration ni contrat HTTP cassant.  
> **Non-objectif** : moteur « apprenant », auto-complétion systématique à chaque tentative exercice (hors périmètre).

---

## 0. Où le clic « open » est branché (dashboard)

| Zone UI | `POST /api/recommendations/open` (`recordOpen`) |
|---------|--------------------------------------------------|
| Carte **`Recommendations.tsx`** | Oui — lien « S'entraîner » / « Relever le défi » vers exercice ou défi. |
| **`QuickStartActions.tsx`** | **Oui (R4b)** — uniquement si le CTA est **guidé** : lien direct vers `/exercises/:id` ou `/challenge/:id` issu d’une reco avec `id` API. **Non** si l’utilisateur part vers la liste (`/exercises`, `/challenges`) ou **Session entrelacée** (pas de reco ciblée). |

Avant R4b, seule la carte **Recommendations** remontait le signal ; la doc ne doit pas laisser entendre que tout le dashboard l’était déjà.

---

## 1. Signaux et sémantique

| Signal | Où c’est branché | Sémantique |
|--------|-------------------|------------|
| **`shown_count`** | Fin de `GET /api/recommendations` (liste effectivement renvoyée) | Nombre de **réponses GET liste** ayant inclus cette reco (+1 par requête où elle apparaît). Limite les surcomptes **React** : pas d’incrément au render, seulement au fetch API. |
| **`clicked_count`**, **`last_clicked_at`** | `POST /api/recommendations/open` (+ alias `/clicked`) via **`recordOpen`** depuis **`Recommendations.tsx`** et **`QuickStartActions.tsx`** (parcours guidés uniquement) | **Intent** utilisateur : ouverture depuis une reco identifiée (`recommendation_id`). Chaque POST incrémente (non idempotent). Vérification **user_id** = propriétaire de la reco. |
| **`is_completed`**, **`completed_at`** | `POST /api/recommendations/complete` (inchangé côté URL) | **Acquittement manuel** (`completion_kind: manual_ack`). Le JSON inclut **`verified_by_attempt`** : `true` si, **au moment du POST**, une tentative **réussie** existe déjà sur l’`exercise_id` ou `challenge_id` recommandé — corrélation **honnête** avec le contenu ; `false` sinon. |

---

## 2. Endpoints

- `GET /api/recommendations` — inchangé pour le client ; effet serveur : impression liste (voir ci-dessus).
- `POST /api/recommendations/open` — body `{ "recommendation_id": int }` ; réponse `{ id, clicked_count, last_clicked_at }`.
- `POST /api/recommendations/clicked` — **alias** du même handler (même body/réponse), au cas où une couche intermédiaire filtrerait le segment `open`.
- `POST /api/recommendations/complete` — body inchangé ; réponse enrichie : `verified_by_attempt`, `completion_kind`.

---

## 3. Limites explicites (honnêteté produit)

- **Pas** d’auto-complétion de reco au moment où l’utilisateur termine un exercice ailleurs (ex. page exercice) dans ce lot — blast radius trop large.
- **`verified_by_attempt`** ne prouve pas que l’utilisateur a « fait cette reco » le même jour ; seulement qu’**une** réussite existe sur le **même** contenu cible.
- **`shown_count`** augmente à chaque GET utile (ex. refocus onglet + refetch React Query) : borné par l’usage réel, pas une « vue unique » sans colonne dédiée.

---

## 4. Fichiers principaux

- `app/services/recommendation/recommendation_service.py`
- `server/handlers/recommendation_handlers.py`
- `server/routes/misc.py`
- `frontend/hooks/useRecommendations.ts`
- `frontend/components/dashboard/Recommendations.tsx`
- `frontend/components/dashboard/QuickStartActions.tsx` (R4b — `recordOpen` sur CTA guidés)

---

## 5. Validation (R4b — 2026-03-20)

- **Tests Vitest** : `QuickStartActions.test.tsx` — 10 tests, dont 3 spécifiques R4b (`recordOpen` guidé / non guidé / entrelacé).
- **Backend ciblé** : `tests/unit/test_recommendation_service.py` + `tests/api/test_recommendation_endpoints.py` → **29 passed** (×2 runs identiques).
- **Full gate** : `pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py --no-cov` → **980 passed, 2 skipped** sur la machine de clôture R4b.

**Stabilité** : une exécution full gate **antérieure** à R4b avait été observée comme instable (échec puis succès) ; **aucune cause n’a été isolée dans le périmètre R4b** (pas de changement backend dans ce micro-lot). Si le symptôme réapparaît : isoler le test fautif, vérifier DB partagée / ordre des tests, hors refactor reco.
