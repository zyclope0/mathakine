# F07 — Implémentation Guidée: Courbe d'Évolution Temporelle

**Date**: 07/03/2026  
**Statut**: Prêt à implémenter  
**Niveau**: Moyen  
**Objectif**: Livrer un suivi temporel robuste de la progression utilisateur (backend + frontend + tests + docs) avec risque faible.

---

## 1. Contexte

La roadmap identifie F07 ("Courbe d'évolution temporelle") comme une priorité P1.  
Le besoin est d'afficher l'évolution quotidienne de l'activité et de la réussite, sur 7 ou 30 jours, de manière exploitable pour l'élève et cohérente avec les principes pédagogiques.

Cette implémentation doit rester:
- factuelle (données issues des tentatives réelles),
- lisible (graphique simple),
- industrialisée (pas de duplication, tests ciblés, contrats clairs).

---

## 2. Objectif Produit

Ajouter une visualisation temporelle de progression sur le dashboard (onglet Progression), alimentée par un endpoint backend dédié.

Résultat attendu:
- l'utilisateur voit sa dynamique quotidienne (volume + réussite),
- le produit peut ensuite brancher des feedbacks personnalisés (phase future),
- la base technique est réutilisable pour d'autres widgets analytics.

---

## 3. Scope MVP+

### 3.1 Backend

Ajouter un endpoint authentifié:
- `GET /api/users/me/progress/timeline?period=7d|30d`

Réponse attendue:
- `period`
- `from`
- `to`
- `points`: liste journalière triée croissante
  - `date` (`YYYY-MM-DD`)
  - `attempts`
  - `correct`
  - `success_rate_pct`
  - `avg_time_spent_s` (nullable)
- `summary`
  - `total_attempts`
  - `total_correct`
  - `overall_success_rate_pct`

Amélioration incluse (plus-value):
- `by_type` par point journalier (map `exercise_type -> {attempts, correct, success_rate_pct}`), même si non affiché dans l'UI initiale.

### 3.2 Frontend

Ajouter un widget "Évolution temporelle" dans l'onglet Progression:
- sélecteur période `7j` / `30j`,
- ligne de tendance (taux de réussite),
- barres de volume (tentatives),
- états `loading`, `empty`, `error`.

Contraintes UI:
- réutiliser les patterns existants dashboard,
- respecter i18n FR/EN,
- ne pas introduire de style isolé non conforme au design system.

### 3.3 Tests & Docs

Inclure:
- tests backend service + handler,
- test frontend hook (mapping + états),
- mise à jour docs:
  - `docs/02-FEATURES/ROADMAP_FONCTIONNALITES.md` (F07 statut/avancement),
  - `docs/02-FEATURES/API_QUICK_REFERENCE.md` (nouvel endpoint),
  - `CHANGELOG.md`.

---

## 4. Hors Scope (important)

Ne pas inclure dans ce lot:
- recommandations IA basées sur la timeline,
- segmentation hebdomadaire avancée,
- comparaisons utilisateurs,
- recalibrage adaptatif automatique depuis la courbe,
- migrations lourdes de schéma.

---

## 5. Critères d'Acceptation

### 5.1 Fonctionnel

- L'endpoint renvoie des données correctes pour `7d` et `30d`.
- Les jours sans activité sont présents avec `attempts=0`.
- Le calcul `success_rate_pct` est fiable (0 si `attempts=0`).
- `avg_time_spent_s` est `null` si aucune donnée valide.
- Le widget affiche correctement les courbes et gère tous les états UX.

### 5.2 Qualité

- Pas de duplication inutile (agrégations centralisées).
- Typage propre backend/frontend.
- Aucune régression sur endpoints existants.
- Tests ciblés verts.
- i18n structure valide.

---

## 6. Contrat API (proposé)

Exemple de réponse:

```json
{
  "period": "7d",
  "from": "2026-03-01",
  "to": "2026-03-07",
  "points": [
    {
      "date": "2026-03-01",
      "attempts": 6,
      "correct": 4,
      "success_rate_pct": 66.7,
      "avg_time_spent_s": 41.2,
      "by_type": {
        "addition": { "attempts": 2, "correct": 2, "success_rate_pct": 100.0 },
        "division": { "attempts": 4, "correct": 2, "success_rate_pct": 50.0 }
      }
    }
  ],
  "summary": {
    "total_attempts": 23,
    "total_correct": 17,
    "overall_success_rate_pct": 73.9
  }
}
```

---

## 7. Plan d'Implémentation

### Étape 1 — Backend Service

- Implémenter une fonction d'agrégation timeline dans le service utilisateur/progression.
- Construire la série journalière continue (`from -> to`) avec remplissage des jours vides.
- Calculer les métriques globales (`summary`).

### Étape 2 — Backend Handler + Route

- Ajouter le handler HTTP.
- Valider `period` (`7d`, `30d`; fallback `7d`).
- Brancher la route dans `server/routes/users.py`.

### Étape 3 — Frontend Hook

- Créer un hook dédié:
  - fetch endpoint timeline,
  - cache query key stable (`["user","progress","timeline",period]`),
  - typage strict des structures.

### Étape 4 — Widget Dashboard

- Créer composant graphique timeline.
- Intégrer dans onglet Progression.
- États `loading/empty/error` cohérents.

### Étape 5 — Tests + Documentation

- Tests backend et frontend.
- MAJ roadmap, API quick reference, changelog.

---

## 8. Checklist Validation

### Backend

- `pytest` ciblé sur service/handler timeline.
- Vérification des cas:
  - aucune tentative,
  - jours vides intermédiaires,
  - temps moyen null/valide.

### Frontend

- `eslint` sur fichiers touchés.
- tests du hook (`loading/error/data mapping`).
- rendu du widget vérifié en local.

### i18n

- `npm run i18n:validate` dans `frontend/`.

---

## 9. Risques et Mitigation

Risque:
- erreur d'agrégation temporelle (timezone/jours manquants).

Mitigation:
- normaliser les dates côté backend en UTC date-only,
- tester explicitement les bornes `from/to`.

Risque:
- couplage trop fort UI/API.

Mitigation:
- utiliser types dédiés côté hook,
- garder une adaptation locale du payload avant rendu.

---

## 10. Définition de Fini (DoD)

La feature est "Done" si:
- endpoint opérationnel et testé,
- widget visible et stable sur `7j/30j`,
- docs backlog/API/changelog à jour,
- lint/tests/i18n valides,
- commit unique propre orienté intention.

---

## 11. Prompt Cursor (exécution)

```md
Implémente F07 (courbe d’évolution temporelle) selon docs/03-PROJECT/IMPLEMENTATION_F07_TIMELINE.md.

Contraintes:
- Industrialisation + no-DRY
- Pas de régression
- Typage strict
- i18n FR/EN

Livrables:
1) Endpoint GET /api/users/me/progress/timeline?period=7d|30d
2) Agrégation journalière continue avec summary + by_type
3) Hook frontend + widget dashboard progression
4) Tests backend/frontend ciblés
5) MAJ docs (ROADMAP/API_QUICK_REFERENCE/CHANGELOG)

A la fin:
- liste des fichiers modifiés
- commandes de validation lancées
- limites connues éventuelles
```

---

## 12. Prompt Cursor (revue qualité)

```md
Fais une revue qualité de l’implémentation F07:
- bugs potentiels
- régressions comportementales
- duplication résiduelle
- écarts au contrat API
- trous de tests
- incohérences i18n

Propose un patch minimal, puis applique-le.
```

